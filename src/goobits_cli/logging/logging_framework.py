"""
Core Logging Framework
======================

This module contains the central logging framework that orchestrates
logging code generation across all supported languages.

Previously, this logic was embedded in 1,215 lines of logger.j2 template.
Now it's testable, maintainable Python code.
"""

import os
from dataclasses import dataclass
from typing import Dict, Any, Optional, List
from enum import Enum


class LogLevel(Enum):
    """Logging levels supported across all languages."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class Environment(Enum):
    """Deployment environments that affect logging behavior."""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


@dataclass
class LoggingConfig:
    """
    Universal logging configuration extracted from template conditionals.
    
    This represents the business logic that was previously scattered
    throughout the logger.j2 template in various {% if %} blocks.
    """
    
    # Basic configuration
    project_name: str
    command_name: str
    display_name: str
    description: str
    
    # Logging behavior
    environment: Environment = Environment.DEVELOPMENT
    log_level: LogLevel = LogLevel.INFO
    structured_logging: bool = False
    
    # Output configuration
    log_to_file: bool = False
    log_file_path: Optional[str] = None
    log_to_stdout: bool = True
    log_to_stderr: bool = False
    
    # Advanced features
    include_context: bool = True
    include_timestamp: bool = True
    include_caller_info: bool = True
    json_format_in_production: bool = True
    colorized_output: bool = True
    
    # Performance settings
    async_logging: bool = False
    buffer_size: int = 1024
    
    def should_use_json_format(self) -> bool:
        """Determine if JSON format should be used based on environment."""
        return (
            self.structured_logging or 
            (self.environment == Environment.PRODUCTION and self.json_format_in_production)
        )
    
    def get_output_stream(self) -> str:
        """Determine the primary output stream based on configuration."""
        if self.log_to_file and self.log_file_path:
            return f"file:{self.log_file_path}"
        elif self.log_to_stderr:
            return "stderr"
        else:
            return "stdout"
    
    def should_include_color(self) -> bool:
        """Determine if colorized output should be used."""
        return (
            self.colorized_output and 
            self.environment != Environment.PRODUCTION and
            not self.structured_logging
        )


class LoggingFramework:
    """
    Central logging framework extracted from 1,215-line logger.j2 template.
    
    This class orchestrates logging code generation for all supported languages,
    extracting the complex business logic that was previously embedded in
    template conditionals.
    """
    
    def __init__(self):
        """Initialize the logging framework with language adapters."""
        # Lazy import to avoid circular dependencies
        from .language_adapters import (
            PythonLoggingAdapter,
            NodeJSLoggingAdapter,
            TypeScriptLoggingAdapter,
            RustLoggingAdapter
        )
        
        self.adapters = {
            "python": PythonLoggingAdapter(),
            "nodejs": NodeJSLoggingAdapter(),
            "typescript": TypeScriptLoggingAdapter(),
            "rust": RustLoggingAdapter()
        }
    
    def generate_logging_code(self, language: str, config: Dict[str, Any]) -> str:
        """
        Generate language-specific logging code using testable business logic.
        
        This method replaces the complex template conditionals with proper
        Python code that can be unit tested.
        
        Args:
            language: Target language (python, nodejs, typescript, rust)
            config: Raw configuration dictionary
            
        Returns:
            Generated logging code for the specified language
        """
        # Process configuration (previously in template conditionals)
        logging_config = self._process_configuration(config)
        
        # Validate configuration
        self._validate_configuration(logging_config)
        
        # Get appropriate language adapter
        adapter = self._get_language_adapter(language)
        
        # Generate code using adapter
        return adapter.generate_code(logging_config)
    
    def _process_configuration(self, raw_config: Dict[str, Any]) -> LoggingConfig:
        """
        Process raw configuration into structured LoggingConfig.
        
        This extracts all the business logic that was previously embedded
        in template conditionals like:
        {% if config.environment == "production" and config.structured_logging %}
        
        Now it's testable Python code.
        """
        # Extract project information
        project_info = raw_config.get("project", {})
        
        # Process environment
        env_str = raw_config.get("environment", "development").lower()
        environment = Environment.DEVELOPMENT
        for env in Environment:
            if env.value == env_str:
                environment = env
                break
        
        # Process log level
        level_str = raw_config.get("log_level", "INFO").upper()
        log_level = LogLevel.INFO
        for level in LogLevel:
            if level.value == level_str:
                log_level = level
                break
        
        # Create configuration
        config = LoggingConfig(
            project_name=project_info.get("name", "cli"),
            command_name=project_info.get("command_name", "cli"),
            display_name=project_info.get("display_name", "CLI"),
            description=project_info.get("description", ""),
            environment=environment,
            log_level=log_level,
            structured_logging=raw_config.get("structured_logging", False),
            log_to_file=raw_config.get("log_to_file", False),
            log_file_path=raw_config.get("log_file_path"),
            log_to_stdout=raw_config.get("log_to_stdout", True),
            log_to_stderr=raw_config.get("log_to_stderr", False),
            include_context=raw_config.get("include_context", True),
            include_timestamp=raw_config.get("include_timestamp", True),
            include_caller_info=raw_config.get("include_caller_info", True),
            json_format_in_production=raw_config.get("json_format_in_production", True),
            colorized_output=raw_config.get("colorized_output", True),
            async_logging=raw_config.get("async_logging", False),
            buffer_size=raw_config.get("buffer_size", 1024)
        )
        
        return config
    
    def _validate_configuration(self, config: LoggingConfig) -> None:
        """
        Validate logging configuration for consistency.
        
        This validation logic was previously scattered throughout
        the template in various conditional blocks.
        """
        # Validate file logging configuration
        if config.log_to_file and not config.log_file_path:
            raise ValueError("log_to_file is True but log_file_path is not specified")
        
        # Validate output streams
        if not any([config.log_to_file, config.log_to_stdout, config.log_to_stderr]):
            raise ValueError("At least one output stream must be enabled")
        
        # Validate buffer size
        if config.async_logging and config.buffer_size < 1:
            raise ValueError("Buffer size must be positive when async logging is enabled")
    
    def _get_language_adapter(self, language: str):
        """
        Get the appropriate language adapter.
        
        Args:
            language: Target language
            
        Returns:
            Language-specific adapter instance
            
        Raises:
            ValueError: If language is not supported
        """
        if language not in self.adapters:
            raise ValueError(
                f"Unsupported language: {language}. "
                f"Supported languages: {', '.join(self.adapters.keys())}"
            )
        
        return self.adapters[language]
    
    def get_supported_languages(self) -> List[str]:
        """Get list of supported languages."""
        return list(self.adapters.keys())
    
    def get_default_configuration(self) -> LoggingConfig:
        """Get default logging configuration for reference."""
        return LoggingConfig(
            project_name="default-cli",
            command_name="cli",
            display_name="CLI",
            description="Command Line Interface"
        )