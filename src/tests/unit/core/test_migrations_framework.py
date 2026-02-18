"""Unit tests for migration framework utilities."""

import goobits_cli.migrations as migrations_module
from goobits_cli.migrations import apply_all_migrations, get_applicable_migrations
from goobits_cli.migrations.migration import Migration


class _NoopMigration(Migration):
    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def description(self) -> str:
        return "Noop migration"

    def should_migrate(self, data):
        return False

    def migrate(self, data):
        return data


class _AddKeyMigration(Migration):
    @property
    def version(self) -> str:
        return "2.0.0"

    @property
    def description(self) -> str:
        return "Add key migration"

    def should_migrate(self, data):
        return "added" not in data

    def migrate(self, data):
        updated = data.copy()
        updated["added"] = True
        self.warnings = ["added key"]
        return updated


class _FailingMigration(Migration):
    @property
    def version(self) -> str:
        return "9.9.9"

    @property
    def description(self) -> str:
        return "Failing migration"

    def should_migrate(self, data):
        return True

    def migrate(self, data):
        raise RuntimeError("boom")


def test_get_applicable_migrations_filters_registry(monkeypatch):
    migrations = [_NoopMigration(), _AddKeyMigration()]
    monkeypatch.setattr(migrations_module, "MIGRATIONS", migrations)

    applicable = get_applicable_migrations({"x": 1})
    assert len(applicable) == 1
    assert isinstance(applicable[0], _AddKeyMigration)


def test_apply_all_migrations_applies_changes_and_warnings(monkeypatch):
    migrations = [_AddKeyMigration()]
    monkeypatch.setattr(migrations_module, "MIGRATIONS", migrations)

    migrated, changes, warnings = apply_all_migrations({"x": 1}, "file.yaml")
    assert migrated["added"] is True
    assert any("Applied Add key migration" in c for c in changes)
    assert "added key" in warnings


def test_apply_all_migrations_handles_failures_as_warnings(monkeypatch):
    migrations = [_FailingMigration()]
    monkeypatch.setattr(migrations_module, "MIGRATIONS", migrations)

    migrated, changes, warnings = apply_all_migrations({"x": 1}, "file.yaml")
    assert migrated == {"x": 1}
    assert changes == []
    assert any("Migration 9.9.9 failed: boom" in w for w in warnings)


def test_base_migration_helpers_cover_recursive_walk_and_changes():
    migration = _NoopMigration()

    original = {"a": 1}
    same = {"a": 1}
    changed = {"a": 2}
    assert migration.get_changes(original, same) == []
    assert migration.get_changes(original, changed) == ["Applied Noop migration"]

    nested = {"a": [{"b": 1}, 2, "x"]}
    assert migration._migrate_value(nested, "root") == nested
