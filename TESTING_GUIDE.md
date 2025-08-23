# 🧪 Goobits CLI Framework Testing Guide

Comprehensive guide to the multi-layered testing architecture for developers working on the Goobits CLI Framework.

## 🏗️ Testing Architecture Philosophy

Goobits CLI Framework uses a **purpose-built multi-system testing architecture** designed specifically for multi-language CLI generation:

```
┌─────────────────┐    ┌──────────────────────┐    ┌─────────────────────┐
│   PyTest Suite  │    │  Feature Parity     │    │  Performance Suite  │
│   (Traditional) │    │  (YAML-Driven)      │    │   (Benchmarking)    │
└─────────────────┘    └──────────────────────┘    └─────────────────────┘
         │                        │                           │
    Unit/Integration      Cross-Language CLI         Production-Ready
    Code Quality          Behavior Validation        Performance Analysis
```

### Why Three Systems?

**Each system serves a fundamentally different purpose:**

1. **PyTest**: Code quality, regressions, component testing
2. **Feature Parity**: Cross-language CLI behavior consistency  
3. **Performance**: Production readiness and optimization

## 📋 Testing Systems Overview

### 1. 🐍 PyTest Suite (`src/tests/`)

**Purpose**: Traditional software testing (unit, integration, e2e)  
**Target**: Framework code quality and regression prevention  
**Execution**: `make test-pytest` or `pytest src/tests/`

```bash
# Quick unit tests during development
make test-unit

# Integration tests for complex workflows  
make test-integration

# End-to-end CLI generation testing
make test-e2e

# Performance regression tests (basic)
make test-performance
```

**Categories:**
- **Unit** (`src/tests/unit/`): Component-level testing (generators, schemas, etc.)
- **Integration** (`src/tests/integration/`): Cross-component workflows
- **E2E** (`src/tests/e2e/`): Complete CLI generation and execution
- **Performance** (`src/tests/performance/`): Basic performance regression testing

### 2. 🌐 Feature Parity System (`src/tests/feature-parity/`)

**Purpose**: Cross-language CLI behavior validation  
**Target**: Ensure generated CLIs behave consistently across Python/Node.js/TypeScript/Rust  
**Execution**: `make test-parity`

```bash
# Run all parity tests
make test-parity

# Test specific language (if supported)
python src/tests/feature-parity/run_parity_tests.py --language python nodejs
```

**YAML-Driven Test Definitions:**
```yaml
# Example: src/tests/feature-parity/suites/basic-commands.yaml
suite_name: basic-commands
description: Tests for basic command execution

tests:
  - name: help_command
    description: Verify help command shows expected output
    command: --help
    stdout:
      contains:
        - "test-cli"
        - "hello"
```

**Key Features:**
- **Declarative**: Tests defined in YAML, not code
- **Cross-Language**: Single test runs against all 4 language implementations  
- **CLI-Focused**: Tests actual command execution, not framework internals

### 3. ⚡ Performance Suite (`performance/`)

**Purpose**: Production performance validation and benchmarking  
**Target**: Startup times, memory usage, template rendering performance  
**Execution**: `python performance/performance_suite.py`

```bash
# Complete performance validation
python performance/performance_suite.py --quick

# Specific performance tools
python performance/startup_validator.py --target 90 --iterations 10
python performance/memory_profiler.py --command "python cli.py --help"
python performance/template_benchmark.py --complexity all
```

**Production Thresholds:**
- **Startup Time**: Python <90ms, Node.js <70ms, TypeScript <80ms
- **Memory Usage**: <50MB for typical operations
- **Template Rendering**: <500ms for complex CLI generation
- **Success Rate**: >95% reliability required

## 🚀 Development Workflows

### During Development (Daily)

```bash
# Quick feedback loop
make test-fast          # PyTest only (~2-5 min)
make lint               # Code quality
make typecheck          # Type validation
```

### Before Pull Request

```bash
# Comprehensive validation
make test-all           # All systems (~10-20 min)
make test-parity        # Cross-language validation
```

### Release Validation

```bash
# Full production readiness check
make test-all
python performance/performance_suite.py
# Manual review of performance benchmarks
```

## 🎯 When to Use Each System

### Use PyTest Suite When:
- ✅ Testing framework components (generators, schemas)
- ✅ Validating template rendering logic
- ✅ Checking error handling and edge cases
- ✅ Running regression tests during development
- ✅ Testing internal APIs and utilities

### Use Feature Parity When:
- ✅ Adding new CLI features (commands, options, arguments)
- ✅ Modifying command-line behavior
- ✅ Ensuring consistency across language implementations
- ✅ Validating help text, error messages, exit codes
- ✅ Testing complex nested command structures

### Use Performance Suite When:
- ✅ Optimizing startup times or memory usage
- ✅ Before major releases
- ✅ After significant template system changes
- ✅ Investigating performance regressions
- ✅ Validating production readiness

## 🔧 Adding New Tests

### Adding PyTest Tests

```python
# src/tests/unit/test_new_feature.py
import pytest
from goobits_cli.new_feature import NewFeature

class TestNewFeature:
    def test_basic_functionality(self):
        feature = NewFeature()
        assert feature.process() == expected_result
```

### Adding Feature Parity Tests

```yaml
# src/tests/feature-parity/suites/new-feature.yaml
suite_name: new-feature
description: Tests for new CLI feature

tests:
  - name: new_command_help
    description: Verify new command shows help
    command: new-command --help
    stdout:
      contains:
        - "new-command"
        - "usage"
```

### Adding Performance Benchmarks

```python
# performance/custom_benchmark.py
def benchmark_new_feature():
    # Custom performance validation
    with measure_performance():
        result = new_feature.execute()
    
    assert result.duration_ms < target_ms
    assert result.memory_mb < target_mb
```

## 🔍 Debugging Test Failures

### PyTest Failures
```bash
# Run specific failing test with verbose output
pytest src/tests/unit/test_feature.py::TestClass::test_method -v -s

# Run with debugger
pytest --pdb src/tests/unit/test_feature.py::test_method
```

### Feature Parity Failures
```bash
# Run single parity suite with verbose output  
python src/tests/feature-parity/run_parity_tests.py --suite basic-commands --verbose

# Check generated CLI manually
cd /tmp/parity_test_output/python && python cli.py --help
```

### Performance Failures
```bash
# Run performance suite with detailed output
python performance/performance_suite.py --verbose

# Profile specific component
python performance/memory_profiler.py --command "your-command" --profile
```

## 📊 CI/CD Integration

### Current CI Pipeline
```yaml
# .github/workflows/test.yml (current)
- Lint and type check
- PyTest suite with coverage
- Basic CLI generation testing
- Multi-version Python testing (3.8-3.12)
```

### Recommended Tiered Approach

**Tier 1: PR Checks** (~5-10 minutes)
```bash
make test-fast    # PyTest only
make lint         # Ruff + mypy  
make typecheck    # Type validation
```

**Tier 2: Integration Validation** (~10-20 minutes)
```bash
make test-all     # Complete test suite
```

**Tier 3: Release Validation** (~20-30 minutes)  
```bash
make test-all
python performance/performance_suite.py
# Manual performance review
```

## 🎓 Best Practices

### Test Organization
- **Keep tests close to code**: Unit tests mirror source structure
- **Use descriptive names**: Test names should explain what's being validated
- **Group related tests**: Use test classes and logical groupings

### Performance Considerations
- **Basic regression tests in PyTest**: Quick performance checks during development
- **Detailed benchmarks separate**: Use performance suite for comprehensive analysis
- **Profile before optimizing**: Use performance tools to identify bottlenecks

### Cross-Language Consistency
- **Add parity tests for new features**: Every CLI feature should have cross-language validation
- **Test edge cases**: Error handling, invalid inputs, boundary conditions
- **Validate user experience**: Help text, error messages, command structure

## 🚨 Common Issues & Solutions

### "Tests pass individually but fail in CI"
- **Race conditions**: Use proper test isolation
- **Environment differences**: Check Python versions, dependencies
- **Resource constraints**: Increase timeouts for performance tests

### "Parity tests failing for one language"
- **Generation issues**: Check generator logic for specific language
- **Template problems**: Validate language-specific templates
- **CLI execution**: Test generated CLI manually

### "Performance tests flaky"
- **System load**: Run on consistent hardware
- **Warm-up iterations**: Allow JIT compilation/caching to stabilize
- **Statistical analysis**: Use multiple iterations and averages

## 🔗 Related Documentation

- **[CODEMAP.md](./CODEMAP.md)**: Complete project architecture overview
- **[CLAUDE.md](./CLAUDE.md)**: Development setup and commands  
- **[Makefile](./Makefile)**: All available test commands
- **[performance/README.md](./performance/README.md)**: Detailed performance suite documentation
- **[.github/workflows/](/.github/workflows/)**: CI/CD pipeline configuration

---

*This testing guide reflects the multi-layered architecture designed specifically for multi-language CLI generation. Each system serves its purpose - use them in combination for comprehensive validation.*