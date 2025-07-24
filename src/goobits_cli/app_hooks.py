#!/usr/bin/env python3
"""
App hooks for goobits-cli generated CLI.
This file contains the actual implementation for CLI commands.
"""

from pathlib import Path

def on_build(config_path, output_dir, output, backup):
    """Hook for build command - delegate to main.py implementation."""
    import goobits_cli.main as main
    
    # Convert string paths to Path objects if needed
    config_path_obj = Path(config_path) if config_path else None
    output_dir_obj = Path(output_dir) if output_dir else None
    
    # Call the actual build function
    try:
        main.build(config_path_obj, output_dir_obj, output, backup)
    except SystemExit:
        # Handle typer.Exit gracefully
        pass

def on_init(project_name, template, force):
    """Hook for init command - delegate to main.py implementation."""
    import goobits_cli.main as main
    
    try:
        main.init(project_name, template, force)
    except SystemExit:
        # Handle typer.Exit gracefully
        pass

def on_serve(directory, host, port):
    """Hook for serve command - delegate to main.py implementation."""
    import goobits_cli.main as main
    
    directory_obj = Path(directory)
    
    try:
        main.serve(directory_obj, host, port)
    except SystemExit:
        # Handle typer.Exit gracefully
        pass

def on_upgrade(source, version, pre, dry_run):
    """Hook for upgrade command - delegate to main.py implementation."""
    import goobits_cli.main as main
    
    try:
        main.upgrade(source, version, pre, dry_run)
    except SystemExit:
        # Handle typer.Exit gracefully
        pass