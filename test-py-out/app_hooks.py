#!/usr/bin/env python3
"""
Hook implementations for test-python-cli
This file contains the business logic for your CLI commands.
"""

def on_hello(**kwargs):
    """Hook function for 'hello' command"""
    print("Hello from Python CLI!")
    return True

def on_serve(**kwargs):
    """Hook function for 'serve' command"""
    print("Serving from Python CLI...")
    return True

def on_build_project(**kwargs):
    """Hook function for 'build project' command"""
    print("Building project with Python CLI...")
    return True