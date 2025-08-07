"""
Integration utilities for dynamic completion with interactive modes.

Provides helper functions and classes to integrate the completion system
with existing interactive modes across all supported languages.
"""

import asyncio
from typing import List, Dict, Any, Optional, Callable
from pathlib import Path

from .registry import get_completion_registry, CompletionContext
from .providers import setup_default_providers


class InteractiveCompletionIntegrator:
    """
    Integrates dynamic completion with interactive CLI modes.
    
    Provides seamless integration between the completion system and
    language-specific interactive modes (Python, Node.js, TypeScript, Rust).
    """
    
    def __init__(self, language: str = "python"):
        """Initialize the integrator for a specific language."""
        self.language = language
        self.registry = get_completion_registry()
        
        # Setup default providers if not already done
        self._setup_default_providers()
    
    def _setup_default_providers(self) -> None:
        """Setup default completion providers."""
        # Only setup if no providers are registered
        if not self.registry.get_providers():
            providers = setup_default_providers()
            for provider in providers:
                self.registry.register_provider(provider)
    
    async def get_completions_for_interactive(self, 
                                            current_input: str,
                                            cursor_position: int = None) -> List[str]:
        """
        Get completions for interactive mode input.
        
        Args:
            current_input: The current input line
            cursor_position: Position of cursor in input (default: end of input)
            
        Returns:
            List of completion suggestions
        """
        if cursor_position is None:
            cursor_position = len(current_input)
        
        # Extract the current word being completed
        before_cursor = current_input[:cursor_position]
        words = before_cursor.split()
        current_word = words[-1] if words and not before_cursor.endswith(' ') else ""
        
        # Get completions using the registry
        return await self.registry.get_completions(
            current_word=current_word,
            full_command=current_input,
            language=self.language
        )
    
    def create_completion_function(self) -> Callable[[str, int], List[str]]:
        """
        Create a completion function compatible with readline/prompt_toolkit.
        
        Returns:
            A completion function that can be used with interactive prompts
        """
        def completion_function(text: str, state: int) -> Optional[str]:
            """Completion function for readline interface."""
            if not hasattr(completion_function, '_completions'):
                # Get completions asynchronously
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    completions = loop.run_until_complete(
                        self.get_completions_for_interactive(text)
                    )
                    completion_function._completions = completions
                finally:
                    loop.close()
            
            completions = getattr(completion_function, '_completions', [])
            
            try:
                return completions[state]
            except IndexError:
                return None
        
        return completion_function
    
    async def setup_prompt_toolkit_completion(self):
        """Setup completion for prompt_toolkit (if available)."""
        try:
            from prompt_toolkit.completion import Completer, Completion
            
            class DynamicCompleter(Completer):
                def __init__(self, integrator: InteractiveCompletionIntegrator):
                    self.integrator = integrator
                
                def get_completions(self, document, complete_event):
                    # Get completions synchronously for prompt_toolkit
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    try:
                        completions = loop.run_until_complete(
                            self.integrator.get_completions_for_interactive(
                                document.current_line,
                                document.cursor_position
                            )
                        )
                        
                        for completion in completions:
                            yield Completion(completion)
                    finally:
                        loop.close()
            
            return DynamicCompleter(self)
            
        except ImportError:
            # prompt_toolkit not available
            return None


def setup_completion_for_language(language: str) -> InteractiveCompletionIntegrator:
    """
    Setup completion integration for a specific language.
    
    Args:
        language: Target language (python, nodejs, typescript, rust)
        
    Returns:
        Configured completion integrator
    """
    return InteractiveCompletionIntegrator(language)


def add_plugin_commands_to_context(context: CompletionContext) -> None:
    """
    Add plugin-provided commands to completion context.
    
    This function integrates with the plugin system to provide
    completions for dynamically loaded plugin commands.
    """
    try:
        from ..plugins import get_plugin_manager
        
        manager = get_plugin_manager()
        plugins = manager.list_plugins(status='enabled')
        
        for plugin in plugins:
            # Add plugin commands to available commands
            context.available_commands.update(plugin.provides_commands)
            
            # Add plugin-specific completion options
            if plugin.plugin_type.value == 'completion':
                context.metadata['plugin_completions'] = True
    
    except ImportError:
        # Plugin system not available
        pass


# Helper functions for specific interactive modes

def setup_python_interactive_completion() -> Optional[Callable]:
    """Setup completion for Python interactive mode."""
    integrator = setup_completion_for_language('python')
    return integrator.create_completion_function()


def setup_nodejs_interactive_completion() -> Dict[str, Any]:
    """Setup completion configuration for Node.js interactive mode."""
    integrator = setup_completion_for_language('nodejs')
    
    # Return configuration that can be used with Node.js readline
    return {
        'completer': integrator,
        'language': 'nodejs'
    }


def setup_typescript_interactive_completion() -> Dict[str, Any]:
    """Setup completion configuration for TypeScript interactive mode."""
    integrator = setup_completion_for_language('typescript')
    
    return {
        'completer': integrator, 
        'language': 'typescript'
    }


def setup_rust_interactive_completion() -> Dict[str, Any]:
    """Setup completion configuration for Rust interactive mode."""
    integrator = setup_completion_for_language('rust')
    
    return {
        'completer': integrator,
        'language': 'rust'
    }