"""
Completion Framework
===================

Public interface for the Completion framework extracted from completion templates.
Provides shell completion systems for bash, zsh, fish, and PowerShell across all languages.
"""

from .completion_framework import CompletionFramework, CompletionConfig
from .completion_manager import CompletionManager, ShellType, CompletionScript
from .completion_engine import CompletionEngine, CompletionContext, CompletionResult
from .language_adapters import (
    PythonCompletionAdapter,
    NodeJSCompletionAdapter,
    TypeScriptCompletionAdapter,
    RustCompletionAdapter
)

__all__ = [
    'CompletionFramework',
    'CompletionConfig',
    'CompletionManager',
    'ShellType',
    'CompletionScript',
    'CompletionEngine',
    'CompletionContext',
    'CompletionResult',
    'PythonCompletionAdapter',
    'NodeJSCompletionAdapter',
    'TypeScriptCompletionAdapter',
    'RustCompletionAdapter'
]