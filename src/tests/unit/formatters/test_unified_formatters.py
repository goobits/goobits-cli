"""
Tests for Unified Help Formatters

These tests verify that the unified formatter system generates consistent
help output configuration across all supported languages.
"""

import pytest

from goobits_cli.universal.formatters import (
    HelpFormatSpec,
    DEFAULT_FORMAT,
    PythonHelpFormatter,
    NodeJSHelpFormatter,
    TypeScriptHelpFormatter,
    RustHelpFormatter,
)


class TestHelpFormatSpec:
    """Tests for the unified help format specification."""

    def test_default_format_exists(self):
        """Default format spec should be available."""
        assert DEFAULT_FORMAT is not None
        assert isinstance(DEFAULT_FORMAT, HelpFormatSpec)

    def test_default_headers(self):
        """Default section headers should be uppercase."""
        spec = DEFAULT_FORMAT
        assert spec.usage_header == "USAGE"
        assert spec.arguments_header == "ARGUMENTS"
        assert spec.options_header == "OPTIONS"
        assert spec.commands_header == "COMMANDS"

    def test_format_option_signature_short_only(self):
        """Option signature with short flag only."""
        spec = DEFAULT_FORMAT
        result = spec.format_option_signature(short="v", long=None)
        assert result == "-v"

    def test_format_option_signature_long_only(self):
        """Option signature with long flag only."""
        spec = DEFAULT_FORMAT
        result = spec.format_option_signature(short=None, long="verbose")
        assert result == "--verbose"

    def test_format_option_signature_both(self):
        """Option signature with both short and long flags."""
        spec = DEFAULT_FORMAT
        result = spec.format_option_signature(short="v", long="verbose")
        assert result == "-v, --verbose"

    def test_format_option_signature_with_value(self):
        """Option signature with value type."""
        spec = DEFAULT_FORMAT
        result = spec.format_option_signature(
            short="o", long="output", value_type="path"
        )
        assert result == "-o, --output <PATH>"

    def test_format_argument_signature_required(self):
        """Argument signature for required argument."""
        spec = DEFAULT_FORMAT
        result = spec.format_argument_signature("input", required=True)
        assert result == "<INPUT>"

    def test_format_argument_signature_optional(self):
        """Argument signature for optional argument."""
        spec = DEFAULT_FORMAT
        result = spec.format_argument_signature("output", required=False)
        assert result == "[OUTPUT]"

    def test_format_argument_signature_variadic(self):
        """Argument signature for variadic argument."""
        spec = DEFAULT_FORMAT
        result = spec.format_argument_signature("files", variadic=True)
        assert result == "[FILES...]"

    def test_format_usage_line_no_commands(self):
        """Usage line without subcommands."""
        spec = DEFAULT_FORMAT
        result = spec.format_usage_line("mycli", has_commands=False)
        assert "mycli" in result
        assert "[OPTIONS]" in result

    def test_format_usage_line_with_commands(self):
        """Usage line with subcommands."""
        spec = DEFAULT_FORMAT
        result = spec.format_usage_line("mycli", has_commands=True)
        assert "mycli" in result
        assert "<COMMAND>" in result

    def test_layout_config_defaults(self):
        """Layout configuration should have sensible defaults."""
        spec = DEFAULT_FORMAT
        assert spec.layout.command_column_width == 24
        assert spec.layout.option_column_width == 28
        assert spec.layout.max_content_width == 100
        assert spec.layout.indent_size == 4

    def test_color_scheme_defaults(self):
        """Color scheme should have defaults."""
        spec = DEFAULT_FORMAT
        assert spec.colors.command == "cyan"
        assert spec.colors.option == "green"
        assert spec.colors.error == "red"


class TestPythonHelpFormatter:
    """Tests for Python/Click formatter generation."""

    def test_generate_formatter_class(self):
        """Should generate a valid Python class."""
        formatter = PythonHelpFormatter()
        code = formatter.generate_formatter_class()

        assert "class GoobitsHelpFormatter" in code
        assert "class GoobitsGroup" in code
        assert "class GoobitsCommand" in code
        assert "def write_usage" in code

    def test_generate_rich_click_config(self):
        """Should generate rich-click configuration."""
        formatter = PythonHelpFormatter()
        code = formatter.generate_rich_click_config()

        assert "click.rich_click" in code
        assert "USE_RICH_MARKUP" in code
        assert "OPTIONS_PANEL_TITLE" in code
        assert "COMMANDS_PANEL_TITLE" in code

    def test_generate_full_code(self):
        """Should generate complete formatter code."""
        formatter = PythonHelpFormatter()
        code = formatter.generate_full_code()

        # Should include both config and classes
        assert "rich_click" in code
        assert "GoobitsHelpFormatter" in code

    def test_get_group_class(self):
        """Should return the custom group class name."""
        formatter = PythonHelpFormatter()
        assert formatter.get_group_class() == "GoobitsGroup"

    def test_get_command_class(self):
        """Should return the custom command class name."""
        formatter = PythonHelpFormatter()
        assert formatter.get_command_class() == "GoobitsCommand"

    def test_context_settings(self):
        """Should generate proper context settings."""
        formatter = PythonHelpFormatter()
        settings = formatter.generate_context_settings()

        assert "help_option_names" in settings
        assert "-h" in settings["help_option_names"]
        assert "--help" in settings["help_option_names"]


class TestNodeJSHelpFormatter:
    """Tests for Node.js/Commander formatter generation."""

    def test_generate_help_config(self):
        """Should generate Commander configureHelp code."""
        formatter = NodeJSHelpFormatter()
        code = formatter.generate_help_config()

        assert "configureUnifiedHelp" in code
        assert "formatHelp" in code
        assert "formatDefinitionList" in code
        assert "HELP_CONFIG" in code

    def test_generate_version_handler(self):
        """Should generate version handler."""
        formatter = NodeJSHelpFormatter()
        code = formatter.generate_version_handler()

        assert "configureUnifiedVersion" in code
        assert ".version(" in code

    def test_generate_error_handler(self):
        """Should generate error handler."""
        formatter = NodeJSHelpFormatter()
        code = formatter.generate_error_handler()

        assert "configureUnifiedErrors" in code
        assert "showHelpAfterError" in code

    def test_generate_full_code(self):
        """Should generate complete formatter code."""
        formatter = NodeJSHelpFormatter()
        code = formatter.generate_full_code()

        assert "configureUnifiedHelp" in code
        assert "configureUnifiedVersion" in code
        assert "configureUnifiedErrors" in code

    def test_generate_setup_call(self):
        """Should generate setup call code."""
        formatter = NodeJSHelpFormatter()
        code = formatter.generate_setup_call()

        assert "configureUnifiedHelp(program" in code


class TestTypeScriptHelpFormatter:
    """Tests for TypeScript/Commander formatter generation."""

    def test_generate_types(self):
        """Should generate TypeScript type definitions."""
        formatter = TypeScriptHelpFormatter()
        code = formatter.generate_types()

        assert "interface HelpConfig" in code
        assert "type DefinitionItem" in code

    def test_generate_help_config(self):
        """Should generate typed Commander configureHelp code."""
        formatter = TypeScriptHelpFormatter()
        code = formatter.generate_help_config()

        assert "configureUnifiedHelp" in code
        assert "program: Command" in code
        assert "version: string" in code

    def test_generate_additional_imports(self):
        """Should generate Commander imports."""
        formatter = TypeScriptHelpFormatter()
        code = formatter.generate_additional_imports()

        assert "import { Command" in code
        assert "Help" in code
        assert "Option" in code

    def test_generate_full_code(self):
        """Should generate complete TypeScript formatter code."""
        formatter = TypeScriptHelpFormatter()
        code = formatter.generate_full_code()

        # Should include types
        assert "interface HelpConfig" in code
        # Should include functions
        assert "configureUnifiedHelp" in code


class TestRustHelpFormatter:
    """Tests for Rust/Clap formatter generation."""

    def test_generate_help_template(self):
        """Should generate Clap help template."""
        formatter = RustHelpFormatter()
        code = formatter.generate_help_template()

        assert "HELP_TEMPLATE" in code
        assert "{name}" in code
        assert "{version}" in code
        assert "{usage}" in code
        assert "USAGE:" in code

    def test_generate_styles(self):
        """Should generate Clap styling configuration."""
        formatter = RustHelpFormatter()
        code = formatter.generate_styles()

        assert "unified_styles" in code
        assert "Styles::styled()" in code
        assert "AnsiColor" in code

    def test_generate_command_builder(self):
        """Should generate helper functions."""
        formatter = RustHelpFormatter()
        code = formatter.generate_command_builder()

        assert "with_unified_help" in code
        assert "with_subcommand_help" in code
        assert "with_standard_flags" in code

    def test_generate_full_code(self):
        """Should generate complete Rust formatter code."""
        formatter = RustHelpFormatter()
        code = formatter.generate_full_code()

        assert "HELP_TEMPLATE" in code
        assert "unified_styles" in code
        assert "with_unified_help" in code

    def test_help_template_sections(self):
        """Help template should include all standard sections."""
        formatter = RustHelpFormatter()
        code = formatter.generate_help_template()

        assert "USAGE:" in code
        assert "ARGUMENTS:" in code
        assert "OPTIONS:" in code
        assert "COMMANDS:" in code


class TestCrossLanguageConsistency:
    """Tests to verify consistency across all language formatters."""

    def test_all_formatters_use_same_spec(self):
        """All formatters should use the same default spec."""
        python_fmt = PythonHelpFormatter()
        nodejs_fmt = NodeJSHelpFormatter()
        ts_fmt = TypeScriptHelpFormatter()
        rust_fmt = RustHelpFormatter()

        # All should reference the same spec instance or equivalent values
        assert python_fmt.spec.usage_header == nodejs_fmt.spec.usage_header
        assert nodejs_fmt.spec.usage_header == ts_fmt.spec.usage_header
        assert ts_fmt.spec.usage_header == rust_fmt.spec.usage_header

    def test_all_formatters_same_section_headers(self):
        """All formatters should produce same section headers."""
        python_fmt = PythonHelpFormatter()
        nodejs_fmt = NodeJSHelpFormatter()
        ts_fmt = TypeScriptHelpFormatter()
        rust_fmt = RustHelpFormatter()

        python_code = python_fmt.generate_full_code()
        nodejs_code = nodejs_fmt.generate_full_code()
        ts_code = ts_fmt.generate_full_code()
        rust_code = rust_fmt.generate_full_code()

        # All should contain the same section headers from the spec
        for header in ["USAGE", "OPTIONS", "COMMANDS"]:
            assert header in python_code, f"Python missing {header}"
            assert header in nodejs_code, f"Node.js missing {header}"
            assert header in ts_code, f"TypeScript missing {header}"
            assert header in rust_code, f"Rust missing {header}"

    def test_custom_spec_propagates(self):
        """Custom spec should propagate to all formatters."""
        custom_spec = HelpFormatSpec(
            usage_header="HOW TO USE",
            options_header="FLAGS",
            commands_header="SUBCOMMANDS",
        )

        python_fmt = PythonHelpFormatter(spec=custom_spec)
        nodejs_fmt = NodeJSHelpFormatter(spec=custom_spec)
        ts_fmt = TypeScriptHelpFormatter(spec=custom_spec)
        rust_fmt = RustHelpFormatter(spec=custom_spec)

        python_code = python_fmt.generate_full_code()
        nodejs_code = nodejs_fmt.generate_full_code()
        ts_code = ts_fmt.generate_full_code()
        rust_code = rust_fmt.generate_full_code()

        # All should use custom headers
        for code, name in [
            (python_code, "Python"),
            (nodejs_code, "Node.js"),
            (ts_code, "TypeScript"),
            (rust_code, "Rust"),
        ]:
            assert "FLAGS" in code, f"{name} missing custom FLAGS header"
            assert "SUBCOMMANDS" in code, f"{name} missing custom SUBCOMMANDS header"
