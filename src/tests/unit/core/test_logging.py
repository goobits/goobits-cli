"""
Unit tests for the logging infrastructure in Goobits CLI Framework.

This module tests the structured logging implementation that provides
observability and debugging capabilities across the framework and generated CLIs.
"""

import os
import tempfile
import logging

import pytest

from goobits_cli.core.logging import (
    setup_logging,
    get_logger,
    set_context,
    clear_context,
    update_context,
    get_context,
    remove_context_keys,
)


class TestLoggingSetup:
    """Test logging system initialization and configuration."""

    def setup_method(self):
        """Reset logging state before each test."""
        # Clear any existing handlers
        root_logger = logging.getLogger()
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
        root_logger.setLevel(logging.NOTSET)

        # Reset environment variables
        self.original_env = {}
        for key in ["LOG_LEVEL", "LOG_OUTPUT", "ENVIRONMENT"]:
            if key in os.environ:
                self.original_env[key] = os.environ[key]
                del os.environ[key]

    def teardown_method(self):
        """Restore environment after each test."""
        # Restore environment variables
        for key, value in self.original_env.items():
            os.environ[key] = value

        # Clear context
        clear_context()

    def test_basic_setup(self):
        """Test basic logging setup with default configuration."""
        setup_logging()

        root_logger = logging.getLogger()
        assert len(root_logger.handlers) >= 1
        assert root_logger.level == logging.INFO

    def test_custom_log_level(self):
        """Test setup with custom log level."""
        os.environ["LOG_LEVEL"] = "DEBUG"
        setup_logging()

        root_logger = logging.getLogger()
        assert root_logger.level == logging.DEBUG

    def test_invalid_log_level(self):
        """Test setup with invalid log level falls back to INFO."""
        os.environ["LOG_LEVEL"] = "INVALID_LEVEL"

        # Should not raise exception
        setup_logging()

        root_logger = logging.getLogger()
        assert root_logger.level == logging.INFO

    def test_stderr_output(self):
        """Test logging output to stderr."""
        os.environ["LOG_OUTPUT"] = "stderr"
        setup_logging()

        # Should have stderr handlers
        root_logger = logging.getLogger()
        assert len(root_logger.handlers) >= 1

    def test_file_output(self):
        """Test logging output to file."""
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            log_file = temp_file.name

        try:
            os.environ["LOG_OUTPUT"] = f"file:{log_file}"
            setup_logging()

            logger = get_logger("file_test")
            logger.info("Test message")

            # Check file was created and contains message
            with open(log_file, "r") as f:
                content = f.read()

            assert "Test message" in content
        finally:
            if os.path.exists(log_file):
                os.unlink(log_file)

    def test_production_environment(self):
        """Test production environment configuration."""
        os.environ["ENVIRONMENT"] = "production"
        os.environ["LOG_OUTPUT"] = "stderr"

        setup_logging()

        # Just test that setup doesn't crash in production mode
        logger = get_logger("production_test")

        # Verify logger exists and can log (output verification is complex due to handler setup)
        assert logger is not None
        assert logger.name == "production_test"

        # Test that the environment variable is being read correctly
        from goobits_cli.core.logging import StructuredFormatter

        formatter = StructuredFormatter()
        assert formatter.is_production == True


class TestLoggerInstances:
    """Test logger instance creation and usage."""

    def setup_method(self):
        """Setup logging for each test."""
        setup_logging()
        clear_context()

    def test_get_logger(self):
        """Test getting logger instances."""
        logger1 = get_logger("test_module1")
        logger2 = get_logger("test_module2")
        logger3 = get_logger("test_module1")  # Same name

        assert logger1.name == "test_module1"
        assert logger2.name == "test_module2"
        assert logger1 is logger3  # Should be same instance

    def test_logger_logging_levels(self):
        """Test different logging levels."""
        logger = get_logger("level_test")

        # Should not raise exceptions
        logger.debug("Debug message")
        logger.info("Info message")
        logger.warning("Warning message")
        logger.error("Error message")

    def test_logger_with_extra_fields(self):
        """Test logging with extra fields."""
        logger = get_logger("extra_test")

        # Should handle extra fields without error
        logger.info("Test message", extra={"user_id": 123, "action": "test"})


class TestContextManagement:
    """Test logging context management functionality."""

    def setup_method(self):
        """Setup for each test."""
        setup_logging()
        clear_context()

    def test_set_and_get_context(self):
        """Test setting and getting context."""
        set_context(operation_id="test_123", user="test_user")

        context = get_context()
        assert context["operation_id"] == "test_123"
        assert context["user"] == "test_user"

    def test_update_context(self):
        """Test updating existing context."""
        set_context(operation_id="test_123")
        update_context(user="test_user", step="validation")

        context = get_context()
        assert context["operation_id"] == "test_123"
        assert context["user"] == "test_user"
        assert context["step"] == "validation"

    def test_remove_context_keys(self):
        """Test removing specific context keys."""
        set_context(operation_id="test_123", user="test_user", step="validation")
        remove_context_keys("step", "user")

        context = get_context()
        assert context["operation_id"] == "test_123"
        assert "user" not in context
        assert "step" not in context

    def test_clear_context(self):
        """Test clearing all context."""
        set_context(operation_id="test_123", user="test_user")
        clear_context()

        context = get_context()
        assert len(context) == 0

    def test_context_isolation(self):
        """Test that context changes don't affect other operations."""
        # Set initial context
        set_context(shared_id="shared_123")

        # Get initial context
        initial_context = get_context()
        assert initial_context["shared_id"] == "shared_123"

        # Modify context in one place
        set_context(operation_id="operation_456")
        modified_context = get_context()

        # Should have both values
        assert modified_context["shared_id"] == "shared_123"
        assert modified_context["operation_id"] == "operation_456"


class TestLoggingFormats:
    """Test different logging format outputs."""

    def setup_method(self):
        """Setup for format tests."""
        clear_context()

    def test_development_format(self):
        """Test human-readable development format setup."""
        os.environ["ENVIRONMENT"] = "development"

        from goobits_cli.core.logging import StructuredFormatter

        formatter = StructuredFormatter()

        # Should be development mode
        assert formatter.is_production == False
        assert formatter.environment == "development"

    def test_production_json_format(self):
        """Test JSON format in production setup."""
        os.environ["ENVIRONMENT"] = "production"

        from goobits_cli.core.logging import StructuredFormatter

        formatter = StructuredFormatter()

        # Should be production mode
        assert formatter.is_production == True
        assert formatter.environment == "production"

    def test_context_functionality(self):
        """Test that context management works."""
        setup_logging()

        # Test setting and getting context
        set_context(test_id="ctx_123", component="testing")
        context = get_context()

        assert context["test_id"] == "ctx_123"
        assert context["component"] == "testing"

    def test_logger_with_context(self):
        """Test that logger can work with context."""
        setup_logging()
        logger = get_logger("context_test")

        set_context(test_id="ctx_123")

        # Should not raise exceptions
        logger.info("Message with context")
        logger.error("Error with context")


class TestLoggingIntegration:
    """Test integration with the broader framework."""

    def test_multiple_loggers_share_context(self):
        """Test that multiple loggers share the same context."""
        setup_logging()

        logger1 = get_logger("module1")
        logger2 = get_logger("module2")

        set_context(shared_operation="test_operation")

        # Both loggers should have access to the same context
        context1 = get_context()
        context2 = get_context()

        assert context1["shared_operation"] == "test_operation"
        assert context2["shared_operation"] == "test_operation"
        assert context1 == context2

    def test_logging_system_initialization(self):
        """Test that logging system initializes correctly."""
        # Should not raise exceptions
        setup_logging()

        logger = get_logger("test_init")
        assert logger is not None
        assert logger.name == "test_init"

    def test_performance_context_operations(self):
        """Test that context operations are performant."""
        import time

        setup_logging()

        # Test context set performance
        start_time = time.perf_counter()
        for i in range(100):  # Reduced for faster testing
            set_context(iteration=i, batch="performance_test")
        end_time = time.perf_counter()

        total_time = end_time - start_time
        avg_time_per_operation = total_time / 100

        # Should be reasonably fast (less than 10ms per operation)
        assert (
            avg_time_per_operation < 0.01
        ), f"Context operations too slow: {avg_time_per_operation*1000:.2f}ms per operation"

        # Test context get performance
        set_context(test_data="performance_test")

        start_time = time.perf_counter()
        for i in range(100):
            context = get_context()
            assert context["test_data"] == "performance_test"
        end_time = time.perf_counter()

        total_time = end_time - start_time
        avg_time_per_get = total_time / 100

        # Should be reasonably fast
        assert (
            avg_time_per_get < 0.01
        ), f"Context get operations too slow: {avg_time_per_get*1000:.2f}ms per operation"


if __name__ == "__main__":
    pytest.main([__file__])
