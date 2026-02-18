"""
Unified Help Format Specification

This module defines the single source of truth for help output formatting
across all languages. Language-specific formatters read this spec and
generate appropriate formatter code for their respective frameworks.

The format is designed to be:
- Consistent across Python (Click), Node.js (Commander), TypeScript (Commander), Rust (Clap)
- Clean and readable
- Properly aligned
- Color-aware (when terminals support it)
"""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class ColorScheme:
    """Color scheme for help output (terminal-aware)."""

    command: str = "cyan"
    option: str = "green"
    argument: str = "yellow"
    description: str = "white"
    header: str = "bold"
    error: str = "red"
    success: str = "green"
    muted: str = "dim"


@dataclass
class LayoutConfig:
    """Layout configuration for help output."""

    # Column widths
    command_column_width: int = 24
    option_column_width: int = 28
    max_content_width: int = 100

    # Indentation
    indent_size: int = 4
    description_indent: int = 2

    # Spacing
    section_spacing: int = 1
    item_spacing: int = 0


@dataclass
class SectionOrder:
    """Order of sections in help output."""

    order: List[str] = field(
        default_factory=lambda: [
            "header",  # Name + version
            "description",  # Brief description
            "usage",  # Usage pattern
            "arguments",  # Positional arguments
            "options",  # Optional flags
            "commands",  # Subcommands
            "examples",  # Usage examples (if any)
            "footer",  # Additional notes
        ]
    )


@dataclass
class HelpFormatSpec:
    """
    Complete specification for unified help output format.

    This is the SINGLE SOURCE OF TRUTH for help formatting.
    All language-specific formatters derive their output from this spec.
    """

    # Section headers
    usage_header: str = "USAGE"
    arguments_header: str = "ARGUMENTS"
    options_header: str = "OPTIONS"
    commands_header: str = "COMMANDS"
    examples_header: str = "EXAMPLES"

    # Section templates
    header_template: str = "{name} v{version}"
    usage_template: str = "{name} [OPTIONS] {usage_args}"
    usage_with_commands_template: str = "{name} [OPTIONS] <COMMAND> [ARGS]"

    # Option formatting
    short_option_prefix: str = "-"
    long_option_prefix: str = "--"
    option_separator: str = ", "
    option_value_format: str = "<{type}>"
    required_marker: str = "(required)"
    default_format: str = "[default: {value}]"

    # Argument formatting
    argument_required_format: str = "<{name}>"
    argument_optional_format: str = "[{name}]"
    argument_variadic_format: str = "[{name}...]"

    # Command formatting
    command_format: str = "{name}"

    # Alignment
    align_descriptions: bool = True

    # Colors
    colors: ColorScheme = field(default_factory=ColorScheme)

    # Layout
    layout: LayoutConfig = field(default_factory=LayoutConfig)

    # Section order
    sections: SectionOrder = field(default_factory=SectionOrder)

    # Help/Version options (always present)
    help_short: str = "-h"
    help_long: str = "--help"
    help_description: str = "Show this help message and exit"
    version_short: str = "-V"
    version_long: str = "--version"
    version_description: str = "Show version information"

    def format_option_signature(
        self,
        short: Optional[str],
        long: Optional[str],
        value_type: Optional[str] = None,
        required: bool = False,
    ) -> str:
        """Format an option signature consistently."""
        parts = []

        if short:
            parts.append(f"{self.short_option_prefix}{short}")
        if long:
            parts.append(f"{self.long_option_prefix}{long}")

        signature = self.option_separator.join(parts)

        if value_type and value_type != "flag":
            signature += f" {self.option_value_format.format(type=value_type.upper())}"

        return signature

    def format_argument_signature(
        self, name: str, required: bool = True, variadic: bool = False
    ) -> str:
        """Format an argument signature consistently."""
        if variadic:
            return self.argument_variadic_format.format(name=name.upper())
        elif required:
            return self.argument_required_format.format(name=name.upper())
        else:
            return self.argument_optional_format.format(name=name.upper())

    def format_usage_line(
        self,
        name: str,
        has_commands: bool = False,
        arguments: Optional[List[dict]] = None,
    ) -> str:
        """Format the usage line consistently."""
        if has_commands:
            return self.usage_with_commands_template.format(name=name)

        usage_args = ""
        if arguments:
            arg_parts = []
            for arg in arguments:
                arg_parts.append(
                    self.format_argument_signature(
                        arg.get("name", "ARG"),
                        arg.get("required", True),
                        arg.get("variadic", False),
                    )
                )
            usage_args = " ".join(arg_parts)

        return self.usage_template.format(name=name, usage_args=usage_args).strip()


# Default format specification - THE source of truth
DEFAULT_FORMAT = HelpFormatSpec()
