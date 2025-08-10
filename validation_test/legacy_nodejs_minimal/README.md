# NodeJS Test CLI

A NodeJS test CLI for validation

> A simple NodeJS test CLI

## Installation

### From Package Manager (Recommended)

```bash
npm install -g nodejs-test-cli
```

### From Source

Clone this repository and build from source:

```bash
git clone https://github.com/user/repo
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

#### `nodejs-test hello`
Say hello to someone

```bash
nodejs-test hello [OPTIONS]```


**Options:**
- `--name <str>`: Name to greet (default: World)

### Global Options


### Examples

```bash
# Show help
nodejs-test --help

# Show version
nodejs-test --version

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
npm link && nodejs-test --help
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
source completions/nodejs-test.bash
```

**Zsh:**
```bash
# Add to your ~/.zshrc
fpath=(./completions $fpath)
autoload -U compinit && compinit
```

**Fish:**
```bash
cp completions/nodejs-test.fish ~/.config/fish/completions/
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
- `hello` command: Say hello to someone
