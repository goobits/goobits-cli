"""
Builtin Framework
================

Core framework extracted from builtin_manager.j2 template.
Orchestrates built-in command generation for all languages with consistent functionality.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
from enum import Enum


class BuiltinCommandType(Enum):
    """Types of built-in commands."""
    UPGRADE = "upgrade"
    VERSION = "version" 
    COMPLETION = "completion"
    CONFIG = "config"
    DOCTOR = "doctor"


class ShellType(Enum):
    """Supported shell types for completion."""
    BASH = "bash"
    ZSH = "zsh"
    FISH = "fish"
    POWERSHELL = "powershell"


@dataclass
class BuiltinCommand:
    """Built-in command configuration."""
    name: str
    type: BuiltinCommandType
    description: str
    enabled: bool = True
    options: Dict[str, Any] = field(default_factory=dict)


@dataclass
class BuiltinConfig:
    """Built-in framework configuration schema."""
    project_name: str
    display_name: str
    command_name: str
    package_name: str
    pypi_name: Optional[str] = None
    npm_name: Optional[str] = None
    cargo_name: Optional[str] = None
    version_module: str = "__version__"
    config_dir: Optional[str] = None
    completion_enabled: bool = True
    doctor_enabled: bool = True
    upgrade_enabled: bool = True
    commands: List[BuiltinCommand] = field(default_factory=list)


class BuiltinFramework:
    """
    Built-in framework extracted from builtin_manager.j2.
    
    Generates built-in command implementations for all supported languages
    with consistent functionality for upgrade, version, completion, config, and doctor commands.
    """
    
    def __init__(self):
        """Initialize the builtin framework."""
        from .language_adapters import (
            PythonBuiltinAdapter,
            NodeJSBuiltinAdapter,
            TypeScriptBuiltinAdapter,
            RustBuiltinAdapter
        )
        
        self._adapters = {
            'python': PythonBuiltinAdapter(),
            'nodejs': NodeJSBuiltinAdapter(), 
            'typescript': TypeScriptBuiltinAdapter(),
            'rust': RustBuiltinAdapter()
        }
    
    def generate_builtin_code(self, language: str, config: Dict[str, Any]) -> str:
        """
        Generate built-in command code for specified language.
        
        Args:
            language: Target language ('python', 'nodejs', 'typescript', 'rust')
            config: Configuration including project metadata and installation settings
            
        Returns:
            Generated built-in commands code as string
            
        Raises:
            ValueError: If language is not supported
        """
        if language not in self._adapters:
            supported = ', '.join(self._adapters.keys())
            raise ValueError(f"Unsupported language: {language}. Supported languages: {supported}")
        
        # Process configuration
        builtin_config = self._process_configuration(config)
        
        # Validate configuration
        self._validate_configuration(builtin_config)
        
        # Generate code using appropriate adapter
        adapter = self._adapters[language]
        return adapter.generate_code(builtin_config)
    
    def _process_configuration(self, config: Dict[str, Any]) -> BuiltinConfig:
        """Process raw configuration into structured builtin schema."""
        project = config.get('project', {})
        installation = config.get('installation', {})
        features = config.get('features', {})
        
        # Extract project information
        project_name = project.get('name', 'CLI')
        display_name = project.get('display_name', project_name)
        command_name = project.get('command_name', project_name.lower().replace(' ', '-'))
        
        # Extract package names
        package_name = installation.get('pypi_name', project_name.lower().replace('-', '_'))
        pypi_name = installation.get('pypi_name')
        npm_name = installation.get('npm_name', project_name.lower().replace(' ', '-'))
        cargo_name = installation.get('cargo_name', project_name.lower().replace(' ', '-'))
        
        # Feature flags
        completion_enabled = features.get('completion', {}).get('enabled', True)
        doctor_enabled = features.get('doctor', {}).get('enabled', True)
        upgrade_enabled = features.get('upgrade', {}).get('enabled', True)
        
        # Build default commands
        commands = []
        
        if upgrade_enabled:
            commands.append(BuiltinCommand(
                name="upgrade",
                type=BuiltinCommandType.UPGRADE,
                description="Upgrade to the latest version",
                options={
                    'check_only': False,
                    'pre_release': False,
                    'version': None,
                    'dry_run': False
                }
            ))
        
        commands.append(BuiltinCommand(
            name="version",
            type=BuiltinCommandType.VERSION,
            description="Show version information"
        ))
        
        if completion_enabled:
            commands.append(BuiltinCommand(
                name="completion",
                type=BuiltinCommandType.COMPLETION,
                description="Manage shell completion",
                options={
                    'shell': None,
                    'install': False,
                    'generate': False
                }
            ))
        
        commands.append(BuiltinCommand(
            name="config",
            type=BuiltinCommandType.CONFIG,
            description="Manage configuration",
            options={
                'get_key': None,
                'set_key': None,
                'set_value': None,
                'reset': False,
                'path': False
            }
        ))
        
        if doctor_enabled:
            commands.append(BuiltinCommand(
                name="doctor",
                type=BuiltinCommandType.DOCTOR,
                description="Diagnose system health"
            ))
        
        return BuiltinConfig(
            project_name=project_name,
            display_name=display_name,
            command_name=command_name,
            package_name=package_name,
            pypi_name=pypi_name,
            npm_name=npm_name,
            cargo_name=cargo_name,
            version_module=installation.get('version_module', '__version__'),
            config_dir=features.get('config', {}).get('directory'),
            completion_enabled=completion_enabled,
            doctor_enabled=doctor_enabled,
            upgrade_enabled=upgrade_enabled,
            commands=commands
        )
    
    def _validate_configuration(self, config: BuiltinConfig) -> None:
        """Validate the processed builtin configuration."""
        if not config.project_name:
            raise ValueError("Project name is required for builtin generation")
        
        if not config.command_name:
            raise ValueError("Command name is required for builtin generation")
        
        if not config.package_name:
            raise ValueError("Package name is required for builtin generation")
        
        # Validate commands
        for command in config.commands:
            if not command.name:
                raise ValueError("Builtin command name is required")
            
            if not command.description:
                raise ValueError(f"Builtin command '{command.name}' requires a description")
    
    def get_available_commands(self, config: BuiltinConfig) -> List[str]:
        """Get list of available builtin command names."""
        return [cmd.name for cmd in config.commands if cmd.enabled]
    
    def get_command_by_type(self, config: BuiltinConfig, command_type: BuiltinCommandType) -> Optional[BuiltinCommand]:
        """Get builtin command by type."""
        for command in config.commands:
            if command.type == command_type and command.enabled:
                return command
        return None
    
    def supports_feature(self, config: BuiltinConfig, feature: str) -> bool:
        """Check if a feature is supported/enabled."""
        feature_map = {
            'completion': config.completion_enabled,
            'doctor': config.doctor_enabled,
            'upgrade': config.upgrade_enabled
        }
        return feature_map.get(feature, False)
    
    def get_package_name_for_language(self, config: BuiltinConfig, language: str) -> str:
        """Get appropriate package name for the target language."""
        if language == 'python':
            return config.pypi_name or config.package_name
        elif language in ('nodejs', 'typescript'):
            return config.npm_name or config.command_name
        elif language == 'rust':
            return config.cargo_name or config.command_name
        else:
            return config.package_name
    
    def get_supported_shells(self) -> List[str]:
        """Get list of supported shells for completion."""
        return [shell.value for shell in ShellType]