"""Unit tests for builder.py module."""
import pytest
import sys
import yaml
import json
from pathlib import Path
from unittest.mock import Mock, patch, mock_open, MagicMock
from pydantic import ValidationError

from goobits_cli.builder import load_yaml_config, generate_cli_code, main, Builder
from goobits_cli.schemas import ConfigSchema, CLISchema, CommandSchema


class TestBuilder:
    """Test cases for Builder class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.builder = Builder()
        self.mock_config = Mock(spec=ConfigSchema)
        self.mock_cli = Mock(spec=CLISchema)
        self.mock_config.cli = self.mock_cli
        
        # Mock the model_dump method
        self.mock_cli.model_dump.return_value = {
            "name": "test-cli",
            "tagline": "Test CLI Application",
            "commands": {
                "hello": {
                    "desc": "Say hello command"
                }
            }
        }
    
    @patch("goobits_cli.builder.Path")
    def test_builder_initialization(self, mock_path):
        """Test Builder class initialization."""
        mock_template_dir = Mock()
        mock_path.return_value.parent = mock_template_dir
        mock_template_dir.__truediv__ = Mock(return_value="templates/path")
        
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
    
    @patch("goobits_cli.builder.Path")
    def test_build(self, mock_path):
        """Test Builder.build method returns rendered template string."""
        # Setup mocks
        mock_template_dir = Mock()
        mock_path.return_value.parent = mock_template_dir
        mock_template_dir.__truediv__ = Mock(return_value="templates/path")
        
        # Create a fresh builder with mocked environment
        with patch("goobits_cli.builder.Environment") as mock_env_class:
            mock_env = Mock()
            mock_env_class.return_value = mock_env
            mock_env.filters = {}
            
            mock_template = Mock()
            mock_env.get_template.return_value = mock_template
            mock_template.render.return_value = "rendered_template"
            
            builder = Builder()
            
            # Call build method
            result = builder.build(self.mock_config, "test.yaml")
            
            # Assertions
            assert result == "rendered_template"
            mock_env.get_template.assert_called_once_with("cli_template.py.j2")
            mock_template.render.assert_called_once()
            
            # Verify that render was called with correct schema data
            render_call = mock_template.render.call_args
            assert render_call[1]['cli'] == self.mock_cli
            assert render_call[1]['file_name'] == "test.yaml"
            assert 'cli_config_json' in render_call[1]
    
    @patch("goobits_cli.builder.Path")
    def test_build_with_default_filename(self, mock_path):
        """Test Builder.build method with default filename."""
        # Setup mocks
        mock_template_dir = Mock()
        mock_path.return_value.parent = mock_template_dir
        mock_template_dir.__truediv__ = Mock(return_value="templates/path")
        
        with patch("goobits_cli.builder.Environment") as mock_env_class:
            mock_env = Mock()
            mock_env_class.return_value = mock_env
            mock_env.filters = {}
            
            mock_template = Mock()
            mock_env.get_template.return_value = mock_template
            mock_template.render.return_value = "rendered_template"
            
            builder = Builder()
            
            # Call build method without filename
            result = builder.build(self.mock_config)
            
            # Check that default filename was used
            render_call = mock_template.render.call_args
            assert render_call[1]['file_name'] == "config.yaml"
    
    @patch("goobits_cli.builder.Path")
    def test_build_json_serialization(self, mock_path):
        """Test Builder.build method properly serializes config to JSON."""
        # Setup mocks
        mock_template_dir = Mock()
        mock_path.return_value.parent = mock_template_dir
        mock_template_dir.__truediv__ = Mock(return_value="templates/path")
        
        # Set up config with special characters that need escaping
        self.mock_cli.model_dump.return_value = {
            "name": "test-cli",
            "description": "Text with \\ and ''' quotes"
        }
        
        with patch("goobits_cli.builder.Environment") as mock_env_class:
            mock_env = Mock()
            mock_env_class.return_value = mock_env
            mock_env.filters = {}
            
            mock_template = Mock()
            mock_env.get_template.return_value = mock_template
            mock_template.render.return_value = "rendered_template"
            
            builder = Builder()
            
            # Call build method
            result = builder.build(self.mock_config, "test.yaml")
            
            # Check that render was called with properly escaped JSON
            render_call = mock_template.render.call_args
            cli_config_json = render_call[1]['cli_config_json']
            
            # Should escape backslashes and triple quotes
            assert "\\\\" in cli_config_json
            assert "\\'\\'\\'" in cli_config_json


class TestLoadYamlConfig:
    """Test cases for load_yaml_config function."""
    
    @patch("builtins.open", new_callable=mock_open, read_data="cli:\n  name: test\n  tagline: Test CLI\n  commands: {}")
    def test_load_valid_yaml_config(self, mock_file):
        """Test load_yaml_config with valid YAML configuration."""
        result = load_yaml_config("test.yaml")
        
        assert isinstance(result, ConfigSchema)
        assert result.cli.name == "test"
        assert result.cli.tagline == "Test CLI"
        mock_file.assert_called_once_with("test.yaml", 'r')
    
    @patch("builtins.open", side_effect=FileNotFoundError)
    @patch("sys.exit")
    def test_load_yaml_config_file_not_found(self, mock_exit, mock_file):
        """Test load_yaml_config with non-existent file."""
        with patch("builtins.print") as mock_print:
            load_yaml_config("nonexistent.yaml")
            
            mock_print.assert_called_once()
            assert "Error: File 'nonexistent.yaml' not found." in str(mock_print.call_args)
            mock_exit.assert_called_once_with(1)
    
    @patch("builtins.open", new_callable=mock_open, read_data="invalid: yaml: content: [")
    @patch("sys.exit")
    def test_load_yaml_config_invalid_yaml(self, mock_exit, mock_file):
        """Test load_yaml_config with invalid YAML syntax."""
        with patch("builtins.print") as mock_print:
            load_yaml_config("invalid.yaml")
            
            mock_print.assert_called_once()
            assert "Error parsing YAML:" in str(mock_print.call_args)
            mock_exit.assert_called_once_with(1)
    
    @patch("builtins.open", new_callable=mock_open, read_data="cli:\n  name: test\n  invalid_field: value")
    @patch("sys.exit")
    def test_load_yaml_config_validation_error(self, mock_exit, mock_file):
        """Test load_yaml_config with validation errors."""
        with patch("builtins.print") as mock_print:
            load_yaml_config("invalid_schema.yaml")
            
            mock_print.assert_called_once()
            assert "Error validating configuration:" in str(mock_print.call_args)
            mock_exit.assert_called_once_with(1)
    
    @patch("builtins.open", new_callable=mock_open, read_data="cli:\n  name: test\n  tagline: Test CLI\n  commands:\n    hello:\n      desc: Hello command")
    def test_load_yaml_config_with_commands(self, mock_file):
        """Test load_yaml_config with commands defined."""
        result = load_yaml_config("test.yaml")
        
        assert isinstance(result, ConfigSchema)
        assert "hello" in result.cli.commands
        assert result.cli.commands["hello"].desc == "Hello command"


class TestGenerateCliCode:
    """Test cases for generate_cli_code function."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.mock_config = Mock(spec=ConfigSchema)
        self.mock_cli = Mock(spec=CLISchema)
        self.mock_config.cli = self.mock_cli
        
        # Mock the model_dump method
        self.mock_cli.model_dump.return_value = {
            "name": "test-cli",
            "tagline": "Test CLI",
            "commands": {}
        }
    
    @patch("goobits_cli.builder.Path")
    @patch("goobits_cli.builder.Environment")
    def test_generate_cli_code_basic(self, mock_env_class, mock_path):
        """Test generate_cli_code with basic configuration."""
        # Setup mocks
        mock_template_dir = Mock()
        mock_path.return_value.parent = mock_template_dir
        mock_template_dir.__truediv__ = Mock(return_value="templates/path")
        
        mock_env = Mock()
        mock_env_class.return_value = mock_env
        mock_env.filters = {}
        
        mock_template = Mock()
        mock_env.get_template.return_value = mock_template
        mock_template.render.return_value = "generated_cli_code"
        
        # Call function
        result = generate_cli_code(self.mock_config, "test.yaml")
        
        # Assertions
        assert result == "generated_cli_code"
        mock_env_class.assert_called_once()
        mock_env.get_template.assert_called_once_with("cli_template.py.j2")
        mock_template.render.assert_called_once()
    
    @patch("goobits_cli.builder.Path")
    @patch("goobits_cli.builder.Environment")
    def test_generate_cli_code_with_filters(self, mock_env_class, mock_path):
        """Test generate_cli_code adds custom filters."""
        # Setup mocks
        mock_template_dir = Mock()
        mock_path.return_value.parent = mock_template_dir
        mock_template_dir.__truediv__ = Mock(return_value="templates/path")
        
        mock_env = Mock()
        mock_env_class.return_value = mock_env
        mock_env.filters = {}
        
        mock_template = Mock()
        mock_env.get_template.return_value = mock_template
        mock_template.render.return_value = "generated_code"
        
        # Call function
        generate_cli_code(self.mock_config, "test.yaml")
        
        # Check that filters were added
        expected_filters = [
            'align_examples', 'format_multiline', 'escape_docstring',
            'align_setup_steps', 'format_icon', 'align_header_items'
        ]
        for filter_name in expected_filters:
            assert filter_name in mock_env.filters
    
    @patch("goobits_cli.builder.Path")
    @patch("goobits_cli.builder.Environment")
    def test_generate_cli_code_json_serialization(self, mock_env_class, mock_path):
        """Test generate_cli_code properly serializes config to JSON."""
        # Setup mocks
        mock_template_dir = Mock()
        mock_path.return_value.parent = mock_template_dir
        mock_template_dir.__truediv__ = Mock(return_value="templates/path")
        
        mock_env = Mock()
        mock_env_class.return_value = mock_env
        mock_env.filters = {}
        
        mock_template = Mock()
        mock_env.get_template.return_value = mock_template
        mock_template.render.return_value = "generated_code"
        
        # Set up config with special characters
        self.mock_cli.model_dump.return_value = {
            "name": "test-cli",
            "description": "Text with \\ and ''' quotes"
        }
        
        # Call function
        generate_cli_code(self.mock_config, "test.yaml")
        
        # Check that render was called with properly escaped JSON
        render_call = mock_template.render.call_args
        cli_config_json = render_call[1]['cli_config_json']
        
        # Should escape backslashes and triple quotes
        assert "\\\\" in cli_config_json
        assert "\\'\\'\\'" in cli_config_json
    
    @patch("goobits_cli.builder.Path")
    @patch("goobits_cli.builder.Environment")
    def test_generate_cli_code_template_rendering(self, mock_env_class, mock_path):
        """Test generate_cli_code passes correct parameters to template."""
        # Setup mocks
        mock_template_dir = Mock()
        mock_path.return_value.parent = mock_template_dir
        mock_template_dir.__truediv__ = Mock(return_value="templates/path")
        
        mock_env = Mock()
        mock_env_class.return_value = mock_env
        mock_env.filters = {}
        
        mock_template = Mock()
        mock_env.get_template.return_value = mock_template
        mock_template.render.return_value = "generated_code"
        
        # Call function
        generate_cli_code(self.mock_config, "config.yaml")
        
        # Check render call arguments
        render_call = mock_template.render.call_args
        assert render_call[1]['cli'] == self.mock_cli
        assert render_call[1]['file_name'] == "config.yaml"
        assert 'cli_config_json' in render_call[1]


class TestMain:
    """Test cases for main function."""
    
    @patch("sys.argv", ["builder.py", "config.yaml"])
    @patch("goobits_cli.builder.load_yaml_config")
    @patch("goobits_cli.builder.generate_cli_code")
    @patch("builtins.print")
    def test_main_success(self, mock_print, mock_generate, mock_load, ):
        """Test main function with valid arguments."""
        # Setup mocks
        mock_config = Mock()
        mock_load.return_value = mock_config
        mock_generate.return_value = "generated_cli_code"
        
        # Call main
        main()
        
        # Assertions
        mock_load.assert_called_once_with("config.yaml")
        mock_generate.assert_called_once_with(mock_config, "config.yaml")
        mock_print.assert_called_once_with("generated_cli_code")
    
    @patch("sys.argv", ["builder.py"])
    def test_main_no_arguments(self):
        """Test main function with no arguments."""
        with patch("builtins.print") as mock_print, \
             patch("sys.exit", side_effect=SystemExit(1)) as mock_exit:
            
            with pytest.raises(SystemExit):
                main()
            
            mock_print.assert_called_once()
            assert "Usage: python -m src.builder <yaml_file>" in str(mock_print.call_args)
            mock_exit.assert_called_once_with(1)
    
    @patch("sys.argv", ["builder.py", "arg1", "arg2", "arg3"])
    def test_main_too_many_arguments(self):
        """Test main function with too many arguments."""
        with patch("builtins.print") as mock_print, \
             patch("sys.exit", side_effect=SystemExit(1)) as mock_exit:
            
            with pytest.raises(SystemExit):
                main()
            
            mock_print.assert_called_once()
            assert "Usage: python -m src.builder <yaml_file>" in str(mock_print.call_args)
            mock_exit.assert_called_once_with(1)
    
    @patch("sys.argv", ["builder.py", "config.yaml"])
    @patch("goobits_cli.builder.load_yaml_config")
    @patch("goobits_cli.builder.generate_cli_code")
    @patch("builtins.print")
    def test_main_with_path_object(self, mock_print, mock_generate, mock_load):
        """Test main function correctly handles Path object for file name."""
        # Setup mocks
        mock_config = Mock()
        mock_load.return_value = mock_config
        mock_generate.return_value = "generated_code"
        
        # Call main
        main()
        
        # Check that generate_cli_code was called with the filename
        mock_generate.assert_called_once_with(mock_config, "config.yaml")
    
    @patch("sys.argv", ["builder.py", "/path/to/config.yaml"])
    @patch("goobits_cli.builder.load_yaml_config")
    @patch("goobits_cli.builder.generate_cli_code")
    @patch("builtins.print")
    def test_main_with_absolute_path(self, mock_print, mock_generate, mock_load):
        """Test main function with absolute path."""
        # Setup mocks
        mock_config = Mock()
        mock_load.return_value = mock_config
        mock_generate.return_value = "generated_code"
        
        # Call main
        main()
        
        # Check calls
        mock_load.assert_called_once_with("/path/to/config.yaml")
        mock_generate.assert_called_once_with(mock_config, "config.yaml")


class TestModuleExecution:
    """Test cases for module execution behavior."""
    
    @patch("goobits_cli.builder.main")
    def test_main_called_when_module_executed(self, mock_main):
        """Test that main is called when module is executed directly."""
        # This test would require actual module execution simulation
        # For now, we just verify the structure exists
        from goobits_cli import builder
        assert hasattr(builder, 'main')
        assert callable(builder.main)


class TestIntegrationScenarios:
    """Integration test scenarios combining multiple functions."""
    
    @patch("builtins.open", new_callable=mock_open)
    @patch("goobits_cli.builder.Path")
    @patch("goobits_cli.builder.Environment")
    def test_full_workflow_simulation(self, mock_env_class, mock_path, mock_file):
        """Test a complete workflow from YAML loading to code generation."""
        # Setup YAML content
        yaml_content = """
cli:
  name: test-cli
  tagline: Test CLI Application
  commands:
    hello:
      desc: Say hello
      args:
        - name: name
          desc: Name to greet
"""
        mock_file.return_value.read.return_value = yaml_content
        
        # Setup template environment
        mock_template_dir = Mock()
        mock_path.return_value.parent = mock_template_dir
        mock_template_dir.__truediv__ = Mock(return_value="templates/path")
        
        mock_env = Mock()
        mock_env_class.return_value = mock_env
        mock_env.filters = {}
        
        mock_template = Mock()
        mock_env.get_template.return_value = mock_template
        mock_template.render.return_value = "# Generated CLI Code"
        
        # Execute workflow
        config = load_yaml_config("test.yaml")
        result = generate_cli_code(config, "test.yaml")
        
        # Verify results
        assert result == "# Generated CLI Code"
        assert config.cli.name == "test-cli"
        assert "hello" in config.cli.commands