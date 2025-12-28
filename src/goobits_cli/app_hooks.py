#!/usr/bin/env python3

"""

App hooks for goobits-cli generated CLI.

This file contains the actual implementation for CLI commands.

"""


from pathlib import Path

from typing import Optional


def on_build(
    config_path: Optional[str],
    output_dir: Optional[str],
    output: Optional[str],
    backup: bool,
) -> None:
    """Hook for build command - delegate to main.py implementation."""

    try:
        # Try package import first (when installed)
        import goobits_cli.main as main  # type: ignore[import-untyped]
    except ImportError:
        # Fallback to relative import (development mode)
        from . import main  # type: ignore[import-untyped]

    # Convert string paths to Path objects if needed

    config_path_obj = Path(config_path) if config_path else None

    output_dir_obj = Path(output_dir) if output_dir else None

    # Call the actual build function

    try:

        main.build(config_path_obj, output_dir_obj, output, backup)

    except SystemExit:

        # Handle typer.Exit gracefully

        pass


def on_init(project_name: Optional[str], template: str, force: bool) -> None:
    """Hook for init command - delegate to main.py implementation."""

    try:
        # Try package import first (when installed)
        import goobits_cli.main as main  # type: ignore[import-untyped]
    except ImportError:
        # Fallback to relative import (development mode)
        from . import main  # type: ignore[import-untyped]

    try:

        main.init(project_name, template, force)

    except SystemExit:

        # Handle typer.Exit gracefully

        pass


def on_serve(directory: str, host: str, port: int) -> None:
    """Hook for serve command - delegate to main.py implementation."""

    try:
        # Try package import first (when installed)
        import goobits_cli.main as main  # type: ignore[import-untyped]
    except ImportError:
        # Fallback to relative import (development mode)
        from . import main  # type: ignore[import-untyped]

    directory_obj = Path(directory)

    try:

        main.serve(directory_obj, host, port)

    except SystemExit:

        # Handle typer.Exit gracefully

        pass


def on_validate(config_path: Optional[str] = None, verbose: bool = False) -> None:
    """Hook for validate command - delegate to main.py implementation."""

    try:
        # Try package import first (when installed)
        import goobits_cli.main as main  # type: ignore[import-untyped]
    except ImportError:
        # Fallback to relative import (development mode)
        from . import main  # type: ignore[import-untyped]

    config_path_obj = Path(config_path) if config_path else None

    try:

        main.validate(config_path_obj, verbose)

    except SystemExit:

        # Handle typer.Exit gracefully

        pass


def on_migrate(
    path: str, backup: bool = True, dry_run: bool = False, pattern: str = "*.yaml"
) -> None:
    """Hook for migrate command - delegate to main.py implementation."""

    try:
        # Try package import first (when installed)
        import goobits_cli.main as main  # type: ignore[import-untyped]
    except ImportError:
        # Fallback to relative import (development mode)
        from . import main  # type: ignore[import-untyped]

    try:

        main.migrate(path, backup, dry_run, pattern)

    except SystemExit:

        # Handle typer.Exit gracefully

        pass
