/**
 * Plugin system for Test Rust CLI
 * Auto-generated from test-rust-verification.yaml
 */

use std::collections::HashMap;
use std::path::{Path, PathBuf};
use std::sync::{Arc, Mutex};
use libloading::{Library, Symbol};
use serde::{Deserialize, Serialize};
use crate::config::AppConfig;
use crate::commands::{Command, CommandArgs};
use crate::errors::{CliResult, CLIError};

/// Plugin trait that all plugins must implement
pub trait Plugin: Send + Sync {
    /// Get the plugin name
    fn name(&self) -> &str;
    
    /// Get the plugin version
    fn version(&self) -> &str;
    
    /// Get the plugin description
    fn description(&self) -> &str;
    
    /// Get the plugin author
    fn author(&self) -> &str;
    
    /// Initialize the plugin with configuration
    fn init(&mut self, config: &AppConfig) -> CliResult<()>;
    
    /// Register commands that this plugin provides
    fn register_commands(&self) -> Vec<Box<dyn Command>>;
    
    /// Get plugin-specific configuration schema (optional)
    fn config_schema(&self) -> Option<serde_json::Value> {
        None
    }
    
    /// Handle plugin-specific configuration updates
    fn configure(&mut self, _config: &serde_json::Value) -> CliResult<()> {
        Ok(())
    }
    
    /// Cleanup when plugin is unloaded
    fn cleanup(&mut self) -> CliResult<()> {
        Ok(())
    }
}

/// Plugin metadata loaded from plugin manifest
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PluginMetadata {
    pub name: String,
    pub version: String,
    pub description: String,
    pub author: String,
    pub entry_point: String,
    pub dependencies: Vec<String>,
    pub min_cli_version: Option<String>,
    pub config_schema: Option<serde_json::Value>,
}

/// Dynamically loaded plugin from external library
pub struct DynamicPlugin {
    #[allow(dead_code)]
    library: Library,
    plugin: Box<dyn Plugin>,
    metadata: PluginMetadata,
}

impl DynamicPlugin {
    /// Load a plugin from a dynamic library
    pub fn load(library_path: &Path, metadata: PluginMetadata) -> CliResult<Self> {
        unsafe {
            let library = Library::new(library_path)
                .map_err(|e| CLIError::plugin(&metadata.name, format!("Failed to load library: {}", e)))?;
            let create_plugin: Symbol<fn() -> Box<dyn Plugin>> = library
                .get(metadata.entry_point.as_bytes())
                .map_err(|e| CLIError::plugin(&metadata.name, format!("Failed to find entry point '{}': {}", metadata.entry_point, e)))?;
            
            let plugin = create_plugin();
            
            Ok(Self {
                library,
                plugin,
                metadata,
            })
        }
    }
    
    /// Get plugin metadata
    pub fn metadata(&self) -> &PluginMetadata {
        &self.metadata
    }
    
    /// Get mutable reference to the plugin
    pub fn plugin_mut(&mut self) -> &mut dyn Plugin {
        self.plugin.as_mut()
    }
    
    /// Get immutable reference to the plugin
    pub fn plugin(&self) -> &dyn Plugin {
        self.plugin.as_ref()
    }
}

/// Built-in plugins that come with the CLI
pub struct BuiltinPlugins;

impl BuiltinPlugins {
    /// Get all built-in plugins
    pub fn all() -> Vec<Box<dyn Plugin>> {
        vec![
            Box::new(CorePlugin::new()),
            Box::new(ConfigPlugin::new()),
            
        ]
    }
}

/// Core plugin providing essential functionality
pub struct CorePlugin {
    name: String,
    version: String,
}

impl CorePlugin {
    pub fn new() -> Self {
        Self {
            name: "core".to_string(),
            version: "2.0.0-beta.1".to_string(),
        }
    }
}

impl Plugin for CorePlugin {
    fn name(&self) -> &str {
        &self.name
    }
    
    fn version(&self) -> &str {
        &self.version
    }
    
    fn description(&self) -> &str {
        "Core functionality for Test Rust CLI"
    }
    
    fn author(&self) -> &str {
        "goobits-cli"
    }
    
    fn init(&mut self, _config: &AppConfig) -> CliResult<()> {
        Ok(())
    }
    
    fn register_commands(&self) -> Vec<Box<dyn Command>> {
        vec![
            // Core commands are handled by the main CLI, not as plugin commands
        ]
    }
}

/// Configuration management plugin
pub struct ConfigPlugin {
    name: String,
    version: String,
}

impl ConfigPlugin {
    pub fn new() -> Self {
        Self {
            name: "config".to_string(),
            version: "2.0.0-beta.1".to_string(),
        }
    }
}

impl Plugin for ConfigPlugin {
    fn name(&self) -> &str {
        &self.name
    }
    
    fn version(&self) -> &str {
        &self.version
    }
    
    fn description(&self) -> &str {
        "Configuration management commands"
    }
    
    fn author(&self) -> &str {
        "goobits-cli"
    }
    
    fn init(&mut self, _config: &AppConfig) -> CliResult<()> {
        Ok(())
    }
    
    fn register_commands(&self) -> Vec<Box<dyn Command>> {
        vec![
            Box::new(ConfigGetCommand::new()),
            Box::new(ConfigSetCommand::new()),
            Box::new(ConfigListCommand::new()),
        ]
    }
}



/// Plugin command implementations for config management
pub struct ConfigGetCommand;
pub struct ConfigSetCommand;
pub struct ConfigListCommand;

impl ConfigGetCommand {
    pub fn new() -> Self {
        Self
    }
}

impl Command for ConfigGetCommand {
    fn name(&self) -> &str {
        "config-get"
    }
    
    fn description(&self) -> &str {
        "Get a configuration value"
    }
    
    fn execute(&self, args: &CommandArgs) -> CliResult<()> {
        if let Some(key) = args.get_arg(0) {
            let config = &args.config;
            if let Some(value) = config.get_custom(key) {
                println!("{}", value);
            } else {
                println!("Configuration key '{}' not found", key);
            }
        } else {
            return Err(CLIError::plugin("built-in", "Configuration key is required"));
        }
        Ok(())
    }
    
    fn validate(&self, args: &CommandArgs) -> CliResult<()> {
        if args.get_arg(0).is_none() {
            return Err(CLIError::plugin("built-in", "Configuration key is required"));
        }
        Ok(())
    }
}

impl ConfigSetCommand {
    pub fn new() -> Self {
        Self
    }
}

impl Command for ConfigSetCommand {
    fn name(&self) -> &str {
        "config-set"
    }
    
    fn description(&self) -> &str {
        "Set a configuration value"
    }
    
    fn execute(&self, args: &CommandArgs) -> CliResult<()> {
        let key = args.get_arg(0)
            .ok_or_else(|| CLIError::plugin("built-in", "Configuration key is required"))?;
        let value = args.get_arg(1)
            .ok_or_else(|| CLIError::plugin("built-in", "Configuration value is required"))?;
        
        let mut config = args.config.clone();
        config.set_custom(key.clone(), value.clone());
        config.save()?;
        
        println!("Set {} = {}", key, value);
        Ok(())
    }
    
    fn validate(&self, args: &CommandArgs) -> CliResult<()> {
        if args.get_arg(0).is_none() {
            return Err(CLIError::plugin("built-in", "Configuration key is required"));
        }
        if args.get_arg(1).is_none() {
            return Err(CLIError::plugin("built-in", "Configuration value is required"));
        }
        Ok(())
    }
}

impl ConfigListCommand {
    pub fn new() -> Self {
        Self
    }
}

impl Command for ConfigListCommand {
    fn name(&self) -> &str {
        "config-list"
    }
    
    fn description(&self) -> &str {
        "List all configuration values"
    }
    
    fn execute(&self, args: &CommandArgs) -> CliResult<()> {
        let config = &args.config;
        
        println!("Configuration:");
        for (key, value) in &config.preferences.custom {
            println!("  {} = {}", key, value);
        }
        
        println!("\nAliases:");
        for (alias, command) in &config.preferences.aliases {
            println!("  {} -> {}", alias, command);
        }
        
        Ok(())
    }
}

/// Plugin registry managing all loaded plugins
pub struct PluginRegistry {
    builtin_plugins: Vec<Box<dyn Plugin>>,
    dynamic_plugins: Vec<DynamicPlugin>,
    commands: HashMap<String, Box<dyn Command>>,
}

impl PluginRegistry {
    /// Create a new plugin registry
    pub fn new() -> Self {
        Self {
            builtin_plugins: Vec::new(),
            dynamic_plugins: Vec::new(),
            commands: HashMap::new(),
        }
    }
    
    /// Initialize the registry with built-in plugins
    pub fn init(&mut self, config: &AppConfig) -> CliResult<()> {
        // Load built-in plugins
        let mut builtin_plugins = BuiltinPlugins::all();
        for plugin in &mut builtin_plugins {
            plugin.init(config)?;
            
            // Register commands from this plugin
            let commands = plugin.register_commands();
            for command in commands {
                self.commands.insert(command.name().to_string(), command);
            }
        }
        self.builtin_plugins = builtin_plugins;
        
        // Load dynamic plugins from plugins directory
        self.load_dynamic_plugins(config)?;
        
        Ok(())
    }
    
    /// Load dynamic plugins from the plugins directory
    fn load_dynamic_plugins(&mut self, config: &AppConfig) -> CliResult<()> {
        let plugins_dir = AppConfig::config_dir()?.join("plugins");
        if !plugins_dir.exists() {
            return Ok(());
        }
        
        // Look for plugin manifests
        for entry in std::fs::read_dir(&plugins_dir)? {
            let entry = entry?;
            let path = entry.path();
            
            if path.is_dir() {
                let manifest_path = path.join("plugin.json");
                if manifest_path.exists() {
                    if let Err(e) = self.load_plugin_from_manifest(&manifest_path, config) {
                        eprintln!("Warning: Failed to load plugin from {}: {}", path.display(), e);
                    }
                }
            }
        }
        
        Ok(())
    }
    
    /// Load a plugin from its manifest file
    fn load_plugin_from_manifest(&mut self, manifest_path: &Path, config: &AppConfig) -> CliResult<()> {
        let content = std::fs::read_to_string(manifest_path)?;
        let metadata: PluginMetadata = serde_json::from_str(&content)?;
        
        // Check CLI version compatibility
        if let Some(min_version) = &metadata.min_cli_version {
            // TODO: Implement version checking
            eprintln!("Note: Plugin {} requires CLI version {}", metadata.name, min_version);
        }
        
        // Find the plugin library
        let plugin_dir = manifest_path.parent().unwrap();
        let library_path = plugin_dir.join(&metadata.entry_point);
        
        if !library_path.exists() {
            return Err(CLIError::plugin("dynamic", format!("Plugin library not found: {}", library_path.display())));
        }
        
        // Load the dynamic plugin
        let mut dynamic_plugin = DynamicPlugin::load(&library_path, metadata)?;
        dynamic_plugin.plugin_mut().init(config)?;
        
        // Register commands from this plugin
        let commands = dynamic_plugin.plugin().register_commands();
        for command in commands {
            self.commands.insert(command.name().to_string(), command);
        }
        
        self.dynamic_plugins.push(dynamic_plugin);
        
        Ok(())
    }
    
    /// Get all available plugin names
    pub fn plugin_names(&self) -> Vec<String> {
        let mut names = Vec::new();
        
        for plugin in &self.builtin_plugins {
            names.push(plugin.name().to_string());
        }
        
        for plugin in &self.dynamic_plugins {
            names.push(plugin.plugin().name().to_string());
        }
        
        names
    }
    
    /// Get a command by name
    pub fn get_command(&self, name: &str) -> Option<&dyn Command> {
        self.commands.get(name).map(|cmd| cmd.as_ref())
    }
    
    /// Execute a plugin command
    pub fn execute_command(&self, name: &str, args: &CommandArgs) -> CliResult<()> {
        if let Some(command) = self.get_command(name) {
            command.validate(args)?;
            command.execute(args)
        } else {
            return Err(CLIError::plugin("registry", format!("Unknown plugin command: {}", name)))
        }
    }
    
    /// List all available commands from plugins
    pub fn list_commands(&self) -> Vec<(&str, &str)> {
        self.commands
            .values()
            .map(|cmd| (cmd.name(), cmd.description()))
            .collect()
    }
    
    /// Get plugin information
    pub fn get_plugin_info(&self, name: &str) -> Option<PluginInfo> {
        // Check built-in plugins
        for plugin in &self.builtin_plugins {
            if plugin.name() == name {
                return Some(PluginInfo {
                    name: plugin.name().to_string(),
                    version: plugin.version().to_string(),
                    description: plugin.description().to_string(),
                    author: plugin.author().to_string(),
                    plugin_type: "builtin".to_string(),
                    commands: plugin.register_commands().iter().map(|cmd| cmd.name().to_string()).collect(),
                });
            }
        }
        
        // Check dynamic plugins
        for plugin in &self.dynamic_plugins {
            if plugin.plugin().name() == name {
                return Some(PluginInfo {
                    name: plugin.plugin().name().to_string(),
                    version: plugin.plugin().version().to_string(),
                    description: plugin.plugin().description().to_string(),
                    author: plugin.plugin().author().to_string(),
                    plugin_type: "dynamic".to_string(),
                    commands: plugin.plugin().register_commands().iter().map(|cmd| cmd.name().to_string()).collect(),
                });
            }
        }
        
        None
    }
    
    /// Unload all plugins and cleanup
    pub fn cleanup(&mut self) -> CliResult<()> {
        for plugin in &mut self.builtin_plugins {
            plugin.cleanup()?;
        }
        
        for plugin in &mut self.dynamic_plugins {
            plugin.plugin_mut().cleanup()?;
        }
        
        Ok(())
    }
}

/// Plugin information for display
#[derive(Debug, Clone, Serialize)]
pub struct PluginInfo {
    pub name: String,
    pub version: String,
    pub description: String,
    pub author: String,
    pub plugin_type: String,
    pub commands: Vec<String>,
}

/// Global plugin registry instance
static PLUGIN_REGISTRY: Mutex<Option<PluginRegistry>> = Mutex::new(None);

/// Initialize the global plugin registry
pub fn initialize_plugins(config: &AppConfig) -> CliResult<()> {
    let mut registry = PluginRegistry::new();
    registry.init(config)?;
    
    let mut global_registry = PLUGIN_REGISTRY.lock().unwrap();
    *global_registry = Some(registry);
    
    Ok(())
}

/// Execute a plugin command using the global registry
pub fn execute_plugin_command(command: &str, args: &CommandArgs) -> CliResult<()> {
    let global_registry = PLUGIN_REGISTRY.lock().unwrap();
    if let Some(ref registry) = *global_registry {
        registry.execute_command(command, args)
    } else {
        return Err(CLIError::plugin("registry", "Plugin registry not initialized"))
    }
}

/// Get plugin information
pub fn get_plugin_info(name: &str) -> Option<PluginInfo> {
    let global_registry = PLUGIN_REGISTRY.lock().unwrap();
    if let Some(ref registry) = *global_registry {
        registry.get_plugin_info(name)
    } else {
        None
    }
}

/// List all available plugins
pub fn list_plugins() -> Vec<String> {
    let global_registry = PLUGIN_REGISTRY.lock().unwrap();
    if let Some(ref registry) = *global_registry {
        registry.plugin_names()
    } else {
        Vec::new()
    }
}

/// List all plugin commands
pub fn list_plugin_commands() -> Vec<(String, String)> {
    let global_registry = PLUGIN_REGISTRY.lock().unwrap();
    if let Some(ref registry) = *global_registry {
        registry.list_commands().into_iter().map(|(name, desc)| (name.to_string(), desc.to_string())).collect()
    } else {
        Vec::new()
    }
}

/// Cleanup plugins
pub fn cleanup_plugins() -> CliResult<()> {
    let mut global_registry = PLUGIN_REGISTRY.lock().unwrap();
    if let Some(ref mut registry) = *global_registry {
        registry.cleanup()?;
    }
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::config::AppConfig;
    
    #[test]
    fn test_builtin_plugins() {
        let plugins = BuiltinPlugins::all();
        assert!(!plugins.is_empty());
        
        // Core plugin should be present
        let core_plugin = plugins.iter().find(|p| p.name() == "core");
        assert!(core_plugin.is_some());
    }
    
    #[test]
    fn test_plugin_registry() {
        let mut registry = PluginRegistry::new();
        let config = AppConfig::default();
        
        assert!(registry.init(&config).is_ok());
        assert!(!registry.plugin_names().is_empty());
    }
    
    #[test]
    fn test_config_commands() {
        let config = AppConfig::default();
        let mut options = HashMap::new();
        
        let args = CommandArgs {
            command: "config-list".to_string(),
            subcommand: None,
            args: vec![],
            options,
            config,
        };
        
        let cmd = ConfigListCommand::new();
        assert!(cmd.execute(&args).is_ok());
    }
}