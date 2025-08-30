"""
Unit tests for universal logger components in the Goobits CLI Framework.

This module tests the cross-language logger component generation that provides
consistent logging functionality across Python, Node.js, TypeScript, and Rust.
"""

import pytest
from pathlib import Path

from jinja2 import Template


# Test the universal logger template rendering
class TestUniversalLoggerTemplate:
    """Test universal logger template rendering across languages."""

    @pytest.fixture
    def logger_template(self):
        """Load the universal logger template with framework support."""
        import jinja2
        import sys
        
        # Add src to path to import the framework
        src_path = Path(__file__).parent.parent.parent.parent
        sys.path.insert(0, str(src_path))
        
        # Import the framework integration
        from goobits_cli.universal.framework_integration import register_framework_functions
        
        template_path = src_path / "goobits_cli/universal/components/logger.j2"
        
        # Create Jinja2 environment with framework functions
        env = jinja2.Environment(loader=jinja2.BaseLoader())
        register_framework_functions(env)
        
        with open(template_path, "r") as f:
            return env.from_string(f.read())

    def test_python_logger_generation(self, logger_template):
        """Test Python logger component generation."""
        context = {"language": "python", "project": {"name": "test-python-app"}}

        rendered = logger_template.render(**context)

        # Should be substantial content
        assert len(rendered) > 1000

        # Should contain Python-specific imports and functions
        assert "import logging" in rendered
        assert "import os" in rendered
        assert "import sys" in rendered
        assert "from contextvars import ContextVar" in rendered
        assert "def setup_logging()" in rendered
        # Note: Framework generates different function names
        assert "class StructuredFormatter" in rendered

        # Should contain context management functions
        assert "def add_context(" in rendered or "def set_context(" in rendered
        assert "def clear_context()" in rendered
        assert "def get_context()" in rendered

        # Should contain environment variable handling
        assert "LOG_LEVEL" in rendered
        assert "LOG_OUTPUT" in rendered
        assert "ENVIRONMENT" in rendered

    def test_nodejs_logger_generation(self, logger_template):
        """Test Node.js logger component generation."""
        context = {"language": "nodejs", "project": {"name": "test-nodejs-app"}}

        rendered = logger_template.render(**context)

        # Should be substantial content
        assert len(rendered) > 1000

        # Should contain Node.js-specific code
        assert "const winston = require('winston');" in rendered
        assert "const { AsyncLocalStorage } = require('async_hooks');" in rendered
        assert "function setupLogging()" in rendered
        assert "function getLogger(" in rendered
        assert "module.exports" in rendered

        # Should contain structured logging
        assert "structuredFormatter" in rendered
        assert "JSON.stringify" in rendered

        # Should contain environment variable handling
        assert "process.env.LOG_LEVEL" in rendered
        assert "process.env.LOG_OUTPUT" in rendered
        assert "process.env.ENVIRONMENT" in rendered

    def test_typescript_logger_generation(self, logger_template):
        """Test TypeScript logger component generation."""
        context = {"language": "typescript", "project": {"name": "test-typescript-app"}}

        rendered = logger_template.render(**context)

        # Should be substantial content
        assert len(rendered) > 1000

        # Should contain TypeScript-specific code
        assert "import winston from 'winston';" in rendered
        assert "import { AsyncLocalStorage } from 'async_hooks';" in rendered
        assert "export function setupLogging():" in rendered
        assert "export function getLogger(" in rendered
        assert "export interface LogContext" in rendered
        assert (
            "export interface LogLevel" in rendered
            or "export type LogLevel" in rendered
        )

        # Should contain type definitions
        assert "LogContext" in rendered
        assert ": void" in rendered  # TypeScript return types
        assert ": string" in rendered  # TypeScript parameter types

        # Should contain structured logging
        assert "structuredFormatter" in rendered
        assert "JSON.stringify" in rendered

    def test_rust_logger_generation(self, logger_template):
        """Test Rust logger component generation."""
        context = {"language": "rust", "project": {"name": "test-rust-app"}}

        rendered = logger_template.render(**context)

        # Should be substantial content
        assert len(rendered) > 1000

        # Should contain Rust-specific code
        assert "use serde_json::{json, Value};" in rendered
        assert "use std::collections::HashMap;" in rendered
        assert "pub fn setup_logging()" in rendered
        assert "pub enum LogLevel" in rendered
        assert "thread_local!" in rendered

        # Should contain structured logging
        assert "json!" in rendered
        assert "to_string()" in rendered

        # Should contain environment variable handling
        assert "env::var(" in rendered  # Simplified check
        assert "LOG_LEVEL" in rendered
        assert "LOG_OUTPUT" in rendered

    def test_unsupported_language(self, logger_template):
        """Test behavior with unsupported language."""
        context = {"language": "unsupported", "project": {"name": "test-app"}}

        rendered = logger_template.render(**context)

        # Should contain fallback message
        assert "Logger not implemented for language: unsupported" in rendered
        assert "Supported languages: python, nodejs, typescript, rust" in rendered

    def test_all_languages_have_consistent_features(self, logger_template):
        """Test that all languages support the same core features."""
        languages = ["python", "nodejs", "typescript", "rust"]

        # Features that should be present in all languages
        core_features = {
            "environment_variables": ["LOG_LEVEL", "LOG_OUTPUT", "ENVIRONMENT"],
            "logging_levels": ["debug", "info", "warn", "error"],
            "context_management": ["context", "Context"],
            "structured_logging": ["structured", "JSON"],
        }

        for language in languages:
            context = {
                "language": language,
                "project": {"name": f"test-{language}-app"},
            }

            rendered = logger_template.render(**context)

            # Check core features
            for feature_category, features in core_features.items():
                features_found = sum(1 for feature in features if feature in rendered)
                assert (
                    features_found >= 1
                ), f"{language} missing features from {feature_category}: {features}"

    def test_template_project_name_substitution(self, logger_template):
        """Test that project name is properly substituted."""
        test_project_name = "my-awesome-cli-tool"

        for language in ["python", "nodejs", "typescript", "rust"]:
            context = {"language": language, "project": {"name": test_project_name}}

            rendered = logger_template.render(**context)

            # Project name should appear in the rendered content
            assert test_project_name in rendered

    def test_template_rendering_performance(self, logger_template):
        """Test that template rendering is reasonably fast."""
        import time

        context = {"language": "python", "project": {"name": "performance-test"}}

        # Time multiple renders
        start_time = time.perf_counter()
        for i in range(10):
            rendered = logger_template.render(**context)
        end_time = time.perf_counter()

        total_time = end_time - start_time
        avg_time_per_render = total_time / 10

        # Should be fast (less than 10ms per render)
        assert (
            avg_time_per_render < 0.01
        ), f"Template rendering too slow: {avg_time_per_render*1000:.2f}ms per render"

        # Should generate substantial content
        assert len(rendered) > 1000


class TestLoggerComponentIntegration:
    """Test integration of logger components with the framework."""

    def test_logger_template_file_exists(self):
        """Test that the logger template file exists and is readable."""
        template_path = (
            Path(__file__).parent.parent.parent.parent
            / "goobits_cli/universal/components/logger.j2"
        )

        assert template_path.exists(), f"Logger template not found at {template_path}"
        assert (
            template_path.is_file()
        ), f"Logger template path is not a file: {template_path}"

        # Should be readable
        with open(template_path, "r") as f:
            content = f.read()

        assert len(content) > 10000, "Logger template seems too small"
        assert "language ==" in content, "Logger template missing language conditionals"

    def test_logger_template_syntax(self):
        """Test that the logger template has valid Jinja2 syntax."""
        template_path = (
            Path(__file__).parent.parent.parent.parent
            / "goobits_cli/universal/components/logger.j2"
        )

        with open(template_path, "r") as f:
            template_content = f.read()

        # Should be able to create Template without syntax errors
        try:
            template = Template(template_content)
        except Exception as e:
            pytest.fail(f"Logger template has invalid Jinja2 syntax: {e}")

        # Should be able to render with minimal context
        try:
            rendered = template.render(language="python", project={"name": "test"})
            assert len(rendered) > 100
        except Exception as e:
            pytest.fail(f"Logger template rendering failed: {e}")

    def test_logger_component_completeness(self):
        """Test that logger component provides complete functionality."""
        template_path = (
            Path(__file__).parent.parent.parent.parent
            / "goobits_cli/universal/components/logger.j2"
        )

        with open(template_path, "r") as f:
            template_content = f.read()

        template = Template(template_content)

        # Test each language for completeness
        for language in ["python", "nodejs", "typescript", "rust"]:
            context = {"language": language, "project": {"name": "completeness-test"}}
            rendered = template.render(**context)

            # Each language should have substantial implementation
            assert (
                len(rendered) > 2000
            ), f"{language} logger implementation seems incomplete ({len(rendered)} chars)"

            # Should have setup function
            setup_patterns = {
                "python": "def setup_logging(",
                "nodejs": "function setupLogging(",
                "typescript": "export function setupLogging(",
                "rust": "pub fn setup_logging(",
            }

            pattern = setup_patterns[language]
            assert pattern in rendered, f"{language} missing setup function: {pattern}"


if __name__ == "__main__":
    pytest.main([__file__])
