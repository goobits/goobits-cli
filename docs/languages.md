# Language Support Guide

Goobits generates production-ready CLIs in Python, Node.js, TypeScript, and Rust from a single YAML configuration.

## Quick Language Selection

```yaml
language: python      # Default
# or: nodejs, typescript, rust
```

## Python

```yaml
language: python
cli_path: "cli.py"  # Optional, this is default

python:
  minimum_version: "3.8"
  maximum_version: "3.13"
```

**Generated Files:**
- `cli.py` - Complete CLI with all utilities embedded
- `setup.sh` - Installation script

**Hook File:** `cli_hooks.py`
```python
def on_command_name(*args, **kwargs):
    """Your business logic here"""
    print(f"Hello from Python!")
```

## Node.js

```yaml
language: nodejs
cli_path: "cli.mjs"  # Optional, this is default

nodejs:
  minimum_version: "14.0.0"
  package_manager: npm  # or yarn, pnpm
```

**Generated Files:**
- `cli.mjs` - ES6 module with embedded components
- `setup.sh` - Installation script with npm setup

**Hook File:** `cli_hooks.mjs`
```javascript
export async function on_command_name(args) {
    console.log("Hello from Node.js!");
}
```

## TypeScript

```yaml
language: typescript
cli_path: "cli.ts"  # Optional, this is default

typescript:
  strict_mode: true
  target: "ES2020"
  module: "commonjs"
```

**Generated Files:**
- `cli.ts` - TypeScript CLI implementation
- `cli_types.d.ts` - Type definitions
- `setup.sh` - Build and installation script

**Hook File:** `cli_hooks.ts`
```typescript
export async function on_command_name(args: any): Promise<void> {
    console.log("Hello from TypeScript!");
}
```

## Rust

```yaml
language: rust
cli_path: "src/main.rs"  # Optional, this is default

rust:
  minimum_version: "1.70.0"
  edition: "2021"
  release_build: true
```

**Generated Files:**
- `src/main.rs` - Rust CLI with inline modules
- `setup.sh` - Cargo build and installation

**Hook File:** `src/cli_hooks.rs`
```rust
use clap::ArgMatches;
use anyhow::Result;

pub fn on_command_name(matches: &ArgMatches) -> Result<()> {
    println!("Hello from Rust!");
    Ok(())
}
```

## Performance Comparison

| Language   | Startup Time | Memory Usage | Binary Size |
|------------|--------------|--------------|-------------|
| Rust       | ~10ms        | ~1MB         | ~2MB        |
| Node.js    | ~24ms        | ~20MB        | N/A         |
| Python     | ~72ms        | ~15MB        | N/A         |
| TypeScript | ~30ms        | ~25MB        | N/A         |

## Choosing a Language

- **Python**: Best for data science, scripting, rapid prototyping
- **Node.js**: Best for web tooling, npm ecosystem integration
- **TypeScript**: Best for type safety, large teams, enterprise
- **Rust**: Best for performance-critical tools, system utilities

## Package Manager Integration

Each language integrates with its native package manager:

- **Python**: pip/pipx, PyPI publishing ready
- **Node.js**: npm/yarn/pnpm, npmjs.com ready
- **TypeScript**: Same as Node.js + type definitions
- **Rust**: cargo, crates.io ready

## Advanced Configuration

See [Configuration Reference](user-guide/configuration.md) for complete language-specific options including:
- Custom package metadata
- Build configurations
- Runtime requirements
- Dependency management