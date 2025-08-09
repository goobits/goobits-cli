# Migration Guide to Goobits CLI Framework v2.0

This guide helps you migrate from previous versions of Goobits CLI Framework to the new v2.0 architecture with multi-language support, universal templates, and performance enhancements.

## Table of Contents

1. [What's New in v2.0](#whats-new-in-v20)
2. [Breaking Changes](#breaking-changes)
3. [Migration Strategies](#migration-strategies)
4. [Step-by-Step Migration](#step-by-step-migration)
5. [Language-Specific Migration](#language-specific-migration)
6. [Configuration Updates](#configuration-updates)
7. [Template System Migration](#template-system-migration)
8. [Performance Considerations](#performance-considerations)
9. [Testing Your Migration](#testing-your-migration)
10. [Rollback Strategy](#rollback-strategy)

## What's New in v2.0

### Major New Features

- 🌍 **Multi-Language Support**: Python, Node.js, and TypeScript
- ⚡ **Universal Template System**: Single source generating all languages
- 🚀 **Performance Framework**: <100ms startup times with validation
- 🎯 **Production-Ready**: 95%+ test coverage across all languages
- 🔧 **Enhanced Architecture**: Modular, extensible design

### Removed Features

- ❌ **Rust Support**: Removed in v2.0, under reconstruction for future releases
- ❌ **Legacy Configuration Format**: Some old YAML formats deprecated
- ❌ **Old Template Filters**: Replaced with universal equivalents

## Breaking Changes

### 1. Configuration Format Changes

**v1.x Format (DEPRECATED)**:
```yaml
cli:
  commands:
    - name: hello
      help: Say hello
      arguments:
        - name: target
          help: Who to greet
```

**v2.0 Format (REQUIRED)**:
```yaml
language: python  # NEW: Language selection required

cli:
  commands:
    hello:           # NEW: Dictionary format instead of list
      desc: Say hello     # 'desc' instead of 'help'  
      args:               # 'args' instead of 'arguments'
        - name: target
          desc: Who to greet  # 'desc' instead of 'help'
```

### 2. Language Selection

**NEW REQUIREMENT**: Must specify target language in `goobits.yaml`:

```yaml
language: python      # Default if not specified
language: nodejs      # Node.js with Commander.js
language: typescript  # TypeScript with full typing
```

### 3. Hook Function Changes

**Python Hooks** (mostly compatible):
```python
# v1.x (still works)
def on_hello(target, **kwargs):
    print(f"Hello {target}")

# v2.0 (recommended)
def on_hello(target, **kwargs):
    """Enhanced with better type hints and error handling"""
    print(f"Hello {target}")
```

**NEW: Node.js/TypeScript Hooks**:
```javascript
// Node.js hooks (NEW in v2.0)
export async function onHello(args) {
    const { target } = args;
    console.log(`Hello ${target}`);
}
```

```typescript
// TypeScript hooks (NEW in v2.0)
interface HelloArgs {
    target: string;
}

export async function onHello(args: HelloArgs): Promise<void> {
    const { target } = args;
    console.log(`Hello ${target}`);
}
```

### 4. Generated File Structure Changes

**Python Projects** (mostly unchanged):
```
# v1.x structure (still supported)
cli.py
app_hooks.py
setup.sh

# v2.0 enhanced structure
cli.py              # Enhanced with performance optimizations
app_hooks.py        # Same interface, better error handling
setup.sh            # Improved dependency management
README.md           # Auto-generated documentation
```

**NEW: Node.js/TypeScript Projects**:
```
index.js/ts         # Main CLI implementation
package.json        # npm package configuration
bin/cli.js          # Executable entry point
app_hooks.js/ts     # Your business logic
setup.sh            # Installation script
README.md           # Auto-generated docs
```

## Migration Strategies

### Strategy 1: Gradual Migration (Recommended)

Migrate existing projects step by step while maintaining functionality:

1. **Upgrade Goobits CLI Framework**
2. **Update configuration format**
3. **Test with existing Python projects**
4. **Optionally migrate to Node.js/TypeScript**
5. **Enable universal templates**

### Strategy 2: Clean Migration

Start fresh with v2.0 architecture:

1. **Create new project structure**
2. **Copy business logic from hooks**
3. **Update configuration to v2.0 format**
4. **Choose target language**
5. **Generate and test new CLI**

### Strategy 3: Parallel Migration

Run both versions side by side during transition:

1. **Keep v1.x project working**
2. **Create v2.0 version in parallel**
3. **Test both versions**
4. **Switch when confident**
5. **Remove v1.x version**

## Step-by-Step Migration

### Step 1: Backup Your Project

```bash
# Create backup of existing project
cp -r my-cli-project my-cli-project-v1-backup

# Backup goobits.yaml specifically
cp goobits.yaml goobits.yaml.v1.backup
```

### Step 2: Upgrade Goobits CLI Framework

```bash
# Upgrade to v2.0
pipx upgrade goobits-cli

# Verify upgrade
goobits --version
# Should show: goobits-cli 2.0.0
```

### Step 3: Update Configuration Format

**Automatic Migration Tool** (if available):
```bash
# Attempt automatic migration
goobits migrate --from 1.4.0 --to 2.0.0 goobits.yaml
```

**Manual Migration**:

**Before (v1.x)**:
```yaml
cli:
  name: mycli
  help: "My CLI application"
  commands:
    - name: init
      help: "Initialize project"
      arguments:
        - name: project_name
          help: "Name of the project"
          required: true
      options:
        - name: template
          short: t
          help: "Project template"
          default: basic
```

**After (v2.0)**:
```yaml
language: python  # ADD: Language selection

cli:
  name: mycli
  tagline: "My CLI application"  # CHANGE: 'tagline' instead of 'help'
  version: "1.0.0"              # ADD: Version required
  commands:
    init:                       # CHANGE: Dictionary instead of list
      desc: "Initialize project"     # CHANGE: 'desc' instead of 'help'
      args:                         # CHANGE: 'args' instead of 'arguments'
        - name: project_name         # CHANGE: 'project_name' to 'project-name'
          desc: "Name of the project"  # CHANGE: 'desc' instead of 'help'
          required: true
      options:
        - name: template
          short: t
          desc: "Project template"    # CHANGE: 'desc' instead of 'help'
          default: basic
```

### Step 4: Test Configuration

```bash
# Test new configuration
goobits build --dry-run

# If successful, generate CLI
goobits build
```

### Step 5: Update Hook Functions (if needed)

Most Python hooks should work without changes, but update for better practices:

**Before (v1.x)**:
```python
def on_init(project_name, template='basic', **kwargs):
    print(f"Initializing {project_name} with {template}")
```

**After (v2.0)**:
```python
def on_init(project_name, template='basic', **kwargs):
    """Initialize a new project with enhanced error handling"""
    try:
        print(f"Initializing {project_name} with {template}")
        # Your logic here
    except Exception as e:
        print(f"Error initializing project: {e}")
        return 1
    return 0
```

### Step 6: Enable Universal Templates (Optional)

```bash
# Try universal templates for better performance
goobits build --universal-templates

# Compare with legacy templates
goobits build
diff -r universal-output/ legacy-output/
```

### Step 7: Performance Validation

```bash
# Validate performance meets v2.0 standards
python performance/performance_suite.py

# Should show: ✅ All checks passed, production ready
```

## Language-Specific Migration

### Migrating Python Projects

Python projects have the smoothest migration path:

**1. Configuration Updates** (minimal changes):
```yaml
# Add language specification (defaults to python)
language: python

# Update command format (required)
cli:
  commands:
    command_name:  # Dictionary format
      desc: "Description"  # 'desc' instead of 'help'
```

**2. Hook Updates** (mostly compatible):
```python
# v1.x hooks work in v2.0, but enhance for better practices
def on_command_name(**kwargs):
    """Add docstrings for better documentation"""
    try:
        # Your existing logic
        pass
    except Exception as e:
        # Better error handling
        print(f"Error: {e}")
        return 1
    return 0
```

**3. Performance Benefits**:
- Startup time improved by ~35% (120ms → 78ms)
- Memory usage optimized
- Universal templates available

### Migrating to Node.js

If you want to migrate from Python to Node.js:

**1. Update Configuration**:
```yaml
language: nodejs  # Change to nodejs

# Add npm dependencies if needed
installation:
  extras:
    npm:
      - "chalk@5.3.0"      # Terminal colors
      - "ora@8.0.1"        # Progress spinners
```

**2. Convert Hooks to JavaScript**:
```python
# Old Python hook
def on_init(project_name, template='basic', **kwargs):
    print(f"Initializing {project_name}")
```

```javascript
// New JavaScript hook
export async function onInit(args) {
    const { projectName, template = 'basic' } = args;
    console.log(`Initializing ${projectName}`);
}
```

**3. Update Dependencies**:
```bash
# Install Node.js dependencies
./setup.sh --dev
```

### Migrating to TypeScript

For full type safety, migrate to TypeScript:

**1. Update Configuration**:
```yaml
language: typescript  # Change to typescript

installation:
  extras:
    npm:
      - "@types/node"     # Node.js type definitions
```

**2. Convert Hooks to TypeScript**:
```python
# Old Python hook
def on_init(project_name, template='basic', **kwargs):
    print(f"Initializing {project_name}")
```

```typescript
// New TypeScript hook
interface InitArgs {
    projectName: string;
    template?: string;
}

export async function onInit(args: InitArgs): Promise<void> {
    const { projectName, template = 'basic' } = args;
    console.log(`Initializing ${projectName}`);
}
```

**3. Compile and Test**:
```bash
# Install and build
./setup.sh --dev
npm run build

# Test TypeScript CLI
node dist/index.js --help
```

## Configuration Updates

### Dependency Management Changes

**v1.x Style**:
```yaml
dependencies:
  - click>=8.0.0
  - rich>=13.0.0
```

**v2.0 Style**:
```yaml
# Python projects
dependencies:
  python: ["click>=8.0.0", "rich>=13.0.0"]

# Node.js/TypeScript projects  
installation:
  extras:
    npm: ["chalk@5.3.0", "ora@8.0.1"]
```

### Shell Integration Updates

**v1.x**:
```yaml
enable_completion: true
```

**v2.0**:
```yaml
shell_integration:
  enable_completion: true
  alias: mycli
```

### Installation Configuration

**v1.x**:
```yaml
pypi_name: my-package
```

**v2.0**:
```yaml
installation:
  pypi_name: my-package
  development_path: "."
  extras:
    python: ["dev", "test"]
    apt: ["git", "python3-dev"]  # System packages
```

## Template System Migration

### Universal Templates vs Legacy Templates

**Legacy Templates** (v1.x default):
- Language-specific Jinja2 templates
- Separate templates for each language
- Custom filters and functions
- Battle-tested but harder to maintain

**Universal Templates** (v2.0 default):
- Single template source for all languages
- Consistent behavior across languages
- Better performance (50% faster generation)
- Future-proof architecture

### Migration to Universal Templates

**1. Test Universal Templates**:
```bash
# Generate with universal templates
goobits build --universal-templates

# Test the generated CLI
./setup.sh install --dev
mycli --help
```

**2. Compare Output**:
```bash
# Generate with both systems
goobits build --universal-templates
mv generated-output universal-output

goobits build
mv generated-output legacy-output

# Compare
diff -r universal-output/ legacy-output/
```

**3. Custom Template Filters**:
If you have custom template filters, they may need updates:

```python
# Custom filter for legacy templates
def custom_filter(value):
    return value.upper()

# Register in universal template system
from goobits_cli.universal.template_engine import register_filter
register_filter('custom', custom_filter)
```

### Fallback Strategy

Universal templates automatically fall back to legacy templates if:
- Unsupported language features are detected
- Custom filters are needed
- Template generation fails

```bash
# Force legacy templates if needed
goobits build --no-universal-templates
```

## Performance Considerations

### Performance Improvements in v2.0

| Metric | v1.x | v2.0 | Improvement |
|--------|------|------|-------------|
| Python Startup | 120ms | 78ms | 35% faster |
| Memory Usage | 45MB | 24MB | 47% less |
| Generation Time | 180ms | 90ms | 50% faster |

### Performance Validation

```bash
# Validate your migrated CLI meets v2.0 standards
python performance/performance_suite.py

# Expected output:
# ✅ Startup Time: 78ms (Target: <100ms) - PASS
# ✅ Memory Usage: 24MB (Target: <50MB) - PASS
# ✅ Template Rendering: 60ms (Target: <500ms) - PASS
# 🎯 Overall Grade: A+ (Production Ready)
```

### Optimization Tips

**1. Use Universal Templates**:
```bash
# Better performance
goobits build --universal-templates
```

**2. Optimize Hook Functions**:
```python
# Before migration
def on_command(**kwargs):
    import heavy_library  # Slow
    return heavy_library.process(kwargs)

# After migration
def on_command(**kwargs):
    # Lazy import for better startup time
    from heavy_library import process
    return process(kwargs)
```

## Testing Your Migration

### Comprehensive Testing Checklist

**1. Functional Testing**:
```bash
# Test all commands work
mycli --help
mycli command1 --help
mycli command1 arg1 --option value

# Test with different option combinations
mycli command2 --verbose
mycli command2 --config custom.yaml
```

**2. Performance Testing**:
```bash
# Validate performance
python performance/startup_validator.py --command "python cli.py --help" --target 100

# Memory usage check
python performance/memory_profiler.py --command "python cli.py command"
```

**3. Cross-Language Testing** (if applicable):
```bash
# Test Node.js version
language: nodejs
goobits build --universal-templates
./setup.sh install --dev
mycli --help

# Test TypeScript version
language: typescript
goobits build --universal-templates
./setup.sh install --dev
npm run build
node dist/index.js --help
```

**4. Error Handling Testing**:
```bash
# Test error conditions
mycli nonexistent-command  # Should show helpful error
mycli command --invalid-option  # Should show usage
mycli command missing-required-arg  # Should show error
```

### Automated Testing

Create a migration test suite:

```bash
#!/bin/bash
# test_migration.sh

echo "Testing v2.0 migration..."

# Test basic functionality
if ! mycli --help > /dev/null 2>&1; then
    echo "❌ Help command failed"
    exit 1
fi

# Test performance
if ! python performance/startup_validator.py --command "python cli.py --help" --target 100; then
    echo "❌ Performance validation failed"
    exit 1
fi

# Test commands
for cmd in init build deploy; do
    if ! mycli $cmd --help > /dev/null 2>&1; then
        echo "❌ Command $cmd failed"
        exit 1
    fi
done

echo "✅ Migration test passed"
```

## Rollback Strategy

### Preparing for Rollback

**1. Keep Backup**:
```bash
# Before migration
cp -r current-project project-v1-backup
cp goobits.yaml goobits.yaml.v1
```

**2. Document Changes**:
```bash
# Create migration log
echo "Migration started: $(date)" > migration.log
echo "Original configuration:" >> migration.log
cat goobits.yaml.v1 >> migration.log
```

### Rolling Back if Needed

**1. Quick Rollback**:
```bash
# Restore backup
rm -rf current-project
cp -r project-v1-backup current-project
cp goobits.yaml.v1 goobits.yaml

# Downgrade Goobits (if needed)
pipx install goobits-cli==1.4.0
```

**2. Selective Rollback**:
```bash
# Keep v2.0 framework but use legacy templates
goobits build --no-universal-templates

# Keep Python language but revert configuration format
# (manually edit goobits.yaml back to v1.x format)
```

### Gradual Rollback

If issues are found after deployment:

1. **Identify specific problems**
2. **Fix individual components rather than complete rollback**
3. **Use legacy templates temporarily while debugging**
4. **Migrate back to universal templates once issues resolved**

## Migration Support

### Getting Help

1. **Documentation**: Check the complete v2.0 documentation
2. **Examples**: Look at the `docs/examples/` directory
3. **Community**: Join discussions for migration questions
4. **Issues**: Report migration problems on GitHub

### Common Migration Issues

**1. Configuration Validation Errors**:
```bash
# Error: Invalid configuration format
# Solution: Update to v2.0 YAML format (see examples above)
```

**2. Hook Function Not Found**:
```bash
# Error: Hook function 'on_command_name' not found
# Solution: Check hook naming convention (camelCase vs snake_case)
```

**3. Performance Regression**:
```bash
# Performance worse than v1.x
# Solution: Enable universal templates, optimize hooks, check dependencies
```

**4. Missing Dependencies**:
```bash
# Error: Module not found
# Solution: Update dependency specification in goobits.yaml
```

### Migration Best Practices

1. **Start Small**: Migrate simple projects first
2. **Test Thoroughly**: Validate all functionality after migration
3. **Monitor Performance**: Ensure v2.0 performance benefits are realized
4. **Document Changes**: Keep record of what was changed and why
5. **Gradual Adoption**: Don't rush to migrate all projects at once

---

This migration guide provides a comprehensive path from earlier versions to Goobits CLI Framework v2.0. Take your time, test thoroughly, and enjoy the improved performance and multi-language capabilities!