# Troubleshooting Guide

This comprehensive troubleshooting guide helps you resolve common issues when working with Goobits CLI Framework v2.0. Issues are organized by category with detailed solutions and prevention tips.

## Table of Contents

1. [Installation Issues](#installation-issues)
2. [Configuration Problems](#configuration-problems)
3. [Generation Failures](#generation-failures)
4. [Runtime Errors](#runtime-errors)
5. [Performance Issues](#performance-issues)
6. [Language-Specific Problems](#language-specific-problems)
7. [Template System Issues](#template-system-issues)
8. [Dependency Problems](#dependency-problems)
9. [Platform-Specific Issues](#platform-specific-issues)
10. [Debug Mode and Diagnostics](#debug-mode-and-diagnostics)

## Installation Issues

### Issue: `goobits` command not found after installation

**Symptoms:**
```bash
$ goobits --version
bash: goobits: command not found
```

**Solutions:**

1. **Check pipx installation:**
   ```bash
   # Verify pipx is installed
   pipx --version
   
   # List installed packages
   pipx list
   
   # Reinstall if missing
   pipx install goobits-cli
   ```

2. **Check PATH configuration:**
   ```bash
   # Find where pipx installs binaries
   pipx environment
   
   # Add to PATH (add to ~/.bashrc or ~/.zshrc)
   export PATH="$HOME/.local/bin:$PATH"
   
   # Reload shell configuration
   source ~/.bashrc  # or ~/.zshrc
   ```

3. **Alternative installation methods:**
   ```bash
   # Try pip instead of pipx
   pip install --user goobits-cli
   
   # Or install globally (not recommended)
   sudo pip install goobits-cli
   ```

### Issue: Permission denied during installation

**Symptoms:**
```bash
$ ./setup.sh --dev
Permission denied: ./setup.sh
```

**Solution:**
```bash
# Make setup script executable
chmod +x setup.sh

# Then run installation
./setup.sh --dev
```

### Issue: Python version incompatibility

**Symptoms:**
```bash
ERROR: Package 'goobits-cli' requires Python 3.8 or higher
```

**Solutions:**

1. **Check Python version:**
   ```bash
   python --version
   python3 --version
   ```

2. **Install correct Python version:**
   ```bash
   # Ubuntu/Debian
   sudo apt update
   sudo apt install python3.8 python3.8-pip
   
   # macOS with Homebrew
   brew install python@3.8
   
   # Use pyenv for version management
   pyenv install 3.8.10
   pyenv global 3.8.10
   ```

## Configuration Problems

### Issue: YAML syntax errors

**Symptoms:**
```bash
$ goobits build
Error: Invalid YAML syntax in goobits.yaml
```

**Solutions:**

1. **Validate YAML syntax:**
   ```bash
   # Use online YAML validator or
   python -c "import yaml; yaml.safe_load(open('goobits.yaml'))"
   ```

2. **Common YAML issues:**
   ```yaml
   # BAD: Inconsistent indentation
   cli:
     name: mycli
       commands:  # Wrong indentation
   
   # GOOD: Consistent indentation
   cli:
     name: mycli
     commands:
   ```

3. **Fix common YAML mistakes:**
   ```yaml
   # BAD: Missing quotes for special characters
   description: CLI with special chars: []{}
   
   # GOOD: Quoted strings with special characters
   description: "CLI with special chars: []{}"
   ```

### Issue: Configuration validation errors

**Symptoms:**
```bash
$ goobits build
Error: Configuration validation failed:
- Field 'commands' is required
- Invalid language 'javascript'
```

**Solutions:**

1. **Check required fields:**
   ```yaml
   # Minimum required configuration
   language: python  # Required in v2.0
   package_name: my-cli
   command_name: mycli
   cli:
     name: mycli
     version: "1.0.0"
     commands: {}  # At least empty commands object
   ```

2. **Validate supported languages:**
   ```yaml
   # Supported languages in v2.0
   language: python      # ✅ Supported
   language: nodejs      # ✅ Supported  
   language: typescript  # ✅ Supported
   language: rust        # ❌ Not supported in v2.0
   ```

3. **Use validation command:**
   ```bash
   # Validate configuration before building
   goobits validate
   goobits validate --config custom.yaml
   ```

### Issue: Migration from v1.x configuration format

**Symptoms:**
```bash
$ goobits build
Error: Deprecated configuration format detected
```

**Solution:**
```bash
# Use migration guide
# Convert v1.x format to v2.0 format manually
# See docs/migration_guide.md for details

# Before (v1.x)
cli:
  commands:
    - name: hello
      help: Say hello

# After (v2.0)
language: python  # Add this
cli:
  commands:
    hello:          # Dictionary format
      desc: Say hello  # 'desc' instead of 'help'
```

## Generation Failures

### Issue: Template rendering errors

**Symptoms:**
```bash
$ goobits build
Error: Template rendering failed: 'dict object' has no attribute 'name'
```

**Solutions:**

1. **Try universal templates:**
   ```bash
   # Universal templates are more robust
   goobits build --universal-templates
   ```

2. **Check configuration structure:**
   ```yaml
   # Ensure proper command structure
   cli:
     commands:
       hello:  # Must be dictionary format
         desc: "Say hello"
         args: []  # Must be list, even if empty
   ```

3. **Enable debug mode:**
   ```bash
   # Get detailed error information
   GOOBITS_DEBUG=true goobits build --verbose
   ```

### Issue: Output directory errors

**Symptoms:**
```bash
$ goobits build
Error: Permission denied writing to output directory
```

**Solutions:**

1. **Check directory permissions:**
   ```bash
   # Ensure write permissions
   ls -la .
   chmod 755 .
   ```

2. **Specify output directory:**
   ```bash
   # Generate in specific directory
   mkdir -p output
   goobits build --output-dir ./output
   ```

### Issue: Universal template fallback

**Symptoms:**
```bash
$ goobits build --universal-templates
Warning: Falling back to legacy templates
```

**Analysis:**
This is not an error but a fallback mechanism. Universal templates automatically fall back to legacy templates when:

- Unsupported language features are detected
- Custom template filters are needed
- Complex template logic is required

**Solutions:**

1. **Check what caused fallback:**
   ```bash
   goobits build --universal-templates --verbose
   ```

2. **Accept fallback (recommended):**
   ```bash
   # Fallback ensures your CLI still generates correctly
   # Performance may be slightly lower but functionality is preserved
   ```

3. **Force universal templates (not recommended):**
   ```bash
   # Only if you need to debug template issues
   goobits build --universal-templates --strict
   ```

## Runtime Errors

### Issue: Hook function not found

**Symptoms:**
```bash
$ mycli command
Error: Hook function 'on_command' not found
```

**Solutions:**

1. **Check hook function naming:**
   ```python
   # Python: snake_case with 'on_' prefix
   def on_command_name(**kwargs):  # ✅ Correct
       pass
   
   def command_name(**kwargs):     # ❌ Missing 'on_' prefix
       pass
   ```

   ```javascript
   // JavaScript/TypeScript: camelCase with 'on' prefix
   export async function onCommandName(args) {}  // ✅ Correct
   export async function commandName(args) {}    // ❌ Missing 'on' prefix
   ```

2. **Check hook file location:**
   ```bash
   # Ensure hook file exists in project root
   ls -la app_hooks.py   # Python
   ls -la app_hooks.js   # Node.js
   ls -la app_hooks.ts   # TypeScript
   ```

3. **Check hook function exports:**
   ```javascript
   // JavaScript/TypeScript: Ensure functions are exported
   export async function onCommand(args) {}  // ✅ Correct
   async function onCommand(args) {}         // ❌ Not exported
   ```

### Issue: Import/module errors in hooks

**Symptoms:**
```bash
$ mycli command
ModuleNotFoundError: No module named 'requests'
```

**Solutions:**

1. **Install missing dependencies:**
   ```bash
   # Check if dependencies are specified in goobits.yaml
   dependencies:
     python: ["requests>=2.25.0"]
   
   # Reinstall with dependencies
   ./setup.sh --dev
   ```

2. **Check import statements:**
   ```python
   # Python: Use standard library when possible
   import json          # ✅ Standard library
   import requests      # ✅ If in dependencies
   import some_local    # ❌ Local modules not supported
   ```

### Issue: Command-line argument parsing errors

**Symptoms:**
```bash
$ mycli command --invalid-option
Error: No such option: --invalid-option
```

**Solutions:**

1. **Check configuration matches usage:**
   ```yaml
   # In goobits.yaml
   commands:
     command:
       options:
         - name: valid-option  # Use hyphens in config
           short: v
   ```

   ```bash
   # Usage
   mycli command --valid-option value  # ✅ Correct
   mycli command --invalid-option      # ❌ Not in config
   ```

2. **Check help text:**
   ```bash
   # Always check available options
   mycli command --help
   ```

## Advanced Features Issues

### Issue: Interactive mode not working

**Symptoms:**
```bash
$ mycli --interactive
Error: unrecognized arguments: --interactive
```

**Solutions:**

1. **Check language support:**
   ```bash
   # Interactive mode availability by language:
   # ✅ Python: Fully functional
   # ⚠️ Node.js: Framework available, partial integration
   # ⚠️ TypeScript: Framework exists, integration needs validation
   # ❌ Rust: Not yet integrated
   ```

2. **Verify Python CLI generation:**
   ```bash
   # Ensure you're using a Python-generated CLI
   python cli.py --help
   # Should show --interactive option in help text
   ```

3. **Test interactive mode:**
   ```bash
   # Test with simple exit command
   echo 'exit' | python cli.py --interactive
   
   # Expected output:
   # 🚀 Welcome to Enhanced Interactive Mode!
   # 📝 Type 'help' for available commands, 'exit' to quit.
   # > 👋 Goodbye!
   ```

### Issue: Shell completion not available

**Symptoms:**
```bash
$ mycli [TAB]
# No completion suggestions appear
```

**Solutions:**

1. **Generate completion scripts:**
   ```bash
   # Generate completion files
   ./setup.sh --completions
   
   # Check generated files
   ls -la completions/
   ```

2. **Install completion scripts:**
   ```bash
   # Bash
   source completions/mycli.bash
   
   # Zsh (add to ~/.zshrc)
   fpath=(./completions $fpath)
   autoload -U compinit && compinit
   
   # Fish
   cp completions/mycli.fish ~/.config/fish/completions/
   ```

3. **Check language support:**
   ```bash
   # Completion template availability:
   # ✅ Node.js: Full completion templates (bash, zsh, fish)
   # ✅ TypeScript: Full completion templates (bash, zsh, fish)
   # ✅ Rust: Completion scripts generated in setup.sh
   # ⚠️ Python: Minimal completion support (design decision)
   ```

### Issue: Advanced features causing slow startup

**Symptoms:**
```bash
$ time mycli --help
# Takes >250ms when advanced features are loaded
real    0m0.265s
```

**Analysis:**
This is a known issue. Advanced features add approximately +177ms overhead to CLI startup time.

**Solutions:**

1. **Use lazy loading (recommended):**
   ```python
   # In hook implementations, avoid importing advanced features at module level
   def on_command(**kwargs):
       # Import only when needed
       if kwargs.get('interactive'):
           from goobits_cli.enhanced_interactive_mode import InteractiveMode
           interactive = InteractiveMode()
           return interactive.start()
   ```

2. **Disable advanced features if not needed:**
   ```bash
   # Generate CLI without advanced features integration
   # (This option may be available in future versions)
   goobits build --minimal-features
   ```

3. **Accept the overhead for advanced functionality:**
   ```bash
   # Generated CLIs still meet targets (88.7ms average)
   # Overhead occurs only when advanced features are actually used
   ```

## Performance Issues

### Issue: Slow CLI startup time

**Symptoms:**
```bash
# CLI takes >2 seconds to start
$ time mycli --help
real    0m2.145s
```

**Solutions:**

1. **Use universal templates:**
   ```bash
   # Universal templates are optimized for performance
   goobits build --universal-templates
   ```

2. **Optimize hook imports:**
   ```python
   # BAD: Heavy imports at module level
   import pandas as pd
   import tensorflow as tf
   
   def on_command(**kwargs):
       # Use heavy libraries
   
   # GOOD: Lazy imports
   def on_command(**kwargs):
       import pandas as pd  # Import only when needed
       # Use pandas
   ```

3. **Profile startup time:**
   ```bash
   # Use performance validator
   python performance/startup_validator.py --command "python cli.py --help" --target 100
   ```

### Issue: High memory usage

**Symptoms:**
```bash
# CLI uses excessive memory
$ mycli command
# Memory usage spikes to >500MB
```

**Solutions:**

1. **Profile memory usage:**
   ```bash
   python performance/memory_profiler.py --command "python cli.py command"
   ```

2. **Optimize data structures:**
   ```python
   # BAD: Loading large datasets upfront
   BIG_DATA = load_massive_dataset()
   
   def on_command(**kwargs):
       return process_data(BIG_DATA)
   
   # GOOD: Load data when needed
   def on_command(**kwargs):
       data = load_data_incrementally()
       return process_data(data)
   ```

### Issue: Performance validation failures

**Symptoms:**
```bash
$ python performance/performance_suite.py
❌ Startup Time: 150ms (Target: <100ms) - FAIL
```

**Solutions:**

1. **Check performance benchmarks:**
   ```bash
   # Run individual validators
   python performance/startup_validator.py --debug
   python performance/memory_profiler.py --verbose
   ```

2. **Follow performance optimization guide:**
   ```bash
   # See docs/performance_guide.md for detailed optimization techniques
   ```

## Language-Specific Problems

### Python Issues

**Issue: Click library conflicts**

**Symptoms:**
```bash
ImportError: cannot import name 'click' from partially initialized module
```

**Solution:**
```bash
# Ensure proper Click version
pip install --upgrade click>=8.0.0

# Check for conflicting packages
pip list | grep click
```

### Node.js Issues

**Issue: ES Module import errors**

**Symptoms:**
```bash
$ node index.js
SyntaxError: Cannot use import statement outside a module
```

**Solutions:**

1. **Check package.json:**
   ```json
   {
     "type": "module",  // Required for ES modules
     "engines": {
       "node": ">=18.0.0"
     }
   }
   ```

2. **Use correct import syntax:**
   ```javascript
   // ✅ Correct ES module imports
   import { onCommand } from './app_hooks.js';  // Note .js extension
   
   // ❌ CommonJS syntax (won't work)
   const { onCommand } = require('./app_hooks');
   ```

**Issue: Missing npm dependencies**

**Symptoms:**
```bash
$ node index.js
Error: Cannot find module 'chalk'
```

**Solution:**
```bash
# Ensure all dependencies are installed
npm install
npm list  # Check installed packages

# If using Goobits setup
./setup.sh --dev
```

### TypeScript Issues

**Issue: Compilation errors**

**Symptoms:**
```bash
$ npm run build
error TS2307: Cannot find module './app_hooks'
```

**Solutions:**

1. **Check TypeScript configuration:**
   ```json
   // tsconfig.json
   {
     "compilerOptions": {
       "module": "NodeNext",
       "moduleResolution": "NodeNext",
       "allowSyntheticDefaultImports": true,
       "esModuleInterop": true
     }
   }
   ```

2. **Use correct import paths:**
   ```typescript
   // ✅ Correct TypeScript imports
   import { onCommand } from './app_hooks.js';  // Use .js extension
   
   // ❌ Incorrect imports
   import { onCommand } from './app_hooks';     // Missing extension
   ```

**Issue: Type definition errors**

**Symptoms:**
```bash
error TS2345: Argument of type 'string' is not assignable to parameter of type 'number'
```

**Solution:**
```typescript
// Define proper interfaces for hook arguments
interface CommandArgs {
    name: string;
    count?: number;  // Optional number
    verbose?: boolean;
}

export async function onCommand(args: CommandArgs): Promise<void> {
    const { name, count = 1, verbose = false } = args;
    // Type-safe implementation
}
```

### Rust Issues

**Issue: Rust compilation failures**

**Symptoms:**
```bash
$ goobits build
# Generates Rust files but...

$ cargo build
error[E0308]: mismatched types
  --> src/main.rs:42:23
   |
42 |     let result = match.value_of("arg")
   |                       ^^^^^^^^^ expected `&str`, found `Option<&str>`
```

**Analysis:**
This is a known critical issue. Generated Rust code has type conversion errors that prevent compilation.

**Status:**
- **Current State**: Rust generation produces files but code doesn't compile
- **Issue Type**: Type mismatches in generated code, hook system return type issues
- **Production Readiness**: ❌ Not ready for production use

**Workarounds:**

1. **Use alternative languages:**
   ```bash
   # Python, Node.js, and TypeScript are production-ready
   language: python      # ✅ Recommended
   language: nodejs      # ✅ Works well
   language: typescript  # ✅ Functional
   ```

2. **Manual Rust implementation:**
   ```bash
   # Use generated Rust code as a template and fix manually
   # This requires Rust knowledge to resolve type issues
   ```

3. **Wait for fix:**
   ```bash
   # Rust support is planned for future releases
   # Current completion: ~60% due to compilation issues
   ```

## Template System Issues

### Issue: Template filter not found

**Symptoms:**
```bash
$ goobits build
Error: No filter named 'custom_filter'
```

**Solutions:**

1. **Use built-in filters:**
   ```yaml
   # Built-in filters that work across all templates
   {{ command.name | lower }}
   {{ option.desc | title }}
   ```

2. **Register custom filters (advanced):**
   ```python
   # In custom generator
   from goobits_cli.templates import register_filter
   
   @register_filter('custom_filter')
   def my_filter(value):
       return value.upper()
   ```

### Issue: Universal template component not found

**Symptoms:**
```bash
$ goobits build --universal-templates
Error: Component 'custom_component' not found in registry
```

**Solution:**
```bash
# Check available components
python -c "from goobits_cli.universal.component_registry import ComponentRegistry; print(ComponentRegistry.list_components())"

# Use built-in components or fall back to legacy templates
goobits build  # Without --universal-templates
```

## Dependency Problems

### Issue: Conflicting package versions

**Symptoms:**
```bash
ERROR: pip's dependency resolver does not currently consider all the packages that are installed
```

**Solutions:**

1. **Use virtual environment:**
   ```bash
   # Create fresh virtual environment
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # or
   venv\Scripts\activate  # Windows
   
   # Install Goobits CLI
   pip install goobits-cli
   ```

2. **Clear package cache:**
   ```bash
   # Clear pip cache
   pip cache purge
   
   # Reinstall clean
   pip install --no-cache-dir goobits-cli
   ```

### Issue: System package dependencies

**Symptoms:**
```bash
$ ./setup.sh --dev
Error: Unable to install system packages (git, python3-dev)
```

**Solutions:**

1. **Install system packages manually:**
   ```bash
   # Ubuntu/Debian
   sudo apt update
   sudo apt install git python3-dev python3-pip
   
   # CentOS/RHEL
   sudo yum install git python3-devel python3-pip
   
   # macOS
   brew install git python
   ```

2. **Skip system packages:**
   ```bash
   # Install without system package management
   pip install goobits-cli
   # Then manually install any system dependencies
   ```

## Platform-Specific Issues

### Windows Issues

**Issue: PowerShell execution policy**

**Symptoms:**
```powershell
PS> .\setup.sh
Execution of scripts is disabled on this system
```

**Solution:**
```powershell
# Allow script execution (run as Administrator)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Or run specific script
PowerShell -ExecutionPolicy Bypass -File setup.sh
```

**Issue: Path separator issues**

**Symptoms:**
```bash
Error: Cannot find file at path/to/file
```

**Solution:**
```python
# In hook functions, use os.path or pathlib
import os
from pathlib import Path

def on_command(file_path, **kwargs):
    # ✅ Cross-platform path handling
    path = Path(file_path)
    
    # ❌ Unix-only path handling
    # path = "/".join([dir, file])
```

### macOS Issues

**Issue: Homebrew Python conflicts**

**Symptoms:**
```bash
$ goobits --version
dyld: Library not loaded: /usr/local/lib/python3.8
```

**Solution:**
```bash
# Use system Python or pyenv
pyenv install 3.8.10
pyenv global 3.8.10

# Or use Homebrew Python consistently
brew install python
pip3 install goobits-cli
```

## Debug Mode and Diagnostics

### Enable Debug Logging

```bash
# Enable comprehensive debug output
export GOOBITS_DEBUG=true
export GOOBITS_LOG_LEVEL=DEBUG

# Run with verbose output
goobits build --verbose --debug
```

### Diagnostic Commands

```bash
# Check Goobits installation
goobits --version
goobits validate --config goobits.yaml

# Check Python environment
python --version
pip list | grep goobits
which python

# Check Node.js environment (if applicable)
node --version
npm --version
npm list

# Performance diagnostics
python performance/performance_suite.py --quick --verbose
```

### Common Debug Patterns

**Configuration Debugging:**
```bash
# Validate configuration step by step
goobits validate --verbose

# Test minimal configuration
cat > minimal.yaml << EOF
language: python
package_name: test
command_name: test
cli:
  name: test
  version: "1.0.0"
  commands: {}
EOF

goobits build --config minimal.yaml
```

**Template Debugging:**
```bash
# Test both template systems
goobits build --universal-templates --verbose
goobits build --verbose

# Compare outputs
diff -r universal-output/ legacy-output/
```

**Runtime Debugging:**
```python
# Add debug prints in hooks
def on_command(**kwargs):
    import sys
    print(f"DEBUG: Called with args: {kwargs}", file=sys.stderr)
    print(f"DEBUG: Python version: {sys.version}", file=sys.stderr)
    
    # Your logic here
```

## Getting Additional Help

### Community Support

1. **Documentation**: Check the complete documentation in `docs/`
2. **Examples**: Look at working examples in `docs/examples/`
3. **GitHub Issues**: Search existing issues or create new ones
4. **Performance Analysis**: Use the performance validation tools

### Reporting Issues

When reporting issues, include:

1. **Goobits CLI version**: `goobits --version`
2. **Python version**: `python --version`
3. **Operating system**: `uname -a` (Linux/Mac) or `systeminfo` (Windows)
4. **Configuration file**: Contents of `goobits.yaml`
5. **Complete error message**: Full traceback or error output
6. **Steps to reproduce**: Exact commands that cause the issue

### Emergency Fallbacks

If nothing works:

1. **Use minimal configuration**: Start with the simplest possible CLI
2. **Fall back to legacy templates**: Remove `--universal-templates` flag
3. **Use virtual environment**: Isolate from system dependencies
4. **Try different Python version**: Use Python 3.8, 3.9, or 3.10
5. **Manual generation**: Generate files manually using templates as reference

---

This troubleshooting guide covers the most common issues. If you encounter problems not covered here, please refer to the GitHub issues or create a new issue with detailed information about your problem.