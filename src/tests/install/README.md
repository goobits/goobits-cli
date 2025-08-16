# Installation Workflow Validation Tests

This directory contains comprehensive tests for validating that generated CLIs install correctly across all supported package managers and languages.

## Overview

The installation test suite validates:

- **Python**: `pip` and `pipx` installation workflows
- **Node.js**: `npm` and `yarn` installation workflows  
- **TypeScript**: Build and installation workflows with `npm`/`yarn`
- **Rust**: `cargo` installation workflows

Each test covers the complete pipeline:
1. Generate CLI from test configuration
2. Install via package manager
3. Verify CLI is available and functional
4. Test uninstallation

## Test Structure

### Core Test Modules

- **`test_installation_workflows.py`** - Main installation workflow tests
- **`test_dependency_resolution.py`** - Dependency installation and resolution tests
- **`test_integration_workflows.py`** - End-to-end integration tests

### Support Modules

- **`package_manager_utils.py`** - Package manager interaction utilities
- **`test_configs.py`** - Test configuration templates
- **`test_runner.py`** - Comprehensive test runner with reporting

### Test Data

- **Test configurations** for different scenarios (minimal, complex, dependency-heavy, edge cases)
- **Package manager helpers** for pip, npm, yarn, cargo, pipx
- **Environment validation** utilities

## Running Tests

### Prerequisites

Install the package managers you want to test:

```bash
# Python package managers
pip install --upgrade pip
pip install pipx

# Node.js package managers  
npm install -g npm@latest
npm install -g yarn

# Rust package manager
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
```

### Running Individual Test Suites

```bash
# Run all installation workflow tests
pytest test_installation_workflows.py -v

# Run dependency resolution tests
pytest test_dependency_resolution.py -v

# Run integration tests
pytest test_integration_workflows.py -v

# Run tests for specific language
pytest test_installation_workflows.py -k "python" -v

# Run tests with specific markers
pytest -m "requires_pip" -v
pytest -m "integration" -v
```

### Running with Test Runner

The comprehensive test runner provides detailed reporting:

```bash
# Run all tests with full reporting
python test_runner.py

# Run specific languages
python test_runner.py --languages python nodejs

# Run specific scenarios
python test_runner.py --scenarios minimal complex

# Run specific test types
python test_runner.py --test-types workflows dependencies

# Verbose output
python test_runner.py --verbose

# Custom output directory
python test_runner.py --output-dir my_test_results
```

## Test Categories

### Installation Workflow Tests

Tests the complete installation pipeline for each language:

- **Python Tests**:
  - `test_pip_install_workflow()` - Test pip editable installation
  - `test_pipx_install_workflow()` - Test pipx isolated installation
  - `test_python_generated_files_validation()` - Validate setup.py/pyproject.toml

- **Node.js Tests**:
  - `test_npm_install_workflow()` - Test npm installation and global linking
  - `test_yarn_install_workflow()` - Test yarn installation and global add
  - `test_nodejs_generated_files_validation()` - Validate package.json

- **TypeScript Tests**:
  - `test_typescript_build_and_install()` - Test compilation and installation
  - `test_typescript_generated_files_validation()` - Validate tsconfig.json

- **Rust Tests**:
  - `test_cargo_install_workflow()` - Test cargo build and install
  - `test_rust_generated_files_validation()` - Validate Cargo.toml

### Dependency Resolution Tests

Tests dependency handling across package managers:

- **Minimal Dependencies** - Test basic dependency declarations
- **Complex Dependencies** - Test CLIs with many dependencies
- **Version Constraints** - Test dependency version specifications
- **Cross-Platform** - Test platform-independent dependency resolution
- **Conflict Resolution** - Test handling of dependency conflicts

### Integration Tests

End-to-end tests covering complete workflows:

- **Critical Workflows** - Test essential language/scenario combinations
- **Parallel Installation** - Test multiple CLIs installed simultaneously
- **Environment Validation** - Test environment setup validation
- **Cross-Language Consistency** - Test consistent behavior across languages
- **Performance Benchmarks** - Test installation performance

## Test Configuration Templates

The test suite includes predefined configuration templates:

### Minimal Configuration
```python
config = TestConfigTemplates.minimal_config("python")
```
Basic CLI with minimal dependencies and simple commands.

### Complex Configuration
```python
config = TestConfigTemplates.complex_config("python") 
```
CLI with multiple commands, subcommands, options, and features.

### Dependency Heavy Configuration
```python
config = TestConfigTemplates.dependency_heavy_config("python")
```
CLI with many dependencies to test dependency resolution.

### Edge Case Configuration
```python
config = TestConfigTemplates.edge_case_config("python")
```
CLI with special characters, Unicode, and edge cases.

## Environment Requirements

### Required Package Managers

The tests automatically detect and skip tests for unavailable package managers:

- **pip** - Required for Python tests
- **npm** - Required for Node.js/TypeScript tests
- **cargo** - Required for Rust tests

### Optional Package Managers

- **pipx** - For isolated Python installations
- **yarn** - Alternative Node.js package manager

### System Requirements

- Python 3.8+
- Node.js 14+ (if testing Node.js/TypeScript)
- Rust 1.60+ (if testing Rust)
- Internet connection for dependency downloads

## Test Results and Reporting

The test runner generates comprehensive reports:

### JSON Results
```
install_test_results_YYYYMMDD_HHMMSS.json
```
Detailed machine-readable test results with timing, environment info, and failure details.

### Markdown Report
```
install_test_report_YYYYMMDD_HHMMSS.md
```
Human-readable report with summary, environment details, and recommendations.

### Console Output
Real-time progress and final summary with pass/fail rates and recommendations.

## Common Issues and Troubleshooting

### Package Manager Not Available
```
pytest.skip("pip not available")
```
Tests automatically skip when required package managers aren't installed.

### Permission Issues
Some package managers may require elevated permissions:
- Use virtual environments for Python testing
- Use `npm config set prefix` to set user-global npm directory
- Use `cargo install --root` for user-local Rust installations

### Network Issues
Tests require network access for dependency downloads:
- Ensure internet connectivity
- Check corporate firewall/proxy settings
- Consider using package manager caches/mirrors

### Platform Differences
Tests are designed to work across platforms but may have differences:
- Path separators (Windows vs Unix)
- Executable permissions
- Package manager behavior variations

## Extending the Test Suite

### Adding New Test Scenarios

1. Create new configuration template in `test_configs.py`:
```python
@staticmethod
def my_scenario_config(language: str) -> GoobitsConfigSchema:
    # Define configuration
    return GoobitsConfigSchema(**config_data)
```

2. Add to test matrix in `test_runner.py`

### Adding New Package Managers

1. Create manager class in `package_manager_utils.py`:
```python
class MyPackageManager:
    @staticmethod
    def is_available() -> bool:
        return shutil.which("my-pm") is not None
    
    @staticmethod 
    def install_from_path(package_path: str) -> subprocess.CompletedProcess:
        # Implementation
        pass
```

2. Register in `PackageManagerRegistry.managers`

3. Add test methods in appropriate test classes

### Adding New Languages

1. Update language support in `test_configs.py` templates
2. Add language-specific installation methods in test classes
3. Create language-specific file generation helpers
4. Update test matrices to include new language

## Performance Considerations

- Tests create temporary directories and install/uninstall packages
- Rust compilation can be slow (several minutes)
- Network dependencies add variability to test timing
- Use `--durations=10` to identify slow tests
- Consider running subsets for faster iteration

## Security Considerations

- Tests install packages globally which may affect system
- Use virtual environments and containers when possible
- Review generated code before installation
- Tests clean up installed packages but failures may leave artifacts
- Don't run tests with elevated privileges unless necessary

## Contributing

When adding new tests:

1. Follow existing naming conventions (`test_*`)
2. Use appropriate pytest markers
3. Include cleanup in teardown methods
4. Add error handling for package manager failures
5. Update documentation for new test scenarios
6. Ensure cross-platform compatibility