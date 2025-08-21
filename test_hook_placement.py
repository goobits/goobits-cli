#!/usr/bin/env python3
"""Test to verify hook file placement logic."""
from pathlib import Path

# Simulate the all_files dict from the test
all_files = {
    'src/e2e_test_python/cli.py': 'content',
    'pyproject.toml': 'content',
    'src/e2e_test_python/__init__.py': 'content'
}

# Test the logic from my fix
cli_dir = None
for filename in all_files.keys():
    print(f"Checking: {filename}")
    if filename.endswith('/cli.py'):
        print(f"  -> Found CLI file!")
        # Extract the directory part
        cli_dir = Path(filename).parent
        print(f"  -> CLI directory: {cli_dir}")
        break

if cli_dir:
    print(f"\nHook file would be placed at: {cli_dir}/app_hooks.py")
else:
    print("\nNo CLI directory found, would use root")