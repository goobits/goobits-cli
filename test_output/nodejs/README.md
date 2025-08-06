# TestNodeJSCLI

Test Node.js CLI for verification

> Test Node.js CLI for verification

## Installation

### From Package Manager (Recommended)

```bash
npm install -g test-nodejs-cli
```

### From Source

Clone this repository and build from source:

```bash
git clone https://github.com/user/repo
cd test-nodejs-cli
./setup.sh --dev
```

### Development Installation

For development with live updates:

```bash
./setup.sh --dev
```

## Usage

### Basic Commands

#### `testnjs hello`
Say hello

```bash
testnjs hello <name> [OPTIONS]```

**Arguments:**
- `name`: Name to greet
**Options:**
- `-g, --greeting <str>`: Custom greeting (default: Hello)

### Global Options


### Examples

```bash
# Show help
testnjs --help

# Show version
testnjs --version

# Example hello command
testnjs hello "example_name"
```

## Configuration

Configuration locations:

- **Linux**: `~/.config/test-nodejs-cli/`
- **macOS**: `~/Library/Application Support/test-nodejs-cli/`
- **Windows**: `%APPDATA%\test-nodejs-cli\`

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
npm link && testnjs --help
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
source completions/testnjs.bash
```

**Zsh:**
```bash
# Add to your ~/.zshrc
fpath=(./completions $fpath)
autoload -U compinit && compinit
```

**Fish:**
```bash
cp completions/testnjs.fish ~/.config/fish/completions/
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
