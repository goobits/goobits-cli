"""Infrastructure validation tests for installation test suite.

This module validates that the test infrastructure itself is working correctly
before running the actual installation tests.
"""

import tempfile
from pathlib import Path

import pytest

from .package_manager_utils import (
    PackageManagerRegistry,
    validate_installation_environment,
    PipManager,
    NpmManager,
)
from .test_configs import TestConfigTemplates, TestScenarioRunner


class TestInfrastructureValidation:
    """Test that the test infrastructure itself is working."""

    def test_environment_validation(self):
        """Test that environment validation works."""
        env_info = validate_installation_environment()

        # Check required structure
        assert "python" in env_info
        assert "nodejs" in env_info
        assert "rust" in env_info
        assert "available_managers" in env_info

        # Check Python info
        python_info = env_info["python"]
        assert "version" in python_info
        assert "executable" in python_info
        assert "pip_available" in python_info
        assert "pipx_available" in python_info

        # Check available managers
        available_managers = env_info["available_managers"]
        required_managers = ["pip", "pipx", "npm", "yarn", "cargo"]
        for manager in required_managers:
            assert manager in available_managers
            assert isinstance(available_managers[manager], bool)

    def test_package_manager_registry(self):
        """Test package manager registry functionality."""
        # Test getting managers
        pip_manager = PackageManagerRegistry.get_manager("pip")
        assert pip_manager == PipManager

        npm_manager = PackageManagerRegistry.get_manager("npm")
        assert npm_manager == NpmManager

        # Test invalid manager
        with pytest.raises(ValueError):
            PackageManagerRegistry.get_manager("invalid_manager")

        # Test availability check
        available = PackageManagerRegistry.get_available_managers()
        assert isinstance(available, dict)
        assert len(available) > 0

        # Test requirements check
        is_valid, missing = PackageManagerRegistry.check_requirements(["pip"])
        assert isinstance(is_valid, bool)
        assert isinstance(missing, list)

    def test_config_template_generation(self):
        """Test that configuration templates generate correctly."""
        languages = ["python", "nodejs", "typescript", "rust"]
        scenarios = ["minimal", "complex", "dependency_heavy", "edge_case"]

        for language in languages:
            for scenario in scenarios:
                config = TestConfigTemplates.get_template_for_scenario(
                    scenario, language
                )

                # Verify basic structure
                assert hasattr(config, "package_name")
                assert hasattr(config, "command_name")
                assert hasattr(config, "language")
                assert hasattr(config, "cli")

                # Verify language is correct
                assert config.language == language

                # Verify CLI structure
                assert hasattr(config.cli, "name")
                assert hasattr(config.cli, "commands")
                assert len(config.cli.commands) > 0

    def test_scenario_runner_matrices(self):
        """Test that test scenario matrices are generated correctly."""
        # Test full matrix
        full_matrix = TestScenarioRunner.get_test_matrix()
        assert isinstance(full_matrix, list)
        assert len(full_matrix) > 0

        for test_case in full_matrix:
            assert "language" in test_case
            assert "scenario" in test_case
            assert "test_id" in test_case

        # Test critical matrix
        critical_matrix = TestScenarioRunner.get_critical_test_matrix()
        assert isinstance(critical_matrix, list)
        assert len(critical_matrix) <= len(full_matrix)

        # Test language-specific matrix
        python_matrix = TestScenarioRunner.get_language_specific_matrix("python")
        assert isinstance(python_matrix, list)

        for test_case in python_matrix:
            assert test_case["language"] == "python"

    def test_cli_test_helper_file_generation(self):
        """Test that CLI test helper generates files correctly."""
        from tests.e2e.test_installation_flows import CLITestHelper

        with tempfile.TemporaryDirectory() as temp_dir:
            # Test Python CLI generation
            config = TestConfigTemplates.minimal_config("python", "test-infra-python")
            generated_files = CLITestHelper.generate_cli(config, temp_dir)

            assert "cli_file" in generated_files
            assert "setup_file" in generated_files
            assert "pyproject_file" in generated_files

            # Verify files exist
            cli_file = Path(generated_files["cli_file"])
            setup_file = Path(generated_files["setup_file"])
            pyproject_file = Path(generated_files["pyproject_file"])

            assert cli_file.exists()
            assert setup_file.exists()
            assert pyproject_file.exists()

            # Verify files have content
            assert cli_file.stat().st_size > 0
            assert setup_file.stat().st_size > 0
            assert pyproject_file.stat().st_size > 0

            # Verify content contains expected elements
            setup_content = setup_file.read_text()
            assert config.package_name in setup_content
            assert config.command_name in setup_content

    @pytest.mark.skipif(not PipManager.is_available(), reason="pip not available")
    def test_pip_manager_functionality(self):
        """Test pip manager basic functionality."""
        # Test listing installed packages
        installed = PipManager.list_installed()
        assert isinstance(installed, list)

        # Should have some packages installed
        assert len(installed) > 0

    @pytest.mark.skipif(not NpmManager.is_available(), reason="npm not available")
    def test_npm_manager_functionality(self):
        """Test npm manager basic functionality."""
        # Test listing global packages
        global_packages = NpmManager.list_global()
        assert isinstance(global_packages, list)

    def test_all_template_scenarios_generate_valid_configs(self):
        """Test that all template scenarios generate valid configurations."""
        templates = TestConfigTemplates.get_all_templates()
        languages = ["python", "nodejs", "typescript", "rust"]

        for scenario_name, template_func in templates.items():
            for language in languages:
                try:
                    config = template_func(language, f"test-{scenario_name}-{language}")

                    # Basic validation
                    assert config.package_name == f"test-{scenario_name}-{language}"
                    assert config.language == language
                    assert len(config.cli.commands) > 0

                    # Ensure package name is valid
                    assert (
                        "-" in config.package_name
                        or "_" in config.package_name
                        or config.package_name.isalnum()
                    )

                    # Ensure command name is valid
                    assert (
                        config.command_name.replace("-", "").replace("_", "").isalnum()
                    )

                except Exception as e:
                    pytest.fail(f"Template {scenario_name} failed for {language}: {e}")

    def test_package_manager_error_handling(self):
        """Test that package managers handle errors gracefully."""
        # Test with non-existent directory
        with tempfile.TemporaryDirectory() as temp_dir:
            non_existent = Path(temp_dir) / "non_existent"

            if PipManager.is_available():
                try:
                    PipManager.install_editable(str(non_existent))
                except Exception:
                    pass  # Expected to fail

            if NpmManager.is_available():
                try:
                    NpmManager.install_dependencies(str(non_existent))
                except Exception:
                    pass  # Expected to fail

    def test_cleanup_utilities(self):
        """Test cleanup utility functions."""
        from .package_manager_utils import cleanup_global_packages

        # Test with empty package list
        results = cleanup_global_packages([])
        assert isinstance(results, list)
        assert len(results) == 0

        # Test with invalid package info
        results = cleanup_global_packages([{"invalid": "data"}])
        assert isinstance(results, list)

    def test_test_case_generation_consistency(self):
        """Test that test case generation is consistent."""
        # Generate the same test case multiple times
        config1 = TestConfigTemplates.minimal_config("python", "consistent-test")
        config2 = TestConfigTemplates.minimal_config("python", "consistent-test")

        # Should generate identical configurations
        assert config1.package_name == config2.package_name
        assert config1.command_name == config2.command_name
        assert config1.language == config2.language
        assert config1.version == config2.version

        # CLI structure should be identical
        assert config1.cli.name == config2.cli.name
        assert len(config1.cli.commands) == len(config2.cli.commands)

        for cmd_name in config1.cli.commands:
            assert cmd_name in config2.cli.commands


if __name__ == "__main__":
    pytest.main([__file__])
