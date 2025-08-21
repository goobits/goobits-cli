#!/usr/bin/env python3
"""Debug the Click command registration issue."""

import sys
import click
from click.core import Command

# Monkey patch parse_args to see what's being passed
original_parse_args = Command.parse_args

def traced_parse_args(self, ctx, args):
    print(f"\n=== parse_args for command '{self.name}' ===")
    print(f"  Input args: {args}")
    print(f"  Context: {ctx}")
    print(f"  Context params before: {ctx.params if hasattr(ctx, 'params') else 'No params'}")
    
    try:
        result = original_parse_args(self, ctx, args)
        print(f"  Result: {result}")
        print(f"  Context params after: {ctx.params if hasattr(ctx, 'params') else 'No params'}")
        return result
    except Exception as e:
        print(f"  EXCEPTION: {e}")
        raise

Command.parse_args = traced_parse_args

# Import after patching
sys.path.insert(0, '/tmp/testcli2/src')
from testcli2.cli import main

# Test the command
print("=" * 60)
print("TESTING: hello World")
print("=" * 60)

try:
    main(['hello', 'World'], standalone_mode=False)
except click.UsageError as e:
    print(f"\nFinal UsageError: {e}")
except SystemExit as e:
    print(f"\nSystemExit: {e.code}")