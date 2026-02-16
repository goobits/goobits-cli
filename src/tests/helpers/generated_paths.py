"""Helpers for locating generated CLI entry files in tests."""

from pathlib import Path

MAIN_CLI_CANDIDATES = {
    "python": ("cli.py", "main.py"),
    "nodejs": ("cli.js", "main.js", "cli.mjs", "main.mjs"),
    "typescript": ("cli.ts", "main.ts"),
    "rust": ("src/cli.rs", "src/main.rs", "cli.rs", "main.rs"),
}


def find_main_cli_path(files: dict[str, str], language: str) -> str | None:
    """Return the main generated CLI path for a language."""
    candidates = MAIN_CLI_CANDIDATES.get(language, ())

    for candidate in candidates:
        if candidate in files:
            return candidate

    for path in files:
        name = Path(path).name
        if "hooks" in name:
            continue
        if language == "python" and name.endswith(".py") and ("cli" in name or "main" in name):
            return path
        if language == "nodejs" and name.endswith((".js", ".mjs")) and ("cli" in name or "main" in name):
            return path
        if language == "typescript" and name.endswith(".ts") and ("cli" in name or "main" in name):
            return path
        if language == "rust" and name.endswith(".rs") and ("cli" in name or "main" in name):
            return path

    return None

