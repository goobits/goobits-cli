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
 * Hook function for 'calculate' command
 * @param args - Command arguments and options
 * @returns Promise<void>
 */
export async function onCalculate(args: CommandArgs): Promise<void> {
    // TODO: Implement your 'calculate' command logic here
    console.log('🚀 Executing calculate command...');
    console.log('   Command:', args.commandName);
    
    // Example: access raw arguments
    if (args.rawArgs) {
        console.log('   Raw arguments:');
        Object.entries(args.rawArgs).forEach(([key, value]) => {
            console.log(`   ${key}: ${value}`);
        });
    }
    
    console.log('✅ calculate command completed successfully!');
}

/**
 * Hook function for 'status' command
 * @param args - Command arguments and options
 * @returns Promise<void>
 */
export async function onStatus(args: CommandArgs): Promise<void> {
    // TODO: Implement your 'status' command logic here
    console.log('🚀 Executing status command...');
    console.log('   Command:', args.commandName);
    
    // Example: access raw arguments
    if (args.rawArgs) {
        console.log('   Raw arguments:');
        Object.entries(args.rawArgs).forEach(([key, value]) => {
            console.log(`   ${key}: ${value}`);
        });
    }
    
    console.log('✅ status command completed successfully!');
}
