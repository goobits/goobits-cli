"""Unit tests for validation framework primitives."""

from goobits_cli.validation.framework import (
    ValidationMessage,
    ValidationResult,
    ValidationSeverity,
)


def test_validation_message_str_includes_location_and_suggestion():
    message = ValidationMessage(
        severity=ValidationSeverity.ERROR,
        message="Invalid value",
        field_path="config.name",
        suggestion="Use a non-empty name",
    )

    rendered = str(message)
    assert "ERROR" in rendered
    assert "config.name" in rendered
    assert "Use a non-empty name" in rendered


def test_validation_result_add_error_and_critical_set_invalid():
    result = ValidationResult()
    assert result.is_valid

    result.add_error("Missing field", field_path="cli.name")
    assert not result.is_valid
    assert result.has_errors()

    result.add_critical("Broken config")
    errors = result.get_errors()
    assert len(errors) == 2


def test_validation_result_summary_stats_and_get_summary():
    result = ValidationResult()
    result.add_info("Info")
    result.add_warning("Warn")
    result.add_error("Err")

    stats = result.summary_stats()
    assert stats["info"] == 1
    assert stats["warning"] == 1
    assert stats["error"] == 1
    assert stats["critical"] == 0

    summary = result.get_summary()
    assert "Validation failed" in summary
    assert "1 errors" in summary
    assert "1 warnings" in summary


def test_validation_result_merge_combines_messages_and_validity():
    left = ValidationResult()
    right = ValidationResult()
    left.add_warning("left warning")
    right.add_error("right error")

    merged = left.merge(right)
    assert merged is left
    assert len(left.messages) == 2
    assert not left.is_valid
