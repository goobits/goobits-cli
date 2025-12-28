"""
Fixtures for acceptance testing.
"""

import subprocess
from pathlib import Path
from typing import Any, Dict

import pytest
import yaml


@pytest.fixture
def temp_project_dir(tmp_path: Path):
    """Create a temporary project directory."""
    project_dir = tmp_path / "test_project"
    project_dir.mkdir(parents=True, exist_ok=True)
    yield project_dir
    # Cleanup is automatic via tmp_path


@pytest.fixture
def sample_goobits_yaml() -> Dict[str, Any]:
    """Provide a minimal sample goobits.yaml configuration."""
    return {
        "package_name": "test_cli",
        "command_name": "testcli",
        "display_name": "Test CLI",
        "description": "A test CLI application",
        "version": "1.0.0",
        "language": "python",
        "cli": {
            "name": "Test CLI",
            "tagline": "A test CLI for acceptance testing",
            "commands": {
                "hello": {
                    "desc": "Say hello",
                    "args": [
                        {"name": "name", "desc": "Name to greet", "required": False}
                    ],
                    "options": [
                        {
                            "name": "loud",
                            "short": "l",
                            "type": "bool",
                            "desc": "Shout the greeting",
                        }
                    ],
                },
                "version": {"desc": "Show version information"},
            }
        },
    }


@pytest.fixture
def write_config(temp_project_dir: Path, sample_goobits_yaml: Dict[str, Any]):
    """Write the sample config to the temp directory."""

    def _write(config: Dict[str, Any] = None, language: str = None):
        cfg = config or sample_goobits_yaml
        if language:
            cfg = {**cfg, "language": language}
        config_path = temp_project_dir / "goobits.yaml"
        with open(config_path, "w") as f:
            yaml.dump(cfg, f)
        return config_path

    return _write


def run_command(cmd: list, cwd: Path = None, timeout: int = 30) -> subprocess.CompletedProcess:
    """Run a command and return the result."""
    return subprocess.run(
        cmd,
        cwd=cwd,
        capture_output=True,
        text=True,
        timeout=timeout,
    )


def run_generated_cli(cli_path: Path, args: list = None, cwd: Path = None) -> subprocess.CompletedProcess:
    """Run a generated CLI script."""
    args = args or []

    if cli_path.suffix == ".py":
        cmd = ["python", str(cli_path)] + args
    elif cli_path.suffix in (".mjs", ".js"):
        cmd = ["node", str(cli_path)] + args
    elif cli_path.suffix == ".ts":
        # TypeScript needs to be transpiled first or run with ts-node
        cmd = ["npx", "ts-node", str(cli_path)] + args
    elif cli_path.name == "main":
        # Rust binary
        cmd = [str(cli_path)] + args
    else:
        raise ValueError(f"Unknown CLI type: {cli_path}")

    return run_command(cmd, cwd=cwd)


@pytest.fixture
def goobits_build():
    """Provide a function to run goobits build."""

    def _build(config_path: Path, output_dir: Path = None) -> subprocess.CompletedProcess:
        cmd = ["goobits", "build", str(config_path)]
        return run_command(cmd, cwd=config_path.parent)

    return _build


@pytest.fixture
def golden_dir() -> Path:
    """Return path to golden files directory."""
    return Path(__file__).parent / "golden"
