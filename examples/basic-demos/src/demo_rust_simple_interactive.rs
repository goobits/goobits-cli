use rustyline::error::ReadlineError;
use rustyline::{DefaultEditor, Result};
use std::collections::HashMap;

mod hooks;

pub struct DemorustsimplecliInteractive {
    editor: DefaultEditor,
    commands: HashMap<String, fn(&[&str]) -> Result<()>>,
}

impl DemorustsimplecliInteractive {
    pub fn new() -> Result<Self> {
        let mut editor = DefaultEditor::new()?;
        let mut commands = HashMap::new();
        
        // Register commands        commands.insert("hello".to_string(), |args| {
            match hooks::on_hello(args) {
                Ok(_) => Ok(()),
                Err(e) => {
                    eprintln!("Error: {}", e);
                    Ok(())
                }
            }
        });        
        Ok(Self { editor, commands })
    }
    
    pub fn run(&mut self) -> Result<()> {
        println!("Welcome to Demo Rust Simple CLI interactive mode. Type 'help' for commands, 'exit' to quit.");
        
        let prompt = "demo_rust_simple> ";
        
        loop {
            let readline = self.editor.readline(prompt);
            match readline {
                Ok(line) => {
                    if line.trim().is_empty() {
                        continue;
                    }
                    
                    self.editor.add_history_entry(line.as_str())?;
                    
                    let parts: Vec<&str> = line.trim().split_whitespace().collect();
                    if parts.is_empty() {
                        continue;
                    }
                    
                    match parts[0] {
                        "exit" | "quit" => {
                            println!("Goodbye!");
                            break;
                        }
                        "help" => {
                            self.show_help();
                        }
                        cmd => {
                            if let Some(handler) = self.commands.get(cmd) {
                                let args = &parts[1..];
                                if let Err(e) = handler(args) {
                                    eprintln!("Error executing command: {}", e);
                                }
                            } else {
                                println!("Unknown command: {}", cmd);
                                println!("Type 'help' for available commands");
                            }
                        }
                    }
                }
                Err(ReadlineError::Interrupted) => {
                    println!("^C");
                    continue;
                }
                Err(ReadlineError::Eof) => {
                    println!("^D");
                    break;
                }
                Err(err) => {
                    eprintln!("Error: {:?}", err);
                    break;
                }
            }
        }
        
        Ok(())
    }
    
    fn show_help(&self) {
        println!("\nAvailable commands:");
        println!("  {:15} {}", "help", "Show available commands");
        println!("  {:15} {}", "exit", "Exit interactive mode");        println!("  {:15} {}", "hello", "Say hello");        println!();
    }
}

pub fn run_interactive() -> Result<()> {
    let mut interactive = DemorustsimplecliInteractive::new()?;
    interactive.run()
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_interactive_creation() {
        let result = DemorustsimplecliInteractive::new();
        assert!(result.is_ok());
    }
}