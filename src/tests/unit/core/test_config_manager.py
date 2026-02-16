"""Unit tests for ConfigManager / RCConfigLoader behavior."""

import json
from pathlib import Path

import pytest

from goobits_cli.core.config import ConfigManager, RCConfigLoader
from goobits_cli.core.errors import ConfigFileError, ConfigValidationError


def test_set_non_serializable_value_raises_validation_error():
    manager = ConfigManager()
    manager._config = {}

    with pytest.raises(ConfigValidationError):
        manager.set("bad.value", object())


def test_set_rolls_back_when_save_fails(monkeypatch):
    manager = ConfigManager()
    manager._config = {"a": {"b": 1}}
    monkeypatch.setattr(manager, "save", lambda: False)

    assert manager.set("a.b", 2) is False
    assert manager._config["a"]["b"] == 1


def test_get_set_delete_nested_values():
    manager = ConfigManager()
    manager._config = {}
    manager.save = lambda: True  # type: ignore[assignment]

    assert manager.set("api.endpoint.url", "https://example.com")
    assert manager.get("api.endpoint.url") == "https://example.com"
    assert manager.delete("api.endpoint.url")
    assert manager.get("api.endpoint.url") is None


def test_merge_with_env_parses_json_values(monkeypatch):
    manager = ConfigManager()
    manager._config = {}
    manager.save = lambda: True  # type: ignore[assignment]

    monkeypatch.setenv("GOOBITS_CLI_FEATURE_FLAG", "true")
    monkeypatch.setenv("GOOBITS_CLI_MAX_RETRIES", "3")
    monkeypatch.setenv("GOOBITS_CLI_ENDPOINT_URL", "https://api.example.com")

    manager.merge_with_env()

    assert manager.get("feature.flag") is True
    assert manager.get("max.retries") == 3
    assert manager.get("endpoint.url") == "https://api.example.com"


def test_find_rc_file_walks_up_directory_tree(tmp_path: Path):
    root = tmp_path / "root"
    child = root / "a" / "b"
    child.mkdir(parents=True)

    rc = root / ".goobits-clirc.json"
    rc.write_text(json.dumps({"key": "value"}), encoding="utf-8")

    loader = RCConfigLoader()
    found = loader.find_rc_file(start_dir=child)

    assert found == rc


def test_load_rc_file_json_success(tmp_path: Path):
    rc = tmp_path / ".goobits-clirc.json"
    rc.write_text(json.dumps({"x": 1, "name": "demo"}), encoding="utf-8")

    loader = RCConfigLoader()
    data = loader.load_rc_file(rc)

    assert data == {"x": 1, "name": "demo"}


def test_load_rc_file_json_invalid_raises_config_file_error(tmp_path: Path):
    rc = tmp_path / ".goobits-clirc.json"
    rc.write_text("{invalid json", encoding="utf-8")

    loader = RCConfigLoader()
    with pytest.raises(ConfigFileError):
        loader.load_rc_file(rc)


def test_load_prefers_rc_file_over_default_load(tmp_path: Path, monkeypatch):
    rc = tmp_path / ".goobits-clirc.json"
    rc.write_text(json.dumps({"version": "9.9.9", "custom": True}), encoding="utf-8")

    loader = RCConfigLoader()
    monkeypatch.setattr(loader, "find_rc_file", lambda start_dir=None: rc)

    loaded = loader.load()
    assert loaded["version"] == "9.9.9"
    assert loaded["custom"] is True
