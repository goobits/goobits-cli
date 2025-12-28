"""
Base validation framework for Goobits CLI configurations.

This module provides the foundation for validating CLI configurations across
all supported languages (Python, Node.js, TypeScript, Rust).

NOTE: ValidationResult, ValidationMessage, and ValidationSeverity are now
imported from the unified goobits_cli.validation module. They are re-exported
here for backward compatibility.
"""

import re
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

# Import unified validation classes from the canonical location
from goobits_cli.validation import (
    ValidationResult,
)


class ValidationMode(Enum):
    """Validation modes for different use cases."""

    STRICT = "strict"  # All warnings become errors
    LENIENT = "lenient"  # Only critical errors fail validation
    DEV = "dev"  # Extra checks for development
    PRODUCTION = "production"  # Minimal checks for production


@dataclass
class ValidationContext:
    """Context passed to validators with configuration and metadata."""

    config: Any  # The configuration being validated
    language: str = "python"  # Target language
    mode: ValidationMode = ValidationMode.STRICT
    file_path: Optional[str] = None
    working_dir: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    # Cross-validator communication
    shared_data: Dict[str, Any] = field(default_factory=dict)

    def get_absolute_path(self, relative_path: str) -> str:
        """Convert relative path to absolute based on working directory."""
        if self.working_dir:
            return str(Path(self.working_dir) / relative_path)
        return relative_path

    def is_dev_mode(self) -> bool:
        """Check if validation is running in development mode."""
        return self.mode == ValidationMode.DEV

    def is_strict_mode(self) -> bool:
        """Check if validation is running in strict mode."""
        return self.mode == ValidationMode.STRICT


class BaseValidator(ABC):
    """Abstract base class for all validators.

    Validators should:
    1. Inherit from this class
    2. Implement the validate() method
    3. Return ValidationResult with appropriate messages
    4. Use the provided context for language-specific validation
    """

    def __init__(self, name: Optional[str] = None):
        self.name = name or self.__class__.__name__
        self.dependencies: Set[str] = set()  # Names of validators this depends on
        self.supported_languages: Set[str] = {"python", "nodejs", "typescript", "rust"}

    @abstractmethod
    def validate(self, context: ValidationContext) -> ValidationResult:
        """Validate configuration and return result.

        Args:
            context: Validation context with config and metadata

        Returns:
            ValidationResult with any validation messages
        """
        pass

    def can_validate(self, context: ValidationContext) -> bool:
        """Check if this validator can handle the given context."""
        return context.language in self.supported_languages

    def get_field_value(self, config: Any, field_path: str, default: Any = None) -> Any:
        """Safely get a nested field value from config."""
        try:
            current = config
            for part in field_path.split("."):
                if hasattr(current, part):
                    current = getattr(current, part)
                elif isinstance(current, dict) and part in current:
                    current = current[part]
                else:
                    return default
            return current
        except (AttributeError, KeyError, TypeError):
            return default

    def validate_identifier(
        self,
        name: str,
        field_path: str,
        result: ValidationResult,
        allow_hyphens: bool = True,
        language: str = "python",
    ) -> bool:
        """Validate that a name is a valid identifier for the target language.

        Args:
            name: The identifier to validate
            field_path: Path to the field being validated
            result: ValidationResult to add messages to
            allow_hyphens: Whether to allow hyphens (for CLI names)
            language: Target language for validation rules

        Returns:
            True if valid, False otherwise
        """
        if not name:
            result.add_error("Identifier cannot be empty", field_path)
            return False

        # Common rules across languages
        if not name[0].isalpha() and name[0] != "_":
            result.add_error(
                f"Identifier '{name}' must start with a letter or underscore",
                field_path,
                f"Try '{name.lstrip('0123456789-')}' or '_{name}'",
            )
            return False

        # Language-specific rules
        if language == "python":
            # Python identifiers: letters, numbers, underscores, and optionally hyphens for CLI names
            if allow_hyphens:
                valid_pattern = r"^[a-zA-Z_][a-zA-Z0-9_-]*$"
                invalid_chars_msg = (
                    "Use letters, numbers, underscores, and hyphens only"
                )
            else:
                valid_pattern = r"^[a-zA-Z_][a-zA-Z0-9_]*$"
                invalid_chars_msg = "Use letters, numbers, and underscores only"

            if not re.match(valid_pattern, name):
                result.add_error(
                    f"Python identifier '{name}' contains invalid characters",
                    field_path,
                    invalid_chars_msg,
                )
                return False
        elif language == "rust":
            # Rust allows underscores but not hyphens in identifiers
            if not allow_hyphens and "-" in name:
                result.add_error(
                    f"Rust identifier '{name}' cannot contain hyphens",
                    field_path,
                    f"Try '{name.replace('-', '_')}'",
                )
                return False
        elif language in ["nodejs", "typescript"]:
            # JavaScript/TypeScript identifiers
            valid_pattern = (
                r"^[a-zA-Z_$][a-zA-Z0-9_$]*$"
                if not allow_hyphens
                else r"^[a-zA-Z_$][a-zA-Z0-9_$-]*$"
            )
            if not re.match(valid_pattern, name):
                result.add_error(
                    f"JavaScript identifier '{name}' contains invalid characters",
                    field_path,
                    "Use letters, numbers, underscores, and $ only",
                )
                return False

        # Check for reserved words
        reserved_words = self._get_reserved_words(language)
        if name.lower() in reserved_words:
            result.add_error(
                f"'{name}' is a reserved word in {language}",
                field_path,
                f"Try '{name}_cmd' or 'my_{name}'",
            )
            return False

        return True

    def _get_reserved_words(self, language: str) -> Set[str]:
        """Get reserved words for a language."""
        reserved = {
            "python": {
                "and",
                "as",
                "assert",
                "break",
                "class",
                "continue",
                "def",
                "del",
                "elif",
                "else",
                "except",
                "exec",
                "finally",
                "for",
                "from",
                "global",
                "if",
                "import",
                "in",
                "is",
                "lambda",
                "not",
                "or",
                "pass",
                "print",
                "raise",
                "return",
                "try",
                "while",
                "with",
                "yield",
                "None",
                "True",
                "False",
            },
            "nodejs": {
                "abstract",
                "arguments",
                "boolean",
                "break",
                "byte",
                "case",
                "catch",
                "char",
                "class",
                "const",
                "continue",
                "debugger",
                "default",
                "delete",
                "do",
                "double",
                "else",
                "enum",
                "eval",
                "export",
                "extends",
                "false",
                "final",
                "finally",
                "float",
                "for",
                "function",
                "goto",
                "if",
                "implements",
                "import",
                "in",
                "instanceof",
                "int",
                "interface",
                "let",
                "long",
                "native",
                "new",
                "null",
                "package",
                "private",
                "protected",
                "public",
                "return",
                "short",
                "static",
                "super",
                "switch",
                "synchronized",
                "this",
                "throw",
                "throws",
                "transient",
                "true",
                "try",
                "typeof",
                "var",
                "void",
                "volatile",
                "while",
                "with",
                "yield",
            },
            "typescript": {
                # Include JavaScript keywords plus TypeScript-specific ones
                "abstract",
                "arguments",
                "boolean",
                "break",
                "byte",
                "case",
                "catch",
                "char",
                "class",
                "const",
                "continue",
                "debugger",
                "default",
                "delete",
                "do",
                "double",
                "else",
                "enum",
                "eval",
                "export",
                "extends",
                "false",
                "final",
                "finally",
                "float",
                "for",
                "function",
                "goto",
                "if",
                "implements",
                "import",
                "in",
                "instanceof",
                "int",
                "interface",
                "let",
                "long",
                "native",
                "new",
                "null",
                "package",
                "private",
                "protected",
                "public",
                "return",
                "short",
                "static",
                "super",
                "switch",
                "synchronized",
                "this",
                "throw",
                "throws",
                "transient",
                "true",
                "try",
                "typeof",
                "var",
                "void",
                "volatile",
                "while",
                "with",
                "yield",
                "any",
                "never",
                "unknown",
                "string",
                "number",
                "bigint",
                "symbol",
                "object",
            },
            "rust": {
                "as",
                "break",
                "const",
                "continue",
                "crate",
                "else",
                "enum",
                "extern",
                "false",
                "fn",
                "for",
                "if",
                "impl",
                "in",
                "let",
                "loop",
                "match",
                "mod",
                "move",
                "mut",
                "pub",
                "ref",
                "return",
                "self",
                "Self",
                "static",
                "struct",
                "super",
                "trait",
                "true",
                "type",
                "unsafe",
                "use",
                "where",
                "while",
                "async",
                "await",
                "dyn",
            },
        }
        return reserved.get(language, set())


class ValidationRegistry:
    """Registry for managing validators and their dependencies."""

    def __init__(self):
        self._validators: Dict[str, BaseValidator] = {}
        self._execution_order: List[str] = []

    def register(self, validator: BaseValidator) -> None:
        """Register a validator."""
        self._validators[validator.name] = validator
        self._compute_execution_order()

    def unregister(self, name: str) -> None:
        """Unregister a validator."""
        if name in self._validators:
            del self._validators[name]
            self._compute_execution_order()

    def get_validator(self, name: str) -> Optional[BaseValidator]:
        """Get a validator by name."""
        return self._validators.get(name)

    def list_validators(self) -> List[str]:
        """Get list of registered validator names in execution order."""
        return self._execution_order.copy()

    def _compute_execution_order(self) -> None:
        """Compute execution order based on dependencies using topological sort."""
        # Simple topological sort
        visited = set()
        temp_visited = set()
        order = []

        def visit(validator_name: str):
            if validator_name in temp_visited:
                raise ValueError(
                    f"Circular dependency detected involving {validator_name}"
                )
            if validator_name in visited:
                return

            temp_visited.add(validator_name)

            validator = self._validators.get(validator_name)
            if validator:
                for dep in validator.dependencies:
                    if dep in self._validators:
                        visit(dep)

            temp_visited.remove(validator_name)
            visited.add(validator_name)
            order.append(validator_name)

        for validator_name in self._validators.keys():
            if validator_name not in visited:
                visit(validator_name)

        self._execution_order = order


class ValidationRunner:
    """Runs validation across multiple validators with proper ordering."""

    def __init__(self, registry: Optional[ValidationRegistry] = None):
        self.registry = registry or ValidationRegistry()
        self._results_cache: Dict[str, ValidationResult] = {}

    def validate_all(self, context: ValidationContext) -> ValidationResult:
        """Run all registered validators and return combined result."""
        combined_result = ValidationResult(validator_name="ValidationRunner")

        for validator_name in self.registry.list_validators():
            validator = self.registry.get_validator(validator_name)
            if not validator or not validator.can_validate(context):
                continue

            try:
                import time

                start_time = time.perf_counter()
                result = validator.validate(context)
                end_time = time.perf_counter()

                result.validator_name = validator_name
                result.execution_time_ms = (end_time - start_time) * 1000

                combined_result.merge(result)
                self._results_cache[validator_name] = result

            except Exception as e:
                combined_result.add_critical(
                    f"Validator {validator_name} failed with exception: {str(e)}",
                    suggestion="Check validator implementation or configuration data",
                )

        return combined_result

    def validate_specific(
        self, validator_names: List[str], context: ValidationContext
    ) -> ValidationResult:
        """Run specific validators only."""
        combined_result = ValidationResult(validator_name="ValidationRunner")

        for validator_name in validator_names:
            validator = self.registry.get_validator(validator_name)
            if not validator:
                combined_result.add_error(f"Validator '{validator_name}' not found")
                continue

            if not validator.can_validate(context):
                combined_result.add_warning(
                    f"Validator '{validator_name}' cannot validate {context.language} configurations"
                )
                continue

            try:
                import time

                start_time = time.perf_counter()
                result = validator.validate(context)
                end_time = time.perf_counter()

                result.validator_name = validator_name
                result.execution_time_ms = (end_time - start_time) * 1000

                combined_result.merge(result)
                self._results_cache[validator_name] = result

            except Exception as e:
                combined_result.add_critical(
                    f"Validator {validator_name} failed with exception: {str(e)}",
                    suggestion="Check validator implementation or configuration data",
                )

        return combined_result

    def get_cached_result(self, validator_name: str) -> Optional[ValidationResult]:
        """Get cached result for a validator."""
        return self._results_cache.get(validator_name)

    def clear_cache(self) -> None:
        """Clear cached validation results."""
        self._results_cache.clear()


# Convenience functions for common validation patterns
def create_default_runner() -> ValidationRunner:
    """Create a validation runner with all default validators registered."""
    # This will be populated when individual validators are imported
    return ValidationRunner()


def validate_config(
    config: Any,
    language: str = "python",
    mode: ValidationMode = ValidationMode.STRICT,
    file_path: Optional[str] = None,
) -> ValidationResult:
    """Convenience function to validate a configuration with default validators."""
    runner = create_default_runner()
    context = ValidationContext(
        config=config, language=language, mode=mode, file_path=file_path
    )
    return runner.validate_all(context)
