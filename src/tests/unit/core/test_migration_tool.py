"""Unit tests for YAML migration tool behavior."""

from pathlib import Path

import yaml

from goobits_cli.commands.migration_tool import YAMLMigrationTool


def test_migrate_file_missing_path_records_error(tmp_path: Path):
    tool = YAMLMigrationTool()
    missing = tmp_path / "missing.yaml"

    assert not tool.migrate_file(missing)
    assert any("File not found" in msg for msg in tool.errors)


def test_migrate_file_dry_run_does_not_modify_file(tmp_path: Path, monkeypatch):
    source = tmp_path / "goobits.yaml"
    source.write_text("cli:\n  name: test\n", encoding="utf-8")

    tool = YAMLMigrationTool()

    def fake_migrate(_data, _path):
        return {"cli": {"name": "test"}, "new_key": True}, ["added key"], []

    # Patch through the actual module import path used at runtime.
    import goobits_cli.migrations as migrations_module

    monkeypatch.setattr(migrations_module, "apply_all_migrations", fake_migrate)

    original = source.read_text(encoding="utf-8")
    assert tool.migrate_file(source, backup=True, dry_run=True)

    # File should remain unchanged in dry-run mode and no backup should exist.
    assert source.read_text(encoding="utf-8") == original
    assert not source.with_suffix(".yaml.bak").exists()


def test_migrate_file_writes_backup_and_migrated_content(tmp_path: Path, monkeypatch):
    source = tmp_path / "goobits.yaml"
    source.write_text("cli:\n  name: test\n", encoding="utf-8")

    tool = YAMLMigrationTool()

    def fake_migrate(_data, _path):
        return {"cli": {"name": "test"}, "new_key": True}, ["added key"], []

    import goobits_cli.migrations as migrations_module

    monkeypatch.setattr(migrations_module, "apply_all_migrations", fake_migrate)

    assert tool.migrate_file(source, backup=True, dry_run=False)

    backup = source.with_suffix(".yaml.bak")
    assert backup.exists()

    migrated = yaml.safe_load(source.read_text(encoding="utf-8"))
    assert migrated["new_key"] is True


def test_find_changes_detects_added_removed_and_type_changes():
    tool = YAMLMigrationTool()
    original = {"a": 1, "b": {"x": 1}, "c": [1, 2]}
    migrated = {"a": "1", "b": {"y": 2}, "d": 5, "c": {"items": [1, 2]}}

    changes = tool._find_changes(original, migrated)
    descriptions = [c["description"] for c in changes]

    assert any("Type Change" == c["type"] for c in changes)
    assert any("Key removed" in d for d in descriptions)
    assert any("Key added" in d for d in descriptions)
    assert any("Subcommands array converted to object format" in d for d in descriptions)
