"""
Engine module for Universal Template System.

This module provides the core engine components for CLI generation:
- Orchestrator: Main entry point coordinating the pipeline
- Stages: Pure functions for each pipeline step
"""

from ..renderers.interface import LanguageRenderer
from .orchestrator import Orchestrator, generate
from .stages import (
    build_frozen_ir,
    build_ir,
    parse_config,
    pipeline,
    render,
    render_with_templates,
    validate_config,
    write_artifacts,
    write_files,
)

__all__ = [
    # Orchestrator
    "Orchestrator",
    "generate",
    # Stages
    "parse_config",
    "validate_config",
    "build_ir",
    "build_frozen_ir",
    "render",
    "render_with_templates",
    "write_artifacts",
    "write_files",
    "pipeline",
    # Re-export for convenience
    "LanguageRenderer",
]
