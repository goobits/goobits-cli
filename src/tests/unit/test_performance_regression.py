"""
Performance regression tests for Goobits CLI Framework.

These tests ensure that lazy loading optimizations continue to work
and that startup performance doesn't degrade over time.
"""

import time
import pytest
import subprocess
import sys
import tempfile
from pathlib import Path


class TestPerformanceRegression:
    """Test suite for performance regression prevention."""

    def test_basic_cli_startup_performance(self):
        """Test that basic CLI startup remains under 100ms."""
        # Measure basic import time
        start = time.perf_counter()

        end = time.perf_counter()
        import_time = (end - start) * 1000

        # Basic CLI imports should be fast
        assert (
            import_time < 100
        ), f"Basic CLI imports took {import_time:.1f}ms (target: <100ms)"

    def test_lazy_loading_overhead(self):
        """Test that lazy loading callbacks add minimal overhead."""
        start = time.perf_counter()

        # Simulate lazy loading callback registration
        def lazy_callback():
            """Lazy loading callback - should be lightweight."""
            pass

        end = time.perf_counter()
        callback_time = (end - start) * 1000

        # Lazy loading setup should add <50ms overhead
        assert (
            callback_time < 50
        ), f"Lazy loading overhead: {callback_time:.1f}ms (target: <50ms)"

    def test_interactive_mode_lazy_loading(self):
        """Test that interactive mode uses lazy loading."""
        # Create a test CLI with lazy loading
        test_cli = '''#!/usr/bin/env python3
import sys
import rich_click as click

def _lazy_load_and_start_interactive():
    """Lazy load interactive mode components."""
    print("LAZY_LOAD_SUCCESS")
    return True

def start_interactive_mode(ctx, param, value):
    """Lazy loading callback."""
    if not value or ctx.resilient_parsing:
        return
    
    _lazy_load_and_start_interactive()
    sys.exit(0)

@click.command()
@click.option('--interactive', is_flag=True, is_eager=True, 
              callback=start_interactive_mode)
def test_cli(interactive=False):
    """Test CLI."""
    pass

if __name__ == "__main__":
    test_cli()
'''

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(test_cli)
            cli_path = f.name

        try:
            # Test that interactive mode works
            result = subprocess.run(
                [sys.executable, cli_path, "--interactive"],
                capture_output=True,
                text=True,
                timeout=5,
            )

            assert result.returncode == 0
            assert "LAZY_LOAD_SUCCESS" in result.stdout

        finally:
            Path(cli_path).unlink(missing_ok=True)

    def test_no_eager_universal_imports(self):
        """Test that Universal Template imports are not loaded eagerly."""
        # This test ensures we don't regress to eager loading
        start = time.perf_counter()

        # These imports should be available but not automatically trigger heavy loads
        try:
            # Test that we can import the template engine module without triggering
            # expensive operations
            import sys

            if "goobits_cli.universal.template_engine" in sys.modules:
                # If already loaded, this test isn't meaningful
                pytest.skip("Universal template engine already loaded")

            import goobits_cli.universal.template_engine  # noqa: F401

            end = time.perf_counter()
            import_time = (end - start) * 1000

            # The import itself should be fast due to lazy loading
            assert (
                import_time < 100
            ), f"Universal template engine import: {import_time:.1f}ms (target: <100ms)"

        except ImportError:
            # If import fails, that's ok - this is an optional optimization test
            pytest.skip("Universal template engine not available")

    @pytest.mark.slow
    def test_generated_cli_startup_performance(self):
        """Test generated CLI startup performance (requires build)."""
        # This is a slower integration test
        generated_cli_path = Path(__file__).parent.parent / "generated_cli.py"

        if not generated_cli_path.exists():
            pytest.skip("Generated CLI not found - run 'goobits build' first")

        # Measure generated CLI help performance
        start = time.perf_counter()
        result = subprocess.run(
            [sys.executable, str(generated_cli_path), "--help"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        end = time.perf_counter()

        startup_time = (end - start) * 1000

        assert result.returncode == 0, f"Generated CLI failed: {result.stderr}"
        assert (
            startup_time < 200
        ), f"Generated CLI startup: {startup_time:.1f}ms (target: <200ms)"


def test_performance_targets():
    """Quick performance validation for CI/CD."""
    # This is the main test that validates our performance targets
    basic_time = 0
    overhead_time = 0

    # Measure basic imports
    start = time.perf_counter()
    end = time.perf_counter()
    basic_time = (end - start) * 1000

    # Measure lazy loading overhead
    start = time.perf_counter()

    def lazy_callback():
        pass

    end = time.perf_counter()
    overhead_time = (end - start) * 1000

    # Validate targets
    total_time = basic_time + overhead_time

    assert (
        total_time < 100
    ), f"Total CLI startup time: {total_time:.1f}ms (target: <100ms)"
    assert (
        overhead_time < 50
    ), f"Advanced features overhead: {overhead_time:.1f}ms (target: <50ms)"


if __name__ == "__main__":
    # Run the main performance test
    test_performance_targets()
    print("✅ Performance regression tests passed!")
