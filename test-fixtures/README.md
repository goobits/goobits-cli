# Test Fixtures

This directory contains test configurations and their outputs for the Goobits CLI Framework.

## Structure

- `configs/` - Test YAML configuration files organized by language
  - `python/` - Python test configurations
  - `nodejs/` - Node.js test configurations
  - `typescript/` - TypeScript test configurations
  - `rust/` - Rust test configurations
  
- `outputs/` - Generated test outputs (gitignored)
  - Organized by language, contains generated CLIs from test runs

## Usage

To run a test configuration:
```bash
goobits build test-fixtures/configs/python/basic.yaml --output test-fixtures/outputs/python/
```

## Note

The `outputs/` directory is gitignored. Generated files should not be committed to the repository.
