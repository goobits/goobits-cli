"""Shared test utilities for goobits-cli testing framework.



This module provides common test utilities, fixtures, and comparison tools

that can be used across all language generators and testing scenarios.



## Key Components



### Fixtures (`fixtures.py`)

- `TestFixtures`: Central repository of test configurations and data

- `create_test_config()`: Create test configurations for any language

- Common command, option, and argument schemas



### Comparison Tools (`comparison_tools.py`)

- `CrossLanguageComparator`: Compare CLI behavior across languages

- `normalize_cli_output()`: Normalize outputs for comparison

- `compare_command_outputs()`: Compare command outputs

- `generate_diff_report()`: Generate detailed diff reports



### Test Helpers (`test_helpers.py`)

- `TestEnvironment`: Isolated test environment management

- `CLITestRunner`: CLI execution and testing utilities

- `FileSystemHelper`: File system operations for tests

- Context managers for temporary environments



### Phase 1 Integration (`phase1_integration.py`)

- `Phase1IntegrationRunner`: Enhanced test runner for Phase 1 framework

- Scenario-based testing capabilities

- Cross-language test validation



### Validation (`validation.py`)

- `validate_test_data()`: Validate test configurations and data

- `validate_framework_integration()`: Check integration compatibility

- Quality assurance for test utilities



## Usage Example



```python

from goobits_cli.shared.test_utils import (

    create_test_config,

    create_isolated_test_env,

    compare_command_outputs

)



# Create test configuration

config = create_test_config('my-cli', 'python', 'basic')



# Run tests in isolated environment

with create_isolated_test_env() as env:

    runner = CLITestRunner(env)

    result = runner.test_cli_help('my-cli')



# Compare outputs across languages

outputs = {'python': output1, 'nodejs': output2}

comparison = compare_command_outputs(outputs, ['--help'])

```

"""

from .fixtures import (
    TestFixtures,
    create_test_config,
    create_minimal_cli_config,
    create_complex_cli_config,
    get_test_command_data,
    get_test_option_data,
    get_test_argument_data,
    get_error_scenario,
    get_expected_patterns,
)

from .comparison_tools import (
    CrossLanguageComparator,
    ComparisonResult,
    normalize_cli_output,
    compare_command_outputs,
    generate_diff_report,
    compare_file_structures,
    extract_command_help_sections,
    validate_cross_language_consistency,
)

from .test_helpers import (
    TestEnvironment,
    CLITestRunner,
    FileSystemHelper,
    CommandResult,
    cleanup_test_environment,
    capture_command_output,
    validate_cli_execution,
    create_isolated_test_env,
    generate_cli_and_test,
    compare_cli_behaviors,
)

from .phase1_integration import (
    Phase1IntegrationRunner,
    create_phase1_integration_suite,
    run_comprehensive_cross_language_tests,
    validate_phase1_compatibility,
    enhance_test_with_cross_language_validation,
)

from .validation import (
    ValidationResult,
    TestDataValidator,
    FrameworkIntegrationValidator,
    validate_test_data,
    validate_framework_integration,
    run_complete_validation,
)


__all__ = [
    # Fixtures
    "TestFixtures",
    "create_test_config",
    "create_minimal_cli_config",
    "create_complex_cli_config",
    "get_test_command_data",
    "get_test_option_data",
    "get_test_argument_data",
    "get_error_scenario",
    "get_expected_patterns",
    # Comparison tools
    "CrossLanguageComparator",
    "ComparisonResult",
    "normalize_cli_output",
    "compare_command_outputs",
    "generate_diff_report",
    "compare_file_structures",
    "extract_command_help_sections",
    "validate_cross_language_consistency",
    # Test helpers
    "TestEnvironment",
    "CLITestRunner",
    "FileSystemHelper",
    "CommandResult",
    "cleanup_test_environment",
    "capture_command_output",
    "validate_cli_execution",
    "create_isolated_test_env",
    "generate_cli_and_test",
    "compare_cli_behaviors",
    # Phase 1 integration
    "Phase1IntegrationRunner",
    "create_phase1_integration_suite",
    "run_comprehensive_cross_language_tests",
    "validate_phase1_compatibility",
    "enhance_test_with_cross_language_validation",
    # Validation
    "ValidationResult",
    "TestDataValidator",
    "FrameworkIntegrationValidator",
    "validate_test_data",
    "validate_framework_integration",
    "run_complete_validation",
]
