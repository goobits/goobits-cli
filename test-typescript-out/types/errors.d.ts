/**
 * TypeScript error type definitions for Test TypeScript CLI
 * Provides strongly-typed error handling
 */

// Exit codes enum - Extended with comprehensive codes
export enum ExitCode {
  SUCCESS = 0,
  GENERAL_ERROR = 1,
  MISUSE_OF_SHELL_BUILTIN = 2,
  CONFIG_ERROR = 3,
  COMMAND_NOT_FOUND = 127,
  OS_FILE_MISSING = 66,
  PERMISSION_ERROR = 77,
  SERVICE_UNAVAILABLE = 69,
  SOFTWARE_ERROR = 70,
  SCRIPT_TERMINATED_BY_CTRL_C = 130,
  FATAL_ERROR_SIGNAL_N = 128,
  
  // Legacy aliases
  MISUSE = 2,
  HOOK_ERROR = 4,
  PLUGIN_ERROR = 5,
  DEPENDENCY_ERROR = 6,
  NETWORK_ERROR = 7,
  CANCELLED = 130
}

// Error severity levels - Extended with comprehensive levels
export enum ErrorSeverity {
  INFO = 'info',
  WARNING = 'warning', 
  ERROR = 'error',
  FATAL = 'fatal',
  
  // Legacy aliases
  LOW = 'info',
  MEDIUM = 'warning',
  HIGH = 'error',
  CRITICAL = 'fatal'
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

// Comprehensive error context for debugging and error handling
export interface ErrorContext {
  command?: string;
  subcommand?: string;
  args?: string[];
  options?: Record<string, unknown>;
  workingDirectory?: string;
  environment?: Record<string, string>;
  
  // Additional context fields expected by lib/errors.ts
  commandName?: string;
  parameterName?: string;
  filePath?: string;
  metadata?: Record<string, unknown>;
  cause?: Error;
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
  readonly code: CLIErrorCode.CONFIG_INVALID;
  readonly configPath?: string;
  readonly configKey?: string;
  readonly configSection?: string;
  readonly validationErrors?: readonly ValidationError[];

  constructor(
    message: string,
    configPath?: string,
    configSection?: string,
    cause?: Error
  );
}

export declare class HookError extends CLIError {
  readonly code: CLIErrorCode.HOOK_FAILED;
  readonly hookName: string;
  readonly commandName: string;
  readonly hookPhase?: string;
  readonly executionTime?: number;

  constructor(
    hookName: string,
    message: string,
    hookPhase?: string,
    cause?: Error
  );
}

export declare class PluginError extends CLIError {
  readonly code: CLIErrorCode.PLUGIN_LOAD_FAILED;
  readonly pluginName: string;
  readonly pluginPath?: string;
  readonly pluginVersion?: string;
  readonly version?: string;

  constructor(
    pluginName: string,
    message: string,
    pluginVersion?: string,
    cause?: Error
  );
}

export declare class ValidationError extends CLIError {
  readonly code: CLIErrorCode.VALIDATION_FAILED;
  readonly parameterName: string;
  readonly parameterValue?: unknown;
  readonly validationRule: string;
  readonly expectedType?: string;
  readonly allowedValues?: readonly unknown[];
  readonly errors?: ValidationErrorDetail[];

  constructor(errors: ValidationErrorDetail[], cause?: Error);
  constructor(field: string, value: unknown, message: string, cause?: Error);
}

export declare class DependencyError extends CLIError {
  readonly dependencies: DependencyInfo[];

  constructor(dependencies: DependencyInfo[], cause?: Error);
  constructor(dependency: string, message: string, cause?: Error);
}

export declare class NetworkError extends CLIError {
  readonly code: CLIErrorCode.NETWORK_ERROR;
  readonly url?: string;
  readonly method?: string;
  readonly statusCode?: number;
  readonly responseTime?: number;

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
  readonly code: CLIErrorCode.INTERNAL_ERROR;
  readonly systemCode?: string;
  readonly signal?: string; 
  readonly resource?: string;
  readonly system?: string;
  readonly command?: string;

  constructor(
    message: string,
    system?: string,
    command?: string,
    cause?: Error
  );
}

export declare class CommandError extends CLIError {
  readonly code: CLIErrorCode.COMMAND_FAILED;
  readonly commandName: string;
  readonly exitCode?: number;

  constructor(
    commandName: string,
    message: string,
    exitCode?: number,
    cause?: Error
  );
}

export declare class FileSystemError extends CLIError {
  readonly code: CLIErrorCode.FILE_NOT_FOUND;
  readonly filePath: string;
  readonly operation: 'read' | 'write' | 'delete' | 'create' | 'access' | 'stat';
  readonly permissions?: string;

  constructor(
    filePath: string,
    operation: 'read' | 'write' | 'delete' | 'create' | 'access' | 'stat',
    message: string,
    cause?: Error
  );
}

// Additional Result type variants
export type Success<T> = {
  success: true;
  data: T;
};

export type Failure<E> = {
  success: false;
  error: E;
};

// Comprehensive error code enum
export enum CLIErrorCode {
  // General errors
  UNKNOWN_ERROR = 'UNKNOWN_ERROR',
  INTERNAL_ERROR = 'INTERNAL_ERROR',
  
  // Command errors  
  COMMAND_NOT_FOUND = 'COMMAND_NOT_FOUND',
  COMMAND_FAILED = 'COMMAND_FAILED',
  COMMAND_TIMEOUT = 'COMMAND_TIMEOUT',
  
  // Validation errors
  VALIDATION_FAILED = 'VALIDATION_FAILED',
  INVALID_ARGUMENT = 'INVALID_ARGUMENT', 
  INVALID_OPTION = 'INVALID_OPTION',
  MISSING_REQUIRED = 'MISSING_REQUIRED',
  
  // Configuration errors
  CONFIG_NOT_FOUND = 'CONFIG_NOT_FOUND',
  CONFIG_INVALID = 'CONFIG_INVALID',
  CONFIG_LOAD_FAILED = 'CONFIG_LOAD_FAILED',
  
  // File system errors
  FILE_NOT_FOUND = 'FILE_NOT_FOUND',
  FILE_ACCESS_DENIED = 'FILE_ACCESS_DENIED',
  PERMISSION_DENIED = 'PERMISSION_DENIED',
  
  // Hook errors
  HOOK_NOT_FOUND = 'HOOK_NOT_FOUND',
  HOOK_FAILED = 'HOOK_FAILED',
  
  // Plugin errors
  PLUGIN_LOAD_FAILED = 'PLUGIN_LOAD_FAILED',
  PLUGIN_FAILED = 'PLUGIN_FAILED',
  
  // Network errors  
  NETWORK_ERROR = 'NETWORK_ERROR',
  CONNECTION_FAILED = 'CONNECTION_FAILED',
  REQUEST_TIMEOUT = 'REQUEST_TIMEOUT',
  TEMPORARY_FAILURE = 'TEMPORARY_FAILURE',
  
  // Legacy aliases for compatibility
  UNKNOWN = 'UNKNOWN_ERROR',
  INVALID_INPUT = 'INVALID_ARGUMENT',
  MISSING_DEPENDENCY = 'CONFIG_LOAD_FAILED',
  INVALID_COMMAND = 'COMMAND_FAILED',
  FILE_WRITE_ERROR = 'FILE_ACCESS_DENIED',
  SYSTEM_ERROR = 'INTERNAL_ERROR',
  CONFIG_PARSE_ERROR = 'CONFIG_INVALID',
  HOOK_EXECUTION_ERROR = 'HOOK_FAILED',
  PLUGIN_NOT_FOUND = 'PLUGIN_LOAD_FAILED',
  PLUGIN_LOAD_ERROR = 'PLUGIN_LOAD_FAILED',
  PLUGIN_EXECUTION_ERROR = 'PLUGIN_FAILED',
  VALIDATION_ERROR = 'VALIDATION_FAILED',
  TYPE_ERROR = 'VALIDATION_FAILED'
}

// Error factory types - Enhanced for comprehensive error handling
export type ErrorFactory<T extends CLIError> = (
  message: string,
  context?: ErrorContext
) => T;

// Enhanced error management interfaces
export interface ErrorManager {
  create<T extends CLIError>(factory: ErrorFactory<T>, message: string, context?: ErrorContext): T;
  handle<T extends CLIError>(error: T, context?: ErrorContext, verbose?: boolean): Promise<void>;
  recover<T extends CLIError>(error: T, recovery: ErrorRecovery<T>, context?: ErrorContext): Promise<Result<unknown, CLIError>>;
  format<T extends CLIError>(error: T, verbose?: boolean): {
    userMessage: string;
    developerMessage?: string;
    suggestions: readonly string[];
    exitCode: ExitCode;
  };
  registerHandler<T extends CLIError>(errorType: CLIErrorCode, handler: ErrorHandler<T>): void;
  registerRecovery<T extends CLIError>(errorType: CLIErrorCode, recovery: ErrorRecovery<T>): void;
  registerFormatter<T extends CLIError>(errorType: CLIErrorCode, formatter: ErrorFormatter<T>): void;
}

export interface ErrorFormatter<T extends CLIError = CLIError> {
  (error: T, verbose?: boolean): {
    userMessage: string;
    developerMessage?: string; 
    suggestions: readonly string[];
    exitCode: ExitCode;
  };
}

export interface ErrorHandler<T extends CLIError = CLIError> {
  (error: T, context: ErrorContext): Promise<void> | void;
}

export interface ErrorRecovery<T extends CLIError = CLIError> {
  (error: T, context: ErrorContext): Promise<Result<unknown, CLIError>>;
}

// Base error class alias
export type BaseCLIError = CLIError;

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

// Error creator functions
export declare function createSystemError(
  message: string,
  context?: {
    cause?: Error;
    metadata?: Record<string, unknown>;
  }
): SystemError;

export declare function createCommandError(
  message: string,
  context?: {
    cause?: Error;
    metadata?: Record<string, unknown>;
  }
): CommandError;

export declare function createFileSystemError(
  message: string,
  context?: {
    cause?: Error;
    metadata?: Record<string, unknown>;
  }
): FileSystemError;

export declare function createConfigError(
  message: string,
  context?: {
    cause?: Error;
    metadata?: Record<string, unknown>;
  }
): ConfigError;

export declare function createHookError(
  message: string,
  context?: {
    cause?: Error;
    metadata?: Record<string, unknown>;
  }
): HookError;

export declare function createPluginError(
  message: string,
  context?: {
    cause?: Error;
    metadata?: Record<string, unknown>;
  }
): PluginError;

export declare function createValidationError(
  message: string,
  context?: {
    cause?: Error;
    metadata?: Record<string, unknown>;
  }
): ValidationError;

export declare function createNetworkError(
  message: string,
  context?: {
    cause?: Error;
    metadata?: Record<string, unknown>;
  }
): NetworkError;

// Result pattern utility functions
export declare function success<T>(data: T, warnings?: readonly string[]): Success<T>;
export declare function failure<E extends CLIError>(error: E, recoverable?: boolean): Failure<E>;
export declare function isSuccess<T, E extends CLIError>(result: Result<T, E>): result is Success<T>;
export declare function isFailure<T, E extends CLIError>(result: Result<T, E>): result is Failure<E>;

// Result pattern async utilities
export declare function asyncResult<T, E extends CLIError>(
  operation: () => Promise<T>,
  errorHandler: (error: unknown) => E
): Promise<Result<T, E>>;

export declare function syncResult<T, E extends CLIError>(
  operation: () => T,
  errorHandler: (error: unknown) => E
): Result<T, E>;