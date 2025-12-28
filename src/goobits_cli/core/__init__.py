"""Core infrastructure for Goobits CLI Framework.

This module exports:
- config: Configuration management (ConfigManager, ConfigError, etc.)
- schemas: Pydantic schemas for YAML validation
- logging: Structured logging infrastructure
- manifest: Manifest file updater for package.json and Cargo.toml
"""

from .config import (
    ConfigError,
    ConfigFileError,
    ConfigManager,
    ConfigValidationError,
    RCConfigLoader,
    config_manager,
    get_config,
    get_config_value,
    load_config,
    set_config_value,
)
from .logging import (
    StructuredFormatter,
    clear_context,
    get_context,
    get_logger,
    remove_context_keys,
    set_context,
    setup_logging,
    update_context,
)
from .manifest import (
    ManifestUpdater,
    Result,
    update_manifests_for_build,
)
from .schemas import (
    ArgumentSchema,
    CLISchema,
    CommandGroupSchema,
    CommandSchema,
    ConfigSchema,
    DependenciesSchema,
    DependencyItem,
    ExtrasSchema,
    FeaturesSchema,
    GoobitsConfigSchema,
    HeaderItemSchema,
    HeaderSectionSchema,
    InstallationSchema,
    InteractiveModeSchema,
    MessagesSchema,
    OptionSchema,
    PythonConfigSchema,
    RichConfigSchema,
    ShellIntegrationSchema,
    ValidationSchema,
)

__all__ = [
    # Config
    "ConfigManager",
    "ConfigError",
    "ConfigFileError",
    "ConfigValidationError",
    "RCConfigLoader",
    "config_manager",
    "get_config",
    "load_config",
    "get_config_value",
    "set_config_value",
    # Schemas
    "ConfigSchema",
    "CLISchema",
    "CommandSchema",
    "ArgumentSchema",
    "OptionSchema",
    "GoobitsConfigSchema",
    "HeaderItemSchema",
    "HeaderSectionSchema",
    "CommandGroupSchema",
    "RichConfigSchema",
    "PythonConfigSchema",
    "DependencyItem",
    "DependenciesSchema",
    "ExtrasSchema",
    "InstallationSchema",
    "ShellIntegrationSchema",
    "ValidationSchema",
    "MessagesSchema",
    "InteractiveModeSchema",
    "FeaturesSchema",
    # Logging
    "setup_logging",
    "get_logger",
    "set_context",
    "clear_context",
    "update_context",
    "get_context",
    "remove_context_keys",
    "StructuredFormatter",
    # Manifest
    "ManifestUpdater",
    "Result",
    "update_manifests_for_build",
]
