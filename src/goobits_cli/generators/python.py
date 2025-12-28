"""Backward compatibility stub - PythonGenerator has moved to generation.renderers.python.

This module re-exports PythonGenerator from its new location for backward compatibility.
New code should import from goobits_cli.generation.renderers.python instead.
"""

from ..generation.renderers.python import PythonGenerator

__all__ = ["PythonGenerator"]
