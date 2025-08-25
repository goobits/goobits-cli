//! Hook implementations for Demo Rust CLI
//! 
//! This file contains the business logic for your CLI commands.
//! Implement the hook functions below to handle your CLI commands.
//! 
//! Each command in your CLI corresponds to a hook function.

use clap::ArgMatches;
use anyhow::{Result, anyhow};

/// Hook function for 'greet' command
/// Greet someone with style
pub fn on_greet(matches: &ArgMatches) -> Result<()> {
    // Add your business logic here
    println!("Executing greet command...");
    
    // Extract arguments
    if let Some(name) = matches.get_one::<String>("name") {
        println!("name: {}", name);
    }
    if let Some(message) = matches.get_one::<String>("message") {
        println!("message: {}", message);
    }
    
    // Extract options
    if let Some(style) = matches.get_one::<String>("style") {
        println!("style: {}", style);
    }
    if let Some(count) = matches.get_one::<String>("count") {
        println!("count: {}", count);
    }
    let uppercase = matches.get_flag("uppercase");
    println!("uppercase: {}", uppercase);
    if let Some(language) = matches.get_one::<String>("language") {
        println!("language: {}", language);
    }
    
    // Return Ok(()) for success, Err(...) for error
    Ok(())
}

/// Hook function for 'info' command
/// Display system and environment information
pub fn on_info(matches: &ArgMatches) -> Result<()> {
    // Add your business logic here
    println!("Executing info command...");
    
    // Extract options
    if let Some(format) = matches.get_one::<String>("format") {
        println!("format: {}", format);
    }
    let verbose = matches.get_flag("verbose");
    println!("verbose: {}", verbose);
    if let Some(sections) = matches.get_one::<String>("sections") {
        println!("sections: {}", sections);
    }
    
    // Return Ok(()) for success, Err(...) for error
    Ok(())
}


/// Simple hook manager for compatibility with other templates
pub struct HookManager;

impl HookManager {
    /// Create a new hook manager
    pub fn new() -> Self {
        Self
    }
    
    /// Execute a hook by name
    pub fn execute_hook(&self, name: &str, matches: &ArgMatches) -> Result<()> {
        match name {

            "on_greet" => on_greet(matches),
            "on_info" => on_info(matches),
            _ => Err(anyhow::anyhow!("Unknown hook: {}", name)),
        }
    }
}

impl Default for HookManager {
    fn default() -> Self {
        Self::new()
    }
}

// Add any utility functions or structures here