/**
 * Hook implementations for test CLI commands (Rust).
 */
use clap::ArgMatches;
use anyhow::Result;

pub fn on_hello(matches: &ArgMatches) -> Result<i32> {
    let name = matches.get_one::<String>("name");
    let loud = matches.get_flag("loud");
    
    let mut greeting = if let Some(n) = name {
        format!("Hello, {}!", n)
    } else {
        "Hello, World!".to_string()
    };
    
    if loud {
        greeting = greeting.to_uppercase();
    }
    
    println!("{}", greeting);
    Ok(0)
}

pub fn on_version(_matches: &ArgMatches) -> Result<i32> {
    println!("Test CLI v0.1.0");
    Ok(0)
}