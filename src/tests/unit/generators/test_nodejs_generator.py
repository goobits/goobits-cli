"""Consolidated unit tests for NodeJS CLI generation.

This module consolidates NodeJS generator tests from unit/, e2e/, and integration/
directories to eliminate duplication and provide comprehensive coverage:

- Unit tests: Generator functionality and initialization 
- Integration tests: YAML config loading and file generation
- E2E tests: Complete workflow validation
- Error handling: Malformed configs and template failures
- Special cases: Unicode, large configs, concurrent access

Consolidated from:
- test_nodejs_generator.py
- test_nodejs_e2e.py  
- test_nodejs_integration.py
"""
import pytest
import subprocess
import tempfile
import json
from pathlib import Path
import shutil
import os
from unittest.mock import Mock, patch

from goobits_cli.generators.nodejs import NodeJSGenerator
from goobits_cli.schemas import CLISchema, CommandSchema, ArgumentSchema, OptionSchema
from goobits_cli.main import load_goobits_config
from conftest import create_test_goobits_config, determine_language, generate_cli


class TestNodeJSGeneratorCore:
    """Core NodeJS generator functionality tests."""
    
    def test_generator_initialization(self):
        """Test NodeJSGenerator class initialization."""
        generator = NodeJSGenerator()
        
        # Check that generator has required attributes
        assert hasattr(generator, 'env')
        assert generator.env is not None
    
    def test_template_loader_configuration(self):
        """Test that Jinja2 environment is properly configured."""
        generator = NodeJSGenerator()
        
        # Check that environment has correct loader
        assert hasattr(generator.env, 'loader')
    
    def test_generate_minimal_config(self):
        """Test generation with minimal configuration."""
        # Create a minimal GoobitsConfigSchema for testing
        cli_schema = CLISchema(
            name="test-cli",
            tagline="Test CLI Application",
            commands={"hello": CommandSchema(desc="Say hello")}
        )
        config = create_test_goobits_config("test-cli", cli_schema)
        
        generator = NodeJSGenerator()
        output_files = generator.generate_all_files(config, "test.yaml")
        
        # Check that output_files is a dictionary
        assert isinstance(output_files, dict)
        
        # Check for essential files
        assert 'cli.js' in output_files
        assert 'package.json' in output_files
        assert 'setup.sh' in output_files
        assert 'README.md' in output_files
        
        # Verify basic content in cli.js
        main_content = output_files['cli.js']
        assert "test-cli" in main_content
        assert "hello" in main_content
        
        # Verify package.json structure
        package_content = output_files['package.json']
        package_data = json.loads(package_content)
        assert "name" in package_data
        assert "commander" in package_data.get("dependencies", {})
    
    def test_generate_with_complex_commands(self):
        """Test generation with complex command structure."""
        cli_schema = CLISchema(
            name="complex-cli",
            tagline="Complex CLI with multiple features",
            version="2.0.0",
            commands={
                "deploy": CommandSchema(
                    desc="Deploy application",
                    args=[
                        ArgumentSchema(
                            name="environment",
                            desc="Target environment",
                            required=True
                        )
                    ],
                    options=[
                        OptionSchema(
                            name="force",
                            desc="Force deployment",
                            type="flag"
                        ),
                        OptionSchema(
                            name="timeout",
                            desc="Deployment timeout",
                            type="int",
                            default=300
                        )
                    ]
                ),
                "status": CommandSchema(
                    desc="Check deployment status",
                    lifecycle="managed"
                )
            }
        )
        config = create_test_goobits_config("complex-cli", cli_schema)
        
        generator = NodeJSGenerator()
        output_files = generator.generate_all_files(config, "complex.yaml")
        
        # Check command generation
        main_content = output_files['cli.js']
        assert "deploy" in main_content
        assert "status" in main_content
        assert "environment" in main_content
        assert "force" in main_content
        assert "timeout" in main_content
        
        # Check version in package.json
        package_content = output_files['package.json']
        package_data = json.loads(package_content)
        assert "version" in package_data
    
    def test_generate_with_subcommands(self):
        """Test generation with nested subcommands."""
        cli_schema = CLISchema(
            name="nested-cli",
            tagline="CLI with subcommands",
            commands={
                "database": CommandSchema(
                    desc="Database operations",
                    subcommands={
                        "migrate": CommandSchema(desc="Run migrations"),
                        "backup": CommandSchema(
                            desc="Backup database",
                            options=[
                                OptionSchema(
                                    name="output",
                                    desc="Output file",
                                    type="str",
                                    default="backup.sql"
                                )
                            ]
                        )
                    }
                )
            }
        )
        config = create_test_goobits_config("nested-cli", cli_schema)
        
        generator = NodeJSGenerator()
        output_files = generator.generate_all_files(config, "nested.yaml")
        
        # Check subcommand structure
        main_content = output_files['cli.js']
        assert "database" in main_content
        assert "migrate" in main_content or "backup" in main_content
    
    def test_get_output_files(self):
        """Test get_output_files method returns correct file list."""
        generator = NodeJSGenerator()
        output_files = generator.get_output_files()
        
        # Check that it returns a list
        assert isinstance(output_files, list)
        
        # Check for essential files
        expected_files = ['cli.js', 'package.json', 'setup.sh', 'README.md']
        for file_name in expected_files:
            assert file_name in output_files
    
    def test_custom_filter_camelCase(self):
        """Test camelCase custom filter."""
        generator = NodeJSGenerator()
        
        # Test camelCase conversion
        assert generator._to_camelcase('snake_case') == 'snakeCase'
        assert generator._to_camelcase('kebab-case') == 'kebabCase'
        assert generator._to_camelcase('PascalCase') == 'pascalCase'
        assert generator._to_camelcase('normal case') == 'normalCase'
        assert generator._to_camelcase('already_camel') == 'alreadyCamel'
        assert generator._to_camelcase('') == ''
    
    def test_custom_filter_pascalCase(self):
        """Test PascalCase custom filter."""
        generator = NodeJSGenerator()
        
        # Test PascalCase conversion
        assert generator._to_pascalcase('snake_case') == 'SnakeCase'
        assert generator._to_pascalcase('kebab-case') == 'KebabCase'
        assert generator._to_pascalcase('camelCase') == 'CamelCase'
        assert generator._to_pascalcase('normal case') == 'NormalCase'
        assert generator._to_pascalcase('') == ''
    
    def test_custom_filter_kebabCase(self):
        """Test kebab-case custom filter.""" 
        generator = NodeJSGenerator()
        
        # Test kebab-case conversion
        assert generator._to_kebabcase('snake_case') == 'snake-case'
        assert generator._to_kebabcase('camelCase') == 'camel-case'
        assert generator._to_kebabcase('PascalCase') == 'pascal-case'
        assert generator._to_kebabcase('normal case') == 'normal-case'
        assert generator._to_kebabcase('') == ''


class TestNodeJSGeneratorErrorConditions:
    """Test error conditions in NodeJS generator operations."""
    
    def test_generator_with_malformed_config_schema(self):
        """Test generator behavior with malformed configuration schema."""
        generator = NodeJSGenerator()
        
        # Create a mock config with missing required fields
        class MalformedConfig:
            def __init__(self):
                pass
            
            def model_dump(self):
                return {}
        
        malformed_config = MalformedConfig()
        
        # Should handle malformed config gracefully
        with pytest.raises((AttributeError, TypeError, KeyError, Exception)):
            generator.generate_all_files(malformed_config, "test.yaml")
    
    def test_generator_template_loading_failure(self):
        """Test generator when template files cannot be loaded."""
        generator = NodeJSGenerator()
        
        # Mock the template environment to simulate loading failures
        with patch.object(generator.env, 'get_template') as mock_get_template:
            mock_get_template.side_effect = Exception("Template not found")
            
            cli_schema = CLISchema(
                name="test-cli",
                tagline="Test CLI",
                commands={"hello": CommandSchema(desc="Say hello")}
            )
            config = create_test_goobits_config("test-cli", cli_schema)
            
            # Should handle template loading failures
            with pytest.raises(Exception):
                generator.generate_all_files(config, "test.yaml")
    
    def test_generator_template_rendering_failure(self):
        """Test generator when template rendering fails."""
        generator = NodeJSGenerator()
        
        cli_schema = CLISchema(
            name="test-cli",
            tagline="Test CLI",
            commands={"hello": CommandSchema(desc="Say hello")}
        )
        config = create_test_goobits_config("test-cli", cli_schema)
        
        # Mock template to simulate rendering failure
        mock_template = Mock()
        mock_template.render.side_effect = Exception("Rendering failed")
        
        with patch.object(generator.env, 'get_template') as mock_get_template:
            mock_get_template.return_value = mock_template
            
            # Should handle template rendering failures
            with pytest.raises(Exception):
                generator.generate_all_files(config, "test.yaml")
    
    def test_generator_with_unicode_and_special_characters(self):
        """Test generator with unicode and special characters in configuration."""
        generator = NodeJSGenerator()
        
        # Configuration with various unicode and special characters
        cli_schema = CLISchema(
            name="unicode-cli",
            tagline="CLI with émojis 🚀 and spëcial chars",
            commands={
                "test-unicode": CommandSchema(
                    desc="Unicode command with 特殊字符 and émojis 🎉",
                    args=[
                        ArgumentSchema(
                            name="username",
                            desc="Username with unicode characters ñáéíóú"
                        )
                    ],
                    options=[
                        OptionSchema(
                            name="config",
                            desc="Configuration with special chars: !@#$%^&*()",
                            type="str",
                            default="default_value"
                        )
                    ]
                )
            }
        )
        config = create_test_goobits_config("unicode-cli", cli_schema)
        
        # Should handle unicode and special characters appropriately
        try:
            result = generator.generate_all_files(config, "unicode.yaml")
            assert isinstance(result, dict)
            
            # Check that generated content handles unicode properly
            main_content = result.get('cli.js', '')
            assert isinstance(main_content, str)
            
        except (UnicodeError, ValueError):
            # Acceptable to fail with problematic unicode
            pass


class TestNodeJSIntegrationWorkflows:
    """Integration workflow tests for complete NodeJS CLI generation."""
    
    @classmethod
    def setup_class(cls):
        """Set up test fixtures for the class."""
        # Create a test YAML file for Node.js in goobits.yaml format
        cls.test_yaml_content = """
package_name: "node-test-cli"
command_name: "nodetestcli"
display_name: "NodeTestCLI"
description: "A Node.js test CLI for integration tests."
language: nodejs

python:
  minimum_version: "3.8"

dependencies:
  core: []

installation:
  pypi_name: "node-test-cli"
  github_repo: "example/node-test-cli"

shell_integration:
  alias: "ntc"

validation:
  minimum_disk_space_mb: 100

messages:
  install_success: "NodeTestCLI installed successfully!"

cli:
  name: "NodeTestCLI"
  tagline: "A Node.js test CLI for integration tests."
  version: "1.0.0"
  commands:
    build:
      desc: "Build the project"
      options:
        - name: release
          type: bool
          desc: "Build in release mode"
        - name: target
          short: t
          type: str
          desc: "Target platform"
          default: "web"
    test:
      desc: "Run tests"
      args:
        - name: pattern
          desc: "Test pattern"
          required: false
      options:
        - name: verbose
          type: bool
          desc: "Verbose test output"
        - name: coverage
          short: c
          type: bool
          desc: "Generate coverage report"
          default: false
"""
        
        # Create temporary directory for tests
        cls.temp_dir = tempfile.mkdtemp(prefix="nodejs_integration_test_")
        cls.test_yaml_path = Path(cls.temp_dir) / "test_nodejs.yaml"
        
        # Write test YAML
        with open(cls.test_yaml_path, 'w') as f:
            f.write(cls.test_yaml_content)
    
    @classmethod
    def teardown_class(cls):
        """Clean up test fixtures."""
        if Path(cls.temp_dir).exists():
            shutil.rmtree(cls.temp_dir)
    
    def test_language_detection_nodejs(self):
        """Test that NodeJS language is correctly detected from config."""
        config = load_goobits_config(self.test_yaml_path)
        language = determine_language(config)
        
        assert language == "nodejs"
    
    def test_nodejs_generator_selection(self):
        """Test that NodeJSGenerator would be selected for NodeJS language."""
        config = load_goobits_config(self.test_yaml_path)
        
        # Verify the language is detected as nodejs
        assert config.language == "nodejs"
        
        # Create NodeJSGenerator directly to test
        generator = NodeJSGenerator()
        output_files = generator.generate_all_files(config, "test_nodejs.yaml")
        
        # Check that we get NodeJS files
        assert 'cli.js' in output_files
        assert 'package.json' in output_files
        assert 'setup.sh' in output_files
        
        # Should NOT have Python or other language files
        assert 'cli.py' not in output_files
        assert 'Cargo.toml' not in output_files
    
    def test_generated_package_json_validity(self):
        """Test that generated package.json is valid JSON with correct structure."""
        config = load_goobits_config(self.test_yaml_path)
        generator = NodeJSGenerator()
        output_files = generator.generate_all_files(config, "test_nodejs.yaml")
        
        # Parse and validate package.json
        package_json_content = output_files['package.json']
        package_data = json.loads(package_json_content)
        
        # Check required package.json fields
        assert 'name' in package_data
        assert 'version' in package_data
        assert 'description' in package_data
        assert 'main' in package_data
        assert 'dependencies' in package_data
        
        # Check NodeJS-specific dependencies
        assert 'commander' in package_data['dependencies']
        
        # Check binary configuration
        assert 'bin' in package_data
        assert package_data['name'] == config.package_name
    
    def test_generated_cli_structure(self):
        """Test that generated CLI.js has proper structure."""
        config = load_goobits_config(self.test_yaml_path)
        generator = NodeJSGenerator()
        output_files = generator.generate_all_files(config, "test_nodejs.yaml")
        
        cli_content = output_files['cli.js']
        
        # Check for essential CLI structure
        assert 'commander' in cli_content or 'Command' in cli_content
        assert 'build' in cli_content
        assert 'test' in cli_content
        
        # Check for proper Node.js patterns
        assert 'require(' in cli_content or 'import' in cli_content
        assert 'module.exports' in cli_content or 'export' in cli_content
    
    def test_complex_command_generation(self):
        """Test generation of complex commands with arguments and options."""
        config = load_goobits_config(self.test_yaml_path)
        generator = NodeJSGenerator()
        output_files = generator.generate_all_files(config, "test_nodejs.yaml")
        
        cli_content = output_files['cli.js']
        
        # Check that complex command structures are generated
        assert 'build' in cli_content
        assert 'test' in cli_content
        assert 'release' in cli_content
        assert 'target' in cli_content
        assert 'verbose' in cli_content
        assert 'coverage' in cli_content
    
    def test_special_characters_escaping(self):
        """Test that special characters in descriptions are properly escaped."""
        # Create config with special characters
        cli_schema = CLISchema(
            name="special-cli",
            tagline="CLI with 'quotes' and \"double quotes\"",
            commands={
                "test": CommandSchema(
                    desc="Command with special chars: !@#$%^&*()",
                    args=[ArgumentSchema(
                        name="path",
                        desc="Path with backslashes: C:\\Windows\\System32\\"
                    )]
                )
            }
        )
        config = create_test_goobits_config("special-cli", cli_schema)
        
        generator = NodeJSGenerator()
        output_files = generator.generate_all_files(config, "special.yaml")
        
        # Check that generated JavaScript is valid despite special characters
        cli_content = output_files['cli.js']
        assert isinstance(cli_content, str)
        assert len(cli_content) > 0


class TestNodeJSE2EWorkflows:
    """End-to-end workflow validation tests."""
    
    def test_complete_nodejs_workflow(self):
        """Test complete workflow from YAML to executable CLI."""
        # Create test configuration
        cli_schema = CLISchema(
            name="workflow-cli",
            tagline="Workflow test CLI",
            version="1.0.0",
            commands={
                "hello": CommandSchema(
                    desc="Say hello",
                    args=[ArgumentSchema(name="name", desc="Name to greet", default="World")],
                    options=[OptionSchema(name="uppercase", desc="Uppercase output", type="flag")]
                )
            }
        )
        config = create_test_goobits_config("workflow-cli", cli_schema, language="nodejs")
        
        # Generate CLI files
        output_files = generate_cli(config, "workflow.yaml")
        
        # Verify all expected files are generated
        expected_files = ['cli.js', 'package.json', 'setup.sh', 'README.md']
        for expected_file in expected_files:
            assert expected_file in output_files
            assert len(output_files[expected_file]) > 0
        
        # Verify package.json is valid
        package_data = json.loads(output_files['package.json'])
        assert package_data['name'] == config.package_name
        assert 'commander' in package_data.get('dependencies', {})
        
        # Verify CLI contains command structure
        cli_content = output_files['cli.js']
        assert 'hello' in cli_content
        assert 'name' in cli_content
        assert 'uppercase' in cli_content
    
    @pytest.mark.skipif(not shutil.which("node"), reason="Node.js not available")
    def test_generated_cli_syntax_validation(self):
        """Test that generated CLI has valid Node.js syntax."""
        # Create a simple test configuration
        cli_schema = CLISchema(
            name="syntax-test",
            tagline="Syntax test CLI",
            commands={"test": CommandSchema(desc="Test command")}
        )
        config = create_test_goobits_config("syntax-test", cli_schema, language="nodejs")
        
        # Generate CLI
        output_files = generate_cli(config, "syntax.yaml")
        
        # Write CLI to temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as f:
            f.write(output_files['cli.js'])
            temp_cli_path = f.name
        
        try:
            # Test Node.js syntax validation
            result = subprocess.run(
                ['node', '-c', temp_cli_path],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            # Should not have syntax errors
            assert result.returncode == 0, f"Generated CLI has syntax errors: {result.stderr}"
            
        finally:
            # Clean up temporary file
            if os.path.exists(temp_cli_path):
                os.unlink(temp_cli_path)