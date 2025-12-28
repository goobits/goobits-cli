"""Backward compatibility stub - RustGenerator has moved to generation.renderers.rust.

This module re-exports RustGenerator from its new location for backward compatibility.
New code should import from goobits_cli.generation.renderers.rust instead.
"""

from ..generation.renderers.rust import RustGenerator

__all__ = ["RustGenerator"]
