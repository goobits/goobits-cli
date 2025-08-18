#!/usr/bin/env python3
"""Debug Node.js CLI dependency resolution test manually."""

import tempfile
import subprocess
import os
import sys
from pathlib import Path

# Add the source directory to Python path
sys.path.insert(0, '/workspace/src')

from tests.install.test_configs import TestConfigTemplates
from tests.install.test_installation_workflows import CLITestHelper
from tests.install.package_manager_utils import NpmManager, validate_installation_environment

def debug_nodejs_cli():
    """Debug the Node.js CLI generation and installation process."""
    print("=== DEBUGGING NODE.JS CLI DEPENDENCY TEST ===")
    
    # Create temporary directory
    temp_dir = tempfile.mkdtemp(prefix="debug_nodejs_cli_")
    print(f"Using temp directory: {temp_dir}")
    
    try:
        # 1. Generate configuration
        print("\n1. Generating configuration...")
        config = TestConfigTemplates.dependency_heavy_config("nodejs")
        print(f"Package name: {config.package_name}")
        print(f"Command name: {config.command_name}")
        print(f"Language: {config.language}")
        
        # 2. Generate CLI files
        print("\n2. Generating CLI files...")
        generated_files = CLITestHelper.generate_cli(config, temp_dir)
        print(f"Generated files: {generated_files}")
        
        # 3. List generated files
        print("\n3. Listing generated files:")
        for root, dirs, files in os.walk(temp_dir):
            level = root.replace(temp_dir, '').count(os.sep)
            indent = ' ' * 2 * level
            print(f"{indent}{os.path.basename(root)}/")
            subindent = ' ' * 2 * (level + 1)
            for file in files:
                file_path = os.path.join(root, file)
                size = os.path.getsize(file_path)
                print(f"{subindent}{file} ({size} bytes)")
        
        # 4. Check key files exist
        print("\n4. Checking key files:")
        cli_file = Path(generated_files.get("cli_file", ""))
        package_json = Path(generated_files.get("package_file", ""))
        
        print(f"CLI file exists: {cli_file.exists()} - {cli_file}")
        print(f"package.json exists: {package_json.exists()} - {package_json}")
        
        # 5. Check CLI file permissions and content
        if cli_file.exists():
            print(f"\n5. CLI file permissions:")
            stat = cli_file.stat()
            permissions = oct(stat.st_mode)[-3:]
            print(f"Permissions: {permissions}")
            print(f"Is executable: {os.access(cli_file, os.X_OK)}")
            
            print(f"\n5. CLI file content (first 30 lines):")
            content = cli_file.read_text()
            lines = content.split('\n')[:30]
            for i, line in enumerate(lines, 1):
                print(f"{i:2d}: {line}")
        
        # 6. Check package.json content
        if package_json.exists():
            print(f"\n6. package.json content:")
            content = package_json.read_text()
            print(content)
        
        # 7. Try to run CLI directly without installation
        print(f"\n7. Testing CLI direct execution:")
        try:
            result = subprocess.run([
                "node", str(cli_file), "--help"
            ], capture_output=True, text=True, timeout=10, cwd=temp_dir)
            print(f"Direct execution return code: {result.returncode}")
            print(f"STDOUT: {result.stdout}")
            print(f"STDERR: {result.stderr}")
        except Exception as e:
            print(f"Direct execution failed: {e}")
        
        # 8. Check environment info
        print(f"\n8. Environment info:")
        env_info = validate_installation_environment()
        print(f"Environment info: {env_info}")
        print(f"npm available: {NpmManager.is_available()}")
        
        # 9. Attempt npm install
        print(f"\n9. Attempting npm installation:")
        try:
            print(f"Installing from: {temp_dir}")
            # Use direct npm commands for debugging
            result = subprocess.run([
                "npm", "install"
            ], capture_output=True, text=True, timeout=60, cwd=temp_dir)
            print(f"npm install return code: {result.returncode}")
            print(f"npm install STDOUT: {result.stdout}")
            print(f"npm install STDERR: {result.stderr}")
            
            if result.returncode == 0:
                print("npm install successful!")
                
                # 10. Try npm link
                print(f"\n10. Attempting npm link:")
                result = subprocess.run([
                    "npm", "link"
                ], capture_output=True, text=True, timeout=60, cwd=temp_dir)
                print(f"npm link return code: {result.returncode}")
                print(f"npm link STDOUT: {result.stdout}")
                print(f"npm link STDERR: {result.stderr}")
                
                if result.returncode == 0:
                    print("npm link successful!")
                    
                    # 11. Test installed CLI
                    print(f"\n11. Testing linked CLI:")
                    command_name = config.command_name
                    
                    # Test --help
                    try:
                        result = subprocess.run([
                            command_name, "--help"
                        ], capture_output=True, text=True, timeout=10)
                        print(f"--help return code: {result.returncode}")
                        print(f"--help STDOUT: {result.stdout}")
                        print(f"--help STDERR: {result.stderr}")
                    except FileNotFoundError:
                        print(f"Command '{command_name}' not found in PATH")
                        # Check what's in PATH
                        print("PATH contents:")
                        for p in os.environ.get("PATH", "").split(":"):
                            if os.path.exists(p):
                                try:
                                    files = [f for f in os.listdir(p) if command_name in f]
                                    if files:
                                        print(f"  {p}: {files}")
                                except PermissionError:
                                    pass
                    
                    # Test --version
                    try:
                        result = subprocess.run([
                            command_name, "--version"
                        ], capture_output=True, text=True, timeout=10)
                        print(f"--version return code: {result.returncode}")
                        print(f"--version STDOUT: {result.stdout}")
                        print(f"--version STDERR: {result.stderr}")
                    except FileNotFoundError:
                        print(f"Command '{command_name}' not found in PATH for --version")
                else:
                    print("npm link failed!")
            else:
                print("npm install failed!")
                
        except Exception as e:
            print(f"Installation exception: {e}")
        
    finally:
        # Cleanup
        import shutil
        print(f"\nCleaning up: {temp_dir}")
        shutil.rmtree(temp_dir, ignore_errors=True)

if __name__ == "__main__":
    debug_nodejs_cli()