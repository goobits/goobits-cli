#!/usr/bin/env python3
"""Test to reproduce the exact hook integration test scenario."""
import tempfile
import subprocess
import sys
from pathlib import Path
from goobits_cli.generators.python import PythonGenerator
from goobits_cli.schemas import ConfigSchema, CLISchema, CommandSchema, ArgumentSchema

# Create the exact test configuration the integration test uses
def create_test_config():
    """Create test config matching integration test."""
    cli_schema = CLISchema(
        name="test-python",
        tagline="Test CLI for Python",
        description="Test CLI for Python integration",
        commands={
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
    )
    
    return ConfigSchema(
        package_name="test-python",
        cli=cli_schema
    )

def main():
    # Step 1: Create test config
    config = create_test_config()
    print(f"✅ Created test config with CLI name: {config.cli.name}")
    
    # Step 2: Initialize generator with use_universal_templates=False (like the test)
    generator = PythonGenerator(use_universal_templates=False)
    print(f"✅ Initialized generator with use_universal_templates=False")
    
    # Step 3: Generate files (exactly like the test)
    all_files = generator.generate_all_files(config, "e2e_test_python.yaml", "1.0.0")
    print(f"✅ Generated {len(all_files)} files: {list(all_files.keys())}")
    
    # Step 4: Create temp directory and write files
    with tempfile.TemporaryDirectory(prefix="test_hook_") as temp_dir:
        print(f"✅ Created temp directory: {temp_dir}")
        
        # Write generated files
        for filename, content in all_files.items():
            file_path = Path(temp_dir) / filename
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(content)
            print(f"  - Wrote {filename} ({len(content)} bytes)")
        
        # Step 5: Create hook file (exactly like the test)
        hook_content = '''
def on_hello(name: str, greeting: str = "Hello", uppercase: bool = False, **kwargs):
    """Handle hello command execution."""
    message = f"{greeting} {name}!"
    if uppercase:
        message = message.upper()
    print(f"HOOK_EXECUTED: {message}")
    return {"status": "success", "message": message}
'''
        hook_path = Path(temp_dir) / "app_hooks.py"
        hook_path.write_text(hook_content)
        print(f"✅ Created app_hooks.py with on_hello function")
        
        # Step 6: Find the CLI file
        cli_file = None
        for pattern in ["cli.py", "generated_cli.py", "main.py"]:
            test_path = Path(temp_dir) / pattern
            if test_path.exists():
                cli_file = test_path
                break
        
        if not cli_file:
            # Check subdirectories
            for filename in all_files.keys():
                if filename.endswith('.py') and 'cli' in filename:
                    cli_file = Path(temp_dir) / filename
                    if cli_file.exists():
                        break
        
        if cli_file:
            print(f"✅ Found CLI file: {cli_file}")
            
            # Step 7: Test help command
            help_result = subprocess.run(
                [sys.executable, str(cli_file), "--help"],
                capture_output=True, text=True, cwd=temp_dir
            )
            print(f"✅ Help command exit code: {help_result.returncode}")
            if help_result.returncode == 0:
                help_text = help_result.stdout.lower()
                if "hello" in help_text:
                    print("✅ Found 'hello' command in help output")
            
            # Step 8: Test hello command (the critical test)
            hello_result = subprocess.run(
                [sys.executable, str(cli_file), "hello", "World"],
                capture_output=True, text=True, cwd=temp_dir
            )
            print(f"\n🔍 Hello command results:")
            print(f"  Exit code: {hello_result.returncode}")
            print(f"  Stdout: {hello_result.stdout}")
            print(f"  Stderr: {hello_result.stderr}")
            
            # Step 9: Check for HOOK_EXECUTED
            if "HOOK_EXECUTED" in hello_result.stdout:
                print("✅ SUCCESS: Hook was executed! Found 'HOOK_EXECUTED' in output")
            else:
                print("❌ FAILURE: Hook was NOT executed. 'HOOK_EXECUTED' not found in output")
                
                # Debug: Show the CLI file content
                print("\n📄 Generated CLI file content (first 100 lines):")
                cli_content = cli_file.read_text()
                lines = cli_content.split('\n')
                for i, line in enumerate(lines[:100], 1):
                    print(f"{i:3}: {line}")
        else:
            print("❌ No CLI file found!")

if __name__ == "__main__":
    main()