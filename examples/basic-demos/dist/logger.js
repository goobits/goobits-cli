"use strict";
/**
 * Structured logging infrastructure for Demo TypeScript CLI.
 *
 * This module provides structured logging with context management and full TypeScript support.
 * Environment variables:
 * - LOG_LEVEL: Set logging level (debug, info, warn, error) - default: info
 * - LOG_OUTPUT: Set output destination (stdout, stderr, file:<path>) - default: stdout
 * - ENVIRONMENT: Set environment (production/development) - affects format
 */
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.setupLogging = setupLogging;
exports.getLogger = getLogger;
exports.setContext = setContext;
exports.setContext = setContext;
exports.clearContext = clearContext;
exports.updateContext = updateContext;
exports.getContext = getContext;
exports.removeContextKeys = removeContextKeys;
const async_hooks_1 = require("async_hooks");
const winston_1 = __importDefault(require("winston"));
const fs = __importStar(require("fs"));
const path = __importStar(require("path"));
// Context storage for async context management
const contextStorage = new async_hooks_1.AsyncLocalStorage();
// Custom formatter that outputs structured logs based on environment
const structuredFormatter = winston_1.default.format.printf(({ timestamp, level, message, ...meta }) => {
    const context = contextStorage.getStore() || {};
    const environment = process.env.ENVIRONMENT || 'development';
    const isProduction = environment.toLowerCase() === 'production' || environment.toLowerCase() === 'prod';
    const logData = {
        timestamp,
        level,
        message,
        ...meta
    };
    // Add context if available
    if (Object.keys(context).length > 0) {
        logData.context = context;
    }
    if (isProduction) {
        // JSON format for production
        return JSON.stringify(logData);
    }
    else {
        // Human-readable format for development
        const contextStr = Object.keys(context).length > 0
            ? ` [${Object.entries(context).map(([k, v]) => `${k}=${v}`).join(', ')}]`
            : '';
        const extraFields = Object.keys(meta).filter(key => !['timestamp', 'level', 'message', 'context'].includes(key));
        const extraStr = extraFields.length > 0
            ? ` ${JSON.stringify(extraFields.reduce((acc, key) => ({ ...acc, [key]: meta[key] }), {}))}`
            : '';
        return `${timestamp} ${level.toUpperCase().padEnd(8)} Demo TypeScript CLI.${message}${contextStr}${extraStr}`;
    }
});
// Create logger instance
let logger = null;
/**
 * Initialize structured logging for Demo TypeScript CLI.
 *
 * Environment Variables:
 * - LOG_LEVEL: Set logging level (debug, info, warn, error) - default: info
 * - LOG_OUTPUT: Set output destination (stdout, stderr, file:<path>) - default: stdout
 * - ENVIRONMENT: Set environment (production/development) - affects format
 */
function setupLogging() {
    const logLevel = process.env.LOG_LEVEL || 'info';
    const logOutput = process.env.LOG_OUTPUT || 'stdout';
    const transports = [];
    if (logOutput === 'stderr') {
        // All logs to stderr
        transports.push(new winston_1.default.transports.Console({
            stderrLevels: ['error', 'warn', 'info', 'debug'],
            format: winston_1.default.format.combine(winston_1.default.format.timestamp(), structuredFormatter)
        }));
    }
    else if (logOutput.startsWith('file:')) {
        // Log to file
        const logFile = logOutput.substring(5); // Remove 'file:' prefix
        const logDir = path.dirname(logFile);
        // Ensure log directory exists
        if (!fs.existsSync(logDir)) {
            fs.mkdirSync(logDir, { recursive: true });
        }
        transports.push(new winston_1.default.transports.File({
            filename: logFile,
            format: winston_1.default.format.combine(winston_1.default.format.timestamp(), structuredFormatter)
        }));
    }
    else if (logOutput === 'stdout') {
        // Container-friendly: info/debug to stdout, warn/error to stderr
        transports.push(new winston_1.default.transports.Console({
            level: 'info',
            stderrLevels: ['error', 'warn'],
            format: winston_1.default.format.combine(winston_1.default.format.timestamp(), structuredFormatter)
        }));
    }
    else {
        // Default to stdout for unknown options
        transports.push(new winston_1.default.transports.Console({
            format: winston_1.default.format.combine(winston_1.default.format.timestamp(), structuredFormatter)
        }));
    }
    logger = winston_1.default.createLogger({
        level: logLevel,
        transports,
        exitOnError: false
    });
    // Log startup message
    logger.info(`Logging initialized: level=${logLevel}, output=${logOutput}`);
}
/**
 * Get a logger instance with full TypeScript support.
 *
 * @param name - Logger name (module name)
 * @returns Winston logger instance with context support
 */
function getLogger(name = 'main') {
    if (!logger) {
        setupLogging();
    }
    // Return logger with context-aware methods and full typing
    return {
        debug: (message, meta = {}) => logger.debug(message, { module: name, ...meta }),
        info: (message, meta = {}) => logger.info(message, { module: name, ...meta }),
        warn: (message, meta = {}) => logger.warn(message, { module: name, ...meta }),
        error: (message, meta = {}) => logger.error(message, { module: name, ...meta }),
        // Context management methods
        setContext,
        clearContext,
        updateContext,
        getContext,
        removeContextKeys
    };
}
/**
 * Set logging context variables that will be included in all log messages within the current async context.
 *
 * @param contextData - Key-value pairs to add to logging context
 * @param callback - Function to execute with the context
 *
 * @example
 * ```typescript
 * setContext({ operationId: 'op_123', user: 'admin' }, () => {
 *     logger.info('Operation started'); // Will include context automatically
 * });
 *
 * // Async version
 * await setContext({ operationId: 'op_123' }, async () => {
 *     await someAsyncOperation();
 *     logger.info('Operation completed'); // Context included
 * });
 * ```
 */
function setContext(contextData, callback) {
    const currentContext = contextStorage.getStore() || {};
    const newContext = { ...currentContext, ...contextData };
    return contextStorage.run(newContext, callback);
}
function setContext(contextDataOrCallback, callback) {
    if (typeof contextDataOrCallback === 'function' && !callback) {
        // If only one function is provided, treat it as callback with empty context
        return contextStorage.run({}, contextDataOrCallback);
    }
    const contextData = contextDataOrCallback;
    const cb = callback;
    const currentContext = contextStorage.getStore() || {};
    const newContext = { ...currentContext, ...contextData };
    return contextStorage.run(newContext, cb);
}
/**
 * Clear all logging context variables.
 */
function clearContext() {
    contextStorage.run({}, () => { });
}
/**
 * Update existing context with new values.
 *
 * @param contextData - Key-value pairs to update in logging context
 */
function updateContext(contextData) {
    const currentContext = contextStorage.getStore() || {};
    const updatedContext = { ...currentContext, ...contextData };
    contextStorage.run(updatedContext, () => { });
}
/**
 * Get current logging context.
 *
 * @returns Current context object
 */
function getContext() {
    return { ...(contextStorage.getStore() || {}) };
}
/**
 * Remove specific keys from logging context.
 *
 * @param keys - Context keys to remove
 */
function removeContextKeys(...keys) {
    const currentContext = contextStorage.getStore() || {};
    const updatedContext = { ...currentContext };
    keys.forEach(key => {
        delete updatedContext[key];
    });
    contextStorage.run(updatedContext, () => { });
}
// Default export for convenience
exports.default = {
    setupLogging,
    getLogger,
    setContext,
    clearContext,
    updateContext,
    getContext,
    removeContextKeys
};
//# sourceMappingURL=logger.js.map