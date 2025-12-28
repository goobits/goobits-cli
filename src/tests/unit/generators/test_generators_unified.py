"""Unified parameterized tests for all language generators.

This module provides consolidated tests that validate common patterns
across all language generators (Python, Node.js, TypeScript, Rust).
These tests use parameterized fixtures to avoid code duplication while
ensuring consistent behavior across all supported languages.

The existing language-specific test files remain in place for:
- Language-specific edge cases
- Detailed validation of language-unique features
- Backward compatibility

This file focuses on:
- Common initialization patterns
- Basic generation functionality
- Command handling across all languages
"""

import pytest
from goobits_cli.generation.renderers.python import PythonGenerator
from goobits_cli.generation.renderers.nodejs import NodeJSGenerator
from goobits_cli.generation.renderers.typescript import TypeScriptGenerator
from goobits_cli.generation.renderers.rust import RustGenerator
from goobits_cli.core.schemas import (
    ConfigSchema,
    CLISchema,
    CommandSchema,
    GoobitsConfigSchema,
)
from ...conftest import create_test_goobits_config


class TestGeneratorInitialization:
    """Test initialization patterns for all generators."""

    def test_generator_initialization(self, parameterized_generator):
        """Test that all generators initialize correctly with required attributes."""
        generator, language = parameterized_generator

        # All generators should have a template environment
        assert generator is not None

        # Check for template environment (attribute name varies by generator)
        has_template_env = (
            hasattr(generator, "template_env")
            or hasattr(generator, "env")
            or hasattr(generator, "jinja_env")
        )
        assert has_template_env, (
            f"{language} generator missing template environment attribute"
        )

    def test_generator_has_generate_method(self, parameterized_generator):
        """Test that all generators have a generate method."""
        generator, language = parameterized_generator

        assert hasattr(generator, "generate"), (
            f"{language} generator missing generate method"
        )
        assert callable(generator.generate), (
            f"{language} generator.generate is not callable"
        )

    def test_generator_has_generate_all_files_method(self, parameterized_generator):
        """Test that all generators have a generate_all_files method."""
        generator, language = parameterized_generator

        assert hasattr(generator, "generate_all_files"), (
            f"{language} generator missing generate_all_files method"
        )
        assert callable(generator.generate_all_files), (
            f"{language} generator.generate_all_files is not callable"
        )

    def test_generator_has_get_output_files_method(self, parameterized_generator):
        """Test that all generators have a get_output_files method."""
        generator, language = parameterized_generator

        assert hasattr(generator, "get_output_files"), (
            f"{language} generator missing get_output_files method"
        )
        assert callable(generator.get_output_files), (
            f"{language} generator.get_output_files is not callable"
        )


class TestGeneratorBasicGeneration:
    """Test basic generation functionality across all generators."""

    def test_generator_basic_generation(self, parameterized_generator, tmp_path):
        """Test that all generators can perform basic CLI generation."""
        generator, language = parameterized_generator

        # Create a minimal config
        config = ConfigSchema(
            cli=CLISchema(
                name="test-cli",
                tagline="Test CLI",
                description="Test CLI",
                version="1.0.0",
                commands={},
            )
        )

        # Test that generation doesn't raise exceptions
        try:
            result = generator.generate(config, str(tmp_path))
            assert result is not None, (
                f"{language} generator returned None for basic generation"
            )
        except Exception as e:
            pytest.fail(f"{language} generator basic generation failed: {e}")

    def test_generator_returns_content(self, parameterized_generator, basic_cli_schema):
        """Test that all generators return non-empty content."""
        generator, language = parameterized_generator

        config = create_test_goobits_config(
            package_name=f"test-{language}-cli",
            cli=basic_cli_schema,
            language=language,
        )

        output_files = generator.generate_all_files(config, "test.yaml")

        # All generators should return a dictionary of files
        assert isinstance(output_files, dict), (
            f"{language} generator did not return a dict"
        )
        assert len(output_files) > 0, (
            f"{language} generator returned empty file dict"
        )

        # All generated files should have content
        for filename, content in output_files.items():
            assert content is not None, (
                f"{language} generator returned None for {filename}"
            )
            assert len(content) > 0, (
                f"{language} generator returned empty content for {filename}"
            )


class TestGeneratorWithCommands:
    """Test command generation across all generators."""

    def test_generator_with_commands(self, parameterized_generator, tmp_path):
        """Test that all generators can generate CLIs with commands."""
        generator, language = parameterized_generator

        config = ConfigSchema(
            cli=CLISchema(
                name="test-cli",
                tagline="Test CLI",
                description="Test CLI",
                version="1.0.0",
                commands={"hello": CommandSchema(desc="Say hello")},
            )
        )

        # Test generation with commands
        try:
            result = generator.generate(config, str(tmp_path))
            assert result is not None, (
                f"{language} generator returned None for command generation"
            )
        except Exception as e:
            pytest.fail(f"{language} generator command generation failed: {e}")

    def test_generator_command_appears_in_output(
        self, parameterized_generator, basic_cli_schema
    ):
        """Test that commands appear in generated output."""
        generator, language = parameterized_generator

        config = create_test_goobits_config(
            package_name=f"test-{language}-cli",
            cli=basic_cli_schema,
            language=language,
        )

        output_files = generator.generate_all_files(config, "test.yaml")

        # Find the main CLI file and check for command reference
        # Different languages use different main file extensions
        main_extensions = {
            "python": ".py",
            "nodejs": ".mjs",
            "typescript": ".ts",
            "rust": ".rs",
        }

        expected_ext = main_extensions.get(language, ".py")
        cli_files = [f for f in output_files.keys() if f.endswith(expected_ext)]

        assert len(cli_files) > 0, (
            f"No {expected_ext} files found for {language}: {list(output_files.keys())}"
        )

        # Check that at least one CLI file contains the command
        # The basic_cli_schema has a "test" command
        command_found = False
        for cli_file in cli_files:
            content = output_files[cli_file]
            if "test" in content.lower():
                command_found = True
                break

        assert command_found, (
            f"{language} generator output does not contain 'test' command"
        )


class TestLanguageTestConfig:
    """Test the language_test_config parameterized fixture."""

    def test_language_test_config_creates_valid_config(self, language_test_config):
        """Test that language_test_config creates valid configurations."""
        config = language_test_config

        # Should be a GoobitsConfigSchema
        assert isinstance(config, GoobitsConfigSchema)

        # Should have required fields
        assert config.package_name is not None
        assert config.language in ["python", "nodejs", "typescript", "rust"]
        assert config.cli is not None

    def test_language_test_config_has_correct_language(self, language_test_config):
        """Test that config language matches package name."""
        config = language_test_config

        # Package name should contain the language
        assert config.language in config.package_name, (
            f"Package name {config.package_name} does not contain language {config.language}"
        )

    def test_language_test_config_has_cli_schema(self, language_test_config):
        """Test that config has a valid CLI schema."""
        config = language_test_config

        assert config.cli is not None
        assert isinstance(config.cli, CLISchema)
        assert config.cli.commands is not None
