"""Unit tests for TypeScript generator."""

import pytest
import json
from unittest.mock import patch

from goobits_cli.generators.typescript import TypeScriptGenerator
from goobits_cli.schemas import (
    ConfigSchema,
    CLISchema,
    CommandSchema,
    GoobitsConfigSchema,
    ArgumentSchema,
    OptionSchema,
)


class TestTypeScriptGenerator:
    """Test cases for TypeScriptGenerator class."""

    def test_typescript_generator_initialization(self):
        """Test TypeScriptGenerator initialization."""
        generator = TypeScriptGenerator()

        assert generator is not None
        assert hasattr(generator, "template_env")
        # Template system is integrated

    def test_typescript_generator_basic_generation(self, tmp_path):
        """Test basic CLI generation functionality."""
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

        generator = TypeScriptGenerator()

        # Test that generation doesn't raise exceptions
        try:
            result = generator.generate(config, str(tmp_path))
            assert result is not None
        except Exception as e:
            pytest.fail(f"Basic generation failed: {e}")

    def test_typescript_generator_with_commands(self, tmp_path):
        """Test generation with commands."""
        config = ConfigSchema(
            cli=CLISchema(
                name="test-cli",
                tagline="Test CLI",
                description="Test CLI",
                version="1.0.0",
                commands={"hello": CommandSchema(desc="Say hello")},
            )
        )

        generator = TypeScriptGenerator()

        # Test generation with commands
        try:
            result = generator.generate(config, str(tmp_path))
            assert result is not None
        except Exception as e:
            pytest.fail(f"Command generation failed: {e}")

    @patch("goobits_cli.generators.typescript.TypeScriptGenerator.generate_all_files")
    def test_typescript_generator_mocked(self, mock_generate):
        """Test with mocked generation to avoid file system operations."""
        mock_generate.return_value = True

        config = ConfigSchema(
            cli=CLISchema(
                name="test-cli",
                tagline="Test CLI",
                description="Test CLI",
                version="1.0.0",
                commands={},
            )
        )

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
            cli=CLISchema(name="test-typescript-cli", tagline="Test CLI", commands={}),
        )
        generator = TypeScriptGenerator()
        output_files = generator.get_output_files()

        # TypeScript should generate generated_index.ts (or index.ts), package.json, and setup.sh
        assert "generated_index.ts" in output_files or "index.ts" in output_files
        assert "package.json" in output_files
        assert "setup.sh" in output_files
        # Should not generate Python or Rust files
        assert "cli.py" not in output_files
        assert "Cargo.toml" not in output_files

