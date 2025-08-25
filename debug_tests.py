#!/usr/bin/env python3
"""Debug individual test failures"""

import os
import subprocess
import tempfile
import shutil
import yaml
from pathlib import Path

def generate_cli(language, config_path, output_dir):
    """Generate CLI for a specific language"""
    cmd = [
        "python3", "-m", "goobits_cli.main", "build",
        config_path, "-o", output_dir
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True, cwd="/workspace")
    if result.returncode != 0:
        print(f"Error generating {language} CLI: {result.stderr}")
        return False
    return True

def run_cli_command(cli_path, command_args):
    """Run a command against a CLI and return result"""
    if cli_path.endswith('.py'):
        cmd = ["python3", cli_path] + command_args
    elif cli_path.endswith('.js'):
        cmd = ["node", cli_path] + command_args
    elif cli_path.endswith('.ts'):
        cmd = ["npx", "ts-node", cli_path] + command_args
    else:  # rust
        cmd = [cli_path] + command_args
    
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=cli_path.parent if hasattr(cli_path, 'parent') else Path(cli_path).parent)
    return result

def debug_test():
    # Use temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Copy config files and modify them to use basic-demos hooks
        config_source = Path("/workspace/examples/basic-demos/python-example.yaml")
        hooks_source = Path("/workspace/examples/basic-demos/app_hooks.py")
        
        # Create config for python
        config_python = temp_path / "config-python.yaml"
        with open(config_source) as f:
            config_data = yaml.safe_load(f)
        
        config_data['language'] = 'python'
        config_data['cli_output_path'] = 'cli.py'
        
        with open(config_python, 'w') as f:
            yaml.safe_dump(config_data, f)
        
        # Copy hooks file
        shutil.copy(hooks_source, temp_path / "app_hooks.py")
        
        # Generate Python CLI
        python_dir = temp_path / "python"
        python_dir.mkdir()
        
        if generate_cli('python', str(config_python), str(python_dir)):
            cli_path = python_dir / "cli.py"
            
            # Test 1: greet_basic
            print("=== Testing greet_basic ===")
            result = run_cli_command(str(cli_path), ["greet", "Alice"])
            print(f"Exit code: {result.returncode}")
            print(f"STDOUT: {repr(result.stdout)}")
            print(f"STDERR: {repr(result.stderr)}")
            
            # Test 2: greet missing argument
            print("\n=== Testing greet_missing_argument ===")
            result = run_cli_command(str(cli_path), ["greet"])
            print(f"Exit code: {result.returncode}")
            print(f"STDOUT: {repr(result.stdout)}")
            print(f"STDERR: {repr(result.stderr)}")
            
            # Test 3: Help command
            print("\n=== Testing help_command ===")
            result = run_cli_command(str(cli_path), ["--help"])
            print(f"Exit code: {result.returncode}")
            print(f"STDOUT: {repr(result.stdout)}")
            print(f"STDERR: {repr(result.stderr)}")

if __name__ == "__main__":
    debug_test()