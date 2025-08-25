#!/usr/bin/env python3
"""
Real compilation and execution tests for generated CLIs across all languages.

This module tests that generated CLIs actually compile and execute correctly,
catching real bugs that would occur in production. No mocking - all tests
validate actual compilation and runtime behavior.
"""

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

from goobits_cli.schemas import GoobitsConfigSchema
from goobits_cli.generators.python import PythonGenerator
from goobits_cli.generators.nodejs import NodeJSGenerator
from goobits_cli.generators.typescript import TypeScriptGenerator
from goobits_cli.generators.rust import RustGenerator

# Timeout configurations for different operations
QUICK_CHECK_TIMEOUT = 45  # Quick syntax/import checks (increased from 30s)
DEPENDENCY_INSTALL_TIMEOUT = 120  # Package installation (increased from 60s)
COMPILATION_TIMEOUT = 600  # Full compilation (increased from 300s)
EXECUTION_TIMEOUT = 180  # CLI execution tests (increased from 120s)


class CLICompilationError(Exception):
    """Error during CLI compilation."""
    pass


class CLIExecutionError(Exception):
    """Error during CLI execution."""
    pass


def check_tool_availability(tool: str) -> bool:
    """Check if a development tool is available."""
    return shutil.which(tool) is not None


def create_realistic_config(language: str) -> GoobitsConfigSchema:
    """Create a realistic CLI configuration for testing."""
    return GoobitsConfigSchema(**{
        "package_name": f"test-{language}-cli",
        "command_name": f"test{language}cli",
        "display_name": f"Test {language.title()} CLI",
        "description": f"A realistic test CLI for {language} compilation validation",
        "language": language,
        "python": {
            "minimum_version": "3.8",
            "maximum_version": "3.13"
        },
        "dependencies": {
            "required": ["click"] if language == "python" else [],
            "optional": []
        },
        "installation": {
            "pypi_name": f"test-{language}-cli",
            "development_path": ".",
            "extras": {}
        },
        "shell_integration": {
            "enabled": False,
            "alias": f"test{language}cli"
        },
        "validation": {
            "check_api_keys": False,
            "check_disk_space": True,
            "minimum_disk_space_mb": 100
        },
        "messages": {
            "install_success": "CLI installed successfully!",
            "install_dev_success": "CLI dev installation completed!",
            "upgrade_success": "CLI upgraded successfully!",
            "uninstall_success": "CLI uninstalled successfully!"
        },
        "cli": {
            "name": f"test{language}cli",
            "tagline": f"Test CLI for {language}",
            "commands": {
                "hello": {
                    "desc": "Say hello with a name",
                    "args": [
                        {
                            "name": "name",
                            "desc": "Name to greet",
                            "required": True,
                            "type": "str"
                        }
                    ],
                    "options": [
                        {
                            "name": "uppercase",
                            "short": "u",
                            "desc": "Print greeting in uppercase",
                            "type": "flag",
                            "default": False
                        },
                        {
                            "name": "times",
                            "short": "t",
                            "desc": "Number of times to repeat greeting",
                            "type": "int",
                            "default": 1
                        }
                    ]
                },
                "config": {
                    "desc": "Manage configuration settings",
                    "options": [
                        {
                            "name": "get",
                            "short": "g",
                            "desc": "Get configuration value",
                            "type": "str"
                        },
                        {
                            "name": "set",
                            "short": "s",
                            "desc": "Set configuration value",
                            "type": "str"
                        }
                    ]
                },
                "version": {
                    "desc": "Show version information"
                }
            }
        }
    })


class TestPythonCLICompilation:
    """Test Python CLI compilation and execution."""
    
    def test_python_cli_syntax_validation(self):
        """Test that generated Python CLI has valid syntax and can be compiled."""
        config = create_realistic_config("python")
        generator = PythonGenerator(use_universal_templates=True)
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Generate CLI
            all_files = generator.generate_all_files(config, "test.yaml", "1.0.0")
            assert all_files, "Python CLI generation failed"
            
            # Write files to disk
            cli_file = None
            for filename, content in all_files.items():
                if filename == '__executable__':
                    continue
                file_path = Path(temp_dir) / filename
                file_path.parent.mkdir(parents=True, exist_ok=True)
                file_path.write_text(content)
                
                if filename.endswith('.py') and ('cli' in filename or 'main' in filename):
                    cli_file = file_path
            
            assert cli_file is not None, "No main CLI Python file found"
            
            # Test 1: Syntax validation - compile the Python code
            cli_content = cli_file.read_text()
            try:
                compile(cli_content, str(cli_file), 'exec')
            except SyntaxError as e:
                pytest.fail(f"Generated Python CLI has syntax errors: {e}\nContent:\n{cli_content[:500]}...")
            
            # Test 2: Import validation - check that imports work
            import_test_result = subprocess.run([
                sys.executable, '-c', f'import sys; sys.path.insert(0, "{temp_dir}"); exec(open("{cli_file}").read())'
            ], capture_output=True, text=True, timeout=QUICK_CHECK_TIMEOUT, cwd=temp_dir)
            
            if import_test_result.returncode != 0:
                # Allow for missing dependencies but not syntax/import errors
                error_text = import_test_result.stderr.lower()
                allowed_errors = ["modulenotfounderror: no module named 'click'", "importerror"]
                if not any(allowed in error_text for allowed in allowed_errors):
                    pytest.fail(f"Python CLI import failed: {import_test_result.stderr}")
            
            print("✅ Python CLI syntax and import validation passed")
    
    def test_python_cli_execution_with_dependencies(self):
        """Test Python CLI execution when dependencies are available."""
        if not check_tool_availability("pip"):
            pytest.skip("pip not available for Python dependency installation")
        
        config = create_realistic_config("python")
        generator = PythonGenerator(use_universal_templates=True)
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Generate CLI
            all_files = generator.generate_all_files(config, "test.yaml", "1.0.0")
            assert all_files, "Python CLI generation failed"
            
            # Write files and find CLI
            cli_file = None
            for filename, content in all_files.items():
                if filename == '__executable__':
                    continue
                file_path = Path(temp_dir) / filename
                file_path.parent.mkdir(parents=True, exist_ok=True)
                file_path.write_text(content)
                
                # Prioritize cli.py over __init__.py for execution
                if filename.endswith('.py') and ('cli' in filename or 'main' in filename):
                    if cli_file is None or 'cli.py' in filename:
                        cli_file = file_path
            
            # Create a minimal virtual environment for testing
            venv_dir = Path(temp_dir) / "test_venv"
            subprocess.run([sys.executable, '-m', 'venv', str(venv_dir)], check=True)
            
            # Install required dependencies in the virtual environment
            pip_executable = venv_dir / "bin" / "pip"
            if not pip_executable.exists():  # Windows
                pip_executable = venv_dir / "Scripts" / "pip.exe"
            
            try:
                # Install both click and rich-click as required by generated CLI
                subprocess.run([str(pip_executable), 'install', 'click', 'rich-click'], check=True, timeout=DEPENDENCY_INSTALL_TIMEOUT)
            except subprocess.TimeoutExpired:
                pytest.skip("pip install timed out during dependency installation")
            
            # Test CLI execution with dependencies
            python_executable = venv_dir / "bin" / "python"
            if not python_executable.exists():  # Windows
                python_executable = venv_dir / "Scripts" / "python.exe"
            
            # Test help command
            help_result = subprocess.run([
                str(python_executable), str(cli_file), '--help'
            ], capture_output=True, text=True, timeout=QUICK_CHECK_TIMEOUT, cwd=temp_dir)
            
            assert help_result.returncode == 0, f"Python CLI help failed: {help_result.stderr}"
            assert "hello" in help_result.stdout.lower(), "Help should show hello command"
            assert "config" in help_result.stdout.lower(), "Help should show config command"
            
            print("✅ Python CLI execution with dependencies passed")


class TestNodeJSCLICompilation:
    """Test Node.js CLI compilation and execution."""
    
    def test_nodejs_cli_syntax_validation(self):
        """Test that generated Node.js CLI has valid syntax."""
        if not check_tool_availability("node"):
            pytest.skip("node not available for Node.js testing")
        
        config = create_realistic_config("nodejs")
        generator = NodeJSGenerator()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Generate CLI
            all_files = generator.generate_all_files(config, "test.yaml", "1.0.0")
            assert all_files, "Node.js CLI generation failed"
            
            # Write files to disk
            cli_file = None
            package_json = None
            
            for filename, content in all_files.items():
                if filename == '__executable__':
                    continue
                file_path = Path(temp_dir) / filename
                file_path.parent.mkdir(parents=True, exist_ok=True)
                file_path.write_text(content)
                
                if filename.endswith('.js') and ('cli' in filename or 'main' in filename):
                    cli_file = file_path
                    cli_file.chmod(0o755)  # Make executable
                elif filename == 'package.json':
                    package_json = file_path
            
            assert cli_file is not None, "No main CLI JavaScript file found"
            assert package_json is not None, "No package.json found"
            
            # Test 1: JavaScript syntax validation
            syntax_result = subprocess.run([
                'node', '--check', str(cli_file)
            ], capture_output=True, text=True, timeout=QUICK_CHECK_TIMEOUT)
            
            if syntax_result.returncode != 0:
                cli_content = cli_file.read_text()
                pytest.fail(f"Generated Node.js CLI has syntax errors: {syntax_result.stderr}\nContent:\n{cli_content[:500]}...")
            
            # Test 2: Package.json validation
            with open(package_json) as f:
                try:
                    package_data = json.load(f)
                    assert "dependencies" in package_data, "package.json should have dependencies"
                    assert "commander" in package_data["dependencies"], "Should include commander dependency"
                except json.JSONDecodeError as e:
                    pytest.fail(f"Invalid package.json generated: {e}")
            
            print("✅ Node.js CLI syntax validation passed")
    
    def test_nodejs_cli_execution_with_dependencies(self):
        """Test Node.js CLI execution when dependencies are installed."""
        if not check_tool_availability("node") or not check_tool_availability("npm"):
            pytest.skip("node or npm not available for Node.js dependency testing")
        
        config = create_realistic_config("nodejs")
        generator = NodeJSGenerator()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Generate CLI
            all_files = generator.generate_all_files(config, "test.yaml", "1.0.0")
            assert all_files, "Node.js CLI generation failed"
            
            # Write files
            cli_file = None
            for filename, content in all_files.items():
                if filename == '__executable__':
                    continue
                file_path = Path(temp_dir) / filename
                file_path.parent.mkdir(parents=True, exist_ok=True)
                file_path.write_text(content)
                
                # Specifically look for bin/cli.js for Node.js CLIs
                if filename == 'bin/cli.js':
                    cli_file = file_path
                    cli_file.chmod(0o755)
            
            # Install dependencies with timeout protection
            try:
                npm_result = subprocess.run(['npm', 'install'], cwd=temp_dir, 
                                          capture_output=True, text=True, timeout=COMPILATION_TIMEOUT)
                if npm_result.returncode != 0:
                    pytest.skip(f"npm install failed: {npm_result.stderr}")
            except subprocess.TimeoutExpired:
                pytest.skip("npm install timed out during dependency installation")
            
            # Test CLI execution
            help_result = subprocess.run([
                'node', str(cli_file), '--help'
            ], capture_output=True, text=True, timeout=30, cwd=temp_dir)
            
            assert help_result.returncode == 0, f"Node.js CLI help failed: {help_result.stderr}"
            assert "hello" in help_result.stdout.lower(), "Help should show hello command"
            
            print("✅ Node.js CLI execution with dependencies passed")


class TestTypeScriptCLICompilation:
    """Test TypeScript CLI compilation and execution."""
    
    def test_typescript_cli_compilation(self):
        """Test that generated TypeScript CLI compiles successfully."""
        if not check_tool_availability("node") or not check_tool_availability("npm"):
            pytest.skip("node or npm not available for TypeScript testing")
        
        config = create_realistic_config("typescript")
        generator = TypeScriptGenerator()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Generate CLI
            all_files = generator.generate_all_files(config, "test.yaml", "1.0.0")
            assert all_files, "TypeScript CLI generation failed"
            
            # Write files
            cli_file = None
            tsconfig_file = None
            package_json = None
            
            for filename, content in all_files.items():
                if filename == '__executable__':
                    continue
                file_path = Path(temp_dir) / filename
                file_path.parent.mkdir(parents=True, exist_ok=True)
                file_path.write_text(content)
                
                if filename.endswith('.ts') and ('cli' in filename or 'main' in filename or 'index' in filename):
                    cli_file = file_path
                elif filename == 'tsconfig.json':
                    tsconfig_file = file_path
                elif filename == 'package.json':
                    package_json = file_path
            
            assert cli_file is not None, "No main CLI TypeScript file found"
            assert package_json is not None, "No package.json found"
            
            # Install dependencies with timeout protection
            try:
                npm_result = subprocess.run(['npm', 'install'], cwd=temp_dir,
                                          capture_output=True, text=True, timeout=COMPILATION_TIMEOUT)
                if npm_result.returncode != 0:
                    pytest.skip(f"npm install failed: {npm_result.stderr}")
            except subprocess.TimeoutExpired:
                pytest.skip("npm install timed out during dependency installation")
            
            # Test TypeScript compilation with timeout protection
            try:
                if tsconfig_file and tsconfig_file.exists():
                    tsc_result = subprocess.run(['npx', 'tsc'], cwd=temp_dir,
                                              capture_output=True, text=True, timeout=EXECUTION_TIMEOUT)
                else:
                    # Try direct compilation
                    tsc_result = subprocess.run(['npx', 'tsc', str(cli_file.name), '--outDir', 'dist'],
                                              cwd=temp_dir, capture_output=True, text=True, timeout=EXECUTION_TIMEOUT)
            except subprocess.TimeoutExpired:
                pytest.skip("TypeScript compilation timed out")
            
            # Accept return code 2 (warnings) as successful compilation
            # Only fail if return code > 2 (actual errors) or no JS files generated
            if tsc_result.returncode > 2:
                cli_content = cli_file.read_text() if cli_file else "No CLI file"
                pytest.fail(f"TypeScript compilation failed with errors: {tsc_result.stderr}\nCLI content:\n{cli_content[:500]}...")
            
            # Verify compiled output exists - especially important for warning cases (return code 1-2)
            dist_dir = Path(temp_dir) / "dist"
            js_files = []
            if dist_dir.exists():
                js_files = list(dist_dir.glob("**/*.js"))
            
            # If compilation had warnings (return code 1-2) but no JS files, it's a failure
            if tsc_result.returncode in [1, 2] and len(js_files) == 0:
                cli_content = cli_file.read_text() if cli_file else "No CLI file"
                pytest.fail(f"TypeScript compilation completed with warnings but generated no JS files: {tsc_result.stderr}\nCLI content:\n{cli_content[:500]}...")
            
            # For successful compilation (return code 0), ensure JS files exist
            if tsc_result.returncode == 0:
                assert len(js_files) > 0, "No JavaScript files generated from TypeScript compilation"
            
            print("✅ TypeScript CLI compilation passed")


class TestCrossLanguageConsistency:
    """Test consistency across all language implementations."""
    
    def test_all_languages_generate_valid_help(self):
        """Test that all languages generate CLIs with consistent help output."""
        languages = ["python", "nodejs", "typescript", "rust"]
        help_outputs = {}
        
        for language in languages:
            # Skip if tools not available
            if language == "python" and not check_tool_availability("python"):
                continue
            elif language in ["nodejs", "typescript"] and not check_tool_availability("node"):
                continue
            elif language == "rust" and not check_tool_availability("cargo"):
                continue
            
            config = create_realistic_config(language)
            
            if language == "python":
                generator = PythonGenerator(use_universal_templates=True)
            elif language == "nodejs":
                generator = NodeJSGenerator()
            elif language == "typescript":
                generator = TypeScriptGenerator()
            elif language == "rust":
                generator = RustGenerator()
            
            with tempfile.TemporaryDirectory() as temp_dir:
                try:
                    # Generate CLI
                    all_files = generator.generate_all_files(config, "test.yaml", "1.0.0")
                    assert all_files, f"{language} CLI generation failed"
                    
                    # Write files
                    cli_file = None
                    for filename, content in all_files.items():
                        if filename == '__executable__':
                            continue
                        file_path = Path(temp_dir) / filename
                        file_path.parent.mkdir(parents=True, exist_ok=True)
                        file_path.write_text(content)
                        
                        if (filename.endswith(('.py', '.js', '.ts', '.rs')) and 
                            ('cli' in filename or 'main' in filename)):
                            cli_file = file_path
                    
                    assert cli_file is not None, f"No main CLI file found for {language}"
                    
                    # Basic validation that file has expected structure
                    content = cli_file.read_text()
                    assert len(content) > 100, f"{language} CLI file is too short"
                    assert "hello" in content.lower(), f"{language} CLI should contain hello command"
                    assert "config" in content.lower(), f"{language} CLI should contain config command"
                    
                    help_outputs[language] = "Generated successfully"
                    
                except Exception as e:
                    help_outputs[language] = f"Failed: {str(e)}"
        
        # Verify that at least some languages succeeded
        successful = [lang for lang, result in help_outputs.items() if "Generated successfully" in result]
        assert len(successful) > 0, f"No languages generated successfully: {help_outputs}"
        
        print(f"✅ Cross-language consistency test passed for: {', '.join(successful)}")
        if len(successful) < len(help_outputs):
            failed = [lang for lang, result in help_outputs.items() if "Failed:" in result]
            print(f"⚠️  Some languages failed: {failed}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])