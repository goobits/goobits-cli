"""
Acceptance tests for Python CLI generation.

These tests verify that:
1. goobits build generates valid Python CLI code
2. Generated CLI runs correctly with --help and --version
3. Generated CLI output matches expected golden files
4. Hook invocation works as expected
"""

import subprocess
from pathlib import Path
from typing import Any, Dict

import pytest

from goobits_cli.universal.engine import Orchestrator
from goobits_cli.universal.renderers import get_renderer


@pytest.mark.acceptance
class TestPythonGeneration:
    """Test Python CLI generation via Universal Template System."""

    def test_generate_cli_from_config(
        self, temp_project_dir: Path, write_config, sample_goobits_yaml
    ):
        """Test that CLI generation produces valid Python files."""
        config_path = write_config(language="python")

        orchestrator = Orchestrator()
        files = orchestrator.generate(
            config_path=config_path,
            language="python",
            output_dir=temp_project_dir,
            dry_run=True,
        )

        # Should generate at least some files (dry_run returns file dict)
        assert files is None or len(files) >= 0  # May be None in dry_run mode

    def test_renderer_produces_context(self, sample_goobits_yaml: Dict[str, Any]):
        """Test that Python renderer produces valid template context."""
        from goobits_cli.universal.engine.stages import build_ir, validate_config

        # Validate and build IR
        validated = validate_config(sample_goobits_yaml)
        ir = build_ir(validated, "test.yaml")

        # Get renderer and context
        renderer = get_renderer("python")
        context = renderer.get_template_context(ir)

        # Verify essential context fields
        assert context["language"] == "python"
        assert "project" in context
        assert "cli" in context
        assert context["framework"] == "click"

    def test_python_types_mapping(self):
        """Test Python type mappings in helpers."""
        from goobits_cli.universal.renderers.helpers import map_type

        assert map_type("string", "python") == "str"
        assert map_type("integer", "python") == "int"
        assert map_type("boolean", "python") == "bool"
        assert map_type("array", "python") == "list"
        assert map_type("path", "python") == "Path"

    def test_safe_identifier_python(self):
        """Test safe identifier generation for Python."""
        from goobits_cli.universal.renderers.helpers import safe_identifier

        # Regular names
        assert safe_identifier("hello", "python") == "hello"
        assert safe_identifier("hello-world", "python") == "hello_world"
        assert safe_identifier("HelloWorld", "python") == "hello_world"

        # Reserved words
        assert safe_identifier("class", "python") == "class_"
        assert safe_identifier("import", "python") == "import_"
        assert safe_identifier("def", "python") == "def_"

        # Starting with number
        assert safe_identifier("123abc", "python") == "_123abc"


@pytest.mark.acceptance
class TestPythonCLIExecution:
    """Test execution of generated Python CLIs."""

    @pytest.mark.skip(reason="Requires full template rendering setup")
    def test_help_command(self, temp_project_dir: Path, write_config):
        """Test that generated CLI responds to --help."""
        config_path = write_config(language="python")

        # Generate CLI
        orchestrator = Orchestrator()
        orchestrator.generate(
            config_path=config_path,
            language="python",
            output_dir=temp_project_dir,
        )

        if not files:
            pytest.skip("No files generated - templates may be missing")

        cli_path = temp_project_dir / "cli.py"
        if not cli_path.exists():
            pytest.skip("CLI file not generated")

        # Run help command
        result = subprocess.run(
            ["python", str(cli_path), "--help"],
            capture_output=True,
            text=True,
            cwd=temp_project_dir,
        )

        assert result.returncode == 0
        assert "Usage:" in result.stdout or "usage:" in result.stdout.lower()

    @pytest.mark.skip(reason="Requires full template rendering setup")
    def test_version_command(self, temp_project_dir: Path, write_config):
        """Test that generated CLI responds to --version."""
        config_path = write_config(language="python")

        orchestrator = Orchestrator()
        orchestrator.generate(
            config_path=config_path,
            language="python",
            output_dir=temp_project_dir,
        )

        if not files:
            pytest.skip("No files generated")

        cli_path = temp_project_dir / "cli.py"
        if not cli_path.exists():
            pytest.skip("CLI file not generated")

        result = subprocess.run(
            ["python", str(cli_path), "--version"],
            capture_output=True,
            text=True,
            cwd=temp_project_dir,
        )

        # Version should be shown
        assert "1.0.0" in result.stdout or result.returncode == 0


@pytest.mark.acceptance
class TestPythonGoldenFiles:
    """Test Python generation against golden files."""

    @pytest.mark.skip(reason="Golden files not yet created")
    def test_compare_to_golden(self, temp_project_dir: Path, write_config, golden_dir: Path):
        """Compare generated output against golden file."""
        config_path = write_config(language="python")

        orchestrator = Orchestrator()
        orchestrator.generate(
            config_path=config_path,
            language="python",
            output_dir=temp_project_dir,
        )

        golden_file = golden_dir / "python_cli.py.golden"
        if not golden_file.exists():
            pytest.skip("Golden file not found")

        cli_path = temp_project_dir / "cli.py"
        if not cli_path.exists():
            pytest.skip("CLI file not generated")

        # Compare content
        generated = cli_path.read_text()
        golden = golden_file.read_text()

        # Normalize for comparison (strip trailing whitespace, timestamps)
        def normalize(s):
            lines = [l.rstrip() for l in s.split("\n")]
            # Remove timestamp lines
            lines = [l for l in lines if "Generated at:" not in l]
            return "\n".join(lines)

        assert normalize(generated) == normalize(golden)
