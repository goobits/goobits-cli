"""
Migration registry and runner for Goobits CLI Framework.

This module provides the migration registry and orchestration for applying
version-specific YAML configuration migrations.
"""

from typing import Dict, Any, List
from .migration import Migration
from .v3_0_0 import V3_0_0_Migration
from .v3_0_2 import V3_0_2_Migration

# Registry of all available migrations in version order
MIGRATIONS = [
    V3_0_0_Migration(),
    V3_0_2_Migration(),
]


def get_applicable_migrations(data: Dict[str, Any]) -> List[Migration]:
    """
    Get migrations that should be applied to the data.
    
    Args:
        data: YAML configuration data
        
    Returns:
        List of migrations that need to be applied
    """
    return [migration for migration in MIGRATIONS if migration.should_migrate(data)]


def apply_all_migrations(data: Dict[str, Any], file_path) -> tuple[Dict[str, Any], List[str], List[str]]:
    """
    Apply all applicable migrations to the data.
    
    Args:
        data: YAML configuration data
        file_path: Path to the file being migrated (for error reporting)
        
    Returns:
        Tuple of (migrated_data, changes_made, warnings)
    """
    migrated_data = data.copy()
    all_changes = []
    all_warnings = []
    
    applicable_migrations = get_applicable_migrations(migrated_data)
    
    for migration in applicable_migrations:
        try:
            if migration.should_migrate(migrated_data):
                # Store original for change tracking
                original_data = migrated_data.copy()
                
                # Apply migration
                migrated_data = migration.migrate(migrated_data)
                
                # Track changes and warnings
                changes = migration.get_changes(original_data, migrated_data)
                all_changes.extend(changes)
                
                warnings = getattr(migration, 'warnings', [])
                all_warnings.extend(warnings)
        
        except Exception as e:
            all_warnings.append(f"Migration {migration.version} failed: {e}")
            # Continue with other migrations
    
    return migrated_data, all_changes, all_warnings