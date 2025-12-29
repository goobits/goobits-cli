# 🛠️ Goobits CLI Framework

Generate production-ready CLIs in Python, Node.js, TypeScript, or Rust from a single YAML configuration file.

## ✨ Key Features

- **🌐 Multi-Language** - Python, Node.js, TypeScript, Rust from one config
- **🎯 Zero Boilerplate** - Define CLI structure in YAML, get working code
- **📦 Minimal Output** - Only 2-3 files generated per language
- **🔄 Smart Merging** - Non-destructive package.json/Cargo.toml updates
- **⚡ Production Ready** - Setup scripts, shell completions, validation
- **🔧 Self-Hosting** - Framework generates its own CLI

## 🚀 Quick Start

```bash
# Install
pip install goobits-cli
# or
pipx install goobits-cli

# Create and build a project
mkdir my-cli && cd my-cli
goobits init
goobits build
./setup.sh install --dev
```

## 🛠️ Commands

| Command | Description |
|---------|-------------|
| `goobits build [config]` | Generate CLI from goobits.yaml |
| `goobits init` | Create initial goobits.yaml |
| `goobits validate [config]` | Validate configuration without generating |
| `goobits migrate <path>` | Migrate YAML configs to 3.0.0 format |
| `goobits serve <dir>` | Serve local PyPI-compatible package index |
| `goobits upgrade` | Upgrade goobits-cli to latest version |

### Command Options

**build**
- `--output-dir` - Output directory for generated files
- `--output` - Output filename for generated CLI
- `--backup` - Create .bak files when overwriting

**init**
- `--template` - Choose template (basic, advanced, api-client)
- `--force` - Overwrite existing configuration

**validate**
- `--verbose` - Show detailed validation information

**migrate**
- `--backup` - Create backup files (.bak)
- `--dry-run` - Show changes without applying

**serve**
- `--host` - Server host (default: localhost)
- `--port` - Server port (default: 8080)

**upgrade**
- `--check` - Check for updates without installing
- `--pre` - Include pre-release versions

## ⚙️ Configuration

Create a `goobits.yaml` file:

```yaml
package_name: my-awesome-cli
command_name: mycli
display_name: "My Awesome CLI"
description: "A powerful CLI tool"
language: python

cli:
  name: mycli
  tagline: "Do awesome things"
  version: "1.0.0"
  commands:
    hello:
      desc: "Say hello"
      args:
        - name: name
          desc: "Name to greet"
          required: true
      options:
        - name: greeting
          short: g
          type: string
          desc: "Custom greeting"
          default: "Hello"
```

## 🌐 Language Support

| Language | Files Generated | Configuration |
|----------|----------------|---------------|
| Python | `cli.py`, `setup.sh` | Default |
| Node.js | `cli.mjs`, `setup.sh` | `language: nodejs` |
| TypeScript | `cli.ts`, `types.d.ts`, `setup.sh` | `language: typescript` |
| Rust | `src/main.rs`, `setup.sh` | `language: rust` |

### Language-Specific Options

**Python**
```yaml
language: python
python:
  minimum_version: "3.8"
  maximum_version: "3.13"
```

**Node.js**
```yaml
language: nodejs
nodejs:
  minimum_version: "14.0.0"
  package_manager: npm  # or yarn, pnpm
```

**TypeScript**
```yaml
language: typescript
typescript:
  strict_mode: true
  target: "ES2020"
```

**Rust**
```yaml
language: rust
rust:
  minimum_version: "1.70.0"
  edition: "2021"
```

## 🔧 Advanced Features

### Interactive Mode

All generated CLIs support interactive mode:

```bash
mycli --interactive
```

### Shell Completions

```bash
./setup.sh --completions
```

### Hooks System

Implement business logic in language-specific hook files:

| Language | Hook File |
|----------|-----------|
| Python | `cli_hooks.py` |
| Node.js | `cli_hooks.mjs` |
| TypeScript | `cli_hooks.ts` |
| Rust | `src/cli_hooks.rs` |

### Built-in Validation

- API key checking
- Disk space requirements
- System dependencies
- Runtime versions

## 📦 File Generation

### What Gets Generated

- CLI source file with all utilities embedded
- Setup script for installation
- Type definitions (TypeScript only)

### What Does NOT Get Generated

- README.md (preserves your documentation)
- .gitignore (respects your version control)
- Auxiliary lib/ folders
- Separate config/error/util files

### Smart Manifest Handling

Existing `package.json`, `Cargo.toml`, or `pyproject.toml` files are preserved. Dependencies are merged without overwriting your configuration.

## 🧪 Development

### From Source

```bash
git clone https://github.com/goobits/goobits-cli
cd goobits-cli
pip install -e .[dev,test]
```

### Testing

```bash
pytest src/tests/
pytest --cov=goobits_cli src/tests/
mypy src/goobits_cli/
```

### Performance

- CLI startup: <100ms
- Memory usage: <10MB

## 📖 Documentation

- [CONTRIBUTING.md](CONTRIBUTING.md) - Contributing guidelines
- [CHANGELOG.md](CHANGELOG.md) - Version history
- [CLAUDE.md](CLAUDE.md) - AI assistant instructions

## 💡 Examples

See `src/examples/` for sample configurations:

- `validation/` - Generated CLI examples in all 4 languages
- `installation/` - Installation demos

## 📝 License

MIT License - see [LICENSE](LICENSE)

## 🔗 Links

- [GitHub Issues](https://github.com/goobits/goobits-cli/issues)
- [GitHub Discussions](https://github.com/goobits/goobits-cli/discussions)
