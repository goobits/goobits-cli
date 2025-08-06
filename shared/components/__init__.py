"""
Goobits CLI Shared Components

This package contains shared validation logic and components used across
all language generators.
"""

from .validation_framework import (
    ValidationContext,
    ValidationResult,
    ValidationMode,
    ValidationSeverity,
    ValidationMessage,
    ValidationRegistry,
    ValidationRunner,
    BaseValidator,
    validate_config,
    create_default_runner
)

from .validators import (
    CommandValidator,
    ArgumentValidator,
    HookValidator,
    OptionValidator,
    ErrorCodeValidator,
    TypeValidator,
    ConfigValidator,
    CompletionValidator
)

__all__ = [
    # Framework
    'ValidationContext',
    'ValidationResult', 
    'ValidationMode',
    'ValidationSeverity',
    'ValidationMessage',
    'ValidationRegistry',
    'ValidationRunner',
    'BaseValidator',
    'validate_config',
    'create_default_runner',
    
    # Validators
    'CommandValidator',
    'ArgumentValidator', 
    'HookValidator',
    'OptionValidator',
    'ErrorCodeValidator',
    'TypeValidator',
    'ConfigValidator',
    'CompletionValidator'
]