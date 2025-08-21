#!/usr/bin/env python3
"""Test what actually gets generated."""
from goobits_cli.generators.python import PythonGenerator
from goobits_cli.schemas import GoobitsConfigSchema
import tempfile
from pathlib import Path

# Create test config
config_data = {
    'package_name': 'test_cli',
    'command_name': 'test_cli',
    'display_name': 'Test CLI',
    'description': 'Test CLI',
    'cli': {
        'name': 'test_cli',
        'tagline': 'Test',
        'commands': {
            'hello': {
                'desc': 'Say hello',
                'args': [
                    {'name': 'name', 'desc': 'Name', 'required': True}
                ]
            }
        }
    }
}

config = GoobitsConfigSchema(**config_data)
generator = PythonGenerator()
all_files = generator.generate_all_files(config, 'test.yaml', '1.0.0')

# Write to temp and test
with tempfile.TemporaryDirectory() as tmpdir:
    # Write files
    for filename, content in all_files.items():
        filepath = Path(tmpdir) / filename
        filepath.parent.mkdir(parents=True, exist_ok=True)
        filepath.write_text(content)
    
    # Create hook file
    hook_file = Path(tmpdir) / "src" / "test_cli" / "app_hooks.py"
    hook_file.write_text('''
def on_hello(name, **kwargs):
    print(f"HOOK_EXECUTED: Hello {name}!")
    return 0
''')
    
    # Test the CLI
    import subprocess
    import sys
    
    cli_file = Path(tmpdir) / "src" / "test_cli" / "cli.py"
    
    # Test help
    print("Testing --help:")
    result = subprocess.run([sys.executable, str(cli_file), "--help"], 
                          capture_output=True, text=True, cwd=tmpdir)
    print(f"  Exit code: {result.returncode}")
    if "hello" in result.stdout.lower():
        print("  ✅ 'hello' command found in help")
    else:
        print("  ❌ 'hello' command NOT found in help")
    
    # Test hello command
    print("\nTesting hello World:")
    result = subprocess.run([sys.executable, str(cli_file), "hello", "World"],
                          capture_output=True, text=True, cwd=tmpdir)
    print(f"  Exit code: {result.returncode}")
    print(f"  Stdout: {result.stdout}")
    if result.stderr:
        print(f"  Stderr: {result.stderr}")
    
    if "HOOK_EXECUTED" in result.stdout:
        print("  ✅ Hook executed successfully!")
    else:
        print("  ❌ Hook NOT executed")
        
        # If failed, show the actual generated command
        print("\n📄 Generated hello command:")
        import re
        cli_content = cli_file.read_text()
        # Find @main.command for hello
        lines = cli_content.split('\n')
        for i, line in enumerate(lines):
            if '@main.command' in line:
                # Check if this is hello
                for j in range(i, min(i+10, len(lines))):
                    if 'def hello' in lines[j]:
                        # Print this command definition
                        for k in range(i, min(j+15, len(lines))):
                            print(f"  {k:4}: {lines[k]}")
                        break