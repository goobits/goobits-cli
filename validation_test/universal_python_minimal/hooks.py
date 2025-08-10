"""
Hook system interface for Minimal Test CLI

This module defines the interface between the generated CLI and user-defined hooks.
Users should implement hook functions in app_hooks.py to provide business logic.
"""

import importlib
import inspect
import sys
from typing import Any, Callable, Dict, Optional
from pathlib import Path

class HookManager:
    """Manages loading and execution of user-defined hooks."""

    def __init__(self, hooks_module_name: str = "app_hooks"):
        self.hooks_module_name = hooks_module_name
        self.hooks_module = None
        self.hooks_cache: Dict[str, Callable] = {}
        self.load_hooks()

    def load_hooks(self) -> None:
        """Load the hooks module."""
        try:
            # Try to import the hooks module
            self.hooks_module = importlib.import_module(self.hooks_module_name)

            # Cache all hook functions
            for name, obj in inspect.getmembers(self.hooks_module):
                if (inspect.isfunction(obj) and
                    name.startswith('on_') and
                    not name.startswith('_')):
                    self.hooks_cache[name] = obj

        except ImportError:
            # Hooks module doesn't exist yet
            self.hooks_module = None
            self.hooks_cache = {}

    def reload_hooks(self) -> None:
        """Reload the hooks module (useful for development)."""
        if self.hooks_module:
            importlib.reload(self.hooks_module)
        else:
            self.load_hooks()

    def has_hook(self, hook_name: str) -> bool:
        """Check if a hook function exists."""
        return hook_name in self.hooks_cache

    def execute_hook(self, hook_name: str, *args, **kwargs) -> Any:
        """
        Execute a hook function.

        Args:
            hook_name: Name of the hook function
            *args: Positional arguments to pass to the hook
            **kwargs: Keyword arguments to pass to the hook

        Returns:
            The return value of the hook function

        Raises:
            HookNotFoundError: If the hook doesn't exist
            Exception: Any exception raised by the hook
        """
        if not self.has_hook(hook_name):
            raise HookNotFoundError(f"Hook '{hook_name}' not found")

        hook_func = self.hooks_cache[hook_name]

        try:
            return hook_func(*args, **kwargs)
        except Exception as e:
            # Re-raise with additional context
            raise HookExecutionError(f"Error executing hook '{hook_name}': {str(e)}") from e

    def get_hook_signature(self, hook_name: str) -> Optional[inspect.Signature]:
        """Get the signature of a hook function."""
        if hook_name in self.hooks_cache:
            return inspect.signature(self.hooks_cache[hook_name])
        return None

    def list_hooks(self) -> Dict[str, str]:
        """
        List all available hooks with their docstrings.

        Returns:
            Dictionary mapping hook names to their docstrings
        """
        hooks_info = {}
        for name, func in self.hooks_cache.items():
            docstring = inspect.getdoc(func) or "No description available"
            hooks_info[name] = docstring
        return hooks_info

    def generate_hooks_template(self) -> str:
        """Generate a template hooks file for the user."""
        template = f'''"""
Hook implementations for Minimal Test CLI

This file contains the business logic for your CLI commands.
Implement the hook functions below to handle your CLI commands.

Each command in your CLI corresponds to a hook function named 'on_<command_name>'.
Command names with hyphens are converted to underscores.

Example:
- Command 'hello-world' -> Hook function 'on_hello_world'
- Command 'status' -> Hook function 'on_status'
"""

# Import any modules you need here
import sys
import os
def on_hello(name=None):
    """
    Say hello to someone

    Args:        name (str): Name to greet    """
    # TODO: Implement your business logic here
    print(f"Hook on_hello called")    print(f"Options:name={name}")
    # Return 0 for success, non-zero for error
    return 0
# Add any utility functions or classes here
'''
        return template

class HookNotFoundError(Exception):
    """Raised when a requested hook function is not found."""
    pass

class HookExecutionError(Exception):
    """Raised when a hook function execution fails."""
    pass

# Global hook manager instance
_hook_manager = None

def get_hook_manager() -> HookManager:
    """Get the global hook manager instance."""
    global _hook_manager
    if _hook_manager is None:
        _hook_manager = HookManager()
    return _hook_manager

def execute_hook(hook_name: str, *args, **kwargs) -> Any:
    """Convenience function to execute a hook."""
    return get_hook_manager().execute_hook(hook_name, *args, **kwargs)

def has_hook(hook_name: str) -> bool:
    """Convenience function to check if a hook exists."""
    return get_hook_manager().has_hook(hook_name)