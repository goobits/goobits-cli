"""
Command Framework
================

Public interface for the Command framework extracted from command_handler.j2 template.
Provides CLI command generation with argument parsing, option handling, and hook integration.
"""

from .command_framework import CommandFramework, CommandConfig, Command, Argument, Option
from .validation_engine import ValidationEngine, ArgumentValidator, OptionValidator
from .execution_pipeline import ExecutionPipeline, HookLoader, ErrorHandler
from .language_adapters import (
    PythonCommandAdapter,
    NodeJSCommandAdapter,
    TypeScriptCommandAdapter,
    RustCommandAdapter
)

__all__ = [
    'CommandFramework',
    'CommandConfig',
    'Command',
    'Argument', 
    'Option',
    'ValidationEngine',
    'ArgumentValidator',
    'OptionValidator',
    'ExecutionPipeline',
    'HookLoader',
    'ErrorHandler',
    'PythonCommandAdapter',
    'NodeJSCommandAdapter',
    'TypeScriptCommandAdapter',
    'RustCommandAdapter'
]