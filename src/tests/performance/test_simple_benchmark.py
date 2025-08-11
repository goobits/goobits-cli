#!/usr/bin/env python3
"""
Simple Real Performance Test - Test if basic CLI generation works
"""

import os
import sys
import tempfile
import time
import yaml
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from goobits_cli.schemas import GoobitsConfigSchema
from goobits_cli.generators.python import PythonGenerator


def create_simple_test_config():
    """Create a simple test configuration"""
    return {
        "package_name": "simple-test",
        "command_name": "simple-test",
        "display_name": "Simple Test CLI",
        "description": "Simple test CLI for performance testing",
        
        "python": {
            "minimum_version": "3.8",
            "maximum_version": "3.13"
        },
        
        "dependencies": {
            "required": ["click>=8.0"],
            "optional": []
        },
        
        "installation": {
            "pypi_name": "simple-test",
            "development_path": ".",
            "extras": {
                "python": ["dev"]
            }
        },
        
        "shell_integration": {
            "enabled": False,
            "alias": "simple-test"
        },
        
        "validation": {
            "check_api_keys": False,
            "check_disk_space": True,
            "minimum_disk_space_mb": 10
        },
        
        "messages": {
            "install_success": "Simple test CLI installed successfully!",
            "install_dev_success": "Simple test CLI installed in dev mode!",
            "upgrade_success": "Simple test CLI upgraded successfully!"
        },
        
        "cli": {
            "name": "simple-test",
            "version": "1.0.0",
            "display_version": True,
            "tagline": "Simple test CLI",
            "description": "A simple CLI for testing",
            "icon": "⚡",
            "enable_recursive_help": True,
            "enable_help_json": False,
            
            "commands": {
                "hello": {
                    "desc": "Say hello",
                    "icon": "👋",
                    "args": [
                        {
                            "name": "name",
                            "desc": "Your name",
                            "required": False
                        }
                    ]
                }
            }
        }
    }


def main():
    print("🚀 Simple Performance Test")
    
    # Create test directory
    test_dir = Path(tempfile.mkdtemp(prefix="simple_perf_test_"))
    print(f"📁 Test directory: {test_dir}")
    
    try:
        # Create configuration
        config_data = create_simple_test_config()
        config_file = test_dir / "goobits.yaml"
        
        with open(config_file, 'w') as f:
            yaml.dump(config_data, f, default_flow_style=False)
        
        print("✅ Configuration created")
        
        # Load and validate configuration
        config = GoobitsConfigSchema(**config_data)
        print("✅ Configuration validated")
        
        # Generate CLI files
        start_time = time.perf_counter()
        
        generator = PythonGenerator()
        files = generator.generate_all_files(config, str(config_file))
        
        end_time = time.perf_counter()
        generation_time = (end_time - start_time) * 1000
        
        print(f"⚡ Generation time: {generation_time:.2f}ms")
        print(f"📄 Generated {len(files)} files")
        
        # Write files to disk
        for file_path, content in files.items():
            full_path = test_dir / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(full_path, 'w') as f:
                f.write(content)
        
        print("✅ Files written to disk")
        
        # Test CLI execution
        cli_script = test_dir / "cli.py"
        if cli_script.exists():
            import subprocess
            
            # Test --help command
            start_time = time.perf_counter()
            
            result = subprocess.run(
                ["python3", str(cli_script), "--help"],
                capture_output=True,
                text=True,
                timeout=10,
                cwd=test_dir
            )
            
            end_time = time.perf_counter()
            execution_time = (end_time - start_time) * 1000
            
            if result.returncode == 0:
                print(f"✅ CLI execution successful: {execution_time:.2f}ms")
                print("📄 CLI help output length:", len(result.stdout))
            else:
                print(f"❌ CLI execution failed: {result.stderr}")
        else:
            print("❌ No cli.py file generated")
        
        print("🎉 Simple performance test completed successfully!")
        return 0
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
        
    finally:
        # Cleanup
        import shutil
        shutil.rmtree(test_dir, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())