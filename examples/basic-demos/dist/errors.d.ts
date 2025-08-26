/**
 * Error handling utilities for Demo TypeScript CLI
 */
export declare enum ExitCode {
    SUCCESS = 0,
    GENERAL_ERROR = 1,
    USAGE_ERROR = 2,
    CONFIG_ERROR = 3,
    NETWORK_ERROR = 4,
    PERMISSION_ERROR = 5,
    FILE_NOT_FOUND = 6
}
export declare class CliError extends Error {
    readonly exitCode: ExitCode;
    readonly details: Record<string, any>;
    constructor(message: string, exitCode?: ExitCode, details?: Record<string, any>);
}
export declare class UsageError extends CliError {
    constructor(message: string, details?: Record<string, any>);
}
export declare class ConfigError extends CliError {
    constructor(message: string, details?: Record<string, any>);
}
export declare class NetworkError extends CliError {
    constructor(message: string, details?: Record<string, any>);
}
export declare class PermissionError extends CliError {
    constructor(message: string, details?: Record<string, any>);
}
export declare class FileNotFoundError extends CliError {
    constructor(message: string, details?: Record<string, any>);
}
interface ErrorHandlerOptions {
    debug?: boolean;
    verbose?: boolean;
}
export declare class ErrorHandler {
    private debug;
    private verbose;
    constructor(options?: ErrorHandlerOptions);
    handleError(error: Error, context?: string): never;
    private handleCliError;
    private handleUnexpectedError;
    warn(message: string, details?: Record<string, any>): void;
}
export declare function handleKeyboardInterrupt(): void;
export declare function getErrorHandler(): ErrorHandler;
export declare function setErrorHandler(handler: ErrorHandler): void;
export {};
//# sourceMappingURL=errors.d.ts.map