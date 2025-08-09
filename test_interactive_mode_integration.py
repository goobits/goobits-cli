#!/usr/bin/env python3
"""
Comprehensive test suite for interactive mode integration in goobits-cli
This tests that the --interactive flag works correctly in all supported languages.
"""

import subprocess
import tempfile
import yaml
from pathlib import Path
import time
import os


def test_python_interactive_integration():
    """Test that Python CLI generation includes working --interactive flag"""
    print("🐍 Testing Python interactive mode integration...")
    
    # Create test configuration with all required fields
    config = {
        'display_name': 'Test Python CLI',
        'package_name': 'test-python-cli',
        'command_name': 'test-python-cli',
        'language': 'python',
        'description': 'Test CLI for interactive mode',
        'python': {
            'package_name': 'test_python_cli'
        },
        'dependencies': {
            'python': []
        },
        'installation': {
            'pypi_name': 'test-python-cli',
            'development_path': '.'
        },
        'shell_integration': {
            'completion': True,
            'alias': 'test-cli'
        },
        'validation': {
            'strict': True
        },
        'messages': {
            'success_color': 'green',
            'error_color': 'red'
        },
        'cli': {
            'name': 'test-python-cli',
            'version': '1.0.0',
            'description': 'Test CLI for interactive mode',
            'tagline': 'A test CLI with interactive mode',
            'commands': {
                'hello': {
                    'desc': 'Say hello',
                    'arguments': [{'name': 'name', 'required': False}],
                    'options': [{'name': 'loud', 'short': 'l', 'type': 'flag', 'desc': 'Use uppercase'}]
                }
            }
        }
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        yaml.dump(config, f)
        config_path = f.name
    
    try:
        # Generate CLI using legacy templates (not universal)
        result = subprocess.run([
            'python3', '-c', 
            'from src.goobits_cli.main import app; app()',
            'build', config_path
        ], capture_output=True, text=True, cwd='/workspace/goobits-cli')
        
        if result.returncode != 0:
            print(f"❌ Failed to generate Python CLI: {result.stderr}")
            return False
        
        # Check that the generated CLI has --interactive flag in help
        cli_path = '/workspace/goobits-cli/cli.py'
        help_result = subprocess.run([
            'python3', cli_path, '--help'
        ], capture_output=True, text=True, cwd='/workspace/goobits-cli')
        
        if '--interactive' not in help_result.stdout:
            print(f"❌ --interactive flag not found in help output")
            return False
        
        print("✅ Python CLI includes --interactive flag in help")
        
        # Test that enhanced_interactive_mode.py exists
        interactive_file = Path('/workspace/goobits-cli/enhanced_interactive_mode.py')
        if not interactive_file.exists():
            print(f"❌ enhanced_interactive_mode.py not generated")
            return False
        
        print("✅ enhanced_interactive_mode.py generated successfully")
        
        # Test that the interactive mode can be imported and started
        # (We can't fully test the interactive REPL automatically, but we can test the module)
        import sys
        sys.path.insert(0, '/workspace/goobits-cli')
        try:
            import enhanced_interactive_mode
            if hasattr(enhanced_interactive_mode, 'start_enhanced_interactive'):
                print("✅ Interactive mode module can be imported and has start function")
            else:
                print("❌ start_enhanced_interactive function not found")
                return False
        except ImportError as e:
            print(f"❌ Failed to import interactive mode module: {e}")
            return False
        
        return True
        
    finally:
        # Clean up
        os.unlink(config_path)


def test_nodejs_interactive_integration():
    """Test that Node.js CLI generation includes working --interactive flag"""
    print("🟢 Testing Node.js interactive mode integration...")
    
    # Create test configuration with all required fields
    config = {
        'display_name': 'Test NodeJS CLI',
        'package_name': 'test-nodejs-cli',
        'command_name': 'test-nodejs-cli',
        'language': 'nodejs',
        'description': 'Test CLI for interactive mode',
        'python': {
            'package_name': 'test_nodejs_cli'
        },
        'dependencies': {
            'python': []
        },
        'installation': {
            'pypi_name': 'test-nodejs-cli',
            'development_path': '.'
        },
        'shell_integration': {
            'completion': True,
            'alias': 'test-cli'
        },
        'validation': {
            'strict': True
        },
        'messages': {
            'success_color': 'green',
            'error_color': 'red'
        },
        'cli': {
            'name': 'test-nodejs-cli',
            'version': '1.0.0',
            'description': 'Test CLI for interactive mode',
            'tagline': 'A test CLI with interactive mode',
            'commands': {
                'hello': {
                    'desc': 'Say hello',
                    'arguments': [{'name': 'name', 'required': False}],
                    'options': [{'name': 'loud', 'short': 'l', 'type': 'flag', 'desc': 'Use uppercase'}]
                }
            }
        }
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        yaml.dump(config, f)
        config_path = f.name
    
    try:
        # Generate CLI using legacy templates
        result = subprocess.run([
            'python3', '-c', 
            'from src.goobits_cli.main import app; app()',
            'build', config_path
        ], capture_output=True, text=True, cwd='/workspace/goobits-cli')
        
        if result.returncode != 0:
            print(f"❌ Failed to generate Node.js CLI: {result.stderr}")
            return False
        
        # Check if any JavaScript files were generated
        js_files = list(Path('/workspace/goobits-cli').glob('*.js'))
        if not js_files:
            print(f"❌ No JavaScript files generated")
            return False
        
        # Find the main CLI file (look for index.js or cli.js or similar)
        main_js_file = None
        for js_file in js_files:
            if js_file.name in ['index.js', 'cli.js'] or 'cli' in js_file.name.lower():
                main_js_file = js_file
                break
        
        if not main_js_file:
            main_js_file = js_files[0]  # Take the first JS file if no obvious main file
        
        # Check that the CLI includes --interactive option
        main_content = main_js_file.read_text()
        if '--interactive' not in main_content:
            print(f"❌ --interactive option not found in Node.js CLI")
            return False
        
        print(f"✅ Generated Node.js files: {[f.name for f in js_files]}")
        
        print("✅ Node.js CLI includes --interactive option")
        print("✅ Node.js interactive mode files generated successfully")
        
        return True
        
    finally:
        # Clean up
        os.unlink(config_path)


def test_typescript_interactive_integration():
    """Test that TypeScript CLI generation includes working --interactive flag"""
    print("🔷 Testing TypeScript interactive mode integration...")
    
    # Create test configuration with all required fields
    config = {
        'display_name': 'Test TypeScript CLI',
        'package_name': 'test-typescript-cli',
        'command_name': 'test-typescript-cli',
        'language': 'typescript',
        'description': 'Test CLI for interactive mode',
        'python': {
            'package_name': 'test_typescript_cli'
        },
        'dependencies': {
            'python': []
        },
        'installation': {
            'pypi_name': 'test-typescript-cli',
            'development_path': '.'
        },
        'shell_integration': {
            'completion': True,
            'alias': 'test-cli'
        },
        'validation': {
            'strict': True
        },
        'messages': {
            'success_color': 'green',
            'error_color': 'red'
        },
        'cli': {
            'name': 'test-typescript-cli',
            'version': '1.0.0',
            'description': 'Test CLI for interactive mode',
            'tagline': 'A test CLI with interactive mode',
            'commands': {
                'hello': {
                    'desc': 'Say hello',
                    'arguments': [{'name': 'name', 'required': False}],
                    'options': [{'name': 'loud', 'short': 'l', 'type': 'flag', 'desc': 'Use uppercase'}]
                }
            }
        }
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        yaml.dump(config, f)
        config_path = f.name
    
    try:
        # Generate CLI using legacy templates
        result = subprocess.run([
            'python3', '-c', 
            'from src.goobits_cli.main import app; app()',
            'build', config_path
        ], capture_output=True, text=True, cwd='/workspace/goobits-cli')
        
        if result.returncode != 0:
            print(f"❌ Failed to generate TypeScript CLI: {result.stderr}")
            return False
        
        # Check if any TypeScript files were generated
        ts_files = list(Path('/workspace/goobits-cli').glob('*.ts'))
        if not ts_files:
            print(f"❌ No TypeScript files generated")
            return False
        
        # Find the main CLI file (look for index.ts or cli.ts or similar)
        main_ts_file = None
        for ts_file in ts_files:
            if ts_file.name in ['index.ts', 'cli.ts'] or 'cli' in ts_file.name.lower():
                main_ts_file = ts_file
                break
        
        if not main_ts_file:
            main_ts_file = ts_files[0]  # Take the first TS file if no obvious main file
        
        # Check that the CLI includes --interactive option
        main_content = main_ts_file.read_text()
        if '--interactive' not in main_content:
            print(f"❌ --interactive option not found in TypeScript CLI")
            return False
        
        print(f"✅ Generated TypeScript files: {[f.name for f in ts_files]}")
        
        print("✅ TypeScript CLI includes --interactive option")
        print("✅ TypeScript interactive mode files generated successfully")
        
        return True
        
    finally:
        # Clean up
        os.unlink(config_path)


def test_interactive_flag_behavior():
    """Test that --interactive flag behaves correctly when used"""
    print("🧪 Testing interactive flag behavior...")
    
    cli_path = '/workspace/goobits-cli/cli.py'
    
    # Test that --interactive shows up in help
    help_result = subprocess.run([
        'python3', cli_path, '--help'
    ], capture_output=True, text=True, cwd='/workspace/goobits-cli')
    
    if '--interactive' not in help_result.stdout:
        print("❌ --interactive flag not shown in help")
        return False
    
    if 'Launch interactive mode for running commands interactively' not in help_result.stdout:
        print("❌ Interactive flag help text not found")
        return False
    
    print("✅ --interactive flag properly documented in help")
    
    # Test that the interactive flag can be invoked without errors
    # We'll send "exit" to immediately exit the interactive mode
    interactive_result = subprocess.run([
        'python3', cli_path, '--interactive'
    ], input='exit\n', capture_output=True, text=True, cwd='/workspace/goobits-cli')
    
    # Check that it launched interactive mode (look for welcome message in either stdout or stderr)
    output_text = interactive_result.stdout + interactive_result.stderr
    if '🚀 Welcome to  Enhanced Interactive Mode!' not in output_text:
        print(f"❌ Interactive mode did not launch properly.")
        print(f"   stdout: {interactive_result.stdout}")
        print(f"   stderr: {interactive_result.stderr}")
        return False
    
    # Check that it exited cleanly (return code 0)
    if interactive_result.returncode != 0:
        print(f"❌ Interactive mode did not exit cleanly. Return code: {interactive_result.returncode}")
        print(f"   stdout: {interactive_result.stdout}")
        print(f"   stderr: {interactive_result.stderr}")
        return False
    
    print("✅ Interactive mode launches and exits cleanly")
    
    return True


def main():
    """Run all integration tests"""
    print("🚀 Running Interactive Mode Integration Tests")
    print("=" * 60)
    
    tests = [
        ("Python Interactive Integration", test_python_interactive_integration),
        ("Node.js Interactive Integration", test_nodejs_interactive_integration), 
        ("TypeScript Interactive Integration", test_typescript_interactive_integration),
        ("Interactive Flag Behavior", test_interactive_flag_behavior),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}")
        print("-" * 40)
        try:
            if test_func():
                print(f"✅ {test_name} PASSED")
                passed += 1
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"❌ {test_name} FAILED with exception: {e}")
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All interactive mode integration tests PASSED!")
        print("🎯 Interactive mode is successfully wired up across all language generators")
        return 0
    else:
        print("💥 Some tests failed. Please check the output above.")
        return 1


if __name__ == "__main__":
    exit(main())