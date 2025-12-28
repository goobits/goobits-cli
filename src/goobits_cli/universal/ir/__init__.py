"""
Intermediate Representation (IR) module for Universal Template System.

This module provides the IR building functionality that converts Goobits
configuration into a language-agnostic format for template rendering.

Components:
- models: Frozen dataclasses defining the IR schema
- builder: Transforms configuration into IR dictionaries
- feature_analyzer: Detects required features for optimization
"""

from .builder import IRBuilder
from .feature_analyzer import FeatureAnalyzer
from .models import (
    IR,
    IRCLI,
    IRArgument,
    IRCommand,
    IRMetadata,
    IROption,
    IRProject,
    create_ir_from_dict,
)

__all__ = [
    # Models (frozen dataclasses)
    "IR",
    "IRCLI",
    "IRCommand",
    "IROption",
    "IRArgument",
    "IRMetadata",
    "IRProject",
    "create_ir_from_dict",
    # Builder
    "IRBuilder",
    # Analyzer
    "FeatureAnalyzer",
]
