"""Unit tests for lightweight command wrappers (validate/migrate)."""

from pathlib import Path
from types import SimpleNamespace

import pytest
import typer

from goobits_cli.commands.migrate import migrate_command
from goobits_cli.commands.validate import validate_command


def test_validate_command_missing_config_exits_with_code_1(monkeypatch, tmp_path: Path):
    calls: list[tuple[str, bool]] = []

    def fake_echo(message, err=False):
        calls.append((str(message), err))

    monkeypatch.setattr(typer, "echo", fake_echo)

    missing = tmp_path / "missing.yaml"
    with pytest.raises(typer.Exit) as exc:
        validate_command(config_path=missing, verbose=False)

    assert exc.value.exit_code == 1
    assert any("not found" in msg.lower() and err for msg, err in calls)


def test_validate_command_success_verbose_prints_summary(monkeypatch, tmp_path: Path):
    cfg_path = tmp_path / "goobits.yaml"
    cfg_path.write_text("package_name: demo\n", encoding="utf-8")

    calls: list[tuple[str, bool]] = []

    def fake_echo(message, err=False):
        calls.append((str(message), err))

    config = SimpleNamespace(
        package_name="demo",
        command_name="democli",
        language="python",
        cli=SimpleNamespace(
            version="1.2.3",
            commands={"a": {}, "b": {}, "c": {}, "d": {}, "e": {}, "f": {}},
        ),
    )

    monkeypatch.setattr("goobits_cli.commands.validate._lazy_imports", lambda: None)
    monkeypatch.setattr(
        "goobits_cli.commands.validate.load_goobits_config", lambda _p: config
    )
    monkeypatch.setattr(typer, "echo", fake_echo)

    validate_command(config_path=cfg_path, verbose=True)

    rendered = "\n".join(m for m, _ in calls)
    assert "Configuration is valid" in rendered
    assert "Configuration Summary" in rendered
    assert "Package: demo" in rendered
    assert "CLI Version: 1.2.3" in rendered
    assert "... and 1 more" in rendered


def test_validate_command_validation_exception_exits_1(monkeypatch, tmp_path: Path):
    cfg_path = tmp_path / "goobits.yaml"
    cfg_path.write_text("package_name: demo\n", encoding="utf-8")

    monkeypatch.setattr("goobits_cli.commands.validate._lazy_imports", lambda: None)

    def _fail(_path):
        raise RuntimeError("invalid config")

    monkeypatch.setattr("goobits_cli.commands.validate.load_goobits_config", _fail)

    with pytest.raises(typer.Exit) as exc:
        validate_command(config_path=cfg_path, verbose=False)

    assert exc.value.exit_code == 1


def test_migrate_command_no_migrations_exits_0(monkeypatch):
    import goobits_cli.migrations as migrations_module

    calls: list[tuple[str, bool]] = []

    def fake_echo(message, err=False):
        calls.append((str(message), err))

    monkeypatch.setattr(migrations_module, "MIGRATIONS", [])
    monkeypatch.setattr(typer, "echo", fake_echo)

    with pytest.raises(typer.Exit) as exc:
        migrate_command(path="goobits.yaml")

    assert exc.value.exit_code == 0
    assert any("No migrations registered" in msg for msg, _ in calls)


def test_migrate_command_invokes_migration_callback(monkeypatch):
    import goobits_cli.migrations as migrations_module

    captured: dict[str, object] = {}

    def fake_callback(path, backup, dry_run, pattern):
        captured["path"] = path
        captured["backup"] = backup
        captured["dry_run"] = dry_run
        captured["pattern"] = pattern

    monkeypatch.setattr(migrations_module, "MIGRATIONS", [object()])
    monkeypatch.setattr(
        "goobits_cli.commands.migration_tool.migrate_yaml",
        SimpleNamespace(callback=fake_callback),
    )

    migrate_command(path="goobits.yaml", backup=False, dry_run=True, pattern="*.yml")

    assert captured["path"] == Path("goobits.yaml")
    assert captured["backup"] is False
    assert captured["dry_run"] is True
    assert captured["pattern"] == "*.yml"


def test_migrate_command_callback_failure_exits_1(monkeypatch):
    import goobits_cli.migrations as migrations_module

    calls: list[tuple[str, bool]] = []

    def fake_echo(message, err=False):
        calls.append((str(message), err))

    def fake_callback(*_args, **_kwargs):
        raise RuntimeError("boom")

    monkeypatch.setattr(migrations_module, "MIGRATIONS", [object()])
    monkeypatch.setattr(typer, "echo", fake_echo)
    monkeypatch.setattr(
        "goobits_cli.commands.migration_tool.migrate_yaml",
        SimpleNamespace(callback=fake_callback),
    )

    with pytest.raises(typer.Exit) as exc:
        migrate_command(path="goobits.yaml")

    assert exc.value.exit_code == 1
    assert any("Migration failed:" in msg and err for msg, err in calls)
