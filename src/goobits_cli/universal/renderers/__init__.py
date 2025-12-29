"""
Language-specific renderers for the Universal Template System.

This module contains:
- interface: LanguageRenderer ABC and Artifact dataclass
- registry: Factory pattern for renderer instantiation
- helpers: Shared utility functions for renderers
- Concrete renderer implementations (Python, Node.js, TypeScript, Rust)
"""

# Interface and core types
# Helper utilities
from .helpers import (
    escape_string,
    format_docstring,
    get_type_mapping,
    indent,
    map_type,
    safe_identifier,
    to_camel_case,
    to_pascal_case,
    to_snake_case,
)
from .interface import Artifact, LanguageRenderer

# Concrete implementations
from .nodejs_renderer import NodeJSRenderer
from .python_renderer import PythonRenderer

# Registry and factory functions
from .registry import (
    RendererRegistry,
    get_default_registry,
    get_renderer,
)
from .typescript_renderer import TypeScriptRenderer

# Rust renderer may not exist yet
try:
    from .rust_renderer import RustRenderer

    _ = RustRenderer
    _has_rust = True
except ImportError:
    _has_rust = False

__all__ = [
    # Interface
    "LanguageRenderer",
    "Artifact",
    # Registry
    "RendererRegistry",
    "get_default_registry",
    "get_renderer",
    # Helpers
    "escape_string",
    "indent",
    "to_snake_case",
    "to_camel_case",
    "to_pascal_case",
    "format_docstring",
    "get_type_mapping",
    "map_type",
    "safe_identifier",
    # Concrete renderers
    "PythonRenderer",
    "NodeJSRenderer",
    "TypeScriptRenderer",
]

if _has_rust:
    __all__.append("RustRenderer")
