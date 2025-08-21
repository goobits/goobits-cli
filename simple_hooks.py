#!/usr/bin/env python3
"""
Simple hooks file for testing Universal Template System hook integration.
"""

def on_hello(name=None, loud=False):
    """Hook function for the hello command."""
    name = name or "World"
    greeting = f"Hello, {name}!"
    
    if loud:
        greeting = greeting.upper()
    
    print(greeting)
    return 0  # Return success