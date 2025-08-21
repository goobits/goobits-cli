#!/usr/bin/env python3
"""
Check the exact options line in generated CLI.
"""

import sys
import tempfile
from pathlib import Path

# Add the source directory to the path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from tests.integration.test_cross_language import EndToEndIntegrationTester


def main():
    """Check the options line in generated CLI."""
    print("🔍 Check Options Line in Generated CLI")
    print("=" * 50)
    
    tester = EndToEndIntegrationTester()
    
    try:
        # Create configuration exactly like integration test
        config = tester.create_comprehensive_test_config("python", "e2e_test")
        
        # Generate exactly like integration test
        generator = tester._get_generator("python")
        all_files = generator.generate_all_files(config, "e2e_test_python.yaml", "1.0.0")
        
        # Create temp directory exactly like integration test
        temp_dir = tempfile.mkdtemp(prefix="e2e_test_python_")
        
        # Write files exactly like integration test
        executable_files = all_files.pop('__executable__', [])
        for filename, content in all_files.items():
            file_path = Path(temp_dir) / filename
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(content)
        
        # Find and examine the CLI file
        cli_files = list(Path(temp_dir).rglob("cli.py"))
        if cli_files:
            cli_file = cli_files[0]
            content = cli_file.read_text()
            
            # Look for the problematic options line
            lines = content.splitlines()
            for i, line in enumerate(lines, 1):
                if "options = {" in line:
                    print(f"Line {i}: {line}")
                    # Show the next few lines
                    for j in range(i, min(i+5, len(lines))):
                        if j < len(lines):
                            print(f"Line {j+1}: {lines[j]}")
                    break
            else:
                print("No 'options = {' line found")
                
            # Also check if the template was properly applied
            if "options = {\n            'greeting': greeting," in content:
                print("✅ Template fix was applied correctly")
            elif "options = {            'greeting': greeting," in content:
                print("❌ Template fix NOT applied - whitespace issue persists")
            else:
                print("⚠️  Unexpected format")
                
        else:
            print("❌ No CLI file found")
            
        print(f"\nTemp directory: {temp_dir}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()