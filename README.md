# 🎯 Goobits CLI Framework

Generate command-line interfaces for Python, Node.js, TypeScript, or Rust from YAML configuration files.

## ✨ Key Features

- **⚡ Multi-Language Support** - Generate CLIs for Python, Node.js, TypeScript, or Rust from one config
- **📦 Minimal Output** - Produces 3-4 files per language with no unnecessary clutter
- **🛡️ Safe Integration** - Preserves existing package.json/Cargo.toml files during generation
- **🎨 Rich Interfaces** - Includes colors, progress indicators, and interactive modes
- **🔄 Template System** - Universal templates ensure consistent behavior across languages
- **⚙️ Self-Hosting** - Framework generates its own CLI from configuration

## 🚀 Quick Start

```bash
# Install
pip install goobits-cli          # Standard installation
pipx install goobits-cli         # Isolated installation (recommended)

# Create and build CLI
goobits init my-cli              # Generate initial configuration
goobits build                    # Generate CLI files
./setup.sh install --dev        # Install generated CLI

# Use generated CLI
my-cli --help                   # View available commands
```

## ⚙️ Configuration

```yaml
# goobits.yaml
package_name: my-cli
command_name: mycli
display_name: "My CLI"
description: "Command-line tool"
language: python      # Options: python, nodejs, typescript, rust

cli:
  name: mycli
  version: "1.0.0"
  commands:
    greet:
      desc: "Display greeting message"
      args:
        - name: name
          desc: "Name to greet"
          required: false
          default: "World"
      options:
        - name: --uppercase
          desc: "Display in uppercase"
          type: boolean
```

Generated CLI includes help text, argument validation, and structured output formatting.

## 🌐 Language Support

Target multiple languages from the same configuration:

```yaml
# Python - Click framework with rich terminal features
language: python

# Node.js - Commander.js with ES6 modules  
language: nodejs

# TypeScript - Commander.js with type definitions
language: typescript

# Rust - Clap framework with compiled binaries
language: rust
```

Each language generates idiomatic code with framework-specific patterns and dependencies.

**[📖 Language Guide](docs/languages.md)**

## 📦 Generated Files

Output structure per language:

| Language | Files | Description |
|----------|-------|-------------|
| **Python** | 3 files | `cli.py`, `cli_hooks.py`, `setup.sh` |
| **Node.js** | 3 files | `cli.mjs`, `cli_hooks.mjs`, `setup.sh` |
| **TypeScript** | 4 files | `cli.ts`, `cli_hooks.ts`, `cli_types.d.ts`, `setup.sh` |
| **Rust** | 4 files | `src/cli.rs`, `src/cli_hooks.rs`, `Cargo.toml`, `setup.sh` |

Framework preserves existing README files and merges dependencies into existing manifest files.

**[📖 File Generation Details](docs/file-generation.md)**

## 🛠️ Commands

```bash
# Core workflow
goobits init my-cli          # Create initial configuration
goobits validate             # Validate configuration syntax
goobits build               # Generate CLI files

# Additional commands
goobits migrate config.yaml  # Upgrade configuration format
goobits serve ./packages    # Serve local PyPI index
goobits upgrade             # Update goobits-cli version
```

**[📖 Command Reference](docs/commands.md)**

## 🎨 Features

Generated CLIs include:

```bash
# Interactive mode
mycli --interactive          # Enter interactive shell

# Shell completions  
mycli --install-completion   # Install for current shell (bash, zsh, fish)

# Rich output formatting
mycli status --json          # Structured output
mycli deploy --progress      # Progress indicators
```

**Hook System**: Business logic implemented in language-specific hook files:
- `cli_hooks.py` (Python) • `cli_hooks.mjs` (Node.js) • `cli_hooks.ts` (TypeScript) • `cli_hooks.rs` (Rust)

**Template System**: Universal templates provide consistent behavior across all supported languages.

## 📚 Documentation

- **[Configuration Reference](docs/user-guide/configuration.md)** - YAML schema and options
- **[Language Support](docs/languages.md)** - Python, Node.js, TypeScript, Rust details
- **[Command Reference](docs/commands.md)** - Available commands and arguments
- **[File Generation](docs/file-generation.md)** - Output structure and file contents
- **[Examples](examples/)** - Sample configurations and generated CLIs
- **[Troubleshooting](docs/user-guide/troubleshooting.md)** - Common issues and solutions

## 🧪 Development

```bash
# Setup development environment
git clone https://github.com/goobits/goobits-cli
cd goobits-cli
pip install -e .[dev,test]

# Run tests
pytest src/tests/
pytest --cov=goobits_cli       # With coverage
mypy src/goobits_cli/          # Type checking

# Code formatting
black src/
flake8 src/
```

- **[Contributing Guide](CONTRIBUTING.md)** - Development setup and contribution process
- **[Architecture Guide](CODEMAP.md)** - Codebase structure and components

## ⚡ Performance

Framework and generated CLI performance characteristics:

```bash
# Generation time
time goobits build              # ~200ms complete CLI generation

# Generated CLI performance  
time mycli --help              # <100ms startup time
```

- **Memory Usage**: <10MB typical runtime memory
- **Startup Time**: <100ms for generated CLIs
- **Generation Speed**: ~200ms for complete multi-file CLI generation

Optimizations include lazy loading, template caching, and minimal runtime dependencies.

## 📝 License

MIT License - see [LICENSE](LICENSE) for details

## 💡 Support

- **Issues**: [GitHub Issues](https://github.com/goobits/goobits-cli/issues)
- **Discussions**: [GitHub Discussions](https://github.com/goobits/goobits-cli/discussions)