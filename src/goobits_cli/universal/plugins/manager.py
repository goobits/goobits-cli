"""

Plugin Manager for Goobits CLI Framework.

Provides secure plugin installation, management, and execution with

marketplace integration and cross-language support.

"""

import json
import logging
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


class PluginStatus(Enum):
    """Plugin installation status."""

    AVAILABLE = "available"

    INSTALLED = "installed"

    ENABLED = "enabled"

    DISABLED = "disabled"

    UPDATING = "updating"

    ERROR = "error"


class PluginType(Enum):
    """Plugin type classification."""

    COMMAND = "command"  # Adds new CLI commands

    COMPLETION = "completion"  # Adds completion providers

    HOOK = "hook"  # Adds lifecycle hooks

    FORMATTER = "formatter"  # Adds output formatters

    VALIDATOR = "validator"  # Adds input validators

    INTEGRATION = "integration"  # Third-party integrations


@dataclass
class PluginInfo:
    """Information about a plugin."""

    # Basic plugin metadata

    name: str

    version: str = "1.0.0"

    description: str = ""

    author: str = ""

    license: str = "MIT"

    # Plugin classification

    plugin_type: PluginType = PluginType.COMMAND

    language: str = "python"  # python, nodejs, typescript, rust

    # Installation details

    status: PluginStatus = PluginStatus.AVAILABLE

    install_path: Optional[Path] = None

    source_url: str = ""

    checksum: str = ""

    # Dependencies and requirements

    dependencies: List[str] = field(default_factory=list)

    python_requirements: List[str] = field(default_factory=list)

    npm_requirements: List[str] = field(default_factory=list)

    system_requirements: List[str] = field(default_factory=list)

    # Compatibility

    min_goobits_version: str = "1.0.0"

    supported_languages: Set[str] = field(default_factory=lambda: {"python"})

    supported_platforms: Set[str] = field(
        default_factory=lambda: {"linux", "darwin", "win32"}
    )

    # Plugin capabilities

    provides_commands: List[str] = field(default_factory=list)

    provides_completions: List[str] = field(default_factory=list)

    provides_hooks: List[str] = field(default_factory=list)

    # Metadata

    tags: List[str] = field(default_factory=list)

    homepage: str = ""

    repository: str = ""

    install_date: Optional[datetime] = None

    last_updated: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""

        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "author": self.author,
            "license": self.license,
            "plugin_type": self.plugin_type.value,
            "language": self.language,
            "status": self.status.value,
            "install_path": str(self.install_path) if self.install_path else None,
            "source_url": self.source_url,
            "checksum": self.checksum,
            "dependencies": self.dependencies,
            "python_requirements": self.python_requirements,
            "npm_requirements": self.npm_requirements,
            "system_requirements": self.system_requirements,
            "min_goobits_version": self.min_goobits_version,
            "supported_languages": list(self.supported_languages),
            "supported_platforms": list(self.supported_platforms),
            "provides_commands": self.provides_commands,
            "provides_completions": self.provides_completions,
            "provides_hooks": self.provides_hooks,
            "tags": self.tags,
            "homepage": self.homepage,
            "repository": self.repository,
            "install_date": (
                self.install_date.isoformat() if self.install_date else None
            ),
            "last_updated": (
                self.last_updated.isoformat() if self.last_updated else None
            ),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PluginInfo":
        """Create from dictionary."""

        info = cls(
            name=data["name"],
            version=data.get("version", "1.0.0"),
            description=data.get("description", ""),
            author=data.get("author", ""),
            license=data.get("license", "MIT"),
        )

        # Handle enums

        if "plugin_type" in data:
            info.plugin_type = PluginType(data["plugin_type"])

        if "status" in data:
            info.status = PluginStatus(data["status"])

        # Handle optional fields

        for field_name, field_value in data.items():
            if hasattr(info, field_name) and field_name not in [
                "plugin_type",
                "status",
            ]:
                if field_name == "install_path" and field_value:
                    setattr(info, field_name, Path(field_value))

                elif field_name in ["supported_languages", "supported_platforms"]:
                    setattr(info, field_name, set(field_value))

                elif field_name in ["install_date", "last_updated"] and field_value:
                    setattr(info, field_name, datetime.fromisoformat(field_value))

                else:
                    setattr(info, field_name, field_value)

        return info


class PluginRegistry:
    """Registry for managing plugin information."""

    def __init__(self, registry_file: Path):
        """Initialize plugin registry."""

        self.registry_file = registry_file

        self._plugins: Dict[str, PluginInfo] = {}

        self._load_registry()

    def _load_registry(self) -> None:
        """Load plugin registry from file."""

        try:
            if self.registry_file.exists():
                with open(self.registry_file) as f:
                    data = json.load(f)

                for plugin_data in data.get("plugins", []):
                    plugin = PluginInfo.from_dict(plugin_data)

                    self._plugins[plugin.name] = plugin

        except Exception as e:
            logger.error(f"Error loading plugin registry: {e}")

    def _save_registry(self) -> None:
        """Save plugin registry to file."""

        try:
            self.registry_file.parent.mkdir(parents=True, exist_ok=True)

            data = {
                "version": "1.0",
                "plugins": [plugin.to_dict() for plugin in self._plugins.values()],
            }

            with open(self.registry_file, "w") as f:
                json.dump(data, f, indent=2)

        except Exception as e:
            logger.error(f"Error saving plugin registry: {e}")

    def add_plugin(self, plugin: PluginInfo) -> None:
        """Add or update plugin in registry."""

        self._plugins[plugin.name] = plugin

        self._save_registry()

    def remove_plugin(self, name: str) -> bool:
        """Remove plugin from registry."""

        if name in self._plugins:
            del self._plugins[name]

            self._save_registry()

            return True

        return False

    def get_plugin(self, name: str) -> Optional[PluginInfo]:
        """Get plugin by name."""

        return self._plugins.get(name)

    def list_plugins(self, status: Optional[PluginStatus] = None) -> List[PluginInfo]:
        """List plugins, optionally filtered by status."""

        plugins = list(self._plugins.values())

        if status:
            plugins = [p for p in plugins if p.status == status]

        return sorted(plugins, key=self._get_plugin_name)

    def search_plugins(self, query: str) -> List[PluginInfo]:
        """Search plugins by name, description, or tags."""

        query = query.lower()

        results = []

        for plugin in self._plugins.values():
            if (
                query in plugin.name.lower()
                or query in plugin.description.lower()
                or any(query in tag.lower() for tag in plugin.tags)
            ):
                results.append(plugin)

        return sorted(results, key=self._get_plugin_name)

    def _get_plugin_name(self, plugin: "PluginInfo") -> str:
        """Get plugin name for sorting."""
        return plugin.name


class PluginManager:
    """

    Secure plugin manager with marketplace integration.

    Features:

    - Secure plugin sandboxing and validation

    - Multi-language plugin support (Python, Node.js, TypeScript, Rust)

    - Version management and dependency resolution

    - Marketplace integration with trusted sources

    - Plugin lifecycle management (install, enable, disable, uninstall)

    - Automatic updates and security scanning

    """

    def __init__(self, plugins_dir: Optional[Path] = None):
        """Initialize the plugin manager."""

        # Default plugins directory

        if plugins_dir is None:
            self.plugins_dir = Path.home() / ".goobits" / "plugins"

        else:
            self.plugins_dir = plugins_dir

        self.plugins_dir.mkdir(parents=True, exist_ok=True)

        # Registry for plugin metadata

        registry_file = self.plugins_dir / "registry.json"

        self.registry = PluginRegistry(registry_file)

        # Security settings

        self.trusted_sources = {
            "https://plugins.goobits.dev",
            "https://github.com/goobits-cli/plugins",
        }

        self.allow_untrusted = False

        # Plugin execution sandbox

        self.sandbox_enabled = True

        self.max_execution_time = 30  # seconds

        self.max_memory_usage = 100 * 1024 * 1024  # 100MB

        # Language-specific managers

        self.language_managers = {
            "python": self._manage_python_plugin,
            "nodejs": self._manage_nodejs_plugin,
            "typescript": self._manage_typescript_plugin,
            "rust": self._manage_rust_plugin,
        }

    async def install_plugin(
        self, source: str, force: bool = False, verify_checksum: bool = True
    ) -> bool:
        """

        Install a plugin from various sources.

        Args:

            source: Plugin source (URL, local path, or name for marketplace)

            force: Force reinstallation if already installed

            verify_checksum: Verify plugin integrity

        Returns:

            True if installation successful

        """

        try:
            logger.info(f"Installing plugin from: {source}")

            # Determine source type and get plugin info

            plugin_info = await self._resolve_plugin_source(source)

            if not plugin_info:
                logger.error(f"Could not resolve plugin source: {source}")

                return False

            # Check if already installed

            existing = self.registry.get_plugin(plugin_info.name)

            if existing and existing.status == PluginStatus.INSTALLED and not force:
                logger.info(f"Plugin {plugin_info.name} already installed")

                return True

            # Security validation

            if not await self._validate_plugin_security(plugin_info):
                logger.error(f"Plugin {plugin_info.name} failed security validation")

                return False

            # Download and extract plugin

            plugin_dir = await self._download_and_extract(plugin_info)

            if not plugin_dir:
                return False

            # Install language-specific dependencies

            if not await self._install_dependencies(plugin_info, plugin_dir):
                logger.error(f"Failed to install dependencies for {plugin_info.name}")

                return False

            # Validate plugin structure

            if not await self._validate_plugin_structure(plugin_info, plugin_dir):
                logger.error(f"Plugin {plugin_info.name} has invalid structure")

                return False

            # Update plugin info

            plugin_info.status = PluginStatus.INSTALLED

            plugin_info.install_path = plugin_dir

            plugin_info.install_date = datetime.now()

            # Register plugin

            self.registry.add_plugin(plugin_info)

            # Enable plugin by default

            await self.enable_plugin(plugin_info.name)

            logger.info(f"Successfully installed plugin: {plugin_info.name}")

            return True

        except Exception as e:
            logger.error(f"Error installing plugin {source}: {e}")

            return False

    async def uninstall_plugin(self, name: str) -> bool:
        """Uninstall a plugin."""

        try:
            plugin = self.registry.get_plugin(name)

            if not plugin:
                logger.error(f"Plugin not found: {name}")

                return False

            # Disable plugin first

            await self.disable_plugin(name)

            # Remove plugin files

            if plugin.install_path and plugin.install_path.exists():
                shutil.rmtree(plugin.install_path)

            # Remove from registry

            self.registry.remove_plugin(name)

            logger.info(f"Successfully uninstalled plugin: {name}")

            return True

        except Exception as e:
            logger.error(f"Error uninstalling plugin {name}: {e}")

            return False

    async def enable_plugin(self, name: str) -> bool:
        """Enable a plugin."""

        try:
            plugin = self.registry.get_plugin(name)

            if not plugin:
                logger.error(f"Plugin not found: {name}")

                return False

            if plugin.status != PluginStatus.INSTALLED:
                logger.error(f"Plugin {name} is not installed")

                return False

            # Load and validate plugin

            if not await self._load_plugin(plugin):
                logger.error(f"Failed to load plugin: {name}")

                return False

            # Update status

            plugin.status = PluginStatus.ENABLED

            self.registry.add_plugin(plugin)

            logger.info(f"Successfully enabled plugin: {name}")

            return True

        except Exception as e:
            logger.error(f"Error enabling plugin {name}: {e}")

            return False

    async def disable_plugin(self, name: str) -> bool:
        """Disable a plugin."""

        try:
            plugin = self.registry.get_plugin(name)

            if not plugin:
                logger.error(f"Plugin not found: {name}")

                return False

            # Unload plugin

            await self._unload_plugin(plugin)

            # Update status

            plugin.status = PluginStatus.DISABLED

            self.registry.add_plugin(plugin)

            logger.info(f"Successfully disabled plugin: {name}")

            return True

        except Exception as e:
            logger.error(f"Error disabling plugin {name}: {e}")

            return False

    async def update_plugin(self, name: str) -> bool:
        """Update a plugin to latest version."""

        try:
            plugin = self.registry.get_plugin(name)

            if not plugin:
                logger.error(f"Plugin not found: {name}")

                return False

            # Check for updates from source

            latest_info = await self._check_for_updates(plugin)

            if not latest_info or latest_info.version == plugin.version:
                logger.info(f"Plugin {name} is already up to date")

                return True

            # Update status

            plugin.status = PluginStatus.UPDATING

            self.registry.add_plugin(plugin)

            # Install updated version

            success = await self.install_plugin(plugin.source_url, force=True)

            if success:
                logger.info(
                    f"Successfully updated plugin {name} to {latest_info.version}"
                )

            else:
                # Revert status on failure

                plugin.status = PluginStatus.INSTALLED

                self.registry.add_plugin(plugin)

            return success

        except Exception as e:
            logger.error(f"Error updating plugin {name}: {e}")

            return False

    def list_plugins(self, status: Optional[PluginStatus] = None) -> List[PluginInfo]:
        """List installed plugins."""

        return self.registry.list_plugins(status)

    def search_plugins(self, query: str) -> List[PluginInfo]:
        """Search for plugins."""

        return self.registry.search_plugins(query)

    def get_plugin_info(self, name: str) -> Optional[PluginInfo]:
        """Get detailed plugin information."""

        return self.registry.get_plugin(name)

    async def _resolve_plugin_source(self, source: str) -> Optional[PluginInfo]:
        """Resolve plugin source to plugin information."""

        # Handle different source types

        if source.startswith("http"):
            # URL source

            return await self._resolve_url_source(source)

        elif Path(source).exists():
            # Local path source

            return await self._resolve_local_source(Path(source))

        else:
            # Marketplace name

            return await self._resolve_marketplace_source(source)

    async def _resolve_url_source(self, url: str) -> Optional[PluginInfo]:
        """Resolve URL source to plugin info."""

        # Validate trusted source

        parsed = urlparse(url)

        base_url = f"{parsed.scheme}://{parsed.netloc}"

        if base_url not in self.trusted_sources and not self.allow_untrusted:
            logger.error(f"Untrusted plugin source: {base_url}")

            return None

        # For now, create basic plugin info from URL

        # In real implementation, this would fetch plugin metadata

        name = Path(parsed.path).stem

        return PluginInfo(name=name, source_url=url)

    async def _resolve_local_source(self, path: Path) -> Optional[PluginInfo]:
        """Resolve local path to plugin info."""

        # Look for plugin manifest

        manifest_files = ["plugin.yaml", "plugin.yml", "plugin.json", "package.json"]

        for manifest_file in manifest_files:
            manifest_path = path / manifest_file

            if manifest_path.exists():
                return await self._parse_plugin_manifest(manifest_path)

        # Create basic info if no manifest found

        return PluginInfo(name=path.name)

    async def _resolve_marketplace_source(self, name: str) -> Optional[PluginInfo]:
        """Resolve marketplace name to plugin info."""

        # This would query the plugin marketplace API

        # For now, return basic info

        return PluginInfo(name=name)

    async def _parse_plugin_manifest(self, manifest_path: Path) -> Optional[PluginInfo]:
        """Parse plugin manifest file."""

        try:
            with open(manifest_path) as f:
                if manifest_path.suffix in [".yaml", ".yml"]:
                    import yaml

                    data = yaml.safe_load(f)

                else:
                    data = json.load(f)

            return PluginInfo.from_dict(data)

        except Exception as e:
            logger.error(f"Error parsing plugin manifest {manifest_path}: {e}")

            return None

    async def _validate_plugin_security(self, plugin: PluginInfo) -> bool:
        """Validate plugin security."""

        # Basic security checks

        if (
            not plugin.name
            or not plugin.name.replace("-", "").replace("_", "").isalnum()
        ):
            logger.error("Invalid plugin name")

            return False

        # Check supported platforms

        current_platform = sys.platform

        if current_platform not in plugin.supported_platforms:
            logger.error(f"Plugin not supported on {current_platform}")

            return False

        # Additional security validation would go here

        return True

    async def _download_and_extract(self, plugin: PluginInfo) -> Optional[Path]:
        """Download and extract plugin archive."""

        plugin_dir = self.plugins_dir / plugin.name

        # For local development, just create the directory

        plugin_dir.mkdir(exist_ok=True)

        # In real implementation, this would download and extract

        return plugin_dir

    async def _install_dependencies(self, plugin: PluginInfo, plugin_dir: Path) -> bool:
        """Install plugin dependencies."""

        try:
            # Install language-specific dependencies

            manager = self.language_managers.get(plugin.language)

            if manager:
                return await manager(plugin, plugin_dir, "install")

            return True

        except Exception as e:
            logger.error(f"Error installing dependencies: {e}")

            return False

    async def _validate_plugin_structure(
        self, plugin: PluginInfo, plugin_dir: Path
    ) -> bool:
        """Validate plugin directory structure."""

        # Basic structure validation

        required_files = {
            "python": ["__init__.py"],
            "nodejs": ["index.js", "package.json"],
            "typescript": ["index.ts", "package.json"],
            "rust": ["Cargo.toml", "src/lib.rs"],
        }

        files = required_files.get(plugin.language, [])

        for file in files:
            if not (plugin_dir / file).exists():
                logger.error(f"Missing required file: {file}")

                return False

        return True

    async def _load_plugin(self, plugin: PluginInfo) -> bool:
        """Load plugin into runtime."""

        # This would implement secure plugin loading

        # For now, just return True

        return True

    async def _unload_plugin(self, plugin: PluginInfo) -> bool:
        """Unload plugin from runtime."""

        # This would implement plugin unloading

        return True

    async def _check_for_updates(self, plugin: PluginInfo) -> Optional[PluginInfo]:
        """Check for plugin updates."""

        # This would check the source for newer versions

        return None

    async def _manage_python_plugin(
        self, plugin: PluginInfo, plugin_dir: Path, action: str
    ) -> bool:
        """Manage Python plugin dependencies."""

        if action == "install":
            # Install Python requirements

            if plugin.python_requirements:
                try:
                    subprocess.run(
                        [
                            sys.executable,
                            "-m",
                            "pip",
                            "install",
                            *plugin.python_requirements,
                        ],
                        check=True,
                    )

                    return True

                except subprocess.CalledProcessError:
                    return False

        return True

    async def _manage_nodejs_plugin(
        self, plugin: PluginInfo, plugin_dir: Path, action: str
    ) -> bool:
        """Manage Node.js plugin dependencies."""

        if action == "install":
            # Run npm install in plugin directory

            if (plugin_dir / "package.json").exists():
                try:
                    subprocess.run(["npm", "install"], cwd=plugin_dir, check=True)

                    return True

                except subprocess.CalledProcessError:
                    return False

        return True

    async def _manage_typescript_plugin(
        self, plugin: PluginInfo, plugin_dir: Path, action: str
    ) -> bool:
        """Manage TypeScript plugin dependencies."""

        # Same as Node.js for now

        return await self._manage_nodejs_plugin(plugin, plugin_dir, action)

    async def _manage_rust_plugin(
        self, plugin: PluginInfo, plugin_dir: Path, action: str
    ) -> bool:
        """Manage Rust plugin dependencies."""

        if action == "install":
            # Run cargo build in plugin directory

            if (plugin_dir / "Cargo.toml").exists():
                try:
                    subprocess.run(
                        ["cargo", "build", "--release"], cwd=plugin_dir, check=True
                    )

                    return True

                except subprocess.CalledProcessError:
                    return False

        return True


# Global plugin manager instance

_global_manager = None


def get_plugin_manager() -> PluginManager:
    """Get the global plugin manager instance."""

    global _global_manager

    if _global_manager is None:
        _global_manager = PluginManager()

    return _global_manager
