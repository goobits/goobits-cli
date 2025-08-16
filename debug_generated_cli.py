#!/usr/bin/env python3
"""Debug script to examine the generated CLI structure."""

import tempfile
import sys
from pathlib import Path

# Add src to path so we can import goobits_cli
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.tests.install.test_configs import TestConfigTemplates
from src.tests.install.test_integration_workflows import CLITestHelper

def debug_generated_cli():
    """Debug the generated CLI structure."""
    print("🔍 Debugging generated CLI structure...")
    
    # Create temp directory
    temp_dir = tempfile.mkdtemp(prefix="debug_cli_structure_")
    print(f"📁 Created temp directory: {temp_dir}")
    
    try:
        # Generate Python CLI
        print("🛠️ Generating Python CLI...")
        config = TestConfigTemplates.minimal_config("python")
        generated_files = CLITestHelper.generate_cli(config, temp_dir)
        
        # Examine the generated files
        for file_name, file_path in generated_files.items():
            print(f"\n📄 {file_name}: {file_path}")
            if Path(file_path).exists():
                print(f"   📏 Size: {Path(file_path).stat().st_size} bytes")
                if file_name == "cli_file":
                    # Show the first 20 lines of the CLI file
                    print("   📝 First 20 lines:")
                    with open(file_path, 'r') as f:
                        for i, line in enumerate(f):
                            if i >= 20:
                                break
                            print(f"   {i+1:2d}: {line.rstrip()}")
                elif file_name == "setup_file":
                    print("   📝 Setup.py content:")
                    with open(file_path, 'r') as f:
                        content = f.read()
                        # Focus on the entry points section
                        lines = content.split('\n')
                        in_entry_points = False
                        for line in lines:
                            if 'entry_points' in line:
                                in_entry_points = True
                            if in_entry_points:
                                print(f"     {line}")
                                if line.strip().endswith('},') or line.strip().endswith(')'):
                                    break
        
        # Check if the cli.py file has a main function
        cli_file = Path(generated_files["cli_file"])
        content = cli_file.read_text()
        if "def main(" in content:
            print("\n✅ CLI file has main() function")
        else:
            print("\n❌ CLI file missing main() function")
        
        # Check if it has proper imports
        if "import" in content:
            print("📦 Imports found in CLI file:")
            for line in content.split('\n'):
                if line.strip().startswith('import ') or line.strip().startswith('from '):
                    print(f"   {line.strip()}")
                    
    finally:
        # Cleanup
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)
        print(f"\n🧹 Cleaned up temp directory")

if __name__ == "__main__":
    debug_generated_cli()