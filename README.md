# 🎯 Goobits CLI Framework

Transform YAML into production-ready CLIs for Python, Node.js, TypeScript, or Rust. Build once, deploy everywhere.

## ✨ Key Features

- **⚡ Lightning Fast** - Generate a working CLI in under 30 seconds
- **🌐 Multi-Language** - One YAML config generates Python, Node.js, TypeScript, or Rust CLIs
- **📦 Zero Clutter** - Only 3-4 essential files generated, no bloat
- **🛡️ Safe Merging** - Smart dependency handling preserves your existing package.json/Cargo.toml
- **🎨 Rich Terminal UX** - Built-in colors, progress bars, and interactive modes
- **🔄 Self-Hosting** - Goobits uses itself to build its own CLI (meta!)

## 🚀 Quick Start

```bash
# Install globally
pip install goobits-cli          # via pip
pipx install goobits-cli         # via pipx (recommended for CLIs)

# Generate your first CLI in 30 seconds
goobits init my-awesome-cli      # Create starter config
goobits build                     # Generate CLI code
./setup.sh install --dev         # Install with dependencies

# Take it for a spin!
my-awesome-cli hello world        # Your CLI is ready!
```

## 💻 Configuration Example

```yaml
# goobits.yaml - Your entire CLI defined in one place
package_name: my-cli
command_name: mycli
display_name: "My CLI"
description: "Professional CLI tool built with Goobits"
language: python      # Switch to: nodejs, typescript, or rust

cli:
  name: mycli
  version: "1.0.0"
  tagline: "Making the command line beautiful"
  commands:
    greet:
      desc: "Greet someone with style"
      args:
        - name: name
          desc: "Person to greet"
          required: false
          default: "World"
      options:
        - name: --excited
          desc: "Add enthusiasm!"
          type: boolean
```

Run `goobits build` and get a fully-featured CLI with help text, arg validation, and beautiful formatting!

## 🌐 Multi-Language Support

Switch between languages with a single line change - same YAML config, different runtime:

```yaml
# Python (default) - Rich click interfaces with type safety
language: python

# Node.js - ES6 modules with Commander.js
language: nodejs

# TypeScript - Full type definitions and compile-time checking
language: typescript

# Rust - Blazing fast CLIs with Clap and zero runtime dependencies
language: rust
```

**[📖 Language Guide →](docs/languages.md)** - Deep dive into each language's features

## 📦 Generated Files

Clean, minimal output - no clutter, no overwrites, just what you need:

| Language | Files Generated | What You Get |
|----------|----------------|--------------|
| **Python** | 3 files | `cli.py` (consolidated), `cli_hooks.py` (your code), `setup.sh` (installer) |
| **Node.js** | 3 files | `cli.mjs` (ES6 module), `cli_hooks.mjs` (your code), `setup.sh` (installer) |
| **TypeScript** | 4 files | `cli.ts` + `cli_hooks.ts` + `cli_types.d.ts` + `setup.sh` |
| **Rust** | 4 files | `src/cli.rs` + `src/cli_hooks.rs` + `Cargo.toml` + `setup.sh` |

✨ **Smart Features**: Preserves your existing README, merges dependencies intelligently, generates relative to your config location

**[🔧 File Generation Details →](docs/file-generation.md)**

## 🛠️ CLI Commands

```bash
# Essential workflow
goobits init my-cli          # Create starter configuration
goobits validate             # Check config syntax (fast feedback)
goobits build               # Generate your CLI code

# Advanced operations  
goobits migrate old.yaml    # Upgrade configs to latest format
goobits serve ./packages    # Host local PyPI index for development
goobits upgrade             # Update goobits-cli to latest version
```

**[📖 Complete Command Reference →](docs/commands.md)**

## 🎨 Advanced Features

```bash
# Interactive REPL mode (all languages)
mycli --interactive          # Drop into interactive shell

# Shell completions (generated automatically)
mycli --install-completion   # Bash, Zsh, Fish support

# Rich terminal interfaces
mycli deploy --progress      # Progress bars and spinners
mycli config --interactive   # Interactive configuration
```

**🔧 Hook System**: Write your business logic in language-specific hook files:
- `cli_hooks.py` (Python) • `cli_hooks.mjs` (Node.js) • `cli_hooks.ts` (TypeScript) • `cli_hooks.rs` (Rust)

**⚡ Universal Templates**: Consistent behavior and features across all target languages

## 📚 Documentation & Resources

**📖 Guides**
- **[Configuration Schema](docs/user-guide/configuration.md)** - Complete YAML reference
- **[Language Guides](docs/languages.md)** - Python, Node.js, TypeScript, Rust specifics
- **[CLI Commands](docs/commands.md)** - All available commands and flags

**🛠️ Development**
- **[File Generation](docs/file-generation.md)** - What gets created where
- **[Working Examples](examples/)** - Real-world CLI samples
- **[Troubleshooting](docs/user-guide/troubleshooting.md)** - Common issues & solutions

## 🧪 Development & Contributing

```bash
# Get started with development
git clone https://github.com/goobits/goobits-cli
cd goobits-cli
pip install -e .[dev,test]        # Editable install with dev dependencies

# Testing suite
pytest src/tests/               # Run all tests
pytest --cov=goobits_cli       # With coverage reporting
mypy src/goobits_cli/          # Type checking

# Code quality
black src/ && flake8 src/      # Format and lint
```

**📋 Project Resources**
- **[Contributing Guide](CONTRIBUTING.md)** - How to contribute, setup, and PR process
- **[Architecture Overview](CODEMAP.md)** - Codebase walkthrough for contributors

## ⚡ Performance Benchmarks

Built for speed at every level:

```bash
# Generation speed
time goobits build              # ~200ms for complete CLI generation

# Runtime performance (generated CLIs)
time mycli --help              # <100ms cold start
time mycli complex-command     # <10MB memory usage typical
```

**Optimization Highlights**: Lazy loading, efficient template caching, minimal runtime dependencies

## 📝 License

MIT License - see [LICENSE](LICENSE) for details

## 💡 Support & Community

**🐛 Issues & Bugs**: [GitHub Issues](https://github.com/goobits/goobits-cli/issues)
**💬 Questions & Ideas**: [GitHub Discussions](https://github.com/goobits/goobits-cli/discussions)

---

**Made with ❤️ for developers who love clean, fast CLIs**