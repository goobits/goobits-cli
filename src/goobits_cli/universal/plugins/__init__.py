"""
Backward-compatible re-export of plugins module.

This module has been moved to goobits_cli.universal.integrations.plugins.
This file provides backward compatibility for existing imports.

DEPRECATED: Use goobits_cli.universal.integrations.plugins instead.
"""

# Re-export everything from the new location
from ..integrations.plugins import *  # noqa: F401, F403
from ..integrations.plugins import (
    PluginInfo,
    PluginManager,
    PluginRegistry,
    integrate_plugin_system,
    setup_plugin_integration,
)

__all__ = [
    "PluginManager",
    "PluginInfo",
    "PluginRegistry",
    "integrate_plugin_system",
    "setup_plugin_integration",
]
