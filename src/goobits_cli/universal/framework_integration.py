"""
Framework Integration Module
=============================

This module integrates extracted frameworks into the Universal Template System.

Phase 1: Logging Framework Integration (completed)
Phase 3.1: Config Framework Integration (completed)
Phase 2.1: Interactive Framework Integration (completed)
Phase 1.2: Command Framework Integration (completed)
"""

from typing import Dict, Any, Optional


# Singleton instances of frameworks
_logging_framework_instance = None
_config_framework_instance = None
_interactive_framework_instance = None
_command_framework_instance = None
_builtin_framework_instance = None
_hook_framework_instance = None
_error_framework_instance = None
_completion_framework_instance = None
_repl_framework_instance = None
_progress_framework_instance = None
_setup_framework_instance = None


def get_logging_framework():
    """
    Get the singleton LoggingFramework instance for template use.
    
    This function is called from templates like:
    {%- set logging_framework = get_logging_framework() -%}
    
    Returns:
        LoggingFramework instance
    """
    global _logging_framework_instance
    
    if _logging_framework_instance is None:
        try:
            from ..logging import LoggingFramework
            _logging_framework_instance = LoggingFramework()
        except ImportError as e:
            raise ImportError(
                "LoggingFramework not available. "
                "Please ensure src/goobits_cli/logging is properly installed."
            ) from e
    
    return _logging_framework_instance


def get_config_framework():
    """
    Get the singleton ConfigFramework instance for template use.
    
    This function is called from templates like:
    {%- set config_framework = get_config_framework() -%}
    
    Returns:
        ConfigFramework instance
    """
    global _config_framework_instance
    
    if _config_framework_instance is None:
        try:
            from ..config import ConfigFramework
            _config_framework_instance = ConfigFramework()
        except ImportError as e:
            raise ImportError(
                "ConfigFramework not available. "
                "Please ensure src/goobits_cli/config is properly installed."
            ) from e
    
    return _config_framework_instance


def get_interactive_framework():
    """
    Get the singleton InteractiveFramework instance for template use.
    
    This function is called from templates like:
    {%- set interactive_framework = get_interactive_framework() -%}
    
    Returns:
        InteractiveFramework instance
    """
    global _interactive_framework_instance
    
    if _interactive_framework_instance is None:
        try:
            from ..interactive import InteractiveFramework
            _interactive_framework_instance = InteractiveFramework()
        except ImportError as e:
            raise ImportError(
                "InteractiveFramework not available. "
                "Please ensure src/goobits_cli/interactive is properly installed."
            ) from e
    
    return _interactive_framework_instance


def get_command_framework():
    """
    Get the singleton CommandFramework instance for template use.
    
    This function is called from templates like:
    {%- set command_framework = get_command_framework() -%}
    
    Returns:
        CommandFramework instance
    """
    global _command_framework_instance
    
    if _command_framework_instance is None:
        try:
            from ..commands import CommandFramework
            _command_framework_instance = CommandFramework()
        except ImportError as e:
            raise ImportError(
                "CommandFramework not available. "
                "Please ensure src/goobits_cli/commands is properly installed."
            ) from e
    
    return _command_framework_instance


def get_builtin_framework():
    """
    Get the singleton BuiltinFramework instance for template use.
    
    This function is called from templates like:
    {%- set builtin_framework = get_builtin_framework() -%}
    
    Returns:
        BuiltinFramework instance
    """
    global _builtin_framework_instance
    
    if _builtin_framework_instance is None:
        try:
            from ..builtins import BuiltinFramework
            _builtin_framework_instance = BuiltinFramework()
        except ImportError as e:
            raise ImportError(
                "BuiltinFramework not available. "
                "Please ensure src/goobits_cli/builtins is properly installed."
            ) from e
    
    return _builtin_framework_instance


def get_hook_framework():
    """
    Get the singleton HookFramework instance for template use.
    
    This function is called from templates like:
    {%- set hook_framework = get_hook_framework() -%}
    
    Returns:
        HookFramework instance
    """
    global _hook_framework_instance
    
    if _hook_framework_instance is None:
        try:
            from ..hooks import HookFramework
            _hook_framework_instance = HookFramework()
        except ImportError as e:
            raise ImportError(
                "HookFramework not available. "
                "Please ensure src/goobits_cli/hooks is properly installed."
            ) from e
    
    return _hook_framework_instance


def get_error_framework():
    """
    Get the singleton ErrorFramework instance for template use.
    
    This function is called from templates like:
    {%- set error_framework = get_error_framework() -%}
    
    Returns:
        ErrorFramework instance
    """
    global _error_framework_instance
    
    if _error_framework_instance is None:
        try:
            from ..errors import ErrorFramework
            _error_framework_instance = ErrorFramework()
        except ImportError as e:
            raise ImportError(
                "ErrorFramework not available. "
                "Please ensure src/goobits_cli/errors is properly installed."
            ) from e
    
    return _error_framework_instance


def get_completion_framework():
    """
    Get the singleton CompletionFramework instance for template use.
    
    This function is called from templates like:
    {%- set completion_framework = get_completion_framework() -%}
    
    Returns:
        CompletionFramework instance
    """
    global _completion_framework_instance
    
    if _completion_framework_instance is None:
        try:
            from ..completion import CompletionFramework
            _completion_framework_instance = CompletionFramework()
        except ImportError as e:
            raise ImportError(
                "CompletionFramework not available. "
                "Please ensure src/goobits_cli/completion is properly installed."
            ) from e
    
    return _completion_framework_instance


def get_repl_framework():
    """
    Get the singleton REPLFramework instance for template use.
    
    This function is called from templates like:
    {%- set repl_framework = get_repl_framework() -%}
    
    Returns:
        REPLFramework instance
    """
    global _repl_framework_instance
    
    if _repl_framework_instance is None:
        try:
            from ..repl import REPLFramework
            _repl_framework_instance = REPLFramework()
        except ImportError as e:
            raise ImportError(
                "REPLFramework not available. "
                "Please ensure src/goobits_cli/repl is properly installed."
            ) from e
    
    return _repl_framework_instance


def get_progress_framework():
    """
    Get the singleton ProgressFramework instance for template use.
    
    This function is called from templates like:
    {%- set progress_framework = get_progress_framework() -%}
    
    Returns:
        ProgressFramework instance
    """
    global _progress_framework_instance
    
    if _progress_framework_instance is None:
        try:
            from ..progress import ProgressFramework
            _progress_framework_instance = ProgressFramework()
        except ImportError as e:
            raise ImportError(
                "ProgressFramework not available. "
                "Please ensure src/goobits_cli/progress is properly installed."
            ) from e
    
    return _progress_framework_instance


def get_setup_framework():
    """
    Get the singleton SetupFramework instance for template use.
    
    This function is called from templates like:
    {%- set setup_framework = get_setup_framework() -%}
    
    Returns:
        SetupFramework instance
    """
    global _setup_framework_instance
    
    if _setup_framework_instance is None:
        try:
            from ..setup import SetupFramework
            _setup_framework_instance = SetupFramework()
        except ImportError as e:
            raise ImportError(
                "SetupFramework not available. "
                "Please ensure src/goobits_cli/setup is properly installed."
            ) from e
    
    return _setup_framework_instance


def register_framework_functions(environment):
    """
    Register framework functions in Jinja2 environment.
    
    This adds framework integration functions to the template environment
    so they can be called from templates.
    
    Args:
        environment: Jinja2 Environment instance
    """
    # Phase 1: Register logging framework (completed)
    environment.globals['get_logging_framework'] = get_logging_framework
    
    # Phase 3.1: Register config framework (completed)
    environment.globals['get_config_framework'] = get_config_framework
    
    # Phase 2.1: Register interactive framework (completed)
    environment.globals['get_interactive_framework'] = get_interactive_framework
    
    # Phase 1.2: Register command framework (completed)
    environment.globals['get_command_framework'] = get_command_framework
    
    # Phase 2.2: Register builtin framework (completed)
    environment.globals['get_builtin_framework'] = get_builtin_framework
    
    # Phase 2.3: Register hook framework (completed)
    environment.globals['get_hook_framework'] = get_hook_framework
    
    # Phase 3.2: Register error framework (completed)
    environment.globals['get_error_framework'] = get_error_framework
    
    # Phase 3.3: Register completion framework (completed)
    environment.globals['get_completion_framework'] = get_completion_framework
    
    # Phase 3.4: Register REPL framework (completed)
    environment.globals['get_repl_framework'] = get_repl_framework
    
    # Phase 3.5: Register progress framework (completed)
    environment.globals['get_progress_framework'] = get_progress_framework
    
    # Phase 3.6: Register setup framework (completed)
    environment.globals['get_setup_framework'] = get_setup_framework
    
    return environment


def create_framework_context(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create context dictionary with framework integration.
    
    This prepares the context that will be passed to templates,
    including references to extracted frameworks.
    
    Args:
        config: Raw configuration dictionary
        
    Returns:
        Enhanced context with framework references
    """
    context = config.copy()
    
    # Add framework references to context
    context['_frameworks'] = {
        'logging': get_logging_framework(),
        'config': get_config_framework(),
        'interactive': get_interactive_framework(),
        'commands': get_command_framework(),
        'builtins': get_builtin_framework(),
        'hooks': get_hook_framework(),
        'errors': get_error_framework(),
        'completion': get_completion_framework(),
        'repl': get_repl_framework(),
        'progress': get_progress_framework(),
        'setup': get_setup_framework(),
    }
    
    return context