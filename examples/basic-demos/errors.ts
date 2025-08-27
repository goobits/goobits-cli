/**
 * Error handling utilities for Demo TypeScript CLI
 */

// Standard exit codes
export enum ExitCode {
    SUCCESS = 0,
    GENERAL_ERROR = 1,
    USAGE_ERROR = 2,
    CONFIG_ERROR = 3,
    NETWORK_ERROR = 4,
    PERMISSION_ERROR = 5,
    FILE_NOT_FOUND = 6
}

export class CliError extends Error {
    public readonly exitCode: ExitCode;
    public readonly details: Record<string, any>;

    constructor(message: string, exitCode: ExitCode = ExitCode.GENERAL_ERROR, details: Record<string, any> = {}) {
        super(message);
        this.name = 'CliError';
        this.exitCode = exitCode;
        this.details = details;
        Error.captureStackTrace(this, CliError);
    }
}

export class UsageError extends CliError {
    constructor(message: string, details: Record<string, any> = {}) {
        super(message, ExitCode.USAGE_ERROR, details);
        this.name = 'UsageError';
    }
}

export class ConfigError extends CliError {
    constructor(message: string, details: Record<string, any> = {}) {
        super(message, ExitCode.CONFIG_ERROR, details);
        this.name = 'ConfigError';
    }
}

export class NetworkError extends CliError {
    constructor(message: string, details: Record<string, any> = {}) {
        super(message, ExitCode.NETWORK_ERROR, details);
        this.name = 'NetworkError';
    }
}

export class PermissionError extends CliError {
    constructor(message: string, details: Record<string, any> = {}) {
        super(message, ExitCode.PERMISSION_ERROR, details);
        this.name = 'PermissionError';
    }
}

export class FileNotFoundError extends CliError {
    constructor(message: string, details: Record<string, any> = {}) {
        super(message, ExitCode.FILE_NOT_FOUND, details);
        this.name = 'FileNotFoundError';
    }
}

interface ErrorHandlerOptions {
    debug?: boolean;
    verbose?: boolean;
}

export class ErrorHandler {
    private debug: boolean;
    private verbose: boolean;

    constructor(options: ErrorHandlerOptions = {}) {
        this.debug = options.debug || false;
        this.verbose = options.verbose || options.debug || false;  // verbose includes debug functionality
    }

    public handleError(error: Error, context?: string): never {
        if (error instanceof CliError) {
            this.handleCliError(error, context);
        } else {
            this.handleUnexpectedError(error, context);
        }
        // TypeScript requires this even though we never reach here
        process.exit(ExitCode.GENERAL_ERROR);
    }

    private handleCliError(error: CliError, context?: string): never {
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

    private handleUnexpectedError(error: Error, context?: string): never {
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

    public warn(message: string, details: Record<string, any> = {}): void {
        console.error(`Warning: ${message}`);

        if (this.verbose && Object.keys(details).length > 0) {
            for (const [key, value] of Object.entries(details)) {
                console.error(`  ${key}: ${value}`);
            }
        }
    }
}

export function handleKeyboardInterrupt(): void {
    console.error('\nOperation cancelled by user');
    process.exit(ExitCode.GENERAL_ERROR);
}

// Set up global error handlers
process.on('SIGINT', handleKeyboardInterrupt);
process.on('SIGTERM', handleKeyboardInterrupt);

process.on('uncaughtException', (error: Error) => {
    console.error('Uncaught Exception:', error);
    process.exit(ExitCode.GENERAL_ERROR);
});

process.on('unhandledRejection', (reason: any, promise: Promise<any>) => {
    console.error('Unhandled Rejection at:', promise, 'reason:', reason);
    process.exit(ExitCode.GENERAL_ERROR);
});

// Global error handler instance
let _errorHandler: ErrorHandler | null = null;

export function getErrorHandler(): ErrorHandler {
    if (!_errorHandler) {
        _errorHandler = new ErrorHandler();
    }
    return _errorHandler;
}

export function setErrorHandler(handler: ErrorHandler): void {
    _errorHandler = handler;
}