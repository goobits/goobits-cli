#!/usr/bin/env python3
"""
Debug script to reproduce the exact integration test flow.
"""
import sys
import tempfile
from pathlib import Path

# Add the source path
sys.path.insert(0, '/workspace/src')

from goobits_cli.generators.python import PythonGenerator
from goobits_cli.schemas import GoobitsConfigSchema

def create_test_config():
    """Create the same configuration as the integration test."""
    config_data = {
        "package_name": "test_e2e_python",
        "command_name": "test-e2e-python",
        "display_name": "Test E2E Python",
        "description": "End-to-end integration test for Python",
        "version": "1.0.0",
        "author": "Test Author",
        "email": "test@example.com",
        "license": "MIT",
        "language": "python",
        "cli_output_path": "cli.py",
        
        "cli": {
            "name": "test_e2e_python",
            "tagline": "End-to-end integration test CLI for python",
            "commands": {
                "hello": {
                    "desc": "Say hello to someone",
                    "is_default": False,
                    "args": [
                        {
                            "name": "name",
                            "desc": "Name to greet",
                            "required": True
                        }
                    ],
                    "options": [
                        {
                            "name": "greeting",
                            "short": "g",
                            "desc": "Custom greeting message",
                            "default": "Hello"
                        },
                        {
                            "name": "uppercase",
                            "short": "u",
                            "type": "flag",
                            "desc": "Convert output to uppercase"
                        }
                    ]
                }
            }
        }
    }
    
    return GoobitsConfigSchema(**config_data)

def create_hook_implementation():
    """Create the hook implementation exactly as the integration test does."""
    return '''"""
Hook implementations for testing CLI execution.
"""

def on_hello(name: str, greeting: str = "Hello", uppercase: bool = False, **kwargs):
    """Handle hello command execution."""
    message = f"{greeting} {name}!"
    if uppercase:
        message = message.upper()
    print(f"HOOK_EXECUTED: {message}")
    return {"status": "success", "message": message}
'''

def main():
    print("🔍 Reproducing integration test flow...")
    
    # Step 1: Create test configuration
    print("Step 1: Creating test configuration")
    config = create_test_config()
    
    # Step 2: Create generator (exactly as the test does)
    print("Step 2: Creating Python generator with use_universal_templates=False")
    generator = PythonGenerator(use_universal_templates=False)
    print(f"   - Generator use_universal_templates: {generator.use_universal_templates}")
    
    # Step 3: Generate CLI code
    print("Step 3: Generating CLI files")
    all_files = generator.generate_all_files(config, "e2e_test_python.yaml", "1.0.0")
    
    if not all_files:
        print("❌ No files generated!")
        return
    
    print(f"   - Generated {len(all_files)} files")
    for filename in all_files.keys():
        print(f"     - {filename}")
    
    # Step 4: Create temporary directory
    print("Step 4: Creating temporary directory")
    temp_dir = tempfile.mkdtemp(prefix="debug_e2e_python_")
    print(f"   - Created: {temp_dir}")
    
    # Step 5: Write generated files
    print("Step 5: Writing generated files")
    executable_files = all_files.pop('__executable__', [])
    for filename, content in all_files.items():
        file_path = Path(temp_dir) / filename
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content)
        
        # Make executable if needed
        if filename in executable_files or filename.startswith('bin/') or filename == 'setup.sh':
            file_path.chmod(0o755)
        
        print(f"   - Wrote: {file_path}")
    
    # Step 6: Create hook file
    print("Step 6: Creating hook implementation")
    hook_content = create_hook_implementation()
    hook_path = Path(temp_dir) / "app_hooks.py"
    hook_path.write_text(hook_content)
    print(f"   - Created: {hook_path}")
    
    # Step 7: Test CLI execution
    print("Step 7: Testing CLI execution")
    import subprocess
    
    # Find the CLI file
    cli_files = list(Path(temp_dir).glob("*.py"))
    cli_files = [f for f in cli_files if f.name != "app_hooks.py" and f.name != "__init__.py"]
    
    if not cli_files:
        print("❌ No CLI file found!")
        return
    
    cli_file = cli_files[0]
    print(f"   - Testing CLI: {cli_file}")
    
    # Test help command
    print("   - Testing --help:")
    try:
        result = subprocess.run([
            sys.executable, str(cli_file), "--help"
        ], capture_output=True, text=True, cwd=temp_dir, timeout=30)
        
        print(f"     Return code: {result.returncode}")
        if result.returncode == 0:
            print(f"     ✅ Help command succeeded")
        else:
            print(f"     ❌ Help command failed:")
            print(f"     STDERR: {result.stderr}")
    except Exception as e:
        print(f"     ❌ Help command error: {e}")
    
    # Test hello command exactly like the integration test
    print("   - Testing hello command (exactly like integration test):")
    try:
        hello_result = subprocess.run([
            sys.executable, str(cli_file), "hello", "World"
        ], capture_output=True, text=True, cwd=temp_dir, timeout=30)
        
        print(f"     Return code: {hello_result.returncode}")
        print(f"     STDOUT: '{hello_result.stdout}'")
        print(f"     STDERR: '{hello_result.stderr}'")
        
        if hello_result.returncode == 0:
            print("     ✅ Hello command executed successfully")
            if "HOOK_EXECUTED" in hello_result.stdout:
                print("     ✅ Hook execution detected")
                hook_executed = True
            else:
                print("     ❌ Hook execution NOT detected")
                hook_executed = False
        else:
            print(f"     ❌ Hello command failed: {hello_result.stderr}")
            hook_executed = False
        
        print(f"     Final hook_executed: {hook_executed}")
        
        if not hook_executed:
            print("     🔍 HOOK_EXECUTED debug:")
            stdout_lines = hello_result.stdout.split('\n')
            for i, line in enumerate(stdout_lines):
                print(f"       Line {i}: '{line}'")
                if "HOOK" in line:
                    print(f"         ^ Contains 'HOOK'")
            
        if not hook_executed:
            print("     ❌ Hook NOT executed")
            
            # Debug: Show the actual CLI file structure
            print("\n   🔍 CLI file analysis:")
            cli_content = cli_file.read_text()
            
            if "HookManager" in cli_content:
                print("     - Uses HookManager (Universal Template System)")
            else:
                print("     - Uses direct hook loading (Legacy style)")
            
            if "_find_and_import_hooks" in cli_content:
                print("     - Has _find_and_import_hooks function")
                
            if "hook_func(**kwargs)" in cli_content:
                print("     - Has direct hook function call")
            
            # Check hook loading mechanism
            lines = cli_content.split('\n')
            for i, line in enumerate(lines):
                if "app_hooks" in line and ("=" in line or "import" in line):
                    print(f"     - Line {i+1}: {line.strip()}")
                    
    except Exception as e:
        print(f"     ❌ Hello command error: {e}")
    
    print(f"\n🗂️  Files created in: {temp_dir}")
    print("   You can inspect the generated files manually.")

if __name__ == "__main__":
    main()