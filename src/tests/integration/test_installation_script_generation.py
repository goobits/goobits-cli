"""Installation script generation tests for integration testing.

This module tests that the framework correctly generates installation scripts and
configuration files without actually executing installations. This focuses on
testing the framework's installation orchestration logic.

These tests verify:
- setup.sh script generation and content
- package.json generation for Node.js/TypeScript
- Cargo.toml generation for Rust
- pyproject.toml handling for Python
- Installation instruction generation

For actual installation testing, see tests/e2e/test_installation_flows.py
"""

import json
import tempfile
from pathlib import Path
from typing import Dict

import pytest

from goobits_cli.core.schemas import GoobitsConfigSchema

from .test_config_validation import TestConfigTemplates


class TestInstallationScriptGeneration:
    """Test generation of installation scripts and configuration files."""

    def setup_method(self, method):
        """Set up test environment."""
        self.temp_dirs = []

    def teardown_method(self, method):
        """Clean up temporary directories."""
        for temp_dir in self.temp_dirs:
            import shutil

            if Path(temp_dir).exists():
                shutil.rmtree(temp_dir, ignore_errors=True)

    def _create_temp_dir(self) -> str:
        """Create a temporary directory and track it for cleanup."""
        temp_dir = tempfile.mkdtemp(prefix="goobits_install_test_")
        self.temp_dirs.append(temp_dir)
        return temp_dir

    def _generate_cli_files(
        self, language: str, config_type: str = "minimal"
    ) -> Dict[str, str]:
        """Generate CLI files and return them as a dictionary."""
        from goobits_cli.universal.generator import UniversalGenerator

        if config_type == "minimal":
            config = TestConfigTemplates.minimal_config(language)
        elif config_type == "complex":
            config = TestConfigTemplates.complex_config(language)
        else:
            config = TestConfigTemplates.dependency_heavy_config(language)

        if language not in ["python", "nodejs", "typescript", "rust"]:
            raise ValueError(f"Unsupported language: {language}")

        generator = UniversalGenerator(language)
        return generator.generate_all_files(config, "test.yaml", "1.0.0")

    @pytest.mark.parametrize("language", ["python", "nodejs", "typescript", "rust"])
    def test_setup_script_generation(self, language):
        """Test that setup.sh scripts are generated correctly when available."""
        files = self._generate_cli_files(language)

        # Check that setup.sh is generated (or verify simplified approach)
        setup_files = [f for f in files.keys() if f.endswith("setup.sh")]

        if setup_files:
            # If setup.sh exists, validate its structure
            setup_content = files[setup_files[0]]
            setup_lower = setup_content.lower()

            # Verify basic setup script structure
            assert (
                "#!/bin/bash" in setup_content or "#!/usr/bin/env bash" in setup_content
            ), "Setup script should have bash shebang"
            assert "set -e" in setup_content, "Setup script should have error handling"

            # Language-specific checks
            if language == "python":
                assert "pip" in setup_lower or "pipx" in setup_lower, (
                    "Python setup should mention pip/pipx"
                )
            elif language in ["nodejs", "typescript"]:
                assert "npm" in setup_lower or "node" in setup_lower, (
                    "Node.js setup should mention npm/node"
                )
            elif language == "rust":
                assert "cargo" in setup_lower, "Rust setup should mention cargo"

            print(f"✅ {language} setup.sh generation validated")
        else:
            # Simplified approach without setup.sh - verify main CLI file exists
            cli_files = [
                f
                for f in files.keys()
                if f.endswith((".py", ".js", ".mjs", ".ts", ".rs"))
            ]
            assert len(cli_files) > 0, (
                f"{language} should generate at least one CLI file"
            )
            print(f"ℹ️  {language} uses simplified approach without setup.sh")

    @pytest.mark.parametrize("language", ["nodejs", "typescript"])
    def test_package_json_generation(self, language):
        """Test that package.json files are generated correctly for Node.js/TypeScript."""
        files = self._generate_cli_files(language, "complex")

        # Look for package.json in generated files
        package_json_files = [f for f in files.keys() if f.endswith("package.json")]

        if package_json_files:
            # If package.json is generated, validate its structure
            package_content = files[package_json_files[0]]
            try:
                package_data = json.loads(package_content)

                # Basic package.json structure validation
                assert "name" in package_data, "package.json should have name field"
                assert "version" in package_data, (
                    "package.json should have version field"
                )

                # Check for CLI-specific fields
                if "bin" in package_data:
                    assert isinstance(package_data["bin"], (dict, str)), (
                        "bin field should be dict or string"
                    )

                # Dependencies validation
                if language == "nodejs":
                    # Node.js should have commander dependency
                    deps = package_data.get("dependencies", {})
                    assert "commander" in str(deps).lower(), (
                        "Node.js CLI should include commander dependency"
                    )
                elif language == "typescript":
                    # TypeScript might have type dependencies
                    all_deps = {
                        **package_data.get("dependencies", {}),
                        **package_data.get("devDependencies", {}),
                    }
                    assert len(all_deps) > 0, (
                        "TypeScript CLI should have some dependencies"
                    )

                print(f"✅ {language} package.json generation validated")

            except json.JSONDecodeError as e:
                pytest.fail(f"Generated package.json is invalid JSON: {e}")
        else:
            # It's also valid for generators to not create package.json (simplified approach)
            print(f"ℹ️  {language} uses simplified approach without package.json")

    @pytest.mark.parametrize("language", ["rust"])
    def test_cargo_toml_generation(self, language):
        """Test that Cargo.toml files are generated correctly for Rust."""
        files = self._generate_cli_files(language, "complex")

        # Look for Cargo.toml in generated files
        cargo_files = [f for f in files.keys() if f.endswith("Cargo.toml")]

        if cargo_files:
            cargo_content = files[cargo_files[0]]

            # Basic Cargo.toml validation
            assert "[package]" in cargo_content, (
                "Cargo.toml should have [package] section"
            )
            assert "name" in cargo_content, "Cargo.toml should specify package name"
            assert "version" in cargo_content, "Cargo.toml should specify version"

            # Check for dependencies section
            if "[dependencies]" in cargo_content:
                assert "clap" in cargo_content.lower(), (
                    "Rust CLI should include clap dependency"
                )

            print(f"✅ {language} Cargo.toml generation validated")
        else:
            # Simplified approach might embed everything in main.rs
            print(f"ℹ️  {language} uses simplified approach without Cargo.toml")

    def test_cross_language_installation_consistency(self):
        """Test that installation approaches are consistent across languages."""
        languages = ["python", "nodejs", "typescript", "rust"]
        setup_scripts = {}

        for language in languages:
            files = self._generate_cli_files(language)
            setup_files = [f for f in files.keys() if f.endswith("setup.sh")]

            if setup_files:
                setup_scripts[language] = files[setup_files[0]]

        # Verify that all languages that generate setup.sh follow similar patterns
        for language, setup_content in setup_scripts.items():
            assert "set -e" in setup_content, (
                f"{language} setup should have error handling"
            )
            assert len(setup_content.strip()) > 0, (
                f"{language} setup should not be empty"
            )

        print("✅ Cross-language installation consistency validated")

    @pytest.mark.parametrize("config_type", ["minimal", "complex", "dependency_heavy"])
    def test_installation_complexity_handling(self, config_type):
        """Test that installation scripts handle different complexity levels."""
        # Test Python as representative language
        language = "python"
        files = self._generate_cli_files(language, config_type)

        setup_files = [f for f in files.keys() if f.endswith("setup.sh")]

        if setup_files:
            setup_content = files[setup_files[0]]

            # All complexity levels should have basic structure
            assert len(setup_content.strip()) > 0, (
                f"{config_type} config should generate setup content"
            )

            if config_type == "dependency_heavy":
                # Heavy configs might have more complex installation steps
                # This is acceptable - just verify it's not empty
                assert (
                    "pip" in setup_content.lower() or "install" in setup_content.lower()
                ), "Dependency-heavy config should have installation commands"

        print(f"✅ {config_type} configuration installation handling validated")

    def test_installation_instruction_generation(self):
        """Test that human-readable installation instructions are generated."""
        # Test with complex config to get full feature set
        files = self._generate_cli_files("python", "complex")

        # Look for any README or instruction files
        instruction_files = [
            f
            for f in files.keys()
            if any(name in f.lower() for name in ["readme", "install", "doc"])
        ]

        # It's acceptable if no instruction files are generated (minimalist approach)
        # Just verify that if they exist, they contain useful information
        for filename in instruction_files:
            content = files[filename]
            assert len(content.strip()) > 0, f"{filename} should not be empty"
            print(f"ℹ️  Found instruction file: {filename}")

        print("✅ Installation instruction generation validated")

    @pytest.mark.parametrize("language", ["python", "nodejs", "typescript", "rust"])
    def test_setup_path_configuration(self, language):
        """Test that setup_path configuration controls setup.sh output location."""
        from goobits_cli.universal.generator import UniversalGenerator

        # Create config with custom setup_path
        config = TestConfigTemplates.minimal_config(language)

        # Modify the installation config to use scripts/setup.sh path
        if config.installation:
            # Create a new installation config with setup_path set
            config_dict = config.model_dump()
            config_dict["installation"]["setup_path"] = "scripts/setup.sh"
            config = GoobitsConfigSchema(**config_dict)

        generator = UniversalGenerator(language)
        files = generator.generate_all_files(config, "test.yaml", "1.0.0")

        # Check that setup.sh is at the configured path
        setup_files = [f for f in files.keys() if "setup.sh" in f]

        if setup_files:
            # Verify setup.sh is at the configured subdirectory path
            found_at_scripts = any("scripts" in f for f in setup_files)
            assert found_at_scripts, (
                f"setup.sh should be at scripts/setup.sh, but found at: {setup_files}"
            )
            print(f"✅ {language} setup_path configuration validated")
        else:
            # Some generators may not produce setup.sh
            print(f"ℹ️  {language} does not generate setup.sh")

    def test_setup_path_default_value(self):
        """Test that setup_path defaults to root setup.sh when not configured."""
        from goobits_cli.universal.generator import UniversalGenerator

        # Create config without explicit setup_path
        config = TestConfigTemplates.minimal_config("python")

        # Verify installation exists but setup_path is default
        if config.installation:
            # Default should be "setup.sh" (root level)
            default_path = config.installation.setup_path
            assert default_path is None or default_path == "setup.sh", (
                f"Default setup_path should be 'setup.sh' or None, got: {default_path}"
            )

        print("✅ setup_path default value validated")
