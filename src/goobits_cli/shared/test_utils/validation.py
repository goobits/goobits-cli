"""Validation utilities for test data and framework integration.

This module provides utilities to validate test configurations,
check framework integration, and ensure test data quality.

NOTE: ValidationResult is now imported from the unified goobits_cli.validation
module. It is re-exported here for backward compatibility.
"""

import yaml

from typing import Dict, List, Any, Optional
from pathlib import Path

from goobits_cli.core.schemas import GoobitsConfigSchema
from pydantic import ValidationError

# Import unified ValidationResult from canonical location
from goobits_cli.validation import ValidationResult


class TestDataValidator:
    """Validator for test data and configurations."""

    def __init__(self, test_data_path: Optional[Path] = None):

        if test_data_path is None:

            test_data_path = Path(__file__).parent.parent / "test_data"

        self.test_data_path = Path(test_data_path)

    def validate_all_test_configs(self) -> ValidationResult:
        """Validate all test configuration files."""

        result = ValidationResult(passed=True, errors=[], warnings=[], details={})

        configs_path = self.test_data_path / "configs"

        if not configs_path.exists():

            result.add_error(f"Configs directory not found: {configs_path}")

            return result

        validated_configs = {}

        # Validate configs in each complexity directory

        for complexity_dir in configs_path.iterdir():

            if not complexity_dir.is_dir():

                continue

            complexity = complexity_dir.name

            validated_configs[complexity] = {}

            for config_file in complexity_dir.glob("*.yaml"):

                language = config_file.stem

                try:

                    # Load and validate YAML syntax

                    with open(config_file) as f:

                        config_data = yaml.safe_load(f)

                    if config_data is None:

                        result.add_error(f"{config_file}: Empty configuration")

                        continue

                    # Validate against schema

                    try:

                        config_schema = GoobitsConfigSchema(**config_data)

                        validated_configs[complexity][language] = config_schema

                    except ValidationError as e:

                        result.add_error(
                            f"{config_file}: Schema validation failed: {e}"
                        )

                except yaml.YAMLError as e:

                    result.add_error(f"{config_file}: YAML parsing failed: {e}")

                except Exception as e:

                    result.add_error(f"{config_file}: Unexpected error: {e}")

        result.details["validated_configs"] = validated_configs

        return result

    def validate_expected_outputs(self) -> ValidationResult:
        """Validate expected output files."""

        result = ValidationResult(passed=True, errors=[], warnings=[], details={})

        outputs_path = self.test_data_path / "expected_outputs"

        if not outputs_path.exists():

            result.add_error(f"Expected outputs directory not found: {outputs_path}")

            return result

        # Check for required output categories

        required_categories = ["help", "version", "errors"]

        found_categories = []

        for category_dir in outputs_path.iterdir():

            if category_dir.is_dir():

                found_categories.append(category_dir.name)

                # Validate files in each category

                files_count = len(list(category_dir.glob("*")))

                if files_count == 0:

                    result.add_warning(f"No files in {category_dir.name} category")

        # Check for missing required categories

        for required in required_categories:

            if required not in found_categories:

                result.add_warning(f"Missing expected output category: {required}")

        result.details["found_categories"] = found_categories

        return result

    def validate_test_scenarios(self) -> ValidationResult:
        """Validate test scenario files."""

        result = ValidationResult(passed=True, errors=[], warnings=[], details={})

        scenarios_path = self.test_data_path / "scenarios"

        if not scenarios_path.exists():

            result.add_error(f"Scenarios directory not found: {scenarios_path}")

            return result

        validated_scenarios = {}

        for scenario_file in scenarios_path.glob("*.yaml"):

            scenario_name = scenario_file.stem

            try:

                with open(scenario_file) as f:

                    scenario_data = yaml.safe_load(f)

                # Validate scenario structure

                required_fields = ["name", "description", "test_cases"]

                for field in required_fields:

                    if field not in scenario_data:

                        result.add_error(
                            f"{scenario_file}: Missing required field '{field}'"
                        )

                # Validate test cases

                if "test_cases" in scenario_data:

                    for i, test_case in enumerate(scenario_data["test_cases"]):

                        if "name" not in test_case:

                            result.add_error(
                                f"{scenario_file}: Test case {i} missing 'name'"
                            )

                        if "command" not in test_case:

                            result.add_error(
                                f"{scenario_file}: Test case {i} missing 'command'"
                            )

                validated_scenarios[scenario_name] = scenario_data

            except yaml.YAMLError as e:

                result.add_error(f"{scenario_file}: YAML parsing failed: {e}")

            except Exception as e:

                result.add_error(f"{scenario_file}: Unexpected error: {e}")

        result.details["validated_scenarios"] = validated_scenarios

        return result

    def validate_cross_language_consistency(self) -> ValidationResult:
        """Validate that configurations are consistent across languages."""

        result = ValidationResult(passed=True, errors=[], warnings=[], details={})

        # First validate all configs

        config_validation = self.validate_all_test_configs()

        if not config_validation.passed:

            result.add_error("Cannot validate consistency: Config validation failed")

            return result

        validated_configs = config_validation.details.get("validated_configs", {})

        # Check consistency within each complexity level

        for complexity, configs in validated_configs.items():

            if len(configs) < 2:

                result.add_warning(
                    f"Only {len(configs)} language(s) in {complexity} complexity"
                )

                continue

            # Get a reference config (first one)

            reference_lang = list(configs.keys())[0]

            reference_config = configs[reference_lang]

            # Compare other configs to reference

            for language, config in configs.items():

                if language == reference_lang:

                    continue

                # Compare CLI structure

                ref_commands = set(reference_config.cli.commands.keys())

                lang_commands = set(config.cli.commands.keys())

                if ref_commands != lang_commands:

                    result.add_warning(
                        f"{complexity}/{language}: Command set differs from {reference_lang}: "
                        f"missing: {ref_commands - lang_commands}, "
                        f"extra: {lang_commands - ref_commands}"
                    )

                # Compare options

                ref_options = len(reference_config.cli.options or [])

                lang_options = len(config.cli.options or [])

                if ref_options != lang_options:

                    result.add_warning(
                        f"{complexity}/{language}: Different number of global options: "
                        f"{lang_options} vs {ref_options} in {reference_lang}"
                    )

        result.details["consistency_checks"] = {
            "complexities_checked": list(validated_configs.keys()),
            "total_configs": sum(
                len(configs) for configs in validated_configs.values()
            ),
        }

        return result


class FrameworkIntegrationValidator:
    """Validator for framework integration and compatibility."""

    def validate_phase1_integration(self) -> ValidationResult:
        """Validate integration with Phase 1 testing framework."""

        result = ValidationResult(passed=True, errors=[], warnings=[], details={})

        # Test imports

        try:

            # Import from the test conftest.py file

            import sys

            from pathlib import Path

            # Add tests directory to path to import from conftest

            tests_dir = Path(__file__).parents[4] / "tests"

            sys.path.insert(0, str(tests_dir))

            from conftest import generate_cli, determine_language

            result.details["phase1_helpers_imported"] = True

        except ImportError as e:

            result.add_error(f"Cannot import Phase 1 helpers: {e}")

        try:

            from tests.test_helpers import create_test_goobits_config

            result.details["phase1_test_helpers_imported"] = True

        except ImportError as e:

            result.add_error(f"Cannot import Phase 1 test helpers: {e}")

        # Test shared utilities

        try:

            from goobits_cli.shared.test_utils.fixtures import TestFixtures

            # Test basic functionality

            fixtures = TestFixtures()

            config_data = fixtures.get_config("minimal", "python")

            result.details["shared_utilities_functional"] = True

        except Exception as e:

            result.add_error(f"Shared utilities not functional: {e}")

        # Test integration

        try:

            from goobits_cli.shared.test_utils.phase1_integration import (
                validate_phase1_compatibility,
            )

            integration_result = validate_phase1_compatibility()

            if integration_result["compatible"]:

                result.details["integration_test_passed"] = True

            else:

                result.add_error(
                    f"Integration test failed: {integration_result['message']}"
                )

        except Exception as e:

            result.add_error(f"Integration test error: {e}")

        return result

    def validate_schema_compatibility(self) -> ValidationResult:
        """Validate that test utilities work with current schemas."""

        result = ValidationResult(passed=True, errors=[], warnings=[], details={})

        try:

            from goobits_cli.core.schemas import GoobitsConfigSchema

            from goobits_cli.shared.test_utils.fixtures import create_test_config

            # Test creating configs for all languages

            languages = ["python", "nodejs", "typescript", "rust"]

            created_configs = {}

            for language in languages:

                try:

                    config = create_test_config(f"test-{language}", language, "basic")

                    created_configs[language] = config

                except Exception as e:

                    result.add_error(f"Cannot create {language} config: {e}")

            result.details["created_configs"] = list(created_configs.keys())

        except ImportError as e:

            result.add_error(f"Schema compatibility test failed: {e}")

        return result


# Convenience functions


def validate_test_data(test_data_path: Optional[Path] = None) -> ValidationResult:
    """Validate all test data.



    Args:

        test_data_path: Path to test data directory



    Returns:

        Combined validation result

    """

    validator = TestDataValidator(test_data_path)

    # Combine all validation results

    combined_result = ValidationResult(passed=True, errors=[], warnings=[], details={})

    # Validate configs

    config_result = validator.validate_all_test_configs()

    combined_result.errors.extend(config_result.errors)

    combined_result.warnings.extend(config_result.warnings)

    combined_result.details["config_validation"] = config_result.details

    # Validate expected outputs

    output_result = validator.validate_expected_outputs()

    combined_result.errors.extend(output_result.errors)

    combined_result.warnings.extend(output_result.warnings)

    combined_result.details["output_validation"] = output_result.details

    # Validate scenarios

    scenario_result = validator.validate_test_scenarios()

    combined_result.errors.extend(scenario_result.errors)

    combined_result.warnings.extend(scenario_result.warnings)

    combined_result.details["scenario_validation"] = scenario_result.details

    # Validate consistency

    consistency_result = validator.validate_cross_language_consistency()

    combined_result.errors.extend(consistency_result.errors)

    combined_result.warnings.extend(consistency_result.warnings)

    combined_result.details["consistency_validation"] = consistency_result.details

    # Set overall result

    combined_result.passed = len(combined_result.errors) == 0

    return combined_result


def validate_framework_integration() -> ValidationResult:
    """Validate framework integration."""

    validator = FrameworkIntegrationValidator()

    combined_result = ValidationResult(passed=True, errors=[], warnings=[], details={})

    # Validate Phase 1 integration

    phase1_result = validator.validate_phase1_integration()

    combined_result.errors.extend(phase1_result.errors)

    combined_result.warnings.extend(phase1_result.warnings)

    combined_result.details["phase1_integration"] = phase1_result.details

    # Validate schema compatibility

    schema_result = validator.validate_schema_compatibility()

    combined_result.errors.extend(schema_result.errors)

    combined_result.warnings.extend(schema_result.warnings)

    combined_result.details["schema_compatibility"] = schema_result.details

    combined_result.passed = len(combined_result.errors) == 0

    return combined_result


def run_complete_validation() -> Dict[str, ValidationResult]:
    """Run complete validation of test utilities and integration."""

    return {
        "test_data": validate_test_data(),
        "framework_integration": validate_framework_integration(),
    }
