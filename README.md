# Goobits CLI Framework

[![PyPI version](https://badge.fury.io/py/goobits-cli.svg)](https://badge.fury.io/py/goobits-cli)
[![Python Support](https://img.shields.io/pypi/pyversions/goobits-cli.svg)](https://pypi.org/project/goobits-cli/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Build professional command-line tools with YAML configuration. Generate production-ready CLIs in Python, Node.js, TypeScript, or Rust from a single configuration file.

## ✨ Features

- **🚀 Multi-Language Support**: Generate CLIs in Python, Node.js, TypeScript, or Rust
- **📝 YAML Configuration**: Define your entire CLI structure in a simple YAML file
- **🎯 Type Safety**: Full type checking and validation across all languages
- **⚡ High Performance**: Optimized startup times (<100ms) and minimal memory usage
- **🔧 Rich Features**: Interactive mode, shell completions, plugins, and more
- **🏗️ Universal Templates**: Single template system generates for all languages
- **📦 Easy Distribution**: Generated CLIs include setup scripts and package configs

## 📦 Installation

### From PyPI (Recommended)

```bash
pip install goobits-cli
```

### Using pipx (Isolated Environment)

```bash
pipx install goobits-cli
```

### From Source

```bash
git clone https://github.com/goobits/goobits-cli.git
cd goobits-cli
pip install -e .
```

## 🚀 Quick Start

### 1. Create a Configuration File

Create a `goobits.yaml` file:

```yaml
package_name: my-awesome-cli
command_name: awesome
display_name: "My Awesome CLI"
description: "A CLI that does awesome things"
language: python  # or nodejs, typescript, rust

cli:
  name: awesome
  version: "1.0.0"
  tagline: "Make awesome things happen"
  commands:
    greet:
      desc: "Greet someone"
      args:
        - name: name
          desc: "Name of the person to greet"
          type: string
          required: true
      options:
        - name: --excited
          desc: "Add excitement to the greeting"
          type: boolean
          default: false
```

### 2. Generate Your CLI

```bash
goobits build
```

This generates a complete CLI application with:
- Main CLI script (`cli.py`, `cli.js`, `cli.ts`, or `src/main.rs`)
- Hook file for business logic implementation
- Setup/installation script
- Package configuration (`setup.py`, `package.json`, or `Cargo.toml`)
- Shell completion scripts
- README documentation

### 3. Implement Your Business Logic

Edit the generated hooks file:

**Python** (`app_hooks.py`):
```python
def on_greet(name, excited=False):
    greeting = f"Hello, {name}!"
    if excited:
        greeting += " 🎉"
    print(greeting)
```

**Node.js** (`src/hooks.js`):
```javascript
export async function onGreet({ name, excited }) {
    let greeting = `Hello, ${name}!`;
    if (excited) {
        greeting += " 🎉";
    }
    console.log(greeting);
}
```

**TypeScript** (`src/hooks.ts`):
```typescript
interface GreetArgs {
    name: string;
    excited?: boolean;
}

export async function onGreet({ name, excited }: GreetArgs): Promise<void> {
    let greeting = `Hello, ${name}!`;
    if (excited) {
        greeting += " 🎉";
    }
    console.log(greeting);
}
```

**Rust** (`src/hooks.rs`):
```rust
pub fn on_greet(name: &str, excited: bool, _verbose: bool, _config: Option<&str>) -> Result<(), Box<dyn std::error::Error>> {
    let mut greeting = format!("Hello, {}!", name);
    if excited {
        greeting.push_str(" 🎉");
    }
    println!("{}", greeting);
    Ok(())
}
```

### 4. Install and Run

```bash
# Python
./setup.sh install
awesome greet "World" --excited

# Node.js/TypeScript
npm install
npm link
awesome greet "World" --excited

# Rust
cargo install --path .
awesome greet "World" --excited
```

## 📚 Complete Working Example

Here's a real-world example of a file processing CLI:

```yaml
# goobits.yaml
package_name: file-processor
command_name: fp
display_name: "File Processor CLI"
description: "Process and transform files efficiently"
language: python

cli:
  name: fp
  version: "1.0.0"
  tagline: "Your file processing toolkit"
  commands:
    convert:
      desc: "Convert file formats"
      args:
        - name: input
          desc: "Input file path"
          type: string
          required: true
        - name: output
          desc: "Output file path"
          type: string
          required: true
      options:
        - name: --format
          desc: "Output format"
          type: choice
          choices: ["json", "yaml", "xml", "csv"]
          default: "json"
        - name: --pretty
          desc: "Pretty-print output"
          type: boolean
          default: false
    
    compress:
      desc: "Compress files"
      args:
        - name: files
          desc: "Files to compress"
          type: string
          nargs: "+"
          required: true
      options:
        - name: --algorithm
          short: -a
          desc: "Compression algorithm"
          type: choice
          choices: ["gzip", "bzip2", "xz", "zip"]
          default: "gzip"
        - name: --level
          short: -l
          desc: "Compression level (1-9)"
          type: integer
          default: 6
```

Generate and run:
```bash
# Generate the CLI
goobits build

# Install
./setup.sh install

# Use your new CLI
fp convert input.json output.yaml --format yaml --pretty
fp compress *.txt --algorithm gzip --level 9
fp --help
```

## 🎯 Command Line Usage

### Build Command

```bash
# Build with default settings
goobits build

# Specify custom config file
goobits build my-config.yaml

# Use universal template system
goobits build --universal-templates

# Create backups when overwriting
goobits build --backup
```

### Init Command

```bash
# Create a basic goobits.yaml
goobits init

# Use a specific template
goobits init --template advanced

# Available templates: basic, advanced, api-client, text-processor
```


## 🔧 Configuration Options

### Language Selection

```yaml
language: python      # Default
# or
language: nodejs      # Node.js with Commander.js
language: typescript  # TypeScript with type safety
language: rust        # Rust with Clap
```

### Command Types

```yaml
commands:
  simple:
    desc: "Simple command"
    
  with_args:
    desc: "Command with arguments"
    args:
      - name: file
        type: string
        required: true
        
  with_options:
    desc: "Command with options"
    options:
      - name: --verbose
        short: -v
        type: boolean
        default: false
        
  nested:
    desc: "Parent command"
    subcommands:
      child:
        desc: "Nested subcommand"
```

### Option Types

- `string`: Text input
- `integer`: Whole numbers
- `float`: Decimal numbers
- `boolean`: True/false flags
- `choice`: Limited set of values
- `path`: File/directory paths (with validation)

## 🚀 Advanced Features

### Interactive Mode

All generated CLIs support interactive mode:

```bash
# Start interactive REPL
awesome --interactive

# In the REPL
> greet World --excited
Hello, World! 🎉
> help
[Shows available commands]
> exit
```

### Shell Completions

Generate shell completions for your CLI:

```bash
# During installation
./setup.sh --completions

# Completions are generated during build
# and installed via setup.sh

# The setup script handles completions for other languages
```

### Universal Templates

Use the experimental universal template system for consistent cross-language generation:

```bash
goobits build --universal-templates
```

## 🛠️ Troubleshooting

### Common Issues

**YAML Parsing Errors**
```bash
Error: Invalid YAML at line 15: Expected indent of 2 spaces but found 3
```
Fix: Check indentation is consistent (2 spaces recommended)

**Missing Required Fields**
```bash
Error: Missing required field 'cli.name' in configuration
```
Fix: Ensure all required fields are present. See examples above.

**Language Not Supported**
```bash
Error: Language 'perl' is not supported. Choose from: python, nodejs, typescript, rust
```
Fix: Use one of the supported languages.

### Debug Mode

For detailed error messages:
```bash
# Set environment variable
export GOOBITS_DEBUG=1
goobits build

# Or use verbose flag
goobits --verbose build
```

## 📖 Documentation

- [Complete Documentation](https://github.com/goobits/goobits-cli/wiki)
- [YAML Schema Reference](https://github.com/goobits/goobits-cli/wiki/Schema)
- [Language-Specific Guides](https://github.com/goobits/goobits-cli/wiki/Languages)
- [Examples Repository](https://github.com/goobits/goobits-cli-examples)

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

Built with love using:
- [Click](https://click.palletsprojects.com/) (Python CLI framework)
- [Commander.js](https://github.com/tj/commander.js/) (Node.js CLI framework)
- [Clap](https://github.com/clap-rs/clap) (Rust CLI framework)
- [Rich](https://github.com/Textualize/rich) (Terminal formatting)

## 🚦 Project Status

**Production Ready**
- ✅ All 4 languages fully supported
- ✅ Universal template system operational
- ✅ Performance targets met (<100ms startup)
- ✅ Comprehensive test coverage (696 tests)

---

Made with ❤️ by the Goobits Team