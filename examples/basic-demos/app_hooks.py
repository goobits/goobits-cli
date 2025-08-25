#!/usr/bin/env python3
"""
Hook implementations for Python CLI demo
"""
import platform
import sys

def on_greet(name, message="Hello", enthusiastic=False, **kwargs):
    """Handle greet command"""
    greeting = f"{message}, {name}"
    if enthusiastic:
        greeting += "!!!"
    else:
        greeting += "!"
    
    print(greeting)
    print(f"Welcome to the Python CLI demo, {name}!")
    return 0

def on_info(format="text", **kwargs):
    """Handle info command"""
    if format == "json":
        import json
        info = {
            "python_version": sys.version.split()[0],
            "platform": platform.platform(),
            "architecture": platform.architecture()[0],
            "processor": platform.processor()
        }
        print(json.dumps(info, indent=2))
    else:
        print("🐍 Python CLI Information")
        print("-" * 30)
        print(f"Python Version: {sys.version}")
        print(f"Platform: {platform.platform()}")
        print(f"Architecture: {platform.architecture()[0]}")
        print(f"Processor: {platform.processor()}")
    return 0