"""
Goobits CLI Shared Templates

This package contains documentation generation templates and utilities
for all supported languages.
"""

from .doc_generator import (
    DocumentationGenerator,
    DocumentationType,
    OutputFormat,
    DocumentationContext,
    DocumentationSection,
    LanguageAdapter,
    PythonAdapter,
    NodeJSAdapter,
    TypeScriptAdapter,
    RustAdapter,
    generate_documentation,
    create_readme_file
)

__all__ = [
    'DocumentationGenerator',
    'DocumentationType',
    'OutputFormat',
    'DocumentationContext',
    'DocumentationSection',
    'LanguageAdapter',
    'PythonAdapter',
    'NodeJSAdapter',
    'TypeScriptAdapter',
    'RustAdapter',
    'generate_documentation',
    'create_readme_file'
]