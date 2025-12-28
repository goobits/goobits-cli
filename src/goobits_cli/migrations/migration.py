"""
Base migration class for Goobits CLI Framework migrations.

Provides the abstract base class that all version-specific migrations inherit from.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List


class Migration(ABC):
    """Base class for all YAML configuration migrations."""

    def __init__(self):
        self.warnings = []

    @property
    @abstractmethod
    def version(self) -> str:
        """Target version for this migration (e.g., '3.0.0')."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Human-readable description of what this migration does."""
        pass

    @abstractmethod
    def should_migrate(self, data: Dict[str, Any]) -> bool:
        """
        Check if this migration should be applied to the given data.

        Args:
            data: YAML configuration data

        Returns:
            True if migration should be applied, False otherwise
        """
        pass

    @abstractmethod
    def migrate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply the migration to the data.

        Args:
            data: YAML configuration data

        Returns:
            Migrated data
        """
        pass

    def get_changes(
        self, original: Dict[str, Any], migrated: Dict[str, Any]
    ) -> List[str]:
        """
        Get list of human-readable changes made by this migration.

        Args:
            original: Data before migration
            migrated: Data after migration

        Returns:
            List of change descriptions
        """
        # Default implementation - subclasses can override for more specific tracking
        if original != migrated:
            return [f"Applied {self.description}"]
        return []

    def _migrate_value(self, value: Any, key: str) -> Any:
        """
        Recursively migrate values in data structures.

        Args:
            value: Value to migrate
            key: Key name for context

        Returns:
            Migrated value
        """
        if isinstance(value, dict):
            # Recursively migrate dictionary values
            migrated = {}
            for sub_key, sub_value in value.items():
                migrated[sub_key] = self._migrate_value(sub_value, sub_key)
            return migrated

        elif isinstance(value, list):
            # Recursively migrate list items
            return [
                self._migrate_value(item, f"{key}[{i}]") for i, item in enumerate(value)
            ]

        else:
            # Primitive value, return as-is
            return value
