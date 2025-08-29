# Commands Reference

Complete reference for all Goobits CLI commands.

## Core Commands

### `goobits build`
Generate CLI from configuration file.

```bash
goobits build [CONFIG_PATH] [OPTIONS]
```

**Arguments:**
- `CONFIG_PATH` - Path to goobits.yaml (default: `./goobits.yaml`)

**Options:**
- `--output-dir PATH` - Output directory (default: config file directory)
- `--output TEXT` - CLI filename (default: `generated_cli.py`)
- `--backup` - Create .bak files when overwriting

**Examples:**
```bash
# Default build
goobits build

# Custom config location
goobits build configs/my-cli.yaml

# Custom output
goobits build --output cli.py --output-dir src/
```

### `goobits init`
Create initial goobits.yaml template.

```bash
goobits init [OPTIONS]
```

**Options:**
- `--template TEXT` - Template type: `basic`, `advanced`, `api-client`
- `--force` - Overwrite existing goobits.yaml

**Examples:**
```bash
# Basic template
goobits init

# Advanced template
goobits init --template advanced

# Force overwrite
goobits init --force
```

### `goobits validate`
Validate configuration without generating files.

```bash
goobits validate [CONFIG_PATH] [OPTIONS]
```

**Arguments:**
- `CONFIG_PATH` - Path to goobits.yaml

**Options:**
- `--verbose` - Show detailed validation information

**Examples:**
```bash
# Validate default config
goobits validate

# Validate specific file
goobits validate my-config.yaml --verbose
```

### `goobits migrate`
Migrate configurations to latest format.

```bash
goobits migrate PATH [OPTIONS]
```

**Arguments:**
- `PATH` - File or directory to migrate (required)

**Options:**
- `--backup` - Create .bak backup files
- `--dry-run` - Show changes without applying

**Examples:**
```bash
# Migrate single file
goobits migrate old-config.yaml --backup

# Migrate directory
goobits migrate ./configs/

# Preview changes
goobits migrate config.yaml --dry-run
```

### `goobits serve`
Serve local PyPI-compatible package index.

```bash
goobits serve DIRECTORY [OPTIONS]
```

**Arguments:**
- `DIRECTORY` - Directory containing packages (required)

**Options:**
- `--host TEXT` - Server host (default: `localhost`)
- `--port INT` - Server port (default: `8080`)

**Examples:**
```bash
# Serve current directory
goobits serve .

# Custom host/port
goobits serve dist/ --host 0.0.0.0 --port 3000
```

### `goobits upgrade`
Upgrade goobits-cli to latest version.

```bash
goobits upgrade [OPTIONS]
```

**Options:**
- `--check` - Check for updates without installing
- `--pre` - Include pre-release versions

**Examples:**
```bash
# Upgrade to latest stable
goobits upgrade

# Check for updates
goobits upgrade --check

# Include pre-releases
goobits upgrade --pre
```

## Global Options

These options work with all commands:

- `--version` - Show version and exit
- `--help` - Show help message
- `--install-completion` - Install shell completion
- `--show-completion` - Show completion script

## Environment Variables

- `GOOBITS_CONFIG` - Default config file path
- `GOOBITS_OUTPUT_DIR` - Default output directory
- `GOOBITS_LANGUAGE` - Default target language
- `GOOBITS_DEBUG` - Enable debug logging

## Configuration File

Commands use `goobits.yaml` by default. See [Configuration Reference](user-guide/configuration.md) for schema details.

## Exit Codes

- `0` - Success
- `1` - General error
- `2` - Configuration error
- `3` - Validation error
- `4` - File not found
- `5` - Permission denied

## Common Workflows

### Create New CLI
```bash
goobits init
# Edit goobits.yaml
goobits validate
goobits build
./setup.sh install --dev
```

### Update Existing CLI
```bash
# Edit goobits.yaml
goobits validate
goobits build --backup
```

### Migrate Old Project
```bash
goobits migrate old-config.yaml --backup
goobits validate
goobits build
```

## Troubleshooting

See [Troubleshooting Guide](user-guide/troubleshooting.md) for common issues and solutions.