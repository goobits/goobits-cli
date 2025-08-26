/**
 * Hook implementations for Test Universal CLI
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
 * Say hello to someone * @param name Name to greet * @param options Command options * @param options.greeting Custom greeting message * @returns Promise<number> - Exit code (0 for success)
 */
export async function on_hello(    name: string,    options: {        greeting?: string;    }): Promise<number> {
    // Add your business logic here
    console.log('Hook on_hello called');    console.log('Arguments:', { name });    console.log('Options:', options);    
    // Return 0 for success, non-zero for error
    return 0;
}