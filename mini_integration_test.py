#!/usr/bin/env python3
"""
Minimal version of the integration test to debug the issue.
"""

import tempfile
import sys
import subprocess
from pathlib import Path

# Add the source directory to the path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from goobits_cli.schemas import GoobitsConfigSchema
from goobits_cli.generators.python import PythonGenerator


def create_comprehensive_test_config():
    """Create exactly the same configuration as the integration test."""
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


def create_hooks():
    """Create exactly the same hooks as the integration test."""
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
    """Run minimal integration test."""
    print("🧪 Mini Integration Test")
    print("=" * 40)
    
    try:
        # Create configuration
        config = create_comprehensive_test_config()
        
        # Create generator  
        generator = PythonGenerator(use_universal_templates=False)
        
        # Generate files
        all_files = generator.generate_all_files(config, "e2e_test_python.yaml", "1.0.0")
        
        # Create temp directory
        temp_dir = tempfile.mkdtemp(prefix="e2e_test_python_")
        
        # Write generated files
        executable_files = all_files.pop('__executable__', [])
        for filename, content in all_files.items():
            file_path = Path(temp_dir) / filename
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(content)
            
            if filename in executable_files or filename.startswith('bin/') or filename == 'setup.sh':
                file_path.chmod(0o755)
        
        print(f"Generated {len(all_files)} files in {temp_dir}")
        
        # Create hook implementation
        hook_path = Path(temp_dir) / "app_hooks.py"
        hook_path.write_text(create_hooks())
        print(f"Created hook file: {hook_path}")
        
        # Find CLI file
        cli_file = None
        search_patterns = ["cli.py", "generated_cli.py", "main.py"]
        for pattern in search_patterns:
            cli_path = Path(temp_dir) / pattern
            if cli_path.exists():
                cli_file = cli_path
                break
        
        # Fallback search
        if not cli_file:
            for filename in all_files.keys():
                if filename.endswith('.py'):
                    cli_path = Path(temp_dir) / filename  
                    if cli_path.exists():
                        cli_file = cli_path
                        break
        
        # Try recursive search
        if not cli_file:
            cli_files = list(Path(temp_dir).rglob("cli.py"))
            if cli_files:
                cli_file = cli_files[0]
        
        if not cli_file:
            print("❌ No CLI file found")
            return
        
        print(f"Found CLI file: {cli_file}")
        
        # Test help command
        help_result = subprocess.run([
            sys.executable, str(cli_file), "--help"
        ], capture_output=True, text=True, cwd=temp_dir, timeout=30)
        
        if help_result.returncode == 0:
            print("✅ Help command successful")
            
            # Test hello command
            hello_result = subprocess.run([
                sys.executable, str(cli_file), "hello", "World"
            ], capture_output=True, text=True, cwd=temp_dir, timeout=30)
            
            print(f"Hello command return code: {hello_result.returncode}")
            print(f"Hello stdout: {hello_result.stdout}")
            print(f"Hello stderr: {hello_result.stderr}")
            
            if hello_result.returncode == 0:
                print("✅ Hello command executed successfully")
                if "HOOK_EXECUTED" in hello_result.stdout:
                    print("✅ Hook execution detected")
                else:
                    print("❌ No hook execution detected")
            else:
                print("❌ Hello command failed")
        else:
            print(f"❌ Help command failed: {help_result.stderr}")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()