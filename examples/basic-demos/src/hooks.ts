/**
 * Hook functions for Demo TypeScript CLI
 * Auto-generated from typescript-example.yaml
 * 
 * Implement your business logic in these hook functions.
 * Each command will call its corresponding hook function.
 */

// Type definitions for hook arguments
interface CommandArgs {
  commandName: string;
  rawArgs?: Record<string, any>;
  [key: string]: any;
}

/**
 * Hook function for unknown commands
 * @param args - Command arguments and options
 * @returns Promise<void>
 */
export async function onUnknownCommand(args: CommandArgs): Promise<void> {
  console.log(`🤔 Unknown command: ${args.commandName}`);
  console.log('   Use --help to see available commands');
}


/**
 * Hook function for 'greet' command
 * @param args - Command arguments and options
 * @returns Promise<void>
 */
export async function onGreet(args: CommandArgs): Promise<void> {
    // TODO: Implement your 'greet' command logic here
    console.log('🚀 Executing greet command...');
    console.log('   Command:', args.commandName);
    
    // Example: access raw arguments
    if (args.rawArgs) {
        console.log('   Raw arguments:');
        Object.entries(args.rawArgs).forEach(([key, value]) => {
            console.log(`   ${key}: ${value}`);
        });
    }
    
    console.log('✅ greet command completed successfully!');
}

/**
 * Hook function for 'info' command
 * @param args - Command arguments and options
 * @returns Promise<void>
 */
export async function onInfo(args: CommandArgs): Promise<void> {
    // TODO: Implement your 'info' command logic here
    console.log('🚀 Executing info command...');
    console.log('   Command:', args.commandName);
    
    // Example: access raw arguments
    if (args.rawArgs) {
        console.log('   Raw arguments:');
        Object.entries(args.rawArgs).forEach(([key, value]) => {
            console.log(`   ${key}: ${value}`);
        });
    }
    
    console.log('✅ info command completed successfully!');
}
