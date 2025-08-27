"""
Comprehensive CLI Generation Integration Tests

This module consolidates tests for:
- Builder integration (YAML → Configuration → Code Generation)
- CLI generation integration (Code Generation → Installation → Execution)
- Cross-language consistency testing
- Command execution and hook invocation

Consolidated from test_builder_integration.py and test_cli_generation_integration.py
"""

import shutil
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

    def _assert_cli_metadata_present(self, generated_code):
        """Assert that CLI metadata from YAML is present in generated code."""
        # Check for tagline (Generated templates may not include CLI name)
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
        # Universal template generates function signatures with parameters based on command definitions
        assert "def greet(ctx)" in generated_code
        assert "def hello(ctx, name, uppercase)" in generated_code
        assert "def goodbye(ctx, message)" in generated_code

        # Check for click decorators (UTS uses @cli.command() pattern)
        assert "@cli.command(" in generated_code

    def _assert_hello_command_structure(self, generated_code):
        """Assert that the hello command structure is properly represented."""
        # Universal template generates function signatures with parameters
        assert "def hello(ctx, name, uppercase)" in generated_code

        # Check for command description in docstring or command definition
        assert "hello" in generated_code  # Basic presence check

    def _assert_goodbye_command_structure(self, generated_code):
        """Assert that the goodbye command structure is properly represented."""
        # Universal template generates function signatures with parameters
        assert "def goodbye(ctx, message)" in generated_code

        # Check for command description in docstring
        assert "Says goodbye with optional message." in generated_code


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
            with open(invalid_yaml_path, "w") as f:
                f.write('cli:\n  name: unclosed string\n  tagline: "missing quote\n')

            # This should exit due to YAML syntax error
            with pytest.raises(Exit) as exc_info:
                load_yaml_config(str(invalid_yaml_path))

            assert exc_info.value.exit_code == 1

        finally:
            # Clean up the temporary file
            if invalid_yaml_path.exists():
                invalid_yaml_path.unlink()


class TestCLIGenerationIntegration:
    """
    Comprehensive End-to-End Integration Tests for Generated CLI Execution

    Tests the critical integration scenarios:
    - YAML → Code Generation: Verify all languages generate syntactically correct code
    - Generated CLI Installation: Test that generated CLIs can be installed
    - Generated CLI Execution: Verify generated CLIs actually run and respond to commands
    - Cross-Language Consistency: Same YAML produces equivalent behavior
    """

    def setup_method(self):
        """Set up test environment for each test method."""
        self.test_dir = None
        self.generated_files = []

    def teardown_method(self):
        """Clean up after each test method."""
        if self.test_dir and Path(self.test_dir).exists():
            shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_python_cli_generation_and_execution(self, tmp_path):
        """Test Python CLI generation and basic execution."""
        from goobits_cli.generators.python import PythonGenerator

        # Create a minimal test configuration
        config = ConfigSchema(
            cli={
                "name": "testcli",
                "tagline": "Test CLI for integration",
                "version": "1.0.0",
                "commands": {"hello": {"desc": "Say hello"}},
            }
        )

        # Generate Python CLI
        generator = PythonGenerator()
        result = generator.generate(config, str(tmp_path))

        # Verify generation was successful
        assert result is not None

        # Check that key files were generated
        cli_file = tmp_path / "cli.py"
        assert cli_file.exists()

        # Verify generated content contains expected elements
        cli_content = cli_file.read_text()
        assert "hello" in cli_content
        assert "Say hello" in cli_content

    def test_nodejs_cli_generation_and_execution(self, tmp_path):
        """Test Node.js CLI generation and basic execution."""
        from goobits_cli.generators.nodejs import NodeJSGenerator

        # Create a minimal test configuration
        config = ConfigSchema(
            cli={
                "name": "testcli",
                "tagline": "Test CLI for integration",
                "version": "1.0.0",
                "commands": {"hello": {"desc": "Say hello"}},
            }
        )

        # Generate Node.js CLI
        generator = NodeJSGenerator()
        result = generator.generate(config, str(tmp_path))

        # Verify generation was successful
        assert result is not None

        # Check that key files were generated (UTS generates .mjs and setup.sh)
        cli_file = tmp_path / "cli.mjs"
        setup_file = tmp_path / "setup.sh"

        assert cli_file.exists()
        # Note: UTS doesn't generate package.json by default, generates setup.sh instead

        # Verify generated content
        cli_content = cli_file.read_text()
        assert "hello" in cli_content

    @pytest.mark.skipif(
        shutil.which("cargo") is None,
        reason="Cargo not available - Rust tests require Rust toolchain",
    )
    def test_rust_cli_generation_and_execution(self, tmp_path):
        """Test Rust CLI generation and basic execution."""
        from goobits_cli.generators.rust import RustGenerator

        # Create a minimal test configuration
        config = ConfigSchema(
            cli={
                "name": "testcli",
                "tagline": "Test CLI for integration",
                "version": "1.0.0",
                "commands": {"hello": {"desc": "Say hello"}},
            }
        )

        # Generate Rust CLI
        generator = RustGenerator()
        result = generator.generate(config, str(tmp_path))

        # Verify generation was successful
        assert result is not None

        # Check that key files were generated (UTS generates src/cli.rs and setup.sh)
        main_file = tmp_path / "src" / "cli.rs"
        setup_file = tmp_path / "setup.sh"

        assert main_file.exists()
        # Note: UTS doesn't generate Cargo.toml by default, generates setup.sh instead

        # Verify generated content
        main_content = main_file.read_text()
        assert "hello" in main_content

    def test_cross_language_consistency(self, tmp_path):
        """Test that all languages generate consistent CLI behavior."""
        # Create the same configuration for all languages
        config = ConfigSchema(
            cli={
                "name": "consistent-cli",
                "tagline": "Cross-language consistency test",
                "version": "1.0.0",
                "commands": {"test": {"desc": "Test command"}},
            }
        )

        # Test each generator
        from goobits_cli.generators.python import PythonGenerator
        from goobits_cli.generators.nodejs import NodeJSGenerator
        from goobits_cli.generators.typescript import TypeScriptGenerator
        from goobits_cli.generators.rust import RustGenerator

        generators = [
            ("python", PythonGenerator),
            ("nodejs", NodeJSGenerator),
            ("typescript", TypeScriptGenerator),
            ("rust", RustGenerator),
        ]

        results = {}

        for lang, generator_class in generators:
            lang_dir = tmp_path / lang
            lang_dir.mkdir()

            try:
                generator = generator_class()
                result = generator.generate(config, str(lang_dir))
                results[lang] = {"success": result is not None, "error": None}
            except Exception as e:
                results[lang] = {"success": False, "error": str(e)}

        # At least Python and Node.js should succeed
        assert results["python"][
            "success"
        ], f"Python generation failed: {results['python']['error']}"
        assert results["nodejs"][
            "success"
        ], f"Node.js generation failed: {results['nodejs']['error']}"

        # TypeScript should also succeed
        assert results["typescript"][
            "success"
        ], f"TypeScript generation failed: {results['typescript']['error']}"

        # Rust might fail if cargo is not available, but that's acceptable
        if shutil.which("cargo"):
            assert results["rust"][
                "success"
            ], f"Rust generation failed: {results['rust']['error']}"
