"""
Path handling utilities for the Universal Template System.
"""

from pathlib import Path
from typing import Optional, Union


def normalize_path(path: Union[str, Path]) -> Path:
    """
    Normalize a path to an absolute Path object.

    Args:
        path: Path string or Path object

    Returns:
        Normalized absolute Path
    """
    return Path(path).resolve()


def ensure_directory(path: Union[str, Path]) -> Path:
    """
    Ensure a directory exists, creating it if necessary.

    Args:
        path: Directory path

    Returns:
        Path object for the directory
    """
    dir_path = Path(path)
    dir_path.mkdir(parents=True, exist_ok=True)
    return dir_path


def get_relative_path(path: Union[str, Path], base: Union[str, Path]) -> Path:
    """
    Get a path relative to a base directory.

    Args:
        path: The path to make relative
        base: The base directory

    Returns:
        Relative path
    """
    return Path(path).relative_to(Path(base))
