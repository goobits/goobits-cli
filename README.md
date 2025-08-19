# Goobits CLI Framework

Universal CLI generation platform that creates professional command-line interfaces from YAML configuration files.

> Transform simple YAML configuration into rich terminal applications with setup scripts, dependency management, and cross-platform compatibility.

## Features

- **Multi-language support**: Python, Node.js, TypeScript, and Rust (all production-ready)
- **Universal Template System**: Single configuration generates for all languages
- **Rich terminal interfaces**: Built with rich-click, Commander.js, and Clap
- **Automated setup scripts**: Platform-aware installation and dependency management
- **Self-hosting**: Framework generates its own CLI from goobits.yaml
- **Performance optimized**: <100ms startup times, <2MB memory usage

## Installation

### From PyPI (Recommended)

```bash
pipx install goobits-cli
```

### From Source

Clone this repository and install in development mode:

```bash
git clone https://github.com/goobits/goobits-cli.git
cd goobits-cli
./setup.sh install --dev
```

## Quick Start

Create a new CLI project:

```bash
# Start with the working example
cp -r docs/examples/simple-greeting my-awesome-cli
cd my-awesome-cli
goobits build                 # Create CLI and setup scripts
./setup.sh install --dev     # Install for development
```

Or create from scratch in an existing goobits project directory:
```bash
goobits init my-cli           # Generate initial goobits.yaml template
```

## Commands

### `goobits build [CONFIG_PATH]`
Generate CLI and setup scripts from goobits.yaml configuration

**Options:**
- `--output-dir, -o`: Output directory (defaults to same directory as config file)
- `--output`: Output filename for generated CLI (defaults to 'generated_cli.py')
- `--backup`: Create backup files (.bak) when overwriting existing files
- `--universal-templates`: Use Universal Template System (production-ready but marked experimental in CLI)

### `goobits init [PROJECT_NAME]`
Create initial goobits.yaml template

**Options:**
- `--template, -t`: Template type (basic, advanced, api-client, text-processor)
- `--force`: Overwrite existing goobits.yaml file

### `goobits serve DIRECTORY`
Serve local PyPI-compatible package index

**Options:**
- `--host`: Host to bind the server to (default: localhost)
- `--port, -p`: Port to run the server on (default: 8080)

## Global Options

- `--verbose, -v`: Enable verbose error output and debugging information
- `--version`: Show version information
- `--help`: Show help message

## Language Support

### Python
- Framework: Click with rich-click
- Hook file: `app_hooks.py`
- Example: `def on_command_name(*args, **kwargs):`

### Node.js
- Framework: Commander.js
- Hook file: `src/hooks.js`
- Example: `export async function onCommandName(args) {}`

### TypeScript
- Framework: Commander.js with type safety
- Hook file: `src/hooks.ts`
- Example: `export async function onCommandName(args: string[]) {}`

### Rust
- Framework: Clap (high-performance native binaries)
- Hook file: `src/hooks.rs`
- Example: `pub fn on_command_name(matches: &ArgMatches) -> Result<()> {}`

## Configuration

Basic `goobits.yaml` structure:

```yaml
package_name: my-cli
command_name: mycli
display_name: "My Awesome CLI"
description: "A description of what my CLI does"
language: python  # python, nodejs, typescript, or rust

cli_hooks: "app_hooks.py"  # For Python (nodejs: src/hooks.js, rust: src/hooks.rs)

cli:
  name: "My CLI"
  version: "1.0.0"
  tagline: "Short description"
  
  commands:
    hello:
      desc: "Say hello"
      args:
        - name: "name"
          desc: "Name to greet"
          required: true
```

## Development Workflow

1. **Edit goobits.yaml**: Define your CLI structure
2. **Run goobits build**: Generate implementation files
3. **Edit hooks file**: Add your business logic
4. **Test**: `./setup.sh install --dev`

## Examples

See working examples in the repository:

- `demo-examples/`: Complete multi-language CLI examples
- `rust_test_cli/`: Rust CLI implementation example
- Self-hosting: This framework's own CLI is built from `goobits.yaml`

## Architecture

```
goobits.yaml → Generator Engine → Generated CLI
     ↓              ↓                  ↓
Configuration   Template         Python/JS/TS/Rust
(User Input)   Processing        Applications
              (Jinja2/Universal)
```

## Development

### Prerequisites

- Python 3.8+
- pip/pipx

### Building

```bash
# Install dependencies
./setup.sh install --dev

# Generate CLI from goobits.yaml (self-hosting)
goobits build

# Run tests
pytest src/tests/

# Type checking
mypy src/goobits_cli/

# Linting
ruff check src/
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Run tests and ensure they pass
6. Commit your changes (`git commit -am 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.