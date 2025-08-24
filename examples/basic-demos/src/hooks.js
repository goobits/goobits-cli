/**

 * Hook functions for Demo Node.js CLI

 * Auto-generated from nodejs-example.yaml

 * 

 * Implement your business logic in these hook functions.

 * Each command will call its corresponding hook function.

 */



/**

 * Hook function for 'greet' command

 * @param {Object} args - Command arguments and options

 * @returns {Promise<void>}

 */

export async function onGreet(args) {
    const { name, style } = args;
    
    let greeting = `Hello ${name}!`;
    
    if (style === 'excited') {
        greeting = `🎉 ${greeting.toUpperCase()} 🎉`;
    } else if (style === 'formal') {
        greeting = `Good day, ${name}.`;
    }
    
    console.log(greeting);
    console.log(`Welcome to the Node.js CLI demo!`);
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

