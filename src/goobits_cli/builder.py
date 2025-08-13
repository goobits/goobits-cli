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

        typer.echo(f"Error: File '{file_path}' not found.", err=True)

        raise typer.Exit(code=1)

    except yaml.YAMLError as e:

        typer.echo(f"Error parsing YAML: {e}", err=True)

        raise typer.Exit(code=1)

    except ValidationError as e:

        typer.echo(f"Error validating configuration: {e}", err=True)

        raise typer.Exit(code=1)





class Builder:

    """CLI code builder that generates code from YAML configuration.

    

    This class supports multiple languages and can be used for backward compatibility.

    """

    

    def __init__(self, config_data=None, language: str = "python", use_universal_templates: bool = False):

        """Initialize the Builder with appropriate generator.

        

        Args:

            config_data: Configuration data (dict) - for test compatibility

            language: Target language ("python", "nodejs", "typescript")

            use_universal_templates: If True, use Universal Template System

        """

        self.language = language

        self.use_universal_templates = use_universal_templates

        self.config_data = config_data

        

        # Initialize the appropriate generator based on language (lazy import to avoid circular imports)

        if language == "nodejs":

            from .generators.nodejs import NodeJSGenerator

            self.generator = NodeJSGenerator(use_universal_templates=use_universal_templates)

        elif language == "typescript":

            from .generators.typescript import TypeScriptGenerator

            self.generator = TypeScriptGenerator(use_universal_templates=use_universal_templates)

        else:

            # Default to Python

            self.generator = PythonGenerator(use_universal_templates=use_universal_templates)

    

    def build(self, config: Union[ConfigSchema, 'GoobitsConfigSchema', None] = None, file_name: str = "config.yaml", version: Optional[str] = None) -> str:

        """Build CLI code from configuration and return the rendered template string."""

        # If config is not provided but config_data was provided in constructor, use that

        if config is None and self.config_data is not None:

            config = ConfigSchema(**self.config_data)

        

        if config is None:

            raise ValueError("No configuration provided")

            

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