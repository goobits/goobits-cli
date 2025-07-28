#!/usr/bin/env python3
import sys
import yaml
from pathlib import Path
from typing import Union
from jinja2 import Environment, FileSystemLoader
from pydantic import ValidationError
import typer

from .schemas import ConfigSchema
from .formatter import align_examples, format_multiline_text, escape_for_docstring, align_setup_steps, format_icon_spacing, align_header_items


def load_yaml_config(file_path: str) -> ConfigSchema:
    """Load and validate YAML configuration file."""
    try:
        with open(file_path, 'r') as f:
            data = yaml.safe_load(f)
        
        config = ConfigSchema(**data)
        return config
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.", file=sys.stderr)
        raise typer.Exit(code=1)
    except yaml.YAMLError as e:
        print(f"Error parsing YAML: {e}", file=sys.stderr)
        raise typer.Exit(code=1)
    except ValidationError as e:
        print(f"Error validating configuration: {e}", file=sys.stderr)
        raise typer.Exit(code=1)


class Builder:
    """CLI code builder that generates Python code from YAML configuration."""
    
    def __init__(self):
        """Initialize the Builder with Jinja2 environment."""
        # Set up Jinja2 environment
        template_dir = Path(__file__).parent / "templates"
        self.env = Environment(loader=FileSystemLoader(template_dir))
        
        # Add custom filters
        self.env.filters['align_examples'] = align_examples
        self.env.filters['format_multiline'] = format_multiline_text
        self.env.filters['escape_docstring'] = escape_for_docstring
        self.env.filters['align_setup_steps'] = align_setup_steps
        self.env.filters['format_icon'] = format_icon_spacing
        self.env.filters['align_header_items'] = align_header_items
    
    def build(self, config: Union[ConfigSchema, 'GoobitsConfigSchema'], file_name: str = "config.yaml") -> str:
        """Build CLI Python code from configuration and return the rendered template string."""
        # Extract CLI configuration and metadata depending on config type
        if hasattr(config, 'package_name'):  # GoobitsConfigSchema
            cli_config = config.cli
            package_name = config.package_name
            command_name = config.command_name
            display_name = config.display_name
            installation = config.installation
        else:  # ConfigSchema
            cli_config = config.cli
            package_name = ""
            command_name = ""
            display_name = ""
            installation = None
            
        # Validate configuration before building - only validate CLI for GoobitsConfigSchema
        if hasattr(config, 'package_name'):  # GoobitsConfigSchema
            if not cli_config:
                raise ValueError("No CLI configuration found")
        else:  # ConfigSchema
            self._validate_config(config)
        
        # Serialize the CLI part of the config to a JSON string
        # We need to escape backslashes and quotes for embedding in Python code
        import json
        cli_dict = cli_config.model_dump()
        cli_config_json = json.dumps(cli_dict, indent=2, ensure_ascii=False)
        # Escape backslashes so they're preserved when Python interprets the string
        cli_config_json = cli_config_json.replace("\\", "\\\\")
        # Also escape any potential triple quotes
        cli_config_json = cli_config_json.replace("'''", "\\'\\'\\'")
        
        template = self.env.get_template("cli_template.py.j2")
        
        # Render the template
        code = template.render(
            cli=cli_config,
            file_name=file_name,
            cli_config_json=cli_config_json,
            package_name=package_name,
            command_name=command_name,
            display_name=display_name,
            installation=installation
        )
        
        # Explicitly assert the type to satisfy mypy
        assert isinstance(code, str)
        return code
    
    def _validate_config(self, config: ConfigSchema) -> None:
        """Validate configuration and provide helpful error messages."""
        cli = config.cli
        defined_commands = set(cli.commands.keys())
        
        # Validate command groups reference existing commands
        if cli.command_groups:
            for group in cli.command_groups:
                invalid_commands = set(group.commands) - defined_commands
                if invalid_commands:
                    print(f"❌ Error: Command group '{group.name}' references non-existent commands: {', '.join(sorted(invalid_commands))}")
                    print(f"   Available commands: {', '.join(sorted(defined_commands))}")
                    raise typer.Exit(code=1)
        
        # Validate command structure
        for cmd_name, cmd_data in cli.commands.items():
            if not cmd_data.desc:
                print(f"❌ Error: Command '{cmd_name}' is missing required 'desc' field")
                raise typer.Exit(code=1)
            
            # Validate arguments
            if cmd_data.args:
                for arg in cmd_data.args:
                    if not arg.desc:
                        print(f"❌ Error: Argument '{arg.name}' in command '{cmd_name}' is missing required 'desc' field")
                        raise typer.Exit(code=1)
            
            # Validate options
            if cmd_data.options:
                for opt in cmd_data.options:
                    if not opt.desc:
                        print(f"❌ Error: Option '{opt.name}' in command '{cmd_name}' is missing required 'desc' field")
                        raise typer.Exit(code=1)
                    if opt.type not in ['str', 'int', 'float', 'bool', 'flag']:
                        print(f"❌ Error: Option '{opt.name}' in command '{cmd_name}' has invalid type '{opt.type}'")
                        print("   Valid types: str, int, float, bool, flag")
                        raise typer.Exit(code=1)


def generate_cli_code(config: Union[ConfigSchema, 'GoobitsConfigSchema'], file_name: str) -> str:
    """Generate CLI Python code from configuration."""
    builder = Builder()
    return builder.build(config, file_name)