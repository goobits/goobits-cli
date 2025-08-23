/**

 * Hook functions for Test Node.js CLI

 * Auto-generated from test-nodejs.yaml

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

 * Hook function for 'build' command

 * @param {Object} args - Command arguments and options

 * @returns {Promise<void>}

 */

export async function onBuild(args) {

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



/**

 * Hook function for 'serve' command

 * @param {Object} args - Command arguments and options

 * @returns {Promise<void>}

 */

export async function onServe(args) {

    // TODO: Implement your 'serve' command logic here

    console.log('🚀 Executing serve command...');

    console.log('   Command:', args.commandName);

    

    // Example: access raw arguments

    if (args.rawArgs) {

        Object.entries(args.rawArgs).forEach(([key, value]) => {

            console.log(`   ${key}: ${value}`);

        });

    }

    

    console.log('✅ serve command completed successfully!');

}



/**

 * Default hook for unhandled commands

 * @param {Object} args - Command arguments

 * @throws {Error} When no hook implementation is found

 */

export async function onUnknownCommand(args) {

    throw new Error(`No hook implementation found for command: ${args.commandName}`);

}

