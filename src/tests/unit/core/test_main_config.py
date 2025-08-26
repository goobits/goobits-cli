"""
Tests for main CLI configuration handling and validation.

This module tests configuration-related functionality including:
- YAML configuration parsing and validation
- Configuration schema validation
- Error conditions in configuration handling
- Configuration loading and processing
"""

import pytest
import typer

from goobits_cli.main import load_goobits_config
from .test_base import TestMainCLIBase


# ============================================================================
# YAML CONFIGURATION ERROR CONDITIONS TESTS
# ============================================================================


class TestYAMLConfigurationErrorConditions(TestMainCLIBase):
    """Test error conditions in YAML configuration parsing and validation."""

    def test_yaml_syntax_error_unclosed_quotes(self):
        """Test YAML parsing with unclosed quotes."""
        config_content = """
package_name: "test-cli
command_name: testcli
"""
        config_path = self.create_test_config_file(config_content)

        with pytest.raises(typer.Exit):
            load_goobits_config(str(config_path))

    def test_yaml_syntax_error_invalid_indentation(self):
        """Test YAML parsing with invalid indentation."""
        config_content = """
package_name: test-cli
    command_name: testcli
  display_name: "Test CLI"
"""
        config_path = self.create_test_config_file(config_content)

        with pytest.raises(typer.Exit):
            load_goobits_config(str(config_path))

    def test_yaml_syntax_error_unclosed_brackets(self):
        """Test YAML parsing with unclosed brackets."""
        config_content = """
package_name: test-cli
dependencies: [click, rich
"""
        config_path = self.create_test_config_file(config_content)

        with pytest.raises(typer.Exit):
            load_goobits_config(str(config_path))

    def test_yaml_duplicate_keys(self):
        """Test YAML with duplicate keys."""
        config_content = """
package_name: test-cli
package_name: duplicate-cli
"""
        config_path = self.create_test_config_file(config_content)

        # YAML loader should handle duplicates (typically last one wins)
        # But this will fail validation due to missing required fields
        with pytest.raises(typer.Exit):
            load_goobits_config(str(config_path))

    def test_yaml_invalid_list_syntax(self):
        """Test YAML with invalid list syntax."""
        config_content = """
package_name: test-cli
dependencies:
  - click
  - rich
  invalid_item
"""
        config_path = self.create_test_config_file(config_content)

        with pytest.raises(typer.Exit):
            load_goobits_config(str(config_path))

    def test_yaml_invalid_multiline_string(self):
        """Test YAML with invalid multiline string."""
        config_content = """
package_name: test-cli
description: |
    This is a multiline description
  But this line has wrong indentation
"""
        config_path = self.create_test_config_file(config_content)

        with pytest.raises(typer.Exit):
            load_goobits_config(str(config_path))

    def test_empty_yaml_file(self):
        """Test loading empty YAML file."""
        config_path = self.create_test_config_file("")

        # Empty YAML should result in TypeError for NoneType data
        with pytest.raises(TypeError):
            load_goobits_config(str(config_path))

    def test_yaml_with_only_comments(self):
        """Test YAML file with only comments."""
        config_content = """
# This is a comment
# Another comment
"""
        config_path = self.create_test_config_file(config_content)

        # Comments-only YAML should result in TypeError for NoneType data
        with pytest.raises(TypeError):
            load_goobits_config(str(config_path))

    def test_yaml_missing_required_fields(self):
        """Test YAML missing required fields."""
        config_content = """
package_name: test-cli
# Missing other required fields
"""
        config_path = self.create_test_config_file(config_content)

        # Should raise validation error for missing required fields
        with pytest.raises(typer.Exit):
            load_goobits_config(str(config_path))

    def test_yaml_invalid_field_types(self):
        """Test YAML with invalid field types."""
        config_content = """
package_name: test-cli
command_name: testcli
display_name: "Test CLI" 
description: "Test CLI"
language: python
python:
  minimum_version: 3.8  # Should be string, not number
"""
        config_path = self.create_test_config_file(config_content)

        # Should handle type coercion or raise validation error
        try:
            config = load_goobits_config(str(config_path))
            # If successful, verify the type was coerced correctly
            assert isinstance(config.python.minimum_version, str)
        except typer.Exit:
            # This is also acceptable - strict type validation
            pass

    def test_yaml_unicode_handling(self):
        """Test YAML with unicode characters."""
        config_content = """
package_name: test-cli-üñíçødé
command_name: testcli
display_name: "Test CLI 🚀"
description: "CLI with émojis and spëcial chars"
language: python
python:
  minimum_version: "3.8"
"""
        config_path = self.create_test_config_file(config_content)

        # Should handle unicode properly
        config = load_goobits_config(str(config_path))
        assert "üñíçødé" in config.package_name
        assert "🚀" in config.display_name
        assert "émojis" in config.description

    def test_yaml_very_large_file(self):
        """Test YAML with very large content."""
        # Create a config with many repeated sections
        large_commands = {}
        for i in range(100):
            large_commands[f"command_{i}"] = {
                "desc": f"Command {i} description",
                "args": [
                    {"name": f"arg_{j}", "desc": f"Argument {j}"} for j in range(10)
                ],
            }

        config_content = self.get_minimal_valid_config()
        # Add the large CLI section
        config_content += """
cli:
  name: testcli
  tagline: "Test CLI with many commands"
  commands:
"""
        for cmd_name, cmd_data in large_commands.items():
            config_content += f"""
    {cmd_name}:
      desc: "{cmd_data['desc']}"
      args:
"""
            for arg in cmd_data["args"]:
                config_content += f"""
        - name: {arg['name']}
          desc: "{arg['desc']}"
"""

        config_path = self.create_test_config_file(config_content)

        # Should handle large files without issues
        config = load_goobits_config(str(config_path))
        assert len(config.cli.commands) == 100

    def test_yaml_circular_references(self):
        """Test YAML with potential circular references using aliases."""
        config_content = """
package_name: test-cli
command_name: testcli
display_name: "Test CLI"
description: "Test CLI"
language: python

defaults: &defaults
  minimum_version: "3.8"

python: *defaults

# This shouldn't create issues but tests alias handling
validation:
  check_api_keys: false
  minimum_disk_space_mb: 100
"""
        config_path = self.create_test_config_file(config_content)

        # Should handle YAML aliases properly
        config = load_goobits_config(str(config_path))
        assert config.python.minimum_version == "3.8"


# ============================================================================
# MAIN CLI CONFIGURATION TESTS
# ============================================================================


class TestMainCLIConfig(TestMainCLIBase):
    """Test suite for main CLI configuration functionality."""

    def test_load_goobits_config_success(self, basic_config_content):
        """Test successful loading of goobits configuration."""
        config_path = self.create_test_config_file(basic_config_content)

        config = load_goobits_config(str(config_path))

        assert config.package_name == "test-cli"
        assert config.command_name == "testcli"
        assert config.display_name == "Test CLI"
        assert config.language == "python"
        assert config.cli.name == "testcli"

    def test_load_goobits_config_file_not_found(self):
        """Test loading non-existent config file."""
        non_existent_path = self.temp_dir / "nonexistent.yaml"

        with pytest.raises(typer.Exit):
            load_goobits_config(str(non_existent_path))

    def test_load_goobits_config_permission_denied(self):
        """Test loading config file with permission denied."""
        config_path = self.create_test_config_file(self.get_minimal_valid_config())

        # Make file unreadable (on Unix systems)
        try:
            import os

            os.chmod(config_path, 0o000)

            with pytest.raises(PermissionError):
                load_goobits_config(str(config_path))
        except (OSError, PermissionError):
            # If we can't change permissions, skip this test
            pytest.skip("Cannot test permission denied on this system")
        finally:
            # Restore permissions for cleanup
            try:
                os.chmod(config_path, 0o644)
            except (OSError, PermissionError):
                pass

    def test_config_validation_missing_cli_section(self):
        """Test config validation with missing CLI section."""
        config_content = """
package_name: test-cli
command_name: testcli
display_name: "Test CLI"
description: "Test CLI"
language: python
# Missing cli section
"""
        config_path = self.create_test_config_file(config_content)

        # CLI section is optional, so this should succeed
        config = load_goobits_config(str(config_path))
        assert config.package_name == "test-cli"
        assert config.cli is None  # CLI section should be None when missing

    def test_config_validation_invalid_language(self):
        """Test config validation with invalid language."""
        config_content = self.get_minimal_valid_config(language="invalid-language")
        config_path = self.create_test_config_file(config_content)

        # Should either accept unknown language or raise validation error
        try:
            config = load_goobits_config(str(config_path))
            assert config.language == "invalid-language"
        except typer.Exit:
            # Strict validation - also acceptable
            pass

    def test_config_with_all_languages(self):
        """Test config loading with different supported languages."""
        languages = ["python", "nodejs", "typescript", "rust"]

        for language in languages:
            config_content = self.get_minimal_valid_config(language=language)
            config_path = self.create_test_config_file(config_content)

            config = load_goobits_config(str(config_path))
            assert config.language == language

    def test_config_complex_cli_structure(self):
        """Test config with complex CLI structure."""
        config_content = """
package_name: complex-cli
command_name: complexcli
display_name: "Complex CLI"
description: "A complex CLI for testing"
language: python

python:
  minimum_version: "3.8"

dependencies:
  required:
    - pipx

installation:
  pypi_name: "complex-cli"

shell_integration:
  enabled: false
  alias: complexcli

validation:
  check_api_keys: false
  minimum_disk_space_mb: 100

messages:
  install_success: "Installation completed!"

cli:
  name: complexcli
  tagline: "Complex CLI for testing"
  commands:
    hello:
      desc: "Say hello"
      args:
        - name: name
          desc: "Name to greet"
          required: true
      options:
        - name: --uppercase
          short: -u
          desc: "Use uppercase"
          type: bool
          default: false
    goodbye:
      desc: "Say goodbye"
      subcommands:
        formal:
          desc: "Formal goodbye"
        casual:
          desc: "Casual goodbye"
"""
        config_path = self.create_test_config_file(config_content)

        config = load_goobits_config(str(config_path))

        assert len(config.cli.commands) == 2
        assert "hello" in config.cli.commands
        assert "goodbye" in config.cli.commands

        hello_cmd = config.cli.commands["hello"]
        assert len(hello_cmd.args) == 1
        assert len(hello_cmd.options) == 1
        assert hello_cmd.args[0].name == "name"
        assert hello_cmd.args[0].required == True

        goodbye_cmd = config.cli.commands["goodbye"]
        assert goodbye_cmd.subcommands is not None
        assert "formal" in goodbye_cmd.subcommands
        assert "casual" in goodbye_cmd.subcommands

    def test_config_edge_cases(self):
        """Test configuration edge cases and boundary conditions."""
        # Test with minimal required fields only
        minimal_config = """
package_name: minimal
command_name: minimal
display_name: "Minimal"
description: "Minimal config"
language: python

cli:
  name: minimal
  tagline: "Minimal CLI"
  commands:
    test:
      desc: "Test command"
"""
        config_path = self.create_test_config_file(minimal_config)
        config = load_goobits_config(str(config_path))
        assert config.package_name == "minimal"

    def test_config_default_values(self):
        """Test that configuration applies correct default values."""
        config_content = self.get_minimal_valid_config()
        config_path = self.create_test_config_file(config_content)

        config = load_goobits_config(str(config_path))

        # Test that default values are applied where expected
        assert config.python.minimum_version is not None
        assert config.validation is not None
        assert config.messages is not None
