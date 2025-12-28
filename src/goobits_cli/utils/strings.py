"""Shared string utility functions for CLI generators.

This module provides common string manipulation functions used across
multiple language generators (Python, Node.js, TypeScript, Rust).

These functions were extracted from individual generators to reduce
code duplication and ensure consistent behavior.
"""

import json
import re
from typing import Any


def to_camel_case(text: str) -> str:
    """Convert snake_case, kebab-case, or PascalCase to camelCase.

    Args:
        text: Input text in any case format

    Returns:
        Text converted to camelCase

    Examples:
        >>> to_camel_case("hello_world")
        'helloWorld'
        >>> to_camel_case("hello-world")
        'helloWorld'
        >>> to_camel_case("HelloWorld")
        'helloWorld'
    """
    if not text:
        return text

    # Handle different separators: underscores, hyphens, spaces
    # Also handle PascalCase by inserting underscores before capitals
    # First, handle PascalCase by converting to snake_case
    # Insert underscore before each capital letter (except first)
    text = re.sub(r"(?<!^)(?=[A-Z])", "_", text)

    # Replace spaces and hyphens with underscores for consistent processing
    text = text.replace("-", "_").replace(" ", "_")

    # Split by underscores and handle the conversion
    parts = [part.lower() for part in text.split("_") if part]
    if len(parts) <= 1:
        return text.lower()

    # First part stays lowercase, subsequent parts are capitalized
    return parts[0] + "".join(part.capitalize() for part in parts[1:])


def to_pascal_case(text: str) -> str:
    """Convert snake_case, kebab-case, or camelCase to PascalCase.

    Args:
        text: Input text in any case format

    Returns:
        Text converted to PascalCase

    Examples:
        >>> to_pascal_case("hello_world")
        'HelloWorld'
        >>> to_pascal_case("hello-world")
        'HelloWorld'
        >>> to_pascal_case("helloWorld")
        'HelloWorld'
    """
    if not text:
        return text

    # Handle different separators: underscores, hyphens, spaces
    # First, handle existing camelCase/PascalCase by inserting underscores
    text = re.sub(r"(?<!^)(?=[A-Z])", "_", text)

    # Replace spaces and hyphens with underscores for consistent processing
    text = text.replace("-", "_").replace(" ", "_")

    # Split by underscores and capitalize each part
    parts = [part.lower() for part in text.split("_") if part]
    return "".join(part.capitalize() for part in parts)


def to_kebab_case(text: str) -> str:
    """Convert snake_case, camelCase, or PascalCase to kebab-case.

    Args:
        text: Input text in any case format

    Returns:
        Text converted to kebab-case

    Examples:
        >>> to_kebab_case("hello_world")
        'hello-world'
        >>> to_kebab_case("helloWorld")
        'hello-world'
        >>> to_kebab_case("HelloWorld")
        'hello-world'
    """
    if not text:
        return text

    # Handle different input formats
    # First, handle camelCase/PascalCase by inserting hyphens before capitals
    text = re.sub(r"(?<!^)(?=[A-Z])", "-", text)

    # Replace underscores and spaces with hyphens
    text = text.replace("_", "-").replace(" ", "-")

    # Convert to lowercase and clean up multiple consecutive hyphens
    return re.sub(r"-+", "-", text.lower()).strip("-")


def to_snake_case(text: str) -> str:
    """Convert text to snake_case.

    Properly handles camelCase, PascalCase, kebab-case, and space-separated text.

    Args:
        text: Input text in any case format

    Returns:
        Text converted to snake_case

    Examples:
        >>> to_snake_case("hello-world")
        'hello_world'
        >>> to_snake_case("helloWorld")
        'hello_world'
        >>> to_snake_case("Hello World")
        'hello_world'
        >>> to_snake_case("HTTPResponse")
        'http_response'
    """
    if not text:
        return text

    # Replace hyphens and spaces with underscores
    text = text.replace("-", "_").replace(" ", "_")

    # Insert underscores before uppercase letters (handles camelCase/PascalCase)
    s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", text)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()


def escape_javascript_string(value: str) -> str:
    """Escape string for JavaScript while preserving Unicode characters.

    Only escapes necessary characters for JavaScript string literals:
    - Backslashes (must be first to avoid double-escaping)
    - Quote characters that would break string literals
    - Control characters that would break JavaScript parsing

    Unicode characters (like Chinese, Arabic, emoji, etc.) are preserved as-is
    since JavaScript natively supports UTF-8.

    Args:
        value: String to escape

    Returns:
        Escaped string safe for JavaScript string literals
    """
    if not isinstance(value, str):
        return str(value)

    # Only escape characters that would break JavaScript syntax
    # Order matters: backslash first to avoid double-escaping
    escaped = value.replace("\\", "\\\\")  # Escape backslashes first
    escaped = escaped.replace('"', '\\"')  # Escape double quotes
    escaped = escaped.replace("'", "\\'")  # Escape single quotes
    escaped = escaped.replace("\n", "\\n")  # Escape newlines
    escaped = escaped.replace("\r", "\\r")  # Escape carriage returns
    escaped = escaped.replace("\t", "\\t")  # Escape tabs

    # Do NOT escape Unicode characters - they should be preserved
    return escaped


def json_stringify(obj: Any) -> str:
    """Convert to JSON, handling Pydantic models.

    Args:
        obj: Object to convert to JSON (can be a dict, Pydantic model, etc.)

    Returns:
        JSON string representation with 2-space indentation
    """
    if hasattr(obj, "model_dump"):
        return json.dumps(obj.model_dump(), indent=2)
    elif hasattr(obj, "dict"):
        return json.dumps(
            obj.model_dump() if hasattr(obj, "model_dump") else obj.dict(), indent=2
        )
    else:
        return json.dumps(obj, indent=2)
