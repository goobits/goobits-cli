# Goobits CLI Framework

[![Version](https://img.shields.io/badge/version-2.0.0-blue.svg)](https://github.com/goobits/cli)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://python.org)
[![Node.js](https://img.shields.io/badge/node-18+-green.svg)](https://nodejs.org)
[![TypeScript](https://img.shields.io/badge/typescript-5.0+-blue.svg)](https://typescriptlang.org)

**Generate professional command-line interfaces from YAML configuration in Python, Node.js, or TypeScript**

Goobits CLI Framework is a production-ready, multi-language CLI generator that transforms simple YAML configurations into sophisticated command-line applications. With support for Python, Node.js, and TypeScript, along with universal templates and comprehensive performance validation, it's the fastest way to build professional CLIs.

## ✨ Key Features

- 🌍 **Multi-Language Support**: Generate CLIs in Python, Node.js, or TypeScript
- ⚡ **High Performance**: <100ms startup times across all languages
- 🔧 **Universal Templates**: Consistent behavior with language-specific optimizations
- 📋 **Simple YAML Config**: Define your entire CLI structure in one file
- 🎯 **Production Ready**: 95%+ test coverage with comprehensive validation
- 🚀 **Self-Hosting**: Framework builds its own CLI using itself
- 📦 **Automated Setup**: One-command installation with dependency management

## 🚀 Quick Start

### Installation

```bash
# Install Goobits CLI Framework
pipx install goobits-cli

# Verify installation
goobits --version
```

### Your First CLI in 3 Minutes

1. **Create a project directory:**
   ```bash
   mkdir my-awesome-cli
   cd my-awesome-cli
   ```

2. **Create `goobits.yaml` configuration:**
   ```yaml
   # Choose your language
   language: python  # or nodejs, typescript
   
   # Project metadata
   package_name: my-awesome-cli
   command_name: awesome
   display_name: "Awesome CLI"
   description: "A CLI that does awesome things"
   
   # CLI structure
   cli:
     name: awesome
     version: "1.0.0"
     commands:
       greet:
         desc: "Greet someone"
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
   # Generate with universal templates (recommended)
   goobits build --universal-templates
   
   # Or use legacy templates
   goobits build
   ```

4. **Add your business logic:**

   **Python (`app_hooks.py`):**
   ```python
   def on_greet(name, style, **kwargs):
       styles = {
           'friendly': f"Hello {name}! 👋",
           'formal': f"Good day, {name}.",
           'excited': f"🎉 HEY {name.upper()}! 🎉"
       }
       print(styles[style])
   ```

   **Node.js (`app_hooks.js`):**
   ```javascript
   export async function onGreet(args) {
       const { name, style } = args;
       const styles = {
           friendly: `Hello ${name}! 👋`,
           formal: `Good day, ${name}.`,
           excited: `🎉 HEY ${name.toUpperCase()}! 🎉`
       };
       console.log(styles[style]);
   }
   ```

   **TypeScript (`app_hooks.ts`):**
   ```typescript
   interface GreetArgs {
       name: string;
       style: 'friendly' | 'formal' | 'excited';
   }
   
   export async function onGreet(args: GreetArgs): Promise<void> {
       const { name, style } = args;
       const styles: Record<string, string> = {
           friendly: `Hello ${name}! 👋`,
           formal: `Good day, ${name}.`,
           excited: `🎉 HEY ${name.toUpperCase()}! 🎉`
       };
       console.log(styles[style]);
   }
   ```

5. **Install and test:**
   ```bash
   # Install dependencies and create global command
   ./setup.sh --dev
   
   # Test your CLI
   awesome greet "World" --style excited
   # Output: 🎉 HEY WORLD! 🎉
   ```

## 🏗️ Architecture Overview

```
goobits.yaml → Goobits Build → Language-Specific Output → Install → Working CLI

Python:     cli.py + setup.sh → pipx install
Node.js:    cli.js + package.json → npm install  
TypeScript: cli.ts + tsconfig.json → npm install
```

### Generated Project Structure

**Python:**
```
my-cli/
├── cli.py              # Main CLI implementation
├── app_hooks.py        # Your business logic
├── setup.sh            # Installation script
└── README.md           # Auto-generated docs
```

**Node.js/TypeScript:**
```
my-cli/
├── index.js/ts         # Main CLI implementation  
├── package.json        # npm package configuration
├── bin/cli.js          # Executable entry point
├── app_hooks.js/ts     # Your business logic
├── setup.sh            # Installation script
└── README.md           # Auto-generated docs
```

## 🎯 Language Support

| Feature | Python | Node.js | TypeScript |
|---------|--------|---------|------------|
| **Basic CLI** | ✅ | ✅ | ✅ |
| **Subcommands** | ✅ | ✅ | ✅ |
| **Arguments & Options** | ✅ | ✅ | ✅ |
| **Help Generation** | ✅ | ✅ | ✅ |
| **Config Management** | ✅ | ✅ | ✅ |
| **Type Safety** | ⚠️ | ❌ | ✅ |
| **Startup Speed** | ~80ms | ~60ms | ~70ms |
| **Memory Usage** | ~25MB | ~35MB | ~40MB |

## ⚡ Performance Standards

Goobits CLI Framework is built for performance:

- **<100ms startup time** across all languages
- **<50MB memory usage** for typical CLIs
- **95%+ test coverage** with comprehensive validation
- **Production-grade** error handling and logging

### Benchmark Results

```bash
# Run performance validation
python performance/performance_suite.py

# Language-specific benchmarks
Language    Startup Time    Memory Usage    Grade
Python      78ms           24MB            A+
Node.js     53ms           31MB            A+  
TypeScript  66ms           38MB            A
```

## 📚 Documentation

- **[Architecture Guide](docs/architecture.md)** - System design and components
- **[Universal Templates Guide](docs/universal_templates_guide.md)** - Using the universal template system
- **[Node.js & TypeScript Guide](docs/nodejs_guide.md)** - JavaScript/TypeScript development
- **[Performance Guide](docs/performance_guide.md)** - Optimization and benchmarking
- **[Migration Guide](docs/migration_guide.md)** - Upgrading from previous versions
- **[API Reference](docs/api_reference.md)** - Generator interfaces and usage
- **[Examples](docs/examples/)** - Working examples for all languages
- **[Troubleshooting](docs/troubleshooting.md)** - Common issues and solutions

## 🔧 Configuration Reference

### Complete `goobits.yaml` Example

```yaml
# Language selection (required)
language: python  # or nodejs, typescript

# Project metadata
package_name: my-cli
command_name: mycli
display_name: "My CLI"
description: "What your CLI does"

# Python installation (required for all languages)
python:
  minimum_version: "3.8"

# Dependencies
dependencies:
  python: ["click>=8.0.0", "rich>=13.0.0"]  # Python only
  
installation:
  extras:
    npm: ["chalk@5.3.0", "ora@8.0.1"]       # Node.js/TypeScript only

# CLI structure
cli:
  name: mycli
  tagline: "Short description"
  version: "1.0.0"
  
  # Global options
  options:
    - name: verbose
      short: v
      desc: "Verbose output"
      type: flag
    - name: config
      short: c
      desc: "Config file"
      type: str
  
  # Commands
  commands:
    # Simple command
    init:
      desc: "Initialize project"
      args:
        - name: name
          desc: "Project name"
          required: true
      options:
        - name: template
          desc: "Template type"
          choices: ["basic", "advanced"]
          default: "basic"
    
    # Command with subcommands
    config:
      desc: "Manage configuration"
      subcommands:
        get:
          desc: "Get config value"
          args:
            - name: key
              desc: "Config key"
              required: true
        set:
          desc: "Set config value"
          args:
            - name: key
              desc: "Config key"
              required: true
            - name: value
              desc: "Config value"
              required: true
```

### Option Types

- **flag**: Boolean (`--verbose`)
- **str**: String value (`--name "John"`)
- **int**: Integer value (`--port 3000`)
- **float**: Decimal value (`--rate 0.5`)
- **count**: Incremental counter (`-vvv`)

## 🛠️ Advanced Usage

### Universal Template System

Use the universal template system for consistent behavior across languages:

```bash
# Generate with universal templates
goobits build --universal-templates

# Fallback to legacy templates if needed
goobits build
```

### Performance Monitoring

Monitor and validate CLI performance:

```bash
# Full performance suite
python performance/performance_suite.py

# Quick startup validation
python performance/startup_validator.py --target 100

# Memory usage analysis
python performance/memory_profiler.py
```

### Development Workflow

```bash
# Install in development mode
./setup.sh --dev

# Run tests
pytest src/tests/

# Type checking (Python)
mypy src/goobits_cli/

# Linting
ruff check src/
```

## 🤝 Contributing

We welcome contributions! Here's how to get started:

1. **Fork the repository**
2. **Create a feature branch** (`git checkout -b feature/amazing-feature`)
3. **Make your changes** with tests
4. **Run the test suite** (`pytest`)
5. **Commit your changes** (`git commit -am 'Add amazing feature'`)
6. **Push to the branch** (`git push origin feature/amazing-feature`)
7. **Open a Pull Request**

### Development Setup

```bash
# Clone repository
git clone https://github.com/goobits/cli.git
cd goobits-cli

# Install in development mode
./setup.sh --dev

# Run tests
pytest src/tests/

# Build self-hosted CLI
goobits build
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [Click](https://click.palletsprojects.com/) for Python CLIs
- Powered by [Commander.js](https://github.com/tj/commander.js/) for Node.js CLIs
- Type safety with [TypeScript](https://www.typescriptlang.org/)
- Performance validation with comprehensive benchmarking
- Self-hosted architecture using Goobits itself

## 🚀 What's Next

- **Enhanced Type Safety**: Improved Python typing support
- **Plugin System**: Extensible architecture for community plugins  
- **Interactive Mode**: REPL-style command interaction
- **Rust Support**: High-performance compiled binaries (in development)
- **Web Interface**: Browser-based CLI builder

---

**Generate professional CLIs in minutes, not hours. Choose your language, define your structure, and let Goobits handle the rest.**

[![Get Started](https://img.shields.io/badge/Get%20Started-Now-blue.svg?style=for-the-badge)](https://github.com/goobits/cli)