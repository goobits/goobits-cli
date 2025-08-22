//! CLI module for nested-demo
//!
//! This module contains the CLI command structure and argument parsing logic.

use clap::{Arg, Command, ArgMatches, value_parser};
use anyhow::Result;
use crate::hooks::HookManager;
use crate::errors::{CliError, ExitCode};

/// Build the main CLI application
pub fn build_cli() -> Command {
    Command::new("demo")
        .version(crate::VERSION)
        .about("Demonstration of deep nested command capabilities")
        .author("Unknown Author")
        .subcommand(
            Command::new("simple")
                .about("No description provided")                .arg(
                    Arg::new("verbose")
                        .long("verbose")
                        .help("No description provided")                        .action(clap::ArgAction::SetTrue)                )        )        .subcommand(
            Command::new("database")
                .about("No description provided")        )        .subcommand(
            Command::new("api")
                .about("No description provided")        )        .arg(
            Arg::new("verbose")
                .long("verbose")
                .short('v')
                .help("Enable verbose output")
                .action(clap::ArgAction::SetTrue)
        )
}

/// Execute a CLI command using the hook system
pub fn execute_command(matches: &ArgMatches, hook_manager: &HookManager) -> Result<()> {
    match matches.subcommand() {
        Some(("simple", sub_matches)) => {
            let hook_name = "on_simple";
            hook_manager.execute_hook(hook_name, sub_matches)
                .map_err(|e| CliError::new(format!("Failed to execute {}: {}", hook_name, e), ExitCode::GeneralError))?;
        }        Some(("database", sub_matches)) => {
            let hook_name = "on_database";
            hook_manager.execute_hook(hook_name, sub_matches)
                .map_err(|e| CliError::new(format!("Failed to execute {}: {}", hook_name, e), ExitCode::GeneralError))?;
        }        Some(("api", sub_matches)) => {
            let hook_name = "on_api";
            hook_manager.execute_hook(hook_name, sub_matches)
                .map_err(|e| CliError::new(format!("Failed to execute {}: {}", hook_name, e), ExitCode::GeneralError))?;
        }        _ => {
            println!("No command specified. Use --help for available commands.");
        }
    }
    
    Ok(())
}