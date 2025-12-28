"""
Universal Template System for Goobits CLI Framework.

This package provides a unified template system that can generate CLI implementations
for multiple programming languages from a common intermediate representation.

The primary entry point is the Orchestrator class, which coordinates the generation
pipeline using the registry-based renderer system.
"""

from .component_registry import ComponentRegistry

# Primary entry points (recommended)
from .engine.orchestrator import Orchestrator, generate, generate_content
from .generator import UniversalGenerator  # Thin wrapper for backward compat
from .ir.builder import IRBuilder
from .ir.feature_analyzer import FeatureAnalyzer
from .renderers.interface import Artifact, LanguageRenderer
from .renderers.registry import get_default_registry, get_renderer
from .utils import _safe_get_attr
from .utils.paths import ensure_directory, get_relative_path, normalize_path
from .utils.json import safe_json_dumps

# Legacy exports (deprecated, use Orchestrator instead)
from .template_engine import UniversalTemplateEngine

__all__ = [
    # Primary API
    "Orchestrator",
    "generate",
    "generate_content",
    "UniversalGenerator",
    "LanguageRenderer",
    "Artifact",
    "get_renderer",
    "get_default_registry",
    # Supporting classes
    "ComponentRegistry",
    "IRBuilder",
    "FeatureAnalyzer",
    # Utilities
    "_safe_get_attr",
    "normalize_path",
    "ensure_directory",
    "get_relative_path",
    "safe_json_dumps",
    # Deprecated (backward compat)
    "UniversalTemplateEngine",
]
