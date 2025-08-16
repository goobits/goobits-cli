#!/usr/bin/env python3
"""Debug script to check app_hooks usage in generated CLI."""

import tempfile
import sys
from pathlib import Path

# Add src to path so we can import goobits_cli
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.tests.install.test_configs import TestConfigTemplates
from src.tests.install.test_integration_workflows import CLITestHelper

def debug_hooks_usage():
    """Debug how app_hooks is used in generated CLI."""
    print("🔍 Debugging app_hooks usage in generated CLI...")
    
    # Create temp directory
    temp_dir = tempfile.mkdtemp(prefix="debug_hooks_")
    print(f"📁 Created temp directory: {temp_dir}")
    
    try:
        # Generate Python CLI
        print("🛠️ Generating Python CLI...")
        config = TestConfigTemplates.minimal_config("python")
        generated_files = CLITestHelper.generate_cli(config, temp_dir)
        
        # Read the CLI file and look for hooks usage
        cli_file = Path(generated_files["cli_file"])
        content = cli_file.read_text()
        
        print("🔍 Looking for app_hooks usage:")
        lines = content.split('\n')
        for i, line in enumerate(lines, 1):
            if 'hooks' in line.lower() or 'app_hooks' in line.lower():
                print(f"   Line {i}: {line.strip()}")
        
        print("\n🔍 Looking for main function:")
        in_main = False
        for i, line in enumerate(lines, 1):
            if 'def main(' in line:
                in_main = True
                print(f"   Line {i}: {line.strip()}")
                # Show next 10 lines
                for j in range(1, 11):
                    if i + j - 1 < len(lines):
                        print(f"   Line {i+j}: {lines[i+j-1].strip()}")
                break
                    
    finally:
        # Cleanup
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)
        print(f"\n🧹 Cleaned up temp directory")

if __name__ == "__main__":
    debug_hooks_usage()