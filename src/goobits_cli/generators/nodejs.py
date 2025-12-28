"""Backward compatibility stub - NodeJSGenerator has moved to generation.renderers.nodejs.

This module re-exports NodeJSGenerator from its new location for backward compatibility.
New code should import from goobits_cli.generation.renderers.nodejs instead.
"""

from ..generation.renderers.nodejs import NodeJSGenerator

__all__ = ["NodeJSGenerator"]
