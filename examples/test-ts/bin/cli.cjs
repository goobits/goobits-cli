#!/usr/bin/env node

/**
 * Auto-generated from goobits.yaml
 * CLI executable entry point for Test TypeScript
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
    .name('testts')
    .description('Test TS compilation')
    .version('1.0.0');

  // Add help command
  program
    .command('help')
    .description('Display help information')
    .action(() => {
      program.help();
    });

  // hello command
  const helloCommand = program
    .command('hello')
    .description('Say hello');

  helloCommand.argument('<NAME>', 'Name to greet');


  helloCommand.action(async (nameoptions) => {
    try {
      // Try to load hooks
      let hooks = {};
      try {
        hooks = require('../src/hooks');
      } catch (e) {
        console.warn('Warning: hooks module not found');
      }

      const hookName = 'onHello';
      if (hooks[hookName] && typeof hooks[hookName] === 'function') {
        const context = {
          commandName: 'hello',
          args: { name },
          options: options || {},
          globalOptions: program.opts() || {}
        };
        await hooks[hookName](context);
      } else {
        console.log('hello command executed successfully');
        console.log('Hook function "' + hookName + '" not implemented yet');
      }
    } catch (error) {
      console.error('Error executing hello:', error.message);
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