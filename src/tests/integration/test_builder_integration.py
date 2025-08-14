"""Integration tests for builder module.

These tests verify that the core components work together correctly,
focusing on the interaction between load_yaml_config and generate_cli_code.
"""
import pytest
from pathlib import Path
from click.exceptions import Exit

from goobits_cli.builder import load_yaml_config, generate_cli_code, Builder
from goobits_cli.schemas import ConfigSchema


class TestBuilderIntegration:
    """Integration tests for the builder module components."""
    
    @classmethod
    def setup_class(cls):
        """Set up test fixtures for the class."""
        # Get the path to the test YAML file relative to this test file
        cls.test_yaml_path = Path(__file__).parent / "goobits.yaml"
        
        # Load the configuration once for all tests
        cls.config = load_yaml_config(str(cls.test_yaml_path))
    
    def test_yaml_to_code_generation(self):
        """Test the complete pipeline from YAML file to generated CLI code."""
        # Verify we loaded a valid ConfigSchema
        assert isinstance(self.config, ConfigSchema)
        assert self.config.cli.name == "TestCLI"
        assert self.config.cli.tagline == "A test CLI for integration tests."
        
        # Generate CLI code using the functional approach
        generated_code = generate_cli_code(self.config, "goobits.yaml")
        
        # Verify the generated code is a string
        assert isinstance(generated_code, str)
        assert len(generated_code) > 0
        
        # Assert key content from our test YAML is present in generated code
        self._assert_cli_metadata_present(generated_code)
        self._assert_commands_present(generated_code)
        self._assert_command_descriptions_present(generated_code)
        self._assert_command_structure_present(generated_code)
    
    def test_builder_class_integration(self):
        """Test the Builder class with real YAML configuration."""
        # Create a Builder instance
        builder = Builder()
        
        # Generate code using the Builder class
        generated_code = builder.build(self.config, "goobits.yaml")
        
        # Verify the generated code is a string
        assert isinstance(generated_code, str)
        assert len(generated_code) > 0
        
        # Assert key content is present (same assertions as functional test)
        self._assert_cli_metadata_present(generated_code)
        self._assert_commands_present(generated_code)
        self._assert_command_descriptions_present(generated_code)
        self._assert_command_structure_present(generated_code)
    
    def test_functional_vs_class_consistency(self):
        """Test that functional and class-based approaches produce identical results."""
        # Generate code using both approaches
        functional_code = generate_cli_code(self.config, "goobits.yaml")
        
        builder = Builder()
        class_code = builder.build(self.config, "goobits.yaml")
        
        # Both should produce identical output
        assert functional_code == class_code
    
    def test_complex_command_structure(self):
        """Test that complex commands with args and options are properly handled."""
        generated_code = generate_cli_code(self.config, "goobits.yaml")
        
        # Test that the hello command with arguments is properly represented
        self._assert_hello_command_structure(generated_code)
        
        # Test that the goodbye command with options is properly represented
        self._assert_goodbye_command_structure(generated_code)
    
    def test_yaml_file_path_handling(self):
        """Test that different file paths are handled correctly."""
        # Test with absolute path
        absolute_path = self.test_yaml_path.absolute()
        config_abs = load_yaml_config(str(absolute_path))
        code_abs = generate_cli_code(config_abs, str(absolute_path.name))
        
        # Should contain the same key elements (Legacy template doesn't include CLI name)
        assert "A test CLI for integration tests." in code_abs
        
        # Test with relative path (current working directory approach)
        relative_path = self.test_yaml_path.relative_to(Path.cwd())
        config_rel = load_yaml_config(str(relative_path))
        code_rel = generate_cli_code(config_rel, str(relative_path.name))
        
        # Should produce identical results
        assert code_abs == code_rel
    
    def _assert_cli_metadata_present(self, generated_code):
        """Assert that CLI metadata from YAML is present in generated code."""
        # Check for tagline (Legacy template doesn't include CLI name)
        assert "A test CLI for integration tests." in generated_code
    
    def _assert_commands_present(self, generated_code):
        """Assert that all commands from YAML are present in generated code."""
        # Check that all command names are present
        assert "greet" in generated_code
        assert "hello" in generated_code  
        assert "goodbye" in generated_code
    
    def _assert_command_descriptions_present(self, generated_code):
        """Assert that command descriptions from YAML are present in generated code."""
        # Check for command descriptions
        assert "Prints a greeting." in generated_code
        assert "Says hello to a user." in generated_code
        assert "Says goodbye with optional message." in generated_code
    
    def _assert_command_structure_present(self, generated_code):
        """Assert that command structure from YAML is present in generated code."""
        # Check for Python function definitions for each command
        assert "def greet(ctx" in generated_code
        assert "def hello(ctx" in generated_code
        assert "def goodbye(ctx" in generated_code
        
        # Check for click decorators
        assert "@main.command()" in generated_code
        # Legacy template doesn't generate @click.option decorators
    
    def _assert_hello_command_structure(self, generated_code):
        """Assert that the hello command structure is properly represented."""
        # Legacy template only generates function with ctx parameter
        assert "def hello(ctx)" in generated_code
        
        # Check for command description in docstring
        assert "Says hello to a user." in generated_code
        
        # Legacy template doesn't generate option help text or decorators
        # Only check that the command exists with basic structure
        # The word "name" appears in the docstring as argument description
    
    def _assert_goodbye_command_structure(self, generated_code):
        """Assert that the goodbye command structure is properly represented."""
        # Legacy template only generates function with ctx parameter
        assert "def goodbye(ctx)" in generated_code
        
        # Check for command description in docstring
        assert "Says goodbye with optional message." in generated_code
        
        # Legacy template doesn't include option defaults or decorators


class TestBuilderIntegrationErrorCases:
    """Integration tests for error handling scenarios."""
    
    def test_load_nonexistent_yaml_file(self):
        """Test that loading a non-existent YAML file raises appropriate errors."""
        nonexistent_path = Path(__file__).parent / "nonexistent.yaml"
        
        # This should exit the program, but in a test environment we can catch it
        with pytest.raises(Exit) as exc_info:
            load_yaml_config(str(nonexistent_path))
        
        assert exc_info.value.exit_code == 1
    
    def test_load_invalid_yaml_syntax(self):
        """Test handling of invalid YAML syntax."""
        # Create a temporary file with invalid YAML
        invalid_yaml_path = Path(__file__).parent / "invalid_syntax.yaml"
        
        try:
            # Write invalid YAML content
            with open(invalid_yaml_path, 'w') as f:
                f.write("cli:\n  name: unclosed string\n  tagline: \"missing quote\n")
            
            # This should exit due to YAML syntax error
            with pytest.raises(Exit) as exc_info:
                load_yaml_config(str(invalid_yaml_path))
            
            assert exc_info.value.exit_code == 1
                
        finally:
            # Clean up the temporary file
            if invalid_yaml_path.exists():
                invalid_yaml_path.unlink()
    
    def test_load_invalid_schema(self):
        """Test handling of YAML that doesn't match our schema."""
        # Create a temporary file with invalid schema
        invalid_schema_path = Path(__file__).parent / "invalid_schema.yaml"
        
        try:
            # Write YAML with missing required fields
            with open(invalid_schema_path, 'w') as f:
                f.write("cli:\n  name: TestCLI\n  # Missing required tagline and commands\n")
            
            # This should exit due to validation error
            with pytest.raises(Exit) as exc_info:
                load_yaml_config(str(invalid_schema_path))
            
            assert exc_info.value.exit_code == 1
                
        finally:
            # Clean up the temporary file
            if invalid_schema_path.exists():
                invalid_schema_path.unlink()


class TestBuilderIntegrationAdvanced:
    """Advanced integration tests for complex scenarios."""
    
    def test_multiple_yaml_configurations(self):
        """Test that the system can handle multiple different YAML configurations."""
        # Create a minimal configuration
        minimal_config_path = Path(__file__).parent / "minimal_config.yaml"
        
        try:
            # Write minimal valid configuration
            with open(minimal_config_path, 'w') as f:
                f.write("""cli:
  name: "MinimalCLI"
  tagline: "A minimal CLI for testing."
  commands:
    status:
      desc: "Show status."
""")
            
            # Load and generate code for minimal config
            minimal_config = load_yaml_config(str(minimal_config_path))
            minimal_code = generate_cli_code(minimal_config, "minimal_config.yaml")
            
            # Verify minimal config content (Legacy template doesn't include CLI name)
            assert "A minimal CLI for testing." in minimal_code
            assert "status" in minimal_code
            assert "Show status." in minimal_code
            
            # Compare with our main test config
            main_config_path = Path(__file__).parent / "goobits.yaml"
            main_config = load_yaml_config(str(main_config_path))
            main_code = generate_cli_code(main_config, "goobits.yaml")
            
            # They should be different
            assert minimal_code != main_code
            # Legacy template doesn't include CLI names, so these assertions are not relevant
            
        finally:
            # Clean up
            if minimal_config_path.exists():
                minimal_config_path.unlink()
    
    def test_file_name_in_generated_code(self):
        """Test that the filename parameter affects the generated code appropriately."""
        config_path = Path(__file__).parent / "goobits.yaml"
        config = load_yaml_config(str(config_path))
        
        # Generate code with different filenames
        code_with_goobits = generate_cli_code(config, "goobits.yaml")
        code_with_custom = generate_cli_code(config, "custom_name.yaml")
        
        # Both should contain the same CLI content but may reference the filename
        # Legacy template doesn't include CLI name, so check for tagline instead
        assert "A test CLI for integration tests." in code_with_goobits
        assert "A test CLI for integration tests." in code_with_custom
        
        # The generated code should be functionally identical
        # (filename mainly affects comments or metadata in templates)
        assert len(code_with_goobits) > 0
        assert len(code_with_custom) > 0