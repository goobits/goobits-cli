"""
Configuration Framework
======================

Core framework extracted from config_manager.j2 template.
Orchestrates configuration management code generation for all languages.
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional, List
from enum import Enum


class ConfigFormat(Enum):
    """Supported configuration file formats."""
    YAML = "yaml"
    JSON = "json"
    TOML = "toml"


@dataclass
class ConfigProperty:
    """Configuration property definition."""
    name: str
    type: str
    default: Any = None
    description: str = ""
    required: bool = False
    env_var: Optional[str] = None


@dataclass 
class ConfigSchema:
    """Configuration schema definition."""
    properties: List[ConfigProperty]
    format: ConfigFormat = ConfigFormat.YAML
    env_prefix: str = ""
    config_dir_name: str = ""


class ConfigFramework:
    """
    Configuration framework extracted from config_manager.j2.
    
    Generates configuration management code for all supported languages
    with consistent behavior for file I/O, environment variables, and defaults.
    """
    
    def __init__(self):
        """Initialize the configuration framework."""
        from .language_adapters import (
            PythonConfigAdapter,
            NodeJSConfigAdapter, 
            TypeScriptConfigAdapter,
            RustConfigAdapter
        )
        
        self._adapters = {
            'python': PythonConfigAdapter(),
            'nodejs': NodeJSConfigAdapter(),
            'typescript': TypeScriptConfigAdapter(),
            'rust': RustConfigAdapter()
        }
    
    def generate_config_code(self, language: str, config: Dict[str, Any]) -> str:
        """
        Generate configuration management code for specified language.
        
        Args:
            language: Target language ('python', 'nodejs', 'typescript', 'rust')
            config: Configuration including project metadata and schema
            
        Returns:
            Generated configuration management code as string
            
        Raises:
            ValueError: If language is not supported
        """
        if language not in self._adapters:
            supported = ', '.join(self._adapters.keys())
            raise ValueError(f"Unsupported language: {language}. Supported languages: {supported}")
        
        # Process configuration
        config_schema = self._process_configuration(config)
        
        # Validate configuration
        self._validate_configuration(config_schema)
        
        # Generate code using appropriate adapter
        adapter = self._adapters[language]
        return adapter.generate_code(config_schema)
    
    def _process_configuration(self, config: Dict[str, Any]) -> ConfigSchema:
        """Process raw configuration into structured schema."""
        project = config.get('project', {})
        
        # Extract properties from config schema if provided
        properties = []
        config_schema = config.get('config_schema', {})
        
        if 'properties' in config_schema:
            for prop_name, prop_info in config_schema['properties'].items():
                properties.append(ConfigProperty(
                    name=prop_name,
                    type=prop_info.get('type', 'str'),
                    default=prop_info.get('default'),
                    description=prop_info.get('description', ''),
                    required=prop_info.get('required', False),
                    env_var=prop_info.get('env_var')
                ))
        else:
            # Default properties if none specified
            properties = [
                ConfigProperty(
                    name='debug',
                    type='bool', 
                    default=False,
                    description='Enable debug mode'
                ),
                ConfigProperty(
                    name='output_format',
                    type='str',
                    default='text',
                    description='Output format for CLI'
                )
            ]
        
        # Generate environment variable prefix
        project_name = project.get('name', 'app')
        env_prefix = project_name.upper().replace(' ', '_').replace('-', '_')
        
        # Generate config directory name
        config_dir_name = project_name.lower().replace(' ', '-')
        
        return ConfigSchema(
            properties=properties,
            format=ConfigFormat(config.get('config_format', 'yaml')),
            env_prefix=env_prefix,
            config_dir_name=config_dir_name
        )
    
    def _validate_configuration(self, config_schema: ConfigSchema) -> None:
        """Validate the processed configuration schema."""
        if not config_schema.properties:
            raise ValueError("Configuration schema must have at least one property")
        
        # Validate property names
        for prop in config_schema.properties:
            if not prop.name or not prop.name.isidentifier():
                raise ValueError(f"Invalid property name: {prop.name}")
            
            if prop.type not in ['str', 'int', 'float', 'bool', 'list', 'dict']:
                raise ValueError(f"Unsupported property type: {prop.type}")