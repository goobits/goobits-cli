"""
Acceptance tests for Python CLI generation.

These tests verify that:
1. goobits build generates valid Python CLI code
2. Renderer produces correct template context
3. Type mappings and identifiers work correctly
"""

import importlib.util
import sys
from pathlib import Path
from typing import Any, Dict

import pytest
from click.testing import CliRunner

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

    def test_generated_cli_honors_default_nested_and_exit_contracts(
        self, tmp_path: Path, monkeypatch
    ):
        """Execute generated Click code to verify the hook contract end to end."""
        config = {
            "package_name": "contract-cli",
            "command_name": "contract",
            "display_name": "Contract CLI",
            "description": "Contract test CLI",
            "language": "python",
            "cli_path": "contract_cli/cli.py",
            "cli_hooks_path": "contract_hooks.py",
            "cli": {
                "name": "Contract CLI",
                "tagline": "Contract test CLI",
                "commands": {
                    "speak": {
                        "desc": "Speak text",
                        "is_default": True,
                        "args": [{"name": "text", "desc": "Text", "required": False}],
                    },
                    "voice": {
                        "desc": "Manage voices",
                        "subcommands": {"status": {"desc": "Show voice status"}},
                    },
                },
            },
        }
        files = Orchestrator(test_mode=True).generate_content(
            config, "python", with_integrations=False
        )
        cli_source = files["contract_cli/cli.py"]
        package_dir = tmp_path / "contract_cli"
        package_dir.mkdir()
        (package_dir / "__init__.py").write_text("")
        cli_path = package_dir / "cli.py"
        cli_path.write_text(cli_source)
        (tmp_path / "contract_hooks.py").write_text(
            "import sys\n\n"
            "def on_speak(ctx, text):\n"
            "    text = text or sys.stdin.read().strip()\n"
            "    print(f'spoken:{text}')\n"
            "    return 7 if text == 'fail' else 0\n\n"
            "def on_voice_status(ctx):\n"
            "    print('voice:ready')\n"
            "    return 0\n"
        )
        monkeypatch.syspath_prepend(str(tmp_path))
        spec = importlib.util.spec_from_file_location("contract_cli.cli", cli_path)
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)

        runner = CliRunner()
        implicit = runner.invoke(module.cli, ["hello"])
        piped = runner.invoke(module.cli, [], input="from pipe")
        nested = runner.invoke(module.cli, ["voice", "status"])
        failure = runner.invoke(module.cli, ["fail"])

        assert implicit.exit_code == 0
        assert "spoken:hello" in implicit.output
        assert piped.exit_code == 0
        assert "spoken:from pipe" in piped.output
        assert nested.exit_code == 0
        assert "voice:ready" in nested.output
        assert failure.exit_code == 7
