"""
Error Framework
===============

Public interface for the Error framework extracted from error_handler.j2 template.
Provides error handling, exception hierarchies, and error reporting for all languages.
"""

from .error_framework import ErrorFramework, ErrorConfig
from .exception_hierarchy import ExitCode, CliError, UsageError, ConfigError, NetworkError, PermissionError, FileNotFoundError
from .error_handler import ErrorHandler, ErrorContext, ErrorReport
from .language_adapters import (
    PythonErrorAdapter,
    NodeJSErrorAdapter, 
    TypeScriptErrorAdapter,
    RustErrorAdapter
)

__all__ = [
    'ErrorFramework',
    'ErrorConfig',
    'ExitCode',
    'CliError',
    'UsageError', 
    'ConfigError',
    'NetworkError',
    'PermissionError', 
    'FileNotFoundError',
    'ErrorHandler',
    'ErrorContext',
    'ErrorReport',
    'PythonErrorAdapter',
    'NodeJSErrorAdapter',
    'TypeScriptErrorAdapter', 
    'RustErrorAdapter'
]