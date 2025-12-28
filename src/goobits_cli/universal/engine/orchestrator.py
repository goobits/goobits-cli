"""
Orchestrator for the Universal Template System.

This module provides the main entry point for CLI generation, coordinating
the pipeline stages while handling errors and logging.

The Orchestrator follows the Single Responsibility Principle:
- Coordinates stages (delegates to stages.py)
- Handles errors and provides user feedback
- Manages configuration and renderer selection

It does NOT:
- Implement business logic (that's in stages.py)
- Know about specific languages (that's in renderers/)
- Parse or validate config (that's in stages.py)
"""

from pathlib import Path
from typing import Any, Dict, List, Optional

from ...core.errors import (
    ConfigurationError,
    GeneratorError,
    RenderError,
    TemplateError,
)
from ..component_registry import ComponentRegistry
from ..renderers.interface import LanguageRenderer
from ..renderers.registry import get_default_registry, get_renderer
from . import stages


class Orchestrator:
    """
    Main orchestrator for CLI generation.

    Coordinates the generation pipeline:
        config → validate → IR → render → write

    Usage:
        orchestrator = Orchestrator()
        files = orchestrator.generate(
            config_path=Path("goobits.yaml"),
            language="python",
            output_dir=Path("./output"),
        )
    """

    def __init__(
        self,
        template_dir: Optional[Path] = None,
        test_mode: bool = False,
    ) -> None:
        """
        Initialize the orchestrator.

        Args:
            template_dir: Path to component templates directory
            test_mode: When True, disables caching for testing
        """
        self.template_dir = template_dir
        self.test_mode = test_mode
        self._component_registry: Optional[ComponentRegistry] = None

    @property
    def component_registry(self) -> ComponentRegistry:
        """Get or create the component registry."""
        if self._component_registry is None:
            self._component_registry = ComponentRegistry(self.template_dir)
            self._component_registry.load_components()
        return self._component_registry

    def generate(
        self,
        config_path: Path,
        language: str,
        output_dir: Path,
        consolidate: bool = False,
        dry_run: bool = False,
        with_integrations: bool = True,
    ) -> List[Path]:
        """
        Generate CLI implementation from configuration.

        This is the main entry point for CLI generation.

        Args:
            config_path: Path to goobits.yaml
            language: Target language (python, nodejs, typescript, rust)
            output_dir: Directory for generated files
            consolidate: Whether to consolidate into single file (Python only)
            dry_run: If True, don't write files
            with_integrations: If True, apply completion/interactive/plugin integrations

        Returns:
            List of generated file paths

        Raises:
            ConfigurationError: If configuration is invalid
            RenderError: If rendering fails
            GeneratorError: For other generation errors
        """
        try:
            # Stage 1: Parse configuration
            raw_config = stages.parse_config(config_path)
        except FileNotFoundError as e:
            raise ConfigurationError(f"Configuration file not found: {e}") from e
        except Exception as e:
            raise ConfigurationError(f"Failed to parse configuration: {e}") from e

        try:
            # Stage 2: Validate configuration
            validated_config = stages.validate_config(raw_config)
        except Exception as e:
            raise ConfigurationError(f"Configuration validation failed: {e}") from e

        try:
            # Stage 2.5: Apply integrations (completion, interactive, plugins)
            if with_integrations:
                validated_config = stages.apply_integrations(validated_config, language)
        except Exception:
            # Non-fatal: continue without integrations (they're optional enhancements)
            # Integration failures shouldn't block core CLI generation
            pass

        try:
            # Stage 3: Build intermediate representation
            ir = stages.build_ir(validated_config, config_path.name)
        except Exception as e:
            raise GeneratorError(f"Failed to build IR: {e}") from e

        try:
            # Stage 4: Get renderer and render
            renderer = get_renderer(language)

            # Use template-based rendering if component registry available
            rendered_files = stages.render_with_templates(
                ir, language, self.component_registry, renderer
            )
        except ValueError as e:
            raise RenderError(f"Renderer error: {e}") from e
        except Exception as e:
            raise RenderError(f"Rendering failed: {e}") from e

        try:
            # Stage 5: Write files
            return stages.write_files(rendered_files, output_dir, dry_run)
        except Exception as e:
            raise GeneratorError(f"Failed to write files: {e}") from e

    def generate_from_config(
        self,
        config: Any,
        language: str,
        output_dir: Path,
        config_filename: str = "goobits.yaml",
        dry_run: bool = False,
        with_integrations: bool = True,
    ) -> List[Path]:
        """
        Generate CLI from pre-loaded configuration.

        Useful when configuration is already parsed/validated.

        Args:
            config: Configuration dict or Pydantic model
            language: Target language
            output_dir: Directory for generated files
            config_filename: Original filename for metadata
            dry_run: If True, don't write files
            with_integrations: If True, apply completion/interactive/plugin integrations

        Returns:
            List of generated file paths
        """
        # Get rendered content first
        rendered_files = self.generate_content(
            config, language, config_filename, with_integrations
        )

        return stages.write_files(rendered_files, output_dir, dry_run)

    def generate_content(
        self,
        config: Any,
        language: str,
        config_filename: str = "goobits.yaml",
        with_integrations: bool = True,
    ) -> Dict[str, str]:
        """
        Generate CLI content from pre-loaded configuration without writing files.

        This is useful when the caller needs to handle file writing
        (e.g., for backup support, custom permissions).

        Args:
            config: Configuration dict or Pydantic model
            language: Target language
            config_filename: Original filename for metadata
            with_integrations: If True, apply completion/interactive/plugin integrations

        Returns:
            Dictionary mapping file paths to their content
        """
        try:
            # Normalize config to GoobitsConfigSchema if needed
            normalized_config = stages.normalize_config(config)
        except Exception as e:
            raise ConfigurationError(f"Failed to normalize config: {e}") from e

        try:
            # Apply integrations if requested (non-fatal, matches generate() behavior)
            if with_integrations:
                normalized_config = stages.apply_integrations(normalized_config, language)
        except Exception:
            # Non-fatal: continue without integrations (they're optional enhancements)
            pass

        try:
            ir = stages.build_ir(normalized_config, config_filename)
        except Exception as e:
            raise GeneratorError(f"Failed to build IR: {e}") from e

        try:
            rendered_files = stages.render_with_templates(
                ir, language, self.component_registry, get_renderer(language)
            )
        except Exception as e:
            raise RenderError(f"Rendering failed: {e}") from e

        return rendered_files

    def get_ir(
        self,
        config_path: Path,
    ) -> Dict[str, Any]:
        """
        Get the intermediate representation for a configuration.

        Useful for debugging or inspection.

        Args:
            config_path: Path to goobits.yaml

        Returns:
            Intermediate representation dictionary
        """
        raw_config = stages.parse_config(config_path)
        validated_config = stages.validate_config(raw_config)
        return stages.build_ir(validated_config, config_path.name)

    def available_languages(self) -> List[str]:
        """
        Get list of available target languages.

        Returns:
            List of language identifiers
        """
        return get_default_registry().available_languages()


def generate(
    config_path: Path,
    language: str,
    output_dir: Path,
    **kwargs,
) -> List[Path]:
    """
    Convenience function for one-shot generation.

    Args:
        config_path: Path to goobits.yaml
        language: Target language
        output_dir: Output directory
        **kwargs: Additional arguments passed to Orchestrator.generate

    Returns:
        List of generated file paths
    """
    orchestrator = Orchestrator()
    return orchestrator.generate(config_path, language, output_dir, **kwargs)


def generate_content(
    config: Any,
    language: str,
    config_filename: str = "goobits.yaml",
    **kwargs,
) -> Dict[str, str]:
    """
    Convenience function for one-shot content generation without writing files.

    Args:
        config: Configuration dict or Pydantic model
        language: Target language
        config_filename: Original filename for metadata
        **kwargs: Additional arguments passed to Orchestrator.generate_content

    Returns:
        Dictionary mapping file paths to their content
    """
    orchestrator = Orchestrator()
    return orchestrator.generate_content(config, language, config_filename, **kwargs)


__all__ = [
    "Orchestrator",
    "generate",
    "generate_content",
]
