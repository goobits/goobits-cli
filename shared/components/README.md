# Goobits CLI Validation Framework

A comprehensive validation system for Goobits CLI configurations that ensures consistency across all supported languages (Python, Node.js, TypeScript, Rust).

## Overview

The validation framework provides:

- **Unified validation logic** across all language generators
- **Configurable validation modes** (strict, lenient, dev, production)
- **Language-specific validation rules** that respect each language's conventions
- **Dependency-aware validator ordering** for consistent execution
- **Rich error reporting** with suggestions and context
- **Performance optimization** for large configurations

## Architecture

### Core Components

#### `validation_framework.py`
- **`BaseValidator`**: Abstract base class for all validators
- **`ValidationResult`**: Container for validation messages and status
- **`ValidationContext`**: Execution context with configuration and metadata
- **`ValidationRegistry`**: Manages validator registration and dependencies
- **`ValidationRunner`**: Orchestrates validation execution

#### `validators.py`
Contains specific validators implementing the schemas from Agents A and B:

- **`CommandValidator`**: Validates command structure, names, descriptions
- **`ArgumentValidator`**: Validates positional arguments and their requirements
- **`HookValidator`**: Validates hook naming and parameter patterns
- **`OptionValidator`**: Validates CLI options, types, and defaults
- **`ErrorCodeValidator`**: Validates error handling patterns
- **`TypeValidator`**: Validates option types and cross-language compatibility
- **`ConfigValidator`**: Validates basic configuration structure
- **`CompletionValidator`**: Validates shell completion patterns

## Usage

### Basic Usage

```python
from shared.components import validate_config, ValidationMode

# Validate a configuration
config = load_yaml_config("goobits.yaml")
result = validate_config(config, language="python", mode=ValidationMode.STRICT)

if result.is_valid:
    print("✅ Configuration is valid")
else:
    print("❌ Validation failed:")
    for error in result.get_errors():
        print(f"  - {error.field_path}: {error.message}")
        if error.suggestion:
            print(f"    Suggestion: {error.suggestion}")
```

### Advanced Usage

```python
from shared.components import (
    ValidationRegistry, ValidationRunner, ValidationContext,
    CommandValidator, OptionValidator, TypeValidator
)

# Create custom validator set
registry = ValidationRegistry()
registry.register(CommandValidator())
registry.register(OptionValidator()) 
registry.register(TypeValidator())

# Run validation
runner = ValidationRunner(registry)
context = ValidationContext(
    config=config_data,
    language="typescript",
    mode=ValidationMode.DEV,
    file_path="goobits.yaml",
    working_dir="/path/to/project"
)

result = runner.validate_all(context)
```

### Integration with Generators

```python
# In a language generator
from shared.components import create_default_runner, ValidationContext

def generate_cli(self, config_data, language):
    # Validate before generation
    runner = create_default_runner()
    context = ValidationContext(config=config_data, language=language)
    result = runner.validate_all(context)
    
    if not result.is_valid:
        raise ValueError(f"Invalid configuration: {result.get_errors()}")
    
    # Proceed with generation...
```

## Validation Rules

### Command Validation
- Command names must be valid identifiers for target language
- Descriptions are required and should be informative
- Icons should be valid Unicode symbols
- Command groups must reference existing commands
- Only one default command is allowed

### Argument Validation
- Required arguments must come before optional ones
- Variadic arguments (`*`, `+`) must be last
- Argument names must be valid identifiers
- No duplicate argument names within a command

### Option Validation
- Option names should follow kebab-case convention
- Short options must be single characters
- Default values must match declared type
- Choices arrays must contain valid values
- No duplicate option names or short flags

### Type Validation
- Types are mapped consistently across languages
- Constraints are validated based on type
- Language-specific type considerations are checked

### Hook Validation
- Hook names follow language conventions (snake_case for Python, camelCase for JS/TS)
- Expected hooks are derived from command structure
- Parameter counts are reasonable for the target language

### Configuration Validation
- Required fields are present and non-empty
- Package names follow naming conventions
- Version constraints are logical
- Installation configuration is valid

## Validation Modes

### `ValidationMode.STRICT`
- All warnings become errors
- Strictest validation rules apply
- Best for CI/CD and production builds

### `ValidationMode.LENIENT`
- Only critical errors fail validation
- Warnings are informational
- Good for development iteration

### `ValidationMode.DEV`
- Additional development-specific checks
- Performance suggestions
- Completion optimization hints

### `ValidationMode.PRODUCTION`
- Minimal checks for performance
- Focus on critical errors only
- Optimized for fast validation

## Language Support

The framework validates configurations for all supported languages:

- **Python**: Click-based CLIs with snake_case conventions
- **Node.js**: Commander-based CLIs with camelCase conventions  
- **TypeScript**: Type-safe CLIs with strong typing
- **Rust**: Clap-based CLIs with snake_case and strong typing

### Language-Specific Features

#### Python
- Reserved keyword checking
- Click parameter validation
- Python version constraint validation

#### Node.js/TypeScript
- JavaScript identifier validation
- NPM package name validation
- TypeScript type generation support

#### Rust
- Rust identifier validation (no hyphens)
- Cargo package validation
- Memory safety considerations

## Error Messages

Validation messages include:

- **Severity levels**: Info, Warning, Error, Critical
- **Field paths**: Exact location of the issue
- **Clear descriptions**: What went wrong
- **Actionable suggestions**: How to fix it
- **Context information**: Additional relevant details

Example:
```
✗ ERROR at cli.commands.build.options[2].type: Invalid option type: 'stringg'
  Suggestion: Valid types: bool, choice, dir, file, flag, float, int, number, path, str, string
```

## Performance

The validation framework is optimized for:

- **Fast execution**: Typical configurations validate in <1ms
- **Memory efficiency**: Minimal object allocation
- **Scalability**: Handles large configurations (50+ commands)
- **Caching**: Results cached for repeated operations

## Testing

Run the test suite:

```bash
# Test the framework
python3 -m pytest shared/components/test_validators.py -v

# Test against real configuration
python3 test_existing_config.py
```

The test suite includes:
- Unit tests for each validator
- Integration tests with real configurations
- Cross-language compatibility tests
- Performance benchmarks
- Error condition testing

## Extension

### Creating Custom Validators

```python
from shared.components import BaseValidator, ValidationResult

class CustomValidator(BaseValidator):
    def __init__(self):
        super().__init__("CustomValidator")
        self.dependencies.add("CommandValidator")  # Optional dependencies
        
    def validate(self, context):
        result = ValidationResult()
        
        # Your validation logic here
        if some_condition:
            result.add_error("Something is wrong", "field.path", 
                           suggestion="Try this instead")
        
        return result

# Register with framework
registry.register(CustomValidator())
```

### Adding New Validation Rules

1. Identify the appropriate existing validator
2. Add validation logic to the validator
3. Add tests to `test_validators.py`
4. Update documentation

## Configuration

Validators can be configured through the validation context:

```python
context = ValidationContext(
    config=config_data,
    language="python",
    mode=ValidationMode.STRICT,
    metadata={
        "strict_naming": True,
        "allow_experimental": False,
        "max_command_depth": 3
    }
)
```

## Migration from Existing Validation

The framework maintains compatibility with existing Pydantic validation:

1. Existing configurations continue to work
2. New validation adds additional checks
3. Gradual migration path available
4. No breaking changes to existing behavior

## Troubleshooting

### Common Issues

**Import Errors**
```bash
# Make sure Python path includes shared/components
export PYTHONPATH="${PYTHONPATH}:$(pwd)/shared/components"
```

**Validation Failures**
- Check error messages for specific issues
- Use `ValidationMode.DEV` for additional insights
- Verify configuration against examples

**Performance Issues**
- Use `ValidationMode.PRODUCTION` for minimal checks
- Profile with timing information
- Consider validator subset for fast validation

### Debug Mode

Enable detailed logging:

```python
import logging
logging.getLogger('validation_framework').setLevel(logging.DEBUG)
```

## Contributing

When contributing to the validation framework:

1. Add tests for new validators or rules
2. Update documentation for new features
3. Ensure cross-language compatibility
4. Follow the established patterns
5. Test against real configurations

## Future Enhancements

Planned improvements:

- **Schema evolution**: Handle configuration format changes
- **Plugin validation**: Support for user-defined plugins
- **IDE integration**: Language server protocol support
- **Incremental validation**: Only validate changed parts
- **Custom rule sets**: Project-specific validation profiles