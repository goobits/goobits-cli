"""Shared utility functions for Goobits CLI Framework.

This module provides utility functions used throughout the framework,
centralized to avoid circular imports.
"""

from typing import Any, Dict


def safe_to_dict(obj: Any) -> Dict[str, Any]:
    """
    Safely convert a Pydantic model or dict to a plain dictionary.

    This handles the type conversion issues where objects might be:
    - Pydantic v2 models (with model_dump())
    - Pydantic v1 models (with dict())
    - Plain dictionaries already
    - None or other types

    Args:
        obj: Object to convert to dict

    Returns:
        Dictionary representation of the object
    """
    if obj is None:
        return {}

    # If it's already a dict, return it as-is
    if isinstance(obj, dict):
        return obj

    # Try Pydantic v2 model_dump() first
    if hasattr(obj, "model_dump") and callable(obj.model_dump):
        try:
            return obj.model_dump()
        except Exception:
            pass

    # Try Pydantic v1 dict() method
    if hasattr(obj, "dict") and callable(obj.dict):
        try:
            return obj.dict()
        except Exception:
            pass

    # If all else fails, try to convert using vars() or return empty dict
    try:
        if hasattr(obj, "__dict__"):
            return vars(obj)
    except Exception:
        pass

    # Last resort: return empty dict
    return {}



def safe_get_attr(obj: Any, attr: str, default: Any = None) -> Any:
    """
    Safely get an attribute from an object or dict.

    Args:
        obj: Object or dict to get attribute from
        attr: Attribute name
        default: Default value if attribute not found

    Returns:
        Attribute value or default
    """
    if obj is None:
        return default

    # Try dict access first
    if isinstance(obj, dict):
        return obj.get(attr, default)

    # Try attribute access
    return getattr(obj, attr, default)


__all__ = [
    "safe_to_dict",
    "safe_get_attr",
]
