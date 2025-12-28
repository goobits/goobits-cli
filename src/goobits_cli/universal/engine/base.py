"""
Abstract base class for language-specific renderers.

This module re-exports the LanguageRenderer interface from renderers/interface.py
for backward compatibility.

DEPRECATED: Import from goobits_cli.universal.renderers.interface instead.
"""

# Re-export LanguageRenderer from the canonical location
from ..renderers.interface import Artifact, LanguageRenderer

__all__ = ["LanguageRenderer", "Artifact"]
