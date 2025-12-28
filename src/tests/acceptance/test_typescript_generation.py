"""
Acceptance tests for TypeScript CLI generation.
"""

import shutil
from pathlib import Path
from typing import Any, Dict

import pytest

from goobits_cli.universal.engine import Orchestrator
from goobits_cli.universal.renderers import get_renderer


@pytest.mark.acceptance
class TestTypeScriptGeneration:
    """Test TypeScript CLI generation via Universal Template System."""

    def test_renderer_produces_context(self, sample_goobits_yaml: Dict[str, Any]):
        """Test that TypeScript renderer produces valid template context."""
        from goobits_cli.universal.engine.stages import build_ir, validate_config

        sample_goobits_yaml["language"] = "typescript"
        validated = validate_config(sample_goobits_yaml)
        ir = build_ir(validated, "test.yaml")

        renderer = get_renderer("typescript")
        context = renderer.get_template_context(ir)

        assert context["language"] == "typescript"
        assert "project" in context
        assert "cli" in context

    def test_typescript_types_mapping(self):
        """Test TypeScript type mappings in helpers."""
        from goobits_cli.universal.renderers.helpers import map_type

        assert map_type("string", "typescript") == "string"
        assert map_type("integer", "typescript") == "number"
        assert map_type("boolean", "typescript") == "boolean"
        assert map_type("any", "typescript") == "unknown"
        assert map_type("object", "typescript") == "Record<string, unknown>"

    def test_safe_identifier_typescript(self):
        """Test safe identifier generation for TypeScript."""
        from goobits_cli.universal.renderers.helpers import safe_identifier

        # Same as Node.js (camelCase)
        assert safe_identifier("hello", "typescript") == "helloWorld" or safe_identifier("hello-world", "typescript") == "helloWorld"

        # TypeScript-specific reserved words
        assert safe_identifier("interface", "typescript") == "interface_"
        assert safe_identifier("type", "typescript") == "type_"
        assert safe_identifier("enum", "typescript") == "enum_"

    @pytest.mark.skipif(
        not shutil.which("node"),
        reason="Node.js/TypeScript not installed"
    )
    def test_generate_cli_produces_files(
        self, temp_project_dir: Path, write_config, sample_goobits_yaml
    ):
        """Test that CLI generation produces TypeScript files."""
        config_path = write_config(language="typescript")

        orchestrator = Orchestrator()
        files = orchestrator.generate(
            config_path=config_path,
            language="typescript",
            output_dir=temp_project_dir,
            dry_run=True,
        )

        assert isinstance(files, list)


@pytest.mark.acceptance
@pytest.mark.skipif(not shutil.which("npx"), reason="npx not installed")
class TestTypeScriptCLIExecution:
    """Test execution of generated TypeScript CLIs."""

    @pytest.mark.skip(reason="Requires full template rendering and ts-node setup")
    def test_help_command(self, temp_project_dir: Path, write_config):
        """Test that generated CLI responds to --help."""
        pass
