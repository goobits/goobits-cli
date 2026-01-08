use std::fs;
use std::io::{self, Write};
use std::path::Path;
use std::env;
use clap::ArgMatches;
use anyhow::{Result, anyhow};

pub fn on_hello(matches: &ArgMatches) -> Result<()> {
    let name = matches.get_one::<String>("name").map(|s| s.as_str()).unwrap_or("");
    let greeting = matches.get_one::<String>("greeting").map(|s| s.as_str()).unwrap_or("Hello");
    println!("{} {}", greeting, name);
    Ok(())
}

pub fn on_config_get(matches: &ArgMatches) -> Result<()> {
    let key = matches.get_one::<String>("key").map(|s| s.as_str()).unwrap_or("");
    let theme = env::var("TEST_CLI_THEME").unwrap_or_else(|_| "default".to_string());
    
    let value = match key {
        "theme" => theme,
        "api_key" => "".to_string(),
        "timeout" => "30".to_string(),
        _ => {
            return Err(anyhow!("Config key not found: {}", key));
        }
    };
    
    println!("{}: {}", key, value);
    Ok(())
}

pub fn on_config_set(matches: &ArgMatches) -> Result<()> {
    let key = matches.get_one::<String>("key").map(|s| s.as_str()).unwrap_or("");
    let value = matches.get_one::<String>("value").map(|s| s.as_str()).unwrap_or("");
    println!("Setting {} to {}", key, value);
    Ok(())
}

pub fn on_config_list(_matches: &ArgMatches) -> Result<()> {
    println!("theme: default");
    println!("api_key: ");
    println!("timeout: 30");
    Ok(())
}

pub fn on_config_reset(matches: &ArgMatches) -> Result<()> {
    let force = matches.get_flag("force");
    if !force {
        print!("Are you sure you want to reset the configuration? (y/N): ");
        io::stdout().flush()?;
        
        let mut input = String::new();
        io::stdin().read_line(&mut input)?;
        
        if input.trim().to_lowercase() != "y" {
            println!("Reset cancelled");
            return Ok(());
        }
    }
    
    println!("Configuration reset to defaults");
    Ok(())
}

pub fn on_fail(matches: &ArgMatches) -> Result<()> {
    let exit_code = matches.get_one::<String>("code")
        .and_then(|s| s.parse::<i32>().ok())
        .unwrap_or(1);
    eprintln!("Error: Command failed with exit code {}", exit_code);
    std::process::exit(exit_code);
}

pub fn on_echo(matches: &ArgMatches) -> Result<()> {
    let words = matches.get_one::<String>("words").map(|s| s.as_str()).unwrap_or("");
    if !words.is_empty() {
        println!("{}", words);
    }
    Ok(())
}

pub fn on_file_create(matches: &ArgMatches) -> Result<()> {
    let path = matches.get_one::<String>("path").map(|s| s.as_str()).unwrap_or("");
    let content = matches.get_one::<String>("content").map(|s| s.as_str());
    let file_path = Path::new(path);
    
    if let Some(parent) = file_path.parent() {
        fs::create_dir_all(parent)?;
    }
    
    if let Some(content) = content {
        fs::write(file_path, content)?;
    } else {
        fs::write(file_path, "")?;
    }
    
    println!("Created file: {}", path);
    Ok(())
}

pub fn on_file_delete(matches: &ArgMatches) -> Result<()> {
    let path = matches.get_one::<String>("path").map(|s| s.as_str()).unwrap_or("");
    match fs::remove_file(path) {
        Ok(_) => {
            println!("Deleted file: {}", path);
            Ok(())
        }
        Err(e) => {
            if e.kind() == io::ErrorKind::NotFound {
                Err(anyhow!("File not found: {}", path))
            } else if e.kind() == io::ErrorKind::PermissionDenied {
                Err(anyhow!("Permission denied: {}", path))
            } else {
                Err(anyhow!("Error deleting file: {}", e))
            }
        }
    }
}

pub fn on_config(_matches: &ArgMatches) -> Result<()> {
    Ok(())
}

pub fn on_file(_matches: &ArgMatches) -> Result<()> {
    Ok(())
}