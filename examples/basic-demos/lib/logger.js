/**
 * Structured logging infrastructure for Demo Node.js CLI.
 * 
 * This module provides structured logging with context management using AsyncLocalStorage.
 * Environment variables:
 * - LOG_LEVEL: Set logging level (debug, info, warn, error) - default: info
 * - LOG_OUTPUT: Set output destination (stdout, stderr, file:<path>) - default: stdout
 * - ENVIRONMENT: Set environment (production/development) - affects format
 */

const { AsyncLocalStorage } = require('async_hooks');
const winston = require('winston');
const fs = require('fs');
const path = require('path');

// Context storage for async context management
const contextStorage = new AsyncLocalStorage();

// Custom formatter that outputs structured logs based on environment
const structuredFormatter = winston.format.printf(({ timestamp, level, message, ...meta }) => {
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
    } else {
        // Human-readable format for development
        const contextStr = Object.keys(context).length > 0 
            ? ` [${Object.entries(context).map(([k, v]) => `${k}=${v}`).join(', ')}]` 
            : '';
        
        const extraFields = Object.keys(meta).filter(key => 
            !['timestamp', 'level', 'message', 'context'].includes(key)
        );
        const extraStr = extraFields.length > 0 
            ? ` ${JSON.stringify(extraFields.reduce((acc, key) => ({ ...acc, [key]: meta[key] }), {}))}` 
            : '';
        
        return `${timestamp} ${level.toUpperCase().padEnd(8)} Demo Node.js CLI.${message}${contextStr}${extraStr}`;
    }
});

// Create logger instance
let logger = null;

/**
 * Initialize structured logging for Demo Node.js CLI.
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
        transports.push(new winston.transports.Console({ 
            stderrLevels: ['error', 'warn', 'info', 'debug'],
            format: winston.format.combine(
                winston.format.timestamp(),
                structuredFormatter
            )
        }));
    } else if (logOutput.startsWith('file:')) {
        // Log to file
        const logFile = logOutput.substring(5); // Remove 'file:' prefix
        const logDir = path.dirname(logFile);
        
        // Ensure log directory exists
        if (!fs.existsSync(logDir)) {
            fs.mkdirSync(logDir, { recursive: true });
        }
        
        transports.push(new winston.transports.File({
            filename: logFile,
            format: winston.format.combine(
                winston.format.timestamp(),
                structuredFormatter
            )
        }));
    } else if (logOutput === 'stdout') {
        // Container-friendly: info/debug to stdout, warn/error to stderr
        transports.push(new winston.transports.Console({
            level: 'info',
            stderrLevels: ['error', 'warn'],
            format: winston.format.combine(
                winston.format.timestamp(),
                structuredFormatter
            )
        }));
    } else {
        // Default to stdout for unknown options
        transports.push(new winston.transports.Console({
            format: winston.format.combine(
                winston.format.timestamp(),
                structuredFormatter
            )
        }));
    }
    
    logger = winston.createLogger({
        level: logLevel,
        transports,
        exitOnError: false
    });
    
    // Log startup message
    logger.info(`Logging initialized: level=${logLevel}, output=${logOutput}`);
}

/**
 * Get a logger instance.
 * 
 * @param {string} name - Logger name (module name)
 * @returns {Object} Winston logger instance with context support
 */
function getLogger(name = 'main') {
    if (!logger) {
        setupLogging();
    }
    
    // Return logger with context-aware methods
    return {
        debug: (message, meta = {}) => logger.debug(message, { module: name, ...meta }),
        info: (message, meta = {}) => logger.info(message, { module: name, ...meta }),
        warn: (message, meta = {}) => logger.warn(message, { module: name, ...meta }),
        error: (message, meta = {}) => logger.error(message, { module: name, ...meta }),
        
        // Context management methods
        setContext: setContext,
        clearContext: clearContext,
        updateContext: updateContext,
        getContext: getContext,
        removeContextKeys: removeContextKeys
    };
}

/**
 * Set logging context variables that will be included in all log messages within the current async context.
 * 
 * @param {Object} contextData - Key-value pairs to add to logging context
 * @param {Function} callback - Function to execute with the context
 * 
 * @example
 * setContext({ operationId: 'op_123', user: 'admin' }, () => {
 *     logger.info('Operation started'); // Will include context automatically
 * });
 */
function setContext(contextData, callback) {
    if (typeof contextData === 'function' && !callback) {
        // If only one function is provided, treat it as callback with empty context
        callback = contextData;
        contextData = {};
    }
    
    const currentContext = contextStorage.getStore() || {};
    const newContext = { ...currentContext, ...contextData };
    
    if (callback) {
        return contextStorage.run(newContext, callback);
    } else {
        // For synchronous context setting (less recommended)
        return contextStorage.run(newContext, () => {});
    }
}

/**
 * Clear all logging context variables.
 */
function clearContext() {
    return contextStorage.run({}, () => {});
}

/**
 * Update existing context with new values.
 * 
 * @param {Object} contextData - Key-value pairs to update in logging context
 */
function updateContext(contextData) {
    const currentContext = contextStorage.getStore() || {};
    const updatedContext = { ...currentContext, ...contextData };
    return contextStorage.run(updatedContext, () => {});
}

/**
 * Get current logging context.
 * 
 * @returns {Object} Current context object
 */
function getContext() {
    return { ...(contextStorage.getStore() || {}) };
}

/**
 * Remove specific keys from logging context.
 * 
 * @param {...string} keys - Context keys to remove
 */
function removeContextKeys(...keys) {
    const currentContext = contextStorage.getStore() || {};
    const updatedContext = { ...currentContext };
    
    keys.forEach(key => {
        delete updatedContext[key];
    });
    
    return contextStorage.run(updatedContext, () => {});
}

// Export the logging interface
module.exports = {
    setupLogging,
    getLogger,
    setContext,
    clearContext,
    updateContext,
    getContext,
    removeContextKeys
};