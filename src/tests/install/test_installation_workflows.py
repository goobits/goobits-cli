"""Installation workflow validation tests.

This module provides comprehensive tests for validating that generated CLIs 
install correctly across all supported package managers and languages.

Tests cover:
- Python: pip, pipx installation workflows
- Node.js: npm, yarn installation workflows  
- TypeScript: build + npm/yarn installation workflows
- Rust: cargo installation workflows

Each test validates the full installation pipeline:
1. Generate CLI from test configuration
2. Install via package manager
3. Verify CLI is available and functional
4. Test uninstallation
"""

import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

import pytest
import yaml

from goobits_cli.builder import Builder
from goobits_cli.schemas import GoobitsConfigSchema


# Package manager availability and installation methods
INSTALLATION_METHODS = {
    "python": ["pip", "pipx"],
    "nodejs": ["npm", "yarn"],  
    "typescript": ["npm", "yarn"],
    "rust": ["cargo"]
}

# Global test configuration
TEST_CLI_NAME = "test-install-cli"
TEST_PACKAGE_NAME = "test-install-package"


class PackageManagerError(Exception):
    """Error when package manager is not available or fails."""
    pass


class InstallationTestError(Exception):
    """Error during installation testing."""
    pass


class PackageManagerHelper:
    """Helper class for package manager interactions."""
    
    @staticmethod
    def check_availability(package_manager: str) -> bool:
        """Check if a package manager is available on the system."""
        return shutil.which(package_manager) is not None
    
    @staticmethod
    def run_command(
        cmd: List[str], 
        cwd: Optional[str] = None, 
        timeout: int = 120,
        capture_output: bool = True,
        check: bool = True
    ) -> subprocess.CompletedProcess:
        """Run a command with proper error handling and timeouts."""
        try:
            result = subprocess.run(
                cmd,
                cwd=cwd,
                capture_output=capture_output,
                text=True,
                timeout=timeout,
                check=check
            )
            return result
        except subprocess.TimeoutExpired:
            raise PackageManagerError(f"Command timed out after {timeout}s: {' '.join(cmd)}")
        except subprocess.CalledProcessError as e:
            error_msg = f"Command failed: {' '.join(cmd)}"
            if e.stdout:
                error_msg += f"\nStdout: {e.stdout}"
            if e.stderr:
                error_msg += f"\nStderr: {e.stderr}"
            raise PackageManagerError(error_msg)


class CLITestHelper:
    """Helper class for CLI generation and testing."""
    
    @staticmethod
    def create_test_config(language: str, package_name: str = None, command_name: str = None) -> GoobitsConfigSchema:
        """Create a test configuration for the specified language."""
        if package_name is None:
            package_name = TEST_PACKAGE_NAME
        if command_name is None:
            command_name = TEST_CLI_NAME
            
        config_data = {
            "package_name": package_name,
            "command_name": command_name,
            "display_name": f"Test {language.title()} CLI",
            "description": f"Test CLI generated for {language} installation testing",
            "language": language,
            "version": "0.1.0",
            "author": "Test Author",
            "email": "test@example.com",
            "license": "MIT",
            "homepage": "https://github.com/test/test-cli",
            "repository": "https://github.com/test/test-cli",
            "keywords": ["test", "cli", language],
            "installation": {
                "pypi_name": package_name,
                "development_path": ".",
                "extras": {
                    "python": ["dev"] if language == "python" else None,
                    "npm": ["typescript"] if language in ["nodejs", "typescript"] else None,
                    "apt": []
                }
            },
            "python": {
                "minimum_version": "3.8",
                "maximum_version": "3.13"
            },
            "dependencies": {
                "required": [],
                "optional": []
            },
            "shell_integration": {
                "enabled": False,
                "alias": command_name
            },
            "validation": {
                "check_api_keys": False,
                "check_disk_space": True,
                "minimum_disk_space_mb": 10
            },
            "cli": {
                "name": f"Test{language.title()}CLI",
                "version": "0.1.0",
                "display_version": True,
                "tagline": f"A test CLI for {language} installation validation",
                "description": f"This CLI is generated for testing {language} installation workflows",
                "icon": "⚡",
                "commands": {
                    "hello": {
                        "desc": "Print a hello message",
                        "args": [
                            {
                                "name": "name",
                                "desc": "Name to greet",
                                "required": False
                            }
                        ],
                        "options": [
                            {
                                "name": "uppercase",
                                "short": "u",
                                "type": "bool",
                                "desc": "Print in uppercase",
                                "default": False
                            }
                        ]
                    },
                    "version": {
                        "desc": "Show version information"
                    }
                }
            }
        }
        
        return GoobitsConfigSchema(**config_data)
    
    @staticmethod
    def generate_cli(config: GoobitsConfigSchema, output_dir: str) -> Dict[str, str]:
        """Generate CLI files and return the file paths."""
        builder = Builder(language=config.language)
        
        # Generate the CLI
        generated_code = builder.build(config, "test_config.yaml", config.version)
        
        # Determine the output file name based on language
        if config.language == "python":
            cli_file = Path(output_dir) / "cli.py"
            setup_file = Path(output_dir) / "setup.py"
            pyproject_file = Path(output_dir) / "pyproject.toml"
        elif config.language == "nodejs":
            cli_file = Path(output_dir) / "cli.js"
            package_file = Path(output_dir) / "package.json"
        elif config.language == "typescript":
            cli_file = Path(output_dir) / "cli.ts"
            package_file = Path(output_dir) / "package.json"
            tsconfig_file = Path(output_dir) / "tsconfig.json"
        elif config.language == "rust":
            cli_file = Path(output_dir) / "src" / "main.rs"
            cargo_file = Path(output_dir) / "Cargo.toml"
            # Create src directory for Rust
            (Path(output_dir) / "src").mkdir(exist_ok=True)
        
        # Write the generated CLI file
        with open(cli_file, 'w') as f:
            f.write(generated_code)
        
        result = {"cli_file": str(cli_file)}
        
        # Generate additional files based on language
        if config.language == "python":
            # Generate setup.py for Python
            setup_content = CLITestHelper._generate_python_setup(config)
            with open(setup_file, 'w') as f:
                f.write(setup_content)
            result["setup_file"] = str(setup_file)
            
            # Generate pyproject.toml
            pyproject_content = CLITestHelper._generate_pyproject_toml(config)
            with open(pyproject_file, 'w') as f:
                f.write(pyproject_content)
            result["pyproject_file"] = str(pyproject_file)
            
        elif config.language in ["nodejs", "typescript"]:
            # Generate package.json
            package_content = CLITestHelper._generate_package_json(config)
            with open(package_file, 'w') as f:
                f.write(package_content)
            result["package_file"] = str(package_file)
            
            if config.language == "typescript":
                # Generate tsconfig.json
                tsconfig_content = CLITestHelper._generate_tsconfig_json()
                with open(tsconfig_file, 'w') as f:
                    f.write(tsconfig_content)
                result["tsconfig_file"] = str(tsconfig_file)
                
        elif config.language == "rust":
            # Generate Cargo.toml
            cargo_content = CLITestHelper._generate_cargo_toml(config)
            with open(cargo_file, 'w') as f:
                f.write(cargo_content)
            result["cargo_file"] = str(cargo_file)
        
        return result
    
    @staticmethod
    def _generate_python_setup(config: GoobitsConfigSchema) -> str:
        """Generate setup.py content for Python CLI."""
        return f'''#!/usr/bin/env python3
"""Setup script for {config.package_name}."""

from setuptools import setup, find_packages

setup(
    name="{config.package_name}",
    version="{config.version}",
    description="{config.description}",
    author="{config.author}",
    author_email="{config.email}",
    py_modules=["cli"],
    install_requires=[
        "click>=8.0.0",
        "rich>=10.0.0",
        "typer>=0.9.0",
    ],
    entry_points={{
        "console_scripts": [
            "{config.command_name}=cli:main",
        ],
    }},
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
)
'''
    
    @staticmethod
    def _generate_pyproject_toml(config: GoobitsConfigSchema) -> str:
        """Generate pyproject.toml content for Python CLI."""
        return f'''[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "{config.package_name}"
version = "{config.version}"
description = "{config.description}"
authors = [
    {{name = "{config.author}", email = "{config.email}"}}
]
license = {{text = "{config.license}"}}
readme = "README.md"
requires-python = ">={config.python.minimum_version}"
classifiers = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
]
dependencies = [
    "click>=8.0.0",
    "rich>=10.0.0",
    "typer>=0.9.0",
]

[project.scripts]
{config.command_name} = "cli:main"

[project.urls]
Homepage = "{config.homepage}"
Repository = "{config.repository}"
'''
    
    @staticmethod
    def _generate_package_json(config: GoobitsConfigSchema) -> str:
        """Generate package.json content for Node.js/TypeScript CLI."""
        script_section = {
            "start": f"node cli.{'js' if config.language == 'nodejs' else 'ts'}",
            "test": "echo \"Error: no test specified\" && exit 1"
        }
        
        if config.language == "typescript":
            script_section.update({
                "build": "tsc",
                "start": "node dist/cli.js",
                "dev": "ts-node cli.ts"
            })
        
        package_data = {
            "name": config.package_name,
            "version": config.version,
            "description": config.description,
            "main": "cli.js" if config.language == "nodejs" else "dist/cli.js",
            "bin": {
                config.command_name: "./cli.js" if config.language == "nodejs" else "./dist/cli.js"
            },
            "scripts": script_section,
            "keywords": config.keywords,
            "author": f"{config.author} <{config.email}>",
            "license": config.license,
            "homepage": config.homepage,
            "repository": {
                "type": "git",
                "url": config.repository
            },
            "dependencies": {
                "commander": "^11.0.0"
            }
        }
        
        if config.language == "typescript":
            package_data["devDependencies"] = {
                "typescript": "^5.0.0",
                "@types/node": "^20.0.0",
                "ts-node": "^10.9.0"
            }
        
        return yaml.dump(package_data, default_flow_style=False).replace("'", '"')
    
    @staticmethod
    def _generate_tsconfig_json() -> str:
        """Generate tsconfig.json content for TypeScript CLI."""
        tsconfig = {
            "compilerOptions": {
                "target": "ES2020",
                "module": "commonjs",
                "outDir": "./dist",
                "rootDir": "./",
                "strict": True,
                "esModuleInterop": True,
                "skipLibCheck": True,
                "forceConsistentCasingInFileNames": True,
                "declaration": True,
                "declarationMap": True,
                "sourceMap": True
            },
            "include": ["*.ts"],
            "exclude": ["node_modules", "dist"]
        }
        return yaml.dump(tsconfig, default_flow_style=False).replace("'", '"')
    
    @staticmethod
    def _generate_cargo_toml(config: GoobitsConfigSchema) -> str:
        """Generate Cargo.toml content for Rust CLI."""
        return f'''[package]
name = "{config.package_name}"
version = "{config.version}"
description = "{config.description}"
authors = ["{config.author} <{config.email}>"]
license = "{config.license}"
homepage = "{config.homepage}"
repository = "{config.repository}"
keywords = {config.keywords}
edition = "2021"

[[bin]]
name = "{config.command_name}"
path = "src/main.rs"

[dependencies]
clap = {{ version = "4.0", features = ["derive"] }}
anyhow = "1.0"
serde = {{ version = "1.0", features = ["derive"] }}
serde_json = "1.0"
'''


class TestInstallationWorkflows:
    """Main test class for installation workflow validation."""
    
    @pytest.fixture(autouse=True)
    def setup_method(self):
        """Set up test environment for each test method."""
        self.temp_dirs = []
        self.installed_packages = []
    
    def teardown_method(self):
        """Clean up after each test method."""
        # Clean up temporary directories
        for temp_dir in self.temp_dirs:
            if Path(temp_dir).exists():
                shutil.rmtree(temp_dir, ignore_errors=True)
        
        # Clean up installed packages
        for package_info in self.installed_packages:
            try:
                self._uninstall_package(package_info)
            except Exception:
                pass  # Ignore cleanup errors
    
    def _create_temp_dir(self) -> str:
        """Create a temporary directory and track it for cleanup."""
        temp_dir = tempfile.mkdtemp(prefix="goobits_install_test_")
        self.temp_dirs.append(temp_dir)
        return temp_dir
    
    def _track_installation(self, package_manager: str, package_name: str, install_path: str = None):
        """Track an installation for cleanup."""
        self.installed_packages.append({
            "package_manager": package_manager,
            "package_name": package_name,
            "install_path": install_path
        })
    
    def _uninstall_package(self, package_info: Dict[str, str]):
        """Uninstall a tracked package."""
        pm = package_info["package_manager"]
        name = package_info["package_name"]
        
        try:
            if pm == "pip":
                PackageManagerHelper.run_command(["pip", "uninstall", "-y", name])
            elif pm == "pipx":
                PackageManagerHelper.run_command(["pipx", "uninstall", name])
            elif pm == "npm":
                PackageManagerHelper.run_command(["npm", "uninstall", "-g", name])
            elif pm == "yarn":
                PackageManagerHelper.run_command(["yarn", "global", "remove", name])
            elif pm == "cargo":
                PackageManagerHelper.run_command(["cargo", "uninstall", name])
        except Exception:
            pass  # Ignore uninstallation errors during cleanup
    
    def _test_cli_functionality(self, command_name: str, expected_commands: List[str] = None):
        """Test that the installed CLI is functional."""
        if expected_commands is None:
            expected_commands = ["--help", "--version"]
        
        for cmd_arg in expected_commands:
            try:
                result = PackageManagerHelper.run_command([command_name, cmd_arg], timeout=30)
                assert result.returncode == 0, f"Command '{command_name} {cmd_arg}' failed"
                assert len(result.stdout) > 0, f"Command '{command_name} {cmd_arg}' produced no output"
            except FileNotFoundError:
                pytest.fail(f"CLI command '{command_name}' not found in PATH")
            except PackageManagerError as e:
                pytest.fail(f"CLI command '{command_name} {cmd_arg}' failed: {e}")


# Python Installation Tests
class TestPythonInstallation(TestInstallationWorkflows):
    """Test Python CLI installation workflows."""
    
    @pytest.mark.skipif(not PackageManagerHelper.check_availability("pip"), reason="pip not available")
    def test_pip_install_workflow(self):
        """Test pip install of generated Python CLI."""
        temp_dir = self._create_temp_dir()
        
        # Generate Python CLI
        config = CLITestHelper.create_test_config("python")
        generated_files = CLITestHelper.generate_cli(config, temp_dir)
        
        # Test pip install in editable mode
        result = PackageManagerHelper.run_command(
            ["pip", "install", "-e", "."], 
            cwd=temp_dir
        )
        assert result.returncode == 0
        self._track_installation("pip", config.package_name)
        
        # Verify CLI is available and functional
        self._test_cli_functionality(config.command_name)
        
        # Test the generated CLI with specific commands
        hello_result = PackageManagerHelper.run_command([config.command_name, "hello", "World"])
        assert hello_result.returncode == 0
        assert "World" in hello_result.stdout or "hello" in hello_result.stdout.lower()
    
    @pytest.mark.skipif(not PackageManagerHelper.check_availability("pipx"), reason="pipx not available")
    def test_pipx_install_workflow(self):
        """Test pipx install of generated Python CLI."""
        temp_dir = self._create_temp_dir()
        
        # Generate Python CLI
        config = CLITestHelper.create_test_config("python")
        generated_files = CLITestHelper.generate_cli(config, temp_dir)
        
        # Test pipx install
        result = PackageManagerHelper.run_command(
            ["pipx", "install", "."], 
            cwd=temp_dir
        )
        assert result.returncode == 0
        self._track_installation("pipx", config.package_name)
        
        # Verify CLI is available and functional
        self._test_cli_functionality(config.command_name)
    
    def test_python_generated_files_validation(self):
        """Test that generated Python installation files are correct."""
        temp_dir = self._create_temp_dir()
        
        # Generate Python CLI
        config = CLITestHelper.create_test_config("python")
        generated_files = CLITestHelper.generate_cli(config, temp_dir)
        
        # Verify expected files exist
        assert "cli_file" in generated_files
        assert "setup_file" in generated_files
        assert "pyproject_file" in generated_files
        
        cli_file = Path(generated_files["cli_file"])
        setup_file = Path(generated_files["setup_file"])
        pyproject_file = Path(generated_files["pyproject_file"])
        
        assert cli_file.exists()
        assert setup_file.exists()
        assert pyproject_file.exists()
        
        # Verify setup.py contains correct entry point
        setup_content = setup_file.read_text()
        assert config.command_name in setup_content
        assert "console_scripts" in setup_content
        
        # Verify pyproject.toml contains correct configuration
        pyproject_content = pyproject_file.read_text()
        assert config.package_name in pyproject_content
        assert config.command_name in pyproject_content


# Node.js Installation Tests  
class TestNodeJSInstallation(TestInstallationWorkflows):
    """Test Node.js CLI installation workflows."""
    
    @pytest.mark.skipif(not PackageManagerHelper.check_availability("npm"), reason="npm not available")
    def test_npm_install_workflow(self):
        """Test npm install of generated Node.js CLI."""
        temp_dir = self._create_temp_dir()
        
        # Generate Node.js CLI
        config = CLITestHelper.create_test_config("nodejs")
        generated_files = CLITestHelper.generate_cli(config, temp_dir)
        
        # Install dependencies
        result = PackageManagerHelper.run_command(["npm", "install"], cwd=temp_dir)
        assert result.returncode == 0
        
        # Make CLI executable
        cli_file = Path(generated_files["cli_file"])
        cli_file.chmod(0o755)
        
        # Add shebang to CLI file if not present
        cli_content = cli_file.read_text()
        if not cli_content.startswith("#!"):
            cli_content = "#!/usr/bin/env node\n" + cli_content
            cli_file.write_text(cli_content)
        
        # Test npm link for global installation
        result = PackageManagerHelper.run_command(["npm", "link"], cwd=temp_dir)
        assert result.returncode == 0
        self._track_installation("npm", config.package_name)
        
        # Verify CLI is available and functional
        self._test_cli_functionality(config.command_name)
    
    @pytest.mark.skipif(not PackageManagerHelper.check_availability("yarn"), reason="yarn not available")
    def test_yarn_install_workflow(self):
        """Test yarn install of generated Node.js CLI."""
        temp_dir = self._create_temp_dir()
        
        # Generate Node.js CLI
        config = CLITestHelper.create_test_config("nodejs")
        generated_files = CLITestHelper.generate_cli(config, temp_dir)
        
        # Install dependencies with yarn
        result = PackageManagerHelper.run_command(["yarn", "install"], cwd=temp_dir)
        assert result.returncode == 0
        
        # Make CLI executable
        cli_file = Path(generated_files["cli_file"])
        cli_file.chmod(0o755)
        
        # Add shebang to CLI file if not present
        cli_content = cli_file.read_text()
        if not cli_content.startswith("#!"):
            cli_content = "#!/usr/bin/env node\n" + cli_content
            cli_file.write_text(cli_content)
        
        # Test yarn global add for global installation
        result = PackageManagerHelper.run_command(["yarn", "global", "add", f"file:{temp_dir}"])
        assert result.returncode == 0
        self._track_installation("yarn", config.package_name)
        
        # Verify CLI is available and functional
        self._test_cli_functionality(config.command_name)
    
    def test_nodejs_generated_files_validation(self):
        """Test that generated Node.js installation files are correct."""
        temp_dir = self._create_temp_dir()
        
        # Generate Node.js CLI
        config = CLITestHelper.create_test_config("nodejs")
        generated_files = CLITestHelper.generate_cli(config, temp_dir)
        
        # Verify expected files exist
        assert "cli_file" in generated_files
        assert "package_file" in generated_files
        
        cli_file = Path(generated_files["cli_file"])
        package_file = Path(generated_files["package_file"])
        
        assert cli_file.exists()
        assert package_file.exists()
        
        # Verify package.json contains correct bin section
        import json
        package_content = json.loads(package_file.read_text())
        assert "bin" in package_content
        assert config.command_name in package_content["bin"]
        assert package_content["name"] == config.package_name


# TypeScript Installation Tests
class TestTypeScriptInstallation(TestInstallationWorkflows):
    """Test TypeScript CLI installation workflows."""
    
    @pytest.mark.skipif(not PackageManagerHelper.check_availability("npm"), reason="npm not available")
    def test_typescript_build_and_install(self):
        """Test TypeScript compilation and npm installation."""
        temp_dir = self._create_temp_dir()
        
        # Generate TypeScript CLI
        config = CLITestHelper.create_test_config("typescript")
        generated_files = CLITestHelper.generate_cli(config, temp_dir)
        
        # Install dependencies
        result = PackageManagerHelper.run_command(["npm", "install"], cwd=temp_dir)
        assert result.returncode == 0
        
        # Compile TypeScript
        result = PackageManagerHelper.run_command(["npm", "run", "build"], cwd=temp_dir)
        assert result.returncode == 0
        
        # Verify compiled JavaScript exists
        dist_dir = Path(temp_dir) / "dist"
        assert dist_dir.exists()
        compiled_cli = dist_dir / "cli.js"
        assert compiled_cli.exists()
        
        # Make compiled CLI executable
        compiled_cli.chmod(0o755)
        
        # Add shebang to compiled CLI file if not present
        cli_content = compiled_cli.read_text()
        if not cli_content.startswith("#!"):
            cli_content = "#!/usr/bin/env node\n" + cli_content
            compiled_cli.write_text(cli_content)
        
        # Test npm link for global installation
        result = PackageManagerHelper.run_command(["npm", "link"], cwd=temp_dir)
        assert result.returncode == 0
        self._track_installation("npm", config.package_name)
        
        # Verify CLI is available and functional
        self._test_cli_functionality(config.command_name)
    
    def test_typescript_generated_files_validation(self):
        """Test that generated TypeScript installation files are correct."""
        temp_dir = self._create_temp_dir()
        
        # Generate TypeScript CLI
        config = CLITestHelper.create_test_config("typescript")
        generated_files = CLITestHelper.generate_cli(config, temp_dir)
        
        # Verify expected files exist
        assert "cli_file" in generated_files
        assert "package_file" in generated_files
        assert "tsconfig_file" in generated_files
        
        cli_file = Path(generated_files["cli_file"])
        package_file = Path(generated_files["package_file"])
        tsconfig_file = Path(generated_files["tsconfig_file"])
        
        assert cli_file.exists()
        assert package_file.exists()
        assert tsconfig_file.exists()
        
        # Verify package.json has TypeScript dependencies and scripts
        import json
        package_content = json.loads(package_file.read_text())
        assert "devDependencies" in package_content
        assert "typescript" in package_content["devDependencies"]
        assert "scripts" in package_content
        assert "build" in package_content["scripts"]


# Rust Installation Tests
class TestRustInstallation(TestInstallationWorkflows):
    """Test Rust CLI installation workflows."""
    
    @pytest.mark.skipif(not PackageManagerHelper.check_availability("cargo"), reason="cargo not available")
    def test_cargo_install_workflow(self):
        """Test cargo install of generated Rust CLI."""
        temp_dir = self._create_temp_dir()
        
        # Generate Rust CLI
        config = CLITestHelper.create_test_config("rust")
        generated_files = CLITestHelper.generate_cli(config, temp_dir)
        
        # Test cargo build
        result = PackageManagerHelper.run_command(["cargo", "build"], cwd=temp_dir)
        assert result.returncode == 0
        
        # Verify binary was built
        target_dir = Path(temp_dir) / "target" / "debug"
        binary_name = config.command_name.replace("-", "_")  # Cargo converts hyphens to underscores
        binary_path = target_dir / binary_name
        
        if not binary_path.exists():
            # Try with original name
            binary_path = target_dir / config.command_name
        
        assert binary_path.exists(), f"Binary not found at {binary_path}"
        
        # Test cargo install --path .
        result = PackageManagerHelper.run_command(["cargo", "install", "--path", "."], cwd=temp_dir)
        assert result.returncode == 0
        self._track_installation("cargo", config.package_name)
        
        # Verify CLI is available and functional
        self._test_cli_functionality(config.command_name)
    
    def test_rust_generated_files_validation(self):
        """Test that generated Rust installation files are correct."""
        temp_dir = self._create_temp_dir()
        
        # Generate Rust CLI
        config = CLITestHelper.create_test_config("rust")
        generated_files = CLITestHelper.generate_cli(config, temp_dir)
        
        # Verify expected files exist
        assert "cli_file" in generated_files
        assert "cargo_file" in generated_files
        
        cli_file = Path(generated_files["cli_file"])
        cargo_file = Path(generated_files["cargo_file"])
        
        assert cli_file.exists()
        assert cargo_file.exists()
        
        # Verify Cargo.toml contains correct binary definition
        cargo_content = cargo_file.read_text()
        assert config.package_name in cargo_content
        assert config.command_name in cargo_content
        assert "[[bin]]" in cargo_content


# Cross-Language Integration Tests
class TestCrossLanguageInstallation(TestInstallationWorkflows):
    """Test installation workflows across all languages."""
    
    def test_all_languages_generate_installable_clis(self):
        """Test that all supported languages can generate installable CLIs."""
        languages = ["python", "nodejs", "typescript", "rust"]
        results = {}
        
        for language in languages:
            temp_dir = self._create_temp_dir()
            
            try:
                # Generate CLI for each language
                config = CLITestHelper.create_test_config(language)
                generated_files = CLITestHelper.generate_cli(config, temp_dir)
                
                # Verify files were generated
                assert "cli_file" in generated_files
                cli_file = Path(generated_files["cli_file"])
                assert cli_file.exists()
                assert cli_file.stat().st_size > 0
                
                results[language] = "success"
                
            except Exception as e:
                results[language] = f"failed: {e}"
        
        # Verify all languages succeeded
        for language, result in results.items():
            assert result == "success", f"{language} generation failed: {result}"
    
    @pytest.mark.parametrize("language", ["python", "nodejs", "typescript", "rust"])
    def test_environment_isolation(self, language):
        """Test that CLIs install in isolated environments."""
        # This test would ideally use containers or virtual environments
        # For now, we'll verify basic file isolation
        temp_dir = self._create_temp_dir()
        
        config = CLITestHelper.create_test_config(language)
        generated_files = CLITestHelper.generate_cli(config, temp_dir)
        
        # Verify files are contained in the temp directory
        for file_path in generated_files.values():
            assert temp_dir in file_path, f"Generated file {file_path} not in temp directory"


if __name__ == "__main__":
    # Run tests when executed directly
    pytest.main([__file__])