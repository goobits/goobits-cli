"""
Universal Generator - Unified interface for all language generators.

This module provides a single generator class that wraps the Orchestrator
for convenient CLI generation across all supported languages.

Usage:
    generator = UniversalGenerator("python")
    files = generator.generate_all_files(config, "goobits.yaml")
"""

from typing import Any, Dict, Optional

from .engine.orchestrator import Orchestrator
from .renderers.registry import get_default_registry


class UniversalGenerator:
    """
    Unified generator for all supported languages.

    Provides a consistent interface for CLI generation across Python,
    Node.js, TypeScript, and Rust.

    Usage:
        generator = UniversalGenerator("python")
        files = generator.generate_all_files(config, "goobits.yaml")
    """

    def __init__(self, language: str):
        """
        Initialize the generator for a specific language.

        Args:
            language: Target language (python, nodejs, typescript, rust)
        """
        self.language = language.lower()

        # Validate language is supported via registry
        registry = get_default_registry()
        if not registry.has(self.language):
            available = registry.available_languages()
            raise ValueError(
                f"Unsupported language: {language}. "
                f"Supported: {available}"
            )

        # Initialize orchestrator for generation
        self._orchestrator = Orchestrator()

    def generate_all_files(
        self,
        config: Any,
        config_filename: str,
        version: Optional[str] = None,
    ) -> Dict[str, str]:
        """
        Generate all files for the CLI.

        Args:
            config: The configuration object (GoobitsConfigSchema or dict)
            config_filename: Name of the configuration file
            version: Optional version string (unused, kept for API compatibility)

        Returns:
            Dictionary mapping file paths to their contents
        """
        return self._orchestrator.generate_content(
            config=config,
            language=self.language,
            config_filename=config_filename,
        )

    def generate(
        self,
        config: Any,
        config_filename: str,
        version: Optional[str] = None,
    ) -> str:
        """
        Generate the main CLI file content.

        Args:
            config: The configuration object
            config_filename: Name of the configuration file
            version: Optional version string

        Returns:
            Generated CLI code as a string
        """
        files = self.generate_all_files(config, config_filename, version)

        # Return the main CLI file content
        for path, content in files.items():
            if "cli.py" in path or "cli.mjs" in path or "cli.ts" in path or "cli.rs" in path:
                return content

        # Fallback: return first file content
        if files:
            return next(iter(files.values()))

        return ""


__all__ = ["UniversalGenerator"]
