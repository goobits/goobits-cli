"use strict";
/**
 * Hook implementations for Demo TypeScript CLI
 *
 * This file contains the business logic for your CLI commands.
 * Implement the hook functions below to handle your CLI commands.
 *
 * IMPORTANT: Hook names must use snake_case with 'on_' prefix
 * Example:
 * - Command 'hello' -> Hook function 'on_hello'
 * - Command 'hello-world' -> Hook function 'on_hello_world'
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.on_greet = on_greet;
exports.on_info = on_info;
/**
 * Greet someone with style * @param name Name to greet * @param message Custom greeting message * @param options Command options * @param options.style Greeting style * @param options.count Repeat greeting N times * @param options.uppercase Convert to uppercase * @param options.language Language code * @returns Promise<number> - Exit code (0 for success)
 */
async function on_greet(name, message, options) {
    // Add your business logic here
    console.log('Hook on_greet called');
    console.log('Arguments:', { name, message });
    console.log('Options:', options);
    // Return 0 for success, non-zero for error
    return 0;
}
/**
 * Display system and environment information * @param options Command options * @param options.format Output format * @param options.verbose Show detailed information * @param options.sections Comma-separated sections to show * @returns Promise<number> - Exit code (0 for success)
 */
async function on_info(options) {
    // Add your business logic here
    console.log('Hook on_info called');
    console.log('Options:', options);
    // Return 0 for success, non-zero for error
    return 0;
}
//# sourceMappingURL=hooks.js.map