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
      help: "Greets a person with their name"
      arguments:
        - name: name
          help: "Name of the person to greet"
          type: string
          required: true
      options:
        - name: --excited
          help: "Add excitement to the greeting"
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

**Node.js/TypeScript** (`src/hooks.js` or `src/hooks.ts`):
```javascript
export async function onGreet({ name, excited }) {
    let greeting = `Hello, ${name}!`;
    if (excited) {
        greeting += " 🎉";
    }
    console.log(greeting);
}
```

**Rust** (`src/hooks.rs`):
```rust
use anyhow::Result;

pub fn on_greet(matches: &clap::ArgMatches) -> Result<()> {
    let name = matches.get_one::<String>("name").unwrap();
    let excited = matches.get_flag("excited");
    
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
# Install your CLI
./setup.sh

# Run your CLI
awesome greet "World" --excited
# Output: Hello, World! 🎉
```

## 📖 Documentation

### Configuration Schema

The `goobits.yaml` file supports comprehensive CLI configuration:

```yaml
# Required fields
package_name: string          # Package identifier
command_name: string          # CLI command name
display_name: string          # Display name for documentation
description: string           # Package description

# Optional configuration
language: python|nodejs|typescript|rust  # Target language (default: python)
cli_output_path: string       # Output path for generated CLI
cli_hooks: string            # Path to hooks file

# Language-specific settings
python:
  minimum_version: "3.8"
  maximum_version: "3.13"

# Installation configuration
installation:
  pypi_name: string
  development_path: "."
  extras:
    python: ["dev", "test"]
    apt: ["git", "curl"]
    npm: ["prettier"]

# CLI structure
cli:
  name: string
  version: string
  tagline: string
  commands:
    command_name:
      desc: string
      help: string
      arguments:
        - name: string
          help: string
          type: string|number|boolean
          required: boolean
          default: any
      options:
        - name: string
          help: string
          type: string|number|boolean
          default: any
      subcommands:
        # Nested command structure
```

### Advanced Features

#### Universal Template System

Generate consistent CLIs across all languages:

```bash
goobits build --universal-templates
```

#### Interactive Mode

All generated CLIs support interactive mode:

```bash
my-cli --interactive
```

#### Shell Completions

Generated setup scripts include completion installation:

```bash
./setup.sh --completions
```

#### Performance Optimization

The framework generates highly optimized CLIs with:
- Lazy loading for faster startup
- Minimal dependencies
- Efficient command routing
- Smart caching strategies

## 🏗️ Project Structure

```
goobits-cli/
├── src/goobits_cli/
│   ├── main.py              # Entry point
│   ├── builder.py           # Build orchestration
│   ├── schemas.py           # Configuration validation
│   ├── generators/         # Language-specific generators
│   │   ├── python.py
│   │   ├── nodejs.py
│   │   ├── typescript.py
│   │   └── rust.py
│   ├── templates/          # Language templates
│   └── universal/          # Universal template system
├── tests/                  # Comprehensive test suite
├── performance/           # Performance benchmarks
└── examples/             # Example configurations
```

## 🧪 Development

### Setting Up Development Environment

```bash
# Clone the repository
git clone https://github.com/goobits/goobits-cli.git
cd goobits-cli

# Install in development mode
pip install -e .[dev,test]

# Run tests
pytest

# Run linting
ruff check src/
mypy src/goobits_cli/
```

### Running Tests

```bash
# All tests
pytest

# Unit tests only
pytest tests/unit/

# With coverage
pytest --cov=goobits_cli
```

### Performance Testing

```bash
python performance/performance_suite.py
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [Click](https://click.palletsprojects.com/) (Python)
- Powered by [Commander.js](https://github.com/tj/commander.js) (Node.js)
- Enhanced by [Clap](https://github.com/clap-rs/clap) (Rust)
- Styled with [Rich](https://github.com/Textualize/rich)

## 📞 Support

- **Documentation**: [https://goobits.dev/docs](https://goobits.dev/docs)
- **Issues**: [GitHub Issues](https://github.com/goobits/goobits-cli/issues)
- **Discussions**: [GitHub Discussions](https://github.com/goobits/goobits-cli/discussions)

---

**Made with ❤️ by the Goobits Team**