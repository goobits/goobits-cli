"""End-to-end tests for CLI generation and execution.

These tests simulate the complete user experience:
1. Generate CLI code from YAML configuration
2. Install generated CLI in isolated virtual environment  
3. Execute CLI commands via subprocess
4. Verify output, stderr, and exit codes
"""
import pytest
import subprocess
import tempfile
import venv
from pathlib import Path
import sys
import os
import shutil

from goobits_cli.builder import load_yaml_config, Builder


class TestCLIE2E:
    """End-to-end tests for CLI generation and execution."""

    @pytest.fixture(scope="class")
    def test_config(self):
        """Load the test YAML configuration."""
        config_path = Path(__file__).parent.parent / "integration" / "goobits.yaml"
        return load_yaml_config(str(config_path))

    @pytest.fixture(scope="class") 
    def generated_cli_code(self, test_config):
        """Generate CLI code from test configuration."""
        builder = Builder()
        return builder.build(test_config, "goobits.yaml")

    @pytest.fixture(scope="class")
    def temp_venv_dir(self):
        """Create isolated temporary virtual environment."""
        with tempfile.TemporaryDirectory(prefix="e2e_test_venv_") as temp_dir:
            venv_path = Path(temp_dir) / "test_venv"
            
            # Create virtual environment
            venv.create(venv_path, with_pip=True)
            
            yield venv_path

    @pytest.fixture(scope="class")
    def installed_cli(self, generated_cli_code, temp_venv_dir):
        """Install generated CLI into isolated virtual environment."""
        # Determine Python executable in venv
        if sys.platform == "win32":
            python_exe = temp_venv_dir / "Scripts" / "python.exe"
            pip_exe = temp_venv_dir / "Scripts" / "pip.exe"
        else:
            python_exe = temp_venv_dir / "bin" / "python"
            pip_exe = temp_venv_dir / "bin" / "pip"

        # Create temporary package directory
        package_dir = temp_venv_dir / "test_cli_package"
        package_dir.mkdir()
        
        # Write generated CLI code
        cli_file = package_dir / "generated_cli.py"
        cli_file.write_text(generated_cli_code)
        
        # Make CLI executable
        cli_file.chmod(0o755)
        
        # Install required dependencies in venv
        subprocess.run([
            str(pip_exe), "install", "rich-click", "pydantic", "jinja2", "pyyaml"
        ], check=True, capture_output=True)
        
        return {
            "python_exe": python_exe,
            "cli_file": cli_file,
            "package_dir": package_dir
        }

    def test_cli_greet_command(self, installed_cli):
        """Test the greet command execution and output."""
        result = subprocess.run([
            str(installed_cli["python_exe"]),
            str(installed_cli["cli_file"]),
            "greet"
        ], capture_output=True, text=True)
        
        # Verify successful execution
        assert result.returncode == 0
        
        # Verify expected output
        assert "Executing greet command..." in result.stdout
        
        # Verify no error output
        assert result.stderr == ""

    def test_cli_hello_command_with_arguments(self, installed_cli):
        """Test the hello command with name argument and uppercase option."""
        result = subprocess.run([
            str(installed_cli["python_exe"]),
            str(installed_cli["cli_file"]),
            "hello",
            "Bob",
            "--uppercase", "true"
        ], capture_output=True, text=True)
        
        # Verify successful execution
        assert result.returncode == 0
        
        # Verify expected output contains command execution
        assert "Executing hello command..." in result.stdout
        
        # Verify argument and option are displayed
        assert "name: Bob" in result.stdout
        assert "uppercase: True" in result.stdout
        
        # Verify no error output
        assert result.stderr == ""

    def test_cli_hello_command_without_required_argument(self, installed_cli):
        """Test hello command fails when required argument is missing."""
        result = subprocess.run([
            str(installed_cli["python_exe"]),
            str(installed_cli["cli_file"]),
            "hello"
        ], capture_output=True, text=True)
        
        # Verify command fails
        assert result.returncode != 0
        
        # Verify error message about missing argument
        assert "Missing argument" in result.stderr or "Usage:" in result.stderr

    def test_cli_goodbye_command_with_option(self, installed_cli):
        """Test goodbye command with custom message option."""
        result = subprocess.run([
            str(installed_cli["python_exe"]),
            str(installed_cli["cli_file"]),
            "goodbye",
            "--message", "Have a great day!"
        ], capture_output=True, text=True)
        
        # Verify successful execution
        assert result.returncode == 0
        
        # Verify expected output
        assert "Executing goodbye command..." in result.stdout
        assert "message: Have a great day!" in result.stdout
        
        # Verify no error output
        assert result.stderr == ""

    def test_cli_help_output(self, installed_cli):
        """Test CLI help output shows correct structure."""
        result = subprocess.run([
            str(installed_cli["python_exe"]),
            str(installed_cli["cli_file"]),
            "--help"
        ], capture_output=True, text=True)
        
        # Verify successful execution
        assert result.returncode == 0
        
        # Verify CLI metadata from test YAML
        assert "TestCLI" in result.stdout
        assert "A test CLI for integration tests." in result.stdout
        
        # Verify commands are listed
        assert "greet" in result.stdout
        assert "hello" in result.stdout
        assert "goodbye" in result.stdout
        
        # Verify command descriptions
        assert "Prints a greeting." in result.stdout
        assert "Says hello to a user." in result.stdout
        assert "Says goodbye with optional message." in result.stdout

    def test_invalid_command_shows_error(self, installed_cli):
        """Test that invalid commands show appropriate error messages."""
        result = subprocess.run([
            str(installed_cli["python_exe"]),
            str(installed_cli["cli_file"]),
            "nonexistent"
        ], capture_output=True, text=True)
        
        # Verify command fails
        assert result.returncode != 0
        
        # Verify error message about invalid command
        assert "No such command" in result.stderr or "Usage:" in result.stderr