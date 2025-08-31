"""
Completion Framework
====================

Core framework extracted from completion_manager.j2 and completion_engine.j2 templates.
Orchestrates completion system generation for all languages with consistent functionality.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List
from enum import Enum
from .completion_manager import ShellType
from .language_adapters import (
    PythonCompletionAdapter,
    NodeJSCompletionAdapter,
    TypeScriptCompletionAdapter,
    RustCompletionAdapter
)


class CompletionMode(Enum):
    """Completion generation modes."""
    MANAGER_ONLY = "manager"
    ENGINE_ONLY = "engine"
    BOTH = "both"


@dataclass
class CompletionConfig:
    """Completion framework configuration schema."""
    project_name: str
    language: str
    commands: Dict[str, Any] = field(default_factory=dict)
    supported_shells: List[str] = field(default_factory=lambda: ['bash', 'zsh', 'fish'])
    completion_mode: CompletionMode = CompletionMode.BOTH
    install_instructions: bool = True
    advanced_completion: bool = True
    file_completion: bool = True
    context_aware: bool = True
    custom_completions: Dict[str, Any] = field(default_factory=dict)


class CompletionFramework:
    """
    Completion framework extracted from completion templates.
    
    Generates shell completion systems for all supported languages
    with advanced features like context awareness and multi-shell support.
    """
    
    def __init__(self):
        """Initialize the completion framework."""
        self._adapters = {
            'python': PythonCompletionAdapter(),
            'nodejs': NodeJSCompletionAdapter(),
            'typescript': TypeScriptCompletionAdapter(),
            'rust': RustCompletionAdapter()
        }
    
    def generate_completion_code(self, language: str, config: Dict[str, Any]) -> str:
        """
        Generate completion system code for specified language.
        
        Args:
            language: Target language ('python', 'nodejs', 'typescript', 'rust')
            config: Configuration including project metadata and CLI commands
            
        Returns:
            Generated completion system code as string
            
        Raises:
            ValueError: If language is not supported
        """
        if language not in self._adapters:
            supported = ', '.join(self._adapters.keys())
            raise ValueError(f"Unsupported language: {language}. Supported languages: {supported}")
        
        # Process configuration
        completion_config = self._process_configuration(config, language)
        
        # Validate configuration
        self._validate_configuration(completion_config)
        
        # Generate code using appropriate adapter
        adapter = self._adapters[language]
        
        if completion_config.completion_mode == CompletionMode.MANAGER_ONLY:
            return adapter.generate_manager_code(config)
        elif completion_config.completion_mode == CompletionMode.ENGINE_ONLY:
            return adapter.generate_engine_code(config)
        else:  # CompletionMode.BOTH
            manager_code = adapter.generate_manager_code(config)
            engine_code = adapter.generate_engine_code(config)
            
            # Combine both codes
            return self._combine_completion_codes(manager_code, engine_code, language)
    
    def _process_configuration(self, config: Dict[str, Any], language: str) -> CompletionConfig:
        """Process raw configuration into structured completion schema."""
        project = config.get('project', {})
        cli_config = config.get('cli', {})
        completion_settings = config.get('completion', {})
        
        # Extract project information
        project_name = project.get('name', 'CLI')
        
        # Extract CLI commands
        commands = cli_config.get('commands', {})
        
        # Process completion settings
        supported_shells = completion_settings.get('shells', ['bash', 'zsh', 'fish'])
        completion_mode = completion_settings.get('mode', 'both')
        
        # Convert mode string to enum
        mode_map = {
            'manager': CompletionMode.MANAGER_ONLY,
            'engine': CompletionMode.ENGINE_ONLY,
            'both': CompletionMode.BOTH
        }
        completion_mode = mode_map.get(completion_mode, CompletionMode.BOTH)
        
        return CompletionConfig(
            project_name=project_name,
            language=language,
            commands=commands,
            supported_shells=supported_shells,
            completion_mode=completion_mode,
            install_instructions=completion_settings.get('install_instructions', True),
            advanced_completion=completion_settings.get('advanced', True),
            file_completion=completion_settings.get('file_completion', True),
            context_aware=completion_settings.get('context_aware', True),
            custom_completions=completion_settings.get('custom', {})
        )
    
    def _validate_configuration(self, config: CompletionConfig) -> None:
        """Validate the processed completion configuration."""
        if not config.project_name:
            raise ValueError("Project name is required for completion generation")
        
        if not config.language:
            raise ValueError("Language is required for completion generation")
        
        if config.language not in self._adapters:
            supported = ', '.join(self._adapters.keys())
            raise ValueError(f"Unsupported language: {config.language}. Supported: {supported}")
        
        # Validate shell support
        valid_shells = ['bash', 'zsh', 'fish', 'powershell']
        for shell in config.supported_shells:
            if shell not in valid_shells:
                raise ValueError(f"Unsupported shell: {shell}. Supported: {', '.join(valid_shells)}")
    
    def _combine_completion_codes(self, manager_code: str, engine_code: str, language: str) -> str:
        """Combine manager and engine codes into a single module."""
        if language == 'python':
            return self._combine_python_codes(manager_code, engine_code)
        elif language in ('nodejs', 'typescript'):
            return self._combine_js_codes(manager_code, engine_code, language)
        elif language == 'rust':
            return self._combine_rust_codes(manager_code, engine_code)
        else:
            return manager_code + '\n\n' + engine_code
    
    def _combine_python_codes(self, manager_code: str, engine_code: str) -> str:
        """Combine Python completion codes."""
        lines = [
            '"""',
            'Complete shell completion system',
            'Generated by Goobits CLI Framework',
            '"""',
            '',
            '# Completion Manager',
            manager_code.split('"""', 2)[-1],  # Remove the docstring
            '',
            '# Completion Engine', 
            engine_code.split('"""', 2)[-1],   # Remove the docstring
            '',
            '# Combined interface',
            'def setup_completion(cli_name: str = None, commands: Dict[str, Any] = None):',
            '    """Setup both completion manager and engine."""',
            '    manager = CompletionManager(cli_name) if cli_name else CompletionManager()',
            '    engine = CompletionEngine(commands) if commands else CompletionEngine({})',
            '    return manager, engine'
        ]
        
        return '\n'.join(lines)
    
    def _combine_js_codes(self, manager_code: str, engine_code: str, language: str) -> str:
        """Combine JavaScript/TypeScript completion codes."""
        # Extract imports and class definitions
        manager_lines = manager_code.split('\n')
        engine_lines = engine_code.split('\n')
        
        # Combine imports
        imports = []
        manager_imports = [line for line in manager_lines if line.startswith('import')]
        engine_imports = [line for line in engine_lines if line.startswith('import')]
        
        # Merge and deduplicate imports
        all_imports = manager_imports + engine_imports
        seen_imports = set()
        for imp in all_imports:
            if imp not in seen_imports:
                imports.append(imp)
                seen_imports.add(imp)
        
        # Get class definitions
        manager_content = '\n'.join([line for line in manager_lines if not line.startswith('import') and not line.startswith('/**')])
        engine_content = '\n'.join([line for line in engine_lines if not line.startswith('import') and not line.startswith('/**')])
        
        lines = [
            '/**',
            ' * Complete shell completion system',
            ' * Generated by Goobits CLI Framework',
            ' */',
            '',
            *imports,
            '',
            '// Completion Manager',
            manager_content,
            '',
            '// Completion Engine',
            engine_content
        ]
        
        return '\n'.join(lines)
    
    def _combine_rust_codes(self, manager_code: str, engine_code: str) -> str:
        """Combine Rust completion codes."""
        lines = [
            '//! Complete shell completion system',
            '//! Generated by Goobits CLI Framework',
            '',
            '// Completion Manager',
            manager_code.split('//!', 2)[-1],  # Remove the module docstring
            '',
            '// Completion Engine',
            engine_code.split('//!', 2)[-1],   # Remove the module docstring
        ]
        
        return '\n'.join(lines)
    
    def generate_shell_scripts(self, config: Dict[str, Any]) -> Dict[str, str]:
        """
        Generate shell completion scripts for all supported shells.
        
        Args:
            config: Configuration dictionary
            
        Returns:
            Dictionary mapping shell names to completion scripts
        """
        completion_config = self._process_configuration(config, 'python')  # Language doesn't matter for shell scripts
        
        from .completion_manager import CompletionManager
        cli_name = completion_config.project_name.lower().replace(' ', '-')
        manager = CompletionManager(cli_name)
        
        scripts = manager.generate_completion_scripts(
            completion_config.commands,
            completion_config.language
        )
        
        return {shell.value: script.content for shell, script in scripts.items()}
    
    def get_installation_instructions(self, config: Dict[str, Any]) -> Dict[str, List[str]]:
        """
        Get installation instructions for all supported shells.
        
        Args:
            config: Configuration dictionary
            
        Returns:
            Dictionary mapping shell names to installation instruction lists
        """
        completion_config = self._process_configuration(config, 'python')
        
        from .completion_manager import CompletionManager
        cli_name = completion_config.project_name.lower().replace(' ', '-')
        manager = CompletionManager(cli_name)
        
        scripts = manager.generate_completion_scripts(
            completion_config.commands,
            completion_config.language
        )
        
        return {shell.value: script.get_install_instructions() for shell, script in scripts.items()}
    
    def get_supported_languages(self) -> List[str]:
        """Get list of supported languages."""
        return list(self._adapters.keys())
    
    def get_supported_shells(self) -> List[str]:
        """Get list of supported shells."""
        return [shell.value for shell in ShellType]
    
    def validate_command_structure(self, commands: Dict[str, Any]) -> List[str]:
        """
        Validate command structure for completion generation.
        
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
            
            # Validate options
            for opt in cmd_data.get('options', []):
                if not isinstance(opt, dict):
                    warnings.append(f"Option in command '{cmd_name}' should be a dictionary")
                    continue
                
                if not opt.get('name'):
                    warnings.append(f"Option in command '{cmd_name}' missing name")
                
                if not opt.get('description') and not opt.get('desc'):
                    warnings.append(f"Option '{opt.get('name', 'unnamed')}' in command '{cmd_name}' missing description")
        
        return warnings
    
    def get_completion_stats(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get statistics about completion capabilities.
        
        Args:
            config: Configuration dictionary
            
        Returns:
            Dictionary with completion statistics
        """
        completion_config = self._process_configuration(config, 'python')
        
        stats = {
            'project_name': completion_config.project_name,
            'supported_languages': len(self._adapters),
            'supported_shells': len(self.get_supported_shells()),
            'total_commands': len(completion_config.commands),
            'completion_mode': completion_config.completion_mode.value,
            'advanced_features': {
                'file_completion': completion_config.file_completion,
                'context_aware': completion_config.context_aware,
                'install_instructions': completion_config.install_instructions
            }
        }
        
        # Count options across all commands
        total_options = 0
        for cmd_data in completion_config.commands.values():
            if isinstance(cmd_data, dict):
                total_options += len(cmd_data.get('options', []))
        
        stats['total_options'] = total_options
        
        # Check for subcommands
        has_subcommands = any(
            'subcommands' in cmd_data 
            for cmd_data in completion_config.commands.values()
            if isinstance(cmd_data, dict)
        )
        stats['has_subcommands'] = has_subcommands
        
        return stats