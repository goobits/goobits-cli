# Goobits CLI Framework Examples

This directory contains working examples demonstrating how to use Goobits CLI Framework v2.0 across all supported languages. Each example includes complete configuration files, hook implementations, and usage instructions.

## Available Examples

### Basic Examples

- **[simple-greeting/](#simple-greeting)** - Simple greeting CLI with basic commands
- **[file-processor/](#file-processor)** - File processing CLI with options and validation
- **[task-manager/](#task-manager)** - Task management CLI with subcommands

### Advanced Examples

- **[deployment-tool/](#deployment-tool)** - Production deployment tool with complex workflows
- **[api-client/](#api-client)** - REST API client with authentication and error handling
- **[development-toolkit/](#development-toolkit)** - Complete development toolkit with plugins

### Language-Specific Features

- **[python-advanced/](#python-advanced)** - Python-specific features and optimizations
- **[nodejs-modern/](#nodejs-modern)** - Modern Node.js with ES modules and async/await
- **[typescript-enterprise/](#typescript-enterprise)** - Enterprise TypeScript with full type safety

## Quick Start

Each example can be run immediately:

```bash
# Navigate to any example
cd docs/examples/simple-greeting

# Generate the CLI
goobits build --universal-templates

# Install and test
./setup.sh --dev
greeting --help
```

## Example Structure

Each example follows this structure:

```
example-name/
├── goobits.yaml           # Configuration file
├── README.md              # Example-specific documentation
├── app_hooks.py           # Python hooks (if applicable)
├── app_hooks.js           # Node.js hooks (if applicable)
├── app_hooks.ts           # TypeScript hooks (if applicable)
├── test_example.py        # Test script
└── expected_output/       # Expected CLI output samples
```

## Running Examples

### Python Examples

```bash
cd example-directory

# Generate Python CLI
language: python
goobits build --universal-templates

# Install and test
./setup.sh --dev
python cli.py --help
```

### Node.js Examples

```bash
cd example-directory

# Generate Node.js CLI
language: nodejs  # Update goobits.yaml
goobits build --universal-templates

# Install and test
./setup.sh --dev
node index.js --help
```

### TypeScript Examples

```bash
cd example-directory

# Generate TypeScript CLI
language: typescript  # Update goobits.yaml
goobits build --universal-templates

# Install, build, and test
./setup.sh --dev
npm run build
node dist/index.js --help
```

## Performance Testing

All examples can be performance tested:

```bash
# Validate performance
python ../../performance/startup_validator.py --command "python cli.py --help" --target 100

# Memory usage
python ../../performance/memory_profiler.py --command "python cli.py --version"

# Full performance suite
python ../../performance/performance_suite.py
```

## Contributing Examples

To contribute a new example:

1. **Create directory**: `docs/examples/my-example/`
2. **Add configuration**: Create `goobits.yaml` with clear, educational structure
3. **Implement hooks**: Add hook files for relevant languages
4. **Write documentation**: Include README.md explaining the example
5. **Add tests**: Include test script and expected outputs
6. **Test thoroughly**: Verify example works across all target languages

### Example Contribution Template

```yaml
# goobits.yaml
language: python  # Change to test different languages

package_name: my-example
command_name: myexample
display_name: "My Example CLI"
description: "Demonstrates specific Goobits CLI Framework features"

cli:
  name: myexample
  tagline: "Example CLI demonstrating X, Y, and Z"
  version: "1.0.0"
  
  commands:
    demo:
      desc: "Demonstrate core functionality"
      args:
        - name: input
          desc: "Input parameter"
          required: true
      options:
        - name: verbose
          short: v
          desc: "Verbose output"
          type: flag
```

```python
# app_hooks.py
def on_demo(input, verbose=False, **kwargs):
    """Demonstrate core functionality"""
    if verbose:
        print(f"Processing input: {input}")
    
    print(f"Demo result for: {input}")
    return 0
```

## Example Categories

### Learning Path

Follow examples in this order for best learning experience:

1. **simple-greeting** - Basic CLI structure
2. **file-processor** - Arguments and options
3. **task-manager** - Subcommands and complex structure
4. **api-client** - Error handling and external dependencies
5. **deployment-tool** - Production-ready patterns

### Feature Focus

Examples organized by feature demonstration:

- **Commands & Arguments**: simple-greeting, file-processor
- **Subcommands**: task-manager, deployment-tool
- **Error Handling**: api-client, development-toolkit
- **Performance**: All examples with performance validation
- **Type Safety**: typescript-enterprise
- **Async Operations**: nodejs-modern

## Testing All Examples

Run comprehensive testing across all examples:

```bash
#!/bin/bash
# test_all_examples.sh

echo "Testing all Goobits CLI examples..."

for example in docs/examples/*/; do
    if [[ -f "$example/goobits.yaml" ]]; then
        echo "Testing $(basename "$example")..."
        
        cd "$example"
        
        # Test Python
        sed -i 's/language:.*/language: python/' goobits.yaml
        goobits build --universal-templates && ./setup.sh --dev
        
        # Test Node.js
        sed -i 's/language:.*/language: nodejs/' goobits.yaml
        goobits build --universal-templates && ./setup.sh --dev
        
        # Test TypeScript
        sed -i 's/language:.*/language: typescript/' goobits.yaml
        goobits build --universal-templates && ./setup.sh --dev && npm run build
        
        cd - > /dev/null
        echo "✅ $(basename "$example") passed"
    fi
done

echo "All examples tested successfully!"
```

## Common Patterns

### Configuration Patterns

**Simple Command Structure**:
```yaml
cli:
  commands:
    action:
      desc: "Perform action"
      args: [...]
      options: [...]
```

**Subcommand Structure**:
```yaml
cli:
  commands:
    resource:
      desc: "Manage resources"
      subcommands:
        create: {...}
        delete: {...}
        list: {...}
```

**Complex Options**:
```yaml
options:
  - name: config
    short: c
    desc: "Configuration file"
    type: str
    default: "config.yaml"
  - name: verbose
    short: v
    desc: "Verbose output"
    type: count  # -v, -vv, -vvv
```

### Hook Patterns

**Error Handling Pattern**:
```python
def on_command(**kwargs):
    try:
        # Business logic
        result = perform_operation(kwargs)
        print(f"Success: {result}")
        return 0
    except ValidationError as e:
        print(f"Validation error: {e}")
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}")
        return 2
```

**Async Pattern (Node.js/TypeScript)**:
```javascript
export async function onCommand(args) {
    try {
        const result = await performAsyncOperation(args);
        console.log(`Success: ${result}`);
    } catch (error) {
        console.error(`Error: ${error.message}`);
        process.exit(1);
    }
}
```

## Best Practices from Examples

1. **Clear Command Structure**: Use descriptive command and option names
2. **Comprehensive Help**: Include detailed descriptions and examples
3. **Error Handling**: Always handle errors gracefully with helpful messages
4. **Performance**: Implement lazy loading for heavy operations
5. **Type Safety**: Use TypeScript for complex CLIs requiring type safety
6. **Testing**: Include test scripts and expected output validation

---

These examples provide hands-on learning experiences for mastering Goobits CLI Framework v2.0 across all supported languages.