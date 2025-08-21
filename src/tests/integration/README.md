# NodeJSTestCLI

A comprehensive Node.js CLI for testing all features.

> A comprehensive Node.js CLI for testing all features.

## Installation

### From Package Manager (Recommended)

```bash
npm install -g nodejs-test-cli
```

### From Source

Clone this repository and build from source:

```bash
git clone 
cd nodejs-test-cli
./setup.sh --dev
```

### Development Installation

For development with live updates:

```bash
./setup.sh --dev
```

## Usage

### Basic Commands

#### `nodejstestcli init`
Initialize a new project

```bash
nodejstestcli init <name> [OPTIONS]```

**Arguments:**
- `name`: Project name
**Options:**
- `-t, --template <str>`: Project template to use (default: default)- `--skip-install`: Skip npm install
#### `nodejstestcli deploy`
Deploy the application

```bash
nodejstestcli deploy <environment> [OPTIONS]```

**Arguments:**
- `environment`: Target environment (dev, staging, prod)
**Options:**
- `-f, --force`: Force deployment without confirmation- `--dry-run`: Simulate deployment without making changes
#### `nodejstestcli server`
Server management commands

**Subcommands:**
- `start`: Start the server
- `stop`: Stop the server
- `restart`: Restart the server
#### `nodejstestcli database`
Database operations

**Subcommands:**
- `migrate`: Run database migrations
- `seed`: Seed the database
- `backup`: Backup the database
#### `nodejstestcli test`
Run tests

```bash
nodejstestcli test [pattern] [OPTIONS]```

**Arguments:**
- `pattern`: Test file pattern
**Options:**
- `--coverage`: Generate coverage report- `-w, --watch`: Watch files for changes- `--bail`: Stop on first test failure

### Global Options

All commands support these global options:

- `--help`: Show help message and exit
- `--version`: Show version information
- `-v, --verbose`: Enable verbose logging- `-c, --config <str>`: Path to configuration file
**Verbose Mode:**
When `--verbose` is enabled, the CLI provides:
- Detailed error messages with full context
- Stack traces for debugging issues
- Additional diagnostic information
- Progress details for long-running operations

### Examples

```bash
# Show help
nodejstestcli --help

# Show version
nodejstestcli --version

# Enable verbose output for detailed error messages
nodejstestcli --verbose init

# Short form of verbose flag
nodejstestcli -v init

# Example init command
nodejstestcli init "example_name"
# Same command with verbose output
nodejstestcli --verbose init "example_name"
# Example deploy command
nodejstestcli deploy "example_environment"
# Same command with verbose output
nodejstestcli --verbose deploy "example_environment"
# Example test command
nodejstestcli test
# Same command with verbose output
nodejstestcli --verbose test
# Error handling examples
nodejstestcli invalid-command              # Standard error message
nodejstestcli --verbose invalid-command   # Detailed error with stack trace
```

## Configuration

Configuration locations:

- **Linux**: `~/.config/nodejs-test-cli/`
- **macOS**: `~/Library/Application Support/nodejs-test-cli/`
- **Windows**: `%APPDATA%\nodejs-test-cli\`

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
export NODEJSTESTCLI_VERBOSE=true
nodejstestcli init

# Disable verbose mode (overrides config)
export NODEJSTESTCLI_VERBOSE=false
nodejstestcli init
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
npm link && nodejstestcli --help
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
source completions/nodejstestcli.bash
```

**Zsh:**
```bash
# Add to your ~/.zshrc
fpath=(./completions $fpath)
autoload -U compinit && compinit
```

**Fish:**
```bash
cp completions/nodejstestcli.fish ~/.config/fish/completions/
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
- `init` command: Initialize a new project
- `deploy` command: Deploy the application
- `server` command: Server management commands
- `database` command: Database operations
- `test` command: Run tests
