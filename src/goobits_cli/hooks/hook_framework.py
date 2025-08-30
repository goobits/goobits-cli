"""
Hook Framework
=============

Core framework extracted from hook_system.j2 template.
Orchestrates hook system generation for all languages with consistent functionality.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List, Callable
from enum import Enum


class HookType(Enum):
    """Types of hooks."""
    COMMAND = "command"
    SUBCOMMAND = "subcommand"
    BUILTIN = "builtin"
    LIFECYCLE = "lifecycle"


class HookExecutionMode(Enum):
    """Hook execution modes."""
    SYNC = "sync"
    ASYNC = "async"
    BOTH = "both"


@dataclass
class HookDefinition:
    """Hook function definition."""
    name: str
    hook_name: str
    description: str
    hook_type: HookType = HookType.COMMAND
    arguments: List[Dict[str, Any]] = field(default_factory=list)
    options: List[Dict[str, Any]] = field(default_factory=list)
    return_type: str = "int"
    execution_mode: HookExecutionMode = HookExecutionMode.SYNC
    required: bool = True
    
    def get_function_name(self) -> str:
        """Get the hook function name."""
        return self.hook_name
    
    def get_signature_args(self) -> List[str]:
        """Get function signature arguments."""
        args = []
        
        # Add arguments
        for arg in self.arguments:
            arg_name = arg.get('name', '')
            if arg.get('multiple', False):
                args.append(f"{arg_name}: List[str]")
            else:
                arg_type = arg.get('type', 'str')
                python_type = {
                    'string': 'str',
                    'integer': 'int', 
                    'float': 'float',
                    'boolean': 'bool'
                }.get(arg_type, 'str')
                args.append(f"{arg_name}: {python_type}")
        
        # Add options
        for opt in self.options:
            opt_name = opt.get('name', '').replace('-', '_')
            opt_type = opt.get('type', 'str')
            default_value = opt.get('default')
            
            if opt_type == 'boolean':
                args.append(f"{opt_name}: bool = {str(default_value or False)}")
            elif opt_type == 'integer':
                args.append(f"{opt_name}: Optional[int] = {default_value or 'None'}")
            elif opt_type == 'float':
                args.append(f"{opt_name}: Optional[float] = {default_value or 'None'}")
            else:
                if default_value:
                    args.append(f"{opt_name}: str = '{default_value}'")
                else:
                    args.append(f"{opt_name}: Optional[str] = None")
        
        return args


@dataclass
class HookConfig:
    """Hook framework configuration schema."""
    project_name: str
    language: str
    commands: List[HookDefinition] = field(default_factory=list)
    hook_file: str = "cli_hooks"
    hook_file_extension: str = ""
    module_search_paths: List[str] = field(default_factory=list)
    auto_reload: bool = False
    cache_hooks: bool = True
    error_handling: Dict[str, Any] = field(default_factory=dict)
    template_format: str = "default"


class HookFramework:
    """
    Hook framework extracted from hook_system.j2.
    
    Generates hook system implementations for all supported languages
    with consistent hook loading, discovery, execution, and template generation.
    """
    
    def __init__(self):
        """Initialize the hook framework."""
        from .language_adapters import (
            PythonHookAdapter,
            NodeJSHookAdapter,
            TypeScriptHookAdapter,
            RustHookAdapter
        )
        
        self._adapters = {
            'python': PythonHookAdapter(),
            'nodejs': NodeJSHookAdapter(),
            'typescript': TypeScriptHookAdapter(),
            'rust': RustHookAdapter()
        }
    
    def generate_hook_code(self, language: str, config: Dict[str, Any]) -> str:
        """
        Generate hook system code for specified language.
        
        Args:
            language: Target language ('python', 'nodejs', 'typescript', 'rust')
            config: Configuration including project metadata and CLI commands
            
        Returns:
            Generated hook system code as string
            
        Raises:
            ValueError: If language is not supported
        """
        if language not in self._adapters:
            supported = ', '.join(self._adapters.keys())
            raise ValueError(f"Unsupported language: {language}. Supported languages: {supported}")
        
        # Process configuration
        hook_config = self._process_configuration(config, language)
        
        # Validate configuration
        self._validate_configuration(hook_config)
        
        # Generate code using appropriate adapter
        adapter = self._adapters[language]
        return adapter.generate_code(hook_config)
    
    def _process_configuration(self, config: Dict[str, Any], language: str) -> HookConfig:
        """Process raw configuration into structured hook schema."""
        project = config.get('project', {})
        cli_config = config.get('cli', {})
        
        # Extract project information
        project_name = project.get('name', 'CLI')
        
        # Process commands into hook definitions
        commands = []
        cli_commands = cli_config.get('commands', {})
        
        for cmd_name, cmd_data in cli_commands.items():
            hook_name = f"on_{cmd_name.replace('-', '_')}"
            
            commands.append(HookDefinition(
                name=cmd_name,
                hook_name=hook_name,
                description=cmd_data.get('desc', cmd_data.get('description', f'Handle {cmd_name} command')),
                hook_type=HookType.COMMAND,
                arguments=cmd_data.get('args', []),
                options=cmd_data.get('options', []),
                return_type=self._get_return_type_for_language(language),
                execution_mode=self._get_execution_mode_for_language(language)
            ))
            
            # Process subcommands
            for sub_name, sub_data in cmd_data.get('subcommands', {}).items():
                sub_hook_name = f"on_{cmd_name.replace('-', '_')}_{sub_name.replace('-', '_')}"
                
                commands.append(HookDefinition(
                    name=f"{cmd_name}.{sub_name}",
                    hook_name=sub_hook_name,
                    description=sub_data.get('desc', sub_data.get('description', f'Handle {cmd_name} {sub_name} subcommand')),
                    hook_type=HookType.SUBCOMMAND,
                    arguments=sub_data.get('args', []),
                    options=sub_data.get('options', []),
                    return_type=self._get_return_type_for_language(language),
                    execution_mode=self._get_execution_mode_for_language(language)
                ))
        
        # Language-specific hook file settings
        hook_file_settings = self._get_hook_file_settings(language)
        
        return HookConfig(
            project_name=project_name,
            language=language,
            commands=commands,
            hook_file=hook_file_settings['file'],
            hook_file_extension=hook_file_settings['extension'],
            module_search_paths=hook_file_settings.get('search_paths', []),
            auto_reload=config.get('development', {}).get('auto_reload', False),
            cache_hooks=config.get('performance', {}).get('cache_hooks', True),
            error_handling=config.get('error_handling', {}),
            template_format=config.get('template_format', 'default')
        )
    
    def _get_return_type_for_language(self, language: str) -> str:
        """Get appropriate return type for language."""
        return_types = {
            'python': 'int',
            'nodejs': 'number',
            'typescript': 'number | Promise<number>',
            'rust': 'Result<()>'
        }
        return return_types.get(language, 'int')
    
    def _get_execution_mode_for_language(self, language: str) -> HookExecutionMode:
        """Get execution mode for language."""
        modes = {
            'python': HookExecutionMode.SYNC,
            'nodejs': HookExecutionMode.ASYNC,
            'typescript': HookExecutionMode.BOTH,
            'rust': HookExecutionMode.SYNC
        }
        return modes.get(language, HookExecutionMode.SYNC)
    
    def _get_hook_file_settings(self, language: str) -> Dict[str, Any]:
        """Get hook file settings for language."""
        settings = {
            'python': {
                'file': 'cli_hooks',
                'extension': '.py',
                'search_paths': ['.', 'hooks', 'src']
            },
            'nodejs': {
                'file': 'hooks',
                'extension': '.js',
                'search_paths': ['.', 'hooks', 'src']
            },
            'typescript': {
                'file': 'hooks',
                'extension': '.ts',
                'search_paths': ['.', 'hooks', 'src']
            },
            'rust': {
                'file': 'hooks',
                'extension': '.rs',
                'search_paths': ['src']
            }
        }
        return settings.get(language, settings['python'])
    
    def _validate_configuration(self, config: HookConfig) -> None:
        """Validate the processed hook configuration."""
        if not config.project_name:
            raise ValueError("Project name is required for hook generation")
        
        if not config.language:
            raise ValueError("Language is required for hook generation")
        
        if not config.commands:
            raise ValueError("At least one command must be defined for hook generation")
        
        # Validate hook definitions
        for hook_def in config.commands:
            if not hook_def.name:
                raise ValueError("Hook definition name is required")
            
            if not hook_def.hook_name:
                raise ValueError(f"Hook name is required for command '{hook_def.name}'")
            
            if not hook_def.description:
                raise ValueError(f"Hook description is required for command '{hook_def.name}'")
    
    def get_hook_definitions(self, config: HookConfig) -> List[HookDefinition]:
        """Get list of hook definitions."""
        return config.commands
    
    def get_hook_by_name(self, config: HookConfig, hook_name: str) -> Optional[HookDefinition]:
        """Get hook definition by hook name."""
        for hook_def in config.commands:
            if hook_def.hook_name == hook_name:
                return hook_def
        return None
    
    def generate_hook_template(self, language: str, config: Dict[str, Any]) -> str:
        """
        Generate hook template file for users.
        
        Args:
            language: Target language
            config: Configuration dictionary
            
        Returns:
            Generated hook template code
        """
        hook_config = self._process_configuration(config, language)
        adapter = self._adapters[language]
        return adapter.generate_template(hook_config)
    
    def get_supported_languages(self) -> List[str]:
        """Get list of supported languages."""
        return list(self._adapters.keys())
    
    def supports_async_execution(self, language: str) -> bool:
        """Check if language supports async hook execution."""
        return language in ('nodejs', 'typescript')
    
    def get_hook_file_path(self, config: HookConfig) -> str:
        """Get full hook file path."""
        return f"{config.hook_file}{config.hook_file_extension}"