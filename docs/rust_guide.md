# Goobits Rust CLI Generation Guide

A comprehensive guide for Rust developers using Goobits to generate production-ready CLI applications.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Understanding the Architecture](#understanding-the-architecture)
3. [Configuration Reference](#configuration-reference)
4. [Hook System](#hook-system)
5. [Advanced Features](#advanced-features)
6. [Testing Your CLI](#testing-your-cli)
7. [Publishing to crates.io](#publishing-to-cratesio)
8. [Real-World Examples](#real-world-examples)
9. [Troubleshooting](#troubleshooting)
10. [Best Practices](#best-practices)

## Quick Start

### Installation

```bash
# Install goobits globally
npm install -g goobits-cli

# Or use npx
npx goobits-cli init my-rust-cli
```

### Your First Rust CLI

Create a `goobits.yaml` file:

```yaml
app_name: task-manager
language: rust
rust_binary_name: taskman
commands:
  - name: add
    description: Add a new task
    arguments:
      - name: title
        type: string
        required: true
        description: Task title
    options:
      - name: priority
        type: choice
        choices: [low, medium, high]
        default: medium
        description: Task priority
      - name: due
        type: string
        description: Due date (YYYY-MM-DD)
  - name: list
    description: List all tasks
    options:
      - name: status
        type: choice
        choices: [pending, completed, all]
        default: pending
      - name: sort
        type: choice
        choices: [date, priority, title]
        default: date
```

Generate your CLI:

```bash
goobits generate

# This creates:
# ├── Cargo.toml
# ├── src/
# │   ├── main.rs      # CLI entry point with clap
# │   ├── lib.rs       # Library module
# │   ├── config.rs    # Configuration management
# │   ├── commands.rs  # Command registry
# │   └── utils.rs     # Utility functions
# ├── .gitignore
# ├── LICENSE
# └── README.md
```

### Implement Your Business Logic

Create `src/hooks.rs`:

```rust
use anyhow::Result;
use chrono::{Local, NaiveDate};
use serde::{Deserialize, Serialize};
use std::fs;
use std::path::PathBuf;

#[derive(Debug, Serialize, Deserialize)]
struct Task {
    id: String,
    title: String,
    priority: String,
    due_date: Option<String>,
    created_at: String,
    completed: bool,
}

pub fn on_add(args: &crate::Args) -> Result<()> {
    let title = args.raw_args.get("title")
        .ok_or_else(|| anyhow::anyhow!("Title is required"))?;
    let priority = args.raw_args.get("priority")
        .unwrap_or(&"medium".to_string());
    let due_date = args.raw_args.get("due").cloned();
    
    // Validate due date if provided
    if let Some(ref due) = due_date {
        NaiveDate::parse_from_str(due, "%Y-%m-%d")
            .map_err(|_| anyhow::anyhow!("Invalid date format. Use YYYY-MM-DD"))?;
    }
    
    let task = Task {
        id: uuid::Uuid::new_v4().to_string(),
        title: title.clone(),
        priority: priority.clone(),
        due_date,
        created_at: Local::now().to_rfc3339(),
        completed: false,
    };
    
    // Load existing tasks
    let tasks_file = get_tasks_file()?;
    let mut tasks = load_tasks(&tasks_file)?;
    
    // Add new task
    tasks.push(task);
    
    // Save tasks
    save_tasks(&tasks_file, &tasks)?;
    
    println!("✅ Task added successfully!");
    Ok(())
}

pub fn on_list(args: &crate::Args) -> Result<()> {
    let status = args.raw_args.get("status")
        .unwrap_or(&"pending".to_string());
    let sort_by = args.raw_args.get("sort")
        .unwrap_or(&"date".to_string());
    
    let tasks_file = get_tasks_file()?;
    let mut tasks = load_tasks(&tasks_file)?;
    
    // Filter by status
    let filtered_tasks: Vec<_> = match status.as_str() {
        "pending" => tasks.iter().filter(|t| !t.completed).collect(),
        "completed" => tasks.iter().filter(|t| t.completed).collect(),
        "all" => tasks.iter().collect(),
        _ => return Err(anyhow::anyhow!("Invalid status")),
    };
    
    // Sort tasks
    let mut sorted_tasks = filtered_tasks;
    match sort_by.as_str() {
        "date" => sorted_tasks.sort_by(|a, b| a.created_at.cmp(&b.created_at)),
        "priority" => sorted_tasks.sort_by(|a, b| {
            let prio_order = |p: &str| match p {
                "high" => 0,
                "medium" => 1,
                "low" => 2,
                _ => 3,
            };
            prio_order(&a.priority).cmp(&prio_order(&b.priority))
        }),
        "title" => sorted_tasks.sort_by(|a, b| a.title.cmp(&b.title)),
        _ => return Err(anyhow::anyhow!("Invalid sort option")),
    }
    
    // Display tasks
    if sorted_tasks.is_empty() {
        println!("No tasks found.");
    } else {
        println!("Tasks ({}):", status);
        println!("{:-<60}", "");
        for task in sorted_tasks {
            let status_icon = if task.completed { "✓" } else { "○" };
            let priority_icon = match task.priority.as_str() {
                "high" => "🔴",
                "medium" => "🟡",
                "low" => "🟢",
                _ => "⚪",
            };
            
            println!(
                "{} {} {} - {}",
                status_icon,
                priority_icon,
                task.title,
                task.due_date.as_deref().unwrap_or("No due date")
            );
        }
    }
    
    Ok(())
}

fn get_tasks_file() -> Result<PathBuf> {
    let home = dirs::home_dir()
        .ok_or_else(|| anyhow::anyhow!("Could not find home directory"))?;
    let data_dir = home.join(".taskman");
    fs::create_dir_all(&data_dir)?;
    Ok(data_dir.join("tasks.json"))
}

fn load_tasks(file: &PathBuf) -> Result<Vec<Task>> {
    if file.exists() {
        let content = fs::read_to_string(file)?;
        Ok(serde_json::from_str(&content)?)
    } else {
        Ok(Vec::new())
    }
}

fn save_tasks(file: &PathBuf, tasks: &[Task]) -> Result<()> {
    let content = serde_json::to_string_pretty(tasks)?;
    fs::write(file, content)?;
    Ok(())
}
```

Update `src/main.rs` to use hooks:

```rust
// Replace the placeholder hooks with:
mod hooks {
    use super::*;
    
    pub fn try_call_hook(command_name: &str, args: &Args) -> Result<()> {
        match command_name {
            "add" => crate::hooks::on_add(args),
            "list" => crate::hooks::on_list(args),
            _ => anyhow::bail!("Unknown command: {}", command_name),
        }
    }
}

// Add the hooks module
mod hooks;
```

Add dependencies to `Cargo.toml`:

```toml
[dependencies]
# ... existing dependencies ...
uuid = { version = "1.0", features = ["v4"] }
chrono = { version = "0.4", features = ["serde"] }
```

Build and run:

```bash
cargo build --release
./target/release/taskman add "Write documentation" --priority high
./target/release/taskman list
```

## Understanding the Architecture

### Generated File Structure

```
my-rust-cli/
├── Cargo.toml          # Project metadata and dependencies
├── src/
│   ├── main.rs         # CLI entry point with clap parsing
│   ├── lib.rs          # Library interface for plugins
│   ├── config.rs       # Configuration management
│   ├── commands.rs     # Command registry and traits
│   └── utils.rs        # Shared utilities
├── tests/              # Integration tests
├── examples/           # Example usage
└── benches/            # Performance benchmarks
```

### Key Components

1. **main.rs**: Entry point using clap for argument parsing
2. **lib.rs**: Exposes public API for extending the CLI
3. **config.rs**: Handles RC files and user preferences
4. **commands.rs**: Command trait system for extensibility
5. **utils.rs**: Common functionality (logging, errors, etc.)

### Clap Integration

Goobits generates a strongly-typed CLI using clap's derive API:

```rust
#[derive(Parser)]
#[command(name = "myapp")]
#[command(about = "My application description")]
struct Cli {
    #[command(subcommand)]
    command: Commands,
}

#[derive(Subcommand)]
enum Commands {
    /// Command description
    CommandName {
        /// Argument description
        arg: String,
        
        /// Option description
        #[arg(short, long)]
        option: Option<String>,
    },
}
```

## Configuration Reference

### Complete goobits.yaml Options

```yaml
# Application metadata
app_name: my-rust-cli
language: rust
version: 0.1.0
author: Your Name <email@example.com>
license: MIT
description: A powerful CLI tool
long_description: |
  A comprehensive command-line tool
  with multiple features and extensibility.

# Rust-specific settings
rust_binary_name: mycli        # Binary name (defaults to app_name)
rust_edition: "2021"           # Rust edition (2015, 2018, 2021)
rust_min_version: "1.70.0"     # Minimum Rust version

# Crate dependencies
rust_crates:
  - name: tokio
    version: "1.0"
    features: ["full"]
  - name: reqwest
    version: "0.11"
    features: ["json", "rustls-tls"]
  - name: sqlx
    version: "0.7"
    features: ["runtime-tokio-rustls", "postgres"]
    optional: true

# Dev dependencies
rust_dev_dependencies:
  - name: mockall
    version: "0.11"
  - name: criterion
    version: "0.5"

# Cargo features
rust_features:
  default: ["cli"]
  database: ["sqlx"]
  async: ["tokio/full"]
  
# Build configuration
rust_profile_release:
  lto: true
  codegen-units: 1
  strip: true

# Commands
commands:
  - name: serve
    description: Start the server
    rust_async: true           # Generate async command
    arguments:
      - name: port
        type: integer
        default: 8080
        validation:
          min: 1
          max: 65535
    options:
      - name: host
        type: string
        default: "127.0.0.1"
        env: SERVER_HOST       # Environment variable
      - name: workers
        type: integer
        short: w
        long: workers
        default: 4
        
# Global options
global_options:
  - name: config
    type: string
    short: c
    long: config
    description: Config file path
    env: MYCLI_CONFIG
  - name: verbose
    type: count              # -v, -vv, -vvv
    short: v
    long: verbose
    description: Increase verbosity

# Aliases
aliases:
  s: serve
  h: help

# Configuration file support
config:
  enabled: true
  format: toml               # toml, json, yaml
  locations:
    - "~/.config/mycli/config.toml"
    - "./.mycli.toml"
    
# Plugin system
plugins:
  enabled: true
  directory: "~/.mycli/plugins"
  
# Hook configuration
hooks:
  pre_command: "validate_env"
  post_command: "cleanup"
  error: "handle_error"
```

### Rust-Specific Features

1. **Async Commands**: Set `rust_async: true` for tokio-based async commands
2. **Feature Flags**: Define Cargo features for conditional compilation
3. **Build Profiles**: Optimize release builds with LTO and stripping
4. **Crate Features**: Specify features for each dependency

## Hook System

### Basic Hook Implementation

Create a separate crate for hooks or include in main:

```rust
// src/hooks.rs
use anyhow::Result;
use crate::{Args, ExecutionContext};

/// Called before any command executes
pub fn pre_command(args: &Args, ctx: &ExecutionContext) -> Result<()> {
    // Validate environment
    // Set up logging
    // Check permissions
    Ok(())
}

/// Command-specific hooks
pub fn on_serve(args: &Args, ctx: &ExecutionContext) -> Result<()> {
    let port = args.raw_args.get("port")
        .and_then(|p| p.parse::<u16>().ok())
        .unwrap_or(8080);
    
    let host = args.raw_args.get("host")
        .map(|s| s.as_str())
        .unwrap_or("127.0.0.1");
    
    // Start server
    start_server(host, port)?;
    Ok(())
}

/// Error handling hook
pub fn handle_error(error: &anyhow::Error, ctx: &ExecutionContext) -> Result<()> {
    eprintln!("Error: {}", error);
    
    // Log to file
    if let Ok(log_file) = std::env::var("MYCLI_LOG") {
        let _ = std::fs::write(
            log_file,
            format!("{}: {}\n", chrono::Local::now(), error)
        );
    }
    
    Ok(())
}
```

### Async Hook Support

For async commands:

```rust
// src/async_hooks.rs
use tokio::runtime::Runtime;

pub fn on_fetch(args: &Args) -> Result<()> {
    let rt = Runtime::new()?;
    rt.block_on(async_fetch(args))
}

async fn async_fetch(args: &Args) -> Result<()> {
    let url = args.raw_args.get("url")
        .ok_or_else(|| anyhow::anyhow!("URL required"))?;
    
    let client = reqwest::Client::new();
    let response = client.get(url)
        .send()
        .await?
        .text()
        .await?;
    
    println!("{}", response);
    Ok(())
}
```

### Plugin System

Create loadable plugins:

```rust
// plugin_example/src/lib.rs
use mycli::{Plugin, PluginCommand, Config};

pub struct MyPlugin {
    name: String,
    version: String,
}

impl Plugin for MyPlugin {
    fn name(&self) -> &str {
        &self.name
    }
    
    fn version(&self) -> &str {
        &self.version
    }
    
    fn init(&mut self, config: &Config) -> Result<()> {
        // Initialize plugin
        Ok(())
    }
    
    fn register_commands(&self) -> Vec<PluginCommand> {
        vec![
            PluginCommand {
                name: "plugin-cmd".to_string(),
                description: "Custom plugin command".to_string(),
                handler: |args| {
                    println!("Plugin command executed!");
                    Ok(())
                },
            }
        ]
    }
}

// Export plugin constructor
#[no_mangle]
pub extern "C" fn create_plugin() -> Box<dyn Plugin> {
    Box::new(MyPlugin {
        name: "my-plugin".to_string(),
        version: "0.1.0".to_string(),
    })
}
```

## Advanced Features

### Configuration Management

Implement RC file support:

```rust
// src/config_manager.rs
use config::{Config, File, Environment};
use serde::{Deserialize, Serialize};

#[derive(Debug, Deserialize, Serialize)]
pub struct AppSettings {
    pub server: ServerConfig,
    pub database: DatabaseConfig,
    pub features: Features,
}

#[derive(Debug, Deserialize, Serialize)]
pub struct ServerConfig {
    pub host: String,
    pub port: u16,
    pub workers: usize,
}

impl AppSettings {
    pub fn load() -> Result<Self> {
        let mut builder = Config::builder();
        
        // Default configuration
        builder = builder.add_source(File::from_str(
            include_str!("../config/default.toml"),
            config::FileFormat::Toml,
        ));
        
        // User configuration files
        if let Some(home) = dirs::home_dir() {
            let user_config = home.join(".config/mycli/config.toml");
            if user_config.exists() {
                builder = builder.add_source(File::from(user_config));
            }
        }
        
        // Local configuration
        builder = builder.add_source(
            File::with_name(".mycli")
                .required(false)
        );
        
        // Environment variables (MYCLI_SERVER_PORT, etc.)
        builder = builder.add_source(
            Environment::with_prefix("MYCLI")
                .separator("_")
        );
        
        let config = builder.build()?;
        Ok(config.try_deserialize()?)
    }
}
```

### Progress Indicators

Use indicatif for progress bars:

```rust
use indicatif::{ProgressBar, ProgressStyle};

pub fn process_files(files: Vec<PathBuf>) -> Result<()> {
    let pb = ProgressBar::new(files.len() as u64);
    pb.set_style(
        ProgressStyle::default_bar()
            .template("{spinner:.green} [{bar:40.cyan/blue}] {pos}/{len} {msg}")
            .unwrap()
            .progress_chars("#>-")
    );
    
    for file in files {
        pb.set_message(format!("Processing {}", file.display()));
        
        // Process file
        process_single_file(&file)?;
        
        pb.inc(1);
    }
    
    pb.finish_with_message("Processing complete!");
    Ok(())
}
```

### Interactive Prompts

Use dialoguer for user interaction:

```rust
use dialoguer::{theme::ColorfulTheme, Input, Select, Confirm};

pub fn interactive_setup() -> Result<Config> {
    let theme = ColorfulTheme::default();
    
    let name = Input::with_theme(&theme)
        .with_prompt("Project name")
        .default("my-project".to_string())
        .interact_text()?;
    
    let template = Select::with_theme(&theme)
        .with_prompt("Choose a template")
        .items(&["basic", "async", "full"])
        .default(0)
        .interact()?;
    
    let git = Confirm::with_theme(&theme)
        .with_prompt("Initialize git repository?")
        .default(true)
        .interact()?;
    
    Ok(Config { name, template, git })
}
```

### Logging

Implement structured logging:

```rust
use tracing::{info, warn, error, debug};
use tracing_subscriber::{layer::SubscriberExt, util::SubscriberInitExt};

pub fn init_logging(verbosity: u8) {
    let level = match verbosity {
        0 => tracing::Level::WARN,
        1 => tracing::Level::INFO,
        2 => tracing::Level::DEBUG,
        _ => tracing::Level::TRACE,
    };
    
    tracing_subscriber::registry()
        .with(
            tracing_subscriber::EnvFilter::try_from_default_env()
                .unwrap_or_else(|_| format!("{}={}", env!("CARGO_PKG_NAME"), level).into())
        )
        .with(tracing_subscriber::fmt::layer())
        .init();
    
    info!("Logging initialized at level: {:?}", level);
}

// Use in commands
pub fn on_command(args: &Args) -> Result<()> {
    debug!("Executing command with args: {:?}", args);
    
    match do_work() {
        Ok(result) => {
            info!("Command completed successfully");
            Ok(result)
        }
        Err(e) => {
            error!("Command failed: {}", e);
            Err(e)
        }
    }
}
```

### Shell Completions

Generate shell completions:

```rust
use clap::CommandFactory;
use clap_complete::{generate, Generator, Shell};

pub fn generate_completions<G: Generator>(generator: G, cmd: &mut Command) {
    generate(generator, cmd, cmd.get_name().to_string(), &mut std::io::stdout());
}

// In main.rs
#[derive(Parser)]
struct Cli {
    /// Generate shell completions
    #[arg(long, value_enum)]
    completions: Option<Shell>,
    
    #[command(subcommand)]
    command: Option<Commands>,
}

fn main() {
    let cli = Cli::parse();
    
    if let Some(shell) = cli.completions {
        let mut cmd = Cli::command();
        generate_completions(shell, &mut cmd);
        return;
    }
    
    // Normal command execution...
}
```

## Testing Your CLI

### Unit Tests

```rust
// src/lib.rs
#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_parse_arguments() {
        let args = Args {
            command_name: "test".to_string(),
            raw_args: [
                ("name".to_string(), "value".to_string()),
            ].into(),
        };
        
        assert_eq!(args.raw_args.get("name"), Some(&"value".to_string()));
    }
    
    #[test]
    fn test_config_loading() {
        let config = Config::default();
        assert!(config.validate().is_ok());
    }
}
```

### Integration Tests

```rust
// tests/integration.rs
use assert_cmd::Command;
use predicates::prelude::*;
use tempfile::TempDir;

#[test]
fn test_help_command() {
    let mut cmd = Command::cargo_bin("mycli").unwrap();
    cmd.arg("--help")
        .assert()
        .success()
        .stdout(predicate::str::contains("USAGE"));
}

#[test]
fn test_serve_command() {
    let mut cmd = Command::cargo_bin("mycli").unwrap();
    cmd.args(&["serve", "--port", "9999"])
        .assert()
        .success();
}

#[test]
fn test_config_file() {
    let temp_dir = TempDir::new().unwrap();
    let config_path = temp_dir.path().join("config.toml");
    
    std::fs::write(&config_path, r#"
        [server]
        port = 3000
    "#).unwrap();
    
    let mut cmd = Command::cargo_bin("mycli").unwrap();
    cmd.args(&["--config", config_path.to_str().unwrap(), "serve"])
        .assert()
        .success();
}
```

### Property-Based Testing

```rust
// tests/proptest.rs
use proptest::prelude::*;

proptest! {
    #[test]
    fn test_port_validation(port in 1u16..=65535u16) {
        let args = Args {
            command_name: "serve".to_string(),
            raw_args: [
                ("port".to_string(), port.to_string()),
            ].into(),
        };
        
        let result = validate_port(&args);
        prop_assert!(result.is_ok());
    }
    
    #[test]
    fn test_invalid_ports(port in 65536u32..u32::MAX) {
        let args = Args {
            command_name: "serve".to_string(),
            raw_args: [
                ("port".to_string(), port.to_string()),
            ].into(),
        };
        
        let result = validate_port(&args);
        prop_assert!(result.is_err());
    }
}
```

### Benchmarks

```rust
// benches/performance.rs
use criterion::{black_box, criterion_group, criterion_main, Criterion};

fn benchmark_command_parsing(c: &mut Criterion) {
    c.bench_function("parse serve command", |b| {
        b.iter(|| {
            let args = vec!["mycli", "serve", "--port", "8080"];
            let parsed = Cli::try_parse_from(args);
            black_box(parsed);
        });
    });
}

fn benchmark_config_loading(c: &mut Criterion) {
    c.bench_function("load config", |b| {
        b.iter(|| {
            let config = Config::load();
            black_box(config);
        });
    });
}

criterion_group!(benches, benchmark_command_parsing, benchmark_config_loading);
criterion_main!(benches);
```

## Publishing to crates.io

### Prepare for Publishing

1. **Update Cargo.toml**:
```toml
[package]
name = "my-awesome-cli"
version = "0.1.0"
authors = ["Your Name <email@example.com>"]
edition = "2021"
description = "A powerful CLI tool for X"
readme = "README.md"
homepage = "https://github.com/username/my-awesome-cli"
repository = "https://github.com/username/my-awesome-cli"
license = "MIT OR Apache-2.0"
keywords = ["cli", "tool", "productivity"]
categories = ["command-line-utilities"]

[package.metadata.docs.rs]
all-features = true

[badges]
maintenance = { status = "actively-developed" }
```

2. **Create comprehensive documentation**:
```rust
//! # My Awesome CLI
//! 
//! A powerful command-line tool for managing tasks.
//! 
//! ## Quick Start
//! 
//! ```bash
//! $ cargo install my-awesome-cli
//! $ mycli add "New task" --priority high
//! ```
//! 
//! ## Features
//! 
//! - Fast task management
//! - Multiple output formats
//! - Plugin support

/// Main application struct
/// 
/// # Examples
/// 
/// ```
/// use my_awesome_cli::App;
/// 
/// let app = App::new();
/// app.run()?;
/// ```
pub struct App {
    // ...
}
```

3. **Add examples**:
```rust
// examples/basic.rs
use my_awesome_cli::{App, Config};

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let config = Config::default();
    let app = App::with_config(config);
    app.run()
}
```

### Publishing Process

```bash
# Run all checks
cargo check
cargo test
cargo clippy -- -D warnings
cargo fmt --check
cargo doc --no-deps

# Dry run
cargo publish --dry-run

# Publish
cargo publish
```

### Version Management

Use cargo-release for automated releases:

```bash
# Install
cargo install cargo-release

# Configure in Cargo.toml
[package.metadata.release]
sign-commit = true
sign-tag = true
push-remote = "origin"
pre-release-hook = ["cargo", "test"]

# Release
cargo release patch  # 0.1.0 -> 0.1.1
cargo release minor  # 0.1.1 -> 0.2.0
cargo release major  # 0.2.0 -> 1.0.0
```

## Real-World Examples

### Example 1: File Processing CLI

```yaml
app_name: file-processor
language: rust
rust_binary_name: fproc
rust_crates:
  - name: walkdir
    version: "2.0"
  - name: rayon
    version: "1.7"
  - name: regex
    version: "1.0"
    
commands:
  - name: analyze
    description: Analyze files in directory
    rust_async: false
    arguments:
      - name: path
        type: string
        required: true
    options:
      - name: pattern
        type: string
        description: File pattern to match
      - name: parallel
        type: boolean
        default: true
        description: Process files in parallel
      - name: max-depth
        type: integer
        default: 10
```

Implementation:

```rust
use rayon::prelude::*;
use regex::Regex;
use walkdir::WalkDir;

pub fn on_analyze(args: &Args) -> Result<()> {
    let path = args.raw_args.get("path").unwrap();
    let pattern = args.raw_args.get("pattern")
        .map(|p| Regex::new(p))
        .transpose()?;
    let parallel = args.raw_args.get("parallel")
        .map(|p| p.parse().unwrap_or(true))
        .unwrap_or(true);
    let max_depth = args.raw_args.get("max-depth")
        .and_then(|d| d.parse().ok())
        .unwrap_or(10);
    
    let entries: Vec<_> = WalkDir::new(path)
        .max_depth(max_depth)
        .into_iter()
        .filter_map(Result::ok)
        .filter(|e| e.file_type().is_file())
        .filter(|e| {
            pattern.as_ref()
                .map(|p| p.is_match(e.file_name().to_str().unwrap_or("")))
                .unwrap_or(true)
        })
        .collect();
    
    if parallel {
        let results: Vec<_> = entries
            .par_iter()
            .map(|entry| analyze_file(entry.path()))
            .collect();
        
        for result in results {
            if let Ok(analysis) = result {
                println!("{}", analysis);
            }
        }
    } else {
        for entry in entries {
            let analysis = analyze_file(entry.path())?;
            println!("{}", analysis);
        }
    }
    
    Ok(())
}
```

### Example 2: Database Migration CLI

```yaml
app_name: db-migrator
language: rust
rust_binary_name: dbmigrate
rust_crates:
  - name: sqlx
    version: "0.7"
    features: ["runtime-tokio-rustls", "postgres", "sqlite", "mysql"]
  - name: tokio
    version: "1.0"
    features: ["full"]
    
commands:
  - name: create
    description: Create a new migration
    arguments:
      - name: name
        type: string
        required: true
        
  - name: up
    description: Run pending migrations
    rust_async: true
    options:
      - name: database-url
        type: string
        env: DATABASE_URL
        required: true
      - name: steps
        type: integer
        description: Number of migrations to run
        
  - name: down
    description: Rollback migrations
    rust_async: true
    options:
      - name: database-url
        type: string
        env: DATABASE_URL
        required: true
      - name: steps
        type: integer
        default: 1
```

Implementation:

```rust
use sqlx::{Connection, PgConnection, migrate::Migrator};
use chrono::Utc;

pub fn on_create(args: &Args) -> Result<()> {
    let name = args.raw_args.get("name").unwrap();
    let timestamp = Utc::now().format("%Y%m%d%H%M%S");
    let filename = format!("{}_{}.sql", timestamp, name);
    
    let migrations_dir = std::path::Path::new("migrations");
    std::fs::create_dir_all(migrations_dir)?;
    
    let filepath = migrations_dir.join(&filename);
    std::fs::write(&filepath, 
        "-- Add migration script here\n\n-- Rollback script\n-- DOWN\n"
    )?;
    
    println!("Created migration: {}", filepath.display());
    Ok(())
}

pub async fn on_up_async(args: &Args) -> Result<()> {
    let database_url = args.raw_args.get("database-url")
        .ok_or_else(|| anyhow::anyhow!("Database URL required"))?;
    let steps = args.raw_args.get("steps")
        .and_then(|s| s.parse().ok());
    
    let mut conn = PgConnection::connect(database_url).await?;
    let migrator = Migrator::new(std::path::Path::new("./migrations")).await?;
    
    if let Some(n) = steps {
        for _ in 0..n {
            migrator.run_next(&mut conn).await?;
        }
        println!("Ran {} migrations", n);
    } else {
        migrator.run(&mut conn).await?;
        println!("All migrations completed");
    }
    
    Ok(())
}
```

### Example 3: API Client CLI

```yaml
app_name: api-client
language: rust
rust_binary_name: apicli
rust_crates:
  - name: reqwest
    version: "0.11"
    features: ["json", "rustls-tls"]
  - name: tokio
    version: "1.0"
    features: ["full"]
    
commands:
  - name: request
    description: Make API request
    rust_async: true
    arguments:
      - name: method
        type: choice
        choices: [GET, POST, PUT, DELETE, PATCH]
        required: true
      - name: url
        type: string
        required: true
    options:
      - name: data
        type: string
        short: d
        description: Request body (JSON)
      - name: header
        type: string
        short: H
        multiple: true
        description: Headers (format: "Key: Value")
      - name: output
        type: choice
        choices: [json, yaml, table, raw]
        default: json
```

Implementation:

```rust
use reqwest::{Client, Method};
use serde_json::Value;

pub async fn on_request_async(args: &Args) -> Result<()> {
    let method = args.raw_args.get("method")
        .and_then(|m| m.parse::<Method>().ok())
        .unwrap_or(Method::GET);
    let url = args.raw_args.get("url").unwrap();
    let data = args.raw_args.get("data");
    let headers = args.raw_args.get("header")
        .map(|h| parse_headers(h))
        .unwrap_or_default();
    let output_format = args.raw_args.get("output")
        .map(|s| s.as_str())
        .unwrap_or("json");
    
    let client = Client::new();
    let mut request = client.request(method.clone(), url);
    
    // Add headers
    for (key, value) in headers {
        request = request.header(key, value);
    }
    
    // Add body if provided
    if let Some(body) = data {
        request = request.body(body.clone());
        request = request.header("Content-Type", "application/json");
    }
    
    let response = request.send().await?;
    let status = response.status();
    let body = response.text().await?;
    
    println!("Status: {}", status);
    
    match output_format {
        "json" => {
            let json: Value = serde_json::from_str(&body)?;
            println!("{}", serde_json::to_string_pretty(&json)?);
        }
        "yaml" => {
            let json: Value = serde_json::from_str(&body)?;
            println!("{}", serde_yaml::to_string(&json)?);
        }
        "raw" => {
            println!("{}", body);
        }
        _ => {
            println!("{}", body);
        }
    }
    
    Ok(())
}
```

## Troubleshooting

### Common Issues

1. **Binary not found after cargo install**
   ```bash
   # Ensure cargo bin directory is in PATH
   export PATH="$HOME/.cargo/bin:$PATH"
   ```

2. **Linking errors with system libraries**
   ```toml
   # Use vendored OpenSSL
   [dependencies]
   openssl = { version = "0.10", features = ["vendored"] }
   ```

3. **Cross-compilation issues**
   ```bash
   # Install cross
   cargo install cross
   
   # Build for Linux musl (static binary)
   cross build --target x86_64-unknown-linux-musl --release
   ```

4. **Large binary sizes**
   ```toml
   [profile.release]
   opt-level = "z"     # Optimize for size
   lto = true          # Link-time optimization
   codegen-units = 1   # Single codegen unit
   strip = true        # Strip symbols
   panic = "abort"     # Smaller panic handler
   ```

### Debugging Tips

1. **Enable debug logging**:
   ```bash
   RUST_LOG=debug mycli command
   RUST_BACKTRACE=1 mycli command
   ```

2. **Use cargo expand**:
   ```bash
   cargo install cargo-expand
   cargo expand commands
   ```

3. **Profile performance**:
   ```bash
   cargo install flamegraph
   cargo flamegraph --bin mycli -- command
   ```

### Platform-Specific Issues

**Windows**:
```rust
#[cfg(windows)]
fn setup_console() {
    // Enable ANSI colors on Windows
    let _ = ansi_term::enable_ansi_support();
}
```

**macOS**:
```rust
#[cfg(target_os = "macos")]
fn get_config_dir() -> PathBuf {
    dirs::home_dir()
        .map(|h| h.join("Library/Application Support/mycli"))
        .unwrap_or_else(|| PathBuf::from("."))
}
```

## Best Practices

### 1. Error Handling

Use anyhow for applications, thiserror for libraries:

```rust
use thiserror::Error;

#[derive(Error, Debug)]
pub enum CliError {
    #[error("Configuration error: {0}")]
    Config(String),
    
    #[error("Network error: {0}")]
    Network(#[from] reqwest::Error),
    
    #[error("IO error: {0}")]
    Io(#[from] std::io::Error),
}
```

### 2. Performance

- Use `&str` instead of `String` where possible
- Leverage Rust's zero-cost abstractions
- Use rayon for CPU-bound parallel tasks
- Profile before optimizing

### 3. Security

- Validate all user input
- Use secure defaults
- Avoid shell execution when possible
- Sanitize file paths

### 4. Testing

- Write tests for all public APIs
- Use property-based testing for complex logic
- Test error conditions
- Benchmark performance-critical code

### 5. Documentation

- Document all public items
- Include examples in doc comments
- Keep README up to date
- Generate API docs with `cargo doc`

### 6. Versioning

Follow semantic versioning:
- MAJOR: Breaking API changes
- MINOR: New features (backward compatible)
- PATCH: Bug fixes

### 7. CI/CD

Example GitHub Actions workflow:

```yaml
name: CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest, macOS-latest]
        rust: [stable, nightly]
    steps:
    - uses: actions/checkout@v2
    - uses: actions-rs/toolchain@v1
      with:
        toolchain: ${{ matrix.rust }}
    - run: cargo build --all-features
    - run: cargo test --all-features
    - run: cargo clippy -- -D warnings
```

---

This guide covers the complete lifecycle of building Rust CLIs with Goobits. The generated code provides a solid foundation that you can extend with your business logic while maintaining Rust best practices and idioms.