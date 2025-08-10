# Complex CLI Test Tool

A complex CLI tool for testing code generation quality

> Test complex code generation patterns

## Installation

### From Package Manager (Recommended)

```bash
npm install -g complex-cli-test
```

### From Source

Clone this repository and build from source:

```bash
git clone https://github.com/user/repo
cd complex-cli-test
./setup.sh --dev
```

### Development Installation

For development with live updates:

```bash
./setup.sh --dev
```

## Usage

### Basic Commands

#### `complex-cli build`
Build the project with various options

```bash
complex-cli build <target> [source] [OPTIONS]```

**Arguments:**
- `target`: Build target directory- `source`: Source files pattern
**Options:**
- `-v, --verbose <bool>`: Enable verbose output- `-f, --output-format <str>`: Output format (default: json)- `-j, --parallel-jobs <int>`: Number of parallel jobs (default: 4)- `--timeout <float>`: Build timeout in seconds (default: 30.0)
#### `complex-cli deploy`
Deploy application to various environments

```bash
complex-cli deploy <environment> [OPTIONS]```

**Arguments:**
- `environment`: Target environment (choices: dev, staging, prod)
**Options:**
- `--dry-run`: Perform dry run without actual deployment- `-c, --config-file <str>`: Custom configuration file- `-f, --force`: Force deployment ignoring checks
#### `complex-cli test`
Run comprehensive test suite

**Subcommands:**
- `unit`: Run unit tests
- `integration`: Run integration tests
- `performance`: Run performance benchmarks
#### `complex-cli config`
Configuration management commands

**Subcommands:**
- `get`: Get configuration value
- `set`: Set configuration value
- `list`: List all configuration values

### Global Options


### Examples

```bash
# Show help
complex-cli --help

# Show version
complex-cli --version

# Example build command
complex-cli build "example_target"
# Example deploy command
complex-cli deploy "example_environment"
```

## Configuration

Configuration locations:

- **Linux**: `~/.config/complex-cli-test/`
- **macOS**: `~/Library/Application Support/complex-cli-test/`
- **Windows**: `%APPDATA%\complex-cli-test\`

You can edit this file directly or use the CLI to manage settings.

### Configuration Options

- `settings.auto_update`: Enable automatic updates (default: false)
- `settings.log_level`: Set logging level (debug, info, warn, error)
- `features.colored_output`: Enable colored terminal output (default: true)
- `features.progress_bars`: Show progress bars for long operations (default: true)

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
npm link && complex-cli --help
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
source completions/complex-cli.bash
```

**Zsh:**
```bash
# Add to your ~/.zshrc
fpath=(./completions $fpath)
autoload -U compinit && compinit
```

**Fish:**
```bash
cp completions/complex-cli.fish ~/.config/fish/completions/
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
- `build` command: Build the project with various options
- `deploy` command: Deploy application to various environments
- `test` command: Run comprehensive test suite
- `config` command: Configuration management commands
