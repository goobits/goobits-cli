#!/usr/bin/env python3
"""
Simple End-to-End Integration Test for Python CLI Generation

This is a focused test that validates the core functionality:
1. Generate a Python CLI from YAML configuration
2. Create hook implementations
3. Execute the CLI and verify it works
4. Test basic error handling

Agent: Dave-IntegrationTester
"""

import json
import os
import tempfile
import time
import subprocess
import shutil
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any

# Import framework components
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from goobits_cli.schemas import GoobitsConfigSchema
from goobits_cli.generators.python import PythonGenerator


def create_test_config() -> GoobitsConfigSchema:
    """Create a simple test configuration for Python CLI."""
    config_data = {
        "package_name": "simple-test-cli",
        "command_name": "simple_test",
        "display_name": "Simple Test CLI", 
        "description": "A simple test CLI for integration testing",
        "language": "python",
        
        "python": {
            "minimum_version": "3.8"
        },
        
        "dependencies": {
            "required": ["click"],
            "optional": []
        },
        
        "installation": {
            "pypi_name": "simple-test-cli",
            "development_path": "."
        },
        
        "shell_integration": {
            "enabled": False,
            "alias": "simple_test"
        },
        
        "validation": {
            "check_api_keys": False,
            "check_disk_space": False
        },
        
        "messages": {
            "install_success": "Installation completed successfully!",
            "install_dev_success": "Development installation completed successfully!",
            "upgrade_success": "Upgrade completed successfully!",
            "uninstall_success": "Uninstall completed successfully!"
        },
        
        "cli": {
            "name": "simple_test",
            "tagline": "Simple test CLI",
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
                        }
                    ]
                },
                "status": {
                    "desc": "Show system status",
                    "is_default": True
                }
            }
        }
    }
    
    return GoobitsConfigSchema(**config_data)


def create_hook_implementation() -> str:
    """Create hook implementation for testing."""
    return '''"""
Hook implementations for testing CLI execution.
"""

def on_hello(name: str, greeting: str = "Hello", **kwargs):
    """Handle hello command execution."""
    message = f"{greeting} {name}!"
    print(f"HOOK_EXECUTED: {message}")
    return {"status": "success", "message": message}

def on_status(**kwargs):
    """Handle status command execution."""
    print("HOOK_EXECUTED: System status is OK")
    return {"status": "success", "system_status": "ok"}
'''


def test_python_cli_integration() -> Dict[str, Any]:
    """Test Python CLI integration end-to-end."""
    result = {
        "success": False,
        "warnings": [],
        "error_message": "",
        "generation_success": False,
        "hook_execution_success": False,
        "help_command_success": False,
        "error_handling_success": False
    }
    
    temp_dir = None
    try:
        # Step 1: Create test configuration
        print("📋 Creating test configuration...")
        config = create_test_config()
        result["warnings"].append("Test configuration created")
        
        # Step 2: Generate CLI code
        print("⚙️  Generating Python CLI...")
        generator = PythonGenerator(use_universal_templates=False)
        all_files = generator.generate_all_files(config, "simple_test.yaml", "1.0.0")
        
        if not all_files:
            result["error_message"] = "No files generated"
            return result
        
        result["generation_success"] = True
        result["warnings"].append(f"Generated {len(all_files)} files")
        
        # Step 3: Create temporary directory for CLI
        temp_dir = tempfile.mkdtemp(prefix="simple_integration_test_")
        print(f"📁 Created temp directory: {temp_dir}")
        
        # Step 4: Write generated files
        executable_files = all_files.pop('__executable__', [])
        for filename, content in all_files.items():
            file_path = Path(temp_dir) / filename
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(content)
            
            # Make executable if needed
            if filename in executable_files or filename.startswith('bin/') or filename == 'setup.sh':
                file_path.chmod(0o755)
        
        result["warnings"].append(f"Files written to {temp_dir}")
        
        # Step 5: Create hook implementation
        hook_content = create_hook_implementation()
        hook_path = Path(temp_dir) / "app_hooks.py"
        hook_path.write_text(hook_content)
        result["warnings"].append("Hook implementation created")
        
        # Step 6: Find the main CLI file
        cli_file = None
        for filename in ["cli.py", "generated_cli.py", "main.py"]:
            potential_file = Path(temp_dir) / filename
            if potential_file.exists():
                cli_file = potential_file
                break
        
        # Look for any Python file if main ones not found
        if not cli_file:
            for filename in all_files.keys():
                if filename.endswith('.py'):
                    potential_file = Path(temp_dir) / filename
                    if potential_file.exists():
                        cli_file = potential_file
                        break
        
        if not cli_file:
            result["error_message"] = "No Python CLI file found"
            return result
        
        print(f"🐍 Found CLI file: {cli_file}")
        
        # Step 7: Test CLI help command
        print("🆘 Testing help command...")
        help_result = subprocess.run([
            sys.executable, str(cli_file), "--help"
        ], capture_output=True, text=True, cwd=temp_dir, timeout=30)
        
        if help_result.returncode == 0:
            result["help_command_success"] = True
            result["warnings"].append("Help command executed successfully")
            
            # Verify expected content in help output
            help_text = help_result.stdout.lower()
            if "hello" in help_text and "status" in help_text:
                result["warnings"].append("Expected commands found in help")
            else:
                result["warnings"].append("Some expected commands missing from help")
        else:
            result["warnings"].append(f"Help command failed: {help_result.stderr}")
        
        # Step 8: Test hook execution
        print("🔗 Testing hook execution...")
        hello_result = subprocess.run([
            sys.executable, str(cli_file), "hello", "World"
        ], capture_output=True, text=True, cwd=temp_dir, timeout=30)
        
        if hello_result.returncode == 0:
            if "HOOK_EXECUTED" in hello_result.stdout:
                result["hook_execution_success"] = True
                result["warnings"].append("Hook execution detected")
            else:
                result["warnings"].append("Hello command executed but no hook detected")
        else:
            result["warnings"].append(f"Hello command failed: {hello_result.stderr}")
        
        # Step 9: Test error handling
        print("❌ Testing error handling...")
        error_result = subprocess.run([
            sys.executable, str(cli_file), "hello"  # Missing required argument
        ], capture_output=True, text=True, cwd=temp_dir, timeout=30)
        
        if error_result.returncode != 0:
            # Error exit is expected
            if error_result.stderr.strip() or "error" in error_result.stdout.lower():
                result["error_handling_success"] = True
                result["warnings"].append("Error handling works correctly")
            else:
                result["warnings"].append("Error exit but no error message")
        else:
            result["warnings"].append("Command should have failed but succeeded")
        
        # Overall success assessment
        if (result["generation_success"] and 
            result["help_command_success"] and 
            result["hook_execution_success"]):
            result["success"] = True
        
    except subprocess.TimeoutExpired:
        result["error_message"] = "CLI execution timed out"
    except Exception as e:
        result["error_message"] = f"Integration test failed: {str(e)}"
    finally:
        # Cleanup
        if temp_dir and Path(temp_dir).exists():
            try:
                shutil.rmtree(temp_dir, ignore_errors=True)
                print(f"🧹 Cleaned up temp directory: {temp_dir}")
            except Exception:
                pass
    
    return result


def run_simple_integration_test():
    """Run the simple integration test and display results."""
    print("🚀 Starting Simple Python CLI Integration Test")
    print("=" * 50)
    
    start_time = time.time()
    result = test_python_cli_integration()
    execution_time = (time.time() - start_time) * 1000
    
    print(f"\n📊 TEST RESULTS:")
    print(f"   Overall Success: {'✅' if result['success'] else '❌'}")
    print(f"   CLI Generation: {'✅' if result['generation_success'] else '❌'}")
    print(f"   Help Command: {'✅' if result['help_command_success'] else '❌'}")
    print(f"   Hook Execution: {'✅' if result['hook_execution_success'] else '❌'}")
    print(f"   Error Handling: {'✅' if result['error_handling_success'] else '❌'}")
    print(f"   Execution Time: {execution_time:.1f}ms")
    
    if result["warnings"]:
        print(f"\n📝 DETAILS:")
        for warning in result["warnings"]:
            print(f"   • {warning}")
    
    if result["error_message"]:
        print(f"\n❌ ERROR: {result['error_message']}")
    
    print(f"\n🏁 FINAL RESULT: {'✅ TEST PASSED' if result['success'] else '❌ TEST FAILED'}")
    
    return result["success"]


if __name__ == "__main__":
    success = run_simple_integration_test()
    sys.exit(0 if success else 1)