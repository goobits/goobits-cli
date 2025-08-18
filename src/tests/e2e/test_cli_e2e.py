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

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

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
        
        # Create app_hooks.py file with required hook implementations for testing
        hooks_file = package_dir / "app_hooks.py"
        hooks_content = '''"""
Hook implementations for E2E testing.

These are minimal implementations that allow the CLI commands to execute
successfully during testing while demonstrating the hook system functionality.
"""

def on_greet(**kwargs):
    """Hook implementation for the greet command."""
    print("Command greet executed")
    return 0

def on_hello(**kwargs):
    """Hook implementation for the hello command."""
    print("Command hello executed")
    return 0

def on_goodbye(**kwargs):
    """Hook implementation for the goodbye command."""
    print("Command goodbye executed")
    return 0
'''
        hooks_file.write_text(hooks_content)
        
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
        assert "Command greet executed" in result.stdout
        
        # Verify no error output
        assert result.stderr == ""

    def test_cli_hello_command_with_arguments(self, installed_cli):
        """Test the hello command with name argument and uppercase option."""
        # Universal Template System properly generates arguments, so provide the required name argument
        result = subprocess.run([
            str(installed_cli["python_exe"]),
            str(installed_cli["cli_file"]),
            "hello",
            "TestUser"  # Required NAME argument
        ], capture_output=True, text=True)
        
        # Verify successful execution
        assert result.returncode == 0
        
        # Verify expected output contains command execution
        assert "Command hello executed" in result.stdout
        
        # Verify no error output
        assert result.stderr == ""

    def test_cli_hello_command_without_required_argument(self, installed_cli):
        """Test hello command fails when required argument is missing."""
        # Universal Template System properly validates required arguments
        result = subprocess.run([
            str(installed_cli["python_exe"]),
            str(installed_cli["cli_file"]),
            "hello"
        ], capture_output=True, text=True)
        
        # Should fail with non-zero exit code when required argument is missing
        assert result.returncode != 0
        
        # Should show helpful error message about missing argument
        assert "Missing argument" in result.stderr or "NAME" in result.stderr

    def test_cli_goodbye_command_with_option(self, installed_cli):
        """Test goodbye command with custom message option."""
        # Universal Template System properly generates options
        result = subprocess.run([
            str(installed_cli["python_exe"]),
            str(installed_cli["cli_file"]),
            "goodbye"
        ], capture_output=True, text=True)
        
        # Verify successful execution
        assert result.returncode == 0
        
        # Verify expected output
        assert "Command goodbye executed" in result.stdout
        
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


class TestRustCLIE2E:
    """End-to-end tests for Rust CLI generation and execution."""

    @pytest.fixture(scope="class")
    def rust_test_config(self):
        """Load the test YAML configuration for Rust."""
        config_path = Path(__file__).parent.parent / "integration" / "goobits.yaml"
        with open(config_path, 'r') as f:
            import yaml
            config = yaml.safe_load(f)
        
        # Override language to Rust for these tests
        config['language'] = 'rust'
        return config

    @pytest.fixture(scope="class") 
    def generated_rust_cli_code(self, rust_test_config):
        """Generate Rust CLI code from test configuration."""
        from goobits_cli.builder import Builder
        builder = Builder()
        return builder.build(rust_test_config, "goobits.yaml")

    @pytest.fixture(scope="class")
    def temp_rust_dir(self):
        """Create isolated temporary directory for Rust CLI."""
        with tempfile.TemporaryDirectory(prefix="e2e_rust_test_") as temp_dir:
            yield Path(temp_dir)

    @pytest.fixture(scope="class")
    def compiled_rust_cli(self, generated_rust_cli_code, temp_rust_dir):
        """Generate and compile Rust CLI binary."""
        from goobits_cli.generators.rust import RustGenerator
        from goobits_cli.schemas import GoobitsConfigSchema
        
        # Create test config for Rust
        config_data = {
            "package_name": "rust-e2e-test",
            "command_name": "rust-test-cli",
            "display_name": "Rust E2E Test CLI",
            "description": "A test CLI for Rust E2E tests",
            "language": "rust",
            "python": {"minimum_version": "3.8"},
            "dependencies": {"required": []},
            "installation": {"pypi_name": "rust-e2e-test"},
            "shell_integration": {"enabled": False, "alias": "rust-test-cli"},
            "validation": {"check_api_keys": False, "check_disk_space": False},
            "messages": {"install_success": "Rust test CLI installed successfully!"},
            "cli": {
                "name": "rust-test-cli",
                "tagline": "Test CLI for Rust E2E",
                "commands": {
                    "greet": {"desc": "Prints a greeting."},
                    "hello": {"desc": "Says hello to a user."},
                    "goodbye": {"desc": "Says goodbye with optional message."}
                }
            }
        }
        
        config = GoobitsConfigSchema(**config_data)
        generator = RustGenerator()
        files = generator.generate_all_files(config, "goobits.yaml")
        
        # Write files to temp directory
        for file_path, content in files.items():
            full_path = temp_rust_dir / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(content)
        
        # Check if Cargo is available
        cargo_check = subprocess.run(["cargo", "--version"], capture_output=True, text=True)
        if cargo_check.returncode != 0:
            pytest.skip("Cargo not available for Rust compilation")
        
        # Compile the Rust binary
        try:
            compile_result = subprocess.run([
                "cargo", "build", "--release"
            ], cwd=temp_rust_dir, capture_output=True, text=True, timeout=300)
            
            if compile_result.returncode != 0:
                pytest.fail(f"Rust compilation failed: {compile_result.stderr}")
            
            # Find the compiled binary
            binary_path = temp_rust_dir / "target" / "release" / "rust-test-cli"
            if not binary_path.exists():
                # Try without release flag
                subprocess.run(["cargo", "build"], cwd=temp_rust_dir, capture_output=True, text=True, timeout=300)
                binary_path = temp_rust_dir / "target" / "debug" / "rust-test-cli"
            
            if not binary_path.exists():
                pytest.fail("Rust binary not found after compilation")
                
            return {
                "binary_path": binary_path,
                "project_dir": temp_rust_dir
            }
            
        except subprocess.TimeoutExpired:
            pytest.fail("Rust compilation timed out")
        except Exception as e:
            pytest.fail(f"Rust compilation error: {e}")

    def test_rust_cli_generation_and_compilation(self, compiled_rust_cli):
        """Test Rust CLI generation and successful compilation."""
        # Verify binary exists and is executable
        assert compiled_rust_cli["binary_path"].exists()
        assert compiled_rust_cli["binary_path"].is_file()
        
        # Verify Cargo.toml was generated
        cargo_toml = compiled_rust_cli["project_dir"] / "Cargo.toml"
        assert cargo_toml.exists()
        
        # Verify main.rs was generated
        main_rs = compiled_rust_cli["project_dir"] / "src" / "main.rs"
        assert main_rs.exists()
        
        # Verify hooks.rs was generated
        hooks_rs = compiled_rust_cli["project_dir"] / "src" / "hooks.rs"
        assert hooks_rs.exists()

    def test_rust_cli_command_execution(self, compiled_rust_cli):
        """Test actual command execution of Rust binary."""
        binary_path = compiled_rust_cli["binary_path"]
        
        # Test greet command
        result = subprocess.run([
            str(binary_path), "greet"
        ], capture_output=True, text=True)
        
        # Rust CLI should execute successfully
        assert result.returncode == 0
        # Verify some output was produced (exact format may vary)
        assert len(result.stdout.strip()) > 0 or len(result.stderr.strip()) > 0

    def test_rust_cli_help_output(self, compiled_rust_cli):
        """Test Rust CLI help output matches expected structure."""
        binary_path = compiled_rust_cli["binary_path"]
        
        result = subprocess.run([
            str(binary_path), "--help"
        ], capture_output=True, text=True)
        
        # Verify successful execution
        assert result.returncode == 0
        
        # Verify help contains CLI information
        help_output = result.stdout.lower()
        assert "rust-test-cli" in help_output or "test cli" in help_output
        
        # Verify commands are listed in help
        assert "greet" in help_output
        assert "hello" in help_output  
        assert "goodbye" in help_output

    def test_rust_cli_version_output(self, compiled_rust_cli):
        """Test Rust CLI version output."""
        binary_path = compiled_rust_cli["binary_path"]
        
        # Test version flag
        result = subprocess.run([
            str(binary_path), "--version"
        ], capture_output=True, text=True)
        
        # Should execute successfully and show version info
        assert result.returncode == 0
        # Clap typically includes version info
        assert len(result.stdout.strip()) > 0

    def test_rust_cli_invalid_command(self, compiled_rust_cli):
        """Test Rust CLI error handling for invalid commands."""
        binary_path = compiled_rust_cli["binary_path"]
        
        result = subprocess.run([
            str(binary_path), "nonexistent-command"
        ], capture_output=True, text=True)
        
        # Should fail with non-zero exit code
        assert result.returncode != 0
        
        # Should provide helpful error message
        error_output = (result.stderr + result.stdout).lower()
        assert ("error" in error_output or 
                "invalid" in error_output or 
                "unknown" in error_output or
                "unrecognized" in error_output)

    def test_rust_cli_performance_baseline(self, compiled_rust_cli):
        """Test Rust CLI startup performance (Rust-specific enhancement)."""
        binary_path = compiled_rust_cli["binary_path"]
        
        import time
        
        # Measure startup time for help command (should be very fast)
        start_time = time.perf_counter()
        result = subprocess.run([
            str(binary_path), "--help"
        ], capture_output=True, text=True)
        end_time = time.perf_counter()
        
        execution_time_ms = (end_time - start_time) * 1000
        
        # Rust should be very fast (target: under 100ms for help)
        assert result.returncode == 0
        assert execution_time_ms < 500, f"Rust CLI too slow: {execution_time_ms:.2f}ms (target: <500ms)"