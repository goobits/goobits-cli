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