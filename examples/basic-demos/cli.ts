#!/usr/bin/env node
/**
 * Auto-generated from typescript-example.yaml
 * Demo TypeScript CLI CLI - TypeScript Implementation
 */

import { Command } from 'commander';
import * as path from 'path';
import * as fs from 'fs';
import { spawn, execSync } from 'child_process';
import { createRequire } from 'module';
import { fileURLToPath } from 'url';

// Create require function for ES modules
const require = createRequire(import.meta.url);
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Enhanced Error Classes
class CLIError extends Error {
    public exitCode: number;
    public suggestion: string | null;

    constructor(message: string, exitCode: number = 1, suggestion: string | null = null) {
        super(message);
        this.name = 'CLIError';
        this.exitCode = exitCode;
        this.suggestion = suggestion;
    }
}

class ConfigError extends CLIError {
    constructor(message: string, suggestion: string | null = null) {
        super(message, 2, suggestion);
        this.name = 'ConfigError';
    }
}

class HookError extends CLIError {
    public hookName: string | null;

    constructor(message: string, hookName: string | null = null) {
        const suggestion = hookName ? `Check the '${hookName}' function in your hooks file` : null;
        super(message, 3, suggestion);
        this.name = 'HookError';
        this.hookName = hookName;
    }
}

class DependencyError extends CLIError {
    public dependency: string;
    public installCommand: string | null;

    constructor(message: string, dependency: string, installCommand: string | null = null) {
        const suggestion = installCommand ? `Install with: ${installCommand}` : `Install the '${dependency}' package`;
        super(message, 4, suggestion);
        this.name = 'DependencyError';
        this.dependency = dependency;
        this.installCommand = installCommand;
    }
}

// Interface definitions
interface GlobalOptions {
    
}

interface CommandArgs {
    [key: string]: any;
}

interface HookFunction {
    (args: CommandArgs): Promise<any> | any;
}

interface ManagedCommand {
    execute(args: CommandArgs): Promise<any> | any;
}

interface AppHooks {
    [key: string]: HookFunction | ManagedCommand;
}

// Global error handler
function handleCLIError(error: Error, verbose: boolean = false): number {
    if (error instanceof CLIError) {
        console.error(`❌ Error: ${error.message}`);
        if (error.suggestion) {
            console.error(`💡 Suggestion: ${error.suggestion}`);
        }
        if (verbose) {
            console.error('\n🔍 Verbose traceback:');
            console.error(error.stack);
        }
        return error.exitCode;
    } else {
        // Unexpected errors
        console.error(`❌ Unexpected error: ${error.message}`);
        console.error('💡 This may be a bug. Please report it with the following details:');
        if (verbose) {
            console.error(error.stack);
        } else {
            console.error(`   Error type: ${error.constructor.name}`);
            console.error(`   Error message: ${error.message}`);
            console.error('   Run with --verbose for full traceback');
        }
        return 1;
    }
}

// Helper module loading with error handling
let configManager: any, progressHelper: any, promptsHelper: any, completionHelper: any;
let HAS_CONFIG_MANAGER = false;
let HAS_PROGRESS_HELPER = false;
let HAS_PROMPTS_HELPER = false;
let HAS_COMPLETION_HELPER = false;

try {
    configManager = require('./lib/config');
    HAS_CONFIG_MANAGER = true;
} catch (e) {
    if (process.env.DEBUG) console.debug('Config manager not available:', (e as Error).message);
}

try {
    progressHelper = require('./lib/progress');
    HAS_PROGRESS_HELPER = true;
} catch (e) {
    if (process.env.DEBUG) console.debug('Progress helper not available:', (e as Error).message);
}

try {
    promptsHelper = require('./lib/prompts');
    HAS_PROMPTS_HELPER = true;
} catch (e) {
    if (process.env.DEBUG) console.debug('Prompts helper not available:', (e as Error).message);
}

try {
    completionHelper = require('./lib/completion');
    HAS_COMPLETION_HELPER = true;
} catch (e) {
    if (process.env.DEBUG) console.debug('Completion helper not available:', (e as Error).message);
}

// Initialize global helpers
let config: any = null;
let progress: any = null;
let prompts: any = null;
let completion: any = null;

if (HAS_CONFIG_MANAGER) {
    try {
        config = configManager.getConfig();
    } catch (e) {
        console.warn(`Failed to initialize config manager: ${(e as Error).message}`);
        HAS_CONFIG_MANAGER = false;
    }
}

if (HAS_PROGRESS_HELPER) {
    try {
        progress = progressHelper.getProgressHelper();
    } catch (e) {
        console.warn(`Failed to initialize progress helper: ${(e as Error).message}`);
        HAS_PROGRESS_HELPER = false;
    }
}

if (HAS_PROMPTS_HELPER) {
    try {
        prompts = promptsHelper.getPromptsHelper();
    } catch (e) {
        console.warn(`Failed to initialize prompts helper: ${(e as Error).message}`);
        HAS_PROMPTS_HELPER = false;
    }
}

if (HAS_COMPLETION_HELPER) {
    try {
        completion = completionHelper.getCompletionHelper();
    } catch (e) {
        console.warn(`Failed to initialize completion helper: ${(e as Error).message}`);
        HAS_COMPLETION_HELPER = false;
    }
}

// Load hooks module
let appHooks: AppHooks | null = null;

// No hooks path configured, try default locations
try {
    // Try relative to script location
    const possiblePaths = [
        path.join(process.cwd(), 'src/hooks.js'),  // Prioritize compiled local hooks
        path.join(process.cwd(), 'src/hooks.ts'),
        path.join(process.cwd(), 'hooks.js'),
        path.join(process.cwd(), 'hooks.ts'),
        path.join(__dirname, '../src/hooks.js'),
        path.join(__dirname, '../src/hooks.ts'),
        path.join(__dirname, '../hooks.js'),
        path.join(__dirname, '../hooks.ts')
    ];
    
    for (const hookPath of possiblePaths) {
        if (fs.existsSync(hookPath)) {
            try {
                appHooks = require(hookPath);
                break;
            } catch (err) {
                // Failed to load this hooks file, try next
            }
        }
    }
} catch (e) {
    // No hooks module found
}


// Get version function
function getVersion(): string {
    try {
        // Try package.json first
        const packagePath = path.join(__dirname, '../package.json');
        if (fs.existsSync(packagePath)) {
            const pkg = JSON.parse(fs.readFileSync(packagePath, 'utf8'));
            return pkg.version;
        }
    } catch (e) {
        // Ignore
    }
    
    // Fallback to configured version
    
    return '1.0.0';
    
}

// Built-in upgrade command

async function builtinUpgradeCommand(checkOnly: boolean = false, pre: boolean = false, version: string | null = null, dryRun: boolean = false): Promise<void> {
    if (checkOnly) {
        console.log(`Checking for updates to Demo TypeScript CLI...`);
        console.log('Update check not yet implemented. Run without --check to upgrade.');
        return;
    }

    if (dryRun) {
        console.log('Dry run - would execute: npm update -g demo-typescript-cli');
        return;
    }

    // Find the setup.sh script
    let setupScript: string | null = null;
    const searchPaths = [
        path.join(__dirname, 'setup.sh'),
        path.join(__dirname, '../setup.sh'),
        path.join(process.env.HOME || process.env.USERPROFILE || '', '.local', 'share', 'demo-typescript-cli', 'setup.sh')
    ];
    
    for (const scriptPath of searchPaths) {
        if (fs.existsSync(scriptPath)) {
            setupScript = scriptPath;
            break;
        }
    }
    
    if (!setupScript) {
        // Fallback to basic upgrade
        console.log(`Enhanced setup script not found. Using basic upgrade for Demo TypeScript CLI...`);
        
        const packageName = 'demo-typescript-cli';
        const npmName = 'demo-typescript-cli';
        
        try {
            const cmd = process.platform === 'win32' ? 'npm.cmd' : 'npm';
            execSync(`${cmd} update -g ${npmName}`, { stdio: 'inherit' });
            console.log(`✅ Demo TypeScript CLI upgraded successfully!`);
            console.log(`Run 'demo_ts --version' to verify the new version.`);
        } catch (e) {
            console.error(`❌ Upgrade failed: ${(e as Error).message}`);
            process.exit(1);
        }
        return;
    }

    // Use the enhanced setup.sh script
    try {
        execSync(`${setupScript} upgrade`, { stdio: 'inherit' });
    } catch (e: any) {
        process.exit(e.status || 1);
    }
}


// Plugin loading
function loadPlugins(program: Command): void {
    const pluginDirs = [
        path.join(process.env.HOME || process.env.USERPROFILE || '', '.config', 'goobits', 'demo_ts', 'plugins'),
        path.join(__dirname, 'plugins')
    ];
    
    for (const pluginDir of pluginDirs) {
        if (!fs.existsSync(pluginDir)) continue;
        
        const files = fs.readdirSync(pluginDir);
        for (const file of files) {
            if (!file.endsWith('.js') && !file.endsWith('.ts')) continue;
            if (file.startsWith('_')) continue;
            if (['loader.js', 'loader.ts', 'index.js', 'index.ts'].includes(file)) continue;
            
            const pluginName = path.basename(file, path.extname(file));
            
            try {
                const pluginPath = path.join(pluginDir, file);
                const plugin = require(pluginPath);
                
                if (typeof plugin.registerPlugin === 'function') {
                    plugin.registerPlugin(program);
                    console.error(`Loaded plugin: ${pluginName}`);
                }
            } catch (e) {
                console.error(`Failed to load plugin ${pluginName}: ${(e as Error).message}`);
            }
        }
    }
}

// Create the main program
const program = new Command();

// Configure program
program
    .name('demo_ts')
    .version(getVersion())
    .description(`demo_ts v${getVersion()} - TypeScript CLI demonstration`)
    .helpOption('-h, --help', 'Display help for command')
    .configureHelp({
        sortSubcommands: true,
        sortOptions: true
    });

// Add custom help formatting
program.addHelpText('after', `



`);

// Global options
const globalOptions: Partial<GlobalOptions> = {};


// Built-in upgrade command

program
    .command('upgrade')
    .description('Upgrade Demo TypeScript CLI to the latest version')
    .option('--check', 'Check for updates without installing')
    .option('--version <version>', 'Install specific version')
    .option('--pre', 'Include pre-release versions')
    .option('--dry-run', 'Show what would be done without doing it')
    .action(async (options: { check?: boolean; version?: string; pre?: boolean; dryRun?: boolean }) => {
        await builtinUpgradeCommand(options.check, options.pre, options.version, options.dryRun);
    });


// Commands from configuration


// Command: calculate
interface CalculateOptions {
    
    precision: number | undefined;
    
    verbose?: boolean;
}

const calculateCmd = program
    .command('calculate')
    .description('Perform calculations')
    
    .argument('<operation>', 'Math operation')
    
    .argument('<a>', 'First number')
    
    .argument('<b>', 'Second number')
    
    
    .option('-p, --precision <value>', 'Decimal precision', '2')
    
    .action(async (operation: string, a: string, b: string, options: CalculateOptions, command: Command) => {
        try {
            // Validate operation choices
            const validOperations = ['add', 'subtract', 'multiply', 'divide'];
            if (!validOperations.includes(operation)) {
                console.error(`Error: Invalid operation '${operation}'. Valid operations: ${validOperations.join(', ')}`);
                process.exit(1);
            }
            
            // Standard command - use hook pattern
            const hookName = 'onCalculate';
            if (appHooks && typeof appHooks[hookName] === 'function') {
                const kwargs: CommandArgs = {
                    commandName: 'calculate',
                    
                    
                    operation: operation,
                    
                    a: a,
                    
                    b: b,
                    
                    
                    ...options,
                    // Add global options
                    
                };
                
                await (appHooks[hookName] as HookFunction)(kwargs);
            } else {
                // Default placeholder behavior
                console.log(`Executing calculate command...`);
                
                
                console.log(`  operation: $${operation}`);  
                
                console.log(`  a: $${a}`);  
                
                console.log(`  b: $${b}`);  
                
                
                
                
                console.log(`  precision: ${options.precision}`);
                
                
            }
            
        } catch (error) {
            const exitCode = handleCLIError(error as Error, options.verbose || false);
            process.exit(exitCode);
        }
    });




// Command: status
interface StatusOptions {
    
    verbose?: boolean;
}

const statusCmd = program
    .command('status')
    .description('Show TypeScript environment status')
    
    
    .action(async (options: StatusOptions, command: Command) => {
        try {
            
            // Standard command - use hook pattern
            const hookName = 'onStatus';
            if (appHooks && typeof appHooks[hookName] === 'function') {
                const kwargs: CommandArgs = {
                    commandName: 'status',
                    
                    ...options,
                    // Add global options
                    
                };
                
                await (appHooks[hookName] as HookFunction)(kwargs);
            } else {
                // Default placeholder behavior
                console.log(`Executing status command...`);
                
                
            }
            
        } catch (error) {
            const exitCode = handleCLIError(error as Error, options.verbose || false);
            process.exit(exitCode);
        }
    });




// Completion commands
const completionCmd = program
    .command('completion')
    .description('🔧 Shell completion management');

completionCmd
    .command('generate <shell>')
    .description('Generate shell completion script')
    .option('-o, --output <file>', 'Output file path')
    .action((shell: string, options: { output?: string }) => {
        if (!HAS_COMPLETION_HELPER) {
            console.error('❌ Completion helper not available. Missing completion module.');
            return;
        }
        
        try {
            const script = completion.generateCompletionScript(shell);
            
            if (options.output) {
                fs.writeFileSync(options.output, script);
                console.log(`✅ ${shell} completion script saved to: ${options.output}`);
            } else {
                console.log(script);
            }
        } catch (e) {
            console.error(`❌ Error generating ${shell} completion: ${(e as Error).message}`);
        }
    });

completionCmd
    .command('install <shell>')
    .description('Install shell completion script')
    .option('--user', 'Install for current user (default)', true)
    .option('--system', 'Install system-wide (requires sudo)')
    .action(async (shell: string, options: { user?: boolean; system?: boolean }) => {
        if (!HAS_COMPLETION_HELPER) {
            console.error('❌ Completion helper not available. Missing completion module.');
            return;
        }
        
        try {
            const userInstall = !options.system;
            const success = await completion.installCompletion(shell, userInstall);
            
            if (success) {
                console.log(`✅ ${shell} completion installed successfully!`);
                
                const instructions = completion.getInstallInstructions(shell);
                if (instructions && instructions.reloadCmd) {
                    console.log(`💡 Reload your shell: ${instructions.reloadCmd}`);
                }
            } else {
                console.error(`❌ Failed to install ${shell} completion`);
            }
        } catch (e) {
            console.error(`❌ Error installing ${shell} completion: ${(e as Error).message}`);
        }
    });

completionCmd
    .command('instructions <shell>')
    .description('Show installation instructions for shell completion')
    .action((shell: string) => {
        if (!HAS_COMPLETION_HELPER) {
            console.error('❌ Completion helper not available. Missing completion module.');
            return;
        }
        
        const instructions = completion.getInstallInstructions(shell);
        if (!instructions) {
            console.error(`❌ No instructions available for ${shell}`);
            return;
        }
        
        console.log(`📋 ${shell} completion installation instructions:\n`);
        
        console.log('🏠 User installation (recommended):');
        console.log(`   mkdir -p ${path.dirname(instructions.userScriptPath)}`);
        console.log(`   demo_ts completion generate ${shell} > completion.${shell}`);
        console.log(`   cp completion.${shell} ${instructions.userScriptPath}\n`);
        
        console.log('🌐 System-wide installation:');
        console.log(`   demo_ts completion generate ${shell} > completion.${shell}`);
        console.log(`   ${instructions.installCmd}\n`);
        
        console.log('🔄 Reload shell:');
        console.log(`   ${instructions.reloadCmd}`);
    });

// Hidden internal completion command
program
    .command('_completion <shell> <currentLine> [cursorPos]', { hidden: true })
    .option('--debug', 'Debug completion engine')
    .action((shell: string, currentLine: string, cursorPos?: string, options?: { debug?: boolean }) => {
        try {
            const enginePath = path.join(__dirname, 'completion_engine.js');
            
            if (fs.existsSync(enginePath)) {
                const CompletionEngine = require(enginePath).CompletionEngine;
                const engine = new CompletionEngine();
                const completions = engine.getCompletions(shell, currentLine, cursorPos);
                
                completions.forEach((completion: string) => console.log(completion));
            } else if (options?.debug) {
                console.error('completion_engine.js not found');
            }
        } catch (e) {
            if (options?.debug) {
                console.error(`Completion error: ${(e as Error).message}`);
            }
        }
    });

// Config commands
const configCmd = program
    .command('config')
    .description('⚙️ Configuration management');

configCmd
    .command('get [key]')
    .description('Get configuration value')
    .action((key?: string) => {
        if (!HAS_CONFIG_MANAGER) {
            console.error('❌ Configuration manager not available.');
            return;
        }
        
        try {
            if (key) {
                const value = config.getConfigValue(key);
                if (value !== null && value !== undefined) {
                    console.log(`${key}: ${value}`);
                } else {
                    console.error(`❌ Configuration key '${key}' not found`);
                }
            } else {
                // Show all configuration
                const configData = config.loadConfig();
                console.log(JSON.stringify(configData, null, 2));
            }
        } catch (e) {
            console.error(`❌ Error getting configuration: ${(e as Error).message}`);
        }
    });

configCmd
    .command('set <key> <value>')
    .description('Set configuration value')
    .action((key: string, value: string) => {
        if (!HAS_CONFIG_MANAGER) {
            console.error('❌ Configuration manager not available.');
            return;
        }
        
        try {
            // Try to parse value as JSON for complex types
            let parsedValue: any;
            try {
                parsedValue = JSON.parse(value);
            } catch (e) {
                parsedValue = value;
            }
            
            const success = config.setConfigValue(key, parsedValue);
            if (success) {
                console.log(`✅ Set ${key} = ${parsedValue}`);
            } else {
                console.error('❌ Failed to set configuration value');
            }
        } catch (e) {
            console.error(`❌ Error setting configuration: ${(e as Error).message}`);
        }
    });

configCmd
    .command('reset')
    .description('Reset configuration to defaults')
    .action(async () => {
        if (!HAS_CONFIG_MANAGER) {
            console.error('❌ Configuration manager not available.');
            return;
        }
        
        try {
            if (HAS_PROMPTS_HELPER) {
                const confirmed = await prompts.confirm('Are you sure you want to reset all configuration to defaults?');
                if (confirmed) {
                    config.reset();
                    console.log('✅ Configuration reset to defaults');
                } else {
                    console.log('❌ Reset cancelled');
                }
            } else {
                config.reset();
                console.log('✅ Configuration reset to defaults');
            }
        } catch (e) {
            console.error(`❌ Error resetting configuration: ${(e as Error).message}`);
        }
    });

configCmd
    .command('path')
    .description('Show configuration file path')
    .action(() => {
        if (!HAS_CONFIG_MANAGER) {
            console.error('❌ Configuration manager not available.');
            return;
        }
        
        try {
            const configPath = config.getConfigPath();
            console.log(`📁 Configuration file: ${configPath}`);
            
            // Check for RC files
            const rcFile = config.findRcFile();
            if (rcFile) {
                console.log(`📄 Active RC file: ${rcFile}`);
            }
        } catch (e) {
            console.error(`❌ Error getting configuration path: ${(e as Error).message}`);
        }
    });










// CLI entry point
function cliEntry(): void {
    try {
        // Load plugins before parsing
        loadPlugins(program);
        
        // Parse command line
        program.parse(process.argv);
        
        // Show help if no args
        if (!process.argv.slice(2).length) {
            program.outputHelp();
        }
    } catch (e) {
        if ((e as any).code === 'commander.help') {
            // Normal help display
            process.exit(0);
        }
        
        // Get verbose flag from program options
        const verbose = program.opts().verbose || false;
        const exitCode = handleCLIError(e as Error, verbose);
        process.exit(exitCode);
    }
}

// Handle uncaught errors
process.on('uncaughtException', (error: Error) => {
    // Get verbose flag from program options if available, fallback to process.argv check
    const verbose = program.opts().verbose || process.argv.includes('--verbose');
    const exitCode = handleCLIError(error, verbose);
    process.exit(exitCode);
});

process.on('unhandledRejection', (reason: any, promise: Promise<any>) => {
    const error = reason instanceof Error ? reason : new Error(String(reason));
    // Get verbose flag from program options if available, fallback to process.argv check
    const verbose = program.opts().verbose || process.argv.includes('--verbose');
    const exitCode = handleCLIError(error, verbose);
    process.exit(exitCode);
});

// Handle Ctrl+C
process.on('SIGINT', () => {
    console.error('\n⏹️  Operation cancelled by user');
    process.exit(130); // Standard exit code for Ctrl+C
});

// Export for use as module
export { program, cliEntry };

// Run if called directly (ES module check)
const isMainModule = import.meta.url === `file://${process.argv[1]}`;
if (isMainModule) {
    cliEntry();
}