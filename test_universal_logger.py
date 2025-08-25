#!/usr/bin/env python3
"""
Test script for universal template system logger component integration.
"""

import os
import sys
import tempfile
import shutil
import yaml
from pathlib import Path

# Add the source directory to path
sys.path.insert(0, '/workspace/src')

def create_test_config(language, output_dir):
    """Create a test goobits.yaml configuration."""
    config = {
        'project': {
            'name': f'test-{language}-logger',
            'version': '1.0.0',
            'description': f'Test {language.title()} CLI with logging'
        },
        'language': language,
        'cli_output_path': f'{output_dir}/cli.{get_extension(language)}',
        'installation': {
            'pip_install_name': f'test-{language}-logger'
        },
        'cli': {
            'name': f'test-{language}-cli',
            'description': f'Test {language.title()} CLI with logging',
            'commands': {
                'hello': {
                    'description': 'Say hello with logging',
                    'arguments': [
                        {
                            'name': 'name',
                            'description': 'Name to greet',
                            'required': True
                        }
                    ],
                    'options': [
                        {
                            'name': 'verbose',
                            'short': 'v',
                            'description': 'Enable verbose logging',
                            'type': 'flag'
                        }
                    ]
                },
                'test': {
                    'description': 'Test logging functionality',
                    'commands': {
                        'context': {
                            'description': 'Test context management',
                            'options': [
                                {
                                    'name': 'operation-id',
                                    'description': 'Operation ID for context',
                                    'type': 'string'
                                }
                            ]
                        }
                    }
                }
            }
        }
    }
    return config

def get_extension(language):
    """Get file extension for language."""
    extensions = {
        'python': 'py',
        'nodejs': 'js', 
        'typescript': 'ts',
        'rust': 'rs'
    }
    return extensions.get(language, 'txt')

def test_universal_template_generation():
    """Test generating CLIs with universal templates for all languages."""
    print("=== Testing Universal Template Logger Generation ===")
    
    languages = ['python', 'nodejs', 'typescript', 'rust']
    results = {}
    
    for language in languages:
        print(f"\nTesting {language.upper()} CLI generation...")
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test configuration
            config = create_test_config(language, temp_dir)
            config_file = os.path.join(temp_dir, 'goobits.yaml')
            
            with open(config_file, 'w') as f:
                yaml.dump(config, f)
            
            try:
                # Import and use the universal template engine
                from goobits_cli.universal.template_engine import UniversalTemplateEngine
                from goobits_cli.schemas import GoobitsConfigSchema
                
                # Load and validate config
                with open(config_file, 'r') as f:
                    config_data = yaml.safe_load(f)
                
                validated_config = GoobitsConfigSchema(**config_data)
                
                # Generate CLI using universal templates
                engine = UniversalTemplateEngine()
                output_files = engine.generate_cli(validated_config)
                
                # Check that CLI file was generated
                cli_file = config['cli_output_path']
                if os.path.exists(cli_file):
                    with open(cli_file, 'r') as f:
                        content = f.read()
                    
                    # Check for logger-specific content
                    logger_indicators = {
                        'python': ['import logging', 'setup_logging', 'get_logger', 'contextvars'],
                        'nodejs': ['winston', 'AsyncLocalStorage', 'setupLogging', 'getLogger'],
                        'typescript': ['winston', 'AsyncLocalStorage', 'LogLevel', 'LogContext'],
                        'rust': ['serde_json', 'setup_logging', 'get_logger', 'LogLevel', 'thread_local']
                    }
                    
                    found_indicators = []
                    for indicator in logger_indicators.get(language, []):
                        if indicator in content:
                            found_indicators.append(indicator)
                    
                    results[language] = {
                        'generated': True,
                        'file_size': len(content),
                        'logger_indicators': found_indicators,
                        'has_logging': len(found_indicators) > 0
                    }
                    
                    print(f"  ✓ Generated {cli_file} ({len(content)} chars)")
                    print(f"  ✓ Found logging indicators: {found_indicators}")
                else:
                    results[language] = {
                        'generated': False,
                        'error': 'CLI file not found'
                    }
                    print(f"  ✗ CLI file not generated: {cli_file}")
                
            except Exception as e:
                results[language] = {
                    'generated': False,
                    'error': str(e)
                }
                print(f"  ✗ Generation failed: {e}")
                import traceback
                traceback.print_exc()
    
    return results

def test_component_registry():
    """Test that logger components are properly registered."""
    print("\n=== Testing Universal Component Registry ===")
    
    try:
        from goobits_cli.universal.components.registry import ComponentRegistry
        
        registry = ComponentRegistry()
        
        # Check if logger component exists
        if registry.has_component('logger'):
            print("✓ Logger component is registered")
            
            # Test rendering for each language
            languages = ['python', 'nodejs', 'typescript', 'rust']
            
            for language in languages:
                try:
                    # Create a minimal project config
                    project_config = {
                        'name': f'test-{language}',
                        'version': '1.0.0'
                    }
                    
                    rendered = registry.render_component('logger', language, {
                        'project': project_config
                    })
                    
                    if rendered and len(rendered) > 100:  # Should be substantial
                        print(f"  ✓ {language.upper()} logger component renders ({len(rendered)} chars)")
                    else:
                        print(f"  ✗ {language.upper()} logger component render failed or too small")
                        
                except Exception as e:
                    print(f"  ✗ {language.upper()} logger component render error: {e}")
            
            return True
        else:
            print("✗ Logger component is NOT registered")
            return False
            
    except Exception as e:
        print(f"✗ Component registry test failed: {e}")
        return False

def main():
    """Run all universal template system logger tests."""
    print("Testing Universal Template System Logger Integration")
    print("=" * 60)
    
    # Test 1: Universal template generation
    generation_results = test_universal_template_generation()
    
    # Test 2: Component registry
    registry_success = test_component_registry()
    
    # Summary
    print(f"\n{'=' * 60}")
    print("Universal Template System Logger Test Results")
    print(f"{'=' * 60}")
    
    # Generation results
    total_languages = len(generation_results)
    successful_generations = sum(1 for r in generation_results.values() if r.get('generated', False))
    languages_with_logging = sum(1 for r in generation_results.values() if r.get('has_logging', False))
    
    print(f"CLI Generation: {successful_generations}/{total_languages} languages successful")
    print(f"Logger Integration: {languages_with_logging}/{total_languages} languages have logging")
    print(f"Component Registry: {'✓ PASS' if registry_success else '✗ FAIL'}")
    
    # Detailed results
    for language, result in generation_results.items():
        if result.get('generated'):
            indicators = len(result.get('logger_indicators', []))
            print(f"  {language.upper()}: ✓ Generated with {indicators} logging indicators")
        else:
            error = result.get('error', 'Unknown error')
            print(f"  {language.upper()}: ✗ Failed - {error}")
    
    # Overall assessment
    overall_success = (successful_generations == total_languages and 
                      languages_with_logging >= 3 and  # At least 3 out of 4 should work
                      registry_success)
    
    if overall_success:
        print("\n✅ Universal template system logger integration PASSED")
        return True
    else:
        print("\n❌ Universal template system logger integration FAILED")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)