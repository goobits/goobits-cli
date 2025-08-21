#!/usr/bin/env python3
"""
Debug script to understand the exact issue with the integration test.
"""
import sys
import tempfile
import subprocess
from pathlib import Path

# Add the source path
sys.path.insert(0, '/workspace/src')

from tests.integration.test_cross_language import EndToEndIntegrationTester

def main():
    print("🔍 Debugging the exact integration test issue...")
    
    tester = EndToEndIntegrationTester()
    
    # Create a test config for Python
    config = tester.create_comprehensive_test_config("python", "debug_test")
    print(f"✅ Created config with language: {config.language}")
    
    # Generate CLI code
    generator = tester._get_generator("python")
    print(f"✅ Created generator with use_universal_templates: {generator.use_universal_templates}")
    
    all_files = generator.generate_all_files(config, "debug_test_python.yaml", "1.0.0")
    print(f"✅ Generated {len(all_files)} files:")
    for filename in all_files.keys():
        print(f"   - {filename}")
    
    # Create temp directory and write files
    temp_dir = tempfile.mkdtemp(prefix="debug_exact_")
    print(f"✅ Created temp dir: {temp_dir}")
    
    # Write all files
    executable_files = all_files.pop('__executable__', [])
    for filename, content in all_files.items():
        file_path = Path(temp_dir) / filename
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content)
        
        if filename in executable_files or filename.startswith('bin/') or filename == 'setup.sh':
            file_path.chmod(0o755)
        
        print(f"   Wrote: {file_path}")
    
    # Create hook files exactly like the test
    hooks = tester.create_hook_implementations(temp_dir, "python")
    for hook_file, hook_content in hooks.items():
        hook_path = Path(temp_dir) / hook_file
        hook_path.parent.mkdir(parents=True, exist_ok=True)
        hook_path.write_text(hook_content)
        print(f"   Created hook: {hook_path}")
    
    print(f"\\n📁 Final directory structure:")
    for item in sorted(Path(temp_dir).rglob("*")):
        if item.is_file():
            print(f"   {item.relative_to(temp_dir)}")
    
    # Now test CLI finding logic exactly like the integration test
    print(f"\\n🔍 Testing CLI finding logic...")
    cli_file = tester._find_cli_file(temp_dir, all_files, "python")
    print(f"   Found CLI file: {cli_file}")
    
    if cli_file:
        print(f"   CLI file exists: {cli_file.exists()}")
        print(f"   CLI file is file: {cli_file.is_file()}")
        
        # Test help command
        print(f"\\n📋 Testing help command...")
        try:
            help_result = subprocess.run([
                sys.executable, str(cli_file), "--help"
            ], capture_output=True, text=True, cwd=temp_dir, timeout=30)
            
            print(f"   Return code: {help_result.returncode}")
            if help_result.returncode == 0:
                help_text = help_result.stdout.lower()
                expected_commands = ["hello", "count", "config", "status"]
                found_commands = [cmd for cmd in expected_commands if cmd in help_text]
                print(f"   Found commands: {found_commands}")
                
                if len(found_commands) >= 2:
                    # Test hello command
                    print(f"\\n👋 Testing hello command...")
                    hello_result = subprocess.run([
                        sys.executable, str(cli_file), "hello", "World"
                    ], capture_output=True, text=True, cwd=temp_dir, timeout=30)
                    
                    print(f"   Return code: {hello_result.returncode}")
                    print(f"   STDOUT: '{hello_result.stdout}'")
                    print(f"   STDERR: '{hello_result.stderr}'")
                    
                    if "HOOK_EXECUTED" in hello_result.stdout:
                        print(f"   ✅ Hook executed successfully!")
                    else:
                        print(f"   ❌ Hook NOT executed")
                        
                        # Debug more details
                        if hello_result.returncode != 0:
                            print(f"   ❌ Command failed - that's why hook not executed")
                        else:
                            print(f"   ❓ Command succeeded but no HOOK_EXECUTED output")
                            
                else:
                    print(f"   ❌ Not enough commands found in help: {found_commands}")
            else:
                print(f"   ❌ Help command failed")
                print(f"   STDERR: {help_result.stderr}")
        except Exception as e:
            print(f"   ❌ Exception during help test: {e}")
    else:
        print(f"   ❌ No CLI file found!")
        print(f"   Available files in temp_dir:")
        for item in Path(temp_dir).rglob("*.py"):
            print(f"     {item}")

if __name__ == "__main__":
    main()