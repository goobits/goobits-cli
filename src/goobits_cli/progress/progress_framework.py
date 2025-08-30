"""
Progress Framework
==================

Main orchestration framework for progress indicators and visual feedback systems.
Coordinates between progress managers, display adapters, and language adapters.
"""

import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from pathlib import Path

from .progress_manager import ProgressManager, ProgressIndicator, ProgressType, SpinnerStyle
from .display_adapters import DisplayAdapter, RichDisplayAdapter, FallbackDisplayAdapter, SmartDisplayAdapter
from .language_adapters import (
    PythonProgressAdapter, NodeJSProgressAdapter, 
    TypeScriptProgressAdapter, RustProgressAdapter
)

logger = logging.getLogger(__name__)


@dataclass
class ProgressConfig:
    """Configuration for progress framework."""
    language: str = "python"
    use_rich: bool = True
    fallback_enabled: bool = True
    default_spinner_style: SpinnerStyle = SpinnerStyle.DOTS
    show_time: bool = True
    show_percentage: bool = True
    show_count: bool = False
    update_interval: float = 0.1
    console_output: bool = True
    log_progress: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'language': self.language,
            'use_rich': self.use_rich,
            'fallback_enabled': self.fallback_enabled,
            'default_spinner_style': self.default_spinner_style.value,
            'show_time': self.show_time,
            'show_percentage': self.show_percentage,
            'show_count': self.show_count,
            'update_interval': self.update_interval,
            'console_output': self.console_output,
            'log_progress': self.log_progress
        }


class ProgressFramework:
    """
    Main progress framework orchestrator.
    
    Coordinates progress management, display adapters, and code generation
    for creating consistent progress indicators across all supported languages.
    """
    
    def __init__(self, config: Optional[ProgressConfig] = None):
        """
        Initialize progress framework.
        
        Args:
            config: Framework configuration
        """
        self.config = config or ProgressConfig()
        self.progress_manager = ProgressManager(
            use_rich=self.config.use_rich and self.config.fallback_enabled
        )
        
        # Initialize display adapter
        if self.config.use_rich:
            try:
                self.display_adapter = SmartDisplayAdapter(prefer_rich=True)
            except ImportError:
                logger.warning("Rich not available, using fallback display adapter")
                self.display_adapter = FallbackDisplayAdapter()
        else:
            self.display_adapter = FallbackDisplayAdapter()
        
        # Initialize language adapters
        self.language_adapters = {
            'python': PythonProgressAdapter(),
            'nodejs': NodeJSProgressAdapter(),
            'typescript': TypeScriptProgressAdapter(),
            'rust': RustProgressAdapter()
        }
        
        logger.info(f"Progress framework initialized for {self.config.language}")
    
    def create_progress_indicator(
        self,
        progress_type: ProgressType,
        description: str = "Processing...",
        total: Optional[int] = None,
        **kwargs
    ) -> ProgressIndicator:
        """
        Create a progress indicator with framework defaults.
        
        Args:
            progress_type: Type of progress indicator
            description: Description text
            total: Total items (for progress bars)
            **kwargs: Additional configuration
            
        Returns:
            Configured progress indicator
        """
        return ProgressIndicator(
            type=progress_type,
            description=description,
            total=total,
            show_time=kwargs.get('show_time', self.config.show_time),
            show_percentage=kwargs.get('show_percentage', self.config.show_percentage),
            show_count=kwargs.get('show_count', self.config.show_count),
            spinner_style=kwargs.get('spinner_style', self.config.default_spinner_style),
            update_interval=kwargs.get('update_interval', self.config.update_interval)
        )
    
    def get_progress_manager(self) -> ProgressManager:
        """Get the managed progress manager instance."""
        return self.progress_manager
    
    def get_display_adapter(self) -> DisplayAdapter:
        """Get the configured display adapter."""
        return self.display_adapter
    
    def generate_language_code(
        self,
        language: Optional[str] = None,
        template_vars: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate progress management code for specified language.
        
        Args:
            language: Target language (defaults to config.language)
            template_vars: Additional template variables
            
        Returns:
            Generated code string
        """
        target_language = language or self.config.language
        
        if target_language not in self.language_adapters:
            raise ValueError(f"Unsupported language: {target_language}")
        
        adapter = self.language_adapters[target_language]
        config_dict = self.config.to_dict()
        
        if template_vars:
            config_dict.update(template_vars)
        
        # Generate code sections
        sections = []
        
        # Header comment
        sections.append(f"// Progress management for {target_language}")
        sections.append(f"// Generated by Goobits CLI Framework Progress System")
        sections.append("")
        
        # Imports
        sections.append(adapter.generate_imports(config_dict))
        sections.append("")
        
        # Main class/struct
        if hasattr(adapter, 'generate_progress_manager_class'):
            sections.append(adapter.generate_progress_manager_class(config_dict))
        elif hasattr(adapter, 'generate_progress_manager_struct'):
            sections.append(adapter.generate_progress_manager_struct(config_dict))
        
        sections.append("")
        
        # Convenience functions
        if hasattr(adapter, 'generate_convenience_functions'):
            sections.append(adapter.generate_convenience_functions(config_dict))
        
        # Additional dependencies (for Rust)
        if hasattr(adapter, 'generate_cargo_dependencies'):
            sections.append("")
            sections.append("/*")
            sections.append(adapter.generate_cargo_dependencies(config_dict))
            sections.append("*/")
        
        return "\n".join(sections)
    
    def validate_framework(self) -> bool:
        """
        Validate framework configuration and dependencies.
        
        Returns:
            True if framework is properly configured
        """
        try:
            # Test progress manager
            if not self.progress_manager:
                logger.error("Progress manager not initialized")
                return False
            
            # Test display adapter
            if not self.display_adapter:
                logger.error("Display adapter not initialized")
                return False
            
            # Test language adapter
            target_language = self.config.language
            if target_language not in self.language_adapters:
                logger.error(f"Language adapter not available: {target_language}")
                return False
            
            # Test code generation
            try:
                generated_code = self.generate_language_code()
                if not generated_code or len(generated_code.strip()) == 0:
                    logger.error("Generated code is empty")
                    return False
            except Exception as e:
                logger.error(f"Code generation failed: {e}")
                return False
            
            logger.info("Progress framework validation successful")
            return True
            
        except Exception as e:
            logger.error(f"Framework validation failed: {e}")
            return False
    
    def get_framework_info(self) -> Dict[str, Any]:
        """
        Get framework information and status.
        
        Returns:
            Framework information dictionary
        """
        info = {
            'language': self.config.language,
            'use_rich': self.config.use_rich,
            'fallback_enabled': self.config.fallback_enabled,
            'rich_available': False,
            'supported_languages': list(self.language_adapters.keys()),
            'display_adapter_type': type(self.display_adapter).__name__,
            'progress_manager_stats': self.progress_manager.get_manager_stats()
        }
        
        # Check Rich availability
        try:
            from rich.console import Console
            info['rich_available'] = True
        except ImportError:
            info['rich_available'] = False
        
        # Check if smart adapter is being used
        if isinstance(self.display_adapter, SmartDisplayAdapter):
            info['smart_adapter_using_rich'] = self.display_adapter.is_rich_available()
        
        return info
    
    def create_spinner_indicator(
        self,
        text: str = "Processing...",
        spinner_style: Optional[SpinnerStyle] = None
    ) -> ProgressIndicator:
        """
        Convenience method to create a spinner indicator.
        
        Args:
            text: Spinner text
            spinner_style: Spinner animation style
            
        Returns:
            Configured spinner indicator
        """
        return self.create_progress_indicator(
            ProgressType.SPINNER,
            description=text,
            spinner_style=spinner_style or self.config.default_spinner_style
        )
    
    def create_progress_bar_indicator(
        self,
        description: str = "Processing...",
        total: Optional[int] = None,
        show_time: Optional[bool] = None,
        show_percentage: Optional[bool] = None,
        show_count: Optional[bool] = None
    ) -> ProgressIndicator:
        """
        Convenience method to create a progress bar indicator.
        
        Args:
            description: Progress description
            total: Total number of items
            show_time: Show elapsed/remaining time
            show_percentage: Show percentage complete
            show_count: Show item count
            
        Returns:
            Configured progress bar indicator
        """
        return self.create_progress_indicator(
            ProgressType.PROGRESS_BAR,
            description=description,
            total=total,
            show_time=show_time if show_time is not None else self.config.show_time,
            show_percentage=show_percentage if show_percentage is not None else self.config.show_percentage,
            show_count=show_count if show_count is not None else self.config.show_count
        )
    
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
        
        logger.info("Progress framework configuration updated")
    
    def reset_framework(self) -> None:
        """Reset framework to default state."""
        self.config = ProgressConfig()
        self.progress_manager = ProgressManager(use_rich=self.config.use_rich)
        
        if self.config.use_rich:
            try:
                self.display_adapter = SmartDisplayAdapter(prefer_rich=True)
            except ImportError:
                self.display_adapter = FallbackDisplayAdapter()
        else:
            self.display_adapter = FallbackDisplayAdapter()
        
        logger.info("Progress framework reset to defaults")