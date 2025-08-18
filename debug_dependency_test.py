#!/usr/bin/env python3
"""Debug dependency resolution test manually."""

import tempfile
import subprocess
import os
import sys
from pathlib import Path

# Add the source directory to Python path
sys.path.insert(0, '/workspace/src')

from tests.install.test_configs import TestConfigTemplates
from tests.install.test_installation_workflows import CLITestHelper
from tests.install.package_manager_utils import PipManager, validate_installation_environment

def debug_python_cli():
    """Debug the Python CLI generation and installation process."""
    print("=== DEBUGGING PYTHON CLI DEPENDENCY TEST ===")
    
    # Create temporary directory
    temp_dir = tempfile.mkdtemp(prefix="debug_python_cli_")
    print(f"Using temp directory: {temp_dir}")
    
    try:
        # 1. Generate configuration
        print("\n1. Generating configuration...")
        config = TestConfigTemplates.dependency_heavy_config("python")
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
        setup_py = Path(temp_dir) / "setup.py" 
        pyproject_toml = Path(temp_dir) / "pyproject.toml"
        
        print(f"CLI file exists: {cli_file.exists()} - {cli_file}")
        print(f"setup.py exists: {setup_py.exists()} - {setup_py}")
        print(f"pyproject.toml exists: {pyproject_toml.exists()} - {pyproject_toml}")
        
        # 5. Check CLI file content (first 50 lines)
        if cli_file.exists():
            print(f"\n5. CLI file content (first 50 lines):")
            content = cli_file.read_text()
            lines = content.split('\n')[:50]
            for i, line in enumerate(lines, 1):
                print(f"{i:2d}: {line}")
        
        # 6. Check installation files
        if pyproject_toml.exists():
            print(f"\n6. pyproject.toml content:")
            content = pyproject_toml.read_text()
            print(content)
        elif setup_py.exists():
            print(f"\n6. setup.py content:")
            content = setup_py.read_text()
            print(content)
        
        # 7. Try to run CLI directly without installation
        print(f"\n7. Testing CLI direct execution:")
        try:
            result = subprocess.run([
                sys.executable, str(cli_file), "--help"
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
        print(f"pip available: {PipManager.is_available()}")
        
        # 9. Attempt pip installation
        print(f"\n9. Attempting pip installation:")
        try:
            print(f"Installing from: {temp_dir}")
            # Use direct pip command for debugging
            result = subprocess.run([
                sys.executable, "-m", "pip", "install", "-e", temp_dir
            ], capture_output=True, text=True, timeout=60)
            print(f"Installation return code: {result.returncode}")
            print(f"Installation STDOUT: {result.stdout}")
            print(f"Installation STDERR: {result.stderr}")
            
            if result.returncode == 0:
                print("Installation successful!")
                
                # 10. Test installed CLI
                print(f"\n10. Testing installed CLI:")
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
                print("Installation failed!")
                
        except Exception as e:
            print(f"Installation exception: {e}")
        
    finally:
        # Cleanup
        import shutil
        print(f"\nCleaning up: {temp_dir}")
        shutil.rmtree(temp_dir, ignore_errors=True)

if __name__ == "__main__":
    debug_python_cli()