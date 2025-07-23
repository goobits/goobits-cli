# Goobits CLI

Unified CLI for Goobits projects that streamlines tooling into a single, powerful command-line interface.

## Overview

This tool replaces the previous `goobits-cli-builder` and `goobits-setup-framework` projects by providing a unified `goobits build` command that generates both CLI scripts and setup scripts from a single `goobits.yaml` configuration file.

## Installation

```bash
cd goobits-cli
pip install -e .
```

## Usage

### Build Command

Generate CLI and setup scripts from a `goobits.yaml` configuration:

```bash
# Build from goobits.yaml in current directory
goobits build

# Build from specific config file
goobits build path/to/goobits.yaml

# Build to specific output directory
goobits build --output-dir /path/to/output
```

### Serve Command

Start a local PyPI-compatible server for testing package dependencies:

```bash
# Serve packages from a directory
goobits serve ./packages

# Serve on specific host and port
goobits serve /path/to/packages --host 0.0.0.0 --port 9000

# Install packages from the local server
pip install --index-url http://localhost:8080 --trusted-host localhost PACKAGE_NAME
```

## Configuration Format

The `goobits.yaml` file combines setup configuration with optional CLI configuration:

```yaml
# Basic package information
package_name: goobits-example
command_name: example
display_name: "Example CLI Tool"
description: "An example CLI tool built with goobits"

# Python requirements
python:
  minimum_version: "3.8"
  maximum_version: ""

# Dependencies
dependencies:
  required:
    - git
    - pipx
  optional:
    - curl

# Installation settings
installation:
  pypi_name: goobits-example
  development_path: "."

# Shell integration
shell_integration:
  enabled: false
  alias: "example"

# Validation rules
validation:
  check_api_keys: false
  check_disk_space: true
  minimum_disk_space_mb: 100

# Post-installation messages
messages:
  install_success: |
    Example CLI has been installed successfully!
    Run 'example --help' to get started.
  
  install_dev_success: |
    Example CLI has been installed in development mode!
    Your changes will be reflected immediately.
  
  upgrade_success: |
    Example CLI has been upgraded successfully!
  
  uninstall_success: |
    Example CLI has been uninstalled.

# Optional CLI configuration (for backward compatibility)
cli:
  name: example
  tagline: "An example CLI tool"
  commands:
    hello:
      desc: "Say hello"
```

## Output Files

The `goobits build` command generates:

1. **`cli.py`** - Project-specific CLI script (if CLI configuration is provided)
2. **`setup.sh`** - Project setup script with installation, upgrade, and uninstall functionality

## Project Structure

```
goobits-cli/
├── src/
│   ├── goobits_cli/
│   │   ├── __init__.py
│   │   ├── main.py            # Main CLI logic with build command
│   │   ├── builder.py         # CLI code generation logic
│   │   ├── schemas.py         # Pydantic schemas for validation
│   │   └── templates/
│   │       ├── cli_template.py.j2      # Jinja2 template for CLI code
│   │       └── setup_template.sh.j2    # Jinja2 template for setup script
│   └── __init__.py
├── pyproject.toml             # Project configuration and dependencies
└── README.md                  # This file
```

## Features

- **Unified Configuration**: Single `goobits.yaml` file for all project settings
- **Template-Based Generation**: Uses Jinja2 templates for flexible code generation
- **Schema Validation**: Pydantic schemas ensure configuration correctness
- **Backward Compatibility**: Supports existing CLI configurations
- **Rich Setup Scripts**: Generated setup.sh includes validation, dependency checking, and user-friendly messages
- **Local PyPI Server**: Built-in HTTP server for serving Python packages in Docker environments
- **Dynamic Package Index**: Automatically generates PyPI-compatible index.html for package discovery
- **Cross-Platform Support**: Works on Linux, macOS, and Windows