#!/usr/bin/env python3
"""Test with the exact comprehensive config from the integration test."""
from goobits_cli.generators.python import PythonGenerator
from goobits_cli.schemas import GoobitsConfigSchema
import tempfile
from pathlib import Path
import subprocess
import sys

# Create the EXACT config the integration test uses
config_data = {
    "package_name": "e2e_test_python",
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
            },
            "count": {
                "desc": "Count items or words",
                "args": [
                    {
                        "name": "items",
                        "desc": "Items to count",
                        "nargs": "*"
                    }
                ],
                "options": [
                    {
                        "name": "type",
                        "short": "t",
                        "choices": ["words", "chars", "lines"],
                        "default": "words",
                        "desc": "Type of counting to perform"
                    }
                ]
            },
            "config": {
                "desc": "Manage configuration",
                "subcommands": {
                    "show": {
                        "desc": "Show current configuration"
                    },
                    "set": {
                        "desc": "Set configuration value",
                        "args": [
                            {
                                "name": "key",
                                "desc": "Configuration key"
                            },
                            {
                                "name": "value",
                                "desc": "Configuration value"
                            }
                        ]
                    }
                }
            },
            "status": {
                "desc": "Show system status",
                "is_default": True
            }
        }
    }
}

config = GoobitsConfigSchema(**config_data)

# Generate with use_universal_templates=False (like the test)
generator = PythonGenerator(use_universal_templates=False)
all_files = generator.generate_all_files(config, "e2e_test_python.yaml", "1.0.0")

print(f"✅ Generated {len(all_files)} files: {list(all_files.keys())}")

# Test in temp directory
with tempfile.TemporaryDirectory() as tmpdir:
    # Write files
    for filename, content in all_files.items():
        filepath = Path(tmpdir) / filename
        filepath.parent.mkdir(parents=True, exist_ok=True)
        filepath.write_text(content)
    
    # Create hook file WHERE THE TEST PUTS IT (based on my fix)
    # Find CLI directory
    cli_dir = None
    for filename in all_files.keys():
        if filename.endswith('/cli.py'):
            cli_dir = Path(filename).parent
            break
    
    if cli_dir:
        hook_path = Path(tmpdir) / cli_dir / "app_hooks.py"
    else:
        hook_path = Path(tmpdir) / "app_hooks.py"
    
    print(f"✅ Placing hook file at: {hook_path.relative_to(tmpdir)}")
    
    hook_path.parent.mkdir(parents=True, exist_ok=True)
    hook_path.write_text('''
def on_hello(name: str, greeting: str = "Hello", uppercase: bool = False, **kwargs):
    """Handle hello command execution."""
    message = f"{greeting} {name}!"
    if uppercase:
        message = message.upper()
    print(f"HOOK_EXECUTED: {message}")
    return {"status": "success", "message": message}

def on_count(items: list = None, type: str = "words", **kwargs):
    """Handle count command execution."""
    print(f"HOOK_EXECUTED: Count")
    return {"status": "success"}

def on_config_show(**kwargs):
    """Handle config show subcommand."""
    print("HOOK_EXECUTED: Configuration settings")
    return {"status": "success"}

def on_config_set(key: str, value: str, **kwargs):
    """Handle config set subcommand."""
    print(f"HOOK_EXECUTED: Set {key} = {value}")
    return {"status": "success"}

def on_status(**kwargs):
    """Handle status command execution."""
    print("HOOK_EXECUTED: System status is OK")
    return {"status": "success"}
''')
    
    # Find CLI file
    cli_file = Path(tmpdir) / "src" / "e2e_test_python" / "cli.py"
    
    # Test help
    print("\n🔍 Testing --help:")
    result = subprocess.run([sys.executable, str(cli_file), "--help"], 
                          capture_output=True, text=True, cwd=tmpdir)
    print(f"  Exit code: {result.returncode}")
    
    # Check for expected commands
    help_text = result.stdout.lower()
    expected_commands = ["hello", "count", "config", "status"]
    found_commands = [cmd for cmd in expected_commands if cmd in help_text]
    print(f"  Found commands: {found_commands} ({len(found_commands)}/4)")
    
    # Test hello command (THE CRITICAL TEST)
    print("\n🔍 Testing hello World:")
    result = subprocess.run([sys.executable, str(cli_file), "hello", "World"],
                          capture_output=True, text=True, cwd=tmpdir)
    print(f"  Exit code: {result.returncode}")
    print(f"  Stdout: {result.stdout}")
    if result.stderr:
        print(f"  Stderr: {result.stderr}")
    
    if "HOOK_EXECUTED" in result.stdout:
        print("  ✅ SUCCESS: Hook executed!")
    else:
        print("  ❌ FAILURE: Hook NOT executed")