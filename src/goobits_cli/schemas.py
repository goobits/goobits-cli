from typing import Dict, List, Optional, Any, Union, Literal
from pydantic import BaseModel, Field, field_validator, model_validator


class HeaderItemSchema(BaseModel):
    item: str
    desc: str
    style: str = 'example'  # Can be 'example' or 'setup'


class HeaderSectionSchema(BaseModel):
    title: str
    icon: Optional[str] = None
    items: List[HeaderItemSchema]


class ArgumentSchema(BaseModel):
    name: str
    desc: str
    nargs: Optional[str] = None
    choices: Optional[List[str]] = None
    required: Optional[bool] = True


class OptionSchema(BaseModel):
    name: str
    short: Optional[str] = None
    type: str = "str"
    desc: str
    default: Optional[Any] = None
    choices: Optional[List[str]] = None
    multiple: Optional[bool] = False


class CommandSchema(BaseModel):
    desc: str
    icon: Optional[str] = None
    is_default: Optional[bool] = False
    lifecycle: Optional[Literal["standard", "managed"]] = "standard"
    args: Optional[List[ArgumentSchema]] = Field(default_factory=list)
    options: Optional[List[OptionSchema]] = Field(default_factory=list)
    subcommands: Optional[Dict[str, "CommandSchema"]] = None


class CommandGroupSchema(BaseModel):
    name: str
    commands: List[str]
    icon: Optional[str] = None


class RichConfigSchema(BaseModel):
    rich_help_panel: Optional[bool] = True
    show_metavars_column: Optional[bool] = False
    append_metavars_help: Optional[bool] = True
    style_errors_suggestion: Optional[bool] = True
    max_width: Optional[int] = 120


class CLISchema(BaseModel):
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
    cli: CLISchema


# Enable forward references for nested command schemas
CommandSchema.model_rebuild()


# New schemas for goobits.yaml format (setup configuration)
class PythonConfigSchema(BaseModel):
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
    check_method: Optional[Literal["pkg_config", "dpkg_query", "rpm_query", "file_exists", "brew_list"]] = None
    check_args: Optional[List[str]] = None
    
    # Installation instructions
    install_instructions: Optional[Dict[str, str]] = None
    
    @field_validator('install_instructions')
    @classmethod
    def validate_install_instructions(cls, v):
        if v is None:
            return v
        valid_platforms = {'ubuntu', 'debian', 'centos', 'fedora', 'macos', 'windows', 'generic'}
        for platform in v.keys():
            if platform not in valid_platforms:
                raise ValueError(f"Invalid platform '{platform}'. Must be one of {valid_platforms}")
        return v


class DependenciesSchema(BaseModel):
    """Dependencies with backward compatibility for string format."""
    required: Union[List[str], List[DependencyItem], List[Union[str, DependencyItem]]] = Field(default_factory=list)
    optional: Union[List[str], List[DependencyItem], List[Union[str, DependencyItem]]] = Field(default_factory=list)
    
    @field_validator('required', 'optional')
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
    npm: Optional[List[str]] = None     # NPM packages (e.g., ["typescript", "@types/node"])
    apt: Optional[List[str]] = None     # APT packages (e.g., ["ffmpeg", "libportaudio2-dev"])
    cargo: Optional[List[str]] = None   # Cargo features (e.g., ["cuda", "mkl"])


class InstallationSchema(BaseModel):
    pypi_name: str
    development_path: str = "."
    extras: Optional[ExtrasSchema] = None  # Multi-language package extras


class ShellIntegrationSchema(BaseModel):
    enabled: bool = False
    alias: str


class ValidationSchema(BaseModel):
    check_api_keys: bool = False
    check_disk_space: bool = True
    minimum_disk_space_mb: int = 100


class MessagesSchema(BaseModel):
    install_success: str = "Installation completed successfully!"
    install_dev_success: str = "Development installation completed successfully!"
    upgrade_success: str = "Upgrade completed successfully!"
    uninstall_success: str = "Uninstall completed successfully!"


class GoobitsConfigSchema(BaseModel):
    """Schema for the new unified goobits.yaml configuration format."""
    # Basic package information
    package_name: str
    command_name: str
    display_name: str
    description: str
    
    # Language selection (rust support now available)
    language: Literal["python", "nodejs", "typescript", "rust"] = "python"
    
    # CLI generation configuration
    cli_output_path: str = "src/{package_name}/cli.py"
    hooks_path: Optional[str] = None
    
    # Python configuration
    python: PythonConfigSchema
    
    # Dependencies
    dependencies: DependenciesSchema
    
    # Language-specific dependencies
    
    # Installation settings
    installation: InstallationSchema
    
    # Shell integration
    shell_integration: ShellIntegrationSchema
    
    # Validation rules
    validation: ValidationSchema
    
    # Post-installation messages
    messages: MessagesSchema
    
    # Optional CLI configuration (for backward compatibility)
    cli: Optional[CLISchema] = None