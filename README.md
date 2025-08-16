# TestNodeCLI

Node.js test CLI for validation

> Node.js test CLI for validation

## Installation

### From Package Manager (Recommended)

```bash
npm install -g test-node-cli
```

### From Source

Clone this repository and build from source:

```bash
git clone 
cd test-node-cli
./setup.sh --dev
```

### Development Installation

For development with live updates:

```bash
./setup.sh --dev
```

## Usage

### Basic Commands

#### `testnodecli hello`
Say hello

```bash
testnodecli hello <name>```

**Arguments:**
- `name`: Name to greet

#### `testnodecli test`
Run a test

```bash
testnodecli test```




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
testnodecli --help

# Show version
testnodecli --version

# Enable verbose output for detailed error messages
testnodecli --verbose hello

# Short form of verbose flag
testnodecli -v hello

# Example hello command
testnodecli hello "example_name"
# Same command with verbose output
testnodecli --verbose hello "example_name"
# Error handling examples
testnodecli invalid-command              # Standard error message
testnodecli --verbose invalid-command   # Detailed error with stack trace
```

## Configuration

Configuration locations:

- **Linux**: `~/.config/test-node-cli/`
- **macOS**: `~/Library/Application Support/test-node-cli/`
- **Windows**: `%APPDATA%\test-node-cli\`

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
export TESTNODECLI_VERBOSE=true
testnodecli hello

# Disable verbose mode (overrides config)
export TESTNODECLI_VERBOSE=false
testnodecli hello
```

## Development

### Building

```bash
# Install dependencies
npm install

# Build (if TypeScript)
npm run build

# Run tests
npm test
```

### Testing

```bash
# Run all tests
npm test

# Run with coverage
npm run test:coverage
```

### Running

```bash
# Run from source (development)
node cli.js --help

# Or using npm link
npm link && testnodecli --help
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
source completions/testnodecli.bash
```

**Zsh:**
```bash
# Add to your ~/.zshrc
fpath=(./completions $fpath)
autoload -U compinit && compinit
```

**Fish:**
```bash
cp completions/testnodecli.fish ~/.config/fish/completions/
```

## Architecture

This CLI is built using:

- **[Commander.js](https://github.com/tj/commander.js/)**: Complete solution for command-line interfaces
- **[Inquirer.js](https://github.com/SBoudrias/Inquirer.js/)**: Interactive command-line prompts
- **[Chalk](https://github.com/chalk/chalk)**: Terminal string styling

### Project Structure

```
├── cli.js           # CLI entry point
├── package.json         # NPM package configuration
├── src/
│   ├── hooks.js       # User-defined business logic
│   ├── config.js      # Configuration management
│   └── utils.js       # Utility functions
└── completions/         # Shell completion scripts
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
- `test` command: Run a test
