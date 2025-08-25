# Configuration Reference

Complete reference for `goobits.yaml` configuration files.

## Basic Structure

```yaml
# Project metadata
package_name: my-cli
command_name: mycli
display_name: "My Awesome CLI"
description: "A description of what my CLI does"
language: python  # python, nodejs, typescript, or rust

# CLI generation
cli_output_path: "src/my_cli/cli.py"  # Optional, language-specific defaults
cli_hooks: "app_hooks.py"  # Hook file path (language-specific)

# CLI definition
cli:
  name: "My CLI"
  version: "3.0.0-alpha.1"
  tagline: "Short description"
  
  commands:
    hello:
      desc: "Say hello"
      args:
        - name: "name"
          desc: "Name to greet"
          required: true
```

## Language-Specific Settings

### Python Configuration
```yaml
language: python
cli_hooks: "app_hooks.py"
cli_output_path: "cli.py"  # Default

python:
  minimum_version: "3.8"
  maximum_version: "3.13"
```

### Node.js Configuration
```yaml
language: nodejs
cli_hooks: "src/hooks.js"
cli_output_path: "cli.js"  # Default
```

### TypeScript Configuration
```yaml
language: typescript
cli_hooks: "src/hooks.ts"
cli_output_path: "cli.ts"  # Default
```

### Rust Configuration
```yaml
language: rust
cli_hooks: "src/hooks.rs"
cli_output_path: "src/main.rs"  # Default
```

## Advanced Configuration

### Installation Settings
```yaml
installation:
  pypi_name: my-cli
  development_path: "."
  extras:
    python: ["dev", "test"]      # Python extras from pyproject.toml
    apt: ["git", "python3-dev"]   # System packages
    npm: ["prettier"]            # NPM packages
```

### Dependencies
```yaml
dependencies:
  required: ["requests", "click"]
  optional: ["pytest"]
```

### Messages
```yaml
messages:
  install_success: |
    🎉 CLI installed successfully!
    Get started with: mycli --help
```

## CLI Schema

### Commands
```yaml
cli:
  commands:
    command_name:
      desc: "Command description"
      icon: "🔨"  # Optional emoji
      args:
        - name: "arg_name"
          desc: "Argument description"
          required: true
      options:
        - name: "option-name"
          short: "o"
          type: "str"  # str, int, flag
          desc: "Option description"
          default: "value"
```

### Global Options
```yaml
cli:
  options:
    - name: "verbose"
      short: "v"
      type: "flag"
      desc: "Enable verbose output"
```

### Command Groups
```yaml
cli:
  command_groups:
    - name: "Core Commands"
      commands: ["build", "init"]
    - name: "Development Tools"
      commands: ["serve"]
```

## Complete Example

See the framework's own configuration: [`goobits.yaml`](../../goobits.yaml)

## Validation

The framework uses Pydantic for configuration validation. Common validation errors:

- **Missing required fields**: `package_name`, `cli.name`
- **Invalid language**: Must be one of `python`, `nodejs`, `typescript`, `rust`
- **Invalid command structure**: Commands must have `desc` field
- **Invalid option types**: Must be `str`, `int`, or `flag`

Run `goobits build` to validate your configuration.