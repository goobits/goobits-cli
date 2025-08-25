use std::fs;
use std::path::PathBuf;
use std::env;

pub struct CompletionEngine {
    cli_name: String,
    commands: Vec<CompletionCommand>,
}

#[derive(Clone)]
struct CompletionCommand {
    name: String,
    description: String,
    options: Vec<CompletionOption>,
    arguments: Vec<CompletionArgument>,
}

#[derive(Clone)]
struct CompletionOption {
    name: String,
    short: Option<String>,
    description: String,
}

#[derive(Clone)]
struct CompletionArgument {
    name: String,
    #[allow(dead_code)]
    description: String,
}

impl CompletionEngine {
    pub fn new() -> Self {
        Self {
            cli_name: "demo".to_string(),
            commands: vec![                CompletionCommand {
                    name: "simple".to_string(),
                    description: "Simple command that works today".to_string(),
                    options: vec![                        CompletionOption {
                            name: "verbose".to_string(),
                            short: None,
                            description: "Verbose output".to_string(),
                        },                    ],
                    arguments: vec![                        CompletionArgument {
                            name: "message".to_string(),
                            description: "Message to display".to_string(),
                        },                    ],
                },                CompletionCommand {
                    name: "database".to_string(),
                    description: "Database operations".to_string(),
                    options: vec![                    ],
                    arguments: vec![                    ],
                },                CompletionCommand {
                    name: "api".to_string(),
                    description: "API management".to_string(),
                    options: vec![                    ],
                    arguments: vec![                    ],
                },            ],
        }
    }
    pub fn generate_bash_completion(&self) -> String {        let mut script = format!(r#"#!/bin/bash
# Bash completion for {}

_{}_completions()
{{
    local cur prev words cword
    COMPREPLY=()
    cur="${{COMP_WORDS[COMP_CWORD]}}"
    prev="${{COMP_WORDS[COMP_CWORD-1]}}"
    
    # Global options
    local global_opts="--help -h --version"
    
    # Subcommands
    local subcommands=""#, self.cli_name, self.cli_name.replace("-", "_"));

        for cmd in &self.commands {
            script.push_str(&format!(" {}", cmd.name));
        }

        script.push_str(r#""
    
    case ${{COMP_CWORD}} in
        1)
            COMPREPLY=($(compgen -W "$subcommands $global_opts" -- "$cur"))
            ;;
        *)
            case "${{words[1]}}" in"#);

        for cmd in &self.commands {
            script.push_str(&format!("\n                {})\n                    local {}_opts=\"--help -h", 
                cmd.name, cmd.name.replace("-", "_")));
            
            for opt in &cmd.options {
                script.push_str(&format!(" --{}", opt.name));
                if let Some(short) = &opt.short {
                    script.push_str(&format!(" -{}", short));
                }
            }
            
            script.push_str(&format!("\"\n                    COMPREPLY=($(compgen -W \"${}_opts\" -- \"$cur\"))\n                    ;;", 
                cmd.name.replace("-", "_")));
        }

        script.push_str(&format!(r#"
            esac
            ;;
    esac
}}

complete -F _{}_completions {}
"#, self.cli_name.replace("-", "_"), self.cli_name));

        script    }
    pub fn generate_zsh_completion(&self) -> String {        let mut script = format!(r#"#compdef {}
# Zsh completion for {}

_{}() {{
    local context state line
    
    _arguments -C \
        '(--help -h){{--help,-h}}[Show help information]' \
        '(--version)--version[Show version information]' \
        '1: :_{}_commands' \
        '*::arg:->args'
    
    case $state in
        args)
            case $words[1] in"#, 
            self.cli_name, self.cli_name, 
            self.cli_name.replace("-", "_"), self.cli_name.replace("-", "_"));

        for cmd in &self.commands {
            script.push_str(&format!("\n                {})\n                    _arguments \\", cmd.name));
            script.push_str("\n                        '(--help -h){{--help,-h}}[Show help information]' \\");
            
            for opt in &cmd.options {
                if let Some(short) = &opt.short {
                    script.push_str(&format!("\n                        '(--{} -{}){{--{},-{}}}[{}]' \\", 
                        opt.name, short, opt.name, short, opt.description));
                } else {
                    script.push_str(&format!("\n                        '(--{})--{}[{}]' \\", 
                        opt.name, opt.name, opt.description));
                }
            }
            
            for (i, arg) in cmd.arguments.iter().enumerate() {
                script.push_str(&format!("\n                        '{}:{}:_files'", i + 1, arg.name));
                if i < cmd.arguments.len() - 1 {
                    script.push_str(" \\");
                }
            }
            
            script.push_str("\n                    ;;");
        }

        script.push_str(&format!(r#"
            esac
            ;;
    esac
}}

_{}_commands() {{
    local commands
    commands=("#, self.cli_name.replace("-", "_")));

        for cmd in &self.commands {
            script.push_str(&format!("\n        '{}:{}'", cmd.name, cmd.description));
        }

        script.push_str(&format!(r#"
    )
    _describe 'commands' commands
}}

_{} "$@"
"#, self.cli_name.replace("-", "_")));

        script    }
    pub fn generate_fish_completion(&self) -> String {        let mut script = format!(r#"# Fish completion for {}

# Global options
complete -c {} -f
complete -c {} -s h -l help -d "Show help information"
complete -c {} -l version -d "Show version information"

# Subcommands"#, 
            self.cli_name, self.cli_name, self.cli_name, self.cli_name);

        for cmd in &self.commands {
            script.push_str(&format!("\ncomplete -c {} -n \"__fish_use_subcommand\" -a \"{}\" -d \"{}\"", 
                self.cli_name, cmd.name, cmd.description));
            
            for opt in &cmd.options {
                script.push_str(&format!("\ncomplete -c {} -n \"__fish_seen_subcommand_from {}\" -l {}", 
                    self.cli_name, cmd.name, opt.name));
                
                if let Some(short) = &opt.short {
                    script.push_str(&format!(" -s {}", short));
                }
                
                script.push_str(&format!(" -d \"{}\"", opt.description));
            }
        }

        script.push('\n');
        script    }
    pub fn install_completion(&self, shell: Option<&str>) -> Result<(), Box<dyn std::error::Error>> {
        let shell_name = match shell {
            Some(s) => s.to_string(),
            None => {
                let shell_path = env::var("SHELL").unwrap_or_else(|_| "/bin/bash".to_string());
                shell_path.split('/').last().unwrap_or("bash").to_string()
            }
        };
        let shell = shell_name.as_str();

        let (script, completion_dir, filename) = match shell {
            "bash" => {
                let script = self.generate_bash_completion();
                let completion_dir = PathBuf::from(env::var("HOME")?).join(".bash_completion.d");
                let filename = self.cli_name.clone();
                (script, completion_dir, filename)
            }
            "zsh" => {
                let script = self.generate_zsh_completion();
                let completion_dir = PathBuf::from(env::var("HOME")?).join(".zsh").join("completions");
                let filename = format!("{}.zsh", self.cli_name);
                (script, completion_dir, filename)
            }
            "fish" => {
                let script = self.generate_fish_completion();
                let completion_dir = PathBuf::from(env::var("HOME")?).join(".config").join("fish").join("completions");
                let filename = format!("{}.fish", self.cli_name);
                (script, completion_dir, filename)
            }
            _ => return Err(format!("Unsupported shell: {}", shell).into()),
        };

        fs::create_dir_all(&completion_dir)?;
        let filepath = completion_dir.join(filename);
        fs::write(&filepath, script)?;

        println!("Completion script installed: {}", filepath.display());

        match shell {
            "bash" => println!("Please restart your terminal or run: source ~/.bashrc"),
            "zsh" => println!("Please restart your terminal or add to ~/.zshrc: fpath=(~/.zsh/completions $fpath)"),
            _ => {}
        }

        Ok(())
    }
}