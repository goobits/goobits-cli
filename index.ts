/**
 * Auto-generated from goobits.yaml
 * Main CLI implementation for Goobits CLI Framework
 * 
 * Features:
 * - Comprehensive TypeScript type definitions
 * - Decorator-based command definition support
 * - Advanced plugin system
 * - Built-in validation framework
 * - Hot reload development support
 */

import 'reflect-metadata';
import { Command } from 'commander';
import chalk from 'chalk';
import { readdir } from 'fs/promises';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';
import { existsSync } from 'fs';

// Import enhanced type definitions
import type {
  CommandContext,
  GlobalOptions,
  HookRegistry,
  ConfigSchema,
} from './types/cli';

// Import comprehensive error handling
import type {
  CLIError,
  Result,
  CommandError,
  HookError,
  PluginError,
  FileSystemError,
  SystemError,
} from './types/errors';
import {
  CLIErrorCode,
  ExitCode,
  ErrorSeverity,
  createCommandError,
  createHookError,
  createPluginError,
  createFileSystemError,
  createSystemError,
  errorManager,
  success,
  failure,
  asyncResult,
  syncResult,
  isSuccess,
  isFailure,
  handleError,
} from './lib/errors';

// Import decorator system (optional)
try {
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  import { registerDecoratorCommands } from './examples/decorators';
} catch {
  // Decorator system not available or not used
}

const __filename: string = fileURLToPath(import.meta.url);
const __dirname: string = dirname(__filename);

// Create the main program
const program: Command = new Command();

// Legacy interface for backwards compatibility
interface PackageJson {
  readonly version: string;
  readonly [key: string]: unknown;
}

// Use the comprehensive type definitions from ./types/cli
type AppHooks = HookRegistry;

// Enhanced upgrade options with strict typing
interface UpgradeOptions {
  readonly check?: boolean;
  readonly version?: string;
  readonly pre?: boolean;
  readonly dryRun?: boolean;
}

// Runtime configuration (will be replaced by compile-time types in production)
const runtimeConfig: Partial<ConfigSchema> = {
  package_name: 'goobits-cli',
  command_name: 'goobits',
  display_name: 'Goobits CLI Framework',
  description: 'Build professional command-line tools with YAML configuration',
  version: '2.0.0-beta.1',
};

// Enhanced version helper function with Result pattern
async function getVersion(): Promise<Result<string, FileSystemError>> {
  return await asyncResult(
    async () => {
      const packagePath: string = join(__dirname, 'package.json');
      
      // Check if package.json exists
      if (!existsSync(packagePath)) {
        throw new Error(`Package file not found at ${packagePath}`);
      }
      
      const { default: pkg }: { default: PackageJson } = await import(packagePath, { assert: { type: 'json' } });
      
      if (!pkg.version || typeof pkg.version !== 'string') {
        throw new Error('Invalid or missing version in package.json');
      }
      
      return pkg.version;
    },
    (error) => createFileSystemError(
      error instanceof Error ? error.message : 'Failed to read version from package.json',
      {
        filePath: join(__dirname, 'package.json'),
        metadata: {
          operation: 'read',
          cause: error,
        },
      }
    )
  );
}

// Safe version getter that returns fallback on error
async function getVersionSafe(): Promise<string> {
  const result = await getVersion();
  if (isSuccess(result)) {
    return result.data;
  }
  
  // Log the error but continue with fallback
  console.debug && console.debug(chalk.yellow(`Warning: ${result.error.message}, using fallback version`));
  return '2.0.0-beta.1';
}

// Enhanced hooks system with Result pattern and type safety
let appHooks: AppHooks | null = null;

/**
 * Load hooks module with comprehensive error handling
 */
async function loadHooks(): Promise<Result<AppHooks | null, SystemError>> {
  
  // No hooks path configured, try default locations
  const hooksPath: string = join(__dirname, 'app_hooks.js');
  

  return await asyncResult(
    async () => {
      if (!existsSync(hooksPath)) {
        console.debug && console.debug(chalk.gray(`Hooks file not found at ${hooksPath}, continuing without hooks`));
        return null;
      }

      console.debug && console.debug(chalk.gray(`Loading hooks from ${hooksPath}`));
      const hooksModule = await import(hooksPath);
      
      // Validate hooks module structure
      if (!hooksModule || typeof hooksModule !== 'object') {
        throw new Error('Hooks module does not export a valid object');
      }

      console.debug && console.debug(chalk.green(`✓ Hooks loaded successfully from ${hooksPath}`));
      return hooksModule as AppHooks;
    },
    (error) => createSystemError(
      `Failed to load hooks module: ${error instanceof Error ? error.message : String(error)}`,
      {
        filePath: hooksPath,
        cause: error instanceof Error ? error : new Error(String(error)),
        metadata: {
          operation: 'import',
          hooksPath,
        },
      }
    )
  );
}

// Initialize hooks with error handling
const hooksResult = await loadHooks();
if (isSuccess(hooksResult)) {
  appHooks = hooksResult.data;
} else {
  // Log warning but continue - hooks are optional
  console.debug && console.debug(chalk.yellow(`Warning: ${hooksResult.error.message}`));
  appHooks = null;
}

// Gracefully handle missing hooks with meaningful errors
function getHook(hookName: string): unknown {
  if (!appHooks) {
    console.debug && console.debug(chalk.gray(`No hooks available, skipping ${hookName}`));
    return null;
  }
  
  const hook = appHooks[hookName];
  if (!hook) {
    console.debug && console.debug(chalk.gray(`Hook ${hookName} not found in hooks module`));
    return null;
  }
  
  return hook;
}

// Enhanced command loading with Result pattern and comprehensive error handling
async function loadCommands(program: Command): Promise<Result<number, FileSystemError>> {
  const commandsDir: string = join(__dirname, 'commands');
  
  return await asyncResult(
    async () => {
      if (!existsSync(commandsDir)) {
        console.debug && console.debug(chalk.gray(`Commands directory not found at ${commandsDir}, skipping dynamic commands`));
        return 0;
      }

      console.debug && console.debug(chalk.gray(`Loading commands from ${commandsDir}`));
      const files: string[] = await readdir(commandsDir);
      let loadedCount = 0;
      const errors: string[] = [];
      
      for (const file of files) {
        if (file.endsWith('.js') && !file.startsWith('_')) {
          const commandResult = await loadSingleCommand(program, commandsDir, file);
          if (isSuccess(commandResult)) {
            loadedCount++;
            console.debug && console.debug(chalk.green(`  ✓ Loaded command: ${file}`));
          } else {
            errors.push(`${file}: ${commandResult.error.message}`);
            console.warn && console.warn(chalk.yellow(`  ⚠ Failed to load command ${file}: ${commandResult.error.message}`));
          }
        }
      }
      
      if (errors.length > 0 && errors.length === files.filter(f => f.endsWith('.js') && !f.startsWith('_')).length) {
        throw new Error(`Failed to load any commands. Errors: ${errors.join('; ')}`);
      }
      
      console.debug && console.debug(chalk.green(`✓ Loaded ${loadedCount} dynamic commands`));
      return loadedCount;
    },
    (error) => createFileSystemError(
      `Failed to load commands directory: ${error instanceof Error ? error.message : String(error)}`,
      {
        filePath: commandsDir,
        cause: error instanceof Error ? error : new Error(String(error)),
        metadata: {
          operation: 'read',
          directory: commandsDir,
        },
      }
    )
  );
}

// Load a single command file with proper error handling
async function loadSingleCommand(program: Command, commandsDir: string, file: string): Promise<Result<void, SystemError>> {
  return await asyncResult(
    async () => {
      const commandPath: string = join(commandsDir, file);
      const { default: commandModule } = await import(commandPath);
      
      if (typeof commandModule === 'function') {
        commandModule(program);
      } else if (commandModule && typeof commandModule.register === 'function') {
        commandModule.register(program);
      } else {
        throw new Error(`Command module ${file} does not export a function or register method`);
      }
    },
    (error) => createSystemError(
      `Failed to load command ${file}: ${error instanceof Error ? error.message : String(error)}`,
      {
        filePath: join(commandsDir, file),
        cause: error instanceof Error ? error : new Error(String(error)),
        metadata: {
          operation: 'import',
          commandFile: file,
        },
      }
    )
  );
}

// Enhanced plugin loading with Result pattern and comprehensive error handling
async function loadPlugins(program: Command): Promise<Result<number, PluginError[]>> {
  const pluginDirs: string[] = [
    // User-specific plugin directory
    join(process.env.HOME || '', '.config', 'goobits', 'Goobits CLI', 'plugins'),
    // Local plugin directory
    join(__dirname, 'plugins'),
  ];
  
  const errors: PluginError[] = [];
  let totalLoaded = 0;
  
  for (const pluginDir of pluginDirs) {
    const result = await loadPluginsFromDirectory(program, pluginDir);
    if (isSuccess(result)) {
      totalLoaded += result.data;
    } else {
      errors.push(...result.error);
    }
  }
  
  console.debug && console.debug(chalk.green(`✓ Loaded ${totalLoaded} plugins total`));
  
  if (errors.length > 0 && totalLoaded === 0) {
    return failure(errors, false);
  }
  
  return success(totalLoaded, errors.length > 0 ? errors.map(e => e.message) : undefined);
}

// Load plugins from a single directory
async function loadPluginsFromDirectory(program: Command, pluginDir: string): Promise<Result<number, PluginError[]>> {
  return await asyncResult(
    async () => {
      if (!existsSync(pluginDir)) {
        console.debug && console.debug(chalk.gray(`Plugin directory not found: ${pluginDir}`));
        return 0;
      }
      
      console.debug && console.debug(chalk.gray(`Loading plugins from ${pluginDir}`));
      const files: string[] = await readdir(pluginDir);
      let loadedCount = 0;
      const errors: PluginError[] = [];
      
      for (const file of files) {
        if (file.endsWith('.js') && !file.startsWith('_')) {
          const pluginResult = await loadSinglePlugin(program, pluginDir, file);
          if (isSuccess(pluginResult)) {
            loadedCount++;
            console.debug && console.debug(chalk.green(`  ✓ Loaded plugin: ${file}`));
          } else {
            errors.push(pluginResult.error);
            console.warn && console.warn(chalk.yellow(`  ⚠ Failed to load plugin ${file}: ${pluginResult.error.message}`));
          }
        }
      }
      
      if (errors.length > 0) {
        throw errors;
      }
      
      return loadedCount;
    },
    (error) => Array.isArray(error) ? error : [createPluginError(
      `Failed to access plugin directory: ${error instanceof Error ? error.message : String(error)}`,
      {
        filePath: pluginDir,
        cause: error instanceof Error ? error : new Error(String(error)),
        metadata: {
          pluginName: 'unknown',
          operation: 'directory-access',
        },
      }
    )]
  );
}

// Load a single plugin file with proper error handling
async function loadSinglePlugin(program: Command, pluginDir: string, file: string): Promise<Result<void, PluginError>> {
  return await asyncResult(
    async () => {
      const pluginPath: string = join(pluginDir, file);
      const { default: pluginModule } = await import(pluginPath);
      
      if (typeof pluginModule === 'function') {
        pluginModule(program);
      } else if (pluginModule && typeof pluginModule.register === 'function') {
        pluginModule.register(program);
      } else {
        throw new Error(`Plugin ${file} does not export a function or register method`);
      }
    },
    (error) => createPluginError(
      `Failed to load plugin ${file}: ${error instanceof Error ? error.message : String(error)}`,
      {
        filePath: join(pluginDir, file),
        cause: error instanceof Error ? error : new Error(String(error)),
        metadata: {
          pluginName: file.replace(/\.js$/, ''),
          operation: 'load',
        },
      }
    )
  );
}


// Built-in upgrade command
async function builtinUpgradeCommand(options: UpgradeOptions): Promise<void> {
  const { execSync } = await import('child_process');
  const packageName: string = 'goobits-cli';
  const displayName: string = 'Goobits CLI Framework';
  
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
    let cmd: string = `npm install -g ${packageName}`;
    if (options.version) {
      cmd = `npm install -g ${packageName}@${options.version}`;
    } else if (options.pre) {
      cmd = `npm install -g ${packageName}@next`;
    }
    
    execSync(cmd, { stdio: 'inherit' });
    console.log(chalk.green(`✅ ${displayName} upgraded successfully!`));
    console.log(chalk.gray(`Run 'goobits --version' to verify the new version.`));
  } catch (error: any) {
    console.error(chalk.red(`❌ Upgrade failed: ${error.message}`));
    process.exit(1);
  }
}


// Main CLI setup
export async function cli(): Promise<void> {
  // Get version with safe fallback
  const version: string = await getVersionSafe();
  
  program
    .name('Goobits CLI')
    .description(`Build professional command-line tools with YAML configuration\n\nTransform simple YAML configuration into rich terminal applications with setup scripts, dependency management, and cross-platform compatibility.`)
    .version(version)
    .helpOption('-h, --help', 'Display help for command')
    .addHelpCommand('help [command]', 'Display help for command');

  // Configure help formatting
  program.configureHelp({
    sortSubcommands: true,
    subcommandTerm: (cmd: Command) => cmd.name() + ' ' + cmd.usage(),
  });

  // Global options
  
  
  program
    .option(
      '-v, --verbose',
      'Enable verbose output with detailed error messages and stack traces'
    );
  
  

  // Interactive mode option
  program
    .option('--interactive', 'Launch interactive mode for running commands interactively')
    .on('option:interactive', async () => {
      try {
        // Try to import interactive mode
        const { runInteractive } = await import('./interactive_mode.js'); // Note: imports compiled .js file
        runInteractive();
        process.exit(0);
      } catch (error) {
        console.error(chalk.red('❌ Interactive mode not available. Missing interactive mode module.'));
        console.error(chalk.gray(`Error: ${error instanceof Error ? error.message : String(error)}`));
        process.exit(1);
      }
    });

  

  
  // Add --help-all option
  program
    .option('--help-all', 'Show help for all commands', false)
    .on('option:help-all', () => {
      console.log(program.helpInformation());
      console.log('\n' + chalk.bold('All Commands:') + '\n');
      
      program.commands.forEach((cmd: Command) => {
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
  

  // Internal completion command (hidden from help)
  program
    .command('_completion <shell> <current_line> [cursor_pos]', { hidden: true })
    .option('--debug', 'Debug completion engine')
    .action(async (shell: string, currentLine: string, cursorPos?: string, options?: { debug?: boolean }) => {
      try {
        // Import completion engine
        const enginePath = join(__dirname, 'completion_engine.js');
        
        if (existsSync(enginePath)) {
          const { CompletionEngine } = await import(enginePath);
          const engine = new CompletionEngine();
          const completions = engine.getCompletions(shell, currentLine, cursorPos ? parseInt(cursorPos) : undefined);
          
          // Output completions
          for (const completion of completions) {
            console.log(completion);
          }
        } else if (options?.debug) {
          console.error('completion_engine.js not found');
        }
      } catch (error: unknown) {
        if (options?.debug) {
          const errorMessage = error instanceof Error ? error.message : String(error);
          console.error(`Completion error: ${errorMessage}`);
        }
        // Silently fail in production to avoid breaking shell completion
      }
    });

  // Define commands from configuration
  
  
  {
    const cmd = program
      .command('build')
      .description('🔨 Build CLI and setup scripts from goobits.yaml configuration')
      
      
      .isDefault(true)
      ;

    
    
    cmd.argument(
      '[config_path]',
      'Path to goobits.yaml file (defaults to ./goobits.yaml)'
    );
    
    

    
    
    cmd.option(
      '-o, --output-dir <str>',
      '📁 Output directory (defaults to same directory as config file)'
    );
    
    cmd.option(
      '--output <str>',
      '📝 Output filename for generated CLI (defaults to 'generated_cli.py')'
    );
    
    cmd.option(
      '--backup',
      '💾 Create backup files (.bak) when overwriting existing files'
    );
    
    cmd.option(
      '--universal-templates',
      '🧪 Use Universal Template System (experimental)'
    );
    
    

    cmd.action(async (config_path: unknown, options: Record<string, unknown>, command: Command) => {
      
      // Standard command - use hook pattern
      const hookName: string = 'onBuild';
      if (appHooks && appHooks[hookName]) {
        const hookFunc = appHooks[hookName];
        
        // Prepare strongly-typed command context
        const globalOptions: GlobalOptions = {
          
          verbose: command.parent?.opts().verbose as boolean,
          
        };
        
        const context: CommandContext = {
          commandName: 'build',
          args: {
            
            
            config_path: config_path as any,
            
            
          },
          options: options as Record<string, unknown>,
          globalOptions,
        };
        
        try {
          const result = await hookFunc(context);
          return result;
        } catch (error: unknown) {
          const errorMessage = error instanceof Error ? error.message : String(error);
          console.error(chalk.red(`Error: ${errorMessage}`));
          process.exit(1);
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
      'Name of the project (optional)'
    );
    
    

    
    
    cmd.option(
      '-t, --template <str>',
      '🎯 Template type',
      'basic'
    );
    
    cmd.option(
      '--force',
      '🔥 Overwrite existing goobits.yaml file'
    );
    
    

    cmd.action(async (project_name: unknown, options: Record<string, unknown>, command: Command) => {
      
      // Standard command - use hook pattern
      const hookName: string = 'onInit';
      if (appHooks && appHooks[hookName]) {
        const hookFunc = appHooks[hookName];
        
        // Prepare strongly-typed command context
        const globalOptions: GlobalOptions = {
          
          verbose: command.parent?.opts().verbose as boolean,
          
        };
        
        const context: CommandContext = {
          commandName: 'init',
          args: {
            
            
            project_name: project_name as any,
            
            
          },
          options: options as Record<string, unknown>,
          globalOptions,
        };
        
        try {
          const result = await hookFunc(context);
          return result;
        } catch (error: unknown) {
          const errorMessage = error instanceof Error ? error.message : String(error);
          console.error(chalk.red(`Error: ${errorMessage}`));
          process.exit(1);
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
      'Directory containing packages to serve'
    );
    
    

    
    
    cmd.option(
      '--host <str>',
      '🌍 Host to bind the server to',
      'localhost'
    );
    
    cmd.option(
      '-p, --port <int>',
      '🔌 Port to run the server on',
      8080
    );
    
    

    cmd.action(async (directory: unknown, options: Record<string, unknown>, command: Command) => {
      
      // Standard command - use hook pattern
      const hookName: string = 'onServe';
      if (appHooks && appHooks[hookName]) {
        const hookFunc = appHooks[hookName];
        
        // Prepare strongly-typed command context
        const globalOptions: GlobalOptions = {
          
          verbose: command.parent?.opts().verbose as boolean,
          
        };
        
        const context: CommandContext = {
          commandName: 'serve',
          args: {
            
            
            directory: directory as any,
            
            
          },
          options: options as Record<string, unknown>,
          globalOptions,
        };
        
        try {
          const result = await hookFunc(context);
          return result;
        } catch (error: unknown) {
          const errorMessage = error instanceof Error ? error.message : String(error);
          console.error(chalk.red(`Error: ${errorMessage}`));
          process.exit(1);
        }
      } else {
        // Default placeholder behavior
        console.log(chalk.blue(`Executing serve command...`));
        
        
        console.log(`  directory: ${directory}`);
        
        
        console.log('Options:', options);
      }
      
    });
  }
  
  

  // Load dynamic commands from commands directory with error handling
  const commandsResult = await loadCommands(program);
  if (isFailure(commandsResult)) {
    console.warn && console.warn(chalk.yellow(`Warning: ${commandsResult.error.message}`));
    if (process.env.DEBUG) {
      console.debug && console.debug(chalk.gray('Commands loading failed, continuing without dynamic commands'));
    }
  }
  
  // Load plugins with error handling
  const pluginsResult = await loadPlugins(program);
  if (isFailure(pluginsResult)) {
    console.warn && console.warn(chalk.yellow(`Warning: Failed to load plugins`));
    if (process.env.DEBUG) {
      pluginsResult.error.forEach(error => {
        console.debug && console.debug(chalk.gray(`  Plugin error: ${error.message}`));
      });
    }
  }

  
  // Command groups for help display
  program.addHelpText('after', '\n' + chalk.bold('Command Groups:'));
  
  program.addHelpText('after', `\n${chalk.yellow('Core Commands:')}`);
  
  
  const buildCmd = program.commands.find((c: Command) => c.name() === 'build');
  if (buildCmd) {
    program.addHelpText('after', `  ${buildCmd.name().padEnd(15)} ${buildCmd.description()}`);
  }
  
  
  
  const initCmd = program.commands.find((c: Command) => c.name() === 'init');
  if (initCmd) {
    program.addHelpText('after', `  ${initCmd.name().padEnd(15)} ${initCmd.description()}`);
  }
  
  
  
  program.addHelpText('after', `\n${chalk.yellow('Development Tools:')}`);
  
  
  const serveCmd = program.commands.find((c: Command) => c.name() === 'serve');
  if (serveCmd) {
    program.addHelpText('after', `  ${serveCmd.name().padEnd(15)} ${serveCmd.description()}`);
  }
  
  
  
  

  
  // Add header sections to help
  let headerText: string = '';
  
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
  

  // Parse arguments
  program.parse(process.argv);
  
  // Show help if no arguments provided and no default command
  
  
  
  
  
  
  
  
  
  
  
}

// Export for use as a module
export default cli;