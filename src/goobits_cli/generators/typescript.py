"""Backward compatibility stub - TypeScriptGenerator has moved to generation.renderers.typescript.

This module re-exports TypeScriptGenerator from its new location for backward compatibility.
New code should import from goobits_cli.generation.renderers.typescript instead.
"""

from ..generation.renderers.typescript import TypeScriptGenerator

__all__ = ["TypeScriptGenerator"]
