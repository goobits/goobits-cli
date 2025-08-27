//! Hook implementations for Rust CLI demo

use std::error::Error;

/// Handle greet command
pub fn on_greet(
    name: &str, 
    message: &str, 
    style: Option<&str>, 
    count: Option<i32>, 
    uppercase: bool, 
    language: Option<&str>, 
    _verbose: bool, 
    _config: Option<&str>
) -> Result<(), Box<dyn Error>> {
    let message = if message.is_empty() { "Hello" } else { message };
    let style = style.unwrap_or("casual");
    let count = count.unwrap_or(1);
    let _language = language.unwrap_or("en");
    
    let mut greeting = format!("{}, {}", message, name);
    
    // Handle style variations
    greeting = match style {
        "formal" => format!("{}.", greeting),
        "excited" => format!("{}!!!", greeting),
        _ => format!("{}!", greeting), // casual
    };
    
    if uppercase {
        greeting = greeting.to_uppercase();
    }
    
    // Repeat greeting based on count
    for _i in 0..count {
        println!("{}", greeting);
    }
    
    println!("Welcome to the Rust CLI demo, {}!", name);
    Ok(())
}

/// Handle info command  
pub fn on_info(
    format: Option<&str>, 
    verbose: bool, 
    sections: Option<&str>, 
    _global_verbose: bool, 
    _config: Option<&str>
) -> Result<(), Box<dyn Error>> {
    let format = format.unwrap_or("text");
    let _sections = sections.unwrap_or("all");
    
    if format == "json" {
        println!("{{");
        println!("  \"rust_version\": \"{}\",", env!("CARGO_PKG_VERSION"));
        println!("  \"platform\": \"{}\",", std::env::consts::OS);
        println!("  \"architecture\": \"{}\"", std::env::consts::ARCH);
        println!("}}");
    } else {
        println!("🦀 Rust CLI Information");
        println!("{}", "-".repeat(30));
        println!("Rust Version: {}", env!("CARGO_PKG_VERSION"));
        println!("Platform: {}", std::env::consts::OS);
        println!("Architecture: {}", std::env::consts::ARCH);
        
        if verbose {
            println!("Target: {}", std::env::consts::FAMILY);
        }
    }
    
    Ok(())
}