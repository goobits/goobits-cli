#!/usr/bin/env node

/**
 * Auto-generated from nested-command-demo.yaml
 * CLI executable entry point for Nested Command Demo
 * Simplified version for reliable testing
 */

const { Command } = require('commander');
const path = require('path');
const fs = require('fs');

/**
 * Simple CLI implementation that works reliably
 */
function createCLI() {
  const program = new Command();
  
  program
    .name('demo')
    .description('Deep nesting demo')
    .version('1.0.0');

  // Add help command
  program
    .command('help')
    .description('Display help information')
    .action(() => {
      program.help();
    });

  // simple command
  const simpleCommand = program
    .command('simple')
    .description('Simple command that works today');

  simpleCommand.argument('<MESSAGE>', 'Message to display');

  simpleCommand.option('--verbose', 'Verbose output');

  simpleCommand.action(async (message, options) => {
    try {
      // Try to load hooks
      let hooks = {};
      try {
        hooks = require('../src/hooks');
      } catch (e) {
        console.warn('Warning: hooks module not found');
      }

      const hookName = 'onSimple';
      if (hooks[hookName] && typeof hooks[hookName] === 'function') {
        const context = {
          commandName: 'simple',
          args: { message },
          options: options || {},
          globalOptions: program.opts() || {}
        };
        await hooks[hookName](context);
      } else {
        console.log('simple command executed successfully');
        console.log('Hook function "' + hookName + '" not implemented yet');
      }
    } catch (error) {
      console.error('Error executing simple:', error.message);
      process.exit(1);
    }
  });
  // database command
  const databaseCommand = program
    .command('database')
    .description('Database operations');



  databaseCommand.action(async (options) => {
    try {
      // Try to load hooks
      let hooks = {};
      try {
        hooks = require('../src/hooks');
      } catch (e) {
        console.warn('Warning: hooks module not found');
      }

      const hookName = 'onDatabase';
      if (hooks[hookName] && typeof hooks[hookName] === 'function') {
        const context = {
          commandName: 'database',
          args: {  },
          options: options || {},
          globalOptions: program.opts() || {}
        };
        await hooks[hookName](context);
      } else {
        console.log('database command executed successfully');
        console.log('Hook function "' + hookName + '" not implemented yet');
      }
    } catch (error) {
      console.error('Error executing database:', error.message);
      process.exit(1);
    }
  });
  // api command
  const apiCommand = program
    .command('api')
    .description('API management');



  apiCommand.action(async (options) => {
    try {
      // Try to load hooks
      let hooks = {};
      try {
        hooks = require('../src/hooks');
      } catch (e) {
        console.warn('Warning: hooks module not found');
      }

      const hookName = 'onApi';
      if (hooks[hookName] && typeof hooks[hookName] === 'function') {
        const context = {
          commandName: 'api',
          args: {  },
          options: options || {},
          globalOptions: program.opts() || {}
        };
        await hooks[hookName](context);
      } else {
        console.log('api command executed successfully');
        console.log('Hook function "' + hookName + '" not implemented yet');
      }
    } catch (error) {
      console.error('Error executing api:', error.message);
      process.exit(1);
    }
  });

  return program;
}

// Main execution
function main() {
  try {
    const program = createCLI();
    program.parse(process.argv);
  } catch (error) {
    console.error('CLI Error:', error.message);
    process.exit(1);
  }
}

// Execute if this is the main module
if (require.main === module) {
  main();
}

module.exports = { createCLI, main };