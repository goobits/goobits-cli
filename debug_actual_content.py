#!/usr/bin/env python3
"""
Debug script to examine the actual content of generated CLI files.
"""

import os
import sys
import tempfile
import subprocess
import yaml

# Add the source directory to path
sys.path.insert(0, '/workspace/src')

def generate_and_examine_python_cli():
    """Generate a Python CLI and examine its actual content."""
    print("=== Generating and Examining Python CLI ===")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        config = {
            'package_name': 'debug-python-cli',
            'command_name': 'debugpy',
            'display_name': 'Debug Python CLI',
            'description': 'Debug Python CLI to examine logging',
            'language': 'python',
            'cli_output_path': f'{temp_dir}/cli.py',
            
            'python': {
                'minimum_version': '3.8',
                'maximum_version': '3.13'
            },
            
            'installation': {
                'pypi_name': 'debug-python-cli'
            },
            
            'shell_integration': {
                'enabled': False,
                'alias': 'debugpy'
            },
            
            'validation': {
                'check_api_keys': False,
                'check_disk_space': False
            },
            
            'cli': {
                'name': 'debugpy',
                'tagline': 'Debug Python CLI',
                'description': 'Debug Python CLI',
                'commands': {
                    'hello': {
                        'desc': 'Say hello',
                        'args': [{
                            'name': 'name',
                            'desc': 'Name to greet',
                            'type': 'string',
                            'required': True
                        }]
                    }
                }
            }
        }
        
        config_file = os.path.join(temp_dir, 'goobits.yaml')
        with open(config_file, 'w') as f:
            yaml.dump(config, f)
        
        # Generate CLI
        print("Generating CLI...")
        build_cmd = [sys.executable, '-m', 'goobits_cli.main', 'build', config_file]
        result = subprocess.run(build_cmd, cwd=temp_dir, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"Build failed: {result.stderr}")
            return
        
        # Read and examine content
        cli_file = config['cli_output_path']
        if not os.path.exists(cli_file):
            print(f"CLI file not found: {cli_file}")
            return
        
        with open(cli_file, 'r') as f:
            content = f.read()
        
        print(f"✓ Generated CLI file ({len(content)} chars)")
        
        # Search for specific logging-related content
        logging_searches = {
            'setup_cli_logging function': 'def setup_cli_logging():',
            'StructuredFormatter class': 'class StructuredFormatter',
            'contextvars import': 'contextvars',
            'ContextVar usage': 'ContextVar',
            'LOG_LEVEL environment': '_LOG_LEVEL',
            'LOG_OUTPUT environment': '_LOG_OUTPUT',
            'json.dumps usage': 'json.dumps',
            'logging import': 'import logging',
            'structured logging': 'structured',
            'get_cli_logger function': 'def get_cli_logger',
        }
        
        print("\nSearching for logging functionality:")
        found_items = []
        for description, search_term in logging_searches.items():
            if search_term in content:
                found_items.append(description)
                print(f"  ✓ Found: {description}")
                
                # Show context around the match
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    if search_term in line:
                        start = max(0, i-1)
                        end = min(len(lines), i+2)
                        print(f"    Context (lines {start+1}-{end}):")
                        for j in range(start, end):
                            marker = "    >>> " if j == i else "        "
                            print(f"{marker}{j+1}: {lines[j]}")
                        break
                print()
        
        if not found_items:
            print("  ✗ No logging functionality found")
            
            # Show a sample of the file to understand what it contains
            print("\nSample of generated content (first 50 lines):")
            print("=" * 60)
            lines = content.split('\n')
            for i, line in enumerate(lines[:50]):
                print(f"{i+1:3d}: {line}")
            print("=" * 60)
            
            # Check if this uses a different template system
            if "cli_template.py.j2" in content:
                print("\n✓ Uses cli_template.py.j2 (should have logging)")
            else:
                print("\n? Template source unclear")
        
        else:
            print(f"\n✅ Found {len(found_items)} logging features:")
            for item in found_items:
                print(f"  - {item}")

def main():
    generate_and_examine_python_cli()

if __name__ == "__main__":
    main()