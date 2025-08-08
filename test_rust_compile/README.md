# Test Rust CLI

A test Rust CLI

## Installation

### From Crates.io (Recommended)

```bash
cargo install test-rust-cli
```

### From Source

Clone this repository and build from source:

```bash
git clone 
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



#### `test-rust-cli hello`

Hello command

```bash
test-rust-cli hello [OPTIONS]
```




**Options:**

- `----name <str>`: Name to greet (default: World)






### Global Options



### Examples

```bash
# Show help
test-rust-cli --help

# Show version
test-rust-cli --version




```

## Configuration

The CLI stores configuration in `~/.config/test-rust-cli/config.yaml`. You can edit this file directly or use the CLI to manage settings.

### Configuration Options

- `settings.auto_update`: Enable automatic updates (default: false)
- `settings.log_level`: Set logging level (debug, info, warn, error)
- `features.colored_output`: Enable colored terminal output (default: true)
- `features.progress_bars`: Show progress bars for long operations (default: true)

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
source completions/test-rust-cli.bash
```

**Zsh:**
```bash
# Add to your ~/.zshrc
fpath=(./completions $fpath)
autoload -U compinit && compinit
```

**Fish:**
```bash
cp completions/test-rust-cli.fish ~/.config/fish/completions/
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
└── utils.rs         # Utility functions
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Run tests (`cargo test`)
6. Commit your changes (`git commit -am 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Changelog

### 1.0.0
- Initial release
- Core CLI functionality implemented

- `hello` command: Hello command
