"""Goobits CLI package."""

from .__version__ import __version__


def main() -> None:
    from .generated_cli import main as generated_main

    generated_main()


__all__ = ["main", "__version__"]
