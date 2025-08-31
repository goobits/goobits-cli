"""
Setup Framework
===============

Main orchestration framework for setup and installation management.
Coordinates between setup managers, system detection, and language adapters.
"""

import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

from .setup_manager import SetupManager, InstallationConfig, InstallationMethod, InstallationResult
from .system_detection import SystemDetector
from .language_adapters import (
    PythonSetupAdapter, NodeJSSetupAdapter, 
    TypeScriptSetupAdapter, RustSetupAdapter
)
from .installation_runners import (
    PythonInstallationRunner,
    NodeJSInstallationRunner, TypeScriptInstallationRunner,
    RustInstallationRunner
)

logger = logging.getLogger(__name__)


@dataclass
class SetupConfig:
    """Configuration for setup framework."""
    language: str = "python"
    package_name: str = "app"
    command_name: str = "app"
    development_mode: bool = False
    user_install: bool = True
    global_install: bool = False
    system_packages: List[str] = None
    extras: List[str] = None
    python_version: str = "3.8"
    node_version: str = "16"
    rust_version: str = "1.70"
    
    def __post_init__(self):
        """Initialize default values."""
        if self.system_packages is None:
            self.system_packages = []
        if self.extras is None:
            self.extras = []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'language': self.language,
            'package_name': self.package_name,
            'command_name': self.command_name,
            'development_mode': self.development_mode,
            'user_install': self.user_install,
            'global_install': self.global_install,
            'system_packages': self.system_packages,
            'extras': self.extras,
            'python_version': self.python_version,
            'node_version': self.node_version,
            'rust_version': self.rust_version
        }


class SetupFramework:
    """
    Main setup framework orchestrator.
    
    Coordinates setup management, system detection, and code generation
    for creating consistent installation experiences across all supported languages.
    """
    
    def __init__(self, config: Optional[SetupConfig] = None):
        """
        Initialize setup framework.
        
        Args:
            config: Framework configuration
        """
        self.config = config or SetupConfig()
        
        # Initialize core components
        self.detector = SystemDetector()
        self.setup_manager = SetupManager(self.detector)
        
        # Initialize language adapters
        self.language_adapters = {
            'python': PythonSetupAdapter(),
            'nodejs': NodeJSSetupAdapter(),
            'typescript': TypeScriptSetupAdapter(),
            'rust': RustSetupAdapter()
        }
        
        # Initialize installation runners
        self.installation_runners = {
            'python': PythonInstallationRunner(self.detector),
            'nodejs': NodeJSInstallationRunner(self.detector),
            'typescript': TypeScriptInstallationRunner(self.detector),
            'rust': RustInstallationRunner(self.detector)
        }
        
        logger.info(f"Setup framework initialized for {self.config.language}")
    
    def validate_environment(self, language: Optional[str] = None) -> Dict[str, Any]:
        """
        Validate environment for setup operations.
        
        Args:
            language: Target language (defaults to config.language)
            
        Returns:
            Validation results
        """
        target_language = language or self.config.language
        
        # Use setup manager validation
        validation = self.setup_manager.validate_environment(target_language)
        
        # Add runner-specific validation
        if target_language in self.installation_runners:
            runner = self.installation_runners[target_language]
            validation['runner_valid'] = runner.validate_environment()
        
        return validation
    
    def create_installation_config(
        self,
        method: Optional[InstallationMethod] = None,
        **overrides
    ) -> InstallationConfig:
        """
        Create installation configuration with framework defaults.
        
        Args:
            method: Installation method (auto-determined if None)
            **overrides: Configuration overrides
            
        Returns:
            Installation configuration
        """
        # Determine method if not specified
        if method is None:
            method = self.setup_manager.determine_installation_method(
                self.config.language,
                self.config.to_dict()
            )
        
        # Create config with defaults
        config_dict = self.config.to_dict()
        config_dict.update(overrides)
        
        return InstallationConfig(
            method=method,
            package_name=config_dict.get('package_name', self.config.package_name),
            command_name=config_dict.get('command_name', self.config.command_name),
            development_mode=config_dict.get('development_mode', self.config.development_mode),
            user_install=config_dict.get('user_install', self.config.user_install),
            global_install=config_dict.get('global_install', self.config.global_install),
            extras=config_dict.get('extras', self.config.extras),
            system_packages=config_dict.get('system_packages', self.config.system_packages)
        )
    
    def install_package(
        self,
        method: Optional[InstallationMethod] = None,
        **overrides
    ) -> InstallationResult:
        """
        Install package using framework.
        
        Args:
            method: Installation method (auto-determined if None)
            **overrides: Configuration overrides
            
        Returns:
            Installation result
        """
        config = self.create_installation_config(method, **overrides)
        
        # Use appropriate runner
        runner = self.installation_runners.get(self.config.language)
        if runner:
            return runner.install(config)
        else:
            # Fallback to setup manager
            return self.setup_manager.install_package(config)
    
    def upgrade_package(
        self,
        method: Optional[InstallationMethod] = None,
        **overrides
    ) -> InstallationResult:
        """
        Upgrade package using framework.
        
        Args:
            method: Installation method (auto-determined if None)
            **overrides: Configuration overrides
            
        Returns:
            Upgrade result
        """
        config = self.create_installation_config(method, **overrides)
        
        runner = self.installation_runners.get(self.config.language)
        if runner:
            return runner.upgrade(config)
        else:
            return self.setup_manager.upgrade_package(config)
    
    def uninstall_package(
        self,
        method: Optional[InstallationMethod] = None,
        **overrides
    ) -> InstallationResult:
        """
        Uninstall package using framework.
        
        Args:
            method: Installation method (auto-determined if None)
            **overrides: Configuration overrides
            
        Returns:
            Uninstall result
        """
        config = self.create_installation_config(method, **overrides)
        
        runner = self.installation_runners.get(self.config.language)
        if runner:
            return runner.uninstall(config)
        else:
            return self.setup_manager.uninstall_package(config)
    
    def generate_setup_script(
        self,
        language: Optional[str] = None,
        template_vars: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate setup script for specified language.
        
        Args:
            language: Target language (defaults to config.language)
            template_vars: Additional template variables
            
        Returns:
            Generated setup script
        """
        target_language = language or self.config.language
        
        if target_language not in self.language_adapters:
            raise ValueError(f"Unsupported language: {target_language}")
        
        adapter = self.language_adapters[target_language]
        config_dict = self.config.to_dict()
        
        if template_vars:
            config_dict.update(template_vars)
        
        # Generate script sections
        sections = []
        
        # Header
        sections.append(adapter.generate_imports(config_dict))
        
        # Main functions
        sections.append(adapter.generate_setup_functions(config_dict))
        
        # Main entry point
        sections.append(adapter.generate_main_function(config_dict))
        
        return "\n".join(sections)
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get comprehensive system information."""
        return self.detector.get_system_info()
    
    def get_available_methods(self) -> Dict[str, List[str]]:
        """Get available installation methods by language."""
        info = self.setup_manager.get_manager_info()
        return info['available_methods']
    
    def validate_framework(self) -> bool:
        """
        Validate framework configuration and dependencies.
        
        Returns:
            True if framework is properly configured
        """
        try:
            # Test system detection
            if not self.detector:
                logger.error("System detector not initialized")
                return False
            
            # Test setup manager
            if not self.setup_manager:
                logger.error("Setup manager not initialized")
                return False
            
            # Test language adapter
            target_language = self.config.language
            if target_language not in self.language_adapters:
                logger.error(f"Language adapter not available: {target_language}")
                return False
            
            # Test script generation
            try:
                generated_script = self.generate_setup_script()
                if not generated_script or len(generated_script.strip()) == 0:
                    logger.error("Generated script is empty")
                    return False
            except Exception as e:
                logger.error(f"Script generation failed: {e}")
                return False
            
            # Test environment validation
            validation = self.validate_environment()
            if not validation.get('valid', False):
                logger.warning(f"Environment validation issues: {validation.get('missing_tools', [])}")
            
            logger.info("Setup framework validation successful")
            return True
            
        except Exception as e:
            logger.error(f"Framework validation failed: {e}")
            return False
    
    def get_framework_info(self) -> Dict[str, Any]:
        """
        Get framework information and capabilities.
        
        Returns:
            Framework information dictionary
        """
        info = {
            'language': self.config.language,
            'package_name': self.config.package_name,
            'command_name': self.config.command_name,
            'platform': self.detector.get_platform().value,
            'supported_languages': list(self.language_adapters.keys()),
            'available_methods': self.get_available_methods(),
            'system_info': self.get_system_info(),
            'environment_validation': self.validate_environment()
        }
        
        return info
    
    def update_config(self, **kwargs) -> None:
        """
        Update framework configuration.
        
        Args:
            **kwargs: Configuration updates
        """
        for key, value in kwargs.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)
            else:
                logger.warning(f"Unknown configuration key: {key}")
        
        logger.info("Setup framework configuration updated")
    
    def reset_framework(self) -> None:
        """Reset framework to default state."""
        self.config = SetupConfig()
        self.detector = SystemDetector()
        self.setup_manager = SetupManager(self.detector)
        
        # Reinitialize runners with new detector
        for language, runner_class in [
            ('python', PythonInstallationRunner),
            ('nodejs', NodeJSInstallationRunner),
            ('typescript', TypeScriptInstallationRunner),
            ('rust', RustInstallationRunner)
        ]:
            self.installation_runners[language] = runner_class(self.detector)
        
        logger.info("Setup framework reset to defaults")