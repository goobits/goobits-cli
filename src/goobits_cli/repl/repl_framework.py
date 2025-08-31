"""
REPL Framework
==============

Core framework extracted from repl_loop.j2 template.
Orchestrates REPL generation for all languages with consistent functionality.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
from enum import Enum
from .repl_engine import REPLEngine
from .history_manager import HistoryManager
from .language_adapters import (
    PythonREPLAdapter,
    NodeJSREPLAdapter,
    TypeScriptREPLAdapter,
    RustREPLAdapter
)


class REPLMode(Enum):
    """REPL generation modes."""
    BASIC = "basic"
    ENHANCED = "enhanced"
    FULL_FEATURED = "full"


@dataclass
class REPLConfig:
    """REPL framework configuration schema."""
    project_name: str
    language: str
    cli_commands: Dict[str, Any] = field(default_factory=dict)
    repl_mode: REPLMode = REPLMode.ENHANCED
    enable_history: bool = True
    enable_completion: bool = True
    enable_multiline: bool = True
    enable_system_commands: bool = True
    max_history_entries: int = 1000
    prompt_template: Optional[str] = None
    continuation_prompt_template: Optional[str] = None
    welcome_message: Optional[str] = None
    features: Dict[str, Any] = field(default_factory=dict)


class REPLFramework:
    """
    REPL framework extracted from repl_loop.j2 template.
    
    Generates enhanced Read-Eval-Print Loop systems for all supported languages
    with multi-line support, command history, smart completion, and session management.
    """
    
    def __init__(self):
        """Initialize the REPL framework."""
        self._adapters = {
            'python': PythonREPLAdapter(),
            'nodejs': NodeJSREPLAdapter(),
            'typescript': TypeScriptREPLAdapter(),
            'rust': RustREPLAdapter()
        }
    
    def generate_repl_code(self, language: str, config: Dict[str, Any]) -> str:
        """
        Generate REPL system code for specified language.
        
        Args:
            language: Target language ('python', 'nodejs', 'typescript', 'rust')
            config: Configuration including project metadata and CLI commands
            
        Returns:
            Generated REPL system code as string
            
        Raises:
            ValueError: If language is not supported
        """
        if language not in self._adapters:
            supported = ', '.join(self._adapters.keys())
            raise ValueError(f"Unsupported language: {language}. Supported languages: {supported}")
        
        # Process configuration
        repl_config = self._process_configuration(config, language)
        
        # Validate configuration
        self._validate_configuration(repl_config)
        
        # Generate code using appropriate adapter
        adapter = self._adapters[language]
        return adapter.generate_repl_code(config)
    
    def generate_session_manager_code(self, language: str, config: Dict[str, Any]) -> str:
        """
        Generate session management code for specified language.
        
        Args:
            language: Target language
            config: Configuration dictionary
            
        Returns:
            Generated session manager code as string
        """
        if language not in self._adapters:
            supported = ', '.join(self._adapters.keys())
            raise ValueError(f"Unsupported language: {language}. Supported languages: {supported}")
        
        adapter = self._adapters[language]
        return adapter.generate_session_manager_code(config)
    
    def _process_configuration(self, config: Dict[str, Any], language: str) -> REPLConfig:
        """Process raw configuration into structured REPL schema."""
        project = config.get('project', {})
        cli_config = config.get('cli', {})
        repl_settings = config.get('features', {}).get('interactive_mode', {}).get('repl', {})
        
        # Extract project information
        project_name = project.get('name', 'CLI')
        
        # Extract CLI commands
        commands = cli_config.get('commands', {})
        
        # Process REPL settings
        repl_mode = repl_settings.get('mode', 'enhanced')
        mode_map = {
            'basic': REPLMode.BASIC,
            'enhanced': REPLMode.ENHANCED,
            'full': REPLMode.FULL_FEATURED
        }
        repl_mode = mode_map.get(repl_mode, REPLMode.ENHANCED)
        
        return REPLConfig(
            project_name=project_name,
            language=language,
            cli_commands=commands,
            repl_mode=repl_mode,
            enable_history=repl_settings.get('enable_history', True),
            enable_completion=repl_settings.get('enable_completion', True),
            enable_multiline=repl_settings.get('enable_multiline', True),
            enable_system_commands=repl_settings.get('enable_system_commands', True),
            max_history_entries=repl_settings.get('max_history_entries', 1000),
            prompt_template=repl_settings.get('prompt_template'),
            continuation_prompt_template=repl_settings.get('continuation_prompt_template'),
            welcome_message=repl_settings.get('welcome_message'),
            features=repl_settings.get('features', {})
        )
    
    def _validate_configuration(self, config: REPLConfig) -> None:
        """Validate the processed REPL configuration."""
        if not config.project_name:
            raise ValueError("Project name is required for REPL generation")
        
        if not config.language:
            raise ValueError("Language is required for REPL generation")
        
        if config.language not in self._adapters:
            supported = ', '.join(self._adapters.keys())
            raise ValueError(f"Unsupported language: {config.language}. Supported: {supported}")
        
        if config.max_history_entries < 0:
            raise ValueError("max_history_entries must be non-negative")
    
    def create_repl_engine(self, config: Dict[str, Any]) -> REPLEngine:
        """
        Create a REPL engine instance for runtime use.
        
        Args:
            config: Configuration dictionary
            
        Returns:
            Configured REPLEngine instance
        """
        return REPLEngine(config)
    
    def create_history_manager(self, cli_name: str, **kwargs) -> HistoryManager:
        """
        Create a history manager instance.
        
        Args:
            cli_name: Name of the CLI application
            **kwargs: Additional history manager options
            
        Returns:
            Configured HistoryManager instance
        """
        return HistoryManager(cli_name, **kwargs)
    
    def get_supported_languages(self) -> List[str]:
        """Get list of supported languages."""
        return list(self._adapters.keys())
    
    def get_repl_features(self, language: str) -> Dict[str, Any]:
        """
        Get available REPL features for a language.
        
        Args:
            language: Target language
            
        Returns:
            Dictionary of available features
        """
        features = {
            'multi_line_support': True,
            'command_history': True,
            'session_variables': True,
            'system_commands': True,
            'builtin_commands': ['help', 'exit', 'quit', 'history', 'vars', 'clear'],
        }
        
        # Language-specific features
        if language == 'python':
            features.update({
                'readline_integration': True,
                'tab_completion': True,
                'history_persistence': True,
                'async_support': False
            })
        elif language in ('nodejs', 'typescript'):
            features.update({
                'readline_integration': True,
                'tab_completion': True,
                'history_persistence': True,
                'async_support': True
            })
        elif language == 'rust':
            features.update({
                'readline_integration': False,  # Basic implementation
                'tab_completion': False,       # Basic implementation
                'history_persistence': False,  # Basic implementation
                'async_support': False
            })
        
        return features
    
    def validate_command_structure(self, commands: Dict[str, Any]) -> List[str]:
        """
        Validate command structure for REPL generation.
        
        Args:
            commands: Command structure to validate
            
        Returns:
            List of validation warnings/errors
        """
        warnings = []
        
        for cmd_name, cmd_data in commands.items():
            if not isinstance(cmd_data, dict):
                warnings.append(f"Command '{cmd_name}' should be a dictionary")
                continue
            
            # Check for description
            if not cmd_data.get('description') and not cmd_data.get('desc'):
                warnings.append(f"Command '{cmd_name}' missing description")
            
            # Check for hook name
            hook_name = cmd_data.get('hook_name')
            if not hook_name:
                expected_hook = f"on_{cmd_name.replace('-', '_')}"
                warnings.append(f"Command '{cmd_name}' missing hook_name, expected '{expected_hook}'")
            
            # Validate arguments
            for arg in cmd_data.get('arguments', []):
                if not isinstance(arg, dict):
                    warnings.append(f"Argument in command '{cmd_name}' should be a dictionary")
                    continue
                
                if not arg.get('name'):
                    warnings.append(f"Argument in command '{cmd_name}' missing name")
            
            # Validate options
            for opt in cmd_data.get('options', []):
                if not isinstance(opt, dict):
                    warnings.append(f"Option in command '{cmd_name}' should be a dictionary")
                    continue
                
                if not opt.get('name'):
                    warnings.append(f"Option in command '{cmd_name}' missing name")
        
        return warnings
    
    def get_repl_statistics(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get statistics about REPL capabilities.
        
        Args:
            config: Configuration dictionary
            
        Returns:
            Dictionary with REPL statistics
        """
        repl_config = self._process_configuration(config, 'python')  # Language doesn't matter for stats
        
        stats = {
            'project_name': repl_config.project_name,
            'supported_languages': len(self._adapters),
            'total_commands': len(repl_config.cli_commands),
            'repl_mode': repl_config.repl_mode.value,
            'features_enabled': {
                'history': repl_config.enable_history,
                'completion': repl_config.enable_completion,
                'multiline': repl_config.enable_multiline,
                'system_commands': repl_config.enable_system_commands
            },
            'max_history_entries': repl_config.max_history_entries
        }
        
        # Count arguments and options across all commands
        total_arguments = 0
        total_options = 0
        for cmd_data in repl_config.cli_commands.values():
            if isinstance(cmd_data, dict):
                total_arguments += len(cmd_data.get('arguments', []))
                total_options += len(cmd_data.get('options', []))
        
        stats['total_arguments'] = total_arguments
        stats['total_options'] = total_options
        
        # Check for advanced features
        has_subcommands = any(
            'subcommands' in cmd_data 
            for cmd_data in repl_config.cli_commands.values()
            if isinstance(cmd_data, dict)
        )
        stats['has_subcommands'] = has_subcommands
        
        return stats
    
    def generate_completion_helpers(self, config: Dict[str, Any]) -> Dict[str, str]:
        """
        Generate completion helper functions for different shells.
        
        Args:
            config: Configuration dictionary
            
        Returns:
            Dictionary mapping shell names to completion helper code
        """
        project = config.get('project', {})
        cli_name = project.get('name', 'CLI').lower().replace(' ', '-')
        commands = config.get('cli', {}).get('commands', {})
        
        helpers = {}
        
        # Bash completion helper
        bash_lines = [
            f"# Bash completion helper for {cli_name} REPL",
            f"_{cli_name}_repl_completion() {{",
            "    local cur prev words cword",
            "    _init_completion || return",
            "",
            f"    local commands='{' '.join(commands.keys())}'",
            "    COMPREPLY=($(compgen -W \"$commands\" -- \"$cur\"))",
            "}",
            "",
            f"complete -F _{cli_name}_repl_completion {cli_name}"
        ]
        helpers['bash'] = '\\n'.join(bash_lines)
        
        # Zsh completion helper
        zsh_lines = [
            f"#compdef {cli_name}",
            f"# Zsh completion helper for {cli_name} REPL",
            "",
            f"_{cli_name}_repl() {{",
            "    local context curcontext=\"$curcontext\" state line",
            "    typeset -A opt_args",
            "",
            "    _arguments -C \\",
            "        '1: :_command_names' \\",
            "        '*::arg:->args'",
            "",
            "    case $state in",
            "        args)",
            "            # Add command-specific completion here",
            "            ;;",
            "    esac",
            "}",
            "",
            f"_{cli_name}_repl \"$@\""
        ]
        helpers['zsh'] = '\\n'.join(zsh_lines)
        
        return helpers
    
    def get_template_variables(self, config: Dict[str, Any], language: str) -> Dict[str, Any]:
        """
        Get template variables for REPL generation.
        
        Args:
            config: Configuration dictionary
            language: Target language
            
        Returns:
            Dictionary of template variables
        """
        repl_config = self._process_configuration(config, language)
        project = config.get('project', {})
        cli_name = project.get('name', 'CLI').lower().replace(' ', '-')
        
        return {
            'project_name': repl_config.project_name,
            'cli_name': cli_name,
            'class_name': repl_config.project_name.replace('-', '').replace(' ', '').title(),
            'language': language,
            'commands': repl_config.cli_commands,
            'repl_mode': repl_config.repl_mode.value,
            'enable_history': repl_config.enable_history,
            'enable_completion': repl_config.enable_completion,
            'enable_multiline': repl_config.enable_multiline,
            'enable_system_commands': repl_config.enable_system_commands,
            'max_history_entries': repl_config.max_history_entries,
            'prompt': repl_config.prompt_template or f"{cli_name}> ",
            'continuation_prompt': repl_config.continuation_prompt_template or f"{cli_name}... ",
            'welcome_message': repl_config.welcome_message or f"Welcome to {repl_config.project_name} Enhanced REPL mode.",
            'features': repl_config.features
        }
    
    def estimate_performance_impact(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Estimate the performance impact of REPL features.
        
        Args:
            config: Configuration dictionary
            
        Returns:
            Dictionary with performance estimates
        """
        repl_config = self._process_configuration(config, 'python')
        
        # Base overhead estimates (in milliseconds)
        base_startup = 50
        history_overhead = 10 if repl_config.enable_history else 0
        completion_overhead = 20 if repl_config.enable_completion else 0
        multiline_overhead = 5 if repl_config.enable_multiline else 0
        
        total_startup = base_startup + history_overhead + completion_overhead + multiline_overhead
        
        # Memory estimates (in MB)
        base_memory = 2.0
        history_memory = (repl_config.max_history_entries * 0.001) if repl_config.enable_history else 0
        completion_memory = 0.5 if repl_config.enable_completion else 0
        
        total_memory = base_memory + history_memory + completion_memory
        
        return {
            'estimated_startup_time_ms': total_startup,
            'estimated_memory_usage_mb': total_memory,
            'breakdown': {
                'base_overhead_ms': base_startup,
                'history_overhead_ms': history_overhead,
                'completion_overhead_ms': completion_overhead,
                'multiline_overhead_ms': multiline_overhead,
                'base_memory_mb': base_memory,
                'history_memory_mb': history_memory,
                'completion_memory_mb': completion_memory
            },
            'optimization_suggestions': self._get_optimization_suggestions(repl_config)
        }
    
    def _get_optimization_suggestions(self, config: REPLConfig) -> List[str]:
        """Get optimization suggestions based on configuration."""
        suggestions = []
        
        if config.max_history_entries > 10000:
            suggestions.append("Consider reducing max_history_entries for better memory usage")
        
        if not config.enable_completion and config.repl_mode == REPLMode.FULL_FEATURED:
            suggestions.append("Enable completion for better user experience in full-featured mode")
        
        if config.enable_system_commands:
            suggestions.append("System commands can be a security risk - consider disabling in production")
        
        if config.repl_mode == REPLMode.BASIC and (config.enable_history or config.enable_completion):
            suggestions.append("Advanced features enabled in basic mode - consider upgrading to enhanced mode")
        
        return suggestions