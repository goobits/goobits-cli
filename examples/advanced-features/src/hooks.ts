/**
 * Hook functions for Nested Command Demo
 * Auto-generated from nested-command-demo.yaml
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
 * Hook function for 'simple' command
 * @param args - Command arguments and options
 * @returns Promise<void>
 */
export async function onSimple(args: CommandArgs): Promise<void> {
    // TODO: Implement your 'simple' command logic here
    console.log('🚀 Executing simple command...');
    console.log('   Command:', args.commandName);
    
    // Example: access raw arguments
    if (args.rawArgs) {
        console.log('   Raw arguments:');
        Object.entries(args.rawArgs).forEach(([key, value]) => {
            console.log(`   ${key}: ${value}`);
        });
    }
    
    console.log('✅ simple command completed successfully!');
}

/**
 * Hook function for 'database' command
 * @param args - Command arguments and options
 * @returns Promise<void>
 */
export async function onDatabase(args: CommandArgs): Promise<void> {
    // TODO: Implement your 'database' command logic here
    console.log('🚀 Executing database command...');
    console.log('   Command:', args.commandName);
    
    // Example: access raw arguments
    if (args.rawArgs) {
        console.log('   Raw arguments:');
        Object.entries(args.rawArgs).forEach(([key, value]) => {
            console.log(`   ${key}: ${value}`);
        });
    }
    
    console.log('✅ database command completed successfully!');
}

/**
 * Hook function for 'api' command
 * @param args - Command arguments and options
 * @returns Promise<void>
 */
export async function onApi(args: CommandArgs): Promise<void> {
    // TODO: Implement your 'api' command logic here
    console.log('🚀 Executing api command...');
    console.log('   Command:', args.commandName);
    
    // Example: access raw arguments
    if (args.rawArgs) {
        console.log('   Raw arguments:');
        Object.entries(args.rawArgs).forEach(([key, value]) => {
            console.log(`   ${key}: ${value}`);
        });
    }
    
    console.log('✅ api command completed successfully!');
}
