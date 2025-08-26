use rustyline::error::ReadlineError;
use rustyline::{DefaultEditor, Result};
use std::collections::HashMap;

mod hooks;

pub struct QuadruplecheckcliInteractive {
    editor: DefaultEditor,
    commands: HashMap<String, fn(&[&str]) -> Result<()>>,
}

impl QuadruplecheckcliInteractive {
    pub fn new() -> Result<Self> {
        let mut editor = DefaultEditor::new()?;
        let mut commands = HashMap::new();
        
        // Register commands        commands.insert("greet".to_string(), |args| {
            match hooks::on_greet(args) {
                Ok(_) => Ok(()),
                Err(e) => {
                    eprintln!("Error: {}", e);
                    Ok(())
                }
            }
        });        commands.insert("info".to_string(), |args| {
            match hooks::on_info(args) {
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
        println!("Welcome to Quadruple Check CLI interactive mode. Type 'help' for commands, 'exit' to quit.");
        
        let prompt = "Quadruple Check CLI> ";
        
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
        println!("  {:15} {}", "exit", "Exit interactive mode");        println!("  {:15} {}", "greet", "Greet someone with multi-language support");        println!("  {:15} {}", "info", "Display system information");        println!();
    }
}

pub fn run_interactive() -> Result<()> {
    let mut interactive = QuadruplecheckcliInteractive::new()?;
    interactive.run()
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_interactive_creation() {
        let result = QuadruplecheckcliInteractive::new();
        assert!(result.is_ok());
    }
}