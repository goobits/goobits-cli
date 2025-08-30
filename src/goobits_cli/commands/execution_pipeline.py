"""
Execution Pipeline
=================

Execution framework extracted from command_handler.j2 template.
Provides command execution pipeline with hook loading, error handling, and middleware support.
"""

import sys
import os
import importlib.util
import traceback
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Callable, Union
from dataclasses import dataclass
from pathlib import Path

from .command_framework import Command, CommandConfig
from .validation_engine import ValidationEngine, ValidationError


class ExecutionError(Exception):
    """Raised when command execution fails."""
    pass


class HookLoadError(Exception):
    """Raised when hook loading fails."""
    pass


@dataclass
class ExecutionContext:
    """Context passed to hooks and middleware."""
    command_name: str
    arguments: Dict[str, Any]
    options: Dict[str, Any]
    config: Dict[str, Any]
    project_root: Optional[Path] = None
    
    def get_arg(self, name: str, default: Any = None) -> Any:
        """Get argument value with optional default."""
        return self.arguments.get(name, default)
    
    def get_option(self, name: str, default: Any = None) -> Any:
        """Get option value with optional default."""
        return self.options.get(name, default)
    
    def has_arg(self, name: str) -> bool:
        """Check if argument exists."""
        return name in self.arguments
    
    def has_option(self, name: str) -> bool:
        """Check if option exists."""
        return name in self.options


class HookLoader:
    """
    Hook loading system extracted from command_handler.j2.
    
    Dynamically loads and executes hook functions from user-defined hook files.
    """
    
    def __init__(self, hook_file: str = ""):
        """Initialize hook loader."""
        self.hook_file = hook_file
        self._loaded_module = None
        self._hook_cache = {}
    
    def load_hooks(self, project_root: Optional[Path] = None) -> None:
        """
        Load hooks from the hook file.
        
        Args:
            project_root: Root directory to search for hook file
            
        Raises:
            HookLoadError: If hook file cannot be loaded
        """
        if not self.hook_file:
            return
        
        hook_path = self._find_hook_file(project_root)
        if not hook_path:
            raise HookLoadError(f"Hook file not found: {self.hook_file}")
        
        try:
            # Load module dynamically
            spec = importlib.util.spec_from_file_location("cli_hooks", hook_path)
            if not spec or not spec.loader:
                raise HookLoadError(f"Cannot create module spec for {hook_path}")
            
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            self._loaded_module = module
            self._cache_hooks()
            
        except Exception as e:
            raise HookLoadError(f"Failed to load hook file {hook_path}: {e}")
    
    def _find_hook_file(self, project_root: Optional[Path]) -> Optional[Path]:
        """Find the hook file in various locations."""
        search_paths = []
        
        if project_root:
            search_paths.extend([
                project_root / self.hook_file,
                project_root / "src" / self.hook_file,
                project_root / "hooks" / self.hook_file,
            ])
        
        # Also search in current directory
        search_paths.extend([
            Path(self.hook_file),
            Path("src") / self.hook_file,
            Path("hooks") / self.hook_file,
        ])
        
        for path in search_paths:
            if path.exists() and path.is_file():
                return path
        
        return None
    
    def _cache_hooks(self) -> None:
        """Cache available hook functions from loaded module."""
        if not self._loaded_module:
            return
        
        self._hook_cache.clear()
        
        for attr_name in dir(self._loaded_module):
            if attr_name.startswith('on_') and callable(getattr(self._loaded_module, attr_name)):
                self._hook_cache[attr_name] = getattr(self._loaded_module, attr_name)
    
    def has_hook(self, hook_name: str) -> bool:
        """Check if a hook function exists."""
        return hook_name in self._hook_cache
    
    def get_hook(self, hook_name: str) -> Optional[Callable]:
        """Get a hook function by name."""
        return self._hook_cache.get(hook_name)
    
    def execute_hook(self, hook_name: str, context: ExecutionContext) -> Any:
        """
        Execute a hook function with the given context.
        
        Args:
            hook_name: Name of the hook function to execute
            context: Execution context to pass to hook
            
        Returns:
            Return value from hook function
            
        Raises:
            ExecutionError: If hook execution fails
        """
        hook_func = self.get_hook(hook_name)
        if not hook_func:
            raise ExecutionError(f"Hook function '{hook_name}' not found")
        
        try:
            # Different calling conventions based on function signature
            import inspect
            sig = inspect.signature(hook_func)
            params = list(sig.parameters.keys())
            
            if len(params) == 1:
                # Single context parameter
                return hook_func(context)
            elif len(params) >= 2:
                # Legacy: separate args and options
                return hook_func(context.arguments, context.options)
            else:
                # No parameters
                return hook_func()
                
        except Exception as e:
            error_msg = f"Hook '{hook_name}' execution failed: {e}"
            error_msg += f"\n{traceback.format_exc()}"
            raise ExecutionError(error_msg)
    
    def get_available_hooks(self) -> List[str]:
        """Get list of available hook function names."""
        return list(self._hook_cache.keys())


class ErrorHandler:
    """
    Error handling system extracted from command_handler.j2.
    
    Provides consistent error formatting and handling across all languages.
    """
    
    def __init__(self, error_config: Dict[str, Any] = None):
        """Initialize error handler."""
        self.config = error_config or {}
        self.verbose = self.config.get('verbose', False)
        self.show_traceback = self.config.get('show_traceback', False)
        self.exit_on_error = self.config.get('exit_on_error', True)
    
    def handle_validation_error(self, error: ValidationError, command_name: str) -> None:
        """Handle validation errors."""
        self._print_error("Validation Error", str(error))
        
        if self.show_traceback:
            self._print_traceback(error)
        
        if self.exit_on_error:
            sys.exit(1)
    
    def handle_execution_error(self, error: ExecutionError, command_name: str) -> None:
        """Handle command execution errors."""
        self._print_error("Execution Error", str(error))
        
        if self.show_traceback:
            self._print_traceback(error)
        
        if self.exit_on_error:
            sys.exit(1)
    
    def handle_hook_load_error(self, error: HookLoadError, hook_file: str) -> None:
        """Handle hook loading errors."""
        self._print_error("Hook Load Error", str(error))
        
        if self.show_traceback:
            self._print_traceback(error)
        
        if self.exit_on_error:
            sys.exit(1)
    
    def handle_generic_error(self, error: Exception, context: str = "") -> None:
        """Handle generic errors."""
        error_msg = str(error)
        if context:
            error_msg = f"{context}: {error_msg}"
        
        self._print_error("Error", error_msg)
        
        if self.show_traceback or self.verbose:
            self._print_traceback(error)
        
        if self.exit_on_error:
            sys.exit(1)
    
    def _print_error(self, error_type: str, message: str) -> None:
        """Print formatted error message."""
        print(f"❌ {error_type}: {message}", file=sys.stderr)
    
    def _print_traceback(self, error: Exception) -> None:
        """Print error traceback."""
        print("\nTraceback:", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)


class ExecutionPipeline:
    """
    Command execution pipeline extracted from command_handler.j2.
    
    Orchestrates the complete command execution flow:
    1. Hook loading
    2. Input validation  
    3. Hook execution
    4. Error handling
    """
    
    def __init__(self, command_config: CommandConfig):
        """Initialize execution pipeline."""
        self.config = command_config
        self.hook_loader = HookLoader(command_config.hook_file)
        self.error_handler = ErrorHandler(command_config.error_handling)
        self.validation_engine = ValidationEngine()
        self._middleware = []
    
    def add_middleware(self, middleware: Callable[[ExecutionContext], ExecutionContext]) -> None:
        """Add middleware to the execution pipeline."""
        self._middleware.append(middleware)
    
    def execute_command(self, command_name: str, arguments: Dict[str, Any], options: Dict[str, Any], 
                       project_root: Optional[Path] = None) -> Any:
        """
        Execute a command through the complete pipeline.
        
        Args:
            command_name: Name of command to execute
            arguments: Command arguments
            options: Command options
            project_root: Project root directory
            
        Returns:
            Result from hook execution
            
        Raises:
            ExecutionError: If execution fails at any stage
        """
        try:
            # Step 1: Load hooks
            self._load_hooks_if_needed(project_root)
            
            # Step 2: Create execution context
            context = ExecutionContext(
                command_name=command_name,
                arguments=arguments,
                options=options,
                config=self.config.__dict__,
                project_root=project_root
            )
            
            # Step 3: Apply middleware
            for middleware in self._middleware:
                context = middleware(context)
            
            # Step 4: Validate inputs
            validated = self._validate_inputs(context)
            context.arguments = validated['arguments']
            context.options = validated['options']
            
            # Step 5: Execute hook
            hook_name = self._get_hook_name(command_name)
            result = self.hook_loader.execute_hook(hook_name, context)
            
            return result
            
        except ValidationError as e:
            self.error_handler.handle_validation_error(e, command_name)
            raise
            
        except HookLoadError as e:
            self.error_handler.handle_hook_load_error(e, self.config.hook_file)
            raise
            
        except ExecutionError as e:
            self.error_handler.handle_execution_error(e, command_name)
            raise
            
        except Exception as e:
            self.error_handler.handle_generic_error(e, f"Command '{command_name}' execution")
            raise ExecutionError(f"Unexpected error during command execution: {e}")
    
    def _load_hooks_if_needed(self, project_root: Optional[Path]) -> None:
        """Load hooks if not already loaded."""
        if not self.config.hook_file:
            return
        
        if self.hook_loader._loaded_module is None:
            self.hook_loader.load_hooks(project_root)
    
    def _validate_inputs(self, context: ExecutionContext) -> Dict[str, Any]:
        """Validate command arguments and options."""
        # For now, pass through - validation setup happens in command generation
        return {
            'arguments': context.arguments,
            'options': context.options
        }
    
    def _get_hook_name(self, command_name: str) -> str:
        """Convert command name to hook function name."""
        # Convert command name like 'build-project' to 'on_build_project'
        return f"on_{command_name.replace('-', '_')}"
    
    def get_command_help(self, command_name: str) -> Optional[str]:
        """Get help text for a command."""
        command = self.config.commands.get(command_name)
        if command:
            help_text = f"{command.description}\n"
            
            if command.arguments:
                help_text += "\nArguments:\n"
                for arg in command.arguments:
                    required_marker = " (required)" if arg.required else " (optional)"
                    help_text += f"  {arg.name}: {arg.description}{required_marker}\n"
            
            if command.options:
                help_text += "\nOptions:\n"
                for opt in command.options:
                    short_flag = f"-{opt.short}, " if opt.short else ""
                    default_text = f" (default: {opt.default})" if opt.default is not None else ""
                    help_text += f"  {short_flag}--{opt.name}: {opt.description}{default_text}\n"
            
            return help_text.strip()
        
        return None
    
    def list_available_commands(self) -> List[str]:
        """Get list of available commands."""
        return list(self.config.commands.keys())
    
    def list_available_hooks(self) -> List[str]:
        """Get list of available hook functions."""
        return self.hook_loader.get_available_hooks()