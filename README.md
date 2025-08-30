# 🎯 Goobits CLI Framework

Generate production-ready CLIs in Python, Node.js, TypeScript, or Rust from a single YAML configuration. Zero boilerplate, minimal files, instant results.

## ✨ Features

- **🚀 One YAML** - Define once, generate for 4 languages
- **📦 Minimal files** - Only 2-3 files generated, no clutter
- **⚡ Instant CLI** - Working command-line tool in 30 seconds
- **🔧 Smart merging** - Never overwrites your package.json/Cargo.toml
- **🎨 Rich interfaces** - Colors, progress bars, interactive modes
- **🔄 Self-hosting** - Framework uses itself for its own CLI

## 🚀 Quick Start

```bash
# Install
pip install goobits-cli          # or: pipx install goobits-cli

# Create CLI in 30 seconds
goobits init
goobits build
./setup.sh install --dev

# Use your CLI
mycli hello world
```

## 💻 Example

```yaml
# goobits.yaml
package_name: my-cli
command_name: mycli
display_name: "My CLI"
description: "A simple CLI tool"
language: python      # or: nodejs, typescript, rust

cli:
  name: mycli
  version: "3.0.1"
  tagline: "Simple and powerful"
  commands:
    greet:
      desc: "Say hello"
      args:
        - name: name
          desc: "Who to greet"
```

Run `goobits build` → Get working CLI with help, completions, and colors.

## 🌐 Languages

Generate CLIs in **Python**, **Node.js**, **TypeScript**, or **Rust** from one config.
```yaml
language: nodejs    # Just change this line
```
[Full language guide →](docs/languages.md)

## 📦 What's Generated

2-3 files only. No README overwriting. Smart dependency merging.

| Language | Files | Description |
|----------|-------|-------------|
| Python | 2 | `cli.py`, `setup.sh` |
| Node.js | 2 | `cli.mjs`, `setup.sh` |
| TypeScript | 3 | `cli.ts`, `types.d.ts`, `setup.sh` |
| Rust | 2 | `src/main.rs`, `setup.sh` |

[Details →](docs/file-generation.md)

## 🛠️ Commands

```bash
goobits build      # Generate CLI from goobits.yaml
goobits init       # Create starter config
goobits validate   # Check config without generating
```
[All commands →](docs/commands.md)

## 🎨 Advanced Features

- **Interactive Mode** - Built-in REPL for all languages
- **Shell Completions** - Bash, Zsh, Fish auto-generated
- **Hook System** - Business logic in `cli_hooks.py/js/ts/rs`
- **Universal Templates** - Consistent behavior across languages

## 📚 Documentation

- **[Commands](docs/commands.md)** - All CLI commands
- **[Languages](docs/languages.md)** - Language-specific setup
- **[Configuration](docs/user-guide/configuration.md)** - YAML schema
- **[File Generation](docs/file-generation.md)** - What gets created
- **[Examples](examples/)** - Working demos
- **[Troubleshooting](docs/user-guide/troubleshooting.md)** - Common issues

## 🧪 Development

```bash
# Setup
git clone https://github.com/goobits/goobits-cli
cd goobits-cli
pip install -e .[dev,test]

# Test
pytest src/tests/
mypy src/goobits_cli/

# Lint
black src/
flake8 src/
```

[Contributing Guide](CONTRIBUTING.md) | [Architecture](CODEMAP.md)

## ⚡ Performance

- **Startup**: <100ms for generated CLIs
- **Memory**: <10MB typical usage
- **File generation**: ~200ms for complete CLI

## 📝 License

MIT - See [LICENSE](LICENSE)

## 💬 Support

[Issues](https://github.com/goobits/goobits-cli/issues) | [Discussions](https://github.com/goobits/goobits-cli/discussions)