export async function onUnknownCommand(args) {
    console.log(`🤔 Unknown command: ${args.commandName}`);
    console.log('   Use --help to see available commands');
}
export async function onGreet(args) {
    console.log('🚀 Executing greet command...');
    console.log('   Command:', args.commandName);
    if (args.rawArgs) {
        console.log('   Raw arguments:');
        Object.entries(args.rawArgs).forEach(([key, value]) => {
            console.log(`   ${key}: ${value}`);
        });
    }
    console.log('✅ greet command completed successfully!');
}
export async function onInfo(args) {
    console.log('🚀 Executing info command...');
    console.log('   Command:', args.commandName);
    if (args.rawArgs) {
        console.log('   Raw arguments:');
        Object.entries(args.rawArgs).forEach(([key, value]) => {
            console.log(`   ${key}: ${value}`);
        });
    }
    console.log('✅ info command completed successfully!');
}
//# sourceMappingURL=hooks.js.map