//! Hook functions for Test Rust CLI

//! Auto-generated from goobits.yaml

//! 

//! Implement your business logic in these hook functions.

//! Each command will call its corresponding hook function.



use clap::ArgMatches;

use anyhow::Result;



/// Hook function for 'hello' command

pub fn on_hello(matches: &ArgMatches) -> Result<()> {

    // Get the name argument
    let name = matches.get_one::<String>("name").expect("Name is required");
    
    // Check if uppercase flag is set
    let uppercase = matches.get_flag("uppercase");
    
    // Create greeting
    let greeting = if uppercase {
        format!("HELLO, {}!", name.to_uppercase())
    } else {
        format!("Hello, {}!", name)
    };
    
    println!("{}", greeting);
    Ok(())

}



/// Hook function for 'info' command

pub fn on_info(matches: &ArgMatches) -> Result<()> {

    // Return error indicating this hook is not implemented
    // This allows the main CLI to show placeholder behavior
    Err(anyhow::anyhow!("Hook function 'on_info' not implemented"))

}



