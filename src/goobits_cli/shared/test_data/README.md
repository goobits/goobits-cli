# Test Data Repository

This directory contains common test data, configurations, and expected outputs for testing the goobits-cli framework across all supported languages.

## Directory Structure

```
test_data/
├── configs/                    # Test CLI configurations
│   ├── minimal/               # Minimal test configurations
│   │   ├── python.yaml
│   │   ├── nodejs.yaml
│   │   ├── typescript.yaml
│   │   └── rust.yaml
│   ├── basic/                 # Basic test configurations
│   └── complex/               # Complex test configurations
├── expected_outputs/          # Expected CLI outputs
│   ├── help/                  # Help command outputs
│   ├── version/               # Version command outputs
│   └── errors/                # Error condition outputs
├── performance/               # Performance baseline data
├── scenarios/                 # Test scenario definitions
└── fixtures/                  # Additional test fixtures
```

## Usage

### Using Test Configurations

```python
from goobits_cli.shared.test_utils.fixtures import TestFixtures
from goobits_cli.main import load_goobits_config
from pathlib import Path

# Load a test configuration
config_path = Path(__file__).parent / "test_data" / "configs" / "basic" / "python.yaml"
config = load_goobits_config(config_path)

# Or use the fixtures helper
fixtures = TestFixtures()
config_data = fixtures.get_config('basic', 'python')
```

### Using Expected Outputs

```python
from goobits_cli.shared.test_utils import compare_command_outputs

# Load expected output for comparison
expected_file = "test_data/expected_outputs/help/python_basic_help.txt"
with open(expected_file) as f:
    expected_output = f.read()

# Compare with actual output
result = compare_command_outputs({
    'expected': expected_output,
    'actual': actual_output
}, ['--help'])
```

### Using Test Scenarios

```python
import yaml
from goobits_cli.shared.test_utils import CLITestRunner

# Load a test scenario
with open("test_data/scenarios/cross_language_consistency.yaml") as f:
    scenario = yaml.safe_load(f)

# Run the scenario
for test in scenario['tests']:
    # Execute test commands...
```

## Test Data Types

### Configuration Files (configs/)

Standard YAML configurations for testing different CLI complexities:

- **minimal/**: Single command CLIs with basic functionality
- **basic/**: Multiple commands with options and arguments
- **complex/**: Full-featured CLIs with subcommands, validation, etc.

Each configuration is available in all supported languages.

### Expected Outputs (expected_outputs/)

Normalized expected outputs for different CLI operations:

- **help/**: Output from `--help` commands
- **version/**: Output from `--version` commands  
- **errors/**: Expected error messages and formats

### Performance Data (performance/)

Baseline performance metrics for:

- CLI generation time by language and complexity
- Generated file sizes
- Memory usage during generation
- Execution time for common commands

### Test Scenarios (scenarios/)

YAML files defining comprehensive test scenarios:

- Cross-language consistency tests
- Feature parity validation
- Error handling verification
- Performance benchmarks

### Fixtures (fixtures/)

Additional test fixtures including:

- Mock file systems
- Sample input files
- Configuration variants
- Edge case data

## Maintenance

### Adding New Test Data

1. **New Configuration**: Add to appropriate complexity level in `configs/`
2. **Expected Output**: Capture and normalize output in `expected_outputs/`
3. **Performance Data**: Benchmark and store in `performance/`
4. **Test Scenario**: Define comprehensive test in `scenarios/`

### Updating Expected Outputs

When CLI behavior changes:

1. Generate fresh outputs using the test utilities
2. Normalize outputs using the comparison tools
3. Update expected output files
4. Verify cross-language consistency

### Validating Test Data

Use the validation utilities to ensure test data quality:

```python
from goobits_cli.shared.test_utils import validate_test_data

# Validate all test configurations
validation_report = validate_test_data("test_data/configs/")
```

## Integration with Testing Framework

This test data integrates with:

- **Unit Tests**: Individual component testing
- **Integration Tests**: End-to-end workflow testing
- **E2E Tests**: Full CLI lifecycle testing
- **Performance Tests**: Benchmarking and regression detection
- **Cross-Language Tests**: Consistency validation across languages

The data is designed to work seamlessly with the Phase 1 testing framework and the new shared test utilities.