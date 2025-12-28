# Hook Contract

**Status**: FROZEN (do not modify without migration plan)
**Version**: 1.0.0
**Created**: Phase 0 of Universal-First Refactor

---

## Overview

Hooks are user-defined functions that implement CLI command business logic. The generated CLI code discovers and invokes these hooks at runtime, providing a clean separation between generated infrastructure and user code.

```
User runs: mycli status --verbose
Generated CLI: Parses args → Finds on_status hook → Calls hook with kwargs
User hook: def on_status(command_name, verbose, **kwargs): ...
```

---

## Hook Naming Convention

### Pattern

```
on_{command_name}
```

Where `{command_name}` is the command name with:
- Hyphens (`-`) replaced with underscores (`_`)
- All lowercase

### Examples

| Command | Hook Name |
|---------|-----------|
| `status` | `on_status` |
| `list-models` | `on_list_models` |
| `config get` | `on_config_get` |
| `tools enable` | `on_tools_enable` |

### Subcommand Hooks

For nested subcommands, the hook name is flattened with underscores:

```
Command: mycli config get
Hook: on_config_get

Command: mycli tools list
Hook: on_tools_list
```

---

## Hook Signature

### Required Parameters

```python
def on_command_name(
    command_name: str,  # The command being executed (e.g., "status")
    **kwargs,           # All other parameters
) -> Optional[Any]:
    """
    Hook implementation for the command.

    Args:
        command_name: Name of the command being executed
        **kwargs: All command options and arguments

    Returns:
        Optional return value (usually None, but may return data for testing)
    """
    pass
```

### kwargs Contents

The `**kwargs` dict contains:

1. **All command options** by name (snake_case):
   ```python
   # CLI: mycli status --verbose --format json
   kwargs = {
       "verbose": True,
       "format": "json",
   }
   ```

2. **All command arguments** by name:
   ```python
   # CLI: mycli process file.txt
   kwargs = {
       "file": "file.txt",
   }
   ```

3. **Debug flag** (if enabled globally):
   ```python
   kwargs = {
       "debug": True,  # From --debug global option
   }
   ```

4. **Context object** (optional, for advanced use):
   ```python
   kwargs = {
       "ctx": click.Context,  # Click context object
   }
   ```

---

## Hook Discovery

The generated CLI discovers hooks using a three-tier fallback mechanism:

### Tier 1: Module Import

```python
# Try importing as a Python module
module_path = "src/my_cli/app_hooks".replace("/", ".")
app_hooks = importlib.import_module(module_path)
```

### Tier 2: Relative Import

```python
# Try relative import from CLI package
from . import app_hooks
```

### Tier 3: File-Based Import

```python
# Try loading from file path
hooks_file = Path(__file__).parent / "app_hooks.py"
spec = importlib.util.spec_from_file_location("app_hooks", hooks_file)
app_hooks = importlib.util.module_from_spec(spec)
spec.loader.exec_module(app_hooks)
```

### Fallback Behavior

If no hooks module is found, the CLI:
1. Logs a debug message (if debug enabled)
2. Uses default placeholder behavior
3. Does NOT raise an error (graceful degradation)

---

## Hook Invocation

### Python Generated Code Pattern

```python
def invoke_hook(hook_name: str, **kwargs) -> Any:
    """Invoke a hook function if it exists."""
    if app_hooks and hasattr(app_hooks, hook_name):
        hook_func = getattr(app_hooks, hook_name)
        return hook_func(**kwargs)
    else:
        # Default behavior: print message or no-op
        click.echo(f"Command '{kwargs.get('command_name')}' executed (no hook)")
        return None

# In command handler:
@main.command()
@click.option("--verbose", is_flag=True)
def status(verbose):
    return invoke_hook(
        "on_status",
        command_name="status",
        verbose=verbose,
    )
```

### Node.js Generated Code Pattern

```javascript
async function invokeHook(hookName, kwargs) {
    if (appHooks && typeof appHooks[hookName] === 'function') {
        return await appHooks[hookName](kwargs);
    }
    console.log(`Command '${kwargs.commandName}' executed (no hook)`);
    return null;
}

// In command handler:
program
    .command('status')
    .option('--verbose', 'Enable verbose output')
    .action(async (options) => {
        await invokeHook('on_status', {
            commandName: 'status',
            verbose: options.verbose,
        });
    });
```

### TypeScript Generated Code Pattern

```typescript
async function invokeHook(hookName: string, kwargs: Record<string, any>): Promise<any> {
    if (appHooks && typeof (appHooks as any)[hookName] === 'function') {
        return await (appHooks as any)[hookName](kwargs);
    }
    console.log(`Command '${kwargs.commandName}' executed (no hook)`);
    return null;
}
```

### Rust Generated Code Pattern

```rust
fn invoke_hook(hook_name: &str, matches: &ArgMatches) -> Result<()> {
    match hook_name {
        "on_status" => hooks::on_status(matches),
        _ => {
            println!("Command executed (no hook)");
            Ok(())
        }
    }
}
```

---

## Error Handling

### Hook Errors

Hooks are responsible for their own error handling. The generated CLI:

1. **Does NOT catch hook exceptions** (they propagate to user)
2. **Does NOT retry on failure**
3. **Does NOT provide fallback behavior on error**

### Recommended Pattern

```python
def on_status(command_name: str, **kwargs) -> None:
    try:
        # Business logic here
        result = do_something()
        click.echo(f"Status: {result}")
    except MyAppError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)
    except Exception as e:
        click.echo(f"Unexpected error: {e}", err=True)
        raise
```

---

## Hook File Structure

### Recommended Layout (Python)

```python
# app_hooks.py

"""Business logic hooks for the CLI."""

from typing import Optional

def on_status(command_name: str, verbose: bool = False, **kwargs) -> None:
    """Handle the status command."""
    if verbose:
        print("Verbose mode enabled")
    print("Status: OK")

def on_config_get(command_name: str, key: str, **kwargs) -> Optional[str]:
    """Handle the config get command."""
    config = load_config()
    return config.get(key)

def on_config_set(command_name: str, key: str, value: str, **kwargs) -> None:
    """Handle the config set command."""
    config = load_config()
    config[key] = value
    save_config(config)
```

### Recommended Layout (Node.js)

```javascript
// cli_hooks.mjs

export async function on_status({ commandName, verbose }) {
    if (verbose) {
        console.log('Verbose mode enabled');
    }
    console.log('Status: OK');
}

export async function on_config_get({ commandName, key }) {
    const config = await loadConfig();
    return config[key];
}
```

---

## Re-Export Pattern

For larger projects, hooks can be organized into submodules and re-exported:

```python
# app_hooks.py (facade)

"""Re-export all hooks from submodules."""

from .hooks.core import on_status, on_info
from .hooks.config import on_config_get, on_config_set, on_config_list
from .hooks.tools import on_tools_enable, on_tools_disable

__all__ = [
    "on_status",
    "on_info",
    "on_config_get",
    "on_config_set",
    "on_config_list",
    "on_tools_enable",
    "on_tools_disable",
]
```

```
hooks/
├── __init__.py
├── core.py      # on_status, on_info
├── config.py    # on_config_*
└── tools.py     # on_tools_*
```

---

## Async Hooks

### Python

Async hooks are supported when the CLI uses asyncio:

```python
import asyncio

async def on_status(command_name: str, **kwargs) -> None:
    """Async hook implementation."""
    result = await fetch_status()
    print(f"Status: {result}")

# CLI invocation wraps in asyncio.run()
def status_command(**kwargs):
    asyncio.run(invoke_async_hook("on_status", **kwargs))
```

### Node.js / TypeScript

All hooks are async by default:

```javascript
export async function on_status({ commandName }) {
    const result = await fetchStatus();
    console.log(`Status: ${result}`);
}
```

---

## Testing Hooks

### Unit Testing Pattern

```python
# test_hooks.py

import pytest
from my_cli.app_hooks import on_status

def test_on_status_verbose():
    """Test status command with verbose flag."""
    result = on_status(
        command_name="status",
        verbose=True,
        debug=False,
    )
    assert result is None  # or check side effects

def test_on_status_returns_data():
    """Test status command returns expected data."""
    result = on_status(command_name="status")
    assert result == expected_status
```

### Integration Testing Pattern

```python
# test_cli_integration.py

from click.testing import CliRunner
from my_cli.cli import main

def test_status_command():
    runner = CliRunner()
    result = runner.invoke(main, ["status", "--verbose"])
    assert result.exit_code == 0
    assert "Status:" in result.output
```

---

## Migration Notes

- **v1.0.0**: Initial frozen contract
- Hook naming convention is guaranteed stable
- Parameter passing via `**kwargs` is guaranteed stable
- Breaking changes require version bump and migration guide
