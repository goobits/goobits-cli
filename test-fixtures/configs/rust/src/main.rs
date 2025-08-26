use clap::{Arg, Command, ArgMatches};
use std::process;
use anyhow::{Result, anyhow};

// Conditional imports based on detected features
#[cfg(feature = "colored")]
use colored::*;
#[cfg(feature = "indicatif")]
use indicatif::{ProgressBar, ProgressStyle};
mod hooks;
mod logger;
use logger::{setup_logging, info, error, set_context, create_command_context, log_error};

/// Enhanced error handling function
fn handle_error(err: anyhow::Error, context: &str, verbose: bool) -> ! {
    log_error(context, &err);
    
    if verbose {
        error(context, &format!("Details: {:#}", err), None);
    }
    
    // Check for specific error types to provide better exit codes
    if err.to_string().contains("not implemented") {
        process::exit(2); // Configuration/implementation error
    } else if err.to_string().contains("permission denied") {
        process::exit(3); // Permission error
    } else {
        process::exit(1); // General error
    }
}

fn main() {
    // Initialize logging as early as possible
    if let Err(e) = setup_logging() {
        eprintln!("Failed to initialize logging: {}", e);
        process::exit(1);
    }

    info("main", "Starting  CLI", None);

    let app = Command::new("")
        .version("1.0.0")
        .about("Test Rust CLI")
        .arg_required_else_help(true)        .arg(
            Arg::new("verbose")
                .long("verbose")
                .short('v')
                .help("Enable verbose error output and debugging information")
                .action(clap::ArgAction::SetTrue)
        )        .arg(
            Arg::new("interactive")
                .long("interactive")                .short('i')
                .help("None")                .action(clap::ArgAction::SetTrue)        )
        // Built-in upgrade subcommand
        .subcommand(
            Command::new("upgrade")
                .about("Upgrade Test Rust CLI to the latest version")
                .arg(
                    Arg::new("check")
                        .long("check")
                        .help("Check for updates without installing")
                        .action(clap::ArgAction::SetTrue)
                )
                .arg(
                    Arg::new("version")
                        .long("version")
                        .help("Install specific version")
                        .action(clap::ArgAction::Set)
                )
                .arg(
                    Arg::new("pre")
                        .long("pre")
                        .help("Include pre-release versions")
                        .action(clap::ArgAction::SetTrue)
                )
                .arg(
                    Arg::new("dry-run")
                        .long("dry-run")
                        .help("Show what would be done without doing it")
                        .action(clap::ArgAction::SetTrue)
                )
        )
        .subcommand(
            Command::new("hello")
                .about("Say hello")
        )
        .subcommand(
            Command::new("build")
                .about("Build something")
        )
        .subcommand(
            Command::new("build project")
                .about("Build a project")
        )
        .subcommand(
            Command::new("serve")
                .about("Start server")
        )
;

    let matches = app.get_matches();
    
    // Extract verbose flag for global error handling
    let verbose = matches.get_flag("verbose");
    match matches.subcommand() {
        Some(("upgrade", sub_matches)) => {
            // Built-in upgrade command implementation
            let context = create_command_context("upgrade", &[]);
            set_context(context);
            info("main", "Executing upgrade command", None);
            let package_name = "test-rust-cli";
            let command_name = "testrust";
            let display_name = "Test Rust CLI";
            
            // Get current version (simple fallback for Rust)
            let current_version = "1.0.0";
            println!("Current version: {}", current_version);
            
            let check_only = sub_matches.get_flag("check");
            let version = sub_matches.get_one::<String>("version");
            let pre = sub_matches.get_flag("pre");
            let dry_run = sub_matches.get_flag("dry-run");
            
            if check_only {
                info("upgrade", &format!("Checking for updates to {}...", display_name), None);
                info("upgrade", "Update check not yet implemented for Rust. Use without --check to upgrade.", None);
                return;
            }
            
            // Build the cargo install command
            let mut cmd_args = vec!["install"];
            
            if let Some(v) = version {
                cmd_args.push("--version");
                cmd_args.push(v);
            } else {
                cmd_args.push("--force"); // Force reinstall for upgrade
            }
            
            if pre {
                // Cargo doesn't have direct pre-release flag, but we can note it
                println!("Note: Cargo install will use the latest compatible version");
            }
            
            cmd_args.push(package_name);
            
            if dry_run {
                info("upgrade", &format!("Dry run - would execute: cargo {}", cmd_args.join(" ")), None);
                return;
            }
            
            // Execute upgrade
            info("upgrade", &format!("Upgrading {} with cargo...", display_name), None);
            
            let output = std::process::Command::new("cargo")
                .args(&cmd_args)
                .output();
                
            match output {
                Ok(result) => {
                    if result.status.success() {
                        println!("✅ {} upgraded successfully!", display_name);
                        println!("Run '{} --version' to verify the new version.", command_name);
                    } else {
                        eprintln!("❌ Upgrade failed with exit code {:?}", result.status.code());
                        process::exit(result.status.code().unwrap_or(1));
                    }
                }
                Err(e) => {
                    eprintln!("❌ Failed to execute cargo install: {}", e);
                    process::exit(1);
                }
            }
        }
        Some(("hello", sub_matches)) => {
            // Enhanced error handling for Rust commands with structured logging
            let context = create_command_context("hello", &[]);
            set_context(context);
            info("main", "Executing hello command", None);
            
            let hook_name = "on_hello";
            match hooks::on_hello(sub_matches) {
                Ok(_) => {
                    info("main", "Command hello executed successfully", None);
                }
                Err(e) => {
                    let error_context = format!("Command 'hello' execution");
                    
                    // Check for specific error types
                    if e.to_string().contains("not implemented") {
                        let enhanced_error = anyhow!(
                            "Hook function '{}' not implemented in src/hooks.rs. \
                            Please implement: pub fn {}(matches: &ArgMatches) -> Result<()>",
                            hook_name, hook_name
                        );
                        handle_error(enhanced_error, &error_context, verbose);
                    } else {
                        handle_error(e, &error_context, verbose);
                    }
                }
            }
        }
        Some(("build project", sub_matches)) => {
            // Enhanced error handling for Rust commands with structured logging
            let context = create_command_context("build project", &[]);
            set_context(context);
            info("main", "Executing build project command", None);
            
            let hook_name = "on_build_project";
            match hooks::on_build_project(sub_matches) {
                Ok(_) => {
                    info("main", "Command build project executed successfully", None);
                }
                Err(e) => {
                    let error_context = format!("Command 'build project' execution");
                    
                    // Check for specific error types
                    if e.to_string().contains("not implemented") {
                        let enhanced_error = anyhow!(
                            "Hook function '{}' not implemented in src/hooks.rs. \
                            Please implement: pub fn {}(matches: &ArgMatches) -> Result<()>",
                            hook_name, hook_name
                        );
                        handle_error(enhanced_error, &error_context, verbose);
                    } else {
                        handle_error(e, &error_context, verbose);
                    }
                }
            }
        }
        Some(("serve", sub_matches)) => {
            // Enhanced error handling for Rust commands with structured logging
            let context = create_command_context("serve", &[]);
            set_context(context);
            info("main", "Executing serve command", None);
            
            let hook_name = "on_serve";
            match hooks::on_serve(sub_matches) {
                Ok(_) => {
                    info("main", "Command serve executed successfully", None);
                }
                Err(e) => {
                    let error_context = format!("Command 'serve' execution");
                    
                    // Check for specific error types
                    if e.to_string().contains("not implemented") {
                        let enhanced_error = anyhow!(
                            "Hook function '{}' not implemented in src/hooks.rs. \
                            Please implement: pub fn {}(matches: &ArgMatches) -> Result<()>",
                            hook_name, hook_name
                        );
                        handle_error(enhanced_error, &error_context, verbose);
                    } else {
                        handle_error(e, &error_context, verbose);
                    }
                }
            }
        }
        _ => {
            info("main", "No subcommand provided. Use --help for available commands.", None);
            process::exit(1);
        }
    }
    
    info("main", "CLI execution completed successfully", None);
}