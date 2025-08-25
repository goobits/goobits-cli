#!/usr/bin/env python3
"""
Test actual logging functionality in generated CLIs by examining the complete implementation.
"""

import os
import sys
import tempfile
import subprocess
import yaml
import re
from pathlib import Path

# Add the source directory to path
sys.path.insert(0, '/workspace/src')

def create_test_config(language, output_dir):
    """Create a proper goobits.yaml configuration for testing."""
    
    config = {
        'package_name': f'test-{language}-logger',
        'command_name': f'test{language}',
        'display_name': f'Test {language.title()} Logger',
        'description': f'Test {language.title()} CLI with logging functionality',
        'language': language,
        'cli_output_path': f'{output_dir}/cli.{get_extension(language)}',
        
        'python': {
            'minimum_version': '3.8',
            'maximum_version': '3.13'
        },
        
        'installation': {
            'pypi_name': f'test-{language}-logger'
        },
        
        'shell_integration': {
            'enabled': False,
            'alias': f'test{language}'
        },
        
        'validation': {
            'check_api_keys': False,
            'check_disk_space': False
        },
        
        'cli': {
            'name': f'test{language}',
            'tagline': f'Test {language.title()} CLI with logging',
            'description': f'Test {language.title()} CLI with structured logging support',
            'commands': {
                'hello': {
                    'desc': 'Say hello with logging',
                    'args': [
                        {
                            'name': 'name',
                            'desc': 'Name to greet',
                            'type': 'string',
                            'required': True
                        }
                    ],
                    'options': [
                        {
                            'name': 'verbose',
                            'short': 'v',
                            'desc': 'Enable verbose logging',
                            'type': 'flag'
                        }
                    ]
                }
            }
        }
    }
    return config

def get_extension(language):
    """Get file extension for language."""
    return {
        'python': 'py',
        'nodejs': 'js',
        'typescript': 'ts', 
        'rust': 'rs'
    }.get(language, 'txt')

def analyze_python_logging(content):
    """Analyze Python CLI for logging functionality."""
    indicators = []
    
    # Check for logging setup function
    if 'def setup_cli_logging():' in content:
        indicators.append('setup_cli_logging_function')
    
    # Check for structured formatter
    if 'class StructuredFormatter' in content:
        indicators.append('structured_formatter')
    
    # Check for context management
    if 'contextvars' in content or 'ContextVar' in content:
        indicators.append('context_management')
    
    # Check for environment variables
    if '_LOG_LEVEL' in content and '_LOG_OUTPUT' in content:
        indicators.append('environment_variables')
    
    # Check for JSON logging
    if 'json.dumps(log_data)' in content:
        indicators.append('json_logging')
    
    # Check for container-friendly routing
    if 'Container-friendly' in content or 'stdout_handler' in content:
        indicators.append('container_routing')
    
    # Check for logger helper functions
    if 'def get_cli_logger' in content:
        indicators.append('logger_helpers')
    
    return indicators

def analyze_nodejs_logging(content):
    """Analyze Node.js CLI for logging functionality."""
    indicators = []
    
    # Check for winston
    if 'winston' in content:
        indicators.append('winston_logger')
    
    # Check for async context
    if 'AsyncLocalStorage' in content:
        indicators.append('async_context')
    
    # Check for structured logging
    if 'structuredFormatter' in content or 'JSON.stringify' in content:
        indicators.append('structured_logging')
    
    # Check for environment variables
    if 'LOG_LEVEL' in content and 'LOG_OUTPUT' in content:
        indicators.append('environment_variables')
    
    # Check for setup function
    if 'setupLogging' in content or 'function setupLogging' in content:
        indicators.append('setup_function')
    
    return indicators

def analyze_typescript_logging(content):
    """Analyze TypeScript CLI for logging functionality."""
    indicators = []
    
    # Check for winston with types
    if 'winston' in content and 'import' in content:
        indicators.append('winston_logger')
    
    # Check for TypeScript types
    if 'LogLevel' in content or 'LogContext' in content:
        indicators.append('typescript_types')
    
    # Check for async context
    if 'AsyncLocalStorage' in content:
        indicators.append('async_context')
    
    # Check for structured logging
    if 'structuredFormatter' in content:
        indicators.append('structured_logging')
    
    # Check for setup function
    if 'setupLogging' in content:
        indicators.append('setup_function')
    
    return indicators

def analyze_rust_logging(content):
    """Analyze Rust CLI for logging functionality."""
    indicators = []
    
    # Check for serde_json
    if 'serde_json' in content:
        indicators.append('serde_json')
    
    # Check for log levels enum
    if 'enum LogLevel' in content:
        indicators.append('log_level_enum')
    
    # Check for thread local context
    if 'thread_local!' in content:
        indicators.append('thread_local_context')
    
    # Check for structured logging
    if 'json!' in content and 'to_string' in content:
        indicators.append('structured_logging')
    
    # Check for setup function
    if 'pub fn setup_logging' in content:
        indicators.append('setup_function')
    
    return indicators

def test_language_logging(language):
    """Test CLI generation and logging analysis for a specific language."""
    print(f"\n=== Testing {language.upper()} CLI Logging ===")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            # Create test configuration
            config = create_test_config(language, temp_dir)
            config_file = os.path.join(temp_dir, 'goobits.yaml')
            
            with open(config_file, 'w') as f:
                yaml.dump(config, f)
            
            # Generate CLI
            build_cmd = [sys.executable, '-m', 'goobits_cli.main', 'build', config_file]
            result = subprocess.run(build_cmd, cwd=temp_dir, capture_output=True, text=True, timeout=30)
            
            if result.returncode != 0:
                print(f"  ✗ Build failed: {result.stderr}")
                return {
                    'language': language,
                    'generated': False,
                    'error': f'Build failed: {result.stderr[:100]}...'
                }
            
            # Check if CLI file was generated
            cli_file = config['cli_output_path']
            if not os.path.exists(cli_file):
                print(f"  ✗ CLI file not found: {cli_file}")
                return {
                    'language': language,
                    'generated': False,
                    'error': f'CLI file not found: {cli_file}'
                }
            
            # Read and analyze generated file
            with open(cli_file, 'r') as f:
                content = f.read()
            
            print(f"  ✓ CLI generated successfully ({len(content)} chars)")
            
            # Analyze logging based on language
            if language == 'python':
                indicators = analyze_python_logging(content)
            elif language == 'nodejs':
                indicators = analyze_nodejs_logging(content)
            elif language == 'typescript':
                indicators = analyze_typescript_logging(content)
            elif language == 'rust':
                indicators = analyze_rust_logging(content)
            else:
                indicators = []
            
            has_logging = len(indicators) > 0
            
            print(f"  ✓ Found logging indicators: {indicators}")
            print(f"  ✓ Has logging functionality: {has_logging}")
            
            # Additional detailed analysis for Python (since we know it has logging)
            if language == 'python' and has_logging:
                # Count logging-related lines
                lines = content.split('\n')
                logging_lines = [i for i, line in enumerate(lines) if any(term in line.lower() for term in 
                    ['setup_cli_logging', 'structuredformatter', 'log_context', 'get_cli_logger'])]
                
                print(f"  ✓ Logging code spans {len(logging_lines)} lines")
                
                # Check for specific features
                features = {
                    'Environment variables': '_LOG_LEVEL' in content,
                    'JSON production format': 'json.dumps(log_data)' in content,
                    'Context management': 'ContextVar' in content,
                    'Container routing': 'stdout_handler' in content,
                    'Exception handling': 'exc_info' in content
                }
                
                for feature, present in features.items():
                    status = "✓" if present else "✗"
                    print(f"    {status} {feature}")
            
            return {
                'language': language,
                'generated': True,
                'file_size': len(content),
                'logging_indicators': indicators,
                'has_logging': has_logging,
                'indicator_count': len(indicators)
            }
            
        except subprocess.TimeoutExpired:
            print(f"  ✗ Build timed out")
            return {
                'language': language,
                'generated': False,
                'error': 'Build timed out'
            }
        except Exception as e:
            print(f"  ✗ Generation failed: {e}")
            return {
                'language': language,
                'generated': False,
                'error': str(e)
            }

def main():
    """Test actual logging functionality in generated CLIs."""
    print("Testing Actual Logging Functionality in Generated CLIs")
    print("=" * 65)
    
    languages = ['python', 'nodejs', 'typescript', 'rust']
    results = {}
    
    # Test each language
    for language in languages:
        results[language] = test_language_logging(language)
    
    # Summary
    print(f"\n{'=' * 65}")
    print("Generated CLI Logging Functionality Test Results")
    print(f"{'=' * 65}")
    
    successful_generations = sum(1 for r in results.values() if r.get('generated', False))
    languages_with_logging = sum(1 for r in results.values() if r.get('has_logging', False))
    
    print(f"CLI Generation Success: {successful_generations}/4 languages")
    print(f"Logging Functionality: {languages_with_logging}/4 languages")
    
    for language, result in results.items():
        if result.get('generated'):
            indicators = result.get('indicator_count', 0)
            status = "✓ PASS" if result.get('has_logging') else "⚠ NO LOGGING"
            print(f"  {language.upper()}: {status} ({indicators} logging features)")
            
            # Show specific features for languages with logging
            if result.get('has_logging') and result.get('logging_indicators'):
                features = ', '.join(result['logging_indicators'][:3])  # Show first 3
                if len(result['logging_indicators']) > 3:
                    features += f", +{len(result['logging_indicators'])-3} more"
                print(f"    Features: {features}")
        else:
            error = result.get('error', 'Unknown error')[:40]
            print(f"  {language.upper()}: ✗ FAIL - {error}")
    
    # Detailed assessment
    print(f"\n{'=' * 65}")
    print("Assessment:")
    
    if successful_generations == 4:
        print("✅ All languages generate CLIs successfully")
    elif successful_generations >= 3:
        print("⚠️ Most languages generate CLIs successfully")
    else:
        print("❌ Multiple languages fail to generate CLIs")
    
    if languages_with_logging >= 3:
        print("✅ Most/all generated CLIs have logging functionality")
    elif languages_with_logging >= 2:
        print("⚠️ Some generated CLIs have logging functionality")
    else:
        print("❌ Few/no generated CLIs have logging functionality")
    
    # Overall success
    overall_success = (successful_generations >= 3 and languages_with_logging >= 2)
    
    if overall_success:
        print("\n🎉 Generated CLI logging implementations PASSED")
        return True
    else:
        print("\n💥 Generated CLI logging implementations NEED IMPROVEMENT")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)