"""
Robust manifest file updater for Node.js package.json and Rust Cargo.toml.
Handles atomic updates with backup/rollback capabilities.
"""

import json
import re
import shutil
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional

import toml


class Result:
    """Simple Result type for error handling."""

    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error

    @classmethod
    def Ok(cls, value=None):
        return cls(value=value)

    @classmethod
    def Err(cls, error):
        return cls(error=error)

    def is_err(self):
        return self.error is not None

    def err(self):
        return self.error


class ManifestUpdater:
    """Handles atomic updates to package manifests with rollback capability."""

    def __init__(self):
        self.backup_files: List[Path] = []

    def update_package_json(
        self,
        package_json_path: Path,
        cli_name: str,
        cli_file: str,
        dependencies: Optional[Dict[str, str]] = None,
    ):
        """
        Atomically update package.json with CLI configuration and dependencies.

        Args:
            package_json_path: Path to package.json
            cli_name: Name of the CLI command
            cli_file: Path to the generated CLI file
            dependencies: Optional additional dependencies to merge
        """
        try:
            # Create backup
            backup_path = self._create_backup(package_json_path)

            # Load or create package.json
            if package_json_path.exists():
                with open(package_json_path) as f:
                    package_data = json.load(f)
            else:
                package_data = {}

            # Merge CLI configuration
            warnings = self._merge_nodejs_config(
                package_data, cli_name, cli_file, dependencies
            )

            # Atomic write
            self._atomic_write_json(package_json_path, package_data)

            return Result.Ok(warnings)

        except Exception as e:
            self._rollback_from_backup(package_json_path, backup_path)
            return Result.Err(f"Failed to update package.json: {e}")

    def update_cargo_toml(
        self,
        cargo_toml_path: Path,
        cli_name: str,
        cli_file: str,
        dependencies: Optional[Dict[str, Any]] = None,
    ):
        """
        Atomically update Cargo.toml with CLI configuration and dependencies.

        Args:
            cargo_toml_path: Path to Cargo.toml
            cli_name: Name of the CLI command
            cli_file: Path to the generated CLI file (relative to Cargo.toml)
            dependencies: Optional additional dependencies to merge
        """
        try:
            # Create backup
            backup_path = self._create_backup(cargo_toml_path)

            # Load or create Cargo.toml
            if cargo_toml_path.exists():
                with open(cargo_toml_path) as f:
                    cargo_data = toml.load(f)
            else:
                cargo_data = {}

            # Merge CLI configuration
            self._merge_rust_config(cargo_data, cli_name, cli_file, dependencies)

            # Atomic write
            self._atomic_write_toml(cargo_toml_path, cargo_data)

            return Result.Ok(None)

        except Exception as e:
            self._rollback_from_backup(cargo_toml_path, backup_path)
            return Result.Err(f"Failed to update Cargo.toml: {e}")

    def _merge_nodejs_config(
        self,
        package_data: Dict[str, Any],
        cli_name: str,
        cli_file: str,
        additional_deps: Optional[Dict[str, str]],
    ) -> List[str]:
        """
        Merge Node.js CLI configuration into package.json without overwriting user data.
        Returns list of warnings for user attention.
        """
        warnings = []

        # Handle type field - warn before overwriting non-module types
        current_type = package_data.get("type")
        if current_type is None:
            package_data["type"] = "module"
        elif current_type != "module":
            import typer

            typer.echo(
                f"⚠️  Warning: package.json has type='{current_type}' but generated CLI requires ES6 modules."
            )
            typer.echo(
                "   This will change your package.json type to 'module' which may affect existing CommonJS code."
            )

            proceed = typer.confirm("   Continue and change type to 'module'?")
            if proceed:
                package_data["type"] = "module"
                warnings.append(
                    f"Changed package.json type from '{current_type}' to 'module'"
                )
            else:
                # User declined - this should be treated as an error to abort manifest update
                raise ValueError(
                    f"User declined to change package.json type from '{current_type}' to 'module'"
                )

        # Set main entry point if not present
        if "main" not in package_data:
            package_data["main"] = cli_file

        # Merge bin configuration (preserve existing bins)
        if "bin" not in package_data:
            package_data["bin"] = {}

        if isinstance(package_data["bin"], str):
            # Convert string bin to object format
            old_bin = package_data["bin"]
            package_data["bin"] = {package_data.get("name", cli_name): old_bin}

        package_data["bin"][cli_name] = cli_file

        # Merge essential dependencies (don't overwrite existing versions)
        essential_deps = {
            "commander": "^11.1.0",
            "chalk": "^5.6.0",
            "js-yaml": "^4.1.0",
        }

        if additional_deps:
            for dep, version in additional_deps.items():
                if dep not in essential_deps:
                    essential_deps[dep] = version

        if "dependencies" not in package_data:
            package_data["dependencies"] = {}

        for dep, version in essential_deps.items():
            if dep not in package_data["dependencies"]:
                package_data["dependencies"][dep] = version

        # Set minimum Node.js version if not present
        if "engines" not in package_data:
            package_data["engines"] = {}
        if "node" not in package_data["engines"]:
            package_data["engines"]["node"] = ">=14.0.0"

        return warnings

    def extract_nodejs_import_dependencies(self, cli_source_path: Path) -> Dict[str, str]:
        """Extract external ESM import dependencies from a generated Node.js source file."""
        if not cli_source_path.exists():
            return {}

        content = cli_source_path.read_text(encoding="utf-8")
        imports = re.findall(r"from\s+['\"]([^'\"]+)['\"]", content)

        stdlib_modules = {
            "assert",
            "async_hooks",
            "buffer",
            "child_process",
            "crypto",
            "events",
            "fs",
            "http",
            "https",
            "module",
            "net",
            "os",
            "path",
            "process",
            "readline",
            "stream",
            "timers",
            "tty",
            "url",
            "util",
            "zlib",
        }

        external_deps: Dict[str, str] = {}
        for module_name in imports:
            if module_name.startswith((".", "/")):
                continue
            root_module = module_name.split("/", 1)[0]
            if root_module in stdlib_modules:
                continue
            external_deps[root_module] = "latest"

        return external_deps

    def _merge_rust_config(
        self,
        cargo_data: Dict[str, Any],
        cli_name: str,
        cli_file: str,
        additional_deps: Optional[Dict[str, Any]],
    ):
        """Merge Rust CLI configuration into Cargo.toml without overwriting user data."""

        # Ensure package section exists
        if "package" not in cargo_data:
            cargo_data["package"] = {}

        package_section = cargo_data["package"]

        # Set edition if not present
        if "edition" not in package_section:
            package_section["edition"] = "2021"

        # Add or update bin configuration
        if "bin" not in cargo_data:
            cargo_data["bin"] = []

        # Check if bin entry already exists
        existing_bin = None
        for bin_entry in cargo_data["bin"]:
            if bin_entry.get("name") == cli_name:
                existing_bin = bin_entry
                break

        if existing_bin:
            existing_bin["path"] = cli_file
        else:
            cargo_data["bin"].append({"name": cli_name, "path": cli_file})

        # Merge essential dependencies
        essential_deps = {
            "clap": {"version": "4.4", "features": ["derive", "color"]},
            "clap_complete": "4.4",
            "anyhow": "1.0",
            "thiserror": "1.0",
            "serde": {"version": "1.0", "features": ["derive"]},
            "serde_json": "1.0",
            "serde_yaml": "0.9",
            "chrono": {"version": "0.4", "features": ["serde"]},
            "dirs": "5.0",
            "log": "0.4",
            "env_logger": "0.10",
            "colored": "2.0",
        }

        if additional_deps:
            essential_deps.update(additional_deps)

        if "dependencies" not in cargo_data:
            cargo_data["dependencies"] = {}

        for dep, config in essential_deps.items():
            if dep not in cargo_data["dependencies"]:
                cargo_data["dependencies"][dep] = config

    def _create_backup(self, original_path: Path) -> Path:
        """Create a backup of the original file."""
        if not original_path.exists():
            return None

        backup_path = original_path.with_suffix(f"{original_path.suffix}.backup")
        shutil.copy2(original_path, backup_path)
        self.backup_files.append(backup_path)
        return backup_path

    def _atomic_write_json(self, file_path: Path, data: Dict[str, Any]):
        """Atomically write JSON data to file."""
        with tempfile.NamedTemporaryFile(
            mode="w", dir=file_path.parent, delete=False, suffix=".tmp"
        ) as temp_file:
            json.dump(data, temp_file, indent=2, ensure_ascii=False)
            temp_file.flush()
            temp_path = Path(temp_file.name)

        # Atomic move
        temp_path.replace(file_path)

    def _atomic_write_toml(self, file_path: Path, data: Dict[str, Any]):
        """Atomically write TOML data to file."""
        with tempfile.NamedTemporaryFile(
            mode="w", dir=file_path.parent, delete=False, suffix=".tmp"
        ) as temp_file:
            toml.dump(data, temp_file)
            temp_file.flush()
            temp_path = Path(temp_file.name)

        # Atomic move
        temp_path.replace(file_path)

    def _rollback_from_backup(self, original_path: Path, backup_path: Optional[Path]):
        """Rollback file from backup in case of failure."""
        if backup_path and backup_path.exists():
            shutil.copy2(backup_path, original_path)

    def cleanup_backups(self):
        """Clean up all backup files created during this session."""
        for backup_file in self.backup_files:
            if backup_file.exists():
                backup_file.unlink()
        self.backup_files.clear()


def update_manifests_for_build(
    config: Dict[str, Any], output_dir: Path, cli_path: Path
):
    """
    Update package manifests after CLI generation.

    Args:
        config: The goobits configuration
        output_dir: Directory where files are generated
        cli_path: Path to the generated CLI file
    """
    updater = ManifestUpdater()
    language = str(config.get("language", "python")).lower()
    cli_config = config.get("cli") if isinstance(config.get("cli"), dict) else {}
    cli_name = cli_config.get("name", "cli")
    installation = config.get("installation")
    installation_config = installation if isinstance(installation, dict) else {}
    extras = installation_config.get("extras")
    extras_config = extras if isinstance(extras, dict) else {}
    all_warnings = []

    try:
        if language == "nodejs":
            package_json_path = output_dir / "package.json"
            cli_file = cli_path.as_posix()

            # Extract additional dependencies from config if present
            extra_deps = dict(extras_config.get("npm", {}))
            generated_cli_path = output_dir / cli_path
            extra_deps.update(updater.extract_nodejs_import_dependencies(generated_cli_path))

            result = updater.update_package_json(
                package_json_path, cli_name, cli_file, extra_deps
            )

            if result.is_err():
                return result
            else:
                all_warnings.extend(result.value or [])

        elif language == "rust":
            cargo_toml_path = output_dir / "Cargo.toml"
            cli_file = cli_path.as_posix()

            # Extract additional dependencies from config if present
            extra_deps = extras_config.get("cargo", {})

            result = updater.update_cargo_toml(
                cargo_toml_path, cli_name, cli_file, extra_deps
            )

            if result.is_err():
                return result
            # Note: Rust updates don't return warnings currently

        return Result.Ok(all_warnings)

    except Exception as e:
        updater.cleanup_backups()
        return Result.Err(f"Manifest update failed: {e}")

    finally:
        # Clean up backups on success
        updater.cleanup_backups()
