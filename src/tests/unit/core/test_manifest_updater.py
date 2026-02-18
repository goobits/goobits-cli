"""Unit tests for manifest update logic."""

import json
from pathlib import Path

import pytest

from goobits_cli.core.manifest import (
    ManifestUpdater,
    Result,
    update_manifests_for_build,
)


def test_result_ok_err_helpers():
    ok = Result.Ok(["warn"])
    err = Result.Err("fail")
    assert not ok.is_err()
    assert ok.value == ["warn"]
    assert err.is_err()
    assert err.err() == "fail"


def test_merge_nodejs_config_default_path():
    updater = ManifestUpdater()
    package_data = {}
    warnings = updater._merge_nodejs_config(package_data, "mycli", "cli.js", None)

    assert warnings == []
    assert package_data["type"] == "module"
    assert package_data["main"] == "cli.js"
    assert package_data["bin"]["mycli"] == "cli.js"
    assert package_data["dependencies"]["commander"].startswith("^")
    assert package_data["engines"]["node"] == ">=14.0.0"


def test_merge_nodejs_config_type_change_requires_confirmation(monkeypatch):
    updater = ManifestUpdater()
    package_data = {"type": "commonjs"}

    monkeypatch.setattr("typer.confirm", lambda *_args, **_kwargs: False)
    with pytest.raises(ValueError):
        updater._merge_nodejs_config(package_data, "mycli", "cli.js", None)

    monkeypatch.setattr("typer.confirm", lambda *_args, **_kwargs: True)
    warnings = updater._merge_nodejs_config(package_data, "mycli", "cli.js", None)
    assert package_data["type"] == "module"
    assert any("Changed package.json type" in w for w in warnings)


def test_merge_nodejs_config_converts_string_bin_and_keeps_existing_deps():
    updater = ManifestUpdater()
    package_data = {
        "name": "pkg",
        "type": "module",
        "bin": "old.js",
        "dependencies": {"commander": "0.0.1"},
    }

    updater._merge_nodejs_config(package_data, "mycli", "cli.js", {"leftpad": "^1.0.0"})
    assert isinstance(package_data["bin"], dict)
    assert package_data["bin"]["pkg"] == "old.js"
    assert package_data["bin"]["mycli"] == "cli.js"
    # Existing version should not be overwritten
    assert package_data["dependencies"]["commander"] == "0.0.1"
    assert package_data["dependencies"]["leftpad"] == "^1.0.0"


def test_merge_rust_config_adds_bin_and_dependencies():
    updater = ManifestUpdater()
    cargo_data = {}
    updater._merge_rust_config(
        cargo_data, "mycli", "src/cli.rs", {"serde_json": "1.0.1"}
    )

    assert cargo_data["package"]["edition"] == "2021"
    assert cargo_data["bin"][0]["name"] == "mycli"
    assert cargo_data["bin"][0]["path"] == "src/cli.rs"
    # Existing defaults exist
    assert "clap" in cargo_data["dependencies"]
    # Additional dep merged
    assert cargo_data["dependencies"]["serde_json"] == "1.0.1"


def test_update_package_json_writes_file_and_returns_warnings(tmp_path: Path):
    updater = ManifestUpdater()
    pkg = tmp_path / "package.json"
    pkg.write_text(json.dumps({"type": "module"}), encoding="utf-8")

    result = updater.update_package_json(pkg, "mycli", "cli.js", {"x": "^1.0.0"})
    assert not result.is_err()
    data = json.loads(pkg.read_text(encoding="utf-8"))
    assert data["bin"]["mycli"] == "cli.js"
    assert data["dependencies"]["x"] == "^1.0.0"


def test_update_manifests_for_build_nodejs_and_rust_paths(tmp_path: Path):
    # Node.js path
    node_cfg = {
        "language": "nodejs",
        "cli": {"name": "nodecli"},
        "installation": {"extras": {"npm": {"foo": "^1.0.0"}}},
    }
    node_cli = tmp_path / "cli.js"
    node_cli.write_text("// cli", encoding="utf-8")

    node_res = update_manifests_for_build(node_cfg, tmp_path, node_cli)
    assert not node_res.is_err()
    assert (tmp_path / "package.json").exists()

    # Rust path
    rust_cfg = {
        "language": "rust",
        "cli": {"name": "rustcli"},
        "installation": {"extras": {"cargo": {"rand": "0.8"}}},
    }
    rust_cli = tmp_path / "src" / "main.rs"
    rust_cli.parent.mkdir(parents=True, exist_ok=True)
    rust_cli.write_text("fn main(){}", encoding="utf-8")

    rust_res = update_manifests_for_build(rust_cfg, tmp_path, rust_cli)
    assert not rust_res.is_err()
    assert (tmp_path / "Cargo.toml").exists()


def test_update_manifests_for_build_handles_none_installation_and_scans_node_imports(
    tmp_path: Path,
):
    cli_dir = tmp_path / "src" / "test_cli"
    cli_dir.mkdir(parents=True, exist_ok=True)
    node_cli = cli_dir / "cli.js"
    node_cli.write_text(
        "import { Command } from 'commander';\n"
        "import ora from 'ora';\n"
        "import winston from 'winston';\n"
        "import { join } from 'path';\n",
        encoding="utf-8",
    )

    node_cfg = {
        "language": "nodejs",
        "cli": {"name": "nodecli"},
        "installation": None,
    }

    node_res = update_manifests_for_build(
        node_cfg, tmp_path, node_cli.relative_to(tmp_path)
    )
    assert not node_res.is_err()
    package_data = json.loads((tmp_path / "package.json").read_text(encoding="utf-8"))

    assert package_data["bin"]["nodecli"] == "src/test_cli/cli.js"
    assert package_data["dependencies"]["commander"].startswith("^")
    assert package_data["dependencies"]["ora"] == "latest"
    assert package_data["dependencies"]["winston"] == "latest"
