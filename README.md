# Goobits CLI Framework

Build professional command-line tools with YAML configuration. Generate production-ready CLIs in Python, Node.js, TypeScript, or Rust from a single configuration file.

## Features

- **Multi-language support**: Python, Node.js, TypeScript, Rust
- **Zero boilerplate**: Define CLI structure in YAML, get working code
- **Minimal file generation**: Only 2-3 files per language, no repository clutter
- **Smart manifest merging**: Non-destructive package.json/Cargo.toml updates
- **Production ready**: Generates setup scripts, package configs, completions
- **Universal Template System**: Single template generates for all languages
- **Self-hosting**: Framework uses itself for its own CLI

## Installation

### From PyPI
```bash
pip install goobits-cli
# or
pipx install goobits-cli  # Recommended for CLI tools
```

### From Source
```bash
git clone https://github.com/goobits/goobits-cli
cd goobits-cli
pip install -e .[dev,test]
```

## Quick Start

```bash
# Create new project
mkdir my-cli && cd my-cli

# Generate initial configuration
goobits init

# Build CLI and setup scripts
goobits build

# Install for development
./setup.sh install --dev
```

## Usage

### Core Commands

- `goobits build [config_path]` - Generate CLI from goobits.yaml
  - `--output-dir`: Output directory for generated files
  - `--output`: Output filename for generated CLI
  - `--backup`: Create .bak files when overwriting

- `goobits init` - Create initial goobits.yaml
  - `--template`: Choose template (basic, advanced, api-client)
  - `--force`: Overwrite existing configuration

- `goobits validate [config_path]` - Validate goobits.yaml without generating files
  - `--verbose`: Show detailed validation information

- `goobits migrate <path>` - Migrate YAML configurations to 3.0.0 format
  - `--backup`: Create backup files (.bak)
  - `--dry-run`: Show changes without applying

- `goobits serve <directory>` - Serve local PyPI-compatible package index
  - `--host`: Server host (default: localhost)
  - `--port`: Server port (default: 8080)

- `goobits upgrade` - Upgrade goobits-cli to latest version
  - `--check`: Check for updates without installing
  - `--pre`: Include pre-release versions

## Configuration

Create a `goobits.yaml` file:

```yaml
package_name: my-awesome-cli
command_name: mycli
display_name: "My Awesome CLI"
description: "A powerful CLI tool"
language: python  # or nodejs, typescript, rust

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

## Minimal File Generation

Goobits generates only essential files to keep your repository clean:

### Generated Files by Language

| Language   | Files Generated | Description |
|------------|----------------|-------------|
| Python     | 2 files | `cli.py` (everything embedded), `setup.sh` |
| Node.js    | 2 files | `cli.mjs` (ES6 module), `setup.sh` |
| TypeScript | 3 files | `cli.ts`, `types.d.ts`, `setup.sh` |
| Rust       | 2 files | `src/main.rs` (inline modules), `setup.sh` |

### Smart Manifest Handling

- **No overwriting**: Existing `package.json`, `Cargo.toml`, or `pyproject.toml` are preserved
- **Smart merging**: Dependencies are added without destroying your configuration
- **User control**: You maintain full control over project metadata

### What's NOT Generated

- ❌ No README.md (preserves your documentation)
- ❌ No .gitignore (respects your version control)
- ❌ No auxiliary lib/ folders
- ❌ No separate config/error/util files (all embedded)

## Language Support

### Python (Default)
```yaml
language: python
python:
  minimum_version: "3.8"
  maximum_version: "3.13"
```

### Node.js
```yaml
language: nodejs
nodejs:
  minimum_version: "14.0.0"
  package_manager: npm  # or yarn, pnpm
```

### TypeScript
```yaml
language: typescript
typescript:
  strict_mode: true
  target: "ES2020"
```

### Rust
```yaml
language: rust
rust:
  minimum_version: "1.70.0"
  edition: "2021"
```

## Advanced Features

### Interactive Mode
All generated CLIs support interactive mode:
```bash
mycli --interactive
```

### Shell Completions
Generated CLIs include shell completion scripts:
```bash
./setup.sh --completions  # Generate completion scripts
```

### Hooks System
Implement business logic in language-specific hook files:
- Python: `app_hooks.py`
- Node.js: `src/hooks.js`
- TypeScript: `src/hooks.ts`
- Rust: `src/hooks.rs`

### Validation
Built-in validation for:
- API key checking
- Disk space requirements
- System dependencies
- Runtime versions

## Development

### Testing
```bash
# Run all tests
pytest src/tests/

# Run with coverage
pytest --cov=goobits_cli src/tests/

# Type checking
mypy src/goobits_cli/
```

### Performance
- CLI startup: <100ms
- Memory usage: <10MB
- Universal Template System with lazy loading

### Documentation
- [CONTRIBUTING.md](CONTRIBUTING.md) - Contributing guidelines
- [CHANGELOG.md](CHANGELOG.md) - Version history
- [CLAUDE.md](CLAUDE.md) - AI assistant instructions
- [CODEMAP.md](CODEMAP.md) - Codebase structure

## Examples

See the `examples/` directory for sample configurations:
- `basic.yaml` - Simple CLI with basic commands
- `advanced.yaml` - Complex CLI with subcommands
- `api-client.yaml` - REST API client CLI
- `multi-language/` - Same CLI in all 4 languages

## License

MIT License - see [LICENSE](LICENSE) file

## Contributing

Contributions welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) first.

## Support

- Issues: [GitHub Issues](https://github.com/goobits/goobits-cli/issues)
- Discussions: [GitHub Discussions](https://github.com/goobits/goobits-cli/discussions)
- Documentation: [https://docs.goobits.io](https://docs.goobits.io)

---

Built with ❤️ by the Goobits team