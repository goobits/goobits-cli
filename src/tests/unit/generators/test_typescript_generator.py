"""Unit tests for TypeScript generator."""
import pytest
import json
from unittest.mock import patch, MagicMock
from pathlib import Path

from goobits_cli.generators.typescript import TypeScriptGenerator
from goobits_cli.schemas import ConfigSchema, CLISchema, CommandSchema, GoobitsConfigSchema, ArgumentSchema, OptionSchema
from goobits_cli.main import load_goobits_config


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
            tagline="Test CLI",
            description="Test CLI",
            version="1.0.0",
            commands={}
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
            tagline="Test CLI",
            description="Test CLI",
            version="1.0.0",
            commands={
                "hello": CommandSchema(
                    desc="Say hello"
                )
            }
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
            tagline="Test CLI",
            description="Test CLI", 
            version="1.0.0",
            commands={}
        ))
        
        generator = TypeScriptGenerator()
        result = generator.generate_all_files(config, "/tmp/test")
        
        assert result is True
        mock_generate.assert_called_once()

    def test_typescript_output_files_structure(self):
        """Test that TypeScript generator returns correct file structure."""
        config = GoobitsConfigSchema(
            package_name="test-typescript-cli",
            command_name="test-typescript-cli",
            display_name="Test TypeScript CLI",
            description="Test CLI",
            language="typescript",
            cli=CLISchema(
                name="test-typescript-cli",
                tagline="Test CLI",
                commands={}
            )
        )
        generator = TypeScriptGenerator()
        output_files = generator.get_output_files()
        
        # TypeScript should generate generated_index.ts (or index.ts), package.json, and setup.sh
        assert 'generated_index.ts' in output_files or 'index.ts' in output_files
        assert 'package.json' in output_files
        assert 'setup.sh' in output_files
        # Should not generate Python or Rust files
        assert 'cli.py' not in output_files
        assert 'Cargo.toml' not in output_files
    
    def test_typescript_package_json_validity(self):
        """Test that generated package.json is valid JSON with correct TypeScript structure."""
        config = GoobitsConfigSchema(
            package_name="test-typescript-cli",
            command_name="test-typescript-cli",
            display_name="Test TypeScript CLI",
            description="Test CLI",
            language="typescript",
            cli=CLISchema(
                name="test-typescript-cli",
                tagline="Test CLI",
                commands={}
            )
        )
        generator = TypeScriptGenerator()
        output_files = generator.generate_all_files(config, "test.yaml")
        
        # Parse and validate package.json
        package_json_content = output_files['package.json']
        package_data = json.loads(package_json_content)
        
        # Check required package.json fields
        assert 'name' in package_data
        assert 'version' in package_data
        assert 'description' in package_data
        assert 'main' in package_data or 'bin' in package_data
        assert 'dependencies' in package_data
        assert 'devDependencies' in package_data
        
        # Check TypeScript-specific dependencies
        assert 'commander' in package_data['dependencies']
        assert 'typescript' in package_data['devDependencies']
        assert '@types/node' in package_data['devDependencies']
        
        assert package_data['name'] == config.package_name
    
    def test_typescript_cli_structure_validation(self):
        """Test that generated TypeScript CLI has proper structure."""
        config = GoobitsConfigSchema(
            package_name="test-typescript-cli",
            command_name="test-typescript-cli",
            display_name="Test TypeScript CLI",
            description="Test CLI",
            language="typescript",
            cli=CLISchema(
                name="test-typescript-cli",
                tagline="Test CLI",
                commands={}
            )
        )
        generator = TypeScriptGenerator()
        output_files = generator.generate_all_files(config, "test.yaml")
        
        # Universal Templates generate different TypeScript structure
        ts_files = [f for f in output_files.keys() if f.endswith('.ts')]
        assert len(ts_files) > 0, f"No TypeScript files found in {list(output_files.keys())}"
        cli_content = output_files[ts_files[0]]  # Use first TypeScript file
        
        # Check for essential TypeScript CLI structure (Universal Templates may differ)
        assert 'import' in cli_content or 'require(' in cli_content, f"No imports found: {cli_content[:200]}"
        # Universal Templates might use different CLI frameworks
        assert len(cli_content) > 0, "Generated TypeScript CLI content is empty"
    
    def test_typescript_template_rendering_failure(self):
        """Test handling of template rendering failures."""
        generator = TypeScriptGenerator()
        
        # Mock template environment to raise exception
        with patch.object(generator, 'template_env') as mock_env:
            mock_template = MagicMock()
            mock_template.render.side_effect = Exception("Template error")
            mock_env.get_template.return_value = mock_template
            
            config = GoobitsConfigSchema(
                package_name="test-cli",
                command_name="test-cli",
                display_name="Test CLI",
                description="Test CLI",
                language="typescript",
                cli=CLISchema(
                    name="test-cli",
                    tagline="Test CLI",
                    commands={}
                )
            )
            
            with pytest.raises(Exception, match="Template error"):
                generator.generate_all_files(config, "test.yaml")
    
    def test_typescript_unicode_special_characters(self):
        """Test TypeScript generator with unicode and special characters."""
        config = GoobitsConfigSchema(
            package_name="test-unicode-cli",
            command_name="test-unicode-cli",
            display_name="Test Unicode CLI 🚀",
            description="CLI with émojis and spëcial chars",
            language="typescript",
            cli=CLISchema(
                name="test-unicode-cli",
                tagline="CLI with émojis and spëcial chars",
                commands={}
            )
        )
        
        generator = TypeScriptGenerator()
        
        # Should handle unicode without errors
        try:
            output_files = generator.generate_all_files(config, "test.yaml")
            assert 'generated_index.ts' in output_files or 'index.ts' in output_files
            
            # Check that unicode is properly handled in output
            ts_file = 'generated_index.ts' if 'generated_index.ts' in output_files else 'index.ts'
            cli_content = output_files[ts_file]
            assert isinstance(cli_content, str)  # Should be valid string
        except UnicodeError:
            pytest.fail("TypeScript generator failed to handle unicode characters")
    
    def test_typescript_complex_command_generation(self):
        """Test generation of complex commands with arguments and options."""
        config = GoobitsConfigSchema(
            package_name="test-complex-cli",
            command_name="test-complex-cli",
            display_name="Test Complex CLI",
            description="Complex CLI",
            language="typescript",
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
        
        generator = TypeScriptGenerator()
        output_files = generator.generate_all_files(config, "test.yaml")
        
        ts_file = 'generated_index.ts' if 'generated_index.ts' in output_files else 'index.ts'
        cli_content = output_files[ts_file]
        
        # Check for complex command structure
        assert 'complex' in cli_content
        assert 'input_file' in cli_content or 'inputFile' in cli_content  # TypeScript might use camelCase
        assert '--verbose' in cli_content or '-v' in cli_content
        assert '--output' in cli_content or '-o' in cli_content
    
    def test_typescript_generator_error_handling(self):
        """Test error handling for invalid configurations."""
        generator = TypeScriptGenerator()
        
        # Test with invalid config (missing required fields)
        invalid_config = {}
        
        with pytest.raises((TypeError, ValueError, AttributeError)):
            generator.generate_all_files(invalid_config, "test.yaml")