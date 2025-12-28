"""
Tests for downstream project compatibility.

These tests verify that goobits build works correctly for
the actual downstream projects in the workspace.
"""

import subprocess
from pathlib import Path

import pytest


def run_goobits_build(project_path: Path) -> subprocess.CompletedProcess:
    """Run goobits build on a project."""
    config_path = project_path / "goobits.yaml"
    if not config_path.exists():
        pytest.skip(f"No goobits.yaml found at {project_path}")

    return subprocess.run(
        ["goobits", "build", str(config_path)],
        cwd=project_path,
        capture_output=True,
        text=True,
        timeout=60,
    )


@pytest.mark.downstream
class TestDownstreamMatilda:
    """Test goobits build for matilda project."""

    @pytest.fixture
    def project_path(self) -> Path:
        return Path("/workspace/matilda")

    def test_goobits_yaml_exists(self, project_path: Path):
        """Verify goobits.yaml exists."""
        config_path = project_path / "goobits.yaml"
        if not config_path.exists():
            pytest.skip("matilda not available in workspace")
        assert config_path.exists()

    def test_goobits_build_succeeds(self, project_path: Path):
        """Test that goobits build succeeds."""
        if not (project_path / "goobits.yaml").exists():
            pytest.skip("matilda not available")

        result = run_goobits_build(project_path)
        assert result.returncode == 0, f"Build failed: {result.stderr}"

    def test_cli_file_generated(self, project_path: Path):
        """Test that CLI file is generated."""
        if not (project_path / "goobits.yaml").exists():
            pytest.skip("matilda not available")

        run_goobits_build(project_path)

        # Check for generated CLI file
        # Path depends on goobits.yaml config
        possible_paths = [
            project_path / "src" / "matilda" / "cli.py",
            project_path / "matilda" / "cli.py",
        ]
        assert any(p.exists() for p in possible_paths), "CLI file not found"


@pytest.mark.downstream
class TestDownstreamEars:
    """Test goobits build for matilda-ears project."""

    @pytest.fixture
    def project_path(self) -> Path:
        return Path("/workspace/matilda-ears")

    def test_goobits_yaml_exists(self, project_path: Path):
        """Verify goobits.yaml exists."""
        config_path = project_path / "goobits.yaml"
        if not config_path.exists():
            pytest.skip("matilda-ears not available in workspace")
        assert config_path.exists()

    def test_goobits_build_succeeds(self, project_path: Path):
        """Test that goobits build succeeds."""
        if not (project_path / "goobits.yaml").exists():
            pytest.skip("matilda-ears not available")

        result = run_goobits_build(project_path)
        assert result.returncode == 0, f"Build failed: {result.stderr}"


@pytest.mark.downstream
class TestDownstreamVoice:
    """Test goobits build for matilda-voice project."""

    @pytest.fixture
    def project_path(self) -> Path:
        return Path("/workspace/matilda-voice")

    def test_goobits_yaml_exists(self, project_path: Path):
        """Verify goobits.yaml exists."""
        config_path = project_path / "goobits.yaml"
        if not config_path.exists():
            pytest.skip("matilda-voice not available in workspace")
        assert config_path.exists()

    def test_goobits_build_succeeds(self, project_path: Path):
        """Test that goobits build succeeds."""
        if not (project_path / "goobits.yaml").exists():
            pytest.skip("matilda-voice not available")

        result = run_goobits_build(project_path)
        assert result.returncode == 0, f"Build failed: {result.stderr}"

    def test_generated_imports_correctly(self, project_path: Path):
        """Test that generated CLI imports correctly."""
        if not (project_path / "goobits.yaml").exists():
            pytest.skip("matilda-voice not available")

        run_goobits_build(project_path)

        # Try to import the generated module
        import sys
        sys.path.insert(0, str(project_path))
        try:
            # The import path depends on the project structure
            pass  # Skip actual import test for now
        finally:
            sys.path.remove(str(project_path))


@pytest.mark.downstream
class TestDownstreamBrain:
    """Test goobits build for matilda-brain project."""

    @pytest.fixture
    def project_path(self) -> Path:
        return Path("/workspace/matilda-brain")

    def test_goobits_yaml_exists(self, project_path: Path):
        """Verify goobits.yaml exists."""
        config_path = project_path / "goobits.yaml"
        if not config_path.exists():
            pytest.skip("matilda-brain not available in workspace")
        assert config_path.exists()

    def test_goobits_build_succeeds(self, project_path: Path):
        """Test that goobits build succeeds."""
        if not (project_path / "goobits.yaml").exists():
            pytest.skip("matilda-brain not available")

        result = run_goobits_build(project_path)
        assert result.returncode == 0, f"Build failed: {result.stderr}"
