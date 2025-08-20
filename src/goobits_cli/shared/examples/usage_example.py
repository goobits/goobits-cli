#!/usr/bin/env python3

"""Example usage of the shared documentation templates.



This script demonstrates how to use the documentation generator

to create consistent documentation across different languages.

"""



import os

import sys

from pathlib import Path



# Add the parent directory to Python path for imports

sys.path.insert(0, str(Path(__file__).parent.parent.parent))



from shared.components.doc_generator import DocumentationGenerator



def create_sample_config():

    """Create a sample configuration for demonstration."""

    return {

        'display_name': 'MyAwesome CLI',

        'package_name': 'myawesome-cli',

        'command_name': 'myawesome',

        'version': '1.0.0',

        'description': 'An awesome CLI tool for doing awesome things',

        'author': 'John Doe <john@example.com>',

        'license': 'MIT',

        'repository': 'https://github.com/johndoe/myawesome-cli',

        'cli': {

            'tagline': 'Make your workflow awesome',

            'description': 'A comprehensive CLI tool for developers',

            'commands': {

                'build': {

                    'desc': 'Build your project',

                    'icon': '🔨',

                    'args': [

                        {

                            'name': 'source',

                            'desc': 'Source directory to build from',

                            'required': True

                        },

                        {

                            'name': 'output',

                            'desc': 'Output directory for build artifacts',

                            'required': False,

                            'default': './dist'

                        }

                    ],

                    'options': [

                        {

                            'name': 'verbose',

                            'short': 'v',

                            'desc': 'Enable verbose output',

                            'type': 'flag'

                        },

                        {

                            'name': 'format',

                            'short': 'f',

                            'desc': 'Output format',

                            'type': 'choice',

                            'choices': ['json', 'yaml', 'toml'],

                            'default': 'json'

                        }

                    ]

                },

                'deploy': {

                    'desc': 'Deploy your application',

                    'icon': '🚀',

                    'args': [

                        {

                            'name': 'environment',

                            'desc': 'Target environment',

                            'required': True,

                            'choices': ['dev', 'staging', 'prod']

                        }

                    ],

                    'options': [

                        {

                            'name': 'dry-run',

                            'desc': 'Show what would be deployed without actually deploying',

                            'type': 'flag'

                        }

                    ]

                },

                'config': {

                    'desc': 'Manage configuration settings',

                    'icon': '⚙️',

                    'subcommands': {

                        'get': {

                            'desc': 'Get a configuration value'

                        },

                        'set': {

                            'desc': 'Set a configuration value'

                        },

                        'list': {

                            'desc': 'List all configuration values'

                        }

                    }

                }

            },

            'options': [

                {

                    'name': 'config',

                    'short': 'c',

                    'desc': 'Path to configuration file',

                    'type': 'file'

                },

                {

                    'name': 'debug',

                    'desc': 'Enable debug mode',

                    'type': 'flag'

                }

            ]

        },

        'installation': {

            'pypi_name': 'myawesome-cli',

            'npm_name': '@johndoe/myawesome-cli',

            'extras': {

                'python': ['dev', 'test'],

                'apt': ['git', 'build-essential'],

                'npm': ['prettier', 'eslint']

            }

        },

        'python': {

            'minimum_version': '3.8',

            'maximum_version': '3.12'

        },

        'node': {

            'minimum_version': '16.0.0'

        },

        'rust': {

            'minimum_version': '1.70.0'

        }

    }



def demonstrate_language_generation(config: dict, language: str):

    """Demonstrate documentation generation for a specific language."""

    print(f"\n{'='*60}")

    print(f"GENERATING DOCUMENTATION FOR {language.upper()}")

    print(f"{'='*60}")

    

    # Create documentation generator

    generator = DocumentationGenerator(language, config)

    

    # Generate README

    print(f"\n--- README.md for {language} ---")

    readme = generator.generate_readme()

    print(readme[:500] + "..." if len(readme) > 500 else readme)

    

    # Generate installation guide  

    print(f"\n--- Installation Guide for {language} ---")

    install_guide = generator.generate_installation_guide()

    print(install_guide[:500] + "..." if len(install_guide) > 500 else install_guide)

    

    # Generate help text for a command

    print(f"\n--- Help Text for 'build' command in {language} ---")

    help_text = generator.generate_help_text('build', config['cli']['commands']['build'])

    print(help_text)

    

    # Show language-specific features

    print(f"\n--- Language-specific features for {language} ---")

    print(f"Package manager: {generator.get_language_config('package_manager')}")

    print(f"Test command: {generator.get_language_config('test_command')}")

    print(f"Supports virtual env: {generator.supports_feature('virtual_env')}")

    print(f"Dependencies: {generator.get_language_config('dependencies')}")

    

    # Show error message generation

    print(f"\n--- Error Messages for {language} ---")

    error_msg = generator.generate_error_message(

        'missing_dependency',

        dependency='requests',

        package='myawesome-cli'

    )

    print(f"Missing dependency error: {error_msg}")



def main():

    """Main demonstration function."""

    print("Shared Documentation Templates - Usage Example")

    print("=" * 50)

    

    # Create sample configuration

    config = create_sample_config()

    

    # Demonstrate generation for each supported language

    languages = ['python', 'nodejs', 'typescript', 'rust']

    

    for language in languages:

        try:

            demonstrate_language_generation(config, language)

        except Exception as e:

            print(f"Error generating documentation for {language}: {e}")

    

    print(f"\n{'='*60}")

    print("DEMONSTRATION COMPLETE")

    print(f"{'='*60}")

    

    # Show file generation example

    print("\nTo save generated files:")

    print("generator = DocumentationGenerator('python', config)")

    print("with open('README.md', 'w') as f:")

    print("    f.write(generator.generate_readme())")

    print("with open('INSTALL.md', 'w') as f:")

    print("    f.write(generator.generate_installation_guide())")



if __name__ == '__main__':

    main()