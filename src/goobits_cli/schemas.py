"""Pydantic schemas for YAML configuration validation.

This module defines all schema classes used for validating YAML configuration
files in both the legacy CLI-only format and the new unified goobits.yaml format.
It supports multi-language CLI generation including Python, Node.js, TypeScript, and Rust.
"""

from typing import Dict, List, Optional, Any, Union, Literal
from pydantic import BaseModel, Field, field_validator, model_validator


class HeaderItemSchema(BaseModel):
    """Schema for individual header items in CLI help display."""

    item: str
    desc: str
    style: str = "example"  # Can be 'example' or 'setup'


class HeaderSectionSchema(BaseModel):
    """Schema for header sections in CLI help display."""

    title: str
    icon: Optional[str] = None
    items: List[HeaderItemSchema]


class ArgumentSchema(BaseModel):
    """Schema for positional command arguments."""

    name: str
    desc: str
    nargs: Optional[str] = None
    choices: Optional[List[str]] = None
    required: Optional[bool] = True


class OptionSchema(BaseModel):
    """Schema for command-line options/flags."""

    name: str
    short: Optional[str] = None
    type: str = "str"
    desc: Optional[str] = None  # Make optional for defensive programming
    default: Optional[Any] = None
    choices: Optional[List[str]] = None
    multiple: Optional[bool] = False


class CommandSchema(BaseModel):
    """Schema for CLI commands including arguments, options, and nested subcommands."""

    desc: str
    icon: Optional[str] = None
    is_default: Optional[bool] = False
    lifecycle: Optional[Literal["standard", "managed"]] = "standard"
    args: Optional[List[ArgumentSchema]] = Field(default_factory=list)
    options: Optional[List[OptionSchema]] = Field(default_factory=list)
    subcommands: Optional[Dict[str, "CommandSchema"]] = None

    @model_validator(mode="before")
    @classmethod
    def validate_no_arguments_field(cls, data):
        """Validate that 'arguments' field is not used - should be 'args' instead."""
        if isinstance(data, dict) and "arguments" in data:
            raise ValueError(
                "Invalid field 'arguments' in command configuration. "
                "Please use 'args' instead. Example:\n"
                "  commands:\n"
                "    greet:\n"
                "      desc: 'Greet someone'\n"
                "      args:  # <-- Use 'args', not 'arguments'\n"
                "        - name: name\n"
                "          desc: 'Name to greet'\n"
                "          type: string"
            )
        return data


class CommandGroupSchema(BaseModel):
    """Schema for grouping related commands in help display."""

    name: str
    commands: List[str]
    icon: Optional[str] = None


class RichConfigSchema(BaseModel):
    """Schema for Rich terminal formatting configuration."""

    rich_help_panel: Optional[bool] = True
    show_metavars_column: Optional[bool] = False
    append_metavars_help: Optional[bool] = True
    style_errors_suggestion: Optional[bool] = True
    max_width: Optional[int] = 120


class CLISchema(BaseModel):
    """Schema for CLI configuration including commands, options, and display settings."""

    name: str
    version: Optional[str] = None
    display_version: Optional[bool] = True
    tagline: str
    description: Optional[str] = None
    icon: Optional[str] = None
    header_sections: Optional[List[HeaderSectionSchema]] = None
    footer_note: Optional[str] = None
    options: Optional[List[OptionSchema]] = Field(default_factory=list)
    commands: Dict[str, CommandSchema]
    command_groups: Optional[List[CommandGroupSchema]] = None
    config: Optional[RichConfigSchema] = None
    enable_recursive_help: Optional[bool] = False
    enable_help_json: Optional[bool] = False


class ConfigSchema(BaseModel):
    """Legacy schema for CLI-only configuration files."""

    cli: CLISchema


# Enable forward references for nested command schemas
CommandSchema.model_rebuild()


# New schemas for goobits.yaml format (setup configuration)


class PythonConfigSchema(BaseModel):
    """Schema for Python-specific configuration."""

    minimum_version: str = "3.8"
    maximum_version: str = "3.13"


class DependencyItem(BaseModel):
    """Individual dependency with type and platform-specific configuration."""

    type: Literal["command", "system_package"] = "command"
    name: str
    description: Optional[str] = None

    # Platform-specific package names
    ubuntu: Optional[str] = None
    debian: Optional[str] = None
    centos: Optional[str] = None
    fedora: Optional[str] = None
    macos: Optional[str] = None
    windows: Optional[str] = None

    # Detection configuration
    check_method: Optional[
        Literal["pkg_config", "dpkg_query", "rpm_query", "file_exists", "brew_list"]
    ] = None
    check_args: Optional[List[str]] = None

    # Installation instructions
    install_instructions: Optional[Dict[str, str]] = None

    @field_validator("install_instructions")
    @classmethod
    def validate_install_instructions(cls, v):
        """Validate that install instructions use supported platform keys."""
        if v is None:
            return v

        valid_platforms = {
            "ubuntu",
            "debian",
            "centos",
            "fedora",
            "macos",
            "windows",
            "generic",
        }
        for platform in v.keys():
            if platform not in valid_platforms:
                raise ValueError(
                    f"Invalid platform '{platform}'. Must be one of {valid_platforms}"
                )

        return v


class DependenciesSchema(BaseModel):
    """Dependencies with backward compatibility for string format."""

    required: Union[
        List[str], List[DependencyItem], List[Union[str, DependencyItem]]
    ] = Field(default_factory=list)
    optional: Union[
        List[str], List[DependencyItem], List[Union[str, DependencyItem]]
    ] = Field(default_factory=list)

    @field_validator("required", "optional")
    @classmethod
    def normalize_dependencies(cls, v):
        """Convert strings to DependencyItem objects for backward compatibility."""
        if not v:
            return []

        normalized = []
        for item in v:
            if isinstance(item, str):
                # Convert string to DependencyItem
                normalized.append(DependencyItem(name=item, type="command"))
            elif isinstance(item, dict):
                # Handle dict format (from YAML)
                normalized.append(DependencyItem(**item))
            elif isinstance(item, DependencyItem):
                # Already a DependencyItem
                normalized.append(item)
            else:
                raise ValueError(f"Invalid dependency format: {item}")

        return normalized


class ExtrasSchema(BaseModel):
    """Schema for multi-language package extras/features."""

    python: Optional[List[str]] = None  # Python extras (e.g., ["audio", "dev"])
    npm: Optional[List[str]] = (
        None  # NPM packages (e.g., ["typescript", "@types/node"])
    )
    apt: Optional[List[str]] = (
        None  # APT packages (e.g., ["ffmpeg", "libportaudio2-dev"])
    )
    cargo: Optional[List[str]] = None  # Cargo features (e.g., ["cuda", "mkl"])


class InstallationSchema(BaseModel):
    """Schema for package installation configuration."""

    pypi_name: str
    development_path: str = "."
    extras: Optional[ExtrasSchema] = None  # Multi-language package extras


class ShellIntegrationSchema(BaseModel):
    """Schema for shell integration features."""

    enabled: bool = False
    alias: str


class ValidationSchema(BaseModel):
    """Schema for installation validation rules."""

    check_api_keys: bool = False
    check_disk_space: bool = True
    minimum_disk_space_mb: int = 100


class MessagesSchema(BaseModel):
    """Schema for customizable installation messages."""

    install_success: str = "Installation completed successfully!"
    install_dev_success: str = "Development installation completed successfully!"
    upgrade_success: str = "Upgrade completed successfully!"
    uninstall_success: str = "Uninstall completed successfully!"


class InteractiveModeSchema(BaseModel):
    """Schema for interactive mode features."""

    enabled: bool = True
    repl: bool = False  # Enable enhanced REPL features
    smart_completion: bool = True  # Enable smart completion from Phase 1A
    history_enabled: bool = True
    tab_completion: bool = True
    prompt: Optional[str] = None  # Custom prompt (defaults to CLI name)

    # Session Management (Phase 2 Advanced Interactive Mode)
    session_persistence: bool = False  # Enable session save/load functionality
    auto_save: bool = False  # Auto-save sessions on exit
    auto_load_last: bool = False  # Auto-load most recent session on startup
    max_sessions: int = 20  # Maximum number of sessions to keep
    max_history: int = 1000  # Maximum commands per session
    session_directory: Optional[str] = (
        None  # Custom session storage directory (defaults to ~/.goobits/sessions/)
    )

    # Variable System (Phase 3 Advanced Interactive Mode)
    variables: bool = False  # Enable variable storage and management
    variable_expansion: bool = True  # Enable $variable_name substitution in commands
    variable_types: bool = True  # Enable automatic type inference
    max_variables: int = 100  # Maximum number of variables to store per session

    # Pipeline System (Phase 4 Advanced Interactive Mode)
    pipelines: bool = (
        False  # Enable Unix-style pipeline operations (command1 | command2)
    )
    pipeline_templates: bool = (
        True  # Enable pipeline template definitions and execution
    )
    max_pipelines: int = 50  # Maximum number of pipeline templates to store
    pipeline_timeout: int = 60  # Default timeout for pipeline execution in seconds


class FeaturesSchema(BaseModel):
    """Schema for optional CLI features."""

    interactive_mode: Optional[InteractiveModeSchema] = Field(
        default_factory=InteractiveModeSchema
    )


class GoobitsConfigSchema(BaseModel):
    """Schema for the new unified goobits.yaml configuration format.

    This schema supports multi-language CLI generation including Python, Node.js,
    TypeScript, and Rust, with comprehensive package configuration options.
    """

    # Basic package information
    package_name: str
    command_name: str
    display_name: str
    description: str
    version: Optional[str] = "1.0.0"

    # Author and license information
    author: Optional[str] = "Unknown Author"
    email: Optional[str] = "unknown@example.com"
    license: Optional[str] = "MIT"
    homepage: Optional[str] = ""
    repository: Optional[str] = ""
    keywords: Optional[List[str]] = Field(default_factory=list)

    # Language selection (rust support now available)
    language: Optional[Literal["python", "nodejs", "typescript", "rust"]] = "python"

    # Multi-language target support
    languages: Optional[List[Literal["python", "nodejs", "typescript", "rust"]]] = None

    # CLI generation configuration
    cli_path: Optional[str] = None  # Path for main CLI file
    cli_hooks_path: Optional[str] = None  # Path for hooks file
    cli_types_path: Optional[str] = (
        None  # Path for TypeScript types file (TypeScript only)
    )

    # Python configuration
    python: Optional[PythonConfigSchema] = Field(default_factory=PythonConfigSchema)

    # Dependencies
    dependencies: Optional[DependenciesSchema] = Field(
        default_factory=DependenciesSchema
    )

    # Installation settings
    installation: Optional[InstallationSchema] = None

    # Shell integration
    shell_integration: Optional[ShellIntegrationSchema] = None

    # Validation rules
    validation: Optional[ValidationSchema] = Field(default_factory=ValidationSchema)

    # Post-installation messages
    messages: Optional[MessagesSchema] = Field(default_factory=MessagesSchema)

    # Optional feature configuration
    features: Optional[FeaturesSchema] = Field(default_factory=FeaturesSchema)

    # Optional CLI configuration (for backward compatibility)
    cli: Optional[CLISchema] = None

    @model_validator(mode="after")
    def validate_language_configuration(self):
        """Validate language/languages field consistency and set defaults."""
        # If languages is provided, ensure it's not empty
        if self.languages is not None:
            if not self.languages:
                raise ValueError(
                    "'languages' field cannot be empty. Provide at least one target language."
                )

            # Remove duplicates while preserving order
            seen = set()
            unique_languages = []
            for lang in self.languages:
                if lang not in seen:
                    seen.add(lang)
                    unique_languages.append(lang)
            self.languages = unique_languages

            # If both language and languages are provided, languages takes precedence
            if self.language is not None and self.language != "python":
                # Only warn if the single language isn't in the languages list
                if self.language not in self.languages:
                    raise ValueError(
                        f"Conflicting language configuration: 'language: {self.language}' "
                        f"not found in 'languages: {self.languages}'. "
                        f"Use either 'language' OR 'languages', not both."
                    )

        # If neither is provided, default to Python
        elif self.language is None:
            self.language = "python"

        return self

    def get_target_languages(self) -> List[str]:
        """Get the list of target languages for generation.

        Returns:
            List of target languages. If 'languages' is specified, returns that list.
            Otherwise, returns a single-item list with the 'language' value.
        """
        if self.languages is not None:
            return self.languages
        else:
            return [self.language or "python"]
