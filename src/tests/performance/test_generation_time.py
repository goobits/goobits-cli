"""
Performance tests for generation time.

These tests verify that:
1. Python generation completes within 1 second
2. Node.js generation completes within 1 second
3. TypeScript generation completes within 1 second
4. Rust generation completes within 1 second
"""

import time
from pathlib import Path
from typing import Any, Dict

import pytest

from goobits_cli.universal.engine.stages import build_ir, validate_config
from goobits_cli.universal.renderers import get_renderer


@pytest.fixture
def sample_config() -> Dict[str, Any]:
    """Provide a sample configuration for benchmarking."""
    return {
        "package_name": "benchmark_cli",
        "command_name": "benchcli",
        "display_name": "Benchmark CLI",
        "description": "A benchmark CLI",
        "version": "1.0.0",
        "language": "python",
        "cli": {
            "name": "Benchmark CLI",
            "tagline": "A CLI for performance benchmarking",
            "commands": {
                "hello": {
                    "desc": "Say hello",
                    "args": [{"name": "name", "desc": "Name", "required": False}],
                    "options": [
                        {"name": "loud", "type": "bool", "desc": "Be loud"},
                        {"name": "times", "type": "int", "default": 1, "desc": "Times"},
                    ],
                },
                "goodbye": {"desc": "Say goodbye"},
                "config": {
                    "desc": "Configuration",
                    "subcommands": {
                        "show": {"desc": "Show config"},
                        "set": {"desc": "Set config"},
                    },
                },
            },
        },
    }


@pytest.mark.performance
class TestGenerationTime:
    """Test that generation completes within time limits."""

    MAX_GENERATION_TIME = 1.0  # 1 second target

    def test_python_generation_time(
        self, sample_config: Dict[str, Any], tmp_path: Path
    ):
        """Test Python generation completes within 1 second."""
        sample_config["language"] = "python"

        start = time.perf_counter()

        validated = validate_config(sample_config)
        ir = build_ir(validated, "benchmark.yaml")
        renderer = get_renderer("python")
        renderer.get_template_context(ir)
        _ = renderer.get_output_structure(ir)

        elapsed = time.perf_counter() - start

        assert (
            elapsed < self.MAX_GENERATION_TIME
        ), f"Python generation took {elapsed:.2f}s, expected < {self.MAX_GENERATION_TIME}s"

    def test_nodejs_generation_time(
        self, sample_config: Dict[str, Any], tmp_path: Path
    ):
        """Test Node.js generation completes within 1 second."""
        sample_config["language"] = "nodejs"

        start = time.perf_counter()

        validated = validate_config(sample_config)
        ir = build_ir(validated, "benchmark.yaml")
        renderer = get_renderer("nodejs")
        renderer.get_template_context(ir)
        _ = renderer.get_output_structure(ir)

        elapsed = time.perf_counter() - start

        assert (
            elapsed < self.MAX_GENERATION_TIME
        ), f"Node.js generation took {elapsed:.2f}s, expected < {self.MAX_GENERATION_TIME}s"

    def test_typescript_generation_time(
        self, sample_config: Dict[str, Any], tmp_path: Path
    ):
        """Test TypeScript generation completes within 1 second."""
        sample_config["language"] = "typescript"

        start = time.perf_counter()

        validated = validate_config(sample_config)
        ir = build_ir(validated, "benchmark.yaml")
        renderer = get_renderer("typescript")
        renderer.get_template_context(ir)
        _ = renderer.get_output_structure(ir)

        elapsed = time.perf_counter() - start

        assert (
            elapsed < self.MAX_GENERATION_TIME
        ), f"TypeScript generation took {elapsed:.2f}s, expected < {self.MAX_GENERATION_TIME}s"

    def test_rust_generation_time(self, sample_config: Dict[str, Any], tmp_path: Path):
        """Test Rust generation completes within 1 second."""
        sample_config["language"] = "rust"

        start = time.perf_counter()

        validated = validate_config(sample_config)
        ir = build_ir(validated, "benchmark.yaml")
        renderer = get_renderer("rust")
        renderer.get_template_context(ir)
        _ = renderer.get_output_structure(ir)

        elapsed = time.perf_counter() - start

        assert (
            elapsed < self.MAX_GENERATION_TIME
        ), f"Rust generation took {elapsed:.2f}s, expected < {self.MAX_GENERATION_TIME}s"


@pytest.mark.performance
class TestIRBuildTime:
    """Test IR building performance."""

    def test_ir_build_time(self, sample_config: Dict[str, Any]):
        """Test IR building completes quickly."""
        start = time.perf_counter()

        validated = validate_config(sample_config)
        ir = build_ir(validated, "benchmark.yaml")

        elapsed = time.perf_counter() - start

        # IR building should be very fast (< 100ms)
        assert elapsed < 0.1, f"IR building took {elapsed:.3f}s, expected < 0.1s"
        assert ir is not None
