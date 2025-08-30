"""
REPL Framework
==============

Public interface for the REPL framework extracted from repl_loop.j2 template.
Provides enhanced Read-Eval-Print Loop functionality with multi-line support,
smart completion, command history, and cross-language compatibility.
"""

from .repl_framework import REPLFramework, REPLConfig
from .repl_engine import REPLEngine, REPLSession, REPLCommand
from .history_manager import HistoryManager, HistoryEntry
from .language_adapters import (
    PythonREPLAdapter,
    NodeJSREPLAdapter, 
    TypeScriptREPLAdapter,
    RustREPLAdapter
)

__all__ = [
    'REPLFramework',
    'REPLConfig',
    'REPLEngine', 
    'REPLSession',
    'REPLCommand',
    'HistoryManager',
    'HistoryEntry',
    'PythonREPLAdapter',
    'NodeJSREPLAdapter',
    'TypeScriptREPLAdapter', 
    'RustREPLAdapter'
]