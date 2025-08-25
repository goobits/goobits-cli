"""

Universal completion system for Goobits CLI Framework.



This module provides dynamic, context-aware completion capabilities

that work across all supported languages (Python, Node.js, TypeScript, Rust).

"""



from .registry import DynamicCompletionRegistry, CompletionProvider, CompletionContext

from .providers import (

    FilePathCompletionProvider,

    EnvironmentVariableProvider, 

    ConfigKeyProvider,

    HistoryProvider

)

from .smart_completion import (
    SmartCompletionEngine,
    HistoryCompletionProvider,
    FuzzyMatchProvider,
    get_smart_completion_registry
)



__all__ = [

    'DynamicCompletionRegistry',

    'CompletionProvider', 

    'CompletionContext',

    'FilePathCompletionProvider',

    'EnvironmentVariableProvider',

    'ConfigKeyProvider',

    'HistoryProvider',

    'SmartCompletionEngine',

    'HistoryCompletionProvider',

    'FuzzyMatchProvider',

    'get_smart_completion_registry',

    'integrate_completion_system'

]


def integrate_completion_system(cli_config: dict, language: str) -> dict:
    """
    Integrate shell completion system into CLI configuration.
    
    This function adds the necessary metadata and configuration to enable
    shell completion scripts generation in the generated CLI.
    
    Args:
        cli_config: The CLI configuration dictionary.
        language: The target programming language.
        
    Returns:
        Modified CLI configuration with completion system support.
    """
    # Add completion system metadata
    if 'features' not in cli_config:
        cli_config['features'] = {}
    
    # Get CLI name from appropriate configuration structure
    cli_name = 'cli'
    if 'cli' in cli_config and 'name' in cli_config['cli']:
        cli_name = cli_config['cli']['name']
    elif 'root_command' in cli_config and 'name' in cli_config['root_command']:
        cli_name = cli_config['root_command']['name']
    
    cli_config['features']['completion_system'] = {
        'enabled': True,
        'shells': ['bash', 'zsh', 'fish'],
        'dynamic_completion': is_dynamic_completion_supported(language),
        'cli_name': cli_name
    }
    
    return cli_config


def is_completion_supported(language: str) -> bool:
    """
    Check if completion system is supported for the given language.
    
    Args:
        language: The target programming language.
        
    Returns:
        True if completion is supported, False otherwise.
    """
    supported_languages = ['python', 'nodejs', 'typescript', 'rust']
    return language.lower() in supported_languages


def is_dynamic_completion_supported(language: str) -> bool:
    """
    Check if dynamic completion is supported for the given language.
    
    Args:
        language: The target programming language.
        
    Returns:
        True if dynamic completion is supported, False otherwise.
    """
    # All our implementations support dynamic completion
    return is_completion_supported(language)


def get_completion_files_for_language(language: str, cli_name: str) -> list:
    """
    Get the list of completion files to generate for a specific language.
    
    Args:
        language: The target programming language.
        cli_name: The name of the CLI.
        
    Returns:
        List of completion file definitions.
    """
    # All supported languages now have completion templates available
    supported_languages = ['nodejs', 'typescript', 'rust']
    
    if language.lower() in supported_languages:
        base_files = [
            {
                'template': f'{language}/completions/bash-completion.j2',
                'output': f'completions/{cli_name}-completion.bash',
                'shell': 'bash'
            },
            {
                'template': f'{language}/completions/zsh-completion.j2', 
                'output': f'completions/_{cli_name}',
                'shell': 'zsh'
            },
            {
                'template': f'{language}/completions/fish-completion.j2',
                'output': f'completions/{cli_name}.fish',
                'shell': 'fish'
            }
        ]
        return base_files
    else:
        # Return empty list for languages without completion templates yet
        return []