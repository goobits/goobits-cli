"""Python CLI generator implementation."""

import json
import sys
from pathlib import Path
from typing import List, Optional, Union
from jinja2 import Environment, FileSystemLoader
import typer

from . import BaseGenerator
from ..schemas import ConfigSchema, GoobitsConfigSchema
from ..formatter import (
    align_examples, format_multiline_text, escape_for_docstring,
    align_setup_steps, format_icon_spacing, align_header_items
)


class PythonGenerator(BaseGenerator):
    """CLI code generator for Python using Typer framework."""
    
    def __init__(self):
        """Initialize the Python generator with Jinja2 environment."""
        # Set up Jinja2 environment
        template_dir = Path(__file__).parent.parent / "templates"
        self.env = Environment(loader=FileSystemLoader(template_dir))
        
        # Add custom filters
        self.env.filters['align_examples'] = align_examples
        self.env.filters['format_multiline'] = format_multiline_text
        self.env.filters['escape_docstring'] = escape_for_docstring
        self.env.filters['align_setup_steps'] = align_setup_steps
        self.env.filters['format_icon'] = format_icon_spacing
        self.env.filters['align_header_items'] = align_header_items
    
    def generate(self, config: Union[ConfigSchema, GoobitsConfigSchema], 
                 config_filename: str, version: Optional[str] = None) -> str:
        """
        Generate Python CLI code from configuration.
        
        Args:
            config: The configuration object
            config_filename: Name of the configuration file
            version: Optional version string
            
        Returns:
            Generated Python CLI code
        """
        # Extract metadata using base class helper
        metadata = self._extract_config_metadata(config)
        cli_config = metadata['cli_config']
        
        # Validate configuration before building - only validate CLI for GoobitsConfigSchema
        if hasattr(config, 'package_name'):  # GoobitsConfigSchema
            if not cli_config:
                raise ValueError("No CLI configuration found")
        else:  # ConfigSchema
            self._validate_config(config)
        
        # Serialize the CLI part of the config to a JSON string
        # We need to escape backslashes and quotes for embedding in Python code
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
            file_name=config_filename,
            cli_config_json=cli_config_json,
            package_name=metadata['package_name'],
            command_name=metadata['command_name'],
            display_name=metadata['display_name'],
            installation=metadata['installation'],
            hooks_path=metadata['hooks_path'],
            version=version
        )
        
        # Explicitly assert the type to satisfy mypy
        assert isinstance(code, str)
        return code
    
    def get_output_files(self) -> List[str]:
        """Return list of files this generator creates."""
        return ["cli.py"]  # Python generator creates a single CLI file
    
    def get_default_output_path(self, package_name: str) -> str:
        """Get the default output path for Python CLI."""
        return "src/{package_name}/cli.py"
    
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