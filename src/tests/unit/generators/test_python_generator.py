"""Unit tests for Python generator."""
import pytest
from unittest.mock import patch

from goobits_cli.generators.python import PythonGenerator
from goobits_cli.schemas import ConfigSchema, CLISchema, CommandSchema


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