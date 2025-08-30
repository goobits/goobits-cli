"""
Test suite for the plugin system.

⚠️  FRAMEWORK-ONLY FEATURE: Plugin system exists in framework but is NOT integrated into generated CLIs.
    Users who run 'goobits build' will NOT have access to these features yet.

    Integration Status:
    - Framework: 60% complete (tested here)
    - User Integration: 0% complete
    - Generated CLIs: Basic local plugin scanning only

    These tests validate the framework implementation that will eventually be integrated.

Tests the PluginManager, PluginInfo, PluginRegistry, and integration components.
"""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock

from goobits_cli.universal.plugins.manager import (
    PluginManager,
    PluginInfo,
    PluginRegistry,
    PluginStatus,
    PluginType,
    get_plugin_manager,
)
from goobits_cli.universal.plugins.integration import (
    PluginCLIIntegrator,
    PluginCommandManager,
    setup_plugin_integration,
    create_plugin_template_context,
)


class TestPluginInfo:
    """Test PluginInfo data class."""

    def test_plugin_info_creation(self):
        """Test creating plugin info."""
        info = PluginInfo(
            name="test-plugin",
            version="1.0.0",
            description="Test plugin",
            author="Test Author",
        )

        assert info.name == "test-plugin"
        assert info.version == "1.0.0"
        assert info.description == "Test plugin"
        assert info.author == "Test Author"
        assert info.plugin_type == PluginType.COMMAND
        assert info.language == "python"
        assert info.status == PluginStatus.AVAILABLE

    def test_plugin_info_to_dict(self):
        """Test converting plugin info to dictionary."""
        info = PluginInfo(
            name="test-plugin", version="1.0.0", description="Test plugin"
        )

        data = info.to_dict()

        assert isinstance(data, dict)
        assert data["name"] == "test-plugin"
        assert data["version"] == "1.0.0"
        assert data["plugin_type"] == "command"
        assert data["language"] == "python"
        assert data["status"] == "available"

    def test_plugin_info_from_dict(self):
        """Test creating plugin info from dictionary."""
        data = {
            "name": "test-plugin",
            "version": "1.0.0",
            "description": "Test plugin",
            "plugin_type": "completion",
            "status": "installed",
            "language": "nodejs",
        }

        info = PluginInfo.from_dict(data)

        assert info.name == "test-plugin"
        assert info.plugin_type == PluginType.COMPLETION
        assert info.status == PluginStatus.INSTALLED
        assert info.language == "nodejs"


class TestPluginRegistry:
    """Test PluginRegistry functionality."""

    def setup_method(self):
        """Setup test registry."""
        self.temp_file = Path(tempfile.mktemp(suffix=".json"))
        self.registry = PluginRegistry(self.temp_file)

    def teardown_method(self):
        """Cleanup test registry."""
        if self.temp_file.exists():
            self.temp_file.unlink()

    def test_registry_initialization(self):
        """Test registry initializes properly."""
        assert len(self.registry.list_plugins()) == 0

    def test_add_plugin(self):
        """Test adding plugin to registry."""
        info = PluginInfo(name="test-plugin", version="1.0.0")
        self.registry.add_plugin(info)

        plugins = self.registry.list_plugins()
        assert len(plugins) == 1
        assert plugins[0].name == "test-plugin"

    def test_get_plugin(self):
        """Test getting plugin by name."""
        info = PluginInfo(name="test-plugin", version="1.0.0")
        self.registry.add_plugin(info)

        retrieved = self.registry.get_plugin("test-plugin")
        assert retrieved is not None
        assert retrieved.name == "test-plugin"

        not_found = self.registry.get_plugin("nonexistent")
        assert not_found is None

    def test_remove_plugin(self):
        """Test removing plugin from registry."""
        info = PluginInfo(name="test-plugin", version="1.0.0")
        self.registry.add_plugin(info)

        assert len(self.registry.list_plugins()) == 1

        removed = self.registry.remove_plugin("test-plugin")
        assert removed is True
        assert len(self.registry.list_plugins()) == 0

        not_removed = self.registry.remove_plugin("nonexistent")
        assert not_removed is False

    def test_list_plugins_by_status(self):
        """Test listing plugins filtered by status."""
        info1 = PluginInfo(name="plugin1", version="1.0.0")
        info1.status = PluginStatus.INSTALLED

        info2 = PluginInfo(name="plugin2", version="1.0.0")
        info2.status = PluginStatus.ENABLED

        self.registry.add_plugin(info1)
        self.registry.add_plugin(info2)

        installed = self.registry.list_plugins(PluginStatus.INSTALLED)
        assert len(installed) == 1
        assert installed[0].name == "plugin1"

        enabled = self.registry.list_plugins(PluginStatus.ENABLED)
        assert len(enabled) == 1
        assert enabled[0].name == "plugin2"

    def test_search_plugins(self):
        """Test searching plugins."""
        info1 = PluginInfo(
            name="test-plugin", description="A test plugin", tags=["testing"]
        )
        info2 = PluginInfo(
            name="other-plugin", description="Another plugin", tags=["utility"]
        )

        self.registry.add_plugin(info1)
        self.registry.add_plugin(info2)

        # Search by name
        results = self.registry.search_plugins("test")
        assert len(results) == 1
        assert results[0].name == "test-plugin"

        # Search by description
        results = self.registry.search_plugins("another")
        assert len(results) == 1
        assert results[0].name == "other-plugin"

        # Search by tag
        results = self.registry.search_plugins("testing")
        assert len(results) == 1
        assert results[0].name == "test-plugin"

    def test_registry_persistence(self):
        """Test that registry persists to file."""
        info = PluginInfo(name="test-plugin", version="1.0.0")
        self.registry.add_plugin(info)

        # Create new registry with same file
        new_registry = PluginRegistry(self.temp_file)
        plugins = new_registry.list_plugins()

        assert len(plugins) == 1
        assert plugins[0].name == "test-plugin"


class TestPluginManager:
    """Test PluginManager functionality."""

    def setup_method(self):
        """Setup test manager."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.manager = PluginManager(self.temp_dir)

    def teardown_method(self):
        """Cleanup test manager."""
        import shutil

        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    def test_manager_initialization(self):
        """Test manager initializes properly."""
        assert self.manager.plugins_dir.exists()
        assert isinstance(self.manager.registry, PluginRegistry)
        assert self.manager.sandbox_enabled is True

    @pytest.mark.asyncio
    async def test_resolve_local_plugin_source(self):
        """Test resolving local plugin source."""
        # Create a test plugin directory
        plugin_dir = self.temp_dir / "test-plugin"
        plugin_dir.mkdir()

        # Create plugin manifest
        manifest = plugin_dir / "plugin.yaml"
        manifest_content = """
name: test-plugin
version: 1.0.0
description: Test plugin
plugin_type: command
language: python
"""
        manifest.write_text(manifest_content)

        info = await self.manager._resolve_local_source(plugin_dir)

        assert info is not None
        assert info.name == "test-plugin"

    @pytest.mark.asyncio
    async def test_validate_plugin_security(self):
        """Test plugin security validation."""
        # Valid plugin
        valid_info = PluginInfo(
            name="valid-plugin",
            version="1.0.0",
            supported_platforms={"linux", "darwin", "win32"},
        )

        result = await self.manager._validate_plugin_security(valid_info)
        assert result is True

        # Invalid name
        invalid_info = PluginInfo(name="invalid-plugin!", version="1.0.0")

        result = await self.manager._validate_plugin_security(invalid_info)
        assert result is False

    def test_list_plugins(self):
        """Test listing plugins."""
        # Add some test plugins to registry
        info1 = PluginInfo(name="plugin1", version="1.0.0")
        info1.status = PluginStatus.INSTALLED

        info2 = PluginInfo(name="plugin2", version="1.0.0")
        info2.status = PluginStatus.ENABLED

        self.manager.registry.add_plugin(info1)
        self.manager.registry.add_plugin(info2)

        # List all plugins
        all_plugins = self.manager.list_plugins()
        assert len(all_plugins) == 2

        # List by status
        enabled_plugins = self.manager.list_plugins(PluginStatus.ENABLED)
        assert len(enabled_plugins) == 1
        assert enabled_plugins[0].name == "plugin2"

    def test_search_plugins(self):
        """Test searching plugins."""
        info = PluginInfo(name="test-search", description="Searchable plugin")
        self.manager.registry.add_plugin(info)

        results = self.manager.search_plugins("search")
        assert len(results) == 1
        assert results[0].name == "test-search"

    def test_get_plugin_info(self):
        """Test getting plugin information."""
        info = PluginInfo(name="test-info", version="3.0.1")
        self.manager.registry.add_plugin(info)

        retrieved = self.manager.get_plugin_info("test-info")
        assert retrieved is not None
        assert retrieved.version == "3.0.1"


class TestPluginCLIIntegrator:
    """Test PluginCLIIntegrator functionality."""

    def setup_method(self):
        """Setup test integrator."""
        self.integrator = PluginCLIIntegrator("python")

    @pytest.mark.asyncio
    async def test_get_plugin_commands(self):
        """Test getting plugin commands."""
        # Mock the plugin manager
        mock_manager = Mock()
        command_plugin = PluginInfo(
            name="cmd-plugin",
            plugin_type=PluginType.COMMAND,
            provides_commands=["custom-cmd"],
        )
        mock_manager.list_plugins.return_value = [command_plugin]

        self.integrator.manager = mock_manager

        commands = await self.integrator.get_plugin_commands()

        assert "cmd-plugin" in commands
        assert commands["cmd-plugin"] == command_plugin

    @pytest.mark.asyncio
    async def test_get_plugin_completions(self):
        """Test getting plugin completion providers."""
        # Mock the plugin manager
        mock_manager = Mock()
        completion_plugin = PluginInfo(
            name="completion-plugin", plugin_type=PluginType.COMPLETION
        )
        mock_manager.list_plugins.return_value = [completion_plugin]

        self.integrator.manager = mock_manager

        completions = await self.integrator.get_plugin_completions()

        assert len(completions) == 1
        assert completions[0] == completion_plugin

    @pytest.mark.asyncio
    async def test_integrate_plugins_with_cli(self):
        """Test integrating plugins with CLI config."""
        # Mock plugin commands
        with patch.object(
            self.integrator,
            "get_plugin_commands",
            AsyncMock(
                return_value={
                    "test-cmd": PluginInfo(
                        name="test-plugin", provides_commands=["test-cmd"]
                    )
                }
            ),
        ):

            base_config = {"name": "test-cli"}
            enhanced_config = await self.integrator.integrate_plugins_with_cli(
                base_config
            )

            assert "commands" in enhanced_config
            assert "test-cmd" in enhanced_config["commands"]

    def test_generate_python_integration_code(self):
        """Test generating Python integration code."""
        plugins = [
            PluginInfo(
                name="test-plugin",
                plugin_type=PluginType.COMMAND,
                provides_commands=["test-cmd"],
                install_path=Path("/path/to/plugin"),
            )
        ]

        code = self.integrator._generate_python_integration_code(plugins)

        assert "test-plugin" in code
        assert "load_plugins" in code
        assert "activate_plugins" in code

    def test_generate_nodejs_integration_code(self):
        """Test generating Node.js integration code."""
        plugins = [
            PluginInfo(
                name="test-plugin",
                plugin_type=PluginType.COMMAND,
                install_path=Path("/path/to/plugin"),
            )
        ]

        code = self.integrator._generate_nodejs_integration_code(plugins)

        assert "test-plugin" in code
        assert "loadPlugins" in code
        assert "activatePlugins" in code


class TestPluginCommandManager:
    """Test PluginCommandManager functionality."""

    def setup_method(self):
        """Setup test command manager."""
        self.manager = PluginCommandManager()

    @pytest.mark.asyncio
    async def test_register_plugin_commands(self):
        """Test registering plugin commands."""
        # Mock the plugin manager
        mock_plugin_manager = Mock()
        command_plugin = PluginInfo(
            name="test-plugin",
            plugin_type=PluginType.COMMAND,
            provides_commands=["cmd1", "cmd2"],
        )
        mock_plugin_manager.list_plugins.return_value = [command_plugin]

        self.manager.manager = mock_plugin_manager

        registered = await self.manager.register_plugin_commands()

        assert "cmd1" in registered
        assert "cmd2" in registered
        assert registered["cmd1"] == command_plugin

    @pytest.mark.asyncio
    async def test_unregister_plugin_commands(self):
        """Test unregistering plugin commands."""
        # Setup registered commands
        self.manager.registered_commands.add("test-cmd")

        # Mock plugin info
        mock_plugin_manager = Mock()
        plugin_info = PluginInfo(name="test-plugin", provides_commands=["test-cmd"])
        mock_plugin_manager.get_plugin_info.return_value = plugin_info

        self.manager.manager = mock_plugin_manager

        await self.manager.unregister_plugin_commands("test-plugin")

        assert "test-cmd" not in self.manager.registered_commands

    def test_is_plugin_command(self):
        """Test checking if command is from plugin."""
        self.manager.registered_commands.add("plugin-cmd")

        assert self.manager.is_plugin_command("plugin-cmd") is True
        assert self.manager.is_plugin_command("builtin-cmd") is False


class TestPluginIntegrationUtilities:
    """Test plugin integration utility functions."""

    def test_setup_plugin_integration(self):
        """Test setting up plugin integration."""
        integrator = setup_plugin_integration("python")

        assert isinstance(integrator, PluginCLIIntegrator)
        assert integrator.language == "python"

    def test_create_plugin_template_context(self):
        """Test creating plugin template context."""
        context = create_plugin_template_context(
            plugin_name="test-plugin",
            plugin_type="command",
            language="python",
            plugin_author="Test Author",
        )

        assert context["plugin_name"] == "test-plugin"
        assert context["plugin_type"] == "command"
        assert context["plugin_language"] == "python"
        assert context["plugin_author"] == "Test Author"
        assert context["plugin_version"] == "1.0.0"
        assert "test-plugin" in context["plugin_provides_commands"]


class TestGlobalPluginManager:
    """Test global plugin manager functionality."""

    def test_global_plugin_manager_singleton(self):
        """Test that global plugin manager is a singleton."""
        manager1 = get_plugin_manager()
        manager2 = get_plugin_manager()

        assert manager1 is manager2


if __name__ == "__main__":
    pytest.main([__file__])
