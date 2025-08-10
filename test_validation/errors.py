"""
Error handling utilities for Test Python CLI
"""

import sys
import traceback
from typing import Optional, Any, Dict
from enum import Enum

class ExitCode(Enum):
    """Standard exit codes for the CLI."""
    SUCCESS = 0
    GENERAL_ERROR = 1
    USAGE_ERROR = 2
    CONFIG_ERROR = 3
    NETWORK_ERROR = 4
    PERMISSION_ERROR = 5
    FILE_NOT_FOUND = 6

class CliError(Exception):
    """Base exception class for CLI errors."""

    def __init__(self, message: str, exit_code: ExitCode = ExitCode.GENERAL_ERROR,
                 details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.exit_code = exit_code
        self.details = details or {}

class UsageError(CliError):
    """Raised when command usage is incorrect."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, ExitCode.USAGE_ERROR, details)

class ConfigError(CliError):
    """Raised when configuration is invalid or missing."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, ExitCode.CONFIG_ERROR, details)

class NetworkError(CliError):
    """Raised when network operations fail."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, ExitCode.NETWORK_ERROR, details)

class PermissionError(CliError):
    """Raised when permission is denied."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, ExitCode.PERMISSION_ERROR, details)

class FileNotFoundError(CliError):
    """Raised when a required file is not found."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, ExitCode.FILE_NOT_FOUND, details)

class ErrorHandler:
    """Centralized error handling for the CLI."""

    def __init__(self, debug: bool = False, verbose: bool = False):
        self.debug = debug
        self.verbose = verbose

    def handle_error(self, error: Exception, context: Optional[str] = None) -> None:
        """
        Handle an error and exit the program with appropriate code.

        Args:
            error: The exception that occurred
            context: Optional context information
        """
        if isinstance(error, CliError):
            self._handle_cli_error(error, context)
        else:
            self._handle_unexpected_error(error, context)

    def _handle_cli_error(self, error: CliError, context: Optional[str] = None) -> None:
        """Handle a known CLI error."""
        message = f"Error: {error.message}"
        if context:
            message = f"{context}: {message}"

        print(message, file=sys.stderr)

        if self.verbose and error.details:
            print("Additional details:", file=sys.stderr)
            for key, value in error.details.items():
                print(f"  {key}: {value}", file=sys.stderr)

        if self.debug:
            traceback.print_exc()

        sys.exit(error.exit_code.value)

    def _handle_unexpected_error(self, error: Exception, context: Optional[str] = None) -> None:
        """Handle an unexpected error."""
        message = f"Unexpected error: {str(error)}"
        if context:
            message = f"{context}: {message}"

        print(message, file=sys.stderr)

        if self.debug or self.verbose:
            traceback.print_exc()
        else:
            print("Run with --debug for more details", file=sys.stderr)

        sys.exit(ExitCode.GENERAL_ERROR.value)

    def warn(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        """Issue a warning without exiting."""
        print(f"Warning: {message}", file=sys.stderr)

        if self.verbose and details:
            for key, value in details.items():
                print(f"  {key}: {value}", file=sys.stderr)

def handle_keyboard_interrupt():
    """Handle Ctrl+C gracefully."""
    print("\nOperation cancelled by user", file=sys.stderr)
    sys.exit(ExitCode.GENERAL_ERROR.value)

# Global error handler instance
_error_handler = None

def get_error_handler() -> ErrorHandler:
    """Get the global error handler instance."""
    global _error_handler
    if _error_handler is None:
        _error_handler = ErrorHandler()
    return _error_handler

def set_error_handler(handler: ErrorHandler) -> None:
    """Set the global error handler instance."""
    global _error_handler
    _error_handler = handler