"""
Execution Pipeline
=================

Hook execution pipeline extracted from hook_system.j2.
Provides safe hook execution with error handling and result processing.
"""

import sys
import traceback
import asyncio
from typing import Any, Callable, Dict, List, Optional, Union
from dataclasses import dataclass
from enum import Enum
from .discovery_engine import DiscoveryEngine


class ExecutionResult(Enum):
    """Hook execution results."""
    SUCCESS = "success"
    FAILURE = "failure"
    NOT_FOUND = "not_found"
    ERROR = "error"


@dataclass
class ExecutionContext:
    """Context for hook execution."""
    hook_name: str
    arguments: Dict[str, Any]
    options: Dict[str, Any]
    command_name: str
    language: str
    project_name: str = ""
    
    def get_all_params(self) -> Dict[str, Any]:
        """Get all parameters as a single dictionary."""
        params = self.arguments.copy()
        params.update(self.options)
        return params


@dataclass
class ExecutionReport:
    """Report of hook execution."""
    result: ExecutionResult
    return_value: Any = None
    error: Optional[Exception] = None
    execution_time: float = 0.0
    hook_found: bool = False
    
    @property
    def success(self) -> bool:
        """Check if execution was successful."""
        return self.result == ExecutionResult.SUCCESS
    
    @property
    def failed(self) -> bool:
        """Check if execution failed."""
        return self.result in (ExecutionResult.FAILURE, ExecutionResult.ERROR)


class HookNotFoundError(Exception):
    """Raised when a requested hook function is not found."""
    pass


class HookExecutionError(Exception):
    """Raised when a hook function execution fails."""
    pass


class ErrorHandler:
    """
    Error handling system extracted from hook_system.j2.
    
    Provides consistent error formatting and handling for hook execution.
    """
    
    def __init__(self, verbose: bool = False, exit_on_error: bool = False):
        """Initialize error handler."""
        self.verbose = verbose
        self.exit_on_error = exit_on_error
    
    def handle_hook_not_found(self, hook_name: str, context: ExecutionContext) -> ExecutionReport:
        """Handle hook not found error."""
        error = HookNotFoundError(f"Hook '{hook_name}' not found")
        
        if self.verbose:
            self._print_error("Hook Not Found", str(error))
        
        if self.exit_on_error:
            sys.exit(1)
        
        return ExecutionReport(
            result=ExecutionResult.NOT_FOUND,
            error=error,
            hook_found=False
        )
    
    def handle_execution_error(self, hook_name: str, error: Exception, context: ExecutionContext) -> ExecutionReport:
        """Handle hook execution error."""
        execution_error = HookExecutionError(f"Error executing hook '{hook_name}': {str(error)}")
        
        if self.verbose:
            self._print_error("Hook Execution Error", str(execution_error))
            self._print_traceback(error)
        
        if self.exit_on_error:
            sys.exit(1)
        
        return ExecutionReport(
            result=ExecutionResult.ERROR,
            error=execution_error,
            hook_found=True
        )
    
    def handle_return_value_error(self, hook_name: str, return_value: Any, context: ExecutionContext) -> ExecutionReport:
        """Handle invalid return value."""
        if return_value is None:
            # None is treated as success (0)
            return ExecutionReport(
                result=ExecutionResult.SUCCESS,
                return_value=0,
                hook_found=True
            )
        
        # For numeric return values, non-zero indicates failure
        if isinstance(return_value, int):
            result = ExecutionResult.SUCCESS if return_value == 0 else ExecutionResult.FAILURE
            return ExecutionReport(
                result=result,
                return_value=return_value,
                hook_found=True
            )
        
        # Other types are treated as success
        return ExecutionReport(
            result=ExecutionResult.SUCCESS,
            return_value=return_value,
            hook_found=True
        )
    
    def _print_error(self, error_type: str, message: str) -> None:
        """Print formatted error message."""
        print(f"❌ {error_type}: {message}", file=sys.stderr)
    
    def _print_traceback(self, error: Exception) -> None:
        """Print error traceback."""
        print("\nTraceback:", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)


class HookExecutor:
    """
    Hook execution system extracted from hook_system.j2.
    
    Handles safe execution of hook functions with proper error handling.
    """
    
    def __init__(self, language: str, error_handler: ErrorHandler = None):
        """Initialize hook executor."""
        self.language = language
        self.error_handler = error_handler or ErrorHandler()
    
    def execute_sync(self, hook_func: Callable, context: ExecutionContext) -> ExecutionReport:
        """
        Execute synchronous hook function.
        
        Args:
            hook_func: Hook function to execute
            context: Execution context
            
        Returns:
            Execution report
        """
        import time
        start_time = time.time()
        
        try:
            # Prepare arguments based on language
            args, kwargs = self._prepare_arguments(hook_func, context)
            
            # Execute hook
            return_value = hook_func(*args, **kwargs)
            
            execution_time = time.time() - start_time
            
            # Process return value
            report = self.error_handler.handle_return_value_error(
                context.hook_name, return_value, context
            )
            report.execution_time = execution_time
            
            return report
            
        except Exception as e:
            execution_time = time.time() - start_time
            report = self.error_handler.handle_execution_error(
                context.hook_name, e, context
            )
            report.execution_time = execution_time
            return report
    
    async def execute_async(self, hook_func: Callable, context: ExecutionContext) -> ExecutionReport:
        """
        Execute asynchronous hook function.
        
        Args:
            hook_func: Hook function to execute
            context: Execution context
            
        Returns:
            Execution report
        """
        import time
        start_time = time.time()
        
        try:
            # Prepare arguments based on language
            args, kwargs = self._prepare_arguments(hook_func, context)
            
            # Execute async hook
            if asyncio.iscoroutinefunction(hook_func):
                return_value = await hook_func(*args, **kwargs)
            else:
                # Fallback to sync execution
                return_value = hook_func(*args, **kwargs)
            
            execution_time = time.time() - start_time
            
            # Process return value
            report = self.error_handler.handle_return_value_error(
                context.hook_name, return_value, context
            )
            report.execution_time = execution_time
            
            return report
            
        except Exception as e:
            execution_time = time.time() - start_time
            report = self.error_handler.handle_execution_error(
                context.hook_name, e, context
            )
            report.execution_time = execution_time
            return report
    
    def _prepare_arguments(self, hook_func: Callable, context: ExecutionContext) -> tuple:
        """Prepare arguments for hook function based on language conventions."""
        if self.language == 'python':
            return self._prepare_python_arguments(hook_func, context)
        elif self.language in ('nodejs', 'typescript'):
            return self._prepare_js_arguments(hook_func, context)
        elif self.language == 'rust':
            return self._prepare_rust_arguments(hook_func, context)
        else:
            # Default: pass all parameters as keyword arguments
            return (), context.get_all_params()
    
    def _prepare_python_arguments(self, hook_func: Callable, context: ExecutionContext) -> tuple:
        """Prepare arguments for Python hook function."""
        import inspect
        
        try:
            sig = inspect.signature(hook_func)
            params = list(sig.parameters.keys())
            
            # If hook expects a single context parameter
            if len(params) == 1 and 'context' in params[0].lower():
                return (context,), {}
            
            # If hook expects separate arguments and options
            if len(params) >= 2:
                return (), {
                    **context.arguments,
                    **context.options
                }
            
            # Default: pass all as keyword arguments
            return (), context.get_all_params()
            
        except Exception:
            # Fallback to keyword arguments
            return (), context.get_all_params()
    
    def _prepare_js_arguments(self, hook_func: Callable, context: ExecutionContext) -> tuple:
        """Prepare arguments for JavaScript/TypeScript hook function."""
        # For JS/TS, typically pass arguments as array and options as object
        args = list(context.arguments.values())
        if context.options:
            args.append(context.options)
        
        return tuple(args), {}
    
    def _prepare_rust_arguments(self, hook_func: Callable, context: ExecutionContext) -> tuple:
        """Prepare arguments for Rust hook function."""
        # For Rust, typically pass a matches object or structured data
        # This would be implemented with proper Rust FFI integration
        return (context.get_all_params(),), {}


class ExecutionPipeline:
    """
    Hook execution pipeline extracted from hook_system.j2.
    
    Orchestrates the complete hook execution flow with discovery, validation, and execution.
    """
    
    def __init__(self, language: str, search_paths: List[str] = None, error_handler: ErrorHandler = None):
        """Initialize execution pipeline."""
        self.language = language
        self.discovery = DiscoveryEngine(language, search_paths)
        self.executor = HookExecutor(language, error_handler or ErrorHandler())
        self.error_handler = error_handler or ErrorHandler()
    
    def execute_hook(self, hook_name: str, context: ExecutionContext) -> ExecutionReport:
        """
        Execute a hook through the complete pipeline.
        
        Args:
            hook_name: Name of hook to execute
            context: Execution context
            
        Returns:
            Execution report
        """
        # Step 1: Discover hook function
        hook_func = self.discovery.find_hook(hook_name)
        
        if hook_func is None:
            return self.error_handler.handle_hook_not_found(hook_name, context)
        
        # Step 2: Validate hook signature (optional)
        # Could add signature validation here
        
        # Step 3: Execute hook
        if self.language in ('nodejs', 'typescript'):
            # For async languages, try async execution
            try:
                import asyncio
                if asyncio.iscoroutinefunction(hook_func):
                    return asyncio.run(self.executor.execute_async(hook_func, context))
                else:
                    return self.executor.execute_sync(hook_func, context)
            except Exception:
                return self.executor.execute_sync(hook_func, context)
        else:
            # For sync languages, use sync execution
            return self.executor.execute_sync(hook_func, context)
    
    def execute_command_hook(self, command_name: str, arguments: Dict[str, Any], options: Dict[str, Any], project_name: str = "") -> ExecutionReport:
        """
        Execute hook for a command.
        
        Args:
            command_name: Name of command
            arguments: Command arguments
            options: Command options
            project_name: Project name
            
        Returns:
            Execution report
        """
        hook_name = f"on_{command_name.replace('-', '_')}"
        
        context = ExecutionContext(
            hook_name=hook_name,
            arguments=arguments,
            options=options,
            command_name=command_name,
            language=self.language,
            project_name=project_name
        )
        
        return self.execute_hook(hook_name, context)
    
    def list_available_hooks(self) -> Dict[str, Dict[str, Any]]:
        """List all available hooks."""
        return self.discovery.list_available_hooks()
    
    def reload_hooks(self) -> None:
        """Reload all hook modules."""
        # Clear discovery cache
        self.discovery.loader.clear_cache()
    
    def validate_hooks(self, expected_hooks: List[str]) -> Dict[str, bool]:
        """
        Validate that expected hooks are available.
        
        Args:
            expected_hooks: List of expected hook names
            
        Returns:
            Dictionary mapping hook names to availability
        """
        available_hooks = self.discovery.discover_hooks()
        validation_results = {}
        
        for hook_name in expected_hooks:
            validation_results[hook_name] = hook_name in available_hooks
        
        return validation_results