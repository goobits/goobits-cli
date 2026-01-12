"""Migrate command handler for goobits CLI."""

import typer


def migrate_command(
    path: str = typer.Argument(..., help="Path to YAML file or directory to migrate"),
    backup: bool = typer.Option(
        True, "--backup/--no-backup", help="Create backup files (.bak)"
    ),
    dry_run: bool = typer.Option(
        False, "--dry-run", help="Show changes without applying them"
    ),
    pattern: str = typer.Option(
        "*.yaml", "--pattern", help="File pattern for directory migration"
    ),
):
    """
    Migrate YAML configurations to current format.

    Applies any registered migrations to update configuration files.
    """
    from ..migrations import MIGRATIONS

    if not MIGRATIONS:
        typer.echo("No migrations registered. Your configuration is up to date.")
        raise typer.Exit(0)

    from .migration_tool import migrate_yaml

    try:
        from pathlib import Path

        migrate_yaml.callback(Path(path), backup, dry_run, pattern)
    except Exception as e:
        typer.echo(f"Migration failed: {e}", err=True)
        raise typer.Exit(1)
