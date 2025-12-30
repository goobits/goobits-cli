"""
Unified Help Formatters for Goobits CLI Framework

This module provides a unified help output format across all supported languages
(Python, Node.js, TypeScript, Rust) while still using native CLI frameworks
(Click, Commander, Clap) under the hood.

The formatters customize only the display output, not the functionality.
All argument parsing, validation, completion, and other features remain native.
"""

from .spec import HelpFormatSpec, DEFAULT_FORMAT
from .python_formatter import PythonHelpFormatter
from .nodejs_formatter import NodeJSHelpFormatter
from .typescript_formatter import TypeScriptHelpFormatter
from .rust_formatter import RustHelpFormatter

__all__ = [
    "HelpFormatSpec",
    "DEFAULT_FORMAT",
    "PythonHelpFormatter",
    "NodeJSHelpFormatter",
    "TypeScriptHelpFormatter",
    "RustHelpFormatter",
]
