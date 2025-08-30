"""
Validation Engine
================

Validation framework extracted from command_handler.j2 template.
Provides argument and option validation with type checking and custom validation rules.
"""

import re
import os
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union, Callable
from pathlib import Path
from urllib.parse import urlparse
from email.utils import parseaddr

from .command_framework import Argument, Option, ArgumentType, OptionType


class ValidationError(Exception):
    """Raised when validation fails."""
    pass


class BaseValidator(ABC):
    """Base class for validators."""
    
    @abstractmethod
    def validate(self, value: Any, context: Dict[str, Any] = None) -> Any:
        """
        Validate and potentially transform a value.
        
        Args:
            value: Value to validate
            context: Additional validation context
            
        Returns:
            Validated (potentially transformed) value
            
        Raises:
            ValidationError: If validation fails
        """
        pass


class ArgumentValidator(BaseValidator):
    """Validator for command arguments."""
    
    def __init__(self, argument: Argument):
        """Initialize argument validator."""
        self.argument = argument
        self._type_validators = {
            ArgumentType.STRING: self._validate_string,
            ArgumentType.INTEGER: self._validate_integer,
            ArgumentType.FLOAT: self._validate_float,
            ArgumentType.BOOLEAN: self._validate_boolean,
            ArgumentType.PATH: self._validate_path,
            ArgumentType.EMAIL: self._validate_email,
            ArgumentType.URL: self._validate_url
        }
    
    def validate(self, value: Any, context: Dict[str, Any] = None) -> Any:
        """Validate argument value."""
        context = context or {}
        
        # Handle multiple values
        if self.argument.multiple:
            if not isinstance(value, (list, tuple)):
                raise ValidationError(f"Argument '{self.argument.name}' expects multiple values")
            
            validated_values = []
            for i, item in enumerate(value):
                try:
                    validated_values.append(self._validate_single_value(item, context))
                except ValidationError as e:
                    raise ValidationError(f"Argument '{self.argument.name}' item {i+1}: {e}")
            
            return validated_values
        else:
            return self._validate_single_value(value, context)
    
    def _validate_single_value(self, value: Any, context: Dict[str, Any]) -> Any:
        """Validate a single argument value."""
        # Required check
        if self.argument.required and (value is None or value == ''):
            raise ValidationError(f"Argument '{self.argument.name}' is required")
        
        # Allow None/empty for optional arguments
        if not self.argument.required and (value is None or value == ''):
            return None
        
        # Type validation
        validator = self._type_validators.get(self.argument.type)
        if validator:
            value = validator(value, context)
        
        # Custom validation rules
        if self.argument.validation:
            value = self._apply_custom_validation(value, self.argument.validation, context)
        
        return value
    
    def _validate_string(self, value: Any, context: Dict[str, Any]) -> str:
        """Validate string value."""
        if not isinstance(value, str):
            value = str(value)
        return value
    
    def _validate_integer(self, value: Any, context: Dict[str, Any]) -> int:
        """Validate integer value."""
        try:
            return int(value)
        except (ValueError, TypeError):
            raise ValidationError(f"Argument '{self.argument.name}' must be an integer")
    
    def _validate_float(self, value: Any, context: Dict[str, Any]) -> float:
        """Validate float value."""
        try:
            return float(value)
        except (ValueError, TypeError):
            raise ValidationError(f"Argument '{self.argument.name}' must be a number")
    
    def _validate_boolean(self, value: Any, context: Dict[str, Any]) -> bool:
        """Validate boolean value."""
        if isinstance(value, bool):
            return value
        
        if isinstance(value, str):
            lower_value = value.lower()
            if lower_value in ('true', '1', 'yes', 'y', 'on'):
                return True
            elif lower_value in ('false', '0', 'no', 'n', 'off'):
                return False
        
        raise ValidationError(f"Argument '{self.argument.name}' must be a boolean value")
    
    def _validate_path(self, value: Any, context: Dict[str, Any]) -> Path:
        """Validate path value."""
        try:
            path = Path(str(value))
            # Expand user and resolve relative paths
            path = path.expanduser().resolve()
            return path
        except Exception as e:
            raise ValidationError(f"Argument '{self.argument.name}' must be a valid path: {e}")
    
    def _validate_email(self, value: Any, context: Dict[str, Any]) -> str:
        """Validate email value."""
        value_str = str(value)
        
        # Basic email validation using email.utils
        name, email = parseaddr(value_str)
        if not email or '@' not in email:
            raise ValidationError(f"Argument '{self.argument.name}' must be a valid email address")
        
        # Additional basic validation
        if not re.match(r'^[^@]+@[^@]+\.[^@]+$', email):
            raise ValidationError(f"Argument '{self.argument.name}' must be a valid email address")
        
        return email
    
    def _validate_url(self, value: Any, context: Dict[str, Any]) -> str:
        """Validate URL value."""
        value_str = str(value)
        
        try:
            result = urlparse(value_str)
            if not all([result.scheme, result.netloc]):
                raise ValueError("Invalid URL format")
            return value_str
        except Exception:
            raise ValidationError(f"Argument '{self.argument.name}' must be a valid URL")
    
    def _apply_custom_validation(self, value: Any, validation_rules: Dict[str, Any], context: Dict[str, Any]) -> Any:
        """Apply custom validation rules."""
        # Min/max length for strings
        if 'min_length' in validation_rules and isinstance(value, str):
            if len(value) < validation_rules['min_length']:
                raise ValidationError(f"Argument '{self.argument.name}' must be at least {validation_rules['min_length']} characters")
        
        if 'max_length' in validation_rules and isinstance(value, str):
            if len(value) > validation_rules['max_length']:
                raise ValidationError(f"Argument '{self.argument.name}' must be no more than {validation_rules['max_length']} characters")
        
        # Min/max value for numbers
        if 'min_value' in validation_rules and isinstance(value, (int, float)):
            if value < validation_rules['min_value']:
                raise ValidationError(f"Argument '{self.argument.name}' must be at least {validation_rules['min_value']}")
        
        if 'max_value' in validation_rules and isinstance(value, (int, float)):
            if value > validation_rules['max_value']:
                raise ValidationError(f"Argument '{self.argument.name}' must be no more than {validation_rules['max_value']}")
        
        # Regex pattern matching
        if 'pattern' in validation_rules and isinstance(value, str):
            pattern = validation_rules['pattern']
            if not re.match(pattern, value):
                error_msg = validation_rules.get('pattern_error', f"Argument '{self.argument.name}' format is invalid")
                raise ValidationError(error_msg)
        
        # Custom validator function
        if 'custom' in validation_rules:
            custom_validator = validation_rules['custom']
            if callable(custom_validator):
                try:
                    value = custom_validator(value, context)
                except Exception as e:
                    raise ValidationError(f"Argument '{self.argument.name}' validation failed: {e}")
        
        return value


class OptionValidator(BaseValidator):
    """Validator for command options."""
    
    def __init__(self, option: Option):
        """Initialize option validator."""
        self.option = option
        self._type_validators = {
            OptionType.STRING: self._validate_string,
            OptionType.INTEGER: self._validate_integer,
            OptionType.FLOAT: self._validate_float,
            OptionType.BOOLEAN: self._validate_boolean,
            OptionType.CHOICE: self._validate_choice,
            OptionType.PATH: self._validate_path,
            OptionType.FILE: self._validate_file,
            OptionType.DIRECTORY: self._validate_directory
        }
    
    def validate(self, value: Any, context: Dict[str, Any] = None) -> Any:
        """Validate option value."""
        context = context or {}
        
        # Handle multiple values
        if self.option.multiple:
            if not isinstance(value, (list, tuple)):
                # Single value to list
                value = [value] if value is not None else []
            
            validated_values = []
            for i, item in enumerate(value):
                try:
                    validated_values.append(self._validate_single_value(item, context))
                except ValidationError as e:
                    raise ValidationError(f"Option '{self.option.name}' item {i+1}: {e}")
            
            return validated_values
        else:
            return self._validate_single_value(value, context)
    
    def _validate_single_value(self, value: Any, context: Dict[str, Any]) -> Any:
        """Validate a single option value."""
        # Use default if value is None
        if value is None:
            value = self.option.default
        
        # Required check
        if self.option.required and (value is None or value == ''):
            raise ValidationError(f"Option '{self.option.name}' is required")
        
        # Allow None/empty for optional options
        if not self.option.required and (value is None or value == ''):
            return value
        
        # Type validation
        validator = self._type_validators.get(self.option.type)
        if validator:
            value = validator(value, context)
        
        # Custom validation rules
        if self.option.validation:
            value = self._apply_custom_validation(value, self.option.validation, context)
        
        return value
    
    def _validate_string(self, value: Any, context: Dict[str, Any]) -> str:
        """Validate string value."""
        return str(value)
    
    def _validate_integer(self, value: Any, context: Dict[str, Any]) -> int:
        """Validate integer value."""
        try:
            return int(value)
        except (ValueError, TypeError):
            raise ValidationError(f"Option '{self.option.name}' must be an integer")
    
    def _validate_float(self, value: Any, context: Dict[str, Any]) -> float:
        """Validate float value."""
        try:
            return float(value)
        except (ValueError, TypeError):
            raise ValidationError(f"Option '{self.option.name}' must be a number")
    
    def _validate_boolean(self, value: Any, context: Dict[str, Any]) -> bool:
        """Validate boolean value."""
        if isinstance(value, bool):
            return value
        
        if isinstance(value, str):
            lower_value = value.lower()
            if lower_value in ('true', '1', 'yes', 'y', 'on'):
                return True
            elif lower_value in ('false', '0', 'no', 'n', 'off'):
                return False
        
        raise ValidationError(f"Option '{self.option.name}' must be a boolean value")
    
    def _validate_choice(self, value: Any, context: Dict[str, Any]) -> str:
        """Validate choice value."""
        value_str = str(value)
        
        if not self.option.choices:
            raise ValidationError(f"Option '{self.option.name}' has no valid choices defined")
        
        if value_str not in self.option.choices:
            choices_str = ', '.join(self.option.choices)
            raise ValidationError(f"Option '{self.option.name}' must be one of: {choices_str}")
        
        return value_str
    
    def _validate_path(self, value: Any, context: Dict[str, Any]) -> Path:
        """Validate path value."""
        try:
            path = Path(str(value))
            path = path.expanduser().resolve()
            return path
        except Exception as e:
            raise ValidationError(f"Option '{self.option.name}' must be a valid path: {e}")
    
    def _validate_file(self, value: Any, context: Dict[str, Any]) -> Path:
        """Validate file path value."""
        path = self._validate_path(value, context)
        
        # Check if file exists (optional validation)
        validation_rules = self.option.validation or {}
        if validation_rules.get('must_exist', False) and not path.is_file():
            raise ValidationError(f"Option '{self.option.name}' must be an existing file: {path}")
        
        return path
    
    def _validate_directory(self, value: Any, context: Dict[str, Any]) -> Path:
        """Validate directory path value."""
        path = self._validate_path(value, context)
        
        # Check if directory exists (optional validation)
        validation_rules = self.option.validation or {}
        if validation_rules.get('must_exist', False) and not path.is_dir():
            raise ValidationError(f"Option '{self.option.name}' must be an existing directory: {path}")
        
        return path
    
    def _apply_custom_validation(self, value: Any, validation_rules: Dict[str, Any], context: Dict[str, Any]) -> Any:
        """Apply custom validation rules (shared with ArgumentValidator)."""
        # Same implementation as ArgumentValidator
        if 'min_length' in validation_rules and isinstance(value, str):
            if len(value) < validation_rules['min_length']:
                raise ValidationError(f"Option '{self.option.name}' must be at least {validation_rules['min_length']} characters")
        
        if 'max_length' in validation_rules and isinstance(value, str):
            if len(value) > validation_rules['max_length']:
                raise ValidationError(f"Option '{self.option.name}' must be no more than {validation_rules['max_length']} characters")
        
        if 'min_value' in validation_rules and isinstance(value, (int, float)):
            if value < validation_rules['min_value']:
                raise ValidationError(f"Option '{self.option.name}' must be at least {validation_rules['min_value']}")
        
        if 'max_value' in validation_rules and isinstance(value, (int, float)):
            if value > validation_rules['max_value']:
                raise ValidationError(f"Option '{self.option.name}' must be no more than {validation_rules['max_value']}")
        
        if 'pattern' in validation_rules and isinstance(value, str):
            pattern = validation_rules['pattern']
            if not re.match(pattern, value):
                error_msg = validation_rules.get('pattern_error', f"Option '{self.option.name}' format is invalid")
                raise ValidationError(error_msg)
        
        if 'custom' in validation_rules:
            custom_validator = validation_rules['custom']
            if callable(custom_validator):
                try:
                    value = custom_validator(value, context)
                except Exception as e:
                    raise ValidationError(f"Option '{self.option.name}' validation failed: {e}")
        
        return value


class ValidationEngine:
    """
    Central validation engine for commands.
    
    Orchestrates validation of all arguments and options for a command.
    """
    
    def __init__(self):
        """Initialize validation engine."""
        self._argument_validators = {}
        self._option_validators = {}
    
    def register_argument_validator(self, arg_name: str, validator: ArgumentValidator) -> None:
        """Register an argument validator."""
        self._argument_validators[arg_name] = validator
    
    def register_option_validator(self, opt_name: str, validator: OptionValidator) -> None:
        """Register an option validator."""
        self._option_validators[opt_name] = validator
    
    def validate_arguments(self, arguments: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Validate all command arguments.
        
        Args:
            arguments: Dictionary of argument name -> value
            context: Additional validation context
            
        Returns:
            Dictionary of validated arguments
            
        Raises:
            ValidationError: If any argument validation fails
        """
        context = context or {}
        validated = {}
        
        for arg_name, value in arguments.items():
            validator = self._argument_validators.get(arg_name)
            if validator:
                try:
                    validated[arg_name] = validator.validate(value, context)
                except ValidationError as e:
                    raise ValidationError(f"Argument validation failed: {e}")
            else:
                # No validator registered, pass through
                validated[arg_name] = value
        
        return validated
    
    def validate_options(self, options: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Validate all command options.
        
        Args:
            options: Dictionary of option name -> value
            context: Additional validation context
            
        Returns:
            Dictionary of validated options
            
        Raises:
            ValidationError: If any option validation fails
        """
        context = context or {}
        validated = {}
        
        for opt_name, value in options.items():
            validator = self._option_validators.get(opt_name)
            if validator:
                try:
                    validated[opt_name] = validator.validate(value, context)
                except ValidationError as e:
                    raise ValidationError(f"Option validation failed: {e}")
            else:
                # No validator registered, pass through
                validated[opt_name] = value
        
        return validated
    
    def validate_command(self, arguments: Dict[str, Any], options: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Validate complete command input (arguments + options).
        
        Args:
            arguments: Dictionary of argument name -> value
            options: Dictionary of option name -> value
            context: Additional validation context
            
        Returns:
            Dictionary with 'arguments' and 'options' keys containing validated values
            
        Raises:
            ValidationError: If any validation fails
        """
        return {
            'arguments': self.validate_arguments(arguments, context),
            'options': self.validate_options(options, context)
        }