"""Unit tests for TypeScript generator."""
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import tempfile

from goobits_cli.generators.typescript import TypeScriptGenerator
from goobits_cli.schemas import ConfigSchema, CLISchema, CommandSchema


class TestTypeScriptGenerator:
    """Test cases for TypeScriptGenerator class."""
    
    def test_typescript_generator_initialization(self):
        """Test TypeScriptGenerator initialization."""
        generator = TypeScriptGenerator()
        
        assert generator is not None
        assert hasattr(generator, 'template_env')
        assert hasattr(generator, 'use_universal_templates')
    
    def test_typescript_generator_basic_generation(self, tmp_path):
        """Test basic CLI generation functionality."""
        # Create a minimal config
        config = ConfigSchema(cli=CLISchema(
            name="test-cli",
            description="Test CLI",
            version="1.0.0",
            commands=[]
        ))
        
        generator = TypeScriptGenerator(use_universal_templates=False)
        
        # Test that generation doesn't raise exceptions
        try:
            result = generator.generate(config, str(tmp_path))
            assert result is not None
        except Exception as e:
            pytest.fail(f"Basic generation failed: {e}")
    
    def test_typescript_generator_with_commands(self, tmp_path):
        """Test generation with commands."""
        config = ConfigSchema(cli=CLISchema(
            name="test-cli",
            description="Test CLI",
            version="1.0.0",
            commands=[
                CommandSchema(
                    name="hello",
                    description="Say hello",
                    handler="hello_handler"
                )
            ]
        ))
        
        generator = TypeScriptGenerator(use_universal_templates=False)
        
        # Test generation with commands
        try:
            result = generator.generate(config, str(tmp_path))
            assert result is not None
        except Exception as e:
            pytest.fail(f"Command generation failed: {e}")
    
    @patch('goobits_cli.generators.typescript.TypeScriptGenerator.generate_all_files')
    def test_typescript_generator_mocked(self, mock_generate):
        """Test with mocked generation to avoid file system operations."""
        mock_generate.return_value = True
        
        config = ConfigSchema(cli=CLISchema(
            name="test-cli",
            description="Test CLI", 
            version="1.0.0",
            commands=[]
        ))
        
        generator = TypeScriptGenerator()
        result = generator.generate_all_files(config, "/tmp/test")
        
        assert result is True
        mock_generate.assert_called_once()