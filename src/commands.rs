/**
 * Commands module for Test Rust CLI
 * Auto-generated from test-rust-verification.yaml
 */

use crate::errors::{CliResult, CommandError, CLIError};
use crate::config::AppConfig;
use std::collections::HashMap;

/// Base trait for all commands
pub trait Command: Send + Sync {
    /// Get the command name
    fn name(&self) -> &str;
    
    /// Get the command description
    fn description(&self) -> &str;
    
    /// Execute the command with given arguments
    fn execute(&self, args: &CommandArgs) -> CliResult<()>;
    
    /// Validate command arguments before execution
    fn validate(&self, args: &CommandArgs) -> CliResult<()> {
        // Default implementation - no validation
        Ok(())
    }
}

/// Command arguments structure
#[derive(Debug, Clone)]
pub struct CommandArgs {
    /// Command name being executed
    pub command: String,
    /// Subcommand if applicable
    pub subcommand: Option<String>,
    /// Positional arguments
    pub args: Vec<String>,
    /// Flag and option values
    pub options: HashMap<String, String>,
    /// Application configuration
    pub config: AppConfig,
}

impl CommandArgs {
    /// Get a positional argument by index
    pub fn get_arg(&self, index: usize) -> Option<&String> {
        self.args.get(index)
    }
    
    /// Get an option value by name
    pub fn get_option(&self, name: &str) -> Option<&String> {
        self.options.get(name)
    }
    
    /// Check if a flag is set
    pub fn has_flag(&self, name: &str) -> bool {
        self.options.get(name).map(|v| v == "true").unwrap_or(false)
    }
    
    /// Get option as integer
    pub fn get_option_as_int(&self, name: &str) -> Option<i32> {
        self.get_option(name)?.parse().ok()
    }
    
    /// Get option with default value
    pub fn get_option_or(&self, name: &str, default: &str) -> String {
        self.get_option(name).cloned().unwrap_or_else(|| default.to_string())
    }
}

/// Command registry for managing available commands
pub struct CommandRegistry {
    commands: HashMap<String, Box<dyn Command>>,
}

impl CommandRegistry {
    /// Create a new command registry
    pub fn new() -> Self {
        Self {
            commands: HashMap::new(),
        }
    }
    
    /// Register a command
    pub fn register<C: Command + 'static>(&mut self, command: C) {
        self.commands.insert(command.name().to_string(), Box::new(command));
    }
    
    /// Execute a command by name
    pub fn execute(&self, name: &str, args: &CommandArgs) -> CliResult<()> {
        if let Some(command) = self.commands.get(name) {
            command.validate(args)?;
            command.execute(args)
        } else {
            let available: Vec<String> = self.command_names().iter().map(|s| s.to_string()).collect();
            Err(CLIError::command_not_found(name, available))
        }
    }
    
    /// Get available command names
    pub fn command_names(&self) -> Vec<&String> {
        self.commands.keys().collect()
    }
    
    /// Check if a command exists
    pub fn has_command(&self, name: &str) -> bool {
        self.commands.contains_key(name)
    }
}

/// Built-in commands implementations


pub struct HelloCommand;

impl Command for HelloCommand {
    fn name(&self) -> &str {
        "hello"
    }
    
    fn description(&self) -> &str {
        "Simple hello command"
    }
    
    fn execute(&self, args: &CommandArgs) -> CliResult<()> {
        println!("🚀 Executing hello command...");
        
        
        // Process positional arguments
        
        
        let name = args.get_arg(0)
            .ok_or_else(|| CLIError::validation("name", "", "Missing required argument"))?;
        println!("  name: {}", name);
        
        
        
        
        
        // Process options
        
        
        if args.has_flag("--loud") {
            println!("  --loud: enabled");
        }
        
        
        
        
        // TODO: Implement actual hello command logic here
        // This is a placeholder implementation
        
        println!("✅ Hello command completed successfully!");
        Ok(())
    }
    
    fn validate(&self, args: &CommandArgs) -> CliResult<()> {
        
        // Validate required arguments
        
        
        if args.get_arg(0).is_none() {
            return Err(CLIError::validation("name", "", "Missing required argument"));
        }
        
        
        
        
        
        
        // Validate options
        
        
        
        
        
        Ok(())
    }
}





/// Initialize and return command registry with all built-in commands
pub fn create_command_registry() -> CommandRegistry {
    let mut registry = CommandRegistry::new();
    
    
    
    registry.register(HelloCommand);
    
    
    
    
    
    registry
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_command_args() {
        let config = AppConfig::default();
        let mut options = HashMap::new();
        options.insert("verbose".to_string(), "true".to_string());
        options.insert("count".to_string(), "42".to_string());
        
        let args = CommandArgs {
            command: "test".to_string(),
            subcommand: None,
            args: vec!["arg1".to_string(), "arg2".to_string()],
            options,
            config,
        };
        
        assert_eq!(args.get_arg(0), Some(&"arg1".to_string()));
        assert_eq!(args.get_arg(1), Some(&"arg2".to_string()));
        assert_eq!(args.get_arg(2), None);
        
        assert!(args.has_flag("verbose"));
        assert!(!args.has_flag("quiet"));
        
        assert_eq!(args.get_option_as_int("count"), Some(42));
        assert_eq!(args.get_option_or("missing", "default"), "default");
    }
    
    #[test]
    fn test_command_registry() {
        let registry = create_command_registry();
        
        
        
        assert!(registry.has_command("hello"));
        
        
        
        
        
        let names = registry.command_names();
        assert!(!names.is_empty());
    }
}