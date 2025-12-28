"""Goobits CLI Features - Interactive, Completion, Plugins.

This module provides a clean public API for the three main feature systems:
- Interactive: REPL mode with command execution
- Completion: Shell completion with smart providers
- Plugins: Plugin management and marketplace

Example usage:
    from goobits_cli.features import (
        InteractiveEngine,
        create_basic_repl,
        integrate_interactive_mode,
        SmartCompletionEngine,
        DynamicCompletionRegistry,
        PluginManager,
    )
"""

# Interactive mode re-exports
from ..universal.interactive import (
    InteractiveCommand,
    InteractiveEngine,
    InteractiveRenderer,
    BasicREPL,
    create_basic_repl,
    integrate_interactive_mode,
    is_interactive_supported,
)

# Completion system re-exports
from ..universal.completion import (
    DynamicCompletionRegistry,
    CompletionProvider,
    CompletionContext,
    FilePathCompletionProvider,
    EnvironmentVariableProvider,
    ConfigKeyProvider,
    HistoryProvider,
    SmartCompletionEngine,
    HistoryCompletionProvider,
    FuzzyMatchProvider,
    get_smart_completion_registry,
    integrate_completion_system,
)

# Plugin system re-exports
from ..universal.plugins import (
    PluginManager,
    PluginInfo,
    PluginRegistry,
    integrate_plugin_system,
)

__all__ = [
    # Interactive mode
    "InteractiveCommand",
    "InteractiveEngine",
    "InteractiveRenderer",
    "BasicREPL",
    "create_basic_repl",
    "integrate_interactive_mode",
    "is_interactive_supported",
    # Completion system
    "DynamicCompletionRegistry",
    "CompletionProvider",
    "CompletionContext",
    "FilePathCompletionProvider",
    "EnvironmentVariableProvider",
    "ConfigKeyProvider",
    "HistoryProvider",
    "SmartCompletionEngine",
    "HistoryCompletionProvider",
    "FuzzyMatchProvider",
    "get_smart_completion_registry",
    "integrate_completion_system",
    # Plugin system
    "PluginManager",
    "PluginInfo",
    "PluginRegistry",
    "integrate_plugin_system",
]
