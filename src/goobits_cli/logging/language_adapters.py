"""
Language-Specific Logging Adapters
===================================

This module contains the language-specific code generators for logging.
Each adapter generates appropriate logging code for its target language,
replacing the language-specific sections of the logger.j2 template.

Previously, these were embedded in the template as:
{% if language == 'python' %} ... {% elif language == 'nodejs' %} ... etc.
"""

from abc import ABC, abstractmethod
from .logging_framework import LoggingConfig, Environment


class LoggingAdapter(ABC):
    """Abstract base class for language-specific logging adapters."""
    
    @abstractmethod
    def generate_code(self, config: LoggingConfig) -> str:
        """Generate language-specific logging code."""
        pass
    
    @abstractmethod
    def get_import_statements(self, config: LoggingConfig) -> str:
        """Generate import statements for logging."""
        pass
    
    @abstractmethod
    def get_formatter_class(self, config: LoggingConfig) -> str:
        """Generate formatter class implementation."""
        pass


class PythonLoggingAdapter(LoggingAdapter):
    """
    Python logging adapter extracted from lines 18-249 of logger.j2.
    
    Generates Python logging code using the standard library logging module
    with structured formatting capabilities.
    """
    
    def generate_code(self, config: LoggingConfig) -> str:
        """Generate complete Python logging implementation."""
        
        imports = self.get_import_statements(config)
        formatter_class = self.get_formatter_class(config)
        setup_function = self._get_setup_function(config)
        context_manager = self._get_context_manager(config)
        
        return f'''"""
Structured logging infrastructure for {config.project_name}.

This module provides structured logging with context management for enhanced observability.
Environment variables:
- LOG_LEVEL: Set logging level (DEBUG, INFO, WARNING, ERROR) - default: {config.log_level.value}
- LOG_OUTPUT: Set output destination (stdout, stderr, file:<path>) - default: {config.get_output_stream()}
- ENVIRONMENT: Set environment (production/development) - affects format
"""

{imports}

{formatter_class}

{context_manager}

{setup_function}

# Initialize logging on module import
setup_logging()
'''
    
    def get_import_statements(self, config: LoggingConfig) -> str:
        """Generate Python import statements."""
        imports = [
            "import json",
            "import logging",
            "import os",
            "import sys",
            "from contextvars import ContextVar",
            "from typing import Dict, Any, Optional",
            "from pathlib import Path"
        ]
        
        if config.async_logging:
            imports.append("import asyncio")
            imports.append("from concurrent.futures import ThreadPoolExecutor")
        
        return "\n".join(imports)
    
    def get_formatter_class(self, config: LoggingConfig) -> str:
        """Generate Python StructuredFormatter class."""
        
        json_format = "self.is_production" if config.json_format_in_production else "False"
        
        # Build optional fields based on configuration
        optional_fields = []
        if config.include_caller_info:
            optional_fields.append("            'module': record.module,")
            optional_fields.append("            'function': record.funcName,")
            optional_fields.append("            'line': record.lineno,")
        
        optional_fields_str = "\n".join(optional_fields) if optional_fields else ""
        
        return f'''# Context variables for structured logging
_log_context: ContextVar[Dict[str, Any]] = ContextVar('log_context', default={{}})

class StructuredFormatter(logging.Formatter):
    """Custom formatter that outputs structured logs based on environment."""
    
    def __init__(self):
        super().__init__()
        self.environment = os.getenv('ENVIRONMENT', '{config.environment.value}')
        self.is_production = self.environment.lower() in ('production', 'prod')
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON for production or readable format for development."""
        
        # Get current context
        context = _log_context.get({{}})
        
        # Build log data
        log_data = {{
            'timestamp': self.formatTime(record),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
{optional_fields_str}
        }}
        
        # Add context if available
        if context and {str(config.include_context).lower()}:
            log_data['context'] = context
        
        # Add exception info if present
        if record.exc_info:
            log_data['exception'] = {{
                'type': record.exc_info[0].__name__ if record.exc_info[0] else None,
                'message': str(record.exc_info[1]) if record.exc_info[1] else None,
                'traceback': self.formatException(record.exc_info) if record.exc_info else None
            }}
        
        if {json_format}:
            # JSON format for production
            return json.dumps(log_data)
        else:
            # Human-readable format for development
            context_str = f" [{{', '.join(f'{{k}}={{v}}' for k, v in context.items())}}]" if context else ""
            
            base_msg = f"{{log_data['timestamp']}} {{log_data['level']:8}} {{log_data['logger']:20}} {{log_data['message']}}"
            
            if context_str:
                base_msg += context_str
            
            if record.exc_info:
                base_msg += f"\\n{{self.formatException(record.exc_info)}}"
            
            return base_msg'''
    
    def _get_setup_function(self, config: LoggingConfig) -> str:
        """Generate the setup_logging function."""
        
        output_config = self._get_output_configuration(config)
        
        return f'''def setup_logging():
    """Initialize structured logging based on environment configuration."""
    
    # Get configuration from environment
    log_level = os.getenv('LOG_LEVEL', '{config.log_level.value}').upper()
    log_output = os.getenv('LOG_OUTPUT', '{config.get_output_stream()}')
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level, logging.INFO))
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Create formatter
    formatter = StructuredFormatter()
    
    {output_config}
    
    # Set formatter for all handlers
    for handler in root_logger.handlers:
        handler.setFormatter(formatter)
    
    # Log initialization
    logger = logging.getLogger('{config.command_name}')
    logger.info(
        "Logging initialized",
        extra={{
            'log_level': log_level,
            'log_output': log_output,
            'environment': os.getenv('ENVIRONMENT', '{config.environment.value}')
        }}
    )'''
    
    def _get_output_configuration(self, config: LoggingConfig) -> str:
        """Generate output stream configuration code."""
        
        handlers = []
        
        if config.log_to_stdout:
            handlers.append("""
    # Stdout handler for INFO and DEBUG
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(logging.DEBUG)
    stdout_handler.addFilter(lambda record: record.levelno < logging.WARNING)
    root_logger.addHandler(stdout_handler)""")
        
        if config.log_to_stderr or config.environment == Environment.PRODUCTION:
            handlers.append("""
    # Stderr handler for WARNING and above
    stderr_handler = logging.StreamHandler(sys.stderr)
    stderr_handler.setLevel(logging.WARNING)
    root_logger.addHandler(stderr_handler)""")
        
        if config.log_to_file:
            handlers.append(f"""
    # File handler if specified
    if log_output.startswith('file:'):
        file_path = Path(log_output[5:])
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(file_path)
        root_logger.addHandler(file_handler)""")
        
        return "\n".join(handlers)
    
    def _get_context_manager(self, config: LoggingConfig) -> str:
        """Generate context management functions."""
        
        if not config.include_context:
            return "# Context management disabled"
        
        return '''def add_context(**kwargs):
    """Add key-value pairs to the logging context."""
    current = _log_context.get({})
    updated = {**current, **kwargs}
    _log_context.set(updated)

def clear_context():
    """Clear the logging context."""
    _log_context.set({})

def get_context() -> Dict[str, Any]:
    """Get the current logging context."""
    return _log_context.get({})'''


class NodeJSLoggingAdapter(LoggingAdapter):
    """
    Node.js logging adapter extracted from lines 250-489 of logger.j2.
    
    Generates Node.js logging code using the winston library with
    structured formatting capabilities.
    """
    
    def generate_code(self, config: LoggingConfig) -> str:
        """Generate complete Node.js logging implementation."""
        
        imports = self.get_import_statements(config)
        formatter_class = self.get_formatter_class(config)
        setup_function = self._get_setup_function(config)
        context_manager = self._get_context_manager(config)
        
        return f'''/**
 * Structured logging infrastructure for {config.project_name}
 * 
 * Environment variables:
 * - LOG_LEVEL: Set logging level (debug, info, warn, error) - default: {config.log_level.value.lower()}
 * - LOG_OUTPUT: Set output destination (stdout, stderr, file:<path>) - default: {config.get_output_stream()}
 * - NODE_ENV: Set environment (production/development) - affects format
 */

{imports}

{formatter_class}

{context_manager}

{setup_function}

// Initialize logging
const logger = setupLogging();

export {{ logger, addContext, clearContext, getContext }};'''
    
    def get_import_statements(self, config: LoggingConfig) -> str:
        """Generate Node.js import statements."""
        imports = [
            "import winston from 'winston';",
            "import chalk from 'chalk';",
            "import path from 'path';",
            "import { fileURLToPath } from 'url';"
        ]
        
        if config.async_logging:
            imports.append("import { AsyncLocalStorage } from 'async_hooks';")
        
        return "\n".join(imports)
    
    def get_formatter_class(self, config: LoggingConfig) -> str:
        """Generate Node.js formatter configuration."""
        
        json_format = "isProduction" if config.json_format_in_production else "false"
        
        return f'''// Determine if running in production
const isProduction = process.env.NODE_ENV === 'production';

// Context storage for structured logging
const logContext = {{}};

// Custom format for structured logging
const structuredFormat = winston.format.printf(({{ level, message, timestamp, ...metadata }}) => {{
    const logData = {{
        timestamp,
        level,
        message,
        {'module: metadata.module || "unknown",' if config.include_caller_info else ''}
        {'function: metadata.function || "unknown",' if config.include_caller_info else ''}
        {'line: metadata.line || 0,' if config.include_caller_info else ''}
        ...metadata
    }};
    
    // Add context if available
    if (Object.keys(logContext).length > 0 && {str(config.include_context).lower()}) {{
        logData.context = {{ ...logContext }};
    }}
    
    if ({json_format}) {{
        // JSON format for production
        return JSON.stringify(logData);
    }} else {{
        // Human-readable format for development
        const contextStr = Object.keys(logContext).length > 0 
            ? ` [${{Object.entries(logContext).map(([k, v]) => `${{k}}=${{v}}`).join(', ')}}]` 
            : '';
        
        const coloredLevel = chalk.bold(
            level === 'error' ? chalk.red(level.toUpperCase()) :
            level === 'warn' ? chalk.yellow(level.toUpperCase()) :
            level === 'info' ? chalk.green(level.toUpperCase()) :
            chalk.gray(level.toUpperCase())
        );
        
        return `${{timestamp}} ${{coloredLevel.padEnd(17)}} ${{message}}${{contextStr}}`;
    }}
}});'''
    
    def _get_setup_function(self, config: LoggingConfig) -> str:
        """Generate the setupLogging function."""
        
        transports = self._get_transports_configuration(config)
        
        return f'''function setupLogging() {{
    const logLevel = process.env.LOG_LEVEL || '{config.log_level.value.lower()}';
    const logOutput = process.env.LOG_OUTPUT || '{config.get_output_stream()}';
    
    // Create transports
    const transports = [];
    
    {transports}
    
    // Create logger
    const logger = winston.createLogger({{
        level: logLevel,
        format: winston.format.combine(
            winston.format.timestamp(),
            winston.format.errors({{ stack: true }}),
            structuredFormat
        ),
        transports
    }});
    
    // Log initialization
    logger.info('Logging initialized', {{
        logLevel,
        logOutput,
        environment: process.env.NODE_ENV || '{config.environment.value}'
    }});
    
    return logger;
}}'''
    
    def _get_transports_configuration(self, config: LoggingConfig) -> str:
        """Generate transport configuration code."""
        
        transports = []
        
        if config.log_to_stdout:
            transports.append("""// Console transport for stdout
    transports.push(new winston.transports.Console({
        stderrLevels: ['error', 'warn']
    }));""")
        
        if config.log_to_file:
            transports.append("""// File transport if specified
    if (logOutput.startsWith('file:')) {
        const filePath = logOutput.substring(5);
        transports.push(new winston.transports.File({
            filename: filePath
        }));
    }""")
        
        return "\n    ".join(transports)
    
    def _get_context_manager(self, config: LoggingConfig) -> str:
        """Generate context management functions."""
        
        if not config.include_context:
            return "// Context management disabled"
        
        return '''// Context management functions
function addContext(key, value) {
    if (typeof key === 'object') {
        Object.assign(logContext, key);
    } else {
        logContext[key] = value;
    }
}

function clearContext() {
    Object.keys(logContext).forEach(key => delete logContext[key]);
}

function getContext() {
    return { ...logContext };
}'''


class TypeScriptLoggingAdapter(LoggingAdapter):
    """
    TypeScript logging adapter extracted from lines 490-779 of logger.j2.
    
    Generates TypeScript logging code with full type safety.
    """
    
    def generate_code(self, config: LoggingConfig) -> str:
        """Generate complete TypeScript logging implementation."""
        
        # TypeScript is very similar to Node.js but with type annotations
        nodejs_adapter = NodeJSLoggingAdapter()
        base_code = nodejs_adapter.generate_code(config)
        
        # Add TypeScript-specific type definitions
        type_definitions = self._get_type_definitions(config)
        
        # Convert to TypeScript syntax
        ts_code = base_code.replace("function ", "export function ")
        ts_code = ts_code.replace("const ", "export const ")
        
        return f'''{type_definitions}

{ts_code}'''
    
    def get_import_statements(self, config: LoggingConfig) -> str:
        """Generate TypeScript import statements."""
        imports = [
            "import winston from 'winston';",
            "import chalk from 'chalk';",
            "import path from 'path';",
            "import { fileURLToPath } from 'url';",
            "import type { Logger } from 'winston';"
        ]
        
        return "\n".join(imports)
    
    def get_formatter_class(self, config: LoggingConfig) -> str:
        """Generate TypeScript formatter with type annotations."""
        # Use Node.js formatter as base
        nodejs_adapter = NodeJSLoggingAdapter()
        return nodejs_adapter.get_formatter_class(config)
    
    def _get_type_definitions(self, config: LoggingConfig) -> str:
        """Generate TypeScript type definitions."""
        
        return '''/**
 * TypeScript type definitions for logging
 */

export interface LogContext {
    [key: string]: any;
}

export interface LogEntry {
    timestamp: string;
    level: string;
    message: string;
    module?: string;
    function?: string;
    line?: number;
    context?: LogContext;
    [key: string]: any;
}

export type LogLevel = 'debug' | 'info' | 'warn' | 'error';

export interface LoggerConfig {
    level: LogLevel;
    output: string;
    environment: string;
}'''


class RustLoggingAdapter(LoggingAdapter):
    """
    Rust logging adapter extracted from lines 780-1215 of logger.j2.
    
    Generates Rust logging code using the log and env_logger crates.
    """
    
    def generate_code(self, config: LoggingConfig) -> str:
        """Generate complete Rust logging implementation."""
        
        imports = self.get_import_statements(config)
        formatter_struct = self.get_formatter_class(config)
        setup_function = self._get_setup_function(config)
        context_manager = self._get_context_manager(config)
        
        return f'''//! Structured logging infrastructure for {config.project_name}
//!
//! Environment variables:
//! - RUST_LOG: Set logging level (debug, info, warn, error) - default: {config.log_level.value.lower()}
//! - LOG_OUTPUT: Set output destination (stdout, stderr, file:<path>) - default: {config.get_output_stream()}
//! - ENVIRONMENT: Set environment (production/development) - affects format

{imports}

{formatter_struct}

{context_manager}

{setup_function}

/// Initialize logging on module load
pub fn init() {{
    setup_logging();
}}'''
    
    def get_import_statements(self, config: LoggingConfig) -> str:
        """Generate Rust import statements."""
        imports = [
            "use log::{debug, error, info, warn, Level, LevelFilter, Metadata, Record};",
            "use env_logger::{Builder, Env};",
            "use chrono::Local;",
            "use serde_json::json;",
            "use std::io::Write;",
            "use std::sync::RwLock;",
            "use std::collections::HashMap;",
            "use std::path::Path;"
        ]
        
        if config.async_logging:
            imports.append("use tokio::sync::RwLock as AsyncRwLock;")
        
        return "\n".join(imports)
    
    def get_formatter_class(self, config: LoggingConfig) -> str:
        """Generate Rust formatter struct."""
        
        json_format = "is_production" if config.json_format_in_production else "false"
        
        return f'''/// Custom formatter for structured logging
pub struct StructuredFormatter {{
    environment: String,
    is_production: bool,
}}

impl StructuredFormatter {{
    pub fn new() -> Self {{
        let environment = std::env::var("ENVIRONMENT").unwrap_or_else(|_| "{config.environment.value}".to_string());
        let is_production = environment.to_lowercase() == "production";
        
        Self {{
            environment,
            is_production,
        }}
    }}
    
    pub fn format(&self, record: &Record) -> String {{
        let timestamp = Local::now().format("%Y-%m-%d %H:%M:%S%.3f");
        
        let mut log_data = json!({{
            "timestamp": timestamp.to_string(),
            "level": record.level().to_string(),
            "target": record.target(),
            "message": record.args().to_string(),
        }});
        
        if {str(config.include_caller_info).lower()} {{
            if let Some(module) = record.module_path() {{
                log_data["module"] = json!(module);
            }}
            if let Some(file) = record.file() {{
                log_data["file"] = json!(file);
            }}
            if let Some(line) = record.line() {{
                log_data["line"] = json!(line);
            }}
        }}
        
        // Add context if available
        if {str(config.include_context).lower()} {{
            if let Ok(context) = LOG_CONTEXT.read() {{
                if !context.is_empty() {{
                    log_data["context"] = json!(&*context);
                }}
            }}
        }}
        
        if {json_format} {{
            // JSON format for production
            serde_json::to_string(&log_data).unwrap_or_else(|_| format!("{{}}", record.args()))
        }} else {{
            // Human-readable format for development
            let level_str = match record.level() {{
                Level::Error => "\\x1b[31mERROR\\x1b[0m",
                Level::Warn => "\\x1b[33mWARN\\x1b[0m",
                Level::Info => "\\x1b[32mINFO\\x1b[0m",
                Level::Debug => "\\x1b[37mDEBUG\\x1b[0m",
                Level::Trace => "\\x1b[90mTRACE\\x1b[0m",
            }};
            
            format!(
                "{{}} {{:5}} {{:20}} {{}}",
                timestamp,
                level_str,
                record.target(),
                record.args()
            )
        }}
    }}
}}'''
    
    def _get_setup_function(self, config: LoggingConfig) -> str:
        """Generate the setup_logging function."""
        
        return f'''/// Setup logging based on environment configuration
pub fn setup_logging() {{
    let env = Env::default()
        .filter_or("RUST_LOG", "{config.log_level.value.lower()}")
        .write_style_or("RUST_LOG_STYLE", "always");
    
    let formatter = StructuredFormatter::new();
    
    Builder::from_env(env)
        .format(move |buf, record| {{
            writeln!(buf, "{{}}", formatter.format(&record))
        }})
        .init();
    
    info!(
        "Logging initialized: level={{}}, environment={{}}",
        std::env::var("RUST_LOG").unwrap_or_else(|_| "{config.log_level.value.lower()}".to_string()),
        std::env::var("ENVIRONMENT").unwrap_or_else(|_| "{config.environment.value}".to_string())
    );
}}'''
    
    def _get_context_manager(self, config: LoggingConfig) -> str:
        """Generate context management functions."""
        
        if not config.include_context:
            return "// Context management disabled"
        
        return '''/// Global context storage for structured logging
static LOG_CONTEXT: RwLock<HashMap<String, String>> = RwLock::new(HashMap::new());

/// Add key-value pair to logging context
pub fn add_context(key: impl Into<String>, value: impl Into<String>) {
    if let Ok(mut context) = LOG_CONTEXT.write() {
        context.insert(key.into(), value.into());
    }
}

/// Clear the logging context
pub fn clear_context() {
    if let Ok(mut context) = LOG_CONTEXT.write() {
        context.clear();
    }
}

/// Get copy of current logging context
pub fn get_context() -> HashMap<String, String> {
    LOG_CONTEXT.read()
        .map(|context| context.clone())
        .unwrap_or_else(|_| HashMap::new())
}'''