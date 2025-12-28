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
# Completion system re-exports from universal
from ..universal.integrations.completion import (
    CompletionContext,
    CompletionProvider,
    ConfigKeyProvider,
    DynamicCompletionRegistry,
    EnvironmentVariableProvider,
    FilePathCompletionProvider,
    FuzzyMatchProvider,
    HistoryCompletionProvider,
    HistoryProvider,
    SmartCompletionEngine,
    get_smart_completion_registry,
    integrate_completion_system,
)
from ..universal.integrations.interactive import (
    BasicREPL,
    InteractiveCommand,
    InteractiveEngine,
    InteractiveRenderer,
    create_basic_repl,
    integrate_interactive_mode,
    is_interactive_supported,
)

# Plugin system re-exports
from ..universal.integrations.plugins import (
    PluginInfo,
    PluginManager,
    PluginRegistry,
    integrate_plugin_system,
)

# Local completion modules
from .completion_engine import (
    CompletionEngine,
)
from .completion_helper import (
    CompletionHelper,
    generate_completion_script,
    get_completion_helper,
    get_install_instructions,
    install_completion,
)
from .enhanced_interactive import (
    ENHANCED_FEATURES_AVAILABLE,
    EnhancedInteractive,
    start_enhanced_interactive,
)

# Local interactive modules
from .interactive import (
    GoobitscliframeworkInteractive,
    run_interactive,
)

# Prompts helper
from .prompts import (
    HAS_QUESTIONARY,
    HAS_RICH_PROMPT,
    PromptsHelper,
    confirm,
    float_input,
    get_prompts_helper,
    integer,
    multiselect,
    password,
    path,
    select,
    text,
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
