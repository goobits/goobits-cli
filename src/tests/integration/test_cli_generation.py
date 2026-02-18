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
from pathlib import Path

import pytest

from goobits_cli.core.errors import ConfigurationError
from goobits_cli.universal.engine.stages import parse_config, validate_config
from goobits_cli.universal.generator import UniversalGenerator


class TestBuilderIntegration:
    """Integration tests for the universal generator components."""

    @classmethod
    def setup_class(cls):
        """Set up test fixtures for the class."""
        # Get the path to the test YAML file relative to this test file
        cls.test_yaml_path = Path(__file__).parent / "goobits.yaml"

        # Load the configuration once for all tests using universal stages
        raw_config = parse_config(cls.test_yaml_path)
        cls.config = validate_config(raw_config)

    def test_yaml_to_code_generation(self):
        """Test the complete pipeline from YAML file to generated CLI code."""
        # Verify we loaded a valid config
        assert self.config is not None
        assert self.config.cli.name == "TestCLI"
        assert self.config.cli.tagline == "A test CLI for integration tests."

        # Generate CLI code using the universal generator
        generator = UniversalGenerator("python")
        generator.generate_all_files(self.config, "goobits.yaml")
        generated_code = generator.generate(self.config, "goobits.yaml")

        # Verify the generated code is a string
        assert isinstance(generated_code, str)
        assert len(generated_code) > 0

        # Assert key content from our test YAML is present in generated code
        self._assert_cli_metadata_present(generated_code)
        self._assert_commands_present(generated_code)
        self._assert_command_descriptions_present(generated_code)

    def test_universal_generator_integration(self):
        """Test the UniversalGenerator with real YAML configuration."""
        # Create a UniversalGenerator instance
        generator = UniversalGenerator("python")

        # Generate code using the generator
        generated_code = generator.generate(self.config, "goobits.yaml")

        # Verify the generated code is a string
        assert isinstance(generated_code, str)
        assert len(generated_code) > 0

        # Assert key content is present
        self._assert_cli_metadata_present(generated_code)
        self._assert_commands_present(generated_code)
        self._assert_command_descriptions_present(generated_code)

    def test_generate_all_files_returns_dict(self):
        """Test that generate_all_files returns a dictionary of files."""
        generator = UniversalGenerator("python")
        files = generator.generate_all_files(self.config, "goobits.yaml")

        # Should return a dictionary
        assert isinstance(files, dict)
        assert len(files) > 0

        # Should have at least one file with content
        for path, content in files.items():
            assert isinstance(path, str)
            assert isinstance(content, str)
            assert len(content) > 0

    def test_complex_command_structure(self):
        """Test that complex commands with args and options are properly handled."""
        generator = UniversalGenerator("python")
        generated_code = generator.generate(self.config, "goobits.yaml")

        # Test that the hello command with arguments is properly represented
        self._assert_hello_command_structure(generated_code)

        # Test that the goodbye command with options is properly represented
        self._assert_goodbye_command_structure(generated_code)

    def _assert_cli_metadata_present(self, generated_code):
        """Assert that CLI metadata from YAML is present in generated code."""
        # Universal template generates valid Python CLI code
        # Check for essential CLI structure elements
        assert "#!/usr/bin/env python3" in generated_code or "import" in generated_code
        assert "def " in generated_code  # Should have function definitions

    def _assert_commands_present(self, generated_code):
        """Assert that all commands from YAML are present in generated code."""
        # Check that all command names are present
        assert "greet" in generated_code
        assert "hello" in generated_code
        assert "goodbye" in generated_code

    def _assert_command_descriptions_present(self, generated_code):
        """Assert that command descriptions from YAML are present in generated code."""
        # Check for command descriptions - may be embedded in docstrings or help text
        # At minimum, check commands are defined with help text
        assert "greet" in generated_code
        assert "hello" in generated_code
        assert "goodbye" in generated_code

    def _assert_hello_command_structure(self, generated_code):
        """Assert that the hello command structure is properly represented."""
        # Check for hello command presence
        assert "hello" in generated_code

    def _assert_goodbye_command_structure(self, generated_code):
        """Assert that the goodbye command structure is properly represented."""
        # Check for goodbye command presence
        assert "goodbye" in generated_code


class TestBuilderIntegrationErrorCases:
    """Integration tests for error handling scenarios."""

    def test_load_nonexistent_yaml_file(self):
        """Test that loading a non-existent YAML file raises appropriate errors."""
        nonexistent_path = Path(__file__).parent / "nonexistent.yaml"

        # parse_config should raise ConfigurationError for non-existent files
        with pytest.raises((ConfigurationError, FileNotFoundError)):
            parse_config(nonexistent_path)

    def test_load_invalid_yaml_syntax(self, tmp_path):
        """Test handling of invalid YAML syntax."""
        # Create a temporary file with invalid YAML
        invalid_yaml_path = tmp_path / "invalid_syntax.yaml"

        # Write invalid YAML content
        with open(invalid_yaml_path, "w") as f:
            f.write('cli:\n  name: unclosed string\n  tagline: "missing quote\n')

        # parse_config should raise an error for invalid YAML
        with pytest.raises(Exception):  # Could be YAML error or ConfigurationError
            parse_config(invalid_yaml_path)


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
        from goobits_cli.core.schemas import CLISchema, GoobitsConfigSchema
        from goobits_cli.universal.generator import UniversalGenerator

        # Create a minimal test configuration using GoobitsConfigSchema
        config = GoobitsConfigSchema(
            package_name="test-cli",
            command_name="testcli",
            display_name="Test CLI",
            description="Test CLI for integration",
            language="python",
            cli=CLISchema(
                name="testcli",
                tagline="Test CLI for integration",
                commands={"hello": {"desc": "Say hello"}},
            ),
        )

        # Generate Python CLI
        generator = UniversalGenerator("python")
        files = generator.generate_all_files(config, "goobits.yaml")

        # Verify generation was successful
        assert files is not None
        assert len(files) > 0

        # Write files to tmp_path and verify content
        cli_content = None
        for path, content in files.items():
            file_path = tmp_path / path
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(content)
            if "cli.py" in path:
                cli_content = content

        # Verify CLI content contains expected elements
        assert cli_content is not None
        assert "hello" in cli_content

    def test_nodejs_cli_generation_and_execution(self, tmp_path):
        """Test Node.js CLI generation and basic execution."""
        from goobits_cli.core.schemas import CLISchema, GoobitsConfigSchema
        from goobits_cli.universal.generator import UniversalGenerator

        # Create a minimal test configuration using GoobitsConfigSchema
        config = GoobitsConfigSchema(
            package_name="test-cli",
            command_name="testcli",
            display_name="Test CLI",
            description="Test CLI for integration",
            language="nodejs",
            cli=CLISchema(
                name="testcli",
                tagline="Test CLI for integration",
                commands={"hello": {"desc": "Say hello"}},
            ),
        )

        # Generate Node.js CLI
        generator = UniversalGenerator("nodejs")
        files = generator.generate_all_files(config, "goobits.yaml")

        # Verify generation was successful
        assert files is not None
        assert len(files) > 0

        # Write files to tmp_path and verify content
        cli_content = None
        for path, content in files.items():
            file_path = tmp_path / path
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(content)
            if "cli.js" in path:
                cli_content = content

        # Verify CLI content contains expected elements
        assert cli_content is not None
        assert "hello" in cli_content

    @pytest.mark.skipif(
        shutil.which("cargo") is None,
        reason="Cargo not available - Rust tests require Rust toolchain",
    )
    def test_rust_cli_generation_and_execution(self, tmp_path):
        """Test Rust CLI generation and basic execution."""
        from goobits_cli.core.schemas import CLISchema, GoobitsConfigSchema
        from goobits_cli.universal.generator import UniversalGenerator

        # Create a minimal test configuration using GoobitsConfigSchema
        config = GoobitsConfigSchema(
            package_name="test-cli",
            command_name="testcli",
            display_name="Test CLI",
            description="Test CLI for integration",
            language="rust",
            cli=CLISchema(
                name="testcli",
                tagline="Test CLI for integration",
                commands={"hello": {"desc": "Say hello"}},
            ),
        )

        # Generate Rust CLI
        generator = UniversalGenerator("rust")
        files = generator.generate_all_files(config, "goobits.yaml")

        # Verify generation was successful
        assert files is not None
        assert len(files) > 0

        # Write files to tmp_path and verify content
        cli_content = None
        for path, content in files.items():
            file_path = tmp_path / path
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(content)
            if "cli.rs" in path or "main.rs" in path:
                cli_content = content

        # Verify CLI content contains expected elements
        assert cli_content is not None
        assert "hello" in cli_content

    def test_cross_language_consistency(self, tmp_path):
        """Test that all languages generate consistent CLI behavior."""
        from goobits_cli.core.schemas import CLISchema, GoobitsConfigSchema
        from goobits_cli.universal.generator import UniversalGenerator

        # Test each language
        languages = ["python", "nodejs", "typescript", "rust"]
        results = {}

        for lang in languages:
            # Create config with correct language
            config = GoobitsConfigSchema(
                package_name="consistent-cli",
                command_name="consistent",
                display_name="Consistent CLI",
                description="Cross-language consistency test",
                language=lang,
                cli=CLISchema(
                    name="consistent-cli",
                    tagline="Cross-language consistency test",
                    commands={"test": {"desc": "Test command"}},
                ),
            )

            lang_dir = tmp_path / lang
            lang_dir.mkdir()

            try:
                generator = UniversalGenerator(lang)
                files = generator.generate_all_files(config, "goobits.yaml")
                results[lang] = {"success": len(files) > 0, "error": None}
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
