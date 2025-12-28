"""Documentation Generator - Shared component for generating documentation across all language generators.

This module provides utilities for generating consistent documentation (README, help text,

installation guides) across Python, Node.js, TypeScript, and Rust CLI generators.

Usage:

    from goobits_cli.shared.components.doc_generator import DocumentationGenerator

    generator = DocumentationGenerator(language='python', config=config_data)

    readme_content = generator.generate_readme()

    install_guide = generator.generate_installation_guide()

"""

from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml
from jinja2 import Environment, FileSystemLoader


class DocumentationGenerator:
    """Generates documentation templates for any supported language."""

    def __init__(
        self, language: str, config: Dict[str, Any], template_dir: Optional[str] = None
    ):
        """Initialize the documentation generator.

        Args:

            language: Target language (python, nodejs, typescript, rust)

            config: Full configuration dictionary from goobits.yaml

            template_dir: Optional custom template directory path

        """

        self.language = language.lower()

        self.config = config

        # Set up template directory

        if template_dir:
            self.template_dir = Path(template_dir)

        else:
            # Default to shared templates directory

            current_dir = Path(__file__).parent.parent

            self.template_dir = current_dir / "templates"

        # Load language customizations

        self._load_customizations()

        # Set up Jinja2 environment

        self.jinja_env = Environment(
            loader=FileSystemLoader(str(self.template_dir)),
            trim_blocks=True,
            lstrip_blocks=True,
        )

        # Add custom filters

        self._register_filters()

    def _load_customizations(self) -> None:
        """Load language-specific customizations from YAML file."""

        customizations_file = self.template_dir / "language_customizations.yaml"

        if customizations_file.exists():
            with open(customizations_file) as f:
                self.customizations = yaml.safe_load(f)

        else:
            self.customizations = {}

    def _register_filters(self) -> None:
        """Register custom Jinja2 filters for documentation generation."""

        def format_multiline(text: str, max_width: int = 80) -> str:
            """Format multi-line text with word wrapping."""

            lines = text.split("\n")

            formatted_lines = []

            for line in lines:
                if len(line) <= max_width:
                    formatted_lines.append(line)

                else:
                    # Simple word wrap

                    words = line.split(" ")

                    current_line = ""

                    for word in words:
                        if len(current_line + " " + word) <= max_width:
                            current_line += (" " if current_line else "") + word

                        else:
                            if current_line:
                                formatted_lines.append(current_line)

                            current_line = word

                    if current_line:
                        formatted_lines.append(current_line)

            return "\n".join(formatted_lines)

        def escape_docstring(text: str) -> str:
            """Escape text for use in Python docstrings."""

            return text.replace('"""', r"\"\"\"").replace("\\", "\\\\")

        def align_examples(examples: List[Dict[str, str]], indent: int = 4) -> str:
            """Align command examples with consistent formatting."""

            if not examples:
                return ""

            max_cmd_length = max(len(ex.get("command", "")) for ex in examples)

            aligned = []

            for example in examples:
                cmd = example.get("command", "")

                desc = example.get("description", "")

                padding = " " * (max_cmd_length - len(cmd) + 2)

                aligned.append(f"{' ' * indent}{cmd}{padding}# {desc}")

            return "\n".join(aligned)

        # Register filters

        self.jinja_env.filters["format_multiline"] = format_multiline

        self.jinja_env.filters["escape_docstring"] = escape_docstring

        self.jinja_env.filters["align_examples"] = align_examples

    def _get_template_context(self) -> Dict[str, Any]:
        """Build the complete template context with language-specific data."""

        context = self.config.copy()

        # Add language-specific information

        context["language"] = self.language

        # Add language customizations if available

        lang_config = self.customizations.get("languages", {}).get(self.language, {})

        context.update(lang_config)

        # Add platform-specific information

        context["platforms"] = self.customizations.get("platforms", {})

        # Add error templates

        context["error_templates"] = self.customizations.get("error_templates", {}).get(
            self.language, {}
        )

        # Add completion support info

        context["completion_support"] = self.customizations.get(
            "completion_support", {}
        ).get(self.language, {})

        # Add help formatting preferences

        context["help_formatting"] = self.customizations.get("help_formatting", {}).get(
            self.language, {}
        )

        return context

    def generate_readme(self) -> str:
        """Generate README.md content using the shared template."""

        template = self.jinja_env.get_template("readme_template.md.j2")

        context = self._get_template_context()

        return template.render(**context)

    def generate_installation_guide(self) -> str:
        """Generate installation guide content."""

        template = self.jinja_env.get_template("installation_template.md.j2")

        context = self._get_template_context()

        return template.render(**context)

    def generate_help_text(
        self, command_name: str, command_data: Dict[str, Any]
    ) -> str:
        """Generate help text for a specific command.

        Args:

            command_name: Name of the command

            command_data: Command configuration data

        Returns:

            Formatted help text for the command

        """

        self.jinja_env.get_template("help_text_template.j2")

        context = self._get_template_context()

        context.update(
            {"current_command": command_name, "current_command_data": command_data}
        )

        # Use the command_description macro from the template

        help_template = """

{%- from 'help_text_template.j2' import command_description, command_usage, format_arguments, format_options -%}

{{ command_description(current_command_data) }}


Usage: {{ command_usage(command_name, current_command, current_command_data) }}


{{ format_arguments(current_command_data.args) }}

{{ format_options(current_command_data.options) }}

"""

        rendered_template = self.jinja_env.from_string(help_template)

        return rendered_template.render(**context)

    def generate_error_message(self, error_type: str, **kwargs) -> str:
        """Generate language-appropriate error messages.

        Args:

            error_type: Type of error (missing_dependency, permission_error, etc.)

            **kwargs: Error-specific parameters

        Returns:

            Formatted error message

        """

        error_templates = self.customizations.get("error_templates", {}).get(
            self.language, {}
        )

        template_str = error_templates.get(error_type, "Error: {error_type}")

        # Create a simple template and render with kwargs

        template = self.jinja_env.from_string(template_str)

        return template.render(error_type=error_type, **kwargs)

    def get_language_config(self, key: str) -> Any:
        """Get language-specific configuration value.

        Args:

            key: Configuration key (e.g., 'package_manager', 'test_command')

        Returns:

            Language-specific configuration value

        """

        return self.customizations.get("languages", {}).get(self.language, {}).get(key)

    def supports_feature(self, feature: str) -> bool:
        """Check if the current language supports a specific feature.

        Args:

            feature: Feature name (e.g., 'completion_support', 'virtual_env')

        Returns:

            True if the language supports the feature

        """

        lang_config = self.customizations.get("languages", {}).get(self.language, {})

        return lang_config.get(feature, False)

    def get_documentation_sections(self) -> Dict[str, List[str]]:
        """Get language-specific documentation sections to include/exclude.

        Returns:

            Dictionary with 'include' and 'exclude' lists

        """

        return self.customizations.get("documentation_sections", {}).get(
            self.language, {"include": [], "exclude": []}
        )

    def generate_custom_section(
        self, section_name: str, template_string: str, **kwargs
    ) -> str:
        """Generate a custom documentation section using a template string.

        Args:

            section_name: Name of the section

            template_string: Jinja2 template string

            **kwargs: Additional template variables

        Returns:

            Rendered section content

        """

        template = self.jinja_env.from_string(template_string)

        context = self._get_template_context()

        context.update(kwargs)

        context["section_name"] = section_name

        return template.render(**context)


def create_documentation_generator(
    language: str, config: Dict[str, Any]
) -> DocumentationGenerator:
    """Factory function to create a documentation generator.

    Args:

        language: Target language

        config: Configuration dictionary

    Returns:

        Configured DocumentationGenerator instance

    """

    return DocumentationGenerator(language, config)


# Convenience functions for common documentation tasks


def generate_readme_for_language(language: str, config: Dict[str, Any]) -> str:
    """Generate README content for a specific language.

    Args:

        language: Target language

        config: Configuration dictionary

    Returns:

        README.md content

    """

    generator = create_documentation_generator(language, config)

    return generator.generate_readme()


def generate_installation_guide_for_language(
    language: str, config: Dict[str, Any]
) -> str:
    """Generate installation guide for a specific language.

    Args:

        language: Target language

        config: Configuration dictionary

    Returns:

        Installation guide content

    """

    generator = create_documentation_generator(language, config)

    return generator.generate_installation_guide()


def get_language_help_formatting(language: str) -> Dict[str, Any]:
    """Get help text formatting preferences for a language.

    Args:

        language: Target language

    Returns:

        Help formatting configuration

    """

    current_dir = Path(__file__).parent.parent

    customizations_file = current_dir / "templates" / "language_customizations.yaml"

    if customizations_file.exists():
        with open(customizations_file) as f:
            customizations = yaml.safe_load(f)

            return customizations.get("help_formatting", {}).get(language, {})

    return {}
