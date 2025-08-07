# Node.js & TypeScript CLI Generation Guide

This comprehensive guide will help JavaScript and TypeScript developers use Goobits CLI to generate professional command-line tools. Whether you're building developer tools, automation scripts, or full-featured CLI applications, Goobits provides a consistent, maintainable approach.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Understanding the Architecture](#understanding-the-architecture)
3. [Configuration Guide](#configuration-guide)
4. [Working with app_hooks.js](#working-with-app_hooksjs)
5. [TypeScript Development](#typescript-development)
6. [Advanced Features](#advanced-features)
7. [Testing Your CLI](#testing-your-cli)
8. [Publishing to npm](#publishing-to-npm)
9. [Real-World Examples](#real-world-examples)
10. [Troubleshooting](#troubleshooting)

## Quick Start

### Prerequisites

- Node.js 18+ and npm installed
- Goobits CLI installed (`pipx install goobits-cli`)

### Your First Node.js CLI in 5 Minutes

1. **Create your project directory:**
```bash
mkdir my-awesome-cli
cd my-awesome-cli
```

2. **Create a `goobits.yaml` configuration:**
```yaml
# goobits.yaml
language: nodejs  # or 'typescript' for TypeScript
package_name: my-awesome-cli
command_name: awesome
display_name: "Awesome CLI"
description: "A CLI tool that does awesome things"

# Node.js specific configuration
installation:
  extras:
    npm:
      - "chalk@5.3.0"        # Terminal colors
      - "ora@8.0.1"          # Spinner for long operations
      - "inquirer@9.2.15"    # Interactive prompts

# CLI structure
cli:
  name: awesome
  tagline: "Make awesome things happen"
  version: "1.0.0"
  commands:
    greet:
      desc: "Greet someone with style"
      args:
        - name: name
          desc: "Name to greet"
          required: true
      options:
        - name: style
          short: s
          desc: "Greeting style"
          choices: ["friendly", "formal", "excited"]
          default: "friendly"
```

3. **Generate your CLI:**
```bash
# Generate using legacy templates (stable)
goobits build

# Generate using Universal Template System (experimental)
goobits build --universal-templates
```

This creates:
```
my-awesome-cli/
├── index.js          # Main CLI entry point
├── package.json      # npm package configuration
├── bin/
│   └── cli.js        # Executable wrapper
├── lib/
│   └── config.js     # Configuration utilities
├── app_hooks.js      # YOUR business logic goes here
├── setup.sh          # Installation script
├── README.md         # Auto-generated documentation
└── .gitignore        # Node.js ignores
```

4. **Add your business logic:**
```javascript
// app_hooks.js
import chalk from 'chalk';
import ora from 'ora';

export async function onGreet(args) {
    const { name, style } = args;
    
    const spinner = ora('Preparing greeting...').start();
    
    // Simulate some work
    await new Promise(resolve => setTimeout(resolve, 500));
    
    let greeting;
    switch (style) {
        case 'formal':
            greeting = chalk.blue(`Good day, ${name}.`);
            break;
        case 'excited':
            greeting = chalk.yellow.bold(`🎉 HEY ${name.toUpperCase()}! 🎉`);
            break;
        default:
            greeting = chalk.green(`Hello ${name}! 👋`);
    }
    
    spinner.succeed('Greeting ready!');
    console.log(greeting);
}
```

5. **Install and test:**
```bash
# Install dependencies and create global link
./setup.sh --dev

# Test your CLI
awesome greet "World" --style excited

# Launch interactive mode (if generated with --universal-templates)
awesome --interactive
```

## Understanding the Architecture

### How Goobits Works with Node.js

Goobits generates a complete Node.js CLI project using Commander.js, the de facto standard for Node.js CLI applications. Here's the flow:

```
goobits.yaml → Goobits Build → Generated CLI Structure → Your Hooks → Working CLI
```

### Generated Project Structure

```
your-cli/
├── index.js              # Main CLI logic with Commander.js setup
├── package.json          # npm package manifest
├── bin/
│   └── cli.js           # Executable entry point (#!/usr/bin/env node)
├── lib/
│   └── config.js        # Configuration management utilities
├── app_hooks.js         # Your business logic implementation
├── commands/            # Optional: dynamically loaded commands
├── test/
│   └── cli.test.js      # Basic test setup
├── setup.sh             # Smart installation script
├── README.md            # Generated documentation
├── .gitignore           # Node.js specific ignores
└── .npmignore           # npm publish ignores
```

### Key Components

**1. index.js - The CLI Engine**
- Sets up Commander.js with your command structure
- Loads and validates configurations
- Calls your hook functions
- Handles errors gracefully

**2. app_hooks.js - Your Business Logic**
- Contains functions for each command
- Receives parsed arguments and options
- Can be async for complex operations
- Full access to any npm packages

**3. lib/config.js - Configuration Management**
- Loads config from multiple sources
- Supports .rc files (JSON/YAML)
- Environment variable overrides
- User preferences storage

## Configuration Guide

### Complete goobits.yaml Reference

```yaml
# Language selection
language: nodejs          # Use 'typescript' for TypeScript

# Package metadata
package_name: my-cli      # npm package name
command_name: mycli       # Command users type
display_name: "My CLI"    # Human-readable name
description: "What your CLI does"

# Node.js specific settings
installation:
  extras:
    npm:              # npm dependencies to include
      - "commander@11.1.0"     # Already included by default
      - "chalk@5.3.0"          # Terminal colors
      - "ora@8.0.1"           # Progress spinners
      - "inquirer@9.2.15"      # Interactive prompts
      - "axios@1.6.5"          # HTTP client
      - "dotenv@16.3.1"        # Environment variables
      - "yargs@17.7.2"        # Alternative CLI parser
      - "conf@12.0.0"         # Simple config storage

# Required for all projects
python:
  minimum_version: "3.8"  # Required even for Node.js

dependencies:
  python: []              # Keep empty for Node.js

# Shell integration
shell_integration:
  enable_completion: true
  alias: mycli

# Validation settings
validation:
  check_disk_space: true
  minimum_disk_space_mb: 100

# Post-installation messages
messages:
  install_success: |
    🎉 My CLI installed successfully!
    Try: mycli --help

# CLI Structure
cli:
  name: mycli
  tagline: "Short description for help"
  version: "1.0.0"        # npm package version
  
  # Global options (available to all commands)
  options:
    - name: config
      short: c
      desc: "Config file location"
      type: str
    - name: verbose
      short: v
      desc: "Verbose output"
      type: flag
  
  # Command definitions
  commands:
    # Simple command
    init:
      desc: "Initialize a new project"
      args:
        - name: project-name
          desc: "Name of the project"
          required: true
      options:
        - name: template
          short: t
          desc: "Project template"
          choices: ["basic", "advanced", "minimal"]
          default: "basic"
    
    # Command with subcommands
    config:
      desc: "Manage configuration"
      subcommands:
        get:
          desc: "Get a config value"
          args:
            - name: key
              desc: "Config key"
              required: true
        
        set:
          desc: "Set a config value"
          args:
            - name: key
              desc: "Config key"
              required: true
            - name: value
              desc: "Config value"
              required: true
        
        list:
          desc: "List all config values"
          options:
            - name: format
              desc: "Output format"
              choices: ["json", "table"]
              default: "table"
    
    # Command with complex options
    deploy:
      desc: "Deploy your application"
      args:
        - name: environment
          desc: "Target environment"
          required: true
          choices: ["dev", "staging", "prod"]
      options:
        - name: dry-run
          desc: "Show what would be deployed"
          type: flag
        - name: force
          short: f
          desc: "Force deployment"
          type: flag
        - name: timeout
          desc: "Deployment timeout in seconds"
          type: int
          default: 300
```

### Option Types

Goobits supports several option types:

- **flag**: Boolean true/false (`--verbose`)
- **str**: String value (`--name "John"`)
- **int**: Integer value (`--port 3000`)
- **float**: Decimal value (`--rate 0.5`)
- **count**: Incremental counter (`-vvv` for verbosity)

## Working with app_hooks.js

### Hook Function Naming Convention

Hooks follow a predictable naming pattern:

- **Simple commands**: `on{CommandName}`
  - `greet` → `onGreet`
  - `deploy` → `onDeploy`

- **Subcommands**: `on{ParentCommand}{SubCommand}`
  - `config get` → `onConfigGet`
  - `config set` → `onConfigSet`

### Hook Function Signature

All hook functions receive a single `args` object:

```javascript
export async function onCommandName(args) {
    // args contains:
    // - All command arguments by name
    // - All options (both command-specific and global)
    // - Special properties: commandName, rawArgs
}
```

### Complete app_hooks.js Example

```javascript
// app_hooks.js
import chalk from 'chalk';
import ora from 'ora';
import inquirer from 'inquirer';
import { promises as fs } from 'fs';
import path from 'path';
import axios from 'axios';

// Simple command implementation
export async function onInit(args) {
    const { projectName, template, verbose } = args;
    
    console.log(chalk.blue(`Creating new project: ${projectName}`));
    
    if (verbose) {
        console.log(`Using template: ${template}`);
    }
    
    // Create project directory
    const projectPath = path.join(process.cwd(), projectName);
    await fs.mkdir(projectPath, { recursive: true });
    
    // Create basic files based on template
    const files = getTemplateFiles(template);
    
    const spinner = ora('Creating project files...').start();
    
    for (const [filename, content] of Object.entries(files)) {
        await fs.writeFile(
            path.join(projectPath, filename),
            content
        );
    }
    
    spinner.succeed('Project created successfully!');
    
    console.log(chalk.green(`
✨ Project ${projectName} created!

Next steps:
  cd ${projectName}
  npm install
  npm start
`));
}

// Subcommand implementation
export async function onConfigGet(args) {
    const { key, config: configPath } = args;
    
    // Load configuration
    const configFile = configPath || '.myapp.json';
    
    try {
        const data = await fs.readFile(configFile, 'utf8');
        const config = JSON.parse(data);
        
        if (key in config) {
            console.log(`${key}: ${config[key]}`);
        } else {
            console.error(chalk.red(`Key '${key}' not found`));
            process.exit(1);
        }
    } catch (error) {
        console.error(chalk.red('Config file not found'));
        process.exit(1);
    }
}

export async function onConfigSet(args) {
    const { key, value, config: configPath } = args;
    
    const configFile = configPath || '.myapp.json';
    let config = {};
    
    // Load existing config
    try {
        const data = await fs.readFile(configFile, 'utf8');
        config = JSON.parse(data);
    } catch (error) {
        // Config doesn't exist yet
    }
    
    // Set value
    config[key] = value;
    
    // Save config
    await fs.writeFile(
        configFile,
        JSON.stringify(config, null, 2)
    );
    
    console.log(chalk.green(`✓ Set ${key} = ${value}`));
}

// Interactive command with prompts
export async function onDeploy(args) {
    const { environment, dryRun, force, timeout, verbose } = args;
    
    console.log(chalk.blue(`Deploying to ${environment}...`));
    
    // Confirmation for production
    if (environment === 'prod' && !force && !dryRun) {
        const { confirmed } = await inquirer.prompt([{
            type: 'confirm',
            name: 'confirmed',
            message: 'Deploy to PRODUCTION? This cannot be undone!',
            default: false
        }]);
        
        if (!confirmed) {
            console.log(chalk.yellow('Deployment cancelled'));
            return;
        }
    }
    
    if (dryRun) {
        console.log(chalk.yellow('DRY RUN - No actual deployment'));
    }
    
    const spinner = ora('Preparing deployment...').start();
    
    try {
        // Simulate deployment steps
        await sleep(1000);
        spinner.text = 'Building application...';
        await sleep(1500);
        spinner.text = 'Uploading files...';
        await sleep(2000);
        spinner.text = 'Running health checks...';
        await sleep(1000);
        
        if (dryRun) {
            spinner.info('Dry run completed');
        } else {
            spinner.succeed(`Deployed to ${environment} successfully!`);
        }
        
        // Show deployment URL
        const url = getDeploymentUrl(environment);
        console.log(chalk.green(`\n🚀 Application deployed to: ${url}`));
        
    } catch (error) {
        spinner.fail(`Deployment failed: ${error.message}`);
        process.exit(1);
    }
}

// Helper functions
function getTemplateFiles(template) {
    const base = {
        'package.json': JSON.stringify({
            name: 'my-project',
            version: '1.0.0',
            type: 'module'
        }, null, 2),
        'index.js': 'console.log("Hello from your new project!");'
    };
    
    if (template === 'advanced') {
        base['src/app.js'] = '// Your application code here';
        base['.gitignore'] = 'node_modules/\n.env';
    }
    
    return base;
}

function getDeploymentUrl(env) {
    const urls = {
        dev: 'https://dev.myapp.com',
        staging: 'https://staging.myapp.com',
        prod: 'https://myapp.com'
    };
    return urls[env];
}

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}
```

### Error Handling in Hooks

Always handle errors gracefully:

```javascript
export async function onApiCall(args) {
    const { endpoint, method = 'GET' } = args;
    
    try {
        const response = await axios({
            method,
            url: endpoint,
            timeout: 5000
        });
        
        console.log(JSON.stringify(response.data, null, 2));
        
    } catch (error) {
        if (error.code === 'ECONNREFUSED') {
            console.error(chalk.red('❌ Connection refused. Is the server running?'));
        } else if (error.response) {
            console.error(chalk.red(`❌ HTTP ${error.response.status}: ${error.response.statusText}`));
        } else {
            console.error(chalk.red(`❌ Error: ${error.message}`));
        }
        
        process.exit(1);
    }
}
```

### Working with Async Operations

All hooks can be async:

```javascript
export async function onBackup(args) {
    const { source, destination } = args;
    
    // Multiple async operations
    const spinner = ora('Starting backup...').start();
    
    try {
        // Check source exists
        spinner.text = 'Checking source...';
        await fs.access(source);
        
        // Create destination
        spinner.text = 'Preparing destination...';
        await fs.mkdir(destination, { recursive: true });
        
        // Copy files
        spinner.text = 'Copying files...';
        await copyDirectory(source, destination);
        
        // Verify backup
        spinner.text = 'Verifying backup...';
        const verified = await verifyBackup(source, destination);
        
        if (verified) {
            spinner.succeed('Backup completed successfully!');
        } else {
            throw new Error('Backup verification failed');
        }
        
    } catch (error) {
        spinner.fail(`Backup failed: ${error.message}`);
        process.exit(1);
    }
}
```

## TypeScript Development

### Setting Up TypeScript

1. **Use `language: typescript` in goobits.yaml:**
```yaml
language: typescript  # Instead of nodejs
package_name: my-ts-cli
# ... rest of configuration
```

2. **Generated TypeScript structure:**
```
my-ts-cli/
├── index.ts          # TypeScript entry point
├── package.json      # Includes TypeScript dependencies
├── tsconfig.json     # TypeScript configuration
├── bin/
│   └── cli.js        # JavaScript wrapper
├── lib/
│   └── config.ts     # TypeScript config utilities
├── app_hooks.ts      # Your TypeScript hooks
└── dist/             # Compiled JavaScript (after build)
```

3. **TypeScript app_hooks.ts:**
```typescript
// app_hooks.ts
import chalk from 'chalk';
import ora from 'ora';

interface GreetArgs {
    name: string;
    style?: 'friendly' | 'formal' | 'excited';
    verbose?: boolean;
    // Global options
    config?: string;
}

export async function onGreet(args: GreetArgs): Promise<void> {
    const { name, style = 'friendly', verbose } = args;
    
    if (verbose) {
        console.log(chalk.gray(`Greeting ${name} with ${style} style`));
    }
    
    const messages: Record<string, string> = {
        friendly: chalk.green(`Hello ${name}! 👋`),
        formal: chalk.blue(`Good day, ${name}.`),
        excited: chalk.yellow.bold(`🎉 HEY ${name.toUpperCase()}! 🎉`)
    };
    
    console.log(messages[style]);
}

// TypeScript enables better IDE support and type safety
interface ConfigGetArgs {
    key: string;
    config?: string;
}

export async function onConfigGet(args: ConfigGetArgs): Promise<void> {
    // Implementation with full type safety
}
```

### TypeScript Configuration

Generated `tsconfig.json`:
```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "NodeNext",
    "moduleResolution": "NodeNext",
    "lib": ["ES2022"],
    "outDir": "./dist",
    "rootDir": "./",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "resolveJsonModule": true,
    "declaration": true,
    "declarationMap": true
  },
  "include": ["**/*.ts"],
  "exclude": ["node_modules", "dist"]
}
```

### Building and Running TypeScript CLIs

```bash
# Development (watches for changes)
npm run dev

# Build for production
npm run build

# Run directly with ts-node
npm start

# After building
node dist/index.js
```

## Advanced Features

### 1. Configuration Management

The generated `lib/config.js` provides powerful configuration:

```javascript
// In your hooks
import { loadConfig, saveConfig } from './lib/config.js';

export async function onInit(args) {
    // Load existing config
    const config = await loadConfig();
    
    // Update config
    config.lastProject = args.projectName;
    config.projectCount = (config.projectCount || 0) + 1;
    
    // Save config
    await saveConfig(config);
}
```

Configuration search order:
1. `.myapprc` in current directory
2. `.myapprc.json` in current directory
3. `.myapprc.yaml` in current directory
4. `~/.config/myapp/config.json`
5. Environment variables (MYAPP_CONFIG)

### 2. Plugin System

Create a plugin architecture:

```javascript
// In app_hooks.js
import { promises as fs } from 'fs';
import path from 'path';

const PLUGIN_DIR = path.join(process.cwd(), 'plugins');

async function loadPlugins() {
    const plugins = [];
    
    try {
        const files = await fs.readdir(PLUGIN_DIR);
        
        for (const file of files) {
            if (file.endsWith('.js')) {
                const plugin = await import(path.join(PLUGIN_DIR, file));
                plugins.push(plugin);
            }
        }
    } catch (error) {
        // No plugins directory
    }
    
    return plugins;
}

export async function onRunWithPlugins(args) {
    const plugins = await loadPlugins();
    
    // Run plugins
    for (const plugin of plugins) {
        if (plugin.beforeCommand) {
            await plugin.beforeCommand(args);
        }
    }
    
    // Your command logic
    console.log('Running command...');
    
    // Run plugin post-hooks
    for (const plugin of plugins) {
        if (plugin.afterCommand) {
            await plugin.afterCommand(args);
        }
    }
}
```

### 3. Progress and Animations

Create rich terminal UIs:

```javascript
import ora from 'ora';
import chalk from 'chalk';

export async function onLongTask(args) {
    const tasks = [
        { name: 'Downloading files', duration: 2000 },
        { name: 'Processing data', duration: 3000 },
        { name: 'Generating report', duration: 1500 },
        { name: 'Cleaning up', duration: 500 }
    ];
    
    console.log(chalk.blue.bold('Starting long operation...\n'));
    
    for (const [index, task] of tasks.entries()) {
        const spinner = ora({
            text: task.name,
            prefixText: chalk.gray(`[${index + 1}/${tasks.length}]`)
        }).start();
        
        // Simulate work
        await new Promise(resolve => setTimeout(resolve, task.duration));
        
        spinner.succeed(chalk.green(task.name));
    }
    
    console.log(chalk.green.bold('\n✨ All tasks completed!'));
}
```

### 4. Interactive Prompts

Build interactive CLIs with inquirer:

```javascript
import inquirer from 'inquirer';

export async function onInteractiveSetup(args) {
    const answers = await inquirer.prompt([
        {
            type: 'input',
            name: 'projectName',
            message: 'What is your project name?',
            default: 'my-project',
            validate: (input) => {
                if (/^[a-z0-9-]+$/.test(input)) return true;
                return 'Project name must be lowercase with hyphens only';
            }
        },
        {
            type: 'list',
            name: 'language',
            message: 'Choose your language:',
            choices: ['JavaScript', 'TypeScript', 'Both'],
            default: 'TypeScript'
        },
        {
            type: 'checkbox',
            name: 'features',
            message: 'Select features to include:',
            choices: [
                { name: 'ESLint', value: 'eslint', checked: true },
                { name: 'Prettier', value: 'prettier', checked: true },
                { name: 'Jest Testing', value: 'jest' },
                { name: 'GitHub Actions', value: 'github-actions' }
            ]
        },
        {
            type: 'confirm',
            name: 'installDeps',
            message: 'Install dependencies now?',
            default: true
        }
    ]);
    
    // Use the answers
    console.log(chalk.blue('Creating project with:'));
    console.log(answers);
}
```

### 5. HTTP Client Integration

Build API clients:

```javascript
import axios from 'axios';
import chalk from 'chalk';

export async function onApiStatus(args) {
    const { endpoint, verbose } = args;
    
    const spinner = ora('Checking API status...').start();
    
    try {
        const start = Date.now();
        const response = await axios.get(endpoint, {
            timeout: 5000,
            validateStatus: () => true // Don't throw on any status
        });
        const duration = Date.now() - start;
        
        spinner.stop();
        
        // Status indicator
        const statusColor = response.status < 400 ? chalk.green : chalk.red;
        console.log(statusColor(`● ${response.status} ${response.statusText}`));
        
        if (verbose) {
            console.log(chalk.gray(`Response time: ${duration}ms`));
            console.log(chalk.gray(`Server: ${response.headers.server || 'Unknown'}`));
        }
        
        // Show body for non-200 responses
        if (response.status >= 400) {
            console.log(chalk.red('\nError response:'));
            console.log(response.data);
        }
        
    } catch (error) {
        spinner.fail(chalk.red('Failed to reach API'));
        console.error(error.message);
        process.exit(1);
    }
}
```

## Testing Your CLI

### Basic Test Setup

Goobits generates a basic test file. Enhance it:

```javascript
// test/cli.test.js
import { describe, it } from 'node:test';
import assert from 'node:assert';
import { spawn } from 'child_process';
import path from 'path';

const CLI_PATH = path.join(process.cwd(), 'bin/cli.js');

describe('CLI Tests', () => {
    it('should display help', async () => {
        const result = await runCLI(['--help']);
        assert.match(result.stdout, /Usage:/);
        assert.equal(result.code, 0);
    });
    
    it('should greet with name', async () => {
        const result = await runCLI(['greet', 'World']);
        assert.match(result.stdout, /Hello World/);
        assert.equal(result.code, 0);
    });
    
    it('should handle missing required args', async () => {
        const result = await runCLI(['greet']);
        assert.match(result.stderr, /required/i);
        assert.notEqual(result.code, 0);
    });
    
    it('should respect style option', async () => {
        const result = await runCLI(['greet', 'World', '--style', 'formal']);
        assert.match(result.stdout, /Good day/);
    });
});

function runCLI(args) {
    return new Promise((resolve) => {
        const proc = spawn('node', [CLI_PATH, ...args]);
        let stdout = '';
        let stderr = '';
        
        proc.stdout.on('data', (data) => { stdout += data; });
        proc.stderr.on('data', (data) => { stderr += data; });
        
        proc.on('close', (code) => {
            resolve({ stdout, stderr, code });
        });
    });
}
```

### Testing Hooks Directly

```javascript
// test/hooks.test.js
import { describe, it, beforeEach, afterEach } from 'node:test';
import assert from 'node:assert';
import { onGreet, onConfigSet } from '../app_hooks.js';
import fs from 'fs/promises';

describe('Hook Tests', () => {
    describe('onGreet', () => {
        it('should greet with default style', async () => {
            // Mock console.log
            const logs = [];
            const originalLog = console.log;
            console.log = (...args) => logs.push(args.join(' '));
            
            await onGreet({ name: 'Test', style: 'friendly' });
            
            console.log = originalLog;
            assert.match(logs.join(''), /Hello Test/);
        });
    });
    
    describe('onConfigSet', () => {
        const testConfig = '.test-config.json';
        
        afterEach(async () => {
            try {
                await fs.unlink(testConfig);
            } catch {}
        });
        
        it('should save config values', async () => {
            await onConfigSet({
                key: 'testKey',
                value: 'testValue',
                config: testConfig
            });
            
            const data = await fs.readFile(testConfig, 'utf8');
            const config = JSON.parse(data);
            
            assert.equal(config.testKey, 'testValue');
        });
    });
});
```

### Integration Testing

```javascript
// test/integration.test.js
import { describe, it } from 'node:test';
import assert from 'node:assert';
import { spawn } from 'child_process';
import fs from 'fs/promises';
import path from 'path';

describe('Integration Tests', () => {
    it('should create and configure a project', async () => {
        const projectName = `test-project-${Date.now()}`;
        
        // Run init command
        let result = await runCLI(['init', projectName, '--template', 'basic']);
        assert.equal(result.code, 0);
        
        // Verify project created
        const projectPath = path.join(process.cwd(), projectName);
        const stats = await fs.stat(projectPath);
        assert(stats.isDirectory());
        
        // Clean up
        await fs.rm(projectPath, { recursive: true });
    });
});
```

## Publishing to npm

### 1. Prepare for Publishing

Update your `package.json`:
```json
{
  "name": "@yourscope/my-cli",
  "version": "1.0.0",
  "description": "My awesome CLI tool",
  "keywords": ["cli", "tool", "awesome"],
  "homepage": "https://github.com/yourusername/my-cli",
  "bugs": {
    "url": "https://github.com/yourusername/my-cli/issues"
  },
  "repository": {
    "type": "git",
    "url": "git+https://github.com/yourusername/my-cli.git"
  },
  "files": [
    "bin/",
    "lib/",
    "index.js",
    "app_hooks.js"
  ],
  "engines": {
    "node": ">=18.0.0"
  }
}
```

### 2. Add Pre-publish Scripts

```json
{
  "scripts": {
    "prepublishOnly": "npm test && npm run lint",
    "lint": "eslint .",
    "test": "node --test"
  }
}
```

### 3. Create .npmignore

```
# .npmignore
src/
tests/
docs/
.env
.env.*
*.log
.DS_Store
coverage/
.nyc_output/
```

### 4. Publish Process

```bash
# Login to npm
npm login

# Test what will be published
npm pack --dry-run

# Publish
npm publish

# For scoped packages
npm publish --access public
```

### 5. Installation Instructions

After publishing, users can install:
```bash
# Global installation
npm install -g @yourscope/my-cli

# Or use npx
npx @yourscope/my-cli greet World
```

## Real-World Examples

### 1. Git-Style CLI

```yaml
# goobits.yaml
language: nodejs
package_name: gitlike-cli
command_name: gitlike

cli:
  name: gitlike
  tagline: "Git-style command structure"
  commands:
    init:
      desc: "Initialize a new repository"
      options:
        - name: bare
          desc: "Create a bare repository"
          type: flag
    
    add:
      desc: "Add files to staging"
      args:
        - name: files
          desc: "Files to add"
          required: true
          nargs: "*"  # Accept multiple files
    
    commit:
      desc: "Commit changes"
      options:
        - name: message
          short: m
          desc: "Commit message"
          required: true
    
    push:
      desc: "Push to remote"
      args:
        - name: remote
          desc: "Remote name"
          default: "origin"
        - name: branch
          desc: "Branch name"
          default: "main"
```

### 2. Database Migration Tool

```yaml
# goobits.yaml
language: typescript
package_name: db-migrate
command_name: migrate

installation:
  extras:
    npm:
      - "pg@8.11.3"
      - "mysql2@3.6.5"
      - "sqlite3@5.1.6"

cli:
  name: migrate
  commands:
    create:
      desc: "Create a new migration"
      args:
        - name: name
          desc: "Migration name"
          required: true
    
    up:
      desc: "Run pending migrations"
      options:
        - name: steps
          desc: "Number of migrations to run"
          type: int
        - name: dry-run
          desc: "Show SQL without executing"
          type: flag
    
    down:
      desc: "Rollback migrations"
      options:
        - name: steps
          desc: "Number to rollback"
          type: int
          default: 1
    
    status:
      desc: "Show migration status"
      options:
        - name: format
          choices: ["table", "json"]
          default: "table"
```

### 3. API Testing Tool

```yaml
# goobits.yaml
language: nodejs
package_name: api-tester
command_name: apitest

installation:
  extras:
    npm:
      - "axios@1.6.5"
      - "chalk@5.3.0"
      - "cli-table3@0.6.3"

cli:
  name: apitest
  commands:
    run:
      desc: "Run API tests"
      args:
        - name: suite
          desc: "Test suite to run"
          required: true
      options:
        - name: env
          short: e
          desc: "Environment"
          choices: ["local", "dev", "staging", "prod"]
          default: "local"
        - name: parallel
          short: p
          desc: "Run tests in parallel"
          type: flag
    
    list:
      desc: "List available test suites"
    
    report:
      desc: "Generate test report"
      options:
        - name: format
          choices: ["html", "json", "junit"]
          default: "html"
        - name: output
          short: o
          desc: "Output file"
```

## Troubleshooting

### Common Issues and Solutions

#### 1. "Command not found" after installation

**Problem**: CLI isn't available globally after running `./setup.sh --dev`

**Solution**:
```bash
# Check if npm global bin is in PATH
npm bin -g

# Add to PATH if needed (add to ~/.bashrc or ~/.zshrc)
export PATH="$PATH:$(npm bin -g)"

# Or use npm link directly
npm link
```

#### 2. "Cannot find module" errors

**Problem**: Import errors when running the CLI

**Solution**:
```bash
# Ensure all dependencies are installed
npm install

# For TypeScript, ensure it's built
npm run build

# Check node_modules exists
ls -la node_modules/
```

#### 3. Hook function not being called

**Problem**: Your hook function isn't executing

**Checklist**:
1. Verify function name matches pattern (`onCommandName`)
2. Ensure function is exported
3. Check for typos in command name
4. Verify app_hooks.js is in project root

```javascript
// Debugging hook
export async function onMyCommand(args) {
    console.log('Hook called with args:', args);
    // Your logic
}
```

#### 4. TypeScript compilation errors

**Problem**: TypeScript won't compile

**Common fixes**:
```bash
# Clear build artifacts
rm -rf dist/

# Check TypeScript version
npx tsc --version

# Reinstall dependencies
rm -rf node_modules package-lock.json
npm install

# Build with verbose output
npx tsc --listFiles
```

#### 5. Permission denied when running CLI

**Problem**: Can't execute the CLI command

**Solution**:
```bash
# Make bin file executable
chmod +x bin/cli.js

# Or reinstall
npm unlink
npm link
```

### Debug Mode

Add debug output to your hooks:

```javascript
const DEBUG = process.env.DEBUG === 'true';

export async function onCommand(args) {
    if (DEBUG) {
        console.log('[DEBUG] Command called with:', JSON.stringify(args, null, 2));
        console.log('[DEBUG] Current directory:', process.cwd());
        console.log('[DEBUG] Environment:', process.env.NODE_ENV);
    }
    
    // Your logic
}

// Run with: DEBUG=true mycli command
```

### Getting Help

1. **Check generated files**: Look at the generated code to understand the structure
2. **Enable verbose mode**: Add `--verbose` to see more output
3. **Check examples**: Look at the generated README.md for usage examples
4. **File issues**: Report bugs at the Goobits CLI repository

## Best Practices

### 1. Structure Your Hooks

Organize complex CLIs:

```javascript
// app_hooks.js
import { initCommand } from './commands/init.js';
import { deployCommand } from './commands/deploy.js';
import { configCommands } from './commands/config.js';

// Re-export organized commands
export const onInit = initCommand;
export const onDeploy = deployCommand;
export const { onConfigGet, onConfigSet } = configCommands;
```

### 2. Use Environment Variables

```javascript
// Support .env files
import dotenv from 'dotenv';
dotenv.config();

export async function onApiCall(args) {
    const apiKey = process.env.API_KEY || args.apiKey;
    
    if (!apiKey) {
        console.error(chalk.red('API key required. Set API_KEY or use --api-key'));
        process.exit(1);
    }
    
    // Use API key
}
```

### 3. Provide Helpful Error Messages

```javascript
export async function onProcess(args) {
    const { input, output } = args;
    
    try {
        await processFile(input, output);
    } catch (error) {
        if (error.code === 'ENOENT') {
            console.error(chalk.red(`❌ File not found: ${input}`));
            console.error(chalk.yellow('\nTip: Check the file path and try again'));
        } else if (error.code === 'EACCES') {
            console.error(chalk.red(`❌ Permission denied: ${output}`));
            console.error(chalk.yellow('\nTip: Check file permissions or use sudo'));
        } else {
            console.error(chalk.red(`❌ Unexpected error: ${error.message}`));
        }
        
        process.exit(1);
    }
}
```

### 4. Add Progress for Long Operations

```javascript
export async function onBackup(args) {
    const { source, destination } = args;
    
    // For determinate progress
    const files = await getFileList(source);
    const progressBar = new cliProgress.SingleBar({}, cliProgress.Presets.shades_classic);
    
    progressBar.start(files.length, 0);
    
    for (const [index, file] of files.entries()) {
        await copyFile(file, destination);
        progressBar.update(index + 1);
    }
    
    progressBar.stop();
    console.log(chalk.green('✓ Backup completed'));
}
```

### 5. Support Both CLI and Programmatic Use

```javascript
// Make your hooks reusable
export async function onProcess(args) {
    const result = await processCore(args);
    console.log(result);
    return result;
}

// Core logic that can be imported
export async function processCore({ input, output, format }) {
    // Processing logic
    return { success: true, processed: 42 };
}

// Now others can: import { processCore } from 'your-cli/app_hooks.js'
```

## Conclusion

Goobits CLI makes it incredibly easy to create professional Node.js and TypeScript command-line tools. With automatic project setup, Commander.js integration, and a simple hook system, you can focus on your business logic while Goobits handles the CLI infrastructure.

Key takeaways:
- Start simple with basic commands and grow complexity as needed
- Use TypeScript for better IDE support and type safety
- Leverage the npm ecosystem for rich terminal UIs
- Test your CLI thoroughly before publishing
- Follow Node.js best practices for async operations

Happy CLI building! 🚀