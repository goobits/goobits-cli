"""
Error Framework
===============

Core framework extracted from error_handler.j2 template.
Orchestrates error handling generation for all languages with consistent functionality.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
from enum import Enum
from .exception_hierarchy import ExitCode, ErrorDefinitions
from .language_adapters import (
    PythonErrorAdapter,
    NodeJSErrorAdapter, 
    TypeScriptErrorAdapter,
    RustErrorAdapter
)


@dataclass
class ErrorConfig:
    """Error framework configuration schema."""
    project_name: str
    language: str
    debug_mode: bool = False
    verbose_mode: bool = False
    custom_errors: List[Dict[str, Any]] = field(default_factory=list)
    exit_on_error: bool = True
    error_reporting: Dict[str, Any] = field(default_factory=dict)
    global_handler: bool = True
    keyboard_interrupt_handler: bool = True
    context_tracking: bool = True


class ErrorFramework:
    """
    Error framework extracted from error_handler.j2.
    
    Generates error handling implementations for all supported languages
    with consistent error types, exit codes, and handling patterns.
    """
    
    def __init__(self):
        """Initialize the error framework."""
        self._adapters = {
            'python': PythonErrorAdapter(),
            'nodejs': NodeJSErrorAdapter(),
            'typescript': TypeScriptErrorAdapter(),
            'rust': RustErrorAdapter()
        }
        self.error_definitions = ErrorDefinitions()
    
    def generate_error_code(self, language: str, config: Dict[str, Any]) -> str:
        """
        Generate error handling code for specified language.
        
        Args:
            language: Target language ('python', 'nodejs', 'typescript', 'rust')
            config: Configuration including project metadata
            
        Returns:
            Generated error handling code as string
            
        Raises:
            ValueError: If language is not supported
        """
        if language not in self._adapters:
            supported = ', '.join(self._adapters.keys())
            raise ValueError(f"Unsupported language: {language}. Supported languages: {supported}")
        
        # Process configuration
        error_config = self._process_configuration(config, language)
        
        # Validate configuration
        self._validate_configuration(error_config)
        
        # Generate code using appropriate adapter
        adapter = self._adapters[language]
        return adapter.generate_code(config)
    
    def _process_configuration(self, config: Dict[str, Any], language: str) -> ErrorConfig:
        """Process raw configuration into structured error schema."""
        project = config.get('project', {})
        error_settings = config.get('error_handling', {})
        
        # Extract project information
        project_name = project.get('name', 'CLI')
        
        # Process error handling settings
        debug_mode = error_settings.get('debug', False)
        verbose_mode = error_settings.get('verbose', False)
        exit_on_error = error_settings.get('exit_on_error', True)
        
        # Extract custom errors if defined
        custom_errors = error_settings.get('custom_errors', [])
        
        return ErrorConfig(
            project_name=project_name,
            language=language,
            debug_mode=debug_mode,
            verbose_mode=verbose_mode,
            custom_errors=custom_errors,
            exit_on_error=exit_on_error,
            error_reporting=error_settings.get('reporting', {}),
            global_handler=error_settings.get('global_handler', True),
            keyboard_interrupt_handler=error_settings.get('keyboard_interrupt_handler', True),
            context_tracking=error_settings.get('context_tracking', True)
        )
    
    def _validate_configuration(self, config: ErrorConfig) -> None:
        """Validate the processed error configuration."""
        if not config.project_name:
            raise ValueError("Project name is required for error handling generation")
        
        if not config.language:
            raise ValueError("Language is required for error handling generation")
        
        if config.language not in self._adapters:
            supported = ', '.join(self._adapters.keys())
            raise ValueError(f"Unsupported language: {config.language}. Supported: {supported}")
        
        # Validate custom errors format
        for i, error_def in enumerate(config.custom_errors):
            if not isinstance(error_def, dict):
                raise ValueError(f"Custom error {i} must be a dictionary")
            
            required_fields = ['name', 'message', 'exit_code']
            for field in required_fields:
                if field not in error_def:
                    raise ValueError(f"Custom error {i} missing required field: {field}")
    
    def get_standard_errors(self) -> Dict[str, Any]:
        """Get standard error definitions."""
        return self.error_definitions.get_standard_errors()
    
    def get_exit_codes(self) -> Dict[str, int]:
        """Get standard exit codes.""" 
        return {code.name: code.value for code in ExitCode}
    
    def get_supported_languages(self) -> List[str]:
        """Get list of supported languages."""
        return list(self._adapters.keys())
    
    def validate_error_definition(self, error_def: Dict[str, Any]) -> bool:
        """Validate a custom error definition."""
        required_fields = ['name', 'message', 'exit_code']
        
        # Check required fields
        for field in required_fields:
            if field not in error_def:
                return False
        
        # Validate exit code
        exit_code = error_def['exit_code']
        if isinstance(exit_code, str):
            try:
                ExitCode[exit_code.upper()]
            except KeyError:
                return False
        elif isinstance(exit_code, int):
            valid_codes = [code.value for code in ExitCode]
            if exit_code not in valid_codes:
                return False
        else:
            return False
        
        return True
    
    def generate_error_documentation(self, config: Dict[str, Any]) -> str:
        """Generate documentation for error handling."""
        error_config = self._process_configuration(config, 'python')
        
        lines = [
            f"# Error Handling Documentation for {error_config.project_name}",
            "",
            "## Standard Exit Codes",
            ""
        ]
        
        # Document exit codes
        for code in ExitCode:
            lines.append(f"- **{code.name}** ({code.value}): {self._get_exit_code_description(code)}")
        
        lines.extend([
            "",
            "## Standard Error Types",
            ""
        ])
        
        # Document error types
        errors = self.error_definitions.get_standard_errors()
        for error_name, error_def in errors.items():
            lines.append(f"### {error_name}")
            lines.append(f"- **Exit Code**: {error_def.exit_code.name}")
            lines.append(f"- **Description**: {error_def.details.context}")
            if error_def.details.suggestions:
                lines.append(f"- **Suggestions**: {error_def.details.suggestions}")
            lines.append("")
        
        if error_config.custom_errors:
            lines.extend([
                "## Custom Error Types",
                ""
            ])
            
            for error_def in error_config.custom_errors:
                lines.append(f"### {error_def['name']}")
                lines.append(f"- **Message**: {error_def['message']}")
                lines.append(f"- **Exit Code**: {error_def['exit_code']}")
                if 'description' in error_def:
                    lines.append(f"- **Description**: {error_def['description']}")
                lines.append("")
        
        return '\n'.join(lines)
    
    def _get_exit_code_description(self, code: ExitCode) -> str:
        """Get description for exit code."""
        descriptions = {
            ExitCode.SUCCESS: "Operation completed successfully",
            ExitCode.GENERAL_ERROR: "General error occurred",
            ExitCode.USAGE_ERROR: "Incorrect command usage",
            ExitCode.CONFIG_ERROR: "Configuration error",
            ExitCode.NETWORK_ERROR: "Network operation failed",
            ExitCode.PERMISSION_ERROR: "Permission denied",
            ExitCode.FILE_NOT_FOUND: "Required file not found"
        }
        return descriptions.get(code, "Unknown error code")