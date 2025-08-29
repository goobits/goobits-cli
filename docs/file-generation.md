# File Generation Guide

Goobits generates minimal files to keep your repository clean while providing full CLI functionality.

## Philosophy

- **Minimal files**: 2-3 files per language
- **No overwriting**: Preserves your existing files
- **Smart merging**: Updates dependencies without destroying configuration
- **User control**: You own your project structure

## What Gets Generated

### Python
```
my-cli/
├── cli.py           # Complete CLI (all utilities embedded)
├── cli_hooks.py     # Your business logic (if not exists)
└── setup.sh         # Installation script
```

### Node.js
```
my-cli/
├── cli.mjs          # ES6 module (all components embedded)
├── cli_hooks.mjs    # Your business logic (if not exists)
└── setup.sh         # npm/yarn/pnpm setup
```

### TypeScript
```
my-cli/
├── cli.ts           # TypeScript CLI
├── cli_types.d.ts   # Type definitions
├── cli_hooks.ts     # Your business logic (if not exists)
└── setup.sh         # Build and install script
```

### Rust
```
my-cli/
├── src/
│   ├── main.rs      # Rust CLI (modules inline)
│   └── cli_hooks.rs # Your business logic (if not exists)
└── setup.sh         # Cargo build script
```

## What's NOT Generated

Goobits respects your existing project structure:

- ❌ **No README.md** - Your documentation stays untouched
- ❌ **No .gitignore** - Your version control settings preserved
- ❌ **No package.json overwrite** - Dependencies merged smartly
- ❌ **No Cargo.toml overwrite** - Rust config preserved
- ❌ **No pyproject.toml overwrite** - Python config preserved
- ❌ **No test files** - You control your test structure
- ❌ **No CI/CD files** - Your pipeline stays as-is

## Smart Manifest Handling

### Python (pyproject.toml / setup.py)
- If exists: Dependencies added to existing file
- If not exists: Creates minimal pyproject.toml

### Node.js/TypeScript (package.json)
- If exists: Merges dependencies, preserves all other fields
- If not exists: Creates minimal package.json

### Rust (Cargo.toml)
- If exists: Updates dependencies section only
- If not exists: Creates complete Cargo.toml

## Controlling Output Location

### Default Behavior
Files generated in same directory as `goobits.yaml`:
```bash
goobits build  # Creates files next to goobits.yaml
```

### Custom Output
```yaml
# In goobits.yaml
cli_path: "src/my_package/cli.py"  # Specify exact location
```

Or via command line:
```bash
goobits build --output-dir ./src --output cli.py
```

## File Consolidation Benefits

### Before (v2.x) - 15+ files
```
❌ lib/config.js
❌ lib/logger.js
❌ lib/errors.js
❌ utils/helpers.js
❌ commands/command1.js
❌ commands/command2.js
... many more files
```

### After (v3.x) - 2-3 files
```
✅ cli.py         # Everything embedded
✅ setup.sh       # Smart installer
```

## Hook Files

Hook files contain your business logic and are only created if they don't exist:

```python
# cli_hooks.py - Created only if missing
def on_my_command(name: str, verbose: bool = False):
    """Your implementation here"""
    if verbose:
        print(f"Processing {name}...")
    return {"status": "success"}
```

## Backup Option

Preserve existing files with backup:
```bash
goobits build --backup  # Creates .bak files
```

## Clean Uninstall

Generated files are self-contained:
```bash
rm cli.py cli_hooks.py setup.sh  # Complete removal
```

## Examples

See working examples in:
- `examples/basic-demos/` - Simple configurations
- `examples/advanced-features/` - Complex CLIs

Each example shows the exact files that will be generated.