"""Common test helper functions and utilities.

This module provides utilities for CLI testing, environment management,
file system operations, and test execution helpers.
"""
import os
import sys
import tempfile
import subprocess
import shutil
import venv
from typing import Dict, List, Optional, Any, Tuple, Union, ContextManager
from dataclasses import dataclass, field
from pathlib import Path
import json
import yaml
from contextlib import contextmanager
import time
import signal

from goobits_cli.schemas import GoobitsConfigSchema
# Import from the test conftest.py file
import sys
from pathlib import Path

# Add tests directory to path to import from conftest
tests_dir = Path(__file__).parents[4] / "tests"
sys.path.insert(0, str(tests_dir))

from conftest import generate_cli


@dataclass
class CommandResult:
    """Result of executing a CLI command."""
    
    exit_code: int
    stdout: str
    stderr: str
    command: List[str]
    execution_time: float
    working_directory: str
    
    @property
    def success(self) -> bool:
        """Whether the command executed successfully."""
        return self.exit_code == 0
    
    @property
    def failed(self) -> bool:
        """Whether the command failed."""
        return self.exit_code != 0
    
    def assert_success(self):
        """Assert that the command was successful."""
        assert self.success, f"Command failed with exit code {self.exit_code}. stderr: {self.stderr}"
    
    def assert_failure(self):
        """Assert that the command failed."""
        assert self.failed, f"Command should have failed but succeeded. stdout: {self.stdout}"
    
    def contains_output(self, text: str, case_sensitive: bool = True) -> bool:
        """Check if output contains specific text."""
        output = self.stdout + self.stderr
        if not case_sensitive:
            return text.lower() in output.lower()
        return text in output
    
    def assert_contains(self, text: str, case_sensitive: bool = True):
        """Assert that output contains specific text."""
        assert self.contains_output(text, case_sensitive), \
            f"Output does not contain '{text}'. Output: {self.stdout}{self.stderr}"


@dataclass
class TestEnvironment:
    """Isolated test environment for CLI testing."""
    
    temp_dir: Path
    venv_path: Optional[Path] = None
    python_exe: Optional[Path] = None
    pip_exe: Optional[Path] = None
    installed_clis: Dict[str, Path] = field(default_factory=dict)
    env_vars: Dict[str, str] = field(default_factory=dict)
    
    def __post_init__(self):
        """Initialize the test environment."""
        self.temp_dir = Path(self.temp_dir)
        if not self.temp_dir.exists():
            self.temp_dir.mkdir(parents=True)
    
    def create_virtual_environment(self) -> Path:
        """Create a Python virtual environment for isolated testing."""
        if self.venv_path:
            return self.venv_path
        
        self.venv_path = self.temp_dir / "test_venv"
        venv.create(self.venv_path, with_pip=True)
        
        # Set up Python and pip executables
        if sys.platform == "win32":
            self.python_exe = self.venv_path / "Scripts" / "python.exe"
            self.pip_exe = self.venv_path / "Scripts" / "pip.exe"
        else:
            self.python_exe = self.venv_path / "bin" / "python"
            self.pip_exe = self.venv_path / "bin" / "pip"
        
        return self.venv_path
    
    def install_python_packages(self, packages: List[str]):
        """Install Python packages in the virtual environment."""
        if not self.venv_path or not self.pip_exe:
            self.create_virtual_environment()
        
        for package in packages:
            result = subprocess.run([
                str(self.pip_exe), "install", package
            ], capture_output=True, text=True)
            
            if result.returncode != 0:
                raise RuntimeError(f"Failed to install {package}: {result.stderr}")
    
    def install_cli_from_files(self, cli_name: str, files: Dict[str, str]) -> Path:
        """Install a CLI from generated files.
        
        Args:
            cli_name: Name of the CLI
            files: Dictionary mapping filename to content
            
        Returns:
            Path to the installed CLI
        """
        cli_dir = self.temp_dir / cli_name
        cli_dir.mkdir(exist_ok=True)
        
        # Write all files
        main_cli_file = None
        for filename, content in files.items():
            file_path = cli_dir / filename
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(content)
            
            # Make executable files executable
            if filename.endswith(('.sh', '.py')) or filename == 'index.js':
                file_path.chmod(0o755)
                
            # Identify main CLI file
            if filename in ['cli.py', 'index.js', 'cli.ts'] or filename.endswith('main.rs'):
                main_cli_file = file_path
        
        # Install dependencies if needed
        if 'package.json' in files and shutil.which('npm'):
            result = subprocess.run(['npm', 'install'], cwd=cli_dir, capture_output=True)
            if result.returncode != 0:
                print(f"Warning: npm install failed: {result.stderr.decode()}")
        
        # For Python CLIs, install required packages
        if main_cli_file and main_cli_file.suffix == '.py':
            self.install_python_packages(['rich-click', 'pydantic', 'jinja2', 'pyyaml'])
        
        if main_cli_file:
            self.installed_clis[cli_name] = main_cli_file
        
        return main_cli_file or cli_dir
    
    def get_cli_command(self, cli_name: str) -> List[str]:
        """Get the command to execute a CLI.
        
        Args:
            cli_name: Name of the CLI
            
        Returns:
            Command list to execute the CLI
        """
        if cli_name not in self.installed_clis:
            raise ValueError(f"CLI {cli_name} not installed")
        
        cli_path = self.installed_clis[cli_name]
        
        if cli_path.suffix == '.py':
            return [str(self.python_exe or 'python'), str(cli_path)]
        elif cli_path.suffix == '.js':
            return ['node', str(cli_path)]
        elif cli_path.suffix == '.ts':
            if shutil.which('ts-node'):
                return ['ts-node', str(cli_path)]
            else:
                return ['node', str(cli_path)]
        elif cli_path.name.endswith('main') or cli_path.parent.name == 'target':
            return [str(cli_path)]  # Compiled Rust binary
        else:
            return [str(cli_path)]
    
    def set_env_var(self, key: str, value: str):
        """Set an environment variable for this test environment."""
        self.env_vars[key] = value
    
    def get_env(self) -> Dict[str, str]:
        """Get environment variables for this test environment."""
        env = os.environ.copy()
        env.update(self.env_vars)
        return env
    
    def cleanup(self):
        """Clean up the test environment."""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)


class CLITestRunner:
    """Runner for CLI tests with various execution options."""
    
    def __init__(self, test_env: TestEnvironment):
        self.test_env = test_env
    
    def run_command(
        self,
        command: List[str],
        input_text: Optional[str] = None,
        timeout: float = 30.0,
        working_directory: Optional[Path] = None,
        env_vars: Optional[Dict[str, str]] = None
    ) -> CommandResult:
        """Execute a command and return the result.
        
        Args:
            command: Command to execute
            input_text: Optional stdin input
            timeout: Command timeout in seconds
            working_directory: Working directory for command
            env_vars: Additional environment variables
            
        Returns:
            CommandResult with execution details
        """
        start_time = time.time()
        
        # Prepare environment
        env = self.test_env.get_env()
        if env_vars:
            env.update(env_vars)
        
        # Set working directory
        cwd = working_directory or self.test_env.temp_dir
        
        try:
            result = subprocess.run(
                command,
                input=input_text,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=str(cwd),
                env=env
            )
            
            execution_time = time.time() - start_time
            
            return CommandResult(
                exit_code=result.returncode,
                stdout=result.stdout,
                stderr=result.stderr,
                command=command,
                execution_time=execution_time,
                working_directory=str(cwd)
            )
        
        except subprocess.TimeoutExpired:
            execution_time = time.time() - start_time
            return CommandResult(
                exit_code=-1,
                stdout="",
                stderr=f"Command timed out after {timeout} seconds",
                command=command,
                execution_time=execution_time,
                working_directory=str(cwd)
            )
    
    def run_cli_command(
        self,
        cli_name: str,
        args: List[str],
        **kwargs
    ) -> CommandResult:
        """Execute a CLI command.
        
        Args:
            cli_name: Name of the CLI to execute
            args: Arguments to pass to the CLI
            **kwargs: Additional arguments passed to run_command
            
        Returns:
            CommandResult
        """
        base_command = self.test_env.get_cli_command(cli_name)
        full_command = base_command + args
        
        return self.run_command(full_command, **kwargs)
    
    def test_cli_help(self, cli_name: str) -> CommandResult:
        """Test CLI help output."""
        return self.run_cli_command(cli_name, ['--help'])
    
    def test_cli_version(self, cli_name: str) -> CommandResult:
        """Test CLI version output."""
        return self.run_cli_command(cli_name, ['--version'])
    
    def test_cli_invalid_command(self, cli_name: str) -> CommandResult:
        """Test CLI behavior with invalid command."""
        return self.run_cli_command(cli_name, ['nonexistent-command'])
    
    def test_command_help(self, cli_name: str, command: str) -> CommandResult:
        """Test specific command help."""
        return self.run_cli_command(cli_name, [command, '--help'])


class FileSystemHelper:
    """Helper for file system operations in tests."""
    
    def __init__(self, base_path: Path):
        self.base_path = Path(base_path)
    
    def create_file(self, path: str, content: str) -> Path:
        """Create a file with content."""
        file_path = self.base_path / path
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content)
        return file_path
    
    def create_yaml_file(self, path: str, data: Dict[str, Any]) -> Path:
        """Create a YAML file."""
        content = yaml.dump(data, default_flow_style=False)
        return self.create_file(path, content)
    
    def create_json_file(self, path: str, data: Dict[str, Any]) -> Path:
        """Create a JSON file."""
        content = json.dumps(data, indent=2)
        return self.create_file(path, content)
    
    def read_file(self, path: str) -> str:
        """Read file content."""
        return (self.base_path / path).read_text()
    
    def file_exists(self, path: str) -> bool:
        """Check if file exists."""
        return (self.base_path / path).exists()
    
    def create_directory(self, path: str) -> Path:
        """Create a directory."""
        dir_path = self.base_path / path
        dir_path.mkdir(parents=True, exist_ok=True)
        return dir_path
    
    def list_files(self, pattern: str = "*") -> List[Path]:
        """List files matching a pattern."""
        return list(self.base_path.glob(pattern))
    
    def copy_file(self, src: str, dest: str) -> Path:
        """Copy a file."""
        src_path = self.base_path / src
        dest_path = self.base_path / dest
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src_path, dest_path)
        return dest_path


# Context managers and convenience functions

@contextmanager
def create_isolated_test_env() -> TestEnvironment:
    """Create an isolated test environment."""
    with tempfile.TemporaryDirectory(prefix="goobits_test_") as temp_dir:
        env = TestEnvironment(temp_dir=Path(temp_dir))
        try:
            yield env
        finally:
            env.cleanup()


@contextmanager
def temporary_directory() -> Path:
    """Create a temporary directory."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


def cleanup_test_environment(env: TestEnvironment):
    """Clean up a test environment."""
    env.cleanup()


def capture_command_output(
    command: List[str],
    timeout: float = 30.0,
    working_directory: Optional[Path] = None
) -> CommandResult:
    """Capture output from a command execution.
    
    Args:
        command: Command to execute
        timeout: Timeout in seconds
        working_directory: Working directory
        
    Returns:
        CommandResult
    """
    start_time = time.time()
    
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=str(working_directory) if working_directory else None
        )
        
        execution_time = time.time() - start_time
        
        return CommandResult(
            exit_code=result.returncode,
            stdout=result.stdout,
            stderr=result.stderr,
            command=command,
            execution_time=execution_time,
            working_directory=str(working_directory) if working_directory else os.getcwd()
        )
    
    except subprocess.TimeoutExpired:
        execution_time = time.time() - start_time
        return CommandResult(
            exit_code=-1,
            stdout="",
            stderr=f"Command timed out after {timeout} seconds",
            command=command,
            execution_time=execution_time,
            working_directory=str(working_directory) if working_directory else os.getcwd()
        )


def validate_cli_execution(
    result: CommandResult,
    expected_exit_code: int = 0,
    expected_output_patterns: Optional[List[str]] = None,
    expected_error_patterns: Optional[List[str]] = None
) -> bool:
    """Validate CLI execution result.
    
    Args:
        result: CommandResult to validate
        expected_exit_code: Expected exit code
        expected_output_patterns: Patterns that should be in stdout
        expected_error_patterns: Patterns that should be in stderr
        
    Returns:
        True if validation passes
    """
    # Check exit code
    if result.exit_code != expected_exit_code:
        return False
    
    # Check output patterns
    if expected_output_patterns:
        for pattern in expected_output_patterns:
            if pattern not in result.stdout:
                return False
    
    # Check error patterns
    if expected_error_patterns:
        for pattern in expected_error_patterns:
            if pattern not in result.stderr:
                return False
    
    return True


def generate_cli_and_test(
    config: GoobitsConfigSchema,
    config_filename: str,
    test_commands: List[List[str]]
) -> Dict[str, CommandResult]:
    """Generate CLI and run test commands.
    
    Args:
        config: GoobitsConfigSchema to generate CLI from
        config_filename: Name of the config file
        test_commands: List of command arguments to test
        
    Returns:
        Dictionary mapping command to result
    """
    with create_isolated_test_env() as env:
        # Generate CLI files
        files = generate_cli(config, config_filename)
        
        # Install CLI
        cli_name = config.package_name
        env.install_cli_from_files(cli_name, files)
        
        # Create test runner
        runner = CLITestRunner(env)
        
        # Run test commands
        results = {}
        for command_args in test_commands:
            command_key = ' '.join(command_args)
            results[command_key] = runner.run_cli_command(cli_name, command_args)
        
        return results


def compare_cli_behaviors(
    configs: Dict[str, GoobitsConfigSchema],
    test_commands: List[List[str]]
) -> Dict[str, Dict[str, CommandResult]]:
    """Compare CLI behaviors across different configurations.
    
    Args:
        configs: Dictionary mapping language/name to config
        test_commands: Commands to test
        
    Returns:
        Nested dictionary: config_name -> command -> result
    """
    all_results = {}
    
    for config_name, config in configs.items():
        config_filename = f"{config_name}.yaml"
        all_results[config_name] = generate_cli_and_test(
            config, config_filename, test_commands
        )
    
    return all_results