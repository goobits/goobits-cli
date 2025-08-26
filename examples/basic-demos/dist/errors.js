"use strict";
/**
 * Error handling utilities for Demo TypeScript CLI
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.ErrorHandler = exports.FileNotFoundError = exports.PermissionError = exports.NetworkError = exports.ConfigError = exports.UsageError = exports.CliError = exports.ExitCode = void 0;
exports.handleKeyboardInterrupt = handleKeyboardInterrupt;
exports.getErrorHandler = getErrorHandler;
exports.setErrorHandler = setErrorHandler;
// Standard exit codes
var ExitCode;
(function (ExitCode) {
    ExitCode[ExitCode["SUCCESS"] = 0] = "SUCCESS";
    ExitCode[ExitCode["GENERAL_ERROR"] = 1] = "GENERAL_ERROR";
    ExitCode[ExitCode["USAGE_ERROR"] = 2] = "USAGE_ERROR";
    ExitCode[ExitCode["CONFIG_ERROR"] = 3] = "CONFIG_ERROR";
    ExitCode[ExitCode["NETWORK_ERROR"] = 4] = "NETWORK_ERROR";
    ExitCode[ExitCode["PERMISSION_ERROR"] = 5] = "PERMISSION_ERROR";
    ExitCode[ExitCode["FILE_NOT_FOUND"] = 6] = "FILE_NOT_FOUND";
})(ExitCode || (exports.ExitCode = ExitCode = {}));
class CliError extends Error {
    constructor(message, exitCode = ExitCode.GENERAL_ERROR, details = {}) {
        super(message);
        this.name = 'CliError';
        this.exitCode = exitCode;
        this.details = details;
        Error.captureStackTrace(this, CliError);
    }
}
exports.CliError = CliError;
class UsageError extends CliError {
    constructor(message, details = {}) {
        super(message, ExitCode.USAGE_ERROR, details);
        this.name = 'UsageError';
    }
}
exports.UsageError = UsageError;
class ConfigError extends CliError {
    constructor(message, details = {}) {
        super(message, ExitCode.CONFIG_ERROR, details);
        this.name = 'ConfigError';
    }
}
exports.ConfigError = ConfigError;
class NetworkError extends CliError {
    constructor(message, details = {}) {
        super(message, ExitCode.NETWORK_ERROR, details);
        this.name = 'NetworkError';
    }
}
exports.NetworkError = NetworkError;
class PermissionError extends CliError {
    constructor(message, details = {}) {
        super(message, ExitCode.PERMISSION_ERROR, details);
        this.name = 'PermissionError';
    }
}
exports.PermissionError = PermissionError;
class FileNotFoundError extends CliError {
    constructor(message, details = {}) {
        super(message, ExitCode.FILE_NOT_FOUND, details);
        this.name = 'FileNotFoundError';
    }
}
exports.FileNotFoundError = FileNotFoundError;
class ErrorHandler {
    constructor(options = {}) {
        this.debug = options.debug || false;
        this.verbose = options.verbose || options.debug || false; // verbose includes debug functionality
    }
    handleError(error, context) {
        if (error instanceof CliError) {
            this.handleCliError(error, context);
        }
        else {
            this.handleUnexpectedError(error, context);
        }
        // TypeScript requires this even though we never reach here
        process.exit(ExitCode.GENERAL_ERROR);
    }
    handleCliError(error, context) {
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
    handleUnexpectedError(error, context) {
        let message = `Unexpected error: ${error.message}`;
        if (context) {
            message = `${context}: ${message}`;
        }
        console.error(message);
        if (this.verbose) {
            console.error(error.stack);
        }
        else {
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
exports.ErrorHandler = ErrorHandler;
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
//# sourceMappingURL=errors.js.map