# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Goobits CLI Framework is a **next-generation multi-language** CLI generator that creates professional command-line interfaces from YAML configuration files. It supports **Python, Node.js, TypeScript, and Rust** with advanced features including **Universal Template System**, **Interactive REPL mode**, **Dynamic completion**, and **Plugin ecosystem**. The framework generates language-specific code with rich terminal interfaces, setup scripts, and installation management.

## Development Commands

### Building and Installation

```bash
# Use the virtual environment when running commands, not the global python (see README for setup details)

# Build the CLI from goobits.yaml (self-hosting)
goobits build

# Build with Universal Template System (experimental)
goobits build --universal-templates

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

The framework generates language-specific CLIs:
```
goobits.yaml → goobits build → [Language-specific output] → Install → Working CLI

Python:   cli.py + setup.sh → pipx install
Node.js:  cli.js + package.json → npm install  
TypeScript: cli.ts + package.json → npm install
Rust:     src/*.rs + Cargo.toml → cargo install
```

### Key Components

1. **main.py** - Entry point with commands: `build`, `init`, `serve`, `upgrade`
2. **schemas.py** - Pydantic models for YAML validation (ConfigSchema, GoobitsConfigSchema)
3. **builder.py** - Routes to language-specific generators based on `language` field
4. **generators/** - Language-specific generators with shared component integration:
   - `python.py` - Python/Click generator with DocumentationGenerator
   - `nodejs.py` - Node.js/Commander generator with validation placeholders
   - `typescript.py` - TypeScript generator with TestDataValidator
   - `rust.py` - Rust/Clap generator with DocumentationGenerator
5. **templates/** - Jinja2 templates organized by language:
   - `templates/` - Python templates
   - `templates/nodejs/` - Node.js templates
   - `templates/typescript/` - TypeScript templates  
   - `templates/rust/` - Rust templates
6. **universal/** - Universal Template System (Phase 3):
   - `template_engine.py` - Core universal template engine
   - `renderers/` - Language-specific renderers for universal templates
   - `components/` - Universal component templates
   - `interactive/` - Interactive REPL mode system
   - `completion/` - Dynamic completion system
   - `plugins/` - Plugin marketplace and management
   - `performance/` - Performance optimization and monitoring
7. **shared/** - Shared Components (Phase 2):
   - `components/` - Validation framework and utilities
   - `schemas/` - Common schema definitions
   - `templates/` - DocumentationGenerator for unified docs

### Configuration Schema

The framework uses two configuration formats:
- **goobits.yaml**: Full project configuration (setup + CLI)
- **CLI section**: Defines commands, arguments, options, subcommands

### Hook System

User projects implement business logic in language-specific hook files:

**Python** - `app_hooks.py`:
```python
def on_command_name(*args, **kwargs):
    # Business logic here
    pass
```

**Node.js/TypeScript** - `src/hooks.js` or `src/hooks.ts`:
```javascript
export async function onCommandName(args) {
    // Business logic here
}
```

**Rust** - `src/hooks.rs`:
```rust
pub fn on_command_name(args: &Args) -> Result<()> {
    // Business logic here
    Ok(())
}
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

The framework supports both legacy and Universal Template Systems:

**Legacy Templates:** Language-specific Jinja2 templates with custom filters:
- `align_examples`: Aligns CLI examples
- `format_multiline`: Handles multi-line text in help
- `escape_docstring`: Escapes strings for Python docstrings

**Universal Template System (Phase 3):** Single template generates for all languages:
- **UniversalTemplateEngine**: Core engine with Intermediate Representation (IR)
- **LanguageRenderers**: Python, Node.js, TypeScript, Rust-specific renderers
- **ComponentRegistry**: Universal component template management
- **Interactive Mode**: REPL-style interaction for all generated CLIs
- **Dynamic Completion**: Context-aware tab completion
- **Plugin System**: Extensible plugin architecture with marketplace

## Implementation History

The repository contains implementation phases and proposals:
- **PROPOSAL_06_UNIFIED_IMPLEMENTATION.md**: Master implementation roadmap (✅ COMPLETED)
- **Phase 0**: Foundation - Complete language implementations (✅ COMPLETED)
- **Phase 1**: Testing Framework - YAML-based CLI testing (✅ COMPLETED) 
- **Phase 2**: Shared Components - Validation and documentation integration (✅ COMPLETED)
- **Phase 3**: Universal Template System - Single-source multi-language generation (✅ COMPLETED)
- **Phase 4**: Advanced Features - Interactive mode, plugins, performance optimization (✅ COMPLETED)

## Common Tasks

### Selecting Target Language

Add the `language` field to your `goobits.yaml`:
```yaml
language: python      # Default if not specified
# or
language: nodejs      # Node.js with Commander.js
language: typescript  # TypeScript with type safety
language: rust        # Rust with Clap
```

### Adding a New Command

1. Update the CLI section in `goobits.yaml`
2. Run `goobits build`
3. Implement the hook in your language-specific hook file:
   - Python: `app_hooks.py`
   - Node.js: `src/hooks.js`
   - TypeScript: `src/hooks.ts`
   - Rust: `src/hooks.rs`

### Debugging Generated Code

The generated CLI includes the source YAML filename in comments for traceability.

### Working with Templates

Templates are in `src/goobits_cli/templates/`. After modifying:
1. Run `goobits build` to regenerate (or `goobits build --universal-templates` for universal system)
2. Test with `./setup.sh install --dev`

### Using Advanced Features

**Interactive Mode:** Generated CLIs support REPL-style interaction:
```bash
my-cli --interactive  # Launch interactive mode
```

**Universal Templates:** Generate CLIs using the universal template system:
```bash
goobits build --universal-templates
```

**Performance Monitoring:** Built-in performance optimization ensures <100ms startup times with comprehensive monitoring and lazy loading.

**Plugin System:** Extensible architecture with secure plugin marketplace integration (framework ready, activation in future release).