#!/usr/bin/env python3
"""
Hook implementations for Python CLI demo
"""
import platform
import sys

def on_greet(name, enthusiastic=False, **kwargs):
    """Handle greet command"""
    greeting = f"Hello, {name}"
    if enthusiastic:
        greeting += "!!!"
    else:
        greeting += "!"
    
    print(greeting)
    print(f"Welcome to the Python CLI demo, {name}!")
    return True

def on_info(**kwargs):
    """Handle info command"""
    print("🐍 Python CLI Information")
    print("-" * 30)
    print(f"Python Version: {sys.version}")
    print(f"Platform: {platform.platform()}")
    print(f"Architecture: {platform.architecture()[0]}")
    print(f"Processor: {platform.processor()}")
    return True