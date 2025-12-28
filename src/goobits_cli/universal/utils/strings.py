"""
String and attribute manipulation utilities.
"""

from typing import Any


def _safe_get_attr(obj: Any, attr: str, default: Any = "") -> Any:
    """
    Safely get an attribute from an object or dict.

    This handles cases where the object might be:
    - A Pydantic model with attributes
    - A plain dictionary with keys
    - None or other types

    Args:
        obj: Object to get attribute from
        attr: Attribute name to get
        default: Default value if attribute not found

    Returns:
        Attribute value or default
    """
    if obj is None:
        return default

    # If it's a dictionary, use dict access
    if isinstance(obj, dict):
        return obj.get(attr, default)

    # If it's an object with attributes, use getattr
    if hasattr(obj, attr):
        return getattr(obj, attr, default)

    # If it's a dict-like object that doesn't respond to hasattr properly
    try:
        return obj[attr] if attr in obj else default
    except (TypeError, KeyError):
        pass

    return default
