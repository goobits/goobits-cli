"""Core infrastructure for Goobits CLI Framework.

This module exports:
- config: Configuration management (ConfigManager, ConfigError, etc.)
- schemas: Pydantic schemas for YAML validation
- logging: Structured logging infrastructure
- manifest: Manifest file updater for package.json and Cargo.toml
"""

from .config import (
    ConfigManager,
    ConfigError,
    ConfigFileError,
    ConfigValidationError,
    RCConfigLoader,
    config_manager,
    get_config,
    load_config,
    get_config_value,
    set_config_value,
)

from .schemas import (
    ConfigSchema,
    CLISchema,
    CommandSchema,
    ArgumentSchema,
    OptionSchema,
    GoobitsConfigSchema,
    HeaderItemSchema,
    HeaderSectionSchema,
    CommandGroupSchema,
    RichConfigSchema,
    PythonConfigSchema,
    DependencyItem,
    DependenciesSchema,
    ExtrasSchema,
    InstallationSchema,
    ShellIntegrationSchema,
    ValidationSchema,
    MessagesSchema,
    InteractiveModeSchema,
    FeaturesSchema,
)

from .logging import (
    setup_logging,
    get_logger,
    set_context,
    clear_context,
    update_context,
    get_context,
    remove_context_keys,
    StructuredFormatter,
)

from .manifest import (
    ManifestUpdater,
    Result,
    update_manifests_for_build,
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
