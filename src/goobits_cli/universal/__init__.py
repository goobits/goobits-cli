"""
Universal Template System for Goobits CLI Framework

This package provides a unified template system that can generate CLI implementations
for multiple programming languages from a common intermediate representation.
"""

from .template_engine import (
    LanguageRenderer,
    ComponentRegistry,
    UniversalTemplateEngine,
)

__all__ = [
    "LanguageRenderer",
    "ComponentRegistry", 
    "UniversalTemplateEngine",
]