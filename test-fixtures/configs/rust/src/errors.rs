use std::fmt;
use std::process;

#[derive(Debug, Clone, Copy)]
/// Application exit codes
pub enum ExitCode {
    /// Successful execution
    Success = 0,
    /// General error
    GeneralError = 1,
    /// Usage error
    UsageError = 2,
    /// Configuration error
    ConfigError = 3,
    /// Network error
    NetworkError = 4,
    /// Permission error
    PermissionError = 5,
    /// File not found error
    FileNotFound = 6,
}

impl ExitCode {
    /// Convert exit code to i32
    pub fn as_i32(&self) -> i32 {
        *self as i32
    }
}

#[derive(Debug)]
/// CLI error structure
pub struct CliError {
    message: String,
    exit_code: ExitCode,
    details: std::collections::HashMap<String, String>,
}

impl CliError {
    pub fn new(message: String, exit_code: ExitCode) -> Self {
        Self {
            message,
            exit_code,
            details: std::collections::HashMap::new(),
        }
    }

    pub fn with_details(mut self, details: std::collections::HashMap<String, String>) -> Self {
        self.details = details;
        self
    }

    pub fn add_detail<K: Into<String>, V: Into<String>>(mut self, key: K, value: V) -> Self {
        self.details.insert(key.into(), value.into());
        self
    }

    pub fn exit_code(&self) -> ExitCode {
        self.exit_code
    }

    pub fn details(&self) -> &std::collections::HashMap<String, String> {
        &self.details
    }
}

impl fmt::Display for CliError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "{}", self.message)
    }
}

impl std::error::Error for CliError {}

// Convenience constructors
pub fn usage_error(message: String) -> CliError {
    CliError::new(message, ExitCode::UsageError)
}

pub fn config_error(message: String) -> CliError {
    CliError::new(message, ExitCode::ConfigError)
}

pub fn network_error(message: String) -> CliError {
    CliError::new(message, ExitCode::NetworkError)
}

pub fn permission_error(message: String) -> CliError {
    CliError::new(message, ExitCode::PermissionError)
}

pub fn file_not_found_error(message: String) -> CliError {
    CliError::new(message, ExitCode::FileNotFound)
}

pub struct ErrorHandler {
    _debug: bool,
    verbose: bool,
}

impl ErrorHandler {
    pub fn new(debug: bool, verbose: bool) -> Self {
        Self { _debug: debug, verbose: verbose || debug }  // verbose includes debug functionality
    }

    pub fn handle_error(&self, error: &dyn std::error::Error, context: Option<&str>) -> ! {
        // For simplicity, always handle as unexpected error
        // In practice, we'd use proper error types
        self.handle_unexpected_error(error, context);
    }
    
    pub fn handle_cli_error_direct(&self, error: &CliError, context: Option<&str>) -> ! {
        self.handle_cli_error(error, context);
    }

    fn handle_cli_error(&self, error: &CliError, context: Option<&str>) -> ! {
        let message = if let Some(ctx) = context {
            format!("{}: Error: {}", ctx, error.message)
        } else {
            format!("Error: {}", error.message)
        };

        eprintln!("{}", message);

        if self.verbose && !error.details.is_empty() {
            eprintln!("Additional details:");
            for (key, value) in &error.details {
                eprintln!("  {}: {}", key, value);
            }
        }

        if self.verbose {
            eprintln!("{:?}", error);
        }

        process::exit(error.exit_code.as_i32());
    }

    fn handle_unexpected_error(&self, error: &dyn std::error::Error, context: Option<&str>) -> ! {
        let message = if let Some(ctx) = context {
            format!("{}: Unexpected error: {}", ctx, error)
        } else {
            format!("Unexpected error: {}", error)
        };

        eprintln!("{}", message);

        if self.verbose {
            eprintln!("{:?}", error);
        } else {
            eprintln!("Run with --verbose for more details");
        }

        process::exit(ExitCode::GeneralError.as_i32());
    }

    pub fn warn(&self, message: &str, details: Option<&std::collections::HashMap<String, String>>) {
        eprintln!("Warning: {}", message);

        if self.verbose {
            if let Some(detail_map) = details {
                for (key, value) in detail_map {
                    eprintln!("  {}: {}", key, value);
                }
            }
        }
    }
}

pub fn handle_keyboard_interrupt() -> ! {
    eprintln!("\nOperation cancelled by user");
    process::exit(ExitCode::GeneralError.as_i32());
}

// Global error handler
static mut ERROR_HANDLER: Option<ErrorHandler> = None;
static mut ERROR_HANDLER_INIT: std::sync::Once = std::sync::Once::new();

pub fn get_error_handler() -> &'static ErrorHandler {
    unsafe {
        ERROR_HANDLER_INIT.call_once(|| {
            ERROR_HANDLER = Some(ErrorHandler::new(false, false));
        });
        ERROR_HANDLER.as_ref().unwrap()
    }
}

pub fn set_error_handler(handler: ErrorHandler) {
    unsafe {
        ERROR_HANDLER = Some(handler);
    }
}

// Result type alias for convenience
pub type CliResult<T> = Result<T, CliError>;