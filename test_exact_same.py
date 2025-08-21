#!/usr/bin/env python3
"""
Test with exact same setup as mini test but same calling pattern as debug test.
"""

import sys
import tempfile
import subprocess
from pathlib import Path

# Add the source directory to the path
sys.path.insert(0, str(Path(__file__).parent / 'src'))


def create_comprehensive_test_config():
    """Create exactly the same configuration as the working mini test."""
    from goobits_cli.schemas import GoobitsConfigSchema
    
    config_data = {
        "package_name": "e2e_test-python",
        "command_name": "e2e_test_python",
        "display_name": "E2e_Test Python CLI",
        "description": "End-to-end integration test CLI for python",
        "language": "python",
        
        "python": {
            "minimum_version": "3.8"
        },
        
        "dependencies": {
            "required": ["pipx"],
            "optional": []
        },
        
        "installation": {
            "pypi_name": "e2e_test-python",
            "development_path": ".",
            "extras": {
                "python": ["click", "rich"],
                "npm": [],
                "cargo": []
            }
        },
        
        "shell_integration": {
            "enabled": False,
            "alias": "e2e_test_python"
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
            "name": "e2e_test_python",
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


def main():
    """Test exact same setup."""
    print("🔍 Test Exact Same Setup")
    print("=" * 40)
    
    try:
        # Create configuration
        config = create_comprehensive_test_config()
        
        # Create generator exactly like mini test
        from goobits_cli.generators.python import PythonGenerator
        generator = PythonGenerator(use_universal_templates=False)  # Ignored
        
        # Generate files exactly like mini test
        all_files = generator.generate_all_files(config, "e2e_test_python.yaml", "1.0.0")
        
        # Create temp directory exactly like mini test
        temp_dir = tempfile.mkdtemp(prefix="e2e_test_python_")
        
        # Write files exactly like mini test
        executable_files = all_files.pop('__executable__', [])
        for filename, content in all_files.items():
            file_path = Path(temp_dir) / filename
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(content)
        
        print(f"Generated {len(all_files)} files in {temp_dir}")
        
        # Create hooks exactly like mini test
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
        
        # Find CLI file exactly like mini test
        cli_files = list(Path(temp_dir).rglob("cli.py"))
        cli_file = cli_files[0]
        
        print(f"Found CLI file: {cli_file}")
        
        # Test exactly like debug integration test (this is where it fails)
        hello_result = subprocess.run([
            sys.executable, str(cli_file), "hello", "World"
        ], capture_output=True, text=True, cwd=temp_dir, timeout=30)
        
        print(f"Return code: {hello_result.returncode}")
        print(f"Stdout: {hello_result.stdout}")
        print(f"Stderr: {hello_result.stderr}")
        
        if hello_result.returncode == 0:
            print("✅ Hello command executed successfully")
            if "HOOK_EXECUTED" in hello_result.stdout:
                print("✅ Hook execution detected")
            else:
                print("❌ No hook execution detected")
        else:
            print("❌ Hello command failed")
            
        print(f"Temp directory: {temp_dir}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()