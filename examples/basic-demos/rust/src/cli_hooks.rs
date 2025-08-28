// Hook implementations for Multi-Language Demo CLI
//
// This file contains the business logic for your CLI commands.
// Implement the hook functions below to handle your CLI commands.
//
// IMPORTANT: Hook names must use snake_case with 'on_' prefix
// Example:
// - Command 'hello' -> Hook function 'on_hello'
// - Command 'hello-world' -> Hook function 'on_hello_world'

use clap::ArgMatches;
use anyhow::Result;

/// Greet someone with style
pub fn on_greet(matches: &ArgMatches) -> Result<()> {
    // Add your business logic here
    println!("Executing greet command");
    // Access options
    if let Some(style) = matches.get_one::<String>("style") {
        println!("style: {}", style);
    }
    if let Some(count) = matches.get_one::<String>("count") {
        println!("count: {}", count);
    }
    if let Some(uppercase) = matches.get_one::<String>("uppercase") {
        println!("uppercase: {}", uppercase);
    }
    if let Some(language) = matches.get_one::<String>("language") {
        println!("language: {}", language);
    }
    
    Ok(())
}/// Display system and environment information
pub fn on_info(matches: &ArgMatches) -> Result<()> {
    // Add your business logic here
    println!("Executing info command");
    // Access options
    if let Some(format) = matches.get_one::<String>("format") {
        println!("format: {}", format);
    }
    if let Some(verbose) = matches.get_one::<String>("verbose") {
        println!("verbose: {}", verbose);
    }
    if let Some(sections) = matches.get_one::<String>("sections") {
        println!("sections: {}", sections);
    }
    
    Ok(())
}