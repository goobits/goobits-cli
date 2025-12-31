"""
v3.0.2 Migration: Standardize field names.

Migrates deprecated field names to new standardized names:
- cli_output_path → cli_path
- hooks_output_path → cli_hooks_path
- types_output_path → cli_types_path
"""

from typing import Any, Dict, List

from .migration import Migration


class V3_0_2_Migration(Migration):
    """Migration for standardizing field names."""

    # Field mapping: old_name → new_name
    FIELD_MAPPINGS = {
        "cli_output_path": "cli_path",
        "hooks_output_path": "cli_hooks_path",
        "types_output_path": "cli_types_path",
    }

    @property
    def version(self) -> str:
        return "3.0.2"

    @property
    def description(self) -> str:
        return "Standardize field names: cli_output_path → cli_path, etc."

    def should_migrate(self, data: Dict[str, Any]) -> bool:
        """Check if any deprecated fields exist in the data."""
        return self._has_deprecated_fields(data)

    def migrate(self, data: Any) -> Any:
        """Apply field name standardization."""
        if not isinstance(data, dict):
            return data

        migrated = data.copy()

        # Apply field name migrations at root level
        for old_field, new_field in self.FIELD_MAPPINGS.items():
            if old_field in migrated:
                # Check if new field already exists
                if new_field in migrated:
                    # New field takes precedence, remove old field with warning
                    self.warnings.append(
                        f"Both {old_field} and {new_field} found. Using {new_field}, removing {old_field}"
                    )
                    migrated.pop(old_field)
                else:
                    # Move value from old field to new field
                    migrated[new_field] = migrated.pop(old_field)

        return migrated

    def _has_deprecated_fields(self, data: Any) -> bool:
        """Check if data contains any deprecated fields."""
        if isinstance(data, dict):
            # Check if any deprecated fields exist at root level
            for old_field in self.FIELD_MAPPINGS.keys():
                if old_field in data:
                    return True

        return False

    def get_changes(
        self, original: Dict[str, Any], migrated: Dict[str, Any]
    ) -> List[str]:
        """Get specific changes made by this migration."""
        changes = []

        for old_field, new_field in self.FIELD_MAPPINGS.items():
            if old_field in original and new_field in migrated:
                # Check if this was actually migrated (old field removed, new field added/kept)
                if old_field not in migrated:
                    if new_field not in original:
                        changes.append(f"Renamed field: {old_field} → {new_field}")
                    else:
                        changes.append(
                            f"Removed deprecated field: {old_field} (kept existing {new_field})"
                        )

        return changes
