# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Goobits CLI Framework is a tool that generates professional command-line interfaces from YAML configuration files. It creates rich terminal interfaces, setup scripts, and handles installation management automatically.

## Development Commands

### Building and Installation

```bash
# Build the CLI from goobits.yaml (self-hosting)
goobits build

# Install in development mode (includes dev dependencies, changes reflected immediately)
./setup.sh install --dev

# Install in production mode (production dependencies only)
./setup.sh install

# Upgrade existing installation
./setup.sh upgrade

# Uninstall
./setup.sh uninstall
```

### Testing

```bash
# Run all tests
pytest src/tests/

# Run specific test file
pytest src/tests/unit/test_builder.py

# Run with coverage
pytest --cov=goobits_cli src/tests/

# Run integration tests only
pytest src/tests/integration/

# Run e2e tests only
pytest src/tests/e2e/
```

### Linting and Type Checking

```bash
# Run mypy for type checking
mypy src/goobits_cli/

# Python linting (ruff installed automatically with dev extras)
ruff check src/
```

## Architecture

### Code Generation Flow

The framework follows this generation pattern:
```
goobits.yaml → goobits build → generated_cli.py + setup.sh → ./setup.sh install --dev → working CLI
```

### Key Components

1. **main.py** - Entry point with commands: `build`, `init`, `serve`, `upgrade`
2. **schemas.py** - Pydantic models for YAML validation (ConfigSchema, GoobitsConfigSchema)
3. **builder.py** - Generates Python CLI code from YAML using Jinja2 templates
4. **templates/** - Jinja2 templates for CLI and setup script generation
5. **generated_cli.py** - Self-hosted CLI (generated from goobits.yaml)

### Configuration Schema

The framework uses two configuration formats:
- **goobits.yaml**: Full project configuration (setup + CLI)
- **CLI section**: Defines commands, arguments, options, subcommands

### Hook System

User projects implement business logic via `app_hooks.py`:
```python
def on_command_name(*args, **kwargs):
    # Business logic here
    pass
```

### Self-Hosting

This project uses itself to generate its own CLI. The `goobits.yaml` file in the root configures the `goobits` command, which is built using:
```bash
goobits build  # Generates src/goobits_cli/generated_cli.py
```

## Important Implementation Details

### Dependency Handling

Dependencies are now managed through the structured extras format in the installation section:
```yaml
installation:
  pypi_name: my-package
  development_path: "."
  extras:
    python: ["dev", "test"]      # Python extras from pyproject.toml
    apt: ["git", "python3-dev"]   # System packages (installed automatically)
    npm: ["prettier"]            # NPM packages (if needed)
```

The setup.sh script automatically installs all specified dependencies:
- Python extras are installed with pip
- APT packages prompt for sudo password when needed
- NPM packages are installed globally

### Generated Files

- **generated_cli.py**: Created by `goobits build`, should not be edited manually
- **setup.sh**: Platform-aware installation script with dependency checking

### Template System

Uses Jinja2 with custom filters for formatting:
- `align_examples`: Aligns CLI examples
- `format_multiline`: Handles multi-line text in help
- `escape_docstring`: Escapes strings for Python docstrings

## Proposals

The repository contains unimplemented proposals in the root:
- **PROPOSAL_TESTING_FRAMEWORK.md**: Framework for YAML-based CLI testing (not implemented)
- **PROPOSAL_01_RUST.md**: Multi-language support starting with Rust (not implemented)
- **PROPOSAL_02_UNIVERSAL.md**: Universal CLI DSL for multiple languages (depends on PROPOSAL_01)

## Common Tasks

### Adding a New Command

1. Update the CLI section in `goobits.yaml`
2. Run `goobits build`
3. Implement the hook in target project's `app_hooks.py`

### Debugging Generated Code

The generated CLI includes the source YAML filename in comments for traceability.

### Working with Templates

Templates are in `src/goobits_cli/templates/`. After modifying:
1. Run `goobits build` to regenerate
2. Test with `./setup.sh install --dev`