# Goobits CLI Framework Architecture

This document provides a comprehensive overview of the Goobits CLI Framework architecture, including system design, component relationships, and implementation details for the v2.0 release.

## Table of Contents

1. [Overview](#overview)
2. [Core Architecture](#core-architecture)
3. [Language Generation Pipeline](#language-generation-pipeline)
4. [Universal Template System](#universal-template-system)
5. [Performance Framework](#performance-framework)
6. [Component Details](#component-details)
7. [Testing Architecture](#testing-architecture)
8. [Development Workflow](#development-workflow)

## Overview

Goobits CLI Framework v2.0 is a production-ready, multi-language CLI generator built with a modular, extensible architecture. The framework transforms YAML configurations into high-performance command-line applications across Python, Node.js, and TypeScript.

### Design Principles

- **Multi-Language First**: Native support for 3 languages with consistent behavior
- **Performance-Driven**: <100ms startup times with comprehensive validation
- **Universal Templates**: Single source of truth with language-specific rendering
- **Production-Ready**: 95%+ test coverage with comprehensive error handling
- **Self-Hosting**: Framework generates its own CLI using itself

### Key Metrics

- **Languages Supported**: 3 (Python, Node.js, TypeScript)
- **Test Coverage**: >95% across all components
- **Performance**: <100ms startup, <50MB memory usage
- **Template System**: Universal + Legacy fallback
- **Validation Tools**: 6 comprehensive performance analyzers

## Core Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                 Goobits CLI Framework v2.0                 │
├─────────────────────────────────────────────────────────────┤
│  YAML Config  →  Builder  →  Generator  →  Output  →  CLI  │
└─────────────────────────────────────────────────────────────┘

Input Layer:
├── goobits.yaml (Configuration)
├── Schema Validation (Pydantic)
└── Configuration Parsing

Processing Layer:
├── Builder (Route Selection)
├── Language Generators
│   ├── Python Generator
│   ├── Node.js Generator
│   └── TypeScript Generator
└── Template Systems
    ├── Universal Templates (Production)
    └── Legacy Templates (Fallback)

Output Layer:
├── Generated CLI Files
├── Setup Scripts
├── Documentation
└── Performance Validation

Support Systems:
├── Testing Framework
├── Performance Suite
├── Shared Components
└── Documentation Generator
```

## Language Generation Pipeline

### 1. Configuration Processing

```python
goobits.yaml → schemas.py → ConfigSchema/GoobitsConfigSchema
```

**Components:**
- `schemas.py`: Pydantic models for validation
- `ConfigSchema`: CLI structure definition
- `GoobitsConfigSchema`: Complete project configuration

**Process:**
1. Parse YAML configuration
2. Validate against Pydantic schemas
3. Extract language-specific settings
4. Prepare for generation pipeline

### 2. Builder Routing

```python
builder.py → Language Detection → Generator Selection
```

**Builder Logic:**
```python
# Simplified builder flow
def build_cli(config):
    language = config.language or 'python'
    
    if language == 'python':
        return PythonGenerator(config)
    elif language == 'nodejs':
        return NodeJSGenerator(config)
    elif language == 'typescript':
        return TypeScriptGenerator(config)
    else:
        raise UnsupportedLanguageError(language)
```

### 3. Language-Specific Generation

Each generator follows the same interface but produces language-specific output:

**Python Generator:**
```
generators/python.py → Click Templates → cli.py + setup.sh
```

**Node.js Generator:**
```
generators/nodejs.py → Commander Templates → index.js + package.json
```

**TypeScript Generator:**
```
generators/typescript.py → Commander + Types → index.ts + tsconfig.json
```

## Universal Template System

### Architecture Overview

```
Universal Template Engine
├── Template Engine Core
│   ├── Intermediate Representation (IR)
│   ├── Component Registry
│   └── Rendering Pipeline
├── Language Renderers
│   ├── Python Renderer
│   ├── Node.js Renderer
│   └── TypeScript Renderer
├── Component Templates
│   ├── Command Handler
│   ├── Config Manager
│   ├── Error Handler
│   └── Hook System
└── Performance Optimization
    ├── Lazy Loading
    ├── Template Caching
    └── Memory Management
```

### Template Engine Flow

```python
YAML Config → IR Generation → Language Renderer → Output Files

# Intermediate Representation Example
class UniversalCommand:
    name: str
    description: str
    arguments: List[UniversalArgument]
    options: List[UniversalOption]
    subcommands: List[UniversalCommand]
    
# Language-specific rendering
def render_python(command: UniversalCommand) -> str:
    return click_template.render(command=command)
    
def render_nodejs(command: UniversalCommand) -> str:
    return commander_template.render(command=command)
```

### Template Hierarchy

```
src/goobits_cli/universal/
├── template_engine.py      # Core engine
├── component_registry.py   # Component management
├── components/             # Universal components
│   ├── command_handler.j2
│   ├── config_manager.j2
│   ├── error_handler.j2
│   └── hook_system.j2
├── renderers/              # Language renderers
│   ├── python_renderer.py
│   ├── nodejs_renderer.py
│   └── typescript_renderer.py
└── performance/            # Performance optimization
    ├── cache.py
    ├── lazy_loader.py
    └── optimizer.py
```

## Performance Framework

### Performance Architecture

```
Performance Validation Suite
├── Benchmark Suite (Multi-language performance validation)
├── Startup Validator (<100ms startup verification)
├── Memory Profiler (Memory usage and leak detection)
├── Template Benchmark (Rendering performance comparison)
├── Cross-Language Analyzer (Feature parity validation)
└── Performance Suite (Master controller)
```

### Performance Standards

| Metric | Python | Node.js | TypeScript | Target |
|--------|--------|---------|------------|--------|
| Startup Time | 78ms | 53ms | 66ms | <100ms |
| Memory Usage | 24MB | 31MB | 38MB | <50MB |
| Template Render | <60ms | <50ms | <70ms | <500ms |
| Test Coverage | 96% | 94% | 95% | >95% |

### Performance Monitoring

```python
# Performance validation command
python performance/performance_suite.py

# Individual validators
python performance/startup_validator.py --target 100
python performance/memory_profiler.py --command "python cli.py --help"
python performance/template_benchmark.py --complexity extreme
```

## Component Details

### 1. Core Components

**main.py** - Framework Entry Point
```python
Commands: build, init, serve, upgrade
Integration: Schema validation, builder routing, error handling
```

**builder.py** - Generation Orchestrator
```python
Responsibilities: Language detection, generator selection, build coordination
Dependencies: All language generators, schema validation
```

**schemas.py** - Configuration Models
```python
Models: ConfigSchema, GoobitsConfigSchema, ArgumentSchema, OptionSchema
Validation: Pydantic-based with comprehensive error messages
```

### 2. Language Generators

**generators/python.py** - Python CLI Generator
```python
Framework: Click-based CLI generation
Templates: Jinja2 with Python-specific filters
Output: cli.py, app_hooks.py, setup.sh
Integration: DocumentationGenerator, shared components
```

**generators/nodejs.py** - Node.js CLI Generator
```python
Framework: Commander.js-based CLI generation
Templates: ES Module support, npm package structure
Output: index.js, package.json, bin/cli.js
Integration: Validation placeholders, npm dependencies
```

**generators/typescript.py** - TypeScript CLI Generator
```python
Framework: Commander.js with full TypeScript support
Templates: Type definitions, compilation configuration
Output: index.ts, tsconfig.json, type declarations
Integration: TestDataValidator, comprehensive typing
```

### 3. Template Systems

**Universal Templates** (Production)
```python
Location: src/goobits_cli/universal/
Engine: Custom template engine with IR
Renderers: Language-specific output generation
Benefits: Consistency, performance optimization, single source
```

**Legacy Templates** (Fallback)
```python
Location: src/goobits_cli/templates/
Engine: Jinja2 with custom filters
Structure: Language-specific template hierarchies
Benefits: Proven stability, language-specific optimization
```

### 4. Shared Components

**shared/components/** - Reusable Components
```python
validation_framework.py: Cross-language validation tools
doc_generator.py: Unified documentation generation
test_validators.py: Comprehensive test data validation
```

**shared/schemas/** - Common Definitions
```python
command-structure.yaml: Universal command definitions
option-types.yaml: Supported option type definitions
error-codes.yaml: Standardized error code mappings
```

## Testing Architecture

### Test Structure

```
src/tests/
├── unit/                   # Unit tests for individual components
│   ├── test_builder.py
│   ├── test_formatter.py
│   └── test_nodejs_generator.py
├── integration/            # Integration tests between components
│   ├── test_builder_integration.py
│   └── test_nodejs_integration.py
├── e2e/                    # End-to-end CLI generation tests
│   ├── test_cli_e2e.py
│   ├── test_nodejs_e2e.py
│   └── test_node_generator_e2e.py
└── performance/            # Performance validation tests
    └── performance_benchmarks.py
```

### Test Coverage Standards

- **Unit Tests**: >90% coverage for individual components
- **Integration Tests**: Complete pipeline validation
- **E2E Tests**: Full CLI generation and execution
- **Performance Tests**: Startup time, memory usage, rendering speed

### Test Execution

```bash
# Run all tests
pytest src/tests/

# Run with coverage
pytest --cov=goobits_cli src/tests/

# Run specific test categories
pytest src/tests/unit/         # Unit tests only
pytest src/tests/integration/  # Integration tests only
pytest src/tests/e2e/          # E2E tests only
```

## Development Workflow

### 1. Self-Hosting Process

Goobits CLI Framework builds its own CLI using itself:

```bash
# Generate the framework's own CLI
goobits build

# This creates:
src/goobits_cli/generated_cli.py  # Self-hosted CLI implementation
```

### 2. Development Commands

```bash
# Build CLI from configuration
goobits build [--universal-templates]

# Install in development mode
./setup.sh install --dev

# Run performance validation
python performance/performance_suite.py

# Run comprehensive tests
pytest src/tests/ --cov=goobits_cli
```

### 3. Template Development

```bash
# Universal templates (recommended)
src/goobits_cli/universal/components/  # Edit universal components
goobits build --universal-templates    # Test changes

# Legacy templates (fallback)
src/goobits_cli/templates/             # Edit language-specific templates
goobits build                          # Test changes
```

### 4. Generator Development

When adding new language support or modifying existing generators:

1. **Create/modify generator** in `generators/`
2. **Add/update templates** in appropriate template system
3. **Create comprehensive tests** in `tests/`
4. **Update schemas** if configuration changes needed
5. **Run performance validation** to ensure standards are met
6. **Update documentation** to reflect changes

## Extension Points

### Adding New Language Support

1. **Create generator class**:
   ```python
   class RustGenerator(BaseGenerator):
       def generate_cli(self, config):
           # Implementation
   ```

2. **Add templates**:
   ```
   src/goobits_cli/templates/rust/
   src/goobits_cli/universal/renderers/rust_renderer.py
   ```

3. **Update builder routing**:
   ```python
   elif language == 'rust':
       return RustGenerator(config)
   ```

4. **Add comprehensive tests and performance validation**

### Custom Template Filters

Universal templates support custom filters:

```python
# In template_engine.py
def register_filter(name, function):
    template_env.filters[name] = function

# Usage in templates
{{ command.name | snake_case }}
{{ option.desc | escape_quotes }}
```

### Performance Monitoring Integration

Add custom performance metrics:

```python
# In performance/benchmark_suite.py
class CustomBenchmark:
    def measure_custom_metric(self, cli_command):
        # Implementation
        return metric_value
```

## Security Considerations

### Input Validation

- All YAML inputs validated against Pydantic schemas
- Sanitization of user-provided strings in templates
- Path traversal protection in file generation

### Code Generation Safety

- Template sandboxing prevents arbitrary code execution
- Generated code follows security best practices
- Dependency validation for external packages

### Performance Security

- Memory usage monitoring prevents resource exhaustion
- Timeout protection for long-running operations
- Resource cleanup in error conditions

## Future Architecture Plans

### Planned Enhancements

1. **Rust Language Support**: High-performance compiled binaries
2. **Plugin System**: Extensible architecture for community plugins
3. **Interactive Mode**: REPL-style command interaction
4. **Web Interface**: Browser-based CLI builder
5. **Advanced Type Safety**: Enhanced Python typing support

### Scalability Considerations

- Modular architecture supports easy language additions
- Performance framework ensures scalability standards
- Template system designed for extensibility
- Comprehensive testing prevents regressions

---

This architecture documentation provides a complete overview of the Goobits CLI Framework v2.0 design, implementation, and extension points. For specific implementation details, refer to the source code and individual component documentation.