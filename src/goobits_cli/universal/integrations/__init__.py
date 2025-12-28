"""
Universal CLI integrations for Goobits CLI Framework.

This module provides integration support for:
- Completion system (shell completions)
- Plugin system

All integration modules are designed to be optional enhancements
that can be applied during CLI generation.
"""

from . import completion, plugins

__all__ = [
    "completion",
    "plugins",
]
