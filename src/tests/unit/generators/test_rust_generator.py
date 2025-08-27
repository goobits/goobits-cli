"""Comprehensive unit tests for RustGenerator module.

This module provides comprehensive tests for Rust CLI generation including:
- Basic generator functionality and initialization
- Clap framework integration specifics
- Rust type system handling and conversions
- Cargo ecosystem features and dependency management
- Rust-specific error handling patterns
- Rust naming and code conventions
- Edge cases specific to Rust generation

Merged from test_rust_generator.py and test_rust_specific_features.py
to eliminate duplicate coverage and provide unified testing.
"""

import pytest
from unittest.mock import Mock, patch
from pathlib import Path
import tempfile
import shutil
import threading
from functools import wraps

from goobits_cli.generators.rust import RustGenerator
from goobits_cli.generators import (
    ConfigurationError,
    TemplateError,
    ValidationError,
)
from goobits_cli.schemas import (
    ConfigSchema,
    CLISchema,
    CommandSchema,
    ArgumentSchema,
    OptionSchema,
)
from goobits_cli.main import load_goobits_config
from ...conftest import create_test_goobits_config, determine_language


# Timeout decorator for hanging tests
def timeout(seconds=30):
    """Decorator to add timeout to test methods to prevent hanging."""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = [None]
            exception = [None]

            def target():
                try:
                    result[0] = func(*args, **kwargs)
                except Exception as e:
                    exception[0] = e

            thread = threading.Thread(target=target)
            thread.daemon = True
            thread.start()
            thread.join(timeout=seconds)

            if thread.is_alive():
                pytest.fail(f"Test {func.__name__} timed out after {seconds} seconds")

            if exception[0]:
                raise exception[0]

            return result[0]

        return wrapper

    return decorator


class TestRustGenerator:
    """Test cases for RustGenerator class."""

    def test_generator_initialization_universal_templates(self):
        """Test RustGenerator initialization with universal templates enabled."""
        generator = RustGenerator()

        # Check that generator has required attributes
        assert hasattr(generator, "env")
        assert generator.env is not None
        # Template system is integrated

    def test_generator_initialization_template_system(self):
        """Test RustGenerator initialization with template system."""
        generator = RustGenerator()

        # Check that generator has required attributes
        assert hasattr(generator, "env")
        assert generator.env is not None
        # Template system is always integrated

    def test_template_loader_configuration(self):
        """Test that Jinja2 environment is properly configured."""
        generator = RustGenerator()

        # Check that environment has correct loader
        assert hasattr(generator.env, "loader")
        assert hasattr(generator.env, "filters")

        # Check custom filters are registered
        assert "to_rust_type" in generator.env.filters
        assert "to_snake_case" in generator.env.filters
        assert "to_screaming_snake_case" in generator.env.filters
        assert "to_pascal_case" in generator.env.filters
        assert "escape_rust_string" in generator.env.filters

