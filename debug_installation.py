#!/usr/bin/env python3
"""Debug script to understand installation failures."""

import tempfile
import subprocess
import sys
from pathlib import Path

# Add src to path so we can import goobits_cli
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.tests.install.test_configs import TestConfigTemplates
from src.tests.install.test_integration_workflows import CLITestHelper
from src.tests.install.package_manager_utils import PipManager

def debug_python_installation():
    """Debug Python CLI installation step by step."""
    print("🔍 Debugging Python CLI installation...")
    
    # Create temp directory
    temp_dir = tempfile.mkdtemp(prefix="debug_install_")
    print(f"📁 Created temp directory: {temp_dir}")
    
    try:
        # Generate Python CLI
        print("🛠️ Generating Python CLI...")
        config = TestConfigTemplates.minimal_config("python")
        generated_files = CLITestHelper.generate_cli(config, temp_dir)
        
        print(f"✅ Generated files: {generated_files}")
        
        # List files in temp directory
        print("📂 Files in temp directory:")
        for item in Path(temp_dir).rglob("*"):
            if item.is_file():
                print(f"  - {item.relative_to(temp_dir)}")
        
        # Check if pip is available
        print(f"🔧 Pip available: {PipManager.is_available()}")
        
        # Try to install and capture detailed error
        print("📦 Attempting pip installation...")
        try:
            result = PipManager.install_editable(temp_dir)
            print(f"✅ Installation successful! Return code: {result.returncode}")
            print(f"📤 Stdout: {result.stdout}")
            print(f"📤 Stderr: {result.stderr}")
        except subprocess.CalledProcessError as e:
            print(f"❌ Installation failed with CalledProcessError!")
            print(f"Return code: {e.returncode}")
            print(f"Command: {e.cmd}")
            print(f"Stdout: {e.stdout}")
            print(f"Stderr: {e.stderr}")
        except Exception as e:
            print(f"❌ Installation failed with unexpected error: {e}")
            print(f"Error type: {type(e)}")
            
    finally:
        # Cleanup
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)
        print(f"🧹 Cleaned up temp directory")

if __name__ == "__main__":
    debug_python_installation()