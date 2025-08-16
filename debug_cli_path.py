#!/usr/bin/env python3
"""Debug script to check CLI installation and PATH."""

import tempfile
import subprocess
import sys
import os
from pathlib import Path

# Add src to path so we can import goobits_cli
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.tests.install.test_configs import TestConfigTemplates
from src.tests.install.test_integration_workflows import CLITestHelper
from src.tests.install.package_manager_utils import PipManager

def debug_cli_path():
    """Debug CLI installation and PATH availability."""
    print("🔍 Debugging CLI PATH availability...")
    
    # Create temp directory
    temp_dir = tempfile.mkdtemp(prefix="debug_cli_path_")
    print(f"📁 Created temp directory: {temp_dir}")
    
    try:
        # Generate Python CLI
        print("🛠️ Generating Python CLI...")
        config = TestConfigTemplates.minimal_config("python")
        print(f"📋 Command name: {config.command_name}")
        print(f"📋 Package name: {config.package_name}")
        
        generated_files = CLITestHelper.generate_cli(config, temp_dir)
        print(f"✅ Generated files: {generated_files}")
        
        # Check generated setup.py for entry points
        setup_file = Path(temp_dir) / "setup.py"
        if setup_file.exists():
            content = setup_file.read_text()
            print("📄 Setup.py entry points section:")
            for line in content.split('\n'):
                if 'entry_points' in line or 'console_scripts' in line or config.command_name in line:
                    print(f"  {line.strip()}")
        
        # Install CLI
        print("📦 Installing CLI...")
        result = PipManager.install_editable(temp_dir)
        if result.returncode == 0:
            print("✅ Installation successful!")
        else:
            print(f"❌ Installation failed: {result.stderr}")
            return
        
        # Check if CLI is in PATH
        print(f"🔍 Checking if '{config.command_name}' is in PATH...")
        cli_which = subprocess.run(['which', config.command_name], capture_output=True, text=True)
        if cli_which.returncode == 0:
            print(f"✅ CLI found at: {cli_which.stdout.strip()}")
        else:
            print(f"❌ CLI not found in PATH")
        
        # List installed packages to see if our package is there
        print("📋 Checking pip list for our package...")
        pip_list = subprocess.run([sys.executable, '-m', 'pip', 'list'], capture_output=True, text=True)
        for line in pip_list.stdout.split('\n'):
            if config.package_name in line:
                print(f"✅ Package found: {line}")
        
        # Check available console scripts
        print("🔍 Checking console scripts...")
        try:
            import pkg_resources
            for entry_point in pkg_resources.iter_entry_points('console_scripts'):
                if config.command_name in str(entry_point):
                    print(f"✅ Console script found: {entry_point}")
        except Exception as e:
            print(f"❌ Error checking console scripts: {e}")
        
        # Try running the CLI directly
        print(f"🧪 Testing CLI execution...")
        try:
            cli_result = subprocess.run([config.command_name, '--help'], capture_output=True, text=True, timeout=10)
            if cli_result.returncode == 0:
                print("✅ CLI execution successful!")
                print(f"Output: {cli_result.stdout[:200]}...")
            else:
                print(f"❌ CLI execution failed with return code {cli_result.returncode}")
                print(f"Stderr: {cli_result.stderr}")
        except FileNotFoundError:
            print(f"❌ CLI command '{config.command_name}' not found")
        except Exception as e:
            print(f"❌ CLI execution error: {e}")
            
    finally:
        # Cleanup
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)
        print(f"🧹 Cleaned up temp directory")

if __name__ == "__main__":
    debug_cli_path()