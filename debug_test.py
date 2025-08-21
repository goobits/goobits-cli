#!/usr/bin/env python3
"""
Debug test to isolate the Universal Template System issue.
"""

import tempfile
import sys
from pathlib import Path

# Add the source directory to the path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from goobits_cli.schemas import GoobitsConfigSchema
from goobits_cli.generators.python import PythonGenerator


def create_simple_test_config():
    """Create a simple test configuration."""
    config_data = {
        "package_name": "debug-test",
        "command_name": "debug_test",
        "display_name": "Debug Test CLI",
        "description": "Simple debug test CLI",
        "language": "python",
        
        "python": {
            "minimum_version": "3.8"
        },
        
        "dependencies": {
            "required": ["pipx"],
            "optional": []
        },
        
        "installation": {
            "pypi_name": "debug-test",
            "development_path": ".",
            "extras": {
                "python": ["click", "rich"]
            }
        },
        
        "shell_integration": {
            "enabled": False,
            "alias": "debug_test"
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
            "name": "debug_test",
            "tagline": "Debug test CLI",
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
    """Main debug function."""
    print("🔍 Debug Test: Universal Template System Configuration")
    print("=" * 60)
    
    try:
        # Create test configuration
        config = create_simple_test_config()
        print("✅ Test configuration created successfully")
        
        # Create generator
        generator = PythonGenerator(use_universal_templates=False)  # This will be ignored
        print(f"✅ Generator created (use_universal_templates={generator.use_universal_templates})")
        
        # Generate CLI files
        all_files = generator.generate_all_files(config, "debug_test.yaml", "1.0.0")
        print(f"✅ Generated {len(all_files)} files")
        
        # Create temporary directory and write files
        temp_dir = tempfile.mkdtemp(prefix="debug_test_")
        executable_files = all_files.pop('__executable__', [])
        
        for filename, content in all_files.items():
            file_path = Path(temp_dir) / filename
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(content)
            
            if filename in executable_files or filename.startswith('bin/') or filename == 'setup.sh':
                file_path.chmod(0o755)
        
        print(f"✅ Files written to: {temp_dir}")
        
        # List files
        print("\n📁 Generated files:")
        for file_path in Path(temp_dir).rglob("*"):
            if file_path.is_file():
                print(f"   {file_path.relative_to(temp_dir)}")
        
        # Test the CLI file
        cli_files = list(Path(temp_dir).rglob("cli.py"))
        if cli_files:
            cli_file = cli_files[0]
            print(f"\n🧪 Testing CLI file: {cli_file.name}")
            
            # Try to import and check syntax
            content = cli_file.read_text()
            try:
                compile(content, str(cli_file), 'exec')
                print("✅ CLI file compiles successfully")
                
                # Check for key content
                if "command.options" in content:
                    print("✅ Found 'command.options' in CLI file")
                elif "command.opts" in content:
                    print("❌ Found 'command.opts' in CLI file - THIS IS THE BUG!")
                else:
                    print("⚠️  No command options references found")
                
                # Show the problematic line if it exists
                for i, line in enumerate(content.splitlines(), 1):
                    if "command.opts" in line:
                        print(f"   Line {i}: {line.strip()}")
                        
            except SyntaxError as e:
                print(f"❌ CLI file has syntax errors: {e}")
                print(f"   Line {e.lineno}: {e.text}")
        
        else:
            print("❌ No CLI files found")
        
        print(f"\n🗂️  Temp directory: {temp_dir}")
        print("   (Not cleaned up for inspection)")
        
    except Exception as e:
        print(f"❌ Debug test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()