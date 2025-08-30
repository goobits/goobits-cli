"""
Config Framework for Goobits CLI Template System
==============================================

This package provides the configuration management framework extracted from
the config_manager.j2 template. It generates configuration management code
for all supported languages with consistent behavior.

Phase 3.1 of PROPOSAL_07_TEMPLATE_EXTRACTION_WITH_TESTING implementation.
"""

from .config_framework import ConfigFramework, ConfigSchema
from .language_adapters import (
    PythonConfigAdapter,
    NodeJSConfigAdapter,
    TypeScriptConfigAdapter,
    RustConfigAdapter
)

__all__ = [
    "ConfigFramework",
    "ConfigSchema",
    "PythonConfigAdapter",
    "NodeJSConfigAdapter", 
    "TypeScriptConfigAdapter",
    "RustConfigAdapter"
]