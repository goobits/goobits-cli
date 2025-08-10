/**
 * Hook system interface for Test Node.js CLI
 * 
 * This module defines the interface between the generated CLI and user-defined hooks.
 * Users should implement hook functions in hooks.js to provide business logic.
 */

const fs = require('fs');
const path = require('path');

class HookManager {
    constructor(hooksModulePath = './hooks.js') {
        this.hooksModulePath = hooksModulePath;
        this.hooks = {};
        this.loadHooks();
    }

    loadHooks() {
        try {
            // Clear require cache to allow reloading
            delete require.cache[require.resolve(this.hooksModulePath)];
            
            const hooksModule = require(this.hooksModulePath);
            this.hooks = {};
            
            // Cache all exported hook functions
            for (const [name, func] of Object.entries(hooksModule)) {
                if (typeof func === 'function' && name.startsWith('on')) {
                    this.hooks[name] = func;
                }
            }
        } catch (error) {
            if (error.code === 'MODULE_NOT_FOUND') {
                // Hooks module doesn't exist yet
                this.hooks = {};
            } else {
                console.warn(`Warning: Failed to load hooks: ${error.message}`);
                this.hooks = {};
            }
        }
    }

    reloadHooks() {
        this.loadHooks();
    }

    hasHook(hookName) {
        return hookName in this.hooks;
    }

    async executeHook(hookName, ...args) {
        if (!this.hasHook(hookName)) {
            throw new HookNotFoundError(`Hook '${hookName}' not found`);
        }

        const hookFunc = this.hooks[hookName];

        try {
            const result = await hookFunc(...args);
            return result;
        } catch (error) {
            throw new HookExecutionError(`Error executing hook '${hookName}': ${error.message}`);
        }
    }

    listHooks() {
        const hooksInfo = {};
        for (const [name, func] of Object.entries(this.hooks)) {
            // Try to extract function docstring/comments
            const funcString = func.toString();
            const commentMatch = funcString.match(/\/\*\*([\s\S]*?)\*\//);
            const description = commentMatch ? commentMatch[1].trim() : 'No description available';
            hooksInfo[name] = description;
        }
        return hooksInfo;
    }

    generateHooksTemplate() {
        return `/**
 * Hook implementations for Test Node.js CLI
 * 
 * This file contains the business logic for your CLI commands.
 * Implement the hook functions below to handle your CLI commands.
 * 
 * Each command in your CLI corresponds to a hook function named 'on<CommandName>'.
 * Command names with hyphens are converted to camelCase.
 * 
 * Example:
 * - Command 'hello-world' -> Hook function 'onHelloWorld'
 * - Command 'status' -> Hook function 'onStatus'
 */

// Import any modules you need here
const fs = require('fs');
const path = require('path');

/**
 * Greet someone
 *
 * @param {Object} options - Command options
 * @param {str} options.__loud - Greet loudly
 * @returns {Promise<void>}
 */
async function on_greet(options) {
    // TODO: Implement your business logic here
    console.log('Hook on_greet called');
    console.log('Options:', options);
    
    // You can return a value or throw an error
    // Returning nothing is equivalent to success
}

// Export all hook functions
module.exports = {
    on_greet,
};

// Add any utility functions or classes here
`;
    }
}

class HookNotFoundError extends Error {
    constructor(message) {
        super(message);
        this.name = 'HookNotFoundError';
    }
}

class HookExecutionError extends Error {
    constructor(message) {
        super(message);
        this.name = 'HookExecutionError';
    }
}

// Global hook manager instance
let _hookManager = null;

function getHookManager() {
    if (!_hookManager) {
        _hookManager = new HookManager();
    }
    return _hookManager;
}

async function executeHook(hookName, ...args) {
    return getHookManager().executeHook(hookName, ...args);
}

function hasHook(hookName) {
    return getHookManager().hasHook(hookName);
}

module.exports = {
    HookManager,
    HookNotFoundError,
    HookExecutionError,
    getHookManager,
    executeHook,
    hasHook
};
