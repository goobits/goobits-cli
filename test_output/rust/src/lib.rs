/**
 * Auto-generated from test_rust_valid.yaml
 * Library module for TestRustCLI
 */

use anyhow::Result;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::path::PathBuf;

pub mod config;
pub mod commands;
pub mod utils;
pub mod hooks;
pub mod plugins;
pub mod styling;

// Re-export commonly used types
pub use config::AppConfig;
pub use commands::{Command, CommandArgs, CommandRegistry};
pub use hooks::{HookContext, ExecutionPhase};
pub use plugins::{Plugin, PluginInfo};
pub use styling::{StyledOutput, ColorTheme};

/// Library version
pub const VERSION: &str = "1.0.0";

/// Configuration structure for the CLI application
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Config {
    /// Application configuration directory
    pub config_dir: PathBuf,
    /// User-specific settings
    pub settings: HashMap<String, String>,
    /// Feature flags
    pub features: HashMap<String, bool>,
}

impl Config {
    /// Load configuration from default locations
    pub fn load() -> Result<Self> {
        let config_dir = Self::get_config_dir()?;
        let config_file = config_dir.join("config.yaml");
        
        if config_file.exists() {
            let content = std::fs::read_to_string(&config_file)?;
            let config: Config = serde_yaml::from_str(&content)?;
            Ok(config)
        } else {
            // Create default configuration
            let config = Self::default_config(config_dir);
            config.save()?;
            Ok(config)
        }
    }
    
    /// Save configuration to file
    pub fn save(&self) -> Result<()> {
        std::fs::create_dir_all(&self.config_dir)?;
        let config_file = self.config_dir.join("config.yaml");
        let content = serde_yaml::to_string(self)?;
        std::fs::write(config_file, content)?;
        Ok(())
    }
    
    /// Get the configuration directory path
    fn get_config_dir() -> Result<PathBuf> {
        let home_dir = dirs::home_dir()
            .ok_or_else(|| anyhow::anyhow!("Could not determine home directory"))?;
        
        Ok(home_dir.join(".config").join("test-rust-cli"))
    }
    
    /// Create default configuration
    fn default_config(config_dir: PathBuf) -> Self {
        let mut settings = HashMap::new();
        settings.insert("version".to_string(), VERSION.to_string());
        settings.insert("auto_update".to_string(), "false".to_string());
        
        let mut features = HashMap::new();
        features.insert("colored_output".to_string(), true);
        features.insert("progress_bars".to_string(), true);
        
        Self {
            config_dir,
            settings,
            features,
        }
    }
    
    /// Get a setting value
    pub fn get_setting(&self, key: &str) -> Option<&String> {
        self.settings.get(key)
    }
    
    /// Set a setting value
    pub fn set_setting(&mut self, key: String, value: String) {
        self.settings.insert(key, value);
    }
    
    /// Check if a feature is enabled
    pub fn is_feature_enabled(&self, feature: &str) -> bool {
        self.features.get(feature).copied().unwrap_or(false)
    }
    
    /// Enable or disable a feature
    pub fn set_feature(&mut self, feature: String, enabled: bool) {
        self.features.insert(feature, enabled);
    }
}

/// Plugin trait for extending CLI functionality
pub trait Plugin {
    /// Get the plugin name
    fn name(&self) -> &str;
    
    /// Get the plugin version
    fn version(&self) -> &str;
    
    /// Initialize the plugin
    fn init(&mut self, config: &Config) -> Result<()>;
    
    /// Register commands with the CLI
    fn register_commands(&self) -> Vec<PluginCommand>;
}

/// Command provided by a plugin
#[derive(Debug, Clone)]
pub struct PluginCommand {
    pub name: String,
    pub description: String,
    pub handler: fn(&[String]) -> Result<()>,
}

/// Hook system for command execution
pub struct HookRegistry {
    hooks: HashMap<String, Vec<Box<dyn Fn(&Args) -> Result<()>>>>,
}

impl HookRegistry {
    pub fn new() -> Self {
        Self {
            hooks: HashMap::new(),
        }
    }
    
    /// Register a hook for a command
    pub fn register_hook<F>(&mut self, command: String, hook: F)
    where
        F: Fn(&Args) -> Result<()> + 'static,
    {
        self.hooks.entry(command).or_insert_with(Vec::new).push(Box::new(hook));
    }
    
    /// Execute hooks for a command
    pub fn execute_hooks(&self, command: &str, args: &Args) -> Result<()> {
        if let Some(hooks) = self.hooks.get(command) {
            for hook in hooks {
                hook(args)?;
            }
        }
        Ok(())
    }
}

/// Execution context for commands
#[derive(Debug, Clone)]
pub struct ExecutionContext {
    pub config: Config,
    pub working_dir: PathBuf,
    pub start_time: std::time::Instant,
}

impl ExecutionContext {
    pub fn new(config: Config) -> Result<Self> {
        Ok(Self {
            config,
            working_dir: std::env::current_dir()?,
            start_time: std::time::Instant::now(),
        })
    }
    
    /// Get elapsed time since command started
    pub fn elapsed(&self) -> std::time::Duration {
        self.start_time.elapsed()
    }
}

/// Arguments structure for command execution
#[derive(Debug, Clone)]
pub struct Args {
    pub command_name: String,
    
    pub raw_args: HashMap<String, String>,
}

/// Base trait for command implementations
pub trait CommandTrait {
    fn name(&self) -> &str;
    fn description(&self) -> &str;
    fn execute(&self, args: &Args, context: &ExecutionContext) -> Result<()>;
}

/// Managed command trait for lifecycle-managed commands
pub trait ManagedCommand: CommandTrait {
    fn validate(&self, args: &Args) -> Result<()>;
    fn setup(&mut self, context: &ExecutionContext) -> Result<()>;
    fn cleanup(&mut self) -> Result<()>;
}

#[cfg(test)]
mod tests {
    use super::*;
    use tempfile::TempDir;
    
    #[test]
    fn test_config_creation() {
        let temp_dir = TempDir::new().unwrap();
        let config = Config::default_config(temp_dir.path().to_path_buf());
        
        assert!(config.is_feature_enabled("colored_output"));
        assert!(config.is_feature_enabled("progress_bars"));
        assert_eq!(config.get_setting("version"), Some(&VERSION.to_string()));
    }
    
    #[test]
    fn test_hook_registry() {
        let mut registry = HookRegistry::new();
        
        registry.register_hook("test".to_string(), |_args| {
            Ok(())
        });
        
        let args = Args {
            command_name: "test".to_string(),
            
            raw_args: HashMap::new(),
        };
        
        assert!(registry.execute_hooks("test", &args).is_ok());
    }
}