"""Unified validation framework for Goobits CLI.

This package provides validation functionality including:
- ValidationResult: Unified result class for validation operations
- ValidationMessage: Rich validation message with metadata
- ValidationSeverity: Severity levels for validation messages
"""

from goobits_cli.validation.framework import (
    ValidationMessage,
    ValidationResult,
    ValidationSeverity,
)

__all__ = [
    "ValidationMessage",
    "ValidationResult",
    "ValidationSeverity",
]
