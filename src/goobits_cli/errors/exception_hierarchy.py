"""
Exception Hierarchy
===================

Exception classes and exit codes extracted from error_handler.j2 template.
Provides a consistent exception hierarchy across all languages.
"""

from enum import Enum
from typing import Optional, Dict, Any
from dataclasses import dataclass


class ExitCode(Enum):
    """Standard exit codes for CLI applications."""
    SUCCESS = 0
    GENERAL_ERROR = 1
    USAGE_ERROR = 2
    CONFIG_ERROR = 3
    NETWORK_ERROR = 4
    PERMISSION_ERROR = 5
    FILE_NOT_FOUND = 6
    
    @classmethod
    def get_language_mapping(cls, language: str) -> Dict[str, Any]:
        """Get language-specific exit code representation."""
        if language == 'python':
            return {code.name: code.value for code in cls}
        elif language in ('nodejs', 'typescript'):
            return {code.name: code.value for code in cls}
        elif language == 'rust':
            return {code.name: code.value for code in cls}
        else:
            return {code.name: code.value for code in cls}


@dataclass
class ErrorDetails:
    """Container for additional error details."""
    context: Optional[str] = None
    suggestions: Optional[str] = None
    help_text: Optional[str] = None
    related_errors: Optional[list] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'context': self.context,
            'suggestions': self.suggestions,
            'help_text': self.help_text,
            'related_errors': self.related_errors or [],
            'metadata': self.metadata or {}
        }


class BaseCliError:
    """Base CLI error definition for framework use."""
    
    def __init__(self, 
                 name: str,
                 message: str, 
                 exit_code: ExitCode, 
                 details: Optional[ErrorDetails] = None):
        self.name = name
        self.message = message
        self.exit_code = exit_code
        self.details = details or ErrorDetails()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary for template generation."""
        return {
            'name': self.name,
            'message': self.message,
            'exit_code': self.exit_code.value,
            'exit_code_name': self.exit_code.name,
            'details': self.details.to_dict()
        }


class ErrorDefinitions:
    """Standard error definitions for CLI applications."""
    
    @staticmethod
    def get_standard_errors() -> Dict[str, BaseCliError]:
        """Get standard CLI error definitions."""
        return {
            'CliError': BaseCliError(
                'CliError',
                'General CLI error',
                ExitCode.GENERAL_ERROR,
                ErrorDetails(context='Base exception class for CLI errors')
            ),
            'UsageError': BaseCliError(
                'UsageError', 
                'Command usage is incorrect',
                ExitCode.USAGE_ERROR,
                ErrorDetails(
                    context='Raised when command usage is incorrect',
                    suggestions='Check command syntax and arguments'
                )
            ),
            'ConfigError': BaseCliError(
                'ConfigError',
                'Configuration is invalid or missing', 
                ExitCode.CONFIG_ERROR,
                ErrorDetails(
                    context='Configuration validation failed',
                    suggestions='Verify configuration file format and required fields'
                )
            ),
            'NetworkError': BaseCliError(
                'NetworkError',
                'Network operation failed',
                ExitCode.NETWORK_ERROR, 
                ErrorDetails(
                    context='Network connectivity or API error',
                    suggestions='Check network connection and API endpoints'
                )
            ),
            'PermissionError': BaseCliError(
                'PermissionError',
                'Permission denied',
                ExitCode.PERMISSION_ERROR,
                ErrorDetails(
                    context='Insufficient permissions for operation',
                    suggestions='Check file permissions or run with appropriate privileges'
                )
            ),
            'FileNotFoundError': BaseCliError(
                'FileNotFoundError', 
                'Required file not found',
                ExitCode.FILE_NOT_FOUND,
                ErrorDetails(
                    context='Required file or resource missing',
                    suggestions='Verify file path and ensure file exists'
                )
            )
        }
    
    @staticmethod
    def get_error_hierarchy() -> Dict[str, str]:
        """Get error inheritance hierarchy."""
        return {
            'CliError': None,  # Base class
            'UsageError': 'CliError',
            'ConfigError': 'CliError', 
            'NetworkError': 'CliError',
            'PermissionError': 'CliError',
            'FileNotFoundError': 'CliError'
        }


# Python-specific implementations for runtime use
class CliError(Exception):
    """Base exception class for CLI errors."""
    
    def __init__(self, message: str, exit_code: ExitCode = ExitCode.GENERAL_ERROR, 
                 details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.exit_code = exit_code
        self.details = details or {}


class UsageError(CliError):
    """Raised when command usage is incorrect."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, ExitCode.USAGE_ERROR, details)


class ConfigError(CliError):
    """Raised when configuration is invalid or missing."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, ExitCode.CONFIG_ERROR, details)


class NetworkError(CliError):
    """Raised when network operations fail."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, ExitCode.NETWORK_ERROR, details)


class PermissionError(CliError):
    """Raised when permission is denied."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, ExitCode.PERMISSION_ERROR, details)


class FileNotFoundError(CliError):
    """Raised when a required file is not found."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, ExitCode.FILE_NOT_FOUND, details)