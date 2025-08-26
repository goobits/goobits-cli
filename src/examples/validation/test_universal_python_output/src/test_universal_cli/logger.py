"""
Structured logging infrastructure for Test Universal CLI.

This module provides structured logging with context management for enhanced observability.
Environment variables:
- LOG_LEVEL: Set logging level (DEBUG, INFO, WARNING, ERROR) - default: INFO
- LOG_OUTPUT: Set output destination (stdout, stderr, file:<path>) - default: stdout
- ENVIRONMENT: Set environment (production/development) - affects format
"""

import json
import logging
import os
import sys
from contextvars import ContextVar
from typing import Dict, Any, Optional
from pathlib import Path

# Context variables for structured logging
_log_context: ContextVar[Dict[str, Any]] = ContextVar("log_context", default={})


class StructuredFormatter(logging.Formatter):
    """Custom formatter that outputs structured logs based on environment."""

    def __init__(self):
        super().__init__()
        self.environment = os.getenv("ENVIRONMENT", "development")
        self.is_production = self.environment.lower() in ("production", "prod")

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON for production or readable format for development."""

        # Get current context
        context = _log_context.get({})

        # Build log data
        log_data = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add context if available
        if context:
            log_data["context"] = context

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = {
                "type": record.exc_info[0].__name__ if record.exc_info[0] else None,
                "message": str(record.exc_info[1]) if record.exc_info[1] else None,
                "traceback": (
                    self.formatException(record.exc_info) if record.exc_info else None
                ),
            }

        # Add extra fields from log record
        extra_fields = {}
        for key, value in record.__dict__.items():
            if key not in [
                "name",
                "msg",
                "args",
                "levelname",
                "levelno",
                "pathname",
                "filename",
                "module",
                "lineno",
                "funcName",
                "created",
                "msecs",
                "relativeCreated",
                "thread",
                "threadName",
                "processName",
                "process",
                "message",
                "exc_info",
                "exc_text",
                "stack_info",
            ]:
                extra_fields[key] = value

        if extra_fields:
            log_data["extra"] = extra_fields

        if self.is_production:
            # JSON format for production
            return json.dumps(log_data)
        else:
            # Human-readable format for development
            context_str = (
                f" [{', '.join(f'{k}={v}' for k, v in context.items())}]"
                if context
                else ""
            )
            extra_str = f" {extra_fields}" if extra_fields else ""

            base_msg = f"{log_data['timestamp']} {log_data['level']:8} {log_data['logger']:20} {log_data['message']}"

            if context_str or extra_str:
                base_msg += f"{context_str}{extra_str}"

            # Add exception info if present
            if record.exc_info:
                base_msg += f"\n{self.formatException(record.exc_info)}"

            return base_msg


def setup_logging() -> None:
    """
    Initialize structured logging for Test Universal CLI.

    Environment Variables:
    - LOG_LEVEL: Set logging level (DEBUG, INFO, WARNING, ERROR) - default: INFO
    - LOG_OUTPUT: Set output destination (stdout, stderr, file:<path>) - default: stdout
    - ENVIRONMENT: Set environment (production/development) - affects format
    """

    # Get configuration from environment
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    log_output = os.getenv("LOG_OUTPUT", "stdout").lower()

    # Configure logging level
    try:
        level = getattr(logging, log_level)
    except AttributeError:
        level = logging.INFO
        print(f"Warning: Invalid LOG_LEVEL '{log_level}', using INFO", file=sys.stderr)

    # Set up formatter
    formatter = StructuredFormatter()

    # Configure handlers based on LOG_OUTPUT
    handlers = []

    if log_output == "stderr":
        # All logs to stderr
        handler = logging.StreamHandler(sys.stderr)
        handler.setFormatter(formatter)
        handlers.append(handler)
    elif log_output.startswith("file:"):
        # Log to file
        log_file = log_output[5:]  # Remove 'file:' prefix
        log_path = Path(log_file)

        # Ensure log directory exists
        log_path.parent.mkdir(parents=True, exist_ok=True)

        handler = logging.FileHandler(log_path)
        handler.setFormatter(formatter)
        handlers.append(handler)
    elif log_output == "stdout":
        # Container-friendly: INFO/DEBUG to stdout, WARN/ERROR to stderr
        stdout_handler = logging.StreamHandler(sys.stdout)
        stdout_handler.setFormatter(formatter)
        stdout_handler.setLevel(logging.DEBUG)
        stdout_handler.addFilter(lambda record: record.levelno < logging.WARNING)

        stderr_handler = logging.StreamHandler(sys.stderr)
        stderr_handler.setFormatter(formatter)
        stderr_handler.setLevel(logging.WARNING)

        handlers.extend([stdout_handler, stderr_handler])
    else:
        # Default to stdout for unknown options
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(formatter)
        handlers.append(handler)

    # Configure root logger
    root_logger = logging.getLogger()

    # Clear existing handlers to avoid duplicates
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Add new handlers
    for handler in handlers:
        root_logger.addHandler(handler)

    root_logger.setLevel(level)

    # Log startup message
    logger = get_logger(__name__)
    logger.info(f"Logging initialized: level={log_level}, output={log_output}")


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for the specified name.

    Args:
        name: Logger name (typically __name__ from calling module)

    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)


def set_context(**kwargs: Any) -> None:
    """
    Set logging context variables that will be included in all log messages.

    Args:
        **kwargs: Key-value pairs to add to logging context

    Example:
        set_context(operation_id="operation_123", user="admin")
    """
    current_context = _log_context.get({})
    updated_context = {**current_context, **kwargs}
    _log_context.set(updated_context)


def clear_context() -> None:
    """Clear all logging context variables."""
    _log_context.set({})


def update_context(**kwargs: Any) -> None:
    """
    Update existing context with new values.

    Args:
        **kwargs: Key-value pairs to update in logging context
    """
    current_context = _log_context.get({})
    current_context.update(kwargs)
    _log_context.set(current_context)


def get_context() -> Dict[str, Any]:
    """Get current logging context."""
    return _log_context.get({}).copy()


def remove_context_keys(*keys: str) -> None:
    """
    Remove specific keys from logging context.

    Args:
        *keys: Context keys to remove
    """
    current_context = _log_context.get({})
    for key in keys:
        current_context.pop(key, None)
    _log_context.set(current_context)
