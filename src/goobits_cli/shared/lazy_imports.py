"""Shared lazy import utilities for generator modules.

This module provides common lazy import patterns used across all generators
to reduce code duplication and maintain consistent import behavior.
"""

from typing import Dict, Any, Optional


class LazyImporter:
    """Manages lazy loading of heavy dependencies for generator modules."""
    
    def __init__(self):
        self._imports: Dict[str, Any] = {}
    
    def get_jinja2_environment(self):
        """Get Jinja2 Environment class with lazy loading."""
        if 'Environment' not in self._imports:
            from jinja2 import Environment
            self._imports['Environment'] = Environment
        return self._imports['Environment']
    
    def get_jinja2_dict_loader(self):
        """Get Jinja2 DictLoader class with lazy loading."""
        if 'DictLoader' not in self._imports:
            from jinja2 import DictLoader
            self._imports['DictLoader'] = DictLoader
        return self._imports['DictLoader']
    
    def get_jinja2_filesystem_loader(self):
        """Get Jinja2 FileSystemLoader class with lazy loading."""
        if 'FileSystemLoader' not in self._imports:
            from jinja2 import FileSystemLoader
            self._imports['FileSystemLoader'] = FileSystemLoader
        return self._imports['FileSystemLoader']
    
    def get_jinja2_template_not_found(self):
        """Get Jinja2 TemplateNotFound exception with lazy loading."""
        if 'TemplateNotFound' not in self._imports:
            from jinja2 import TemplateNotFound
            self._imports['TemplateNotFound'] = TemplateNotFound
        return self._imports['TemplateNotFound']
    
    def get_typer(self):
        """Get typer module with lazy loading."""
        if 'typer' not in self._imports:
            import typer
            self._imports['typer'] = typer
        return self._imports['typer']
    
    def get_yaml(self):
        """Get yaml module with lazy loading."""
        if 'yaml' not in self._imports:
            import yaml
            self._imports['yaml'] = yaml
        return self._imports['yaml']
    
    def get_toml(self):
        """Get toml module with lazy loading."""
        if 'toml' not in self._imports:
            import toml
            self._imports['toml'] = toml
        return self._imports['toml']
    
    def get_pydantic_validation_error(self):
        """Get Pydantic ValidationError with lazy loading."""
        if 'ValidationError' not in self._imports:
            from pydantic import ValidationError
            self._imports['ValidationError'] = ValidationError
        return self._imports['ValidationError']
    
    def get_deepcopy(self):
        """Get copy.deepcopy function with lazy loading."""
        if 'deepcopy' not in self._imports:
            from copy import deepcopy
            self._imports['deepcopy'] = deepcopy
        return self._imports['deepcopy']


# Global lazy importer instance for generators
_generator_importer = LazyImporter()


# Legacy-style functions for backward compatibility with existing _lazy_imports() pattern
def get_jinja2_imports() -> tuple:
    """Get common Jinja2 imports: (Environment, DictLoader, FileSystemLoader, TemplateNotFound)."""
    return (
        _generator_importer.get_jinja2_environment(),
        _generator_importer.get_jinja2_dict_loader(), 
        _generator_importer.get_jinja2_filesystem_loader(),
        _generator_importer.get_jinja2_template_not_found(),
    )


def get_typer_import():
    """Get typer module with lazy loading."""
    return _generator_importer.get_typer()


def get_common_generator_imports() -> Dict[str, Any]:
    """Get all common generator imports as a dictionary.
    
    Returns:
        Dictionary with keys: Environment, DictLoader, FileSystemLoader, 
        TemplateNotFound, typer
    """
    return {
        'Environment': _generator_importer.get_jinja2_environment(),
        'DictLoader': _generator_importer.get_jinja2_dict_loader(),
        'FileSystemLoader': _generator_importer.get_jinja2_filesystem_loader(),
        'TemplateNotFound': _generator_importer.get_jinja2_template_not_found(),
        'typer': _generator_importer.get_typer(),
    }


# Convenience functions matching existing patterns in generators
def lazy_import_jinja2_environment():
    """Lazy import Jinja2 Environment - matches existing generator pattern."""
    return _generator_importer.get_jinja2_environment()


def lazy_import_jinja2_dict_loader():
    """Lazy import Jinja2 DictLoader - matches existing generator pattern."""
    return _generator_importer.get_jinja2_dict_loader()


def lazy_import_jinja2_filesystem_loader():
    """Lazy import Jinja2 FileSystemLoader - matches existing generator pattern."""
    return _generator_importer.get_jinja2_filesystem_loader()


def lazy_import_jinja2_template_not_found():
    """Lazy import Jinja2 TemplateNotFound - matches existing generator pattern."""
    return _generator_importer.get_jinja2_template_not_found()


def lazy_import_typer():
    """Lazy import typer - matches existing generator pattern."""
    return _generator_importer.get_typer()


# Additional main.py specific lazy imports
def lazy_import_yaml():
    """Lazy import yaml module."""
    return _generator_importer.get_yaml()


def lazy_import_toml():
    """Lazy import toml module."""
    return _generator_importer.get_toml()


def lazy_import_pydantic_validation_error():
    """Lazy import Pydantic ValidationError."""
    return _generator_importer.get_pydantic_validation_error()


def lazy_import_deepcopy():
    """Lazy import copy.deepcopy function."""
    return _generator_importer.get_deepcopy()