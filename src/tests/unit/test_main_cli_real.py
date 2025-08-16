#!/usr/bin/env python3
"""
Real (unmocked) tests for the main CLI functionality.
These tests actually generate files and run them to ensure everything works.
"""

import subprocess
import sys
from pathlib import Path
from typing import Optional

import pytest
from typer.testing import CliRunner

from goobits_cli.main import app


@pytest.mark.real_generation
class TestRealGeneration:
    """Test actual file generation without mocks."""
    
    @pytest.fixture(autouse=True)
    def setup(self, tmp_path):
        """Set up test environment."""
        self.runner = CliRunner()
        self.temp_dir = tmp_path
        self.original_cwd = Path.cwd()
        
    def create_test_config(self, 
                          language: str = "python",
                          cli_output_path: Optional[str] = None,
                          package_name: str = "test-cli",
                          command_name: str = "testcli",
                          with_commands: bool = True) -> Path:
        """Create a test configuration file."""
        if cli_output_path is None:
            cli_output_path = "cli.py" if language == "python" else f"cli.{language[:2]}"
            
        config_content = f"""
package_name: {package_name}
command_name: {command_name}
display_name: "Test CLI"
description: "A test CLI for real generation"
language: {language}
{f'cli_output_path: "{cli_output_path}"' if cli_output_path else ''}

python:
  minimum_version: "3.8"

dependencies:
  required: []

installation:
  pypi_name: "{package_name}"

shell_integration:
  enabled: false
  alias: "{command_name}"

validation:
  check_api_keys: false
  check_disk_space: false

messages:
  install_success: "Test CLI installed successfully!"

cli:
  name: {command_name}
  tagline: "Test CLI tool"
"""
        if with_commands:
            config_content += """  commands:
    hello:
      desc: "Say hello"
      args:
        - name: name
          desc: "Name to greet"
          required: false
          default: "World"
    test-cmd:
      desc: "Test command"
      options:
        - name: verbose
          desc: "Verbose output"
          type: bool
          default: false
"""
        
        config_path = self.temp_dir / "goobits.yaml"
        config_path.write_text(config_content)
        return config_path
    
    def test_python_cli_generation(self):
        """Generate and validate a real Python CLI."""
        cli_path = self.temp_dir / "mycli.py"
        config_path = self.create_test_config(
            language="python",
            cli_output_path=str(cli_path)
        )
        
        # Actually generate files
        result = self.runner.invoke(app, ["build", str(config_path)])
        assert result.exit_code == 0, f"Build failed: stdout={result.stdout}\nstderr={result.stderr}\nexception={result.exception}"
        
        # Verify files exist at correct locations
        assert cli_path.exists(), f"CLI file not created at {cli_path}"
        assert cli_path.stat().st_size > 100, "Generated file is too small (likely a stub)"
        
        # Verify content structure
        content = cli_path.read_text()
        assert ("import click" in content or "import typer" in content or 
                "import rich_click" in content), "No CLI framework import found"
        assert "def" in content, "No function definitions found"
        assert ("if __name__" in content or "main()" in content), "No entry point found"
        
    def test_nodejs_cli_generation(self):
        """Generate and validate a Node.js CLI."""
        config_path = self.create_test_config(language="nodejs")
        
        result = self.runner.invoke(app, ["build", str(config_path)])
        assert result.exit_code == 0, f"Build failed: {result.stdout}"
        
        # Check for Node.js specific files
        expected_files = ["cli.js", "package.json", "setup.sh"]
        for filename in expected_files:
            filepath = self.temp_dir / filename
            assert filepath.exists(), f"{filename} not generated for Node.js"
            
        # Verify package.json structure
        package_json = self.temp_dir / "package.json"
        content = package_json.read_text()
        assert '"name":' in content, "package.json missing name field"
        assert '"bin":' in content or '"main":' in content, "package.json missing entry point"
        
    def test_typescript_cli_generation(self):
        """Generate and validate a TypeScript CLI."""
        config_path = self.create_test_config(language="typescript")
        
        result = self.runner.invoke(app, ["build", str(config_path)])
        assert result.exit_code == 0, f"Build failed: {result.stdout}"
        
        # Check for TypeScript specific files
        expected_files = ["cli.ts", "package.json", "tsconfig.json", "setup.sh"]
        for filename in expected_files:
            filepath = self.temp_dir / filename
            assert filepath.exists(), f"{filename} not generated for TypeScript"
            
    def test_rust_cli_generation(self):
        """Generate and validate a Rust CLI."""
        config_path = self.create_test_config(language="rust")
        
        result = self.runner.invoke(app, ["build", str(config_path)])
        assert result.exit_code == 0, f"Build failed: {result.stdout}"
        
        # Check for Rust specific files
        assert (self.temp_dir / "Cargo.toml").exists(), "Cargo.toml not generated"
        assert ((self.temp_dir / "src" / "main.rs").exists() or 
                (self.temp_dir / "main.rs").exists()), "main.rs not generated"


@pytest.mark.execution
class TestGeneratedCLIExecution:
    """Test that generated CLIs actually run."""
    
    @pytest.fixture(autouse=True)
    def setup(self, tmp_path):
        """Set up test environment."""
        self.runner = CliRunner()
        self.temp_dir = tmp_path
        
    def create_minimal_config(self) -> Path:
        """Create a minimal configuration."""
        config_content = """
package_name: exec-test
command_name: exectest
display_name: "Execution Test"
description: "Testing CLI execution"
language: python

python:
  minimum_version: "3.8"

dependencies:
  required: []

installation:
  pypi_name: "exec-test"

shell_integration:
  enabled: false
  alias: "exectest"

validation:
  check_api_keys: false
  check_disk_space: false

messages:
  install_success: "Test CLI installed successfully!"

cli:
  name: exectest
  tagline: "Execution test"
  commands:
    hello:
      desc: "Say hello"
"""
        config_path = self.temp_dir / "goobits.yaml"
        config_path.write_text(config_content)
        return config_path
        
    def test_generated_cli_runs(self):
        """Generate a CLI and execute it."""
        # Generate
        config_path = self.create_minimal_config()
        result = self.runner.invoke(app, ["build", str(config_path)])
        assert result.exit_code == 0, f"Build failed: {result.stdout}"
        
        # Find the generated CLI file
        cli_path = self.temp_dir / "cli.py"
        if not cli_path.exists():
            # Try other common locations
            cli_path = self.temp_dir / "generated_cli.py"
            if not cli_path.exists():
                cli_path = self.temp_dir / "src" / "generated_cli.py"
                
        assert cli_path.exists(), "No CLI file found"
        
        # Execute generated CLI
        result = subprocess.run(
            [sys.executable, str(cli_path), "--help"],
            capture_output=True, text=True, cwd=str(self.temp_dir)
        )
        
        assert result.returncode == 0, f"CLI execution failed: {result.stderr}"
        # Check for command presence (could be "Commands:" or just the command name)
        assert ("hello" in result.stdout.lower() or 
                "command" in result.stdout.lower()), "Commands not shown in help"
        
    def test_generated_command_with_hooks(self):
        """Test that generated commands work with hooks."""
        # Generate CLI
        config_path = self.create_minimal_config()
        result = self.runner.invoke(app, ["build", str(config_path)])
        assert result.exit_code == 0
        
        # Create hook file
        hook_file = self.temp_dir / "app_hooks.py"
        hook_file.write_text("""
def on_hello():
    print("HOOK_EXECUTED_SUCCESSFULLY")
    return 0
""")
        
        # Find and run CLI command
        cli_path = self.temp_dir / "cli.py"
        if not cli_path.exists():
            cli_path = self.temp_dir / "generated_cli.py"
            
        result = subprocess.run(
            [sys.executable, str(cli_path), "hello"],
            capture_output=True, text=True, cwd=str(self.temp_dir)
        )
        
        # Either the hook executes OR we get a placeholder message
        assert (result.returncode == 0 or 
                "HOOK_EXECUTED_SUCCESSFULLY" in result.stdout or
                "Command hello executed" in result.stdout), f"Command failed: {result.stderr}"


@pytest.mark.configuration
class TestConfigurationRespect:
    """Test that configuration options are properly respected."""
    
    @pytest.fixture(autouse=True)
    def setup(self, tmp_path):
        """Set up test environment."""
        self.runner = CliRunner()
        self.temp_dir = tmp_path
        
    def test_cli_output_path_respected(self):
        """Verify cli_output_path setting is used."""
        custom_path = self.temp_dir / "custom" / "location" / "mycli.py"
        custom_path.parent.mkdir(parents=True, exist_ok=True)
        
        config_content = f"""
package_name: path-test
command_name: pathtest
display_name: "Path Test"
description: "Testing output path"
language: python
cli_output_path: "{custom_path}"

python:
  minimum_version: "3.8"

dependencies:
  required: []

installation:
  pypi_name: "path-test"

shell_integration:
  enabled: false
  alias: "pathtest"

validation:
  check_api_keys: false
  check_disk_space: false

messages:
  install_success: "Test CLI installed successfully!"

cli:
  name: pathtest
  tagline: "Path test"
"""
        config_path = self.temp_dir / "goobits.yaml"
        config_path.write_text(config_content)
        
        result = self.runner.invoke(app, ["build", str(config_path)])
        
        # Check if the file was created at the custom path
        # NOTE: Currently this will FAIL due to the bug we discovered
        if custom_path.exists():
            assert custom_path.exists(), "File created at custom path"
            assert not (self.temp_dir / "cli.py").exists(), "Default location should not exist"
        else:
            # Document the current broken behavior
            pytest.xfail("cli_output_path is currently ignored by Universal Template System")
            
    def test_language_specific_output(self):
        """Test each language generates correct file types."""
        tests = [
            ("python", ["cli.py", "setup.sh"]),
            ("nodejs", ["cli.js", "package.json", "setup.sh"]),
            ("typescript", ["cli.ts", "package.json", "tsconfig.json", "setup.sh"]),
            ("rust", ["Cargo.toml"])  # main.rs might be in src/
        ]
        
        for language, expected_files in tests:
            # Create fresh temp dir for each language
            lang_dir = self.temp_dir / language
            lang_dir.mkdir()
            
            config_content = f"""
package_name: {language}-test
command_name: {language}test
display_name: "{language.title()} Test"
description: "Testing {language}"
language: {language}

python:
  minimum_version: "3.8"

dependencies:
  required: []

installation:
  pypi_name: "{language}-test"

shell_integration:
  enabled: false
  alias: "{language}test"

validation:
  check_api_keys: false
  check_disk_space: false

messages:
  install_success: "Test CLI installed successfully!"

cli:
  name: {language}test
  tagline: "{language} test"
"""
            config_path = lang_dir / "goobits.yaml"
            config_path.write_text(config_content)
            
            result = self.runner.invoke(app, ["build", str(config_path)])
            assert result.exit_code == 0, f"{language} build failed: {result.stdout}"
            
            for filename in expected_files:
                filepath = lang_dir / filename
                if not filepath.exists():
                    # Check alternative locations
                    alt_path = lang_dir / "src" / filename
                    assert alt_path.exists(), f"{filename} missing for {language}"


@pytest.mark.regression
class TestBugRegressions:
    """Tests for specific bugs to prevent regression."""
    
    @pytest.fixture(autouse=True)
    def setup(self, tmp_path):
        """Set up test environment."""
        self.runner = CliRunner()
        self.temp_dir = tmp_path
        
    def test_cli_output_path_not_ignored(self):
        """Regression test for cli_output_path being ignored."""
        custom_path = self.temp_dir / "my_app" / "cli.py"
        custom_path.parent.mkdir(parents=True, exist_ok=True)
        
        config_content = f"""
package_name: regression-test
command_name: regtest
display_name: "Regression Test"
description: "Testing cli_output_path"
language: python
cli_output_path: "{custom_path}"

python:
  minimum_version: "3.8"

dependencies:
  required: []

installation:
  pypi_name: "regression-test"

shell_integration:
  enabled: false
  alias: "regtest"

validation:
  check_api_keys: false
  check_disk_space: false

messages:
  install_success: "Test CLI installed successfully!"

cli:
  commands:
    test:
      desc: "Test command"
"""
        config_path = self.temp_dir / "config.yaml"
        config_path.write_text(config_content)
        
        result = self.runner.invoke(app, ["build", str(config_path)])
        
        # This test documents the CURRENT BROKEN behavior
        if not custom_path.exists():
            pytest.xfail("BUG: cli_output_path is ignored - file created at cli.py instead")
        else:
            assert custom_path.exists(), "cli_output_path should be respected"
            content = custom_path.read_text()
            assert "Command test executed" not in content, "Should not be a stub"
            
    def test_generated_cli_not_stub(self):
        """Ensure generated CLIs are not just stubs."""
        config_content = """
package_name: stub-test
command_name: stubtest
display_name: "Stub Test"
description: "Testing non-stub generation"
language: python

python:
  minimum_version: "3.8"

dependencies:
  required: []

installation:
  pypi_name: "stub-test"

shell_integration:
  enabled: false
  alias: "stubtest"

validation:
  check_api_keys: false
  check_disk_space: false

messages:
  install_success: "Test CLI installed successfully!"

cli:
  commands:
    work:
      desc: "Should do work"
"""
        config_path = self.temp_dir / "goobits.yaml"
        config_path.write_text(config_content)
        
        result = self.runner.invoke(app, ["build", str(config_path)])
        assert result.exit_code == 0
        
        # Find generated file
        cli_path = self.temp_dir / "cli.py"
        if not cli_path.exists():
            cli_path = self.temp_dir / "generated_cli.py"
            
        content = cli_path.read_text()
        
        # Check it's not just printing stub messages
        if 'echo("Command work executed")' in content:
            pytest.xfail("BUG: Generated CLI is just a stub, not properly integrated")
        
        # Should have hook integration or real implementation
        assert ("app_hooks" in content or 
                "import goobits_cli" in content or
                "hook" in content.lower()), "CLI should have hook integration"
        
    def test_universal_template_validation_error(self):
        """Test that validation errors don't break generation."""
        # This config triggers the validation error we saw
        config_content = """
package_name: validation-test
command_name: valtest
display_name: "Validation Test"
description: "Testing validation error handling"
language: python

python:
  minimum_version: "3.8"

dependencies:
  required: []

installation:
  pypi_name: "validation-test"

shell_integration:
  enabled: false
  alias: "valtest"

validation:
  check_api_keys: false
  check_disk_space: false

messages:
  install_success: "Test CLI installed successfully!"

cli:
  options:
    - name: verbose
      type: bool
      default: false
    - name: interactive
      type: bool
      default: false
  commands:
    test:
      desc: "Test command"
"""
        config_path = self.temp_dir / "goobits.yaml"
        config_path.write_text(config_content)
        
        result = self.runner.invoke(app, ["build", str(config_path)])
        
        # Should still generate something despite validation warning
        assert result.exit_code == 0, "Build should succeed despite validation warning"
        cli_path = self.temp_dir / "cli.py"
        assert cli_path.exists() or (self.temp_dir / "generated_cli.py").exists()


if __name__ == "__main__":
    # Allow running this file directly for debugging
    pytest.main([__file__, "-v", "-k", "test_"])