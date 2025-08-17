#!/usr/bin/env python3
"""
Debug script to trace file writing bug in goobits build command.
"""

import sys
from pathlib import Path

# Add the goobits_cli to the path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from goobits_cli.main import load_goobits_config
from goobits_cli.generators.python import PythonGenerator

def debug_file_writing():
    """Debug the file writing process step by step."""
    
    print("🔍 DEBUG: Tracing file writing bug")
    print("="*50)
    
    # Step 1: Load configuration
    print("1. Loading configuration...")
    config_path = Path("goobits.yaml")
    goobits_config = load_goobits_config(config_path)
    print(f"   ✅ Config loaded: {goobits_config.command_name}")
    print(f"   ✅ CLI output path: {goobits_config.cli_output_path}")
    
    # Step 2: Initialize generator
    print("\n2. Initializing Python generator...")
    generator = PythonGenerator(use_universal_templates=True)
    print("   ✅ Generator initialized")
    
    # Step 3: Generate all files
    print("\n3. Generating all files...")
    all_files = generator.generate_all_files(goobits_config, "goobits.yaml", "2.0.0-beta.3")
    print(f"   ✅ Generated {len(all_files)} files:")
    
    for file_path, content in all_files.items():
        print(f"      - {file_path}: {len(content)} chars")
        
        # Check if this is the main CLI file
        if "cli.py" in file_path or "generated_cli.py" in file_path:
            print(f"        🔍 Checking content...")
            if "get_version()" in content:
                print(f"        ✅ Contains get_version() function")
            else:
                print(f"        ❌ Missing get_version() function")
            
            # Check if content has build command
            if "def build(" in content:
                print(f"        ✅ Contains build command")
            else:
                print(f"        ❌ Missing build command")
    
    # Step 4: Simulate file writing (what main.py does)
    print("\n4. Simulating file writing process...")
    output_dir = Path(".")
    
    for file_path, content in all_files.items():
        full_path = output_dir / file_path
        print(f"   📝 Would write to: {full_path}")
        print(f"      Content length: {len(content)} chars")
        
        # Check if target file exists
        if full_path.exists():
            print(f"      🔍 Target file exists, current size: {full_path.stat().st_size} bytes")
            
            # Read first few lines to check if it's the old or new content
            with open(full_path, 'r') as f:
                full_content = f.read()
                if "get_version()" in full_content:
                    print(f"      ✅ Current file contains get_version()")
                else:
                    print(f"      ❌ Current file missing get_version()")
                    
                if "def get_version" in full_content:
                    print(f"      ✅ Current file has get_version function definition")
                else:
                    print(f"      ❌ Current file missing get_version function definition")
        else:
            print(f"      ❌ Target file does not exist")
    
    print("\n" + "="*50)
    print("🎯 SUMMARY:")
    print(f"   - Generated files: {len(all_files)}")
    print(f"   - Total characters: {sum(len(content) for content in all_files.values())}")
    
    return all_files

if __name__ == "__main__":
    debug_file_writing()