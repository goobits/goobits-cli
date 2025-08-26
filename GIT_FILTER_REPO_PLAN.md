# Git Filter-Repo Cleanup Plan

## ⚠️ WARNING: THIS WILL REWRITE GIT HISTORY
**BACKUP YOUR REPOSITORY BEFORE PROCEEDING**

## Analysis Summary
- **Repository**: 230 commits
- **Bloat**: ~15,000+ files that shouldn't be tracked
- **Size Impact**: ~200MB+ of unnecessary data
- **First contamination**: Early in project history (commit 1a3dd50)

## Pre-Cleanup Checklist

### 1. Create Full Backup
```bash
# Create a complete backup
cd ..
cp -r workspace workspace-backup-$(date +%Y%m%d-%H%M%S)

# Or create a git bundle
cd workspace
git bundle create ../workspace-backup-$(date +%Y%m%d-%H%M%S).bundle --all
```

### 2. Ensure Clean Working Directory
```bash
git status  # Should show nothing uncommitted
git stash   # If needed
```

### 3. Push Current State to Remote
```bash
git push origin --all
git push origin --tags
```

## Removal Categories (Sorted by Confidence)

### 🔴 Category 1: Virtual Environments (100% Confident - MUST REMOVE)
**15,000+ files, ~150MB+**

These should NEVER be in version control:
- `test_env/` - Python virtual environment (2,566 files)
- `venv/` - Python virtual environment (7,165 files)  
- `test_venv/` - Another Python virtual environment

### 🔴 Category 2: Python Build Artifacts (100% Confident - MUST REMOVE)
**5,000+ files**

Generated files that change on every build:
- All `*.pyc` files - Compiled Python bytecode
- All `__pycache__/` directories - Python cache directories
- All `*.egg-info/` directories - Python package metadata:
  - `src/goobits_cli.egg-info/`
  - `src/complexcli.egg-info/`
  - `src/nodejs_test_cli.egg-info/`
  - `src/test_cli.egg-info/`

### 🔴 Category 3: Build Output Directories (99% Confident - MUST REMOVE)
**1,000+ files**

Compilation and build outputs:
- All `target/` directories - Rust build artifacts
- All `dist/` directories - Distribution builds
- All `build/` directories - Build outputs
- `.pytest_cache/` - Pytest cache
- `.mypy_cache/` - MyPy type checking cache
- `.ruff_cache/` - Ruff linter cache
- `htmlcov/` - Coverage HTML reports
- `.coverage` files - Coverage data

### 🟠 Category 4: Test Output Artifacts (95% Confident - SHOULD REMOVE)
**500+ files**

Generated test outputs (not test source):
- `test-py-legacy/` - Legacy test output
- `test_frameworks/target/` - Test framework build artifacts
- `test_results/` - Test result outputs
- `test_universal_hooks/` - Generated test hooks
- `test_universal_nodejs_output/` - Generated Node.js tests
- `test_universal_python_output/` - Generated Python tests
- `test_universal_typescript_output/` - Generated TypeScript tests

### 🟠 Category 5: Generated Test CLIs in Wrong Location (95% Confident)
**~50 files**

Test CLIs that shouldn't be in src/:
- `src/complexcli/` - Test CLI (keep .egg-info removal separate)
- `src/nodejs_test_cli/` - Test CLI
- `src/test_cli/` - Test CLI
- `src/testcli/` - Test CLI

### 🟡 Category 6: Generated JavaScript in Examples (90% Confident)
**~20 files**

Compiled JS from TypeScript (keep TS sources):
- `examples/*.js` - Generated JavaScript files
- `examples/*.cjs` - CommonJS files
- `examples/*.mjs` - ES Module files
BUT KEEP: `examples/*.ts` - TypeScript source files

### 🟡 Category 7: Dependency Lock Files (80% Confident - DISCUSS)
**2-3 files**

Debatable for libraries/frameworks:
- `Cargo.lock` - Root Rust lock file
- `test_frameworks/Cargo.lock` - Test framework lock
- `package-lock.json` - Node.js lock files (if any)

### 🟢 Category 8: Node Dependencies (90% Confident)
**If present**

- All `node_modules/` directories - Node.js dependencies

## Git Filter-Repo Commands

### Step 1: Remove Virtual Environments (CRITICAL)
```bash
git filter-repo --path test_env/ --invert-paths --force
git filter-repo --path venv/ --invert-paths --force
git filter-repo --path test_venv/ --invert-paths --force
```

### Step 2: Remove Python Build Artifacts
```bash
# Remove all .pyc files
git filter-repo --path-glob '*.pyc' --invert-paths --force

# Remove all __pycache__ directories
git filter-repo --path-glob '*/__pycache__/*' --invert-paths --force
git filter-repo --path __pycache__/ --invert-paths --force

# Remove all .egg-info directories
git filter-repo --path-glob '*.egg-info/*' --invert-paths --force
```

### Step 3: Remove Build/Cache Directories
```bash
# Rust target directories
git filter-repo --path-glob '*/target/*' --invert-paths --force

# Python caches
git filter-repo --path .pytest_cache/ --invert-paths --force
git filter-repo --path .mypy_cache/ --invert-paths --force
git filter-repo --path .ruff_cache/ --invert-paths --force
git filter-repo --path htmlcov/ --invert-paths --force
git filter-repo --path-glob '.coverage*' --invert-paths --force

# Build directories
git filter-repo --path dist/ --invert-paths --force
git filter-repo --path build/ --invert-paths --force
```

### Step 4: Remove Test Outputs
```bash
git filter-repo --path test-py-legacy/ --invert-paths --force
git filter-repo --path test_frameworks/target/ --invert-paths --force
git filter-repo --path test_results/ --invert-paths --force
git filter-repo --path test_universal_hooks/ --invert-paths --force
git filter-repo --path test_universal_nodejs_output/ --invert-paths --force
git filter-repo --path test_universal_python_output/ --invert-paths --force
git filter-repo --path test_universal_typescript_output/ --invert-paths --force
```

### Step 5: Remove Test CLIs from src/
```bash
git filter-repo --path src/complexcli/ --invert-paths --force
git filter-repo --path src/nodejs_test_cli/ --invert-paths --force
git filter-repo --path src/test_cli/ --invert-paths --force
git filter-repo --path src/testcli/ --invert-paths --force
```

### Step 6: Remove Generated JavaScript from Examples
```bash
# This is more complex - need to keep .ts files
git filter-repo --path-glob 'examples/*.js' --invert-paths --force
git filter-repo --path-glob 'examples/*.cjs' --invert-paths --force
git filter-repo --path-glob 'examples/*.mjs' --invert-paths --force
```

### Step 7: Remove Lock Files (OPTIONAL - DISCUSS FIRST)
```bash
git filter-repo --path Cargo.lock --invert-paths --force
git filter-repo --path test_frameworks/Cargo.lock --invert-paths --force
```

### Step 8: Remove Node Dependencies
```bash
git filter-repo --path-glob '*/node_modules/*' --invert-paths --force
```

## Alternative: Single Combined Command

For efficiency, you can create a patterns file:

### Create patterns file: `.git-filter-patterns`
```
# Virtual environments
test_env/
venv/
test_venv/

# Python artifacts
glob:*.pyc
glob:*/__pycache__/*
__pycache__/
glob:*.egg-info/*

# Build directories
glob:*/target/*
dist/
build/
.pytest_cache/
.mypy_cache/
.ruff_cache/
htmlcov/
glob:.coverage*

# Test outputs
test-py-legacy/
test_results/
test_universal_hooks/
test_universal_nodejs_output/
test_universal_python_output/
test_universal_typescript_output/

# Test CLIs in wrong location
src/complexcli/
src/nodejs_test_cli/
src/test_cli/
src/testcli/

# Generated JS
glob:examples/*.js
glob:examples/*.cjs
glob:examples/*.mjs

# Node modules
glob:*/node_modules/*

# Lock files (optional)
Cargo.lock
glob:*/Cargo.lock
```

### Run single command:
```bash
git filter-repo --paths-from-file .git-filter-patterns --invert-paths --force
```

## Post-Cleanup Steps

### 1. Verify Repository
```bash
# Check size reduction
du -sh .git/

# Verify files are gone
git ls-files | grep -E "venv/|\.pyc|__pycache__|\.egg-info" | wc -l
# Should return 0

# Check history is clean
git log --all --name-only | grep -E "\.pyc|__pycache__|venv/" | wc -l
# Should return 0
```

### 2. Update .gitignore
Ensure the comprehensive .gitignore is in place to prevent re-adding these files.

### 3. Force Push to Remote
⚠️ **WARNING: This rewrites history for all collaborators**
```bash
git push origin --force --all
git push origin --force --tags
```

### 4. Notify Team
All team members must:
```bash
# Backup their local changes
git stash

# Delete and re-clone
cd ..
rm -rf workspace
git clone [repository-url] workspace
```

Or if they have local changes to preserve:
```bash
git fetch origin
git reset --hard origin/main  # or current branch
```

## Estimated Impact

### Before Cleanup:
- Repository size: ~350MB+
- File count: ~15,000+ unnecessary files
- Clone time: Slow
- History: Polluted with binary/generated files

### After Cleanup:
- Repository size: ~50-100MB (estimated)
- File count: Only source files
- Clone time: Fast
- History: Clean, meaningful commits only

## Risks and Mitigations

### Risks:
1. **History Rewrite** - All commit SHAs will change
2. **Force Push Required** - Disrupts all forks/clones
3. **Lost Work** - Uncommitted changes could be lost
4. **CI/CD Breakage** - May reference old commit SHAs

### Mitigations:
1. **Full Backup** - Created before starting
2. **Team Notification** - Coordinate timing
3. **Clean Working Directory** - Verified before starting
4. **Update CI/CD** - Update any hardcoded commit references

## Decision Points

### Must Decide:
1. **Lock Files** - Keep or remove Cargo.lock?
2. **Timing** - When to perform cleanup (coordinate with team)?
3. **Backup Strategy** - Where to store backup?
4. **Communication** - How to notify all contributors?

## Recommended Approach

1. **Start Conservative** - Remove only Category 1-3 first (100% confident)
2. **Test Locally** - Run on a copy first
3. **Gradual Cleanup** - Can run multiple passes if needed
4. **Document Everything** - Keep record of what was removed and why

---

## DO NOT RUN YET - REVIEW AND APPROVE FIRST

This plan requires careful review and team coordination before execution.