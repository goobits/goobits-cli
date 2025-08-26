/**
 * Structured logging infrastructure for Demo TypeScript CLI.
 *
 * This module provides structured logging with context management and full TypeScript support.
 * Environment variables:
 * - LOG_LEVEL: Set logging level (debug, info, warn, error) - default: info
 * - LOG_OUTPUT: Set output destination (stdout, stderr, file:<path>) - default: stdout
 * - ENVIRONMENT: Set environment (production/development) - affects format
 */
export interface LogContext {
    [key: string]: any;
}
export interface LogMeta {
    [key: string]: any;
}
export interface LoggerInstance {
    debug: (message: string, meta?: LogMeta) => void;
    info: (message: string, meta?: LogMeta) => void;
    warn: (message: string, meta?: LogMeta) => void;
    error: (message: string, meta?: LogMeta) => void;
    setContext: (contextData: LogContext, callback: () => void | Promise<void>) => void | Promise<void>;
    clearContext: () => void;
    updateContext: (contextData: LogContext) => void;
    getContext: () => LogContext;
    removeContextKeys: (...keys: string[]) => void;
}
export type LogLevel = 'debug' | 'info' | 'warn' | 'error';
export type LogOutput = 'stdout' | 'stderr' | string;
export type Environment = 'development' | 'production' | string;
/**
 * Initialize structured logging for Demo TypeScript CLI.
 *
 * Environment Variables:
 * - LOG_LEVEL: Set logging level (debug, info, warn, error) - default: info
 * - LOG_OUTPUT: Set output destination (stdout, stderr, file:<path>) - default: stdout
 * - ENVIRONMENT: Set environment (production/development) - affects format
 */
export declare function setupLogging(): void;
/**
 * Get a logger instance with full TypeScript support.
 *
 * @param name - Logger name (module name)
 * @returns Winston logger instance with context support
 */
export declare function getLogger(name?: string): LoggerInstance;
/**
 * Set context with only callback (overload for empty context).
 */
export declare function setContext(callback: () => void | Promise<void>): void | Promise<void>;
/**
 * Clear all logging context variables.
 */
export declare function clearContext(): void;
/**
 * Update existing context with new values.
 *
 * @param contextData - Key-value pairs to update in logging context
 */
export declare function updateContext(contextData: LogContext): void;
/**
 * Get current logging context.
 *
 * @returns Current context object
 */
export declare function getContext(): LogContext;
/**
 * Remove specific keys from logging context.
 *
 * @param keys - Context keys to remove
 */
export declare function removeContextKeys(...keys: string[]): void;
declare const _default: {
    setupLogging: typeof setupLogging;
    getLogger: typeof getLogger;
    setContext: typeof setContext;
    clearContext: typeof clearContext;
    updateContext: typeof updateContext;
    getContext: typeof getContext;
    removeContextKeys: typeof removeContextKeys;
};
export default _default;
//# sourceMappingURL=logger.d.ts.map