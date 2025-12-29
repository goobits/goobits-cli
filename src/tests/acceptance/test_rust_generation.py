"""
Acceptance tests for Rust CLI generation.
"""

import shutil
from pathlib import Path
from typing import Any, Dict

import pytest

from goobits_cli.universal.engine import Orchestrator
from goobits_cli.universal.renderers import get_renderer


@pytest.mark.acceptance
class TestRustGeneration:
    """Test Rust CLI generation via Universal Template System."""

    def test_renderer_produces_context(self, sample_goobits_yaml: Dict[str, Any]):
        """Test that Rust renderer produces valid template context."""
        from goobits_cli.universal.engine.stages import build_ir, validate_config

        sample_goobits_yaml["language"] = "rust"
        validated = validate_config(sample_goobits_yaml)
        ir = build_ir(validated, "test.yaml")

        renderer = get_renderer("rust")
        context = renderer.get_template_context(ir)

        assert context["language"] == "rust"
        assert "project" in context
        assert "cli" in context

    def test_rust_types_mapping(self):
        """Test Rust type mappings in helpers."""
        from goobits_cli.universal.renderers.helpers import map_type

        assert map_type("string", "rust") == "String"
        assert map_type("integer", "rust") == "i64"
        assert map_type("float", "rust") == "f64"
        assert map_type("boolean", "rust") == "bool"
        assert map_type("path", "rust") == "PathBuf"
        assert map_type("void", "rust") == "()"

    def test_safe_identifier_rust(self):
        """Test safe identifier generation for Rust."""
        from goobits_cli.universal.renderers.helpers import safe_identifier

        # Regular names (snake_case)
        assert safe_identifier("hello", "rust") == "hello"
        assert safe_identifier("hello-world", "rust") == "hello_world"
        assert safe_identifier("HelloWorld", "rust") == "hello_world"

        # Rust reserved words
        assert safe_identifier("fn", "rust") == "fn_"
        assert safe_identifier("impl", "rust") == "impl_"
        assert safe_identifier("struct", "rust") == "struct_"
        assert safe_identifier("mut", "rust") == "mut_"

    @pytest.mark.skipif(
        not shutil.which("cargo"),
        reason="Cargo/Rust not installed"
    )
    def test_generate_cli_produces_files(
        self, temp_project_dir: Path, write_config, sample_goobits_yaml
    ):
        """Test that CLI generation produces Rust files."""
        config_path = write_config(language="rust")

        orchestrator = Orchestrator()
        files = orchestrator.generate(
            config_path=config_path,
            language="rust",
            output_dir=temp_project_dir,
            dry_run=True,
        )

        assert isinstance(files, list)
