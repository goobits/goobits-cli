#!/usr/bin/env python3
"""
Test validation against existing goobits.yaml configuration.

This script validates that the validation framework works correctly
with real-world configurations.
"""

import sys
import yaml
from pathlib import Path

# Add paths for imports
sys.path.insert(0, str(Path(__file__).parent / "shared" / "components"))
sys.path.insert(0, str(Path(__file__).parent / "src"))

try:
    from shared.components.validation_framework import (
        ValidationContext, ValidationMode, ValidationRegistry, ValidationRunner
    )
    from shared.components.validators import (
        CommandValidator, ArgumentValidator, HookValidator, OptionValidator,
        ErrorCodeValidator, TypeValidator, ConfigValidator, CompletionValidator
    )
    from src.goobits_cli.schemas import GoobitsConfigSchema
    from pydantic import ValidationError
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Make sure you're running from the goobits-cli directory")
    sys.exit(1)


def load_goobits_config() -> dict:
    """Load the existing goobits.yaml configuration."""
    config_path = Path(__file__).parent / "goobits.yaml"
    
    if not config_path.exists():
        raise FileNotFoundError(f"goobits.yaml not found at {config_path}")
    
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


def test_pydantic_validation(config_data: dict):
    """Test that the configuration passes Pydantic schema validation."""
    print("Testing Pydantic schema validation...")
    
    try:
        # Test with GoobitsConfigSchema
        goobits_config = GoobitsConfigSchema(**config_data)
        print("✅ Pydantic validation passed")
        return goobits_config
    except ValidationError as e:
        print("❌ Pydantic validation failed:")
        for error in e.errors():
            print(f"  - {error['loc']}: {error['msg']}")
        return None
    except Exception as e:
        print(f"❌ Unexpected error during Pydantic validation: {e}")
        return None


def test_custom_validation(config_data: dict):
    """Test the custom validation framework."""
    print("\nTesting custom validation framework...")
    
    # Create registry and add all validators
    registry = ValidationRegistry()
    registry.register(ConfigValidator())
    registry.register(TypeValidator())
    registry.register(CommandValidator())
    registry.register(ArgumentValidator())
    registry.register(HookValidator())
    registry.register(OptionValidator())
    registry.register(ErrorCodeValidator())
    registry.register(CompletionValidator())
    
    # Create runner
    runner = ValidationRunner(registry)
    
    # Test for each supported language
    languages = ["python", "nodejs", "typescript", "rust"]
    
    for language in languages:
        print(f"\n  Testing {language} validation...")
        
        context = ValidationContext(
            config=config_data,
            language=language,
            mode=ValidationMode.STRICT,
            file_path="goobits.yaml"
        )
        
        result = runner.validate_all(context)
        
        if result.is_valid:
            print(f"    ✅ {language} validation passed")
            
            # Print any warnings or info messages
            warnings = result.get_warnings()
            if warnings:
                print(f"    ⚠️  {len(warnings)} warning(s):")
                for warning in warnings:
                    print(f"      - {warning.message}")
        else:
            print(f"    ❌ {language} validation failed:")
            errors = result.get_errors()
            for error in errors:
                print(f"      - {error.field_path}: {error.message}")
                if error.suggestion:
                    print(f"        Suggestion: {error.suggestion}")
    
    return result


def test_validator_dependencies():
    """Test that validator dependencies are properly resolved."""
    print("\nTesting validator dependency resolution...")
    
    registry = ValidationRegistry()
    
    # Add validators (dependency order should be automatically resolved)
    validators = [
        CompletionValidator(),  # Depends on CommandValidator, OptionValidator
        OptionValidator(),      # Depends on TypeValidator
        ArgumentValidator(),    # Depends on CommandValidator
        HookValidator(),        # Depends on CommandValidator
        CommandValidator(),     # No dependencies
        TypeValidator(),        # No dependencies
        ConfigValidator(),      # No dependencies
        ErrorCodeValidator()    # No dependencies
    ]
    
    for validator in validators:
        registry.register(validator)
    
    execution_order = registry.list_validators()
    print(f"Execution order: {execution_order}")
    
    # Check that dependencies are satisfied
    validator_positions = {name: i for i, name in enumerate(execution_order)}
    
    for validator in validators:
        for dep in validator.dependencies:
            if dep in validator_positions:
                if validator_positions[dep] > validator_positions[validator.name]:
                    print(f"❌ Dependency error: {validator.name} should come after {dep}")
                    return False
    
    print("✅ All validator dependencies are correctly ordered")
    return True


def test_performance_metrics():
    """Test validation performance and collect metrics."""
    print("\nTesting validation performance...")
    
    config_data = load_goobits_config()
    
    registry = ValidationRegistry()
    validators = [
        ConfigValidator(),
        TypeValidator(), 
        CommandValidator(),
        ArgumentValidator(),
        HookValidator(),
        OptionValidator(),
        ErrorCodeValidator(),
        CompletionValidator()
    ]
    
    for validator in validators:
        registry.register(validator)
    
    runner = ValidationRunner(registry)
    context = ValidationContext(
        config=config_data,
        language="python",
        mode=ValidationMode.STRICT,
        file_path="goobits.yaml"
    )
    
    import time
    start_time = time.perf_counter()
    result = runner.validate_all(context)
    end_time = time.perf_counter()
    
    total_time = (end_time - start_time) * 1000  # Convert to ms
    
    print(f"Total validation time: {total_time:.2f}ms")
    print(f"Number of messages: {len(result.messages)}")
    print(f"Validation result: {'✅ PASSED' if result.is_valid else '❌ FAILED'}")
    
    # Print per-validator timing if available
    for validator_name in registry.list_validators():
        cached_result = runner.get_cached_result(validator_name)
        if cached_result and hasattr(cached_result, 'execution_time_ms'):
            print(f"  {validator_name}: {cached_result.execution_time_ms:.2f}ms")
    
    return result.is_valid


def main():
    """Main test function."""
    print("Testing Goobits CLI Validation Framework")
    print("=" * 50)
    
    try:
        # Load configuration
        config_data = load_goobits_config()
        print(f"✅ Loaded goobits.yaml ({len(config_data)} top-level keys)")
        
        # Test Pydantic validation
        pydantic_result = test_pydantic_validation(config_data)
        
        # Test custom validation
        validation_result = test_custom_validation(config_data)
        
        # Test validator dependencies
        dep_result = test_validator_dependencies()
        
        # Test performance
        perf_result = test_performance_metrics()
        
        # Summary
        print("\n" + "=" * 50)
        print("VALIDATION SUMMARY")
        print("=" * 50)
        
        print(f"Pydantic validation: {'✅ PASSED' if pydantic_result else '❌ FAILED'}")
        print(f"Custom validation: {'✅ PASSED' if validation_result.is_valid else '❌ FAILED'}")
        print(f"Dependency resolution: {'✅ PASSED' if dep_result else '❌ FAILED'}")
        print(f"Performance test: {'✅ PASSED' if perf_result else '❌ FAILED'}")
        
        if all([pydantic_result, validation_result.is_valid, dep_result, perf_result]):
            print("\n🎉 ALL TESTS PASSED! The validation framework is working correctly.")
            return 0
        else:
            print("\n💥 Some tests failed. Check the output above for details.")
            return 1
            
    except Exception as e:
        print(f"❌ Test execution failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())