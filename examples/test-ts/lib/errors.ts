/**
 * Error handling implementation for Test TypeScript
 * Provides strongly-typed error management with Result pattern
 */

import chalk from 'chalk';

// Define enums and runtime values here (since they can't be imported from .d.ts files)
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
}

export enum ErrorSeverity {
  INFO = 'info',
  WARNING = 'warning', 
  ERROR = 'error',
  FATAL = 'fatal',
}

// Type definitions that match those in types/errors.d.ts
export interface CLIErrorData {
  readonly name: string;
  readonly message: string;
  readonly code: ExitCode;
  readonly severity: ErrorSeverity;
  readonly timestamp: string;
  readonly cause?: Error;
  readonly context?: Record<string, unknown>;
}

export type Result<T, E = CLIError> = {
  success: true;
  data: T;
} | {
  success: false;
  error: E;
};

export interface ErrorContext {
  command?: string;
  subcommand?: string;
  args?: string[];
  options?: Record<string, unknown>;
  workingDirectory?: string;
  environment?: Record<string, string>;
  commandName?: string;
  parameterName?: string;
  filePath?: string;
  metadata?: Record<string, unknown>;
  cause?: Error;
}

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
}

// === Type Guards Implementation ===

export function isSuccess<T, E extends CLIError>(result: Result<T, E>): result is Success<T> {
  return result.success === true;
}

export function isFailure<T, E extends CLIError>(result: Result<T, E>): result is Failure<E> {
  return result.success === false;
}

export function isErrorType<T extends CLIError>(
  error: CLIError,
  codes: readonly CLIErrorCode[]
): error is T {
  return codes.includes(error.code);
}

export function isRecoverable(error: CLIError): boolean {
  const recoverableCodes = [
    CLIErrorCode.COMMAND_TIMEOUT,
    CLIErrorCode.NETWORK_ERROR,
    CLIErrorCode.CONNECTION_FAILED,
    CLIErrorCode.REQUEST_TIMEOUT,
    CLIErrorCode.TEMPORARY_FAILURE,
  ];
  return recoverableCodes.includes(error.code);
}

export function isUserFacing(error: CLIError): boolean {
  const userFacingCodes = [
    CLIErrorCode.COMMAND_NOT_FOUND,
    CLIErrorCode.VALIDATION_FAILED,
    CLIErrorCode.INVALID_ARGUMENT,
    CLIErrorCode.INVALID_OPTION,
    CLIErrorCode.MISSING_REQUIRED,
    CLIErrorCode.CONFIG_NOT_FOUND,
    CLIErrorCode.FILE_NOT_FOUND,
    CLIErrorCode.PERMISSION_DENIED,
  ];
  return userFacingCodes.includes(error.code);
}

// === Result Pattern Utilities ===

export function success<T>(data: T, warnings?: readonly string[]): Success<T> {
  return {
    success: true,
    data,
    ...(warnings && { warnings }),
  };
}

export function failure<E extends CLIError>(error: E, recoverable = false): Failure<E> {
  return {
    success: false,
    error,
    recoverable,
  };
}

export async function asyncResult<T, E extends CLIError>(
  asyncFn: () => Promise<T>,
  errorHandler: (error: unknown) => E
): Promise<Result<T, E>> {
  try {
    const data = await asyncFn();
    return success(data);
  } catch (error) {
    const cliError = errorHandler(error);
    return failure(cliError, isRecoverable(cliError));
  }
}

export function syncResult<T, E extends CLIError>(
  syncFn: () => T,
  errorHandler: (error: unknown) => E
): Result<T, E> {
  try {
    const data = syncFn();
    return success(data);
  } catch (error) {
    const cliError = errorHandler(error);
    return failure(cliError, isRecoverable(cliError));
  }
}

// === Error Factory Functions ===

function createBaseError(
  code: CLIErrorCode,
  message: string,
  severity: ErrorSeverity = ErrorSeverity.ERROR,
  context?: ErrorContext
): BaseCLIError {
  return {
    code,
    message,
    severity,
    timestamp: new Date(),
    context: context?.metadata,
    stack: new Error().stack,
    cause: context?.cause,
  };
}

export const createCommandError: ErrorFactory<CommandError> = (message, context) => ({
  ...createBaseError(CLIErrorCode.COMMAND_FAILED, message, ErrorSeverity.ERROR, context),
  code: CLIErrorCode.COMMAND_FAILED,
  commandName: context?.commandName || 'unknown',
});

export const createValidationError: ErrorFactory<ValidationError> = (message, context) => ({
  ...createBaseError(CLIErrorCode.VALIDATION_FAILED, message, ErrorSeverity.ERROR, context),
  code: CLIErrorCode.VALIDATION_FAILED,
  parameterName: context?.parameterName || 'unknown',
  parameterValue: context?.metadata?.value,
  validationRule: context?.metadata?.rule as string || 'unknown',
  expectedType: context?.metadata?.expectedType as string,
  allowedValues: context?.metadata?.allowedValues as readonly unknown[],
});

export const createConfigError: ErrorFactory<ConfigError> = (message, context) => ({
  ...createBaseError(CLIErrorCode.CONFIG_INVALID, message, ErrorSeverity.ERROR, context),
  code: CLIErrorCode.CONFIG_INVALID,
  configPath: context?.filePath,
  configKey: context?.metadata?.key as string,
  validationErrors: context?.metadata?.validationErrors as readonly ValidationError[],
});

export const createHookError: ErrorFactory<HookError> = (message, context) => ({
  ...createBaseError(CLIErrorCode.HOOK_FAILED, message, ErrorSeverity.ERROR, context),
  code: CLIErrorCode.HOOK_FAILED,
  hookName: context?.metadata?.hookName as string || 'unknown',
  commandName: context?.commandName || 'unknown',
  executionTime: context?.metadata?.executionTime as number,
});

export const createPluginError: ErrorFactory<PluginError> = (message, context) => ({
  ...createBaseError(CLIErrorCode.PLUGIN_LOAD_FAILED, message, ErrorSeverity.ERROR, context),
  code: CLIErrorCode.PLUGIN_LOAD_FAILED,
  pluginName: context?.metadata?.pluginName as string || 'unknown',
  pluginPath: context?.filePath,
  version: context?.metadata?.version as string,
});

export const createFileSystemError: ErrorFactory<FileSystemError> = (message, context) => ({
  ...createBaseError(CLIErrorCode.FILE_NOT_FOUND, message, ErrorSeverity.ERROR, context),
  code: CLIErrorCode.FILE_NOT_FOUND,
  filePath: context?.filePath || 'unknown',
  operation: context?.metadata?.operation as FileSystemError['operation'] || 'read',
  permissions: context?.metadata?.permissions as string,
});

export const createNetworkError: ErrorFactory<NetworkError> = (message, context) => ({
  ...createBaseError(CLIErrorCode.NETWORK_ERROR, message, ErrorSeverity.ERROR, context),
  code: CLIErrorCode.NETWORK_ERROR,
  url: context?.metadata?.url as string,
  method: context?.metadata?.method as string,
  statusCode: context?.metadata?.statusCode as number,
  responseTime: context?.metadata?.responseTime as number,
});

export const createSystemError: ErrorFactory<SystemError> = (message, context) => ({
  ...createBaseError(CLIErrorCode.INTERNAL_ERROR, message, ErrorSeverity.FATAL, context),
  code: CLIErrorCode.INTERNAL_ERROR,
  systemCode: context?.metadata?.systemCode as string,
  signal: context?.metadata?.signal as string,
  resource: context?.metadata?.resource as string,
});

// === Error Formatters ===

const defaultFormatter: ErrorFormatter = (error, verbose = false) => {
  const userMessage = formatUserMessage(error);
  const developerMessage = verbose ? formatDeveloperMessage(error) : undefined;
  const suggestions = getSuggestions(error);
  const exitCode = getExitCode(error);

  return {
    userMessage,
    developerMessage,
    suggestions,
    exitCode,
  };
};

function formatUserMessage(error: CLIError): string {
  const prefix = getErrorPrefix(error.severity);
  
  switch (error.code) {
    case CLIErrorCode.COMMAND_NOT_FOUND:
      return `${prefix}Command not found: ${(error as CommandError).commandName}`;
    
    case CLIErrorCode.VALIDATION_FAILED:
    case CLIErrorCode.INVALID_ARGUMENT:
    case CLIErrorCode.INVALID_OPTION:
      const validationError = error as ValidationError;
      return `${prefix}Invalid ${validationError.parameterName}: ${error.message}`;
    
    case CLIErrorCode.MISSING_REQUIRED:
      return `${prefix}Required parameter missing: ${(error as ValidationError).parameterName}`;
    
    case CLIErrorCode.CONFIG_NOT_FOUND:
      return `${prefix}Configuration file not found`;
    
    case CLIErrorCode.CONFIG_INVALID:
      return `${prefix}Invalid configuration: ${error.message}`;
    
    case CLIErrorCode.FILE_NOT_FOUND:
      return `${prefix}File not found: ${(error as FileSystemError).filePath}`;
    
    case CLIErrorCode.PERMISSION_DENIED:
      return `${prefix}Permission denied`;
    
    case CLIErrorCode.HOOK_NOT_FOUND:
      const hookError = error as HookError;
      return `${prefix}Hook '${hookError.hookName}' not found for command '${hookError.commandName}'`;
    
    case CLIErrorCode.PLUGIN_LOAD_FAILED:
      return `${prefix}Failed to load plugin: ${(error as PluginError).pluginName}`;
    
    default:
      return `${prefix}${error.message}`;
  }
}

function formatDeveloperMessage(error: CLIError): string {
  let message = `[${error.code}] ${error.message}`;
  
  if (error.context) {
    message += `\nContext: ${JSON.stringify(error.context, null, 2)}`;
  }
  
  if (error.stack) {
    message += `\nStack trace:\n${error.stack}`;
  }
  
  if (error.cause) {
    message += `\nCaused by: ${error.cause instanceof Error ? error.cause.message : String(error.cause)}`;
    if (error.cause instanceof Error && error.cause.stack) {
      message += `\n${error.cause.stack}`;
    }
  }
  
  return message;
}

function getErrorPrefix(severity: ErrorSeverity): string {
  switch (severity) {
    case ErrorSeverity.INFO:
      return chalk.blue('ℹ ');
    case ErrorSeverity.WARNING:
      return chalk.yellow('⚠ ');
    case ErrorSeverity.ERROR:
      return chalk.red('✗ ');
    case ErrorSeverity.FATAL:
      return chalk.red.bold('💥 ');
    default:
      return '';
  }
}

function getSuggestions(error: CLIError): readonly string[] {
  switch (error.code) {
    case CLIErrorCode.COMMAND_NOT_FOUND:
      return [
        'Check the command spelling',
        'Run with --help to see available commands',
        'Make sure the command is installed and in your PATH',
      ];
    
    case CLIErrorCode.VALIDATION_FAILED:
      const validationError = error as ValidationError;
      const suggestions: string[] = [];
      
      if (validationError.expectedType) {
        suggestions.push(`Expected type: ${validationError.expectedType}`);
      }
      
      if (validationError.allowedValues?.length) {
        suggestions.push(`Allowed values: ${validationError.allowedValues.join(', ')}`);
      }
      
      return suggestions;
    
    case CLIErrorCode.CONFIG_NOT_FOUND:
      return [
        'Create a configuration file',
        'Check the configuration file path',
        'Run with --config to specify a custom config file',
      ];
    
    case CLIErrorCode.FILE_NOT_FOUND:
      return [
        'Check the file path spelling',
        'Ensure the file exists',
        'Check file permissions',
      ];
    
    case CLIErrorCode.PERMISSION_DENIED:
      return [
        'Check file permissions',
        'Run with appropriate privileges',
        'Ensure you have access to the resource',
      ];
    
    default:
      return [];
  }
}

function getExitCode(error: CLIError): ExitCode {
  switch (error.code) {
    case CLIErrorCode.COMMAND_NOT_FOUND:
      return ExitCode.COMMAND_NOT_FOUND;
    
    case CLIErrorCode.VALIDATION_FAILED:
    case CLIErrorCode.INVALID_ARGUMENT:
    case CLIErrorCode.INVALID_OPTION:
    case CLIErrorCode.MISSING_REQUIRED:
      return ExitCode.MISUSE_OF_SHELL_BUILTIN;
    
    case CLIErrorCode.CONFIG_NOT_FOUND:
    case CLIErrorCode.CONFIG_INVALID:
    case CLIErrorCode.CONFIG_LOAD_FAILED:
      return ExitCode.CONFIG_ERROR;
    
    case CLIErrorCode.FILE_NOT_FOUND:
    case CLIErrorCode.FILE_ACCESS_DENIED:
      return ExitCode.OS_FILE_MISSING;
    
    case CLIErrorCode.PERMISSION_DENIED:
      return ExitCode.PERMISSION_ERROR;
    
    case CLIErrorCode.NETWORK_ERROR:
    case CLIErrorCode.CONNECTION_FAILED:
      return ExitCode.SERVICE_UNAVAILABLE;
    
    case CLIErrorCode.INTERNAL_ERROR:
    case CLIErrorCode.UNKNOWN_ERROR:
      return ExitCode.SOFTWARE_ERROR;
    
    default:
      return ExitCode.GENERAL_ERROR;
  }
}

// === Error Manager Implementation ===

export class DefaultErrorManager implements ErrorManager {
  private handlers = new Map<CLIErrorCode, ErrorHandler>();
  private recoveries = new Map<CLIErrorCode, ErrorRecovery>();
  private formatters = new Map<CLIErrorCode, ErrorFormatter>();

  create<T extends CLIError>(
    factory: ErrorFactory<T>,
    message: string,
    context?: ErrorContext
  ): T {
    return factory(message, context);
  }

  async handle<T extends CLIError>(error: T, context?: ErrorContext, verbose = false): Promise<void> {
    const handler = this.handlers.get(error.code);
    if (handler) {
      await handler(error, context || {});
    } else {
      // Default error handling
      const formatted = this.format(error, verbose);
      
      if (formatted.developerMessage && verbose) {
        console.error(formatted.developerMessage);
      } else {
        console.error(formatted.userMessage);
      }
      
      if (formatted.suggestions.length > 0) {
        console.error(chalk.cyan('\nSuggestions:'));
        formatted.suggestions.forEach(suggestion => {
          console.error(chalk.cyan(`  • ${suggestion}`));
        });
      }
    }
  }

  async recover<T extends CLIError>(
    error: T,
    recovery: ErrorRecovery<T>,
    context?: ErrorContext
  ): Promise<Result<unknown, CLIError>> {
    const registeredRecovery = this.recoveries.get(error.code);
    if (registeredRecovery) {
      return await registeredRecovery(error, context || {});
    }
    return await recovery(error, context || {});
  }

  format<T extends CLIError>(error: T, verbose = false) {
    const formatter = this.formatters.get(error.code) || defaultFormatter;
    return formatter(error, verbose);
  }

  registerHandler<T extends CLIError>(
    errorType: CLIErrorCode,
    handler: ErrorHandler<T>
  ): void {
    this.handlers.set(errorType, handler as ErrorHandler);
  }

  registerRecovery<T extends CLIError>(
    errorType: CLIErrorCode,
    recovery: ErrorRecovery<T>
  ): void {
    this.recoveries.set(errorType, recovery as ErrorRecovery);
  }

  registerFormatter<T extends CLIError>(
    errorType: CLIErrorCode,
    formatter: ErrorFormatter<T>
  ): void {
    this.formatters.set(errorType, formatter as ErrorFormatter);
  }
}

// === Global Error Manager Instance ===

export const errorManager = new DefaultErrorManager();

// === Utility Functions ===

export function handleError(error: CLIError, context?: ErrorContext, verbose = false): never {
  errorManager.handle(error, context, verbose);
  const formatted = errorManager.format(error, verbose);
  process.exit(formatted.exitCode);
}

export function handleResult<T>(result: Result<T, CLIError>): T {
  if (isFailure(result)) {
    handleError(result.error);
  }
  return result.data;
}

export async function handleAsyncResult<T>(resultPromise: Promise<Result<T, CLIError>>): Promise<T> {
  const result = await resultPromise;
  return handleResult(result);
}

// Note: Types are already re-exported at the top of this file
// Runtime enums and classes are defined inline above