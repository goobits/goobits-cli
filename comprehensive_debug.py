#!/usr/bin/env python3
"""Comprehensive debug analysis of all failing tests"""

import os
import subprocess
import tempfile
import shutil
import yaml
from pathlib import Path

def generate_and_test_all_languages():
    """Generate CLIs for all languages and test failing scenarios"""
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Language configurations
        languages = {
            'python': {
                'config_source': '/workspace/examples/basic-demos/python-example.yaml',
                'hooks_source': '/workspace/examples/basic-demos/app_hooks.py',
                'cli_file': 'cli.py',
                'run_cmd': lambda path, args: ["python3", str(path)] + args
            },
            'nodejs': {
                'config_source': '/workspace/examples/basic-demos/nodejs-example.yaml', 
                'hooks_source': '/workspace/examples/basic-demos/hooks.js',
                'cli_file': 'cli.js',
                'run_cmd': lambda path, args: ["node", str(path)] + args
            },
            'typescript': {
                'config_source': '/workspace/examples/basic-demos/typescript-example.yaml',
                'hooks_source': '/workspace/examples/basic-demos/hooks.js',  # Uses same hooks
                'cli_file': 'cli.ts', 
                'run_cmd': lambda path, args: ["npx", "ts-node", str(path)] + args
            },
            'rust': {
                'config_source': '/workspace/examples/basic-demos/rust-example.yaml',
                'hooks_source': '/workspace/examples/basic-demos/hooks.rs',
                'cli_file': 'main.rs',  # Rust compiles to binary
                'run_cmd': lambda path, args: [str(path)] + args  # Direct binary execution
            }
        }
        
        results = {}
        
        for lang, config in languages.items():
            print(f"\n{'='*50}")
            print(f"TESTING {lang.upper()}")
            print(f"{'='*50}")
            
            try:
                # Setup directories
                lang_dir = temp_path / lang
                lang_dir.mkdir()
                
                # Copy and modify config
                with open(config['config_source']) as f:
                    config_data = yaml.safe_load(f)
                
                config_data['language'] = lang
                config_data['cli_output_path'] = config['cli_file']
                
                config_file = temp_path / f"config-{lang}.yaml"
                with open(config_file, 'w') as f:
                    yaml.safe_dump(config_data, f)
                
                # Copy hooks file
                hooks_dest = lang_dir / Path(config['hooks_source']).name
                shutil.copy(config['hooks_source'], hooks_dest)
                
                # Generate CLI
                cmd = [
                    "python3", "-m", "goobits_cli.main", "build",
                    str(config_file), "-o", str(lang_dir)
                ]
                
                result = subprocess.run(cmd, capture_output=True, text=True, cwd="/workspace")
                if result.returncode != 0:
                    print(f"ERROR: Failed to generate {lang} CLI")
                    print(f"STDERR: {result.stderr}")
                    continue
                
                cli_path = lang_dir / config['cli_file']
                
                # For Rust, we need to compile first
                if lang == 'rust':
                    # Check if Cargo.toml exists and compile
                    cargo_file = lang_dir / "Cargo.toml"
                    if cargo_file.exists():
                        compile_cmd = ["cargo", "build", "--release"]
                        compile_result = subprocess.run(compile_cmd, capture_output=True, text=True, cwd=lang_dir)
                        if compile_result.returncode == 0:
                            cli_path = lang_dir / "target" / "release" / config_data.get('command_name', 'demo_rust')
                        else:
                            print(f"Rust compilation failed: {compile_result.stderr}")
                            continue
                
                # Test the failing scenarios
                test_results = {}
                
                # Test 1: help_command - looking for "CLI demonstration"
                print(f"\n--- help_command ---")
                result = subprocess.run(config['run_cmd'](cli_path, ["--help"]), 
                                      capture_output=True, text=True, cwd=lang_dir)
                has_cli_demo = "CLI demonstration" in result.stdout
                print(f"Exit code: {result.returncode}")
                print(f"Contains 'CLI demonstration': {has_cli_demo}")
                if not has_cli_demo:
                    print("STDOUT excerpt:", repr(result.stdout[:200]))
                test_results['help_command'] = has_cli_demo
                
                # Test 2: greet_basic - looking for "Hello, Alice!"
                print(f"\n--- greet_basic ---")
                result = subprocess.run(config['run_cmd'](cli_path, ["greet", "Alice"]), 
                                      capture_output=True, text=True, cwd=lang_dir)
                has_hello_alice = "Hello, Alice!" in result.stdout
                print(f"Exit code: {result.returncode}")
                print(f"Contains 'Hello, Alice!': {has_hello_alice}")
                print(f"STDOUT: {repr(result.stdout)}")
                test_results['greet_basic'] = has_hello_alice
                
                # Test 3: greet_with_enthusiastic_flag - looking for "Hello, Frank!"
                print(f"\n--- greet_with_enthusiastic_flag ---")
                result = subprocess.run(config['run_cmd'](cli_path, ["greet", "Frank"]), 
                                      capture_output=True, text=True, cwd=lang_dir)
                has_hello_frank = "Hello, Frank!" in result.stdout
                print(f"Exit code: {result.returncode}")
                print(f"Contains 'Hello, Frank!': {has_hello_frank}")
                print(f"STDOUT: {repr(result.stdout)}")
                test_results['greet_with_enthusiastic_flag'] = has_hello_frank
                
                # Test 4: info_with_format_option - looking for "{"
                print(f"\n--- info_with_format_option ---")
                result = subprocess.run(config['run_cmd'](cli_path, ["info", "--format", "json"]), 
                                      capture_output=True, text=True, cwd=lang_dir)
                has_json_brace = "{" in result.stdout
                print(f"Exit code: {result.returncode}")
                print(f"Contains '{{': {has_json_brace}")
                print(f"STDOUT: {repr(result.stdout)}")
                test_results['info_with_format_option'] = has_json_brace
                
                # Test 5: greet_missing_argument - looking for "error"
                print(f"\n--- greet_missing_argument ---")
                result = subprocess.run(config['run_cmd'](cli_path, ["greet"]), 
                                      capture_output=True, text=True, cwd=lang_dir)
                has_error = "error" in result.stderr.lower()
                print(f"Exit code: {result.returncode}")
                print(f"Contains 'error' in stderr: {has_error}")
                print(f"STDERR: {repr(result.stderr[:200])}")
                test_results['greet_missing_argument'] = has_error
                
                # Test 6: greet_invalid_style - looking for "Hello, Alice!"
                print(f"\n--- greet_invalid_style ---")
                result = subprocess.run(config['run_cmd'](cli_path, ["greet", "Alice", "--style", "invalid"]), 
                                      capture_output=True, text=True, cwd=lang_dir)
                has_hello_alice_invalid = "Hello, Alice!" in result.stdout
                print(f"Exit code: {result.returncode}")
                print(f"Contains 'Hello, Alice!': {has_hello_alice_invalid}")
                print(f"STDOUT: {repr(result.stdout)}")
                test_results['greet_invalid_style'] = has_hello_alice_invalid
                
                # Test 7: command_help - looking for "NAME" and "--count"
                print(f"\n--- command_help ---")
                result = subprocess.run(config['run_cmd'](cli_path, ["greet", "--help"]), 
                                      capture_output=True, text=True, cwd=lang_dir)
                has_name = "NAME" in result.stdout
                has_count = "--count" in result.stdout
                print(f"Exit code: {result.returncode}")
                print(f"Contains 'NAME': {has_name}")
                print(f"Contains '--count': {has_count}")
                print(f"STDOUT excerpt: {repr(result.stdout[:300])}")
                test_results['command_help'] = has_name and has_count
                
                results[lang] = test_results
                
            except Exception as e:
                print(f"ERROR testing {lang}: {e}")
                import traceback
                traceback.print_exc()
        
        # Summary
        print(f"\n{'='*60}")
        print("COMPREHENSIVE FAILURE ANALYSIS SUMMARY")
        print(f"{'='*60}")
        
        failing_tests = [
            'help_command', 'greet_basic', 'greet_with_enthusiastic_flag',
            'info_with_format_option', 'greet_missing_argument',
            'greet_invalid_style', 'command_help'
        ]
        
        for test in failing_tests:
            print(f"\n{test}:")
            for lang, lang_results in results.items():
                if test in lang_results:
                    status = "PASS" if lang_results[test] else "FAIL"
                    print(f"  {lang:12}: {status}")

if __name__ == "__main__":
    generate_and_test_all_languages()