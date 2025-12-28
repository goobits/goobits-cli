"""
JSON serialization utilities for the Universal Template System.
"""

import json
from typing import Any


def safe_json_dumps(obj: Any, **kwargs) -> str:
    """
    Safely serialize an object to JSON string.

    Handles special cases like Path objects and Pydantic models.

    Args:
        obj: Object to serialize
        **kwargs: Additional arguments to json.dumps

    Returns:
        JSON string
    """
    return json.dumps(obj, default=_json_default, **kwargs)


def _json_default(obj: Any) -> Any:
    """
    Default handler for json.dumps to handle non-serializable objects.

    Args:
        obj: Object that couldn't be serialized

    Returns:
        Serializable representation
    """
    # Handle Path objects
    if hasattr(obj, "__fspath__"):
        return str(obj)

    # Handle Pydantic models
    if hasattr(obj, "model_dump"):
        return obj.model_dump()

    # Handle objects with dict method
    if hasattr(obj, "__dict__"):
        return obj.__dict__

    # Fallback to string representation
    return str(obj)
