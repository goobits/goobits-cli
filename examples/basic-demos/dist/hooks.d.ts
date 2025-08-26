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
/**
 * Greet someone with style * @param name Name to greet * @param message Custom greeting message * @param options Command options * @param options.style Greeting style * @param options.count Repeat greeting N times * @param options.uppercase Convert to uppercase * @param options.language Language code * @returns Promise<number> - Exit code (0 for success)
 */
export declare function on_greet(name: string, message: string, options: {
    style?: string;
    count?: string;
    uppercase?: string;
    language?: string;
}): Promise<number>;
/**
 * Display system and environment information * @param options Command options * @param options.format Output format * @param options.verbose Show detailed information * @param options.sections Comma-separated sections to show * @returns Promise<number> - Exit code (0 for success)
 */
export declare function on_info(options: {
    format?: string;
    verbose?: string;
    sections?: string;
}): Promise<number>;
//# sourceMappingURL=hooks.d.ts.map