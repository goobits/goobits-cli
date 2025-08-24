/**
 * Format demonstration command for Demo Node.js CLI
 * Shows off the output formatting capabilities
 */

import { Command } from 'commander';
import chalk from 'chalk';
import { addFormatOption, outputFormatted } from '../../lib/formatter.js';

export default function registerFormatDemoCommand(program) {
  const builtin_formatDemoCmd = program
    .command('format-demo')
    .description('🎨 Demonstrate output formatting capabilities')
    .alias('demo');

  // Add format options to the command
  addFormatOption(builtin_formatDemoCmd);

  // Add demo-specific options
  builtin_formatDemoCmd
    .option('--sample <type>', 'Sample data type (simple|complex|list|mixed)', 'simple')
    .action(async (options) => {
      try {
        const sampleData = generateSampleData(options.sample);
        
        console.log(chalk.bold.blue(`\n🎨 Format Demo: ${options.sample} data\n`));
        
        if (options.format === 'auto') {
          // Show multiple formats for demonstration
          const formats = ['table', 'json', 'yaml', 'list'];
          
          for (const format of formats) {
            console.log(chalk.bold.yellow(`\n═══ ${format.toUpperCase()} Format ═══`));
            outputFormatted(sampleData, { ...options, format });
          }
        } else {
          // Show specific format
          outputFormatted(sampleData, options);
        }
        
        if (options.format === 'auto') {
          showFormatHelp();
        }
      } catch (error) {
        console.error(chalk.red(`Format demo failed: ${error.message}`));
        process.exit(1);
      }
    });

  return builtin_formatDemoCmd;
}

/**
 * Generate sample data for demonstration
 */
function generateSampleData(type) {
  switch (type) {
    case 'simple':
      return [
        { name: 'Alice', age: 30, city: 'New York' },
        { name: 'Bob', age: 25, city: 'San Francisco' },
        { name: 'Charlie', age: 35, city: 'London' },
        { name: 'Diana', age: 28, city: 'Tokyo' }
      ];
      
    case 'complex':
      return {
        project: 'Demo Node.js CLI',
        version: '1.0.0',
        stats: {
          commands: 15,
          plugins: 3,
          tests: 42
        },
        features: [
          'Plugin System',
          'Shell Completions', 
          'Output Formatting',
          'Testing Framework'
        ],
        contributors: [
          { name: 'Developer 1', commits: 156, active: true },
          { name: 'Developer 2', commits: 89, active: false },
          { name: 'Developer 3', commits: 234, active: true }
        ],
        metadata: {
          created: '2024-01-01',
          language: 'JavaScript',
          license: 'MIT',
          dependencies: {
            commander: '^11.1.0',
            chalk: '^5.3.0'
          }
        }
      };
      
    case 'list':
      return [
        'Plugin System Enhancement',
        'Advanced Shell Completions',
        'Built-in Testing Framework', 
        'Standardized Output Formatting',
        'Configuration Management',
        'Error Handling Improvements',
        'Documentation Updates',
        'Performance Optimizations'
      ];
      
    case 'mixed':
      return [
        { 
          type: 'feature', 
          name: 'Plugin System', 
          status: 'completed',
          priority: 'high',
          assignee: 'Alice',
          tags: ['core', 'extensibility']
        },
        { 
          type: 'bug', 
          name: 'Memory leak in command parsing', 
          status: 'in-progress',
          priority: 'medium',
          assignee: 'Bob',
          tags: ['performance', 'critical']
        },
        { 
          type: 'enhancement', 
          name: 'Better error messages', 
          status: 'pending',
          priority: 'low',
          assignee: null,
          tags: ['ux', 'documentation']
        },
        { 
          type: 'feature', 
          name: 'Shell completions', 
          status: 'completed',
          priority: 'high',
          assignee: 'Charlie',
          tags: ['usability', 'shell']
        }
      ];
      
    default:
      throw new Error(`Unknown sample type: ${type}`);
  }
}

/**
 * Show help about available formats
 */
function showFormatHelp() {
  console.log(chalk.bold.blue('\n📖 Available Output Formats:\n'));
  
  const formats = [
    {
      name: 'table',
      description: 'Tabular format with borders (best for arrays of objects)',
      example: 'demo_js format-demo --format table'
    },
    {
      name: 'json',
      description: 'JSON format with syntax highlighting',
      example: 'demo_js format-demo --format json'
    },
    {
      name: 'yaml',
      description: 'YAML format with syntax highlighting',
      example: 'demo_js format-demo --format yaml'
    },
    {
      name: 'csv',
      description: 'Comma-separated values (good for spreadsheets)',
      example: 'demo_js format-demo --format csv'
    },
    {
      name: 'list',
      description: 'Simple bulleted list format',
      example: 'demo_js format-demo --format list --sample list'
    },
    {
      name: 'tree',
      description: 'Tree structure format (good for nested objects)',
      example: 'demo_js format-demo --format tree --sample complex'
    },
    {
      name: 'auto',
      description: 'Automatically choose best format based on data type',
      example: 'demo_js format-demo --format auto'
    }
  ];
  
  formats.forEach(format => {
    console.log(`${chalk.cyan(format.name.padEnd(8))} ${format.description}`);
    console.log(`${' '.repeat(10)}${chalk.gray(format.example)}\n`);
  });
  
  console.log(chalk.bold.yellow('💡 Tips:'));
  console.log('• Use --no-colors to disable colored output');
  console.log('• Use --max-width to control table width');
  console.log('• Use --format auto to let the system choose the best format');
  console.log('• Pipe output to files: demo_js format-demo --format csv > data.csv');
}