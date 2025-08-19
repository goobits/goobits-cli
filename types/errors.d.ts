/**
 * TypeScript error type definitions for TestTSCLI
 * Provides strongly-typed error handling
 */

// Exit codes enum
export enum ExitCode {
  SUCCESS = 0,
  GENERAL_ERROR = 1,
  MISUSE = 2,
  CONFIG_ERROR = 3,
  HOOK_ERROR = 4,
  PLUGIN_ERROR = 5,
  DEPENDENCY_ERROR = 6,
  NETWORK_ERROR = 7,
  SOFTWARE_ERROR = 70,
  FATAL_ERROR_SIGNAL_N = 128,
  SCRIPT_TERMINATED_BY_CTRL_C = 130,
  CANCELLED = 130
}

// Error severity levels
export enum ErrorSeverity {
  LOW = 'low',
  MEDIUM = 'medium',
  HIGH = 'high',
  CRITICAL = 'critical'
}

// CLI error codes for categorizing different types of errors
export enum CLIErrorCode {
  COMMAND_ERROR = 'COMMAND_ERROR',
  VALIDATION_ERROR = 'VALIDATION_ERROR',
  CONFIG_ERROR = 'CONFIG_ERROR',
  HOOK_ERROR = 'HOOK_ERROR',
  PLUGIN_ERROR = 'PLUGIN_ERROR',
  FILESYSTEM_ERROR = 'FILESYSTEM_ERROR',
  NETWORK_ERROR = 'NETWORK_ERROR',
  SYSTEM_ERROR = 'SYSTEM_ERROR',
  DEPENDENCY_ERROR = 'DEPENDENCY_ERROR',
  GENERAL_ERROR = 'GENERAL_ERROR'
}

// Base error interface
export interface CLIErrorData {
  readonly name: string;
  readonly message: string;
  readonly code: ExitCode;
  readonly severity: ErrorSeverity;
  readonly timestamp: string;
  readonly cause?: Error;
  readonly context?: Record<string, unknown>;
}

// Result type for error handling
export type Result<T, E = CLIError> = {
  success: true;
  data: T;
} | {
  success: false;
  error: E;
};

// Error handler function types
export type ErrorHandler<T = void> = (error: CLIError) => T;
export type AsyncErrorHandler<T = void> = (error: CLIError) => Promise<T>;

// Error recovery strategy
export interface ErrorRecoveryStrategy<T = unknown> {
  canRecover(error: CLIError): boolean;
  recover(error: CLIError): Promise<T>;
  maxRetries?: number;
}

// Global error handler options
export interface GlobalErrorHandlerOptions {
  showStack?: boolean;
  colorize?: boolean;
  exitOnError?: boolean;
  logLevel?: 'debug' | 'info' | 'warn' | 'error';
}

// Error context for debugging
export interface ErrorContext {
  command?: string;
  subcommand?: string;
  args?: string[];
  options?: Record<string, unknown>;
  workingDirectory?: string;
  environment?: Record<string, string>;
}

// Validation error details
export interface ValidationErrorDetail {
  field: string;
  value: unknown;
  constraint: string;
  message: string;
}

// Dependency information
export interface DependencyInfo {
  name: string;
  version?: string;
  required: boolean;
  installCommand?: string;
}

// Error classes
export declare class CLIError extends Error {
  readonly code: ExitCode;
  readonly severity: ErrorSeverity;
  readonly timestamp: string;
  readonly cause?: Error;
  readonly context?: ErrorContext;

  constructor(
    message: string,
    code?: ExitCode,
    severity?: ErrorSeverity,
    cause?: Error,
    context?: ErrorContext
  );

  toJSON(): CLIErrorData;
  withContext(context: ErrorContext): CLIError;
  withCause(cause: Error): CLIError;
}

export declare class ConfigError extends CLIError {
  readonly configPath?: string;
  readonly configSection?: string;

  constructor(
    message: string,
    configPath?: string,
    configSection?: string,
    cause?: Error
  );
}

export declare class HookError extends CLIError {
  readonly hookName: string;
  readonly hookPhase?: string;

  constructor(
    hookName: string,
    message: string,
    hookPhase?: string,
    cause?: Error
  );
}

export declare class PluginError extends CLIError {
  readonly pluginName: string;
  readonly pluginVersion?: string;

  constructor(
    pluginName: string,
    message: string,
    pluginVersion?: string,
    cause?: Error
  );
}

export declare class ValidationError extends CLIError {
  readonly errors: ValidationErrorDetail[];

  constructor(errors: ValidationErrorDetail[], cause?: Error);
  constructor(field: string, value: unknown, message: string, cause?: Error);
}

export declare class DependencyError extends CLIError {
  readonly dependencies: DependencyInfo[];

  constructor(dependencies: DependencyInfo[], cause?: Error);
  constructor(dependency: string, message: string, cause?: Error);
}

export declare class NetworkError extends CLIError {
  readonly url?: string;
  readonly statusCode?: number;

  constructor(
    message: string,
    url?: string,
    statusCode?: number,
    cause?: Error
  );
}

export declare class CancelledError extends CLIError {
  constructor(message?: string);
}

export declare class SystemError extends CLIError {
  readonly filePath?: string;
  readonly metadata?: Record<string, unknown>;

  constructor(
    message: string,
    context?: { filePath?: string; cause?: Error; metadata?: Record<string, unknown> }
  );
}

export declare class CommandError extends CLIError {
  readonly commandName: string;

  constructor(
    commandName: string,
    message: string,
    cause?: Error
  );
}

export declare class FileSystemError extends CLIError {
  readonly filePath: string;
  readonly operation?: string;

  constructor(
    message: string,
    context: { filePath: string; operation?: string; cause?: Error; metadata?: Record<string, unknown> }
  );
}

// Utility functions
export declare function handleError(
  error: CLIError,
  options?: { exit?: boolean; log?: boolean }
): CLIError;

export declare function asyncErrorHandler<T extends (...args: any[]) => Promise<any>>(
  fn: T
): T;

export declare function errorHandler<T extends (...args: any[]) => any>(
  fn: T
): T;

export declare function setupGlobalErrorHandlers(
  options?: GlobalErrorHandlerOptions
): {
  handleError: ErrorHandler<CLIError>;
  asyncErrorHandler: typeof asyncErrorHandler;
  errorHandler: typeof errorHandler;
};

export declare function createResult<T>(data: T): Result<T, never>;
export declare function createError<E extends CLIError>(error: E): Result<never, E>;

export declare function isResult<T, E extends CLIError>(
  value: unknown
): value is Result<T, E>;

export declare function unwrapResult<T, E extends CLIError>(
  result: Result<T, E>
): T;

export declare function mapResult<T, U, E extends CLIError>(
  result: Result<T, E>,
  mapper: (data: T) => U
): Result<U, E>;

export declare function chainResult<T, U, E extends CLIError>(
  result: Result<T, E>,
  mapper: (data: T) => Result<U, E>
): Result<U, E>;

export declare function createErrorWithSuggestions(
  message: string,
  suggestions: string[]
): CLIError;

export declare function validateDependencies(
  dependencies: (string | DependencyInfo)[]
): Promise<void>;

export declare function retryOperation<T>(
  operation: () => Promise<T>,
  options?: {
    maxRetries?: number;
    baseDelay?: number;
    maxDelay?: number;
    backoffFactor?: number;
    strategy?: ErrorRecoveryStrategy<T>;
  }
): Promise<T>;