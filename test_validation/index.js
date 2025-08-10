/**
 * Auto-generated from test_nodejs.yaml
 * Main CLI implementation for Test Node.js CLI
 */

import { Command } from 'commander';
import chalk from 'chalk';
import { readdir } from 'fs/promises';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';
import { existsSync } from 'fs';

// Import error handling utilities
import { 
  setupGlobalErrorHandlers, 
  handleError, 
  asyncErrorHandler,
  ConfigError,
  PluginLoadError,
  CommandNotFoundError,
  CLIError
} from './lib/errors.js';





const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// Setup global error handlers
const globalErrorHandler = setupGlobalErrorHandlers({
  showStack: process.env.NODE_ENV === 'development' || process.env.DEBUG,
  colorize: true,
  exitOnError: true
});

// Load configuration if config module exists
let config = null;
try {
  const configModule = await import('./lib/config.js');
  config = configModule.default;
  await config.load();
} catch (error) {
  // Config module not available or error loading
  if (process.env.DEBUG) {
    console.debug('Config module not loaded:', error.message);
  }
  // Don't exit on config load failure during initialization
}

// Create the main program
const program = new Command();

// Version helper function
const getVersion = asyncErrorHandler(async function getVersion() {
  try {
    const packagePath = join(__dirname, 'package.json');
    const { default: pkg } = await import(packagePath, { assert: { type: 'json' } });
    return pkg.version;
  } catch (error) {
    if (process.env.DEBUG) {
      console.debug('Could not load version from package.json:', error.message);
    }
    return '1.0.0';
  }
});

// Hooks system - try to import app_hooks module
let appHooks = null;

// No hooks path configured, try default locations
try {
  const hooksPath = join(__dirname, 'app_hooks.js');
  if (existsSync(hooksPath)) {
    appHooks = await import(hooksPath);
  }
} catch (error) {
  // No hooks module found, use default behavior
  console.debug('Hooks module not found:', error.message);
}


// Load commands dynamically from commands directory
const loadCommands = asyncErrorHandler(async function loadCommands(program) {
  const commandsDir = join(__dirname, 'commands');
  
  try {
    if (!existsSync(commandsDir)) {
      if (process.env.DEBUG) {
        console.debug('Commands directory not found:', commandsDir);
      }
      return;
    }
    
    const files = await readdir(commandsDir);
    let loadedCount = 0;
    
    for (const file of files) {
      if (file.endsWith('.js') && !file.startsWith('_')) {
        try {
          const commandPath = join(commandsDir, file);
          const { default: commandModule } = await import(commandPath);
          
          if (typeof commandModule === 'function') {
            commandModule(program);
            loadedCount++;
          } else if (commandModule.register) {
            commandModule.register(program);
            loadedCount++;
          } else {
            console.warn(chalk.yellow(`Warning: Command file ${file} does not export a function or register method`));
          }
        } catch (error) {
          const commandError = new CLIError(`Failed to load command ${file}: ${error.message}`, 'COMMAND_LOAD_ERROR');
          console.error(chalk.red(commandError.getUserMessage()));
          if (process.env.DEBUG) {
            console.error(error.stack);
          }
        }
      }
    }
    
    if (process.env.DEBUG && loadedCount > 0) {
      console.debug(chalk.gray(`Loaded ${loadedCount} command(s) from ${commandsDir}`));
    }
  } catch (error) {
    throw new CLIError(`Could not load commands directory: ${error.message}`, 'COMMANDS_DIR_ERROR');
  }
});

// Enhanced plugin loading with PluginManager
const loadPlugins = asyncErrorHandler(async function loadPlugins(program) {
  try {
    // Try to use enhanced plugin manager
    const { PluginManager } = await import('./lib/plugin-manager.js');
    const pluginManager = new PluginManager(program);
    
    const loadedCount = await pluginManager.loadAllPlugins();
    if (loadedCount > 0 && process.env.DEBUG) {
      console.debug(chalk.gray(`Loaded ${loadedCount} plugin(s)`));
    }
    
    // Store plugin manager on program for later use
    program.pluginManager = pluginManager;
    
  } catch (error) {
    if (process.env.DEBUG) {
      console.debug('Enhanced plugin manager not available, falling back to basic loading:', error.message);
    }
    
    // Fallback to basic plugin loading
    const pluginDirs = [
      // User-specific plugin directory
      join(process.env.HOME || '', '.config', 'goobits', 'testcli', 'plugins'),
      // Local plugin directory
      join(__dirname, 'plugins'),
    ];
    
    let totalLoaded = 0;
    
    for (const pluginDir of pluginDirs) {
      try {
        if (!existsSync(pluginDir)) {
          continue;
        }
        
        const files = await readdir(pluginDir);
        
        for (const file of files) {
          if (file.endsWith('.js') && !file.startsWith('_')) {
            try {
              const pluginPath = join(pluginDir, file);
              const { default: pluginModule } = await import(pluginPath);
              
              if (typeof pluginModule === 'function') {
                pluginModule(program);
                totalLoaded++;
                if (process.env.DEBUG) {
                  console.debug(chalk.green(`✓ Loaded plugin: ${file}`));
                }
              } else if (pluginModule.register) {
                pluginModule.register(program);
                totalLoaded++;
                if (process.env.DEBUG) {
                  console.debug(chalk.green(`✓ Loaded plugin: ${file}`));
                }
              } else {
                console.warn(chalk.yellow(`Warning: Plugin ${file} does not export a function or register method`));
              }
            } catch (pluginError) {
              const error = new PluginLoadError(file, pluginError);
              console.error(chalk.red(error.getUserMessage()));
              if (process.env.DEBUG) {
                console.error(pluginError.stack);
              }
            }
          }
        }
      } catch (dirError) {
        // Plugin directory doesn't exist or can't be read
        if (process.env.DEBUG) {
          console.debug(`Could not access plugin directory ${pluginDir}:`, dirError.message);
        }
      }
    }
    
    if (process.env.DEBUG && totalLoaded > 0) {
      console.debug(chalk.gray(`Loaded ${totalLoaded} plugin(s) via fallback loading`));
    }
  }
});


// Built-in upgrade command
async function builtinUpgradeCommand(options) {
  const { execSync } = await import('child_process');
  const packageName = 'test-nodejs-cli';
  const displayName = 'Test Node.js CLI';
  
  console.log(chalk.blue(`Current version: ${await getVersion()}`));
  
  if (options.check) {
    console.log(chalk.yellow(`Checking for updates to ${displayName}...`));
    console.log('Update check not yet implemented. Run without --check to upgrade.');
    return;
  }
  
  if (options.dryRun) {
    console.log(chalk.gray(`Dry run - would execute: npm install -g ${packageName}`));
    return;
  }
  
  console.log(chalk.blue(`Upgrading ${displayName}...`));
  
  try {
    let cmd = `npm install -g ${packageName}`;
    if (options.version) {
      cmd = `npm install -g ${packageName}@${options.version}`;
    } else if (options.pre) {
      cmd = `npm install -g ${packageName}@next`;
    }
    
    execSync(cmd, { stdio: 'inherit' });
    console.log(chalk.green(`✅ ${displayName} upgraded successfully!`));
    console.log(chalk.gray(`Run 'testcli --version' to verify the new version.`));
  } catch (error) {
    const upgradeError = new CLIError(
      `Upgrade failed: ${error.message}`,
      'UPGRADE_ERROR',
      `Failed to upgrade ${displayName}. Please check your network connection and permissions.`,
      1
    );
    handleError(upgradeError);
  }
}


// Shell completion generation function
async function generateCompletion(shell) {
  try {
    const completionsDir = join(__dirname, 'completions');
    let templateFile;
    
    switch (shell) {
      case 'bash':
        templateFile = join(completionsDir, 'bash-completion');
        break;
      case 'zsh':
        templateFile = join(completionsDir, 'zsh-completion');
        break;
      case 'fish':
        templateFile = join(completionsDir, 'fish-completion');
        break;
      default:
        console.error(chalk.red(`Unknown shell: ${shell}`));
        return;
    }
    
    if (existsSync(templateFile)) {
      const { readFile } = await import('fs/promises');
      const completionScript = await readFile(templateFile, 'utf8');
      console.log(completionScript);
    } else {
      // Generate dynamic completion based on current commands
      generateDynamicCompletion(shell);
    }
  } catch (error) {
    console.error(chalk.red(`Failed to generate ${shell} completion:`, error.message));
    generateDynamicCompletion(shell);
  }
}

// Generate dynamic completion when template files are not available
function generateDynamicCompletion(shell) {
  const commands = program.commands.map(cmd => cmd.name()).join(' ');
  
  switch (shell) {
    case 'bash':
      console.log(`# Basic bash completion for testcli
_testcli_completions() {
    local cur prev words cword
    _init_completion || return
    
    case "\${prev}" in
        testcli)
            COMPREPLY=($(compgen -W "${commands}" -- "$cur"))
            return 0
            ;;
        --help|-h|--version|-V)
            return 0
            ;;
        *)
            COMPREPLY=($(compgen -W "--help -h --version -V" -- "$cur"))
            return 0
            ;;
    esac
}

complete -F _testcli_completions testcli`);
      break;
      
    case 'zsh':
      console.log(`#compdef testcli
# Basic zsh completion for testcli
_testcli() {
    local commands=(
        ${commands.split(' ').map(cmd => `'${cmd}:${cmd} command'`).join('\n        ')}
    )
    
    _arguments \\
        '(-h --help)'{-h,--help}'[Show help information]' \\
        '(-V --version)'{-V,--version}'[Show version information]' \\
        '1: :_describe "commands" commands' \\
        '*::arg:->args'
}

_testcli "$@"`);
      break;
      
    case 'fish':
      console.log(`# Basic fish completion for testcli
complete -c testcli -f
complete -c testcli -l help -s h -d 'Show help information'
complete -c testcli -l version -s V -d 'Show version information'

${commands.split(' ').map(cmd => 
  `complete -c testcli -n '__fish_use_subcommand' -a ${cmd} -d '${cmd} command'`
).join('\n')}`);
      break;
  }
}

// Main CLI setup
export const cli = asyncErrorHandler(async function cli() {
  const version = await getVersion();
  
  program
    .name('testcli')
    .description(`Test CLI for validation`)
    .version(version)
    .helpOption('-h, --help', 'Display help for command')
    .addHelpCommand('help [command]', 'Display help for command');

  // Configure help formatting
  program.configureHelp({
    sortSubcommands: true,
    subcommandTerm: (cmd) => cmd.name() + ' ' + cmd.usage(),
  });

  // Global options
  

  // Interactive mode option
  program
    .option('--interactive', 'Launch interactive mode for running commands interactively')
    .on('option:interactive', async () => {
      try {
        // Try to import enhanced interactive mode
        const { startEnhancedInteractive } = await import('./enhanced_interactive_mode.js');
        startEnhancedInteractive();
      } catch (error) {
        try {
          // Fallback to basic interactive mode
          const { runInteractive } = await import('./interactive_mode.js');
          runInteractive();
        } catch (fallbackError) {
          console.error(chalk.red('❌ Interactive mode not available. Missing interactive mode modules.'));
          process.exit(1);
        }
      }
      process.exit(0);
    });

  

  // Shell completion support
  program
    .option('--completion-bash', 'Generate bash completion script', false)
    .option('--completion-zsh', 'Generate zsh completion script', false)  
    .option('--completion-fish', 'Generate fish completion script', false)
    .on('option:completion-bash', async () => {
      await generateCompletion('bash');
      process.exit(0);
    })
    .on('option:completion-zsh', async () => {
      await generateCompletion('zsh');
      process.exit(0);
    })
    .on('option:completion-fish', async () => {
      await generateCompletion('fish');
      process.exit(0);
    });

  // Internal completion command (hidden from help)
  const completionCmd = program
    .command('_completion <shell> <current_line> [cursor_pos]', { hidden: true })
    .option('--debug', 'Debug completion engine')
    .action(async (shell, currentLine, cursorPos, options) => {
      try {
        // Import completion engine
        const enginePath = join(__dirname, 'completion_engine.js');
        
        if (existsSync(enginePath)) {
          const { CompletionEngine } = await import(enginePath);
          const engine = new CompletionEngine();
          const completions = engine.getCompletions(shell, currentLine, cursorPos ? parseInt(cursorPos) : null);
          
          // Output completions
          for (const completion of completions) {
            console.log(completion);
          }
        } else if (options.debug) {
          console.error('completion_engine.js not found');
        }
      } catch (error) {
        if (options.debug) {
          console.error(`Completion error: ${error.message}`);
        }
        // Silently fail in production to avoid breaking shell completion
      }
    });

  

  // Built-in commands
  
  program
    .command('upgrade')
    .description('Upgrade Test Node.js CLI to the latest version')
    .option('--check', 'Check for updates without installing')
    .option('--version <version>', 'Install specific version')
    .option('--pre', 'Include pre-release versions')
    .option('--dry-run', 'Show what would be done without doing it')
    .action(builtinUpgradeCommand);
  

  // Enhanced plugin management command
  try {
    const { default: registerPluginCommand } = await import('./commands/builtin/plugin.js');
    registerPluginCommand(program);
  } catch (error) {
    console.debug('Plugin command not available:', error.message);
  }

  // Shell completion command
  try {
    const { default: registerCompletionCommand } = await import('./commands/builtin/completion.js');
    registerCompletionCommand(program);
  } catch (error) {
    console.debug('Completion command not available:', error.message);
  }

  // Format demo command (optional - for demonstration)
  try {
    const { default: registerFormatDemoCommand } = await import('./commands/builtin/format-demo.js');
    registerFormatDemoCommand(program);
  } catch (error) {
    console.debug('Format demo command not available:', error.message);
  }

  // Define commands from configuration
  
  
  {
    const cmd = program
      .command('greet')
      .description('Greet someone')
      
      ;

    

    
    
    cmd.option(
      '----loud <str>',
      'Greet loudly'
    );
    
    

    cmd.action(async (options, command) => {
      
      // Standard command - use hook pattern
      const hookName = 'onGreet';
      if (appHooks && appHooks[hookName]) {
        const hookFunc = appHooks[hookName];
        
        // Prepare arguments
        const args = {
          commandName: 'greet',
          
          ...options,
          // Add global options
          
          // Add config if available
          config: config
        };
        
        try {
          const result = await hookFunc(args);
          return result;
        } catch (error) {
          const hookError = error instanceof CLIError ? error : new CLIError(
            `Hook function '${hookName}' failed: ${error.message}`,
            'HOOK_EXECUTION_ERROR',
            `Failed to execute command 'greet'. ${error.message}`,
            1
          );
          handleError(hookError);
        }
      } else {
        // Default placeholder behavior
        
        
        
        console.log(chalk.blue(`Executing greet command...`));
        
        
        
        console.log('Options:', options);
        
        
      }
      
    });
  }
  
  

  // Load dynamic commands from commands directory
  await loadCommands(program);
  
  // Load plugins
  await loadPlugins(program);

  

  

  

  // Parse arguments with error handling
  try {
    program.parse(process.argv);
    
    // Show help if no arguments provided and no default command
    
    
    
    
    
    if (!process.argv.slice(2).length) {
      program.outputHelp();
    }
    
  } catch (error) {
    // Handle commander.js parsing errors
    if (error.code === 'commander.unknownCommand') {
      const availableCommands = program.commands.map(cmd => cmd.name());
      const unknownCommand = error.message.match(/Unknown command '([^']+)'/)?.[1];
      throw new CommandNotFoundError(unknownCommand, availableCommands);
    }
    
    if (error.code === 'commander.invalidArgument') {
      throw new CLIError(
        error.message,
        'INVALID_ARGUMENT',
        error.message,
        2
      );
    }
    
    // Re-throw other commander errors as CLI errors
    throw new CLIError(
      error.message,
      'PARSE_ERROR',
      `Command line parsing error: ${error.message}`,
      2
    );
  }
});

// Export for use as a module
export default cli;

// Run CLI if this is the main module
if (import.meta.url === `file://${process.argv[1]}`) {
  cli().catch(error => {
    // Error handling is already set up in cli() function with asyncErrorHandler
    // This is a fallback for any errors that slip through
    if (process.env.DEBUG) {
      console.error('Unhandled CLI Error:', error);
      console.error(error.stack);
    }
    process.exit(error.exitCode || 1);
  });
}