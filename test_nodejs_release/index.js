/**
 * Auto-generated from goobits.yaml
 * Main CLI implementation for Goobits CLI Framework
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
    return '3.0.0-alpha.1';
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
      join(process.env.HOME || '', '.config', 'goobits', 'Goobits CLI', 'plugins'),
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
  const packageName = 'goobits-cli';
  const displayName = 'Goobits CLI Framework';
  
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
    console.log(chalk.gray(`Run 'goobits --version' to verify the new version.`));
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
      console.log(`# Basic bash completion for goobits
_goobits_completions() {
    local cur prev words cword
    _init_completion || return
    
    case "\${prev}" in
        goobits)
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

complete -F _goobits_completions goobits`);
      break;
      
    case 'zsh':
      console.log(`#compdef goobits
# Basic zsh completion for goobits
_goobits() {
    local commands=(
        ${commands.split(' ').map(cmd => `'${cmd}:${cmd} command'`).join('\n        ')}
    )
    
    _arguments \\
        '(-h --help)'{-h,--help}'[Show help information]' \\
        '(-V --version)'{-V,--version}'[Show version information]' \\
        '1: :_describe "commands" commands' \\
        '*::arg:->args'
}

_goobits "$@"`);
      break;
      
    case 'fish':
      console.log(`# Basic fish completion for goobits
complete -c goobits -f
complete -c goobits -l help -s h -d 'Show help information'
complete -c goobits -l version -s V -d 'Show version information'

${commands.split(' ').map(cmd => 
  `complete -c goobits -n '__fish_use_subcommand' -a ${cmd} -d '${cmd} command'`
).join('\n')}`);
      break;
  }
}

// Main CLI setup
export const cli = asyncErrorHandler(async function cli() {
  const version = await getVersion();
  
  program
    .name('Goobits CLI')
    .description(`Build professional command-line tools with YAML configuration\n\nTransform simple YAML configuration into rich terminal applications with setup scripts, dependency management, and cross-platform compatibility.`)
    .version(version)
    .helpOption('-h, --help', 'Display help for command')
    .addHelpCommand('help [command]', 'Display help for command');

  // Configure help formatting
  program.configureHelp({
    sortSubcommands: true,
    subcommandTerm: (cmd) => cmd.name() + ' ' + cmd.usage(),
  });

  // Global options
  program
    .option(
      '-v, --verbose',
      'Enable verbose output with detailed error messages and stack traces'    );

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
  const builtin_completionCmd = program
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

  // Add --help-all option
  program
    .option('--help-all', 'Show help for all commands', false)
    .on('option:help-all', () => {
      console.log(program.helpInformation());
      console.log('\n' + chalk.bold('All Commands:') + '\n');
      
      program.commands.forEach(cmd => {
        console.log(chalk.yellow('='.repeat(50)));
        console.log(chalk.bold(`Command: ${cmd.name()}`));
        console.log(cmd.helpInformation());
      });
      
      process.exit(0);
    });

  // Built-in commands
  program
    .command('upgrade')
    .description('Upgrade Goobits CLI Framework to the latest version')
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
      .command('build', { isDefault: true })
      .description('🔨 Build CLI and setup scripts from goobits.yaml configuration')
;

    cmd.argument(
      '[config_path]',
      'Path to goobits.yaml file (defaults to ./goobits.yaml)'    );

    cmd.option(
      '-o, --output-dir <str>',
      '📁 Output directory (defaults to same directory as config file)'    );
    cmd.option(
      '--output <str>',
      '📝 Output filename for generated CLI (defaults to 'generated_cli.py')'    );
    cmd.option(
      '--backup',
      '💾 Create backup files (.bak) when overwriting existing files'    );
    cmd.option(
      '--universal-templates',
      '🧪 Use Universal Template System (experimental)'    );

    cmd.action(async (config_path, options, command) => {
      // Standard command - use hook pattern
      const hookName = 'onBuild';
      if (appHooks && appHooks[hookName]) {
        const hookFunc = appHooks[hookName];
        
        // Prepare arguments
        const args = {
          commandName: 'build',
          config_path: config_path,
          ...options,
          // Add global options
          verbose: command.parent.opts().verbose,
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
            `Failed to execute command 'build'. ${error.message}`,
            1
          );
          handleError(hookError);
        }
      } else {
        // Default placeholder behavior
        
        console.log(chalk.blue(`Executing build command...`));
        
        console.log(`  config_path: ${config_path}`);
        console.log('Options:', options);
        
      }
    });
  }
  {
    const cmd = program
      .command('init')
      .description('🆕 Create initial goobits.yaml template')
;

    cmd.argument(
      '[project_name]',
      'Name of the project (optional)'    );

    cmd.option(
      '-t, --template [str]',
      '🎯 Template type',
'basic'    );
    cmd.option(
      '--force',
      '🔥 Overwrite existing goobits.yaml file'    );

    cmd.action(async (project_name, options, command) => {
      // Standard command - use hook pattern
      const hookName = 'onInit';
      if (appHooks && appHooks[hookName]) {
        const hookFunc = appHooks[hookName];
        
        // Prepare arguments
        const args = {
          commandName: 'init',
          project_name: project_name,
          ...options,
          // Add global options
          verbose: command.parent.opts().verbose,
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
            `Failed to execute command 'init'. ${error.message}`,
            1
          );
          handleError(hookError);
        }
      } else {
        // Default placeholder behavior
        
        console.log(chalk.blue(`Executing init command...`));
        
        console.log(`  project_name: ${project_name}`);
        console.log('Options:', options);
        
      }
    });
  }
  {
    const cmd = program
      .command('serve')
      .description('🌐 Serve local PyPI-compatible package index')
;

    cmd.argument(
      '<directory>',
      'Directory containing packages to serve'    );

    cmd.option(
      '--host [str]',
      '🌍 Host to bind the server to',
'localhost'    );
    cmd.option(
      '-p, --port [int]',
      '🔌 Port to run the server on',
8080    );

    cmd.action(async (directory, options, command) => {
      // Standard command - use hook pattern
      const hookName = 'onServe';
      if (appHooks && appHooks[hookName]) {
        const hookFunc = appHooks[hookName];
        
        // Prepare arguments
        const args = {
          commandName: 'serve',
          directory: directory,
          ...options,
          // Add global options
          verbose: command.parent.opts().verbose,
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
            `Failed to execute command 'serve'. ${error.message}`,
            1
          );
          handleError(hookError);
        }
      } else {
        // Default placeholder behavior
        
        console.log(chalk.blue(`Executing serve command...`));
        
        console.log(`  directory: ${directory}`);
        console.log('Options:', options);
        
      }
    });
  }

  // Load dynamic commands from commands directory
  await loadCommands(program);
  
  // Load plugins
  await loadPlugins(program);

  // Command groups for help display
  program.addHelpText('after', '\n' + chalk.bold('Command Groups:'));
  program.addHelpText('after', `\n${chalk.yellow('Core Commands:')}`);
  const buildCmd = program.commands.find(c => c.name() === 'build');
  if (buildCmd) {
    program.addHelpText('after', `  ${buildCmd.name().padEnd(15)} ${buildCmd.description()}`);
  }
  const initCmd = program.commands.find(c => c.name() === 'init');
  if (initCmd) {
    program.addHelpText('after', `  ${initCmd.name().padEnd(15)} ${initCmd.description()}`);
  }
  program.addHelpText('after', `\n${chalk.yellow('Development Tools:')}`);
  const serveCmd = program.commands.find(c => c.name() === 'serve');
  if (serveCmd) {
    program.addHelpText('after', `  ${serveCmd.name().padEnd(15)} ${serveCmd.description()}`);
  }

  // Add header sections to help
  let headerText = '';
  headerText += '\n' + chalk.bold.yellow('🚀 Quick Start') + '\n';
  headerText += chalk.green('  mkdir my-cli && cd my-cli') + chalk.gray(' # Create new project directory') + '\n';
  headerText += chalk.green('  goobits init') + chalk.gray(' # Generate initial goobits.yaml') + '\n';
  headerText += chalk.green('  goobits build') + chalk.gray(' # Create CLI and setup scripts') + '\n';
  headerText += chalk.green('  ./setup.sh install --dev') + chalk.gray(' # Install for development') + '\n';
  headerText += '\n' + chalk.bold.yellow('💡 Core Commands') + '\n';
  headerText += chalk.green('  build') + '  🔨 Generate CLI and setup scripts from goobits.yaml\n';
  headerText += chalk.green('  serve') + '  🌐 Serve local PyPI-compatible package index\n';
  headerText += chalk.green('  init') + '  🆕 Create initial goobits.yaml template\n';
  headerText += '\n' + chalk.bold.yellow('🔧 Development Workflow') + '\n';
  headerText += chalk.gray('  1. Edit goobits.yaml: ') + chalk.green('Define your CLI structure') + '\n';
  headerText += chalk.gray('  2. goobits build: ') + chalk.green('Generate implementation files') + '\n';
  headerText += chalk.gray('  3. Edit app_hooks.py: ') + chalk.green('Add your business logic') + '\n';
  program.addHelpText('before', headerText);

  // Add footer note
  program.addHelpText('after', '\n' + chalk.gray('📚 For detailed help on a command, run: [color(2)]goobits [COMMAND][/color(2)] [#ff79c6]--help[/#ff79c6]'));

  // Parse arguments with error handling
  try {
    program.parse(process.argv);
    
    // Show help if no arguments provided and no default command
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