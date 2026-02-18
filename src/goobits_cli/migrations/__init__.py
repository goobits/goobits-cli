"""
Migration framework for Goobits CLI.

Provides infrastructure for YAML configuration migrations.
Add new migrations here when needed.
"""

from typing import Any, Dict, List

from .migration import Migration

# Registry of migrations (add new ones here in version order)
MIGRATIONS: List[Migration] = []


def get_applicable_migrations(data: Dict[str, Any]) -> List[Migration]:
    """Get migrations that should be applied to the data."""
    return [m for m in MIGRATIONS if m.should_migrate(data)]


def apply_all_migrations(
    data: Dict[str, Any], file_path: str
) -> tuple[Dict[str, Any], List[str], List[str]]:
    """
    Apply all applicable migrations.

    Returns:
        Tuple of (migrated_data, changes_made, warnings)
    """
    migrated_data = data.copy()
    all_changes: List[str] = []
    all_warnings: List[str] = []

    for migration in get_applicable_migrations(migrated_data):
        try:
            original = migrated_data.copy()
            migrated_data = migration.migrate(migrated_data)
            all_changes.extend(migration.get_changes(original, migrated_data))
            all_warnings.extend(getattr(migration, "warnings", []))
        except Exception as e:
            all_warnings.append(f"Migration {migration.version} failed: {e}")

    return migrated_data, all_changes, all_warnings


__all__ = [
    "Migration",
    "MIGRATIONS",
    "get_applicable_migrations",
    "apply_all_migrations",
]
