"""Hook implementations for test Python CLI."""

def on_hello(ctx, **kwargs):
    """Handle hello command."""
    print("Hello from Python CLI!")

def on_build(ctx, **kwargs):
    """Handle build command."""  
    print("Build command executed!")

def on_project(ctx, **kwargs):
    """Handle build project subcommand."""
    print("Building project...")

def on_serve(ctx, **kwargs):
    """Handle serve command."""
    print("Starting server...")