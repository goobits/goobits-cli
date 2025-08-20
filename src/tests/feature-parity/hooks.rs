use std::fs;
use std::io::{self, Write};
use std::path::Path;
use std::env;

pub fn on_hello(name: &str, greeting: Option<&str>, _verbose: bool, _config: Option<&str>) -> Result<(), Box<dyn std::error::Error>> {
    let greeting = greeting.unwrap_or("Hello");
    println!("{} {}", greeting, name);
    Ok(())
}

pub fn on_config_get(key: &str, _verbose: bool, _config: Option<&str>) -> Result<(), Box<dyn std::error::Error>> {
    let theme = env::var("TEST_CLI_THEME").unwrap_or_else(|_| "default".to_string());
    
    let value = match key {
        "theme" => theme,
        "api_key" => "".to_string(),
        "timeout" => "30".to_string(),
        _ => {
            eprintln!("Config key not found: {}", key);
            std::process::exit(1);
        }
    };
    
    println!("{}: {}", key, value);
    Ok(())
}

pub fn on_config_set(key: &str, value: &str, _verbose: bool, _config: Option<&str>) -> Result<(), Box<dyn std::error::Error>> {
    println!("Setting {} to {}", key, value);
    Ok(())
}

pub fn on_config_list(_verbose: bool, _config: Option<&str>) -> Result<(), Box<dyn std::error::Error>> {
    println!("theme: default");
    println!("api_key: ");
    println!("timeout: 30");
    Ok(())
}

pub fn on_config_reset(force: bool, _verbose: bool, _config: Option<&str>) -> Result<(), Box<dyn std::error::Error>> {
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

pub fn on_fail(code: Option<i32>, _verbose: bool, _config: Option<&str>) -> Result<(), Box<dyn std::error::Error>> {
    let exit_code = code.unwrap_or(1);
    eprintln!("Error: Command failed with exit code {}", exit_code);
    std::process::exit(exit_code);
}

pub fn on_echo(words: Vec<&str>, _verbose: bool, _config: Option<&str>) -> Result<(), Box<dyn std::error::Error>> {
    if !words.is_empty() {
        println!("{}", words.join(" "));
    }
    Ok(())
}

pub fn on_file_create(path: &str, content: Option<&str>, _verbose: bool, _config: Option<&str>) -> Result<(), Box<dyn std::error::Error>> {
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

pub fn on_file_delete(path: &str, _verbose: bool, _config: Option<&str>) -> Result<(), Box<dyn std::error::Error>> {
    match fs::remove_file(path) {
        Ok(_) => {
            println!("Deleted file: {}", path);
            Ok(())
        }
        Err(e) => {
            if e.kind() == io::ErrorKind::NotFound {
                eprintln!("File not found: {}", path);
            } else if e.kind() == io::ErrorKind::PermissionDenied {
                eprintln!("Permission denied: {}", path);
            } else {
                eprintln!("Error deleting file: {}", e);
            }
            std::process::exit(1);
        }
    }
}