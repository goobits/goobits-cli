/**
 * Auto-generated from test-rust-cli.yaml
 * Main CLI implementation for Test Rust CLI
 */

use anyhow::Context;
use clap::{Parser, Subcommand, CommandFactory};
use std::collections::HashMap;
use std::process;

// Import error handling
mod errors;
use errors::{CliResult, CLIError, ExitCode};

// Import modules when building as library
#[cfg(feature = "lib")]
mod config;
#[cfg(feature = "lib")]
mod commands;
#[cfg(feature = "lib")]
mod utils;

// Re-export for hook functions
#[cfg(feature = "lib")]
pub use commands::{Command, CommandArgs};
#[cfg(feature = "lib")]
pub use config::AppConfig;

// Import actual hook system
mod hooks;
use hooks::{HookRegistry, HookContext, ExecutionPhase};

// Import plugin system
mod plugins;
use plugins::{initialize_plugins, execute_plugin_command, cleanup_plugins};

// Import styling system
mod styling;
use styling::initialize_styling;

// Import utilities
mod utils;

#[derive(Parser)]
#[command(name = "testcli")]
#[command(about = "Test CLI for Rust generation")]
#[command(long_about = "A simple test CLI to validate Rust generation")]
#[command(version = "2.0.0-beta.1")]
#[command(author = "")]

struct Cli {
    
    
    #[command(subcommand)]
    command: Option<Commands>,
}

#[derive(Subcommand)]
enum Commands {
    
    
    /// Say hello to someone
    Hello {
        
        
        
        /// Name to greet
        
        name: String,
        
        
        
        
        
        
        
        /// Custom greeting
        #[arg(long = "greeting", short = 'g', default_value = "Hello")]
        greeting: Option<String>,
        
        
        
        /// Verbose output
        #[arg(long = "verbose", short = 'v')]
        verbose: bool,
        
        
        
    },
    
    
    
    /// Process a file
    Process {
        
        
        
        /// Input file
        
        input: String,
        
        
        
        
        
        
        
        /// Output file
        #[arg(long = "output", short = 'o')]
        output: Option<String>,
        
        
        
        /// Output format
        #[arg(long = "format", short = 'f', default_value = "text")]
        format: Option<String>,
        
        
        
    },
    
    
    
    /// Shell completion management
    Completion {
        #[command(subcommand)]
        subcommand: CompletionCommands,
    },
    
    /// Configuration management
    Config {
        #[command(subcommand)]
        subcommand: ConfigCommands,
    },
    
    
    /// Upgrade Test Rust CLI to the latest version
    Upgrade {
        /// Check for updates without installing
        #[arg(long)]
        check: bool,
        
        /// Install specific version
        #[arg(long)]
        version: Option<String>,
        
        /// Include pre-release versions
        #[arg(long)]
        pre: bool,
        
        /// Show what would be done without doing it
        #[arg(long)]
        dry_run: bool,
    },
    
    
    /// Internal completion command - called by shell completion scripts
    #[command(hide = true)]
    #[clap(name = "_completion")]
    InternalCompletion {
        /// Shell type (bash, zsh, fish)
        shell: String,
        
        /// Current command line
        current_line: String,
        
        /// Cursor position
        cursor_pos: Option<usize>,
        
        /// Debug completion engine
        #[arg(long)]
        debug: bool,
    },
}







#[derive(Subcommand)]
enum CompletionCommands {
    /// Generate completion script for a shell
    Generate {
        /// Shell to generate completions for
        #[arg(value_parser = clap::builder::PossibleValuesParser::new(["bash", "zsh", "fish", "powershell"]))]
        shell: String,
        
        /// Output the completion script to a file instead of stdout
        #[arg(long, short)]
        output: Option<String>,
        
        /// Enable verbose output
        #[arg(long, short)]
        verbose: bool,
    },
    
    /// Install completions for current user
    Install {
        /// Shell to install completions for
        #[arg(value_parser = clap::builder::PossibleValuesParser::new(["bash", "zsh", "fish", "powershell"]))]
        shell: String,
        
        /// Install system-wide instead of user-only
        #[arg(long)]
        system: bool,
        
        /// Force overwrite existing completions
        #[arg(long, short)]
        force: bool,
    },
    
    /// Show instructions for manual completion installation
    Instructions {
        /// Shell to show instructions for
        #[arg(value_parser = clap::builder::PossibleValuesParser::new(["bash", "zsh", "fish", "powershell"]))]
        shell: String,
        
        /// Show system-wide installation instructions
        #[arg(long)]
        system: bool,
    },
}

#[derive(Subcommand)]
enum ConfigCommands {
    /// Get configuration value
    Get {
        /// Configuration key to retrieve (optional, shows all if not specified)
        key: Option<String>,
        
        /// Output format
        #[arg(long, value_parser = clap::builder::PossibleValuesParser::new(["json", "yaml", "plain"]))]
        format: Option<String>,
    },
    
    /// Set configuration value
    Set {
        /// Configuration key to set
        key: String,
        
        /// Value to set
        value: String,
        
        /// Data type of the value
        #[arg(long, value_parser = clap::builder::PossibleValuesParser::new(["string", "int", "float", "bool"]))]
        value_type: Option<String>,
    },
    
    /// Reset configuration to defaults
    Reset {
        /// Specific key to reset (resets all if not specified)
        key: Option<String>,
        
        /// Skip confirmation prompt
        #[arg(long, short)]
        yes: bool,
    },
    
    /// Show configuration file path
    Path {
        /// Show directory path instead of file path
        #[arg(long)]
        dir: bool,
        
        /// Create the config file/directory if it doesn't exist
        #[arg(long)]
        create: bool,
    },
}

// Arguments structure for hook functions
#[derive(Debug, Clone)]
pub struct Args {
    pub command_name: String,
    
    pub raw_args: HashMap<String, String>,
}


fn handle_upgrade(check: bool, version: Option<String>, pre: bool, dry_run: bool) -> CliResult<()> {
    let package_name = "test-rust-cli";
    let display_name = "Test Rust CLI";
    let current_version = env!("CARGO_PKG_VERSION");
    
    utils::output::info(&format!("Current version: {}", current_version));
    
    if check {
        utils::output::info(&format!("Checking for updates to {}...", display_name));
        utils::output::info("Update check not yet implemented. Run without --check to upgrade.");
        return Ok(());
    }
    
    if dry_run {
        let cmd = if let Some(ver) = version {
            format!("cargo install {} --version {}", package_name, ver)
        } else if pre {
            format!("cargo install {} --pre", package_name)
        } else {
            format!("cargo install {}", package_name)
        };
        utils::output::info(&format!("Dry run - would execute: {}", cmd));
        return Ok(());
    }
    
    utils::output::info(&format!("Upgrading {}...", display_name));
    
    let mut cmd = std::process::Command::new("cargo");
    cmd.args(&["install", package_name]);
    
    if let Some(ver) = version {
        cmd.args(&["--version", &ver]);
    } else if pre {
        cmd.arg("--pre");
    }
    
    let status = cmd.status()
        .map_err(|e| CLIError::hook("cargo install", &format!("Command execution failed: {}", e)))?;
    
    if status.success() {
        utils::output::success(&format!("{} upgraded successfully!", display_name));
        utils::output::info(&format!("Run '{} --version' to verify the new version.", "testcli"));
    } else {
        return Err(CLIError::hook("cargo install", "Upgrade command failed"));
    }
    
    Ok(())
}


/// Handle internal shell completion requests (called by completion scripts)
fn handle_internal_completion(shell: &str, current_line: &str, cursor_pos: Option<usize>, debug: bool) -> CliResult<()> {
    // Import completion engine at runtime
    mod completion_engine;
    
    let engine = completion_engine::CompletionEngine::new(None);
    let completions = engine.get_completions(shell, current_line, cursor_pos);
    
    // Output completions one per line
    for completion in completions {
        println!("{}", completion);
    }
    
    if debug && completions.is_empty() {
        eprintln!("No completions found");
    }
    
    Ok(())
}

fn main() {
    // Set up panic hook for better error reporting
    std::panic::set_hook(Box::new(|panic_info| {
        eprintln!("💥 Test Rust CLI encountered an unexpected error:");
        eprintln!("{}", panic_info);
        eprintln!("\n🐛 This is likely a bug. Please report it at: https://github.com/your-org/your-repo");
        process::exit(ExitCode::GeneralError as i32);
    }));

    if let Err(error) = run() {
        handle_application_error(&error);
    }
}

fn run() -> CliResult<()> {
    let cli = Cli::parse();
    
    // Initialize configuration and hook system
    let config = crate::config::AppConfig::load()
        .map_err(|e| CLIError::validation_failed(
            message: format!("Failed to load configuration: {}", e),
        }))?;
    let config_dir = crate::config::AppConfig::config_dir()
        .map_err(|e| CLIError::Environment {
            message: format!("Could not determine configuration directory: {}", e),
        })?;
    
    // Initialize styling system
    initialize_styling(
        config.is_feature_enabled("colored_output"),
        config.is_feature_enabled("unicode_symbols")
    );
    
    hooks::initialize_hooks(&config_dir)
        .map_err(|e| CLIError::hook("system", &format!("Failed to initialize hooks in {}: {}", config_dir.display(), e)))?;
    initialize_plugins(&config)
        .map_err(|e| CLIError::plugin("system", &format!("Failed to initialize plugins: {}", e)))?;
    
    // Prepare common arguments structure
    let args = Args {
        command_name: "".to_string(), // Will be set per command
        
        raw_args: HashMap::new(),
    };
    
    match cli.command {
        Some(command) => {
            match command {
                
                
                Commands::Hello { 
                    
                    
                    name,
                    
                    
                    
                    
                    greeting,
                    
                    verbose,
                    
                    
                } => {
                    execute_command_with_hooks("hello", args.clone(), || {
                        execute_hello_command(
                            
                            
                            
                            &name,
                            
                            
                            
                            
                            
                            
                            
                            greeting.as_deref(),
                            
                            
                            
                            
                            verbose,
                            
                            
                            
                        )
                    })?;
                }
                
                
                
                Commands::Process { 
                    
                    
                    input,
                    
                    
                    
                    
                    output,
                    
                    format,
                    
                    
                } => {
                    execute_command_with_hooks("process", args.clone(), || {
                        execute_process_command(
                            
                            
                            
                            &input,
                            
                            
                            
                            
                            
                            
                            
                            output.as_deref(),
                            
                            
                            
                            
                            
                            format.as_deref(),
                            
                            
                            
                            
                        )
                    })?;
                }
                
                
                
                Commands::Completion { subcommand } => {
                    match subcommand {
                        CompletionCommands::Generate { shell, output, verbose } => {
                            handle_completion_generate(&shell, output.as_deref(), verbose)?;
                        }
                        CompletionCommands::Install { shell, system, force } => {
                            handle_completion_install(&shell, system, force)?;
                        }
                        CompletionCommands::Instructions { shell, system } => {
                            handle_completion_instructions(&shell, system)?;
                        }
                    }
                }
                
                Commands::Config { subcommand } => {
                    match subcommand {
                        ConfigCommands::Get { key, format } => {
                            handle_config_get(key.as_deref(), format.as_deref())?;
                        }
                        ConfigCommands::Set { key, value, value_type } => {
                            handle_config_set(&key, &value, value_type.as_deref())?;
                        }
                        ConfigCommands::Reset { key, yes } => {
                            handle_config_reset(key.as_deref(), yes)?;
                        }
                        ConfigCommands::Path { dir, create } => {
                            handle_config_path(dir, create)?;
                        }
                    }
                }
                
                
                Commands::Upgrade { check, version, pre, dry_run } => {
                    handle_upgrade(check, version, pre, dry_run)?;
                }
                
                
                Commands::InternalCompletion { shell, current_line, cursor_pos, debug } => {
                    handle_internal_completion(&shell, &current_line, cursor_pos, debug)?;
                }
            }
        }
        None => {
            
            
            
            
            
            
            
            // No default command, show help
            let mut cmd = Cli::command();
            cmd.print_help().map_err(|e| CLIError::Application {
                message: "Failed to print help".to_string(),
                context: Some(e.to_string()),
            })?;
            println!();
            
        }
    }
    
    Ok(())
}

/// Execute a command with full hook lifecycle management
fn execute_command_with_hooks<F>(command_name: &str, args: Args, execute_fn: F) -> CliResult<()>
where
    F: FnOnce() -> CliResult<()>,
{
    // Prepare hook context
    let hook_context = HookContext::new(
        command_name.to_string(),
        None,
        vec![], // args would be populated from actual command arguments
        HashMap::new(), // options would be populated from actual command options
        ExecutionPhase::PreCommand,
    ).map_err(|e| CLIError::hook(
        name: command_name.to_string(),
        phase: "context_creation".to_string(),
        reason: e.to_string(),
    }))?;
    
    // Execute pre-command hooks
    if let Err(e) = hooks::execute_command_hooks(command_name, ExecutionPhase::PreCommand, &hook_context) {
        let error_context = hook_context.with_error(&e.to_string());
        let _ = hooks::execute_command_hooks(command_name, ExecutionPhase::OnError, &error_context);
        return Err(CLIError::hook(
            name: command_name.to_string(),
            phase: "pre-command".to_string(),
            reason: e.to_string(),
        }));
    }
    
    // Execute the actual command
    let command_result = execute_fn();
    
    // Execute post-command hooks
    let post_context = HookContext::new(
        command_name.to_string(),
        None,
        vec![],
        HashMap::new(),
        if command_result.is_ok() { ExecutionPhase::OnSuccess } else { ExecutionPhase::OnError },
    ).map_err(|e| CLIError::hook(
        name: command_name.to_string(),
        phase: "post_context_creation".to_string(),
        reason: e.to_string(),
    }))?;
    
    match &command_result {
        Ok(_) => {
            let _ = hooks::execute_command_hooks(command_name, ExecutionPhase::PostCommand, &post_context);
            let _ = hooks::execute_command_hooks(command_name, ExecutionPhase::OnSuccess, &post_context);
        }
        Err(e) => {
            let error_context = post_context.with_error(&e.to_string());
            let _ = hooks::execute_command_hooks(command_name, ExecutionPhase::OnError, &error_context);
        }
    }
    
    command_result
}



/// Execute hello command with proper error handling
fn execute_hello_command(
    
    
    
    name: &str,
    
    
    
    
    
    
    
    greeting: Option<&str>,
    
    
    
    
    verbose: bool,
    
    
    
) -> CliResult<()> {
    
    // Default command implementation with validation
    utils::output::info("🚀 Executing hello command...");
    
    // Validate command arguments
    
    
    
    if name.is_empty() {
        return Err(CLIError::Command(errors::CommandError::MissingArgument {
            arg: "name".to_string(),
        }));
    }
    
    
    
    
    
    // Display command execution information
    
    
    
    utils::output::key_value("name", name);
    
    
    
    
    
    
    
    if let Some(value) = greeting {
        utils::output::key_value("greeting", value);
    }
    
    
    
    
    if verbose {
        utils::output::key_value("verbose", "enabled");
    }
    
    
    
    
    // TODO: Implement actual hello command logic here
    // This is a placeholder implementation
    
    utils::output::success("Hello command completed successfully!");
    
    
    Ok(())
}



/// Execute process command with proper error handling
fn execute_process_command(
    
    
    
    input: &str,
    
    
    
    
    
    
    
    output: Option<&str>,
    
    
    
    
    
    format: Option<&str>,
    
    
    
    
) -> CliResult<()> {
    
    // Default command implementation with validation
    utils::output::info("🚀 Executing process command...");
    
    // Validate command arguments
    
    
    
    if input.is_empty() {
        return Err(CLIError::Command(errors::CommandError::MissingArgument {
            arg: "input".to_string(),
        }));
    }
    
    
    
    
    
    // Display command execution information
    
    
    
    utils::output::key_value("input", input);
    
    
    
    
    
    
    
    if let Some(value) = output {
        utils::output::key_value("output", value);
    }
    
    
    
    
    
    if let Some(value) = format {
        utils::output::key_value("format", value);
    }
    
    
    
    
    
    // TODO: Implement actual process command logic here
    // This is a placeholder implementation
    
    utils::output::success("Process command completed successfully!");
    
    
    Ok(())
}



/// Handle completion generate command
fn handle_completion_generate(shell: &str, output: Option<&str>, verbose: bool) -> CliResult<()> {
    use std::io::Write;
    
    if verbose {
        utils::output::info(&format!("Generating {} completion script...", shell));
    }
    
    // Generate completion script based on shell type
    let completion_script = match shell {
        "bash" => generate_bash_completion(),
        "zsh" => generate_zsh_completion(),
        "fish" => generate_fish_completion(),
        "powershell" => generate_powershell_completion(),
        _ => return Err(CLIError::Command(errors::CommandError::InvalidArgument {
            arg: "shell".to_string(),
            value: shell.to_string(),
            expected: "one of: bash, zsh, fish, powershell".to_string(),
        })),
    };
    
    match output {
        Some(file_path) => {
            // Write to file
            let mut file = std::fs::File::create(file_path)
                .map_err(|e| CLIError::Io(std::io::Error::new(
                    std::io::ErrorKind::Other,
                    format!("Failed to create output file '{}': {}", file_path, e)
                )))?;
            
            file.write_all(completion_script.as_bytes())
                .map_err(|e| CLIError::Io(std::io::Error::new(
                    std::io::ErrorKind::Other,
                    format!("Failed to write to output file '{}': {}", file_path, e)
                )))?;
            
            utils::output::success(&format!("Completion script written to: {}", file_path));
        }
        None => {
            // Write to stdout
            print!("{}", completion_script);
        }
    }
    
    Ok(())
}

/// Handle completion install command
fn handle_completion_install(shell: &str, system: bool, force: bool) -> CliResult<()> {
    use std::fs;
    use std::path::PathBuf;
    
    utils::output::info(&format!("Installing {} completions...", shell));
    
    // Determine completion paths based on shell and scope
    let (completion_dir, completion_file) = match shell {
        "bash" => {
            let dir = if system {
                PathBuf::from("/etc/bash_completion.d")
            } else {
                dirs::home_dir()
                    .ok_or_else(|| CLIError::Environment {
                        message: "Could not determine home directory".to_string(),
                    })?
                    .join(".local/share/bash-completion/completions")
            };
            (dir, format!("{}", "testcli"))
        }
        "zsh" => {
            let dir = if system {
                PathBuf::from("/usr/local/share/zsh/site-functions")
            } else {
                dirs::home_dir()
                    .ok_or_else(|| CLIError::Environment {
                        message: "Could not determine home directory".to_string(),
                    })?
                    .join(".local/share/zsh/site-functions")
            };
            (dir, format!("_{}", "testcli"))
        }
        "fish" => {
            let dir = if system {
                PathBuf::from("/usr/share/fish/completions")
            } else {
                dirs::home_dir()
                    .ok_or_else(|| CLIError::Environment {
                        message: "Could not determine home directory".to_string(),
                    })?
                    .join(".config/fish/completions")
            };
            (dir, format!("{}.fish", "testcli"))
        }
        "powershell" => {
            return Err(CLIError::hook(
                command: "completion install".to_string(),
                reason: "PowerShell completion installation not supported on this platform".to_string(),
            }));
        }
        _ => return Err(CLIError::Command(errors::CommandError::InvalidArgument {
            arg: "shell".to_string(),
            value: shell.to_string(),
            expected: "one of: bash, zsh, fish, powershell".to_string(),
        })),
    };
    
    let completion_path = completion_dir.join(&completion_file);
    
    // Check if completion already exists
    if completion_path.exists() && !force {
        return Err(CLIError::hook(
            command: "completion install".to_string(),
            reason: format!(
                "Completion already exists at {}. Use --force to overwrite.",
                completion_path.display()
            ),
        }));
    }
    
    // Create completion directory if it doesn't exist
    if let Some(parent) = completion_path.parent() {
        fs::create_dir_all(parent)
            .map_err(|e| CLIError::Io(std::io::Error::new(
                std::io::ErrorKind::Other,
                format!("Failed to create completion directory '{}': {}", parent.display(), e)
            )))?;
    }
    
    // Generate completion script
    let completion_script = match shell {
        "bash" => generate_bash_completion(),
        "zsh" => generate_zsh_completion(),
        "fish" => generate_fish_completion(),
        _ => unreachable!(),
    };
    
    // Write completion script
    fs::write(&completion_path, completion_script)
        .map_err(|e| CLIError::Io(std::io::Error::new(
            std::io::ErrorKind::Other,
            format!("Failed to write completion file '{}': {}", completion_path.display(), e)
        )))?;
    
    utils::output::success(&format!(
        "Completion installed at: {}",
        completion_path.display()
    ));
    
    // Provide activation instructions
    match shell {
        "bash" => {
            if !system {
                utils::output::info("Add the following to your ~/.bashrc:");
                utils::output::info(&format!(
                    "  source {}",
                    completion_path.display()
                ));
            }
        }
        "zsh" => {
            if !system {
                utils::output::info("Ensure ~/.local/share/zsh/site-functions is in your $fpath");
                utils::output::info("Add to ~/.zshrc if needed:");
                utils::output::info("  fpath=(~/.local/share/zsh/site-functions $fpath)");
            }
        }
        "fish" => {
            utils::output::info("Fish completions are automatically loaded");
        }
        _ => {}
    }
    
    Ok(())
}

/// Handle completion instructions command
fn handle_completion_instructions(shell: &str, system: bool) -> CliResult<()> {
    let scope = if system { "system-wide" } else { "user" };
    
    utils::output::info(&format!("Manual {} completion installation instructions ({})", shell, scope));
    println!();
    
    match shell {
        "bash" => {
            if system {
                println!("1. Generate completion script:");
                println!("   {} completion generate bash | sudo tee /etc/bash_completion.d/{}", "testcli", "testcli");
                println!();
                println!("2. Reload bash completions:");
                println!("   source /etc/bash_completion");
            } else {
                println!("1. Create completion directory:");
                println!("   mkdir -p ~/.local/share/bash-completion/completions");
                println!();
                println!("2. Generate completion script:");
                println!("   {} completion generate bash > ~/.local/share/bash-completion/completions/{}", "testcli", "testcli");
                println!();
                println!("3. Add to ~/.bashrc:");
                println!("   source ~/.local/share/bash-completion/completions/{}",  "testcli");
            }
        }
        "zsh" => {
            if system {
                println!("1. Generate completion script:");
                println!("   {} completion generate zsh | sudo tee /usr/local/share/zsh/site-functions/_{}", "testcli", "testcli");
                println!();
                println!("2. Reload zsh completions:");
                println!("   autoload -U compinit && compinit");
            } else {
                println!("1. Create completion directory:");
                println!("   mkdir -p ~/.local/share/zsh/site-functions");
                println!();
                println!("2. Generate completion script:");
                println!("   {} completion generate zsh > ~/.local/share/zsh/site-functions/_{}", "testcli", "testcli");
                println!();
                println!("3. Add to ~/.zshrc (if not already present):");
                println!("   fpath=(~/.local/share/zsh/site-functions $fpath)");
                println!("   autoload -U compinit && compinit");
            }
        }
        "fish" => {
            if system {
                println!("1. Generate completion script:");
                println!("   {} completion generate fish | sudo tee /usr/share/fish/completions/{}.fish", "testcli", "testcli");
            } else {
                println!("1. Create completion directory:");
                println!("   mkdir -p ~/.config/fish/completions");
                println!();
                println!("2. Generate completion script:");
                println!("   {} completion generate fish > ~/.config/fish/completions/{}.fish", "testcli", "testcli");
            }
            println!();
            println!("Fish completions are automatically loaded when the shell starts.");
        }
        "powershell" => {
            println!("1. Generate completion script:");
            println!("   {} completion generate powershell > {}_completion.ps1", "testcli", "testcli");
            println!();
            println!("2. Add to PowerShell profile:");
            println!("   . ./{}_completion.ps1", "testcli");
            println!();
            println!("Note: You may need to adjust ExecutionPolicy:");
            println!("   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser");
        }
        _ => return Err(CLIError::Command(errors::CommandError::InvalidArgument {
            arg: "shell".to_string(),
            value: shell.to_string(),
            expected: "one of: bash, zsh, fish, powershell".to_string(),
        })),
    }
    
    println!();
    utils::output::info("After installation, restart your shell or source your profile to enable completions.");
    
    Ok(())
}

/// Handle config get command
fn handle_config_get(key: Option<&str>, format: Option<&str>) -> CliResult<()> {
    let config = crate::config::AppConfig::load()
        .map_err(|e| CLIError::validation_failed(
            message: format!("Failed to load configuration: {}", e),
        }))?;
    
    let output_format = format.unwrap_or("plain");
    
    match key {
        Some(key_name) => {
            // Get specific key
            match config.get_value(key_name) {
                Some(value) => {
                    match output_format {
                        "json" => {
                            let json_value = serde_json::json!({key_name: value});
                            println!("{}", serde_json::to_string_pretty(&json_value)
                                .map_err(|e| CLIError::validation_failed(
                                    message: format!("Failed to format as JSON: {}", e),
                                }))?);
                        }
                        "yaml" => {
                            let yaml_map = std::collections::HashMap::<String, serde_yaml::Value>::from([(key_name.to_string(), value.clone())]);
                            println!("{}", serde_yaml::to_string(&yaml_map)
                                .map_err(|e| CLIError::validation_failed(
                                    message: format!("Failed to format as YAML: {}", e),
                                }))?);
                        }
                        "plain" | _ => {
                            println!("{}", value.as_str().unwrap_or(&value.to_string()));
                        }
                    }
                }
                None => {
                    return Err(CLIError::Config(errors::ConfigError::KeyNotFound {
                        key: key_name.to_string(),
                    }));
                }
            }
        }
        None => {
            // Get all configuration
            let all_config = config.to_map();
            
            match output_format {
                "json" => {
                    println!("{}", serde_json::to_string_pretty(&all_config)
                        .map_err(|e| CLIError::validation_failed(
                            message: format!("Failed to format as JSON: {}", e),
                        }))?);
                }
                "yaml" => {
                    println!("{}", serde_yaml::to_string(&all_config)
                        .map_err(|e| CLIError::validation_failed(
                            message: format!("Failed to format as YAML: {}", e),
                        }))?);
                }
                "plain" | _ => {
                    utils::output::info("Configuration values:");
                    for (key, value) in all_config {
                        utils::output::key_value(&key, &value.as_str().unwrap_or(&value.to_string()));
                    }
                }
            }
        }
    }
    
    Ok(())
}

/// Handle config set command
fn handle_config_set(key: &str, value: &str, value_type: Option<&str>) -> CliResult<()> {
    let mut config = crate::config::AppConfig::load()
        .map_err(|e| CLIError::validation_failed(
            message: format!("Failed to load configuration: {}", e),
        }))?;
    
    // Parse value based on type
    let parsed_value = match value_type.unwrap_or("string") {
        "string" => serde_yaml::Value::String(value.to_string()),
        "int" => {
            let int_val: i64 = value.parse()
                .map_err(|_| CLIError::validation_failed(
                    message: format!("Invalid integer value: {}", value),
                }))?;
            serde_yaml::Value::Number(serde_yaml::Number::from(int_val))
        }
        "float" => {
            let float_val: f64 = value.parse()
                .map_err(|_| CLIError::validation_failed(
                    message: format!("Invalid float value: {}", value),
                }))?;
            serde_yaml::Value::Number(serde_yaml::Number::from(float_val))
        }
        "bool" => {
            let bool_val: bool = value.parse()
                .map_err(|_| CLIError::validation_failed(
                    message: format!("Invalid boolean value: {} (use true/false)", value),
                }))?;
            serde_yaml::Value::Bool(bool_val)
        }
        _ => return Err(CLIError::validation_failed(
            message: format!("Invalid value type: {}", value_type.unwrap()),
        })),
    };
    
    // Set the value
    config.set_value(key, parsed_value)
        .map_err(|e| CLIError::validation_failed(
            message: format!("Failed to set configuration value: {}", e),
        }))?;
    
    // Save the configuration
    config.save()
        .map_err(|e| CLIError::Config(errors::ConfigError::SaveFailed {
            message: format!("Failed to save configuration: {}", e),
        }))?;
    
    utils::output::success(&format!("Configuration value set: {} = {}", key, value));
    
    Ok(())
}

/// Handle config reset command
fn handle_config_reset(key: Option<&str>, yes: bool) -> CliResult<()> {
    let config_path = crate::config::AppConfig::config_path()
        .map_err(|e| CLIError::Environment {
            message: format!("Could not determine configuration path: {}", e),
        })?;
    
    match key {
        Some(key_name) => {
            // Reset specific key
            if !yes {
                // TODO: Add prompts helper and use confirmation
                println!("Reset configuration key '{}' to default value? [y/N]: ", key_name);
                let mut input = String::new();
                std::io::stdin().read_line(&mut input)
                    .map_err(|e| CLIError::Io(e))?;
                
                if !input.trim().to_lowercase().starts_with('y') {
                    utils::output::info("Reset cancelled.");
                    return Ok(());
                }
            }
            
            let mut config = crate::config::AppConfig::load()
                .map_err(|e| CLIError::validation_failed(
                    message: format!("Failed to load configuration: {}", e),
                }))?;
            
            config.reset_key(key_name)
                .map_err(|e| CLIError::validation_failed(
                    message: format!("Failed to reset configuration key: {}", e),
                }))?;
            
            config.save()
                .map_err(|e| CLIError::Config(errors::ConfigError::SaveFailed {
                    message: format!("Failed to save configuration: {}", e),
                }))?;
            
            utils::output::success(&format!("Configuration key '{}' reset to default", key_name));
        }
        None => {
            // Reset entire configuration
            if !yes {
                println!("Reset entire configuration to defaults? This will remove all custom settings. [y/N]: ");
                let mut input = String::new();
                std::io::stdin().read_line(&mut input)
                    .map_err(|e| CLIError::Io(e))?;
                
                if !input.trim().to_lowercase().starts_with('y') {
                    utils::output::info("Reset cancelled.");
                    return Ok(());
                }
            }
            
            // Remove config file to reset to defaults
            if config_path.exists() {
                std::fs::remove_file(&config_path)
                    .map_err(|e| CLIError::Io(std::io::Error::new(
                        std::io::ErrorKind::Other,
                        format!("Failed to remove configuration file '{}': {}", config_path.display(), e)
                    )))?;
            }
            
            utils::output::success("Configuration reset to defaults");
        }
    }
    
    Ok(())
}

/// Handle config path command
fn handle_config_path(dir: bool, create: bool) -> CliResult<()> {
    if dir {
        let config_dir = crate::config::AppConfig::config_dir()
            .map_err(|e| CLIError::Environment {
                message: format!("Could not determine configuration directory: {}", e),
            })?;
        
        if create && !config_dir.exists() {
            std::fs::create_dir_all(&config_dir)
                .map_err(|e| CLIError::Io(std::io::Error::new(
                    std::io::ErrorKind::Other,
                    format!("Failed to create configuration directory '{}': {}", config_dir.display(), e)
                )))?;
            utils::output::success(&format!("Created configuration directory: {}", config_dir.display()));
        }
        
        println!("{}", config_dir.display());
    } else {
        let config_path = crate::config::AppConfig::config_path()
            .map_err(|e| CLIError::Environment {
                message: format!("Could not determine configuration path: {}", e),
            })?;
        
        if create {
            // Create directory if needed
            if let Some(parent) = config_path.parent() {
                if !parent.exists() {
                    std::fs::create_dir_all(parent)
                        .map_err(|e| CLIError::Io(std::io::Error::new(
                            std::io::ErrorKind::Other,
                            format!("Failed to create configuration directory '{}': {}", parent.display(), e)
                        )))?;
                }
            }
            
            // Create config file if it doesn't exist
            if !config_path.exists() {
                let default_config = crate::config::AppConfig::default();
                default_config.save()
                    .map_err(|e| CLIError::Config(errors::ConfigError::SaveFailed {
                        message: format!("Failed to create configuration file: {}", e),
                    }))?;
                utils::output::success(&format!("Created configuration file: {}", config_path.display()));
            }
        }
        
        println!("{}", config_path.display());
    }
    
    Ok(())
}

// Helper functions for generating completion scripts
fn generate_bash_completion() -> String {
    format!(r#"#!/bin/bash
# Bash completion for {}
# Generated by goobits-cli

_{}_completion() {{
    local cur prev opts
    COMPREPLY=()
    cur="${{COMP_WORDS[COMP_CWORD]}}"
    prev="${{COMP_WORDS[COMP_CWORD-1]}}"
    
    # Get completions from the CLI
    local completions
    completions=$({} _completion bash "${{COMP_LINE}}" "${{COMP_POINT}}" 2>/dev/null)
    
    # Convert completions to array
    COMPREPLY=( $(compgen -W "${{completions}}" -- "${{cur}}") )
    
    return 0
}}

complete -F _{}_completion {}
"#, "testcli", "testcli", "testcli", "testcli", "testcli")
}

fn generate_zsh_completion() -> String {
    format!(r#"#compdef {}
# Zsh completion for {}
# Generated by goobits-cli

_{}_completion() {{
    local state line
    local -a completions
    
    # Get completions from the CLI
    completions=($({} _completion zsh "${{words[*]}}" "${{CURSOR}}" 2>/dev/null))
    
    # Provide completions
    compadd -a completions
}}

_{}_completion "$@"
"#, "testcli", "testcli", "testcli", "testcli", "testcli")
}

fn generate_fish_completion() -> String {
    format!(r#"# Fish completion for {}
# Generated by goobits-cli

complete -c {} -f -a "({} _completion fish (commandline -cp) (commandline -C) 2>/dev/null)"
"#, "testcli", "testcli", "testcli")
}

fn generate_powershell_completion() -> String {
    format!(r#"# PowerShell completion for {}
# Generated by goobits-cli

Register-ArgumentCompleter -Native -CommandName {} -ScriptBlock {{
    param($commandLine, $wordToComplete, $cursorPosition)
    
    try {{
        $completions = & {} _completion powershell $commandLine $cursorPosition 2>$null
        $completions | ForEach-Object {{
            [System.Management.Automation.CompletionResult]::new($_, $_, 'ParameterValue', $_)
        }}
    }} catch {{
        # Silently ignore errors
    }}
}}
"#, "testcli", "testcli", "testcli")
}

/// Handle application errors with appropriate formatting and exit codes
fn handle_application_error(error: &CLIError) {
    // Initialize styling if not already done (fallback)
    if std::panic::catch_unwind(|| styling::output()).is_err() {
        initialize_styling(true, true);
    }

    // Print user-friendly error message
    formatting::print_error(error);

    // In debug mode, also print the error chain
    #[cfg(debug_assertions)]
    formatting::print_error_chain(error);

    // Cleanup resources before exit
    if let Err(cleanup_error) = cleanup_plugins() {
        eprintln!("Warning: Failed to cleanup plugins: {}", cleanup_error);
    }

    // Exit with appropriate code
    let exit_code = ExitCode::from(error);
    process::exit(exit_code as i32);
}