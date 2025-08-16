/**

 * Hook functions for Demo TypeScript CLI

 * Auto-generated from typescript-example.yaml

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

 * Hook function for 'calculate' command

 * @param args - Command arguments and options

 * @returns Promise<void>

 */

export async function onCalculate(args: CommandArgs): Promise<void> {

    const { operation, a, b, precision } = args;
    
    const numA = parseFloat(a as string);
    const numB = parseFloat(b as string);
    const precisionValue = parseInt(precision as string) || 2;
    
    if (isNaN(numA) || isNaN(numB)) {
        console.error("❌ Error: Invalid numbers provided");
        return;
    }
    
    let result: number;
    
    switch (operation) {
        case 'add':
            result = numA + numB;
            break;
        case 'subtract':
            result = numA - numB;
            break;
        case 'multiply':
            result = numA * numB;
            break;
        case 'divide':
            if (numB === 0) {
                console.error("❌ Error: Division by zero");
                return;
            }
            result = numA / numB;
            break;
        default:
            console.error(`❌ Error: Unknown operation: ${operation}`);
            return;
    }
    
    console.log(`🧮 TypeScript Calculator`);
    console.log(`-`.repeat(25));
    console.log(`Operation: ${numA} ${operation} ${numB}`);
    console.log(`Result: ${result.toFixed(precisionValue)}`);
    console.log(`Precision: ${precisionValue} decimal places`);

}

/**

 * Hook function for 'status' command

 * @param args - Command arguments and options

 * @returns Promise<void>

 */

export async function onStatus(args: CommandArgs): Promise<void> {

    console.log(`⚡ TypeScript CLI Information`);
    console.log(`-`.repeat(30));
    console.log(`Node.js Version: ${process.version}`);
    console.log(`Platform: ${process.platform}`);
    console.log(`Architecture: ${process.arch}`);
    console.log(`TypeScript: Compiled to JavaScript`);
    console.log(`Memory Usage: ${Math.round(process.memoryUsage().heapUsed / 1024 / 1024)}MB`);

}