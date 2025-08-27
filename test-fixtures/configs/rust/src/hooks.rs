// Hook implementations for test Rust CLI

use clap::ArgMatches;
use anyhow::Result;

pub fn on_hello(_matches: &ArgMatches) -> Result<()> {
    println!("Hello from Rust CLI!");
    Ok(())
}

pub fn on_build(_matches: &ArgMatches) -> Result<()> {
    println!("Build command executed!");
    Ok(())
}

pub fn on_build_project(_matches: &ArgMatches) -> Result<()> {
    println!("Building project...");
    Ok(())
}

pub fn on_serve(_matches: &ArgMatches) -> Result<()> {
    println!("Starting server...");
    Ok(())
}