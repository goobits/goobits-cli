"""
Builtin Framework
================

Public interface for the Builtin framework extracted from builtin_manager.j2 template.
Provides built-in commands (upgrade, version, completion, config, doctor) for all languages.
"""

from .builtin_framework import BuiltinFramework, BuiltinConfig, BuiltinCommand, BuiltinCommandType
from .command_registry import CommandRegistry, UpgradeOptions, CompletionOptions, ConfigOptions
from .subprocess_manager import SubprocessManager, ProcessResult, PlatformManager
from .language_adapters import (
    PythonBuiltinAdapter,
    NodeJSBuiltinAdapter,
    TypeScriptBuiltinAdapter,
    RustBuiltinAdapter
)

__all__ = [
    'BuiltinFramework',
    'BuiltinConfig', 
    'BuiltinCommand',
    'BuiltinCommandType',
    'CommandRegistry',
    'UpgradeOptions',
    'CompletionOptions', 
    'ConfigOptions',
    'SubprocessManager',
    'ProcessResult',
    'PlatformManager',
    'PythonBuiltinAdapter',
    'NodeJSBuiltinAdapter',
    'TypeScriptBuiltinAdapter',
    'RustBuiltinAdapter'
]