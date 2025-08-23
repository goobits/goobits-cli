# Goobits CLI Framework

Build professional command-line tools with YAML configuration

> Build professional command-line tools with YAML configuration

## Installation

### From Package Manager (Recommended)

```bash
cargo install goobits-cli
```

### From Source

Clone this repository and build from source:

```bash
git clone 
cd goobits-cli
./setup.sh --dev
```

### Development Installation

For development with live updates:

```bash
./setup.sh --dev
```

## Usage

### Basic Commands

#### `goobits build` 🔨
Build CLI and setup scripts from goobits.yaml configuration

```bash
goobits build [config_path] [OPTIONS]```

**Arguments:**
- `config_path`: Path to goobits.yaml file (defaults to ./goobits.yaml)
**Options:**
- `-o, --output-dir <str>`: 📁 Output directory (defaults to same directory as config file)- `--output <str>`: 📝 Output filename for generated CLI (defaults to 'generated_cli.py')- `--backup`: 💾 Create backup files (.bak) when overwriting existing files- `--universal-templates`: 🧪 Use Universal Template System (experimental)
#### `goobits init` 🆕
Create initial goobits.yaml template

```bash
goobits init [project_name] [OPTIONS]```

**Arguments:**
- `project_name`: Name of the project (optional)
**Options:**
- `-t, --template <str>`: 🎯 Template type (default: basic)- `--force`: 🔥 Overwrite existing goobits.yaml file
#### `goobits serve` 🌐
Serve local PyPI-compatible package index

```bash
goobits serve <directory> [OPTIONS]```

**Arguments:**
- `directory`: Directory containing packages to serve
**Options:**
- `--host <str>`: 🌍 Host to bind the server to (default: localhost)- `-p, --port <int>`: 🔌 Port to run the server on (default: 8080)

### Global Options

All commands support these global options:

- `--help`: Show help message and exit
- `--version`: Show version information
- `-v, --verbose`: Enable verbose output with detailed error messages and stack traces
**Verbose Mode:**
When `--verbose` is enabled, the CLI provides:
- Detailed error messages with full context
- Stack traces for debugging issues
- Additional diagnostic information
- Progress details for long-running operations

### Examples

```bash
# Show help
goobits --help

# Show version
goobits --version

# Enable verbose output for detailed error messages
goobits --verbose build

# Short form of verbose flag
goobits -v build

# Example build command
goobits build
# Same command with verbose output
goobits --verbose build
# Example init command
goobits init
# Same command with verbose output
goobits --verbose init
# Example serve command
goobits serve "example_directory"
# Same command with verbose output
goobits --verbose serve "example_directory"
# Error handling examples
goobits invalid-command              # Standard error message
goobits --verbose invalid-command   # Detailed error with stack trace
```

## Configuration

The CLI stores configuration in `~/.config/goobits-cli/config.yaml`.

You can edit this file directly or use the CLI to manage settings.

### Configuration Options

- `settings.auto_update`: Enable automatic updates (default: false)
- `settings.log_level`: Set logging level (debug, info, warn, error)
- `settings.verbose`: Enable verbose output by default (default: false)
- `features.colored_output`: Enable colored terminal output (default: true)
- `features.progress_bars`: Show progress bars for long operations (default: true)

### Environment Variables

You can also control verbose mode using environment variables:

```bash
# Enable verbose mode for all commands
export GOOBITS_VERBOSE=true
goobits build

# Disable verbose mode (overrides config)
export GOOBITS_VERBOSE=false
goobits build
```

## Development

### Building

```bash
# Debug build
cargo build

# Release build
cargo build --release
```

### Testing

```bash
# Run all tests
cargo test

# Run tests with output
cargo test -- --nocapture
```

### Running

```bash
# Run from source (debug)
cargo run -- --help

# Run specific command
cargo run -- build --help
```

## Shell Completions

Generate shell completions for better command-line experience:

```bash
./setup.sh --completions
```

This creates completion files in the `completions/` directory for:
- Bash
- Zsh  
- Fish

### Installing Completions

**Bash:**
```bash
source completions/goobits.bash
```

**Zsh:**
```bash
# Add to your ~/.zshrc
fpath=(./completions $fpath)
autoload -U compinit && compinit
```

**Fish:**
```bash
cp completions/goobits.fish ~/.config/fish/completions/
```

## Architecture

This CLI is built using:

- **[Clap](https://docs.rs/clap/)**: Command-line argument parsing with derive macros
- **[Anyhow](https://docs.rs/anyhow/)**: Flexible error handling
- **[Serde](https://docs.rs/serde/)**: Serialization/deserialization for configuration
- **[Tokio](https://docs.rs/tokio/)**: Async runtime (optional feature)

### Project Structure

```
src/
├── main.rs          # CLI entry point and command definitions
├── lib.rs           # Library exports and core functionality  
├── config.rs        # Configuration management
├── commands.rs      # Command implementations
├── hooks.rs         # User-defined business logic
└── utils.rs         # Utility functions
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

## Changelog

### 1.0.0
- Initial release
- Core CLI functionality implemented
- `build` command: Build CLI and setup scripts from goobits.yaml configuration
- `init` command: Create initial goobits.yaml template
- `serve` command: Serve local PyPI-compatible package index
