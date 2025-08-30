"""
Logging Framework for Goobits CLI
==================================

This module provides the extracted logging framework that replaces
the complex template-based logging generation with testable, maintainable code.

Key Components:
- LoggingFramework: Main orchestrator for logging code generation
- Language Adapters: Python, Node.js, TypeScript, Rust specific generators
- Configuration Processing: Testable business logic for logging configuration
"""

from .logging_framework import LoggingFramework, LoggingConfig
from .language_adapters import (
    PythonLoggingAdapter,
    NodeJSLoggingAdapter,
    TypeScriptLoggingAdapter,
    RustLoggingAdapter
)

__all__ = [
    'LoggingFramework',
    'LoggingConfig',
    'PythonLoggingAdapter',
    'NodeJSLoggingAdapter', 
    'TypeScriptLoggingAdapter',
    'RustLoggingAdapter'
]