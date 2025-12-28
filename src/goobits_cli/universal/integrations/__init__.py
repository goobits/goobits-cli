"""
Universal CLI integrations for Goobits CLI Framework.

This module provides integration support for:
- Completion system (shell completions)
- Interactive mode (REPL)
- Plugin system

All integration modules are designed to be optional enhancements
that can be applied during CLI generation.
"""

from . import completion, interactive, plugins

__all__ = [
    "completion",
    "interactive",
    "plugins",
]
