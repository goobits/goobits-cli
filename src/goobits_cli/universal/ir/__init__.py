"""
Intermediate Representation (IR) module for Universal Template System.

This module provides the IR building functionality that converts Goobits
configuration into a language-agnostic format for template rendering.
"""

from .builder import IRBuilder
from .feature_analyzer import FeatureAnalyzer

__all__ = ["IRBuilder", "FeatureAnalyzer"]
