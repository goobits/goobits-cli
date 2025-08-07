"""Integration utilities for Phase 1 testing framework.

This module provides utilities to integrate the shared test utilities
with the existing Phase 1 testing framework, enhancing cross-language
testing capabilities while preserving existing functionality.
"""
import yaml
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path

from goobits_cli.main import load_goobits_config
from goobits_cli.schemas import GoobitsConfigSchema

# Import from the test conftest.py file
import sys
from pathlib import Path

# Add tests directory to path to import from conftest
tests_dir = Path(__file__).parents[4] / "tests"
sys.path.insert(0, str(tests_dir))

from conftest import generate_cli

from .fixtures import TestFixtures, fixtures
from .comparison_tools import CrossLanguageComparator, ComparisonResult
from .test_helpers import (
    TestEnvironment, CLITestRunner, create_isolated_test_env,
    CommandResult, generate_cli_and_test, compare_cli_behaviors
)


class Phase1IntegrationRunner:
    """Enhanced test runner that integrates Phase 1 framework with shared utilities."""
    
    def __init__(self):
        self.fixtures = TestFixtures()
        self.comparator = CrossLanguageComparator()
        self.test_data_path = Path(__file__).parent.parent / "test_data"
    
    def run_cross_language_test_suite(
        self,
        complexity: str = 'basic',
        languages: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Run comprehensive cross-language test suite.
        
        Args:
            complexity: Test complexity ('minimal', 'basic', 'complex')
            languages: Languages to test (defaults to all)
            
        Returns:
            Comprehensive test results
        """
        if languages is None:
            languages = ['python', 'nodejs', 'typescript', 'rust']
        
        # Load configurations for all languages
        configs = {}
        for language in languages:
            try:
                config_data = self.fixtures.get_config(complexity, language)
                configs[language] = GoobitsConfigSchema(**config_data)
            except Exception as e:
                print(f"Warning: Could not load {language} config: {e}")
                continue
        
        if not configs:
            raise ValueError("No valid configurations loaded")
        
        # Define standard test commands
        test_commands = [
            ['--help'],
            ['--version'],
            ['greet', '--help'],
            ['nonexistent'],  # Invalid command
            ['greet']         # Missing required argument
        ]
        
        # Run tests for all languages
        all_results = compare_cli_behaviors(configs, test_commands)
        
        # Perform cross-language comparisons
        comparison_results = self._perform_cross_language_comparisons(all_results)
        
        # Generate comprehensive report
        report = self._generate_test_report(all_results, comparison_results, complexity)
        
        return report
    
    def _perform_cross_language_comparisons(
        self,
        test_results: Dict[str, Dict[str, CommandResult]]
    ) -> Dict[str, ComparisonResult]:
        """Perform cross-language comparisons on test results."""
        comparisons = {}
        
        # Get all command variations tested
        all_commands = set()
        for lang_results in test_results.values():
            all_commands.update(lang_results.keys())
        
        # Compare each command across languages
        for command in all_commands:
            # Collect outputs for this command from all languages
            command_outputs = {}
            for language, lang_results in test_results.items():
                if command in lang_results:
                    result = lang_results[command]
                    # Use stdout if successful, stderr if failed
                    output = result.stdout if result.success else result.stderr
                    command_outputs[language] = output
            
            # Only compare if we have multiple languages
            if len(command_outputs) > 1:
                # Determine comparison type
                comparison_type = self._determine_comparison_type(command)
                
                # Perform comparison
                comparison = self.comparator.compare_cli_outputs(
                    command_outputs,
                    command.split(),
                    comparison_type
                )
                
                comparisons[command] = comparison
        
        return comparisons
    
    def _determine_comparison_type(self, command: str) -> str:
        """Determine the type of comparison for a command."""
        if '--help' in command:
            return 'help'
        elif '--version' in command:
            return 'version'
        elif command in ['nonexistent', 'greet']:  # Commands that should fail
            return 'error'
        else:
            return 'generic'
    
    def _generate_test_report(
        self,
        test_results: Dict[str, Dict[str, CommandResult]],
        comparison_results: Dict[str, ComparisonResult],
        complexity: str
    ) -> Dict[str, Any]:
        """Generate a comprehensive test report."""
        report = {
            'test_configuration': {
                'complexity': complexity,
                'languages_tested': list(test_results.keys()),
                'commands_tested': list(next(iter(test_results.values())).keys()),
                'timestamp': None  # Would be set in real implementation
            },
            'individual_results': test_results,
            'cross_language_comparisons': comparison_results,
            'summary': {
                'total_tests': 0,
                'passed_tests': 0,
                'failed_tests': 0,
                'languages_consistent': True,
                'critical_issues': []
            }
        }
        
        # Calculate summary statistics
        total_tests = 0
        passed_tests = 0
        
        for language, lang_results in test_results.items():
            for command, result in lang_results.items():
                total_tests += 1
                # Consider test passed if it behaved as expected
                expected_failure = command in ['nonexistent', 'greet']
                if (result.success and not expected_failure) or (result.failed and expected_failure):
                    passed_tests += 1
        
        report['summary']['total_tests'] = total_tests
        report['summary']['passed_tests'] = passed_tests
        report['summary']['failed_tests'] = total_tests - passed_tests
        
        # Check cross-language consistency
        for command, comparison in comparison_results.items():
            if not comparison.passed:
                report['summary']['languages_consistent'] = False
                report['summary']['critical_issues'].append({
                    'type': 'consistency_issue',
                    'command': command,
                    'description': comparison.summary,
                    'differences': len(comparison.differences)
                })
        
        return report
    
    def run_scenario_based_tests(
        self,
        scenario_name: str = 'cross_language_consistency'
    ) -> Dict[str, Any]:
        """Run tests based on predefined scenarios.
        
        Args:
            scenario_name: Name of the scenario file (without .yaml extension)
            
        Returns:
            Scenario test results
        """
        scenario_path = self.test_data_path / "scenarios" / f"{scenario_name}.yaml"
        
        if not scenario_path.exists():
            raise FileNotFoundError(f"Scenario file not found: {scenario_path}")
        
        with open(scenario_path) as f:
            scenario = yaml.safe_load(f)
        
        # Run tests according to scenario
        languages = scenario.get('languages', ['python'])
        test_cases = scenario.get('test_cases', [])
        
        results = {
            'scenario': scenario_name,
            'languages': languages,
            'test_cases': {},
            'summary': {
                'passed': 0,
                'failed': 0,
                'total': len(test_cases)
            }
        }
        
        for test_case in test_cases:
            case_name = test_case['name']
            command = test_case['command']
            
            # Load appropriate configs
            configs = {}
            for language in languages:
                # Use minimal config for scenario tests
                config_data = self.fixtures.get_config('minimal', language)
                configs[language] = GoobitsConfigSchema(**config_data)
            
            # Run the test command for all languages
            test_results = compare_cli_behaviors(configs, [command])
            
            # Validate against expected characteristics
            case_results = self._validate_test_case(test_case, test_results)
            
            results['test_cases'][case_name] = case_results
            
            if case_results['passed']:
                results['summary']['passed'] += 1
            else:
                results['summary']['failed'] += 1
        
        return results
    
    def _validate_test_case(
        self,
        test_case: Dict[str, Any],
        test_results: Dict[str, Dict[str, CommandResult]]
    ) -> Dict[str, Any]:
        """Validate test results against expected characteristics."""
        expected = test_case.get('expected_characteristics', {})
        command_str = ' '.join(test_case['command'])
        
        validation_results = {
            'passed': True,
            'validations': {},
            'issues': []
        }
        
        # Validate each language's result
        for language, lang_results in test_results.items():
            if command_str not in lang_results:
                validation_results['issues'].append(f"Command not executed for {language}")
                validation_results['passed'] = False
                continue
            
            result = lang_results[command_str]
            
            # Check exit code
            if 'exit_code' in expected:
                expected_code = expected['exit_code']
                if result.exit_code != expected_code:
                    validation_results['issues'].append(
                        f"{language}: Expected exit code {expected_code}, got {result.exit_code}"
                    )
                    validation_results['passed'] = False
            
            # Check output characteristics
            output = result.stdout + result.stderr
            
            if expected.get('contains_usage_line'):
                if 'Usage:' not in output:
                    validation_results['issues'].append(f"{language}: Missing 'Usage:' line")
                    validation_results['passed'] = False
            
            if expected.get('contains_error_message'):
                if 'error' not in output.lower():
                    validation_results['issues'].append(f"{language}: Missing error message")
                    validation_results['passed'] = False
            
            # Add more validations as needed
        
        return validation_results
    
    def enhance_existing_tests(self, test_module_path: str) -> str:
        """Generate enhanced version of existing test module with shared utilities.
        
        Args:
            test_module_path: Path to existing test module
            
        Returns:
            Enhanced test code
        """
        # This would analyze existing test code and suggest enhancements
        # For now, return a template for enhanced testing
        
        enhanced_template = '''
# Enhanced test module using shared test utilities

import pytest
from goobits_cli.shared.test_utils import (
    TestFixtures, create_test_config,
    CrossLanguageComparator, compare_command_outputs,
    TestEnvironment, CLITestRunner, create_isolated_test_env
)

class TestEnhancedCLI:
    """Enhanced CLI tests using shared utilities."""
    
    @pytest.fixture
    def test_fixtures(self):
        return TestFixtures()
    
    @pytest.fixture
    def cross_language_configs(self, test_fixtures):
        """Create configs for all languages."""
        languages = ['python', 'nodejs', 'typescript', 'rust']
        return {
            lang: create_test_config(f'test-{lang}-cli', lang, 'basic')
            for lang in languages
        }
    
    def test_cross_language_help_consistency(self, cross_language_configs):
        """Test that help output is consistent across languages."""
        with create_isolated_test_env() as env:
            runner = CLITestRunner(env)
            outputs = {}
            
            for language, config in cross_language_configs.items():
                # Install CLI
                files = generate_cli(config, f"{language}.yaml")
                cli_path = env.install_cli_from_files(f'test-{language}', files)
                
                # Get help output
                result = runner.run_cli_command(f'test-{language}', ['--help'])
                outputs[language] = result.stdout
            
            # Compare outputs
            comparison = compare_command_outputs(outputs, ['--help'], 'help')
            
            # Assert consistency
            assert comparison.passed, f"Help inconsistency: {comparison.get_diff_summary()}"
            assert len(comparison.similarities) > 0, "No similarities found across languages"
    
    def test_error_handling_consistency(self, cross_language_configs):
        """Test that error handling is consistent."""
        # Similar pattern for error handling tests...
        pass
    
    def test_performance_benchmarks(self, cross_language_configs):
        """Benchmark CLI generation and execution performance."""
        # Performance testing using shared utilities...
        pass
'''
        
        return enhanced_template.strip()


def create_phase1_integration_suite() -> Phase1IntegrationRunner:
    """Create a Phase 1 integration test suite."""
    return Phase1IntegrationRunner()


def run_comprehensive_cross_language_tests(complexity: str = 'basic') -> Dict[str, Any]:
    """Run comprehensive cross-language tests.
    
    Args:
        complexity: Test complexity level
        
    Returns:
        Comprehensive test results
    """
    runner = Phase1IntegrationRunner()
    return runner.run_cross_language_test_suite(complexity)


def validate_phase1_compatibility():
    """Validate that shared utilities are compatible with Phase 1 tests."""
    try:
        # Test that we can import Phase 1 components
        from conftest import generate_cli, determine_language, create_test_goobits_config
        
        # Test basic fixture integration
        fixtures = TestFixtures()
        config_data = fixtures.get_config('minimal', 'python')
        
        # Test that we can create configurations
        from goobits_cli.schemas import GoobitsConfigSchema
        config = GoobitsConfigSchema(**config_data)
        
        # Test CLI generation
        files = generate_cli(config, "test.yaml")
        
        return {
            'compatible': True,
            'message': 'Phase 1 integration successful',
            'tested_components': [
                'fixtures integration',
                'schema compatibility',
                'CLI generation',
                'test helpers'
            ]
        }
    
    except Exception as e:
        return {
            'compatible': False,
            'message': f'Phase 1 integration failed: {e}',
            'error': str(e)
        }


# Convenience functions for integration

def enhance_test_with_cross_language_validation(test_function):
    """Decorator to enhance existing tests with cross-language validation."""
    def wrapper(*args, **kwargs):
        # Run original test
        original_result = test_function(*args, **kwargs)
        
        # Add cross-language validation
        runner = Phase1IntegrationRunner()
        validation_results = runner.run_cross_language_test_suite('minimal')
        
        # Combine results
        return {
            'original_test': original_result,
            'cross_language_validation': validation_results
        }
    
    return wrapper