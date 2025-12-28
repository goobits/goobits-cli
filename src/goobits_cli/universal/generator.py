"""
Universal Generator - Unified interface for all language generators.

This module provides a single generator class that wraps the Orchestrator
and provides the same interface as the legacy language-specific generators.

This is a backward-compatibility layer - new code should use the Orchestrator directly.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional

from .engine.orchestrator import Orchestrator
from .renderers.registry import get_default_registry


class UniversalGenerator:
    """
    Unified generator for all supported languages.

    Provides a consistent interface for CLI generation across all languages,
    replacing the legacy language-specific generator classes.

    Note: This class is a thin wrapper around the Orchestrator for backward
    compatibility. New code should use the Orchestrator directly.

    Usage:
        generator = UniversalGenerator("python")
        files = generator.generate_all_files(config, "goobits.yaml")
    """

    def __init__(self, language: str, consolidate: bool = True):
        """
        Initialize the universal generator for a specific language.

        Args:
            language: Target language (python, nodejs, typescript, rust)
            consolidate: Whether to consolidate output into single file (Python only)
        """
        self.language = language.lower()
        self.consolidate = consolidate

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

        This method provides the same interface as the legacy generators'
        generate_all_files() method.

        Args:
            config: The configuration object (GoobitsConfigSchema or dict)
            config_filename: Name of the configuration file
            version: Optional version string (unused, for compatibility)

        Returns:
            Dictionary mapping file paths to their contents
        """
        # Delegate to orchestrator's generate_content method
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

        This method provides compatibility with legacy generator.generate() calls.

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
            if "cli.py" in path or "cli.mjs" in path or "cli.ts" in path or "main.rs" in path:
                return content

        # Fallback: return first file content
        if files:
            return next(iter(files.values()))

        return ""


# Convenience factory functions for backward compatibility
def get_generator(language: str, consolidate: bool = True) -> UniversalGenerator:
    """
    Get a generator for the specified language.

    Args:
        language: Target language
        consolidate: Whether to consolidate output

    Returns:
        UniversalGenerator instance
    """
    return UniversalGenerator(language, consolidate)


# Backward-compatible generator classes
class PythonGenerator(UniversalGenerator):
    """Backward-compatible Python generator."""
    def __init__(self, consolidate: bool = True):
        super().__init__("python", consolidate)


class NodeJSGenerator(UniversalGenerator):
    """Backward-compatible Node.js generator."""
    def __init__(self):
        super().__init__("nodejs")


class TypeScriptGenerator(UniversalGenerator):
    """Backward-compatible TypeScript generator."""
    def __init__(self):
        super().__init__("typescript")


class RustGenerator(UniversalGenerator):
    """Backward-compatible Rust generator."""
    def __init__(self):
        super().__init__("rust")


__all__ = [
    "UniversalGenerator",
    "get_generator",
    "PythonGenerator",
    "NodeJSGenerator",
    "TypeScriptGenerator",
    "RustGenerator",
]
