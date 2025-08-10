#!/usr/bin/env node

/**
 * Auto-generated from test_config_typescript.yaml
 * CLI executable entry point for TypeScript Test CLI
 * Enhanced with comprehensive typed error handling
 */

import { createRequire } from 'module';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';
import chalk from 'chalk';

// Import error handling types and utilities
import type { 
  CLIError, 
  SystemError, 
  Result 
} from '../types/errors.js';
import { 
  CLIErrorCode, 
  ExitCode, 
  ErrorSeverity,
  createSystemError,
  errorManager,
  handleError,
  isFailure 
} from '../lib/errors.js';

const require = createRequire(import.meta.url);
const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// === Enhanced Error Handling ===

/**
 * Convert a generic error to a typed SystemError
 */
function createSystemErrorFromGeneric(error: unknown, context: string): SystemError {
  const message = error instanceof Error ? error.message : String(error);
  const stack = error instanceof Error ? error.stack : undefined;
  
  return createSystemError(`${context}: ${message}`, {
    cause: error instanceof Error ? error : new Error(String(error)),
    metadata: {
      context,
      systemCode: error instanceof Error && 'code' in error ? String(error.code) : undefined,
      signal: error instanceof Error && 'signal' in error ? String(error.signal) : undefined,
    },
  });
}

/**
 * Enhanced uncaught exception handler with typed errors
 */
process.on('uncaughtException', (error: Error) => {
  const systemError = createSystemErrorFromGeneric(error, 'Uncaught Exception');
  
  console.error(chalk.red.bold('💥 Fatal Error: Uncaught Exception'));
  console.error(chalk.red(`Error: ${error.message}`));
  
  if (process.env.DEBUG) {
    console.error(chalk.gray('Stack trace:'));
    console.error(chalk.gray(error.stack || 'No stack trace available'));
    console.error(chalk.gray('Context:'), systemError.context || 'No additional context');
  } else {
    console.error(chalk.yellow('Run with DEBUG=1 for detailed error information'));
  }
  
  // Log to error manager for potential recovery or logging
  errorManager.handle(systemError).catch(() => {
    // If error manager fails, just exit
    process.exit(ExitCode.FATAL_ERROR_SIGNAL_N);
  });
  
  process.exit(ExitCode.FATAL_ERROR_SIGNAL_N);
});

/**
 * Enhanced unhandled rejection handler with typed errors
 */
process.on('unhandledRejection', (reason: unknown, promise: Promise<unknown>) => {
  const systemError = createSystemErrorFromGeneric(
    reason, 
    'Unhandled Promise Rejection'
  );
  
  console.error(chalk.red.bold('💥 Fatal Error: Unhandled Promise Rejection'));
  console.error(chalk.red(`Reason: ${reason instanceof Error ? reason.message : String(reason)}`));
  
  if (process.env.DEBUG) {
    console.error(chalk.gray('Promise:'), promise);
    if (reason instanceof Error && reason.stack) {
      console.error(chalk.gray('Stack trace:'));
      console.error(chalk.gray(reason.stack));
    }
    console.error(chalk.gray('Context:'), systemError.context || 'No additional context');
  } else {
    console.error(chalk.yellow('Run with DEBUG=1 for detailed error information'));
  }
  
  // Log to error manager
  errorManager.handle(systemError).catch(() => {
    process.exit(ExitCode.FATAL_ERROR_SIGNAL_N);
  });
  
  process.exit(ExitCode.FATAL_ERROR_SIGNAL_N);
});

/**
 * Handle SIGTERM and SIGINT gracefully
 */
process.on('SIGTERM', () => {
  console.log(chalk.yellow('\n⚠ Received SIGTERM, shutting down gracefully...'));
  process.exit(ExitCode.SUCCESS);
});

process.on('SIGINT', () => {
  console.log(chalk.yellow('\n⚠ Received SIGINT (Ctrl+C), shutting down gracefully...'));
  process.exit(ExitCode.SCRIPT_TERMINATED_BY_CTRL_C);
});

// === Main CLI Execution ===

/**
 * Load and execute the main CLI with comprehensive error handling
 */
async function runCLI(): Promise<void> {
  try {
    const mainPath: string = join(__dirname, '..', 'index.js');
    
    // Check if main file exists
    const { existsSync } = await import('fs');
    if (!existsSync(mainPath)) {
      const error = createSystemError(
        `Main CLI file not found: ${mainPath}`,
        {
          filePath: mainPath,
          metadata: {
            operation: 'load',
            expectedPath: mainPath,
          },
        }
      );
      handleError(error);
    }
    
    // Dynamic import with error handling
    let cliModule: { cli?: () => Promise<void> };
    try {
      cliModule = await import(mainPath);
    } catch (importError) {
      const error = createSystemError(
        `Failed to import main CLI module`,
        {
          filePath: mainPath,
          cause: importError instanceof Error ? importError : new Error(String(importError)),
          metadata: {
            operation: 'import',
            modulePath: mainPath,
          },
        }
      );
      handleError(error);
    }
    
    // Check if CLI function exists
    if (!cliModule.cli || typeof cliModule.cli !== 'function') {
      const error = createSystemError(
        'Main CLI module does not export a cli function',
        {
          filePath: mainPath,
          metadata: {
            availableExports: Object.keys(cliModule),
            expectedExport: 'cli',
          },
        }
      );
      handleError(error);
    }
    
    // Execute the CLI
    console.debug && console.debug(chalk.gray(`Starting TypeScript Test CLI...`));
    await cliModule.cli();
    console.debug && console.debug(chalk.gray(`TypeScript Test CLI completed successfully`));
    
  } catch (error: unknown) {
    // Final catch-all error handler
    const systemError = createSystemErrorFromGeneric(
      error,
      'CLI Execution Failed'
    );
    
    console.error(chalk.red.bold('✗ Failed to start TypeScript Test CLI'));
    console.error(chalk.red(`Error: ${systemError.message}`));
    
    if (process.env.DEBUG && systemError.stack) {
      console.error(chalk.gray('Stack trace:'));
      console.error(chalk.gray(systemError.stack));
    }
    
    if (systemError.cause) {
      console.error(chalk.gray('Caused by:'), systemError.cause.message);
    }
    
    // Show helpful suggestions
    console.error(chalk.cyan('\nTroubleshooting:'));
    console.error(chalk.cyan('  • Ensure TypeScript Test CLI is properly installed'));
    console.error(chalk.cyan('  • Check that all dependencies are available'));
    console.error(chalk.cyan('  • Run with DEBUG=1 for detailed error information'));
    console.error(chalk.cyan('  • Try reinstalling: npm install -g typescript-test-cli'));
    
    process.exit(ExitCode.SOFTWARE_ERROR);
  }
}

// Start the CLI
runCLI().catch((error: unknown) => {
  // This should never happen due to comprehensive error handling above,
  // but provide a final safety net
  console.error(chalk.red.bold('💥 Catastrophic failure in CLI startup'));
  console.error(error);
  process.exit(ExitCode.FATAL_ERROR_SIGNAL_N);
});