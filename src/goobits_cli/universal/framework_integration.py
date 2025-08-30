"""
Framework Integration Module
=============================

This module integrates extracted frameworks into the Universal Template System.

Phase 1: Logging Framework Integration (completed)
Phase 3.1: Config Framework Integration (current)
Phase 2: Command Framework Integration (future)
Phase 3: Interactive & Builtin Framework Integration (future)
"""

from typing import Dict, Any, Optional


# Singleton instances of frameworks
_logging_framework_instance = None
_config_framework_instance = None


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
    
    # Phase 3.1: Register config framework (current)
    environment.globals['get_config_framework'] = get_config_framework
    
    # Phase 2: Register command framework (future)
    # environment.globals['get_command_framework'] = get_command_framework
    
    # Phase 3: Register interactive framework (future)
    # environment.globals['get_interactive_framework'] = get_interactive_framework
    
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
        # 'commands': get_command_framework(),  # Phase 2
        # 'interactive': get_interactive_framework(),  # Phase 3
    }
    
    return context