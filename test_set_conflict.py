#!/usr/bin/env python3
"""Test if 'set' name conflicts with builtin."""

import sys
sys.path.insert(0, '/tmp/testcli2/src')

# Monkey patch to see what's being called
original_set = set

def traced_set(*args, **kwargs):
    import traceback
    print(f"\n!!! set() called with args={args}, kwargs={kwargs}")
    print("Traceback:")
    for line in traceback.format_stack()[-4:-1]:
        print(line.strip())
    
    # Check if this looks like a Click command invocation
    if len(args) == 1 and not kwargs:
        # Normal set() usage
        return original_set(*args)
    else:
        # Something else - maybe Click command?
        print("!!! This doesn't look like normal set() usage!")
        raise TypeError(f"traced_set got unexpected arguments: {args}, {kwargs}")

# Replace builtin set in the cli module
import testcli2.cli as cli_module
cli_module.set = traced_set

# Also need to update it in the hello function's globals
if hasattr(cli_module.hello.callback, '__globals__'):
    cli_module.hello.callback.__globals__['set'] = traced_set

# Now run the command
from click.testing import CliRunner
runner = CliRunner()

print("Running hello World command...")
result = runner.invoke(cli_module.main, ['hello', 'World'])
print(f"\nExit code: {result.exit_code}")
if result.exception:
    print(f"Exception: {result.exception}")