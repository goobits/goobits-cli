"""Validation framework for Goobits CLI.

Provides ValidationResult and ValidationMessage for tracking validation state.
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
    """A single validation message with context."""

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
    """Result of a validation operation.

    Example:
        result = ValidationResult()
        result.add_error("missing field", field_path="config.name")
        if not result.is_valid:
            print(result.get_summary())
    """

    messages: List[ValidationMessage] = field(default_factory=list)
    is_valid: bool = True
    validator_name: str = ""
    execution_time_ms: float = 0.0
    details: Dict[str, Any] = field(default_factory=dict)

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
        """Add a warning message."""
        self.messages.append(
            ValidationMessage(
                severity=ValidationSeverity.WARNING,
                message=message,
                field_path=field_path,
                suggestion=suggestion,
                **kwargs,
            )
        )

    def add_error(
        self,
        message: str,
        field_path: str = "",
        suggestion: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """Add an error message (sets is_valid=False)."""
        self.messages.append(
            ValidationMessage(
                severity=ValidationSeverity.ERROR,
                message=message,
                field_path=field_path,
                suggestion=suggestion,
                **kwargs,
            )
        )
        self.is_valid = False

    def add_critical(
        self,
        message: str,
        field_path: str = "",
        suggestion: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """Add a critical error message (sets is_valid=False)."""
        self.messages.append(
            ValidationMessage(
                severity=ValidationSeverity.CRITICAL,
                message=message,
                field_path=field_path,
                suggestion=suggestion,
                **kwargs,
            )
        )
        self.is_valid = False

    def merge(self, other: "ValidationResult") -> "ValidationResult":
        """Merge another validation result into this one."""
        self.messages.extend(other.messages)
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
        return len(self.get_errors()) > 0

    def summary_stats(self) -> Dict[str, int]:
        """Get summary statistics of validation messages."""
        stats = {severity.value: 0 for severity in ValidationSeverity}
        for message in self.messages:
            stats[message.severity.value] += 1
        return stats

    def get_summary(self) -> str:
        """Get a summary of the validation result."""
        errors = self.get_errors()
        warnings = self.get_warnings()

        if self.is_valid:
            summary = "Validation passed"
            if warnings:
                summary += f" ({len(warnings)} warnings)"
        else:
            summary = f"Validation failed ({len(errors)} errors"
            if warnings:
                summary += f", {len(warnings)} warnings"
            summary += ")"
        return summary
