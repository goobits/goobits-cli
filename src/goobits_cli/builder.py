#!/usr/bin/env python3
import sys
import yaml
from pathlib import Path
from typing import Union, Optional
from pydantic import ValidationError
import typer

from .schemas import ConfigSchema
from .generators.python import PythonGenerator


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
    """CLI code builder that generates Python code from YAML configuration.
    
    This class is maintained for backward compatibility.
    It delegates to the PythonGenerator class.
    """
    
    def __init__(self, use_universal_templates: bool = False):
        """Initialize the Builder with a PythonGenerator instance.
        
        Args:
            use_universal_templates: If True, use Universal Template System
        """
        self.generator = PythonGenerator(use_universal_templates=use_universal_templates)
    
    def build(self, config: Union[ConfigSchema, 'GoobitsConfigSchema'], file_name: str = "config.yaml", version: Optional[str] = None) -> str:
        """Build CLI Python code from configuration and return the rendered template string."""
        return self.generator.generate(config, file_name, version)


def generate_cli_code(config: Union[ConfigSchema, 'GoobitsConfigSchema'], file_name: str, version: Optional[str] = None, use_universal_templates: bool = False) -> str:
    """Generate CLI Python code from configuration.
    
    This function is maintained for backward compatibility.
    It delegates to the PythonGenerator class.
    
    Args:
        config: Configuration object
        file_name: Name of configuration file
        version: Optional version string
        use_universal_templates: If True, use Universal Template System
    """
    generator = PythonGenerator(use_universal_templates=use_universal_templates)
    return generator.generate(config, file_name, version)