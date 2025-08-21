#!/usr/bin/env python3
"""
Complex hooks file for testing edge cases in Universal Template System.
"""

def on_process(input_file=None, output_file=None, format=None, verbose=False, count=10, **kwargs):
    """Hook function for the process command with multiple arguments and options."""
    print(f"Processing: {input_file} -> {output_file}")
    print(f"Format: {format}, Count: {count}, Verbose: {verbose}")
    if kwargs:
        print(f"Additional args: {kwargs}")
    return 0

def on_analyze(data_path=None, recursive=False, exclude=None, **kwargs):
    """Hook function for the analyze command with complex options."""
    exclude = exclude or []
    print(f"Analyzing: {data_path}")
    print(f"Recursive: {recursive}")
    print(f"Exclude patterns: {exclude}")
    if kwargs:
        print(f"Additional args: {kwargs}")
    return 0