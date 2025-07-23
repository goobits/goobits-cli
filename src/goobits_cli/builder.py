#!/usr/bin/env python3
import sys
import yaml
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from pydantic import ValidationError

from .schemas import ConfigSchema
from .formatter import align_examples, format_multiline_text, escape_for_docstring, align_setup_steps


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
    
    template = env.get_template("cli_template.py.j2")
    
    # Render the template
    code = template.render(
        cli=config.cli,
        file_name=file_name
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