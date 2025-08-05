# Proposal: Fix Rust Generator to Prevent Overwrites and Minimize File Generation

## Problem Statement

The current Rust generator has critical issues:
1. **Overwrites existing source files** without warning or backup
2. **Generates 10+ files** creating an entire framework instead of a minimal CLI
3. **Violates core Goobits principles** of simplicity and non-destructiveness

## Proposed Solution

### 1. Minimize Generated Files

The Rust generator should match the Python generator's minimal approach:

**Current (TOO MANY):**
```
src/main.rs          ❌ Overwrites user's main.rs!
src/lib.rs
src/config.rs
src/commands.rs
src/utils.rs
src/errors.rs
src/hooks.rs
src/plugins.rs
src/styling.rs
src/completion_engine.rs
Cargo.toml
setup.sh
README.md
.gitignore
```

**Proposed (MINIMAL):**
```
src/cli.rs           ✅ New file, won't conflict
src/hooks.rs         ✅ User implements business logic here
Cargo.toml           ⚠️ Check if exists first
setup.sh             ✅ Installation script
README.md            ⚠️ Check if exists first
.gitignore           ⚠️ Append, don't overwrite
```

### 2. File Conflict Resolution

Implement a safety-first approach:

```python
# In rust.py generator
def generate_all_files(self, config, config_filename, version=None):
    files = {}
    
    # Check for existing Cargo.toml
    if Path("Cargo.toml").exists():
        if not self._should_modify_cargo_toml():
            self._warn_user_about_cargo_toml()
            files['Cargo.toml.goobits'] = self._generate_cargo_toml(context)
        else:
            # Add goobits binary entry to existing Cargo.toml
            files['Cargo.toml'] = self._update_existing_cargo_toml(context)
    else:
        files['Cargo.toml'] = self._generate_cargo_toml(context)
    
    # NEVER overwrite src/main.rs
    if Path("src/main.rs").exists():
        # Generate as src/cli.rs instead
        files['src/cli.rs'] = self._generate_cli_file(context)
        files['src/cli_hooks.rs'] = self._generate_hooks_file(context)
        print("⚠️  Existing src/main.rs detected. Generated src/cli.rs instead.")
    else:
        files['src/main.rs'] = self._generate_cli_file(context)
        files['src/hooks.rs'] = self._generate_hooks_file(context)
```

### 3. Parallel Structure with Python Generator

The Rust generator should create files that mirror the Python generator's style and structure:

#### Python Generator Creates:
```
cli.py                 # CLI definition with click decorators
app_hooks.py          # User's business logic
setup.sh              # Installation script
config_manager.py     # Config helper (if needed)
completion_engine.py  # Tab completion (if enabled)
```

#### Rust Generator Should Create (SAME PATTERN):
```
cli.rs                # CLI definition with clap derives
app_hooks.rs          # User's business logic
setup.sh              # Installation script
Cargo.toml            # (Rust equivalent of pyproject.toml)
```

### 4. Stylistic Consistency Examples

#### Python cli.py structure:
```python
#!/usr/bin/env python3
"""Auto-generated from goobits.yaml"""
import click
from app_hooks import on_daily, on_monthly

@click.group()
@click.version_option()
def main():
    """Fast Python implementation for Claude usage analysis"""
    pass

@main.command()
@click.option('--json', is_flag=True, help='Output in JSON format')
@click.option('--limit', type=int, help='Show last N entries')
def daily(json, limit):
    """Show daily usage with project breakdown"""
    on_daily(json=json, limit=limit)

@main.command()
@click.option('--json', is_flag=True, help='Output in JSON format')
@click.option('--limit', type=int, help='Show last N entries')
def monthly(json, limit):
    """Show monthly usage aggregation"""
    on_monthly(json=json, limit=limit)

if __name__ == '__main__':
    main()
```

#### Rust cli.rs should mirror this structure:
```rust
//! Auto-generated from goobits.yaml
use clap::{Parser, Subcommand};

mod app_hooks;
use app_hooks::{on_daily, on_monthly};

#[derive(Parser)]
#[command(author, version, about = "Fast Rust implementation for Claude usage analysis")]
struct Cli {
    #[command(subcommand)]
    command: Commands,
}

#[derive(Subcommand)]
enum Commands {
    /// Show daily usage with project breakdown
    Daily {
        /// Output in JSON format
        #[arg(long)]
        json: bool,
        /// Show last N entries
        #[arg(long)]
        limit: Option<usize>,
    },
    /// Show monthly usage aggregation
    Monthly {
        /// Output in JSON format
        #[arg(long)]
        json: bool,
        /// Show last N entries
        #[arg(long)]
        limit: Option<usize>,
    },
}

fn main() {
    let cli = Cli::parse();
    
    match cli.command {
        Commands::Daily { json, limit } => {
            on_daily(json, limit);
        }
        Commands::Monthly { json, limit } => {
            on_monthly(json, limit);
        }
    }
}
```

#### Python app_hooks.py structure:
```python
#!/usr/bin/env python3
"""Hook implementations for claude-usage"""

def on_daily(json=False, limit=None, **kwargs):
    """Show daily usage with project breakdown"""
    # TODO: Implement daily command
    print("Daily command called with:", locals())

def on_monthly(json=False, limit=None, **kwargs):
    """Show monthly usage aggregation"""
    # TODO: Implement monthly command
    print("Monthly command called with:", locals())
```

#### Rust app_hooks.rs should mirror this:
```rust
//! Hook implementations for claude-usage

pub fn on_daily(json: bool, limit: Option<usize>) {
    // Show daily usage with project breakdown
    // TODO: Implement daily command
    println!("Daily command called with: json={}, limit={:?}", json, limit);
}

pub fn on_monthly(json: bool, limit: Option<usize>) {
    // Show monthly usage aggregation
    // TODO: Implement monthly command
    println!("Monthly command called with: json={}, limit={:?}", json, limit);
}
```

### Key Consistency Points:

1. **File naming**: Use `cli.rs` and `app_hooks.rs` to match Python's `cli.py` and `app_hooks.py`
2. **Structure**: Simple, flat structure - no complex module hierarchies
3. **Comments**: Same style - auto-generated header, TODOs in hooks
4. **Organization**: CLI definition separate from business logic
5. **Simplicity**: Minimal boilerplate, focus on the commands

### 4. Implementation Changes

#### Update rust.py

```python
def get_output_files(self) -> List[str]:
    """Return minimal list of files this generator creates."""
    return [
        "src/cli.rs",      # Or src/main.rs if no conflict
        "src/hooks.rs",    # User's business logic
        "Cargo.toml",      # Package manifest
        "setup.sh",        # Installation script
        "README.md",       # Documentation
        ".gitignore"       # Git ignore
    ]
```

#### Add to builder.py

```python
# Global option for all generators
@click.option('--force', is_flag=True, help='Overwrite existing files (use with caution)')
@click.option('--backup', is_flag=True, help='Create .bak files when overwriting')
def build(config_path, output_dir, output, backup, force):
    # Pass force flag to generator
    generator.generate_all_files(config, config_filename, version, force=force)
```

### 5. Safety Features

1. **Default behavior**: NEVER overwrite without explicit permission
2. **Conflict detection**: Warn user about existing files
3. **Alternative names**: Use `cli.rs` if `main.rs` exists
4. **Backup option**: Create `.bak` files when `--backup` is used
5. **Dry run**: Add `--dry-run` to show what would be generated

### 6. Migration Path

For users who already generated with the current version:
1. Document the issue in release notes
2. Provide cleanup script to remove excess files
3. Recommend using git to revert unwanted changes

## Visual Comparison: Python vs Rust Output

### Python Generator Output:
```
my-python-cli/
├── cli.py              # ~200 lines - Click-based CLI
├── app_hooks.py        # ~50 lines - User implements here
├── setup.sh            # ~300 lines - Installation script
├── .gitignore          # ~20 lines - Python ignores
└── (optional)
    ├── config_manager.py
    └── completion_engine.py
```

### Rust Generator Output (SHOULD BE):
```
my-rust-cli/
├── cli.rs              # ~200 lines - Clap-based CLI
├── app_hooks.rs        # ~50 lines - User implements here  
├── Cargo.toml          # ~30 lines - Package manifest
├── setup.sh            # ~300 lines - Installation script
└── .gitignore          # ~20 lines - Rust ignores
```

### NOT THIS (current problematic output):
```
my-rust-cli/
├── src/
│   ├── main.rs         # ❌ Overwrites user's code!
│   ├── lib.rs          # ❌ Too many files!
│   ├── config.rs       # ❌ 
│   ├── commands.rs     # ❌
│   ├── utils.rs        # ❌
│   ├── errors.rs       # ❌
│   ├── hooks.rs        # ❌
│   ├── plugins.rs      # ❌
│   ├── styling.rs      # ❌
│   └── completion.rs   # ❌
└── ... (14+ files total)
```

## Benefits

1. **Non-destructive**: Respects existing code
2. **Minimal**: Only generates essential files (4-5 files max)
3. **Consistent**: Same structure across all languages
4. **Simple**: Easy to understand and modify
5. **Safe**: No data loss from overwrites
6. **Predictable**: Users know what to expect

## 7. Universal Templates Approach

Instead of maintaining separate templates for each language, we could use **universal Jinja templates** with language conditionals. This would guarantee consistency across all generators.

### Universal Template Example

```jinja
{#- Universal cli.j2 template for all languages -#}
{%- if language == 'python' -%}
#!/usr/bin/env python3
"""Auto-generated from {{ file_name }}"""
import click
from app_hooks import {{ commands.keys() | map('prefix_on_') | join(', ') }}

@click.group()
@click.version_option(version='{{ version }}')
def main():
    """{{ description }}"""
    pass
{%- elif language == 'rust' -%}
//! Auto-generated from {{ file_name }}
use clap::{Parser, Subcommand};

mod app_hooks;
use app_hooks::{
{%- for cmd in commands.keys() %}
    on_{{ cmd }}{{ ", " if not loop.last else "" }}
{%- endfor %}
};

#[derive(Parser)]
#[command(author, version = "{{ version }}", about = "{{ description }}")]
struct Cli {
    #[command(subcommand)]
    command: Commands,
}
{%- elif language == 'javascript' -%}
#!/usr/bin/env node
const { Command } = require('commander');
const hooks = require('./app_hooks');

const program = new Command();
program
    .name('{{ command_name }}')
    .description('{{ description }}')
    .version('{{ version }}');
{%- endif %}

{#- Command definitions use same structure, different syntax -#}
{%- for cmd_name, cmd in commands.items() %}
  {#- ... language-specific command syntax ... -#}
{%- endfor %}
```

### Benefits of Universal Templates

1. **Single Source of Truth**: One template maintains all languages
2. **Impossible to Diverge**: Languages can't have different structures
3. **Easier Maintenance**: Update once, apply everywhere
4. **Automatic Feature Parity**: New features work for all languages
5. **60% Less Code**: Eliminate duplicate templates

### Implementation

```python
# BaseGenerator uses universal templates
class BaseGenerator:
    def __init__(self, language):
        self.language = language
        self.env = Environment(loader=FileSystemLoader([
            'templates/universal',     # Shared templates
            f'templates/{language}'    # Language-specific (Cargo.toml, package.json)
        ]))
        
        # Add language to all template contexts
        self.env.globals['language'] = language
        
        # Language-specific filters
        self.env.filters.update(self.get_language_filters())
```

### Template Organization

```
templates/
├── universal/           # Used by all languages
│   ├── cli.j2          # Main CLI structure
│   ├── app_hooks.j2    # Hook implementations
│   ├── setup.sh.j2     # Installation script
│   └── README.md.j2    # Documentation
├── python/             # Python-specific only
│   └── pyproject.toml.j2
├── rust/               # Rust-specific only
│   └── Cargo.toml.j2
└── nodejs/             # Node.js-specific only
    └── package.json.j2
```

This approach ensures the Rust generator creates exactly the same minimal structure as Python and Node.js generators, just with different syntax.

## Timeline

- v1.4.1: Implement file conflict detection
- v1.4.2: Convert to universal templates
- v1.5.0: Full generator standardization complete