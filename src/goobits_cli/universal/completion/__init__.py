"""
Backward-compatible re-export of completion module.

This module has been moved to goobits_cli.universal.integrations.completion.
This file provides backward compatibility for existing imports.

DEPRECATED: Use goobits_cli.universal.integrations.completion instead.
"""

# Re-export everything from the new location
from ..integrations.completion import *  # noqa: F401, F403
from ..integrations.completion import (
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
    get_completion_files_for_language,
    get_smart_completion_registry,
    integrate_completion_system,
    is_completion_supported,
    is_dynamic_completion_supported,
)

__all__ = [
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
    "is_completion_supported",
    "is_dynamic_completion_supported",
    "get_completion_files_for_language",
]
