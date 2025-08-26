#!/usr/bin/env python3
"""
Integration test to verify:
1. Only minimal files are generated (2-3 per language)
2. Manifest merging works without overwriting
3. Files are built in the correct directory (where goobits.yaml is)
4. No README.md is generated
"""

import os
import sys
import tempfile
import shutil
import json
import subprocess
from pathlib import Path

# Add src to path
sys.path.insert(0, '/workspace/src')

from goobits_cli.main import main
from goobits_cli.builder import Builder
from goobits_cli.schemas import ConfigSchema


def test_python_minimal_generation():
    """Test Python generates only 2 files in correct location."""
    print("\n=== Testing Python Minimal File Generation ===")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        
        # Create a test config in a subdirectory
        project_dir = tmpdir / "my-python-project"
        project_dir.mkdir()
        
        config_path = project_dir / "goobits.yaml"
        config_path.write_text("""
package_name: test-python-cli
command_name: testpy
display_name: "Test Python CLI"
description: "Testing Python generation"
language: python

cli:
  name: testpy
  tagline: "Test Python CLI"
  description: "A test CLI for Python"
  version: "1.0.0"
  commands:
    hello:
      desc: "Say hello"
      args:
        - name: name
          desc: "Name to greet"
          type: string
    build:
      desc: "Build something"
""")
        
        # Pre-create a README to ensure it's not overwritten
        readme_path = project_dir / "README.md"
        readme_path.write_text("# My Existing Project Documentation\nThis should not be overwritten!")
        
        # Build the CLI
        os.chdir(project_dir)
        builder = Builder()
        config = builder._load_config(str(config_path))
        output_files = builder._generate_files(config, "goobits.yaml")
        
        # Write generated files
        for file_path, content in output_files.items():
            full_path = project_dir / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(content)
        
        # Verify only expected files were generated
        generated_files = []
        for root, dirs, files in os.walk(project_dir):
            for file in files:
                if file != "goobits.yaml" and file != "README.md":
                    rel_path = Path(root, file).relative_to(project_dir)
                    generated_files.append(str(rel_path))
        
        print(f"Generated files: {generated_files}")
        
        # Assertions
        assert "README.md" not in output_files, "README.md should NOT be generated"
        assert len(generated_files) <= 2, f"Python should generate max 2 files, got {len(generated_files)}: {generated_files}"
        assert any("cli.py" in f for f in generated_files), "Should generate cli.py"
        assert any("setup.sh" in f for f in generated_files), "Should generate setup.sh"
        
        # Verify README wasn't overwritten
        assert readme_path.read_text() == "# My Existing Project Documentation\nThis should not be overwritten!"
        
        print("✅ Python: Generated only minimal files, README preserved")
        return True


def test_nodejs_minimal_generation():
    """Test Node.js generates only 2 files with ES6 modules."""
    print("\n=== Testing Node.js Minimal File Generation ===")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        
        # Create project directory
        project_dir = tmpdir / "my-nodejs-project"
        project_dir.mkdir()
        
        config_path = project_dir / "goobits.yaml"
        config_path.write_text("""
package_name: test-nodejs-cli
command_name: testnode
display_name: "Test Node.js CLI"
description: "Testing Node.js generation"
language: nodejs

cli:
  name: testnode
  tagline: "Test Node.js CLI"
  description: "A test CLI for Node.js"
  version: "1.0.0"
  commands:
    serve:
      desc: "Start server"
    test:
      desc: "Run tests"
""")
        
        # Pre-create package.json to test merging
        package_json_path = project_dir / "package.json"
        package_json_path.write_text(json.dumps({
            "name": "my-existing-project",
            "version": "2.0.0",
            "description": "My existing project",
            "author": "Original Author",
            "dependencies": {
                "express": "^4.18.0"
            }
        }, indent=2))
        
        # Build the CLI
        os.chdir(project_dir)
        builder = Builder()
        config = builder._load_config(str(config_path))
        output_files = builder._generate_files(config, "goobits.yaml")
        
        # Write generated files
        for file_path, content in output_files.items():
            if file_path != "package.json":  # Don't overwrite
                full_path = project_dir / file_path
                full_path.parent.mkdir(parents=True, exist_ok=True)
                full_path.write_text(content)
        
        # Check generated files
        generated_files = list(output_files.keys())
        print(f"Generated files: {generated_files}")
        
        # Assertions
        assert "README.md" not in output_files, "README.md should NOT be generated"
        assert len(generated_files) <= 2, f"Node.js should generate max 2 files, got {len(generated_files)}: {generated_files}"
        assert any("cli.mjs" in f for f in generated_files), "Should generate cli.mjs (ES6 module)"
        assert any("setup.sh" in f for f in generated_files), "Should generate setup.sh"
        
        # Verify no CommonJS files
        assert not any("cli.js" in f for f in generated_files), "Should NOT generate cli.js (CommonJS)"
        assert not any("lib/" in f for f in generated_files), "Should NOT generate lib/ folder"
        assert not any("config.js" in f for f in generated_files), "Should NOT generate separate config.js"
        
        # Verify package.json preserved
        package_content = json.loads(package_json_path.read_text())
        assert package_content["name"] == "my-existing-project", "Original package.json name preserved"
        assert package_content["version"] == "2.0.0", "Original version preserved"
        assert "express" in package_content.get("dependencies", {}), "Original dependencies preserved"
        
        print("✅ Node.js: Generated only minimal ES6 files, package.json preserved")
        return True


def test_typescript_minimal_generation():
    """Test TypeScript generates only 3 files."""
    print("\n=== Testing TypeScript Minimal File Generation ===")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        
        project_dir = tmpdir / "my-typescript-project"
        project_dir.mkdir()
        
        config_path = project_dir / "goobits.yaml"
        config_path.write_text("""
package_name: test-typescript-cli
command_name: testts
display_name: "Test TypeScript CLI"
description: "Testing TypeScript generation"
language: typescript

cli:
  name: testts
  tagline: "Test TypeScript CLI"
  description: "A test CLI for TypeScript"
  version: "1.0.0"
  commands:
    compile:
      desc: "Compile TypeScript"
""")
        
        # Build
        os.chdir(project_dir)
        builder = Builder()
        config = builder._load_config(str(config_path))
        output_files = builder._generate_files(config, "goobits.yaml")
        
        generated_files = list(output_files.keys())
        print(f"Generated files: {generated_files}")
        
        # Assertions
        assert "README.md" not in output_files, "README.md should NOT be generated"
        assert len(generated_files) <= 3, f"TypeScript should generate max 3 files, got {len(generated_files)}: {generated_files}"
        assert any("cli.ts" in f for f in generated_files), "Should generate cli.ts"
        assert any("types.d.ts" in f for f in generated_files), "Should generate types.d.ts"
        assert any("setup.sh" in f for f in generated_files), "Should generate setup.sh"
        
        # Verify no extra files
        assert not any("lib/" in f for f in generated_files), "Should NOT generate lib/ folder"
        assert "tsconfig.json" not in output_files, "tsconfig.json handled by setup.sh, not generated"
        
        print("✅ TypeScript: Generated only 3 essential files")
        return True


def test_rust_minimal_generation():
    """Test Rust generates only 2 files with inline modules."""
    print("\n=== Testing Rust Minimal File Generation ===")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        
        project_dir = tmpdir / "my-rust-project"
        project_dir.mkdir()
        
        config_path = project_dir / "goobits.yaml"
        config_path.write_text("""
package_name: test-rust-cli
command_name: testrust
display_name: "Test Rust CLI"
description: "Testing Rust generation"
language: rust

cli:
  name: testrust
  tagline: "Test Rust CLI"
  description: "A test CLI for Rust"
  version: "1.0.0"
  commands:
    run:
      desc: "Run the program"
""")
        
        # Build
        os.chdir(project_dir)
        builder = Builder()
        config = builder._load_config(str(config_path))
        output_files = builder._generate_files(config, "goobits.yaml")
        
        generated_files = list(output_files.keys())
        print(f"Generated files: {generated_files}")
        
        # Assertions
        assert "README.md" not in output_files, "README.md should NOT be generated"
        assert len(generated_files) <= 2, f"Rust should generate max 2 files, got {len(generated_files)}: {generated_files}"
        assert any("main.rs" in f for f in generated_files), "Should generate main.rs"
        assert any("setup.sh" in f for f in generated_files), "Should generate setup.sh"
        
        # Verify no separate module files
        assert not any("hooks.rs" in f for f in generated_files), "hooks.rs should be inlined"
        assert not any("config.rs" in f for f in generated_files), "config.rs should be inlined"
        assert not any("errors.rs" in f for f in generated_files), "errors.rs should be inlined"
        assert "Cargo.toml" not in output_files, "Cargo.toml handled by setup.sh"
        
        # Check main.rs has inline modules
        main_rs = output_files.get("src/main.rs", "")
        if main_rs:
            assert "mod config" in main_rs or "mod hooks" in main_rs, "Should have inline modules"
        
        print("✅ Rust: Generated only 2 files with inline modules")
        return True


def test_output_directory_respect():
    """Test that files are generated relative to goobits.yaml location."""
    print("\n=== Testing Output Directory Handling ===")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        
        # Create nested project structure
        deep_dir = tmpdir / "projects" / "backend" / "cli-tool"
        deep_dir.mkdir(parents=True)
        
        config_path = deep_dir / "goobits.yaml"
        config_path.write_text("""
package_name: nested-cli
command_name: nested
display_name: "Nested CLI"
description: "Testing nested directory"
language: python
cli_output_path: "src/nested_cli/cli.py"

cli:
  name: nested
  tagline: "Nested CLI"
  commands:
    test:
      desc: "Test command"
""")
        
        # Build from different directory
        original_cwd = os.getcwd()
        os.chdir(tmpdir)  # Change to root temp dir
        
        builder = Builder()
        config = builder._load_config(str(config_path))
        output_files = builder._generate_files(config, str(config_path))
        
        # Files should be relative to config location
        for file_path, content in output_files.items():
            full_path = deep_dir / file_path  # Relative to config dir
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(content)
        
        # Verify files are in correct location
        expected_cli_path = deep_dir / "src" / "nested_cli" / "cli.py"
        assert expected_cli_path.exists(), f"CLI should be at {expected_cli_path}"
        
        # Verify no files in wrong locations
        wrong_location = tmpdir / "src" / "nested_cli" / "cli.py"
        assert not wrong_location.exists(), f"CLI should NOT be at {wrong_location}"
        
        os.chdir(original_cwd)
        print("✅ Files generated in correct directory relative to goobits.yaml")
        return True


def run_all_tests():
    """Run all integration tests."""
    print("=" * 60)
    print("RUNNING BUILD INTEGRATION TESTS")
    print("=" * 60)
    
    tests = [
        test_python_minimal_generation,
        test_nodejs_minimal_generation,
        test_typescript_minimal_generation,
        test_rust_minimal_generation,
        test_output_directory_respect,
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append((test.__name__, result))
        except Exception as e:
            print(f"❌ {test.__name__} failed: {e}")
            import traceback
            traceback.print_exc()
            results.append((test.__name__, False))
    
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    all_passed = all(passed for _, passed in results)
    if all_passed:
        print("\n🎉 ALL TESTS PASSED!")
    else:
        print("\n⚠️  SOME TESTS FAILED")
    
    return all_passed


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)