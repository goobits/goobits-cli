#!/usr/bin/env node
/**
 * Auto-generated from goobits.yaml
 * Goobits CLI Framework CLI - Node.js Implementation
 */

import { Command } from 'commander';
import path from 'path';
import fs from 'fs';
import { spawn, execSync } from 'child_process';
import { fileURLToPath } from 'url';
import { dirname } from 'path';

// ES Module equivalents of __filename and __dirname
const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// Enhanced Error Classes
class CLIError extends Error {
    constructor(message, exitCode = 1, suggestion = null) {
        super(message);
        this.name = 'CLIError';
        this.exitCode = exitCode;
        this.suggestion = suggestion;
    }
}

class ConfigError extends CLIError {
    constructor(message, suggestion = null) {
        super(message, 2, suggestion);
        this.name = 'ConfigError';
    }
}

class HookError extends CLIError {
    constructor(message, hookName = null) {
        const suggestion = hookName ? `Check the '${hookName}' function in your hooks file` : null;
        super(message, 3, suggestion);
        this.name = 'HookError';
        this.hookName = hookName;
    }
}

class DependencyError extends CLIError {
    constructor(message, dependency, installCommand = null) {
        const suggestion = installCommand ? `Install with: ${installCommand}` : `Install the '${dependency}' package`;
        super(message, 4, suggestion);
        this.name = 'DependencyError';
        this.dependency = dependency;
        this.installCommand = installCommand;
    }
}

// Global error handler
function handleCLIError(error, verbose = false) {
    if (error instanceof CLIError) {
        console.error(`❌ Error: ${error.message}`);
        if (error.suggestion) {
            console.error(`💡 Suggestion: ${error.suggestion}`);
        }
        if (verbose) {
            console.error('\n🔍 Debug traceback:');
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
let configManager, progressHelper, promptsHelper, completionHelper;
let HAS_CONFIG_MANAGER = false;
let HAS_PROGRESS_HELPER = false;
let HAS_PROMPTS_HELPER = false;
let HAS_COMPLETION_HELPER = false;

// Initialize global helpers
let config = null;
let progress = null;
let prompts = null;
let completion = null;

if (HAS_CONFIG_MANAGER) {
    try {
        config = configManager.getConfig();
    } catch (e) {
        console.warn(`Failed to initialize config manager: ${e.message}`);
        HAS_CONFIG_MANAGER = false;
    }
}

if (HAS_PROGRESS_HELPER) {
    try {
        progress = progressHelper.getProgressHelper();
    } catch (e) {
        console.warn(`Failed to initialize progress helper: ${e.message}`);
        HAS_PROGRESS_HELPER = false;
    }
}

if (HAS_PROMPTS_HELPER) {
    try {
        prompts = promptsHelper.getPromptsHelper();
    } catch (e) {
        console.warn(`Failed to initialize prompts helper: ${e.message}`);
        HAS_PROMPTS_HELPER = false;
    }
}

if (HAS_COMPLETION_HELPER) {
    try {
        completion = completionHelper.getCompletionHelper();
    } catch (e) {
        console.warn(`Failed to initialize completion helper: ${e.message}`);
        HAS_COMPLETION_HELPER = false;
    }
}

// Load hooks module - will be loaded async on first use
let appHooks = null;

// Async hook loader
async function loadHooks() {
    if (appHooks !== null) return appHooks; // Already loaded
    
    try {
        
        // No hooks path configured, try default locations
        const possiblePaths = [
            path.join(__dirname, '../hooks.js'),
            path.join(__dirname, '../src/hooks.js'),
            path.join(process.cwd(), 'hooks.js'),
            path.join(process.cwd(), 'src/hooks.js')
        ];
        
        for (const hookPath of possiblePaths) {
            if (fs.existsSync(hookPath)) {
                appHooks = await import(hookPath);
                break;
            }
        }
        
    } catch (e) {
        // No hooks module found - use empty hooks object
        appHooks = {};
    }
    
    return appHooks;
}

// Get version function
function getVersion() {
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
    
    return '1.2.0';
    
}

// Built-in upgrade command

async function builtinUpgradeCommand(checkOnly = false, pre = false, version = null, dryRun = false) {
    if (checkOnly) {
        console.log(`Checking for updates to Goobits CLI Framework...`);
        console.log('Update check not yet implemented. Run without --check to upgrade.');
        return;
    }

    if (dryRun) {
        console.log('Dry run - would execute: npm update -g goobits-cli');
        return;
    }

    // Find the setup.sh script
    let setupScript = null;
    const searchPaths = [
        path.join(__dirname, 'setup.sh'),
        path.join(__dirname, '../setup.sh'),
        path.join(process.env.HOME, '.local', 'share', 'goobits-cli', 'setup.sh')
    ];
    
    for (const scriptPath of searchPaths) {
        if (fs.existsSync(scriptPath)) {
            setupScript = scriptPath;
            break;
        }
    }
    
    if (!setupScript) {
        // Fallback to basic upgrade
        console.log(`Enhanced setup script not found. Using basic upgrade for Goobits CLI Framework...`);
        
        const packageName = 'goobits-cli';
        const npmName = 'goobits-cli';
        
        try {
            const cmd = process.platform === 'win32' ? 'npm.cmd' : 'npm';
            execSync(`${cmd} update -g ${npmName}`, { stdio: 'inherit' });
            console.log(`✅ Goobits CLI Framework upgraded successfully!`);
            console.log(`Run 'goobits --version' to verify the new version.`);
        } catch (e) {
            console.error(`❌ Upgrade failed: ${e.message}`);
            process.exit(1);
        }
        return;
    }

    // Use the enhanced setup.sh script
    try {
        execSync(`${setupScript} upgrade`, { stdio: 'inherit' });
    } catch (e) {
        process.exit(e.status || 1);
    }
}


// Plugin loading
async function loadPlugins(program) {
    const pluginDirs = [
        path.join(process.env.HOME || process.env.USERPROFILE, '.config', 'goobits', 'Goobits CLI', 'plugins'),
        path.join(__dirname, 'plugins')
    ];
    
    for (const pluginDir of pluginDirs) {
        if (!fs.existsSync(pluginDir)) continue;
        
        const files = fs.readdirSync(pluginDir);
        for (const file of files) {
            if (!file.endsWith('.js') || file.startsWith('_')) continue;
            if (['loader.js', 'index.js'].includes(file)) continue;
            
            const pluginName = path.basename(file, '.js');
            
            try {
                const pluginPath = path.join(pluginDir, file);
                const plugin = await import(pluginPath);
                
                if (typeof plugin.default?.registerPlugin === 'function') {
                    plugin.default.registerPlugin(program);
                    console.error(`Loaded plugin: ${pluginName}`);
                } else if (typeof plugin.registerPlugin === 'function') {
                    plugin.registerPlugin(program);
                    console.error(`Loaded plugin: ${pluginName}`);
                }
            } catch (e) {
                console.error(`Failed to load plugin ${pluginName}: ${e.message}`);
            }
        }
    }
}

// Create the main program
const program = new Command();

// Configure program
program
    .name('Goobits CLI')
    .version(getVersion())
    .description(`🛠️ Goobits CLI v${getVersion()} - Build professional command-line tools with YAML configuration`)
    .helpOption('-h, --help', 'Display help for command')
    .configureHelp({
        sortSubcommands: true,
        sortOptions: true
    });

// Add custom help formatting
program.addHelpText('after', `

Transform simple YAML configuration into rich terminal applications with setup scripts, dependency management, and cross-platform compatibility.




🚀 Quick Start:


  mkdir my-cli && cd my-cli   # Create new project directory


  goobits init                # Generate initial goobits.yaml


  goobits build               # Create CLI and setup scripts


  ./setup.sh install --dev    # Install for development



💡 Core Commands:


  build    🔨 Generate CLI and setup scripts from goobits.yaml


  serve    🌐 Serve local PyPI-compatible package index


  init     🆕 Create initial goobits.yaml template



🔧 Development Workflow:


  1. Edit goobits.yaml: Define your CLI structure

  2. goobits build: Generate implementation files

  3. Edit app_hooks.py: Add your business logic




📚 For detailed help on a command, run: [color(2)]goobits [COMMAND][/color(2)] [#ff79c6]--help[/#ff79c6]
`);

// Global options
const globalOptions = {};


program.option('-v, --verbose',
    'Enable verbose output with detailed error messages and stack traces'
);



// Built-in upgrade command

program
    .command('upgrade')
    .description('Upgrade Goobits CLI Framework to the latest version')
    .option('--check', 'Check for updates without installing')
    .option('--version <version>', 'Install specific version')
    .option('--pre', 'Include pre-release versions')
    .option('--dry-run', 'Show what would be done without doing it')
    .action(async (options) => {
        await builtinUpgradeCommand(options.check, options.pre, options.version, options.dryRun);
    });


// Commands from configuration


// Command: build
const buildCmd = program
    .command('build')
    .description('🔨 Build CLI and setup scripts from goobits.yaml configuration')
    
    .argument('[config_path]', 'Path to goobits.yaml file (defaults to ./goobits.yaml)')
    
    
    .option('-o, --output-dir <value>', '📁 Output directory (defaults to same directory as config file)')
    
    .option('--output <value>', '📝 Output filename for generated CLI (defaults to 'generated_cli.py')')
    
    .option('--backup', '💾 Create backup files (.bak) when overwriting existing files')
    
    .option('--universal-templates', '🧪 Use Universal Template System (experimental)')
    
    .action(async (config_path, options, command) => {
        try {
            
            // Standard command - use hook pattern
            const hookName = 'onBuild';
            const hooks = await loadHooks();
            if (hooks && typeof hooks[hookName] === 'function') {
                const kwargs = {
                    commandName: 'build',
                    
                    
                    config_path: config_path,
                    
                    
                    ...options,
                    // Add global options
                    
                    
                    verbose: command.parent.opts().verbose,
                    
                    
                };
                
                await hooks[hookName](kwargs);
            } else {
                // Default placeholder behavior
                console.log(`Executing build command...`);
                
                
                console.log(`  config_path: $${config_path}`);  
                
                
                
                
                console.log(`  output-dir: ${options.outputdir}`);
                
                console.log(`  output: ${options.output}`);
                
                console.log(`  backup: ${options.backup}`);
                
                console.log(`  universal-templates: ${options.universaltemplates}`);
                
                
            }
            
        } catch (error) {
            handleCLIError(error, options.verbose || command.parent.opts().verbose);
            process.exit(error.exitCode || 1);
        }
    });




// Command: init
const initCmd = program
    .command('init')
    .description('🆕 Create initial goobits.yaml template')
    
    .argument('[project_name]', 'Name of the project (optional)')
    
    
    .option('-t, --template <value>', '🎯 Template type', 'basic')
    
    .option('--force', '🔥 Overwrite existing goobits.yaml file')
    
    .action(async (project_name, options, command) => {
        try {
            
            // Standard command - use hook pattern
            const hookName = 'onInit';
            const hooks = await loadHooks();
            if (hooks && typeof hooks[hookName] === 'function') {
                const kwargs = {
                    commandName: 'init',
                    
                    
                    project_name: project_name,
                    
                    
                    ...options,
                    // Add global options
                    
                    
                    verbose: command.parent.opts().verbose,
                    
                    
                };
                
                await hooks[hookName](kwargs);
            } else {
                // Default placeholder behavior
                console.log(`Executing init command...`);
                
                
                console.log(`  project_name: $${project_name}`);  
                
                
                
                
                console.log(`  template: ${options.template}`);
                
                console.log(`  force: ${options.force}`);
                
                
            }
            
        } catch (error) {
            handleCLIError(error, options.verbose || command.parent.opts().verbose);
            process.exit(error.exitCode || 1);
        }
    });




// Command: serve
const serveCmd = program
    .command('serve')
    .description('🌐 Serve local PyPI-compatible package index')
    
    .argument('<directory>', 'Directory containing packages to serve')
    
    
    .option('--host <value>', '🌍 Host to bind the server to', 'localhost')
    
    .option('-p, --port <value>', '🔌 Port to run the server on', 8080)
    
    .action(async (directory, options, command) => {
        try {
            
            // Standard command - use hook pattern
            const hookName = 'onServe';
            const hooks = await loadHooks();
            if (hooks && typeof hooks[hookName] === 'function') {
                const kwargs = {
                    commandName: 'serve',
                    
                    
                    directory: directory,
                    
                    
                    ...options,
                    // Add global options
                    
                    
                    verbose: command.parent.opts().verbose,
                    
                    
                };
                
                await hooks[hookName](kwargs);
            } else {
                // Default placeholder behavior
                console.log(`Executing serve command...`);
                
                
                console.log(`  directory: $${directory}`);  
                
                
                
                
                console.log(`  host: ${options.host}`);
                
                console.log(`  port: ${options.port}`);
                
                
            }
            
        } catch (error) {
            handleCLIError(error, options.verbose || command.parent.opts().verbose);
            process.exit(error.exitCode || 1);
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
    .action((shell, options) => {
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
            console.error(`❌ Error generating ${shell} completion: ${e.message}`);
        }
    });

completionCmd
    .command('install <shell>')
    .description('Install shell completion script')
    .option('--user', 'Install for current user (default)', true)
    .option('--system', 'Install system-wide (requires sudo)')
    .action(async (shell, options) => {
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
            console.error(`❌ Error installing ${shell} completion: ${e.message}`);
        }
    });

completionCmd
    .command('instructions <shell>')
    .description('Show installation instructions for shell completion')
    .action((shell) => {
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
        console.log(`   Goobits CLI completion generate ${shell} > completion.${shell}`);
        console.log(`   cp completion.${shell} ${instructions.userScriptPath}\n`);
        
        console.log('🌐 System-wide installation:');
        console.log(`   Goobits CLI completion generate ${shell} > completion.${shell}`);
        console.log(`   ${instructions.installCmd}\n`);
        
        console.log('🔄 Reload shell:');
        console.log(`   ${instructions.reloadCmd}`);
    });

// Hidden internal completion command
program
    .command('_completion <shell> <currentLine> [cursorPos]', { hidden: true })
    .option('--debug', 'Debug completion engine')
    .action(async (shell, currentLine, cursorPos, options) => {
        try {
            const enginePath = path.join(__dirname, 'completion_engine.js');
            
            if (fs.existsSync(enginePath)) {
                const { CompletionEngine } = await import(enginePath);
                const engine = new CompletionEngine();
                const completions = engine.getCompletions(shell, currentLine, cursorPos);
                
                completions.forEach(completion => console.log(completion));
            } else if (options.debug) {
                console.error('completion_engine.js not found');
            }
        } catch (e) {
            if (options.debug) {
                console.error(`Completion error: ${e.message}`);
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
    .action((key) => {
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
            console.error(`❌ Error getting configuration: ${e.message}`);
        }
    });

configCmd
    .command('set <key> <value>')
    .description('Set configuration value')
    .action((key, value) => {
        if (!HAS_CONFIG_MANAGER) {
            console.error('❌ Configuration manager not available.');
            return;
        }
        
        try {
            // Try to parse value as JSON for complex types
            let parsedValue;
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
            console.error(`❌ Error setting configuration: ${e.message}`);
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
            console.error(`❌ Error resetting configuration: ${e.message}`);
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
            console.error(`❌ Error getting configuration path: ${e.message}`);
        }
    });












// CLI entry point
async function cliEntry() {
    try {
        // Load plugins before parsing
        await loadPlugins(program);
        
        // Parse command line
        program.parse(process.argv);
        
        // Show help if no args
        if (!process.argv.slice(2).length) {
            program.outputHelp();
        }
    } catch (e) {
        if (e.code === 'commander.help') {
            // Normal help display
            process.exit(0);
        }
        
        const verbose = program.opts().verbose || false;
        const exitCode = handleCLIError(e, verbose);
        process.exit(exitCode);
    }
}

// Handle uncaught errors
process.on('uncaughtException', (error) => {
    const verbose = program.opts().verbose || false;
    const exitCode = handleCLIError(error, verbose);
    process.exit(exitCode);
});

process.on('unhandledRejection', (reason, promise) => {
    const error = reason instanceof Error ? reason : new Error(String(reason));
    const verbose = program.opts().verbose || false;
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
if (import.meta.url === `file://${process.argv[1]}`) {
    cliEntry().catch(error => {
        console.error('Fatal error:', error.message);
        if (process.env.DEBUG) {
            console.error(error.stack);
        }
        process.exit(1);
    });
}