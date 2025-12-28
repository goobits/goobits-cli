"""
Backward-compatible re-export of interactive module.

This module has been moved to goobits_cli.universal.integrations.interactive.
This file provides backward compatibility for existing imports.

DEPRECATED: Use goobits_cli.universal.integrations.interactive instead.
"""

# Re-export everything from the new location
from ..integrations.interactive import *  # noqa: F401, F403
from ..integrations.interactive import (
    BasicREPL,
    InteractiveCommand,
    InteractiveEngine,
    InteractiveRenderer,
    create_basic_repl,
    get_interactive_file_name,
    get_interactive_import_statement,
    get_interactive_launch_code,
    integrate_interactive_mode,
    is_interactive_supported,
    is_tab_completion_supported,
)

__all__ = [
    "InteractiveCommand",
    "InteractiveEngine",
    "InteractiveRenderer",
    "BasicREPL",
    "create_basic_repl",
    "integrate_interactive_mode",
    "is_interactive_supported",
    "is_tab_completion_supported",
    "get_interactive_file_name",
    "get_interactive_import_statement",
    "get_interactive_launch_code",
]
