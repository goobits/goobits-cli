#!/usr/bin/env node

/**
 * Auto-generated from nodejs-example.yaml
 * CLI executable entry point for Demo Node.js CLI
 */

import { createRequire } from 'module';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const require = createRequire(import.meta.url);
const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// Handle process signals gracefully
process.on('SIGINT', () => {
  console.log('\n\nReceived SIGINT (Ctrl+C). Shutting down gracefully...');
  process.exit(130); // Standard SIGINT exit code
});

process.on('SIGTERM', () => {
  console.log('\nReceived SIGTERM. Shutting down gracefully...');
  process.exit(143); // Standard SIGTERM exit code
});

// Try to load advanced error handling
async function setupErrorHandling() {
  try {
    const errorModule = await import('../lib/errors.js');
    const errorHandler = errorModule.setupGlobalErrorHandlers({
      showStack: process.env.NODE_ENV === 'development' || process.env.DEBUG,
      colorize: true,
      exitOnError: true
    });
    return errorHandler;
  } catch (importError) {
    // Fallback to basic error handling if errors module is not available
    if (process.env.DEBUG) {
      console.warn('Warning: Advanced error handling not available, using basic handlers');
    }
    
    // Handle uncaught exceptions gracefully
    process.on('uncaughtException', (err) => {
      console.error('Uncaught Exception:', err.message);
      if (process.env.DEBUG) {
        console.error(err.stack);
      }
      process.exit(1);
    });

    process.on('unhandledRejection', (reason, promise) => {
      console.error('Unhandled Rejection:', reason instanceof Error ? reason.message : reason);
      if (process.env.DEBUG) {
        console.error('Promise:', promise);
        if (reason instanceof Error) {
          console.error(reason.stack);
        }
      }
      process.exit(1);
    });
    
    return null;
  }
}

// Main execution function
async function main() {
  // Setup error handling first
  const errorHandler = await setupErrorHandling();
  
  // Import and run the main CLI
  try {
    const mainPath = join(__dirname, '..', 'index.js');
    const { cli } = await import(mainPath);
    
    // Run the CLI
    await cli();
  } catch (error) {
    // Use advanced error handling if available
    if (errorHandler) {
      // Error will be handled by the global error handler
      throw error;
    } else {
      // Fallback error handling
      console.error('Failed to start Demo Node.js CLI:', error.message);
      if (process.env.DEBUG) {
        console.error(error.stack);
      }
      
      // Use appropriate exit code
      const exitCode = error.exitCode || 
                      (error.code === 'MODULE_NOT_FOUND' ? 127 : 1);
      process.exit(exitCode);
    }
  }
}

// Run main function
main().catch(error => {
  // Final fallback error handler
  console.error('Fatal error:', error.message);
  if (process.env.DEBUG) {
    console.error(error.stack);
  }
  process.exit(1);
});