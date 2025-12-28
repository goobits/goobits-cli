"""
Pipeline Stages for the Universal Template System.

This module provides pure functions for each stage of the generation pipeline:
    config → IR → artifacts → files

Each function is stateless and can be composed or tested independently.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

from ..ir.builder import IRBuilder
from ..ir.models import IR, create_ir_from_dict
from ..renderers.interface import Artifact, LanguageRenderer
from ..renderers.registry import get_renderer


def parse_config(config_path: Path) -> Dict[str, Any]:
    """
    Parse a goobits.yaml configuration file.

    This is the first stage of the pipeline: file → raw config dict.

    Args:
        config_path: Path to the goobits.yaml file

    Returns:
        Parsed configuration as dictionary

    Raises:
        FileNotFoundError: If config file doesn't exist
        yaml.YAMLError: If config is not valid YAML
    """
    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    if config is None:
        config = {}

    return config


def validate_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate configuration against schema.

    Args:
        config: Raw configuration dictionary

    Returns:
        Validated configuration (may be a Pydantic model)

    Raises:
        ValidationError: If configuration is invalid
    """
    # Lazy import to avoid circular dependencies
    from ...core.schemas import GoobitsConfigSchema

    # Validate using Pydantic
    validated = GoobitsConfigSchema(**config)
    return validated


def build_ir(
    config: Any,
    config_filename: str = "goobits.yaml",
) -> Dict[str, Any]:
    """
    Build intermediate representation from configuration.

    This is the second stage: validated config → IR dict.

    Args:
        config: Validated configuration (dict or Pydantic model)
        config_filename: Source filename for metadata

    Returns:
        Intermediate representation as dictionary
    """
    builder = IRBuilder()
    return builder.build(config, config_filename)


def build_frozen_ir(
    config: Any,
    config_filename: str = "goobits.yaml",
) -> IR:
    """
    Build frozen (immutable) intermediate representation.

    Args:
        config: Validated configuration
        config_filename: Source filename for metadata

    Returns:
        Frozen IR dataclass instance
    """
    ir_dict = build_ir(config, config_filename)
    return create_ir_from_dict(ir_dict)


def render(
    ir: Dict[str, Any],
    language: str,
    renderer: Optional[LanguageRenderer] = None,
) -> List[Artifact]:
    """
    Render artifacts from intermediate representation.

    This is the third stage: IR → artifacts.

    Args:
        ir: Intermediate representation dictionary
        language: Target language
        renderer: Optional pre-configured renderer (uses registry if not provided)

    Returns:
        List of generated artifacts
    """
    if renderer is None:
        renderer = get_renderer(language)

    return renderer.render(ir)


def render_with_templates(
    ir: Dict[str, Any],
    language: str,
    component_registry,
    renderer: Optional[LanguageRenderer] = None,
) -> Dict[str, str]:
    """
    Render artifacts using the component template system.

    This is an extended render stage that uses Jinja2 templates.

    Args:
        ir: Intermediate representation dictionary
        language: Target language
        component_registry: ComponentRegistry instance
        renderer: Optional pre-configured renderer

    Returns:
        Dictionary mapping file paths to rendered content
    """
    if renderer is None:
        renderer = get_renderer(language)

    context = renderer.get_template_context(ir)
    output_structure = renderer.get_output_structure(ir)

    rendered_files = {}
    for component_name, output_path in output_structure.items():
        if component_registry.has_component(component_name):
            template_content = component_registry.get_component(component_name)
            rendered_content = renderer.render_component(
                component_name, template_content, context
            )
            rendered_files[output_path] = rendered_content

    return rendered_files


def write_artifacts(
    artifacts: List[Artifact],
    output_dir: Path,
    dry_run: bool = False,
) -> List[Path]:
    """
    Write artifacts to the filesystem.

    This is the fourth stage: artifacts → files.

    Args:
        artifacts: List of artifacts to write
        output_dir: Base directory for output
        dry_run: If True, don't actually write files

    Returns:
        List of written file paths
    """
    written_files = []

    for artifact in artifacts:
        file_path = output_dir / artifact.path

        if not dry_run:
            # Ensure parent directory exists
            file_path.parent.mkdir(parents=True, exist_ok=True)

            # Write the file
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(artifact.content)

        written_files.append(file_path)

    return written_files


def write_files(
    files: Dict[str, str],
    output_dir: Optional[Path] = None,
    dry_run: bool = False,
) -> List[Path]:
    """
    Write a dictionary of files to the filesystem.

    Alternative to write_artifacts for dict-based output.

    Args:
        files: Dictionary mapping file paths to content
        output_dir: Base directory (paths may be absolute)
        dry_run: If True, don't actually write files

    Returns:
        List of written file paths
    """
    written_files = []

    for file_path, content in files.items():
        path = Path(file_path)

        # If output_dir provided and path is relative, join them
        if output_dir and not path.is_absolute():
            path = output_dir / path

        if not dry_run:
            # Ensure parent directory exists
            path.parent.mkdir(parents=True, exist_ok=True)

            # Write the file
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)

        written_files.append(path)

    return written_files


def pipeline(
    config_path: Path,
    language: str,
    output_dir: Path,
    dry_run: bool = False,
) -> List[Path]:
    """
    Execute the complete generation pipeline.

    Convenience function that chains all stages:
        config_path → parse → validate → build_ir → render → write

    Args:
        config_path: Path to goobits.yaml
        language: Target language
        output_dir: Output directory
        dry_run: If True, don't write files

    Returns:
        List of generated file paths
    """
    # Stage 1: Parse
    raw_config = parse_config(config_path)

    # Stage 2: Validate
    validated_config = validate_config(raw_config)

    # Stage 3: Build IR
    ir = build_ir(validated_config, config_path.name)

    # Stage 4: Render
    artifacts = render(ir, language)

    # Stage 5: Write
    return write_artifacts(artifacts, output_dir, dry_run)


__all__ = [
    "parse_config",
    "validate_config",
    "build_ir",
    "build_frozen_ir",
    "render",
    "render_with_templates",
    "write_artifacts",
    "write_files",
    "pipeline",
]
