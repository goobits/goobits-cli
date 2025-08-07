"""
Interactive mode support for Goobits CLI Framework.

This module provides the foundation for interactive (REPL) modes
in generated CLI applications across all supported languages.
"""

from .base import (
    InteractiveCommand,
    InteractiveEngine,
    InteractiveRenderer
)

__all__ = [
    'InteractiveCommand',
    'InteractiveEngine',
    'InteractiveRenderer',
    'integrate_interactive_mode',
    'is_interactive_supported'
]


def integrate_interactive_mode(cli_config: dict, language: str) -> dict:
    """
    Integrate interactive mode support into CLI configuration.
    
    This function adds the necessary flags and configuration to enable
    interactive mode in the generated CLI.
    
    Args:
        cli_config: The CLI configuration dictionary.
        language: The target programming language.
        
    Returns:
        Modified CLI configuration with interactive mode support.
    """
    # Ensure root command has options list
    if 'root_command' not in cli_config:
        cli_config['root_command'] = {}
    
    if 'options' not in cli_config['root_command']:
        cli_config['root_command']['options'] = []
    
    # Check if interactive flag already exists
    has_interactive = any(
        opt.get('name') == 'interactive'
        for opt in cli_config['root_command']['options']
    )
    
    if not has_interactive:
        # Add the interactive flag
        cli_config['root_command']['options'].append({
            'name': 'interactive',
            'short': 'i',
            'description': 'Launch interactive mode',
            'type': 'boolean',
            'default': False
        })
    
    # Add interactive mode metadata
    if 'features' not in cli_config:
        cli_config['features'] = {}
    
    cli_config['features']['interactive_mode'] = {
        'enabled': True,
        'prompt': f"{cli_config['root_command'].get('name', 'cli')}> ",
        'history_enabled': True,
        'tab_completion': is_tab_completion_supported(language)
    }
    
    return cli_config


def is_interactive_supported(language: str) -> bool:
    """
    Check if interactive mode is supported for the given language.
    
    Args:
        language: The target programming language.
        
    Returns:
        True if interactive mode is supported, False otherwise.
    """
    supported_languages = ['python', 'nodejs', 'typescript', 'rust']
    return language.lower() in supported_languages


def is_tab_completion_supported(language: str) -> bool:
    """
    Check if tab completion is supported for the given language.
    
    Args:
        language: The target programming language.
        
    Returns:
        True if tab completion is supported, False otherwise.
    """
    # All our implementations support basic tab completion
    return is_interactive_supported(language)


def get_interactive_file_name(language: str, project_name: str) -> str:
    """
    Get the appropriate file name for the interactive mode module.
    
    Args:
        language: The target programming language.
        project_name: The name of the project.
        
    Returns:
        The file name for the interactive mode module.
    """
    base_name = f"{project_name.replace('-', '_')}_interactive"
    
    file_extensions = {
        'python': '.py',
        'nodejs': '.js',
        'typescript': '.ts',
        'rust': '.rs'
    }
    
    return base_name + file_extensions.get(language, '')


def get_interactive_import_statement(language: str, cli_module: str) -> str:
    """
    Get the import statement for the interactive mode in the main CLI.
    
    Args:
        language: The target programming language.
        cli_module: The name of the CLI module.
        
    Returns:
        The import statement as a string.
    """
    statements = {
        'python': f"from .{cli_module}_interactive import run_interactive",
        'nodejs': f"const {{ runInteractive }} = require('./{cli_module}_interactive');",
        'typescript': f"import {{ runInteractive }} from './{cli_module}_interactive';",
        'rust': f"mod {cli_module}_interactive;\nuse {cli_module}_interactive::run_interactive;"
    }
    
    return statements.get(language, '')


def get_interactive_launch_code(language: str, option_name: str = 'interactive') -> dict:
    """
    Get the code snippet to launch interactive mode based on the flag.
    
    Args:
        language: The target programming language.
        option_name: The name of the interactive option flag.
        
    Returns:
        Dictionary with 'check' and 'launch' code snippets.
    """
    code_snippets = {
        'python': {
            'check': f"if {option_name}:",
            'launch': "    run_interactive()\n    sys.exit(0)"
        },
        'nodejs': {
            'check': f"if (program.opts().{option_name}) {{",
            'launch': "    runInteractive();\n    process.exit(0);\n}"
        },
        'typescript': {
            'check': f"if (program.opts().{option_name}) {{",
            'launch': "    runInteractive();\n    process.exit(0);\n}"
        },
        'rust': {
            'check': f'if matches.get_flag("{option_name}") {{',
            'launch': "    run_interactive().unwrap_or_else(|e| {\n        eprintln!(\"Error: {}\", e);\n        process::exit(1);\n    });\n    return;\n}"
        }
    }
    
    return code_snippets.get(language, {'check': '', 'launch': ''})