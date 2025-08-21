#!/usr/bin/env python3
"""Verify that 'set' is shadowed by the Click command."""

# Simulate what happens in the generated module

import click

# First, set is the builtin
print(f"1. Initially, set is: {set}")
print(f"   Can create a set: {set([1, 2, 3])}")

# Create a Click group
@click.group()
def config():
    pass

# Now define a command named 'set'
@config.command()
@click.argument('key')
@click.argument('value')
def set(key, value):
    """Set a config value."""
    print(f"Setting {key}={value}")

# After defining the function 'set', what is it?
print(f"\n2. After defining 'def set()', set is: {set}")
print(f"   Type: {type(set)}")

# Try to use set() as the builtin
try:
    result = set(['a', 'b', 'c'])
    print(f"   Can still create a set: {result}")
except Exception as e:
    print(f"   ERROR trying to use set(): {e}")

# What if we're in a function defined after set?
def test_function():
    """Function defined after set."""
    print(f"\n3. Inside test_function, set is: {set}")
    try:
        result = set(['x', 'y'])
        print(f"   Created set: {result}")
    except Exception as e:
        print(f"   ERROR: {e}")

test_function()