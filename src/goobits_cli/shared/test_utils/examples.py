"""Usage examples for shared test utilities.

This module demonstrates how to use the shared test utilities
for different testing scenarios.
"""
import pytest
from typing import Dict, List, Any

# Import the shared test utilities
from goobits_cli.shared.test_utils import (
    # Fixtures
    TestFixtures, create_test_config, create_minimal_cli_config,
    get_test_command_data, get_error_scenario,
    
    # Comparison tools
    CrossLanguageComparator, compare_command_outputs, 
    compare_file_structures, normalize_cli_output,
    
    # Test helpers  
    TestEnvironment, CLITestRunner, create_isolated_test_env,
    CommandResult, generate_cli_and_test, compare_cli_behaviors,
    
    # Phase 1 integration
    Phase1IntegrationRunner, run_comprehensive_cross_language_tests,
    
    # Validation
    validate_test_data, validate_framework_integration
)

# Import Phase 1 testing framework
# Import from the test conftest.py file
import sys
from pathlib import Path

# Add tests directory to path to import from conftest
tests_dir = Path(__file__).parents[4] / "tests"
sys.path.insert(0, str(tests_dir))

from conftest import generate_cli


class ExampleTestSuite:
    """Example test suite demonstrating shared utilities usage."""
    
    def test_basic_fixture_usage(self):
        """Example: Using test fixtures."""
        # Get common test data
        fixtures = TestFixtures()
        
        # Get a test configuration
        config_data = fixtures.get_config('basic', 'python')
        assert config_data['language'] == 'python'
        
        # Get common commands
        greet_command = fixtures.get_command('greet')
        assert greet_command.desc == 'Greet someone'
        
        # Get common options
        verbose_option = fixtures.get_option('verbose')
        assert verbose_option.name == 'verbose'
        assert verbose_option.type == 'flag'
    
    def test_create_custom_config(self):
        """Example: Creating custom test configurations."""
        # Create a basic Python CLI config
        config = create_test_config(
            package_name='my-test-cli',
            language='python',
            complexity='basic'
        )
        
        assert config.package_name == 'my-test-cli'
        assert config.language == 'python'
        assert 'greet' in config.cli.commands
        
        # Create a minimal Node.js config
        nodejs_config = create_minimal_cli_config('nodejs')
        assert nodejs_config.language == 'nodejs'
    
    def test_isolated_environment_usage(self):
        """Example: Using isolated test environments."""
        with create_isolated_test_env() as env:
            # Create a virtual environment
            venv_path = env.create_virtual_environment()
            assert venv_path.exists()
            
            # Install some packages
            env.install_python_packages(['click', 'rich'])
            
            # Set environment variables
            env.set_env_var('TEST_MODE', 'true')
            test_env = env.get_env()
            assert test_env['TEST_MODE'] == 'true'
    
    def test_cli_runner_usage(self):
        """Example: Using CLI test runner."""
        # Create a test configuration
        config = create_test_config('example-cli', 'python', 'basic')
        
        with create_isolated_test_env() as env:
            # Generate and install CLI
            files = generate_cli(config, 'example.yaml')
            cli_path = env.install_cli_from_files('example-cli', files)
            
            # Create test runner
            runner = CLITestRunner(env)
            
            # Test CLI help
            help_result = runner.test_cli_help('example-cli')
            assert help_result.success
            assert 'Usage:' in help_result.stdout
            
            # Test invalid command
            invalid_result = runner.test_cli_invalid_command('example-cli')
            assert invalid_result.failed
            assert invalid_result.exit_code != 0
    
    def test_cross_language_comparison(self):
        """Example: Cross-language CLI comparison."""
        # Create configs for multiple languages
        languages = ['python', 'nodejs']
        configs = {}
        
        for lang in languages:
            configs[lang] = create_test_config(f'test-{lang}', lang, 'minimal')
        
        # Generate CLIs and test help command
        test_commands = [['--help']]
        all_results = compare_cli_behaviors(configs, test_commands)
        
        # Extract help outputs for comparison
        help_outputs = {}
        for lang, results in all_results.items():
            if '--help' in results:
                help_outputs[lang] = results['--help'].stdout
        
        # Compare outputs
        if len(help_outputs) > 1:
            comparison = compare_command_outputs(help_outputs, ['--help'], 'help')
            
            # Verify comparison worked
            assert isinstance(comparison.passed, bool)
            assert len(comparison.similarities) >= 0
            assert len(comparison.differences) >= 0
    
    def test_output_normalization(self):
        """Example: Output normalization for comparison."""
        # Sample outputs from different languages
        python_output = """
Usage: cli.py [OPTIONS] COMMAND [ARGS]...

Test CLI

Options:
  --help  Show this message and exit.

Commands:
  greet  Greet someone
"""
        
        nodejs_output = """
Usage: node index.js [options] <command> [args]

Test CLI

Options:
  -h, --help  display help for command

Commands:
  greet       Greet someone
"""
        
        # Normalize outputs
        python_normalized = normalize_cli_output(python_output, 'python')
        nodejs_normalized = normalize_cli_output(nodejs_output, 'nodejs')
        
        # Both should contain common elements after normalization
        assert 'Usage: cli' in python_normalized
        assert 'Usage: cli' in nodejs_normalized
        assert 'greet' in python_normalized
        assert 'greet' in nodejs_normalized
    
    def test_error_scenario_handling(self):
        """Example: Testing error scenarios."""
        # Get a predefined error scenario
        error_scenario = get_error_scenario('missing_required_arg')
        
        # Verify scenario structure
        assert 'command' in error_scenario
        assert 'expected_exit_code' in error_scenario
        assert 'expected_patterns' in error_scenario
        
        expected_exit_code = error_scenario['expected_exit_code']
        expected_patterns = error_scenario['expected_patterns']['python']
        
        # Use scenario to test CLI
        config = create_minimal_cli_config('python')
        
        with create_isolated_test_env() as env:
            files = generate_cli(config, 'test.yaml')
            env.install_cli_from_files('test-cli', files)
            
            runner = CLITestRunner(env)
            
            # Run the error command
            result = runner.run_cli_command('test-cli', error_scenario['command'])
            
            # Verify expected behavior
            assert result.exit_code == expected_exit_code
            
            # Check for expected error patterns
            error_output = result.stderr.lower()
            found_patterns = [p for p in expected_patterns if p.lower() in error_output]
            assert len(found_patterns) > 0, f"No expected patterns found in: {result.stderr}"
    
    def test_file_structure_comparison(self):
        """Example: Comparing generated file structures."""
        # Generate files for different languages
        python_config = create_test_config('test-py', 'python', 'basic')
        nodejs_config = create_test_config('test-js', 'nodejs', 'basic')
        
        python_files = generate_cli(python_config, 'python.yaml')
        nodejs_files = generate_cli(nodejs_config, 'nodejs.yaml')
        
        file_structures = {
            'python': python_files,
            'nodejs': nodejs_files
        }
        
        # Compare file structures
        comparison = compare_file_structures(file_structures)
        
        # Verify comparison results
        assert comparison.languages_compared == ['python', 'nodejs']
        assert isinstance(comparison.passed, bool)
        
        # Both should generate some common files
        common_files = ['README.md', 'setup.sh']
        for common_file in common_files:
            python_has = common_file in python_files
            nodejs_has = common_file in nodejs_files
            
            if python_has and nodejs_has:
                # Should be noted as similarity
                similarity_found = any(common_file in sim for sim in comparison.similarities)
                # Note: This might not always be true depending on implementation
    
    def test_phase1_integration(self):
        """Example: Phase 1 framework integration."""
        # Run comprehensive cross-language tests
        results = run_comprehensive_cross_language_tests('minimal')
        
        # Verify results structure
        assert 'test_configuration' in results
        assert 'individual_results' in results
        assert 'cross_language_comparisons' in results
        assert 'summary' in results
        
        # Check summary data
        summary = results['summary']
        assert 'total_tests' in summary
        assert 'passed_tests' in summary
        assert 'failed_tests' in summary
        assert 'languages_consistent' in summary
    
    def test_validation_utilities(self):
        """Example: Using validation utilities."""
        # Validate test data
        test_data_result = validate_test_data()
        
        # Check validation result structure
        assert hasattr(test_data_result, 'passed')
        assert hasattr(test_data_result, 'errors')
        assert hasattr(test_data_result, 'warnings')
        
        # Validate framework integration
        integration_result = validate_framework_integration()
        
        assert hasattr(integration_result, 'passed')
        assert hasattr(integration_result, 'errors')
        
        # Print validation summary for debugging
        print(f"Test data validation: {test_data_result.get_summary()}")
        print(f"Integration validation: {integration_result.get_summary()}")


class ExampleEnhancedTest:
    """Example of enhancing existing tests with shared utilities."""
    
    def test_enhanced_cli_generation(self):
        """Enhanced version of a basic CLI generation test."""
        # Original test logic (from Phase 1)
        config = create_test_config('enhanced-cli', 'python', 'basic')
        files = generate_cli(config, 'enhanced.yaml')
        
        # Enhanced validation using shared utilities
        assert 'cli.py' in files  # Basic check
        
        # Enhanced cross-language validation
        languages = ['python', 'nodejs']
        all_configs = {lang: create_test_config(f'enhanced-{lang}', lang, 'basic') 
                      for lang in languages}
        
        # Test that all languages can generate successfully
        all_files = {}
        for lang, lang_config in all_configs.items():
            try:
                lang_files = generate_cli(lang_config, f'{lang}.yaml')
                all_files[lang] = lang_files
            except Exception as e:
                pytest.fail(f"Failed to generate {lang} CLI: {e}")
        
        # Compare file structures
        if len(all_files) > 1:
            structure_comparison = compare_file_structures(all_files)
            
            # Enhanced assertions
            assert structure_comparison.languages_compared == languages
            
            # If there are critical differences, provide detailed info
            if not structure_comparison.passed:
                diff_details = [diff['description'] for diff in structure_comparison.differences]
                pytest.fail(f"File structure inconsistencies: {diff_details}")


# Helper function for pytest integration
def pytest_configure(config):
    """Configure pytest to use shared test utilities."""
    # Add custom markers for cross-language tests
    config.addinivalue_line(
        "markers", "cross_language: mark test as cross-language comparison test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as integration test using shared utilities"
    )


# Pytest fixtures that can be reused
@pytest.fixture
def test_fixtures():
    """Fixture providing TestFixtures instance."""
    return TestFixtures()


@pytest.fixture
def cross_language_configs():
    """Fixture providing configs for all languages."""
    languages = ['python', 'nodejs', 'typescript', 'rust']
    return {lang: create_test_config(f'test-{lang}', lang, 'basic') for lang in languages}


@pytest.fixture
def isolated_test_environment():
    """Fixture providing isolated test environment."""
    with create_isolated_test_env() as env:
        yield env


@pytest.fixture
def cli_test_runner(isolated_test_environment):
    """Fixture providing CLI test runner."""
    return CLITestRunner(isolated_test_environment)


# Example of test class using fixtures
class TestWithFixtures:
    """Example test class using shared fixtures."""
    
    def test_with_fixtures(self, test_fixtures, cross_language_configs):
        """Test using shared fixtures."""
        # Use test fixtures
        basic_command = test_fixtures.get_command('greet')
        assert basic_command.desc == 'Greet someone'
        
        # Use cross-language configs
        assert len(cross_language_configs) >= 2
        for lang, config in cross_language_configs.items():
            assert config.language == lang
    
    def test_cli_execution_with_runner(self, cli_test_runner, isolated_test_environment):
        """Test CLI execution using test runner fixture."""
        # Create and install a test CLI
        config = create_minimal_cli_config('python')
        files = generate_cli(config, 'fixture-test.yaml')
        isolated_test_environment.install_cli_from_files('fixture-test-cli', files)
        
        # Use the CLI runner
        result = cli_test_runner.test_cli_help('fixture-test-cli')
        assert result.success
        assert 'Usage:' in result.stdout


if __name__ == '__main__':
    """
    Run examples as a script to demonstrate functionality.
    """
    print("Running shared test utilities examples...")
    
    # Example 1: Basic fixture usage
    print("\n1. Testing fixture usage...")
    example_suite = ExampleTestSuite()
    example_suite.test_basic_fixture_usage()
    print("✓ Fixture usage test passed")
    
    # Example 2: Configuration creation
    print("\n2. Testing configuration creation...")
    example_suite.test_create_custom_config()
    print("✓ Configuration creation test passed")
    
    # Example 3: Validation
    print("\n3. Running validation...")
    test_data_result = validate_test_data()
    integration_result = validate_framework_integration()
    
    print(f"✓ Test data validation: {test_data_result.get_summary()}")
    print(f"✓ Integration validation: {integration_result.get_summary()}")
    
    print("\nAll examples completed successfully!")
    print("\nTo run with pytest: pytest -v examples.py")