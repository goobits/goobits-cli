#!/usr/bin/env node

/**
 * Auto-generated from typescript-example.yaml
 * CLI executable entry point for Demo TypeScript CLI
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
    .name('demo_ts')
    .description('A sample TypeScript CLI built with Goobits')
    .version('1.0.0');

  // Add help command
  program
    .command('help')
    .description('Display help information')
    .action(() => {
      program.help();
    });

  // calculate command
  const calculateCommand = program
    .command('calculate')
    .description('Perform calculations');

  calculateCommand.argument('<operation>', 'Math operation');
  calculateCommand.argument('<a>', 'First number');
  calculateCommand.argument('<b>', 'Second number');

  calculateCommand.option('--precision, -p', 'Decimal precision', 2);

  calculateCommand.action(async (operation, a, b, options) => {
    try {
      // Try to load hooks
      let hooks = {};
      try {
        hooks = require('../src/hooks');
      } catch (e) {
        console.warn('Warning: hooks module not found');
      }

      const hookName = 'onCalculate';
      if (hooks[hookName] && typeof hooks[hookName] === 'function') {
        const context = {
          commandName: 'calculate',
          args: { operation, a, b },
          options: options || {},
          globalOptions: program.opts() || {}
        };
        await hooks[hookName](context);
      } else {
        console.log('calculate command executed successfully');
        console.log('Hook function "' + hookName + '" not implemented yet');
      }
    } catch (error) {
      console.error('Error executing calculate:', error.message);
      process.exit(1);
    }
  });
  // status command
  const statusCommand = program
    .command('status')
    .description('Show TypeScript environment status');



  statusCommand.action(async (options) => {
    try {
      // Try to load hooks
      let hooks = {};
      try {
        hooks = require('../src/hooks');
      } catch (e) {
        console.warn('Warning: hooks module not found');
      }

      const hookName = 'onStatus';
      if (hooks[hookName] && typeof hooks[hookName] === 'function') {
        const context = {
          commandName: 'status',
          args: {  },
          options: options || {},
          globalOptions: program.opts() || {}
        };
        await hooks[hookName](context);
      } else {
        console.log('status command executed successfully');
        console.log('Hook function "' + hookName + '" not implemented yet');
      }
    } catch (error) {
      console.error('Error executing status:', error.message);
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