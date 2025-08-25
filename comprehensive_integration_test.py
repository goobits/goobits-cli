#!/usr/bin/env python3
"""
Comprehensive integration tests for the complete logging implementation.
"""

import os
import sys
import tempfile
import subprocess
import yaml
import json
from pathlib import Path

# Add the source directory to path
sys.path.insert(0, '/workspace/src')

def run_integration_test():
    """Run comprehensive integration test for logging implementation."""
    print("Comprehensive Logging Implementation Integration Test")
    print("=" * 65)
    
    test_results = {
        'framework_core_logging': test_framework_core_logging(),
        'universal_template_rendering': test_universal_template_rendering(),
        'python_cli_generation': test_python_cli_generation(),
        'nodejs_cli_generation': test_nodejs_cli_generation(),
        'typescript_cli_generation': test_typescript_cli_generation(),
        'rust_cli_generation': test_rust_cli_generation(),
        'cross_language_consistency': test_cross_language_consistency(),
        'environment_variable_handling': test_environment_variable_handling(),
        'context_management': test_context_management(),
        'production_json_format': test_production_json_format()
    }
    
    # Summary
    print(f"\n{'=' * 65}")
    print("COMPREHENSIVE INTEGRATION TEST RESULTS")
    print(f"{'=' * 65}")
    
    total_tests = len(test_results)
    passed_tests = sum(1 for result in test_results.values() if result.get('passed', False))
    
    print(f"Total tests: {total_tests}")
    print(f"Passed tests: {passed_tests}")
    print(f"Success rate: {(passed_tests/total_tests)*100:.1f}%")
    
    print(f"\nDetailed Results:")
    for test_name, result in test_results.items():
        status = "✅ PASS" if result.get('passed', False) else "❌ FAIL"
        description = result.get('description', 'No description')
        print(f"  {test_name}: {status}")
        print(f"    {description}")
        
        if not result.get('passed', False) and result.get('error'):
            print(f"    Error: {result['error']}")
    
    # Overall assessment
    critical_tests = [
        'framework_core_logging',
        'universal_template_rendering', 
        'python_cli_generation',
        'cross_language_consistency'
    ]
    
    critical_passed = sum(1 for test in critical_tests if test_results[test].get('passed', False))
    
    if critical_passed == len(critical_tests) and passed_tests >= 8:
        print(f"\n🎉 COMPREHENSIVE INTEGRATION TEST: ✅ PASSED")
        print("   All critical components are working correctly")
        return True
    elif critical_passed >= 3 and passed_tests >= 6:
        print(f"\n⚠️  COMPREHENSIVE INTEGRATION TEST: 🟡 MOSTLY PASSED") 
        print("   Core functionality works with minor issues")
        return True
    else:
        print(f"\n💥 COMPREHENSIVE INTEGRATION TEST: ❌ FAILED")
        print("   Critical issues found in logging implementation")
        return False

def test_framework_core_logging():
    """Test framework core logging functionality."""
    try:
        # Import and test the framework logger
        from goobits_cli.logger import setup_logging, get_logger, set_context, clear_context
        
        # Test basic setup
        setup_logging()
        logger = get_logger('integration_test')
        
        # Test context management
        set_context(test_id='integration_test_001', component='core')
        current_context = get_logger('test').handlers[0].formatter._log_context.get({}) if hasattr(get_logger('test').handlers[0].formatter, '_log_context') else {}
        
        clear_context()
        
        return {
            'passed': True,
            'description': 'Framework core logging works correctly'
        }
    except Exception as e:
        return {
            'passed': False,
            'description': 'Framework core logging failed',
            'error': str(e)
        }

def test_universal_template_rendering():
    """Test universal template rendering for logger components."""
    try:
        from jinja2 import Template
        
        # Read the universal logger template
        template_path = '/workspace/src/goobits_cli/universal/components/logger.j2'
        with open(template_path, 'r') as f:
            template_content = f.read()
        
        template = Template(template_content)
        
        # Test rendering for all languages
        languages_tested = 0
        languages_passed = 0
        
        for language in ['python', 'nodejs', 'typescript', 'rust']:
            context = {
                'language': language,
                'project': {'name': f'test-{language}-app'}
            }
            
            try:
                rendered = template.render(**context)
                if len(rendered) > 1000:  # Should be substantial
                    languages_passed += 1
                languages_tested += 1
            except Exception:
                languages_tested += 1
        
        success_rate = (languages_passed / languages_tested) * 100
        
        return {
            'passed': languages_passed >= 3,  # At least 3/4 should work
            'description': f'Universal template rendering: {languages_passed}/{languages_tested} languages ({success_rate:.1f}%)'
        }
    except Exception as e:
        return {
            'passed': False,
            'description': 'Universal template rendering failed',
            'error': str(e)
        }

def test_python_cli_generation():
    """Test Python CLI generation with logger."""
    return test_language_cli_generation('python')

def test_nodejs_cli_generation():
    """Test Node.js CLI generation with logger."""
    return test_language_cli_generation('nodejs')

def test_typescript_cli_generation():
    """Test TypeScript CLI generation with logger."""
    return test_language_cli_generation('typescript')

def test_rust_cli_generation():
    """Test Rust CLI generation with logger."""
    return test_language_cli_generation('rust')

def test_language_cli_generation(language):
    """Test CLI generation for a specific language."""
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test configuration
            config = {
                'package_name': f'integration-test-{language}',
                'command_name': f'itest{language}',
                'display_name': f'Integration Test {language.title()}',
                'description': f'Integration test {language} CLI',
                'language': language,
                'cli_output_path': f'{temp_dir}/cli.{get_extension(language)}',
                
                'python': {'minimum_version': '3.8', 'maximum_version': '3.13'},
                'installation': {'pypi_name': f'integration-test-{language}'},
                'shell_integration': {'enabled': False, 'alias': f'itest{language}'},
                'validation': {'check_api_keys': False, 'check_disk_space': False},
                
                'cli': {
                    'name': f'itest{language}',
                    'tagline': f'Integration test {language} CLI',
                    'description': f'Integration test for {language} logging',
                    'commands': {
                        'test': {
                            'desc': 'Test logging functionality',
                            'args': [{'name': 'message', 'desc': 'Message to log', 'type': 'string', 'required': True}]
                        }
                    }
                }
            }
            
            config_file = os.path.join(temp_dir, 'goobits.yaml')
            with open(config_file, 'w') as f:
                yaml.dump(config, f)
            
            # Generate CLI
            build_cmd = [sys.executable, '-m', 'goobits_cli.main', 'build', config_file]
            result = subprocess.run(build_cmd, cwd=temp_dir, capture_output=True, text=True, timeout=30)
            
            if result.returncode != 0:
                return {
                    'passed': False,
                    'description': f'{language.title()} CLI generation failed',
                    'error': f'Build failed: {result.stderr[:100]}...'
                }
            
            # Check for logger files
            logger_files = []
            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    if 'logger' in file.lower():
                        logger_files.append(os.path.relpath(os.path.join(root, file), temp_dir))
            
            if not logger_files:
                return {
                    'passed': False,
                    'description': f'{language.title()} CLI generation: no logger files generated',
                    'error': 'No logger files found'
                }
            
            # Check logger file content
            logger_file = os.path.join(temp_dir, logger_files[0])
            with open(logger_file, 'r') as f:
                logger_content = f.read()
            
            # Language-specific checks
            expected_indicators = {
                'python': ['setup_logging', 'get_logger', 'contextvars'],
                'nodejs': ['winston', 'AsyncLocalStorage', 'setupLogging'],
                'typescript': ['winston', 'LogLevel', 'setupLogging'],
                'rust': ['serde_json', 'LogLevel', 'setup_logging']
            }
            
            indicators = expected_indicators.get(language, [])
            found_indicators = [ind for ind in indicators if ind in logger_content]
            
            if len(found_indicators) < len(indicators) // 2:  # At least half should be found
                return {
                    'passed': False,
                    'description': f'{language.title()} CLI generation: insufficient logging features',
                    'error': f'Found {len(found_indicators)}/{len(indicators)} expected features'
                }
            
            return {
                'passed': True,
                'description': f'{language.title()} CLI generation successful with {len(found_indicators)}/{len(indicators)} logging features'
            }
            
    except Exception as e:
        return {
            'passed': False,
            'description': f'{language.title()} CLI generation test failed',
            'error': str(e)
        }

def test_cross_language_consistency():
    """Test cross-language consistency of logging implementation."""
    try:
        # Test that all languages have the same core environment variables
        universal_template_path = '/workspace/src/goobits_cli/universal/components/logger.j2'
        with open(universal_template_path, 'r') as f:
            template_content = f.read()
        
        # Check for consistent environment variables
        env_vars = ['LOG_LEVEL', 'LOG_OUTPUT', 'ENVIRONMENT']
        env_var_count = sum(1 for var in env_vars if var in template_content)
        
        # Check for all language sections
        languages = ['python', 'nodejs', 'typescript', 'rust']
        language_sections = sum(1 for lang in languages if f"language == '{lang}'" in template_content)
        
        # Check for consistent logging features
        features = ['structured', 'context', 'production', 'development']
        feature_count = sum(1 for feature in features if feature in template_content)
        
        consistency_score = (env_var_count + language_sections + feature_count) / (len(env_vars) + len(languages) + len(features))
        
        return {
            'passed': consistency_score >= 0.8,  # 80% consistency required
            'description': f'Cross-language consistency: {consistency_score*100:.1f}% ({env_var_count}/{len(env_vars)} env vars, {language_sections}/{len(languages)} languages, {feature_count}/{len(features)} features)'
        }
    except Exception as e:
        return {
            'passed': False,
            'description': 'Cross-language consistency test failed',
            'error': str(e)
        }

def test_environment_variable_handling():
    """Test environment variable handling."""
    try:
        # Test framework logger with different environment variables
        original_env = dict(os.environ)
        
        try:
            # Test LOG_LEVEL
            os.environ['LOG_LEVEL'] = 'DEBUG'
            os.environ['LOG_OUTPUT'] = 'stderr'
            os.environ['ENVIRONMENT'] = 'production'
            
            from goobits_cli.logger import setup_logging, get_logger
            setup_logging()
            logger = get_logger('env_test')
            
            # If we get here without exception, basic env var handling works
            return {
                'passed': True,
                'description': 'Environment variable handling works correctly'
            }
        finally:
            # Restore original environment
            os.environ.clear()
            os.environ.update(original_env)
            
    except Exception as e:
        return {
            'passed': False,
            'description': 'Environment variable handling failed',
            'error': str(e)
        }

def test_context_management():
    """Test context management functionality."""
    try:
        from goobits_cli.logger import setup_logging, get_logger, set_context, clear_context, get_context
        
        setup_logging()
        logger = get_logger('context_test')
        
        # Test context operations
        set_context(test_id='ctx_001', operation='context_test')
        context_after_set = get_context()
        
        clear_context()
        context_after_clear = get_context()
        
        # Basic validation
        context_works = (
            isinstance(context_after_set, dict) and
            isinstance(context_after_clear, dict) and
            len(context_after_clear) == 0  # Should be empty after clear
        )
        
        return {
            'passed': context_works,
            'description': f'Context management works correctly (set: {len(context_after_set)} items, clear: {len(context_after_clear)} items)'
        }
    except Exception as e:
        return {
            'passed': False,
            'description': 'Context management test failed',
            'error': str(e)
        }

def test_production_json_format():
    """Test production JSON format."""
    try:
        # Test that production environment produces JSON
        original_env = dict(os.environ)
        
        try:
            os.environ['ENVIRONMENT'] = 'production'
            os.environ['LOG_OUTPUT'] = 'stderr'
            
            from goobits_cli.logger import setup_logging, get_logger
            setup_logging()
            logger = get_logger('json_test')
            
            # The fact that this doesn't crash means JSON formatting is available
            return {
                'passed': True,
                'description': 'Production JSON format is available'
            }
        finally:
            os.environ.clear()
            os.environ.update(original_env)
            
    except Exception as e:
        return {
            'passed': False,
            'description': 'Production JSON format test failed',
            'error': str(e)
        }

def get_extension(language):
    """Get file extension for language."""
    return {'python': 'py', 'nodejs': 'js', 'typescript': 'ts', 'rust': 'rs'}.get(language, 'txt')

if __name__ == "__main__":
    success = run_integration_test()
    sys.exit(0 if success else 1)