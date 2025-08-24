# Nested Command Demo

Demonstration of deep nested command capabilities

> Deep nesting demo

## Installation

### From Package Manager (Recommended)

```bash
cargo install nested-demo
```

### From Source

Clone this repository and build from source:

```bash
git clone 
cd nested-demo
./setup.sh --dev
```

### Development Installation

For development with live updates:

```bash
./setup.sh --dev
```

## Usage

### Basic Commands

#### `demo simple`
Simple command that works today

```bash
demo simple <message> [OPTIONS]```

**Arguments:**
- `message`: Message to display
**Options:**
- `--verbose`: Verbose output
#### `demo database`
Database operations

**Subcommands:**
- `users`: User management
- `backup`: Database backup operations
#### `demo api`
API management

**Subcommands:**
- `v1`: API v1 endpoints

### Global Options

All commands support these global options:

- `--help`: Show help message and exit
- `--version`: Show version information

**Verbose Mode:**
When `--verbose` is enabled, the CLI provides:
- Detailed error messages with full context
- Stack traces for debugging issues
- Additional diagnostic information
- Progress details for long-running operations

### Examples

```bash
# Show help
demo --help

# Show version
demo --version

# Enable verbose output for detailed error messages
demo --verbose simple

# Short form of verbose flag
demo -v simple

# Example simple command
demo simple "example_message"
# Same command with verbose output
demo --verbose simple "example_message"
# Error handling examples
demo invalid-command              # Standard error message
demo --verbose invalid-command   # Detailed error with stack trace
```

## Configuration

The CLI stores configuration in `~/.config/nested-demo/config.yaml`.

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
export DEMO_VERBOSE=true
demo simple

# Disable verbose mode (overrides config)
export DEMO_VERBOSE=false
demo simple
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
cargo run -- simple --help
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
source completions/demo.bash
```

**Zsh:**
```bash
# Add to your ~/.zshrc
fpath=(./completions $fpath)
autoload -U compinit && compinit
```

**Fish:**
```bash
cp completions/demo.fish ~/.config/fish/completions/
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
- `simple` command: Simple command that works today
- `database` command: Database operations
- `api` command: API management
