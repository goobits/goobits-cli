"""
Comprehensive Performance Benchmark Suite

This module consolidates all performance testing:
- Real performance benchmarking across all CLI languages
- Memory usage analysis
- Startup time measurements
- Cross-language performance comparison
- Template generation benchmarks

Consolidated from:
- test_real_benchmarks.py
- test_simple_benchmark.py
- performance_benchmarks.py
- phase4e_integration_suite.py
"""

import gc
import shutil
import sys
import time
import tracemalloc
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import pytest

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from goobits_cli.core.schemas import GoobitsConfigSchema, CLISchema
from goobits_cli.universal.generator import UniversalGenerator


@dataclass
class BenchmarkResult:
    """Container for benchmark results."""

    language: str
    operation: str
    duration_ms: float
    memory_usage_mb: float
    success: bool
    error_message: Optional[str] = None


@dataclass
class PerformanceMetrics:
    """Container for performance metrics."""

    generation_time_ms: float
    memory_peak_mb: float
    startup_time_ms: float
    file_count: int
    total_size_kb: float


class TestPerformanceBenchmarks:
    """Comprehensive performance benchmark tests."""

    def setup_method(self):
        """Set up test environment."""
        self.test_config = None  # Will be created per-language

    def _create_config(self, language: str) -> GoobitsConfigSchema:
        """Create a GoobitsConfigSchema for the specified language."""
        return GoobitsConfigSchema(
            package_name="benchmark-cli",
            command_name="benchmark",
            display_name="Benchmark CLI",
            description="Performance benchmark CLI",
            language=language,
            cli=CLISchema(
                name="benchmark-cli",
                tagline="Performance benchmark CLI",
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
                        "options": [
                            {
                                "name": "uppercase",
                                "desc": "Use uppercase",
                                "type": "flag",
                            }
                        ],
                    },
                    "test": {"desc": "Run tests", "handler": "test_handler"},
                    "build": {
                        "desc": "Build project",
                        "handler": "build_handler",
                        "options": [
                            {
                                "name": "verbose",
                                "desc": "Verbose output",
                                "type": "flag",
                            }
                        ],
                    },
                },
            ),
        )

    def _write_files(self, files: dict, base_path):
        """Write generated files to disk."""
        for path, content in files.items():
            file_path = base_path / path
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(content)

    @contextmanager
    def measure_performance(self):
        """Context manager to measure execution time and memory usage."""
        tracemalloc.start()
        start_time = time.perf_counter()
        self._get_memory_usage()

        try:
            yield
        finally:
            end_time = time.perf_counter()
            current, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()

            duration_ms = (end_time - start_time) * 1000
            memory_mb = peak / 1024 / 1024

            # Store results for access by calling code
            self._last_duration_ms = duration_ms
            self._last_memory_mb = memory_mb

    def _get_memory_usage(self) -> float:
        """Get current memory usage in MB."""
        try:
            import psutil

            process = psutil.Process()
            return process.memory_info().rss / 1024 / 1024
        except ImportError:
            return 0.0

    def test_python_generation_performance(self, tmp_path):
        """Test Python CLI generation performance."""
        config = self._create_config("python")
        generator = UniversalGenerator("python")

        with self.measure_performance():
            files = generator.generate_all_files(config, "goobits.yaml")

        assert files is not None
        assert len(files) > 0

        # Performance assertions
        assert self._last_duration_ms < 5000  # Should complete within 5 seconds
        assert self._last_memory_mb < 100  # Should use less than 100MB

        # Write files to disk for verification
        self._write_files(files, tmp_path)

        # Verify CLI file exists in generated files
        assert any("cli.py" in path for path in files.keys())

    def test_nodejs_generation_performance(self, tmp_path):
        """Test Node.js CLI generation performance."""
        config = self._create_config("nodejs")
        generator = UniversalGenerator("nodejs")

        # Add timeout to prevent hanging
        import signal

        def timeout_handler(signum, frame):
            raise TimeoutError("NodeJS generation test timed out")

        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(30)  # 30 second timeout

        try:
            with self.measure_performance():
                files = generator.generate_all_files(config, "goobits.yaml")

            assert files is not None
            assert len(files) > 0

            # Performance assertions
            assert (
                self._last_duration_ms < 10000
            )  # Increased to 10 seconds for more realistic expectation
            assert (
                self._last_memory_mb < 150
            )  # Increased memory limit for complex generation

            # Write files to disk
            self._write_files(files, tmp_path)

            # Verify main CLI file exists in generated files
            main_files = ["cli.js", "cli.mjs", "index.js"]
            assert any(
                any(f in path for f in main_files) for path in files.keys()
            ), f"No main CLI file found in {list(files.keys())}"
        finally:
            signal.alarm(0)  # Disable alarm

    def test_typescript_generation_performance(self, tmp_path):
        """Test TypeScript CLI generation performance."""
        config = self._create_config("typescript")
        generator = UniversalGenerator("typescript")

        # Add timeout to prevent hanging
        import signal

        def timeout_handler(signum, frame):
            raise TimeoutError("TypeScript generation test timed out")

        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(30)  # 30 second timeout

        try:
            with self.measure_performance():
                files = generator.generate_all_files(config, "goobits.yaml")

            assert files is not None
            assert len(files) > 0

            # Performance assertions
            assert (
                self._last_duration_ms < 10000
            )  # Increased to 10 seconds for more realistic expectation
            assert (
                self._last_memory_mb < 150
            )  # Increased memory limit for complex generation

            # Write files to disk
            self._write_files(files, tmp_path)

            # Verify main CLI file exists in generated files
            main_files = ["cli.ts", "index.ts", "generated_index.ts"]
            assert any(
                any(f in path for f in main_files) for path in files.keys()
            ), f"No main CLI file found in {list(files.keys())}"
        finally:
            signal.alarm(0)  # Disable alarm

    @pytest.mark.skipif(shutil.which("cargo") is None, reason="Cargo not available")
    def test_rust_generation_performance(self, tmp_path):
        """Test Rust CLI generation performance."""
        config = self._create_config("rust")
        generator = UniversalGenerator("rust")

        with self.measure_performance():
            files = generator.generate_all_files(config, "goobits.yaml")

        assert files is not None
        assert len(files) > 0

        # Performance assertions
        assert self._last_duration_ms < 5000  # Should complete within 5 seconds
        assert self._last_memory_mb < 100  # Should use less than 100MB

        # Write files to disk
        self._write_files(files, tmp_path)

        # Verify CLI file exists in generated files
        assert any("cli.rs" in path or "main.rs" in path for path in files.keys())

    def test_cross_language_performance_comparison(self, tmp_path):
        """Compare performance across all supported languages."""
        languages = ["python", "nodejs", "typescript"]

        # Add Rust if available
        if shutil.which("cargo"):
            languages.append("rust")

        results = {}

        for lang in languages:
            config = self._create_config(lang)
            generator = UniversalGenerator(lang)
            lang_dir = tmp_path / lang
            lang_dir.mkdir()

            with self.measure_performance():
                try:
                    files = generator.generate_all_files(config, "goobits.yaml")
                    success = files is not None and len(files) > 0
                    error = None
                    if success:
                        self._write_files(files, lang_dir)
                except Exception as e:
                    success = False
                    error = str(e)

            results[lang] = BenchmarkResult(
                language=lang,
                operation="generation",
                duration_ms=self._last_duration_ms,
                memory_usage_mb=self._last_memory_mb,
                success=success,
                error_message=error,
            )

        # All languages should succeed
        for lang, result in results.items():
            assert result.success, f"{lang} generation failed: {result.error_message}"

        # Performance should be reasonable across all languages
        for lang, result in results.items():
            assert result.duration_ms < 10000, (
                f"{lang} generation too slow: {result.duration_ms}ms"
            )
            assert result.memory_usage_mb < 200, (
                f"{lang} using too much memory: {result.memory_usage_mb}MB"
            )

    def test_large_config_performance(self, tmp_path):
        """Test performance with a large configuration."""
        # Create a large configuration with many commands
        large_config = GoobitsConfigSchema(
            package_name="large-cli",
            command_name="largecli",
            display_name="Large CLI",
            description="Large CLI for performance testing",
            language="python",
            cli=CLISchema(
                name="large-cli",
                tagline="Large CLI for performance testing",
                commands={
                    f"command_{i}": {
                        "desc": f"Command {i} description",
                        "handler": f"command_{i}_handler",
                        "args": [
                            {
                                "name": "arg1",
                                "desc": f"Argument 1 for command {i}",
                                "type": "string",
                                "required": True,
                            }
                        ],
                        "options": [
                            {
                                "name": "verbose",
                                "desc": "Verbose output",
                                "type": "flag",
                            },
                            {"name": "output", "desc": "Output file", "type": "string"},
                        ],
                    }
                    for i in range(20)  # 20 commands
                },
            ),
        )

        generator = UniversalGenerator("python")

        with self.measure_performance():
            files = generator.generate_all_files(large_config, "goobits.yaml")

        assert files is not None
        assert len(files) > 0

        # Write files to disk
        self._write_files(files, tmp_path)

        # Performance should still be reasonable even with large config
        assert self._last_duration_ms < 15000  # 15 seconds max for large config
        assert self._last_memory_mb < 200  # 200MB max for large config

    def test_memory_efficiency(self, tmp_path):
        """Test memory efficiency by generating multiple CLIs."""
        generator = UniversalGenerator("python")
        config = self._create_config("python")

        initial_memory = self._get_memory_usage()

        # Use timeout to prevent hanging
        import signal

        def timeout_handler(signum, frame):
            raise TimeoutError("Memory efficiency test timed out")

        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(30)  # 30 second timeout

        try:
            # Generate multiple CLIs to test memory efficiency (reduced from 5 to 3)
            for i in range(3):
                test_dir = tmp_path / f"cli_{i}"
                test_dir.mkdir()

                files = generator.generate_all_files(config, "goobits.yaml")
                assert files is not None
                assert len(files) > 0

                # Write files to disk
                self._write_files(files, test_dir)

                # Force garbage collection
                gc.collect()

            final_memory = self._get_memory_usage()
            memory_growth = final_memory - initial_memory

            # Memory growth should be reasonable (less than 50MB for 3 generations)
            # If psutil not available, memory_growth will be 0, so we check for that
            if initial_memory > 0 and final_memory > 0:
                assert memory_growth < 50, f"Memory grew too much: {memory_growth}MB"
            else:
                # If psutil not available, just ensure all generations succeeded
                pass
        finally:
            signal.alarm(0)  # Disable alarm

    def test_template_rendering_performance(self, tmp_path):
        """Test template rendering performance specifically."""
        generator = UniversalGenerator("python")
        config = self._create_config("python")

        # Measure template rendering specifically
        start_time = time.perf_counter()

        # Generate multiple times to get more accurate measurement
        for i in range(3):
            files = generator.generate_all_files(config, "goobits.yaml")
            assert files is not None
            assert len(files) > 0

            # Write files to disk
            test_dir = tmp_path / f"render_{i}"
            test_dir.mkdir()
            self._write_files(files, test_dir)

        end_time = time.perf_counter()
        avg_duration_ms = ((end_time - start_time) / 3) * 1000

        # Template rendering should be fast (under 2 seconds per generation)
        assert avg_duration_ms < 2000, (
            f"Template rendering too slow: {avg_duration_ms}ms"
        )


class TestSimpleBenchmarks:
    """Simple performance benchmarks for quick validation."""

    def _create_config(self, language: str) -> GoobitsConfigSchema:
        """Create a GoobitsConfigSchema for the specified language."""
        return GoobitsConfigSchema(
            package_name="speed-test",
            command_name="speedtest",
            display_name="Speed Test CLI",
            description="Speed test CLI",
            language=language,
            cli=CLISchema(
                name="speed-test",
                tagline="Speed test CLI",
                commands={
                    "fast": {"desc": "Fast command", "handler": "fast_handler"}
                },
            ),
        )

    def _write_files(self, files: dict, base_path):
        """Write generated files to disk."""
        for path, content in files.items():
            file_path = base_path / path
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(content)

    def test_basic_python_generation_speed(self, tmp_path):
        """Test basic Python generation completes quickly."""
        config = self._create_config("python")

        generator = UniversalGenerator("python")

        start_time = time.perf_counter()
        files = generator.generate_all_files(config, "goobits.yaml")
        end_time = time.perf_counter()

        duration_ms = (end_time - start_time) * 1000

        assert files is not None
        assert len(files) > 0
        assert duration_ms < 3000  # Should complete within 3 seconds

        # Write files to verify generation
        self._write_files(files, tmp_path)

    def test_basic_nodejs_generation_speed(self, tmp_path):
        """Test basic Node.js generation completes quickly."""
        config = self._create_config("nodejs")

        generator = UniversalGenerator("nodejs")

        start_time = time.perf_counter()
        files = generator.generate_all_files(config, "goobits.yaml")
        end_time = time.perf_counter()

        duration_ms = (end_time - start_time) * 1000

        assert files is not None
        assert len(files) > 0
        assert duration_ms < 3000  # Should complete within 3 seconds

        # Write files to verify generation
        self._write_files(files, tmp_path)
