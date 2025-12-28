"""Shared path utility functions for CLI generators.

This module provides common path detection and manipulation functions
used across multiple language generators.
"""

from pathlib import Path


def is_e2e_test_path(config_filename: str) -> bool:
    """Check if config_filename looks like a directory path for E2E test compatibility.

    E2E tests call generator.generate(config, str(tmp_path)) expecting files to be written.
    This function detects such paths.

    Args:
        config_filename: The filename or path to check

    Returns:
        True if this appears to be an E2E test path, False otherwise
    """
    config_path = Path(config_filename)
    return (
        config_path.is_dir()
        or (not config_path.suffix and config_path.exists())
        or (
            not config_path.suffix
            and ("pytest" in config_filename or config_filename.endswith("_test"))
        )
    )
