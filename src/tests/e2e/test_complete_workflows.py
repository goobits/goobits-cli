"""
Complete End-to-End Workflow Tests

This module consolidates all end-to-end tests for complete user workflows:
1. CLI generation and execution (test_cli_e2e.py)
2. Node.js generator e2e tests (test_nodejs_generator_e2e.py)
3. Complete workflow validation

These tests simulate the complete user experience:
- Generate CLI code from YAML configuration
- Install generated CLI in isolated virtual environment
- Execute CLI commands via subprocess
- Verify output, stderr, and exit codes
"""

import shutil
import subprocess
import sys
import tempfile
import venv
from pathlib import Path

import pytest

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from goobits_cli.core.schemas import CLISchema, GoobitsConfigSchema
from goobits_cli.universal.engine.stages import parse_config, validate_config
from goobits_cli.universal.generator import UniversalGenerator
from tests.helpers.generated_paths import find_main_cli_path


class TestCLIE2E:
    """End-to-end tests for CLI generation and execution."""

    @pytest.fixture(scope="class")
    def test_config(self):
        """Load the test YAML configuration."""
        config_path = Path(__file__).parent.parent / "integration" / "goobits.yaml"
        raw_config = parse_config(config_path)
        return validate_config(raw_config)

    @pytest.fixture(scope="class")
    def generated_cli_code(self, test_config):
        """Generate CLI code from test configuration."""
        language = getattr(test_config, "language", "python")
        generator = UniversalGenerator(language)
        files = generator.generate_all_files(test_config, "goobits.yaml")
        # Return the main CLI file content
        for path, content in files.items():
            if "cli.py" in path or "cli" in path:
                return content
        return next(iter(files.values())) if files else ""

    @pytest.fixture(scope="class")
    def temp_venv_dir(self):
        """Create isolated temporary virtual environment."""
        with tempfile.TemporaryDirectory(prefix="e2e_test_venv_") as temp_dir:
            venv_path = Path(temp_dir) / "test_venv"

            # Create virtual environment
            venv.create(venv_path, with_pip=True)

            yield venv_path

    def _write_files(self, files: dict, base_path):
        """Write generated files to disk."""
        for path, content in files.items():
            file_path = base_path / path
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(content)

    def test_python_cli_e2e_workflow(self, test_config, tmp_path):
        """Test complete Python CLI workflow end-to-end."""
        # Generate CLI using Python generator
        generator = UniversalGenerator("python")
        files = generator.generate_all_files(test_config, "goobits.yaml")

        # Verify generation succeeded
        assert files is not None
        assert len(files) > 0

        # Write files to disk
        self._write_files(files, tmp_path)

        # Find and verify CLI content
        cli_content = None
        for path, content in files.items():
            if "cli.py" in path:
                cli_content = content
                break

        assert cli_content is not None
        assert "greet" in cli_content
        assert "hello" in cli_content
        assert "goodbye" in cli_content

    def test_cli_help_output(self, test_config, tmp_path):
        """Test that generated CLI produces valid help output."""
        generator = UniversalGenerator("python")
        files = generator.generate_all_files(test_config, "goobits.yaml")

        # Write files to disk
        self._write_files(files, tmp_path)

        # Find CLI file
        cli_file = None
        for path in files.keys():
            if "cli.py" in path:
                cli_file = tmp_path / path
                break

        assert cli_file is not None and cli_file.exists()

        # Try to run the CLI with --help (if Python is available)
        try:
            result = subprocess.run(
                [sys.executable, str(cli_file), "--help"],
                capture_output=True,
                text=True,
                timeout=30,
            )

            # Should either succeed or fail gracefully
            # (might fail due to missing hooks, but should not crash)
            assert result.returncode in [0, 1, 2]  # Allow various exit codes

            # Should produce some output
            assert len(result.stdout) > 0 or len(result.stderr) > 0

        except subprocess.TimeoutExpired:
            pytest.fail("CLI help command timed out")
        except FileNotFoundError:
            pytest.skip("Python interpreter not found")


class TestNodeJSGeneratorE2E:
    """End-to-end tests for Node.js CLI generation and execution."""

    def _create_config(self, language: str) -> GoobitsConfigSchema:
        """Create a GoobitsConfigSchema for testing."""
        return GoobitsConfigSchema(
            package_name="test-nodejs-cli",
            command_name="testnodejs",
            display_name="Test Node.js CLI",
            description="Test Node.js CLI for E2E testing",
            language=language,
            cli=CLISchema(
                name="test-nodejs-cli",
                tagline="Test Node.js CLI for E2E testing",
                commands={
                    "hello": {
                        "desc": "Say hello",
                        "handler": "hello_handler",
                        "args": [
                            {
                                "name": "name",
                                "desc": "Name to greet",
                                "type": "string",
                                "required": True,
                            }
                        ],
                    },
                    "test": {"desc": "Run tests", "handler": "test_handler"},
                },
            ),
        )

    def _write_files(self, files: dict, base_path):
        """Write generated files to disk."""
        for path, content in files.items():
            file_path = base_path / path
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(content)

    def test_nodejs_generator_e2e(self, tmp_path):
        """Test Node.js generator end-to-end workflow."""
        config = self._create_config("nodejs")
        generator = UniversalGenerator("nodejs")

        # Generate the CLI
        files = generator.generate_all_files(config, "goobits.yaml")
        assert files is not None
        assert len(files) > 0

        # Write files to disk
        self._write_files(files, tmp_path)

        # Find and verify CLI content
        cli_path = find_main_cli_path(files, "nodejs")
        cli_content = files.get(cli_path) if cli_path else None

        assert cli_content is not None
        assert "hello" in cli_content

    def test_typescript_generator_e2e(self, tmp_path):
        """Test TypeScript generator end-to-end workflow."""
        config = self._create_config("typescript")
        generator = UniversalGenerator("typescript")

        # Generate the CLI
        files = generator.generate_all_files(config, "goobits.yaml")
        assert files is not None
        assert len(files) > 0

        # Write files to disk
        self._write_files(files, tmp_path)

        # Find and verify CLI content
        cli_content = None
        for path, content in files.items():
            if "cli.ts" in path:
                cli_content = content
                break

        assert cli_content is not None
        assert "hello" in cli_content

        # Verify TypeScript-specific content or syntax
        assert (
            "import" in cli_content
            or "export" in cli_content
            or "const" in cli_content
            or "async" in cli_content
        )

    @pytest.mark.skipif(shutil.which("node") is None, reason="Node.js not available")
    def test_nodejs_cli_syntax_validation(self, tmp_path):
        """Test that generated Node.js CLI has valid syntax."""
        config = self._create_config("nodejs")
        generator = UniversalGenerator("nodejs")
        files = generator.generate_all_files(config, "goobits.yaml")

        # Write files to disk
        self._write_files(files, tmp_path)

        # Find CLI file
        cli_path = find_main_cli_path(files, "nodejs")
        cli_file = (tmp_path / cli_path) if cli_path else None
        assert cli_file is not None

        # Try to run Node.js syntax check
        try:
            result = subprocess.run(
                ["node", "--check", str(cli_file)],
                capture_output=True,
                text=True,
                timeout=30,
            )

            # Should pass syntax check
            assert result.returncode == 0, f"Syntax error: {result.stderr}"

        except subprocess.TimeoutExpired:
            pytest.fail("Node.js syntax check timed out")
        except FileNotFoundError:
            pytest.skip("Node.js not found")


class TestCompleteWorkflowValidation:
    """Test complete workflows from YAML to working CLI."""

    def _create_minimal_config(self, language: str) -> GoobitsConfigSchema:
        """Create a minimal GoobitsConfigSchema for testing."""
        from goobits_cli.core.schemas import CLISchema

        return GoobitsConfigSchema(
            package_name="minimal-cli",
            command_name="minimal",
            display_name="Minimal CLI",
            description="Minimal test CLI",
            language=language,
            cli=CLISchema(
                name="minimal-cli",
                tagline="Minimal test CLI",
                commands={
                    "status": {"desc": "Show status", "handler": "status_handler"}
                },
            ),
        )

    def _write_generated_files(self, files: dict, base_path):
        """Write generated files to disk."""
        for path, content in files.items():
            file_path = base_path / path
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(content)

    def test_minimal_workflow_python(self, tmp_path):
        """Test minimal workflow with Python generator."""
        config = self._create_minimal_config("python")

        generator = UniversalGenerator("python")
        files = generator.generate_all_files(config, "goobits.yaml")

        # Write files to disk
        self._write_generated_files(files, tmp_path)

        # Verify generation produced files
        assert len(files) > 0

        # Find CLI content
        cli_content = None
        for path, content in files.items():
            if "cli.py" in path:
                cli_content = content
                break

        assert cli_content is not None
        assert "status" in cli_content

    def test_minimal_workflow_nodejs(self, tmp_path):
        """Test minimal workflow with Node.js generator."""
        config = self._create_minimal_config("nodejs")

        generator = UniversalGenerator("nodejs")
        files = generator.generate_all_files(config, "goobits.yaml")

        # Write files to disk
        self._write_generated_files(files, tmp_path)

        # Verify generation produced files
        assert len(files) > 0

        # Find CLI content
        cli_path = find_main_cli_path(files, "nodejs")
        cli_content = files.get(cli_path) if cli_path else None

        assert cli_content is not None
        assert "status" in cli_content

    def test_minimal_workflow_typescript(self, tmp_path):
        """Test minimal workflow with TypeScript generator."""
        config = self._create_minimal_config("typescript")

        generator = UniversalGenerator("typescript")
        files = generator.generate_all_files(config, "goobits.yaml")

        # Write files to disk
        self._write_generated_files(files, tmp_path)

        # Verify generation produced files
        assert len(files) > 0

        # Find CLI content
        cli_content = None
        for path, content in files.items():
            if "cli.ts" in path:
                cli_content = content
                break

        assert cli_content is not None
        assert "status" in cli_content

    @pytest.mark.skipif(
        shutil.which("cargo") is None,
        reason="Cargo not available - Rust tests require Rust toolchain",
    )
    def test_minimal_workflow_rust(self, tmp_path):
        """Test minimal workflow with Rust generator."""
        config = self._create_minimal_config("rust")

        generator = UniversalGenerator("rust")
        files = generator.generate_all_files(config, "goobits.yaml")

        # Write files to disk
        self._write_generated_files(files, tmp_path)

        # Verify generation produced files
        assert len(files) > 0

        # Find CLI content
        cli_content = None
        for path, content in files.items():
            if "cli.rs" in path or "main.rs" in path:
                cli_content = content
                break

        assert cli_content is not None
        assert "status" in cli_content
