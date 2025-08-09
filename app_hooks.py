"""Hook functions for test-cli"""

def on_hello(command_name, name=None, loud=False, **kwargs):
    """Hook for hello command"""
    if name:
        greeting = f"Hello, {name}!"
    else:
        greeting = "Hello, World!"
    
    if loud:
        greeting = greeting.upper()
    
    print(greeting)

def on_goodbye(command_name, name, **kwargs):
    """Hook for goodbye command"""
    print(f"Goodbye, {name}!")