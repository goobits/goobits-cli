# Proposal: Minimal File Generation for Clean Repositories

**Date:** 2025-08-26  
**Status:** IMPLEMENTED ✅  
**Author:** Development Team
**Implementation Complete:** 2025-08-26

## Executive Summary

Goobits should generate the absolute minimum files needed to add a CLI to existing projects without cluttering repositories. This proposal reduces file generation from 5-29 files down to 2-3 files per language using ES6 modules and smart manifest merging.

## Implementation Status ✅

All proposed changes have been successfully implemented:

1. **Consolidated Templates Created**:
   - ✅ `python_cli_consolidated.j2` - Single file with embedded utilities
   - ✅ `nodejs_cli_consolidated.j2` - ES6 module (.mjs) with all components
   - ✅ `typescript_cli_consolidated.j2` + `typescript_types.j2` - Full TypeScript support
   - ✅ `rust_cli_consolidated.j2` - Inline modules in single file

2. **Renderer Updates Complete**:
   - ✅ All `get_output_structure()` methods updated to return minimal files
   - ✅ Python renderer fixed to handle various YAML command formats
   - ✅ No more README.md generation (critical bug fix)

3. **Testing & Documentation**:
   - ✅ Created comprehensive test suite: `test_template_consolidation.py`
   - ✅ Updated existing tests for new file structure
   - ✅ README.md updated with minimal file generation section
   - ✅ CLAUDE.md updated with consolidation details

## Problem Statement

### Current State: Repository Clutter
- **Python**: 5 files
- **Node.js**: 11 files with mixed CommonJS/ES6
- **TypeScript**: 27 files (excessive for a CLI addition)
- **Rust**: 11 files

### Critical Issues
1. **README.md Overwriting**: Destroys project documentation (FIXED)
2. **Module System Chaos**: Mixed CommonJS/ES6 prevents consolidation
3. **Excessive Files**: Users get 27 files when they just want a CLI
4. **Manifest Overwrites**: Destroying existing package.json/Cargo.toml/tsconfig.json

## Solution: Minimal, Clean, Modern

### Final File Structure

**Python (2 files):**
```
cli.py          # Complete CLI with all utilities embedded
setup.sh        # Installation and hook creation
```

**Node.js (2 files):**
```
cli.mjs         # ES6 module with embedded utilities (~1000 lines)
setup.sh        # Handles package.json merge + creates src/hooks.mjs
```

**TypeScript (3 files):**
```
cli.ts          # Complete CLI with embedded utilities and types
setup.sh        # Handles package.json/tsconfig.json merge + creates src/hooks.ts
types.d.ts      # Type definitions (kept separate for IDE support)
```

**Rust (2 files):**
```
src/main.rs     # Complete CLI with inline modules
setup.sh        # Handles Cargo.toml merge + creates src/hooks.rs
```

## Implementation Plan

### Phase 1: Module System Standardization ✅
- Convert all Node.js/TypeScript to ES6 modules only
- Use `.mjs` extension for Node.js to ensure ES6
- Remove all CommonJS (`require`, `module.exports`)

### Phase 2: File Consolidation

**Embedding Strategy:**
- Node.js: ~1000 lines total (config: 110, errors: 171, logger: 237, completion: 144)
- TypeScript: Same as Node.js + type definitions inline
- Python: Simple embedding (no zipapp/Shiv complexity)
- Rust: Inline modules within main.rs

### Phase 3: Smart Manifest Merging

**setup.sh handles all merging** (not in build command):
```bash
# In setup.sh - merge package.json if exists
if [ -f package.json ]; then
    npm pkg set "bin.mycli=./cli.mjs"
    npm pkg set "scripts.mycli=node cli.mjs"
    npm install commander chalk ora
else
    cat > package.json << EOF
    { "type": "module", "bin": {"mycli": "./cli.mjs"}, ... }
EOF
fi
```

**Key Principles:**
- Never overwrite user files from `goobits build`
- setup.sh does all merging/installation
- Use native tools (npm pkg, cargo add) for safety

### Phase 4: Update Renderers

```python
# nodejs_renderer.py - only 2 files
output = {
    "command_handler": "cli.mjs",  # ES6 module
    "setup_script": "setup.sh",
}

# typescript_renderer.py - only 3 files
output = {
    "command_handler": "cli.ts",
    "type_definitions": "types.d.ts",
    "setup_script": "setup.sh",
}

# rust_renderer.py - only 2 files  
output = {
    "command_handler": "src/main.rs",
    "setup_script": "setup.sh",
}
```

## Concrete Implementation Steps

### Step 1: Convert to ES6 Modules
```javascript
// Before (CommonJS in logger.js)
const { AsyncLocalStorage } = require('async_hooks');
module.exports = { setupLogging, getLogger };

// After (ES6 in cli.mjs)
import { AsyncLocalStorage } from 'async_hooks';
export { setupLogging, getLogger };
```

### Step 2: Embed Templates
```javascript
// cli.mjs - single file with everything
#!/usr/bin/env node
import { Command } from 'commander';

// ===== Embedded Config Manager =====
class ConfigManager { /* 110 lines */ }

// ===== Embedded Error Handler =====  
class ErrorHandler { /* 171 lines */ }

// ===== Embedded Logger =====
class Logger { /* 237 lines */ }

// ===== Main CLI Logic =====
const program = new Command();
// ... rest of CLI
```

### Step 3: Smart setup.sh
```bash
#!/bin/bash
# Detect existing package.json and merge intelligently
if [ -f package.json ]; then
    echo "📦 Updating existing package.json..."
    npm pkg set "bin.${CLI_NAME}=./cli.mjs"
    npm install commander@^12.0.0 chalk@^5.3.0
else
    echo "📦 Creating new package.json..."
    cat > package.json << 'EOF'
{
  "type": "module",
  "bin": { "${CLI_NAME}": "./cli.mjs" },
  "dependencies": {
    "commander": "^12.0.0",
    "chalk": "^5.3.0"
  }
}
EOF
fi

# Create hooks file if missing
if [ ! -f src/hooks.mjs ]; then
    mkdir -p src
    cat > src/hooks.mjs << 'EOF'
export async function onBuild(args) {
    console.log('Build command:', args);
}
EOF
fi
```

## Error Handling

### Manifest Corruption
```bash
# In setup.sh - validate JSON before modifying
if ! npm pkg get name > /dev/null 2>&1; then
    echo "⚠️  package.json appears corrupted, creating backup..."
    cp package.json package.json.backup
    # Attempt repair or guide user
fi
```

### Missing Dependencies
```bash
# Check for npm/cargo/pip before running
command -v npm >/dev/null 2>&1 || { 
    echo "❌ npm not found. Please install Node.js"; 
    exit 1; 
}
```

## Benefits

1. **93% File Reduction**: TypeScript from 27→3 files
2. **Zero Overwrites**: setup.sh handles everything safely  
3. **Clean Repos**: Users see only essential files
4. **Modern Code**: ES6 modules throughout
5. **Safe Merging**: Native tools (npm pkg, cargo add)

## Success Criteria

- ✅ Maximum 3 files per language
- ✅ No destructive file operations
- ✅ ES6 modules only (Node.js/TypeScript)
- ✅ setup.sh handles all merging
- ✅ Tests pass with consolidated output

## Implementation Order

1. **Day 1**: Convert Node.js templates to ES6 + .mjs
2. **Day 2**: Update nodejs_renderer.py to output 2 files
3. **Day 3**: Update TypeScript renderer for 3 files
4. **Day 4**: Fix Python consolidation (remove Shiv)
5. **Day 5**: Update all tests for new structure

---

**Decision**: This is not backward compatible by design. Clean repos are the priority.