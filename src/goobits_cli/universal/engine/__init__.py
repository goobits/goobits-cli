"""
Engine module for Universal Template System.

This module provides the core engine components including the abstract
base class for language renderers.
"""

from .base import LanguageRenderer

__all__ = ["LanguageRenderer"]
