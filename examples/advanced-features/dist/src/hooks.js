"use strict";
/**
 * Hook functions for Nested Command Demo
 * Auto-generated from nested-command-demo.yaml
 *
 * Implement your business logic in these hook functions.
 * Each command will call its corresponding hook function.
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.onUnknownCommand = onUnknownCommand;
exports.onSimple = onSimple;
exports.onDatabase = onDatabase;
exports.onApi = onApi;
/**
 * Hook function for unknown commands
 * @param args - Command arguments and options
 * @returns Promise<void>
 */
async function onUnknownCommand(args) {
    console.log(`🤔 Unknown command: ${args.commandName}`);
    console.log('   Use --help to see available commands');
}
/**
 * Hook function for 'simple' command
 * @param args - Command arguments and options
 * @returns Promise<void>
 */
async function onSimple(args) {
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
async function onDatabase(args) {
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
async function onApi(args) {
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
