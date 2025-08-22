/**

 * Hook functions for Nested Command Demo

 * Auto-generated from nested-command-demo.yaml

 * 

 * Implement your business logic in these hook functions.

 * Each command will call its corresponding hook function.

 */



/**

 * Hook function for 'simple' command

 * @param {Object} args - Command arguments and options

 * @returns {Promise<void>}

 */

export async function onSimple(args) {

    // TODO: Implement your 'simple' command logic here

    console.log('🚀 Executing simple command...');

    console.log('   Command:', args.commandName);

    

    // Example: access raw arguments

    if (args.rawArgs) {

        Object.entries(args.rawArgs).forEach(([key, value]) => {

            console.log(`   ${key}: ${value}`);

        });

    }

    

    console.log('✅ simple command completed successfully!');

}



/**

 * Hook function for 'database' command

 * @param {Object} args - Command arguments and options

 * @returns {Promise<void>}

 */

export async function onDatabase(args) {

    // TODO: Implement your 'database' command logic here

    console.log('🚀 Executing database command...');

    console.log('   Command:', args.commandName);

    

    // Example: access raw arguments

    if (args.rawArgs) {

        Object.entries(args.rawArgs).forEach(([key, value]) => {

            console.log(`   ${key}: ${value}`);

        });

    }

    

    console.log('✅ database command completed successfully!');

}



/**

 * Hook function for 'api' command

 * @param {Object} args - Command arguments and options

 * @returns {Promise<void>}

 */

export async function onApi(args) {

    // TODO: Implement your 'api' command logic here

    console.log('🚀 Executing api command...');

    console.log('   Command:', args.commandName);

    

    // Example: access raw arguments

    if (args.rawArgs) {

        Object.entries(args.rawArgs).forEach(([key, value]) => {

            console.log(`   ${key}: ${value}`);

        });

    }

    

    console.log('✅ api command completed successfully!');

}



/**

 * Default hook for unhandled commands

 * @param {Object} args - Command arguments

 * @throws {Error} When no hook implementation is found

 */

export async function onUnknownCommand(args) {

    throw new Error(`No hook implementation found for command: ${args.commandName}`);

}

