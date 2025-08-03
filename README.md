# Goobits CLI Framework

**Build professional command-line tools with YAML configuration.** Goobits CLI generates rich terminal interfaces, setup scripts, and handles installation management automatically.

## Multi-Language Support

Goobits CLI now supports generating command-line applications in **three languages**:

- **Python** - Rich Click-based CLIs with pipx installation
- **Node.js** - Commander.js-based CLIs with npm/npx support  
- **TypeScript** - Fully typed CLIs with modern TypeScript tooling

Choose your language in the `goobits.yaml` configuration:

```yaml
# Python CLI (default)
language: python
package_name: my-python-cli

# Node.js CLI  
language: nodejs
package_name: my-node-cli

# TypeScript CLI
language: typescript  
package_name: my-typescript-cli
```

## What is Goobits CLI?

Goobits CLI transforms a simple YAML file into a complete command-line application with:
- Rich terminal interface with colors and help formatting
- Professional setup scripts with dependency checking
- Pipe support (`echo "text" | your-cli`)
- Plugin system for extensions
- Cross-platform installation with pipx

**Used by:** TTT (AI text processing), TTS (text-to-speech), STT (speech-to-text), and other Goobits tools.

## Quick Start

### 1. Install Goobits CLI
```bash
# Install from PyPI
pipx install goobits-cli

# or clone and install locally:
git clone https://github.com/goobits/goobits-cli
cd goobits-cli && ./setup.sh install
```

### 2. Create Your First CLI

Choose your preferred language:

<details>
<summary><strong>Python CLI</strong> (Click to expand)</summary>

```bash
mkdir my-awesome-cli
cd my-awesome-cli

# Create goobits.yaml
cat > goobits.yaml << 'EOF'
language: python
package_name: my-awesome-cli
command_name: awesome
display_name: "Awesome CLI"
description: "My first Goobits CLI tool"

python:
  minimum_version: "3.8"

installation:
  extras:
    python: ["pipx"]

cli:
  name: awesome
  tagline: "An awesome command-line tool"
  commands:
    greet:
      desc: "Greet someone"
      args:
        - name: name
          desc: "Name to greet"
          required: true
      options:
        - name: greeting
          short: g
          desc: "Custom greeting"
          default: "Hello"
EOF
```

</details>

<details>
<summary><strong>Node.js CLI</strong> (Click to expand)</summary>

```bash
mkdir my-awesome-cli
cd my-awesome-cli

# Create goobits.yaml
cat > goobits.yaml << 'EOF'
language: nodejs
package_name: my-awesome-cli
command_name: awesome
display_name: "Awesome CLI"
description: "My first Goobits CLI tool"

installation:
  extras:
    npm: ["commander@^11.1.0", "chalk@^5.3.0"]

cli:
  name: awesome
  tagline: "An awesome command-line tool"
  version: "1.0.0"
  commands:
    greet:
      desc: "Greet someone"
      args:
        - name: name
          desc: "Name to greet"
          required: true
      options:
        - name: greeting
          short: g
          desc: "Custom greeting"
          default: "Hello"
EOF
```

</details>

<details>
<summary><strong>TypeScript CLI</strong> (Click to expand)</summary>

```bash
mkdir my-awesome-cli
cd my-awesome-cli

# Create goobits.yaml
cat > goobits.yaml << 'EOF'
language: typescript
package_name: my-awesome-cli
command_name: awesome
display_name: "Awesome CLI"
description: "My first Goobits CLI tool"

installation:
  extras:
    npm: ["commander@^11.1.0", "chalk@^5.3.0", "@types/node@^20.0.0", "typescript@^5.0.0"]

cli:
  name: awesome
  tagline: "An awesome command-line tool"
  version: "1.0.0"
  commands:
    greet:
      desc: "Greet someone"
      args:
        - name: name
          desc: "Name to greet"
          required: true
      options:
        - name: greeting
          short: g
          desc: "Custom greeting"
          default: "Hello"
EOF
```

</details>

### 3. Generate Your CLI
```bash
goobits build
```

<details>
<summary><strong>Generated File Structure</strong> (Click to see what's created)</summary>

**Python:**
```
my-awesome-cli/
├── src/
│   └── my_awesome_cli/
│       └── cli.py          # Generated CLI code
├── setup.sh                # Installation script
└── README.md               # Auto-generated docs
```

**Node.js:**
```
my-awesome-cli/
├── index.js                # Main CLI entry point
├── package.json            # NPM configuration
├── bin/
│   └── cli.js              # Executable wrapper
├── app_hooks.js            # Your business logic goes here
├── setup.sh                # Installation script (supports --dev)
├── README.md               # Auto-generated docs
└── .gitignore              # Node.js ignores
```

**TypeScript:**
```
my-awesome-cli/
├── index.ts                # TypeScript CLI entry
├── package.json            # NPM configuration
├── tsconfig.json           # TypeScript config
├── bin/
│   └── cli.js              # Executable wrapper
├── app_hooks.ts            # Your typed business logic
├── setup.sh                # Installation script
├── README.md               # Auto-generated docs
└── .gitignore              # Node.js ignores
```
</details>

### 4. Add Your Business Logic

> **Note:** Hook function signatures differ by language:
> - **Python**: Individual parameters `on_greet(name, greeting)`
> - **Node.js/TypeScript**: Single args object `onGreet(args)` with destructuring

<details>
<summary><strong>Python</strong> (Click to expand)</summary>

```bash
# Create the app hooks file
mkdir -p src/my_awesome_cli
cat > src/my_awesome_cli/app_hooks.py << 'EOF'
import click

def on_greet(name, greeting):
    """Handle the greet command"""
    click.echo(f"{greeting}, {name}!")
    return f"{greeting}, {name}!"
EOF
```

</details>

<details>
<summary><strong>Node.js</strong> (Click to expand)</summary>

```bash
# Create the app hooks file (ES6 modules)
cat > app_hooks.js << 'EOF'
import chalk from 'chalk';

export function onGreet(args) {
    const { name, greeting = 'Hello' } = args;
    const message = `${greeting}, ${name}!`;
    console.log(chalk.green(message));
    return message;
}
EOF
```

</details>

<details>
<summary><strong>TypeScript</strong> (Click to expand)</summary>

```bash
# Create the app hooks file (TypeScript)
cat > app_hooks.ts << 'EOF'
import chalk from 'chalk';

interface GreetArgs {
    name: string;
    greeting?: string;
    [key: string]: any;
}

export function onGreet(args: GreetArgs): string {
    const { name, greeting = 'Hello' } = args;
    const message = `${greeting}, ${name}!`;
    console.log(chalk.green(message));
    return message;
}
EOF
```

</details>

### 5. Install and Test

<details>
<summary><strong>Python</strong> (Click to expand)</summary>

```bash
./setup.sh install --dev  # Install with all dependencies automatically
awesome greet World        # Test your CLI
awesome greet World -g "Hi"  # With custom greeting
echo "Alice" | awesome greet  # Pipe support works automatically!
```

</details>

<details>
<summary><strong>Node.js/TypeScript</strong> (Click to expand)</summary>

```bash
# Option 1: Using setup.sh (recommended)
./setup.sh --dev            # Install dependencies + create global link
awesome greet World         # Test your CLI

# Option 2: Using npm directly
npm install                 # Install dependencies
npm link                    # Make CLI available globally
awesome greet World         # Test your CLI

# Both options support:
awesome greet World -g "Hi" # With custom greeting
echo "Alice" | awesome greet # Pipe support works automatically!
```

</details>

## Development Workflow

### The Goobits Pattern
```
goobits.yaml → goobits build → Generated Files → Install → Working CLI

Python:    goobits.yaml → goobits build → cli.py + setup.sh → ./setup.sh install --dev → working CLI
Node.js:   goobits.yaml → goobits build → index.js + package.json → npm install && npm link → working CLI  
TypeScript: goobits.yaml → goobits build → index.ts + tsconfig.json → npm install && npm link → working CLI
```

### Daily Development Cycle

<details>
<summary><strong>Python Development</strong></summary>

```bash
# 1. Modify your business logic
vim src/my_awesome_cli/app_hooks.py

# 2. Test immediately (changes reflected instantly with --dev)
awesome greet "Test"

# 3. Add new commands/options? Update config
vim goobits.yaml

# 4. Rebuild CLI structure
goobits build

# 5. Update installation
./setup.sh upgrade
```
</details>

<details>
<summary><strong>Node.js/TypeScript Development</strong></summary>

```bash
# 1. Modify your business logic
vim app_hooks.js  # or app_hooks.ts for TypeScript

# 2. Test immediately (changes reflected after rebuild)
awesome greet "Test"

# 3. Add new commands/options? Update config
vim goobits.yaml

# 4. Rebuild CLI structure
goobits build

# 5. For TypeScript, compile the changes
npx tsc  # TypeScript only

# 6. Test your changes
node index.js greet "Test"
```
</details>

### Development vs Production Installation

<details>
<summary><strong>Language-Specific Installation Methods</strong></summary>

**Python (Live Reload):**
```bash
# Development mode - changes reflect immediately without reinstall
./setup.sh install --dev

# Production mode - stable installation
./setup.sh install
```

**Node.js/TypeScript (Manual Reload):**
```bash
# Development mode - creates global link, but requires restart for changes
./setup.sh --dev
# OR
npm install && npm link

# Production mode - install from npm registry
npm install -g my-awesome-cli
```

**Key Difference:** Python's `--dev` mode automatically reflects code changes, while Node.js requires restarting the CLI after modifications.
</details>

### Workflow Differences by Language

| Feature | Python | Node.js | TypeScript |
|---------|---------|----------|-------------|
| **Live reload on code changes** | ✅ Yes (--dev mode) | ❌ No | ❌ No |
| **Global command after dev install** | ✅ Yes | ✅ Yes | ✅ Yes |
| **Restart needed after changes** | ❌ No | ✅ Yes | ✅ Yes + compile |
| **Installation command** | `./setup.sh install --dev` | `./setup.sh --dev` | `./setup.sh --dev` |
| **Hook location** | `src/package_name/app_hooks.py` | `app_hooks.js` | `app_hooks.ts` |

## Real-World Examples

### Text Processing Tool
```yaml
# goobits.yaml
package_name: text-processor
command_name: textproc
display_name: "Text Processor"

cli:
  name: textproc
  tagline: "Process text files with ease"
  commands:
    process:
      desc: "Process text file"
      is_default: true  # Makes this the default command
      args:
        - name: text
          desc: "Text to process"
          nargs: "*"
      options:
        - name: uppercase
          short: u
          type: flag
          desc: "Convert to uppercase"
        - name: output
          short: o
          desc: "Output file"
```

```python
# src/text_processor/app_hooks.py
import click
import sys

def on_process(text, uppercase, output):
    # Handle stdin input automatically
    if not text and not sys.stdin.isatty():
        text = [sys.stdin.read().strip()]
    
    if not text:
        click.echo("Error: No text provided", err=True)
        return
    
    content = " ".join(text)
    if uppercase:
        content = content.upper()
    
    if output:
        with open(output, 'w') as f:
            f.write(content)
        click.echo(f"Written to {output}")
    else:
        click.echo(content)
```

```bash
# Usage examples:
textproc "hello world" --uppercase        # Direct text
echo "hello world" | textproc --uppercase # Pipe input
cat file.txt | textproc -u -o output.txt  # Process file
```

### API Client Tool
```yaml
# goobits.yaml for an API client
package_name: weather-cli
command_name: weather
display_name: "Weather CLI"

installation:
  extras:
    apt: ["curl"]  # System dependencies handled automatically

cli:
  name: weather
  tagline: "Get weather information"
  commands:
    current:
      desc: "Get current weather"
      is_default: true
      args:
        - name: city
          desc: "City name"
          required: true
      options:
        - name: api-key
          desc: "API key for weather service"
        - name: format
          short: f
          choices: ["json", "text"]
          default: "text"
          desc: "Output format"
```

## Configuration Reference

### Essential Configuration
```yaml
# Required fields
package_name: my-package        # Package name (used by pip/pipx)
command_name: mycli            # Command users type
display_name: "My CLI Tool"    # Human-readable name
description: "What it does"    # Brief description

# Python requirements
python:
  minimum_version: "3.8"      # Minimum Python version
  maximum_version: "3.12"     # Maximum (optional)

# Installation with automatic dependency management
installation:
  pypi_name: my-package        # Package name on PyPI
  development_path: "."        # Path for development install
  extras:
    python: ["dev", "test"]    # Python extras from pyproject.toml
    apt: ["git", "curl"]       # System packages (installed automatically)
```

### CLI Commands Structure
```yaml
cli:
  name: mycli
  tagline: "One-line description"
  commands:
    mycommand:
      desc: "Command description"
      is_default: true          # Makes this the default command
      args:
        - name: input
          desc: "Input parameter"
          nargs: "*"            # Multiple arguments
          required: true
      options:
        - name: verbose
          short: v
          type: flag            # Boolean flag
          desc: "Verbose output"
        - name: output
          short: o
          type: str
          desc: "Output file"
          default: "output.txt"
        - name: format
          short: f
          choices: ["json", "yaml", "text"]
          default: "text"
          desc: "Output format"
```

### Installation Customization
```yaml
installation:
  pypi_name: my-package-name   # Name on PyPI (if different)
  development_path: "."        # Path for dev install

validation:
  check_disk_space: true       # Check available disk space
  minimum_disk_space_mb: 100   # Minimum MB required

messages:
  install_success: |
    🎉 My CLI has been installed!
    Get started with: mycli --help
    
  install_dev_success: |
    🚀 Development mode active!
    Your code changes are live - no reinstall needed.
```

## Troubleshooting

### Common Issues

**"Command not found after install"**
```bash
# Fix PATH issue
pipx ensurepath
source ~/.bashrc  # or restart terminal
```

**"Changes not reflected"**
```bash
# Make sure you're using dev install
./setup.sh install --dev
# Check installation type
pipx list | grep your-package
```

**"Failed to load plugin loader"**
```bash
# This is fixed in latest version
pipx upgrade goobits-cli
cd your-project && goobits build && ./setup.sh upgrade
```

**"Module not found during development"**
```bash
# Reinstall in development mode
./setup.sh uninstall
./setup.sh install --dev
```

### Development Tips

**Quick Testing**
```bash
# Test CLI generation without install
goobits build --output-dir /tmp/test-cli
python /tmp/test-cli/cli.py --help
```

**Debug App Hooks**
```python
# Add debugging to app_hooks.py
import click

def on_mycommand(*args, **kwargs):
    click.echo(f"DEBUG: args={args}, kwargs={kwargs}")
    # Your actual logic here
```

**Plugin Development**
```python
# Create plugins/my_plugin.py
def register_plugin(cli_group):
    @cli_group.command()
    def myplugin():
        """My custom plugin command"""
        click.echo("Plugin works!")
```

## Advanced Features

### Pipe Support (Automatic)
All Goobits CLIs support piping automatically:
```bash
echo "input" | mycli           # Works automatically
cat file.txt | mycli process   # Pipe to specific command  
mycli generate | mycli format  # Chain commands
```

### Rich Terminal Interface
Goobits CLIs include rich formatting automatically:
- Colored help text with emoji icons
- Organized command groups
- Professional error messages
- Progress indicators

### Plugin System
```bash
# Plugin directories (searched automatically):
~/.config/goobits/my-cli/plugins/
./plugins/
```

## Node.js & TypeScript Deep Dive

### Generated File Structure

When you run `goobits build` with Node.js or TypeScript, you get:

```
my-awesome-cli/
├── index.js (or index.ts)    # Main CLI entry point
├── package.json              # NPM package configuration  
├── bin/cli.js               # Global command executable
├── app_hooks.js             # Your business logic
├── tsconfig.json            # TypeScript config (TS only)
├── README.md                # Auto-generated documentation
└── .gitignore               # Node.js specific ignores
```

### Advanced Node.js CLI Example

```yaml
# goobits.yaml - Production Node.js API client
language: nodejs
package_name: api-client
command_name: apicli
display_name: "API Client"
description: "Professional REST API client with authentication"

installation:
  extras:
    npm: ["commander@^11.1.0", "chalk@^5.3.0", "axios@^1.6.0", "dotenv@^16.3.0"]

cli:
  name: apicli
  tagline: "Professional REST API client"
  version: "2.1.0"
  options:
    - name: config
      short: c
      type: str
      desc: "Config file path"
      default: ".env"
    - name: verbose
      short: v
      type: flag
      desc: "Verbose output"
  commands:
    auth:
      desc: "Authentication commands"
      subcommands:
        login:
          desc: "Login with API credentials"
          options:
            - name: username
              short: u
              type: str
              desc: "Username"
            - name: save
              type: flag
              desc: "Save credentials"
        logout:
          desc: "Logout and clear credentials"
    get:
      desc: "GET request to API endpoint"
      args:
        - name: endpoint
          desc: "API endpoint path"
          required: true
      options:
        - name: headers
          short: H
          type: str
          desc: "Custom headers (JSON)"
        - name: output
          short: o
          type: str
          desc: "Save response to file"
    post:
      desc: "POST request with data"
      args:
        - name: endpoint
          desc: "API endpoint path"
          required: true
        - name: data
          desc: "JSON data to send"
          required: true
      options:
        - name: file
          short: f
          type: flag
          desc: "Read data from file"
```

```javascript
// app_hooks.js - Professional Node.js implementation
import chalk from 'chalk';
import axios from 'axios';
import { readFileSync, writeFileSync } from 'fs';
import { config } from 'dotenv';

// Load environment variables
config();

const API_BASE = process.env.API_BASE || 'https://api.example.com';
let authToken = process.env.API_TOKEN;

export async function onAuthLogin(args) {
    const { username, save, verbose } = args;
    
    if (verbose) console.log(chalk.blue('Authenticating...'));
    
    try {
        const response = await axios.post(`${API_BASE}/auth/login`, {
            username,
            password: process.env.API_PASSWORD
        });
        
        authToken = response.data.token;
        
        if (save) {
            writeFileSync('.env', `API_TOKEN=${authToken}\n`, { flag: 'a' });
            console.log(chalk.green('✅ Credentials saved'));
        }
        
        console.log(chalk.green('✅ Login successful'));
        return { success: true, token: authToken };
    } catch (error) {
        console.error(chalk.red(`❌ Login failed: ${error.response?.data?.message || error.message}`));
        process.exit(1);
    }
}

export async function onGet(args) {
    const { endpoint, headers, output, verbose } = args;
    
    if (!authToken) {
        console.error(chalk.red('❌ Not authenticated. Run: apicli auth login'));
        process.exit(1);
    }
    
    try {
        const config = {
            headers: { 
                Authorization: `Bearer ${authToken}`,
                ...(headers ? JSON.parse(headers) : {})
            }
        };
        
        if (verbose) console.log(chalk.blue(`GET ${API_BASE}${endpoint}`));
        
        const response = await axios.get(`${API_BASE}${endpoint}`, config);
        
        if (output) {
            writeFileSync(output, JSON.stringify(response.data, null, 2));
            console.log(chalk.green(`✅ Response saved to ${output}`));
        } else {
            console.log(JSON.stringify(response.data, null, 2));
        }
        
        return response.data;
    } catch (error) {
        console.error(chalk.red(`❌ Request failed: ${error.response?.data?.message || error.message}`));
        process.exit(1);
    }
}

export async function onPost(args) {
    const { endpoint, data, file, verbose } = args;
    
    let payload;
    if (file) {
        payload = JSON.parse(readFileSync(data, 'utf8'));
    } else {
        payload = JSON.parse(data);
    }
    
    try {
        const config = {
            headers: { 
                Authorization: `Bearer ${authToken}`,
                'Content-Type': 'application/json'
            }
        };
        
        if (verbose) console.log(chalk.blue(`POST ${API_BASE}${endpoint}`));
        
        const response = await axios.post(`${API_BASE}${endpoint}`, payload, config);
        console.log(JSON.stringify(response.data, null, 2));
        
        return response.data;
    } catch (error) {
        console.error(chalk.red(`❌ Request failed: ${error.response?.data?.message || error.message}`));
        process.exit(1);
    }
}
```

### TypeScript CLI with Advanced Types

```typescript
// app_hooks.ts - Type-safe implementation
import chalk from 'chalk';
import axios, { AxiosResponse } from 'axios';
import { readFileSync, writeFileSync } from 'fs';

interface CommandArgs {
    [key: string]: any;
    verbose?: boolean;
}

interface AuthLoginArgs extends CommandArgs {
    username: string;
    save?: boolean;
}

interface ApiResponse<T = any> {
    data: T;
    message?: string;
    success: boolean;
}

interface LoginResponse {
    token: string;
    user: {
        id: string;
        username: string;
        role: string;
    };
}

class APIClient {
    private baseURL: string;
    private token?: string;

    constructor(baseURL: string, token?: string) {
        this.baseURL = baseURL;
        this.token = token;
    }

    private getHeaders(customHeaders?: Record<string, string>) {
        return {
            Authorization: this.token ? `Bearer ${this.token}` : '',
            'Content-Type': 'application/json',
            ...customHeaders
        };
    }

    async login(username: string, password: string): Promise<LoginResponse> {
        const response: AxiosResponse<ApiResponse<LoginResponse>> = await axios.post(
            `${this.baseURL}/auth/login`,
            { username, password }
        );
        
        this.token = response.data.data.token;
        return response.data.data;
    }

    async get<T = any>(endpoint: string, headers?: Record<string, string>): Promise<T> {
        const response: AxiosResponse<T> = await axios.get(
            `${this.baseURL}${endpoint}`,
            { headers: this.getHeaders(headers) }
        );
        return response.data;
    }

    async post<T = any>(endpoint: string, data: any): Promise<T> {
        const response: AxiosResponse<T> = await axios.post(
            `${this.baseURL}${endpoint}`,
            data,
            { headers: this.getHeaders() }
        );
        return response.data;
    }
}

const client = new APIClient(
    process.env.API_BASE || 'https://api.example.com',
    process.env.API_TOKEN
);

export async function onAuthLogin(args: AuthLoginArgs): Promise<{ success: boolean; token: string }> {
    const { username, save, verbose } = args;
    
    if (verbose) console.log(chalk.blue('Authenticating...'));
    
    try {
        const result = await client.login(username, process.env.API_PASSWORD || '');
        
        if (save) {
            writeFileSync('.env', `API_TOKEN=${result.token}\n`, { flag: 'a' });
            console.log(chalk.green('✅ Credentials saved'));
        }
        
        console.log(chalk.green(`✅ Welcome, ${result.user.username}!`));
        return { success: true, token: result.token };
    } catch (error: any) {
        console.error(chalk.red(`❌ Login failed: ${error.response?.data?.message || error.message}`));
        process.exit(1);
    }
}
```

### Node.js vs TypeScript Benefits

| Feature | Node.js | TypeScript |
|---------|---------|------------|
| **Type Safety** | Runtime only | Compile-time + Runtime |
| **IDE Support** | Good | Excellent (autocomplete, refactoring) |
| **Development Speed** | Fast iteration | Slower build, better DX |
| **Error Detection** | Runtime | Compile-time |
| **Bundle Size** | Smaller | Transpiled to JS |
| **Learning Curve** | JavaScript knowledge | JavaScript + TypeScript |

### Publishing Your CLI

**Node.js CLI:**
```bash
# Build and test
npm run build
npm test

# Publish to npm
npm version patch
npm publish

# Install globally
npm install -g my-awesome-cli
```

**TypeScript CLI:**
```bash
# Build TypeScript
npx tsc

# Test compiled output  
node dist/index.js --help

# Publish (publishes compiled JS)
npm publish

# Install and use
npm install -g my-awesome-cli
awesome --help
```

### Integration Examples
```bash
# Text processing pipeline
echo "fix this grammar" | ttt | tts        # Fix grammar, then speak
stt recording.wav | ttt "summarize" | tts  # Transcribe, summarize, speak

# API workflow  
mycli fetch-data | jq '.results[]' | mycli process

# Node.js CLI chaining
apicli get /users | jq '.[].id' | xargs -I {} apicli get /users/{}
```

## Next Steps

1. **Study existing examples**: Look at TTT, TTS, STT in the Goobits ecosystem
2. **Read the generated code**: Check out generated files after building
3. **Explore multi-language**: Try Node.js and TypeScript CLIs (see [Node.js Guide](docs/nodejs_guide.md))
4. **Explore advanced config**: Add subcommands, command groups, custom validation
5. **Create plugins**: Extend functionality with the plugin system
6. **Share your CLI**: Publish to PyPI (Python) or npm (Node.js/TypeScript)

## Future Development

Check out our [design proposals](docs/proposals/) for upcoming features:
- **Rust Support** - High-performance CLI generation
- **Universal DSL** - Write once, generate for any language
- **Testing Framework** - YAML-based testing for generated CLIs
- **Config Standardization** - Unified configuration across all goobits projects

---

**🚀 Ready to build professional CLIs with minimal boilerplate? Start with `goobits build` and let the framework handle the complexity!**