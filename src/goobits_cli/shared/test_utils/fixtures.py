"""Common test fixtures and data for all language generators.

This module provides standard test configurations, CLI schemas, and mock objects
that can be reused across different test scenarios and language generators.
"""
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from pathlib import Path

from goobits_cli.schemas import (
    GoobitsConfigSchema, CLISchema, CommandSchema, ArgumentSchema, OptionSchema,
    PythonConfigSchema, DependenciesSchema, InstallationSchema, 
    ShellIntegrationSchema, ValidationSchema, MessagesSchema
)


@dataclass
class TestFixtures:
    """Central repository of test fixtures and common test data."""
    
    # Standard test configurations by complexity
    minimal_configs: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    basic_configs: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    complex_configs: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    
    # Command and option templates
    common_commands: Dict[str, CommandSchema] = field(default_factory=dict)
    common_arguments: Dict[str, ArgumentSchema] = field(default_factory=dict)
    common_options: Dict[str, OptionSchema] = field(default_factory=dict)
    
    # Expected outputs for testing
    expected_outputs: Dict[str, Dict[str, str]] = field(default_factory=dict)
    error_scenarios: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    
    def __post_init__(self):
        """Initialize all fixture data."""
        self._initialize_common_arguments()
        self._initialize_common_options()
        self._initialize_common_commands()
        self._initialize_configs()
        self._initialize_expected_outputs()
        self._initialize_error_scenarios()
    
    def _initialize_common_arguments(self):
        """Initialize reusable argument schemas."""
        self.common_arguments = {
            'name': ArgumentSchema(
                name='name',
                desc='Name of the item',
                required=True
            ),
            'file': ArgumentSchema(
                name='file',
                desc='File path',
                required=True
            ),
            'optional_message': ArgumentSchema(
                name='message',
                desc='Optional message',
                required=False
            ),
            'multiple_files': ArgumentSchema(
                name='files',
                desc='Multiple file paths',
                required=True,
                multiple=True
            )
        }
    
    def _initialize_common_options(self):
        """Initialize reusable option schemas."""
        self.common_options = {
            'verbose': OptionSchema(
                name='verbose',
                short='v',
                type='flag',
                desc='Enable verbose output'
            ),
            'debug': OptionSchema(
                name='debug',
                type='flag',
                desc='Enable debug mode'
            ),
            'output': OptionSchema(
                name='output',
                short='o',
                type='str',
                desc='Output directory',
                default='./output'
            ),
            'count': OptionSchema(
                name='count',
                short='n',
                type='int',
                desc='Number of items',
                default=1
            ),
            'format': OptionSchema(
                name='format',
                short='f',
                type='str',
                desc='Output format',
                choices=['json', 'yaml', 'text'],
                default='text'
            ),
            'force': OptionSchema(
                name='force',
                type='flag',
                desc='Force overwrite existing files'
            ),
            'timeout': OptionSchema(
                name='timeout',
                short='t',
                type='float',
                desc='Timeout in seconds',
                default=30.0
            )
        }
    
    def _initialize_common_commands(self):
        """Initialize reusable command schemas."""
        self.common_commands = {
            'greet': CommandSchema(
                desc='Greet someone',
                args=[self.common_arguments['name']],
                options=[self.common_options['count']]
            ),
            'build': CommandSchema(
                desc='Build the project',
                options=[
                    self.common_options['output'],
                    self.common_options['verbose'],
                    self.common_options['force']
                ]
            ),
            'test': CommandSchema(
                desc='Run tests',
                args=[self.common_arguments['optional_message']],
                options=[
                    self.common_options['verbose'],
                    self.common_options['timeout']
                ]
            ),
            'info': CommandSchema(
                desc='Display information',
                options=[self.common_options['format']]
            ),
            'deploy': CommandSchema(
                desc='Deploy the application',
                args=[ArgumentSchema(name='environment', desc='Target environment', required=True)],
                options=[
                    self.common_options['force'],
                    OptionSchema(name='dry_run', type='flag', desc='Preview deployment without executing')
                ]
            ),
            # Complex command with subcommands
            'server': CommandSchema(
                desc='Server management',
                subcommands={
                    'start': CommandSchema(
                        desc='Start the server',
                        options=[
                            OptionSchema(name='port', short='p', type='int', desc='Port number', default=8000),
                            OptionSchema(name='daemon', short='d', type='flag', desc='Run as daemon')
                        ]
                    ),
                    'stop': CommandSchema(
                        desc='Stop the server',
                        options=[
                            OptionSchema(name='graceful', short='g', type='flag', desc='Graceful shutdown')
                        ]
                    ),
                    'status': CommandSchema(
                        desc='Check server status'
                    )
                }
            )
        }
    
    def _initialize_configs(self):
        """Initialize test configurations for all languages."""
        languages = ['python', 'nodejs', 'typescript', 'rust']
        
        for language in languages:
            # Minimal configuration
            self.minimal_configs[language] = {
                'package_name': f'minimal-{language}-cli',
                'command_name': f'minimal{language}',
                'display_name': f'Minimal{language.title()}CLI',
                'description': f'A minimal {language} CLI for testing',
                'language': language,
                'python': {'minimum_version': '3.8'},
                'dependencies': {'core': []},
                'installation': {
                    'pypi_name': f'minimal-{language}-cli',
                    'github_repo': f'example/minimal-{language}-cli'
                },
                'shell_integration': {'alias': f'm{language[0]}'},
                'validation': {'minimum_disk_space_mb': 50},
                'messages': {'install_success': f'Minimal{language.title()}CLI installed successfully!'},
                'cli': {
                    'name': f'Minimal{language.title()}CLI',
                    'tagline': f'A minimal {language} CLI',
                    'version': '0.1.0',
                    'commands': {'greet': self.common_commands['greet'].dict()}
                }
            }
            
            # Basic configuration
            self.basic_configs[language] = {
                'package_name': f'basic-{language}-cli',
                'command_name': f'basic{language}',
                'display_name': f'Basic{language.title()}CLI',
                'description': f'A basic {language} CLI for testing',
                'language': language,
                'python': {'minimum_version': '3.8'},
                'dependencies': {'core': []},
                'installation': {
                    'pypi_name': f'basic-{language}-cli',
                    'github_repo': f'example/basic-{language}-cli'
                },
                'shell_integration': {'alias': f'b{language[0]}'},
                'validation': {'minimum_disk_space_mb': 100},
                'messages': {'install_success': f'Basic{language.title()}CLI installed successfully!'},
                'cli': {
                    'name': f'Basic{language.title()}CLI',
                    'tagline': f'A basic {language} CLI for testing',
                    'version': '1.0.0',
                    'options': [self.common_options['verbose'].dict()],
                    'commands': {
                        'greet': self.common_commands['greet'].dict(),
                        'build': self.common_commands['build'].dict(),
                        'info': self.common_commands['info'].dict()
                    }
                }
            }
            
            # Complex configuration
            self.complex_configs[language] = {
                'package_name': f'complex-{language}-cli',
                'command_name': f'complex{language}',
                'display_name': f'Complex{language.title()}CLI',
                'description': f'A complex {language} CLI for comprehensive testing',
                'language': language,
                'python': {'minimum_version': '3.8'},
                'dependencies': {'core': []},
                'installation': {
                    'pypi_name': f'complex-{language}-cli',
                    'github_repo': f'example/complex-{language}-cli'
                },
                'shell_integration': {'alias': f'c{language[0]}'},
                'validation': {'minimum_disk_space_mb': 200},
                'messages': {'install_success': f'Complex{language.title()}CLI installed successfully!'},
                'cli': {
                    'name': f'Complex{language.title()}CLI',
                    'tagline': f'A comprehensive {language} CLI for testing',
                    'version': '2.0.0',
                    'options': [
                        self.common_options['verbose'].dict(),
                        self.common_options['debug'].dict()
                    ],
                    'commands': {
                        'greet': self.common_commands['greet'].dict(),
                        'build': self.common_commands['build'].dict(),
                        'test': self.common_commands['test'].dict(),
                        'info': self.common_commands['info'].dict(),
                        'deploy': self.common_commands['deploy'].dict(),
                        'server': self.common_commands['server'].dict()
                    }
                }
            }
    
    def _initialize_expected_outputs(self):
        """Initialize expected CLI outputs for comparison testing."""
        self.expected_outputs = {
            'help_patterns': {
                'python': ['Usage:', 'Options:', 'Commands:'],
                'nodejs': ['Usage:', 'Options:', 'Commands:'],
                'typescript': ['Usage:', 'Options:', 'Commands:'],
                'rust': ['Usage:', 'OPTIONS:', 'SUBCOMMANDS:']
            },
            'version_patterns': {
                'python': [r'\d+\.\d+\.\d+'],
                'nodejs': [r'\d+\.\d+\.\d+'],
                'typescript': [r'\d+\.\d+\.\d+'],
                'rust': [r'\d+\.\d+\.\d+']
            },
            'error_patterns': {
                'missing_arg': {
                    'python': ['Missing argument', 'Usage:', 'Error'],
                    'nodejs': ['error', 'required', 'missing'],
                    'typescript': ['error', 'required', 'missing'],
                    'rust': ['error:', 'required', 'argument']
                },
                'invalid_command': {
                    'python': ['No such command', 'Usage:', 'Error'],
                    'nodejs': ['unknown command', 'error'],
                    'typescript': ['unknown command', 'error'],
                    'rust': ['unrecognized subcommand']
                }
            }
        }
    
    def _initialize_error_scenarios(self):
        """Initialize error scenarios for testing."""
        self.error_scenarios = {
            'missing_required_arg': {
                'command': ['greet'],  # Missing required 'name' argument
                'expected_exit_code': 1,
                'expected_patterns': self.expected_outputs['error_patterns']['missing_arg']
            },
            'invalid_command': {
                'command': ['nonexistent'],
                'expected_exit_code': 1,
                'expected_patterns': self.expected_outputs['error_patterns']['invalid_command']
            },
            'invalid_option_value': {
                'command': ['info', '--format', 'invalid'],
                'expected_exit_code': 1,
                'expected_patterns': ['invalid choice', 'error']
            }
        }
    
    def get_config(self, complexity: str, language: str) -> Dict[str, Any]:
        """Get a test configuration by complexity and language.
        
        Args:
            complexity: 'minimal', 'basic', or 'complex'
            language: 'python', 'nodejs', 'typescript', or 'rust'
            
        Returns:
            Configuration dictionary
        """
        config_map = {
            'minimal': self.minimal_configs,
            'basic': self.basic_configs,
            'complex': self.complex_configs
        }
        
        if complexity not in config_map:
            raise ValueError(f"Unknown complexity: {complexity}")
        if language not in config_map[complexity]:
            raise ValueError(f"Unknown language: {language}")
            
        return config_map[complexity][language]
    
    def get_command(self, command_name: str) -> CommandSchema:
        """Get a common command schema by name."""
        if command_name not in self.common_commands:
            raise ValueError(f"Unknown command: {command_name}")
        return self.common_commands[command_name]
    
    def get_option(self, option_name: str) -> OptionSchema:
        """Get a common option schema by name."""
        if option_name not in self.common_options:
            raise ValueError(f"Unknown option: {option_name}")
        return self.common_options[option_name]
    
    def get_argument(self, arg_name: str) -> ArgumentSchema:
        """Get a common argument schema by name."""
        if arg_name not in self.common_arguments:
            raise ValueError(f"Unknown argument: {arg_name}")
        return self.common_arguments[arg_name]


# Global fixture instance
fixtures = TestFixtures()


def create_test_config(
    package_name: str,
    language: str = 'python',
    complexity: str = 'basic',
    custom_commands: Optional[Dict[str, CommandSchema]] = None
) -> GoobitsConfigSchema:
    """Create a test GoobitsConfigSchema with common defaults.
    
    Args:
        package_name: Package name for the CLI
        language: Target language ('python', 'nodejs', 'typescript', 'rust')
        complexity: Configuration complexity ('minimal', 'basic', 'complex')
        custom_commands: Optional custom commands to include
        
    Returns:
        GoobitsConfigSchema instance
    """
    config_data = fixtures.get_config(complexity, language).copy()
    config_data['package_name'] = package_name
    config_data['command_name'] = package_name.replace('-', '')
    config_data['display_name'] = package_name.replace('-', ' ').title()
    
    if custom_commands:
        config_data['cli']['commands'].update({
            name: cmd.dict() for name, cmd in custom_commands.items()
        })
    
    # Convert to proper schema objects
    cli_data = config_data.pop('cli')
    cli_schema = CLISchema(**cli_data)
    
    return GoobitsConfigSchema(
        cli=cli_schema,
        python=PythonConfigSchema(**config_data.get('python', {})),
        dependencies=DependenciesSchema(**config_data.get('dependencies', {})),
        installation=InstallationSchema(**config_data.get('installation', {})),
        shell_integration=ShellIntegrationSchema(**config_data.get('shell_integration', {})),
        validation=ValidationSchema(**config_data.get('validation', {})),
        messages=MessagesSchema(**config_data.get('messages', {})),
        **{k: v for k, v in config_data.items() if k not in [
            'cli', 'python', 'dependencies', 'installation', 
            'shell_integration', 'validation', 'messages'
        ]}
    )


def create_minimal_cli_config(language: str = 'python') -> GoobitsConfigSchema:
    """Create a minimal CLI configuration for testing."""
    return create_test_config(f'test-{language}-cli', language, 'minimal')


def create_complex_cli_config(language: str = 'python') -> GoobitsConfigSchema:
    """Create a complex CLI configuration for testing."""
    return create_test_config(f'complex-{language}-cli', language, 'complex')


def get_test_command_data() -> Dict[str, CommandSchema]:
    """Get a dictionary of common test commands."""
    return fixtures.common_commands.copy()


def get_test_option_data() -> Dict[str, OptionSchema]:
    """Get a dictionary of common test options."""
    return fixtures.common_options.copy()


def get_test_argument_data() -> Dict[str, ArgumentSchema]:
    """Get a dictionary of common test arguments."""
    return fixtures.common_arguments.copy()


def get_error_scenario(scenario_name: str) -> Dict[str, Any]:
    """Get an error scenario for testing error conditions."""
    if scenario_name not in fixtures.error_scenarios:
        raise ValueError(f"Unknown error scenario: {scenario_name}")
    return fixtures.error_scenarios[scenario_name].copy()


def get_expected_patterns(category: str, language: str) -> List[str]:
    """Get expected output patterns for a category and language."""
    if category not in fixtures.expected_outputs:
        raise ValueError(f"Unknown pattern category: {category}")
    if language not in fixtures.expected_outputs[category]:
        raise ValueError(f"Unknown language for {category}: {language}")
    return fixtures.expected_outputs[category][language].copy()