"""Migrate command implementation for goobits CLI.

This module contains the migrate command that converts legacy array-based
YAML configurations to the new 3.0.0 standardized object format.
"""

from pathlib import Path

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
    Migrate YAML configurations to 3.0.0 format.

    Converts legacy array-based subcommands to standardized object format:

    BEFORE: subcommands: [{name: "start", ...}, {name: "stop", ...}]

    AFTER:  subcommands: {start: {...}, stop: {...}}

    This migration ensures compatibility with the new unlimited nested command system.
    """
    try:
        # Import migration tool
        from ..migration import migrate_yaml as migrate_tool
        
        # Convert path argument to Path object
        target_path = Path(path)

        # Call the migration tool with proper parameters
        migrate_tool.callback(target_path, backup, dry_run, pattern)

    except Exception as e:
        typer.echo(f"❌ Migration failed: {e}", err=True)
        raise typer.Exit(1)