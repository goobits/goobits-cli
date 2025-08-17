#!/usr/bin/env python3
"""
Hook implementations for test CLI commands.
These hooks provide the actual business logic for generated CLI commands.
"""

def on_hello(name=None, loud=False):
    """Handle the hello command."""
    if name:
        greeting = f"Hello, {name}!"
    else:
        greeting = "Hello, World!"
    
    if loud:
        greeting = greeting.upper()
    
    print(greeting)
    return 0

def on_version():
    """Handle the version command."""
    print("Test CLI v0.1.0")
    return 0

def on_build(config_path=None, **kwargs):
    """Handle the build command."""
    print(f"Build command executed with config: {config_path}")
    print(f"Options: {kwargs}")
    return 0

def on_init(project_name=None, **kwargs):
    """Handle the init command."""
    print(f"Init command executed with project: {project_name}")
    print(f"Options: {kwargs}")
    return 0

def on_serve(directory=None, **kwargs):
    """Handle the serve command."""
    print(f"Serve command executed with directory: {directory}")
    print(f"Options: {kwargs}")
    return 0