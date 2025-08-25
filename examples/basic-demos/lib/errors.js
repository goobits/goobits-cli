/**
 * Error handling utilities for Demo Node.js CLI
 */

import util from 'util';

// Standard exit codes
const ExitCode = {
    SUCCESS: 0,
    GENERAL_ERROR: 1,
    USAGE_ERROR: 2,
    CONFIG_ERROR: 3,
    NETWORK_ERROR: 4,
    PERMISSION_ERROR: 5,
    FILE_NOT_FOUND: 6
};

class CliError extends Error {
    constructor(message, exitCode = ExitCode.GENERAL_ERROR, details = {}) {
        super(message);
        this.name = 'CliError';
        this.exitCode = exitCode;
        this.details = details;
        Error.captureStackTrace(this, CliError);
    }
}

class UsageError extends CliError {
    constructor(message, details = {}) {
        super(message, ExitCode.USAGE_ERROR, details);
        this.name = 'UsageError';
    }
}

class ConfigError extends CliError {
    constructor(message, details = {}) {
        super(message, ExitCode.CONFIG_ERROR, details);
        this.name = 'ConfigError';
    }
}

class NetworkError extends CliError {
    constructor(message, details = {}) {
        super(message, ExitCode.NETWORK_ERROR, details);
        this.name = 'NetworkError';
    }
}

class PermissionError extends CliError {
    constructor(message, details = {}) {
        super(message, ExitCode.PERMISSION_ERROR, details);
        this.name = 'PermissionError';
    }
}

class FileNotFoundError extends CliError {
    constructor(message, details = {}) {
        super(message, ExitCode.FILE_NOT_FOUND, details);
        this.name = 'FileNotFoundError';
    }
}

class ErrorHandler {
    constructor(options = {}) {
        this.debug = options.debug || false;
        this.verbose = options.verbose || options.debug || false;  // verbose includes debug functionality
    }

    handleError(error, context = null) {
        if (error instanceof CliError) {
            this._handleCliError(error, context);
        } else {
            this._handleUnexpectedError(error, context);
        }
    }

    _handleCliError(error, context) {
        let message = `Error: ${error.message}`;
        if (context) {
            message = `${context}: ${message}`;
        }

        console.error(message);

        if (this.verbose && Object.keys(error.details).length > 0) {
            console.error('Additional details:');
            for (const [key, value] of Object.entries(error.details)) {
                console.error(`  ${key}: ${value}`);
            }
        }

        if (this.verbose) {
            console.error(error.stack);
        }

        process.exit(error.exitCode);
    }

    _handleUnexpectedError(error, context) {
        let message = `Unexpected error: ${error.message}`;
        if (context) {
            message = `${context}: ${message}`;
        }

        console.error(message);

        if (this.verbose) {
            console.error(error.stack);
        } else {
            console.error('Run with --verbose for more details');
        }

        process.exit(ExitCode.GENERAL_ERROR);
    }

    warn(message, details = {}) {
        console.error(`Warning: ${message}`);

        if (this.verbose && Object.keys(details).length > 0) {
            for (const [key, value] of Object.entries(details)) {
                console.error(`  ${key}: ${value}`);
            }
        }
    }
}

function handleKeyboardInterrupt() {
    console.error('\nOperation cancelled by user');
    process.exit(ExitCode.GENERAL_ERROR);
}

// Set up global error handlers
process.on('SIGINT', handleKeyboardInterrupt);
process.on('SIGTERM', handleKeyboardInterrupt);

process.on('uncaughtException', (error) => {
    console.error('Uncaught Exception:', error);
    process.exit(ExitCode.GENERAL_ERROR);
});

process.on('unhandledRejection', (reason, promise) => {
    console.error('Unhandled Rejection at:', promise, 'reason:', reason);
    process.exit(ExitCode.GENERAL_ERROR);
});

// Global error handler instance
let _errorHandler = null;

function getErrorHandler() {
    if (!_errorHandler) {
        _errorHandler = new ErrorHandler();
    }
    return _errorHandler;
}

function setErrorHandler(handler) {
    _errorHandler = handler;
}

export {
    ExitCode,
    CliError,
    UsageError,
    ConfigError,
    NetworkError,
    PermissionError,
    FileNotFoundError,
    ErrorHandler,
    handleKeyboardInterrupt,
    getErrorHandler,
    setErrorHandler
};