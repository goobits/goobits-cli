"""
YAML Migration Tool for Goobits CLI Framework

Converts legacy YAML configurations to current standardized format:
- Array subcommands → Object subcommands (v3.0.0)
- Field name standardization (v3.0.2)
- Validates new structure compatibility
- Creates backup files for safety
"""

import yaml
import shutil
from pathlib import Path
from typing import Dict, List, Any, Tuple
import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()


class YAMLMigrationTool:
    """Tool for migrating Goobits YAML configurations to 3.0.0 format."""

    def __init__(self):
        self.changes_made = []
        self.warnings = []
        self.errors = []

    def migrate_file(
        self, file_path: Path, backup: bool = True, dry_run: bool = False
    ) -> bool:
        """
        Migrate a single YAML file to 3.0.0 format.

        Args:
            file_path: Path to YAML file
            backup: Create .bak backup file
            dry_run: Show changes without applying

        Returns:
            True if migration successful or no changes needed
        """
        if not file_path.exists():
            self.errors.append(f"File not found: {file_path}")
            return False

        try:
            # Load current YAML
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                data = yaml.safe_load(content)

            if not data:
                self.warnings.append(f"Empty or invalid YAML: {file_path}")
                return True

            # Check if migration needed
            original_data = yaml.safe_load(content)  # Deep copy for comparison
            migrated_data = self._migrate_structure(data, file_path)

            if migrated_data == original_data:
                console.print(f"✅ No migration needed: {file_path}")
                return True

            # Show changes
            self._show_migration_summary(file_path, original_data, migrated_data)

            if dry_run:
                console.print(
                    f"🔍 [cyan]Dry run[/cyan] - No changes applied to {file_path}"
                )
                return True

            # Create backup
            if backup:
                backup_path = file_path.with_suffix(file_path.suffix + ".bak")
                shutil.copy2(file_path, backup_path)
                console.print(f"💾 Backup created: {backup_path}")

            # Write migrated YAML
            with open(file_path, "w", encoding="utf-8") as f:
                yaml.dump(
                    migrated_data,
                    f,
                    default_flow_style=False,
                    indent=2,
                    sort_keys=False,
                )

            console.print(f"✅ [green]Migrated successfully[/green]: {file_path}")
            return True

        except Exception as e:
            self.errors.append(f"Migration failed for {file_path}: {e}")
            return False

    def _migrate_structure(
        self, data: Dict[str, Any], file_path: Path
    ) -> Dict[str, Any]:
        """Apply all migration transformations to YAML structure."""
        from .migrations import apply_all_migrations

        if not isinstance(data, dict):
            return data

        # Apply all applicable migrations using the registry system
        migrated_data, changes, warnings = apply_all_migrations(data, file_path)

        # Add changes and warnings to our tracking
        self.changes_made.extend(changes)
        self.warnings.extend(warnings)

        return migrated_data

    def _show_migration_summary(
        self, file_path: Path, original: Dict[str, Any], migrated: Dict[str, Any]
    ):
        """Show summary of changes that will be made."""
        console.print(f"\n📋 [bold]Migration Summary for {file_path}[/bold]")

        # Find specific changes
        changes = self._find_changes(original, migrated)

        if changes:
            table = Table(title="Changes")
            table.add_column("Type", style="cyan")
            table.add_column("Location", style="yellow")
            table.add_column("Change", style="green")

            for change in changes:
                table.add_row(change["type"], change["location"], change["description"])

            console.print(table)
        else:
            console.print("ℹ️  No changes detected")

    def _find_changes(
        self, original: Any, migrated: Any, path: str = ""
    ) -> List[Dict[str, str]]:
        """Recursively find differences between original and migrated structures."""
        changes = []

        if type(original) != type(migrated):
            changes.append(
                {
                    "type": "Type Change",
                    "location": path or "root",
                    "description": f"{type(original).__name__} → {type(migrated).__name__}",
                }
            )
            return changes

        if isinstance(original, dict) and isinstance(migrated, dict):
            # Check for added/removed keys
            orig_keys = set(original.keys())
            migr_keys = set(migrated.keys())

            for key in orig_keys - migr_keys:
                changes.append(
                    {
                        "type": "Removed",
                        "location": f"{path}.{key}" if path else key,
                        "description": f"Key removed: {key}",
                    }
                )

            for key in migr_keys - orig_keys:
                changes.append(
                    {
                        "type": "Added",
                        "location": f"{path}.{key}" if path else key,
                        "description": f"Key added: {key}",
                    }
                )

            # Check for modified keys
            for key in orig_keys & migr_keys:
                key_path = f"{path}.{key}" if path else key
                changes.extend(
                    self._find_changes(original[key], migrated[key], key_path)
                )

        elif isinstance(original, list) and isinstance(migrated, dict):
            # This is the subcommands array → object conversion
            changes.append(
                {
                    "type": "Structure",
                    "location": path or "root",
                    "description": "Subcommands array converted to object format",
                }
            )

        return changes

    def migrate_directory(
        self,
        directory: Path,
        pattern: str = "*.yaml",
        backup: bool = True,
        dry_run: bool = False,
    ) -> Tuple[int, int]:
        """
        Migrate all YAML files in directory.

        Returns:
            Tuple of (successful_migrations, failed_migrations)
        """
        yaml_files = list(directory.glob(pattern))
        yaml_files.extend(directory.glob("*.yml"))  # Also check .yml files

        if not yaml_files:
            console.print(f"⚠️  No YAML files found in {directory}")
            return 0, 0

        console.print(f"🔍 Found {len(yaml_files)} YAML files in {directory}")

        successful = 0
        failed = 0

        for yaml_file in yaml_files:
            if self.migrate_file(yaml_file, backup, dry_run):
                successful += 1
            else:
                failed += 1

        return successful, failed

    def show_summary(self):
        """Show final migration summary."""
        console.print("\n" + "=" * 60)
        console.print("📊 [bold cyan]MIGRATION SUMMARY[/bold cyan]")

        if self.changes_made:
            panel_content = "\n".join(f"✅ {change}" for change in self.changes_made)
            console.print(
                Panel(panel_content, title="✅ Changes Made", border_style="green")
            )

        if self.warnings:
            panel_content = "\n".join(f"⚠️  {warning}" for warning in self.warnings)
            console.print(
                Panel(panel_content, title="⚠️  Warnings", border_style="yellow")
            )

        if self.errors:
            panel_content = "\n".join(f"❌ {error}" for error in self.errors)
            console.print(Panel(panel_content, title="❌ Errors", border_style="red"))

        if not (self.changes_made or self.warnings or self.errors):
            console.print("✨ [green]All files are already up to date![/green]")


@click.command()
@click.argument("path", type=click.Path(exists=True, path_type=Path))
@click.option("--backup/--no-backup", default=True, help="Create backup files (.bak)")
@click.option("--dry-run", is_flag=True, help="Show changes without applying them")
@click.option(
    "--pattern", default="*.yaml", help="File pattern for directory migration"
)
def migrate_yaml(path: Path, backup: bool, dry_run: bool, pattern: str):
    """
    Migrate Goobits YAML configurations to latest format.

    Applies all applicable migrations:

    \b
    v3.0.0: subcommands: [{name: "start", ...}] → {start: {...}}
    v3.0.2: cli_output_path → cli_path, hooks_output_path → cli_hooks_path

    PATH can be a single YAML file or directory containing YAML files.
    """
    console.print("🚀 [bold]Goobits CLI Framework Migration Tool[/bold]")
    console.print("Converting YAML configurations to current standardized format...")

    migrator = YAMLMigrationTool()

    if path.is_file():
        # Single file migration
        success = migrator.migrate_file(path, backup, dry_run)
        if not success:
            console.print("❌ [red]Migration failed[/red]")
            raise click.Abort()

    elif path.is_dir():
        # Directory migration
        successful, failed = migrator.migrate_directory(path, pattern, backup, dry_run)

        if failed > 0:
            console.print(f"⚠️  [yellow]{failed} files failed to migrate[/yellow]")

        if successful == 0 and failed == 0:
            console.print("ℹ️  No YAML files found to migrate")

    else:
        console.print(f"❌ [red]Invalid path: {path}[/red]")
        raise click.Abort()

    migrator.show_summary()

    if dry_run:
        console.print("\n💡 [cyan]Run without --dry-run to apply changes[/cyan]")


if __name__ == "__main__":
    migrate_yaml()
