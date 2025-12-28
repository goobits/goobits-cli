"""

Universal Template System for Goobits CLI Framework

This package provides a unified template system that can generate CLI implementations

for multiple programming languages from a common intermediate representation.

"""

from .component_registry import ComponentRegistry

# Also expose new modular components for advanced usage
from .engine.base import LanguageRenderer as LanguageRendererBase
from .ir.builder import IRBuilder
from .ir.feature_analyzer import FeatureAnalyzer
from .template_engine import (
    LanguageRenderer,
    UniversalTemplateEngine,
)
from .utils import _safe_get_attr

__all__ = [
    "LanguageRenderer",
    "ComponentRegistry",
    "UniversalTemplateEngine",
    # New modular components
    "LanguageRendererBase",
    "IRBuilder",
    "FeatureAnalyzer",
    "_safe_get_attr",
]
