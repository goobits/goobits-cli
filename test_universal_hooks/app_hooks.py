"""
Hook implementations for testing CLI execution.
"""

def on_hello(name: str, greeting: str = "Hello", uppercase: bool = False, **kwargs):
    """Handle hello command execution."""
    message = f"{greeting} {name}!"
    if uppercase:
        message = message.upper()
    print(f"HOOK_EXECUTED: {message}")
    return {"status": "success", "message": message}