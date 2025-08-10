/**
 * Auto-generated from test_typescript.yaml
 * Main CLI implementation for Test TypeScript CLI
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
  package_name: 'test-typescript-cli',
  command_name: 'testcli',
  display_name: 'Test TypeScript CLI',
  description: 'Test CLI for TypeScript validation',
  version: '1.0.0',
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
  return '1.0.0';
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
    join(process.env.HOME || '', '.config', 'goobits', 'testcli', 'plugins'),
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
  const packageName: string = 'test-typescript-cli';
  const displayName: string = 'Test TypeScript CLI';
  
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
    console.log(chalk.gray(`Run 'testcli --version' to verify the new version.`));
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
    .name('testcli')
    .description(`Test CLI for validation`)
    .version(version)
    .helpOption('-h, --help', 'Display help for command')
    .addHelpCommand('help [command]', 'Display help for command');

  // Configure help formatting
  program.configureHelp({
    sortSubcommands: true,
    subcommandTerm: (cmd: Command) => cmd.name() + ' ' + cmd.usage(),
  });

  // Global options
  

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

  

  

  // Built-in commands
  
  program
    .command('upgrade')
    .description('Upgrade Test TypeScript CLI to the latest version')
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
      .command('greet')
      .description('Greet someone')
      
      ;

    

    
    
    cmd.option(
      '----loud <str>',
      'Greet loudly'
    );
    
    

    cmd.action(async (options: Record<string, unknown>, command: Command) => {
      
      // Standard command - use hook pattern
      const hookName: string = 'onGreet';
      if (appHooks && appHooks[hookName]) {
        const hookFunc = appHooks[hookName];
        
        // Prepare strongly-typed command context
        const globalOptions: GlobalOptions = {
          
        };
        
        const context: CommandContext = {
          commandName: 'greet',
          args: {
            
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
        console.log(chalk.blue(`Executing greet command...`));
        
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

  

  

  

  // Parse arguments
  program.parse(process.argv);
  
  // Show help if no arguments provided and no default command
  
  
  
  
  
  if (!process.argv.slice(2).length) {
    program.outputHelp();
  }
  
}

// Export for use as a module
export default cli;