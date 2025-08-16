#!/usr/bin/env python3
"""Debug script to create persistent CLI for debugging."""

import tempfile
import subprocess
import sys
from pathlib import Path

# Add src to path so we can import goobits_cli
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.tests.install.test_configs import TestConfigTemplates
from src.tests.install.test_integration_workflows import CLITestHelper
from src.tests.install.package_manager_utils import PipManager

def debug_persistent_cli():
    """Create a CLI and keep temp directory for debugging."""
    print("🔍 Creating persistent CLI for debugging...")
    
    # Create temp directory
    temp_dir = tempfile.mkdtemp(prefix="debug_persistent_cli_")
    print(f"📁 Created temp directory: {temp_dir}")
    
    try:
        # Generate Python CLI
        print("🛠️ Generating Python CLI...")
        config = TestConfigTemplates.minimal_config("python")
        generated_files = CLITestHelper.generate_cli(config, temp_dir)
        
        print(f"✅ Generated files: {list(generated_files.keys())}")
        for name, path in generated_files.items():
            print(f"   {name}: {path}")
        
        # List all files in temp directory
        print("📂 All files in temp directory:")
        for item in Path(temp_dir).rglob("*"):
            if item.is_file():
                print(f"   {item.relative_to(temp_dir)} ({item.stat().st_size} bytes)")
        
        # Install CLI
        print("📦 Installing CLI...")
        result = PipManager.install_editable(temp_dir)
        if result.returncode == 0:
            print("✅ Installation successful!")
        else:
            print(f"❌ Installation failed: {result.stderr}")
            return
        
        # Try to run the CLI and capture full error
        print(f"🧪 Testing CLI execution...")
        cli_path = f"/workspace/venv/bin/{config.command_name}"
        try:
            cli_result = subprocess.run([cli_path, '--help'], capture_output=True, text=True, timeout=10)
            if cli_result.returncode == 0:
                print("✅ CLI execution successful!")
                print(f"Output: {cli_result.stdout}")
            else:
                print(f"❌ CLI execution failed with return code {cli_result.returncode}")
                print(f"Full stderr: {cli_result.stderr}")
                print(f"Full stdout: {cli_result.stdout}")
        except Exception as e:
            print(f"❌ CLI execution error: {e}")
        
        print(f"\n🔍 Temp directory preserved at: {temp_dir}")
        print("You can examine the files manually and run the CLI directly:")
        print(f"   cd {temp_dir}")
        print(f"   {cli_path} --help")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_persistent_cli()