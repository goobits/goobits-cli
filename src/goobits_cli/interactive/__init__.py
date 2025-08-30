"""
Interactive Framework
====================

Public interface for the Interactive framework extracted from interactive_mode.j2 template.
Provides REPL functionality with session management, variables, and pipeline support.
"""

from .interactive_framework import InteractiveFramework, InteractiveConfig, FeatureConfig
from .language_adapters import (
    PythonInteractiveAdapter,
    NodeJSInteractiveAdapter,
    TypeScriptInteractiveAdapter,
    RustInteractiveAdapter
)

__all__ = [
    'InteractiveFramework',
    'InteractiveConfig',
    'FeatureConfig',
    'PythonInteractiveAdapter',
    'NodeJSInteractiveAdapter', 
    'TypeScriptInteractiveAdapter',
    'RustInteractiveAdapter'
]