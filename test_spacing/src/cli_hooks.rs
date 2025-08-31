// Hook implementations for Spacing Test CLI
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

/// Say hello with spacing
pub fn on_hello(matches: &ArgMatches) -> Result<()> {
    // Add your business logic here
    println!("Executing hello command");
    // Access options
    if let Some(verbose) = matches.get_one::<String>("verbose") {
        println!("verbose: {}", verbose);
    }
    
    Ok(())
}