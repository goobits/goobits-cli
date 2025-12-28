"""Unified validation framework for Goobits CLI.

This module provides a unified ValidationResult class that consolidates
the functionality from both shared/components/validation_framework.py
and shared/test_utils/validation.py.

The unified class supports:
- Rich validation with ValidationMessage objects (from components)
- Simple string-based errors/warnings (from test_utils)
- Both `is_valid` and `passed` properties for backward compatibility
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class ValidationSeverity(Enum):
    """Severity levels for validation messages."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class ValidationMessage:
    """A single validation message with context.

    This class provides rich validation message support with metadata
    for location, suggestions, and contextual information.
    """

    severity: ValidationSeverity
    message: str
    field_path: str = ""
    suggestion: Optional[str] = None
    code: Optional[str] = None
    line_number: Optional[int] = None
    column: Optional[int] = None
    context: Dict[str, Any] = field(default_factory=dict)

    def __str__(self) -> str:
        prefix = {
            ValidationSeverity.INFO: "i",
            ValidationSeverity.WARNING: "!",
            ValidationSeverity.ERROR: "x",
            ValidationSeverity.CRITICAL: "X",
        }[self.severity]

        location = f" at {self.field_path}" if self.field_path else ""
        suggestion_text = (
            f"\n  Suggestion: {self.suggestion}" if self.suggestion else ""
        )
        return f"{prefix} {self.severity.value.upper()}{location}: {self.message}{suggestion_text}"


@dataclass
class ValidationResult:
    """Unified result of a validation operation.

    This class combines functionality from both the rich validation framework
    (with ValidationMessage objects) and the simple test utilities validation
    (with plain string errors/warnings).

    Supports two usage patterns:

    1. Rich validation (ValidationMessage objects):
        result = ValidationResult()
        result.add_error("error message", field_path="config.name")
        result.add_warning("warning message", suggestion="try this")

    2. Simple validation (string lists):
        result = ValidationResult(passed=True, errors=[], warnings=[], details={})
        result.add_error("simple error")
        result.add_warning("simple warning")

    Both patterns work seamlessly together.
    """

    # Rich validation fields (from validation_framework.py)
    messages: List[ValidationMessage] = field(default_factory=list)
    is_valid: bool = True
    validator_name: str = ""
    execution_time_ms: float = 0.0

    # Simple validation fields (from test_utils/validation.py)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    details: Dict[str, Any] = field(default_factory=dict)

    @property
    def passed(self) -> bool:
        """Alias for is_valid for backward compatibility with test_utils."""
        return self.is_valid

    @passed.setter
    def passed(self, value: bool) -> None:
        """Set passed status (alias for is_valid)."""
        self.is_valid = value

    def add_info(
        self,
        message: str,
        field_path: str = "",
        suggestion: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """Add an info message."""
        self.messages.append(
            ValidationMessage(
                severity=ValidationSeverity.INFO,
                message=message,
                field_path=field_path,
                suggestion=suggestion,
                **kwargs,
            )
        )

    def add_warning(
        self,
        message: str,
        field_path: str = "",
        suggestion: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """Add a warning message.

        Adds to both messages list (rich) and warnings list (simple)
        for backward compatibility.
        """
        self.messages.append(
            ValidationMessage(
                severity=ValidationSeverity.WARNING,
                message=message,
                field_path=field_path,
                suggestion=suggestion,
                **kwargs,
            )
        )
        # Also add to simple warnings list for backward compatibility
        self.warnings.append(message)

    def add_error(
        self,
        message: str,
        field_path: str = "",
        suggestion: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """Add an error message.

        Adds to both messages list (rich) and errors list (simple)
        for backward compatibility. Sets is_valid to False.
        """
        self.messages.append(
            ValidationMessage(
                severity=ValidationSeverity.ERROR,
                message=message,
                field_path=field_path,
                suggestion=suggestion,
                **kwargs,
            )
        )
        # Also add to simple errors list for backward compatibility
        self.errors.append(message)
        self.is_valid = False

    def add_critical(
        self,
        message: str,
        field_path: str = "",
        suggestion: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """Add a critical error message.

        Adds to both messages list (rich) and errors list (simple)
        for backward compatibility. Sets is_valid to False.
        """
        self.messages.append(
            ValidationMessage(
                severity=ValidationSeverity.CRITICAL,
                message=message,
                field_path=field_path,
                suggestion=suggestion,
                **kwargs,
            )
        )
        # Also add to simple errors list for backward compatibility
        self.errors.append(f"[CRITICAL] {message}")
        self.is_valid = False

    def merge(self, other: "ValidationResult") -> "ValidationResult":
        """Merge another validation result into this one."""
        self.messages.extend(other.messages)
        self.errors.extend(other.errors)
        self.warnings.extend(other.warnings)
        if not other.is_valid:
            self.is_valid = False
        return self

    def get_errors(self) -> List[ValidationMessage]:
        """Get all error and critical messages."""
        return [
            m
            for m in self.messages
            if m.severity in [ValidationSeverity.ERROR, ValidationSeverity.CRITICAL]
        ]

    def get_warnings(self) -> List[ValidationMessage]:
        """Get all warning messages."""
        return [m for m in self.messages if m.severity == ValidationSeverity.WARNING]

    def has_errors(self) -> bool:
        """Check if there are any error or critical messages."""
        return len(self.get_errors()) > 0 or len(self.errors) > 0

    def summary_stats(self) -> Dict[str, int]:
        """Get summary statistics of validation messages."""
        stats = {severity.value: 0 for severity in ValidationSeverity}
        for message in self.messages:
            stats[message.severity.value] += 1
        return stats

    def get_summary(self) -> str:
        """Get a summary of the validation result.

        From test_utils/validation.py for backward compatibility.
        """
        if self.is_valid:
            summary = "Validation passed"
            if self.warnings:
                summary += f" ({len(self.warnings)} warnings)"
        else:
            summary = f"Validation failed ({len(self.errors)} errors"
            if self.warnings:
                summary += f", {len(self.warnings)} warnings"
            summary += ")"
        return summary
