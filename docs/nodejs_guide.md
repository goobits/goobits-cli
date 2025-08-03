# Node.js and TypeScript CLI Development with Goobits

Welcome to the complete guide for building Node.js and TypeScript command-line applications with Goobits CLI. This document covers everything you need to know to leverage Goobits' powerful multi-language capabilities.

## Table of Contents

1. [Introduction](#introduction)
2. [Getting Started](#getting-started)
3. [Configuration Reference](#configuration-reference)
4. [The Hook System](#the-hook-system)
5. [TypeScript Support](#typescript-support)
6. [Testing](#testing)
7. [Deployment](#deployment)
8. [Advanced Features](#advanced-features)
9. [Migration Guide](#migration-guide)

## Introduction

Goobits CLI brings the same powerful YAML-driven configuration approach to Node.js and TypeScript that has made it popular in the Python ecosystem. When you choose Node.js or TypeScript as your target language, Goobits generates:

- **Modern Commander.js CLIs** - Industry-standard Node.js CLI framework
- **Complete npm package structure** - Ready for publishing to npm registry
- **Professional TypeScript setup** - Full type safety with modern tooling
- **Integrated testing framework** - Jest-based testing out of the box
- **Cross-platform compatibility** - Works on Windows, macOS, and Linux

### Benefits of Goobits for Node.js/TypeScript

- **Zero Configuration** - No webpack, babel, or complex build setup required
- **Best Practices Built-in** - Following Node.js CLI conventions automatically
- **Type Safety** - Full TypeScript support with proper type definitions
- **Rich Terminal Interface** - Colored output, help formatting, and progress indicators
- **Automatic Pipe Support** - stdin/stdout handling works seamlessly
- **Professional Structure** - Generated code follows industry standards

## Getting Started

### Prerequisites

- Node.js 16+ and npm/yarn
- Goobits CLI installed (`pipx install goobits-cli`)

### Creating Your First Node.js CLI

Let's build a text processing CLI to demonstrate the capabilities:

```bash
mkdir text-processor
cd text-processor

# Create the configuration
cat > goobits.yaml << 'EOF'
language: nodejs
package_name: text-processor
command_name: textproc
display_name: "Text Processor"
description: "A powerful text processing CLI built with Goobits"
version: "1.0.0"

dependencies:
  npm_packages: 
    - commander@^9.0.0
    - chalk@^5.0.0

cli:
  name: textproc
  tagline: "Process text files with ease"
  commands:
    process:
      desc: "Process text input"
      is_default: true
      args:
        - name: text
          desc: "Text to process"
          nargs: "*"
      options:
        - name: uppercase
          short: u
          type: flag
          desc: "Convert to uppercase"
        - name: reverse
          short: r
          type: flag
          desc: "Reverse the text"
        - name: output
          short: o
          desc: "Output file"
    stats:
      desc: "Get text statistics"
      args:
        - name: text
          desc: "Text to analyze"
          nargs: "*"
EOF
```

### Generate the CLI

```bash
goobits build
```

This creates:
- `index.js` - Main CLI entry point
- `package.json` - npm package configuration
- `bin/cli.js` - Executable wrapper
- `app_hooks.js` - Your business logic goes here
- `commands/` - Generated command modules
- `lib/` - Utility libraries
- `test/` - Test framework setup

### Add Your Business Logic

Create the hook functions in `app_hooks.js`:

```javascript
const chalk = require('chalk');
const fs = require('fs');

function onProcess(text, options) {
    // Handle stdin input automatically
    if (!text || text.length === 0) {
        if (!process.stdin.isTTY) {
            // Read from stdin
            let input = '';
            process.stdin.setEncoding('utf8');
            process.stdin.on('data', chunk => input += chunk);
            process.stdin.on('end', () => {
                processText([input.trim()], options);
            });
            return;
        } else {
            console.error(chalk.red('Error: No text provided'));
            process.exit(1);
        }
    }
    
    processText(text, options);
}

function processText(textArray, options) {
    let content = textArray.join(' ');
    
    if (options.uppercase) {
        content = content.toUpperCase();
    }
    
    if (options.reverse) {
        content = content.split('').reverse().join('');
    }
    
    if (options.output) {
        fs.writeFileSync(options.output, content);
        console.log(chalk.green(`✅ Written to ${options.output}`));
    } else {
        console.log(content);
    }
}

function onStats(text, options) {
    if (!text || text.length === 0) {
        console.error(chalk.red('Error: No text provided'));
        return;
    }
    
    const content = text.join(' ');
    const stats = {
        characters: content.length,
        words: content.split(/\s+/).filter(w => w.length > 0).length,
        lines: content.split('\n').length,
        paragraphs: content.split(/\n\s*\n/).filter(p => p.trim().length > 0).length
    };
    
    console.log(chalk.blue('📊 Text Statistics:'));
    console.log(`Characters: ${chalk.yellow(stats.characters)}`);
    console.log(`Words: ${chalk.yellow(stats.words)}`);
    console.log(`Lines: ${chalk.yellow(stats.lines)}`);
    console.log(`Paragraphs: ${chalk.yellow(stats.paragraphs)}`);
}

module.exports = { onProcess, onStats };
```

### Install and Test

```bash
# Install dependencies
npm install

# Make CLI available globally (for development)
npm link

# Test your CLI
textproc "Hello World" --uppercase
textproc "Hello World" --reverse
echo "This is piped input" | textproc --uppercase
textproc stats "The quick brown fox jumps over the lazy dog"
```

## Configuration Reference

### Node.js Specific Configuration

```yaml
language: nodejs  # or typescript

# Package metadata (used in package.json)
package_name: my-awesome-cli
command_name: awesome
display_name: "Awesome CLI"
description: "An awesome command-line tool"
version: "1.0.0"
author: "Your Name <your.email@example.com>"
license: "MIT"
homepage: "https://github.com/yourname/awesome-cli"

# Node.js dependencies
dependencies:
  npm_packages:
    - commander@^9.0.0    # CLI framework
    - chalk@^5.0.0        # Colored output
    - inquirer@^8.0.0     # Interactive prompts
    - axios@^0.27.0       # HTTP client

# Development dependencies (automatically added)
dev_dependencies:
  npm_packages:
    - jest@^28.0.0
    - @types/node@^18.0.0

# npm registry configuration
npm:
  registry: "https://registry.npmjs.org/"
  scope: "@yourorg"  # for scoped packages
```

### Command Configuration

```yaml
cli:
  name: awesome
  tagline: "An awesome command-line tool"
  commands:
    process:
      desc: "Process input"
      is_default: true  # Default command when no command specified
      args:
        - name: input
          desc: "Input to process"
          nargs: "*"        # Accept multiple arguments
          required: false
      options:
        - name: config
          short: c
          desc: "Configuration file"
          type: str
        - name: verbose
          short: v
          desc: "Verbose output"
          type: flag         # Boolean flag
        - name: format
          short: f
          desc: "Output format"
          choices: ["json", "yaml", "text"]
          default: "text"
        - name: count
          short: n
          desc: "Number of items"
          type: int
          default: 10
```

### Advanced Package Configuration

```yaml
# Publishing configuration
npm:
  publishConfig:
    registry: "https://npm.yourcompany.com/"
    access: "restricted"
  
  # Package.json fields
  keywords: 
    - cli
    - tool
    - automation
  
  repository:
    type: git
    url: "https://github.com/yourname/awesome-cli.git"
  
  bugs:
    url: "https://github.com/yourname/awesome-cli/issues"
  
  engines:
    node: ">=16.0.0"
    npm: ">=8.0.0"

# Binary configuration
bin:
  awesome: "./bin/cli.js"
  awesome-admin: "./bin/admin.js"  # Multiple binaries
```

## The Hook System

The hook system is where your business logic lives. Goobits generates the CLI structure, and you implement the actual functionality in hook functions.

### Hook Function Naming

Hook functions follow the pattern `on{CommandName}`:

```javascript
// For command 'process'
function onProcess(args..., options) { }

// For command 'deploy'
function onDeploy(args..., options) { }

// For command 'user-create' (kebab-case becomes camelCase)
function onUserCreate(args..., options) { }
```

### Hook Function Signature

```javascript
function onCommandName(arg1, arg2, ..., options) {
    // arg1, arg2, etc. are positional arguments in order
    // options is an object containing all flags/options
    
    // Return values are optional but can be used for testing
    return result;
}
```

### Complete Hook Examples

#### File Processing CLI

```javascript
const fs = require('fs');
const path = require('path');
const chalk = require('chalk');

function onConvert(inputFile, options) {
    if (!fs.existsSync(inputFile)) {
        console.error(chalk.red(`❌ File not found: ${inputFile}`));
        process.exit(1);
    }
    
    const content = fs.readFileSync(inputFile, 'utf8');
    let result;
    
    switch (options.format) {
        case 'json':
            result = JSON.stringify({ content }, null, 2);
            break;
        case 'base64':
            result = Buffer.from(content).toString('base64');
            break;
        default:
            result = content.toUpperCase();
    }
    
    if (options.output) {
        fs.writeFileSync(options.output, result);
        console.log(chalk.green(`✅ Converted ${inputFile} → ${options.output}`));
    } else {
        console.log(result);
    }
    
    return { success: true, outputFile: options.output };
}

function onBatch(directory, options) {
    const files = fs.readdirSync(directory)
        .filter(file => path.extname(file) === '.txt');
    
    console.log(chalk.blue(`📁 Processing ${files.length} files...`));
    
    files.forEach(file => {
        const inputPath = path.join(directory, file);
        const outputPath = path.join(directory, `processed_${file}`);
        
        onConvert(inputPath, { 
            format: options.format, 
            output: outputPath 
        });
    });
}

module.exports = { onConvert, onBatch };
```

#### API Client CLI

```javascript
const axios = require('axios');
const chalk = require('chalk');

async function onGet(endpoint, options) {
    try {
        const url = `${options.baseUrl || 'https://api.example.com'}${endpoint}`;
        const headers = {};
        
        if (options.token) {
            headers.Authorization = `Bearer ${options.token}`;
        }
        
        console.log(chalk.blue(`🌐 GET ${url}`));
        
        const response = await axios.get(url, { headers });
        
        if (options.format === 'json') {
            console.log(JSON.stringify(response.data, null, 2));
        } else {
            console.log(chalk.green('✅ Success:'));
            console.log(response.data);
        }
        
        return response.data;
    } catch (error) {
        console.error(chalk.red(`❌ Error: ${error.message}`));
        if (error.response) {
            console.error(chalk.yellow(`Status: ${error.response.status}`));
            console.error(chalk.yellow(`Data: ${JSON.stringify(error.response.data)}`));
        }
        process.exit(1);
    }
}

async function onPost(endpoint, data, options) {
    try {
        const url = `${options.baseUrl || 'https://api.example.com'}${endpoint}`;
        const headers = { 'Content-Type': 'application/json' };
        
        if (options.token) {
            headers.Authorization = `Bearer ${options.token}`;
        }
        
        // Parse data if it's a JSON string
        let payload = data;
        if (typeof data === 'string') {
            try {
                payload = JSON.parse(data);
            } catch (e) {
                // If not JSON, treat as plain string
            }
        }
        
        console.log(chalk.blue(`📤 POST ${url}`));
        
        const response = await axios.post(url, payload, { headers });
        
        console.log(chalk.green('✅ Created successfully:'));
        console.log(JSON.stringify(response.data, null, 2));
        
        return response.data;
    } catch (error) {
        console.error(chalk.red(`❌ Error: ${error.message}`));
        process.exit(1);
    }
}

module.exports = { onGet, onPost };
```

### Error Handling in Hooks

```javascript
function onRiskyOperation(input, options) {
    try {
        // Your logic here
        if (!input) {
            throw new Error('Input is required');
        }
        
        // Process input
        const result = processInput(input);
        
        console.log(chalk.green('✅ Operation completed successfully'));
        return result;
        
    } catch (error) {
        // Log error with appropriate formatting
        console.error(chalk.red(`❌ Error: ${error.message}`));
        
        if (options.verbose) {
            console.error(chalk.yellow('Stack trace:'));
            console.error(error.stack);
        }
        
        // Exit with error code
        process.exit(1);
    }
}
```

## TypeScript Support

TypeScript support in Goobits provides full type safety and modern development experience.

### Creating a TypeScript CLI

```bash
mkdir my-ts-cli
cd my-ts-cli

cat > goobits.yaml << 'EOF'
language: typescript
package_name: my-typescript-cli
command_name: tscli
display_name: "TypeScript CLI"
description: "A type-safe CLI built with Goobits"

dependencies:
  npm_packages:
    - commander@^9.0.0
    - chalk@^5.0.0

cli:
  name: tscli
  commands:
    process:
      desc: "Process data"
      args:
        - name: input
          desc: "Input data"
          required: true
      options:
        - name: format
          short: f
          choices: ["json", "yaml"]
          default: "json"
EOF

goobits build
```

### TypeScript Hook Implementation

The generated `app_hooks.ts` provides full type safety:

```typescript
import chalk from 'chalk';
import { readFileSync, writeFileSync } from 'fs';

// Types for your options
interface ProcessOptions {
    format: 'json' | 'yaml';
    output?: string;
    verbose?: boolean;
}

interface ApiResponse {
    success: boolean;
    data: any;
    message?: string;
}

// Fully typed hook function
export function onProcess(input: string, options: ProcessOptions): ApiResponse {
    try {
        console.log(chalk.blue(`🔄 Processing: ${input}`));
        
        let data: any;
        
        // Type-safe processing
        if (options.format === 'json') {
            data = JSON.parse(input);
        } else {
            // YAML parsing would go here
            data = { raw: input };
        }
        
        if (options.verbose) {
            console.log(chalk.gray(`Debug: Processing ${Object.keys(data).length} keys`));
        }
        
        const result = {
            processed: true,
            timestamp: new Date().toISOString(),
            data
        };
        
        if (options.output) {
            writeFileSync(options.output, JSON.stringify(result, null, 2));
            console.log(chalk.green(`✅ Saved to ${options.output}`));
        } else {
            console.log(JSON.stringify(result, null, 2));
        }
        
        return {
            success: true,
            data: result
        };
        
    } catch (error: any) {
        console.error(chalk.red(`❌ Error: ${error.message}`));
        return {
            success: false,
            data: null,
            message: error.message
        };
    }
}

// Async operation example
export async function onFetch(url: string, options: { timeout?: number }): Promise<ApiResponse> {
    const timeoutMs = options.timeout || 5000;
    
    try {
        console.log(chalk.blue(`🌐 Fetching: ${url}`));
        
        // Type-safe fetch with timeout
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), timeoutMs);
        
        const response = await fetch(url, { 
            signal: controller.signal 
        });
        
        clearTimeout(timeoutId);
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        
        console.log(chalk.green('✅ Fetch completed'));
        return {
            success: true,
            data
        };
        
    } catch (error: any) {
        console.error(chalk.red(`❌ Fetch failed: ${error.message}`));
        return {
            success: false,
            data: null,
            message: error.message
        };
    }
}
```

### TypeScript Configuration

The generated `tsconfig.json` includes optimized settings:

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "module": "CommonJS",
    "lib": ["ES2020"],
    "outDir": "./dist",
    "rootDir": "./",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "declaration": true,
    "declarationMap": true,
    "sourceMap": true
  },
  "include": ["**/*.ts"],
  "exclude": ["node_modules", "dist"]
}
```

### Building TypeScript Projects

```bash
# Development with watch mode
npm run dev

# Production build
npm run build

# Type checking
npm run type-check

# Run tests
npm test
```

## Testing

Goobits generates a comprehensive testing framework for your CLI.

### Generated Test Structure

```
test/
├── commands/
│   ├── process.test.js
│   └── stats.test.js
├── helpers/
│   └── cli-test.js
└── setup.js
```

### Example Test File

```javascript
// test/commands/process.test.js
const { runCLI } = require('../helpers/cli-test');
const { onProcess } = require('../../app_hooks');

describe('process command', () => {
    test('should process text with uppercase flag', async () => {
        const result = await runCLI(['process', 'hello world', '--uppercase']);
        expect(result.stdout).toContain('HELLO WORLD');
        expect(result.exitCode).toBe(0);
    });
    
    test('should handle pipe input', async () => {
        const result = await runCLI(['process', '--uppercase'], 'hello from pipe');
        expect(result.stdout).toContain('HELLO FROM PIPE');
    });
    
    test('should write to output file', async () => {
        const fs = require('fs');
        const tmpFile = '/tmp/test-output.txt';
        
        await runCLI(['process', 'test content', '--output', tmpFile]);
        
        expect(fs.existsSync(tmpFile)).toBe(true);
        expect(fs.readFileSync(tmpFile, 'utf8')).toBe('test content');
    });
});

describe('hook function tests', () => {
    test('onProcess hook directly', () => {
        const result = onProcess(['hello'], { uppercase: true });
        expect(result).toBeDefined();
    });
});
```

### Running Tests

```bash
# Run all tests
npm test

# Run specific test file
npm test -- process.test.js

# Run tests with coverage
npm run test:coverage

# Watch mode for development
npm run test:watch
```

### TypeScript Testing

For TypeScript projects, tests are also typed:

```typescript
// test/commands/process.test.ts
import { runCLI } from '../helpers/cli-test';
import { onProcess } from '../../app_hooks';

describe('process command', () => {
    test('should process with type safety', async () => {
        const result = await runCLI(['process', 'hello', '--format', 'json']);
        
        expect(result.stdout).toBeTruthy();
        expect(result.exitCode).toBe(0);
        
        // Parse and verify JSON output
        const output = JSON.parse(result.stdout);
        expect(output).toHaveProperty('processed', true);
        expect(output).toHaveProperty('data');
    });
    
    test('hook function with proper types', () => {
        const result = onProcess('test input', { 
            format: 'json', 
            verbose: true 
        });
        
        expect(result.success).toBe(true);
        expect(result.data).toBeDefined();
    });
});
```

## Deployment

### Publishing to npm

```bash
# Build the project (for TypeScript)
npm run build

# Update version
npm version patch  # or minor, major

# Publish to npm
npm publish

# For scoped packages
npm publish --access public
```

### GitHub Actions CI/CD

Create `.github/workflows/ci.yml`:

```yaml
name: CI/CD

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        node-version: [16, 18, 20]
    
    steps:
    - uses: actions/checkout@v3
    - name: Use Node.js ${{ matrix.node-version }}
      uses: actions/setup-node@v3
      with:
        node-version: ${{ matrix.node-version }}
        cache: 'npm'
    
    - run: npm ci
    - run: npm run build  # For TypeScript
    - run: npm test
    
  publish:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
    - uses: actions/checkout@v3
    - uses: actions/setup-node@v3
      with:
        node-version: 18
        registry-url: 'https://registry.npmjs.org'
    
    - run: npm ci
    - run: npm run build
    - run: npm publish
      env:
        NODE_AUTH_TOKEN: ${{ secrets.NPM_TOKEN }}
```

### Docker Deployment

```dockerfile
# Dockerfile
FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production

# Copy application code
COPY . .

# Build TypeScript (if applicable)
RUN npm run build

# Create non-root user
RUN addgroup -g 1001 -S nodejs
RUN adduser -S nodejs -u 1001

USER nodejs

# Expose port if your CLI has a server mode
EXPOSE 3000

CMD ["node", "index.js"]
```

## Advanced Features

### Interactive Prompts

```javascript
const inquirer = require('inquirer');

async function onSetup(options) {
    const answers = await inquirer.prompt([
        {
            type: 'input',
            name: 'name',
            message: 'What is your name?',
            default: 'User'
        },
        {
            type: 'list',
            name: 'theme',
            message: 'Choose a theme:',
            choices: ['dark', 'light', 'auto']
        },
        {
            type: 'confirm',
            name: 'enableFeature',
            message: 'Enable advanced features?',
            default: false
        }
    ]);
    
    console.log(chalk.green(`Setting up for ${answers.name}...`));
    // Save configuration
    return answers;
}
```

### Progress Indicators

```javascript
const chalk = require('chalk');

async function onDownload(url, options) {
    console.log(chalk.blue('📥 Starting download...'));
    
    // Simple progress indicator
    const steps = ['Connecting', 'Downloading', 'Verifying', 'Complete'];
    
    for (let i = 0; i < steps.length; i++) {
        process.stdout.write(`\r${chalk.yellow('⏳')} ${steps[i]}...`);
        await new Promise(resolve => setTimeout(resolve, 1000));
    }
    
    console.log(`\n${chalk.green('✅ Download complete!')}`);
}
```

### Configuration Management

```javascript
const fs = require('fs');
const path = require('path');
const os = require('os');

class Config {
    constructor() {
        this.configPath = path.join(os.homedir(), '.myapp', 'config.json');
        this.load();
    }
    
    load() {
        try {
            if (fs.existsSync(this.configPath)) {
                this.data = JSON.parse(fs.readFileSync(this.configPath, 'utf8'));
            } else {
                this.data = this.getDefaults();
            }
        } catch (error) {
            console.error(chalk.red(`Error loading config: ${error.message}`));
            this.data = this.getDefaults();
        }
    }
    
    save() {
        try {
            fs.mkdirSync(path.dirname(this.configPath), { recursive: true });
            fs.writeFileSync(this.configPath, JSON.stringify(this.data, null, 2));
        } catch (error) {
            console.error(chalk.red(`Error saving config: ${error.message}`));
        }
    }
    
    get(key) {
        return this.data[key];
    }
    
    set(key, value) {
        this.data[key] = value;
        this.save();
    }
    
    getDefaults() {
        return {
            theme: 'auto',
            verbose: false,
            apiUrl: 'https://api.example.com'
        };
    }
}

const config = new Config();

function onConfig(key, value, options) {
    if (!key) {
        // Show all config
        console.log(chalk.blue('📋 Current configuration:'));
        console.log(JSON.stringify(config.data, null, 2));
        return;
    }
    
    if (!value) {
        // Get specific key
        const val = config.get(key);
        console.log(`${key}: ${val}`);
        return val;
    }
    
    // Set value
    config.set(key, value);
    console.log(chalk.green(`✅ Set ${key} = ${value}`));
}
```

## Migration Guide

### From Python to Node.js/TypeScript

If you have an existing Python Goobits CLI and want to migrate to Node.js or TypeScript:

1. **Update your goobits.yaml**:
   ```yaml
   # Change this
   language: python
   
   # To this
   language: nodejs  # or typescript
   ```

2. **Convert Python hooks to JavaScript/TypeScript**:
   ```python
   # Python version
   def on_process(text, uppercase=False, output=None):
       if uppercase:
           text = text.upper()
       if output:
           with open(output, 'w') as f:
               f.write(text)
       else:
           print(text)
   ```
   
   ```javascript
   // JavaScript version
   function onProcess(text, options) {
       if (options.uppercase) {
           text = text.toUpperCase();
       }
       if (options.output) {
           fs.writeFileSync(options.output, text);
       } else {
           console.log(text);
       }
   }
   ```

3. **Update dependencies**:
   ```yaml
   # Replace Python dependencies
   dependencies:
     required: ["requests", "click"]
   
   # With npm packages
   dependencies:
     npm_packages: ["axios", "commander"]
   ```

4. **Regenerate and test**:
   ```bash
   goobits build
   npm install
   npm test
   ```

---

## Next Steps

1. **Explore the Examples** - Check out the generated code to understand the structure
2. **Read the Templates** - Look at the Jinja2 templates in `src/goobits_cli/templates/nodejs/` to understand how generation works
3. **Contribute** - The Node.js and TypeScript generators are actively developed. Contributions welcome!
4. **Build Something Awesome** - Use Goobits to create professional CLIs with minimal boilerplate

For more examples and advanced use cases, see the main [Goobits CLI documentation](../README.md) and the [proposal document](../PROPOSAL_05_NODE.md) for technical details.

**Happy building! 🚀**