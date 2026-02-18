"""
Intermediate Representation (IR) Models for the Universal Template System.

This module defines frozen dataclasses that represent the language-agnostic
intermediate representation used between configuration parsing and code generation.

All models are frozen (immutable) to ensure consistency during the rendering process.

See docs/IR_SCHEMA.md for the complete specification.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass(frozen=True)
class IRArgument:
    """
    Represents a positional argument in a CLI command.

    Attributes:
        name: Argument name
        type: Argument type (string, integer, float, etc.)
        nargs: Number of arguments (None, '?', '*', '+', or int)
        help: Help text for the argument
        required: Whether the argument is required
        default: Default value if not provided
        metavar: Display name in help text
    """

    name: str
    type: str = "string"
    nargs: Optional[str] = None
    help: str = ""
    required: bool = True
    default: Optional[Any] = None
    metavar: Optional[str] = None


@dataclass(frozen=True)
class IROption:
    """
    Represents a command-line option (flag).

    Attributes:
        name: Option name (without dashes)
        short: Short form (single character, e.g., 'v' for -v)
        type: Option type (string, integer, boolean, etc.)
        default: Default value
        required: Whether the option is required
        help: Help text for the option
        multiple: Whether option can be specified multiple times
        choices: Valid choices for the option value
        metavar: Display name in help text
        is_flag: Whether this is a boolean flag (no value)
        envvar: Environment variable to read default from
    """

    name: str
    short: Optional[str] = None
    type: str = "string"
    default: Optional[Any] = None
    required: bool = False
    help: str = ""
    multiple: bool = False
    choices: Optional[tuple] = None
    metavar: Optional[str] = None
    is_flag: bool = False
    envvar: Optional[str] = None


@dataclass(frozen=True)
class IRCommand:
    """
    Represents a CLI command or subcommand.

    Attributes:
        name: Command name
        description: Command description/help text
        options: List of command options
        arguments: List of positional arguments
        subcommands: Nested subcommands
        examples: Usage examples
        aliases: Alternative command names
        hidden: Whether command is hidden from help
    """

    name: str
    description: str = ""
    options: tuple = field(default_factory=tuple)
    arguments: tuple = field(default_factory=tuple)
    subcommands: tuple = field(default_factory=tuple)
    examples: tuple = field(default_factory=tuple)
    aliases: tuple = field(default_factory=tuple)
    hidden: bool = False


@dataclass(frozen=True)
class IRMetadata:
    """
    Metadata about the generated CLI.

    Attributes:
        config_filename: Source configuration filename
        generator_version: Version of goobits-cli used
        generated_at: Timestamp of generation
        features: Feature flags detected during analysis
    """

    config_filename: str = "goobits.yaml"
    generator_version: str = "3.0.0"
    generated_at: Optional[str] = None
    features: Optional[Dict[str, bool]] = None


@dataclass(frozen=True)
class IRProject:
    """
    Project-level information.

    Attributes:
        name: Project/CLI name
        description: Project description
        version: Project version
        author: Project author
        license: Project license
        package_name: Package name for installation
        command_name: CLI command name
    """

    name: str
    description: str = ""
    version: str = "0.1.0"
    author: str = ""
    license: str = ""
    package_name: str = ""
    command_name: str = ""


@dataclass(frozen=True)
class IRCLI:
    """
    CLI-specific configuration.

    Attributes:
        root_command: The root command definition
        commands: Top-level commands
        global_options: Options available on all commands
        completion: Shell completion configuration
        interactive: Interactive mode configuration
    """

    root_command: Optional[IRCommand] = None
    commands: tuple = field(default_factory=tuple)
    global_options: tuple = field(default_factory=tuple)
    completion: Optional[Dict[str, Any]] = None
    interactive: Optional[Dict[str, Any]] = None


@dataclass(frozen=True)
class IR:
    """
    Complete Intermediate Representation for CLI generation.

    This is the root object passed to renderers, containing all
    information needed to generate a CLI implementation.

    Attributes:
        project: Project-level information
        cli: CLI configuration and commands
        metadata: Generation metadata
        installation: Installation configuration
        features: Detected feature requirements
    """

    project: IRProject
    cli: IRCLI
    metadata: IRMetadata = field(default_factory=IRMetadata)
    installation: Optional[Dict[str, Any]] = None
    features: Optional[Dict[str, bool]] = None

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert IR to a dictionary for template rendering.

        Returns:
            Dictionary representation of the IR
        """
        return {
            "project": {
                "name": self.project.name,
                "description": self.project.description,
                "version": self.project.version,
                "author": self.project.author,
                "license": self.project.license,
                "package_name": self.project.package_name,
                "command_name": self.project.command_name,
            },
            "cli": self._cli_to_dict(),
            "metadata": {
                "config_filename": self.metadata.config_filename,
                "generator_version": self.metadata.generator_version,
                "generated_at": self.metadata.generated_at,
                "features": self.metadata.features or {},
            },
            "installation": self.installation or {},
            "features": self.features or {},
        }

    def _cli_to_dict(self) -> Dict[str, Any]:
        """Convert CLI configuration to dictionary."""
        return {
            "root_command": (
                self._command_to_dict(self.cli.root_command)
                if self.cli.root_command
                else None
            ),
            "commands": {
                cmd.name: self._command_to_dict(cmd) for cmd in self.cli.commands
            },
            "global_options": [
                self._option_to_dict(opt) for opt in self.cli.global_options
            ],
            "completion": self.cli.completion,
            "interactive": self.cli.interactive,
        }

    def _command_to_dict(self, cmd: IRCommand) -> Dict[str, Any]:
        """Convert a command to dictionary."""
        return {
            "name": cmd.name,
            "description": cmd.description,
            "options": [self._option_to_dict(opt) for opt in cmd.options],
            "arguments": [self._argument_to_dict(arg) for arg in cmd.arguments],
            "subcommands": {
                sub.name: self._command_to_dict(sub) for sub in cmd.subcommands
            },
            "examples": list(cmd.examples),
            "aliases": list(cmd.aliases),
            "hidden": cmd.hidden,
        }

    def _option_to_dict(self, opt: IROption) -> Dict[str, Any]:
        """Convert an option to dictionary."""
        return {
            "name": opt.name,
            "short": opt.short,
            "type": opt.type,
            "default": opt.default,
            "required": opt.required,
            "help": opt.help,
            "multiple": opt.multiple,
            "choices": list(opt.choices) if opt.choices else None,
            "metavar": opt.metavar,
            "is_flag": opt.is_flag,
            "envvar": opt.envvar,
        }

    def _argument_to_dict(self, arg: IRArgument) -> Dict[str, Any]:
        """Convert an argument to dictionary."""
        return {
            "name": arg.name,
            "type": arg.type,
            "nargs": arg.nargs,
            "help": arg.help,
            "required": arg.required,
            "default": arg.default,
            "metavar": arg.metavar,
        }


def create_ir_from_dict(data: Dict[str, Any]) -> IR:
    """
    Create an IR instance from a dictionary.

    This is useful for converting the output of IRBuilder into
    frozen IR dataclasses.

    Args:
        data: Dictionary with IR data

    Returns:
        Frozen IR instance
    """
    project_data = data.get("project", {})
    project = IRProject(
        name=project_data.get("name", ""),
        description=project_data.get("description", ""),
        version=project_data.get("version", "0.1.0"),
        author=project_data.get("author", ""),
        license=project_data.get("license", ""),
        package_name=project_data.get("package_name", ""),
        command_name=project_data.get("command_name", ""),
    )

    cli_data = data.get("cli", {})
    commands = tuple(
        _create_command_from_dict(name, cmd_data)
        for name, cmd_data in cli_data.get("commands", {}).items()
    )

    root_cmd_data = cli_data.get("root_command")
    root_command = (
        _create_command_from_dict("root", root_cmd_data) if root_cmd_data else None
    )

    global_options = tuple(
        _create_option_from_dict(opt) for opt in cli_data.get("global_options", [])
    )

    cli = IRCLI(
        root_command=root_command,
        commands=commands,
        global_options=global_options,
        completion=cli_data.get("completion"),
        interactive=cli_data.get("interactive"),
    )

    metadata_data = data.get("metadata", {})
    metadata = IRMetadata(
        config_filename=metadata_data.get("config_filename", "goobits.yaml"),
        generator_version=metadata_data.get("generator_version", "3.0.0"),
        generated_at=metadata_data.get("generated_at"),
        features=metadata_data.get("features"),
    )

    return IR(
        project=project,
        cli=cli,
        metadata=metadata,
        installation=data.get("installation"),
        features=data.get("features") or data.get("feature_requirements"),
    )


def _create_command_from_dict(name: str, data: Dict[str, Any]) -> IRCommand:
    """Create an IRCommand from dictionary data."""
    options = tuple(_create_option_from_dict(opt) for opt in data.get("options", []))
    arguments = tuple(
        _create_argument_from_dict(arg) for arg in data.get("arguments", [])
    )
    subcommands = tuple(
        _create_command_from_dict(sub_name, sub_data)
        for sub_name, sub_data in data.get("subcommands", {}).items()
    )

    return IRCommand(
        name=name,
        description=data.get("description", data.get("desc", "")),
        options=options,
        arguments=arguments,
        subcommands=subcommands,
        examples=tuple(data.get("examples", [])),
        aliases=tuple(data.get("aliases", [])),
        hidden=data.get("hidden", False),
    )


def _create_option_from_dict(data: Dict[str, Any]) -> IROption:
    """Create an IROption from dictionary data."""
    choices = data.get("choices")
    return IROption(
        name=data.get("name", ""),
        short=data.get("short"),
        type=data.get("type", "string"),
        default=data.get("default"),
        required=data.get("required", False),
        help=data.get("help", data.get("desc", "")),
        multiple=data.get("multiple", False),
        choices=tuple(choices) if choices else None,
        metavar=data.get("metavar"),
        is_flag=data.get("is_flag", False),
        envvar=data.get("envvar"),
    )


def _create_argument_from_dict(data: Dict[str, Any]) -> IRArgument:
    """Create an IRArgument from dictionary data."""
    return IRArgument(
        name=data.get("name", ""),
        type=data.get("type", "string"),
        nargs=data.get("nargs"),
        help=data.get("help", data.get("desc", "")),
        required=data.get("required", True),
        default=data.get("default"),
        metavar=data.get("metavar"),
    )


__all__ = [
    "IR",
    "IRCLI",
    "IRCommand",
    "IROption",
    "IRArgument",
    "IRMetadata",
    "IRProject",
    "create_ir_from_dict",
]
