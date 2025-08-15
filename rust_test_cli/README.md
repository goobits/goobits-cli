# Test Rust CLI

A simple test CLI for Rust compilation

> Test CLI for Rust compilation

## Installation

### From Package Manager (Recommended)

```bash
cargo install test-rust-cli
```

### From Source

Clone this repository and build from source:

```bash
git clone https://github.com/user/repo
cd test-rust-cli
./setup.sh --dev
```

### Development Installation

For development with live updates:

```bash
./setup.sh --dev
```

## Usage

### Basic Commands

#### `testcli hello`
Say hello

```bash
testcli hello <name> [OPTIONS]```

**Arguments:**
- `name`: Name to greet
**Options:**
- `-u, --uppercase`: Print in uppercase
#### `testcli info`
Show information

```bash
testcli info [OPTIONS]```


**Options:**
- `-d, --detailed`: Show detailed information

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
testcli --help

# Show version
testcli --version

# Enable verbose output for detailed error messages
testcli --verbose hello

# Short form of verbose flag
testcli -v hello

# Example hello command
testcli hello "example_name"
# Same command with verbose output
testcli --verbose hello "example_name"
# Error handling examples
testcli invalid-command              # Standard error message
testcli --verbose invalid-command   # Detailed error with stack trace
```

## Configuration

The CLI stores configuration in `~/.config/test-rust-cli/config.yaml`.

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
export TESTCLI_VERBOSE=true
testcli hello

# Disable verbose mode (overrides config)
export TESTCLI_VERBOSE=false
testcli hello
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
cargo run -- hello --help
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
source completions/testcli.bash
```

**Zsh:**
```bash
# Add to your ~/.zshrc
fpath=(./completions $fpath)
autoload -U compinit && compinit
```

**Fish:**
```bash
cp completions/testcli.fish ~/.config/fish/completions/
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
- `hello` command: Say hello
- `info` command: Show information
