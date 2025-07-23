from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field


class ExampleSchema(BaseModel):
    cmd: str
    desc: str
    section_title: Optional[str] = "Examples"
    section_icon: Optional[str] = None


class SetupStepSchema(BaseModel):
    step: str
    cmd: str
    section_title: Optional[str] = "First-time Setup"
    section_icon: Optional[str] = None


class ArgumentSchema(BaseModel):
    name: str
    desc: str
    nargs: Optional[str] = None
    choices: Optional[List[str]] = None


class OptionSchema(BaseModel):
    name: str
    short: Optional[str] = None
    type: str = "str"
    desc: str
    default: Optional[Any] = None
    choices: Optional[List[str]] = None


class CommandSchema(BaseModel):
    desc: str
    icon: Optional[str] = None
    is_default: Optional[bool] = False
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
    examples: Optional[List[ExampleSchema]] = None
    setup_guide: Optional[str] = None
    setup_steps: Optional[List[SetupStepSchema]] = None
    footer_note: Optional[str] = None
    commands: Dict[str, CommandSchema]
    command_groups: Optional[List[CommandGroupSchema]] = None
    config: Optional[RichConfigSchema] = None


class ConfigSchema(BaseModel):
    cli: CLISchema


# Enable forward references for nested command schemas
CommandSchema.model_rebuild()


# New schemas for goobits.yaml format (setup configuration)
class PythonConfigSchema(BaseModel):
    minimum_version: str = "3.8"
    maximum_version: str = ""


class DependenciesSchema(BaseModel):
    required: List[str] = Field(default_factory=list)
    optional: List[str] = Field(default_factory=list)


class InstallationSchema(BaseModel):
    pypi_name: str
    development_path: str = "."


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
    
    # Python configuration
    python: PythonConfigSchema
    
    # Dependencies
    dependencies: DependenciesSchema
    
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