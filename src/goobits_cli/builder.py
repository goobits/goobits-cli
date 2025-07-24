#!/usr/bin/env python3
import sys
import yaml
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from pydantic import ValidationError

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
        sys.exit(1)
    except yaml.YAMLError as e:
        print(f"Error parsing YAML: {e}", file=sys.stderr)
        sys.exit(1)
    except ValidationError as e:
        print(f"Error validating configuration: {e}", file=sys.stderr)
        sys.exit(1)


def generate_cli_code(config: ConfigSchema, file_name: str) -> str:
    """Generate CLI Python code from configuration."""
    # Set up Jinja2 environment
    template_dir = Path(__file__).parent / "templates"
    env = Environment(loader=FileSystemLoader(template_dir))
    
    # Add custom filters
    env.filters['align_examples'] = align_examples
    env.filters['format_multiline'] = format_multiline_text
    env.filters['escape_docstring'] = escape_for_docstring
    env.filters['align_setup_steps'] = align_setup_steps
    env.filters['format_icon'] = format_icon_spacing
    env.filters['align_header_items'] = align_header_items
    
    # Serialize the CLI part of the config to a JSON string
    # We need to escape backslashes and quotes for embedding in Python code
    import json
    cli_dict = config.cli.model_dump()
    cli_config_json = json.dumps(cli_dict, indent=2, ensure_ascii=False)
    # Escape backslashes so they're preserved when Python interprets the string
    cli_config_json = cli_config_json.replace("\\", "\\\\")
    # Also escape any potential triple quotes
    cli_config_json = cli_config_json.replace("'''", "\\'\\'\\'")
    
    template = env.get_template("cli_template.py.j2")
    
    # Render the template
    code = template.render(
        cli=config.cli,
        file_name=file_name,
        cli_config_json=cli_config_json
    )
    
    return code


def main():
    """Main entry point for the CLI builder."""
    if len(sys.argv) != 2:
        print("Usage: python -m src.builder <yaml_file>", file=sys.stderr)
        sys.exit(1)
    
    yaml_file = sys.argv[1]
    
    # Load and validate configuration
    config = load_yaml_config(yaml_file)
    
    # Generate CLI code
    code = generate_cli_code(config, Path(yaml_file).name)
    
    # Output to stdout
    print(code)


if __name__ == "__main__":
    main()