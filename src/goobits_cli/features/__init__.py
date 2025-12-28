"""Goobits CLI Features - Interactive, Completion, Plugins, Prompts.

This module provides a clean public API for the main feature systems:
- Interactive: REPL mode with command execution
- Completion: Shell completion with smart providers
- Plugins: Plugin management and marketplace
- Prompts: Interactive prompts and input helpers

Example usage:
    from goobits_cli.features import (
        InteractiveEngine,
        create_basic_repl,
        integrate_interactive_mode,
        SmartCompletionEngine,
        DynamicCompletionRegistry,
        PluginManager,
        CompletionEngine,
        PromptsHelper,
    )
"""

# Interactive mode re-exports from universal
from ..universal.interactive import (
    InteractiveCommand,
    InteractiveEngine,
    InteractiveRenderer,
    BasicREPL,
    create_basic_repl,
    integrate_interactive_mode,
    is_interactive_supported,
)

# Local interactive modules
from .interactive import (
    GoobitscliframeworkInteractive,
    run_interactive,
)

from .enhanced_interactive import (
    EnhancedInteractive,
    start_enhanced_interactive,
    ENHANCED_FEATURES_AVAILABLE,
)

# Completion system re-exports from universal
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

# Local completion modules
from .completion_engine import (
    CompletionEngine,
)

from .completion_helper import (
    CompletionHelper,
    get_completion_helper,
    generate_completion_script,
    install_completion,
    get_install_instructions,
)

# Plugin system re-exports
from ..universal.plugins import (
    PluginManager,
    PluginInfo,
    PluginRegistry,
    integrate_plugin_system,
)

# Prompts helper
from .prompts import (
    PromptsHelper,
    get_prompts_helper,
    text,
    password,
    confirm,
    select,
    multiselect,
    integer,
    float_input,
    path,
    HAS_RICH_PROMPT,
    HAS_QUESTIONARY,
)

__all__ = [
    # Interactive mode (universal)
    "InteractiveCommand",
    "InteractiveEngine",
    "InteractiveRenderer",
    "BasicREPL",
    "create_basic_repl",
    "integrate_interactive_mode",
    "is_interactive_supported",
    # Interactive mode (local)
    "GoobitscliframeworkInteractive",
    "run_interactive",
    "EnhancedInteractive",
    "start_enhanced_interactive",
    "ENHANCED_FEATURES_AVAILABLE",
    # Completion system (universal)
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
    # Completion system (local)
    "CompletionEngine",
    "CompletionHelper",
    "get_completion_helper",
    "generate_completion_script",
    "install_completion",
    "get_install_instructions",
    # Plugin system
    "PluginManager",
    "PluginInfo",
    "PluginRegistry",
    "integrate_plugin_system",
    # Prompts helper
    "PromptsHelper",
    "get_prompts_helper",
    "text",
    "password",
    "confirm",
    "select",
    "multiselect",
    "integer",
    "float_input",
    "path",
    "HAS_RICH_PROMPT",
    "HAS_QUESTIONARY",
]
