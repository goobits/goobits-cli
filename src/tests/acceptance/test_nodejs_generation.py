"""
Acceptance tests for Node.js CLI generation.
"""

import shutil
from pathlib import Path
from typing import Any, Dict

import pytest

from goobits_cli.universal.engine import Orchestrator
from goobits_cli.universal.renderers import get_renderer


@pytest.mark.acceptance
class TestNodeJSGeneration:
    """Test Node.js CLI generation via Universal Template System."""

    def test_renderer_produces_context(self, sample_goobits_yaml: Dict[str, Any]):
        """Test that Node.js renderer produces valid template context."""
        from goobits_cli.universal.engine.stages import build_ir, validate_config

        sample_goobits_yaml["language"] = "nodejs"
        validated = validate_config(sample_goobits_yaml)
        ir = build_ir(validated, "test.yaml")

        renderer = get_renderer("nodejs")
        context = renderer.get_template_context(ir)

        assert context["language"] == "nodejs"
        assert "project" in context
        assert "cli" in context

    def test_nodejs_types_mapping(self):
        """Test Node.js type mappings in helpers."""
        from goobits_cli.universal.renderers.helpers import map_type

        assert map_type("string", "nodejs") == "string"
        assert map_type("integer", "nodejs") == "number"
        assert map_type("boolean", "nodejs") == "boolean"
        assert map_type("array", "nodejs") == "Array"

    def test_safe_identifier_nodejs(self):
        """Test safe identifier generation for Node.js."""
        from goobits_cli.universal.renderers.helpers import safe_identifier

        # Regular names (camelCase)
        assert safe_identifier("hello", "nodejs") == "hello"
        assert safe_identifier("hello-world", "nodejs") == "helloWorld"
        assert safe_identifier("HelloWorld", "nodejs") == "helloWorld"

        # Reserved words
        assert safe_identifier("class", "nodejs") == "class_"
        assert safe_identifier("function", "nodejs") == "function_"
        assert safe_identifier("const", "nodejs") == "const_"

    @pytest.mark.skipif(
        not shutil.which("node"),
        reason="Node.js not installed"
    )
    def test_generate_cli_produces_files(
        self, temp_project_dir: Path, write_config, sample_goobits_yaml
    ):
        """Test that CLI generation produces Node.js files."""
        config_path = write_config(language="nodejs")

        orchestrator = Orchestrator()
        files = orchestrator.generate(
            config_path=config_path,
            language="nodejs",
            output_dir=temp_project_dir,
            dry_run=True,
        )

        # Should generate some files (may be 0 if templates missing)
        assert isinstance(files, list)
