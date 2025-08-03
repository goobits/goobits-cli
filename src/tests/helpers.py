"""Helper functions for tests to match the actual implementation."""
from typing import Dict, Optional
from goobits_cli.schemas import ConfigSchema, GoobitsConfigSchema
from goobits_cli.generators.nodejs import NodeJSGenerator
from goobits_cli.generators.python import PythonGenerator


def determine_language(config: GoobitsConfigSchema) -> str:
    """Determine the target language from configuration."""
    return config.language


def generate_cli(config: GoobitsConfigSchema, filename: str, version: Optional[str] = None) -> Dict[str, str]:
    """Generate CLI files based on the configuration language.
    
    Returns a dictionary mapping file paths to their contents.
    For Python, returns a single-entry dict with the CLI script.
    For Node.js, returns multiple files.
    """
    language = determine_language(config)
    
    if language == "nodejs":
        generator = NodeJSGenerator()
        return generator.generate_all_files(config, filename, version)
    else:
        # Default to Python
        generator = PythonGenerator()
        cli_code = generator.generate(config, filename, version)
        return {'cli.py': cli_code}  # Single file for Python