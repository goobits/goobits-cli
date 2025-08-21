#!/usr/bin/env python3
"""
Debug CLI signature issue in integration test.
"""

import sys
import tempfile
import subprocess
from pathlib import Path

# Add the source directory to the path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from tests.integration.test_cross_language import EndToEndIntegrationTester


def main():
    """Debug CLI signature issue."""
    print("🔍 Debug CLI Signature Issue")
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
        
        # Create hooks exactly like integration test
        hooks = tester.create_hook_implementations(temp_dir, "python")
        for hook_file, hook_content in hooks.items():
            hook_path = Path(temp_dir) / hook_file
            hook_path.write_text(hook_content)
        
        # Find CLI file
        cli_files = list(Path(temp_dir).rglob("cli.py"))
        cli_file = cli_files[0]
        
        # Show the command signature
        content = cli_file.read_text()
        lines = content.splitlines()
        
        in_hello_cmd = False
        for i, line in enumerate(lines):
            if "@main.command()" in line and i < len(lines) - 10:
                # Check if the next few lines contain "hello"
                next_lines = lines[i:i+15]
                if any("def hello" in l for l in next_lines):
                    print("Hello command definition:")
                    for j in range(i, min(i+15, len(lines))):
                        print(f"  {j+1:3}: {lines[j]}")
                    break
        
        # Test the exact command from integration test
        print(f"\n🧪 Testing command: python {cli_file} hello World")
        
        result = subprocess.run([
            sys.executable, str(cli_file), "hello", "World"
        ], capture_output=True, text=True, cwd=temp_dir, timeout=10)
        
        print(f"Return code: {result.returncode}")
        print(f"Stdout: {result.stdout[:200]}...")
        print(f"Stderr: {result.stderr[:200]}...")
        
        # Test CLI help to see what arguments it expects
        print(f"\n📖 Command help:")
        help_result = subprocess.run([
            sys.executable, str(cli_file), "hello", "--help"
        ], capture_output=True, text=True, cwd=temp_dir, timeout=10)
        
        if help_result.returncode == 0:
            print(help_result.stdout)
        else:
            print(f"Help failed: {help_result.stderr}")
            
        print(f"Temp directory: {temp_dir}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()