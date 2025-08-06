/**
 * Hook functions for TestNodeJSCLI
 * Auto-generated from test_nodejs_valid.yaml
 * 
 * Implement your business logic in these hook functions.
 * Each command will call its corresponding hook function.
 */

/**
 * Hook function for 'hello' command
 * @param {Object} args - Command arguments and options
 * @returns {Promise<void>}
 */
export async function onHello(args) {
    // TODO: Implement your 'hello' command logic here
    console.log('🚀 Executing hello command...');
    console.log('   Command:', args.commandName);
    
    // Example: access raw arguments
    if (args.rawArgs) {
        Object.entries(args.rawArgs).forEach(([key, value]) => {
            console.log(`   ${key}: ${value}`);
        });
    }
    
    console.log('✅ hello command completed successfully!');
}

/**
 * Default hook for unhandled commands
 * @param {Object} args - Command arguments
 * @throws {Error} When no hook implementation is found
 */
export async function onUnknownCommand(args) {
    throw new Error(`No hook implementation found for command: ${args.commandName}`);
}
