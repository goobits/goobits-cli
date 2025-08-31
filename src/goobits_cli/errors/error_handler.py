"""
Error Handler
=============

Error handling system extracted from error_handler.j2 template.
Provides comprehensive error handling with context, reporting, and debugging support.
"""

import sys
import traceback
from typing import Optional, Any, Dict, List
from dataclasses import dataclass, field
from enum import Enum
from .exception_hierarchy import ExitCode, CliError


class ErrorSeverity(Enum):
    """Error severity levels."""
    DEBUG = "debug"
    INFO = "info" 
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class ErrorContext:
    """Context information for error handling."""
    operation: Optional[str] = None
    component: Optional[str] = None
    user_input: Optional[str] = None
    file_path: Optional[str] = None
    line_number: Optional[int] = None
    stack_trace: Optional[str] = None
    environment: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_context(self, key: str, value: Any) -> None:
        """Add context information."""
        self.metadata[key] = value
    
    def get_context_summary(self) -> str:
        """Get a summary of the error context."""
        parts = []
        if self.operation:
            parts.append(f"Operation: {self.operation}")
        if self.component:
            parts.append(f"Component: {self.component}")
        if self.file_path:
            parts.append(f"File: {self.file_path}")
            if self.line_number:
                parts[-1] += f":{self.line_number}"
        return " | ".join(parts) if parts else "Unknown context"


@dataclass
class ErrorReport:
    """Comprehensive error report."""
    error: Exception
    severity: ErrorSeverity
    context: ErrorContext
    timestamp: Optional[str] = None
    handled: bool = False
    exit_code: Optional[int] = None
    user_message: Optional[str] = None
    debug_info: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert error report to dictionary."""
        return {
            'error_type': type(self.error).__name__,
            'error_message': str(self.error),
            'severity': self.severity.value,
            'context': {
                'operation': self.context.operation,
                'component': self.context.component,
                'file_path': self.context.file_path,
                'line_number': self.context.line_number,
                'metadata': self.context.metadata
            },
            'timestamp': self.timestamp,
            'handled': self.handled,
            'exit_code': self.exit_code,
            'user_message': self.user_message,
            'debug_info': self.debug_info
        }


class ErrorFormatter:
    """Format errors for different output contexts."""
    
    def __init__(self, language: str = 'python'):
        self.language = language
    
    def format_user_message(self, error: Exception, context: ErrorContext) -> str:
        """Format error message for end users."""
        if isinstance(error, CliError):
            message = f"Error: {error.message}"
        else:
            message = f"Unexpected error: {str(error)}"
        
        if context.operation:
            message = f"{context.operation}: {message}"
        
        return message
    
    def format_debug_message(self, error: Exception, context: ErrorContext) -> List[str]:
        """Format detailed debug information."""
        lines = []
        lines.append(f"Error Type: {type(error).__name__}")
        lines.append(f"Message: {str(error)}")
        lines.append(f"Context: {context.get_context_summary()}")
        
        if isinstance(error, CliError) and error.details:
            lines.append("Additional Details:")
            for key, value in error.details.items():
                lines.append(f"  {key}: {value}")
        
        if context.stack_trace:
            lines.append("Stack Trace:")
            lines.append(context.stack_trace)
        
        return lines
    
    def format_warning(self, message: str, details: Optional[Dict[str, Any]] = None) -> List[str]:
        """Format warning message."""
        lines = [f"Warning: {message}"]
        
        if details:
            for key, value in details.items():
                lines.append(f"  {key}: {value}")
        
        return lines


class ErrorHandler:
    """Centralized error handling for CLI applications."""
    
    def __init__(self, 
                 debug: bool = False, 
                 verbose: bool = False,
                 language: str = 'python',
                 exit_on_error: bool = True):
        self.debug = debug
        self.verbose = verbose or debug
        self.language = language
        self.exit_on_error = exit_on_error
        self.formatter = ErrorFormatter(language)
        self._error_history: List[ErrorReport] = []
    
    def handle_error(self, 
                    error: Exception, 
                    context: Optional[ErrorContext] = None,
                    user_message: Optional[str] = None) -> ErrorReport:
        """
        Handle an error and optionally exit the program.
        
        Args:
            error: The exception that occurred
            context: Optional context information
            user_message: Custom user-facing message
            
        Returns:
            ErrorReport with handling details
        """
        context = context or ErrorContext()
        
        # Create error report
        report = ErrorReport(
            error=error,
            severity=self._determine_severity(error),
            context=context,
            user_message=user_message
        )
        
        # Add stack trace if available
        if hasattr(error, '__traceback__') and error.__traceback__:
            context.stack_trace = ''.join(traceback.format_exception(
                type(error), error, error.__traceback__
            ))
        
        # Handle the error based on type
        if isinstance(error, CliError):
            report = self._handle_cli_error(error, report)
        else:
            report = self._handle_unexpected_error(error, report)
        
        # Store in history
        self._error_history.append(report)
        
        # Exit if configured to do so
        if self.exit_on_error and report.exit_code is not None:
            sys.exit(report.exit_code)
        
        return report
    
    def _determine_severity(self, error: Exception) -> ErrorSeverity:
        """Determine error severity."""
        if isinstance(error, CliError):
            if error.exit_code in (ExitCode.USAGE_ERROR, ExitCode.CONFIG_ERROR):
                return ErrorSeverity.WARNING
            else:
                return ErrorSeverity.ERROR
        else:
            return ErrorSeverity.CRITICAL
    
    def _handle_cli_error(self, error: CliError, report: ErrorReport) -> ErrorReport:
        """Handle a known CLI error."""
        user_message = report.user_message or self.formatter.format_user_message(error, report.context)
        print(user_message, file=sys.stderr)
        
        if self.verbose and error.details:
            print("Additional details:", file=sys.stderr)
            for key, value in error.details.items():
                print(f"  {key}: {value}", file=sys.stderr)
        
        if self.debug and report.context.stack_trace:
            print("\nStack trace:", file=sys.stderr)
            print(report.context.stack_trace, file=sys.stderr)
        
        report.handled = True
        report.exit_code = error.exit_code.value
        report.user_message = user_message
        
        return report
    
    def _handle_unexpected_error(self, error: Exception, report: ErrorReport) -> ErrorReport:
        """Handle an unexpected error."""
        user_message = report.user_message or f"Unexpected error: {str(error)}"
        
        if report.context.operation:
            user_message = f"{report.context.operation}: {user_message}"
        
        print(user_message, file=sys.stderr)
        
        if self.verbose or self.debug:
            if report.context.stack_trace:
                print("\nStack trace:", file=sys.stderr)
                print(report.context.stack_trace, file=sys.stderr)
        else:
            print("Run with --verbose for more details", file=sys.stderr)
        
        report.handled = True
        report.exit_code = ExitCode.GENERAL_ERROR.value
        report.user_message = user_message
        
        return report
    
    def warn(self, message: str, 
             details: Optional[Dict[str, Any]] = None,
             context: Optional[ErrorContext] = None) -> None:
        """Issue a warning without exiting."""
        warning_lines = self.formatter.format_warning(message, details)
        
        for line in warning_lines:
            print(line, file=sys.stderr)
        
        # Create warning report
        warning_report = ErrorReport(
            error=UserWarning(message),
            severity=ErrorSeverity.WARNING,
            context=context or ErrorContext(),
            handled=True,
            user_message=message
        )
        self._error_history.append(warning_report)
    
    def get_error_history(self) -> List[ErrorReport]:
        """Get history of handled errors."""
        return self._error_history.copy()
    
    def clear_history(self) -> None:
        """Clear error history."""
        self._error_history.clear()
    
    def handle_keyboard_interrupt(self, context: Optional[ErrorContext] = None) -> ErrorReport:
        """Handle Ctrl+C gracefully."""
        context = context or ErrorContext(operation="User interruption")
        
        print("\nOperation cancelled by user", file=sys.stderr)
        
        report = ErrorReport(
            error=KeyboardInterrupt("User cancelled operation"),
            severity=ErrorSeverity.INFO,
            context=context,
            handled=True,
            exit_code=ExitCode.GENERAL_ERROR.value,
            user_message="Operation cancelled by user"
        )
        
        self._error_history.append(report)
        
        if self.exit_on_error:
            sys.exit(report.exit_code)
        
        return report


# Global error handler management
_error_handler: Optional[ErrorHandler] = None


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


def handle_keyboard_interrupt(context: Optional[ErrorContext] = None):
    """Handle Ctrl+C gracefully using global handler."""
    return get_error_handler().handle_keyboard_interrupt(context)