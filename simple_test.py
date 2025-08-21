#!/usr/bin/env python3
"""
Simple integration test to debug the hook issue.
"""

import tempfile
import sys
import subprocess
from pathlib import Path

# Add the source directory to the path  
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from goobits_cli.schemas import GoobitsConfigSchema
from goobits_cli.generators.python import PythonGenerator


def create_test_config():
    """Create test configuration matching the integration test."""
    config_data = {
        "package_name": "test-cli",
        "command_name": "test_cli",
        "display_name": "Test CLI",
        "description": "Test CLI",
        "language": "python",
        
        "python": {
            "minimum_version": "3.8"
        },
        
        "dependencies": {
            "required": ["pipx"],
            "optional": []
        },
        
        "installation": {
            "pypi_name": "test-cli",
            "development_path": ".",
            "extras": {
                "python": ["click", "rich"]
            }
        },
        
        "shell_integration": {
            "enabled": False,
            "alias": "test_cli"
        },
        
        "validation": {
            "check_api_keys": False,
            "check_disk_space": True,
            "minimum_disk_space_mb": 100
        },
        
        "messages": {
            "install_success": "Installation completed successfully!",
            "install_dev_success": "Development installation completed successfully!",
            "upgrade_success": "Upgrade completed successfully!",
            "uninstall_success": "Uninstall completed successfully!"
        },
        
        "cli": {
            "name": "test_cli",
            "tagline": "Test CLI",
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


def create_hooks_file(temp_dir):
    """Create hooks file exactly like the integration test."""
    hook_content = '''"""
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
    
    hook_path = Path(temp_dir) / "app_hooks.py"
    hook_path.write_text(hook_content)
    return hook_path


def main():
    """Main test function."""
    print("🧪 Simple Integration Test - Debug Hook Loading")
    print("=" * 60)
    
    try:
        # Create configuration
        config = create_test_config()
        print("✅ Configuration created")
        
        # Create generator
        generator = PythonGenerator(use_universal_templates=False)  # Will be ignored
        print(f"✅ Generator created (use_universal_templates={generator.use_universal_templates})")
        
        # Generate files
        all_files = generator.generate_all_files(config, "test.yaml", "1.0.0")
        print(f"✅ Generated {len(all_files)} files")
        
        # Create temp directory
        temp_dir = tempfile.mkdtemp(prefix="simple_test_")
        print(f"✅ Temp directory: {temp_dir}")
        
        # Write generated files
        executable_files = all_files.pop('__executable__', [])
        for filename, content in all_files.items():
            file_path = Path(temp_dir) / filename
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(content)
            
            if filename in executable_files or filename.startswith('bin/') or filename == 'setup.sh':
                file_path.chmod(0o755)
        
        print("✅ Generated files written")
        
        # Create hooks file
        hook_path = create_hooks_file(temp_dir)
        print(f"✅ Hooks file created: {hook_path}")
        
        # Find CLI file
        cli_files = list(Path(temp_dir).rglob("cli.py"))
        if not cli_files:
            print("❌ No CLI file found")
            return
        
        cli_file = cli_files[0]
        print(f"✅ CLI file found: {cli_file}")
        
        # Test CLI execution
        print("\n🚀 Testing CLI execution...")
        
        # Test 1: Help command
        help_result = subprocess.run([
            sys.executable, str(cli_file), "--help"
        ], capture_output=True, text=True, cwd=temp_dir, timeout=10)
        
        print(f"Help command - Return code: {help_result.returncode}")
        if help_result.returncode == 0:
            print("✅ Help command successful")
        else:
            print(f"❌ Help command failed: {help_result.stderr}")
            print(f"Stdout: {help_result.stdout}")
            return
        
        # Test 2: Hello command (this should find hooks)
        hello_result = subprocess.run([
            sys.executable, str(cli_file), "hello", "World"
        ], capture_output=True, text=True, cwd=temp_dir, timeout=10)
        
        print(f"\nHello command - Return code: {hello_result.returncode}")
        print(f"Stdout: {hello_result.stdout}")
        print(f"Stderr: {hello_result.stderr}")
        
        if "HOOK_EXECUTED" in hello_result.stdout:
            print("✅ Hook execution successful!")
        else:
            print("❌ Hook execution failed - no HOOK_EXECUTED marker found")
        
        # Debug: List files in temp directory
        print("\n📁 Files in temp directory:")
        for file_path in Path(temp_dir).rglob("*"):
            if file_path.is_file():
                print(f"   {file_path.relative_to(temp_dir)}")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()