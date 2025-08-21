#!/usr/bin/env python3
"""Test the complete integration with the fix."""
import tempfile
import subprocess
import sys
from pathlib import Path
from goobits_cli.generators.python import PythonGenerator
from goobits_cli.schemas import GoobitsConfigSchema

# Create the exact config the integration test uses
config_data = {
    "package_name": "e2e_test_python",
    "command_name": "e2e_test_python",
    "display_name": "E2e_Test Python CLI",
    "description": "End-to-end integration test CLI for python",
    "language": "python",
    
    "python": {
        "minimum_version": "3.8"
    },
    
    "cli": {
        "name": "e2e_test_python",
        "tagline": "E2e_Test Python CLI",
        "description": "End-to-end integration test CLI for python",
        "commands": {
            "hello": {
                "desc": "Say hello to someone",
                "args": [
                    {"name": "name", "desc": "Name to greet", "required": True}
                ],
                "options": [
                    {"name": "greeting", "desc": "Custom greeting", "default": "Hello"},
                    {"name": "uppercase", "type": "flag", "desc": "Convert to uppercase"}
                ]
            }
        }
    }
}

config = GoobitsConfigSchema(**config_data)

# Generate files
generator = PythonGenerator(use_universal_templates=False)
all_files = generator.generate_all_files(config, "e2e_test_python.yaml", "1.0.0")

print(f"✅ Generated {len(all_files)} files:")
for filepath in sorted(all_files.keys()):
    print(f"  - {filepath}")

# Create temp directory
with tempfile.TemporaryDirectory(prefix="test_fix_") as temp_dir:
    # Write generated files
    for filename, content in all_files.items():
        file_path = Path(temp_dir) / filename
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content)
    
    # Apply the fix: Find CLI directory
    cli_dir = None
    for filename in all_files.keys():
        if filename.endswith('/cli.py'):
            cli_dir = Path(filename).parent
            break
    
    # Create hook file in the RIGHT location (applying the fix)
    hook_content = '''
def on_hello(name: str, greeting: str = "Hello", uppercase: bool = False, **kwargs):
    """Handle hello command execution."""
    message = f"{greeting} {name}!"
    if uppercase:
        message = message.upper()
    print(f"HOOK_EXECUTED: {message}")
    return {"status": "success", "message": message}
'''
    
    if cli_dir:
        hook_path = Path(temp_dir) / cli_dir / "app_hooks.py"
        print(f"\n✅ Placing hook file at: {hook_path.relative_to(temp_dir)}")
    else:
        hook_path = Path(temp_dir) / "app_hooks.py"
        print(f"\n✅ Placing hook file at: app_hooks.py (root)")
    
    hook_path.parent.mkdir(parents=True, exist_ok=True)
    hook_path.write_text(hook_content)
    
    # Find CLI file
    cli_file = Path(temp_dir) / "src" / "e2e_test_python" / "cli.py"
    if not cli_file.exists():
        print(f"❌ CLI file not found at expected location: {cli_file}")
        sys.exit(1)
    
    print(f"✅ Found CLI file: {cli_file.relative_to(temp_dir)}")
    
    # Test the hello command
    print("\n🔍 Testing hello command...")
    hello_result = subprocess.run(
        [sys.executable, str(cli_file), "hello", "World"],
        capture_output=True, text=True, cwd=temp_dir
    )
    
    print(f"  Exit code: {hello_result.returncode}")
    print(f"  Stdout: {hello_result.stdout}")
    if hello_result.stderr:
        print(f"  Stderr: {hello_result.stderr}")
    
    # Check for HOOK_EXECUTED
    if "HOOK_EXECUTED" in hello_result.stdout:
        print("\n✅ SUCCESS: Hook was executed! Integration test should pass.")
    else:
        print("\n❌ FAILURE: Hook was NOT executed.")
        
        # Debug: Check if hook file exists and is in the right place
        print("\n📁 Directory structure:")
        for root, dirs, files in os.walk(temp_dir):
            level = root.replace(temp_dir, '').count(os.sep)
            indent = ' ' * 2 * level
            print(f'{indent}{os.path.basename(root)}/')
            subindent = ' ' * 2 * (level + 1)
            for file in files:
                print(f'{subindent}{file}')

import os