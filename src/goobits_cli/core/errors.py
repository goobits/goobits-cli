"""Unified exception classes for Goobits CLI Framework.

This module provides all exception classes used throughout the framework,
centralized to avoid circular imports and ensure consistent error handling.
"""

from typing import Any, Dict, List, Optional


class GeneratorError(Exception):
    """Base exception for generator errors."""

    def __init__(
        self, message: str, error_code: int = 1, details: Optional[str] = None
    ):
        self.message = message
        self.error_code = error_code
        self.details = details
        super().__init__(self.message)


class ConfigurationError(GeneratorError):
    """Configuration validation or loading error."""

    def __init__(
        self,
        message: str,
        field: Optional[str] = None,
        suggestion: Optional[str] = None,
    ):
        self.field = field
        self.suggestion = suggestion
        error_code = 2  # Configuration errors
        super().__init__(message, error_code, f"Field: {field}" if field else None)


class TemplateError(GeneratorError):
    """Template rendering or loading error."""

    def __init__(
        self,
        message: str,
        template_name: Optional[str] = None,
        line_number: Optional[int] = None,
    ):
        self.template_name = template_name
        self.line_number = line_number
        error_code = 3  # Template errors
        details = f"Template: {template_name}" if template_name else None
        if line_number:
            details += f", Line: {line_number}" if details else f"Line: {line_number}"
        super().__init__(message, error_code, details)


class DependencyError(GeneratorError):
    """Missing or incompatible dependency error."""

    def __init__(
        self, message: str, dependency: str, install_command: Optional[str] = None
    ):
        self.dependency = dependency
        self.install_command = install_command
        error_code = 4  # Dependency errors
        super().__init__(message, error_code, f"Dependency: {dependency}")


class ValidationError(GeneratorError):
    """Input validation error."""

    def __init__(
        self,
        message: str,
        field: str,
        value: Optional[str] = None,
        valid_options: Optional[List[str]] = None,
    ):
        self.field = field
        self.value = value
        self.valid_options = valid_options
        error_code = 2  # Validation errors
        details = f"Field: {field}"
        if value:
            details += f", Value: {value}"
        if valid_options:
            details += f", Valid options: {', '.join(valid_options)}"
        super().__init__(message, error_code, details)


class RenderError(GeneratorError):
    """Error during code rendering."""

    def __init__(
        self,
        message: str,
        language: Optional[str] = None,
        component: Optional[str] = None,
    ):
        self.language = language
        self.component = component
        error_code = 5  # Render errors
        details = []
        if language:
            details.append(f"Language: {language}")
        if component:
            details.append(f"Component: {component}")
        super().__init__(message, error_code, ", ".join(details) if details else None)


__all__ = [
    "GeneratorError",
    "ConfigurationError",
    "TemplateError",
    "DependencyError",
    "ValidationError",
    "RenderError",
]
