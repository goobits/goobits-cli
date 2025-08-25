"""
Performance validation and benchmarking suite for Goobits CLI Framework
"""

import tomllib
from pathlib import Path

def _get_version() -> str:
    """Read version from pyproject.toml"""
    try:
        pyproject_path = Path(__file__).parent.parent / "pyproject.toml"
        with open(pyproject_path, "rb") as f:
            data = tomllib.load(f)
        return str(data["project"]["version"])
    except Exception:
        return "2.0.0"  # Fallback

__version__ = _get_version()