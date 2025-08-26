# Goobits CLI Framework

Build professional command-line tools with YAML configuration. Generate production-ready CLIs in Python, Node.js, TypeScript, or Rust from a single configuration file.

## Features

- **Multi-language support**: Python, Node.js, TypeScript, Rust
- **Zero boilerplate**: Define CLI structure in YAML, get working code
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
goobits init my-cli

# Build CLI and setup scripts
goobits build

# Install for development
./setup.sh install --dev
```

## Usage

### Core Commands

**Generated CLI** (`goobits` command):

- `goobits build <config_path>` - Generate CLI from goobits.yaml
  - `--output-dir`: Output directory for generated files
  - `--output`: Output filename for generated CLI
  - `--backup`: Create .bak files when overwriting

- `goobits init <project_name>` - Create initial goobits.yaml
  - `--template`: Choose template (basic, advanced, api-client, text-processor)
  - `--force`: Overwrite existing configuration

- `goobits serve <directory>` - Serve local PyPI-compatible package index
  - `--host`: Server host (default: localhost)
  - `--port`: Server port (default: 8080)

- `goobits upgrade` - (Not yet implemented in generated CLI)

**Development Commands** (available via `python -m goobits_cli.main`):

- `python -m goobits_cli.main validate [config_path]` - Validate goobits.yaml configuration
  - `--verbose`: Show detailed validation information

- `python -m goobits_cli.main migrate <path>` - Migrate YAML configurations to 3.0.0 format
  - `--backup/--no-backup`: Create backup files (default: true)
  - `--dry-run`: Show changes without applying
  - `--pattern`: File pattern for directory migration (default: *.yaml)

- `python -m goobits_cli.main upgrade` - Upgrade goobits-cli (advanced options)
  - `--source`: Upgrade source (pypi, git, local)
  - `--version`: Specific version to install
  - `--pre`: Include pre-release versions
  - `--dry-run`: Show what would be upgraded without doing it

### Configuration Example

```yaml
# goobits.yaml
package_name: my-awesome-cli
command_name: mycli
display_name: "My Awesome CLI"
description: "My awesome CLI tool"
language: python  # or nodejs, typescript, rust

cli_output_path: "src/mycli/cli.py"

installation:
  pypi_name: my-awesome-cli
  development_path: "."
  extras:
    python: ["dev", "test"]

cli:
  name: "My Awesome CLI"
  tagline: "An awesome command-line tool"
  version: "1.0.0"
  commands:
    greet:
      desc: "Greet someone"
      args:
        - name: "name"
          desc: "Name to greet"
      options:
        - name: "enthusiastic"
          type: "flag"
          desc: "Add enthusiasm!"
```

### Hook Implementation

Create and implement business logic in language-specific hook files (not auto-generated):

**Python** (`app_hooks.py`):
```python
def on_greet(name, enthusiastic=False):
    greeting = f"Hello, {name}"
    if enthusiastic:
        greeting += "!"
    print(greeting)
```

**Node.js** (`src/hooks.js`):
```javascript
export async function onGreet({ name, enthusiastic }) {
    let greeting = `Hello, ${name}`;
    if (enthusiastic) greeting += "!";
    console.log(greeting);
}
```

**TypeScript** (`src/hooks.ts`):
```typescript
interface GreetArgs {
    name: string;
    enthusiastic?: boolean;
}

export async function onGreet({ name, enthusiastic }: GreetArgs): Promise<void> {
    let greeting = `Hello, ${name}`;
    if (enthusiastic) greeting += "!";
    console.log(greeting);
}
```

**Rust** (`src/hooks.rs`):
```rust
use clap::ArgMatches;
use anyhow::Result;

pub fn on_greet(matches: &ArgMatches) -> Result<()> {
    let name = matches.get_one::<String>("name").unwrap();
    let mut greeting = format!("Hello, {}", name);
    if matches.get_flag("enthusiastic") {
        greeting.push('!');
    }
    println!("{}", greeting);
    Ok(())
}
```

## Language Support

| Language | Status | Package Manager | Features |
|----------|--------|----------------|----------|
| Python | ✅ 100% | pip/pipx | Full support, rich terminal UI |
| Node.js | ✅ 100% | npm | Commander.js, completions |
| TypeScript | ✅ 100% | npm | Type safety, completions |
| Rust | ✅ 100% | cargo | High performance, Clap CLI |

## Advanced Features

### Universal Template System

The Universal Template System provides consistent CLI generation across all supported languages from a single template. It is now always enabled for optimal performance and consistency.

### Interactive Mode
Generated CLIs support interactive REPL:
```bash
mycli --interactive
```

### Shell Completions
Setup scripts generate completions for bash, zsh, fish:
```bash
./setup.sh --completions
```

## Development

### Requirements
- Python 3.8+
- Node.js 16+ (for Node.js/TypeScript CLIs)
- Rust/Cargo (for Rust CLIs)

### Testing
```bash
# Run all tests
pytest src/tests/

# Run with coverage
pytest --cov=goobits_cli src/tests/

# Type checking (requires dev dependencies)
mypy src/goobits_cli/

# Linting (requires dev dependencies)
black --check src/
flake8 src/
```

### Building Self-Hosted CLI
```bash
# Goobits uses itself
goobits build
```

## Documentation

- [CODEMAP.md](CODEMAP.md) - Quick project overview for developers
- [CONTRIBUTING.md](CONTRIBUTING.md) - Contribution guidelines
- [CHANGELOG.md](CHANGELOG.md) - Version history

## License

MIT

## Author

DataBassGit

---

Built with ❤️ using [Goobits CLI Framework](https://github.com/goobits/goobits-cli)