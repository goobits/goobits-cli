#!/usr/bin/env python3


import yaml


from typing import Union, Optional

from pydantic import ValidationError

import typer



# Lazy import for heavy schemas to improve startup performance
_schemas = None

def _get_schemas():
    """Lazy load schema classes to avoid Pydantic import overhead."""
    global _schemas
    if _schemas is None:
        from .schemas import ConfigSchema, GoobitsConfigSchema
        _schemas = (ConfigSchema, GoobitsConfigSchema)
    return _schemas

# Lazy import for generator  
_python_generator = None

def _get_python_generator():
    """Lazy load Python generator to reduce startup overhead.""" 
    global _python_generator
    if _python_generator is None:
        from .generators.python import PythonGenerator
        _python_generator = PythonGenerator
    return _python_generator





def load_yaml_config(file_path: str):

    """Load and validate YAML configuration file."""

    try:

        with open(file_path, 'r') as f:

            data = yaml.safe_load(f)

        

        # Get schema classes lazily
        ConfigSchema, GoobitsConfigSchema = _get_schemas()

        # Try to detect which schema format this is
        # If it has top-level fields like package_name, language, etc., it's GoobitsConfigSchema
        # If it only has 'cli' field, it's ConfigSchema
        if any(key in data for key in ['package_name', 'command_name', 'language', 'hooks_path', 'installation']):
            config = GoobitsConfigSchema(**data)
        else:
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
            # Default to Python - lazy load the generator
            PythonGenerator = _get_python_generator()
            self.generator = PythonGenerator()

    def build(self, config = None, file_name: str = "config.yaml", version: Optional[str] = None) -> str:

        """Build CLI code from configuration and return the rendered template string."""

        # If config is not provided but config_data was provided in constructor, use that

        if config is None and self.config_data is not None:
            ConfigSchema, GoobitsConfigSchema = _get_schemas()
            config = ConfigSchema(**self.config_data)

        

        if config is None:

            raise ValueError("No configuration provided")

        
        # Detect language from config and initialize appropriate generator if needed
        config_language = None
        if isinstance(config, dict):
            config_language = config.get('language', self.language)  # Use builder's language as default
        elif hasattr(config, 'language'):
            config_language = config.language
        else:
            # For ConfigSchema, use the language specified in the builder constructor
            # This preserves backward compatibility for tests that specify language in Builder()
            config_language = self.language
        
        # If the detected language differs from initialized language, switch generator
        if config_language != self.language:
            self.language = config_language
            self._initialize_generator(config_language)
            

        return self.generator.generate(config, file_name, version)





def generate_cli_code(config, file_name: str, version: Optional[str] = None) -> str:

    """Generate CLI Python code from configuration.

    

    This function is maintained for backward compatibility.

    It delegates to the PythonGenerator class.

    

    Args:

        config: Configuration object

        file_name: Name of configuration file

        version: Optional version string

    """

    PythonGenerator = _get_python_generator()
    generator = PythonGenerator()

    return generator.generate(config, file_name, version)