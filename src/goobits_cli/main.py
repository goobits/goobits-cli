#!/usr/bin/env python3


# Fast version and help check to avoid heavy imports

import sys
import typer

if len(sys.argv) == 2:

    if sys.argv[1] in ["--version", "-V"]:

        from .__version__ import __version__

        typer.echo(f"goobits-cli {__version__}")

        sys.exit(0)


# Now import heavy dependencies only if needed

from pathlib import Path
from typing import Optional

import typer

# Import centralized logging
from .core.logging import setup_logging, set_context

from .__version__ import __version__  # noqa: E402


def version_callback(value: bool):

    if value:

        typer.echo(f"goobits-cli {__version__}")

        raise typer.Exit()


app = typer.Typer(name="goobits", help="Unified CLI for Goobits projects")


@app.callback()
def main(
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        callback=version_callback,
        is_eager=True,
        help="Show version and exit",
    )
):
    """Goobits CLI Framework - Build professional command-line tools with YAML configuration."""

    # Initialize centralized logging early
    setup_logging()

    # Set global context
    set_context(framework_version=__version__)

    pass


# Register commands from the commands module
# Import is done here to preserve lazy loading optimization
from .commands import (
    build_command,
    validate_command,
    init_command,
    upgrade_command,
    migrate_command,
)

# Re-export utility functions for backward compatibility with tests and external code
from .commands.utils import (
    load_goobits_config,
    normalize_dependencies_for_template,
    dependency_to_dict,
    dependencies_to_json,
    extract_version_from_pyproject,
    generate_setup_script,
    backup_file,
    update_pyproject_toml,
    DEFAULT_CACHE_TTL,
)

# Re-export template generation functions for backward compatibility
from .commands.init import (
    generate_basic_template,
    generate_advanced_template,
    generate_api_client_template,
    generate_text_processor_template,
)

# Register each command with its proper name
app.command(name="build")(build_command)
app.command(name="validate")(validate_command)
app.command(name="init")(init_command)
app.command(name="upgrade")(upgrade_command)
app.command(name="migrate")(migrate_command)


if __name__ == "__main__":

    app()
