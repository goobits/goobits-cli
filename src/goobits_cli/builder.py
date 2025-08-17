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

    

    def __init__(self, config_data=None, language: str = "python"):

        """Initialize the Builder with appropriate generator.

        

        Args:

            config_data: Configuration data (dict) - for test compatibility

            language: Target language ("python", "nodejs", "typescript")

        """

        self.language = language

        self.config_data = config_data

        

        # Initialize the appropriate generator based on language (lazy import to avoid circular imports)
        self._initialize_generator(language)

    def _initialize_generator(self, language: str):
        """Initialize the appropriate generator based on language."""
        if language == "nodejs":
            from .generators.nodejs import NodeJSGenerator
            self.generator = NodeJSGenerator()
        elif language == "typescript":
            from .generators.typescript import TypeScriptGenerator
            self.generator = TypeScriptGenerator()
        elif language == "rust":
            from .generators.rust import RustGenerator
            self.generator = RustGenerator()
        else:
            # Default to Python
            from .generators.python import PythonGenerator
            self.generator = PythonGenerator()

    def build(self, config: Union[ConfigSchema, 'GoobitsConfigSchema', None] = None, file_name: str = "config.yaml", version: Optional[str] = None) -> str:

        """Build CLI code from configuration and return the rendered template string."""

        # If config is not provided but config_data was provided in constructor, use that

        if config is None and self.config_data is not None:

            config = ConfigSchema(**self.config_data)

        

        if config is None:

            raise ValueError("No configuration provided")

        
        # Detect language from config and initialize appropriate generator if needed
        config_language = None
        if isinstance(config, dict):
            config_language = config.get('language', 'python')
        elif hasattr(config, 'language'):
            config_language = config.language
        else:
            # For ConfigSchema, language might be under cli or a separate field
            config_language = getattr(config, 'language', 'python')
        
        # If the detected language differs from initialized language, switch generator
        if config_language != self.language:
            self.language = config_language
            self._initialize_generator(config_language)
            

        return self.generator.generate(config, file_name, version)





def generate_cli_code(config: Union[ConfigSchema, 'GoobitsConfigSchema'], file_name: str, version: Optional[str] = None) -> str:

    """Generate CLI Python code from configuration.

    

    This function is maintained for backward compatibility.

    It delegates to the PythonGenerator class.

    

    Args:

        config: Configuration object

        file_name: Name of configuration file

        version: Optional version string

    """

    generator = PythonGenerator()

    return generator.generate(config, file_name, version)