# Test TypeScript

Test TypeScript helper libraries

> Test TS compilation

## Installation

### From Package Manager (Recommended)

```bash
npm install -g test_ts
```

### From Source

Clone this repository and build from source:

```bash
git clone 
cd test_ts
./setup.sh --dev
```

### Development Installation

For development with live updates:

```bash
./setup.sh --dev
```

## Usage

### Basic Commands

#### `testts hello`
Say hello

```bash
testts hello <name>```

**Arguments:**
- `name`: Name to greet


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
testts --help

# Show version
testts --version

# Enable verbose output for detailed error messages
testts --verbose hello

# Short form of verbose flag
testts -v hello

# Example hello command
testts hello "example_name"
# Same command with verbose output
testts --verbose hello "example_name"
# Error handling examples
testts invalid-command              # Standard error message
testts --verbose invalid-command   # Detailed error with stack trace
```

## Configuration

Configuration locations:

- **Linux**: `~/.config/test_ts/`
- **macOS**: `~/Library/Application Support/test_ts/`
- **Windows**: `%APPDATA%\test_ts\`

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
export TESTTS_VERBOSE=true
testts hello

# Disable verbose mode (overrides config)
export TESTTS_VERBOSE=false
testts hello
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
npm link && testts --help
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
source completions/testts.bash
```

**Zsh:**
```bash
# Add to your ~/.zshrc
fpath=(./completions $fpath)
autoload -U compinit && compinit
```

**Fish:**
```bash
cp completions/testts.fish ~/.config/fish/completions/
```

## Architecture

This CLI is built using:

- **[Commander.js](https://github.com/tj/commander.js/)**: Complete solution for command-line interfaces
- **[TypeScript](https://www.typescriptlang.org/)**: Typed superset of JavaScript
- **[Inquirer.js](https://github.com/SBoudrias/Inquirer.js/)**: Interactive command-line prompts

### Project Structure

```
├── cli.ts           # CLI entry point
├── package.json         # NPM package configuration
├── src/
│   ├── hooks.ts       # User-defined business logic
│   ├── config.ts      # Configuration management
│   └── utils.ts       # Utility functions
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
