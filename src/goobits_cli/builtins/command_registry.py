"""
Command Registry
===============

Command registration and option management extracted from builtin_manager.j2.
Provides structured data classes for builtin command options and configuration.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any, List
from enum import Enum


class PackageManager(Enum):
    """Package manager types."""
    PIP = "pip"
    PIPX = "pipx"
    NPM = "npm"
    YARN = "yarn"
    CARGO = "cargo"


@dataclass
class UpgradeOptions:
    """Options for upgrade command."""
    check_only: bool = False
    pre_release: bool = False
    version: Optional[str] = None
    dry_run: bool = False
    package_manager: Optional[PackageManager] = None
    force: bool = False
    user_install: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for template use."""
        return {
            'checkOnly': self.check_only,
            'pre': self.pre_release,
            'version': self.version,
            'dryRun': self.dry_run,
            'force': self.force,
            'userInstall': self.user_install
        }


@dataclass  
class CompletionOptions:
    """Options for completion command."""
    shell: Optional[str] = None
    install: bool = False
    generate: bool = False
    user_install: bool = True
    completion_dir: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for template use."""
        return {
            'shell': self.shell,
            'install': self.install,
            'generate': self.generate,
            'userInstall': self.user_install,
            'completionDir': self.completion_dir
        }


@dataclass
class ConfigOptions:
    """Options for config command.""" 
    get_key: Optional[str] = None
    set_key: Optional[str] = None
    set_value: Optional[str] = None
    reset: bool = False
    path: bool = False
    global_config: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for template use."""
        return {
            'getKey': self.get_key,
            'setKey': self.set_key,
            'setValue': self.set_value,
            'reset': self.reset,
            'path': self.path,
            'global': self.global_config
        }


@dataclass
class DoctorOptions:
    """Options for doctor command."""
    verbose: bool = False
    fix: bool = False
    check_dependencies: bool = True
    check_permissions: bool = True
    check_environment: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for template use."""
        return {
            'verbose': self.verbose,
            'fix': self.fix,
            'checkDependencies': self.check_dependencies,
            'checkPermissions': self.check_permissions,
            'checkEnvironment': self.check_environment
        }


class CommandRegistry:
    """
    Registry for builtin commands and their configurations.
    
    Manages the registration and retrieval of builtin commands,
    their options, and validation rules.
    """
    
    def __init__(self):
        """Initialize command registry."""
        self._commands = {}
        self._option_schemas = {}
        self._register_default_commands()
    
    def _register_default_commands(self) -> None:
        """Register default builtin commands."""
        # Upgrade command
        self.register_command(
            name="upgrade",
            description="Upgrade to the latest version",
            options_class=UpgradeOptions,
            required_features=[]
        )
        
        # Version command
        self.register_command(
            name="version",
            description="Show version information",
            options_class=None,
            required_features=[]
        )
        
        # Completion command
        self.register_command(
            name="completion",
            description="Manage shell completion",
            options_class=CompletionOptions,
            required_features=["completion"]
        )
        
        # Config command
        self.register_command(
            name="config", 
            description="Manage configuration",
            options_class=ConfigOptions,
            required_features=[]
        )
        
        # Doctor command
        self.register_command(
            name="doctor",
            description="Diagnose system health",
            options_class=DoctorOptions,
            required_features=["doctor"]
        )
    
    def register_command(self, name: str, description: str, options_class=None, required_features: List[str] = None) -> None:
        """Register a builtin command."""
        self._commands[name] = {
            'name': name,
            'description': description,
            'options_class': options_class,
            'required_features': required_features or []
        }
        
        if options_class:
            self._option_schemas[name] = options_class
    
    def get_command(self, name: str) -> Optional[Dict[str, Any]]:
        """Get command configuration by name."""
        return self._commands.get(name)
    
    def get_all_commands(self) -> Dict[str, Dict[str, Any]]:
        """Get all registered commands."""
        return self._commands.copy()
    
    def get_options_class(self, command_name: str) -> Optional[type]:
        """Get options class for a command."""
        return self._option_schemas.get(command_name)
    
    def is_command_available(self, command_name: str, enabled_features: List[str]) -> bool:
        """Check if command is available given enabled features."""
        command = self.get_command(command_name)
        if not command:
            return False
        
        required_features = command.get('required_features', [])
        return all(feature in enabled_features for feature in required_features)
    
    def get_available_commands(self, enabled_features: List[str]) -> List[str]:
        """Get list of available commands given enabled features."""
        available = []
        for name, command in self._commands.items():
            if self.is_command_available(name, enabled_features):
                available.append(name)
        return available
    
    def validate_command_options(self, command_name: str, options: Dict[str, Any]) -> bool:
        """Validate command options against schema."""
        options_class = self.get_options_class(command_name)
        if not options_class:
            return True  # No validation needed
        
        try:
            # Try to instantiate the options class with provided options
            options_class(**options)
            return True
        except (TypeError, ValueError):
            return False
    
    def create_default_options(self, command_name: str) -> Optional[Any]:
        """Create default options instance for a command."""
        options_class = self.get_options_class(command_name)
        if options_class:
            return options_class()
        return None
    
    def get_command_help(self, command_name: str) -> str:
        """Get help text for a command."""
        command = self.get_command(command_name)
        if not command:
            return f"Unknown command: {command_name}"
        
        help_text = f"{command['description']}\n"
        
        options_class = self.get_options_class(command_name)
        if options_class:
            # Get field information from dataclass
            import inspect
            signature = inspect.signature(options_class)
            
            help_text += "\nOptions:\n"
            for param_name, param in signature.parameters.items():
                default_value = param.default if param.default != inspect.Parameter.empty else None
                param_type = param.annotation if param.annotation != inspect.Parameter.empty else 'Any'
                
                help_text += f"  --{param_name.replace('_', '-')}"
                if param_type == bool:
                    help_text += " (flag)"
                else:
                    help_text += f" <{param_type.__name__ if hasattr(param_type, '__name__') else str(param_type)}>"
                
                if default_value is not None:
                    help_text += f" (default: {default_value})"
                help_text += "\n"
        
        return help_text.strip()
    
    def get_package_managers_for_language(self, language: str) -> List[PackageManager]:
        """Get available package managers for a language."""
        managers_by_language = {
            'python': [PackageManager.PIP, PackageManager.PIPX],
            'nodejs': [PackageManager.NPM, PackageManager.YARN],
            'typescript': [PackageManager.NPM, PackageManager.YARN],
            'rust': [PackageManager.CARGO]
        }
        return managers_by_language.get(language, [])
    
    def detect_package_manager(self, language: str) -> Optional[PackageManager]:
        """Detect the most appropriate package manager for a language."""
        # This would contain logic to detect installed package managers
        # For now, return defaults
        defaults = {
            'python': PackageManager.PIPX,
            'nodejs': PackageManager.NPM,
            'typescript': PackageManager.NPM,
            'rust': PackageManager.CARGO
        }
        return defaults.get(language)