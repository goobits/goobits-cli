"""

Plugin system integration utilities for Goobits CLI Framework.

Provides helper functions and classes to integrate the plugin system

with CLI generation and interactive modes across all supported languages.

"""

from typing import Any, Dict, List, Set

from jinja2 import Template

from .manager import PluginInfo, PluginStatus, PluginType, get_plugin_manager


class PluginCLIIntegrator:
    """

    Integrates plugins with CLI generation and command systems.

    Provides seamless integration between plugins and the main CLI

    application across all supported languages.

    """

    def __init__(self, language: str = "python"):
        """Initialize the integrator for a specific language."""

        self.language = language

        self.manager = get_plugin_manager()

    async def get_plugin_commands(self) -> Dict[str, List[PluginInfo]]:
        """

        Get all plugin-provided commands organized by plugin.

        Returns:

            Dictionary mapping plugin names to their command plugins

        """

        command_plugins = {}

        plugins = self.manager.list_plugins(status=PluginStatus.ENABLED)

        for plugin in plugins:
            if plugin.plugin_type == PluginType.COMMAND:
                command_plugins[plugin.name] = plugin

        return command_plugins

    async def get_plugin_completions(self) -> List[PluginInfo]:
        """

        Get all plugin-provided completion providers.

        Returns:

            List of completion plugins

        """

        completion_plugins = []

        plugins = self.manager.list_plugins(status=PluginStatus.ENABLED)

        for plugin in plugins:
            if plugin.plugin_type == PluginType.COMPLETION:
                completion_plugins.append(plugin)

        return completion_plugins

    async def integrate_plugins_with_cli(
        self, cli_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """

        Integrate enabled plugins with CLI configuration.

        Args:

            cli_config: Base CLI configuration

        Returns:

            Enhanced CLI configuration with plugin commands

        """

        enhanced_config = cli_config.copy()

        # Get plugin commands

        plugin_commands = await self.get_plugin_commands()

        # Add plugin commands to CLI configuration

        if "commands" not in enhanced_config:
            enhanced_config["commands"] = {}

        for plugin_name, plugin in plugin_commands.items():
            for command_name in plugin.provides_commands:
                plugin_command_config = {
                    "description": f"Command from {plugin.name} plugin",
                    "plugin_name": plugin.name,
                    "plugin_type": plugin.plugin_type.value,
                    "language": plugin.language,
                }

                enhanced_config["commands"][command_name] = plugin_command_config

        return enhanced_config

    def generate_plugin_integration_code(self, plugins: List[PluginInfo]) -> str:
        """

        Generate language-specific code to integrate plugins.

        Args:

            plugins: List of plugins to integrate

        Returns:

            Generated integration code

        """

        if self.language == "python":
            return self._generate_python_integration_code(plugins)

        elif self.language == "nodejs":
            return self._generate_nodejs_integration_code(plugins)

        elif self.language == "typescript":
            return self._generate_typescript_integration_code(plugins)

        elif self.language == "rust":
            return self._generate_rust_integration_code(plugins)

        else:
            return ""

    def _generate_python_integration_code(self, plugins: List[PluginInfo]) -> str:
        """Generate Python plugin integration code."""

        template = Template(
            '''

# Plugin Integration Code (Generated)

import importlib

import sys

from typing import Dict, Any

# Plugin registry

PLUGINS = {

{% for plugin in plugins %}

    '{{ plugin.name }}': {

        'path': '{{ plugin.install_path }}',

        'type': '{{ plugin.plugin_type.value }}',

        'provides_commands': {{ plugin.provides_commands | list | tojson }},

        'provides_completions': {{ plugin.provides_completions | list | tojson }},

    },

{% endfor %}

}

def load_plugins():

    """Load all enabled plugins."""

    loaded_plugins = {}

    for name, info in PLUGINS.items():

        try:

            # Add plugin path to sys.path if needed

            plugin_path = info['path']

            if str(plugin_path) not in sys.path:

                sys.path.insert(0, str(plugin_path))

            # Import plugin module

            module = importlib.import_module(name)

            plugin_instance = module.create_plugin()

            loaded_plugins[name] = {

                'instance': plugin_instance,

                'info': info,

                'module': module

            }

        except Exception as e:

            print(f"Failed to load plugin {name}: {e}")

    return loaded_plugins

def activate_plugins(plugins: Dict[str, Any]):

    """Activate all loaded plugins."""

    for name, plugin_data in plugins.items():

        try:

            plugin_instance = plugin_data['instance']

            plugin_instance.activate()

        except Exception as e:

            print(f"Failed to activate plugin {name}: {e}")

'''
        )

        return template.render(plugins=plugins)

    def _generate_nodejs_integration_code(self, plugins: List[PluginInfo]) -> str:
        """Generate Node.js plugin integration code."""

        template = Template(
            """

// Plugin Integration Code (Generated)

const path = require('path');

// Plugin registry

const PLUGINS = {

{% for plugin in plugins %}

  '{{ plugin.name }}': {

    path: '{{ plugin.install_path }}',

    type: '{{ plugin.plugin_type.value }}',

    providesCommands: {{ plugin.provides_commands | list | tojson }},

    providesCompletions: {{ plugin.provides_completions | list | tojson }},

  },

{% endfor %}

};

/**

 * Load all enabled plugins.

 */

function loadPlugins() {

  const loadedPlugins = {};

  for (const [name, info] of Object.entries(PLUGINS)) {

    try {

      // Require plugin module

      const pluginPath = path.join(info.path, 'index.js');

      const pluginModule = require(pluginPath);

      const pluginInstance = pluginModule.createPlugin();

      loadedPlugins[name] = {

        instance: pluginInstance,

        info: info,

        module: pluginModule

      };

    } catch (error) {

      console.error(`Failed to load plugin ${name}:`, error);

    }

  }

  return loadedPlugins;

}

/**

 * Activate all loaded plugins.

 */

async function activatePlugins(plugins) {

  for (const [name, pluginData] of Object.entries(plugins)) {

    try {

      const pluginInstance = pluginData.instance;

      await pluginInstance.activate();

    } catch (error) {

      console.error(`Failed to activate plugin ${name}:`, error);

    }

  }

}

module.exports = { loadPlugins, activatePlugins, PLUGINS };

"""
        )

        return template.render(plugins=plugins)

    def _generate_typescript_integration_code(self, plugins: List[PluginInfo]) -> str:
        """Generate TypeScript plugin integration code."""

        template = Template(
            """

// Plugin Integration Code (Generated)

import * as path from 'path';

// Plugin registry

const PLUGINS: Record<string, any> = {

{% for plugin in plugins %}

  '{{ plugin.name }}': {

    path: '{{ plugin.install_path }}',

    type: '{{ plugin.plugin_type.value }}',

    providesCommands: {{ plugin.provides_commands | list | tojson }},

    providesCompletions: {{ plugin.provides_completions | list | tojson }},

  },

{% endfor %}

};

/**

 * Load all enabled plugins.

 */

export function loadPlugins(): Record<string, any> {

  const loadedPlugins: Record<string, any> = {};

  for (const [name, info] of Object.entries(PLUGINS)) {

    try {

      // Import plugin module

      const pluginPath = path.join(info.path, 'dist', 'index.js');

      const pluginModule = require(pluginPath);

      const pluginInstance = pluginModule.createPlugin();

      loadedPlugins[name] = {

        instance: pluginInstance,

        info: info,

        module: pluginModule

      };

    } catch (error) {

      console.error(`Failed to load plugin ${name}:`, error);

    }

  }

  return loadedPlugins;

}

/**

 * Activate all loaded plugins.

 */

export async function activatePlugins(plugins: Record<string, any>): Promise<void> {

  for (const [name, pluginData] of Object.entries(plugins)) {

    try {

      const pluginInstance = pluginData.instance;

      await pluginInstance.activate();

    } catch (error) {

      console.error(`Failed to activate plugin ${name}:`, error);

    }

  }

}

export { PLUGINS };

"""
        )

        return template.render(plugins=plugins)

    def _generate_rust_integration_code(self, plugins: List[PluginInfo]) -> str:
        """Generate Rust plugin integration code."""

        template = Template(
            """

// Plugin Integration Code (Generated)

use std::collections::HashMap;

use std::path::PathBuf;

use async_trait::async_trait;

use log::{info, error};

// Plugin registry

lazy_static::lazy_static! {

    static ref PLUGINS: HashMap<&'static str, PluginInfo> = {

        let mut plugins = HashMap::new();

        {% for plugin in plugins %}

        plugins.insert("{{ plugin.name }}", PluginInfo {

            name: "{{ plugin.name }}".to_string(),

            path: PathBuf::from("{{ plugin.install_path }}"),

            plugin_type: "{{ plugin.plugin_type.value }}".to_string(),

            provides_commands: vec![{% for cmd in plugin.provides_commands %}"{{ cmd }}".to_string(),{% endfor %}],

            provides_completions: vec![{% for comp in plugin.provides_completions %}"{{ comp }}".to_string(),{% endfor %}],

        });

        {% endfor %}

        plugins

    };

}

#[derive(Debug, Clone)]

pub struct PluginInfo {

    pub name: String,

    pub path: PathBuf,

    pub plugin_type: String,

    pub provides_commands: Vec<String>,

    pub provides_completions: Vec<String>,

}

/**

 * Load all enabled plugins.

 */

pub fn load_plugins() -> HashMap<String, Box<dyn Plugin>> {

    let mut loaded_plugins: HashMap<String, Box<dyn Plugin>> = HashMap::new();

    for (name, info) in PLUGINS.iter() {

        match load_plugin_from_path(&info.path) {

            Ok(plugin) => {

                loaded_plugins.insert(name.to_string(), plugin);

                info!("Loaded plugin: {}", name);

            }

            Err(e) => {

                error!("Failed to load plugin {}: {}", name, e);

            }

        }

    }

    loaded_plugins

}

/**

 * Activate all loaded plugins.

 */

pub async fn activate_plugins(plugins: &mut HashMap<String, Box<dyn Plugin>>) {

    for (name, plugin) in plugins.iter_mut() {

        match plugin.activate().await {

            Ok(_) => info!("Activated plugin: {}", name),

            Err(e) => error!("Failed to activate plugin {}: {}", name, e),

        }

    }

}

fn load_plugin_from_path(path: &PathBuf) -> Result<Box<dyn Plugin>, Box<dyn std::error::Error>> {

    // In a real implementation, this would use dynamic loading

    // For now, plugins would need to be statically linked or use a plugin registry

    Err("Dynamic plugin loading not implemented".into())

}

"""
        )

        return template.render(plugins=plugins)


class PluginCommandManager:
    """

    Manages plugin-provided commands in the CLI system.

    """

    def __init__(self):
        """Initialize the command manager."""

        self.manager = get_plugin_manager()

        self.registered_commands: Set[str] = set()

    async def register_plugin_commands(self) -> Dict[str, PluginInfo]:
        """

        Register all plugin-provided commands.

        Returns:

            Dictionary of registered commands and their plugins

        """

        registered = {}

        plugins = self.manager.list_plugins(status=PluginStatus.ENABLED)

        for plugin in plugins:
            if plugin.plugin_type == PluginType.COMMAND:
                for command_name in plugin.provides_commands:
                    if command_name not in self.registered_commands:
                        registered[command_name] = plugin

                        self.registered_commands.add(command_name)

        return registered

    async def unregister_plugin_commands(self, plugin_name: str) -> None:
        """

        Unregister commands from a specific plugin.

        Args:

            plugin_name: Name of the plugin to unregister

        """

        plugin = self.manager.get_plugin_info(plugin_name)

        if plugin:
            for command_name in plugin.provides_commands:
                self.registered_commands.discard(command_name)

    def is_plugin_command(self, command_name: str) -> bool:
        """

        Check if a command is provided by a plugin.

        Args:

            command_name: Name of the command to check

        Returns:

            True if command is from a plugin

        """

        return command_name in self.registered_commands


def setup_plugin_integration(language: str) -> PluginCLIIntegrator:
    """

    Setup plugin integration for a specific language.

    Args:

        language: Target language (python, nodejs, typescript, rust)

    Returns:

        Configured plugin integrator

    """

    return PluginCLIIntegrator(language)


def create_plugin_template_context(
    plugin_name: str, plugin_type: str, language: str, **kwargs
) -> Dict[str, Any]:
    """

    Create template context for plugin generation.

    Args:

        plugin_name: Name of the plugin

        plugin_type: Type of plugin (command, completion, etc.)

        language: Target language

        **kwargs: Additional template variables

    Returns:

        Template context dictionary

    """

    context = {
        "plugin_name": plugin_name,
        "plugin_type": plugin_type,
        "plugin_language": language,
        "plugin_version": "1.0.0",
        "plugin_description": f"{plugin_name} plugin for Goobits CLI",
        "plugin_author": "Plugin Author",
        "plugin_license": "MIT",
        "plugin_priority": 50,
        "plugin_dependencies": [],
        "plugin_python_requirements": [],
        "plugin_npm_requirements": [],
        "plugin_rust_dependencies": [],
        "plugin_system_requirements": [],
        "plugin_min_goobits_version": "1.4.0",
        "plugin_supported_languages": [language],
        "plugin_supported_platforms": ["linux", "darwin", "win32"],
        "plugin_provides_commands": [plugin_name] if plugin_type == "command" else [],
        "plugin_provides_completions": (
            [plugin_name] if plugin_type == "completion" else []
        ),
        "plugin_provides_hooks": [plugin_name] if plugin_type == "hook" else [],
        "plugin_tags": [plugin_type, language],
        "plugin_homepage": "",
        "plugin_repository": "",
        "plugin_config_enabled": True,
        "plugin_config_priority": 50,
        "plugin_config_settings": {},
        "plugin_security_sandbox": True,
        "plugin_security_max_time": 30,
        "plugin_security_max_memory": 104857600,
        "plugin_security_trusted": False,
        "plugin_hook_pre_install": "",
        "plugin_hook_post_install": "",
        "plugin_hook_pre_uninstall": "",
        "plugin_hook_post_uninstall": "",
        "source_config": "goobits.yaml",
    }

    # Update with provided kwargs

    context.update(kwargs)

    return context


# Global instances

_command_manager = None


def get_plugin_command_manager() -> PluginCommandManager:
    """Get the global plugin command manager."""

    global _command_manager

    if _command_manager is None:
        _command_manager = PluginCommandManager()

    return _command_manager
