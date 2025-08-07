"""
Node.js Interactive Mode Utilities (Simplified)

This module provides Node.js-specific utilities for enhanced interactive mode features,
including async command handling, Node.js-specific error formatting, history management,
and tab completion for npm packages and Node.js modules.
"""

import json
import os
from typing import Dict, List, Optional, Any


class NodeJSInteractiveUtils:
    """Utilities for Node.js interactive mode features."""
    
    @staticmethod
    def get_enhanced_readline_config() -> Dict[str, Any]:
        """Get enhanced readline configuration with custom key bindings."""
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
        """Generate async command handling code for Node.js."""
        return '''
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
'''
    
    @staticmethod
    def get_error_formatter() -> str:
        """Generate Node.js-specific error formatting code."""
        return '''
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
'''
    
    @staticmethod
    def get_history_manager() -> str:
        """Generate history management code with file persistence."""
        return '''
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
'''
    
    @staticmethod
    def get_completion_engine() -> str:
        """Generate advanced tab completion for Node.js-specific features."""
        return '''
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
            // Get Node.js built-in modules
            this.nodeModules = [
                'fs', 'path', 'os', 'util', 'events', 'stream', 'buffer',
                'crypto', 'http', 'https', 'url', 'querystring', 'readline'
            ];
        } catch (err) {
            // Use defaults
        }
    }
'''
    
    @staticmethod
    def get_repl_evaluation() -> str:
        """Generate JavaScript expression evaluation support."""
        return '''
    async evaluateExpression(expression) {
        if (expression.startsWith('js:')) {
            const jsCode = expression.substring(3).trim();
            try {
                const result = eval(jsCode);
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
'''
    
    @staticmethod
    def get_integration_features() -> str:
        """Generate Node.js integration features."""
        return '''
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
'''
    
    @classmethod
    def generate_enhanced_interactive_template(cls) -> str:
        """Generate the complete enhanced Node.js interactive mode template."""
        return "Enhanced Node.js interactive template available at: templates/nodejs/interactive_mode_enhanced.js.j2"


def get_nodejs_interactive_dependencies() -> Dict[str, List[str]]:
    """Get the dependencies required for enhanced Node.js interactive mode."""
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
            "@types/node@^20.0.0"
        ]
    }


def get_nodejs_interactive_tests() -> str:
    """Generate test cases for Node.js interactive mode."""
    return '''
const { spawn } = require('child_process');

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
        
        child.stdin.write('help\\n');
        child.stdin.write('js: Promise.resolve("test")\\n');
        child.stdin.write('exit\\n');
        
        return new Promise((resolve) => {
            child.on('close', () => {
                const success = output.includes('Available commands') && 
                               output.includes('"test"');
                resolve({ success, output });
            });
        });
    }
    
    async runAllTests() {
        const tests = [this.testAsyncCommandExecution.bind(this)];
        const results = [];
        
        for (const test of tests) {
            try {
                const result = await test();
                results.push(result);
                console.log(`✓ ${result.success ? 'PASS' : 'FAIL'}: ${test.name}`);
            } catch (error) {
                results.push({ success: false, error: error.message });
                console.log(`✗ FAIL: ${test.name} - ${error.message}`);
            }
        }
        
        return results;
    }
}

module.exports = InteractiveModeTester;
'''