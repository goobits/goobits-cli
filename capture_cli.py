#!/usr/bin/env python3
"""
Capture the generated CLI file for inspection.
"""

import sys
import tempfile
from pathlib import Path

# Add the source directory to the path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from tests.integration.test_cross_language import EndToEndIntegrationTester


def main():
    """Capture the generated CLI file."""
    print("📸 Capturing Generated CLI File")
    
    tester = EndToEndIntegrationTester()
    
    try:
        # Create configuration
        config = tester.create_comprehensive_test_config("python", "e2e_test")
        
        # Generate CLI
        generator = tester._get_generator("python") 
        all_files = generator.generate_all_files(config, "e2e_test_python.yaml", "1.0.0")
        
        # Create temp directory
        temp_dir = tempfile.mkdtemp(prefix="capture_cli_")
        
        # Write files
        executable_files = all_files.pop('__executable__', [])
        for filename, content in all_files.items():
            file_path = Path(temp_dir) / filename
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(content)
        
        # Create hooks
        hooks = tester.create_hook_implementations(temp_dir, "python")
        for hook_file, hook_content in hooks.items():
            hook_path = Path(temp_dir) / hook_file
            hook_path.write_text(hook_content)
        
        # Find and copy CLI file to workspace for inspection
        cli_files = list(Path(temp_dir).rglob("cli.py"))
        if cli_files:
            cli_file = cli_files[0]
            target_path = Path(__file__).parent / "captured_cli.py"
            target_path.write_text(cli_file.read_text())
            print(f"✅ CLI file captured to: {target_path}")
            print(f"Original location: {cli_file}")
            
            # Show the hello command definition
            content = cli_file.read_text()
            lines = content.splitlines()
            
            in_hello_command = False
            hello_lines = []
            
            for i, line in enumerate(lines):
                if "@main.command()" in line:
                    # Check if this is for hello command
                    next_lines = lines[i:i+20]  # Look ahead
                    if any("def hello" in l for l in next_lines):
                        in_hello_command = True
                        hello_lines = []
                
                if in_hello_command:
                    hello_lines.append(f"{i+1:3}: {line}")
                    if line.startswith("def ") and "hello" in line:
                        # Include a few more lines after the function definition
                        for j in range(i+1, min(i+30, len(lines))):
                            hello_lines.append(f"{j+1:3}: {lines[j]}")
                        break
            
            print(f"\n🔍 Hello command definition:")
            for line in hello_lines:
                print(line)
                
        else:
            print("❌ No CLI file found")
            
        print(f"\nTemp directory (not cleaned): {temp_dir}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()