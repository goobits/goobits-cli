# Language Variations Documentation
## Agent A - Code Structure Patterns

This document details what patterns can be truly shared across all 4 languages versus what must remain language-specific to preserve idioms and best practices.

## Fully Shareable Patterns

These patterns exist in ALL 4 languages and can be abstracted:

### 1. Command Structure
- **Command name**: Identical string across all languages
- **Description**: Exact same help text
- **Command hierarchy**: Parent/child relationships preserved
- **Command aliases**: Same alternative names

### 2. Argument & Option Properties
- **Names and descriptions**: Identical strings
- **Required/optional status**: Same boolean flag
- **Default values**: Same values (with type conversion)
- **Choices/enums**: Same set of valid values
- **Environment variable names**: Identical fallbacks

### 3. Hook Naming Convention
- **Pattern**: `on_{command}[_{subcommand}]` works in all languages
- **Discovery**: All languages can map command names to hook names
- **Parameter names**: Can be standardized (with casing conventions)

### 4. Plugin Discovery Locations
- **User directory**: `~/.config/{cli_name}/plugins/`
- **Local directory**: `./plugins/` relative to CLI
- **System directory**: `/usr/share/{cli_name}/plugins/` (where applicable)

## Language-Specific Variations

These must remain different to preserve language idioms:

### 1. Syntax Patterns

#### Python
```python
# Decorators are idiomatic
@click.command()
@click.option('--name', default='world')
def greet(name):
    """Greet someone"""
    click.echo(f"Hello {name}")
```

#### Node.js/TypeScript
```javascript
// Method chaining is idiomatic
program
  .command('greet')
  .option('--name <value>', 'Name to greet', 'world')
  .action((options) => {
    console.log(`Hello ${options.name}`);
  });
```

#### Rust
```rust
// Derive macros are idiomatic
#[derive(Parser)]
struct Cli {
    /// Name to greet
    #[arg(long, default_value = "world")]
    name: String,
}
```

### 2. Type Systems

#### Static vs Dynamic
- **Python**: Dynamic typing with runtime checks
- **Node.js**: Dynamic with optional JSDoc
- **TypeScript**: Static typing with compile-time checks
- **Rust**: Static typing with ownership

#### Type Mappings
| Universal | Python | Node.js | TypeScript | Rust |
|-----------|---------|----------|------------|-------|
| string | str | String | string | String |
| number | int/float | Number | number | i32/f64 |
| boolean | bool | Boolean | boolean | bool |
| array | list | Array | T[] | Vec<T> |
| optional | Optional[T] | T \| undefined | T \| undefined | Option<T> |

### 3. Async Patterns

#### Python
- Primarily synchronous by default
- `async/await` available but not commonly used in CLIs
- Click doesn't natively support async commands

#### Node.js/TypeScript
- Async-first with Promises
- `async/await` is idiomatic
- Commander.js has built-in async support

#### Rust
- Explicit async with `tokio` or `async-std`
- `async fn` and `.await` syntax
- Optional based on feature flags

### 4. Error Handling

#### Python
```python
try:
    result = operation()
except SpecificError as e:
    click.echo(f"Error: {e}", err=True)
    sys.exit(1)
```

#### Node.js/TypeScript
```javascript
try {
  const result = await operation();
} catch (error) {
  console.error(`Error: ${error.message}`);
  process.exit(1);
}
```

#### Rust
```rust
match operation() {
    Ok(result) => result,
    Err(e) => {
        eprintln!("Error: {}", e);
        std::process::exit(1);
    }
}
// Or with ? operator
operation()?;
```

### 5. Module Systems

- **Python**: `import` statements, `__init__.py`, packages
- **Node.js**: CommonJS (`require`) or ESM (`import`)
- **TypeScript**: ESM with TypeScript compilation
- **Rust**: `mod` declarations, `use` statements, crates

## Abstraction Strategy

### What We Abstract
1. **Configuration Schema**: YAML structure is identical
2. **Command Metadata**: Names, descriptions, relationships
3. **Business Logic Interface**: Hook function signatures (adapted per language)
4. **File Locations**: Config files, plugins, data directories

### What We Preserve
1. **Language Syntax**: Decorators, macros, chaining, etc.
2. **Type Idioms**: Dynamic vs static, null handling
3. **Package Managers**: pip, npm, cargo
4. **Build Tools**: setuptools, webpack, cargo

### How We Bridge
1. **Name Mapping**: `snake_case` ↔ `camelCase` ↔ `PascalCase`
2. **Type Conversion**: Preserve semantics across type systems
3. **Async Adaptation**: Sync/async based on language preference
4. **Error Translation**: Exceptions ↔ Results ↔ Errors

## Implementation Guidelines

### For Schema Authors
- Define properties in universal terms
- Avoid language-specific concepts in schemas
- Use examples to show language variations
- Document type mappings explicitly

### For Generator Authors
- Read universal properties from schemas
- Apply language-specific templates
- Preserve idiomatic patterns
- Don't force foreign concepts

### For Framework Users
- Same YAML works across all languages
- Same commands and options everywhere
- Language-appropriate output code
- Native feel in each language

## Coordination with Other Agents

### Agent B (Operational Patterns)
- Error codes are universal (1, 2, 3, etc.)
- Config file formats are shared (JSON/YAML)
- Environment variables are identical
- Terminal output patterns are similar

### Agent C (Documentation)
- Help text is identical across languages
- Examples show language-specific syntax
- Version strings are synchronized
- Command descriptions are reused

### Agent D (Testing)
- Test scenarios are universal
- Assertions are language-specific
- Coverage requirements are similar
- E2E tests work across all CLIs