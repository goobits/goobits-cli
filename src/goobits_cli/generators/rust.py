"""Rust CLI generator implementation."""



import json

import sys

from pathlib import Path

from typing import List, Optional, Union, Dict

from jinja2 import Environment, FileSystemLoader, TemplateNotFound

import typer



from . import BaseGenerator

from ..schemas import ConfigSchema, GoobitsConfigSchema

from ..formatter import (

    align_examples, format_multiline_text, escape_for_docstring,

    align_setup_steps, format_icon_spacing, align_header_items

)



# Universal Template System imports

try:

    from ..universal.template_engine import UniversalTemplateEngine, LanguageRenderer

    from ..universal.renderers.rust_renderer import RustRenderer

    UNIVERSAL_TEMPLATES_AVAILABLE = True

except ImportError:

    UNIVERSAL_TEMPLATES_AVAILABLE = False

    UniversalTemplateEngine = None

    RustRenderer = None



try:

    from ..shared.components.doc_generator import DocumentationGenerator

except ImportError:

    DocumentationGenerator = None





# Custom Exception Classes for Better Error Handling

class RustGeneratorError(Exception):

    """Base exception for Rust generator errors."""

    def __init__(self, message: str, error_code: int = 1, details: Optional[str] = None):

        self.message = message

        self.error_code = error_code

        self.details = details

        super().__init__(self.message)





class ConfigurationError(RustGeneratorError):

    """Configuration validation or loading error."""

    def __init__(self, message: str, field: Optional[str] = None, suggestion: Optional[str] = None):

        self.field = field

        self.suggestion = suggestion

        error_code = 2  # Configuration errors

        super().__init__(message, error_code, f"Field: {field}" if field else None)





class TemplateError(RustGeneratorError):

    """Template rendering or loading error."""

    def __init__(self, message: str, template_name: Optional[str] = None, line_number: Optional[int] = None):

        self.template_name = template_name

        self.line_number = line_number

        error_code = 3  # Template errors

        details = f"Template: {template_name}" if template_name else None

        if line_number:

            details += f", Line: {line_number}" if details else f"Line: {line_number}"

        super().__init__(message, error_code, details)





class DependencyError(RustGeneratorError):

    """Missing or incompatible dependency error."""

    def __init__(self, message: str, dependency: str, install_command: Optional[str] = None):

        self.dependency = dependency

        self.install_command = install_command

        error_code = 4  # Dependency errors

        super().__init__(message, error_code, f"Dependency: {dependency}")





class ValidationError(RustGeneratorError):

    """Input validation error."""

    def __init__(self, message: str, field: str, value: Optional[str] = None, valid_options: Optional[List[str]] = None):

        self.field = field

        self.value = value

        self.valid_options = valid_options

        error_code = 2  # Validation errors

        details = f"Field: {field}"

        if value:

            details += f", Value: {value}"

        if valid_options:

            details += f", Valid options: {', '.join(valid_options)}"

        super().__init__(message, error_code, details)





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

            try:

                self.universal_engine = UniversalTemplateEngine()

                self.rust_renderer = RustRenderer()

                self.universal_engine.register_renderer(self.rust_renderer)

            except Exception as e:

                typer.echo(f"⚠️  Failed to initialize Universal Template System: {e}", err=True)

                typer.echo("   Falling back to legacy template system", err=True)

                self.use_universal_templates = False

                self.universal_engine = None

                self.rust_renderer = None

        

        # Set up Jinja2 environment for legacy mode

        template_dir = Path(__file__).parent.parent / "templates" / "rust"

        fallback_dir = Path(__file__).parent.parent / "templates"

        

        # Try rust subdirectory first, fallback to main templates

        if template_dir.exists():

            self.env = Environment(loader=FileSystemLoader([template_dir, fallback_dir]))

        else:

            # If rust subdirectory doesn't exist, use main templates dir

            self.env = Environment(loader=FileSystemLoader(fallback_dir))

            self.template_missing = True

        

        # Add custom filters

        try:

            self.env.filters['align_examples'] = align_examples

            self.env.filters['format_multiline'] = format_multiline_text

            self.env.filters['escape_docstring'] = escape_for_docstring

            self.env.filters['align_setup_steps'] = align_setup_steps

            self.env.filters['format_icon'] = format_icon_spacing

            self.env.filters['align_header_items'] = align_header_items

            self.env.filters['to_rust_type'] = self._to_rust_type

            self.env.filters['to_snake_case'] = self._to_snake_case

            self.env.filters['to_screaming_snake_case'] = self._to_screaming_snake_case

            self.env.filters['to_pascal_case'] = self._to_pascal_case

            self.env.filters['escape_rust_string'] = self._escape_rust_string

        except Exception as e:

            raise DependencyError(

                f"Failed to register template filters: {str(e)}",

                dependency="goobits-cli formatter"

            ) from e

        

        # Initialize generated files storage

        self._generated_files = {}

        

        # Initialize shared components

        self.doc_generator = None  # Will be initialized when config is available

    

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

            # Ensure universal engine is available

            if not self.universal_engine:

                raise RuntimeError("Universal Template Engine not initialized")

            

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

            

            # Store generated files for later access

            self._generated_files = {}

            for file_path, content in generated_files.items():

                # Extract relative filename for compatibility

                relative_path = Path(file_path).name

                self._generated_files[relative_path] = content

            

            # Return main CLI file for backward compatibility

            main_cli_file = next((content for path, content in generated_files.items() 

                                if "main.rs" in path), "")

            

            if not main_cli_file:

                # If no main CLI file found, use the first available content

                main_cli_file = next(iter(generated_files.values()), "")

                

            return main_cli_file

            

        except Exception as e:

            # Fall back to legacy mode if universal templates fail

            typer.echo(f"⚠️  Universal Templates failed ({type(e).__name__}: {e}), falling back to legacy mode", err=True)

            # Disable universal templates for subsequent calls to avoid repeated failures

            self.use_universal_templates = False

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

        

        # Initialize DocumentationGenerator with config

        if DocumentationGenerator:

            config_dict = config.model_dump() if hasattr(config, 'model_dump') else config.dict()

            self.doc_generator = DocumentationGenerator(language='rust', config=config_dict)

        

        # Validate configuration before building - only validate CLI for GoobitsConfigSchema

        try:

            if hasattr(config, 'package_name'):  # GoobitsConfigSchema

                if not cli_config:

                    raise ConfigurationError(

                        "No CLI configuration found in the project configuration.",

                        field="cli",

                        suggestion="Add a 'cli' section to your goobits.yaml file with at least one command."

                    )

            else:  # ConfigSchema

                self._validate_config(config)

        except (ConfigurationError, ValidationError):

            raise  # Re-raise our custom exceptions

        except Exception as e:

            # Wrap unexpected errors

            raise ConfigurationError(

                f"Unexpected error during configuration validation: {str(e)}",

                suggestion="Check your configuration file syntax and structure."

            ) from e

        

        # Serialize the CLI part of the config to a JSON string

        try:

            cli_dict = cli_config.model_dump()

            cli_config_json = json.dumps(cli_dict, indent=2, ensure_ascii=False)

            # Escape for Rust string literal

            cli_config_json = cli_config_json.replace("\\", "\\\\").replace("\"", "\\\"")

        except Exception as e:

            raise ConfigurationError(

                f"Failed to serialize CLI configuration to JSON: {str(e)}",

                suggestion="Check for circular references or non-serializable objects in your configuration."

            ) from e

        

        # Prepare common template variables

        template_vars = {

            'cli': cli_config,

            'file_name': config_filename,

            'cli_config_json': cli_config_json,

            'package_name': metadata['package_name'],

            'command_name': metadata['command_name'],

            'display_name': metadata['display_name'],

            'installation': metadata['installation'],

            'hooks_path': metadata['hooks_path'],

            'version': version or '0.1.0'

        }

        

        # Generate all templates

        generated_files = {}

        

        # Main Rust template (src/main.rs)

        try:

            template = self.env.get_template("main.rs.j2")

            generated_files['src/main.rs'] = template.render(**template_vars)

        except TemplateNotFound:

            generated_files['src/main.rs'] = self._generate_fallback_main_rs(template_vars)

        except Exception as e:

            raise TemplateError(

                f"Failed to render main Rust template: {str(e)}",

                template_name="main.rs.j2"

            ) from e

        

        # Cargo.toml

        try:

            template = self.env.get_template("Cargo.toml.j2")

            generated_files['Cargo.toml'] = template.render(**template_vars)

        except TemplateNotFound:

            generated_files['Cargo.toml'] = self._generate_fallback_cargo_toml(template_vars)

        except Exception as e:

            raise TemplateError(

                f"Failed to render Cargo.toml template: {str(e)}",

                template_name="Cargo.toml.j2"

            ) from e

        

        # src/hooks.rs

        try:

            template = self.env.get_template("hooks.rs.j2")

            generated_files['src/hooks.rs'] = template.render(**template_vars)

        except TemplateNotFound:

            generated_files['src/hooks.rs'] = self._generate_fallback_hooks_rs(template_vars)

        

        # Helper templates

        helper_templates = [

            "src/cli.rs.j2",

            "src/config.rs.j2",

            "src/errors.rs.j2",

            "src/completion.rs.j2"

        ]

        

        for template_name in helper_templates:

            try:

                helper_template = self.env.get_template(template_name)

                output_name = template_name.replace('.j2', '')

                generated_files[output_name] = helper_template.render(**template_vars)

            except TemplateNotFound:

                # Generate fallback if template doesn't exist

                if template_name == "src/cli.rs.j2":

                    generated_files['src/cli.rs'] = self._generate_fallback_cli_rs(template_vars)

            except Exception as e:

                # If helper template fails, provide better error information

                typer.echo(f"⚠️  Warning: Could not generate {template_name}", err=True)

                typer.echo(f"   Reason: {str(e)}", err=True)

                typer.echo(f"   Impact: The generated CLI will work but without {template_name.replace('.j2', '')} functionality", err=True)

                typer.echo(f"   Solution: Check template syntax or report this issue", err=True)

        

        # Setup script

        try:

            template = self.env.get_template("setup.sh.j2")

            generated_files['setup.sh'] = template.render(**template_vars)

        except TemplateNotFound:

            generated_files['setup.sh'] = self._generate_fallback_setup_sh(template_vars)

        

        # README.md

        generated_files['README.md'] = self._generate_readme(template_vars)

        

        # .gitignore

        generated_files['.gitignore'] = self._generate_gitignore()

        

        # Store generated files for later retrieval

        self._generated_files = generated_files

        

        # For backward compatibility, return the main CLI code

        return generated_files['src/main.rs']

    

    def generate_all_files(self, config, config_filename: str, version: Optional[str] = None) -> Dict[str, str]:

        """

        Generate all files needed for the Rust CLI.

        

        Args:

            config: The configuration object

            config_filename: Name of the configuration file

            version: Optional version string

            

        Returns:

            Dictionary mapping file paths to their contents

        """

        try:

            # Generate main file first to populate _generated_files

            self.generate(config, config_filename, version)

            

            # For universal templates, files are already generated during generate() call

            if self.use_universal_templates and self._generated_files:

                return self._generated_files.copy()  # Return a copy to prevent external modification

            

            # For legacy mode, return the stored files

            return self._generated_files.copy() if self._generated_files else {}

        except Exception as e:

            # Wrap and re-raise any errors

            raise TemplateError(

                f"Failed to generate all files: {str(e)}"

            ) from e

    

    def get_output_files(self) -> List[str]:

        """Return list of files this generator creates."""

        return [

            "src/main.rs",

            "src/hooks.rs",

            "src/cli.rs",

            "src/config.rs",

            "src/errors.rs",

            "src/completion.rs",

            "Cargo.toml",

            "setup.sh",

            "README.md",

            ".gitignore"

        ]

    

    def get_default_output_path(self, package_name: str) -> str:

        """Get the default output path for Rust CLI."""

        return "src/main.rs"

    

    def get_generated_files(self) -> dict:

        """Get all generated files from the last generate() call."""

        return getattr(self, '_generated_files', {})

    

    def _validate_config(self, config: ConfigSchema) -> None:

        """Validate configuration and provide helpful error messages."""

        cli = config.cli

        defined_commands = set(cli.commands.keys())

        

        # Validate command groups reference existing commands

        if cli.command_groups:

            for group in cli.command_groups:

                invalid_commands = set(group.commands) - defined_commands

                if invalid_commands:

                    raise ValidationError(

                        f"Command group '{group.name}' references non-existent commands: {', '.join(sorted(invalid_commands))}",

                        field=f"command_groups.{group.name}.commands",

                        value=str(list(invalid_commands)),

                        valid_options=list(defined_commands)

                    )

        

        # Validate command structure

        for cmd_name, cmd_data in cli.commands.items():

            if not cmd_data.desc:

                raise ValidationError(

                    f"Command '{cmd_name}' is missing required description",

                    field=f"commands.{cmd_name}.desc",

                    value="empty"

                )

            

            # Validate arguments

            if cmd_data.args:

                for arg in cmd_data.args:

                    if not arg.desc:

                        raise ValidationError(

                            f"Argument '{arg.name}' in command '{cmd_name}' is missing required description",

                            field=f"commands.{cmd_name}.args.{arg.name}.desc",

                            value="empty"

                        )

            

            # Validate options

            if cmd_data.options:

                valid_types = ['str', 'int', 'float', 'bool', 'flag']

                for opt in cmd_data.options:

                    if not opt.desc:

                        raise ValidationError(

                            f"Option '{opt.name}' in command '{cmd_name}' is missing required description",

                            field=f"commands.{cmd_name}.options.{opt.name}.desc",

                            value="empty"

                        )

                    if opt.type not in valid_types:

                        raise ValidationError(

                            f"Option '{opt.name}' in command '{cmd_name}' has invalid type '{opt.type}'",

                            field=f"commands.{cmd_name}.options.{opt.name}.type",

                            value=opt.type,

                            valid_options=valid_types

                        )

    

    def _to_rust_type(self, python_type: str) -> str:

        """Convert Python type hints to Rust types."""

        type_map = {

            'str': 'String',

            'int': 'i32',

            'float': 'f64',

            'bool': 'bool',

            'flag': 'bool',

            'list': 'Vec<String>',

            'dict': 'std::collections::HashMap<String, String>',

        }

        return type_map.get(python_type, 'String')

    

    def _to_snake_case(self, text: str) -> str:

        """Convert text to snake_case."""

        return text.replace('-', '_').replace(' ', '_').lower()

    

    def _to_screaming_snake_case(self, text: str) -> str:

        """Convert text to SCREAMING_SNAKE_CASE."""

        return self._to_snake_case(text).upper()

    

    def _to_pascal_case(self, text: str) -> str:

        """Convert text to PascalCase."""

        if not text:

            return text

        words = text.replace('-', '_').replace(' ', '_').split('_')

        return ''.join(word.capitalize() for word in words)

    

    def _escape_rust_string(self, text: str) -> str:

        """Escape string for Rust string literal."""

        return text.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n').replace('\t', '\\t')

    

    def _generate_fallback_main_rs(self, context: dict) -> str:

        """Generate a basic main.rs when templates are missing."""

        cli_config = context['cli']

        package_name = context['package_name'] or 'my-cli'

        command_name = context['command_name'] or package_name

        description = context.get('description', 'A CLI tool')

        version = context['version']

        

        return f'''//! Generated by goobits-cli

//! 

//! Note: Rust templates are not yet installed.

//! This is a basic CLI structure. To get full functionality,

//! ensure Rust templates are installed in:

//! src/goobits_cli/templates/rust/



use clap::{{Arg, ArgMatches, Command}};

use std::process;



mod hooks;



fn main() {{

    let app = Command::new("{command_name}")

        .about("{description}")

        .version("{version}")

        .subcommand_required(false)

        .arg_required_else_help(true);

    

    let app = build_cli(app);

    let matches = app.get_matches();

    

    if let Err(e) = handle_command(&matches) {{

        eprintln!("Error: {{}}", e);

        process::exit(1);

    }}

}}



fn build_cli(app: Command) -> Command {{

    let mut app = app;

    

    // Add commands from configuration

    {self._generate_fallback_commands(context)}

    

    app

}}



fn handle_command(matches: &ArgMatches) -> Result<(), Box<dyn std::error::Error>> {{

    match matches.subcommand() {{

        {self._generate_fallback_command_handlers(context)}

        _ => {{

            println!("No command specified. Use --help for available commands.");

            Ok(())

        }}

    }}

}}

'''

    

    def _generate_fallback_commands(self, context: dict) -> str:

        """Generate command definitions for fallback main.rs."""

        cli_config = context.get('cli')

        if not cli_config or not hasattr(cli_config, 'commands'):

            return '// No commands configured'

        

        commands = []

        for cmd_name, cmd_data in cli_config.commands.items():

            cmd_def = f'''app = app.subcommand(

        Command::new("{cmd_name}")

            .about("{cmd_data.desc if hasattr(cmd_data, 'desc') else 'Command description'}")'''

            

            # Add arguments

            if hasattr(cmd_data, 'args') and cmd_data.args:

                for arg in cmd_data.args:

                    if arg.required:

                        cmd_def += f'''

            .arg(Arg::new("{arg.name}")

                .help("{arg.desc}")

                .required(true)

                .index(1))'''

                    else:

                        cmd_def += f'''

            .arg(Arg::new("{arg.name}")

                .help("{arg.desc}")

                .required(false)

                .index(1))'''

            

            # Add options

            if hasattr(cmd_data, 'options') and cmd_data.options:

                for opt in cmd_data.options:

                    short_flag = f'-{opt.short}' if hasattr(opt, 'short') and opt.short else ''

                    cmd_def += f'''

            .arg(Arg::new("{opt.name}")

                .help("{opt.desc}")

                .short('{opt.short}')

                .long("{opt.name}")'''

                    if opt.type == 'flag':

                        cmd_def += '.action(clap::ArgAction::SetTrue))'

                    else:

                        cmd_def += '.value_name("VALUE"))'

            

            cmd_def += '''

    );'''

            commands.append(cmd_def)

        

        return '\n'.join(commands) if commands else '// No commands configured'

    

    def _generate_fallback_command_handlers(self, context: dict) -> str:

        """Generate command handlers for fallback main.rs."""

        cli_config = context.get('cli')

        if not cli_config or not hasattr(cli_config, 'commands'):

            return ''

        

        handlers = []

        for cmd_name, cmd_data in cli_config.commands.items():

            safe_cmd_name = self._to_snake_case(cmd_name)

            handlers.append(f'''Some(("{cmd_name}", sub_matches)) => {{

            println!("Executing {cmd_name} command...");

            
            // Try to call hook, but gracefully handle if it doesn't exist
            match hooks::on_{safe_cmd_name}(sub_matches) {{
                Ok(_) => Ok(()),
                Err(e) => {{
                    // Check if it's a "function not found" type error
                    let error_msg = format!("{{:?}}", e);
                    if error_msg.contains("not implemented") || error_msg.contains("not found") {{
                        // Hook not implemented - show placeholder behavior
                        println!("Command '{cmd_name}' executed successfully (no custom implementation)");
                        println!("To implement custom behavior, add the 'on_{safe_cmd_name}' function to src/hooks.rs");
                        Ok(())
                    }} else {{
                        // Real error - propagate it
                        Err(e)
                    }}
                }}
            }}

        }}''')

        

        return '\n        '.join(handlers)

    

    def _generate_fallback_cargo_toml(self, context: dict) -> str:

        """Generate minimal Cargo.toml from context."""

        package_name = context['package_name'].replace('-', '_')

        display_name = context['display_name']

        description = context.get('description', 'A CLI tool')

        version = context['version']

        

        return f'''[package]

name = "{package_name}"

version = "{version}"

description = "{description}"

edition = "2021"



[[bin]]

name = "{context['command_name']}"

path = "src/main.rs"



[dependencies]

clap = {{ version = "4.0", features = ["derive"] }}

serde = {{ version = "1.0", features = ["derive"] }}

serde_json = "1.0"

tokio = {{ version = "1.0", features = ["full"] }}

anyhow = "1.0"

thiserror = "1.0"

'''

    

    def _generate_fallback_hooks_rs(self, context: dict) -> str:

        """Generate hooks.rs with function stubs."""

        cli_config = context.get('cli')

        hooks_content = f'''//! Hook functions for {context['display_name']}

//! Auto-generated from {context['file_name']}

//! 

//! Implement your business logic in these hook functions.

//! Each command will call its corresponding hook function.



use clap::ArgMatches;

use anyhow::Result;



'''

        

        # Generate hook functions for each command

        if cli_config and hasattr(cli_config, 'commands'):

            for cmd_name, cmd_data in cli_config.commands.items():

                safe_cmd_name = self._to_snake_case(cmd_name)

                hooks_content += f'''/// Hook function for '{cmd_name}' command

pub fn on_{safe_cmd_name}(matches: &ArgMatches) -> Result<()> {{

    // Return error indicating this hook is not implemented
    // This allows the main CLI to show placeholder behavior
    Err(anyhow::anyhow!("Hook function 'on_{safe_cmd_name}' not implemented"))

}}



'''

        

        return hooks_content

    

    def _generate_fallback_cli_rs(self, context: dict) -> str:

        """Generate cli.rs module."""

        return '''//! CLI command definitions and parsing logic



use clap::Command;



pub fn build_cli() -> Command {

    Command::new(env!("CARGO_PKG_NAME"))

        .about(env!("CARGO_PKG_DESCRIPTION"))

        .version(env!("CARGO_PKG_VERSION"))

}

'''

    

    def _generate_fallback_setup_sh(self, context: dict) -> str:

        """Generate setup.sh script for Rust CLI."""

        return f'''#!/bin/bash

# Setup script for {context['display_name']}

# Auto-generated from {context['file_name']}



set -e



echo "🔧 Setting up {context['display_name']}..."



# Check if Rust is installed

if ! command -v rustc &> /dev/null; then

    echo "❌ Rust not found. Please install Rust first:"

    echo "   https://rustup.rs/"

    exit 1

fi



# Check if Cargo is installed

if ! command -v cargo &> /dev/null; then

    echo "❌ Cargo not found. Please install Rust toolchain first."

    exit 1

fi



# Build the project

echo "🔨 Building Rust project..."

cargo build --release



if [ $? -eq 0 ]; then

    echo "✅ Build successful!"

    echo "📍 Binary location: target/release/{context['command_name']}"

    echo ""

    echo "To install globally:"

    echo "   cargo install --path ."

    echo ""

    echo "To run locally:"

    echo "   cargo run -- --help"

    echo "   # or"

    echo "   ./target/release/{context['command_name']} --help"

else

    echo "❌ Build failed!"

    exit 1

fi

'''

    

    def _generate_readme(self, context: dict) -> str:

        """Generate README.md for the Rust CLI."""

        # Use DocumentationGenerator if available

        if self.doc_generator and DocumentationGenerator:

            try:

                return self.doc_generator.generate_readme()

            except Exception:

                # Fallback to manual generation if doc_generator fails

                pass

        

        # Fallback to existing implementation

        return f"""# {context['display_name']}



{context.get('description', 'A CLI tool built with Rust')}



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

cargo install --path .

```



## Usage



```bash

{context['command_name']} --help

```



## Commands



{self._generate_commands_documentation(context)}



## Development



To run in development mode:

```bash

# Build the project

cargo build



# Run locally

cargo run -- --help



# Run tests

cargo test



# Format code

cargo fmt



# Check with clippy

cargo clippy

```



To implement command logic, edit the hook functions in `src/hooks.rs`.



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

        return """# Rust

/target/

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



# Config (keep local config private)

config.local.toml

"""