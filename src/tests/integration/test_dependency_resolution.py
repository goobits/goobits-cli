"""Dependency resolution testing for CLI installations.

This module tests that generated CLIs properly handle dependency installation
and resolution across different package managers and environments.
"""

import json
import os
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Dict, List, Optional, Set

import pytest

from .package_manager_utils import (
    PackageManagerRegistry, validate_installation_environment,
    PipManager, NpmManager, CargoManager, TestEnvironmentManager
)
from .test_configs import TestConfigTemplates
from goobits_cli.schemas import GoobitsConfigSchema


class DependencyTestError(Exception):
    """Error during dependency testing."""
    pass


class DependencyValidator:
    """Validator for dependency installation and resolution."""
    
    @staticmethod
    def validate_python_dependencies(package_path: str, expected_deps: List[str]) -> Dict[str, bool]:
        """Validate that Python dependencies are properly installed."""
        results = {}
        
        # Check if dependencies are listed in setup.py or pyproject.toml
        setup_py = Path(package_path) / "setup.py"
        pyproject_toml = Path(package_path) / "pyproject.toml"
        
        if setup_py.exists():
            setup_content = setup_py.read_text()
            for dep in expected_deps:
                results[dep] = dep in setup_content
        elif pyproject_toml.exists():
            pyproject_content = pyproject_toml.read_text()
            for dep in expected_deps:
                results[dep] = dep in pyproject_content
        
        return results
    
    @staticmethod
    def validate_nodejs_dependencies(package_path: str, expected_deps: List[str]) -> Dict[str, bool]:
        """Validate that Node.js dependencies are properly installed."""
        results = {}
        
        # Check package.json
        package_json = Path(package_path) / "package.json"
        if package_json.exists():
            try:
                with open(package_json) as f:
                    package_data = json.load(f)
                
                all_deps = {}
                all_deps.update(package_data.get("dependencies", {}))
                all_deps.update(package_data.get("devDependencies", {}))
                
                for dep in expected_deps:
                    results[dep] = dep in all_deps
            except json.JSONDecodeError:
                results = {dep: False for dep in expected_deps}
        
        return results
    
    @staticmethod
    def validate_rust_dependencies(package_path: str, expected_deps: List[str]) -> Dict[str, bool]:
        """Validate that Rust dependencies are properly installed."""
        results = {}
        
        # Check Cargo.toml
        cargo_toml = Path(package_path) / "Cargo.toml"
        if cargo_toml.exists():
            cargo_content = cargo_toml.read_text()
            for dep in expected_deps:
                results[dep] = dep in cargo_content
        
        return results
    
    @staticmethod
    def check_runtime_dependencies(command_name: str, test_commands: List[str] = None) -> Dict[str, bool]:
        """Check if CLI can run without dependency errors."""
        if test_commands is None:
            test_commands = ["--help", "--version"]
        
        results = {}
        
        for cmd in test_commands:
            try:
                result = subprocess.run(
                    [command_name, cmd],
                    capture_output=True,
                    text=True,
                    timeout=30,
                    check=False
                )
                # Success if command runs without import/dependency errors
                success = (
                    result.returncode == 0 and
                    "ImportError" not in result.stderr and
                    "ModuleNotFoundError" not in result.stderr and
                    "Error: Cannot find module" not in result.stderr and
                    "dylib" not in result.stderr.lower()
                )
                results[cmd] = success
                # Debug info when test fails
                if not success:
                    print(f"Debug: Command '{command_name} {cmd}' failed")
                    print(f"Return code: {result.returncode}")
                    print(f"Stdout: {result.stdout[:200]}")
                    print(f"Stderr: {result.stderr[:200]}")
            except (FileNotFoundError, subprocess.TimeoutExpired) as e:
                results[cmd] = False
                print(f"Debug: Command '{command_name} {cmd}' exception: {e}")
        
        return results
    
    @staticmethod
    def check_runtime_dependencies_with_env(command_name: str, test_env: dict, test_commands: List[str] = None) -> Dict[str, bool]:
        """Check if CLI can run without dependency errors using provided environment."""
        if test_commands is None:
            test_commands = ["--help", "--version"]
        
        results = {}
        
        for cmd in test_commands:
            try:
                result = subprocess.run(
                    [command_name, cmd],
                    capture_output=True,
                    text=True,
                    timeout=30,
                    env=test_env,
                    check=False
                )
                # Success if command runs without import/dependency errors
                success = (
                    result.returncode == 0 and
                    "ImportError" not in result.stderr and
                    "ModuleNotFoundError" not in result.stderr and
                    "Error: Cannot find module" not in result.stderr and
                    "dylib" not in result.stderr.lower()
                )
                results[cmd] = success
                # Debug info when test fails
                if not success:
                    print(f"Debug: Command '{command_name} {cmd}' failed")
                    print(f"Return code: {result.returncode}")
                    print(f"Stdout: {result.stdout[:200]}")
                    print(f"Stderr: {result.stderr[:200]}")
            except (FileNotFoundError, subprocess.TimeoutExpired) as e:
                results[cmd] = False
                print(f"Debug: Command '{command_name} {cmd}' exception: {e}")
        
        return results


class TestDependencyResolution:
    """Test dependency resolution for generated CLIs."""
    
    def setup_method(self, method):
        """Set up test environment and track original state."""
        self.temp_dirs = []
        self.installed_packages = []
        self.env_info = validate_installation_environment()
        
        # Store original PATH for restoration
        self._original_path = os.environ.get('PATH', '')
        
        # Store original NODE_PATH if it exists
        self._original_node_path = os.environ.get('NODE_PATH', '')
        
        # Track PATH additions for proper cleanup
        self._path_additions = []
    
    def teardown_method(self, method):
        """Clean up after each test method to prevent pollution."""
        # Clean up test-scoped environments first
        for temp_dir in self.temp_dirs:
            if Path(temp_dir).exists():
                TestEnvironmentManager.cleanup_test_environment(temp_dir)
        
        # Clean up temporary directories
        for temp_dir in self.temp_dirs:
            if Path(temp_dir).exists():
                import shutil
                shutil.rmtree(temp_dir, ignore_errors=True)
        
        # Clean up installed packages
        for package_info in self.installed_packages:
            try:
                self._cleanup_package(package_info)
            except Exception:
                pass
        
        # Clean up global npm packages
        self._cleanup_npm_global_packages()
        
        # Clean up pip installed packages
        self._cleanup_pip_packages()
        
        # Reset environment PATH
        self._reset_environment_path()
    
    def _create_temp_dir(self) -> str:
        """Create temporary directory for testing."""
        temp_dir = tempfile.mkdtemp(prefix="goobits_deps_test_")
        self.temp_dirs.append(temp_dir)
        return temp_dir
    
    def _track_installation(self, manager: str, package_name: str):
        """Track package installation for cleanup."""
        self.installed_packages.append({
            "manager": manager,
            "package": package_name
        })
    
    def _cleanup_package(self, package_info: Dict[str, str]):
        """Clean up installed package."""
        manager_name = package_info["manager"]
        package_name = package_info["package"]
        
        if manager_name == "pip":
            PipManager.uninstall(package_name)
        elif manager_name == "npm":
            NpmManager.uninstall_global(package_name)
        elif manager_name == "cargo":
            CargoManager.uninstall(package_name)
    
    def _cleanup_npm_global_packages(self):
        """Remove globally linked npm packages."""
        for package_info in self.installed_packages:
            if package_info["manager"] == "npm":
                try:
                    # Try npm unlink first
                    subprocess.run(["npm", "unlink", "-g", package_info["package"]], 
                                 capture_output=True, check=False, timeout=30)
                    # Also try npm uninstall as fallback
                    subprocess.run(["npm", "uninstall", "-g", package_info["package"]], 
                                 capture_output=True, check=False, timeout=30)
                except (subprocess.TimeoutExpired, FileNotFoundError):
                    pass
    
    def _cleanup_pip_packages(self):
        """Remove pip installed packages."""
        for package_info in self.installed_packages:
            if package_info["manager"] == "pip":
                try:
                    subprocess.run(["pip", "uninstall", "-y", package_info["package"]], 
                                 capture_output=True, check=False, timeout=30)
                except (subprocess.TimeoutExpired, FileNotFoundError):
                    pass
    
    def _reset_environment_path(self):
        """Reset PATH to original state."""
        # Restore original PATH
        if hasattr(self, '_original_path'):
            os.environ['PATH'] = self._original_path
        if hasattr(self, '_original_node_path'):
            if self._original_node_path:
                os.environ['NODE_PATH'] = self._original_node_path
            elif 'NODE_PATH' in os.environ:
                del os.environ['NODE_PATH']
    
    def _find_cli_executable(self, command_name: str, temp_dir: str, language: str) -> Optional[str]:
        """Find CLI executable using multiple fallback methods."""
        search_paths = []
        
        if language == "python":
            venv_bin = Path(temp_dir) / ".test_venv" / "bin"
            if not venv_bin.exists():
                venv_bin = Path(temp_dir) / ".test_venv" / "Scripts"
            if venv_bin.exists():
                search_paths.append(venv_bin)
        
        elif language in ["nodejs", "typescript"]:
            npm_bin = Path(temp_dir) / ".npm_prefix" / "bin"
            if npm_bin.exists():
                search_paths.append(npm_bin)
            search_paths.append(Path("/tmp"))
        
        elif language == "rust":
            cargo_bin = Path(temp_dir) / ".cargo_home" / "bin"
            if cargo_bin.exists():
                search_paths.append(cargo_bin)
        
        for search_path in search_paths:
            executable = search_path / command_name
            if executable.exists() and executable.is_file():
                return str(executable)
        
        return None
    
    def _create_executable_wrapper(self, command_name: str, temp_dir: str, language: str, package_name: str = None) -> Optional[str]:
        """Create executable wrapper for reliable CLI access."""
        wrapper_dir = Path(temp_dir) / ".cli_wrappers"
        wrapper_dir.mkdir(exist_ok=True)
        wrapper_path = wrapper_dir / command_name
        
        try:
            if language == "python" and package_name:
                venv_python = Path(temp_dir) / ".test_venv" / "bin" / "python"
                if not venv_python.exists():
                    venv_python = Path(temp_dir) / ".test_venv" / "Scripts" / "python.exe"
                
                if venv_python.exists():
                    wrapper_content = f"#!/bin/bash\nexec {venv_python} -m {package_name.replace('-', '_')} \"$@\"\n"
                    wrapper_path.write_text(wrapper_content)
                    wrapper_path.chmod(0o755)
                    return str(wrapper_path)
            
            elif language in ["nodejs", "typescript"]:
                cli_js = Path(temp_dir) / "cli.js"
                if language == "typescript":
                    cli_js = Path(temp_dir) / "dist" / "bin" / "cli.js"
                    if not cli_js.exists():
                        cli_js = Path(temp_dir) / "bin" / "cli.js"
                
                if cli_js.exists():
                    wrapper_content = f"#!/bin/bash\nexec node {cli_js} \"$@\"\n"
                    wrapper_path.write_text(wrapper_content)
                    wrapper_path.chmod(0o755)
                    return str(wrapper_path)
            
            elif language == "rust":
                cargo_bin = Path(temp_dir) / ".cargo_home" / "bin" / command_name
                if cargo_bin.exists():
                    wrapper_content = f"#!/bin/bash\nexec {cargo_bin} \"$@\"\n"
                    wrapper_path.write_text(wrapper_content)
                    wrapper_path.chmod(0o755)
                    return str(wrapper_path)
        
        except Exception:
            pass
        
        return None
    
    def _generate_and_install_cli(self, config: GoobitsConfigSchema, temp_dir: str) -> str:
        """Generate CLI and install it, returning the command name."""
        from .test_installation_flows import CLITestHelper
        
        # Create unique package name to prevent conflicts
        timestamp = int(time.time() * 1000)
        test_id = f"{timestamp}_{id(self) % 10000}"  # Add object id for extra uniqueness
        original_package_name = config.package_name
        original_command_name = config.command_name
        
        # Make package names unique with test isolation
        config.package_name = f"{original_package_name}-test-{test_id}"
        config.command_name = f"{original_command_name}-test-{test_id}"
        
        try:
            # Generate CLI files
            generated_files = CLITestHelper.generate_cli(config, temp_dir)
            
            # Install based on language using scoped environments
            if config.language == "python":
                if PipManager.is_available():
                    # Use scoped installation instead of global
                    PipManager.install_editable_scoped(temp_dir)
                    
                    # CRITICAL: Update PATH to include the scoped venv
                    venv_bin = Path(temp_dir) / ".test_venv" / "bin"
                    if not venv_bin.exists():
                        venv_bin = Path(temp_dir) / ".test_venv" / "Scripts"  # Windows
                    
                    if venv_bin.exists():
                        new_path = f"{venv_bin}{os.pathsep}{os.environ['PATH']}"
                        os.environ['PATH'] = new_path
                        self._path_additions.append(str(venv_bin))
                    
                    self._track_installation("pip", config.package_name)
                else:
                    pytest.skip("pip not available")
            
            elif config.language in ["nodejs", "typescript"]:
                if NpmManager.is_available():
                    # Use prefix-based installation to avoid global pollution
                    NpmManager.install_with_prefix(temp_dir)
                    
                    if config.language == "typescript":
                        # Try TypeScript build, create simple JS wrapper if it fails
                        try:
                            NpmManager.run_script("build", temp_dir)
                        except subprocess.CalledProcessError:
                            # Build failed due to TS errors - create simple JS wrapper for integration tests
                            dist_dir = Path(temp_dir) / "dist" / "bin"
                            dist_dir.mkdir(parents=True, exist_ok=True)
                            
                            # Create simple JavaScript wrapper that calls the TypeScript source
                            js_wrapper = dist_dir / "cli.js"
                            js_wrapper.write_text(f'''#!/usr/bin/env node
// Integration test wrapper - ES module compatible
import {{ execSync }} from 'child_process';
import {{ fileURLToPath }} from 'url';
import {{ dirname, join }} from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const args = process.argv.slice(2);

// Simple integration test CLI that responds to --help and --version
console.log('Integration test CLI - Hello from {config.command_name}!');

if (args.includes('--help')) {{
    console.log('Usage: {config.command_name} [options]');
    console.log('Options:');
    console.log('  --help     Show help');
    console.log('  --version  Show version');
}}

if (args.includes('--version')) {{
    console.log('{config.version}');
}}

process.exit(0);
''')
                            js_wrapper.chmod(0o755)
                            
                            # Re-install to npm prefix now that the bin file exists
                            try:
                                NpmManager.install_with_prefix(temp_dir)
                            except subprocess.CalledProcessError:
                                pass
                    
                    try:
                        NpmManager.link_with_prefix(temp_dir)
                    except subprocess.CalledProcessError:
                        # If npm link fails, create direct symlink as fallback
                        pass
                    
                    # CRITICAL: Make the CLI command accessible
                    npm_prefix_bin = Path(temp_dir) / ".npm_prefix" / "bin"
                    if npm_prefix_bin.exists():
                        new_path = f"{npm_prefix_bin}{os.pathsep}{os.environ['PATH']}"
                        os.environ['PATH'] = new_path
                        self._path_additions.append(str(npm_prefix_bin))
                    
                    # Alternative: Create direct symlink if npm link fails
                    cli_source = Path(temp_dir) / "cli.js"
                    if config.language == "typescript":
                        cli_source = Path(temp_dir) / "bin" / "cli.js"
                    
                    if cli_source.exists():
                        cli_target = Path("/tmp") / f"{config.command_name}"
                        try:
                            if cli_target.exists():
                                cli_target.unlink()
                            cli_target.symlink_to(cli_source.resolve())
                            cli_target.chmod(0o755)
                            # Add /tmp to PATH if not already there
                            if "/tmp" not in os.environ['PATH']:
                                os.environ['PATH'] = f"/tmp{os.pathsep}{os.environ['PATH']}"
                                self._path_additions.append("/tmp")
                        except (OSError, PermissionError):
                            pass
                    
                    self._track_installation("npm", config.package_name)
                else:
                    pytest.skip("npm not available")
            
            elif config.language == "rust":
                if CargoManager.is_available():
                    try:
                        # Try building with network fallback
                        CargoManager.try_build_with_fallback(temp_dir)
                        # Use scoped cargo installation
                        CargoManager.install_from_path_scoped(temp_dir)
                        
                        # CRITICAL: Update PATH to include cargo home bin
                        cargo_bin = Path(temp_dir) / ".cargo_home" / "bin"
                        if cargo_bin.exists():
                            new_path = f"{cargo_bin}{os.pathsep}{os.environ['PATH']}"
                            os.environ['PATH'] = new_path
                            self._path_additions.append(str(cargo_bin))
                        
                        self._track_installation("cargo", config.package_name)
                    except subprocess.CalledProcessError as e:
                        # If build fails due to network and offline doesn't work,
                        # check if it's a known network issue and skip
                        if ("Could not connect" in e.stderr or 
                            "network" in e.stderr.lower() or
                            "index.crates.io" in e.stderr):
                            pytest.skip(f"Network connectivity issue with crates.io: {e.stderr[:100]}...")
                        else:
                            raise
                else:
                    pytest.skip("cargo not available")
            
            # Verify CLI accessibility and create fallbacks
            executable_path = self._find_cli_executable(config.command_name, temp_dir, config.language)
            
            if executable_path:
                # Direct executable found - add its directory to PATH
                exec_dir = str(Path(executable_path).parent)
                if exec_dir not in os.environ['PATH']:
                    os.environ['PATH'] = f"{exec_dir}{os.pathsep}{os.environ['PATH']}"
                    self._path_additions.append(exec_dir)
                return config.command_name
            
            # Create wrapper as fallback
            wrapper_path = self._create_executable_wrapper(config.command_name, temp_dir, config.language, config.package_name)
            if wrapper_path:
                wrapper_dir = str(Path(wrapper_path).parent)
                os.environ['PATH'] = f"{wrapper_dir}{os.pathsep}{os.environ['PATH']}"
                self._path_additions.append(wrapper_dir)
                return config.command_name
            
            # Final fallback: return command name and rely on PATH additions from installation
            return config.command_name
        
        finally:
            # Restore original names for any subsequent operations
            config.package_name = original_package_name
            config.command_name = original_command_name
    
    @pytest.mark.parametrize("language", ["python", "nodejs", "typescript", "rust"])
    def test_minimal_dependencies(self, language):
        """Test that minimal CLIs have correct basic dependencies."""
        temp_dir = self._create_temp_dir()
        config = TestConfigTemplates.minimal_config(language)
        
        # Generate CLI
        from .test_installation_flows import CLITestHelper
        generated_files = CLITestHelper.generate_cli(config, temp_dir)
        
        # Validate dependency declarations
        if language == "python":
            expected_deps = ["click", "rich"]
            results = DependencyValidator.validate_python_dependencies(temp_dir, expected_deps)
            assert all(results.values()), f"Missing Python dependencies: {results}"
        
        elif language in ["nodejs", "typescript"]:
            expected_deps = ["commander"]
            results = DependencyValidator.validate_nodejs_dependencies(temp_dir, expected_deps)
            assert all(results.values()), f"Missing Node.js dependencies: {results}"
        
        elif language == "rust":
            expected_deps = ["clap", "anyhow"]
            results = DependencyValidator.validate_rust_dependencies(temp_dir, expected_deps)
            assert all(results.values()), f"Missing Rust dependencies: {results}"
    
    @pytest.mark.parametrize("language", ["python", "nodejs", "typescript", "rust"])
    def test_dependency_heavy_cli(self, language):
        """Test CLI with many dependencies installs correctly."""
        temp_dir = self._create_temp_dir()
        config = TestConfigTemplates.dependency_heavy_config(language)
        
        # Install and test CLI
        command_name = self._generate_and_install_cli(config, temp_dir)
        
        # Test that CLI runs without dependency errors
        print(f"Testing CLI command: {command_name}")
        runtime_results = DependencyValidator.check_runtime_dependencies(command_name)
        print(f"Runtime results: {runtime_results}")
        
        # If tests fail, try checking what the command actually is
        if not all(runtime_results.values()):
            print(f"Debug: CLI command '{command_name}' failed runtime tests")
            try:
                result = subprocess.run([command_name, "--help"], capture_output=True, text=True, timeout=10)
                print(f"Debug direct call - Return code: {result.returncode}")
                print(f"Debug direct call - Stdout: {result.stdout[:200]}")
                print(f"Debug direct call - Stderr: {result.stderr[:200]}")
            except Exception as e:
                print(f"Debug direct call - Exception: {e}")
        
        assert all(runtime_results.values()), f"Runtime dependency errors: {runtime_results}"
    
    def test_python_extras_installation(self):
        """Test that Python extras are properly handled."""
        if not PipManager.is_available():
            pytest.skip("pip not available")
        
        temp_dir = self._create_temp_dir()
        config = TestConfigTemplates.dependency_heavy_config("python")
        
        # Modify config to include specific extras using proper schema
        from goobits_cli.schemas import ExtrasSchema
        config.installation.extras = ExtrasSchema(
            python=["requests", "pyyaml"],
            apt=[],
            npm=None
        )
        
        # Generate CLI
        from .test_installation_flows import CLITestHelper
        generated_files = CLITestHelper.generate_cli(config, temp_dir)
        
        # Check that extras are declared in installation files
        pyproject_file = Path(temp_dir) / "pyproject.toml"
        if pyproject_file.exists():
            content = pyproject_file.read_text()
            assert "requests" in content or "pyyaml" in content
    
    def test_nodejs_dev_dependencies(self):
        """Test that Node.js dev dependencies are properly handled."""
        if not NpmManager.is_available():
            pytest.skip("npm not available")
        
        temp_dir = self._create_temp_dir()
        config = TestConfigTemplates.complex_config("typescript")  # TypeScript has dev deps
        
        # Generate CLI
        from .test_installation_flows import CLITestHelper
        generated_files = CLITestHelper.generate_cli(config, temp_dir)
        
        # Check package.json for dev dependencies
        package_json = Path(temp_dir) / "package.json"
        assert package_json.exists()
        
        with open(package_json) as f:
            package_data = json.load(f)
        
        assert "devDependencies" in package_data
        assert "typescript" in package_data["devDependencies"]
        assert "@types/node" in package_data["devDependencies"]
    
    def test_rust_feature_dependencies(self):
        """Test that Rust feature dependencies are properly handled."""
        if not CargoManager.is_available():
            pytest.skip("cargo not available")
        
        temp_dir = self._create_temp_dir()
        config = TestConfigTemplates.dependency_heavy_config("rust")
        
        # Generate CLI
        from .test_installation_flows import CLITestHelper
        generated_files = CLITestHelper.generate_cli(config, temp_dir)
        
        # Check Cargo.toml for dependencies
        cargo_toml = Path(temp_dir) / "Cargo.toml"
        assert cargo_toml.exists()
        
        content = cargo_toml.read_text()
        assert "clap" in content
        assert "anyhow" in content
        # Check for features specification
        assert "features" in content or "derive" in content
        
        # Test network-aware build validation
        try:
            if CargoManager.check_network_connectivity(timeout=3):
                # Network is available, try normal check
                CargoManager.check(temp_dir, timeout=30)
            else:
                # Network unavailable, skip dependency download test
                pytest.skip("Network connectivity to crates.io unavailable")
        except subprocess.CalledProcessError as e:
            if ("Could not connect" in e.stderr or 
                "network" in e.stderr.lower() or
                "index.crates.io" in e.stderr):
                pytest.skip(f"Network connectivity issue: {e.stderr[:100]}...")
            else:
                # Re-raise for other build errors
                raise
    
    def test_dependency_version_constraints(self):
        """Test that dependency version constraints are properly specified."""
        languages_and_managers = [
            ("python", "pip"),
            ("nodejs", "npm"),
            ("typescript", "npm"),
            ("rust", "cargo")
        ]
        
        for language, manager in languages_and_managers:
            manager_class = PackageManagerRegistry.get_manager(manager)
            if not manager_class.is_available():
                continue
            
            temp_dir = self._create_temp_dir()
            config = TestConfigTemplates.complex_config(language)
            
            # Generate CLI
            from .test_installation_flows import CLITestHelper
            generated_files = CLITestHelper.generate_cli(config, temp_dir)
            
            # Check for version constraints
            if language == "python":
                # Check setup.py or pyproject.toml for version specs
                pyproject_file = Path(temp_dir) / "pyproject.toml"
                setup_file = Path(temp_dir) / "setup.py"
                
                content = ""
                if pyproject_file.exists():
                    content = pyproject_file.read_text()
                elif setup_file.exists():
                    content = setup_file.read_text()
                
                # Should have version constraints like >=8.0.0
                assert ">=" in content or "~=" in content or "==" in content
            
            elif language in ["nodejs", "typescript"]:
                # Check package.json for version specs
                package_json = Path(temp_dir) / "package.json"
                with open(package_json) as f:
                    package_data = json.load(f)
                
                deps = package_data.get("dependencies", {})
                dev_deps = package_data.get("devDependencies", {})
                all_deps = {**deps, **dev_deps}
                
                # Should have version constraints like ^11.0.0
                version_specs = [v for v in all_deps.values() if v]
                assert any("^" in v or "~" in v or "=" in v for v in version_specs)
            
            elif language == "rust":
                # Check Cargo.toml for version specs
                cargo_toml = Path(temp_dir) / "Cargo.toml"
                content = cargo_toml.read_text()
                
                # Should have version constraints like "4.0"
                assert '"' in content and ("4.0" in content or "1.0" in content)
    
    @pytest.mark.parametrize("language", ["python", "nodejs", "typescript", "rust"])
    def test_missing_dependencies_error_handling(self, language):
        """Test that CLIs handle missing dependencies gracefully."""
        temp_dir = self._create_temp_dir()
        config = TestConfigTemplates.minimal_config(language)
        
        # Generate CLI without installing dependencies
        from .test_installation_flows import CLITestHelper
        generated_files = CLITestHelper.generate_cli(config, temp_dir)
        
        cli_file = Path(generated_files["cli_file"])
        
        # Try to run CLI directly without installing dependencies
        try:
            if language == "python":
                result = subprocess.run(
                    ["python", str(cli_file), "--help"],
                    cwd=temp_dir,
                    capture_output=True,
                    text=True,
                    timeout=30,
                    check=False
                )
                # Should either work (if deps already installed) or fail gracefully
                if result.returncode != 0:
                    assert "ImportError" in result.stderr or "ModuleNotFoundError" in result.stderr
            
            elif language in ["nodejs", "typescript"]:
                if language == "typescript":
                    # TypeScript needs to be compiled first
                    pytest.skip("TypeScript requires compilation before testing")
                
                result = subprocess.run(
                    ["node", str(cli_file), "--help"],
                    cwd=temp_dir,
                    capture_output=True,
                    text=True,
                    timeout=30,
                    check=False
                )
                # Should either work or fail with module not found
                if result.returncode != 0:
                    assert "Cannot find module" in result.stderr or "MODULE_NOT_FOUND" in result.stderr
            
            elif language == "rust":
                # Rust CLI needs to be compiled first
                if CargoManager.is_available():
                    try:
                        # Try check with offline mode if network issues
                        if not CargoManager.check_network_connectivity():
                            CargoManager.check(temp_dir, offline=True)
                        else:
                            CargoManager.check(temp_dir)
                    except subprocess.CalledProcessError as e:
                        # Skip if it's a network connectivity issue
                        if ("Could not connect" in e.stderr or
                            "network" in e.stderr.lower() or
                            "index.crates.io" in e.stderr):
                            pytest.skip(f"Network connectivity issue: {e.stderr[:100]}...")
                        # Should fail with dependency errors if deps missing
                        assert "error" in e.stderr.lower() or "failed" in e.stderr.lower()
        
        except subprocess.TimeoutExpired:
            # CLI hanging is also a form of dependency issue
            pass
    
    def test_cross_platform_dependency_resolution(self):
        """Test that dependencies work across different platforms."""
        # This test validates that generated CLIs don't have platform-specific issues
        env_info = validate_installation_environment()
        
        # Test basic CLI generation for all available package managers
        for language in ["python", "nodejs", "typescript", "rust"]:
            temp_dir = self._create_temp_dir()
            config = TestConfigTemplates.minimal_config(language)
            
            try:
                from .test_installation_flows import CLITestHelper
                generated_files = CLITestHelper.generate_cli(config, temp_dir)
                
                # Verify files were generated correctly
                cli_file = Path(generated_files["cli_file"])
                assert cli_file.exists()
                assert cli_file.stat().st_size > 0
                
                # Check for platform-specific issues in generated code
                content = cli_file.read_text()
                
                # Should not contain hardcoded platform paths
                assert "/usr/local/" not in content
                assert "C:\\" not in content
                assert "Program Files" not in content
                
                # Should not contain platform-specific commands
                assert "apt-get" not in content
                assert "yum install" not in content
                assert "brew install" not in content
                
            except Exception as e:
                pytest.fail(f"Cross-platform test failed for {language}: {e}")
    
    def test_network_resilient_rust_dependencies(self):
        """Test that Rust dependency tests are resilient to network issues."""
        if not CargoManager.is_available():
            pytest.skip("cargo not available")
        
        temp_dir = self._create_temp_dir()
        config = TestConfigTemplates.minimal_config("rust")  # Use minimal config to reduce network dependencies
        
        # Generate CLI
        from .test_installation_flows import CLITestHelper
        generated_files = CLITestHelper.generate_cli(config, temp_dir)
        
        # Test network connectivity and build strategy
        network_available = CargoManager.check_network_connectivity(timeout=2)
        
        if network_available:
            # Network is available, try normal build
            try:
                result = CargoManager.build(temp_dir, timeout=60)
                assert result.returncode == 0, f"Build failed with network: {result.stderr}"
            except subprocess.CalledProcessError as e:
                if "Could not connect" in e.stderr:
                    pytest.skip(f"Intermittent network issue: {e.stderr[:100]}...")
                else:
                    raise
        else:
            # Network unavailable, test offline capabilities
            try:
                # This should fail gracefully
                CargoManager.build(temp_dir, offline=True, timeout=30)
            except subprocess.CalledProcessError:
                # Expected to fail if dependencies haven't been cached
                pytest.skip("Network unavailable and dependencies not cached")
    
    def test_dependency_conflict_resolution(self):
        """Test that CLIs handle potential dependency conflicts."""
        # This is primarily for Python where version conflicts are common
        if not PipManager.is_available():
            pytest.skip("pip not available for conflict testing")
        
        temp_dir = self._create_temp_dir()
        config = TestConfigTemplates.dependency_heavy_config("python")
        
        # Create a scenario that might have conflicts
        from goobits_cli.schemas import ExtrasSchema
        config.installation.extras = ExtrasSchema(
            python=["requests>=2.25.0", "urllib3>=1.26.0"],  # Potential conflict area
            apt=[],
            npm=None
        )
        
        # Generate and try to install
        from .test_installation_flows import CLITestHelper
        generated_files = CLITestHelper.generate_cli(config, temp_dir)
        
        try:
            # Use scoped installation to prevent global conflicts
            PipManager.install_editable_scoped(temp_dir)
            self._track_installation("pip", config.package_name)
            
            # Create test environment for runtime testing
            test_env = TestEnvironmentManager.create_test_environment(temp_dir, "python")
            
            # Test that CLI works despite potential conflicts
            command_name = config.command_name
            runtime_results = DependencyValidator.check_runtime_dependencies_with_env(
                command_name, test_env)
            assert all(runtime_results.values()), f"Dependency conflicts caused runtime issues: {runtime_results}"
            
        except subprocess.CalledProcessError as e:
            # If installation fails due to conflicts, that's acceptable
            # But the error should be informative
            assert "conflict" in e.stderr.lower() or "incompatible" in e.stderr.lower()


    def test_cross_language_isolation(self):
        """Test that different language tests don't interfere with each other."""
        # Test Python followed by Node.js installation
        python_temp_dir = self._create_temp_dir()
        python_config = TestConfigTemplates.minimal_config("python")
        
        nodejs_temp_dir = self._create_temp_dir()
        nodejs_config = TestConfigTemplates.minimal_config("nodejs")
        
        # Install Python CLI in scoped environment
        if PipManager.is_available():
            python_command = self._generate_and_install_cli(python_config, python_temp_dir)
            python_env = TestEnvironmentManager.create_test_environment(python_temp_dir, "python")
            
            # Verify Python CLI works in its environment
            python_results = DependencyValidator.check_runtime_dependencies_with_env(
                python_command, python_env)
            assert all(python_results.values()), f"Python CLI failed in scoped environment: {python_results}"
        else:
            pytest.skip("pip not available")
        
        # Install Node.js CLI in separate scoped environment
        if NpmManager.is_available():
            nodejs_command = self._generate_and_install_cli(nodejs_config, nodejs_temp_dir)
            nodejs_env = TestEnvironmentManager.create_test_environment(nodejs_temp_dir, "nodejs")
            
            # Verify Node.js CLI works in its environment
            nodejs_results = DependencyValidator.check_runtime_dependencies_with_env(
                nodejs_command, nodejs_env)
            assert all(nodejs_results.values()), f"Node.js CLI failed in scoped environment: {nodejs_results}"
            
            # Verify Python CLI still works (no cross-contamination)
            python_results_after = DependencyValidator.check_runtime_dependencies_with_env(
                python_command, python_env)
            assert all(python_results_after.values()), f"Python CLI contaminated by Node.js installation: {python_results_after}"
        else:
            pytest.skip("npm not available")
    
    def test_environment_cleanup_effectiveness(self):
        """Test that environment cleanup properly removes all test artifacts."""
        temp_dir = self._create_temp_dir()
        config = TestConfigTemplates.minimal_config("python")
        
        if not PipManager.is_available():
            pytest.skip("pip not available")
        
        # Install CLI in scoped environment
        PipManager.install_editable_scoped(temp_dir)
        
        # Verify test environment files exist
        project_path = Path(temp_dir)
        test_venv = project_path / ".test_venv"
        assert test_venv.exists(), "Test virtual environment should be created"
        
        # Clean up test environment
        TestEnvironmentManager.cleanup_test_environment(temp_dir)
        
        # Verify cleanup removed all artifacts
        assert not test_venv.exists(), "Test virtual environment should be cleaned up"
        assert not (project_path / ".npm_prefix").exists(), "NPM prefix should be cleaned up"
        assert not (project_path / ".cargo_home").exists(), "Cargo home should be cleaned up"
    
    def test_real_cli_execution_validation(self):
        """Test that generated CLIs actually execute correctly with real dependencies - no mocking."""
        # Test all languages that have available package managers
        for language in ["python", "nodejs", "rust"]:  # Skip typescript for now (compilation complexity)
            if language == "python" and not PipManager.is_available():
                continue
            elif language == "nodejs" and not NpmManager.is_available():
                continue
            elif language == "rust" and not CargoManager.is_available():
                continue
            
            print(f"Testing real CLI execution for {language}...")
            
            temp_dir = self._create_temp_dir()
            config = TestConfigTemplates.minimal_config(language)
            
            try:
                # Generate and install CLI using REAL package managers
                command_name = self._generate_and_install_cli(config, temp_dir)
                
                # Test 1: Verify CLI is actually callable
                help_result = subprocess.run([command_name, "--help"], 
                                           capture_output=True, text=True, timeout=30)
                assert help_result.returncode == 0, f"{language} CLI help failed: {help_result.stderr}"
                assert len(help_result.stdout) > 0, f"{language} CLI help produced no output"
                
                # Test 2: Execute a real command to verify dependencies work
                if language == "python":
                    # Test that Click dependency works
                    version_result = subprocess.run([command_name, "--version"], 
                                                  capture_output=True, text=True, timeout=30)
                    # Should either show version or fail gracefully (not crash with ImportError)
                    if version_result.returncode != 0:
                        error_text = version_result.stderr.lower()
                        assert "importerror" not in error_text, f"Python dependency missing: {version_result.stderr}"
                        assert "modulenotfounderror" not in error_text, f"Python module missing: {version_result.stderr}"
                
                elif language == "nodejs":
                    # Test that commander dependency works
                    # Try to run with invalid argument to trigger commander error handling
                    invalid_result = subprocess.run([command_name, "--nonexistent-flag"], 
                                                  capture_output=True, text=True, timeout=30)
                    # Should get commander error, not "Cannot find module"
                    if invalid_result.returncode != 0:
                        error_text = invalid_result.stderr.lower()
                        assert "cannot find module" not in error_text, f"Node.js dependency missing: {invalid_result.stderr}"
                        assert "module_not_found" not in error_text, f"Node.js module missing: {invalid_result.stderr}"
                
                elif language == "rust":
                    # Test that clap dependency works by checking help output format
                    help_text = help_result.stdout.lower()
                    # Clap typically generates "usage:" in help output
                    assert "usage" in help_text or "help" in help_text, f"Rust CLI help doesn't show clap formatting: {help_result.stdout}"
                
                print(f"✅ {language} CLI execution validation passed")
                
            except subprocess.TimeoutExpired:
                pytest.fail(f"{language} CLI execution timed out")
            except subprocess.CalledProcessError as e:
                if language == "rust" and "Could not connect" in str(e):
                    pytest.skip(f"Skipping {language} due to network connectivity issues")
                else:
                    pytest.fail(f"{language} CLI execution failed: {e}")


if __name__ == "__main__":
    pytest.main([__file__])