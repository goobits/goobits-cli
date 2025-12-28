"""Validate command handler for goobits CLI."""

from pathlib import Path
from typing import Optional

import typer

from .utils import _lazy_imports, load_goobits_config


def validate_command(
    config_path: Optional[Path] = typer.Argument(
        None, help="Path to goobits.yaml file (defaults to ./goobits.yaml)"
    ),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Show detailed validation information"
    ),
):
    """
    Validate a goobits.yaml configuration file without generating any files.

    This command checks:
    - YAML syntax correctness
    - Required fields presence
    - Field type validation
    - Value constraints
    """
    _lazy_imports()

    # Determine config file path
    if config_path is None:
        config_path = Path.cwd() / "goobits.yaml"

    config_path = Path(config_path).resolve()

    if not config_path.exists():
        typer.echo(f"\u274c Configuration file '{config_path}' not found.", err=True)
        raise typer.Exit(1)

    typer.echo(f"\U0001f50d Validating: {config_path}")

    try:
        # Try to load and validate the configuration
        config = load_goobits_config(config_path)

        # If we get here, validation passed
        typer.echo("\u2705 Configuration is valid!")

        if verbose:
            typer.echo("\n\U0001f4cb Configuration Summary:")
            typer.echo(f"   Package: {config.package_name}")
            typer.echo(f"   Command: {config.command_name}")
            typer.echo(f"   Language: {getattr(config, 'language', 'python')}")

            if hasattr(config, "cli") and config.cli:
                typer.echo(f"   CLI Version: {config.cli.version}")
                if hasattr(config.cli, "commands") and config.cli.commands:
                    typer.echo(f"   Commands: {len(config.cli.commands)}")
                    for cmd_name in list(config.cli.commands.keys())[:5]:
                        typer.echo(f"      - {cmd_name}")
                    if len(config.cli.commands) > 5:
                        typer.echo(f"      ... and {len(config.cli.commands) - 5} more")

        typer.echo("\n\U0001f4a1 Ready to build! Run: goobits build")

    except Exception:
        # Errors are already formatted nicely by load_goobits_config
        # Just exit with error code (error message already printed)
        raise typer.Exit(1)
