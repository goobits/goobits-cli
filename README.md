# Goobits CLI Framework

**Build professional command-line tools with YAML configuration.** Goobits CLI generates rich terminal interfaces, setup scripts, and handles installation management automatically.

## What is Goobits CLI?

Goobits CLI transforms a simple YAML file into a complete command-line application with:
- Rich terminal interface with colors and help formatting
- Professional setup scripts with dependency checking
- Pipe support (`echo "text" | your-cli`)
- Plugin system for extensions
- Cross-platform installation with pipx

**Used by:** TTT (AI text processing), TTS (text-to-speech), STT (speech-to-text), and other Goobits tools.

## Quick Start

### 1. Install Goobits CLI
```bash
pipx install goobits-cli
# or clone and install locally:
# git clone https://github.com/goobits/goobits-cli
# cd goobits-cli && pipx install -e .
```

### 2. Create Your First CLI
```bash
mkdir my-awesome-cli
cd my-awesome-cli

# Create goobits.yaml
cat > goobits.yaml << 'EOF'
package_name: my-awesome-cli
command_name: awesome
display_name: "Awesome CLI"
description: "My first Goobits CLI tool"

python:
  minimum_version: "3.8"

dependencies:
  required: ["pipx"]

cli:
  name: awesome
  tagline: "An awesome command-line tool"
  commands:
    greet:
      desc: "Greet someone"
      args:
        - name: name
          desc: "Name to greet"
          required: true
      options:
        - name: greeting
          short: g
          desc: "Custom greeting"
          default: "Hello"
EOF
```

### 3. Generate Your CLI
```bash
goobits build
# This creates:
# - src/my_awesome_cli/cli.py (your CLI interface)
# - setup.sh (installation script)
```

### 4. Add Your Business Logic
```bash
# Create the app hooks file
mkdir -p src/my_awesome_cli
cat > src/my_awesome_cli/app_hooks.py << 'EOF'
import click

def on_greet(name, greeting):
    """Handle the greet command"""
    click.echo(f"{greeting}, {name}!")
    return f"{greeting}, {name}!"
EOF
```

### 5. Install and Test
```bash
./setup.sh install --dev  # Development installation
awesome greet World        # Test your CLI
awesome greet World -g "Hi"  # With custom greeting
echo "Alice" | awesome greet  # Pipe support works automatically!
```

## Development Workflow

### The Goobits Pattern
```
goobits.yaml → goobits build → cli.py + setup.sh → ./setup.sh install --dev → working CLI
```

### Daily Development Cycle
```bash
# 1. Modify your business logic
vim src/my_awesome_cli/app_hooks.py

# 2. Test immediately (changes reflected instantly)
awesome greet "Test"

# 3. Add new commands/options? Update config
vim goobits.yaml

# 4. Rebuild CLI structure
goobits build

# 5. Update installation
./setup.sh upgrade
```

### Development vs Production Installation
```bash
# For development (changes reflected immediately)
./setup.sh install --dev

# For end users (stable, isolated)
./setup.sh install

# Upgrade existing installation
./setup.sh upgrade

# Remove completely
./setup.sh uninstall
```

## Real-World Examples

### Text Processing Tool
```yaml
# goobits.yaml
package_name: text-processor
command_name: textproc
display_name: "Text Processor"

cli:
  name: textproc
  tagline: "Process text files with ease"
  commands:
    process:
      desc: "Process text file"
      is_default: true  # Makes this the default command
      args:
        - name: text
          desc: "Text to process"
          nargs: "*"
      options:
        - name: uppercase
          short: u
          type: flag
          desc: "Convert to uppercase"
        - name: output
          short: o
          desc: "Output file"
```

```python
# src/text_processor/app_hooks.py
import click
import sys

def on_process(text, uppercase, output):
    # Handle stdin input automatically
    if not text and not sys.stdin.isatty():
        text = [sys.stdin.read().strip()]
    
    if not text:
        click.echo("Error: No text provided", err=True)
        return
    
    content = " ".join(text)
    if uppercase:
        content = content.upper()
    
    if output:
        with open(output, 'w') as f:
            f.write(content)
        click.echo(f"Written to {output}")
    else:
        click.echo(content)
```

```bash
# Usage examples:
textproc "hello world" --uppercase        # Direct text
echo "hello world" | textproc --uppercase # Pipe input
cat file.txt | textproc -u -o output.txt  # Process file
```

### API Client Tool
```yaml
# goobits.yaml for an API client
package_name: weather-cli
command_name: weather
display_name: "Weather CLI"

dependencies:
  required: ["pipx", "curl"]

cli:
  name: weather
  tagline: "Get weather information"
  commands:
    current:
      desc: "Get current weather"
      is_default: true
      args:
        - name: city
          desc: "City name"
          required: true
      options:
        - name: api-key
          desc: "API key for weather service"
        - name: format
          short: f
          choices: ["json", "text"]
          default: "text"
          desc: "Output format"
```

## Configuration Reference

### Essential Configuration
```yaml
# Required fields
package_name: my-package        # Package name (used by pip/pipx)
command_name: mycli            # Command users type
display_name: "My CLI Tool"    # Human-readable name
description: "What it does"    # Brief description

# Python requirements
python:
  minimum_version: "3.8"      # Minimum Python version
  maximum_version: "3.12"     # Maximum (optional)

# System dependencies
dependencies:
  required: ["git", "pipx"]    # Must be installed
  optional: ["curl", "jq"]     # Nice to have
```

### CLI Commands Structure
```yaml
cli:
  name: mycli
  tagline: "One-line description"
  commands:
    mycommand:
      desc: "Command description"
      is_default: true          # Makes this the default command
      args:
        - name: input
          desc: "Input parameter"
          nargs: "*"            # Multiple arguments
          required: true
      options:
        - name: verbose
          short: v
          type: flag            # Boolean flag
          desc: "Verbose output"
        - name: output
          short: o
          type: str
          desc: "Output file"
          default: "output.txt"
        - name: format
          short: f
          choices: ["json", "yaml", "text"]
          default: "text"
          desc: "Output format"
```

### Installation Customization
```yaml
installation:
  pypi_name: my-package-name   # Name on PyPI (if different)
  development_path: "."        # Path for dev install

validation:
  check_disk_space: true       # Check available disk space
  minimum_disk_space_mb: 100   # Minimum MB required

messages:
  install_success: |
    🎉 My CLI has been installed!
    Get started with: mycli --help
    
  install_dev_success: |
    🚀 Development mode active!
    Your code changes are live - no reinstall needed.
```

## Troubleshooting

### Common Issues

**"Command not found after install"**
```bash
# Fix PATH issue
pipx ensurepath
source ~/.bashrc  # or restart terminal
```

**"Changes not reflected"**
```bash
# Make sure you're using dev install
./setup.sh install --dev
# Check installation type
pipx list | grep your-package
```

**"Failed to load plugin loader"**
```bash
# This is fixed in latest version
pipx upgrade goobits-cli
cd your-project && goobits build && ./setup.sh upgrade
```

**"Module not found during development"**
```bash
# Reinstall in development mode
./setup.sh uninstall
./setup.sh install --dev
```

### Development Tips

**Quick Testing**
```bash
# Test CLI generation without install
goobits build --output-dir /tmp/test-cli
python /tmp/test-cli/cli.py --help
```

**Debug App Hooks**
```python
# Add debugging to app_hooks.py
import click

def on_mycommand(*args, **kwargs):
    click.echo(f"DEBUG: args={args}, kwargs={kwargs}")
    # Your actual logic here
```

**Plugin Development**
```python
# Create plugins/my_plugin.py
def register_plugin(cli_group):
    @cli_group.command()
    def myplugin():
        """My custom plugin command"""
        click.echo("Plugin works!")
```

## Advanced Features

### Pipe Support (Automatic)
All Goobits CLIs support piping automatically:
```bash
echo "input" | mycli           # Works automatically
cat file.txt | mycli process   # Pipe to specific command  
mycli generate | mycli format  # Chain commands
```

### Rich Terminal Interface
Goobits CLIs include rich formatting automatically:
- Colored help text with emoji icons
- Organized command groups
- Professional error messages
- Progress indicators

### Plugin System
```bash
# Plugin directories (searched automatically):
~/.config/goobits/my-cli/plugins/
./plugins/
```

### Integration Examples
```bash
# Text processing pipeline
echo "fix this grammar" | ttt | tts        # Fix grammar, then speak
stt recording.wav | ttt "summarize" | tts  # Transcribe, summarize, speak

# API workflow  
mycli fetch-data | jq '.results[]' | mycli process
```

## Next Steps

1. **Study existing examples**: Look at TTT, TTS, STT in the Goobits ecosystem
2. **Read the generated code**: Check out `src/your_cli/cli.py` after building
3. **Explore advanced config**: Add subcommands, command groups, custom validation
4. **Create plugins**: Extend functionality with the plugin system
5. **Share your CLI**: Publish to PyPI for others to install with `pipx install your-package`

---

**🚀 Ready to build professional CLIs with minimal boilerplate? Start with `goobits build` and let the framework handle the complexity!**