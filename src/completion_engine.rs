/*!
Universal completion engine for goobits-generated CLIs (Rust)
Reads goobits.yaml at runtime and provides context-aware completions
*/

use std::collections::HashMap;
use std::env;
use std::fs;
use std::path::Path;
use serde::{Deserialize, Serialize};
use serde_yaml;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CliOption {
    pub name: String,
    pub short: Option<String>,
    #[serde(rename = "type")]
    pub option_type: Option<String>,
    pub choices: Option<Vec<String>>,
    pub desc: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Argument {
    pub name: String,
    pub required: Option<bool>,
    pub choices: Option<Vec<String>>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Command {
    pub desc: Option<String>,
    pub args: Option<Vec<Argument>>,
    pub options: Option<Vec<CliOption>>,
    pub subcommands: Option<HashMap<String, Command>>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CliConfig {
    pub commands: Option<HashMap<String, Command>>,
    pub options: Option<Vec<CliOption>>,
    pub enable_upgrade_command: Option<bool>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Config {
    pub cli: Option<CliConfig>,
}

#[derive(Debug, Clone)]
pub struct Context {
    pub context_type: ContextType,
    pub level: i32,
    pub current_command: Option<String>,
    pub subcommand: Option<String>,
    pub last_token: String,
    pub previous_token: String,
    pub partial: Option<String>,
    pub option: Option<String>,
}

#[derive(Debug, Clone, PartialEq)]
pub enum ContextType {
    Command,
    Subcommand,
    Option,
    OptionValue,
    Unknown,
}

pub struct CompletionEngine {
    config_path: String,
    config: Config,
}

impl CompletionEngine {
    pub fn new(config_path: Option<String>) -> Self {
        let config_path = config_path.unwrap_or_else(|| Self::find_config());
        let config = Self::load_config(&config_path);
        
        CompletionEngine {
            config_path,
            config,
        }
    }

    fn find_config() -> String {
        let mut current = env::current_dir().unwrap_or_else(|_| Path::new(".").to_path_buf());
        
        // Search up the directory tree
        loop {
            let config_file = current.join("goobits.yaml");
            if config_file.exists() {
                return config_file.to_string_lossy().to_string();
            }
            
            match current.parent() {
                Some(parent) => current = parent.to_path_buf(),
                None => break,
            }
        }
        
        // Fallback to current directory
        "./goobits.yaml".to_string()
    }

    fn load_config(config_path: &str) -> Config {
        match fs::read_to_string(config_path) {
            Ok(content) => {
                match serde_yaml::from_str(&content) {
                    Ok(config) => config,
                    Err(_) => Config { cli: None },
                }
            }
            Err(_) => Config { cli: None },
        }
    }

    pub fn get_completions(&self, _shell: &str, current_line: &str, cursor_pos: Option<usize>) -> Vec<String> {
        match self.get_completions_impl(current_line, cursor_pos) {
            Ok(completions) => {
                let mut unique_completions: Vec<String> = completions.into_iter().collect::<std::collections::HashSet<_>>().into_iter().collect();
                unique_completions.sort();
                unique_completions
            }
            Err(_) => Vec::new(),
        }
    }

    fn get_completions_impl(&self, current_line: &str, cursor_pos: Option<usize>) -> Result<Vec<String>, Box<dyn std::error::Error>> {
        // Parse the command line
        let tokens = self.parse_command_line(current_line, cursor_pos)?;
        let context = self.analyze_context(&tokens);
        
        // Generate completions based on context
        self.generate_completions(&context)
    }

    fn parse_command_line(&self, line: &str, cursor_pos: Option<usize>) -> Result<Vec<String>, Box<dyn std::error::Error>> {
        let cursor_pos = cursor_pos.unwrap_or(line.len());
        
        // Extract the relevant part of the line up to cursor
        let relevant_line = &line[..cursor_pos.min(line.len())];
        
        // Simple tokenization (could be enhanced for complex cases)
        let mut tokens = Vec::new();
        let mut current_token = String::new();
        let mut in_quotes = false;
        let mut quote_char = None;
        
        for ch in relevant_line.chars() {
            match ch {
                '"' | '\'' if !in_quotes => {
                    in_quotes = true;
                    quote_char = Some(ch);
                    current_token.push(ch);
                }
                ch if Some(ch) == quote_char && in_quotes => {
                    in_quotes = false;
                    current_token.push(ch);
                    quote_char = None;
                }
                ch if ch.is_whitespace() && !in_quotes => {
                    if !current_token.is_empty() {
                        tokens.push(current_token.clone());
                        current_token.clear();
                    }
                }
                ch => {
                    current_token.push(ch);
                }
            }
        }
        
        // Add final token if exists
        if !current_token.is_empty() {
            tokens.push(current_token);
        }
        
        Ok(tokens)
    }

    fn analyze_context(&self, tokens: &[String]) -> Context {
        if tokens.is_empty() {
            return Context {
                context_type: ContextType::Command,
                level: 0,
                current_command: None,
                subcommand: None,
                last_token: String::new(),
                previous_token: String::new(),
                partial: None,
                option: None,
            };
        }
        
        // Skip the program name
        let tokens = if tokens.len() > 0 { &tokens[1..] } else { tokens };
        
        if tokens.is_empty() {
            return Context {
                context_type: ContextType::Command,
                level: 0,
                current_command: None,
                subcommand: None,
                last_token: String::new(),
                previous_token: String::new(),
                partial: None,
                option: None,
            };
        }
        
        let last_token = tokens.last().cloned().unwrap_or_default();
        let previous_token = if tokens.len() > 1 {
            tokens[tokens.len() - 2].clone()
        } else {
            String::new()
        };
        
        let mut context = Context {
            context_type: ContextType::Unknown,
            level: 0,
            current_command: None,
            subcommand: None,
            last_token: last_token.clone(),
            previous_token: previous_token.clone(),
            partial: None,
            option: None,
        };
        
        // Check if we're completing an option
        if last_token.starts_with('-') {
            context.context_type = ContextType::Option;
            return context;
        }
        
        // Check if previous token was an option that expects a value
        if previous_token.starts_with('-') {
            context.context_type = ContextType::OptionValue;
            context.option = Some(previous_token);
            return context;
        }
        
        // Determine command/subcommand context
        let empty_commands = HashMap::new();
        let cli_commands = match &self.config.cli {
            Some(cli) => cli.commands.as_ref().unwrap_or(&empty_commands),
            None => &empty_commands,
        };
        
        if tokens.len() == 1 {
            // Completing top-level command
            context.context_type = ContextType::Command;
            context.level = 0;
            context.partial = Some(tokens[0].clone());
        } else if let Some(command_config) = cli_commands.get(&tokens[0]) {
            // We have a valid command, check for subcommands
            context.current_command = Some(tokens[0].clone());
            
            if command_config.subcommands.is_some() && tokens.len() == 2 {
                context.context_type = ContextType::Subcommand;
                context.level = 1;
                context.partial = Some(tokens[1].clone());
            } else if let Some(subcommands) = &command_config.subcommands {
                if tokens.len() > 2 && subcommands.contains_key(&tokens[1]) {
                    context.context_type = ContextType::Option;
                    context.subcommand = Some(tokens[1].clone());
                    context.level = 2;
                } else {
                    context.context_type = ContextType::Option;
                    context.level = 1;
                }
            } else {
                context.context_type = ContextType::Option;
                context.level = 1;
            }
        }
        
        context
    }

    fn generate_completions(&self, context: &Context) -> Result<Vec<String>, Box<dyn std::error::Error>> {
        let mut completions = Vec::new();
        
        match context.context_type {
            ContextType::Command => {
                completions.extend(self.get_command_completions(context));
            }
            ContextType::Subcommand => {
                completions.extend(self.get_subcommand_completions(context));
            }
            ContextType::Option => {
                completions.extend(self.get_option_completions(context));
            }
            ContextType::OptionValue => {
                completions.extend(self.get_option_value_completions(context));
            }
            ContextType::Unknown => {}
        }
        
        // Filter by partial match if applicable
        if let Some(partial) = &context.partial {
            let filtered: Vec<String> = completions
                .into_iter()
                .filter(|c| c.starts_with(partial))
                .collect();
            return Ok(filtered);
        }
        
        Ok(completions)
    }

    fn get_command_completions(&self, _context: &Context) -> Vec<String> {
        let mut commands = Vec::new();
        
        // CLI commands from config
        if let Some(cli) = &self.config.cli {
            if let Some(cli_commands) = &cli.commands {
                commands.extend(cli_commands.keys().cloned());
            }
        }
        
        // Built-in commands
        let mut builtin_commands = vec!["help", "version", "completion", "config"];
        
        // Check if upgrade is enabled
        let upgrade_enabled = self.config.cli
            .as_ref()
            .and_then(|cli| cli.enable_upgrade_command)
            .unwrap_or(true);
        
        if upgrade_enabled {
            builtin_commands.push("upgrade");
        }
        
        commands.extend(builtin_commands.into_iter().map(String::from));
        
        commands
    }

    fn get_subcommand_completions(&self, context: &Context) -> Vec<String> {
        let command = match &context.current_command {
            Some(cmd) => cmd,
            None => return Vec::new(),
        };
        
        // Handle built-in commands first
        match command.as_str() {
            "completion" => {
                return vec![
                    "generate".to_string(),
                    "install".to_string(),
                    "instructions".to_string(),
                ];
            }
            "config" => {
                return vec![
                    "get".to_string(),
                    "set".to_string(),
                    "reset".to_string(),
                    "path".to_string(),
                ];
            }
            _ => {}
        }
        
        // Handle user-defined commands
        let empty_commands = HashMap::new();
        let cli_commands = match &self.config.cli {
            Some(cli) => cli.commands.as_ref().unwrap_or(&empty_commands),
            None => return Vec::new(),
        };
        
        let command_config = match cli_commands.get(command) {
            Some(config) => config,
            None => return Vec::new(),
        };
        
        let subcommands = match &command_config.subcommands {
            Some(subs) => subs,
            None => return Vec::new(),
        };
        
        subcommands.keys().cloned().collect()
    }

    fn get_option_completions(&self, context: &Context) -> Vec<String> {
        let mut options = Vec::new();
        
        // Global options
        if let Some(cli) = &self.config.cli {
            if let Some(global_options) = &cli.options {
                for opt in global_options {
                    options.push(format!("--{}", opt.name));
                    if let Some(short) = &opt.short {
                        options.push(format!("-{}", short));
                    }
                }
            }
        }
        
        // Command-specific options
        if let Some(command) = &context.current_command {
            let empty_commands = HashMap::new();
            let cli_commands = match &self.config.cli {
                Some(cli) => cli.commands.as_ref().unwrap_or(&empty_commands),
                None => &empty_commands,
            };
            
            if let Some(mut command_config) = cli_commands.get(command).cloned() {
                // Check if we're in a subcommand
                if let Some(subcommand) = &context.subcommand {
                    if let Some(subcommands) = &command_config.subcommands {
                        if let Some(sub_config) = subcommands.get(subcommand) {
                            command_config = sub_config.clone();
                        }
                    }
                }
                
                if let Some(command_options) = &command_config.options {
                    for opt in command_options {
                        options.push(format!("--{}", opt.name));
                        if let Some(short) = &opt.short {
                            options.push(format!("-{}", short));
                        }
                    }
                }
            }
        }
        
        // Standard options
        options.extend(vec![
            "--help".to_string(),
            "-h".to_string(),
            "--version".to_string(),
            "-V".to_string(),
        ]);
        
        options
    }

    fn get_option_value_completions(&self, context: &Context) -> Vec<String> {
        let option = match &context.option {
            Some(opt) => opt.trim_start_matches('-'),
            None => return Vec::new(),
        };
        
        // Handle built-in command option completions
        if let Some(command) = &context.current_command {
            match (command.as_str(), option) {
                ("completion", "shell") => {
                    return vec![
                        "bash".to_string(),
                        "zsh".to_string(),
                        "fish".to_string(),
                        "powershell".to_string(),
                    ];
                }
                ("config", "format") => {
                    return vec![
                        "json".to_string(),
                        "yaml".to_string(),
                        "plain".to_string(),
                    ];
                }
                ("config", "value-type") => {
                    return vec![
                        "string".to_string(),
                        "int".to_string(),
                        "float".to_string(),
                        "bool".to_string(),
                    ];
                }
                _ => {}
            }
        }
        
        // Find option configuration for user-defined commands
        let option_config = match self.find_option_config(option, context) {
            Some(config) => config,
            None => return Vec::new(),
        };
        
        let option_type = option_config.option_type.as_deref().unwrap_or("str");
        
        // Handle different option types
        if option_type == "choice" {
            if let Some(choices) = &option_config.choices {
                return choices.clone();
            }
        } else if option_type == "file" || matches!(option, "config" | "file" | "input" | "output") {
            return self.get_file_completions();
        } else if option_type == "dir" || matches!(option, "directory" | "dir" | "output-dir") {
            return self.get_directory_completions();
        } else if option_type == "bool" || option_type == "flag" {
            return vec!["true".to_string(), "false".to_string()];
        }
        
        Vec::new()
    }

    fn find_option_config(&self, option_name: &str, context: &Context) -> Option<CliOption> {
        // Check global options
        if let Some(cli) = &self.config.cli {
            if let Some(global_options) = &cli.options {
                for opt in global_options {
                    if opt.name == option_name || opt.short.as_deref() == Some(option_name) {
                        return Some(opt.clone());
                    }
                }
            }
        }
        
        // Check command-specific options
        if let Some(command) = &context.current_command {
            let empty_commands = HashMap::new();
            let cli_commands = match &self.config.cli {
                Some(cli) => cli.commands.as_ref().unwrap_or(&empty_commands),
                None => return None,
            };
            
            if let Some(mut command_config) = cli_commands.get(command).cloned() {
                // Check if we're in a subcommand
                if let Some(subcommand) = &context.subcommand {
                    if let Some(subcommands) = &command_config.subcommands {
                        if let Some(sub_config) = subcommands.get(subcommand) {
                            command_config = sub_config.clone();
                        }
                    }
                }
                
                if let Some(command_options) = &command_config.options {
                    for opt in command_options {
                        if opt.name == option_name || opt.short.as_deref() == Some(option_name) {
                            return Some(opt.clone());
                        }
                    }
                }
            }
        }
        
        None
    }

    fn get_file_completions(&self) -> Vec<String> {
        match fs::read_dir(".") {
            Ok(entries) => {
                let mut files = Vec::new();
                for entry in entries.flatten() {
                    if let Ok(metadata) = entry.metadata() {
                        if metadata.is_file() {
                            if let Some(name) = entry.file_name().to_str() {
                                files.push(name.to_string());
                            }
                        }
                    }
                }
                files
            }
            Err(_) => Vec::new(),
        }
    }

    fn get_directory_completions(&self) -> Vec<String> {
        match fs::read_dir(".") {
            Ok(entries) => {
                let mut dirs = Vec::new();
                for entry in entries.flatten() {
                    if let Ok(metadata) = entry.metadata() {
                        if metadata.is_dir() {
                            if let Some(name) = entry.file_name().to_str() {
                                dirs.push(format!("{}/", name));
                            }
                        }
                    }
                }
                dirs
            }
            Err(_) => Vec::new(),
        }
    }
}

// Main completion function - called by CLIs with _completion command
pub fn main() {
    let args: Vec<String> = env::args().collect();
    if args.len() < 4 {
        std::process::exit(1);
    }
    
    let shell = &args[2];
    let current_line = &args[3];
    let cursor_pos = if args.len() > 4 {
        args[4].parse().ok()
    } else {
        None
    };
    
    let engine = CompletionEngine::new(None);
    let completions = engine.get_completions(shell, current_line, cursor_pos);
    
    // Output completions one per line
    for completion in completions {
        println!("{}", completion);
    }
}