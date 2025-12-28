"""Shared configuration utility functions for CLI generators.

This module provides common configuration manipulation functions used
across multiple language generators.
"""

from typing import Any, Dict


def to_dict(obj: Any) -> Dict[str, Any]:
    """Convert a Pydantic model or object to a dictionary.

    Handles both Pydantic v1 (dict()) and v2 (model_dump()) APIs.

    Args:
        obj: Object to convert (typically a Pydantic model)

    Returns:
        Dictionary representation of the object
    """
    if hasattr(obj, "model_dump"):
        return obj.model_dump()
    elif hasattr(obj, "dict"):
        return obj.dict()
    elif isinstance(obj, dict):
        return obj
    else:
        # Fallback for other types
        return dict(obj) if hasattr(obj, "__iter__") else {"value": obj}
