//! Utility functions for Test Rust CLI
//! Auto-generated from test-rust-cli.yaml

use anyhow::{Context, Result};
use std::io::{self, Write};
use std::path::Path;
use std::process::{Command, Stdio};

/// Terminal output utilities
pub mod output {
    use super::*;
    
    /// Print an informational message
    pub fn info(message: &str) {
        if is_tty() {
            println!("🔹 {message}");
        } else {
            println!("INFO: {message}");
        }
    }
    
    /// Print a success message
    pub fn success(message: &str) {
        if is_tty() {
            println!("✅ {message}");
        } else {
            println!("SUCCESS: {message}");
        }
    }
    
    /// Print a warning message
    pub fn warning(message: &str) {
        if is_tty() {
            eprintln!("⚠️  {message}");
        } else {
            eprintln!("WARNING: {message}");
        }
    }
    
    /// Print an error message
    pub fn error(message: &str) {
        if is_tty() {
            eprintln!("❌ {message}");
        } else {
            eprintln!("ERROR: {message}");
        }
    }
    
    /// Print a debug message (only in debug builds)
    pub fn debug(message: &str) {
        #[cfg(debug_assertions)]
        {
            if is_tty() {
                eprintln!("🔧 DEBUG: {message}");
            } else {
                eprintln!("DEBUG: {message}");
            }
        }
    }
    
    /// Print a progress message
    pub fn progress(message: &str) {
        if is_tty() {
            print!("🔄 {message}...");
        } else {
            print!("PROGRESS: {message}...");
        }
        io::stdout().flush().unwrap_or_default();
    }
    
    /// Complete a progress message
    pub fn progress_done() {
        println!(" ✓");
    }
    
    /// Fail a progress message
    pub fn progress_failed() {
        println!(" ✗");
    }
}

/// Input/interaction utilities
pub mod input {
    use super::*;
    
    /// Prompt user for input
    pub fn prompt(message: &str) -> Result<String> {
        if is_tty() {
            print!("❓ {message}: ");
        } else {
            print!("PROMPT {message}: ");
        }
        io::stdout().flush()?;
        
        let mut input = String::new();
        io::stdin().read_line(&mut input)?;
        Ok(input.trim().to_string())
    }
    
    /// Prompt user for input with a default value
    pub fn prompt_with_default(message: &str, default: &str) -> Result<String> {
        if is_tty() {
            print!("❓ {message} [{default}]: ");
        } else {
            print!("PROMPT {message} [{default}]: ");
        }
        io::stdout().flush()?;
        
        let mut input = String::new();
        io::stdin().read_line(&mut input)?;
        let input = input.trim();
        
        if input.is_empty() {
            Ok(default.to_string())
        } else {
            Ok(input.to_string())
        }
    }
    
    /// Prompt user for confirmation (y/n)
    pub fn confirm(message: &str) -> Result<bool> {
        loop {
            let input = prompt(&format!("{message} (y/n)"))?;
            match input.to_lowercase().as_str() {
                "y" | "yes" => return Ok(true),
                "n" | "no" => return Ok(false),
                _ => {
                    output::warning("Please enter 'y' or 'n'");
                    continue;
                }
            }
        }
    }
    
    /// Prompt user to select from a list of options
    pub fn select(message: &str, options: &[&str]) -> Result<usize> {
        println!("❓ {message}");
        for (i, option) in options.iter().enumerate() {
            println!("  {}. {option}", i + 1);
        }
        
        loop {
            let input = prompt("Enter selection number")?;
            if let Ok(selection) = input.parse::<usize>() {
                if selection > 0 && selection <= options.len() {
                    return Ok(selection - 1);
                }
            }
            output::warning(&format!("Please enter a number between 1 and {}", options.len()));
        }
    }
}

/// File system utilities
pub mod fs {
    use super::*;
    use std::fs;
    use std::path::PathBuf;
    
    /// Ensure a directory exists, creating it if necessary
    pub fn ensure_dir(path: &Path) -> Result<()> {
        if !path.exists() {
            fs::create_dir_all(path)
                .with_context(|| format!("Failed to create directory: {}", path.display()))?;
        }
        Ok(())
    }
    
    /// Check if a file exists and is readable
    pub fn is_readable_file(path: &Path) -> bool {
        path.is_file() && fs::metadata(path).is_ok()
    }
    
    /// Check if a directory exists and is accessible
    pub fn is_accessible_dir(path: &Path) -> bool {
        path.is_dir() && fs::read_dir(path).is_ok()
    }
    
    /// Copy a file with progress indication
    pub fn copy_file(src: &Path, dst: &Path) -> Result<()> {
        output::progress(&format!("Copying {}", src.file_name().unwrap_or_default().to_string_lossy()));
        
        if let Some(parent) = dst.parent() {
            ensure_dir(parent)?;
        }
        
        fs::copy(src, dst)
            .with_context(|| format!("Failed to copy {} to {}", src.display(), dst.display()))?;
        
        output::progress_done();
        Ok(())
    }
    
    /// Read a file to string with better error messages
    pub fn read_to_string(path: &Path) -> Result<String> {
        fs::read_to_string(path)
            .with_context(|| format!("Failed to read file: {}", path.display()))
    }
    
    /// Write string to file with directory creation
    pub fn write_string(path: &Path, content: &str) -> Result<()> {
        if let Some(parent) = path.parent() {
            ensure_dir(parent)?;
        }
        
        fs::write(path, content)
            .with_context(|| format!("Failed to write file: {}", path.display()))
    }
    
    /// Find files matching a pattern in a directory
    pub fn find_files(dir: &Path, extension: &str) -> Result<Vec<PathBuf>> {
        let mut files = Vec::new();
        
        if !dir.is_dir() {
            return Ok(files);
        }
        
        for entry in fs::read_dir(dir)? {
            let entry = entry?;
            let path = entry.path();
            
            if path.is_file() {
                if let Some(ext) = path.extension() {
                    if ext == extension {
                        files.push(path);
                    }
                }
            }
        }
        
        files.sort();
        Ok(files)
    }
}

/// Process execution utilities
pub mod process {
    use super::*;
    
    /// Execute a command and return success status
    pub fn execute(command: &str, args: &[&str]) -> Result<bool> {
        let status = Command::new(command)
            .args(args)
            .stdin(Stdio::null())
            .status()
            .with_context(|| format!("Failed to execute: {command} {}", args.join(" ")))?;
        
        Ok(status.success())
    }
    
    /// Execute a command and capture output
    pub fn execute_output(command: &str, args: &[&str]) -> Result<String> {
        let output = Command::new(command)
            .args(args)
            .stdin(Stdio::null())
            .output()
            .with_context(|| format!("Failed to execute: {command} {}", args.join(" ")))?;
        
        if output.status.success() {
            Ok(String::from_utf8_lossy(&output.stdout).to_string())
        } else {
            let stderr = String::from_utf8_lossy(&output.stderr);
            anyhow::bail!("Command failed: {stderr}");
        }
    }
    
    /// Execute a command with inherited stdio
    pub fn execute_interactive(command: &str, args: &[&str]) -> Result<bool> {
        let status = Command::new(command)
            .args(args)
            .status()
            .with_context(|| format!("Failed to execute: {command} {}", args.join(" ")))?;
        
        Ok(status.success())
    }
    
    /// Check if a command is available on the system
    pub fn command_exists(command: &str) -> bool {
        Command::new("which")
            .arg(command)
            .stdout(Stdio::null())
            .stderr(Stdio::null())
            .status()
            .map(|status| status.success())
            .unwrap_or(false)
    }
}

/// String utilities
pub mod string {
    /// Convert string to snake_case
    pub fn to_snake_case(s: &str) -> String {
        let mut result = String::new();
        let chars = s.chars();
        
        for ch in chars {
            if ch.is_uppercase() {
                if !result.is_empty() && !result.ends_with('_') {
                    result.push('_');
                }
                result.push(ch.to_lowercase().next().unwrap());
            } else if ch == '-' || ch == ' ' {
                result.push('_');
            } else {
                result.push(ch);
            }
        }
        
        result
    }
    
    /// Convert string to kebab-case
    pub fn to_kebab_case(s: &str) -> String {
        let mut result = String::new();
        let chars = s.chars();
        
        for ch in chars {
            if ch.is_uppercase() {
                if !result.is_empty() && !result.ends_with('-') {
                    result.push('-');
                }
                result.push(ch.to_lowercase().next().unwrap());
            } else if ch == '_' || ch == ' ' {
                result.push('-');
            } else {
                result.push(ch);
            }
        }
        
        result
    }
    
    /// Truncate string to max length with ellipsis
    pub fn truncate(s: &str, max_len: usize) -> String {
        if s.len() <= max_len {
            s.to_string()
        } else if max_len <= 3 {
            "...".to_string()
        } else {
            format!("{}...", &s[..max_len - 3])
        }
    }
}

/// Time utilities
pub mod time {
    use std::time::{Duration, SystemTime, UNIX_EPOCH};
    
    /// Format duration in human-readable format
    pub fn format_duration(duration: Duration) -> String {
        let secs = duration.as_secs();
        
        if secs < 60 {
            format!("{secs}s")
        } else if secs < 3600 {
            format!("{}m{}s", secs / 60, secs % 60)
        } else {
            format!("{}h{}m{}s", secs / 3600, (secs % 3600) / 60, secs % 60)
        }
    }
    
    /// Get current Unix timestamp
    pub fn unix_timestamp() -> u64 {
        SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .unwrap_or_default()
            .as_secs()
    }
    
    /// Format timestamp as human-readable string
    pub fn format_timestamp(timestamp: u64) -> String {
        use chrono::{DateTime, Utc};
        
        let dt = DateTime::<Utc>::from_timestamp(timestamp as i64, 0)
            .unwrap_or_else(Utc::now);
        
        dt.format("%Y-%m-%d %H:%M:%S UTC").to_string()
    }
}

/// Check if running in a TTY (interactive terminal)
pub fn is_tty() -> bool {
    atty::is(atty::Stream::Stdout)
}

/// Get the current executable path
pub fn current_exe() -> Result<std::path::PathBuf> {
    std::env::current_exe().context("Failed to get current executable path")
}

/// Get the current working directory
pub fn current_dir() -> Result<std::path::PathBuf> {
    std::env::current_dir().context("Failed to get current working directory")
}

/// Check if running in debug mode
pub fn is_debug() -> bool {
    cfg!(debug_assertions)
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_string_conversions() {
        assert_eq!(string::to_snake_case("HelloWorld"), "hello_world");
        assert_eq!(string::to_snake_case("hello-world"), "hello_world");
        assert_eq!(string::to_kebab_case("HelloWorld"), "hello-world");
        assert_eq!(string::to_kebab_case("hello_world"), "hello-world");
    }
    
    #[test]
    fn test_string_truncate() {
        assert_eq!(string::truncate("hello world", 20), "hello world");
        assert_eq!(string::truncate("hello world", 8), "hello...");
        assert_eq!(string::truncate("hello world", 3), "...");
    }
    
    #[test]
    fn test_time_formatting() {
        use std::time::Duration;
        
        assert_eq!(time::format_duration(Duration::from_secs(30)), "30s");
        assert_eq!(time::format_duration(Duration::from_secs(90)), "1m30s");
        assert_eq!(time::format_duration(Duration::from_secs(3661)), "1h1m1s");
    }
    
    #[test]
    fn test_process_command_exists() {
        // Most systems should have these commands
        assert!(process::command_exists("echo"));
        assert!(!process::command_exists("definitely_not_a_real_command_12345"));
    }
}