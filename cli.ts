#!/usr/bin/env node
/**
 * Auto-generated from test_typescript_2level.yaml
 * NodeJSTestCLI CLI - TypeScript Implementation
 */

import { Command, Argument } from 'commander';
import * as path from 'path';
import * as fs from 'fs';
import { execSync } from 'child_process';

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
    verbose: boolean | undefined;
    config: string | undefined;
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
        path.join(__dirname, '../hooks.ts'),
        path.join(__dirname, '../hooks.js'),
        path.join(__dirname, '../src/hooks.ts'),
        path.join(__dirname, '../src/hooks.js'),
        path.join(process.cwd(), 'hooks.ts'),
        path.join(process.cwd(), 'hooks.js'),
        path.join(process.cwd(), 'src/hooks.ts'),
        path.join(process.cwd(), 'src/hooks.js')
    ];
    
    for (const hookPath of possiblePaths) {
        if (fs.existsSync(hookPath)) {
            appHooks = require(hookPath);
            break;
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
    return '1.2.3';
}

// Built-in upgrade command
async function builtinUpgradeCommand(checkOnly: boolean = false, pre: boolean = false, version: string | null = null, dryRun: boolean = false): Promise<void> {
    if (checkOnly) {
        console.log(`Checking for updates to NodeJSTestCLI...`);
        console.log('Update check not yet implemented. Run without --check to upgrade.');
        return;
    }

    if (dryRun) {
        console.log('Dry run - would execute: npm update -g nodejs-test-cli');
        return;
    }

    // Find the setup.sh script
    let setupScript: string | null = null;
    const searchPaths = [
        path.join(__dirname, 'setup.sh'),
        path.join(__dirname, '../setup.sh'),
        path.join(process.env.HOME || process.env.USERPROFILE || '', '.local', 'share', 'nodejs-test-cli', 'setup.sh')
    ];
    
    for (const scriptPath of searchPaths) {
        if (fs.existsSync(scriptPath)) {
            setupScript = scriptPath;
            break;
        }
    }
    
    if (!setupScript) {
        // Fallback to basic upgrade
        console.log(`Enhanced setup script not found. Using basic upgrade for NodeJSTestCLI...`);
        
        const packageName = 'nodejs-test-cli';
        const npmName = 'nodejs-test-cli';
        
        try {
            const cmd = process.platform === 'win32' ? 'npm.cmd' : 'npm';
            execSync(`${cmd} update -g ${npmName}`, { stdio: 'inherit' });
            console.log(`✅ NodeJSTestCLI upgraded successfully!`);
            console.log(`Run 'nodejstestcli --version' to verify the new version.`);
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
        path.join(process.env.HOME || process.env.USERPROFILE || '', '.config', 'goobits', 'NodeJSTestCLI', 'plugins'),
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
    .name('NodeJSTestCLI')
    .version(getVersion())
    .description(`NodeJSTestCLI v${getVersion()} - A comprehensive Node.js CLI for testing all features.`)
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
program.option(
    '-v, --verbose',
    'Enable verbose logging');
program.option(
    '-c, --config <value>',
    'Path to configuration file');

// Built-in upgrade command
program
    .command('upgrade')
    .description('Upgrade NodeJSTestCLI to the latest version')
    .option('--check', 'Check for updates without installing')
    .option('--version <version>', 'Install specific version')
    .option('--pre', 'Include pre-release versions')
    .option('--dry-run', 'Show what would be done without doing it')
    .action(async (options: { check?: boolean; version?: string; pre?: boolean; dryRun?: boolean }) => {
        await builtinUpgradeCommand(options.check, options.pre, options.version, options.dryRun);
    });

// Commands from configuration
// Command: init
interface InitOptions {
    template: string | undefined;
    skipinstall: boolean | undefined;
    verbose?: boolean;
}

const initCmd = program
    .command('init')
    .description('Initialize a new project')
    .argument('<name>', 'Project name')
    .option('-t, --template <value>', 'Project template to use', 'default')
    .option('--skip-install', 'Skip npm install')
    .action(async (name: string, options: InitOptions, command: Command) => {
        try {
            // Standard command - use hook pattern
            const hookName = 'onInit';
            if (appHooks && typeof appHooks[hookName] === 'function') {
                const kwargs: CommandArgs = {
                    commandName: 'init',
                    name: name,
                    ...options,
                    // Add global options
                    verbose: (command.parent?.opts() as GlobalOptions)?.verbose,
                    config: (command.parent?.opts() as GlobalOptions)?.config,
                };
                
                await (appHooks[hookName] as HookFunction)(kwargs);
            } else {
                // Default placeholder behavior
                console.log(`Executing init command...`);
                console.log(`  name: $${name}`);  
                console.log(`  template: ${options.template}`);
                console.log(`  skip-install: ${options.skipinstall}`);
            }
        } catch (error) {
            const exitCode = handleCLIError(error as Error, options.verbose || false);
            process.exit(exitCode);
        }
    });

// Command: deploy
interface DeployOptions {
    force: boolean | undefined;
    dryrun: boolean | undefined;
    verbose?: boolean;
}

const deployCmd = program
    .command('deploy')
    .description('Deploy the application')
    .argument('<environment>', 'Target environment (dev, staging, prod)')
    .option('-f, --force', 'Force deployment without confirmation')
    .option('--dry-run', 'Simulate deployment without making changes')
    .action(async (environment: string, options: DeployOptions, command: Command) => {
        try {
            // Managed command - expect an instance
            const commandInstanceName = 'deployCommand';
            if (appHooks && appHooks[commandInstanceName]) {
                const commandInstance = appHooks[commandInstanceName] as ManagedCommand;
                const kwargs: CommandArgs = {
                    commandName: 'deploy',
                    environment: environment,
                    ...options,
                    // Add global options
                    verbose: (command.parent?.opts() as GlobalOptions)?.verbose,
                    config: (command.parent?.opts() as GlobalOptions)?.config,
                };
                
                if (typeof commandInstance.execute === 'function') {
                    await commandInstance.execute(kwargs);
                } else {
                    throw new Error(`Managed command 'deploy' must have an execute() method`);
                }
            } else {
                throw new Error(`Managed command 'deploy' requires 'deployCommand' export in hooks file`);
            }
        } catch (error) {
            const exitCode = handleCLIError(error as Error, options.verbose || false);
            process.exit(exitCode);
        }
    });

// Command group: server
const serverCmd = program
    .command('server')
    .description('Server management commands');

interface ServerStartOptions {
    port: number | undefined;
    daemon: boolean | undefined;
    verbose?: boolean;
}

serverCmd
    .command('start')
    .description('Start the server')
    .option('-p, --port <value>', 'Port to listen on', 8080)
    .option('-d, --daemon', 'Run as daemon')
    .action(async (options: ServerStartOptions, command: Command) => {
        try {
            const hookName = 'onServerStart';
            if (appHooks && typeof appHooks[hookName] === 'function') {
                const kwargs: CommandArgs = {
                    commandName: 'start',
                    ...options,
                    // Add global options
                    verbose: (command.parent?.parent?.opts() as GlobalOptions)?.verbose,
                    config: (command.parent?.parent?.opts() as GlobalOptions)?.config,
                };
                
                await (appHooks[hookName] as HookFunction)(kwargs);
            } else {
                // Default placeholder behavior
                console.log(`Executing start command...`);
                console.log(`  port: ${options.port}`);
                console.log(`  daemon: ${options.daemon}`);
            }
        } catch (error) {
            const exitCode = handleCLIError(error as Error, options.verbose || false);
            process.exit(exitCode);
        }
    });
interface ServerStopOptions {
    graceful: boolean | undefined;
    verbose?: boolean;
}

serverCmd
    .command('stop')
    .description('Stop the server')
    .option('--graceful', 'Graceful shutdown')
    .action(async (options: ServerStopOptions, command: Command) => {
        try {
            const hookName = 'onServerStop';
            if (appHooks && typeof appHooks[hookName] === 'function') {
                const kwargs: CommandArgs = {
                    commandName: 'stop',
                    ...options,
                    // Add global options
                    verbose: (command.parent?.parent?.opts() as GlobalOptions)?.verbose,
                    config: (command.parent?.parent?.opts() as GlobalOptions)?.config,
                };
                
                await (appHooks[hookName] as HookFunction)(kwargs);
            } else {
                // Default placeholder behavior
                console.log(`Executing stop command...`);
                console.log(`  graceful: ${options.graceful}`);
            }
        } catch (error) {
            const exitCode = handleCLIError(error as Error, options.verbose || false);
            process.exit(exitCode);
        }
    });
interface ServerRestartOptions {
    verbose?: boolean;
}

serverCmd
    .command('restart')
    .description('Restart the server')
    .argument('[service]', 'Service name to restart')
    .action(async (service: string, options: ServerRestartOptions, command: Command) => {
        try {
            const hookName = 'onServerRestart';
            if (appHooks && typeof appHooks[hookName] === 'function') {
                const kwargs: CommandArgs = {
                    commandName: 'restart',
                    service: service,
                    ...options,
                    // Add global options
                    verbose: (command.parent?.parent?.opts() as GlobalOptions)?.verbose,
                    config: (command.parent?.parent?.opts() as GlobalOptions)?.config,
                };
                
                await (appHooks[hookName] as HookFunction)(kwargs);
            } else {
                // Default placeholder behavior
                console.log(`Executing restart command...`);
                console.log(`  service: $${service}`);  
            }
        } catch (error) {
            const exitCode = handleCLIError(error as Error, options.verbose || false);
            process.exit(exitCode);
        }
    });

// Command group: database
const databaseCmd = program
    .command('database')
    .description('Database operations');

interface DatabaseMigrateOptions {
    direction: string | undefined;
    steps: number | undefined;
    verbose?: boolean;
}

databaseCmd
    .command('migrate')
    .description('Run database migrations')
    .option('--direction <value>', 'Migration direction (up/down)', 'up')
    .option('--steps <value>', 'Number of migrations to run')
    .action(async (options: DatabaseMigrateOptions, command: Command) => {
        try {
            const hookName = 'onDatabaseMigrate';
            if (appHooks && typeof appHooks[hookName] === 'function') {
                const kwargs: CommandArgs = {
                    commandName: 'migrate',
                    ...options,
                    // Add global options
                    verbose: (command.parent?.parent?.opts() as GlobalOptions)?.verbose,
                    config: (command.parent?.parent?.opts() as GlobalOptions)?.config,
                };
                
                await (appHooks[hookName] as HookFunction)(kwargs);
            } else {
                // Default placeholder behavior
                console.log(`Executing migrate command...`);
                console.log(`  direction: ${options.direction}`);
                console.log(`  steps: ${options.steps}`);
            }
        } catch (error) {
            const exitCode = handleCLIError(error as Error, options.verbose || false);
            process.exit(exitCode);
        }
    });
interface DatabaseSeedOptions {
    truncate: boolean | undefined;
    verbose?: boolean;
}

databaseCmd
    .command('seed')
    .description('Seed the database')
    .argument('[dataset]', 'Dataset to seed')
    .option('--truncate', 'Truncate tables before seeding')
    .action(async (dataset: string, options: DatabaseSeedOptions, command: Command) => {
        try {
            const hookName = 'onDatabaseSeed';
            if (appHooks && typeof appHooks[hookName] === 'function') {
                const kwargs: CommandArgs = {
                    commandName: 'seed',
                    dataset: dataset,
                    ...options,
                    // Add global options
                    verbose: (command.parent?.parent?.opts() as GlobalOptions)?.verbose,
                    config: (command.parent?.parent?.opts() as GlobalOptions)?.config,
                };
                
                await (appHooks[hookName] as HookFunction)(kwargs);
            } else {
                // Default placeholder behavior
                console.log(`Executing seed command...`);
                console.log(`  dataset: $${dataset}`);  
                console.log(`  truncate: ${options.truncate}`);
            }
        } catch (error) {
            const exitCode = handleCLIError(error as Error, options.verbose || false);
            process.exit(exitCode);
        }
    });
interface DatabaseBackupOptions {
    output: string | undefined;
    compress: boolean | undefined;
    verbose?: boolean;
}

databaseCmd
    .command('backup')
    .description('Backup the database')
    .option('-o, --output <value>', 'Output file path', './backup.sql')
    .option('--compress', 'Compress the backup')
    .action(async (options: DatabaseBackupOptions, command: Command) => {
        try {
            const hookName = 'onDatabaseBackup';
            if (appHooks && typeof appHooks[hookName] === 'function') {
                const kwargs: CommandArgs = {
                    commandName: 'backup',
                    ...options,
                    // Add global options
                    verbose: (command.parent?.parent?.opts() as GlobalOptions)?.verbose,
                    config: (command.parent?.parent?.opts() as GlobalOptions)?.config,
                };
                
                await (appHooks[hookName] as HookFunction)(kwargs);
            } else {
                // Default placeholder behavior
                console.log(`Executing backup command...`);
                console.log(`  output: ${options.output}`);
                console.log(`  compress: ${options.compress}`);
            }
        } catch (error) {
            const exitCode = handleCLIError(error as Error, options.verbose || false);
            process.exit(exitCode);
        }
    });

// Command: test
interface TestOptions {
    coverage: boolean | undefined;
    watch: boolean | undefined;
    bail: boolean | undefined;
    verbose?: boolean;
}

const testCmd = program
    .command('test')
    .description('Run tests')
    .argument('[pattern]', 'Test file pattern')
    .option('--coverage', 'Generate coverage report')
    .option('-w, --watch', 'Watch files for changes')
    .option('--bail', 'Stop on first test failure')
    .action(async (pattern: string, options: TestOptions, command: Command) => {
        try {
            // Standard command - use hook pattern
            const hookName = 'onTest';
            if (appHooks && typeof appHooks[hookName] === 'function') {
                const kwargs: CommandArgs = {
                    commandName: 'test',
                    pattern: pattern,
                    ...options,
                    // Add global options
                    verbose: (command.parent?.opts() as GlobalOptions)?.verbose,
                    config: (command.parent?.opts() as GlobalOptions)?.config,
                };
                
                await (appHooks[hookName] as HookFunction)(kwargs);
            } else {
                // Default placeholder behavior
                console.log(`Executing test command...`);
                console.log(`  pattern: $${pattern}`);  
                console.log(`  coverage: ${options.coverage}`);
                console.log(`  watch: ${options.watch}`);
                console.log(`  bail: ${options.bail}`);
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
        console.log(`   NodeJSTestCLI completion generate ${shell} > completion.${shell}`);
        console.log(`   cp completion.${shell} ${instructions.userScriptPath}\n`);
        
        console.log('🌐 System-wide installation:');
        console.log(`   NodeJSTestCLI completion generate ${shell} > completion.${shell}`);
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

// Daemon management commands
program
    .command('daemonstop <commandName>')
    .description('⏹️ Stop a running daemon process')
    .option('--timeout <seconds>', 'Timeout in seconds for graceful shutdown', '10')
    .option('--json', 'Output in JSON format')
    .action(async (commandName: string, options: { timeout?: string; json?: boolean }) => {
        try {
            const DaemonHelper = require('./lib/daemon').DaemonHelper;
            const daemonHelper = new DaemonHelper(commandName);
            
            if (!daemonHelper.isRunning()) {
                const msg = `No daemon running for command '${commandName}'`;
                if (options.json) {
                    console.log(JSON.stringify({ status: 'not_running', message: msg }));
                } else {
                    console.log(`⚠️  ${msg}`);
                }
                return;
            }
            
            const pid = daemonHelper.getPid();
            const timeout = parseInt(options.timeout || '10');
            
            if (await daemonHelper.stop(timeout)) {
                if (options.json) {
                    console.log(JSON.stringify({
                        status: 'stopped',
                        command: commandName,
                        pid: pid,
                        message: `Successfully stopped daemon for '${commandName}'`
                    }));
                } else {
                    console.log(`✅ Successfully stopped daemon '${commandName}' (PID: ${pid})`);
                }
            } else {
                const errorMsg = `Failed to stop daemon '${commandName}' (PID: ${pid})`;
                if (options.json) {
                    console.log(JSON.stringify({ status: 'error', message: errorMsg }));
                } else {
                    console.error(`❌ ${errorMsg}`);
                }
                process.exit(1);
            }
        } catch (e) {
            const exitCode = handleCLIError(e as Error, options.verbose || program.opts().verbose);
            process.exit(exitCode);
        }
    });

program
    .command('daemonstatus <commandName>')
    .description('📊 Check status of a daemon process')
    .option('--json', 'Output in JSON format')
    .action(async (commandName: string, options: { json?: boolean }) => {
        try {
            const DaemonHelper = require('./lib/daemon').DaemonHelper;
            const daemonHelper = new DaemonHelper(commandName);
            
            const stats = daemonHelper.getDaemonStats();
            
            if (options.json) {
                console.log(JSON.stringify(stats, null, 2));
            } else {
                const isRunning = stats.running;
                const statusEmoji = isRunning ? '🟢' : '🔴';
                const statusText = isRunning ? 'Running' : 'Stopped';
                
                console.log(`📊 Daemon Status for '${commandName}': ${statusEmoji} ${statusText}`);
                
                if (isRunning) {
                    console.log(`   PID: ${stats.pid}`);
                    console.log(`   PID File: ${stats.pidFile}`);
                } else {
                    console.log(`   PID File: ${stats.pidFile} (not found or stale)`);
                }
            }
        } catch (e) {
            const exitCode = handleCLIError(e as Error, options.verbose || program.opts().verbose);
            process.exit(exitCode);
        }
    });

const daemonCmd = program
    .command('daemon')
    .description('🔧 Daemon system integration commands');

daemonCmd
    .command('install <commandName>')
    .description('🔧 Generate systemd service file for daemon management')
    .option('--user', 'Install as user service (default)', true)
    .option('--system', 'Install as system service (requires sudo)')
    .action(async (commandName: string, options: { user?: boolean; system?: boolean }) => {
        try {
            // Implementation would be similar to Python version
            console.log('Daemon installation not yet implemented for TypeScript');
        } catch (e) {
            const exitCode = handleCLIError(e as Error, options.verbose || program.parent?.opts().verbose);
            process.exit(exitCode);
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

// Run if called directly
if (require.main === module) {
    cliEntry();
}