"""Integration tests for end-to-end installation workflows.

This module tests complete installation workflows from CLI generation 
to successful deployment and functionality testing.
"""

import json
import os
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import pytest

from .package_manager_utils import (
    PackageManagerRegistry, validate_installation_environment, 
    cleanup_global_packages
)
from .test_configs import TestConfigTemplates, TestScenarioRunner
from .test_installation_workflows import CLITestHelper


class IntegrationTestRunner:
    """Runner for comprehensive integration tests."""
    
    def __init__(self):
        self.temp_dirs = []
        self.installed_packages = []
        self.test_results = {}
    
    def cleanup(self):
        """Clean up all test artifacts."""
        # Clean up temporary directories
        for temp_dir in self.temp_dirs:
            if Path(temp_dir).exists():
                import shutil
                shutil.rmtree(temp_dir, ignore_errors=True)
        
        # Clean up installed packages
        cleanup_results = cleanup_global_packages(self.installed_packages)
        
        return cleanup_results
    
    def create_temp_dir(self) -> str:
        """Create and track temporary directory."""
        temp_dir = tempfile.mkdtemp(prefix="goobits_integration_test_")
        self.temp_dirs.append(temp_dir)
        return temp_dir
    
    def track_installation(self, manager: str, package_name: str):
        """Track package installation for cleanup."""
        self.installed_packages.append({
            "manager": manager,
            "name": package_name
        })
    
    def run_full_workflow_test(self, language: str, scenario: str) -> Dict[str, any]:
        """Run complete workflow test for language and scenario."""
        test_id = f"{language}_{scenario}"
        self.test_results[test_id] = {
            "language": language,
            "scenario": scenario,
            "started": time.time(),
            "phases": {},
            "success": False,
            "error": None
        }
        
        try:
            # Phase 1: Configuration and Generation
            temp_dir = self.create_temp_dir()
            config = TestConfigTemplates.get_template_for_scenario(scenario, language)
            
            self.test_results[test_id]["phases"]["generation"] = {
                "started": time.time(),
                "config_created": True
            }
            
            # Generate CLI files
            generated_files = CLITestHelper.generate_cli(config, temp_dir)
            
            self.test_results[test_id]["phases"]["generation"].update({
                "files_generated": len(generated_files),
                "cli_file": generated_files.get("cli_file"),
                "completed": time.time()
            })
            
            # Phase 2: Installation
            install_phase = {
                "started": time.time(),
                "package_managers_tested": []
            }
            
            if language == "python":
                install_success = self._test_python_installation(config, temp_dir)
                install_phase["package_managers_tested"].append("pip")
            elif language == "nodejs":
                install_success = self._test_nodejs_installation(config, temp_dir)
                install_phase["package_managers_tested"].append("npm")
            elif language == "typescript":
                install_success = self._test_typescript_installation(config, temp_dir)
                install_phase["package_managers_tested"].append("npm")
            elif language == "rust":
                install_success = self._test_rust_installation(config, temp_dir)
                install_phase["package_managers_tested"].append("cargo")
            else:
                raise ValueError(f"Unsupported language: {language}")
            
            install_phase.update({
                "installation_successful": install_success,
                "completed": time.time()
            })
            
            self.test_results[test_id]["phases"]["installation"] = install_phase
            
            if install_success:
                self.track_installation(
                    self._get_primary_package_manager(language),
                    config.package_name
                )
            
            # Phase 3: Functionality Testing
            if install_success:
                functionality_results = self._test_cli_functionality(config)
                self.test_results[test_id]["phases"]["functionality"] = functionality_results
                
                # Phase 4: Cleanup Testing
                cleanup_results = self._test_cleanup_process(config, language)
                self.test_results[test_id]["phases"]["cleanup"] = cleanup_results
                
                self.test_results[test_id]["success"] = (
                    functionality_results.get("all_commands_work", False) and
                    cleanup_results.get("uninstall_successful", False)
                )
            else:
                self.test_results[test_id]["success"] = False
                self.test_results[test_id]["error"] = "Installation failed"
            
        except Exception as e:
            self.test_results[test_id]["error"] = str(e)
            self.test_results[test_id]["success"] = False
        
        finally:
            self.test_results[test_id]["completed"] = time.time()
            self.test_results[test_id]["duration"] = (
                self.test_results[test_id]["completed"] - 
                self.test_results[test_id]["started"]
            )
        
        return self.test_results[test_id]
    
    def _get_primary_package_manager(self, language: str) -> str:
        """Get the primary package manager for a language."""
        mapping = {
            "python": "pip",
            "nodejs": "npm",
            "typescript": "npm",
            "rust": "cargo"
        }
        return mapping.get(language, "unknown")
    
    def _test_python_installation(self, config, temp_dir: str) -> bool:
        """Test Python CLI installation."""
        try:
            from .package_manager_utils import PipManager
            
            if not PipManager.is_available():
                print(f"❌ PipManager not available")
                return False
            
            # Install in editable mode
            result = PipManager.install_editable(temp_dir)
            if result.returncode != 0:
                print(f"❌ Pip installation failed with return code {result.returncode}")
                print(f"Stdout: {result.stdout}")
                print(f"Stderr: {result.stderr}")
            return result.returncode == 0
        except Exception as e:
            print(f"❌ Python installation exception: {e}")
            return False
    
    def _test_nodejs_installation(self, config, temp_dir: str) -> bool:
        """Test Node.js CLI installation."""
        try:
            from .package_manager_utils import NpmManager
            
            if not NpmManager.is_available():
                print(f"❌ NpmManager not available")
                return False
            
            # Install dependencies and link globally
            deps_result = NpmManager.install_dependencies(temp_dir)
            if deps_result.returncode != 0:
                print(f"❌ npm install failed with return code {deps_result.returncode}")
                print(f"Stdout: {deps_result.stdout}")
                print(f"Stderr: {deps_result.stderr}")
                return False
            
            # Make CLI executable
            cli_file = Path(temp_dir) / "cli.js"
            if cli_file.exists():
                content = cli_file.read_text()
                if not content.startswith("#!"):
                    content = "#!/usr/bin/env node\n" + content
                    cli_file.write_text(content)
                cli_file.chmod(0o755)
            
            result = NpmManager.link_global(temp_dir)
            if result.returncode != 0:
                print(f"❌ npm link failed with return code {result.returncode}")
                print(f"Stdout: {result.stdout}")
                print(f"Stderr: {result.stderr}")
            return result.returncode == 0
        except Exception as e:
            print(f"❌ Node.js installation exception: {e}")
            return False
    
    def _test_typescript_installation(self, config, temp_dir: str) -> bool:
        """Test TypeScript CLI installation."""
        try:
            from .package_manager_utils import NpmManager
            
            if not NpmManager.is_available():
                print(f"❌ NpmManager not available")
                return False
            
            # Install dependencies
            deps_result = NpmManager.install_dependencies(temp_dir)
            if deps_result.returncode != 0:
                print(f"❌ npm install failed with return code {deps_result.returncode}")
                print(f"Stdout: {deps_result.stdout}")
                print(f"Stderr: {deps_result.stderr}")
                return False
            
            # Build TypeScript
            build_result = NpmManager.run_script("build", temp_dir)
            if build_result.returncode != 0:
                print(f"❌ npm run build failed with return code {build_result.returncode}")
                print(f"Stdout: {build_result.stdout}")
                print(f"Stderr: {build_result.stderr}")
                return False
            
            # Make compiled CLI executable
            compiled_cli = Path(temp_dir) / "dist" / "cli.js"
            if compiled_cli.exists():
                content = compiled_cli.read_text()
                if not content.startswith("#!"):
                    content = "#!/usr/bin/env node\n" + content
                    compiled_cli.write_text(content)
                compiled_cli.chmod(0o755)
            
            # Link globally
            result = NpmManager.link_global(temp_dir)
            if result.returncode != 0:
                print(f"❌ npm link failed with return code {result.returncode}")
                print(f"Stdout: {result.stdout}")
                print(f"Stderr: {result.stderr}")
            return result.returncode == 0
        except Exception as e:
            print(f"❌ TypeScript installation exception: {e}")
            return False
    
    def _test_rust_installation(self, config, temp_dir: str) -> bool:
        """Test Rust CLI installation."""
        try:
            from .package_manager_utils import CargoManager
            
            if not CargoManager.is_available():
                print(f"❌ CargoManager not available")
                return False
            
            # Build and install
            build_result = CargoManager.build(temp_dir)
            if build_result.returncode != 0:
                print(f"❌ cargo build failed with return code {build_result.returncode}")
                print(f"Stdout: {build_result.stdout}")
                print(f"Stderr: {build_result.stderr}")
                return False
                
            result = CargoManager.install_from_path(temp_dir)
            if result.returncode != 0:
                print(f"❌ cargo install failed with return code {result.returncode}")
                print(f"Stdout: {result.stdout}")
                print(f"Stderr: {result.stderr}")
            return result.returncode == 0
        except Exception as e:
            print(f"❌ Rust installation exception: {e}")
            return False
    
    def _get_cli_command_path(self, command_name: str, language: str) -> str:
        """Get the full path to the CLI command based on language and installation method."""
        if language == "python":
            # For Python, the CLI is installed in the virtual environment's bin directory
            import sys
            import os
            venv_bin = os.path.dirname(sys.executable)
            cli_path = os.path.join(venv_bin, command_name)
            if os.path.exists(cli_path):
                return cli_path
        
        # For other languages or if not found in venv, try system PATH
        return command_name
    
    def _test_cli_functionality(self, config) -> Dict[str, any]:
        """Test CLI functionality after installation."""
        results = {
            "started": time.time(),
            "commands_tested": [],
            "commands_passed": [],
            "commands_failed": [],
            "all_commands_work": False
        }
        
        command_name = self._get_cli_command_path(config.command_name, config.language)
        test_commands = ["--help", "--version"]
        
        # Add specific commands from config
        if hasattr(config.cli, 'commands'):
            for cmd_name in config.cli.commands.keys():
                test_commands.append(cmd_name)
        
        for cmd in test_commands:
            results["commands_tested"].append(cmd)
            
            try:
                # Test basic command execution
                if cmd.startswith("--"):
                    # Global options
                    result = subprocess.run(
                        [command_name, cmd],
                        capture_output=True,
                        text=True,
                        timeout=30,
                        check=False
                    )
                else:
                    # Subcommands - test with help
                    result = subprocess.run(
                        [command_name, cmd, "--help"],
                        capture_output=True,
                        text=True,
                        timeout=30,
                        check=False
                    )
                
                if result.returncode == 0 and len(result.stdout) > 0:
                    results["commands_passed"].append(cmd)
                else:
                    results["commands_failed"].append({
                        "command": cmd,
                        "returncode": result.returncode,
                        "stderr": result.stderr[:200] if result.stderr else "No stderr",
                        "stdout": result.stdout[:200] if result.stdout else "No stdout"
                    })
            
            except Exception as e:
                results["commands_failed"].append({
                    "command": cmd,
                    "error": str(e)
                })
        
        results["all_commands_work"] = len(results["commands_failed"]) == 0
        results["success_rate"] = len(results["commands_passed"]) / len(results["commands_tested"])
        results["completed"] = time.time()
        
        return results
    
    def _test_cleanup_process(self, config, language: str) -> Dict[str, any]:
        """Test package cleanup/uninstallation."""
        results = {
            "started": time.time(),
            "uninstall_attempted": False,
            "uninstall_successful": False
        }
        
        try:
            package_name = config.package_name
            manager_name = self._get_primary_package_manager(language)
            manager_class = PackageManagerRegistry.get_manager(manager_name)
            
            if manager_name == "pip":
                result = manager_class.uninstall(package_name)
            elif manager_name == "npm":
                result = manager_class.uninstall_global(package_name)
            elif manager_name == "cargo":
                result = manager_class.uninstall(package_name)
            
            results["uninstall_attempted"] = True
            results["uninstall_successful"] = result.returncode == 0
            
            # Verify CLI is no longer available
            try:
                subprocess.run(
                    [config.command_name, "--help"],
                    capture_output=True,
                    timeout=10,
                    check=True
                )
                # If this succeeds, uninstall didn't work properly
                results["uninstall_successful"] = False
            except (subprocess.CalledProcessError, FileNotFoundError):
                # This is expected after successful uninstall
                pass
            
        except Exception as e:
            results["error"] = str(e)
        
        results["completed"] = time.time()
        return results


class TestIntegrationWorkflows:
    """Integration test class for complete workflows."""
    
    @pytest.fixture(autouse=True)
    def setup_method(self):
        """Set up integration test environment."""
        self.runner = IntegrationTestRunner()
        self.env_info = validate_installation_environment()
    
    def teardown_method(self):
        """Clean up after integration tests."""
        self.runner.cleanup()
    
    @pytest.mark.parametrize("test_case", TestScenarioRunner.get_critical_test_matrix())
    def test_critical_installation_workflows(self, test_case):
        """Test critical installation workflows for all languages and scenarios."""
        language = test_case["language"]
        scenario = test_case["scenario"]
        
        # Skip if package manager not available
        primary_manager = self.runner._get_primary_package_manager(language)
        manager_class = PackageManagerRegistry.get_manager(primary_manager)
        
        if not manager_class.is_available():
            pytest.skip(f"Package manager {primary_manager} not available for {language}")
        
        # Run the full workflow test
        result = self.runner.run_full_workflow_test(language, scenario)
        
        # Assert success
        assert result["success"], f"Integration test failed for {language}/{scenario}: {result.get('error', 'Unknown error')}"
        
        # Verify all phases completed
        assert "generation" in result["phases"]
        assert "installation" in result["phases"]
        assert "functionality" in result["phases"]
        assert "cleanup" in result["phases"]
        
        # Verify generation phase
        gen_phase = result["phases"]["generation"]
        assert gen_phase["config_created"]
        assert gen_phase["files_generated"] > 0
        
        # Verify installation phase
        install_phase = result["phases"]["installation"]
        assert install_phase["installation_successful"]
        assert len(install_phase["package_managers_tested"]) > 0
        
        # Verify functionality phase
        func_phase = result["phases"]["functionality"]
        assert func_phase["all_commands_work"]
        assert func_phase["success_rate"] > 0.8  # At least 80% of commands work
        
        # Verify cleanup phase
        cleanup_phase = result["phases"]["cleanup"]
        assert cleanup_phase["uninstall_attempted"]
        assert cleanup_phase["uninstall_successful"]
    
    def test_parallel_installation_isolation(self):
        """Test that multiple CLIs can be installed simultaneously without conflicts."""
        languages = ["python", "nodejs"]  # Test subset for parallel installation
        
        results = {}
        temp_dirs = []
        
        try:
            # Generate multiple CLIs simultaneously
            for i, language in enumerate(languages):
                temp_dir = self.runner.create_temp_dir()
                temp_dirs.append(temp_dir)
                
                config = TestConfigTemplates.minimal_config(
                    language, 
                    package_name=f"test-parallel-{language}-{i}"
                )
                
                # Generate CLI
                generated_files = CLITestHelper.generate_cli(config, temp_dir)
                
                # Install CLI
                primary_manager = self.runner._get_primary_package_manager(language)
                manager_class = PackageManagerRegistry.get_manager(primary_manager)
                
                if manager_class.is_available():
                    if language == "python":
                        install_result = self.runner._test_python_installation(config, temp_dir)
                    elif language == "nodejs":
                        install_result = self.runner._test_nodejs_installation(config, temp_dir)
                    
                    results[language] = {
                        "config": config,
                        "install_success": install_result
                    }
                    
                    if install_result:
                        self.runner.track_installation(primary_manager, config.package_name)
            
            # Verify all CLIs work independently
            for language, result in results.items():
                if result["install_success"]:
                    func_results = self.runner._test_cli_functionality(result["config"])
                    assert func_results["all_commands_work"], f"Parallel installation affected {language} CLI functionality"
        
        finally:
            # Cleanup
            self.runner.cleanup()
    
    def test_installation_environment_validation(self):
        """Test that installation environment is properly validated."""
        env_info = validate_installation_environment()
        
        # Verify structure of environment info
        assert "python" in env_info
        assert "nodejs" in env_info
        assert "rust" in env_info
        assert "available_managers" in env_info
        
        # Verify Python environment info
        python_info = env_info["python"]
        assert "version" in python_info
        assert "executable" in python_info
        assert "pip_available" in python_info
        
        # Verify available managers mapping
        available_managers = env_info["available_managers"]
        for manager in ["pip", "pipx", "npm", "yarn", "cargo"]:
            assert manager in available_managers
            assert isinstance(available_managers[manager], bool)
    
    def test_cross_language_consistency(self):
        """Test that all languages generate consistent CLI behavior."""
        test_commands = ["--help", "--version"]
        results = {}
        
        for language in ["python", "nodejs", "typescript", "rust"]:
            primary_manager = self.runner._get_primary_package_manager(language)
            manager_class = PackageManagerRegistry.get_manager(primary_manager)
            
            if not manager_class.is_available():
                continue
            
            # Generate and install CLI
            temp_dir = self.runner.create_temp_dir()
            config = TestConfigTemplates.minimal_config(language)
            
            generated_files = CLITestHelper.generate_cli(config, temp_dir)
            
            # Install CLI
            if language == "python":
                install_success = self.runner._test_python_installation(config, temp_dir)
            elif language == "nodejs":
                install_success = self.runner._test_nodejs_installation(config, temp_dir)
            elif language == "typescript":
                install_success = self.runner._test_typescript_installation(config, temp_dir)
            elif language == "rust":
                install_success = self.runner._test_rust_installation(config, temp_dir)
            
            if install_success:
                self.runner.track_installation(primary_manager, config.package_name)
                
                # Test commands and capture output
                command_outputs = {}
                for cmd in test_commands:
                    try:
                        result = subprocess.run(
                            [config.command_name, cmd],
                            capture_output=True,
                            text=True,
                            timeout=30,
                            check=True
                        )
                        command_outputs[cmd] = {
                            "returncode": result.returncode,
                            "stdout_length": len(result.stdout),
                            "has_output": len(result.stdout) > 0
                        }
                    except Exception as e:
                        command_outputs[cmd] = {"error": str(e)}
                
                results[language] = command_outputs
        
        # Verify consistency across languages
        if len(results) > 1:
            # All languages should support --help
            for language, outputs in results.items():
                assert "--help" in outputs, f"{language} CLI doesn't support --help"
                assert outputs["--help"].get("has_output", False), f"{language} CLI --help produces no output"
                
                # Version support is optional but should be consistent if present
                if "--version" in outputs and "error" not in outputs["--version"]:
                    assert outputs["--version"].get("has_output", False), f"{language} CLI --version produces no output"
    
    def test_installation_performance_benchmarks(self):
        """Test installation performance across languages."""
        performance_results = {}
        
        for language in ["python", "nodejs", "typescript", "rust"]:
            primary_manager = self.runner._get_primary_package_manager(language)
            manager_class = PackageManagerRegistry.get_manager(primary_manager)
            
            if not manager_class.is_available():
                continue
            
            # Measure installation time
            start_time = time.time()
            
            temp_dir = self.runner.create_temp_dir()
            config = TestConfigTemplates.minimal_config(language)
            
            # Generation time
            gen_start = time.time()
            generated_files = CLITestHelper.generate_cli(config, temp_dir)
            gen_time = time.time() - gen_start
            
            # Installation time
            install_start = time.time()
            if language == "python":
                install_success = self.runner._test_python_installation(config, temp_dir)
            elif language == "nodejs":
                install_success = self.runner._test_nodejs_installation(config, temp_dir)
            elif language == "typescript":
                install_success = self.runner._test_typescript_installation(config, temp_dir)
            elif language == "rust":
                install_success = self.runner._test_rust_installation(config, temp_dir)
            
            install_time = time.time() - install_start
            total_time = time.time() - start_time
            
            performance_results[language] = {
                "generation_time": gen_time,
                "installation_time": install_time,
                "total_time": total_time,
                "install_success": install_success
            }
            
            if install_success:
                self.runner.track_installation(primary_manager, config.package_name)
        
        # Verify reasonable performance
        for language, perf in performance_results.items():
            if perf["install_success"]:
                # Generation should be fast
                assert perf["generation_time"] < 10, f"{language} generation took too long: {perf['generation_time']}s"
                
                # Total time should be reasonable (except Rust which compiles)
                max_time = 300 if language == "rust" else 60  # 5 minutes for Rust, 1 minute for others
                assert perf["total_time"] < max_time, f"{language} installation took too long: {perf['total_time']}s"


if __name__ == "__main__":
    pytest.main([__file__])