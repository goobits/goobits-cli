#!/usr/bin/env node
/**
 * Auto-generated from test_complex_config.yaml
 * Complex CLI Test Tool CLI - Node.js Implementation
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
function handleCLIError(error, debug = false) {
    if (error instanceof CLIError) {
        console.error(`❌ Error: ${error.message}`);
        if (error.suggestion) {
            console.error(`💡 Suggestion: ${error.suggestion}`);
        }
        if (debug) {
            console.error('\n🔍 Debug traceback:');
            console.error(error.stack);
        }
        return error.exitCode;
    } else {
        // Unexpected errors
        console.error(`❌ Unexpected error: ${error.message}`);
        console.error('💡 This may be a bug. Please report it with the following details:');
        if (debug) {
            console.error(error.stack);
        } else {
            console.error(`   Error type: ${error.constructor.name}`);
            console.error(`   Error message: ${error.message}`);
            console.error('   Run with --debug for full traceback');
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
    
    return '1.0.0';
    
}

// Built-in upgrade command

async function builtinUpgradeCommand(checkOnly = false, pre = false, version = null, dryRun = false) {
    if (checkOnly) {
        console.log(`Checking for updates to Complex CLI Test Tool...`);
        console.log('Update check not yet implemented. Run without --check to upgrade.');
        return;
    }

    if (dryRun) {
        console.log('Dry run - would execute: npm update -g complex-cli-test');
        return;
    }

    // Find the setup.sh script
    let setupScript = null;
    const searchPaths = [
        path.join(__dirname, 'setup.sh'),
        path.join(__dirname, '../setup.sh'),
        path.join(process.env.HOME, '.local', 'share', 'complex-cli-test', 'setup.sh')
    ];
    
    for (const scriptPath of searchPaths) {
        if (fs.existsSync(scriptPath)) {
            setupScript = scriptPath;
            break;
        }
    }
    
    if (!setupScript) {
        // Fallback to basic upgrade
        console.log(`Enhanced setup script not found. Using basic upgrade for Complex CLI Test Tool...`);
        
        const packageName = 'complex-cli-test';
        const npmName = 'complex-cli-test';
        
        try {
            const cmd = process.platform === 'win32' ? 'npm.cmd' : 'npm';
            execSync(`${cmd} update -g ${npmName}`, { stdio: 'inherit' });
            console.log(`✅ Complex CLI Test Tool upgraded successfully!`);
            console.log(`Run 'complex-cli --version' to verify the new version.`);
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
        path.join(process.env.HOME || process.env.USERPROFILE, '.config', 'goobits', 'complex-cli', 'plugins'),
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
    .name('complex-cli')
    .version(getVersion())
    .description(`complex-cli v${getVersion()} - Test complex code generation patterns`)
    .helpOption('-h, --help', 'Display help for command')
    .configureHelp({
        sortSubcommands: true,
        sortOptions: true
    });

// Add custom help formatting
program.addHelpText('after', `

Advanced CLI with multiple commands, subcommands, and features



`);

// Global options
const globalOptions = {};


// Built-in upgrade command

program
    .command('upgrade')
    .description('Upgrade Complex CLI Test Tool to the latest version')
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
    .description('Build the project with various options')
    
    .argument('<target>', 'Build target directory')
    
    .argument('[source]', 'Source files pattern')
    
    
    .option('-v, --verbose <value>', 'Enable verbose output')
    
    .option('-f, --output-format <value>', 'Output format', 'json')
    
    .option('-j, --parallel-jobs <value>', 'Number of parallel jobs', 4)
    
    .option('--timeout <value>', 'Build timeout in seconds', 30.0)
    
    .action(async (target, source, options, command) => {
        try {
            
            // Standard command - use hook pattern
            const hookName = 'onBuild';
            const hooks = await loadHooks();
            if (hooks && typeof hooks[hookName] === 'function') {
                const kwargs = {
                    commandName: 'build',
                    
                    
                    target: target,
                    
                    source: source,
                    
                    
                    ...options,
                    // Add global options
                    
                };
                
                await hooks[hookName](kwargs);
            } else {
                // Default placeholder behavior
                console.log(`Executing build command...`);
                
                
                console.log(`  target: $${target}`);  
                
                console.log(`  source: $${source}`);  
                
                
                
                
                console.log(`  verbose: ${options.verbose}`);
                
                console.log(`  output-format: ${options.outputformat}`);
                
                console.log(`  parallel-jobs: ${options.paralleljobs}`);
                
                console.log(`  timeout: ${options.timeout}`);
                
                
            }
            
        } catch (error) {
            handleCLIError(error, options.debug || command.parent.opts().debug);
            process.exit(error.exitCode || 1);
        }
    });




// Command: deploy
const deployCmd = program
    .command('deploy')
    .description('Deploy application to various environments')
    
    .argument('<environment>', 'Target environment', ['dev', 'staging', 'prod'])
    
    
    .option('--dry-run', 'Perform dry run without actual deployment')
    
    .option('-c, --config-file <value>', 'Custom configuration file')
    
    .option('-f, --force', 'Force deployment ignoring checks')
    
    .action(async (environment, options, command) => {
        try {
            
            // Standard command - use hook pattern
            const hookName = 'onDeploy';
            const hooks = await loadHooks();
            if (hooks && typeof hooks[hookName] === 'function') {
                const kwargs = {
                    commandName: 'deploy',
                    
                    
                    environment: environment,
                    
                    
                    ...options,
                    // Add global options
                    
                };
                
                await hooks[hookName](kwargs);
            } else {
                // Default placeholder behavior
                console.log(`Executing deploy command...`);
                
                
                console.log(`  environment: $${environment}`);  
                
                
                
                
                console.log(`  dry-run: ${options.dryrun}`);
                
                console.log(`  config-file: ${options.configfile}`);
                
                console.log(`  force: ${options.force}`);
                
                
            }
            
        } catch (error) {
            handleCLIError(error, options.debug || command.parent.opts().debug);
            process.exit(error.exitCode || 1);
        }
    });




// Command group: test
const testCmd = program
    .command('test')
    .description('Run comprehensive test suite');


testCmd
    .command('unit')
    .description('Run unit tests')
    
    
    .option('--coverage', 'Generate coverage report')
    
    .option('--pattern <value>', 'Test file pattern', 'test_*.py')
    
    .action(async (options, command) => {
        try {
            const hookName = 'onTestUnit';
            const hooks = await loadHooks();
            if (hooks && typeof hooks[hookName] === 'function') {
                const kwargs = {
                    commandName: 'unit',
                    
                    ...options,
                    // Add global options
                    
                };
                
                await hooks[hookName](kwargs);
            } else {
                // Default placeholder behavior
                console.log(`Executing unit command...`);
                
                
                
                console.log(`  coverage: ${options.coverage}`);
                
                console.log(`  pattern: ${options.pattern}`);
                
                
            }
        } catch (error) {
            handleCLIError(error, options.debug || command.parent.parent.opts().debug);
            process.exit(error.exitCode || 1);
        }
    });

testCmd
    .command('integration')
    .description('Run integration tests')
    
    .argument('[service]', 'Service to test')
    
    
    .option('--environment <value>', 'Test environment', 'test')
    
    .option('--parallel <value>', 'Run tests in parallel', true)
    
    .action(async (service, options, command) => {
        try {
            const hookName = 'onTestIntegration';
            const hooks = await loadHooks();
            if (hooks && typeof hooks[hookName] === 'function') {
                const kwargs = {
                    commandName: 'integration',
                    
                    
                    service: service,
                    
                    
                    ...options,
                    // Add global options
                    
                };
                
                await hooks[hookName](kwargs);
            } else {
                // Default placeholder behavior
                console.log(`Executing integration command...`);
                
                
                console.log(`  service: $${service}`);  
                
                
                
                
                console.log(`  environment: ${options.environment}`);
                
                console.log(`  parallel: ${options.parallel}`);
                
                
            }
        } catch (error) {
            handleCLIError(error, options.debug || command.parent.parent.opts().debug);
            process.exit(error.exitCode || 1);
        }
    });

testCmd
    .command('performance')
    .description('Run performance benchmarks')
    
    
    .option('--iterations <value>', 'Number of benchmark iterations', 100)
    
    .option('--threshold <value>', 'Performance threshold in ms', 1000.0)
    
    .action(async (options, command) => {
        try {
            const hookName = 'onTestPerformance';
            const hooks = await loadHooks();
            if (hooks && typeof hooks[hookName] === 'function') {
                const kwargs = {
                    commandName: 'performance',
                    
                    ...options,
                    // Add global options
                    
                };
                
                await hooks[hookName](kwargs);
            } else {
                // Default placeholder behavior
                console.log(`Executing performance command...`);
                
                
                
                console.log(`  iterations: ${options.iterations}`);
                
                console.log(`  threshold: ${options.threshold}`);
                
                
            }
        } catch (error) {
            handleCLIError(error, options.debug || command.parent.parent.opts().debug);
            process.exit(error.exitCode || 1);
        }
    });





// Command group: config
const configCmd = program
    .command('config')
    .description('Configuration management commands');


configCmd
    .command('get')
    .description('Get configuration value')
    
    .argument('<key>', 'Configuration key')
    
    
    .action(async (keyoptions, command) => {
        try {
            const hookName = 'onConfigGet';
            const hooks = await loadHooks();
            if (hooks && typeof hooks[hookName] === 'function') {
                const kwargs = {
                    commandName: 'get',
                    
                    
                    key: key,
                    
                    
                    ...options,
                    // Add global options
                    
                };
                
                await hooks[hookName](kwargs);
            } else {
                // Default placeholder behavior
                console.log(`Executing get command...`);
                
                
                console.log(`  key: $${key}`);  
                
                
                
            }
        } catch (error) {
            handleCLIError(error, options.debug || command.parent.parent.opts().debug);
            process.exit(error.exitCode || 1);
        }
    });

configCmd
    .command('set')
    .description('Set configuration value')
    
    .argument('<key>', 'Configuration key')
    
    .argument('<value>', 'Configuration value')
    
    
    .option('-g, --global', 'Set global configuration')
    
    .action(async (key, value, options, command) => {
        try {
            const hookName = 'onConfigSet';
            const hooks = await loadHooks();
            if (hooks && typeof hooks[hookName] === 'function') {
                const kwargs = {
                    commandName: 'set',
                    
                    
                    key: key,
                    
                    value: value,
                    
                    
                    ...options,
                    // Add global options
                    
                };
                
                await hooks[hookName](kwargs);
            } else {
                // Default placeholder behavior
                console.log(`Executing set command...`);
                
                
                console.log(`  key: $${key}`);  
                
                console.log(`  value: $${value}`);  
                
                
                
                
                console.log(`  global: ${options.global}`);
                
                
            }
        } catch (error) {
            handleCLIError(error, options.debug || command.parent.parent.opts().debug);
            process.exit(error.exitCode || 1);
        }
    });

configCmd
    .command('list')
    .description('List all configuration values')
    
    
    .option('--format <value>', 'Output format', 'table')
    
    .action(async (options, command) => {
        try {
            const hookName = 'onConfigList';
            const hooks = await loadHooks();
            if (hooks && typeof hooks[hookName] === 'function') {
                const kwargs = {
                    commandName: 'list',
                    
                    ...options,
                    // Add global options
                    
                };
                
                await hooks[hookName](kwargs);
            } else {
                // Default placeholder behavior
                console.log(`Executing list command...`);
                
                
                
                console.log(`  format: ${options.format}`);
                
                
            }
        } catch (error) {
            handleCLIError(error, options.debug || command.parent.parent.opts().debug);
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
        console.log(`   complex-cli completion generate ${shell} > completion.${shell}`);
        console.log(`   cp completion.${shell} ${instructions.userScriptPath}\n`);
        
        console.log('🌐 System-wide installation:');
        console.log(`   complex-cli completion generate ${shell} > completion.${shell}`);
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
        
        const debug = process.argv.includes('--debug');
        const exitCode = handleCLIError(e, debug);
        process.exit(exitCode);
    }
}

// Handle uncaught errors
process.on('uncaughtException', (error) => {
    const debug = process.argv.includes('--debug');
    const exitCode = handleCLIError(error, debug);
    process.exit(exitCode);
});

process.on('unhandledRejection', (reason, promise) => {
    const error = reason instanceof Error ? reason : new Error(String(reason));
    const debug = process.argv.includes('--debug');
    const exitCode = handleCLIError(error, debug);
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