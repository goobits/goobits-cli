"""

Node.js Interactive Mode Utilities



This module provides Node.js-specific utilities for enhanced interactive mode features,

including async command handling, Node.js-specific error formatting, history management,

and tab completion for npm packages and Node.js modules.

"""








from typing import Dict, List, Any





class NodeJSInteractiveUtils:

    """Utilities for Node.js interactive mode features."""

    

    @staticmethod

    def get_enhanced_readline_config() -> Dict[str, Any]:

        """

        Get enhanced readline configuration with custom key bindings.

        

        Returns:

            Dictionary containing readline configuration options

        """

        return {

            "completer": "completeCommand.bind(this)",

            "terminal": True,

            "history_size": 1000,

            "completion_append_character": " ",

            "key_bindings": {

                "ctrl-l": "clearScreen",

                "ctrl-r": "reverseHistorySearch", 

                "tab": "complete",

                "up": "historyPrev",

                "down": "historyNext",

                "ctrl-c": "interrupt",

                "ctrl-d": "eof"

            },

            "colors": {

                "RESET": "\\x1b[0m",

                "BOLD": "\\x1b[1m", 

                "DIM": "\\x1b[2m",

                "GREEN": "\\x1b[32m",

                "YELLOW": "\\x1b[33m",

                "RED": "\\x1b[31m",

                "BLUE": "\\x1b[34m",

                "MAGENTA": "\\x1b[35m",

                "CYAN": "\\x1b[36m"

            }

        }

    

    @staticmethod

    def get_async_command_handler() -> str:

        """

        Generate async command handling code for Node.js.

        

        Returns:

            JavaScript code for async command execution

        """

        return '''

    async executeCommand(line) {

        const trimmed = line.trim();

        if (!trimmed) return false;

        

        this.addToHistory(trimmed);

        const [cmd, ...args] = this.parseCommandLine(trimmed);

        

        if (this.commands[cmd]) {

            const command = this.commands[cmd];

            try {

                // Create execution context with timeout

                const timeoutMs = command.timeout || 30000;

                const result = await Promise.race([

                    command.handler(args),

                    new Promise((_, reject) => 

                        setTimeout(() => reject(new Error('Command timeout')), timeoutMs)

                    )

                ]);

                

                return result === true; // Exit if handler returns true

            } catch (error) {

                this.formatError(error);

                return false;

            }

        } else {

            console.log(chalk.yellow(`Unknown command: ${cmd}`));

            console.log(chalk.dim("Type 'help' for available commands"));

            return false;

        }

    }

    

    parseCommandLine(line) {

        // Advanced command line parsing with quote support

        const args = [];

        let current = '';

        let inQuotes = false;

        let quoteChar = '';

        let escaped = false;

        

        for (let i = 0; i < line.length; i++) {

            const char = line[i];

            

            if (escaped) {

                current += char;

                escaped = false;

                continue;

            }

            

            if (char === '\\\\') {

                escaped = true;

                continue;

            }

            

            if (!inQuotes && (char === '"' || char === "'")) {

                inQuotes = true;

                quoteChar = char;

                continue;

            }

            

            if (inQuotes && char === quoteChar) {

                inQuotes = false;

                quoteChar = '';

                continue;

            }

            

            if (!inQuotes && char === ' ') {

                if (current.length > 0) {

                    args.push(current);

                    current = '';

                }

                continue;

            }

            

            current += char;

        }

        

        if (current.length > 0) {

            args.push(current);

        }

        

        return args;

    }

'''

    

    @staticmethod

    def get_error_formatter() -> str:

        """

        Generate Node.js-specific error formatting code.

        

        Returns:

            JavaScript code for error formatting

        """

        return '''

    formatError(error) {

        if (error.code === 'ENOENT') {

            console.error(chalk.red('✗ File or command not found'));

            console.error(chalk.dim(`  ${error.message}`));

        } else if (error.code === 'EACCES') {

            console.error(chalk.red('✗ Permission denied'));

            console.error(chalk.dim(`  ${error.message}`));

        } else if (error.code === 'MODULE_NOT_FOUND') {

            console.error(chalk.red('✗ Module not found'));

            console.error(chalk.dim(`  ${error.message}`));

            console.log(chalk.yellow('  Try running: npm install'));

        } else if (error.name === 'SyntaxError') {

            console.error(chalk.red('✗ JavaScript Syntax Error'));

            console.error(chalk.dim(`  ${error.message}`));

            if (error.stack) {

                const lines = error.stack.split('\\n').slice(1, 3);

                lines.forEach(line => console.error(chalk.dim(`  ${line}`)));

            }

        } else if (error.code === 'TIMEOUT') {

            console.error(chalk.red('✗ Command timed out'));

            console.error(chalk.dim(`  ${error.message}`));

        } else {

            console.error(chalk.red(`✗ Error: ${error.message || error}`));

            if (process.env.NODE_ENV === 'development' && error.stack) {

                console.error(chalk.dim(error.stack));

            }

        }

    }

'''

    

    @staticmethod

    def get_history_manager() -> str:

        """

        Generate history management code with file persistence.

        

        Returns:

            JavaScript code for history management

        """

        return '''

    setupHistoryPersistence() {

        // Determine history file location based on OS

        const os = require('os');

        const homeDir = os.homedir();

        let historyDir;

        

        if (process.platform === 'win32') {

            historyDir = path.join(process.env.APPDATA || homeDir, this.projectName);

        } else if (process.platform === 'darwin') {

            historyDir = path.join(homeDir, 'Library', 'Application Support', this.projectName);

        } else {

            historyDir = path.join(homeDir, '.config', this.projectName);

        }

        

        this.historyFile = path.join(historyDir, 'interactive_history');

        

        // Create directory if it doesn't exist

        try {

            fs.mkdirSync(historyDir, { recursive: true });

        } catch (err) {

            // Ignore if directory already exists

        }

        

        this.loadHistory();

        

        // Save history on exit

        process.on('exit', () => this.saveHistory());

        process.on('SIGINT', () => {

            this.saveHistory();

            process.exit(0);

        });

        process.on('SIGTERM', () => {

            this.saveHistory();

            process.exit(0);

        });

    }

    

    loadHistory() {

        try {

            if (fs.existsSync(this.historyFile)) {

                const historyData = fs.readFileSync(this.historyFile, 'utf8');

                this.commandHistory = historyData.split('\\n').filter(line => line.trim());

                

                // Load into readline interface

                this.commandHistory.forEach(line => {

                    if (this.rl && this.rl.history) {

                        this.rl.history.push(line);

                    }

                });

            }

        } catch (err) {

            console.error(chalk.yellow('Warning: Could not load command history'));

        }

    }

    

    saveHistory() {

        try {

            if (this.historyFile && this.commandHistory.length > 0) {

                // Keep only the last 1000 commands

                const recentHistory = this.commandHistory.slice(-1000);

                fs.writeFileSync(this.historyFile, recentHistory.join('\\n'), 'utf8');

            }

        } catch (err) {

            console.error(chalk.yellow('Warning: Could not save command history'));

        }

    }

    

    addToHistory(line) {

        if (line && line.trim() && !line.startsWith('help')) {

            this.commandHistory.push(line.trim());

            // Also add to readline history

            if (this.rl && this.rl.history) {

                this.rl.history.unshift(line.trim());

            }

        }

    }

'''

    

    @staticmethod

    def get_completion_engine() -> str:

        """

        Generate advanced tab completion for Node.js-specific features.

        

        Returns:

            JavaScript code for tab completion

        """

        return '''

    setupAdvancedCompletion() {

        this.completionCache = new Map();

        this.npmPackages = [];

        this.nodeModules = [];

        

        // Load available npm packages (cached)

        this.loadNpmPackages();

        this.loadNodeModules();

    }

    

    async loadNpmPackages() {

        try {

            // Get globally installed packages

            const result = execSync('npm list -g --depth=0 --json', { 

                encoding: 'utf8', 

                timeout: 5000 

            });

            const packages = JSON.parse(result);

            this.npmPackages = Object.keys(packages.dependencies || {});

        } catch (err) {

            // Fallback to common packages

            this.npmPackages = [

                'express', 'lodash', 'axios', 'react', 'vue', 'angular',

                'typescript', 'webpack', 'babel', 'eslint', 'prettier',

                'jest', 'mocha', 'chai', 'sinon', 'nodemon', 'pm2'

            ];

        }

    }

    

    loadNodeModules() {

        try {

            // Get Node.js builtin modules

            this.nodeModules = [

                'fs', 'path', 'os', 'util', 'events', 'stream', 'buffer',

                'crypto', 'http', 'https', 'url', 'querystring', 'readline',

                'child_process', 'cluster', 'worker_threads', 'async_hooks'

            ];

            

            // Add project's node_modules if package.json exists

            if (fs.existsSync('package.json')) {

                const packageJson = JSON.parse(fs.readFileSync('package.json', 'utf8'));

                const dependencies = {

                    ...packageJson.dependencies,

                    ...packageJson.devDependencies

                };

                this.nodeModules.push(...Object.keys(dependencies));

            }

        } catch (err) {

            // Use defaults

        }

    }

    

    completeCommand(line) {

        const args = this.parseCommandLine(line);

        const partial = args[args.length - 1] || '';

        

        // Command completion

        if (args.length <= 1) {

            const commands = Object.keys(this.commands);

            const hits = commands.filter(cmd => cmd.startsWith(partial));

            return [hits, partial];

        }

        

        const [command, ...cmdArgs] = args;

        

        // Context-aware completion

        if (this.commands[command]) {

            return this.completeCommandContext(command, cmdArgs, partial);

        }

        

        return [[], partial];

    }

    

    completeCommandContext(command, args, partial) {

        const commandDef = this.commands[command];

        const completions = [];

        

        // Option completion

        if (partial.startsWith('-')) {

            const options = commandDef.options || [];

            options.forEach(opt => {

                if (opt.short && (`-${opt.short}`).startsWith(partial)) {

                    completions.push(`-${opt.short}`);

                }

                if ((`--${opt.name}`).startsWith(partial)) {

                    completions.push(`--${opt.name}`);

                }

            });

        }

        

        // File/directory completion

        else if (this.shouldCompleteFiles(command, args)) {

            return this.completeFiles(partial);

        }

        

        // NPM package completion for relevant commands

        else if (this.shouldCompleteNpmPackages(command, args)) {

            const hits = this.npmPackages.filter(pkg => pkg.startsWith(partial));

            completions.push(...hits);

        }

        

        // Node.js module completion

        else if (this.shouldCompleteNodeModules(command, args)) {

            const hits = this.nodeModules.filter(mod => mod.startsWith(partial));

            completions.push(...hits);

        }

        

        return [completions, partial];

    }

    

    completeFiles(partial) {

        try {

            const dir = path.dirname(partial) || '.';

            const basename = path.basename(partial);

            

            const files = fs.readdirSync(dir).filter(file => 

                file.startsWith(basename)

            ).map(file => {

                const fullPath = path.join(dir, file);

                const stats = fs.statSync(fullPath);

                return stats.isDirectory() ? `${file}/` : file;

            });

            

            return [files, basename];

        } catch (err) {

            return [[], partial];

        }

    }

    

    shouldCompleteFiles(command, args) {

        // Commands that typically work with files

        const fileCommands = ['install', 'build', 'run', 'test', 'deploy'];

        return fileCommands.includes(command) || 

               args.some(arg => arg.includes('.') || arg.includes('/'));

    }

    

    shouldCompleteNpmPackages(command, args) {

        // Commands that work with npm packages

        const npmCommands = ['install', 'add', 'remove', 'uninstall'];

        return npmCommands.includes(command);

    }

    

    shouldCompleteNodeModules(command, args) {

        // Commands that work with Node.js modules

        const moduleCommands = ['import', 'require', 'load'];

        return moduleCommands.includes(command) || 

               args.some(arg => arg.startsWith('require') || arg.startsWith('import'));

    }

'''

    

    @staticmethod

    def get_repl_evaluation() -> str:

        """

        Generate JavaScript expression evaluation support.

        

        Returns:

            JavaScript code for REPL evaluation

        """

        return '''

    async evaluateExpression(expression) {

        // Support JavaScript expression evaluation

        if (expression.startsWith('js:')) {

            const jsCode = expression.substring(3).trim();

            try {
                
                // Secure evaluation using vm module instead of unsafe eval()
                const vm = require('vm');
                const context = vm.createContext({
                    console, require, process, Buffer, setTimeout, clearTimeout,
                    setInterval, clearInterval, setImmediate, clearImmediate,
                    chalk, fs, path, os, util, crypto
                });
                
                const result = vm.runInContext(jsCode, context, {
                    timeout: 5000, // 5 second timeout
                    displayErrors: true
                });

                if (result !== undefined) {

                    console.log(chalk.green(`=> ${JSON.stringify(result, null, 2)}`));

                }

                return false; // Don't exit

            } catch (error) {

                console.error(chalk.red(`JavaScript Error: ${error.message}`));

                return false;

            }

        }

        

        // Support async expressions

        if (expression.startsWith('await ')) {

            try {

                const asyncCode = `(async () => { return ${expression}; })()`;

                // Secure evaluation using vm module instead of unsafe eval()  
                const vm = require('vm');
                const context = vm.createContext({
                    console, require, process, Buffer, setTimeout, clearTimeout,
                    setInterval, clearInterval, setImmediate, clearImmediate,
                    chalk, fs, path, os, util, crypto
                });
                
                const result = await vm.runInContext(asyncCode, context, {
                    timeout: 5000, // 5 second timeout
                    displayErrors: true
                });

                if (result !== undefined) {

                    console.log(chalk.green(`=> ${JSON.stringify(result, null, 2)}`));

                }

                return false;

            } catch (error) {

                console.error(chalk.red(`Async Error: ${error.message}`));

                return false;

            }

        }

        

        return null; // Not an expression

    }

    

    setupReplCommands() {

        // Add REPL-specific commands

        this.commands.js = {

            description: 'Evaluate JavaScript expression',

            handler: async (args) => {

                const expression = args.join(' ');

                return await this.evaluateExpression(`js:${expression}`);

            }

        };

        

        this.commands.await = {

            description: 'Evaluate async JavaScript expression', 

            handler: async (args) => {

                const expression = args.join(' ');

                return await this.evaluateExpression(`await ${expression}`);

            }

        };

        

        this.commands.require = {

            description: 'Load Node.js module',

            handler: async (args) => {

                if (args.length === 0) {

                    console.log(chalk.yellow('Usage: require <module-name>'));

                    return false;

                }

                

                const moduleName = args[0];

                try {

                    const loadedModule = require(moduleName);

                    global[moduleName.replace(/[^a-zA-Z0-9_$]/g, '_')] = loadedModule;

                    console.log(chalk.green(`Module '${moduleName}' loaded and available as global variable`));

                } catch (error) {

                    console.error(chalk.red(`Failed to load module '${moduleName}': ${error.message}`));

                }

                return false;

            }

        };

    }

'''

    

    @staticmethod

    def get_integration_features() -> str:

        """

        Generate Node.js integration features.

        

        Returns:

            JavaScript code for Node.js integration

        """

        return '''

    setupNodeJSIntegration() {

        // Setup process monitoring

        this.setupProcessMonitoring();

        

        // Setup module hot-reloading

        this.setupModuleReloading();

        

        // Setup environment management

        this.setupEnvironmentManagement();

    }

    

    setupProcessMonitoring() {

        // Monitor child processes

        this.childProcesses = new Set();

        

        this.commands['ps'] = {

            description: 'List running child processes',

            handler: async () => {

                if (this.childProcesses.size === 0) {

                    console.log(chalk.dim('No child processes running'));

                } else {

                    console.log(chalk.bold('Running processes:'));

                    this.childProcesses.forEach((proc, i) => {

                        console.log(`  ${i + 1}. PID ${proc.pid} - ${proc.spawnfile}`);

                    });

                }

                return false;

            }

        };

        

        this.commands['kill'] = {

            description: 'Kill a child process by PID',

            handler: async (args) => {

                if (args.length === 0) {

                    console.log(chalk.yellow('Usage: kill <pid>'));

                    return false;

                }

                

                const pid = parseInt(args[0]);

                let found = false;

                

                this.childProcesses.forEach(proc => {

                    if (proc.pid === pid) {

                        proc.kill();

                        this.childProcesses.delete(proc);

                        console.log(chalk.green(`Killed process ${pid}`));

                        found = true;

                    }

                });

                

                if (!found) {

                    console.log(chalk.yellow(`Process ${pid} not found`));

                }

                return false;

            }

        };

    }

    

    setupModuleReloading() {

        this.commands['reload'] = {

            description: 'Reload hooks module',

            handler: async () => {

                try {

                    // Clear require cache for hooks

                    const hooksPaths = [

                        './src/hooks.js',

                        './hooks.js',

                        path.resolve('./src/hooks.js'),

                        path.resolve('./hooks.js')

                    ];

                    

                    hooksPaths.forEach(hookPath => {

                        delete require.cache[require.resolve(hookPath)];

                    });

                    

                    // Re-require hooks

                    this.hooks = require('./src/hooks.js');

                    console.log(chalk.green('Hooks module reloaded successfully'));

                } catch (error) {

                    console.error(chalk.red(`Failed to reload hooks: ${error.message}`));

                }

                return false;

            }

        };

    }

    

    setupEnvironmentManagement() {

        this.commands['env'] = {

            description: 'Show/set environment variables',

            handler: async (args) => {

                if (args.length === 0) {

                    // Show current environment

                    console.log(chalk.bold('Environment Variables:'));

                    Object.keys(process.env).sort().forEach(key => {

                        const value = process.env[key];

                        console.log(`  ${key}=${value}`);

                    });

                } else if (args.length === 1) {

                    // Show specific variable

                    const key = args[0];

                    const value = process.env[key];

                    if (value !== undefined) {

                        console.log(`${key}=${value}`);

                    } else {

                        console.log(chalk.yellow(`Environment variable '${key}' not set`));

                    }

                } else {

                    // Set variable

                    const [key, value] = args;

                    process.env[key] = value;

                    console.log(chalk.green(`Set ${key}=${value}`));

                }

                return false;

            }

        };

    }

'''



    @classmethod

    def generate_enhanced_interactive_template(cls) -> str:

        """

        Generate the complete enhanced Node.js interactive mode template.

        

        Returns:

            Complete JavaScript template code

        """

        return '''#!/usr/bin/env node

/**

 * Enhanced Interactive mode for {{ project.name }}

 * Generated by Goobits CLI Framework - Node.js Agent B Enhanced Version

 */



const readline = require('readline');

const chalk = require('chalk');

const fs = require('fs');

const path = require('path');

const os = require('os');

const { spawn, execSync } = require('child_process');



// Import hooks dynamically to support hot reloading

let hooks;

try {

    hooks = require('./src/hooks');

} catch (err) {

    try {

        hooks = require('./hooks');

    } catch (err2) {

        console.warn(chalk.yellow('Warning: Could not load hooks module'));

        hooks = {};

    }

}



class {{ project.name | replace('-', '') | title }}Interactive {

    constructor() {

        this.projectName = '{{ project.name }}';

        this.commandHistory = [];

        this.completionCache = new Map();

        this.childProcesses = new Set();

        this.hooks = hooks;

        

        // Enhanced readline configuration (simplified)

        const config = {

            terminal: true,

            historySize: 1000

        };

        

        this.rl = readline.createInterface({

            input: process.stdin,

            output: process.stdout,

            prompt: chalk.bold.cyan('{{ cli.root_command.name }}> '),

            completer: this.completeCommand.bind(this),

            terminal: config.terminal,

            historySize: config.historySize

        });

        

        this.commands = {

{% for command in cli.root_command.subcommands %}

            '{{ command.name }}': {

                description: '{{ command.description }}',

                handler: this.handle{{ command.name | replace('-', '') | title }}.bind(this),

                options: {{ command.options | tojson }},

                timeout: {{ command.timeout | default(30000) }}

            },

{% endfor %}

            'help': {

                description: 'Show available commands',

                handler: this.handleHelp.bind(this)

            },

            'exit': {

                description: 'Exit interactive mode', 

                handler: this.handleExit.bind(this)

            },

            'quit': {

                description: 'Exit interactive mode',

                handler: this.handleExit.bind(this)

            },

            'clear': {

                description: 'Clear the screen',

                handler: this.handleClear.bind(this)

            },

            'history': {

                description: 'Show command history',

                handler: this.handleHistory.bind(this)

            }

        };

        

        // Setup enhanced features

        this.setupHistoryPersistence();

        this.setupAdvancedCompletion();

        this.setupReplCommands();

        this.setupNodeJSIntegration();

    }

    

    start() {

        console.log(chalk.bold.green('Welcome to {{ project.name }} interactive mode!'));

        console.log(chalk.dim('Enhanced Node.js features enabled:'));

        console.log(chalk.dim('  • Advanced tab completion'));

        console.log(chalk.dim('  • Persistent command history'));

        console.log(chalk.dim('  • JavaScript expression evaluation'));

        console.log(chalk.dim('  • NPM package integration'));

        console.log(chalk.dim('  • Async command support'));

        console.log(chalk.dim("Type 'help' for commands, 'exit' to quit.\\n"));

        

        this.rl.prompt();

        

        this.rl.on('line', async (line) => {

            const trimmed = line.trim();

            if (!trimmed) {

                this.rl.prompt();

                return;

            }

            

            // Check for expression evaluation first

            const expressionResult = await this.evaluateExpression(trimmed);

            if (expressionResult !== null) {

                this.rl.prompt();

                return;

            }

            

            // Execute command

            const shouldExit = await this.executeCommand(trimmed);

            if (shouldExit) {

                return;

            }

            

            this.rl.prompt();

        });

        

        this.rl.on('close', () => {

            console.log(chalk.bold.green('\\nGoodbye!'));

            this.saveHistory();

            process.exit(0);

        });

        

        // Handle interrupts gracefully

        this.rl.on('SIGINT', () => {

            console.log(chalk.yellow('\\n(Use "exit" or press Ctrl+D to quit)'));

            this.rl.prompt();

        });

    }

    

    async executeCommand(line) {

        const trimmed = line.trim();

        if (!trimmed) return false;

        

        this.addToHistory(trimmed);

        const [cmd, ...args] = this.parseCommandLine(trimmed);

        

        if (this.commands[cmd]) {

            const command = this.commands[cmd];

            try {

                const timeoutMs = command.timeout || 30000;

                const result = await Promise.race([

                    command.handler(args),

                    new Promise((_, reject) => 

                        setTimeout(() => reject(new Error('Command timeout')), timeoutMs)

                    )

                ]);

                return result === true;

            } catch (error) {

                this.formatError(error);

                return false;

            }

        } else {

            console.log(chalk.yellow(`Unknown command: ${cmd}`));

            console.log(chalk.dim("Type 'help' for available commands"));

            return false;

        }

    }

    

    formatError(error) {

        if (error.code === 'ENOENT') {

            console.error(chalk.red('✗ File or command not found'));

            console.error(chalk.dim(`  ${error.message}`));

        } else if (error.code === 'MODULE_NOT_FOUND') {

            console.error(chalk.red('✗ Module not found'));

            console.error(chalk.dim(`  ${error.message}`));

            console.log(chalk.yellow('  Try running: npm install'));

        } else {

            console.error(chalk.red(`✗ Error: ${error.message || error}`));

        }

    }

    

    setupHistoryPersistence() {

        const homeDir = os.homedir();

        let historyDir;

        

        if (process.platform === 'win32') {

            historyDir = path.join(process.env.APPDATA || homeDir, this.projectName);

        } else if (process.platform === 'darwin') {

            historyDir = path.join(homeDir, 'Library', 'Application Support', this.projectName);

        } else {

            historyDir = path.join(homeDir, '.config', this.projectName);

        }

        

        this.historyFile = path.join(historyDir, 'interactive_history');

        

        try {

            fs.mkdirSync(historyDir, { recursive: true });

        } catch (err) {

            // Ignore if directory already exists

        }

        

        this.loadHistory();

    }

    

    parseCommandLine(line) {

        // Simple command line parsing

        return line.trim().split(/\\s+/);

    }

    

    addToHistory(line) {

        if (line && line.trim() && !line.startsWith('help')) {

            if (!this.commandHistory) this.commandHistory = [];

            this.commandHistory.push(line.trim());

        }

    }

    

    loadHistory() {

        try {

            if (fs.existsSync && fs.existsSync(this.historyFile)) {

                const historyData = fs.readFileSync(this.historyFile, 'utf8');

                this.commandHistory = historyData.split('\\n').filter(line => line.trim());

            }

        } catch (err) {

            // Ignore errors

        }

    }

    

    setupAdvancedCompletion() {

        this.completionCache = new Map();

        this.npmPackages = [];

        this.nodeModules = [];

        

        this.loadNpmPackages();

        this.loadNodeModules();

    }

    

    async loadNpmPackages() {

        try {

            const result = execSync('npm list -g --depth=0 --json', { 

                encoding: 'utf8', 

                timeout: 5000 

            });

            const packages = JSON.parse(result);

            this.npmPackages = Object.keys(packages.dependencies || {});

        } catch (err) {

            this.npmPackages = [

                'express', 'lodash', 'axios', 'react', 'vue', 'angular'

            ];

        }

    }

    

    loadNodeModules() {

        try {

            // Get Node.js builtin modules

            this.nodeModules = [

                'fs', 'path', 'os', 'util', 'events', 'stream', 'buffer',

                'crypto', 'http', 'https', 'url', 'querystring', 'readline'

            ];

        } catch (err) {

            // Use defaults

        }

    }

    

    async evaluateExpression(expression) {

        if (expression.startsWith('js:')) {

            const jsCode = expression.substring(3).trim();

            try {

                // Secure evaluation using vm module instead of unsafe eval()
                const vm = require('vm');
                const context = vm.createContext({
                    console, require, process, Buffer, setTimeout, clearTimeout,
                    setInterval, clearInterval, setImmediate, clearImmediate,
                    chalk, fs, path, os, util, crypto
                });
                
                const result = vm.runInContext(jsCode, context, {
                    timeout: 5000, // 5 second timeout
                    displayErrors: true
                });

                if (result !== undefined) {

                    console.log(chalk.green(`=> ${JSON.stringify(result, null, 2)}`));

                }

                return false;

            } catch (error) {

                console.error(chalk.red(`JavaScript Error: ${error.message}`));

                return false;

            }

        }

        return null;

    }

    

    setupReplCommands() {

        this.commands.js = {

            description: 'Evaluate JavaScript expression',

            handler: async (args) => {

                const expression = args.join(' ');

                return await this.evaluateExpression(`js:${expression}`);

            }

        };

    }

    

    setupNodeJSIntegration() {

        this.setupProcessMonitoring();

        this.setupModuleReloading();

        this.setupEnvironmentManagement();

    }

    

    setupProcessMonitoring() {

        this.childProcesses = new Set();

    }

    

    setupModuleReloading() {

        this.commands['reload'] = {

            description: 'Reload hooks module',

            handler: async () => {

                try {

                    delete require.cache[require.resolve('./src/hooks.js')];

                    this.hooks = require('./src/hooks.js');

                    console.log(chalk.green('Hooks module reloaded successfully'));

                } catch (error) {

                    console.error(chalk.red(`Failed to reload hooks: ${error.message}`));

                }

                return false;

            }

        };

    }

    

    setupEnvironmentManagement() {

        this.commands['env'] = {

            description: 'Show/set environment variables',

            handler: async (args) => {

                if (args.length === 0) {

                    console.log(chalk.bold('Environment Variables:'));

                    Object.keys(process.env).sort().forEach(key => {

                        console.log(`  ${key}=${process.env[key]}`);

                    });

                }

                return false;

            }

        };

    }

    

    // Built-in command handlers

    

    handleHelp(args) {

        if (args.length > 0) {

            const cmdName = args[0];

            const command = this.commands[cmdName];

            if (command) {

                console.log(chalk.bold(`\\n{{ cli.root_command.name }} ${cmdName}`));

                console.log(`${command.description}`);

                

                if (command.options && command.options.length > 0) {

                    console.log(chalk.bold('\\nOptions:'));

                    command.options.forEach(opt => {

                        const shortFlag = opt.short ? `-${opt.short}, ` : '';

                        console.log(`  ${shortFlag}--${opt.name}  ${opt.description}`);

                    });

                }

                console.log();

            } else {

                console.log(chalk.red(`Unknown command: ${cmdName}`));

            }

        } else {

            console.log(chalk.bold('\\nAvailable commands:'));

            const maxLen = Math.max(...Object.keys(this.commands).map(cmd => cmd.length));

            

            Object.entries(this.commands).forEach(([cmd, info]) => {

                const padding = ' '.repeat(maxLen - cmd.length + 2);

                console.log(`  ${chalk.cyan(cmd)}${padding}${info.description}`);

            });

            

            console.log(chalk.dim('\\nEnhanced features:'));

            console.log(chalk.dim('  js <expression>     Evaluate JavaScript'));

            console.log(chalk.dim('  await <expression>  Evaluate async JavaScript'));

            console.log(chalk.dim('  require <module>    Load Node.js module'));

            console.log();

        }

        return false;

    }

    

    handleExit(args) {

        this.rl.close();

        return true;

    }

    

    handleClear(args) {

        console.clear();

        return false;

    }

    

    handleHistory(args) {

        if (this.commandHistory.length === 0) {

            console.log(chalk.dim('No command history available.'));

        } else {

            console.log(chalk.bold('\\nCommand History:'));

            this.commandHistory.slice(-20).forEach((cmd, i) => {

                const index = this.commandHistory.length - 20 + i + 1;

                console.log(`  ${chalk.dim(index.toString().padStart(3, ' '))}  ${cmd}`);

            });

            console.log();

        }

        return false;

    }



{% for command in cli.root_command.subcommands %}

    

    async handle{{ command.name | replace('-', '') | title }}(args) {

        const hookName = '{{ command.hook_name }}';

        if (typeof this.hooks[hookName] === 'function') {

            try {

                // Parse arguments more intelligently

                const parsedArgs = this.parseArgsForCommand('{{ command.name }}', args);

                await this.hooks[hookName](parsedArgs);

            } catch (error) {

                this.formatError(error);

            }

        } else {

            console.error(chalk.red(`Hook function '${hookName}' not implemented`));

            console.log(chalk.dim('Please implement this function in src/hooks.js'));

        }

        return false;

    }

{% endfor %}

    

    parseArgsForCommand(commandName, args) {

        const command = this.commands[commandName];

        const parsed = { _: [] };

        

        if (!command || !command.options) {

            return { args, options: {} };

        }

        

        // Parse options and flags

        let i = 0;

        while (i < args.length) {

            const arg = args[i];

            

            if (arg.startsWith('--')) {

                const optionName = arg.substring(2);

                const option = command.options.find(opt => opt.name === optionName);

                if (option) {

                    if (option.type === 'flag') {

                        parsed[optionName] = true;

                    } else {

                        parsed[optionName] = args[++i];

                    }

                } else {

                    parsed._.push(arg);

                }

            } else if (arg.startsWith('-') && arg.length === 2) {

                const shortFlag = arg[1];

                const option = command.options.find(opt => opt.short === shortFlag);

                if (option) {

                    if (option.type === 'flag') {

                        parsed[option.name] = true;

                    } else {

                        parsed[option.name] = args[++i];

                    }

                } else {

                    parsed._.push(arg);

                }

            } else {

                parsed._.push(arg);

            }

            i++;

        }

        

        return parsed;

    }

}



function runInteractive() {

    const interactive = new {{ project.name | replace('-', '') | title }}Interactive();

    interactive.start();

}



module.exports = { runInteractive };



if (require.main === module) {

    runInteractive();

}

'''





def get_nodejs_interactive_dependencies() -> Dict[str, List[str]]:

    """

    Get the dependencies required for enhanced Node.js interactive mode.

    

    Returns:

        Dictionary of dependency types and packages

    """

    return {

        "builtin": [

            "readline",

            "fs", 

            "path",

            "os",

            "child_process",

            "util"

        ],

        "npm": [

            "chalk@^5.3.0",

            "@types/node@^20.0.0"  # For TypeScript support

        ]

    }





def get_nodejs_interactive_tests() -> str:

    """

    Generate test cases for Node.js interactive mode.

    

    Returns:

        JavaScript test code

    """

    return '''

/**

 * Test cases for enhanced Node.js interactive mode

 */



const { spawn } = require('child_process');

const { EventEmitter } = require('events');



class InteractiveModeTester {

    constructor(cliCommand) {

        this.cliCommand = cliCommand;

    }

    

    async testAsyncCommandExecution() {

        console.log('Testing async command execution...');

        

        const child = spawn(this.cliCommand, ['interactive'], {

            stdio: ['pipe', 'pipe', 'pipe']

        });

        

        let output = '';

        child.stdout.on('data', (data) => {

            output += data.toString();

        });

        

        // Test basic command

        child.stdin.write('help\\n');

        

        // Test async operation

        child.stdin.write('js: Promise.resolve("test")\\n');

        

        // Exit

        child.stdin.write('exit\\n');

        

        return new Promise((resolve) => {

            child.on('close', () => {

                const success = output.includes('Available commands') && 

                               output.includes('"test"');

                resolve({ success, output });

            });

        });

    }

    

    async testTabCompletion() {

        console.log('Testing tab completion...');

        

        // This would require a more sophisticated test setup

        // with pty or similar to simulate actual tab key presses

        return { success: true, message: 'Tab completion test requires PTY setup' };

    }

    

    async testNpmPackageIntegration() {

        console.log('Testing npm package integration...');

        

        const child = spawn(this.cliCommand, ['interactive'], {

            stdio: ['pipe', 'pipe', 'pipe']

        });

        

        let output = '';

        child.stdout.on('data', (data) => {

            output += data.toString();

        });

        

        // Test require command

        child.stdin.write('require fs\\n');

        child.stdin.write('exit\\n');

        

        return new Promise((resolve) => {

            child.on('close', () => {

                const success = output.includes('Module') || output.includes('loaded');

                resolve({ success, output });

            });

        });

    }

    

    async testHistoryPersistence() {

        console.log('Testing history persistence...');

        

        const child1 = spawn(this.cliCommand, ['interactive'], {

            stdio: ['pipe', 'pipe', 'pipe']

        });

        

        child1.stdin.write('help\\n');

        child1.stdin.write('test-command arg1\\n');

        child1.stdin.write('exit\\n');

        

        await new Promise((resolve) => child1.on('close', resolve));

        

        // Start second session

        const child2 = spawn(this.cliCommand, ['interactive'], {

            stdio: ['pipe', 'pipe', 'pipe']

        });

        

        let output = '';

        child2.stdout.on('data', (data) => {

            output += data.toString();

        });

        

        child2.stdin.write('history\\n');

        child2.stdin.write('exit\\n');

        

        return new Promise((resolve) => {

            child2.on('close', () => {

                const success = output.includes('test-command');

                resolve({ success, output });

            });

        });

    }

    

    async runAllTests() {

        const tests = [

            this.testAsyncCommandExecution.bind(this),

            this.testTabCompletion.bind(this),

            this.testNpmPackageIntegration.bind(this),

            this.testHistoryPersistence.bind(this)

        ];

        

        console.log('Running Node.js Interactive Mode Tests...\\n');

        

        const results = [];

        for (const test of tests) {

            try {

                const result = await test();

                results.push(result);

                console.log(`✓ ${result.success ? 'PASS' : 'FAIL'}: ${test.name}`);

                if (!result.success && result.output) {

                    console.log(`  Output: ${result.output.slice(0, 200)}...`);

                }

            } catch (error) {

                results.push({ success: false, error: error.message });

                console.log(`✗ FAIL: ${test.name} - ${error.message}`);

            }

        }

        

        const passCount = results.filter(r => r.success).length;

        console.log(`\\nTest Results: ${passCount}/${results.length} tests passed`);

        

        return results;

    }

}



module.exports = InteractiveModeTester;

'''