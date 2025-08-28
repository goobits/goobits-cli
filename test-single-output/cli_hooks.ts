/**
 * Hook implementations for Single Language Test CLI
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
import * as fs from 'fs';
import * as path from 'path';
/**
 * Say hello * @param name Name to greet * @returns Promise<number> - Exit code (0 for success)
 */
export async function on_hello(    name: string): Promise<number> {    // Generic command implementation
    console.log('Executing hello command...');    console.log('Arguments received:', { name });    console.log('✅ Command completed successfully!');    
    // Return 0 for success, non-zero for error
    return 0;
}