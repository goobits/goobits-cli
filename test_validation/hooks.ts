/**
 * Hook system interface for Test TypeScript CLI
 * 
 * This module defines the interface between the generated CLI and user-defined hooks.
 * Users should implement hook functions in hooks.ts to provide business logic.
 */

import * as fs from 'fs';
import * as path from 'path';

type HookFunction = (...args: any[]) => Promise<any> | any;

export class HookManager {
    private hooksModulePath: string;
    private hooks: Record<string, HookFunction> = {};

    constructor(hooksModulePath: string = './hooks') {
        this.hooksModulePath = hooksModulePath;
        this.loadHooks();
    }

    public async loadHooks(): Promise<void> {
        try {
            // Dynamic import to support reloading
            const hooksModule = await import(`${this.hooksModulePath}?t=${Date.now()}`);
            this.hooks = {};
            
            // Cache all exported hook functions
            for (const [name, func] of Object.entries(hooksModule)) {
                if (typeof func === 'function' && name.startsWith('on')) {
                    this.hooks[name] = func as HookFunction;
                }
            }
        } catch (error) {
            if ((error as any).code === 'MODULE_NOT_FOUND') {
                // Hooks module doesn't exist yet
                this.hooks = {};
            } else {
                console.warn(`Warning: Failed to load hooks: ${(error as Error).message}`);
                this.hooks = {};
            }
        }
    }

    public async reloadHooks(): Promise<void> {
        await this.loadHooks();
    }

    public hasHook(hookName: string): boolean {
        return hookName in this.hooks;
    }

    public async executeHook(hookName: string, ...args: any[]): Promise<any> {
        if (!this.hasHook(hookName)) {
            throw new HookNotFoundError(`Hook '${hookName}' not found`);
        }

        const hookFunc = this.hooks[hookName];

        try {
            const result = await hookFunc(...args);
            return result;
        } catch (error) {
            throw new HookExecutionError(`Error executing hook '${hookName}': ${(error as Error).message}`);
        }
    }

    public listHooks(): Record<string, string> {
        const hooksInfo: Record<string, string> = {};
        for (const [name, func] of Object.entries(this.hooks)) {
            // Try to extract function docstring/comments
            const funcString = func.toString();
            const commentMatch = funcString.match(/\/\*\*([\s\S]*?)\*\//);
            const description = commentMatch ? commentMatch[1].trim() : 'No description available';
            hooksInfo[name] = description;
        }
        return hooksInfo;
    }

    public generateHooksTemplate(): string {
        return `/**
 * Hook implementations for Test TypeScript CLI
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
import * as fs from 'fs';
import * as path from 'path';

/**
 * Greet someone
 *
 * @param options Command options
 * @param options.__loud Greet loudly
 * @returns Promise<void>
 */
export async function on_greet(
    options: {
        __loud?: string;
    }
): Promise<void> {
    // TODO: Implement your business logic here
    console.log('Hook on_greet called');
    console.log('Options:', options);
    
    // You can return a value or throw an error
    // Returning nothing is equivalent to success
}

// Add any utility functions or classes here
`;
    }
}

export class HookNotFoundError extends Error {
    constructor(message: string) {
        super(message);
        this.name = 'HookNotFoundError';
    }
}

export class HookExecutionError extends Error {
    constructor(message: string) {
        super(message);
        this.name = 'HookExecutionError';
    }
}

// Global hook manager instance
let _hookManager: HookManager | null = null;

export function getHookManager(): HookManager {
    if (!_hookManager) {
        _hookManager = new HookManager();
    }
    return _hookManager;
}

export async function executeHook(hookName: string, ...args: any[]): Promise<any> {
    return getHookManager().executeHook(hookName, ...args);
}

export function hasHook(hookName: string): boolean {
    return getHookManager().hasHook(hookName);
}