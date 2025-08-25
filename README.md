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
git clone https://github.com/DataBassGit/goobits
cd goobits
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
  - `--universal-templates`: Use Universal Template System
  - `--backup`: Create .bak files when overwriting

- `goobits init [project_name]` - Create initial goobits.yaml
  - `--template`: Choose template (basic, advanced, api-client, text-processor)
  - `--force`: Overwrite existing configuration

- `goobits serve <directory>` - Serve local PyPI-compatible package index
  - `--host`: Server host (default: localhost)
  - `--port`: Server port (default: 8080)

- `goobits migrate [config_path]` - Migrate YAML configurations to 3.0.0 format

- `goobits upgrade` - Upgrade goobits-cli to the latest version

### Configuration Example

```yaml
# goobits.yaml
package_name: my-awesome-cli
command_name: mycli
description: "My awesome CLI tool"
language: python  # or nodejs, typescript, rust

cli_output_path: "src/mycli/cli.py"

installation:
  pypi_name: my-awesome-cli
  development_path: "."
  extras:
    python: ["dev", "test"]

cli:
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

Implement business logic in language-specific hook files:

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
```bash
goobits build --universal-templates
```
Single template generates consistent CLIs across all languages.

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

# Type checking
mypy src/goobits_cli/

# Linting
ruff check src/
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

Built with ❤️ using [Goobits CLI Framework](https://github.com/DataBassGit/goobits)