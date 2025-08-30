"""
Language Adapters
================

Language-specific adapters extracted from error_handler.j2 template.
Each adapter generates error handling code for its target language.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List
from .exception_hierarchy import ErrorDefinitions, ExitCode
from .error_handler import ErrorSeverity


class ErrorAdapter(ABC):
    """Base class for language-specific error adapters."""
    
    def __init__(self, language: str):
        self.language = language
        self.error_definitions = ErrorDefinitions()
    
    @abstractmethod
    def generate_code(self, config: Dict[str, Any]) -> str:
        """Generate error handling code for the language."""
        pass
    
    def get_exit_codes(self) -> Dict[str, int]:
        """Get exit codes for the language."""
        return {code.name: code.value for code in ExitCode}


class PythonErrorAdapter(ErrorAdapter):
    """Python error handling adapter."""
    
    def __init__(self):
        super().__init__('python')
    
    def generate_code(self, config: Dict[str, Any]) -> str:
        """Generate Python error handling code."""
        project_name = config.get('project', {}).get('name', 'CLI')
        
        lines = [
            '"""',
            f'Error handling utilities for {project_name}',
            '"""',
            '',
            'import sys',
            'import traceback',
            'from typing import Optional, Any, Dict',
            'from enum import Enum',
            ''
        ]
        
        # Generate exit codes
        lines.extend(self._generate_exit_codes())
        lines.append('')
        
        # Generate exception classes
        lines.extend(self._generate_exception_classes())
        lines.append('')
        
        # Generate error handler class
        lines.extend(self._generate_error_handler_class())
        lines.append('')
        
        # Generate utility functions
        lines.extend(self._generate_utility_functions())
        
        return '\n'.join(lines)
    
    def _generate_exit_codes(self) -> List[str]:
        """Generate Python exit code enum."""
        lines = [
            'class ExitCode(Enum):',
            '    """Standard exit codes for the CLI."""'
        ]
        
        for code in ExitCode:
            lines.append(f'    {code.name} = {code.value}')
        
        return lines
    
    def _generate_exception_classes(self) -> List[str]:
        """Generate Python exception classes."""
        lines = []
        error_defs = self.error_definitions.get_standard_errors()
        hierarchy = self.error_definitions.get_error_hierarchy()
        
        for error_name, error_def in error_defs.items():
            parent = hierarchy.get(error_name, 'Exception')
            
            lines.extend([
                f'class {error_name}({parent}):',
                f'    """{error_def.details.context or error_def.message}"""',
                '    ',
                '    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):'
            ])
            
            if error_name == 'CliError':
                lines.extend([
                    f'        super().__init__(message)',
                    '        self.message = message',
                    f'        self.exit_code = ExitCode.{error_def.exit_code.name}',
                    '        self.details = details or {}',
                ])
            else:
                lines.extend([
                    f'        super().__init__(message, details)',
                ])
            
            lines.append('')
        
        return lines
    
    def _generate_error_handler_class(self) -> List[str]:
        """Generate Python ErrorHandler class."""
        return [
            'class ErrorHandler:',
            '    """Centralized error handling for the CLI."""',
            '    ',
            '    def __init__(self, debug: bool = False, verbose: bool = False):',
            '        self.debug = debug',
            '        self.verbose = verbose or debug  # verbose includes debug functionality',
            '    ',
            '    def handle_error(self, error: Exception, context: Optional[str] = None) -> None:',
            '        """',
            '        Handle an error and exit the program with appropriate code.',
            '        ',
            '        Args:',
            '            error: The exception that occurred',
            '            context: Optional context information',
            '        """',
            '        if isinstance(error, CliError):',
            '            self._handle_cli_error(error, context)',
            '        else:',
            '            self._handle_unexpected_error(error, context)',
            '    ',
            '    def _handle_cli_error(self, error: CliError, context: Optional[str] = None) -> None:',
            '        """Handle a known CLI error."""',
            '        message = f"Error: {error.message}"',
            '        if context:',
            '            message = f"{context}: {message}"',
            '        ',
            '        print(message, file=sys.stderr)',
            '        ',
            '        if self.verbose and error.details:',
            '            print("Additional details:", file=sys.stderr)',
            '            for key, value in error.details.items():',
            '                print(f"  {key}: {value}", file=sys.stderr)',
            '        ',
            '        if self.verbose:',
            '            traceback.print_exc()',
            '        ',
            '        sys.exit(error.exit_code.value)',
            '    ',
            '    def _handle_unexpected_error(self, error: Exception, context: Optional[str] = None) -> None:',
            '        """Handle an unexpected error."""',
            '        message = f"Unexpected error: {str(error)}"',
            '        if context:',
            '            message = f"{context}: {message}"',
            '        ',
            '        print(message, file=sys.stderr)',
            '        ',
            '        if self.verbose:',
            '            traceback.print_exc()',
            '        else:',
            '            print("Run with --verbose for more details", file=sys.stderr)',
            '        ',
            '        sys.exit(ExitCode.GENERAL_ERROR.value)',
            '    ',
            '    def warn(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:',
            '        """Issue a warning without exiting."""',
            '        print(f"Warning: {message}", file=sys.stderr)',
            '        ',
            '        if self.verbose and details:',
            '            for key, value in details.items():',
            '                print(f"  {key}: {value}", file=sys.stderr)'
        ]
    
    def _generate_utility_functions(self) -> List[str]:
        """Generate Python utility functions."""
        return [
            'def handle_keyboard_interrupt():',
            '    """Handle Ctrl+C gracefully."""',
            '    print("\\nOperation cancelled by user", file=sys.stderr)',
            '    sys.exit(ExitCode.GENERAL_ERROR.value)',
            '',
            '# Global error handler instance',
            '_error_handler = None',
            '',
            'def get_error_handler() -> ErrorHandler:',
            '    """Get the global error handler instance."""',
            '    global _error_handler',
            '    if _error_handler is None:',
            '        _error_handler = ErrorHandler()',
            '    return _error_handler',
            '',
            'def set_error_handler(handler: ErrorHandler) -> None:',
            '    """Set the global error handler instance."""',
            '    global _error_handler',
            '    _error_handler = handler'
        ]


class NodeJSErrorAdapter(ErrorAdapter):
    """Node.js error handling adapter."""
    
    def __init__(self):
        super().__init__('nodejs')
    
    def generate_code(self, config: Dict[str, Any]) -> str:
        """Generate Node.js error handling code."""
        project_name = config.get('project', {}).get('name', 'CLI')
        
        lines = [
            '/**',
            f' * Error handling utilities for {project_name}',
            ' */',
            '',
            'import util from \'util\';',
            ''
        ]
        
        # Generate exit codes
        lines.extend(self._generate_exit_codes())
        lines.append('')
        
        # Generate exception classes
        lines.extend(self._generate_exception_classes())
        lines.append('')
        
        # Generate error handler class
        lines.extend(self._generate_error_handler_class())
        lines.append('')
        
        # Generate utility functions and exports
        lines.extend(self._generate_utility_functions())
        
        return '\n'.join(lines)
    
    def _generate_exit_codes(self) -> List[str]:
        """Generate Node.js exit codes."""
        lines = ['// Standard exit codes', 'const ExitCode = {']
        
        for code in ExitCode:
            lines.append(f'    {code.name}: {code.value},')
        
        lines.append('};')
        return lines
    
    def _generate_exception_classes(self) -> List[str]:
        """Generate Node.js exception classes."""
        lines = []
        error_defs = self.error_definitions.get_standard_errors()
        
        for error_name, error_def in error_defs.items():
            lines.extend([
                f'class {error_name} extends Error {{',
                f'    constructor(message, exitCode = ExitCode.{error_def.exit_code.name}, details = {{}}) {{',
                '        super(message);',
                f'        this.name = \'{error_name}\';',
                '        this.exitCode = exitCode;',
                '        this.details = details;',
                f'        Error.captureStackTrace(this, {error_name});',
                '    }',
                '}',
                ''
            ])
        
        return lines
    
    def _generate_error_handler_class(self) -> List[str]:
        """Generate Node.js ErrorHandler class."""
        return [
            'class ErrorHandler {',
            '    constructor(options = {}) {',
            '        this.debug = options.debug || false;',
            '        this.verbose = options.verbose || options.debug || false;',
            '    }',
            '',
            '    handleError(error, context = null) {',
            '        if (error instanceof CliError) {',
            '            this._handleCliError(error, context);',
            '        } else {',
            '            this._handleUnexpectedError(error, context);',
            '        }',
            '    }',
            '',
            '    _handleCliError(error, context) {',
            '        let message = `Error: ${error.message}`;',
            '        if (context) {',
            '            message = `${context}: ${message}`;',
            '        }',
            '',
            '        console.error(message);',
            '',
            '        if (this.verbose && Object.keys(error.details).length > 0) {',
            '            console.error(\'Additional details:\');',
            '            for (const [key, value] of Object.entries(error.details)) {',
            '                console.error(`  ${key}: ${value}`);',
            '            }',
            '        }',
            '',
            '        if (this.verbose) {',
            '            console.error(error.stack);',
            '        }',
            '',
            '        process.exit(error.exitCode);',
            '    }',
            '',
            '    _handleUnexpectedError(error, context) {',
            '        let message = `Unexpected error: ${error.message}`;',
            '        if (context) {',
            '            message = `${context}: ${message}`;',
            '        }',
            '',
            '        console.error(message);',
            '',
            '        if (this.verbose) {',
            '            console.error(error.stack);',
            '        } else {',
            '            console.error(\'Run with --verbose for more details\');',
            '        }',
            '',
            '        process.exit(ExitCode.GENERAL_ERROR);',
            '    }',
            '',
            '    warn(message, details = {}) {',
            '        console.error(`Warning: ${message}`);',
            '',
            '        if (this.verbose && Object.keys(details).length > 0) {',
            '            for (const [key, value] of Object.entries(details)) {',
            '                console.error(`  ${key}: ${value}`);',
            '            }',
            '        }',
            '    }',
            '}'
        ]
    
    def _generate_utility_functions(self) -> List[str]:
        """Generate Node.js utility functions."""
        return [
            'function handleKeyboardInterrupt() {',
            '    console.error(\'\\nOperation cancelled by user\');',
            '    process.exit(ExitCode.GENERAL_ERROR);',
            '}',
            '',
            '// Global error handler instance',
            'let _errorHandler = null;',
            '',
            'function getErrorHandler() {',
            '    if (!_errorHandler) {',
            '        _errorHandler = new ErrorHandler();',
            '    }',
            '    return _errorHandler;',
            '}',
            '',
            'function setErrorHandler(handler) {',
            '    _errorHandler = handler;',
            '}',
            '',
            'export {',
            '    ExitCode,',
            '    CliError,',
            '    UsageError,',
            '    ConfigError,',
            '    NetworkError,',
            '    PermissionError,',
            '    FileNotFoundError,',
            '    ErrorHandler,',
            '    handleKeyboardInterrupt,',
            '    getErrorHandler,',
            '    setErrorHandler',
            '};'
        ]


class TypeScriptErrorAdapter(ErrorAdapter):
    """TypeScript error handling adapter."""
    
    def __init__(self):
        super().__init__('typescript')
    
    def generate_code(self, config: Dict[str, Any]) -> str:
        """Generate TypeScript error handling code."""
        project_name = config.get('project', {}).get('name', 'CLI')
        
        lines = [
            '/**',
            f' * Error handling utilities for {project_name}',
            ' */',
            '',
            'import * as util from \'util\';',
            ''
        ]
        
        # Generate interfaces and types
        lines.extend(self._generate_types_and_interfaces())
        lines.append('')
        
        # Generate exit codes
        lines.extend(self._generate_exit_codes())
        lines.append('')
        
        # Generate exception classes
        lines.extend(self._generate_exception_classes())
        lines.append('')
        
        # Generate error handler class
        lines.extend(self._generate_error_handler_class())
        lines.append('')
        
        # Generate utility functions
        lines.extend(self._generate_utility_functions())
        
        return '\n'.join(lines)
    
    def _generate_types_and_interfaces(self) -> List[str]:
        """Generate TypeScript types and interfaces."""
        return [
            'interface ErrorDetails {',
            '    [key: string]: any;',
            '}',
            '',
            'interface ErrorHandlerOptions {',
            '    debug?: boolean;',
            '    verbose?: boolean;',
            '}'
        ]
    
    def _generate_exit_codes(self) -> List[str]:
        """Generate TypeScript exit codes."""
        lines = ['// Standard exit codes', 'export enum ExitCode {']
        
        for code in ExitCode:
            lines.append(f'    {code.name} = {code.value},')
        
        lines.append('}')
        return lines
    
    def _generate_exception_classes(self) -> List[str]:
        """Generate TypeScript exception classes."""
        lines = []
        error_defs = self.error_definitions.get_standard_errors()
        
        for error_name, error_def in error_defs.items():
            lines.extend([
                f'export class {error_name} extends Error {{',
                '    public readonly exitCode: ExitCode;',
                '    public readonly details: ErrorDetails;',
                '',
                f'    constructor(message: string, exitCode: ExitCode = ExitCode.{error_def.exit_code.name}, details: ErrorDetails = {{}}) {{',
                '        super(message);',
                f'        this.name = \'{error_name}\';',
                '        this.exitCode = exitCode;',
                '        this.details = details;',
                f'        Error.captureStackTrace(this, {error_name});',
                '    }',
                '}',
                ''
            ])
        
        return lines
    
    def _generate_error_handler_class(self) -> List[str]:
        """Generate TypeScript ErrorHandler class.""" 
        return [
            'export class ErrorHandler {',
            '    private readonly debug: boolean;',
            '    private readonly verbose: boolean;',
            '',
            '    constructor(options: ErrorHandlerOptions = {}) {',
            '        this.debug = options.debug || false;',
            '        this.verbose = options.verbose || options.debug || false;',
            '    }',
            '',
            '    public handleError(error: Error, context: string | null = null): void {',
            '        if (error instanceof CliError) {',
            '            this.handleCliError(error, context);',
            '        } else {',
            '            this.handleUnexpectedError(error, context);',
            '        }',
            '    }',
            '',
            '    private handleCliError(error: CliError, context: string | null): void {',
            '        let message = `Error: ${error.message}`;',
            '        if (context) {',
            '            message = `${context}: ${message}`;',
            '        }',
            '',
            '        console.error(message);',
            '',
            '        if (this.verbose && Object.keys(error.details).length > 0) {',
            '            console.error(\'Additional details:\');',
            '            for (const [key, value] of Object.entries(error.details)) {',
            '                console.error(`  ${key}: ${value}`);',
            '            }',
            '        }',
            '',
            '        if (this.verbose) {',
            '            console.error(error.stack);',
            '        }',
            '',
            '        process.exit(error.exitCode);',
            '    }',
            '',
            '    private handleUnexpectedError(error: Error, context: string | null): void {',
            '        let message = `Unexpected error: ${error.message}`;',
            '        if (context) {',
            '            message = `${context}: ${message}`;',
            '        }',
            '',
            '        console.error(message);',
            '',
            '        if (this.verbose) {',
            '            console.error(error.stack);',
            '        } else {',
            '            console.error(\'Run with --verbose for more details\');',
            '        }',
            '',
            '        process.exit(ExitCode.GENERAL_ERROR);',
            '    }',
            '',
            '    public warn(message: string, details: ErrorDetails = {}): void {',
            '        console.error(`Warning: ${message}`);',
            '',
            '        if (this.verbose && Object.keys(details).length > 0) {',
            '            for (const [key, value] of Object.entries(details)) {',
            '                console.error(`  ${key}: ${value}`);',
            '            }',
            '        }',
            '    }',
            '}'
        ]
    
    def _generate_utility_functions(self) -> List[str]:
        """Generate TypeScript utility functions."""
        return [
            'export function handleKeyboardInterrupt(): void {',
            '    console.error(\'\\nOperation cancelled by user\');',
            '    process.exit(ExitCode.GENERAL_ERROR);',
            '}',
            '',
            '// Global error handler instance',
            'let _errorHandler: ErrorHandler | null = null;',
            '',
            'export function getErrorHandler(): ErrorHandler {',
            '    if (!_errorHandler) {',
            '        _errorHandler = new ErrorHandler();',
            '    }',
            '    return _errorHandler;',
            '}',
            '',
            'export function setErrorHandler(handler: ErrorHandler): void {',
            '    _errorHandler = handler;',
            '}'
        ]


class RustErrorAdapter(ErrorAdapter):
    """Rust error handling adapter."""
    
    def __init__(self):
        super().__init__('rust')
    
    def generate_code(self, config: Dict[str, Any]) -> str:
        """Generate Rust error handling code."""
        project_name = config.get('project', {}).get('name', 'CLI')
        
        lines = [
            '//! Error handling utilities',
            '//!',
            f'//! Error handling system for {project_name}',
            '',
            'use std::fmt;',
            'use std::error::Error;',
            'use std::process;',
            'use std::collections::HashMap;',
            ''
        ]
        
        # Generate exit codes
        lines.extend(self._generate_exit_codes())
        lines.append('')
        
        # Generate error types
        lines.extend(self._generate_error_types())
        lines.append('')
        
        # Generate error handler
        lines.extend(self._generate_error_handler())
        lines.append('')
        
        # Generate utility functions
        lines.extend(self._generate_utility_functions())
        
        return '\n'.join(lines)
    
    def _generate_exit_codes(self) -> List[str]:
        """Generate Rust exit codes."""
        lines = [
            '#[derive(Debug, Clone, Copy, PartialEq)]',
            'pub enum ExitCode {'
        ]
        
        for code in ExitCode:
            lines.append(f'    {code.name} = {code.value},')
        
        lines.extend([
            '}',
            '',
            'impl ExitCode {',
            '    pub fn as_i32(&self) -> i32 {',
            '        *self as i32',
            '    }',
            '}'
        ])
        
        return lines
    
    def _generate_error_types(self) -> List[str]:
        """Generate Rust error types."""
        return [
            '#[derive(Debug)]',
            'pub struct CliError {',
            '    pub message: String,',
            '    pub exit_code: ExitCode,',
            '    pub details: HashMap<String, String>,',
            '}',
            '',
            'impl fmt::Display for CliError {',
            '    fn fmt(&self, f: &mut fmt::Formatter<\'_\'>) -> fmt::Result {',
            '        write!(f, "{}", self.message)',
            '    }',
            '}',
            '',
            'impl Error for CliError {}',
            '',
            'impl CliError {',
            '    pub fn new(message: impl Into<String>, exit_code: ExitCode) -> Self {',
            '        Self {',
            '            message: message.into(),',
            '            exit_code,',
            '            details: HashMap::new(),',
            '        }',
            '    }',
            '',
            '    pub fn with_details(mut self, key: impl Into<String>, value: impl Into<String>) -> Self {',
            '        self.details.insert(key.into(), value.into());',
            '        self',
            '    }',
            '',
            '    pub fn usage_error(message: impl Into<String>) -> Self {',
            '        Self::new(message, ExitCode::USAGE_ERROR)',
            '    }',
            '',
            '    pub fn config_error(message: impl Into<String>) -> Self {',
            '        Self::new(message, ExitCode::CONFIG_ERROR)',
            '    }',
            '',
            '    pub fn network_error(message: impl Into<String>) -> Self {',
            '        Self::new(message, ExitCode::NETWORK_ERROR)',
            '    }',
            '',
            '    pub fn permission_error(message: impl Into<String>) -> Self {',
            '        Self::new(message, ExitCode::PERMISSION_ERROR)',
            '    }',
            '',
            '    pub fn file_not_found_error(message: impl Into<String>) -> Self {',
            '        Self::new(message, ExitCode::FILE_NOT_FOUND)',
            '    }',
            '}'
        ]
    
    def _generate_error_handler(self) -> List[str]:
        """Generate Rust error handler."""
        return [
            'pub struct ErrorHandler {',
            '    debug: bool,',
            '    verbose: bool,',
            '}',
            '',
            'impl ErrorHandler {',
            '    pub fn new(debug: bool, verbose: bool) -> Self {',
            '        Self {',
            '            debug,',
            '            verbose: verbose || debug,',
            '        }',
            '    }',
            '',
            '    pub fn handle_error(&self, error: &dyn Error, context: Option<&str>) -> ! {',
            '        if let Some(cli_error) = error.downcast_ref::<CliError>() {',
            '            self.handle_cli_error(cli_error, context);',
            '        } else {',
            '            self.handle_unexpected_error(error, context);',
            '        }',
            '    }',
            '',
            '    pub fn handle_cli_error(&self, error: &CliError, context: Option<&str>) -> ! {',
            '        let message = if let Some(ctx) = context {',
            '            format!("{}: Error: {}", ctx, error.message)',
            '        } else {',
            '            format!("Error: {}", error.message)',
            '        };',
            '',
            '        eprintln!("{}", message);',
            '',
            '        if self.verbose && !error.details.is_empty() {',
            '            eprintln!("Additional details:");',
            '            for (key, value) in &error.details {',
            '                eprintln!("  {}: {}", key, value);',
            '            }',
            '        }',
            '',
            '        process::exit(error.exit_code.as_i32());',
            '    }',
            '',
            '    pub fn handle_unexpected_error(&self, error: &dyn Error, context: Option<&str>) -> ! {',
            '        let message = if let Some(ctx) = context {',
            '            format!("{}: Unexpected error: {}", ctx, error)',
            '        } else {',
            '            format!("Unexpected error: {}", error)',
            '        };',
            '',
            '        eprintln!("{}", message);',
            '',
            '        if self.verbose {',
            '            eprintln!("Debug info: {:?}", error);',
            '        } else {',
            '            eprintln!("Run with --verbose for more details");',
            '        }',
            '',
            '        process::exit(ExitCode::GENERAL_ERROR.as_i32());',
            '    }',
            '',
            '    pub fn warn(&self, message: &str, details: Option<&HashMap<String, String>>) {',
            '        eprintln!("Warning: {}", message);',
            '',
            '        if let Some(details) = details {',
            '            if self.verbose && !details.is_empty() {',
            '                for (key, value) in details {',
            '                    eprintln!("  {}: {}", key, value);',
            '                }',
            '            }',
            '        }',
            '    }',
            '}'
        ]
    
    def _generate_utility_functions(self) -> List[str]:
        """Generate Rust utility functions."""
        return [
            'pub fn handle_keyboard_interrupt() -> ! {',
            '    eprintln!("\\nOperation cancelled by user");',
            '    process::exit(ExitCode::GENERAL_ERROR.as_i32());',
            '}',
            '',
            '// Global error handler',
            'use std::sync::OnceLock;',
            '',
            'static ERROR_HANDLER: OnceLock<ErrorHandler> = OnceLock::new();',
            '',
            'pub fn get_error_handler() -> &\'static ErrorHandler {',
            '    ERROR_HANDLER.get_or_init(|| ErrorHandler::new(false, false))',
            '}',
            '',
            'pub fn set_error_handler(handler: ErrorHandler) {',
            '    ERROR_HANDLER.set(handler).ok();',
            '}'
        ]