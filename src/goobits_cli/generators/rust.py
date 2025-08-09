"""Rust CLI generator implementation."""

import json
from pathlib import Path
from typing import List, Optional, Union, Dict
from jinja2 import Environment, FileSystemLoader, TemplateNotFound
import typer

from . import BaseGenerator
from ..schemas import ConfigSchema, GoobitsConfigSchema
from ..shared.components.doc_generator import DocumentationGenerator

# Universal Template System imports
try:
    from ..universal.template_engine import UniversalTemplateEngine, LanguageRenderer
    from ..universal.renderers.rust_renderer import RustRenderer as UniversalRustRenderer
    UNIVERSAL_TEMPLATES_AVAILABLE = True
except ImportError:
    UNIVERSAL_TEMPLATES_AVAILABLE = False


class RustGenerator(BaseGenerator):
    """CLI code generator for Rust using clap framework."""
    
    def __init__(self, use_universal_templates: bool = False):
        """Initialize the Rust generator with Jinja2 environment.
        
        Args:
            use_universal_templates: If True, use Universal Template System
        """
        self.use_universal_templates = use_universal_templates and UNIVERSAL_TEMPLATES_AVAILABLE
        
        # Initialize Universal Template System if requested
        if self.use_universal_templates:
            self.universal_engine = UniversalTemplateEngine()
            self.rust_renderer = UniversalRustRenderer()
            self.universal_engine.register_renderer(self.rust_renderer)
        
        # Set up Jinja2 environment for Rust templates (legacy mode)
        template_dir = Path(__file__).parent.parent / "templates" / "rust"
        fallback_dir = Path(__file__).parent.parent / "templates"
        
        # Try rust subdirectory first, fallback to main templates
        if template_dir.exists():
            self.env = Environment(
                loader=FileSystemLoader([template_dir, fallback_dir]),
                extensions=['jinja2.ext.do']
            )
        else:
            # If rust subdirectory doesn't exist, use main templates dir
            self.env = Environment(
                loader=FileSystemLoader(fallback_dir),
                extensions=['jinja2.ext.do']
            )
            self.template_missing = True
        
        # Initialize shared documentation generator (will be set when generate is called)
        self.doc_generator = None
        
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
        
        # Initialize generated files storage
        self._generated_files = {}
    
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
    
    def _check_file_conflicts(self, target_files: dict, output_dir: str = None) -> dict:
        """Check for file conflicts and adjust paths if needed."""
        import os
        
        # If no output_dir provided or we're in a test environment, skip conflict detection
        if output_dir is None or os.environ.get('PYTEST_CURRENT_TEST'):
            return target_files
        
        adjusted_files = {}
        warnings = []
        
        for filepath, content in target_files.items():
            full_path = os.path.join(output_dir, filepath) if output_dir else filepath
            if filepath == "src/main.rs" and os.path.exists(full_path):
                # main.rs exists, generate cli.rs instead
                new_filepath = "src/cli.rs"
                adjusted_files[new_filepath] = content
                warnings.append(f"⚠️  Existing src/main.rs detected. Generated src/cli.rs instead.")
                warnings.append(f"   Import cli.rs in your main.rs with: mod cli; pub use cli::*;")
            elif filepath == "Cargo.toml" and os.path.exists(full_path):
                warnings.append(f"⚠️  Existing Cargo.toml detected. Review and merge dependencies manually.")
                adjusted_files[filepath] = content  # Still generate, but warn user
            else:
                adjusted_files[filepath] = content
        
        # Print warnings if any
        if warnings:
            print("\n🔍 File Conflict Detection:")
            for warning in warnings:
                print(f"   {warning}")
            print()
        
        return adjusted_files
    
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
        # Use Universal Template System if enabled
        if self.use_universal_templates:
            return self._generate_with_universal_templates(config, config_filename, version)
        
        # Fall back to legacy implementation
        return self._generate_legacy(config, config_filename, version)
    
    def _generate_with_universal_templates(self, config: Union[ConfigSchema, GoobitsConfigSchema], 
                                         config_filename: str, version: Optional[str] = None) -> str:
        """
        Generate using Universal Template System.
        
        Args:
            config: The configuration object
            config_filename: Name of the configuration file
            version: Optional version string
            
        Returns:
            Generated Rust CLI code
        """
        try:
            # Convert config to GoobitsConfigSchema if needed
            if isinstance(config, ConfigSchema):
                # Create minimal GoobitsConfigSchema for universal system
                goobits_config = GoobitsConfigSchema(
                    package_name=getattr(config, 'package_name', config.cli.name),
                    command_name=getattr(config, 'command_name', config.cli.name),
                    description=getattr(config, 'description', config.cli.description or config.cli.tagline),
                    cli=config,
                    installation=getattr(config, 'installation', None)
                )
            else:
                goobits_config = config
                
            # Generate using universal engine
            output_dir = Path(".")
            generated_files = self.universal_engine.generate_cli(
                goobits_config, "rust", output_dir
            )
            
            # Store generated files
            self._generated_files = {}
            for file_path, content in generated_files.items():
                # Extract relative filename for compatibility
                relative_path = Path(file_path).name
                self._generated_files[relative_path] = content
            
            # Return main Rust file for backward compatibility
            main_file = next((content for path, content in generated_files.items() 
                            if "main.rs" in path or "lib.rs" in path), "")
            return main_file
            
        except Exception as e:
            # Fall back to legacy mode if universal templates fail
            print(f"⚠️  Universal Templates failed ({e}), falling back to legacy mode")
            return self._generate_legacy(config, config_filename, version)
    
    def _generate_legacy(self, config: Union[ConfigSchema, GoobitsConfigSchema], 
                        config_filename: str, version: Optional[str] = None) -> str:
        """
        Generate using legacy template system.
        
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
            'version': version or (cli_config.app.version if cli_config and hasattr(cli_config, 'app') and hasattr(cli_config.app, 'version') else '1.0.0'),
            'installation': metadata['installation'],
            'hooks_path': metadata['hooks_path'],
            'rust_crates': getattr(config, 'rust_crates', {}) if hasattr(config, 'rust_crates') else {},
        }
        
        # Initialize documentation generator with the config
        config_dict = context.copy()
        self.doc_generator = DocumentationGenerator('rust', config_dict)
        
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
            "src/hooks.rs",
            "src/config.rs",
            "src/commands.rs",
            "src/errors.rs",
            "src/utils.rs",
            "src/completion_engine.rs",
            "src/progress.rs",
            "src/prompts.rs",
            "src/styling.rs",
            "src/plugins.rs",
            "src/interactive_mode.rs",
            "src/tests.rs",
            "Cargo.toml",
            "setup.sh",
            "README.md",
            ".gitignore"
        ]
    
    def get_default_output_path(self, package_name: str) -> str:
        """Get the default output path for Rust CLI."""
        return "src/main.rs"  # Main entry point for Rust binaries
    
    def _generate_fallback_code(self, context: dict) -> str:
        """Generate a basic Rust CLI that calls hook functions."""
        cli_config = context['cli']
        package_name = context['package_name'] or 'my-cli'
        command_name = context['command_name'] or package_name
        description = context['description'] or 'A CLI tool'
        version = context['version']
        
        # Generate a minimal clap CLI that calls hooks
        code = f'''//! {context['display_name']} CLI
//! Auto-generated from {context['file_name']}

use clap::{{Parser, Subcommand}};
use std::collections::HashMap;
use anyhow::Result;

mod hooks;
use hooks::{{Args, on_unknown_command}};

#[derive(Parser)]
#[command(name = "{command_name}")]
#[command(about = "{description}")]
#[command(version = "{version}")]
struct Cli {{
    #[command(subcommand)]
    command: Option<Commands>,
}}

#[derive(Subcommand)]
enum Commands {{'''
        
        # Add commands if available
        if cli_config and hasattr(cli_config, 'commands'):
            for cmd_name, cmd_data in cli_config.commands.items():
                title_case = cmd_name.replace('-', ' ').title().replace(' ', '')
                desc = getattr(cmd_data, 'desc', 'Command description')
                code += f'''
    /// {desc}
    {title_case} {{'''
                
                # Add simple args and options support
                if hasattr(cmd_data, 'args') and cmd_data.args:
                    for arg in cmd_data.args:
                        arg_desc = getattr(arg, 'desc', 'Argument')
                        if getattr(arg, 'required', True):
                            code += f'''
        /// {arg_desc}
        {arg.name}: String,'''
                        else:
                            code += f'''
        /// {arg_desc}
        {arg.name}: Option<String>,'''
                
                if hasattr(cmd_data, 'options') and cmd_data.options:
                    for opt in cmd_data.options:
                        opt_desc = getattr(opt, 'desc', 'Option')
                        opt_name = opt.name.replace('-', '_')
                        if getattr(opt, 'type', 'str') == 'flag':
                            code += f'''
        /// {opt_desc}
        #[arg(long = "{opt.name}")]
        {opt_name}: bool,'''
                        else:
                            code += f'''
        /// {opt_desc}
        #[arg(long = "{opt.name}")]
        {opt_name}: Option<String>,'''
                
                code += '''
    },'''
        
        code += '''
}

fn main() -> Result<()> {
    let cli = Cli::parse();
    
    match cli.command {'''
        
        # Add command handlers that call hooks
        if cli_config and hasattr(cli_config, 'commands'):
            for cmd_name, cmd_data in cli_config.commands.items():
                title_case = cmd_name.replace('-', ' ').title().replace(' ', '')
                safe_cmd_name = cmd_name.replace('-', '_')
                code += f'''
        Some(Commands::{title_case} {{ .. }}) => {{
            let args = Args {{
                command_name: "{cmd_name}".to_string(),
                raw_args: HashMap::new(), // TODO: populate from actual args
            }};
            hooks::on_{safe_cmd_name}(&args)?;
        }}'''
        
        code += '''
        None => {
            // Show help if no command provided
            println!("Use --help to see available commands");
        }
    }
    
    Ok(())
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
        # Use Universal Template System if enabled
        if self.use_universal_templates:
            # Generate main file to populate _generated_files
            self.generate(config, config_filename, version)
            return self._generated_files
        
        # Legacy implementation
        return self._generate_all_files_legacy(config, config_filename, version)
    
    def _generate_all_files_legacy(self, config: Union[ConfigSchema, GoobitsConfigSchema], 
                                  config_filename: str, version: Optional[str] = None) -> Dict[str, str]:
        """
        Generate all files using legacy template system.
        
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
            'version': version or (cli_config.app.version if cli_config and hasattr(cli_config, 'app') and hasattr(cli_config.app, 'version') else '1.0.0'),
            'installation': metadata['installation'],
            'hooks_path': metadata['hooks_path'],
            'rust_crates': getattr(config, 'rust_crates', {}) if hasattr(config, 'rust_crates') else {},
        }
        
        # Initialize documentation generator with the config
        config_dict = context.copy()
        self.doc_generator = DocumentationGenerator('rust', config_dict)
        
        files = {}
        
        # Generate main.rs file - this is the CLI entry point
        try:
            template = self.env.get_template("main.rs.j2")
            files['src/main.rs'] = template.render(**context)
        except TemplateNotFound:
            files['src/main.rs'] = self._generate_fallback_code(context)
        
        # Generate hooks.rs file - simple user hook functions
        try:
            template = self.env.get_template("hooks.rs.j2")
            files['src/hooks.rs'] = template.render(**context)
        except TemplateNotFound:
            # Generate minimal hooks.rs similar to Python's app_hooks.py
            files['src/hooks.rs'] = self._generate_simple_hooks(context)
        
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
            files['setup.sh'] = self._generate_setup_script(context)
        
        # Generate README.md
        try:
            template = self.env.get_template("README.md.j2")
            files['README.md'] = template.render(**context)
        except TemplateNotFound:
            files['README.md'] = self._generate_readme(context)
        
        # Generate .gitignore
        files['.gitignore'] = self._generate_gitignore()
        
        # Generate all helper modules from templates
        helper_templates = [
            ('src/lib.rs', 'lib.rs.j2'),
            ('src/config.rs', 'config.rs.j2'),
            ('src/commands.rs', 'commands.rs.j2'),
            ('src/errors.rs', 'errors.rs.j2'),
            ('src/utils.rs', 'utils.rs.j2'),
            ('src/completion_engine.rs', 'completion_engine.rs.j2'),
            ('src/progress.rs', 'progress.rs.j2'),
            ('src/prompts.rs', 'prompts.rs.j2'),
            ('src/styling.rs', 'styling.rs.j2'),
            ('src/plugins.rs', 'plugins.rs.j2'),
            ('src/tests.rs', 'tests.rs.j2'),
            ('src/interactive_mode.rs', 'interactive_mode.rs.j2')
        ]
        
        for output_file, template_name in helper_templates:
            try:
                template = self.env.get_template(template_name)
                files[output_file] = template.render(**context)
            except TemplateNotFound:
                # Skip if template doesn't exist, but log for debugging
                print(f"⚠️  Template {template_name} not found, skipping {output_file}")
            except Exception as e:
                # Log template rendering errors
                print(f"⚠️  Error rendering {template_name}: {str(e)}")
                import traceback
                traceback.print_exc()
        
        # Check for file conflicts and adjust if needed
        files = self._check_file_conflicts(files)
        
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
                    "clap": {"version": "4.0", "features": ["derive"]},
                    "anyhow": "1.0",
                    "rustyline": "14.0",
                    "dirs": "5.0",
                    "serde_json": "1.0"
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
    
    def _generate_simple_hooks(self, context: dict) -> str:
        """Generate a simple hooks.rs file similar to Python's app_hooks.py."""
        cli_config = context.get('cli')
        hooks_content = f'''//! Hook functions for {context['display_name']}
//! Auto-generated from {context['file_name']}
//!
//! Implement your business logic in these hook functions.
//! Each command will call its corresponding hook function.

use anyhow::Result;

/// Arguments structure passed to hook functions
#[derive(Debug, Clone)]
pub struct Args {{
    pub command_name: String,
    pub raw_args: std::collections::HashMap<String, String>,
}}

'''
        
        # Generate hook functions for each command
        if cli_config and hasattr(cli_config, 'commands'):
            for cmd_name, cmd_data in cli_config.commands.items():
                safe_cmd_name = cmd_name.replace('-', '_')
                hooks_content += f'''/// Hook function for '{cmd_name}' command
pub fn on_{safe_cmd_name}(args: &Args) -> Result<()> {{
    // TODO: Implement your '{cmd_name}' command logic here
    println!("🚀 Executing {cmd_name} command...");
    println!("   Command: {{}}", args.command_name);
    
    // Example: access raw arguments
    for (key, value) in &args.raw_args {{
        println!("   {{}}: {{}}", key, value);
    }}
    
    println!("✅ {cmd_name} command completed successfully!");
    Ok(())
}}

'''
        
        # Add a catch-all hook for unhandled commands
        hooks_content += '''/// Default hook for unhandled commands
pub fn on_unknown_command(args: &Args) -> Result<()> {
    anyhow::bail!("No hook implementation found for command: {}", args.command_name);
}
'''
        
        return hooks_content
    
    def _generate_setup_script(self, context: dict) -> str:
        """Generate setup.sh script for Rust CLI."""
        return f'''#!/bin/bash
# Setup script for {context['display_name']}
# Auto-generated from {context['file_name']}

set -e

echo "🔧 Setting up {context['display_name']}..."

# Check if Rust is installed
if ! command -v cargo &> /dev/null; then
    echo "❌ Cargo not found. Please install Rust first:"
    echo "   curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh"
    exit 1
fi

# Build the project
echo "📦 Building project..."
cargo build --release

if [ $? -eq 0 ]; then
    echo "✅ Build successful!"
    echo "📍 Binary location: target/release/{context['command_name']}"
    echo ""
    echo "To install globally:"
    echo "   cargo install --path ."
    echo ""
    echo "To run locally:"
    echo "   ./target/release/{context['command_name']} --help"
else
    echo "❌ Build failed!"
    exit 1
fi
'''
    
    def _generate_readme(self, context: dict) -> str:
        """Generate README.md for the Rust CLI using shared documentation generator."""
        # Create a config dict that the DocumentationGenerator expects
        config = {
            'package_name': context['package_name'],
            'command_name': context['command_name'],
            'display_name': context['display_name'],
            'description': context['description'],
            'version': context['version'],
            'cli': context.get('cli'),
            'installation': context.get('installation', {}),
            'rust_crates': context.get('rust_crates', {})
        }
        
        # Initialize documentation generator if not already done
        if not self.doc_generator:
            self.doc_generator = DocumentationGenerator('rust', config)
        
        # Try to use the shared documentation generator
        try:
            return self.doc_generator.generate_readme()
        except Exception:
            # Fall back to manual generation if shared generator fails
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