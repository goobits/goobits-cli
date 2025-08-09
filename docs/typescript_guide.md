# TypeScript CLI Generation Guide

This comprehensive guide will help TypeScript developers leverage Goobits CLI to generate professional, type-safe command-line tools. Whether you're building developer tools, automation scripts, or full-featured CLI applications, Goobits provides a consistent, maintainable approach with full TypeScript support.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Understanding TypeScript Architecture](#understanding-typescript-architecture)
3. [TypeScript Configuration](#typescript-configuration)
4. [Working with Typed Hooks](#working-with-typed-hooks)
5. [Type Safety Features](#type-safety-features)
6. [Build Pipeline & Compilation](#build-pipeline--compilation)
7. [Advanced TypeScript Features](#advanced-typescript-features)
8. [Testing TypeScript CLIs](#testing-typescript-clis)
9. [IDE Support & IntelliSense](#ide-support--intellisense)
10. [Publishing TypeScript CLIs](#publishing-typescript-cliss)
11. [Common Issues & Troubleshooting](#common-issues--troubleshooting)

## Quick Start

### Prerequisites

- Node.js 18+ and npm 8+ installed
- TypeScript knowledge (basic to intermediate)
- Goobits CLI installed (`pipx install goobits-cli`)

### Your First TypeScript CLI in 5 Minutes

1. **Create your project directory:**
```bash
mkdir my-ts-cli
cd my-ts-cli
```

2. **Create a `goobits.yaml` configuration:**
```yaml
# goobits.yaml
language: typescript  # Enable TypeScript generation
package_name: my-ts-cli
command_name: tscli
display_name: "TypeScript CLI"
description: "A type-safe CLI tool built with TypeScript"

# TypeScript-specific dependencies
installation:
  extras:
    npm:
      - "@types/node@20.11.5"     # Node.js type definitions
      - "typescript@5.3.3"        # TypeScript compiler
      - "tsx@4.7.0"              # TypeScript execution
      - "chalk@5.3.0"            # Terminal colors
      - "ora@8.0.1"              # Progress spinners
      - "@types/inquirer@9.0.7"  # Typed prompts

# CLI structure
cli:
  name: tscli
  tagline: "Type-safe command execution"
  version: "1.0.0"
  commands:
    greet:
      desc: "Greet someone with type safety"
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
        - name: times
          short: t
          desc: "Number of times to greet"
          type: int
          default: 1
```

3. **Generate your TypeScript CLI:**
```bash
# Generate with Universal Template System (recommended)
goobits build --universal-templates

# Or use legacy TypeScript templates
goobits build
```

This creates:
```
my-ts-cli/
├── index.ts          # Main TypeScript entry point
├── package.json      # npm package with TypeScript scripts
├── tsconfig.json     # TypeScript compiler configuration
├── bin/
│   └── cli.ts        # TypeScript executable wrapper
├── lib/
│   ├── config.ts     # Typed configuration utilities
│   └── types.ts      # Generated type definitions
├── src/
│   └── hooks.ts      # YOUR typed business logic
├── dist/             # Compiled JavaScript (after build)
├── setup.sh          # Installation script
├── README.md         # Auto-generated documentation
└── .gitignore        # Includes TypeScript artifacts
```

4. **Add your typed business logic:**
```typescript
// src/hooks.ts
import chalk from 'chalk';
import ora, { Ora } from 'ora';

// TypeScript automatically infers types from your goobits.yaml
interface GreetArgs {
  name: string;
  style?: 'friendly' | 'formal' | 'excited';
  times?: number;
  // Global options
  verbose?: boolean;
  config?: string;
}

export async function onGreet(args: GreetArgs): Promise<void> {
  const { name, style = 'friendly', times = 1, verbose } = args;
  
  const spinner: Ora = ora('Preparing greeting...').start();
  
  // Type-safe delay function
  const delay = (ms: number): Promise<void> => 
    new Promise(resolve => setTimeout(resolve, ms));
  
  await delay(500);
  
  const greetings: Record<typeof style, string> = {
    friendly: chalk.green(`Hello ${name}! 👋`),
    formal: chalk.blue(`Good day, ${name}.`),
    excited: chalk.yellow.bold(`🎉 HEY ${name.toUpperCase()}! 🎉`)
  };
  
  spinner.succeed('Greeting ready!');
  
  // Type-safe loop
  for (let i = 0; i < times; i++) {
    console.log(greetings[style]);
    if (verbose && i < times - 1) {
      console.log(chalk.gray(`(${i + 1}/${times})`));
    }
  }
}
```

5. **Build and test:**
```bash
# Install dependencies and build TypeScript
./setup.sh --dev

# Test your CLI
tscli greet "World" --style excited --times 3

# Run with tsx directly (development)
npx tsx index.ts greet "Developer"

# Launch interactive mode (with universal templates)
tscli --interactive
```

## Understanding TypeScript Architecture

### How Goobits Works with TypeScript

Goobits generates a complete TypeScript CLI project using Commander.js with full type safety. Here's the flow:

```
goobits.yaml → Goobits Build → TypeScript Project → tsc Compilation → JavaScript CLI
                                       ↓
                              Type Definitions & Interfaces
```

### Generated TypeScript Project Structure

```
your-ts-cli/
├── index.ts              # Main CLI logic with typed Commander.js
├── package.json          # NPM manifest with TypeScript scripts
├── tsconfig.json         # TypeScript compiler configuration
├── tsconfig.build.json   # Production build configuration
├── bin/
│   └── cli.ts           # TypeScript CLI entry point
├── lib/
│   ├── config.ts        # Typed configuration management
│   ├── types.ts         # Auto-generated type definitions
│   └── utils.ts         # Typed utility functions
├── src/
│   ├── hooks.ts         # Your typed business logic
│   └── commands/        # Optional: typed command modules
├── types/               # Custom type declarations
│   └── global.d.ts      # Global type augmentations
├── test/
│   ├── hooks.test.ts    # TypeScript tests
│   └── tsconfig.json    # Test-specific TS config
├── dist/                # Compiled JavaScript output
├── setup.sh             # Smart installation script
├── .eslintrc.json       # ESLint with TypeScript rules
└── .prettierrc          # Prettier configuration
```

### Key TypeScript Components

**1. index.ts - Typed CLI Engine**
- Fully typed Commander.js setup
- Type-safe command registration
- Automatic type inference from configuration
- Compile-time validation of command structure

**2. lib/types.ts - Generated Type Definitions**
- Interfaces for all commands and options
- Type unions for choices
- Strict typing for hook functions

**3. src/hooks.ts - Your Typed Business Logic**
- Strongly typed function signatures
- IntelliSense for all arguments
- Compile-time validation
- Async/await with proper typing

## TypeScript Configuration

### Complete goobits.yaml for TypeScript

```yaml
# Language selection
language: typescript      # Enables TypeScript generation

# Package metadata
package_name: my-ts-cli
command_name: mytscli
display_name: "My TypeScript CLI"
description: "A fully typed CLI application"

# TypeScript-specific settings
installation:
  extras:
    npm:
      # Core TypeScript dependencies
      - "typescript@5.3.3"           # TypeScript compiler
      - "@types/node@20.11.5"        # Node.js types
      - "tsx@4.7.0"                  # Fast TS execution
      - "ts-node@10.9.2"            # TS REPL support
      
      # Type definitions
      - "@types/commander@11.0.0"    # Commander types
      - "@types/chalk@2.2.0"         # Chalk types (v5 has built-in)
      - "@types/inquirer@9.0.7"      # Inquirer types
      
      # Development tools
      - "@typescript-eslint/parser@6.19.0"
      - "@typescript-eslint/eslint-plugin@6.19.0"
      - "eslint@8.56.0"
      - "prettier@3.2.4"
      
      # Testing
      - "@types/jest@29.5.11"        # Jest types
      - "jest@29.7.0"                # Test runner
      - "ts-jest@29.1.1"            # TypeScript Jest transformer

# Build configuration
typescript:
  target: "ES2022"        # ECMAScript target
  module: "NodeNext"      # Module system
  strict: true            # Enable all strict checks
  esModuleInterop: true   # CommonJS interop
  skipLibCheck: true      # Skip .d.ts checking
  declaration: true       # Generate .d.ts files
  sourceMap: true         # Generate source maps
  outDir: "./dist"        # Output directory

# CLI Structure with typed commands
cli:
  name: mytscli
  tagline: "Type-safe CLI operations"
  version: "1.0.0"
  
  # Global options (typed)
  options:
    - name: config
      short: c
      desc: "Config file location"
      type: str
    - name: verbose
      short: v
      desc: "Verbose output"
      type: flag
    - name: json
      desc: "Output as JSON"
      type: flag
  
  commands:
    # Command with typed arguments
    process:
      desc: "Process data with type safety"
      args:
        - name: input
          desc: "Input file path"
          required: true
          type: str
        - name: output
          desc: "Output file path"
          required: true
          type: str
      options:
        - name: format
          short: f
          desc: "Output format"
          choices: ["json", "csv", "xml"]
          default: "json"
        - name: threads
          short: t
          desc: "Processing threads"
          type: int
          default: 4
          min: 1
          max: 16
    
    # Complex nested commands
    database:
      desc: "Database operations"
      subcommands:
        migrate:
          desc: "Run migrations"
          options:
            - name: target
              desc: "Target version"
              type: int
            - name: dry-run
              desc: "Preview changes"
              type: flag
        
        seed:
          desc: "Seed database"
          args:
            - name: dataset
              desc: "Dataset to seed"
              choices: ["test", "demo", "production"]
              required: true
```

### Generated tsconfig.json

```json
{
  "compilerOptions": {
    // Language and Environment
    "target": "ES2022",
    "lib": ["ES2022"],
    "module": "NodeNext",
    "moduleResolution": "NodeNext",
    
    // Type Checking
    "strict": true,
    "noImplicitAny": true,
    "strictNullChecks": true,
    "strictFunctionTypes": true,
    "strictBindCallApply": true,
    "strictPropertyInitialization": true,
    "noImplicitThis": true,
    "alwaysStrict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noImplicitReturns": true,
    "noFallthroughCasesInSwitch": true,
    "noUncheckedIndexedAccess": true,
    
    // Emit
    "declaration": true,
    "declarationMap": true,
    "sourceMap": true,
    "outDir": "./dist",
    "rootDir": "./",
    "removeComments": false,
    "importHelpers": true,
    
    // Interop Constraints
    "esModuleInterop": true,
    "allowSyntheticDefaultImports": true,
    "forceConsistentCasingInFileNames": true,
    
    // Skip Lib Check
    "skipLibCheck": true,
    
    // Advanced
    "resolveJsonModule": true,
    "allowJs": false,
    "checkJs": false
  },
  "include": [
    "**/*.ts",
    "types/**/*"
  ],
  "exclude": [
    "node_modules",
    "dist",
    "coverage",
    "**/*.test.ts",
    "**/*.spec.ts"
  ],
  "ts-node": {
    "esm": true,
    "experimentalSpecifierResolution": "node"
  }
}
```

### Build Configuration (tsconfig.build.json)

```json
{
  "extends": "./tsconfig.json",
  "compilerOptions": {
    "rootDir": "./",
    "outDir": "./dist",
    "removeComments": true,
    "sourceMap": false
  },
  "exclude": [
    "node_modules",
    "dist",
    "coverage",
    "**/*.test.ts",
    "**/*.spec.ts",
    "test/**/*"
  ]
}
```

## Working with Typed Hooks

### Hook Function Type System

Goobits generates type-safe interfaces for all your commands:

```typescript
// Generated in lib/types.ts
export interface ProcessArgs {
  // Positional arguments
  input: string;
  output: string;
  
  // Command options
  format?: 'json' | 'csv' | 'xml';
  threads?: number;
  
  // Global options
  config?: string;
  verbose?: boolean;
  json?: boolean;
  
  // System properties
  commandName: string;
  rawArgs: string[];
}

export interface DatabaseMigrateArgs {
  target?: number;
  dryRun?: boolean;
  // ... global options
}

// Hook function types
export type CommandHook<T> = (args: T) => void | Promise<void>;
```

### Complete Typed Hooks Example

```typescript
// src/hooks.ts
import chalk from 'chalk';
import ora, { Ora } from 'ora';
import { promises as fs } from 'fs';
import path from 'path';
import { z } from 'zod';  // For runtime validation

// Import generated types
import type { 
  ProcessArgs, 
  DatabaseMigrateArgs,
  DatabaseSeedArgs 
} from '../lib/types';

// Define custom types
interface ProcessResult {
  success: boolean;
  recordsProcessed: number;
  outputPath: string;
  errors: string[];
}

// Type-safe configuration schema
const ConfigSchema = z.object({
  database: z.object({
    host: z.string(),
    port: z.number(),
    name: z.string()
  }),
  processing: z.object({
    maxThreads: z.number().min(1).max(16),
    timeout: z.number()
  })
});

type Config = z.infer<typeof ConfigSchema>;

// Main process command with full typing
export async function onProcess(args: ProcessArgs): Promise<void> {
  const { input, output, format = 'json', threads = 4, verbose } = args;
  
  // Type-safe spinner
  const spinner: Ora = ora({
    text: 'Initializing processor...',
    color: 'blue'
  }).start();
  
  try {
    // Validate input file exists
    await validateFile(input);
    
    // Process with type safety
    const result = await processFile({
      inputPath: input,
      outputPath: output,
      format,
      threadCount: threads,
      verbose: verbose ?? false
    });
    
    spinner.succeed(chalk.green(`✓ Processed ${result.recordsProcessed} records`));
    
    if (result.errors.length > 0 && verbose) {
      console.warn(chalk.yellow('\nWarnings:'));
      result.errors.forEach(err => console.warn(`  - ${err}`));
    }
    
  } catch (error) {
    spinner.fail(chalk.red('Processing failed'));
    handleError(error);
    process.exit(1);
  }
}

// Database migration with strict typing
export async function onDatabaseMigrate(args: DatabaseMigrateArgs): Promise<void> {
  const { target, dryRun = false, config: configPath } = args;
  
  // Load typed configuration
  const config = await loadConfig(configPath);
  
  console.log(chalk.blue('🗄️  Database Migration'));
  console.log(chalk.gray(`Host: ${config.database.host}:${config.database.port}`));
  console.log(chalk.gray(`Database: ${config.database.name}`));
  
  if (dryRun) {
    console.log(chalk.yellow('\n⚠️  DRY RUN MODE - No changes will be applied'));
  }
  
  // Get migration files with proper typing
  const migrations = await getMigrations();
  const currentVersion = await getCurrentVersion(config);
  const targetVersion = target ?? migrations.length;
  
  // Type-safe migration execution
  const migrationsToRun = migrations.filter(m => 
    m.version > currentVersion && m.version <= targetVersion
  );
  
  if (migrationsToRun.length === 0) {
    console.log(chalk.green('✓ Database is up to date'));
    return;
  }
  
  console.log(chalk.blue(`\nMigrations to run: ${migrationsToRun.length}`));
  
  for (const migration of migrationsToRun) {
    const spinner = ora(`Running migration ${migration.version}: ${migration.name}`).start();
    
    if (!dryRun) {
      await runMigration(migration, config);
      await updateVersion(migration.version, config);
    }
    
    spinner.succeed();
  }
  
  console.log(chalk.green('\n✓ Migration completed successfully'));
}

// Helper functions with strict typing
async function validateFile(filePath: string): Promise<void> {
  try {
    const stats = await fs.stat(filePath);
    if (!stats.isFile()) {
      throw new Error(`Not a file: ${filePath}`);
    }
  } catch (error) {
    if ((error as NodeJS.ErrnoException).code === 'ENOENT') {
      throw new Error(`File not found: ${filePath}`);
    }
    throw error;
  }
}

async function processFile(options: {
  inputPath: string;
  outputPath: string;
  format: 'json' | 'csv' | 'xml';
  threadCount: number;
  verbose: boolean;
}): Promise<ProcessResult> {
  // Implementation with full type safety
  const result: ProcessResult = {
    success: true,
    recordsProcessed: 0,
    outputPath: options.outputPath,
    errors: []
  };
  
  // Process logic here...
  
  return result;
}

async function loadConfig(configPath?: string): Promise<Config> {
  const defaultPath = path.join(process.cwd(), 'config.json');
  const finalPath = configPath || defaultPath;
  
  try {
    const content = await fs.readFile(finalPath, 'utf8');
    const data = JSON.parse(content);
    
    // Runtime validation with Zod
    return ConfigSchema.parse(data);
  } catch (error) {
    if (error instanceof z.ZodError) {
      console.error(chalk.red('Invalid configuration:'));
      error.errors.forEach(err => {
        console.error(`  - ${err.path.join('.')}: ${err.message}`);
      });
      process.exit(1);
    }
    throw error;
  }
}

// Type-safe error handling
function handleError(error: unknown): void {
  if (error instanceof Error) {
    console.error(chalk.red(`Error: ${error.message}`));
    
    if (error.stack && process.env.DEBUG) {
      console.error(chalk.gray(error.stack));
    }
  } else {
    console.error(chalk.red('An unknown error occurred'));
  }
}

// Migration types
interface Migration {
  version: number;
  name: string;
  up: (config: Config) => Promise<void>;
  down: (config: Config) => Promise<void>;
}

async function getMigrations(): Promise<Migration[]> {
  // Load and return typed migrations
  return [];
}

async function getCurrentVersion(config: Config): Promise<number> {
  // Get current DB version
  return 0;
}

async function runMigration(migration: Migration, config: Config): Promise<void> {
  await migration.up(config);
}

async function updateVersion(version: number, config: Config): Promise<void> {
  // Update version in DB
}
```

### Generic Hook Patterns

```typescript
// Generic command handler with constraints
export async function createHandler<T extends Record<string, any>>(
  validator: z.ZodSchema<T>
): Promise<(args: T) => Promise<void>> {
  return async (args: T) => {
    // Validate at runtime
    const validated = validator.parse(args);
    
    // Process with validated data
    await process(validated);
  };
}

// Reusable typed utilities
export class CLIError extends Error {
  constructor(
    message: string,
    public readonly code: string,
    public readonly exitCode: number = 1
  ) {
    super(message);
    this.name = 'CLIError';
  }
}

// Type-safe option parsing
export function parseOptions<T extends Record<string, any>>(
  args: any,
  defaults: T
): T {
  return Object.assign({}, defaults, args) as T;
}
```

## Type Safety Features

### 1. Automatic Type Generation

Goobits generates TypeScript interfaces from your YAML:

```yaml
# In goobits.yaml
commands:
  deploy:
    args:
      - name: environment
        choices: ["dev", "staging", "prod"]
        required: true
    options:
      - name: timeout
        type: int
        default: 300
```

Generated types:
```typescript
// lib/types.ts
export interface DeployArgs {
  environment: 'dev' | 'staging' | 'prod';  // Union type from choices
  timeout?: number;  // Optional with default
  // ... global options
}
```

### 2. Compile-Time Validation

TypeScript catches errors before runtime:

```typescript
// ❌ Compile error: Type '"production"' is not assignable to type '"dev" | "staging" | "prod"'
export async function onDeploy(args: DeployArgs) {
  if (args.environment === 'production') {  // Error!
    // ...
  }
}

// ✅ Correct: Using valid union member
export async function onDeploy(args: DeployArgs) {
  if (args.environment === 'prod') {
    // ...
  }
}
```

### 3. Type Guards and Narrowing

```typescript
// Custom type guards
function isProductionDeploy(args: DeployArgs): args is DeployArgs & { environment: 'prod' } {
  return args.environment === 'prod';
}

export async function onDeploy(args: DeployArgs): Promise<void> {
  if (isProductionDeploy(args)) {
    // TypeScript knows environment is 'prod' here
    await requireConfirmation('Production deployment');
  }
  
  // Discriminated unions
  type Result = 
    | { success: true; data: string }
    | { success: false; error: Error };
  
  const result = await deploy(args);
  
  if (result.success) {
    // TypeScript knows result.data exists
    console.log(result.data);
  } else {
    // TypeScript knows result.error exists
    console.error(result.error.message);
  }
}
```

### 4. Generic Command Builders

```typescript
// Type-safe command factory
export function createCommand<TArgs, TResult>(
  config: {
    name: string;
    validate?: (args: TArgs) => void;
    execute: (args: TArgs) => Promise<TResult>;
    format?: (result: TResult) => string;
  }
) {
  return async (args: TArgs): Promise<void> => {
    try {
      if (config.validate) {
        config.validate(args);
      }
      
      const result = await config.execute(args);
      
      const output = config.format 
        ? config.format(result)
        : JSON.stringify(result, null, 2);
      
      console.log(output);
    } catch (error) {
      handleError(error);
    }
  };
}

// Usage with type inference
export const onApiCall = createCommand({
  name: 'api-call',
  validate: (args: ApiCallArgs) => {
    if (!args.endpoint.startsWith('http')) {
      throw new Error('Endpoint must be a valid URL');
    }
  },
  execute: async (args) => {
    const response = await fetch(args.endpoint);
    return response.json();
  },
  format: (result) => chalk.green(JSON.stringify(result, null, 2))
});
```

## Build Pipeline & Compilation

### Development Build Process

```json
// package.json scripts
{
  "scripts": {
    // Development with watch mode
    "dev": "tsx watch index.ts",
    "dev:build": "tsc --watch",
    
    // Production build
    "build": "tsc -p tsconfig.build.json",
    "build:clean": "rm -rf dist && npm run build",
    
    // Direct execution
    "start": "tsx index.ts",
    "start:prod": "node dist/index.js",
    
    // Type checking
    "type-check": "tsc --noEmit",
    "type-check:watch": "tsc --noEmit --watch",
    
    // Linting and formatting
    "lint": "eslint . --ext .ts",
    "lint:fix": "eslint . --ext .ts --fix",
    "format": "prettier --write \"**/*.{ts,json,md}\"",
    
    // Pre-commit hooks
    "precommit": "npm run type-check && npm run lint && npm run test",
    
    // Bundle for distribution
    "bundle": "esbuild index.ts --bundle --platform=node --outfile=dist/cli.js --minify"
  }
}
```

### Using esbuild for Fast Builds

```javascript
// esbuild.config.js
const esbuild = require('esbuild');

esbuild.build({
  entryPoints: ['index.ts'],
  bundle: true,
  platform: 'node',
  target: 'node18',
  outfile: 'dist/cli.js',
  minify: true,
  sourcemap: true,
  external: [
    // Don't bundle these
    'commander',
    'chalk',
    'ora'
  ],
  define: {
    'process.env.NODE_ENV': '"production"'
  }
}).catch(() => process.exit(1));
```

### Build Optimization

```typescript
// Conditional imports for smaller bundles
export async function onOptionalFeature(args: any): Promise<void> {
  if (args.useFeature) {
    // Dynamic import only when needed
    const { heavyFeature } = await import('./features/heavy');
    await heavyFeature(args);
  } else {
    console.log('Feature not enabled');
  }
}

// Tree-shakeable exports
export { lightFunction } from './utils/light';
// Heavy function not imported unless used
```

## Advanced TypeScript Features

### 1. Decorators (Experimental)

```typescript
// Enable decorators in tsconfig.json:
// "experimentalDecorators": true

// Command decorator
function Command(name: string) {
  return function (target: any, propertyKey: string, descriptor: PropertyDescriptor) {
    const originalMethod = descriptor.value;
    
    descriptor.value = async function (...args: any[]) {
      console.log(chalk.blue(`Executing command: ${name}`));
      const start = Date.now();
      
      try {
        const result = await originalMethod.apply(this, args);
        const duration = Date.now() - start;
        console.log(chalk.gray(`Command completed in ${duration}ms`));
        return result;
      } catch (error) {
        console.error(chalk.red(`Command failed: ${error}`));
        throw error;
      }
    };
  };
}

// Usage
export class CommandHandlers {
  @Command('deploy')
  async onDeploy(args: DeployArgs): Promise<void> {
    // Implementation
  }
}
```

### 2. Advanced Type Manipulation

```typescript
// Utility types for CLI development
type RequiredKeys<T> = {
  [K in keyof T]-?: {} extends Pick<T, K> ? never : K
}[keyof T];

type OptionalKeys<T> = {
  [K in keyof T]-?: {} extends Pick<T, K> ? K : never
}[keyof T];

// Deep partial for config objects
type DeepPartial<T> = T extends object ? {
  [P in keyof T]?: DeepPartial<T[P]>;
} : T;

// Command result types
type CommandResult<T> = 
  | { success: true; data: T }
  | { success: false; error: Error };

// Async command handler
type AsyncCommandHandler<TArgs, TResult> = (
  args: TArgs
) => Promise<CommandResult<TResult>>;

// Usage in hooks
export const onAdvancedCommand: AsyncCommandHandler<AdvancedArgs, ProcessedData> = 
  async (args) => {
    try {
      const data = await process(args);
      return { success: true, data };
    } catch (error) {
      return { success: false, error: error as Error };
    }
  };
```

### 3. Template Literal Types

```typescript
// Dynamic command names
type CommandPrefix = 'get' | 'set' | 'delete';
type ResourceType = 'user' | 'project' | 'config';
type CommandName = `${CommandPrefix}${Capitalize<ResourceType>}`;

// Generates: 'getUser' | 'setUser' | 'deleteUser' | 'getProject' | ...

// Hook mapping
type HookMap = {
  [K in CommandName as `on${Capitalize<K>}`]: (args: any) => Promise<void>
};

// Environment-specific configs
type Environment = 'development' | 'staging' | 'production';
type ConfigKey<E extends Environment> = `${E}_config`;
```

### 4. Conditional Types

```typescript
// Conditional argument types based on command
type CommandArgs<T extends string> = 
  T extends 'deploy' ? DeployArgs :
  T extends 'migrate' ? MigrateArgs :
  T extends 'test' ? TestArgs :
  never;

// Type-safe command executor
export function executeCommand<T extends string>(
  command: T,
  args: CommandArgs<T>
): Promise<void> {
  // Implementation
}

// Nullable handling
type NullableFields<T> = {
  [K in keyof T]: T[K] | null
};

// Extract promise type
type UnwrapPromise<T> = T extends Promise<infer U> ? U : T;
```

## Testing TypeScript CLIs

### Jest Configuration for TypeScript

```javascript
// jest.config.js
module.exports = {
  preset: 'ts-jest',
  testEnvironment: 'node',
  roots: ['<rootDir>/src', '<rootDir>/test'],
  testMatch: ['**/__tests__/**/*.ts', '**/?(*.)+(spec|test).ts'],
  transform: {
    '^.+\\.ts$': 'ts-jest',
  },
  collectCoverageFrom: [
    'src/**/*.ts',
    '!src/**/*.d.ts',
    '!src/types/**',
  ],
  coverageThreshold: {
    global: {
      branches: 80,
      functions: 80,
      lines: 80,
      statements: 80,
    },
  },
  moduleNameMapper: {
    '^@/(.*)$': '<rootDir>/src/$1',
  },
  globals: {
    'ts-jest': {
      tsconfig: {
        // Test-specific TS config
        esModuleInterop: true,
        allowSyntheticDefaultImports: true,
      },
    },
  },
};
```

### Type-Safe Test Examples

```typescript
// test/hooks.test.ts
import { describe, it, expect, jest, beforeEach, afterEach } from '@jest/globals';
import { onDeploy, onProcess } from '../src/hooks';
import type { DeployArgs, ProcessArgs } from '../lib/types';

// Mock types
jest.mock('ora', () => ({
  default: jest.fn(() => ({
    start: jest.fn().mockReturnThis(),
    succeed: jest.fn().mockReturnThis(),
    fail: jest.fn().mockReturnThis(),
  })),
}));

describe('Command Hooks', () => {
  describe('onDeploy', () => {
    it('should deploy to development environment', async () => {
      const args: DeployArgs = {
        environment: 'dev',
        timeout: 300,
        commandName: 'deploy',
        rawArgs: ['deploy', 'dev']
      };
      
      await expect(onDeploy(args)).resolves.not.toThrow();
    });
    
    it('should require confirmation for production', async () => {
      const confirmMock = jest.fn().mockResolvedValue(true);
      jest.mock('inquirer', () => ({
        prompt: confirmMock
      }));
      
      const args: DeployArgs = {
        environment: 'prod',
        timeout: 600,
        commandName: 'deploy',
        rawArgs: ['deploy', 'prod']
      };
      
      await onDeploy(args);
      
      expect(confirmMock).toHaveBeenCalledWith(
        expect.objectContaining({
          type: 'confirm',
          message: expect.stringContaining('production')
        })
      );
    });
  });
  
  describe('onProcess', () => {
    const mockFs = {
      stat: jest.fn(),
      readFile: jest.fn(),
      writeFile: jest.fn(),
    };
    
    beforeEach(() => {
      jest.mock('fs/promises', () => mockFs);
    });
    
    afterEach(() => {
      jest.clearAllMocks();
    });
    
    it('should process JSON format by default', async () => {
      const args: ProcessArgs = {
        input: 'input.txt',
        output: 'output.json',
        threads: 4,
        commandName: 'process',
        rawArgs: ['process', 'input.txt', 'output.json']
      };
      
      mockFs.stat.mockResolvedValue({ isFile: () => true });
      mockFs.readFile.mockResolvedValue('test data');
      
      await onProcess(args);
      
      expect(mockFs.writeFile).toHaveBeenCalledWith(
        'output.json',
        expect.stringContaining('{')
      );
    });
  });
});
```

### Integration Testing with Types

```typescript
// test/integration.test.ts
import { spawn } from 'child_process';
import { promisify } from 'util';
import path from 'path';

const exec = promisify(require('child_process').exec);

interface CLIResult {
  stdout: string;
  stderr: string;
  code: number;
}

async function runCLI(args: string[]): Promise<CLIResult> {
  const cliPath = path.join(__dirname, '../dist/index.js');
  
  return new Promise((resolve) => {
    const proc = spawn('node', [cliPath, ...args], {
      env: { ...process.env, NODE_ENV: 'test' }
    });
    
    let stdout = '';
    let stderr = '';
    
    proc.stdout.on('data', (data) => { stdout += data.toString(); });
    proc.stderr.on('data', (data) => { stderr += data.toString(); });
    
    proc.on('close', (code) => {
      resolve({ stdout, stderr, code: code ?? 0 });
    });
  });
}

describe('CLI Integration Tests', () => {
  beforeAll(async () => {
    // Build the CLI before testing
    await exec('npm run build');
  });
  
  it('should show help information', async () => {
    const result = await runCLI(['--help']);
    
    expect(result.code).toBe(0);
    expect(result.stdout).toContain('Usage:');
    expect(result.stdout).toContain('Commands:');
  });
  
  it('should handle invalid commands', async () => {
    const result = await runCLI(['invalid-command']);
    
    expect(result.code).not.toBe(0);
    expect(result.stderr).toContain('Unknown command');
  });
  
  it('should validate required arguments', async () => {
    const result = await runCLI(['process']);
    
    expect(result.code).not.toBe(0);
    expect(result.stderr).toContain('required');
  });
});
```

### Type-Safe Mocking

```typescript
// test/helpers/mocks.ts
import type { DeployArgs, ProcessArgs } from '../../lib/types';

export function createMockArgs<T extends Record<string, any>>(
  overrides: Partial<T> = {}
): T {
  const defaults = {
    commandName: 'test',
    rawArgs: ['test'],
    verbose: false,
    config: undefined,
    json: false
  };
  
  return { ...defaults, ...overrides } as T;
}

// Usage
const deployArgs = createMockArgs<DeployArgs>({
  environment: 'staging',
  timeout: 300
});
```

## IDE Support & IntelliSense

### VSCode Configuration

```json
// .vscode/settings.json
{
  "typescript.tsdk": "node_modules/typescript/lib",
  "typescript.enablePromptUseWorkspaceTsdk": true,
  "editor.formatOnSave": true,
  "editor.defaultFormatter": "esbenp.prettier-vscode",
  "[typescript]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode",
    "editor.codeActionsOnSave": {
      "source.organizeImports": true,
      "source.fixAll.eslint": true
    }
  },
  "typescript.preferences.includePackageJsonAutoImports": "on",
  "typescript.suggest.completeFunctionCalls": true,
  "typescript.updateImportsOnFileMove.enabled": "always",
  "typescript.suggest.autoImports": true,
  "typescript.preferences.importModuleSpecifier": "relative"
}
```

### Launch Configuration for Debugging

```json
// .vscode/launch.json
{
  "version": "0.2.0",
  "configurations": [
    {
      "type": "node",
      "request": "launch",
      "name": "Debug TypeScript CLI",
      "program": "${workspaceFolder}/index.ts",
      "args": ["greet", "World", "--style", "excited"],
      "runtimeArgs": ["-r", "ts-node/register"],
      "env": {
        "TS_NODE_PROJECT": "${workspaceFolder}/tsconfig.json",
        "NODE_ENV": "development"
      },
      "console": "integratedTerminal",
      "internalConsoleOptions": "neverOpen",
      "skipFiles": ["<node_internals>/**"],
      "sourceMaps": true,
      "outFiles": ["${workspaceFolder}/dist/**/*.js"]
    },
    {
      "type": "node",
      "request": "launch",
      "name": "Debug Current Test",
      "program": "${workspaceFolder}/node_modules/.bin/jest",
      "args": [
        "--runInBand",
        "--no-coverage",
        "${relativeFile}"
      ],
      "console": "integratedTerminal",
      "internalConsoleOptions": "neverOpen",
      "env": {
        "NODE_ENV": "test"
      }
    }
  ]
}
```

### JSDoc for Better IntelliSense

```typescript
/**
 * Processes a file with the specified options
 * @param args - Command arguments
 * @param args.input - Path to input file
 * @param args.output - Path to output file
 * @param args.format - Output format (json, csv, xml)
 * @param args.threads - Number of processing threads
 * @returns Promise that resolves when processing is complete
 * @throws {CLIError} When input file doesn't exist
 * @example
 * await onProcess({
 *   input: './data.txt',
 *   output: './result.json',
 *   format: 'json',
 *   threads: 4
 * });
 */
export async function onProcess(args: ProcessArgs): Promise<void> {
  // Implementation
}
```

## Publishing TypeScript CLIs

### Preparing for npm Publication

```json
// package.json for publishing
{
  "name": "@yourscope/my-ts-cli",
  "version": "1.0.0",
  "description": "Type-safe CLI tool",
  "keywords": ["cli", "typescript", "tool"],
  "main": "dist/index.js",
  "types": "dist/index.d.ts",
  "bin": {
    "mytscli": "./dist/bin/cli.js"
  },
  "files": [
    "dist/",
    "README.md",
    "LICENSE"
  ],
  "scripts": {
    "prepublishOnly": "npm run clean && npm run build && npm run test",
    "clean": "rm -rf dist",
    "build": "tsc -p tsconfig.build.json",
    "postbuild": "chmod +x dist/bin/cli.js"
  },
  "engines": {
    "node": ">=18.0.0"
  },
  "publishConfig": {
    "access": "public",
    "registry": "https://registry.npmjs.org/"
  }
}
```

### TypeScript Declaration Files

```typescript
// Ensure your package exports types correctly
// In index.ts
export * from './lib/types';
export * from './src/hooks';
export { CLIError } from './lib/errors';

// Package consumers can then:
import { ProcessArgs, onProcess } from '@yourscope/my-ts-cli';
```

### Publishing Workflow

```bash
# 1. Clean and build
npm run clean
npm run build

# 2. Test the package locally
npm pack
npm install -g yourscope-my-ts-cli-1.0.0.tgz
mytscli --help

# 3. Publish to npm
npm publish --access public

# 4. For beta releases
npm version prerelease --preid=beta
npm publish --tag beta
```

## Common Issues & Troubleshooting

### TypeScript Compilation Errors

#### Issue: "Cannot find module" errors

```bash
# Error: Cannot find module '@/utils' or its corresponding type declarations
```

**Solution:**
```json
// tsconfig.json - Add path mappings
{
  "compilerOptions": {
    "baseUrl": ".",
    "paths": {
      "@/*": ["src/*"],
      "@lib/*": ["lib/*"],
      "@types/*": ["types/*"]
    }
  }
}
```

#### Issue: Type errors with npm packages

```typescript
// Error: Could not find a declaration file for module 'some-package'
```

**Solution:**
```bash
# Install type definitions
npm install --save-dev @types/some-package

# Or create your own declarations
echo "declare module 'some-package';" > types/some-package.d.ts
```

#### Issue: "TypeError: Cannot read property" at runtime

**Common cause:** Incorrect TypeScript configuration allowing unsafe code

**Solution:**
```json
// tsconfig.json - Enable strict checks
{
  "compilerOptions": {
    "strict": true,
    "strictNullChecks": true,
    "strictPropertyInitialization": true,
    "noUncheckedIndexedAccess": true
  }
}
```

### Build and Performance Issues

#### Issue: Slow TypeScript compilation

**Solution 1:** Use incremental compilation
```json
// tsconfig.json
{
  "compilerOptions": {
    "incremental": true,
    "tsBuildInfoFile": ".tsbuildinfo"
  }
}
```

**Solution 2:** Use esbuild or swc
```bash
# Replace tsc with esbuild
npm install --save-dev esbuild
# Update build script to use esbuild
```

#### Issue: Large bundle size

**Solution:** Analyze and optimize
```bash
# Install bundle analyzer
npm install --save-dev source-map-explorer

# Add script
"analyze": "source-map-explorer dist/**/*.js"

# Run analysis
npm run build && npm run analyze
```

### Runtime Issues

#### Issue: "ReferenceError: exports is not defined"

**Cause:** ESM/CommonJS mismatch

**Solution:**
```json
// package.json
{
  "type": "module",  // For ESM
  // or keep CommonJS and update tsconfig
}

// tsconfig.json for CommonJS
{
  "compilerOptions": {
    "module": "commonjs",
    "esModuleInterop": true
  }
}
```

#### Issue: Async/await not working

**Solution:** Check Node.js version and target
```json
// tsconfig.json
{
  "compilerOptions": {
    "target": "ES2022",  // Modern async/await
    "lib": ["ES2022"]
  }
}
```

### Development Workflow Issues

#### Issue: Hot reload not working

**Solution:** Use proper watch setup
```json
// package.json
{
  "scripts": {
    "dev": "nodemon --exec 'tsx' index.ts",
    "dev:tsc": "tsc --watch --preserveWatchOutput"
  }
}

// nodemon.json
{
  "watch": ["src", "lib"],
  "ext": "ts",
  "ignore": ["dist", "node_modules"],
  "exec": "tsx"
}
```

### Type Safety Gotchas

#### Issue: Type assertions hiding errors

```typescript
// Bad: Type assertion
const result = JSON.parse(data) as MyType;  // Unsafe!

// Good: Runtime validation
import { z } from 'zod';

const MyTypeSchema = z.object({
  id: z.number(),
  name: z.string()
});

const result = MyTypeSchema.parse(JSON.parse(data));  // Safe!
```

#### Issue: Optional chaining gotchas

```typescript
// Gotcha: Optional chaining with arrays
const first = args.items?.[0];  // Type: T | undefined

// Better: Explicit checks
const first = args.items && args.items.length > 0 
  ? args.items[0] 
  : undefined;
```

## Performance Optimization

### TypeScript Performance Standards

Goobits-generated TypeScript CLIs maintain high performance:
- **Startup time**: <70ms (Grade A)
- **Memory usage**: ~40MB (efficient for Node.js)
- **Type checking**: Incremental builds for fast development

### Optimization Strategies

1. **Use `tsx` for Development**: Faster than `ts-node`
```json
{
  "scripts": {
    "dev": "tsx watch index.ts",  // Fast!
    "dev:slow": "ts-node index.ts"  // Slower
  }
}
```

2. **Bundle for Production**: Use esbuild for optimal performance
```bash
# Single-file bundle with tree shaking
esbuild index.ts --bundle --minify --platform=node --outfile=dist/cli.js
```

3. **Lazy Loading**: Load heavy dependencies only when needed
```typescript
export async function onHeavyCommand(args: HeavyArgs): Promise<void> {
  // Load only when command is used
  const { processLargeFile } = await import('./heavy-processor');
  await processLargeFile(args.file);
}
```

## Best Practices Summary

### 1. Type Everything
- Use explicit types for function parameters and returns
- Avoid `any` - use `unknown` when type is truly unknown
- Create interfaces for all data structures

### 2. Leverage TypeScript Features
- Use union types for choices
- Implement type guards for runtime safety
- Use const assertions for literal types

### 3. Maintain Type Safety
- Enable all strict compiler options
- Use runtime validation for external data
- Test types with `expect-type` or `tsd`

### 4. Optimize for Performance
- Use incremental compilation
- Bundle for distribution
- Implement lazy loading for heavy features

### 5. Document with Types
- Types serve as documentation
- Add JSDoc for complex functions
- Export types for package consumers

## Conclusion

TypeScript brings powerful type safety and developer experience improvements to CLI development. With Goobits CLI's TypeScript support, you get:

- **Full type safety** from configuration to runtime
- **Excellent IDE support** with IntelliSense
- **Compile-time error catching** before deployment
- **Modern JavaScript features** with backwards compatibility
- **Professional tooling** integration

The combination of Goobits CLI's code generation and TypeScript's type system creates a robust foundation for building maintainable, scalable command-line tools.

Happy type-safe CLI building! 🚀✨