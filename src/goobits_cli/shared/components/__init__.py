"""Shared components for goobits-cli documentation generation.

This package provides utilities for generating consistent documentation

across all supported programming languages (Python, Node.js, TypeScript, Rust).

"""

from .doc_generator import (
    DocumentationGenerator,
    create_documentation_generator,
    generate_installation_guide_for_language,
    generate_readme_for_language,
    get_language_help_formatting,
)

__all__ = [
    "DocumentationGenerator",
    "create_documentation_generator",
    "generate_readme_for_language",
    "generate_installation_guide_for_language",
    "get_language_help_formatting",
]
