#!/usr/bin/env python3
"""Debug TypeScript CLI dependency resolution test manually."""

import tempfile
import subprocess
import os
import sys
from pathlib import Path

# Add the source directory to Python path
sys.path.insert(0, '/workspace/src')

from tests.install.test_configs import TestConfigTemplates
from tests.install.test_installation_workflows import CLITestHelper

def debug_typescript_cli():
    """Debug the TypeScript CLI generation and installation process."""
    print("=== DEBUGGING TYPESCRIPT CLI DEPENDENCY TEST ===")
    
    # Create temporary directory
    temp_dir = tempfile.mkdtemp(prefix="debug_typescript_cli_")
    print(f"Using temp directory: {temp_dir}")
    
    try:
        # 1. Generate configuration
        print("\n1. Generating configuration...")
        config = TestConfigTemplates.dependency_heavy_config("typescript")
        print(f"Package name: {config.package_name}")
        print(f"Command name: {config.command_name}")
        print(f"Language: {config.language}")
        
        # 2. Generate CLI files
        print("\n2. Generating CLI files...")
        generated_files = CLITestHelper.generate_cli(config, temp_dir)
        print(f"Generated files: {generated_files}")
        
        # 3. List some key files
        print("\n3. Key files:")
        cli_file = Path(generated_files.get("cli_file", ""))
        package_json = Path(generated_files.get("package_file", ""))
        tsconfig = Path(generated_files.get("tsconfig_file", ""))
        
        print(f"CLI file exists: {cli_file.exists()} - {cli_file}")
        print(f"package.json exists: {package_json.exists()} - {package_json}")
        print(f"tsconfig.json exists: {tsconfig.exists()} - {tsconfig}")
        
        # 4. Check CLI file permissions if it exists
        if cli_file.exists() and cli_file.suffix == '.ts':
            print(f"\n4. CLI file permissions:")
            stat = cli_file.stat()
            permissions = oct(stat.st_mode)[-3:]
            print(f"Permissions: {permissions}")
            print(f"File size: {stat.st_size} bytes")
            
            print(f"\n4. CLI file content (first 20 lines):")
            content = cli_file.read_text()
            lines = content.split('\n')[:20]
            for i, line in enumerate(lines, 1):
                print(f"{i:2d}: {line}")
        
        # 5. Try npm install
        print(f"\n5. Attempting npm install:")
        result = subprocess.run([
            "npm", "install"
        ], capture_output=True, text=True, timeout=60, cwd=temp_dir)
        print(f"npm install return code: {result.returncode}")
        print(f"npm install STDERR (last 500 chars): {result.stderr[-500:]}")
        
        if result.returncode == 0:
            print("npm install successful!")
            
            # 6. Try TypeScript build
            print(f"\n6. Attempting TypeScript build:")
            result = subprocess.run([
                "npm", "run", "build"
            ], capture_output=True, text=True, timeout=60, cwd=temp_dir)
            print(f"TypeScript build return code: {result.returncode}")
            print(f"Build STDOUT (last 500 chars): {result.stdout[-500:]}")
            print(f"Build STDERR (last 500 chars): {result.stderr[-500:]}")
            
            if result.returncode == 0:
                print("TypeScript build successful!")
                
                # Check if dist directory was created
                dist_dir = Path(temp_dir) / "dist"
                if dist_dir.exists():
                    print(f"Dist directory created with files:")
                    for file in dist_dir.rglob("*"):
                        if file.is_file():
                            rel_path = file.relative_to(dist_dir)
                            print(f"  {rel_path} ({file.stat().st_size} bytes)")
                else:
                    print("No dist directory found")
            else:
                print("TypeScript build failed!")
        else:
            print("npm install failed!")
        
    except Exception as e:
        print(f"Exception: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        # Cleanup
        import shutil
        print(f"\nCleaning up: {temp_dir}")
        shutil.rmtree(temp_dir, ignore_errors=True)

if __name__ == "__main__":
    debug_typescript_cli()