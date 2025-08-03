"""Rust CLI generator implementation."""

import json
from pathlib import Path
from typing import List, Optional, Union, Dict
from jinja2 import Environment, FileSystemLoader, TemplateNotFound
import typer

from . import BaseGenerator
from ..schemas import ConfigSchema, GoobitsConfigSchema


class RustGenerator(BaseGenerator):
    """CLI code generator for Rust using clap framework."""
    
    def __init__(self):
        """Initialize the Rust generator with Jinja2 environment."""
        # Set up Jinja2 environment for Rust templates
        template_dir = Path(__file__).parent.parent / "templates" / "rust"
        fallback_dir = Path(__file__).parent.parent / "templates"
        
        # Try rust subdirectory first, fallback to main templates
        if template_dir.exists():
            self.env = Environment(loader=FileSystemLoader([template_dir, fallback_dir]))
        else:
            # If rust subdirectory doesn't exist, use main templates dir
            self.env = Environment(loader=FileSystemLoader(fallback_dir))
            self.template_missing = True
        
        # Add custom filters (these may need Rust specific versions later)
        def json_stringify(x):
            """Convert to JSON, handling Pydantic models."""
            if hasattr(x, 'model_dump'):
                return json.dumps(x.model_dump(), indent=2)
            elif hasattr(x, 'dict'):
                return json.dumps(x.dict(), indent=2)
            else:
                return json.dumps(x, indent=2)
        
        self.env.filters['json_stringify'] = json_stringify
        self.env.filters['escape_quotes'] = lambda x: x.replace('"', '\\"')
        self.env.filters['snake_case'] = self._to_snake_case
        self.env.filters['kebab_case'] = self._to_kebab_case
    
    def _to_snake_case(self, text: str) -> str:
        """Convert text to snake_case."""
        if not text:
            return text
        # Replace hyphens and spaces with underscores, convert to lowercase
        return text.replace('-', '_').replace(' ', '_').lower()
    
    def _to_kebab_case(self, text: str) -> str:
        """Convert text to kebab-case."""
        if not text:
            return text
        # Replace underscores and spaces with hyphens, convert to lowercase
        return text.replace('_', '-').replace(' ', '-').lower()
    
    def generate(self, config: Union[ConfigSchema, GoobitsConfigSchema], 
                 config_filename: str, version: Optional[str] = None) -> str:
        """
        Generate Rust CLI code from configuration.
        
        Args:
            config: The configuration object
            config_filename: Name of the configuration file
            version: Optional version string
            
        Returns:
            Generated Rust CLI code
        """
        # Extract metadata using base class helper
        metadata = self._extract_config_metadata(config)
        cli_config = metadata['cli_config']
        
        # Validate configuration
        if hasattr(config, 'package_name'):  # GoobitsConfigSchema
            if not cli_config:
                raise ValueError("No CLI configuration found")
        
        # Prepare context for template rendering
        context = {
            'cli': cli_config,
            'file_name': config_filename,
            'package_name': metadata['package_name'],
            'command_name': metadata['command_name'],
            'display_name': metadata['display_name'],
            'description': getattr(config, 'description', cli_config.description if cli_config else ''),
            'version': version or (cli_config.version if cli_config and hasattr(cli_config, 'version') else '0.1.0'),
            'installation': metadata['installation'],
            'hooks_path': metadata['hooks_path'],
            'rust_crates': getattr(config, 'rust_crates', {}) if hasattr(config, 'rust_crates') else {},
        }
        
        # Try to load Rust specific template
        try:
            template = self.env.get_template("main.rs.j2")
            code = template.render(**context)
            return code
        except TemplateNotFound:
            # Provide helpful error message with template content
            return self._generate_fallback_code(context)
    
    def get_output_files(self) -> List[str]:
        """Return list of files this generator creates."""
        return [
            "src/main.rs",
            "src/lib.rs",
            "src/config.rs",
            "src/commands.rs",
            "src/utils.rs",
            "Cargo.toml",
            "setup.sh",
            "README.md",
            ".gitignore"
        ]
    
    def get_default_output_path(self, package_name: str) -> str:
        """Get the default output path for Rust CLI."""
        return "src/main.rs"  # Main entry point for Rust binaries
    
    def _generate_fallback_code(self, context: dict) -> str:
        """Generate a basic Rust CLI when templates are missing."""
        cli_config = context['cli']
        package_name = context['package_name'] or 'my-cli'
        command_name = context['command_name'] or package_name
        description = context['description'] or 'A CLI tool'
        version = context['version']
        
        # Generate a basic clap CLI
        code = f'''//! Generated by goobits-cli
//! 
//! Note: Rust templates are not yet installed.
//! This is a basic CLI structure. To get full functionality,
//! ensure Rust templates are installed in:
//! src/goobits_cli/templates/rust/

use clap::{{Arg, Command, ArgAction}};

fn main() {{
    let matches = Command::new("{command_name}")
        .about("{description}")
        .version("{version}")
        .subcommand_required(false)
        .arg_required_else_help(true)'''
        
        # Add commands if available
        if cli_config and cli_config.commands:
            code += "\n        // Commands\n"
            for cmd_name, cmd_data in cli_config.commands.items():
                code += f'''        .subcommand(
            Command::new("{cmd_name}")
                .about("{cmd_data.desc}")'''
                
                # Add arguments
                if cmd_data.args:
                    for arg in cmd_data.args:
                        required = "true" if arg.required else "false"
                        code += f'''
                .arg(Arg::new("{arg.name}")
                    .help("{arg.desc}")
                    .required({required}))'''
                
                # Add options
                if cmd_data.options:
                    for opt in cmd_data.options:
                        short_flag = f'.short(\'{opt.short}\')' if opt.short else ''
                        if opt.type == "flag":
                            code += f'''
                .arg(Arg::new("{opt.name}")
                    .long("{opt.name}")
                    {short_flag}
                    .help("{opt.desc}")
                    .action(clap::ArgAction::SetTrue))'''
                        else:
                            code += f'''
                .arg(Arg::new("{opt.name}")
                    .long("{opt.name}")
                    {short_flag}
                    .help("{opt.desc}")
                    .value_parser(clap::value_parser!(String)))'''
                
                code += f'''
        )'''
        
        code += '''
        .get_matches();

    match matches.subcommand() {'''
        
        # Add command handlers
        if cli_config and cli_config.commands:
            for cmd_name, cmd_data in cli_config.commands.items():
                code += f'''
        Some(("{cmd_name}", sub_matches)) => {{
            println!("Executing {cmd_name} command...");
            println!("This is a placeholder. Implement your logic here.");
        }}'''
        
        code += '''
        _ => {
            println!("No valid subcommand was provided.");
        }
    }
}
'''
        
        return code
    
    def generate_all_files(self, config: Union[ConfigSchema, GoobitsConfigSchema], 
                          config_filename: str, version: Optional[str] = None) -> Dict[str, str]:
        """
        Generate all files needed for the Rust CLI.
        
        Args:
            config: The configuration object
            config_filename: Name of the configuration file
            version: Optional version string
            
        Returns:
            Dictionary mapping file paths to their contents
        """
        # Extract metadata using base class helper
        metadata = self._extract_config_metadata(config)
        cli_config = metadata['cli_config']
        
        # Validate configuration
        if hasattr(config, 'package_name'):  # GoobitsConfigSchema
            if not cli_config:
                raise ValueError("No CLI configuration found")
        
        # Prepare context for template rendering
        context = {
            'cli': cli_config,
            'file_name': config_filename,
            'package_name': metadata['package_name'],
            'command_name': metadata['command_name'],
            'display_name': metadata['display_name'],
            'description': getattr(config, 'description', cli_config.description if cli_config else ''),
            'version': version or (cli_config.version if cli_config and hasattr(cli_config, 'version') else '0.1.0'),
            'installation': metadata['installation'],
            'hooks_path': metadata['hooks_path'],
            'rust_crates': getattr(config, 'rust_crates', {}) if hasattr(config, 'rust_crates') else {},
        }
        
        files = {}
        
        # Generate main.rs file
        try:
            template = self.env.get_template("main.rs.j2")
            files['src/main.rs'] = template.render(**context)
        except TemplateNotFound:
            files['src/main.rs'] = self._generate_fallback_code(context)
        
        # Generate lib.rs file
        try:
            template = self.env.get_template("lib.rs.j2")
            files['src/lib.rs'] = template.render(**context)
        except TemplateNotFound:
            # Fallback lib.rs - simplified version without complex hook system
            files['src/lib.rs'] = f'''//! {context['display_name']} Library
//! 
//! Generated by goobits-cli

pub mod config;
pub mod commands;
pub mod utils;

// Re-export commonly used types
pub use config::AppConfig;
pub use commands::{{Command, CommandArgs, CommandRegistry}};

/// Library version
pub const VERSION: &str = "{context['version']}";

/// Simple command execution trait
pub trait CommandTrait {{
    fn name(&self) -> &str;
    fn description(&self) -> &str;
    fn execute(&self, args: &[String]) -> anyhow::Result<()>;
}}
'''
        
        # Generate config.rs file
        try:
            template = self.env.get_template("config.rs.j2")
            files['src/config.rs'] = template.render(**context)
        except TemplateNotFound:
            # Fallback config.rs
            files['src/config.rs'] = '''//! Configuration module

use anyhow::Result;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::path::PathBuf;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AppConfig {
    pub settings: HashMap<String, String>,
}

impl AppConfig {
    pub fn load() -> Result<Self> {
        Ok(Self {
            settings: HashMap::new(),
        })
    }
}
'''
        
        # Generate commands.rs file
        try:
            template = self.env.get_template("commands.rs.j2")
            files['src/commands.rs'] = template.render(**context)
        except TemplateNotFound:
            # Fallback commands.rs
            files['src/commands.rs'] = '''//! Commands module

use anyhow::Result;
use std::collections::HashMap;

#[derive(Debug, Clone)]
pub struct Command {
    pub name: String,
    pub description: String,
}

#[derive(Debug, Clone)]
pub struct CommandArgs {
    pub raw_args: HashMap<String, String>,
}

pub struct CommandRegistry;
'''
        
        # Generate utils.rs file
        try:
            template = self.env.get_template("utils.rs.j2")
            files['src/utils.rs'] = template.render(**context)
        except TemplateNotFound:
            # Fallback utils.rs
            files['src/utils.rs'] = '''//! Utility functions

use anyhow::Result;

/// Utility functions for the CLI
pub fn format_output(message: &str) -> String {
    format!("[{}] {}", chrono::Local::now().format("%Y-%m-%d %H:%M:%S"), message)
}
'''
        
        # Generate Cargo.toml
        try:
            template = self.env.get_template("Cargo.toml.j2")
            files['Cargo.toml'] = template.render(**context)
        except TemplateNotFound:
            files['Cargo.toml'] = self._generate_cargo_toml(context)
        
        # Generate setup script
        try:
            template = self.env.get_template("setup.sh.j2")
            files['setup.sh'] = template.render(**context)
        except TemplateNotFound:
            # Fallback to basic setup script
            files['setup.sh'] = f'''#!/bin/bash
echo "Setting up {context['display_name']}..."
cargo build --release
echo "Setup complete! Binary available at target/release/{context['command_name']}"
'''
        
        # Generate README.md
        files['README.md'] = self._generate_readme(context)
        
        # Generate .gitignore
        files['.gitignore'] = self._generate_gitignore()
        
        return files
    
    def _generate_cargo_toml(self, context: dict) -> str:
        """Generate Cargo.toml from context using template."""
        try:
            template = self.env.get_template("Cargo.toml.j2")
            return template.render(**context)
        except TemplateNotFound:
            # Fallback to basic Cargo.toml
            cargo_data = {
                "package": {
                    "name": context['package_name'].replace('_', '-'),
                    "version": context['version'],
                    "description": context['description'],
                    "edition": "2021"
                },
                "dependencies": {
                    "clap": {"version": "4.0", "features": ["derive"]}
                },
                "bin": [
                    {
                        "name": context['command_name'],
                        "path": "src/main.rs"
                    }
                ]
            }
            
            # Add any rust crates from configuration
            rust_crates = context.get('rust_crates', {})
            if rust_crates:
                cargo_data["dependencies"].update(rust_crates)
            
            # Convert to TOML format
            toml_content = f'''[package]
name = "{cargo_data['package']['name']}"
version = "{cargo_data['package']['version']}"
description = "{cargo_data['package']['description']}"
edition = "{cargo_data['package']['edition']}"

[[bin]]
name = "{context['command_name']}"
path = "src/main.rs"

[dependencies]
'''
            
            # Add dependencies
            for dep_name, dep_info in cargo_data["dependencies"].items():
                if isinstance(dep_info, dict):
                    if "version" in dep_info:
                        if "features" in dep_info:
                            features_str = ", ".join(f'"{f}"' for f in dep_info["features"])
                            toml_content += f'{dep_name} = {{ version = "{dep_info["version"]}", features = [{features_str}] }}\n'
                        else:
                            toml_content += f'{dep_name} = "{dep_info["version"]}"\n'
                    else:
                        # Complex dependency specification
                        toml_content += f'{dep_name} = {dep_info}\n'
                else:
                    toml_content += f'{dep_name} = "{dep_info}"\n'
            
            return toml_content
    
    def _generate_readme(self, context: dict) -> str:
        """Generate README.md for the Rust CLI."""
        return f"""# {context['display_name']}

{context['description']}

## Installation

### From crates.io (when published)
```bash
cargo install {context['package_name']}
```

### For development
```bash
# Clone the repository
git clone <your-repo-url>
cd {context['package_name']}

# Build and install locally
cargo build --release
# The binary will be available at target/release/{context['command_name']}
```

## Usage

```bash
{context['command_name']} --help
```

## Commands

{self._generate_commands_documentation(context)}

## Development

To build in development mode:
```bash
cargo build
```

To run tests:
```bash
cargo test
```

To run in development mode:
```bash
cargo run -- [arguments]
```

## License

MIT
"""
    
    def _generate_commands_documentation(self, context: dict) -> str:
        """Generate commands documentation for README."""
        cli_config = context.get('cli')
        if not cli_config or not hasattr(cli_config, 'commands'):
            return "No commands configured."
        
        commands_doc = []
        for cmd_name, cmd_data in cli_config.commands.items():
            cmd_desc = cmd_data.desc if hasattr(cmd_data, 'desc') else 'Command description'
            commands_doc.append(f"- `{cmd_name}` - {cmd_desc}")
            
            # Add subcommands if they exist
            if hasattr(cmd_data, 'subcommands') and cmd_data.subcommands:
                for sub_name, sub_data in cmd_data.subcommands.items():
                    sub_desc = sub_data.desc if hasattr(sub_data, 'desc') else 'Subcommand description'
                    commands_doc.append(f"  - `{cmd_name} {sub_name}` - {sub_desc}")
        
        return '\n'.join(commands_doc) if commands_doc else "No commands configured."
    
    def _generate_gitignore(self) -> str:
        """Generate .gitignore for Rust project."""
        return """/target/
**/*.rs.bk
Cargo.lock

# IDE files
.idea/
.vscode/
*.swp
*.swo

# OS files
.DS_Store
Thumbs.db

# Environment variables
.env
.env.local

# Logs
*.log

# Build artifacts
/release/
/debug/
"""