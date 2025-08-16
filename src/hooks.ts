/**

 * Hook functions for TestTSCLI

 * Auto-generated from test_typescript_cli.yaml

 * 

 * Implement your business logic in these hook functions.

 * Each command will call its corresponding hook function.

 */



export interface CommandArgs {

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

 * Hook function for 'hello' command

 * @param args - Command arguments and options

 * @returns Promise<void>

 */

export async function onHello(args: CommandArgs): Promise<void> {

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

 * Hook function for 'build' command

 * @param args - Command arguments and options

 * @returns Promise<void>

 */

export async function onBuild(args: CommandArgs): Promise<void> {

    // TODO: Implement your 'build' command logic here

    console.log('🚀 Executing build command...');

    console.log('   Command:', args.commandName);

    

    // Example: access raw arguments

    if (args.rawArgs) {

        Object.entries(args.rawArgs).forEach(([key, value]) => {

            console.log(`   ${key}: ${value}`);

        });

    }

    

    console.log('✅ build command completed successfully!');

}