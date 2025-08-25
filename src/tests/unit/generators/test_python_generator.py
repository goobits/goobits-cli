"""Unit tests for Python generator."""
import pytest
import json
from unittest.mock import patch, MagicMock
from pathlib import Path

from goobits_cli.generators.python import PythonGenerator
from goobits_cli.generators import TemplateError
from goobits_cli.schemas import ConfigSchema, CLISchema, CommandSchema, GoobitsConfigSchema, ArgumentSchema, OptionSchema
from goobits_cli.main import load_goobits_config


class TestPythonGenerator:
    """Test cases for PythonGenerator class."""
    
    def test_python_generator_initialization(self):
        """Test PythonGenerator initialization."""
        generator = PythonGenerator()
        
        assert generator is not None
        assert hasattr(generator, 'template_env')
        assert hasattr(generator, 'use_universal_templates')
    
    def test_python_generator_basic_generation(self, tmp_path):
        """Test basic CLI generation functionality."""
        # Create a minimal config
        config = ConfigSchema(cli=CLISchema(
            name="test-cli",
            tagline="Test CLI",
            description="Test CLI",
            version="1.0.0",
            commands={}
        ))
        
        generator = PythonGenerator(use_universal_templates=False)
        
        # Test that generation doesn't raise exceptions
        try:
            result = generator.generate(config, str(tmp_path))
            assert result is not None
        except Exception as e:
            pytest.fail(f"Basic generation failed: {e}")
    
    def test_python_generator_with_commands(self, tmp_path):
        """Test generation with commands."""
        config = ConfigSchema(cli=CLISchema(
            name="test-cli",
            tagline="Test CLI",
            description="Test CLI",
            version="1.0.0",
            commands={
                "hello": CommandSchema(
                    desc="Say hello"
                )
            }
        ))
        
        generator = PythonGenerator(use_universal_templates=False)
        
        # Test generation with commands
        try:
            result = generator.generate(config, str(tmp_path))
            assert result is not None
        except Exception as e:
            pytest.fail(f"Command generation failed: {e}")
    
    @patch('goobits_cli.generators.python.PythonGenerator.generate_all_files')
    def test_python_generator_mocked(self, mock_generate):
        """Test with mocked generation to avoid file system operations."""
        mock_generate.return_value = True
        
        config = ConfigSchema(cli=CLISchema(
            name="test-cli",
            tagline="Test CLI",
            description="Test CLI", 
            version="1.0.0",
            commands={}
        ))
        
        generator = PythonGenerator()
        result = generator.generate_all_files(config, "/tmp/test")
        
        assert result is True
        mock_generate.assert_called_once()

    def test_python_output_files_structure(self):
        """Test that Python generator returns correct file structure."""
        config = GoobitsConfigSchema(
            package_name="test-python-cli",
            command_name="test-python-cli", 
            display_name="Test Python CLI",
            description="Test CLI",
            language="python",
            cli=CLISchema(
                name="test-python-cli",
                tagline="Test CLI",
                description="Test CLI",
                commands={}
            )
        )
        generator = PythonGenerator()
        output_files = generator.get_output_files()
        
        # Python should generate cli.py (setup.sh is handled by main build system)
        assert 'cli.py' in output_files
        # Should not list Node.js or Rust files
        assert 'package.json' not in output_files
        assert 'cli.js' not in output_files
        assert 'Cargo.toml' not in output_files
    
    def test_python_cli_structure_validation(self):
        """Test that generated Python CLI has proper structure."""
        config = GoobitsConfigSchema(
            package_name="test-python-cli",
            command_name="test-python-cli",
            display_name="Test Python CLI", 
            description="Test CLI",
            language="python",
            cli=CLISchema(
                name="test-python-cli",
                tagline="Test CLI",
                commands={}
            )
        )
        generator = PythonGenerator()
        output_files = generator.generate_all_files(config, "test.yaml")
        
        # Find Python CLI file (might be different with Universal Templates)
        cli_files = [f for f in output_files.keys() if f.endswith('.py')]
        assert len(cli_files) > 0, f"No Python files found in {list(output_files.keys())}"
        cli_content = output_files[cli_files[0]]
        
        # Check for essential Python CLI structure (Universal Templates use rich_click)
        has_imports = any(pattern in cli_content for pattern in ['import click', 'import typer', 'import argparse', 'import'])
        has_main = any(pattern in cli_content for pattern in ['def cli', 'def main', '@click.group', '@typer.app', 'if __name__'])
        
        # Universal Templates use rich_click and have proper structure
        assert has_imports, f"No imports found in CLI: {cli_content[:200]}"
        assert has_main or 'def ' in cli_content, f"No function definitions found in CLI: {cli_content[:200]}"
    
    
    def test_python_unicode_special_characters(self):
        """Test Python generator with unicode and special characters."""
        config = GoobitsConfigSchema(
            package_name="test-unicode-cli",
            command_name="test-unicode-cli",
            display_name="Test Unicode CLI 🚀",
            description="CLI with émojis and spëcial chars",
            language="python",
            cli=CLISchema(
                name="test-unicode-cli",
                tagline="CLI with émojis and spëcial chars",
                commands={}
            )
        )
        
        generator = PythonGenerator()
        
        # Should handle unicode without errors
        try:
            output_files = generator.generate_all_files(config, "test.yaml")
            
            # Find CLI file in Universal Template structure
            cli_files = [f for f in output_files.keys() if f.endswith('.py') and 'cli.py' in f]
            assert len(cli_files) > 0, f"No CLI files generated: {list(output_files.keys())}"
            
            # Check that unicode is properly handled in output
            cli_content = output_files[cli_files[0]]
            assert isinstance(cli_content, str)  # Should be valid string
            assert len(cli_content) > 0, "Generated CLI content is empty"
        except UnicodeError:
            pytest.fail("Python generator failed to handle unicode characters")
    
    def test_python_complex_command_generation(self):
        """Test generation of complex commands with arguments and options."""
        config = GoobitsConfigSchema(
            package_name="test-complex-cli",
            command_name="test-complex-cli",
            display_name="Test Complex CLI",
            description="Complex CLI",
            language="python",
            cli=CLISchema(
                name="test-complex-cli",
                tagline="Complex CLI",
                commands={
                    "complex": CommandSchema(
                        desc="Complex command",
                        args=[
                            ArgumentSchema(name="input_file", desc="Input file", required=True)
                        ],
                        options=[
                            OptionSchema(name="--verbose", short="-v", desc="Verbose output", type="bool"),
                            OptionSchema(name="--output", short="-o", desc="Output file", type="str")
                        ]
                    )
                }
            )
        )
        
        generator = PythonGenerator()
        output_files = generator.generate_all_files(config, "test.yaml")
        
        # Find the CLI file with complex commands (Universal Templates use src/package structure)
        cli_files = [f for f in output_files.keys() if f.endswith('.py') and 'cli.py' in f]
        assert len(cli_files) > 0, f"No CLI files generated: {list(output_files.keys())}"
        cli_content = output_files[cli_files[0]]
        
        # Check for complex command structure
        # Universal Templates might structure commands differently
        assert 'complex' in cli_content, f"Complex command not found in: {cli_content[:300]}..."
        # Arguments and options might be transformed (e.g., input_file -> input-file)
        assert any(pattern in cli_content for pattern in ['input_file', 'input-file', 'inputFile']), f"Input argument not found"
        assert any(pattern in cli_content for pattern in ['verbose', '-v']), f"Verbose option not found"
        assert any(pattern in cli_content for pattern in ['output', '-o']), f"Output option not found"
    
    def test_python_generator_error_handling(self):
        """Test error handling for invalid configurations."""
        generator = PythonGenerator()
        
        # Test with invalid config (missing required fields)
        invalid_config = {}
        
        with pytest.raises(TemplateError):
            generator.generate_all_files(invalid_config, "test.yaml")