# Advanced Features User Guide

This guide covers the advanced features available in Goobits CLI Framework v2.0, including interactive mode, shell completion, and performance optimization.

## Table of Contents

1. [Interactive Mode](#interactive-mode)
2. [Shell Completion](#shell-completion)
3. [Performance Optimization](#performance-optimization)
4. [Language-Specific Features](#language-specific-features)
5. [Troubleshooting](#troubleshooting)

## Interactive Mode

Interactive mode provides a REPL-style interface for your CLI applications, allowing users to run multiple commands in a single session.

### Availability

| Language | Status | Features |
|----------|--------|----------|
| **Python** | ✅ Fully Functional | Enhanced interactive mode with history, completion |
| **Node.js** | ⚠️ Partial | Framework available, needs integration testing |
| **TypeScript** | ⚠️ Framework Only | Framework exists, integration needs validation |
| **Rust** | ❌ Not Available | Not yet integrated |

### Using Interactive Mode

#### Python CLIs

Interactive mode is fully functional in Python-generated CLIs:

```bash
# Launch interactive mode
python mycli.py --interactive

# Example session:
🚀 Welcome to Enhanced Interactive Mode!
📝 Type 'help' for available commands, 'exit' to quit.
> help
Available commands:
  command1    Description of command 1
  command2    Description of command 2
  exit        Exit interactive mode
> command1 --arg value
[Command output here]
> exit
👋 Goodbye!
```

#### Testing Interactive Mode

```bash
# Quick test with automated exit
echo 'exit' | python mycli.py --interactive

# Test with commands
echo -e 'command1\nexit' | python mycli.py --interactive
```

#### Interactive Mode Features

- **Command History**: Navigate through previous commands with up/down arrows
- **Tab Completion**: Auto-complete command names and options
- **Help System**: Built-in help with `help` command
- **Graceful Exit**: Exit with `exit`, `quit`, or Ctrl+C
- **Error Handling**: Errors don't terminate the session

### Customizing Interactive Mode

#### Python Hook Integration

```python
# app_hooks.py
def on_interactive_start(**kwargs):
    """Called when interactive mode starts"""
    print("Welcome to my custom CLI!")
    return {"custom_prompt": "mycli> "}

def on_interactive_command(command, args, **kwargs):
    """Called for each command in interactive mode"""
    print(f"Executing: {command} with args: {args}")
    # Return True to continue, False to exit
    return True

def on_interactive_exit(**kwargs):
    """Called when interactive mode exits"""
    print("Thanks for using my CLI!")
```

## Shell Completion

Shell completion provides context-aware tab completion for your CLI commands and options.

### Availability

| Language | Bash | Zsh | Fish | Status |
|----------|------|-----|------|--------|
| **Node.js** | ✅ | ✅ | ✅ | Full templates generated |
| **TypeScript** | ✅ | ✅ | ✅ | Full templates generated |
| **Rust** | ✅ | ✅ | ✅ | Scripts generated in setup.sh |
| **Python** | ⚠️ | ⚠️ | ⚠️ | Minimal support (design decision) |

### Setting Up Shell Completion

#### 1. Generate Completion Scripts

```bash
# Generate completion files for your CLI
./setup.sh --completions

# Check generated files
ls -la completions/
# Should show: mycli.bash, mycli.zsh, mycli.fish (depending on language)
```

#### 2. Install Completion Scripts

**Bash:**
```bash
# Temporary (current session only)
source completions/mycli.bash

# Permanent (add to ~/.bashrc)
echo "source $(pwd)/completions/mycli.bash" >> ~/.bashrc
source ~/.bashrc
```

**Zsh:**
```bash
# Add completion directory to fpath (add to ~/.zshrc)
echo "fpath=($(pwd)/completions \$fpath)" >> ~/.zshrc
echo "autoload -U compinit && compinit" >> ~/.zshrc
source ~/.zshrc
```

**Fish:**
```bash
# Copy to Fish completion directory
cp completions/mycli.fish ~/.config/fish/completions/

# Restart Fish or reload configuration
fish
```

#### 3. Test Completion

```bash
# Test command completion
mycli [TAB]  # Should show available commands

# Test option completion
mycli command --[TAB]  # Should show available options

# Test argument completion (if supported)
mycli command --file [TAB]  # May show files
```

### Completion Features

#### Dynamic Completion

For languages with full support (Node.js, TypeScript, Rust):

- **Command Names**: Tab completion for all available commands
- **Option Names**: Completion for `--long` and `-short` options
- **Subcommands**: Multi-level command completion
- **Value Completion**: File paths, enum values, etc.

#### Example Completion Behavior

```bash
# Command completion
$ mycli [TAB]
build    deploy   init     serve

# Option completion
$ mycli build --[TAB]
--help     --output   --verbose  --config

# Subcommand completion
$ mycli project [TAB]
init       deploy     status
```

### Customizing Completion

#### Node.js/TypeScript

Completion behavior can be customized in the generated completion files:

```javascript
// In generated completion file
function _mycli_completions() {
    // Custom completion logic
    if (command === 'deploy') {
        // Complete with available environments
        return ['dev', 'staging', 'prod'];
    }
    // Default completion
    return [];
}
```

## Performance Optimization

Understanding and optimizing performance is crucial for production CLIs.

### Performance Characteristics

Based on validation testing:

| Metric | Target | Generated CLIs | Advanced Features |
|--------|--------|----------------|-------------------|
| **Startup Time** | <100ms | 88.7ms ✅ | +177ms ⚠️ |
| **Memory Usage** | <50MB | 1.7MB ✅ | Varies |
| **Success Rate** | >95% | 100% ✅ | 100% ✅ |

### Optimization Strategies

#### 1. Lazy Loading Advanced Features

For Python CLIs with advanced features:

```python
# app_hooks.py - Efficient lazy loading
def on_command(**kwargs):
    # Only load interactive mode when needed
    if kwargs.get('interactive'):
        from goobits_cli.enhanced_interactive_mode import InteractiveMode
        interactive = InteractiveMode()
        return interactive.start()
    
    # Regular command execution
    return handle_regular_command(kwargs)

def on_heavy_command(**kwargs):
    # Lazy import heavy libraries
    import pandas as pd  # Only when this command is used
    import numpy as np
    
    # Process with heavy libraries
    return process_data(kwargs)
```

#### 2. Hook Optimization

```python
# Efficient hook patterns
from functools import lru_cache
import sys

# Cache expensive computations
@lru_cache(maxsize=128)
def expensive_calculation(value):
    return complex_computation(value)

def on_optimized_command(**kwargs):
    # Early return for simple cases
    if kwargs.get('simple'):
        print("Simple response")
        return
    
    # Use cached computation
    result = expensive_calculation(kwargs.get('value'))
    return result

# Memory-efficient data processing
def on_large_data_command(**kwargs):
    # Use generators instead of loading everything
    for item in process_large_dataset_incrementally():
        yield process_item(item)
```

#### 3. Startup Time Monitoring

```python
# Add performance monitoring to hooks
import time
import sys

def performance_monitor(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        
        if end_time - start_time > 1.0:  # Log slow operations
            print(f"WARNING: {func.__name__} took {end_time - start_time:.2f}s", 
                  file=sys.stderr)
        
        return result
    return wrapper

@performance_monitor
def on_slow_command(**kwargs):
    # Your implementation
    pass
```

### Performance Testing

#### Quick Performance Check

```bash
# Test CLI startup time
time mycli --help

# Should complete in <100ms for generated CLIs
# May take longer if advanced features are loaded
```

#### Comprehensive Performance Testing

```bash
# Use Goobits performance validation tools
python performance/startup_validator.py --command "python mycli.py --help" --target 100

# Check memory usage
python performance/memory_profiler.py --command "python mycli.py command"
```

## Language-Specific Features

### Python

**Strengths:**
- Fully functional interactive mode
- Excellent hook system integration
- Rich ecosystem for CLI development

**Advanced Features:**
```python
# Enhanced interactive mode with custom prompts
def on_interactive_start(**kwargs):
    return {
        "prompt": "mycli> ",
        "welcome_message": "Welcome to My CLI!",
        "enable_history": True,
        "enable_completion": True
    }

# Performance monitoring hooks
def on_performance_check(**kwargs):
    import psutil
    import os
    
    process = psutil.Process(os.getpid())
    memory_mb = process.memory_info().rss / 1024 / 1024
    
    return {
        "memory_usage_mb": memory_mb,
        "cpu_percent": process.cpu_percent(),
        "startup_time_ms": kwargs.get('startup_time', 0)
    }
```

### Node.js

**Strengths:**
- Fast startup times (24.3ms when working)
- Full shell completion template generation
- Rich async/await support

**Current Limitations:**
- CLI functionality has issues (validation shows 0% success rate)
- ES module resolution problems in some environments

**Advanced Features:**
```javascript
// hooks.js - Async patterns
export async function onAsyncCommand(args) {
    // Parallel processing
    const [result1, result2] = await Promise.all([
        processTask1(args),
        processTask2(args)
    ]);
    
    return { result1, result2 };
}

// Dynamic imports for performance
export async function onHeavyCommand(args) {
    const { heavyLibrary } = await import('./heavy-library.js');
    return heavyLibrary.process(args);
}
```

### TypeScript

**Strengths:**
- Type safety for large projects
- Full shell completion template generation
- Excellent IDE support

**Current Issues:**
- 913ms startup time due to compilation overhead
- Integration status needs validation

**Advanced Features:**
```typescript
// hooks.ts - Type-safe implementations
interface CommandArgs {
    name: string;
    count?: number;
    verbose?: boolean;
}

interface CommandResult {
    success: boolean;
    message: string;
    data?: any;
}

export async function onTypedCommand(args: CommandArgs): Promise<CommandResult> {
    const { name, count = 1, verbose = false } = args;
    
    try {
        const result = await processCommand(name, count);
        
        if (verbose) {
            console.log(`Processed ${count} items for ${name}`);
        }
        
        return {
            success: true,
            message: `Successfully processed ${name}`,
            data: result
        };
    } catch (error) {
        return {
            success: false,
            message: `Error processing ${name}: ${error.message}`
        };
    }
}
```

### Rust

**Current Status:**
- ❌ Not production-ready due to compilation errors
- ❌ Generated code has type conversion issues
- ✅ Completion scripts are generated

**When Fixed (Future):**
```rust
// hooks.rs - High-performance patterns
use clap::ArgMatches;
use anyhow::Result;
use tokio;

pub async fn on_async_command(matches: &ArgMatches) -> Result<()> {
    let name = matches.value_of("name").unwrap_or("default");
    
    // Parallel processing with Tokio
    let (result1, result2) = tokio::join!(
        process_task_1(name),
        process_task_2(name)
    );
    
    println!("Results: {:?}, {:?}", result1?, result2?);
    Ok(())
}

pub fn on_performance_command(matches: &ArgMatches) -> Result<()> {
    use std::time::Instant;
    
    let start = Instant::now();
    
    // Your logic here
    let result = expensive_operation(matches);
    
    let duration = start.elapsed();
    if duration.as_millis() > 100 {
        eprintln!("WARNING: Operation took {:?}", duration);
    }
    
    result
}
```

## Troubleshooting

### Interactive Mode Issues

**Problem: `--interactive` flag not recognized**

```bash
# Check if you're using a Python CLI
python mycli.py --help | grep interactive

# If not present, regenerate with Python
language: python  # In goobits.yaml
goobits build
```

**Problem: Interactive mode exits immediately**

```bash
# Test with explicit exit command
echo 'exit' | python mycli.py --interactive

# Check for errors in hook functions
GOOBITS_DEBUG=true python mycli.py --interactive
```

### Shell Completion Issues

**Problem: No completion suggestions**

```bash
# Verify completion scripts exist
ls -la completions/

# Re-source shell configuration
source ~/.bashrc  # or ~/.zshrc

# Test with verbose completion
set -x  # Bash debug mode
mycli [TAB]
set +x
```

**Problem: Partial completion only**

```bash
# Check language support
# Node.js/TypeScript: Full support
# Rust: Scripts generated
# Python: Minimal support
```

### Performance Issues

**Problem: Slow startup with advanced features**

```bash
# This is expected (+177ms overhead)
# Use lazy loading patterns in hooks
# Only load advanced features when needed
```

**Problem: High memory usage**

```bash
# Profile memory usage
python performance/memory_profiler.py --command "python mycli.py command"

# Use generators instead of lists for large data
# Clear references when done
```

### Getting Help

1. **Check validation status**: `docs/IMPLEMENTATION_STATUS.md`
2. **Performance guide**: `docs/performance_guide.md`
3. **Language-specific guides**: `docs/{language}_guide.md`
4. **Troubleshooting**: `docs/troubleshooting.md`

---

This guide covers the current state of advanced features in Goobits CLI Framework v2.0. Features and availability may change in future releases as the framework continues to evolve.