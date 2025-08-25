#!/usr/bin/env python3
"""
Test logging implementation across all supported languages.
"""

import os
import sys
import tempfile
import subprocess
import yaml
from pathlib import Path

# Add the source directory to path
sys.path.insert(0, '/workspace/src')

def test_language_logging(language):
    """Test CLI generation and logging analysis for a specific language."""
    print(f"\n=== Testing {language.upper()} Logging ===")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            # Create configuration
            config = {
                'package_name': f'test-{language}-logging',
                'command_name': f'test{language}',
                'display_name': f'Test {language.title()} Logging',
                'description': f'Test {language.title()} CLI with logging',
                'language': language,
                'cli_output_path': f'{temp_dir}/cli.{get_extension(language)}',
                
                'python': {'minimum_version': '3.8', 'maximum_version': '3.13'},
                'installation': {'pypi_name': f'test-{language}-logging'},
                'shell_integration': {'enabled': False, 'alias': f'test{language}'},
                'validation': {'check_api_keys': False, 'check_disk_space': False},
                
                'cli': {
                    'name': f'test{language}',
                    'tagline': f'Test {language.title()} CLI with logging',
                    'description': f'Test {language.title()} CLI logging integration',
                    'commands': {
                        'hello': {
                            'desc': 'Say hello with logging',
                            'args': [{'name': 'name', 'desc': 'Name to greet', 'type': 'string', 'required': True}]
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
                print(f"  ✗ Build failed: {result.stderr}")
                return {'language': language, 'success': False, 'error': 'Build failed'}
            
            # List all generated files
            print(f"  ✓ Build successful")
            
            all_files = []
            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    if file != 'goobits.yaml':  # Skip config file
                        file_path = os.path.join(root, file)
                        relative_path = os.path.relpath(file_path, temp_dir)
                        file_size = os.path.getsize(file_path)
                        all_files.append((relative_path, file_size))
            
            print(f"  ✓ Generated {len(all_files)} files:")
            for file_path, size in all_files:
                print(f"    {file_path} ({size} bytes)")
            
            # Look for logger-related files
            logger_files = [f for f, s in all_files if 'logger' in f.lower()]
            main_cli_files = [f for f, s in all_files if f.startswith('cli.') or 'cli.' in f]
            
            analysis = {
                'language': language,
                'success': True,
                'total_files': len(all_files),
                'logger_files': logger_files,
                'main_cli_files': main_cli_files,
                'has_separate_logger': len(logger_files) > 0
            }
            
            # Check logger files
            for logger_file in logger_files:
                file_path = os.path.join(temp_dir, logger_file)
                with open(file_path, 'r') as f:
                    content = f.read()
                
                # Language-specific logging indicators
                indicators = get_logging_indicators(language, content)
                analysis[f'logger_indicators'] = indicators
                analysis[f'logger_size'] = len(content)
                
                print(f"  ✓ Logger file: {logger_file} ({len(content)} chars)")
                print(f"    Indicators: {indicators}")
            
            # Check main CLI files for logger integration
            for cli_file in main_cli_files:
                file_path = os.path.join(temp_dir, cli_file)
                with open(file_path, 'r') as f:
                    content = f.read()
                
                integration = check_cli_logger_integration(language, content)
                analysis[f'cli_integration'] = integration
                analysis[f'cli_size'] = len(content)
                
                print(f"  ✓ CLI file: {cli_file} ({len(content)} chars)")
                print(f"    Logger integration: {integration}")
            
            return analysis
            
        except subprocess.TimeoutExpired:
            print(f"  ✗ Build timed out")
            return {'language': language, 'success': False, 'error': 'Timeout'}
        except Exception as e:
            print(f"  ✗ Test failed: {e}")
            return {'language': language, 'success': False, 'error': str(e)}

def get_extension(language):
    """Get file extension for language."""
    return {'python': 'py', 'nodejs': 'js', 'typescript': 'ts', 'rust': 'rs'}.get(language, 'txt')

def get_logging_indicators(language, content):
    """Get logging indicators for a specific language."""
    indicators = {
        'python': ['setup_logging', 'get_logger', 'StructuredFormatter', 'contextvars', 'ContextVar'],
        'nodejs': ['winston', 'AsyncLocalStorage', 'setupLogging', 'getLogger', 'structuredFormatter'],
        'typescript': ['winston', 'AsyncLocalStorage', 'LogLevel', 'LogContext', 'setupLogging'],
        'rust': ['serde_json', 'LogLevel', 'setup_logging', 'thread_local', 'pub fn']
    }
    
    language_indicators = indicators.get(language, [])
    return [ind for ind in language_indicators if ind in content]

def check_cli_logger_integration(language, content):
    """Check if CLI integrates with logger module."""
    integrations = {
        'python': ['from .logger import', 'import logger', 'setup_logging()', 'get_logger('],
        'nodejs': ['require(\'./logger\')', 'import.*logger', 'setupLogging()', 'getLogger('],
        'typescript': ['import.*logger', 'from \'./logger\'', 'setupLogging()', 'getLogger('],
        'rust': ['mod logger', 'use.*logger', 'setup_logging()', 'logger::']
    }
    
    language_integrations = integrations.get(language, [])
    return [int_check for int_check in language_integrations if int_check in content or any(part in content for part in int_check.split('.*'))]

def main():
    """Test logging implementation across all languages."""
    print("Testing Logging Implementation Across All Languages")
    print("=" * 60)
    
    languages = ['python', 'nodejs', 'typescript', 'rust']
    results = {}
    
    for language in languages:
        results[language] = test_language_logging(language)
    
    # Summary analysis
    print(f"\n{'=' * 60}")
    print("Cross-Language Logging Test Results")
    print(f"{'=' * 60}")
    
    successful_builds = sum(1 for r in results.values() if r.get('success', False))
    languages_with_logger_files = sum(1 for r in results.values() if r.get('has_separate_logger', False))
    languages_with_integration = sum(1 for r in results.values() if r.get('cli_integration', []))
    
    print(f"Successful builds: {successful_builds}/4 languages")
    print(f"Languages with logger files: {languages_with_logger_files}/4 languages") 
    print(f"Languages with CLI integration: {languages_with_integration}/4 languages")
    
    print("\nDetailed Results:")
    for language, result in results.items():
        if result.get('success'):
            logger_files = len(result.get('logger_files', []))
            logger_indicators = len(result.get('logger_indicators', []))
            integration = len(result.get('cli_integration', []))
            
            status = "✅ EXCELLENT" if logger_files > 0 and logger_indicators > 2 and integration > 0 else \
                     "⚠️  PARTIAL" if logger_files > 0 and logger_indicators > 0 else \
                     "❌ MISSING"
            
            print(f"  {language.upper()}: {status}")
            print(f"    Logger files: {logger_files}, Indicators: {logger_indicators}, Integration: {integration}")
            
            if result.get('logger_files'):
                print(f"    Logger files: {result['logger_files']}")
            if result.get('cli_integration'):
                print(f"    Integration: {result['cli_integration']}")
        else:
            error = result.get('error', 'Unknown error')[:40]
            print(f"  {language.upper()}: ❌ FAILED - {error}")
    
    # Overall assessment
    print(f"\n{'=' * 60}")
    print("Assessment:")
    
    if successful_builds == 4:
        print("✅ All languages build successfully")
    else:
        print(f"⚠️ {successful_builds}/4 languages build successfully")
    
    if languages_with_logger_files >= 3:
        print("✅ Most languages generate logger files")
    else:
        print(f"❌ Only {languages_with_logger_files}/4 languages generate logger files")
    
    if languages_with_integration >= 2:
        print("✅ Some languages have CLI-logger integration")
    elif languages_with_integration >= 1:
        print("⚠️ Limited CLI-logger integration")
    else:
        print("❌ No languages have CLI-logger integration")
    
    # Final verdict
    overall_success = (
        successful_builds >= 3 and
        languages_with_logger_files >= 2
    )
    
    if overall_success:
        print("\n🎉 Cross-language logging implementation: FUNCTIONAL")
        print("   Logger components are being generated correctly")
        if languages_with_integration < 2:
            print("   ⚠️  Integration with CLI files needs improvement")
        return True
    else:
        print("\n💥 Cross-language logging implementation: NEEDS WORK")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)