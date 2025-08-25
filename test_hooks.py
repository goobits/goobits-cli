"""Test hooks for REPL testing."""

def on_hello(name="World", uppercase=False):
    """Say hello with optional name and case conversion."""
    greeting = f"Hello, {name}!"
    if uppercase:
        greeting = greeting.upper()
    print(greeting)
    return greeting

def on_test(verbose=False):
    """Test command with optional verbose output."""
    if verbose:
        print("Running test command with verbose output enabled")
        print("This demonstrates multi-line command support")
    else:
        print("Test command executed")
    return "Test completed"