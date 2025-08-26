/**
 * Hook implementations for Demo Node.js CLI
 * 
 * This file contains the business logic for your CLI commands.
 * Implement the hook functions below to handle your CLI commands.
 * 
 * IMPORTANT: Hook names must use snake_case with 'on_' prefix
 * Example:
 * - Command 'hello' -> Hook function 'on_hello'
 * - Command 'hello-world' -> Hook function 'on_hello_world'
 */

// Import any modules you need here
import fs from 'fs';
import path from 'path';
/**
 * Greet someone with style * @param {string} name - Name to greet * @param {string} message - Custom greeting message * @param {Object} options - Command options * @param {str} options.style - Greeting style * @param {int} options.count - Repeat greeting N times * @param {flag} options.uppercase - Convert to uppercase * @param {str} options.language - Language code * @returns {Promise<number>} - Exit code (0 for success)
 */
async function on_greet(name, message, options) {
    // Add your business logic here
    console.log('Hook on_greet called');    console.log('Arguments:', { name, message });    console.log('Options:', options);    
    // Return 0 for success, non-zero for error
    return 0;
}
/**
 * Display system and environment information * @param {Object} options - Command options * @param {str} options.format - Output format * @param {flag} options.verbose - Show detailed information * @param {str} options.sections - Comma-separated sections to show * @returns {Promise<number>} - Exit code (0 for success)
 */
async function on_info(options) {
    // Add your business logic here
    console.log('Hook on_info called');    console.log('Options:', options);    
    // Return 0 for success, non-zero for error
    return 0;
}
// Export all hook functions
export {    on_greet,    on_info,};