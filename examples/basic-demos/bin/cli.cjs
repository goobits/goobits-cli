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
    .description('TypeScript CLI demonstration')
    .version('1.0.0');

  // Add help command
  program
    .command('help')
    .description('Display help information')
    .action(() => {
      program.help();
    });

  // greet command
  const greetCommand = program
    .command('greet')
    .description('Greet someone with style');

  greetCommand.argument('<NAME>', 'Name to greet');
  greetCommand.argument('[MESSAGE]', 'Custom greeting message');

  greetCommand.option('--style, -s <style>', 'Greeting style', "casual");
  greetCommand.option('--count, -c <count>', 'Repeat greeting N times', 1);
  greetCommand.option('--uppercase, -u', 'Convert to uppercase');
  greetCommand.option('--language, -l <language>', 'Language code', "en");

  greetCommand.action(async (name, message, options) => {
    try {
      // Try to load hooks
      let hooks = {};
      try {
        hooks = require('../src/hooks');
      } catch (e) {
        console.warn('Warning: hooks module not found');
      }

      const hookName = 'onGreet';
      if (hooks[hookName] && typeof hooks[hookName] === 'function') {
        const context = {
          commandName: 'greet',
          args: { name, message },
          options: options || {},
          globalOptions: program.opts() || {}
        };
        await hooks[hookName](context);
      } else {
        console.log('greet command executed successfully');
        console.log('Hook function "' + hookName + '" not implemented yet');
      }
    } catch (error) {
      console.error('Error executing greet:', error.message);
      process.exit(1);
    }
  });
  // info command
  const infoCommand = program
    .command('info')
    .description('Display system and environment information');


  infoCommand.option('--format, -f <format>', 'Output format', "text");
  infoCommand.option('--verbose, -v', 'Show detailed information');
  infoCommand.option('--sections, -s <sections>', 'Comma-separated sections to show', "all");

  infoCommand.action(async (options) => {
    try {
      // Try to load hooks
      let hooks = {};
      try {
        hooks = require('../src/hooks');
      } catch (e) {
        console.warn('Warning: hooks module not found');
      }

      const hookName = 'onInfo';
      if (hooks[hookName] && typeof hooks[hookName] === 'function') {
        const context = {
          commandName: 'info',
          args: {  },
          options: options || {},
          globalOptions: program.opts() || {}
        };
        await hooks[hookName](context);
      } else {
        console.log('info command executed successfully');
        console.log('Hook function "' + hookName + '" not implemented yet');
      }
    } catch (error) {
      console.error('Error executing info:', error.message);
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