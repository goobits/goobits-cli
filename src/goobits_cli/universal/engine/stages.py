"""
Pipeline Stages for the Universal Template System.

This module provides pure functions for each stage of the generation pipeline:
    config → IR → artifacts → files

Each function is stateless and can be composed or tested independently.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

# Import from centralized utils to avoid duplication
from goobits_cli.utils.paths import is_e2e_test_path

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

    with open(config_path, encoding="utf-8") as f:
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


def normalize_config(config: Any) -> Any:
    """
    Normalize configuration to GoobitsConfigSchema.

    Handles conversion from legacy ConfigSchema format if needed.

    Args:
        config: Configuration in any supported format (dict, ConfigSchema, GoobitsConfigSchema)

    Returns:
        GoobitsConfigSchema instance
    """
    # Lazy imports to avoid circular dependencies
    from ...core.schemas import (
        ConfigSchema,
        DependenciesSchema,
        GoobitsConfigSchema,
        InstallationSchema,
        PythonConfigSchema,
        ValidationSchema,
    )

    # Already a GoobitsConfigSchema - return as-is
    if isinstance(config, GoobitsConfigSchema):
        return config

    # Convert from dict
    if isinstance(config, dict):
        return GoobitsConfigSchema(**config)

    # Convert from legacy ConfigSchema
    if isinstance(config, ConfigSchema):
        hooks_path = getattr(config, "hooks_path", None)
        return GoobitsConfigSchema(
            package_name=getattr(config, "package_name", config.cli.name),
            command_name=getattr(config, "command_name", config.cli.name),
            display_name=getattr(config, "display_name", config.cli.name),
            description=getattr(
                config,
                "description",
                config.cli.description or config.cli.tagline,
            ),
            cli=config.cli,
            python=PythonConfigSchema(),
            dependencies=DependenciesSchema(),
            installation=InstallationSchema(
                pypi_name=getattr(config, "package_name", config.cli.name)
            ),
            shell_integration=None,
            validation=ValidationSchema(),
            messages={},
            hooks_path=hooks_path,
        )

    # If it's a Pydantic model with model_dump, use that
    if hasattr(config, "model_dump"):
        return GoobitsConfigSchema(**config.model_dump())

    # Last resort: try direct conversion
    return GoobitsConfigSchema(**dict(config))


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


def apply_integrations(
    config: Any,
    language: str,
) -> Any:
    """
    Apply integration enhancements to configuration.

    Integrates:
    - Interactive mode support
    - Shell completion system
    - Plugin system

    Args:
        config: Configuration (dict or Pydantic model)
        language: Target language

    Returns:
        Enhanced configuration with integrations applied
    """
    from ...core.utils import _safe_to_dict

    # Convert to dict for integration functions
    config_dict = _safe_to_dict(config)

    try:
        from ..integrations.interactive import integrate_interactive_mode

        if integrate_interactive_mode:
            config_dict = integrate_interactive_mode(config_dict, language)
    except ImportError:
        pass  # Interactive mode not available

    try:
        from ..integrations.completion import integrate_completion_system

        if integrate_completion_system:
            config_dict = integrate_completion_system(config_dict, language)
    except ImportError:
        pass  # Completion system not available

    try:
        from ..integrations.plugins import integrate_plugin_system

        if integrate_plugin_system:
            config_dict = integrate_plugin_system(config_dict, language)
    except ImportError:
        pass  # Plugin system not available

    # Convert back to GoobitsConfigSchema
    from ...core.schemas import GoobitsConfigSchema

    return GoobitsConfigSchema(**config_dict)


def pipeline(
    config_path: Path,
    language: str,
    output_dir: Path,
    dry_run: bool = False,
    with_integrations: bool = True,
) -> List[Path]:
    """
    Execute the complete generation pipeline.

    Convenience function that chains all stages:
        config_path → parse → validate → integrate → build_ir → render → write

    Args:
        config_path: Path to goobits.yaml
        language: Target language
        output_dir: Output directory
        dry_run: If True, don't write files
        with_integrations: If True, apply completion/interactive/plugin integrations

    Returns:
        List of generated file paths
    """
    # Stage 1: Parse
    raw_config = parse_config(config_path)

    # Stage 2: Validate
    validated_config = validate_config(raw_config)

    # Stage 2.5: Apply integrations (optional)
    if with_integrations:
        validated_config = apply_integrations(validated_config, language)

    # Stage 3: Build IR
    ir = build_ir(validated_config, config_path.name)

    # Stage 4: Render
    artifacts = render(ir, language)

    # Stage 5: Write
    return write_artifacts(artifacts, output_dir, dry_run)


__all__ = [
    "is_e2e_test_path",
    "parse_config",
    "validate_config",
    "normalize_config",
    "apply_integrations",
    "build_ir",
    "build_frozen_ir",
    "render",
    "render_with_templates",
    "write_artifacts",
    "write_files",
    "pipeline",
]
