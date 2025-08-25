use clap::{Arg, Command, ArgMatches};
use std::process;
use anyhow::{Result, anyhow};

mod hooks;
/// Enhanced error handling function
fn handle_error(error: anyhow::Error, context: &str, verbose: bool) -> ! {
    eprintln!("❌ {}: {}", context, error);
    
    if verbose {
        eprintln!("Details: {:#}", error);
    }
    
    // Check for specific error types to provide better exit codes
    if error.to_string().contains("not implemented") {
        process::exit(2); // Configuration/implementation error
    } else if error.to_string().contains("permission denied") {
        process::exit(3); // Permission error
    } else {
        process::exit(1); // General error
    }
}

fn main() {
    let app = Command::new("")
        .version("None")
        .about("None")
        .arg_required_else_help(true)
        .arg(
            Arg::new("verbose")
                .long("verbose")
                .short('v')
                .help("Enable verbose error output and debugging information")
                .action(clap::ArgAction::SetTrue)
        )        // Built-in upgrade subcommand
        .subcommand(
            Command::new("upgrade")
                .about("Upgrade Demo Rust CLI to the latest version")
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
            Command::new("greet")
                .about("Greet someone with style")
                .arg(
                    Arg::new("name")
                        .help("No description")                        .required(true)
                        .action(clap::ArgAction::Set)
                )
                .arg(
                    Arg::new("message")
                        .help("No description")                        .action(clap::ArgAction::Set)
                )
                .arg(
                    Arg::new("style")
                        .long("style")                        .short('s')
                        .help("Greeting style")                        .action(clap::ArgAction::Set)
                )
                .arg(
                    Arg::new("count")
                        .long("count")                        .short('c')
                        .help("Repeat greeting N times")                        .action(clap::ArgAction::Set)
                )
                .arg(
                    Arg::new("uppercase")
                        .long("uppercase")                        .short('u')
                        .help("Convert to uppercase")                        .action(clap::ArgAction::Set)
                )
                .arg(
                    Arg::new("language")
                        .long("language")                        .short('l')
                        .help("Language code")                        .action(clap::ArgAction::Set)
                )
        )
        .subcommand(
            Command::new("info")
                .about("Display system and environment information")
                .arg(
                    Arg::new("format")
                        .long("format")                        .short('f')
                        .help("Output format")                        .action(clap::ArgAction::Set)
                )
                .arg(
                    Arg::new("verbose")
                        .long("verbose")                        .short('v')
                        .help("Show detailed information")                        .action(clap::ArgAction::Set)
                )
                .arg(
                    Arg::new("sections")
                        .long("sections")                        .short('s')
                        .help("Comma-separated sections to show")                        .action(clap::ArgAction::Set)
                )
        )
;

    let matches = app.get_matches();
    
    // Extract verbose flag for global error handling
    let verbose = matches.get_flag("verbose");
    match matches.subcommand() {
        Some(("upgrade", sub_matches)) => {
            // Built-in upgrade command implementation
            let package_name = "demo-rust-cli";
            let command_name = "demo_rust";
            let display_name = "Demo Rust CLI";
            
            // Get current version (simple fallback for Rust)
            let current_version = "None";
            println!("Current version: {}", current_version);
            
            let check_only = sub_matches.get_flag("check");
            let version = sub_matches.get_one::<String>("version");
            let pre = sub_matches.get_flag("pre");
            let dry_run = sub_matches.get_flag("dry-run");
            
            if check_only {
                println!("Checking for updates to {}...", display_name);
                println!("Update check not yet implemented for Rust. Use without --check to upgrade.");
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
                println!("Dry run - would execute: cargo {}", cmd_args.join(" "));
                return;
            }
            
            // Execute upgrade
            println!("Upgrading {} with cargo...", display_name);
            
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
        Some(("greet", sub_matches)) => {
            // Enhanced error handling for Rust commands
            let hook_name = "on_greet";
            match hooks::on_greet(sub_matches) {
                Ok(_) => {
                    // Command executed successfully
                }
                Err(e) => {
                    let error_context = format!("Command 'greet' execution");
                    
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
        Some(("info", sub_matches)) => {
            // Enhanced error handling for Rust commands
            let hook_name = "on_info";
            match hooks::on_info(sub_matches) {
                Ok(_) => {
                    // Command executed successfully
                }
                Err(e) => {
                    let error_context = format!("Command 'info' execution");
                    
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
            eprintln!("No subcommand provided. Use --help for available commands.");
            process::exit(1);
        }
    }
}