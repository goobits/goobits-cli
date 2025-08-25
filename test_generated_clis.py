#!/usr/bin/env python3
"""
Test script for generated CLI logging implementations across all languages.
"""

import os
import sys
import tempfile
import subprocess
import shutil
import yaml
import time
from pathlib import Path

# Add the source directory to path
sys.path.insert(0, '/workspace/src')

def create_test_config(language, output_dir):
    """Create a proper goobits.yaml configuration for testing."""
    
    # Base configuration matching the actual schema
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
        
        'dependencies': {
            'required': [],
            'optional': []
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
                },
                'test': {
                    'desc': 'Test logging functionality',
                    'commands': {
                        'context': {
                            'desc': 'Test context management',
                            'options': [
                                {
                                    'name': 'operation-id',
                                    'desc': 'Operation ID for context',
                                    'type': 'string'
                                }
                            ]
                        },
                        'levels': {
                            'desc': 'Test different log levels'
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

def create_hooks_file(language, output_dir):
    """Create hooks file with logging tests for each language."""
    
    hooks_content = {
        'python': '''"""
Test hooks for Python CLI with logging.
"""

import os
import sys
from typing import Any, Dict

# Import the logger from the generated CLI
try:
    from .logger import setup_logging, get_logger, set_context, clear_context
except ImportError:
    # Fallback if relative import fails
    try:
        import logging
        setup_logging = lambda: None
        get_logger = lambda name: logging.getLogger(name)
        set_context = lambda **kwargs: None
        clear_context = lambda: None
    except:
        pass

def on_hello(name: str, verbose: bool = False, **kwargs: Any):
    """Handle hello command with logging."""
    
    # Set up logging
    if verbose:
        os.environ['LOG_LEVEL'] = 'DEBUG'
    
    setup_logging()
    logger = get_logger(__name__)
    
    # Set context
    set_context(operation='hello', user_input=name)
    
    logger.info(f"Greeting user: {name}")
    if verbose:
        logger.debug("Verbose mode enabled")
    
    print(f"Hello, {name}!")

def on_test_context(operation_id: str = None, **kwargs: Any):
    """Test context management."""
    
    setup_logging() 
    logger = get_logger(__name__)
    
    if operation_id:
        set_context(operation_id=operation_id, test_type='context')
        logger.info("Context set with operation ID")
    else:
        set_context(test_type='context')
        logger.info("Context set without operation ID")
    
    logger.warning("Testing context management")
    clear_context()
    logger.info("Context cleared")
    
    print("Context management test completed")

def on_test_levels(**kwargs: Any):
    """Test different log levels."""
    
    setup_logging()
    logger = get_logger(__name__)
    
    set_context(test_type='levels')
    
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message") 
    logger.error("This is an error message")
    
    print("Log levels test completed")
''',

        'nodejs': '''/**
 * Test hooks for Node.js CLI with logging.
 */

const { setupLogging, getLogger, setContext, clearContext } = require('./logger');

async function onHello(args) {
    const { name, verbose } = args;
    
    // Set up logging
    if (verbose) {
        process.env.LOG_LEVEL = 'debug';
    }
    
    setupLogging();
    const logger = getLogger('hello');
    
    // Set context and run operation
    await setContext({ operation: 'hello', userInput: name }, async () => {
        logger.info(`Greeting user: ${name}`);
        if (verbose) {
            logger.debug('Verbose mode enabled');
        }
        
        console.log(`Hello, ${name}!`);
    });
}

async function onTestContext(args) {
    const { operationId } = args;
    
    setupLogging();
    const logger = getLogger('test-context');
    
    const context = operationId 
        ? { operationId, testType: 'context' }
        : { testType: 'context' };
    
    await setContext(context, async () => {
        if (operationId) {
            logger.info('Context set with operation ID');
        } else {
            logger.info('Context set without operation ID');
        }
        
        logger.warn('Testing context management');
    });
    
    clearContext();
    logger.info('Context cleared');
    
    console.log('Context management test completed');
}

async function onTestLevels(args) {
    setupLogging();
    const logger = getLogger('test-levels');
    
    await setContext({ testType: 'levels' }, async () => {
        logger.debug('This is a debug message');
        logger.info('This is an info message');
        logger.warn('This is a warning message');
        logger.error('This is an error message');
    });
    
    console.log('Log levels test completed');
}

module.exports = {
    onHello,
    onTestContext,
    onTestLevels
};
''',

        'typescript': '''/**
 * Test hooks for TypeScript CLI with logging.
 */

import { setupLogging, getLogger, setContext, clearContext, LogLevel } from './logger';

interface HelloArgs {
    name: string;
    verbose?: boolean;
}

interface TestContextArgs {
    operationId?: string;
}

export async function onHello(args: HelloArgs): Promise<void> {
    const { name, verbose } = args;
    
    // Set up logging
    if (verbose) {
        process.env.LOG_LEVEL = 'debug';
    }
    
    setupLogging();
    const logger = getLogger('hello');
    
    // Set context and run operation
    await setContext({ operation: 'hello', userInput: name }, async () => {
        logger.info(`Greeting user: ${name}`);
        if (verbose) {
            logger.debug('Verbose mode enabled');
        }
        
        console.log(`Hello, ${name}!`);
    });
}

export async function onTestContext(args: TestContextArgs): Promise<void> {
    const { operationId } = args;
    
    setupLogging();
    const logger = getLogger('test-context');
    
    const context = operationId 
        ? { operationId, testType: 'context' }
        : { testType: 'context' };
    
    await setContext(context, async () => {
        if (operationId) {
            logger.info('Context set with operation ID');
        } else {
            logger.info('Context set without operation ID');
        }
        
        logger.warn('Testing context management');
    });
    
    clearContext();
    logger.info('Context cleared');
    
    console.log('Context management test completed');
}

export async function onTestLevels(): Promise<void> {
    setupLogging();
    const logger = getLogger('test-levels');
    
    await setContext({ testType: 'levels' }, async () => {
        logger.debug('This is a debug message');
        logger.info('This is an info message');
        logger.warn('This is a warning message');
        logger.error('This is an error message');
    });
    
    console.log('Log levels test completed');
}
''',

        'rust': '''//! Test hooks for Rust CLI with logging.

use std::collections::HashMap;
use serde_json::json;
use clap::ArgMatches;
use anyhow::Result;

// Import logger functions
use crate::logger::{setup_logging, info, debug, warn, error, set_context, clear_context};

pub fn on_hello(matches: &ArgMatches) -> Result<()> {
    let name = matches.get_one::<String>("name").unwrap();
    let verbose = matches.get_flag("verbose");
    
    // Set up logging
    if verbose {
        std::env::set_var("LOG_LEVEL", "debug");
    }
    
    setup_logging()?;
    
    // Set context
    let mut context = HashMap::new();
    context.insert("operation".to_string(), json!("hello"));
    context.insert("user_input".to_string(), json!(name));
    set_context(context);
    
    info("hello", &format!("Greeting user: {}", name), None);
    if verbose {
        debug("hello", "Verbose mode enabled", None);
    }
    
    println!("Hello, {}!", name);
    Ok(())
}

pub fn on_test_context(matches: &ArgMatches) -> Result<()> {
    let operation_id = matches.get_one::<String>("operation-id");
    
    setup_logging()?;
    
    let mut context = HashMap::new();
    context.insert("test_type".to_string(), json!("context"));
    
    if let Some(op_id) = operation_id {
        context.insert("operation_id".to_string(), json!(op_id));
        set_context(context);
        info("test-context", "Context set with operation ID", None);
    } else {
        set_context(context);
        info("test-context", "Context set without operation ID", None);
    }
    
    warn("test-context", "Testing context management", None);
    clear_context();
    info("test-context", "Context cleared", None);
    
    println!("Context management test completed");
    Ok(())
}

pub fn on_test_levels(_matches: &ArgMatches) -> Result<()> {
    setup_logging()?;
    
    let mut context = HashMap::new();
    context.insert("test_type".to_string(), json!("levels"));
    set_context(context);
    
    debug("test-levels", "This is a debug message", None);
    info("test-levels", "This is an info message", None);
    warn("test-levels", "This is a warning message", None);
    error("test-levels", "This is an error message", None);
    
    println!("Log levels test completed");
    Ok(())
}
'''
    }
    
    hooks_file = os.path.join(output_dir, f'hooks.{get_extension(language)}')
    with open(hooks_file, 'w') as f:
        f.write(hooks_content[language])
    
    return hooks_file

def test_cli_generation(language):
    """Test CLI generation for a specific language."""
    print(f"\n=== Testing {language.upper()} CLI Generation ===")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            # Create test configuration
            config = create_test_config(language, temp_dir)
            config_file = os.path.join(temp_dir, 'goobits.yaml')
            
            with open(config_file, 'w') as f:
                yaml.dump(config, f)
            
            # Create hooks file
            create_hooks_file(language, temp_dir)
            
            # Generate CLI using the framework
            build_cmd = [sys.executable, '-m', 'goobits_cli.main', 'build', config_file]
            
            # Run build in the temp directory
            result = subprocess.run(
                build_cmd, 
                cwd=temp_dir,
                capture_output=True, 
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                print(f"  ✗ Build failed: {result.stderr}")
                return {
                    'generated': False,
                    'error': f'Build failed: {result.stderr}',
                    'stdout': result.stdout
                }
            
            # Check if CLI file was generated
            cli_file = config['cli_output_path']
            if os.path.exists(cli_file):
                with open(cli_file, 'r') as f:
                    content = f.read()
                
                # Check for logger-specific content
                logger_indicators = {
                    'python': ['import logging', 'setup_logging', 'get_logger'],
                    'nodejs': ['winston', 'AsyncLocalStorage', 'setupLogging'],
                    'typescript': ['winston', 'AsyncLocalStorage', 'LogLevel'],
                    'rust': ['serde_json', 'setup_logging', 'LogLevel']
                }
                
                found_indicators = []
                for indicator in logger_indicators.get(language, []):
                    if indicator in content:
                        found_indicators.append(indicator)
                
                print(f"  ✓ CLI generated successfully ({len(content)} chars)")
                print(f"  ✓ Found logging indicators: {found_indicators}")
                
                return {
                    'generated': True,
                    'file_size': len(content),
                    'logger_indicators': found_indicators,
                    'has_logging': len(found_indicators) > 0,
                    'cli_file': cli_file,
                    'temp_dir': temp_dir  # Keep reference
                }
            else:
                print(f"  ✗ CLI file not found: {cli_file}")
                return {
                    'generated': False,
                    'error': f'CLI file not found: {cli_file}'
                }
                
        except subprocess.TimeoutExpired:
            print(f"  ✗ Build timed out")
            return {
                'generated': False,
                'error': 'Build timed out'
            }
        except Exception as e:
            print(f"  ✗ Generation failed: {e}")
            return {
                'generated': False,
                'error': str(e)
            }

def test_python_cli():
    """Test Python CLI logging functionality."""
    print("\n=== Testing Python CLI Logging ===")
    
    result = test_cli_generation('python')
    
    if not result.get('generated'):
        print(f"  ✗ Python CLI generation failed: {result.get('error')}")
        return result
    
    # Test that the generated CLI has proper logging
    if result.get('has_logging'):
        print("  ✓ Python CLI has logging functionality")
    else:
        print("  ✗ Python CLI missing logging functionality")
    
    result['language'] = 'python'
    return result

def test_nodejs_cli():
    """Test Node.js CLI logging functionality."""
    print("\n=== Testing Node.js CLI Logging ===")
    
    result = test_cli_generation('nodejs')
    
    if not result.get('generated'):
        print(f"  ✗ Node.js CLI generation failed: {result.get('error')}")
        return result
    
    # Test that the generated CLI has proper logging
    if result.get('has_logging'):
        print("  ✓ Node.js CLI has logging functionality")
    else:
        print("  ✗ Node.js CLI missing logging functionality")
    
    result['language'] = 'nodejs'
    return result

def test_typescript_cli():
    """Test TypeScript CLI logging functionality."""
    print("\n=== Testing TypeScript CLI Logging ===")
    
    result = test_cli_generation('typescript')
    
    if not result.get('generated'):
        print(f"  ✗ TypeScript CLI generation failed: {result.get('error')}")
        return result
    
    # Test that the generated CLI has proper logging
    if result.get('has_logging'):
        print("  ✓ TypeScript CLI has logging functionality")
    else:
        print("  ✗ TypeScript CLI missing logging functionality")
    
    result['language'] = 'typescript'
    return result

def test_rust_cli():
    """Test Rust CLI logging functionality."""
    print("\n=== Testing Rust CLI Logging ===")
    
    result = test_cli_generation('rust')
    
    if not result.get('generated'):
        print(f"  ✗ Rust CLI generation failed: {result.get('error')}")
        return result
    
    # Test that the generated CLI has proper logging
    if result.get('has_logging'):
        print("  ✓ Rust CLI has logging functionality")
    else:
        print("  ✗ Rust CLI missing logging functionality")
    
    result['language'] = 'rust'
    return result

def main():
    """Run all language-specific CLI logging tests."""
    print("Testing Generated CLI Logging Implementations")
    print("=" * 60)
    
    # Test each language
    results = {
        'python': test_python_cli(),
        'nodejs': test_nodejs_cli(), 
        'typescript': test_typescript_cli(),
        'rust': test_rust_cli()
    }
    
    # Summary
    print(f"\n{'=' * 60}")
    print("Generated CLI Logging Test Results")
    print(f"{'=' * 60}")
    
    successful_generations = sum(1 for r in results.values() if r.get('generated', False))
    languages_with_logging = sum(1 for r in results.values() if r.get('has_logging', False))
    
    print(f"CLI Generation Success: {successful_generations}/4 languages")
    print(f"Logging Integration: {languages_with_logging}/4 languages")
    
    for language, result in results.items():
        if result.get('generated'):
            indicators = len(result.get('logger_indicators', []))
            status = "✓ PASS" if result.get('has_logging') else "⚠ NO LOGGING"
            print(f"  {language.upper()}: {status} ({indicators} logging indicators)")
        else:
            error = result.get('error', 'Unknown error')[:50]
            print(f"  {language.upper()}: ✗ FAIL - {error}")
    
    # Overall success criteria
    overall_success = (
        successful_generations >= 3 and  # At least 3/4 should generate
        languages_with_logging >= 3      # At least 3/4 should have logging
    )
    
    if overall_success:
        print("\n✅ Generated CLI logging implementations PASSED")
        return True
    else:
        print("\n❌ Generated CLI logging implementations FAILED")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)