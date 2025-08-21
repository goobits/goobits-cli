#!/usr/bin/env python3
"""
Broken hooks file for testing error handling.
"""

def on_process():  # Missing parameters - should cause signature mismatch
    """Hook function with incorrect signature."""
    print("This will fail")
    return 0