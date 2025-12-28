"""Shared utility functions for goobits-cli.

This package provides common utilities used across multiple generators
to reduce code duplication and ensure consistent behavior.
"""

from .strings import (
    to_camel_case,
    to_pascal_case,
    to_kebab_case,
    to_snake_case,
    escape_javascript_string,
    json_stringify,
)
from .config import to_dict
from .paths import is_e2e_test_path

__all__ = [
    "to_camel_case",
    "to_pascal_case",
    "to_kebab_case",
    "to_snake_case",
    "escape_javascript_string",
    "json_stringify",
    "to_dict",
    "is_e2e_test_path",
]
