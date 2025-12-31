"""
v3.0.0 Migration: Convert subcommands array to object format.

Converts legacy array-based subcommands to standardized object format:
BEFORE: subcommands: [{name: "start", ...}, {name: "stop", ...}]
AFTER:  subcommands: {start: {...}, stop: {...}}
"""

from typing import Any, Dict, List

from .migration import Migration


class V3_0_0_Migration(Migration):
    """Migration for converting subcommands array to object format."""

    @property
    def version(self) -> str:
        return "3.0.0"

    @property
    def description(self) -> str:
        return "Convert subcommands array to object format"

    def should_migrate(self, data: Dict[str, Any]) -> bool:
        """Check if data contains array-format subcommands that need migration."""
        return self._has_subcommands_arrays(data)

    def migrate(self, data: Any) -> Any:
        """Apply subcommands array to object conversion."""
        if not isinstance(data, dict):
            return data

        # Deep copy to avoid modifying original
        migrated = {}
        for key, value in data.items():
            migrated[key] = self._migrate_value(value, key)

        return migrated

    def _migrate_value(self, value: Any, key: str) -> Any:
        """Recursively migrate values, handling subcommands conversion."""
        if isinstance(value, dict):
            # Check for subcommands already in object format
            if key == "subcommands" and isinstance(value, dict):
                # Already object format, recurse into subcommands
                migrated_subcommands = {}
                for sub_key, sub_value in value.items():
                    migrated_subcommands[sub_key] = self._migrate_value(
                        sub_value, sub_key
                    )
                return migrated_subcommands
            else:
                # Regular dict, recurse
                migrated = {}
                for sub_key, sub_value in value.items():
                    migrated[sub_key] = self._migrate_value(sub_value, sub_key)
                return migrated

        elif isinstance(value, list):
            # Check for subcommands array format
            if key == "subcommands" and self._is_subcommands_array(value):
                return self._convert_subcommands_array_to_object(value)
            else:
                # Regular list, recurse
                return [
                    self._migrate_value(item, f"{key}[{i}]")
                    for i, item in enumerate(value)
                ]

        else:
            # Primitive value, return as-is
            return value

    def _has_subcommands_arrays(self, data: Any) -> bool:
        """Recursively check if data contains any subcommands arrays."""
        if isinstance(data, dict):
            for key, value in data.items():
                if key == "subcommands" and self._is_subcommands_array(value):
                    return True
                if self._has_subcommands_arrays(value):
                    return True
        elif isinstance(data, list):
            for item in data:
                if self._has_subcommands_arrays(item):
                    return True

        return False

    def _is_subcommands_array(self, value: Any) -> bool:
        """Check if value is a subcommands array format."""
        if not isinstance(value, list) or not value:
            return False

        # Check if list items have 'name' field (indicating subcommand objects)
        return all(isinstance(item, dict) and "name" in item for item in value)

    def _convert_subcommands_array_to_object(
        self, subcommands_array: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Convert subcommands array to object format."""
        subcommands_object = {}

        for subcmd in subcommands_array:
            if not isinstance(subcmd, dict) or "name" not in subcmd:
                self.warnings.append(f"Invalid subcommand: {subcmd}")
                continue

            name = subcmd.pop("name")  # Remove 'name' field

            # Recursively migrate the subcommand structure
            migrated_subcmd = self.migrate(subcmd)
            subcommands_object[name] = migrated_subcmd

        return subcommands_object

    def get_changes(
        self, original: Dict[str, Any], migrated: Dict[str, Any]
    ) -> List[str]:
        """Get specific changes made by this migration."""
        changes = []

        def find_subcommand_changes(orig_data, migr_data, path=""):
            if isinstance(orig_data, dict) and isinstance(migr_data, dict):
                for key in orig_data:
                    if key == "subcommands":
                        if isinstance(orig_data[key], list) and isinstance(
                            migr_data[key], dict
                        ):
                            location = f"{path}.{key}" if path else key
                            changes.append(
                                f"Converted subcommands array → object at {location}"
                            )
                    elif key in migr_data:
                        new_path = f"{path}.{key}" if path else key
                        find_subcommand_changes(
                            orig_data[key], migr_data[key], new_path
                        )
            elif isinstance(orig_data, list):
                for i, item in enumerate(orig_data):
                    if i < len(migr_data):
                        find_subcommand_changes(item, migr_data[i], f"{path}[{i}]")

        find_subcommand_changes(original, migrated)
        return changes
