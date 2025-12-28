"""Generation infrastructure for multi-language CLI code generation.

This package contains:
    - renderers/: Language-specific generators (Python, Node.js, TypeScript, Rust)
    - templates/: Template resources for code generation
"""

from .renderers import (
    PythonGenerator,
    NodeJSGenerator,
    TypeScriptGenerator,
    RustGenerator,
)

__all__ = [
    "PythonGenerator",
    "NodeJSGenerator",
    "TypeScriptGenerator",
    "RustGenerator",
]
