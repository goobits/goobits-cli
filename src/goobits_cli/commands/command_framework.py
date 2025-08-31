"""
Command Framework
================

Core framework extracted from command_handler.j2 template.
Orchestrates CLI command generation for all languages with hierarchical command support.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
from enum import Enum


class ArgumentType(Enum):
    """Supported argument types."""
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    PATH = "path"
    EMAIL = "email"
    URL = "url"


class OptionType(Enum):
    """Supported option types."""
    STRING = "string"
    INTEGER = "integer" 
    FLOAT = "float"
    BOOLEAN = "boolean"
    CHOICE = "choice"
    PATH = "path"
    FILE = "file"
    DIRECTORY = "directory"


@dataclass
class Argument:
    """Command argument configuration."""
    name: str
    description: str
    type: ArgumentType = ArgumentType.STRING
    required: bool = True
    multiple: bool = False
    validation: Optional[Dict[str, Any]] = None


@dataclass
class Option:
    """Command option configuration."""
    name: str
    description: str
    type: OptionType = OptionType.STRING
    short: Optional[str] = None
    default: Any = None
    required: bool = False
    multiple: bool = False
    choices: Optional[List[str]] = None
    validation: Optional[Dict[str, Any]] = None


@dataclass
class Command:
    """Command configuration schema."""
    name: str
    description: str
    hook_name: str
    arguments: List[Argument] = field(default_factory=list)
    options: List[Option] = field(default_factory=list)
    subcommands: Dict[str, 'Command'] = field(default_factory=dict)
    hidden: bool = False
    deprecated: bool = False


@dataclass
class CommandConfig:
    """Command framework configuration schema."""
    project_name: str
    command_name: str
    commands: Dict[str, Command]
    global_options: List[Option] = field(default_factory=list)
    hook_file: str = ""
    error_handling: Dict[str, Any] = field(default_factory=dict)


class CommandFramework:
    """
    Command framework extracted from command_handler.j2.
    
    Generates CLI command structure for all supported languages
    with hierarchical commands, argument validation, and hook integration.
    """
    
    def __init__(self):
        """Initialize the command framework."""
        from .language_adapters import (
            PythonCommandAdapter,
            NodeJSCommandAdapter,
            TypeScriptCommandAdapter,
            RustCommandAdapter
        )
        
        self._adapters = {
            'python': PythonCommandAdapter(),
            'nodejs': NodeJSCommandAdapter(),
            'typescript': TypeScriptCommandAdapter(),
            'rust': RustCommandAdapter()
        }
    
    def generate_command_code(self, language: str, config: Dict[str, Any]) -> str:
        """
        Generate CLI command code for specified language.
        
        Args:
            language: Target language ('python', 'nodejs', 'typescript', 'rust')
            config: Configuration including commands and options
            
        Returns:
            Generated CLI command code as string
            
        Raises:
            ValueError: If language is not supported
        """
        if language not in self._adapters:
            supported = ', '.join(self._adapters.keys())
            raise ValueError(f"Unsupported language: {language}. Supported languages: {supported}")
        
        # Process configuration
        command_config = self._process_configuration(config)
        
        # Validate configuration
        self._validate_configuration(command_config)
        
        # Generate code using appropriate adapter
        adapter = self._adapters[language]
        return adapter.generate_code(command_config)
    
    def _process_configuration(self, config: Dict[str, Any]) -> CommandConfig:
        """Process raw configuration into structured command schema."""
        project = config.get('project', {})
        cli_config = config.get('cli', {})
        
        # Process commands
        commands = {}
        raw_commands = cli_config.get('commands', {})
        for cmd_name, cmd_data in raw_commands.items():
            commands[cmd_name] = self._process_command(cmd_name, cmd_data)
        
        # Process global options
        global_options = []
        for opt_data in cli_config.get('global_options', []):
            global_options.append(self._process_option(opt_data))
        
        return CommandConfig(
            project_name=project.get('name', 'CLI'),
            command_name=project.get('command_name', project.get('name', 'cli')),
            commands=commands,
            global_options=global_options,
            hook_file=cli_config.get('hook_file', ''),
            error_handling=cli_config.get('error_handling', {})
        )
    
    def _process_command(self, name: str, data: Dict[str, Any]) -> Command:
        """Process a single command definition."""
        # Process arguments
        arguments = []
        for arg_data in data.get('args', []):
            arguments.append(self._process_argument(arg_data))
        
        # Process options
        options = []
        for opt_data in data.get('options', []):
            options.append(self._process_option(opt_data))
        
        # Process subcommands recursively
        subcommands = {}
        for sub_name, sub_data in data.get('subcommands', {}).items():
            subcommands[sub_name] = self._process_command(sub_name, sub_data)
        
        return Command(
            name=name,
            description=data.get('desc', data.get('description', '')),
            hook_name=f"on_{name.replace('-', '_')}",
            arguments=arguments,
            options=options,
            subcommands=subcommands,
            hidden=data.get('hidden', False),
            deprecated=data.get('deprecated', False)
        )
    
    def _process_argument(self, data: Dict[str, Any]) -> Argument:
        """Process a single argument definition."""
        arg_type = ArgumentType.STRING
        if 'type' in data:
            try:
                arg_type = ArgumentType(data['type'])
            except ValueError:
                pass  # Default to STRING
        
        return Argument(
            name=data['name'],
            description=data.get('desc', data.get('description', '')),
            type=arg_type,
            required=data.get('required', True),
            multiple=data.get('multiple', False),
            validation=data.get('validation')
        )
    
    def _process_option(self, data: Dict[str, Any]) -> Option:
        """Process a single option definition."""
        opt_type = OptionType.STRING
        if 'type' in data:
            try:
                opt_type = OptionType(data['type'])
            except ValueError:
                pass  # Default to STRING
        
        return Option(
            name=data['name'],
            description=data.get('desc', data.get('description', '')),
            type=opt_type,
            short=data.get('short'),
            default=data.get('default'),
            required=data.get('required', False),
            multiple=data.get('multiple', False),
            choices=data.get('choices'),
            validation=data.get('validation')
        )
    
    def _validate_configuration(self, config: CommandConfig) -> None:
        """Validate the processed command configuration."""
        if not config.project_name:
            raise ValueError("Project name is required for command generation")
        
        if not config.command_name:
            raise ValueError("Command name is required for command generation")
        
        if not config.commands:
            raise ValueError("At least one command must be defined")
        
        # Validate each command recursively
        for cmd_name, command in config.commands.items():
            self._validate_command(cmd_name, command)
    
    def _validate_command(self, name: str, command: Command) -> None:
        """Validate a single command definition."""
        if not command.name:
            raise ValueError(f"Command name is required")
        
        if not command.description:
            raise ValueError(f"Command '{name}' requires a description")
        
        # Validate arguments
        for arg in command.arguments:
            if not arg.name:
                raise ValueError(f"Argument name is required in command '{name}'")
            if not arg.description:
                raise ValueError(f"Argument '{arg.name}' in command '{name}' requires a description")
        
        # Validate options
        for opt in command.options:
            if not opt.name:
                raise ValueError(f"Option name is required in command '{name}'")
            if not opt.description:
                raise ValueError(f"Option '{opt.name}' in command '{name}' requires a description")
            
            # Validate choice options
            if opt.type == OptionType.CHOICE and not opt.choices:
                raise ValueError(f"Choice option '{opt.name}' in command '{name}' requires choices")
        
        # Validate subcommands recursively
        for sub_name, subcommand in command.subcommands.items():
            self._validate_command(sub_name, subcommand)
    
    def build_command_tree(self, commands: Dict[str, Command]) -> Dict[str, Any]:
        """
        Build a hierarchical command tree for template generation.
        
        Args:
            commands: Dictionary of command definitions
            
        Returns:
            Hierarchical command tree structure
        """
        tree = {}
        
        for cmd_name, command in commands.items():
            tree[cmd_name] = {
                'name': command.name,
                'description': command.description,
                'hook_name': command.hook_name,
                'arguments': [self._argument_to_dict(arg) for arg in command.arguments],
                'options': [self._option_to_dict(opt) for opt in command.options],
                'subcommands': self.build_command_tree(command.subcommands) if command.subcommands else {},
                'hidden': command.hidden,
                'deprecated': command.deprecated
            }
        
        return tree
    
    def _argument_to_dict(self, arg: Argument) -> Dict[str, Any]:
        """Convert argument to dictionary for template use."""
        return {
            'name': arg.name,
            'description': arg.description,
            'type': arg.type.value,
            'required': arg.required,
            'multiple': arg.multiple,
            'validation': arg.validation or {}
        }
    
    def _option_to_dict(self, opt: Option) -> Dict[str, Any]:
        """Convert option to dictionary for template use."""
        return {
            'name': opt.name,
            'description': opt.description,
            'type': opt.type.value,
            'short': opt.short,
            'default': opt.default,
            'required': opt.required,
            'multiple': opt.multiple,
            'choices': opt.choices or [],
            'validation': opt.validation or {}
        }
    
    def get_all_hook_names(self, commands: Dict[str, Command]) -> List[str]:
        """
        Get all hook names from command tree for hook file generation.
        
        Args:
            commands: Dictionary of command definitions
            
        Returns:
            List of all hook function names
        """
        hooks = []
        
        for command in commands.values():
            hooks.append(command.hook_name)
            
            # Recursively get subcommand hooks
            if command.subcommands:
                hooks.extend(self.get_all_hook_names(command.subcommands))
        
        return hooks