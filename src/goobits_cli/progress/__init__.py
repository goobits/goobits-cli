"""
Progress Framework
==================

Public interface for the Progress framework extracted from progress_manager.j2 template.
Provides progress indicators, spinners, and visual feedback systems with Rich library integration
and fallback support for all languages.
"""

from .progress_framework import ProgressFramework, ProgressConfig
from .progress_manager import ProgressManager, ProgressIndicator
from .display_adapters import DisplayAdapter, RichDisplayAdapter, FallbackDisplayAdapter
from .language_adapters import (
    PythonProgressAdapter,
    NodeJSProgressAdapter, 
    TypeScriptProgressAdapter,
    RustProgressAdapter
)

__all__ = [
    'ProgressFramework',
    'ProgressConfig',
    'ProgressManager', 
    'ProgressIndicator',
    'DisplayAdapter',
    'RichDisplayAdapter',
    'FallbackDisplayAdapter',
    'PythonProgressAdapter',
    'NodeJSProgressAdapter',
    'TypeScriptProgressAdapter', 
    'RustProgressAdapter'
]