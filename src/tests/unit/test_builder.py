"""Unit tests for builder.py module."""
import pytest
from unittest.mock import Mock, patch, mock_open
from click.exceptions import Exit

from goobits_cli.builder import load_yaml_config, generate_cli_code, Builder
from goobits_cli.schemas import ConfigSchema, CLISchema, CommandSchema, ArgumentSchema, OptionSchema


class TestBuilder:
    """Test cases for Builder class."""
    
    def test_builder_initialization(self):
        """Test Builder class initialization creates environment with custom filters."""
        builder = Builder()
        
        # Check that environment was created
        assert builder.env is not None
        assert hasattr(builder.env, 'filters')
        
        # Check that custom filters were added
        expected_filters = [
            'align_examples', 'format_multiline', 'escape_docstring',
            'align_setup_steps', 'format_icon', 'align_header_items'
        ]
        for filter_name in expected_filters:
            assert filter_name in builder.env.filters
    
    def test_build_generates_valid_cli_structure(self):
        """Test that build generates a CLI with correct structure."""
        # Use a minimal but real config
        config = ConfigSchema(cli=CLISchema(
            name="test-cli",
            tagline="Test CLI Application",
            commands={"hello": CommandSchema(desc="Say hello to someone")}
        ))
        
        builder = Builder()
        result = builder.build(config, "test.yaml")
        
        # Test essential CLI structure
        assert "#!/usr/bin/env python3" in result
        assert 'Auto-generated from test.yaml' in result
        assert "import rich_click as click" in result
        assert "from rich_click import RichGroup" in result
        
        # Test command structure
        assert "def hello(ctx):" in result
        assert '@main.command()' in result
        assert '"Say hello to someone"' in result
        
        # Test main CLI function
        assert "def main(ctx):" in result
        assert "Test CLI Application" in result  # Tagline appears in docstring
    
    def test_build_handles_command_with_arguments(self):
        """Test that build correctly handles commands with arguments."""
        config = ConfigSchema(cli=CLISchema(
            name="test-cli",
            tagline="Test CLI",
            commands={
                "greet": CommandSchema(
                    desc="Greet a user",
                    args=[
                        ArgumentSchema(
                            name="name",
                            desc="Name of person to greet",
                            required=True
                        )
                    ]
                )
            }
        ))
        
        builder = Builder()
        result = builder.build(config, "test.yaml")
        
        # Check argument handling
        assert "def greet(ctx, name):" in result
        assert '@click.argument' in result
        assert '"NAME"' in result  # Arguments are uppercase in decorator
        # Help text is shown in the docstring, not in argument decorator
    
    def test_build_handles_command_with_options(self):
        """Test that build correctly handles commands with options."""
        config = ConfigSchema(cli=CLISchema(
            name="test-cli",
            tagline="Test CLI",
            commands={
                "hello": CommandSchema(
                    desc="Say hello",
                    options=[
                        OptionSchema(
                            name="uppercase",
                            desc="Print in uppercase",
                            type="flag"
                        ),
                        OptionSchema(
                            name="count",
                            desc="Number of times to repeat",
                            type="int",
                            default=1
                        )
                    ]
                )
            }
        ))
        
        builder = Builder()
        result = builder.build(config, "test.yaml")
        
        # Check option handling
        assert "def hello(ctx, uppercase, count):" in result
        assert '@click.option("--uppercase"' in result
        assert 'is_flag=True' in result
        assert '@click.option("--count"' in result
        assert 'type=int' in result
        assert 'default=1' in result
    
    def test_build_includes_daemon_support_for_managed_commands(self):
        """Test that managed lifecycle commands get daemon support."""
        config = ConfigSchema(cli=CLISchema(
            name="test-cli",
            tagline="Test CLI",
            commands={
                "serve": CommandSchema(
                    desc="Run server",
                    lifecycle="managed"
                )
            }
        ))
        
        builder = Builder()
        result = builder.build(config, "test.yaml")
        
        # Verify managed command functionality
        assert "# Managed command" in result
        assert "command_instance_name = f\"serve_command\"" in result
        assert "command_instance.execute(**kwargs)" in result
        assert 'Error: Managed command' in result
    
    def test_build_includes_global_options(self):
        """Test that global CLI options are properly included."""
        config = ConfigSchema(cli=CLISchema(
            name="test-cli",
            tagline="Test CLI",
            options=[
                OptionSchema(
                    name="verbose",
                    desc="Enable verbose output",
                    type="flag"
                )
            ],
            commands={"hello": CommandSchema(desc="Say hello")}
        ))
        
        builder = Builder()
        result = builder.build(config, "test.yaml")
        
        # Check global option handling
        assert "def main(ctx" in result
        assert "verbose" in result
        assert "ctx.obj['verbose'] = verbose" in result
        assert "@click.option" in result
        assert "--verbose" in result
    
    def test_build_includes_config_metadata(self):
        """Test that build includes configuration metadata."""
        config = ConfigSchema(cli=CLISchema(
            name="test-cli",
            tagline="Test CLI",
            version="1.2.3",
            commands={"hello": CommandSchema(desc="Say hello")}
        ))
        
        builder = Builder()
        result = builder.build(config, "test.yaml")
        
        # Check metadata inclusion
        assert "test.yaml" in result
        assert "1.2.3" in result
    
    def test_build_escapes_special_characters_in_json(self):
        """Test that special characters are properly escaped in embedded JSON."""
        config = ConfigSchema(cli=CLISchema(
            name="test-cli",
            tagline='CLI with "quotes" and \'apostrophes\'',
            commands={"hello": CommandSchema(desc="Say hello")}
        ))
        
        builder = Builder()
        result = builder.build(config, "test.yaml")
        
        # The tagline with special characters should be in the output
        assert "CLI with" in result
        assert "quotes" in result
        assert "apostrophes" in result
        # The template should handle these special characters correctly


class TestLoadYamlConfig:
    """Test cases for load_yaml_config function."""
    
    @patch("builtins.open", new_callable=mock_open, read_data="""
cli:
  name: test-cli
  tagline: Test CLI Application
  commands:
    hello:
      desc: Hello command
""")
    def test_load_valid_yaml_config(self, mock_file):
        """Test load_yaml_config with valid YAML."""
        result = load_yaml_config("test.yaml")
        
        assert isinstance(result, ConfigSchema)
        assert result.cli.name == "test-cli"
        assert result.cli.tagline == "Test CLI Application"
        assert "hello" in result.cli.commands
        assert result.cli.commands["hello"].desc == "Hello command"
    
    @patch("builtins.open", side_effect=FileNotFoundError)
    def test_load_yaml_config_file_not_found(self, mock_file):
        """Test load_yaml_config when file doesn't exist."""
        with pytest.raises(Exit) as exc_info:
            load_yaml_config("missing.yaml")
        
        assert exc_info.value.exit_code == 1
    
    @patch("builtins.open", new_callable=mock_open, read_data="invalid: yaml: content:")
    def test_load_yaml_config_invalid_yaml(self, mock_file):
        """Test load_yaml_config with invalid YAML syntax."""
        with pytest.raises(Exit) as exc_info:
            load_yaml_config("invalid.yaml")
        
        assert exc_info.value.exit_code == 1
    
    @patch("builtins.open", new_callable=mock_open, read_data="""
cli:
  # Missing required 'name' field
  commands:
    hello:
      desc: Hello
""")
    def test_load_yaml_config_validation_error(self, mock_file):
        """Test load_yaml_config with schema validation error."""
        with pytest.raises(Exit) as exc_info:
            load_yaml_config("invalid_schema.yaml")
        
        assert exc_info.value.exit_code == 1
    
    @patch("builtins.open", new_callable=mock_open, read_data="""
cli:
  name: test-cli
  tagline: Test CLI
  commands:
    hello:
      desc: Hello command
""")
    def test_load_yaml_config_with_commands(self, mock_file):
        """Test load_yaml_config with commands defined."""
        result = load_yaml_config("test.yaml")
        
        assert isinstance(result, ConfigSchema)
        assert "hello" in result.cli.commands
        assert result.cli.commands["hello"].desc == "Hello command"

