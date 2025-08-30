"""
Interactive Framework
===================

Core framework extracted from interactive_mode.j2 template.
Orchestrates interactive mode generation for all languages with consistent behavior.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Any, Optional, List
from enum import Enum


class REPLMode(Enum):
    """Supported REPL modes."""
    BASIC = "basic"
    SESSION = "session"
    VARIABLES = "variables"
    PIPELINES = "pipelines"


@dataclass
class FeatureConfig:
    """Feature configuration for interactive mode."""
    repl_enabled: bool = False
    session_persistence: bool = False
    variables: bool = False
    pipelines: bool = False
    smart_completion: bool = True
    
    # Session configuration
    auto_save: bool = False
    max_sessions: int = 20
    session_directory: str = ""
    auto_load_last: bool = False
    max_history: int = 1000
    
    # Variable configuration
    variable_expansion: bool = True
    max_variables: int = 100
    
    # Pipeline configuration
    pipeline_templates: bool = True
    pipeline_timeout: int = 60


@dataclass
class InteractiveConfig:
    """Interactive mode configuration schema."""
    project_name: str
    command_name: str
    features: FeatureConfig
    cli_commands: List[Dict[str, Any]]


class InteractiveFramework:
    """
    Interactive framework extracted from interactive_mode.j2.
    
    Generates interactive mode code for all supported languages
    with consistent REPL behavior, session management, and feature support.
    """
    
    def __init__(self):
        """Initialize the interactive framework."""
        from .language_adapters import (
            PythonInteractiveAdapter,
            NodeJSInteractiveAdapter,
            TypeScriptInteractiveAdapter,
            RustInteractiveAdapter
        )
        
        self._adapters = {
            'python': PythonInteractiveAdapter(),
            'nodejs': NodeJSInteractiveAdapter(),
            'typescript': TypeScriptInteractiveAdapter(),
            'rust': RustInteractiveAdapter()
        }
    
    def generate_interactive_code(self, language: str, config: Dict[str, Any]) -> str:
        """
        Generate interactive mode code for specified language.
        
        Args:
            language: Target language ('python', 'nodejs', 'typescript', 'rust')
            config: Configuration including project metadata and features
            
        Returns:
            Generated interactive mode code as string
            
        Raises:
            ValueError: If language is not supported
        """
        if language not in self._adapters:
            supported = ', '.join(self._adapters.keys())
            raise ValueError(f"Unsupported language: {language}. Supported languages: {supported}")
        
        # Process configuration
        interactive_config = self._process_configuration(config)
        
        # Validate configuration
        self._validate_configuration(interactive_config)
        
        # Generate code using appropriate adapter
        adapter = self._adapters[language]
        return adapter.generate_code(interactive_config)
    
    def _process_configuration(self, config: Dict[str, Any]) -> InteractiveConfig:
        """Process raw configuration into structured schema."""
        project = config.get('project', {})
        features_config = config.get('features', {}).get('interactive_mode', {})
        
        # Extract feature configuration
        features = FeatureConfig(
            repl_enabled=features_config.get('repl', False),
            session_persistence=features_config.get('session_persistence', False),
            variables=features_config.get('variables', False),
            pipelines=features_config.get('pipelines', False),
            smart_completion=features_config.get('smart_completion', True),
            
            # Session settings
            auto_save=features_config.get('auto_save', False),
            max_sessions=features_config.get('max_sessions', 20),
            session_directory=features_config.get('session_directory', ''),
            auto_load_last=features_config.get('auto_load_last', False),
            max_history=features_config.get('max_history', 1000),
            
            # Variable settings
            variable_expansion=features_config.get('variable_expansion', True),
            max_variables=features_config.get('max_variables', 100),
            
            # Pipeline settings
            pipeline_templates=features_config.get('pipeline_templates', True),
            pipeline_timeout=features_config.get('pipeline_timeout', 60)
        )
        
        # Extract CLI commands
        cli_commands = []
        cli_config = config.get('cli', {})
        commands = cli_config.get('commands', {})
        for cmd_name, cmd_data in commands.items():
            cli_commands.append({
                'name': cmd_name,
                'description': cmd_data.get('desc', cmd_data.get('description', '')),
                'hook_name': f"on_{cmd_name.replace('-', '_')}",
                'args': cmd_data.get('args', []),
                'options': cmd_data.get('options', [])
            })
        
        return InteractiveConfig(
            project_name=project.get('name', 'CLI'),
            command_name=project.get('command_name', project.get('name', 'cli')),
            features=features,
            cli_commands=cli_commands
        )
    
    def _validate_configuration(self, config: InteractiveConfig) -> None:
        """Validate the processed configuration."""
        if not config.project_name:
            raise ValueError("Project name is required for interactive mode")
        
        if not config.command_name:
            raise ValueError("Command name is required for interactive mode")
        
        # Validate feature dependencies
        if config.features.pipelines and not config.features.variables:
            # Pipelines require variables, auto-enable them
            config.features.variables = True
        
        if config.features.variables and not config.features.session_persistence:
            # Variables work better with sessions, but not required
            pass
        
        # Validate limits
        if config.features.max_sessions < 1:
            raise ValueError("max_sessions must be at least 1")
        
        if config.features.max_variables < 1:
            raise ValueError("max_variables must be at least 1")
        
        if config.features.pipeline_timeout < 1:
            raise ValueError("pipeline_timeout must be at least 1 second")
    
    def get_repl_mode(self, features: FeatureConfig) -> REPLMode:
        """Determine the appropriate REPL mode based on enabled features."""
        if features.pipelines:
            return REPLMode.PIPELINES
        elif features.variables:
            return REPLMode.VARIABLES
        elif features.session_persistence:
            return REPLMode.SESSION
        else:
            return REPLMode.BASIC
    
    def get_feature_list(self, features: FeatureConfig) -> List[str]:
        """Get list of enabled features for display."""
        feature_list = []
        
        if features.smart_completion:
            feature_list.append("Smart completion")
        
        if features.pipelines:
            feature_list.append("Pipeline operations")
        
        if features.variables:
            feature_list.append("Variable management")
        
        if features.session_persistence:
            feature_list.append("Session persistence")
        
        return feature_list