"""Serve command implementation for goobits CLI.

This module contains the serve command that starts a local PyPI-compatible
package index server for testing package dependencies.
"""

from pathlib import Path

import typer


def serve_command(
    directory: Path = typer.Argument(
        ..., help="Directory containing packages to serve."
    ),
    host: str = typer.Option("localhost", help="Host to bind the server to."),
    port: int = typer.Option(8080, help="Port to run the server on."),
):
    """
    Serve a local PyPI-compatible package index.

    This command starts a simple HTTP server that serves Python packages
    (.whl and .tar.gz files) in a PyPI-compatible format. This is useful
    for testing package dependencies in Docker environments.

    The server will automatically generate an index.html file listing all
    available packages and serve them at the specified host and port.

    Examples:
        goobits serve ./packages
        goobits serve /path/to/packages --host 0.0.0.0 --port 9000
    """
    # Import required utilities (avoiding circular imports)
    from ..main import _lazy_imports
    from ..logger import set_context, get_logger
    
    _lazy_imports()

    # Set up logging context for serve operation
    set_context(operation="serve", host=host, port=port)
    logger = get_logger(__name__)
    logger.info("Starting PyPI server")

    directory = Path(directory).resolve()

    # Add directory to context
    set_context(serve_directory=str(directory))

    if not directory.exists():
        logger.error(f"Serve directory does not exist: {directory}")
        typer.echo(f"Error: Directory '{directory}' does not exist.", err=True)
        raise typer.Exit(1)

    if not directory.is_dir():
        typer.echo(f"Error: '{directory}' is not a directory.", err=True)
        raise typer.Exit(1)

    typer.echo(f"Starting PyPI server at http://{host}:{port}")
    typer.echo(f"Serving packages from: {directory}")
    typer.echo()
    typer.echo("Press Ctrl+C to stop the server")
    typer.echo()

    try:
        # Import serve_packages function
        from ..pypi_server import serve_packages
        
        logger.info(f"Starting server on {host}:{port}")
        serve_packages(directory, host, port)

    except KeyboardInterrupt:
        logger.info("Server stopped by user")
        typer.echo("\n👋 Server stopped by user")

    except OSError as e:
        if e.errno == 48:  # Address already in use
            typer.echo(
                f"❌ Error: Port {port} is already in use. Try a different port with --port.",
                err=True,
            )
        else:
            typer.echo(f"❌ Error starting server: {e}", err=True)
        raise typer.Exit(1)

    except Exception as e:
        typer.echo(f"❌ Unexpected error: {e}", err=True)
        raise typer.Exit(1)