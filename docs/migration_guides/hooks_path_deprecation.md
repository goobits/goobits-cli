# hooks_path Deprecation Migration Guide

## Overview

The `hooks_path` field is deprecated and will be removed in **v4.0.0** (planned for Q2 2025). Please migrate to `cli_hooks` for future compatibility.

## Migration Steps

### 1. Update Your Configuration File

**Before (deprecated):**
```yaml
# goobits.yaml
package_name: my-cli
command_name: mycli
hooks_path: "src/my_hooks.py"  # ⚠️ Deprecated

cli:
  name: mycli
  version: "3.0.0-alpha.1"
  # ... rest of config
```

**After (recommended):**
```yaml
# goobits.yaml
package_name: my-cli
command_name: mycli
cli_hooks: "src/my_hooks.py"  # ✅ Recommended

cli:
  name: mycli
  version: "3.0.0-alpha.1"
  # ... rest of config
```

### 2. Verify Migration

Run `goobits build` to ensure no deprecation warnings appear:

```bash
# Should show no warnings after migration
goobits build goobits.yaml
```

## Timeline

| Version | Status |
|---------|--------|
| v3.0.0+ | `hooks_path` deprecated, warning shown |
| v3.x.x  | Both `hooks_path` and `cli_hooks` supported |
| v4.0.0  | `hooks_path` removed, only `cli_hooks` supported |

## Backward Compatibility

During the transition period (v3.x.x):
- Both `hooks_path` and `cli_hooks` are supported
- `cli_hooks` takes precedence if both are specified
- Warning only shown if `hooks_path` is used without `cli_hooks`

## Language Support

This migration applies to all supported languages:
- **Python**: Hook files (`.py`)
- **Node.js**: Hook files (`.js`)
- **TypeScript**: Hook files (`.ts`)
- **Rust**: Hook files (`.rs`)

## Need Help?

If you encounter issues during migration:
1. Check that your hook file path is correct
2. Ensure the hook file exists at the specified location
3. Verify your configuration syntax with `goobits validate`

## Example Migration

For a complete example, see the [advanced-features demo](../../examples/advanced-features/) which uses the modern `cli_hooks` field.