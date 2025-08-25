#!/usr/bin/env rust
//! Hook implementations for Rust CLI demo

use clap::ArgMatches;
use anyhow::Result;
use std::env;

/// Handle greet command
pub fn on_greet(matches: &ArgMatches) -> Result<()> {
    let name = matches.get_one::<String>("name").unwrap();
    let message = matches.get_one::<String>("message").unwrap_or(&"Hello".to_string());
    let style = matches.get_one::<String>("style").unwrap_or(&"casual".to_string());
    let count = *matches.get_one::<i32>("count").unwrap_or(&1);
    let uppercase = matches.get_flag("uppercase");
    let _language = matches.get_one::<String>("language").unwrap_or(&"en".to_string());
    
    let mut greeting = format!("{}, {}", message, name);
    
    // Handle style variations
    greeting = match style.as_str() {
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
pub fn on_info(matches: &ArgMatches) -> Result<()> {
    let format = matches.get_one::<String>("format").unwrap_or(&"text".to_string());
    let verbose = matches.get_flag("verbose");
    let _sections = matches.get_one::<String>("sections").unwrap_or(&"all".to_string());
    
    if format == "json" {
        println!("{{");
        println!("  \"rust_version\": \"{}\",", env!("CARGO_PKG_VERSION"));
        println!("  \"platform\": \"{}\",", env::consts::OS);
        println!("  \"architecture\": \"{}\"", env::consts::ARCH);
        println!("}}");
    } else {
        println!("🦀 Rust CLI Information");
        println!("{}", "-".repeat(30));
        println!("Rust Version: {}", env!("CARGO_PKG_VERSION"));
        println!("Platform: {}", env::consts::OS);
        println!("Architecture: {}", env::consts::ARCH);
        
        if verbose {
            println!("Target: {}", env::consts::FAMILY);
        }
    }
    
    Ok(())
}