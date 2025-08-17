#!/usr/bin/env python3

"""

App hooks for goobits-cli generated CLI.

This file contains the actual implementation for CLI commands.

"""



from pathlib import Path

from typing import Optional



def on_build(config_path: Optional[str], output_dir: Optional[str], output: Optional[str], backup: bool, universal_templates: bool = True) -> None:

    """Hook for build command - delegate to main.py implementation."""

    import goobits_cli.main as main  # type: ignore[import-untyped]

    

    # Convert string paths to Path objects if needed

    config_path_obj = Path(config_path) if config_path else None

    output_dir_obj = Path(output_dir) if output_dir else None

    

    # Call the actual build function

    try:

        main.build(config_path_obj, output_dir_obj, output, backup, universal_templates)

    except SystemExit:

        # Handle typer.Exit gracefully

        pass



def on_init(project_name: Optional[str], template: str, force: bool) -> None:

    """Hook for init command - delegate to main.py implementation."""

    import goobits_cli.main as main  # type: ignore[import-untyped]

    

    try:

        main.init(project_name, template, force)

    except SystemExit:

        # Handle typer.Exit gracefully

        pass



def on_serve(directory: str, host: str, port: int) -> None:

    """Hook for serve command - delegate to main.py implementation."""

    import goobits_cli.main as main  # type: ignore[import-untyped]

    

    directory_obj = Path(directory)

    

    try:

        main.serve(directory_obj, host, port)

    except SystemExit:

        # Handle typer.Exit gracefully

        pass



