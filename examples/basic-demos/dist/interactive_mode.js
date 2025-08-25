#!/usr/bin/env node
import * as readline from 'readline';
import * as fs from 'fs';
import * as path from 'path';
let hooks = {};
try {
    hooks = require('./hooks') || {};
}
catch (e) {
    console.warn('Warning: hooks module not found, using empty hooks');
}
class DemotypescriptcliInteractive {
    rl;
    commands;
    commandHistory = [];
    constructor() {
        this.rl = readline.createInterface({
            input: process.stdin,
            output: process.stdout,
            prompt: 'demo_ts> ',
            completer: this.completer.bind(this)
        });
        this.commands = new Map();
        this.setupCommands();
        this.setupEventHandlers();
        this.loadCommandHistory();
    }
    setupCommands() {
        this.registerCommand({
            name: 'help',
            description: 'Show available commands',
            handler: this.handleHelp.bind(this),
            aliases: ['?', 'h'],
            examples: ['help', 'help <command>']
        });
        this.registerCommand({
            name: 'exit',
            description: 'Exit interactive mode',
            handler: this.handleExit.bind(this),
            aliases: ['quit', 'q'],
            examples: ['exit', 'quit']
        });
        this.registerCommand({
            name: 'history',
            description: 'Show command history',
            handler: this.handleHistory.bind(this),
            examples: ['history', 'history 10']
        });
        this.registerCommand({
            name: 'clear',
            description: 'Clear the screen',
            handler: this.handleClear.bind(this),
            aliases: ['cls'],
            examples: ['clear']
        });
        this.registerCommand({
            name: 'greet',
            description: 'Greet someone with style',
            handler: this.handleGreet.bind(this),
            examples: ['greet <name> <message>']
        });
        this.registerCommand({
            name: 'info',
            description: 'Display system and environment information',
            handler: this.handleInfo.bind(this),
            examples: ['info']
        });
    }
    setupEventHandlers() {
        this.rl.on('line', this.handleLine.bind(this));
        this.rl.on('close', this.handleClose.bind(this));
        this.rl.on('SIGINT', this.handleSigInt.bind(this));
    }
    loadCommandHistory() {
        const historyFile = path.join(process.cwd(), '.demo_ts_history');
        try {
            if (fs.existsSync(historyFile)) {
                const historyContent = fs.readFileSync(historyFile, 'utf-8');
                const historyLines = historyContent
                    .split('\n')
                    .filter(line => line.trim())
                    .slice(-1000);
                this.commandHistory.push(...historyLines);
            }
        }
        catch (error) {
        }
    }
    saveCommandHistory() {
        const historyFile = path.join(process.cwd(), '.demo_ts_history');
        try {
            const historyContent = this.commandHistory.slice(-1000).join('\n') + '\n';
            fs.writeFileSync(historyFile, historyContent);
        }
        catch (error) {
        }
    }
    start() {
        console.log('🚀 Welcome to Demo TypeScript CLI interactive mode');
        console.log('   Type "help" for commands, "exit" to quit');
        console.log();
        this.rl.prompt();
    }
    registerCommand(command) {
        this.commands.set(command.name, command);
        if (command.aliases) {
            command.aliases.forEach(alias => {
                this.commands.set(alias, command);
            });
        }
    }
    async handleLine(line) {
        const trimmed = line.trim();
        if (!trimmed) {
            this.rl.prompt();
            return;
        }
        this.commandHistory.push(trimmed);
        const [commandName, ...args] = this.parseCommandLine(trimmed);
        if (this.commands.has(commandName)) {
            const command = this.commands.get(commandName);
            try {
                await command.handler(args);
            }
            catch (error) {
                console.error(`❌ Error executing command '${commandName}':`, error.message);
            }
        }
        else {
            console.error(`❌ Unknown command: ${commandName}`);
            console.log('💡 Type "help" for available commands');
        }
        this.rl.prompt();
    }
    parseCommandLine(line) {
        const args = [];
        let current = '';
        let inQuotes = false;
        let quoteChar = '';
        for (let i = 0; i < line.length; i++) {
            const char = line[i];
            if (!inQuotes && (char === '"' || char === "'")) {
                inQuotes = true;
                quoteChar = char;
            }
            else if (inQuotes && char === quoteChar) {
                inQuotes = false;
                quoteChar = '';
            }
            else if (!inQuotes && char === ' ') {
                if (current) {
                    args.push(current);
                    current = '';
                }
            }
            else {
                current += char;
            }
        }
        if (current) {
            args.push(current);
        }
        return args;
    }
    completer(line) {
        const commandNames = Array.from(this.commands.keys());
        const hits = commandNames.filter(cmd => cmd.startsWith(line));
        return [hits.length ? hits : commandNames, line];
    }
    handleClose() {
        this.saveCommandHistory();
        console.log('\n👋 Goodbye!');
        process.exit(0);
    }
    handleSigInt() {
        console.log('\n💡 Use "exit" to quit or press Ctrl+C again to force quit');
        this.rl.prompt();
    }
    handleHelp(args) {
        if (args.length > 0) {
            const commandName = args[0];
            const command = this.commands.get(commandName);
            if (command) {
                console.log(`\n📖 ${command.name}: ${command.description}`);
                if (command.examples) {
                    console.log('   Examples:');
                    command.examples.forEach(example => console.log(`     ${example}`));
                }
                if (command.aliases && command.aliases.length > 0) {
                    console.log(`   Aliases: ${command.aliases.join(', ')}`);
                }
            }
            else {
                console.error(`❌ Unknown command: ${commandName}`);
            }
        }
        else {
            console.log('\n📚 Available commands:');
            const uniqueCommands = new Set();
            this.commands.forEach(command => uniqueCommands.add(command));
            Array.from(uniqueCommands)
                .sort((a, b) => a.name.localeCompare(b.name))
                .forEach(command => {
                console.log(`  ${command.name.padEnd(15)} ${command.description}`);
            });
        }
        console.log();
    }
    handleExit() {
        this.rl.close();
    }
    handleHistory(args) {
        const count = args.length > 0 ? parseInt(args[0]) : 20;
        const recentHistory = this.commandHistory.slice(-count);
        console.log(`\n📜 Recent command history (last ${recentHistory.length}):`);
        recentHistory.forEach((cmd, index) => {
            const lineNumber = this.commandHistory.length - recentHistory.length + index + 1;
            console.log(`  ${lineNumber.toString().padStart(4)}: ${cmd}`);
        });
        console.log();
    }
    handleClear() {
        console.clear();
        console.log('🚀 Welcome to Demo TypeScript CLI interactive mode');
        console.log('   Type "help" for commands, "exit" to quit');
        console.log();
    }
    async handleGreet(args) {
        const hookName = 'onGreet';
        const hook = hooks[hookName];
        if (typeof hook === 'function') {
            try {
                const context = {
                    commandName: 'greet',
                    args: this.parseArgumentsToObject(args),
                    options: this.parseOptionsToObject(args),
                    globalOptions: {}
                };
                await hook(context);
            }
            catch (error) {
                console.error(`❌ Error in ${hookName}:`, error.message);
            }
        }
        else {
            console.error(`❌ Hook function '${hookName}' not implemented`);
        }
    }
    async handleInfo(args) {
        const hookName = 'onInfo';
        const hook = hooks[hookName];
        if (typeof hook === 'function') {
            try {
                const context = {
                    commandName: 'info',
                    args: this.parseArgumentsToObject(args),
                    options: this.parseOptionsToObject(args),
                    globalOptions: {}
                };
                await hook(context);
            }
            catch (error) {
                console.error(`❌ Error in ${hookName}:`, error.message);
            }
        }
        else {
            console.error(`❌ Hook function '${hookName}' not implemented`);
        }
    }
    parseArgumentsToObject(args) {
        const result = {};
        args.forEach((arg, index) => {
            if (!arg.startsWith('-')) {
                result[`arg${index}`] = arg;
            }
        });
        return result;
    }
    parseOptionsToObject(args) {
        const result = {};
        for (let i = 0; i < args.length; i++) {
            const arg = args[i];
            if (arg.startsWith('--')) {
                const optionName = arg.slice(2);
                const nextArg = i + 1 < args.length ? args[i + 1] : null;
                if (nextArg && !nextArg.startsWith('-')) {
                    result[optionName] = nextArg;
                    i++;
                }
                else {
                    result[optionName] = true;
                }
            }
            else if (arg.startsWith('-') && arg.length === 2) {
                const shortOption = arg.slice(1);
                const nextArg = i + 1 < args.length ? args[i + 1] : null;
                if (nextArg && !nextArg.startsWith('-')) {
                    result[shortOption] = nextArg;
                    i++;
                }
                else {
                    result[shortOption] = true;
                }
            }
        }
        return result;
    }
}
export function runInteractive() {
    const interactive = new DemotypescriptcliInteractive();
    interactive.start();
}
if (require.main === module) {
    runInteractive();
}
//# sourceMappingURL=interactive_mode.js.map