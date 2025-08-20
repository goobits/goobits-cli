"""Example of how language generators can integrate with shared documentation templates.



This demonstrates how to modify existing language generators to use the shared

documentation system instead of maintaining separate templates.

"""



from typing import Dict, Any




# Import the shared documentation generator

from goobits_cli.shared.components.doc_generator import DocumentationGenerator





class EnhancedPythonGenerator:

    """Example of how PythonGenerator can be enhanced with shared documentation."""

    

    def __init__(self, config: Dict[str, Any]):

        self.config = config

        self.doc_generator = DocumentationGenerator('python', config)

    

    def generate_readme(self) -> str:

        """Generate README using shared template instead of Python-specific one."""

        # Use the shared README template that adapts to Python

        return self.doc_generator.generate_readme()

    

    def generate_installation_guide(self) -> str:

        """Generate installation guide with Python-specific instructions."""

        return self.doc_generator.generate_installation_guide()

    

    def generate_cli_help(self, command_name: str, command_data: Dict[str, Any]) -> str:

        """Generate help text for Click commands using shared patterns."""

        help_text = self.doc_generator.generate_help_text(command_name, command_data)

        

        # Apply Python/Click specific formatting

        if self.doc_generator.get_language_config('click_style'):

            # Convert to Click-compatible docstring format

            return f'"""\n{help_text}\n"""'

        

        return help_text

    

    def generate_error_handler(self) -> str:

        """Generate Python-specific error handling with consistent messages."""

        error_templates = []

        

        # Generate error handlers for common cases

        for error_type in ['missing_dependency', 'permission_error']:

            template = self.doc_generator.generate_error_message(error_type, 

                dependency='{dependency}', package='{package}')

            error_templates.append(f"# {error_type}: {template}")

        

        return '\n'.join(error_templates)





class EnhancedNodeJSGenerator:

    """Example of how NodeJSGenerator can use shared documentation."""

    

    def __init__(self, config: Dict[str, Any]):

        self.config = config

        self.doc_generator = DocumentationGenerator('nodejs', config)

    

    def generate_package_json_fields(self) -> Dict[str, Any]:

        """Generate package.json fields using language-specific config."""

        return {

            'scripts': {

                'test': self.doc_generator.get_language_config('test_command'),

                'build': self.doc_generator.get_language_config('build_command'),

                'start': "node cli.js"

            },

            'engines': {

                'node': f">={self.doc_generator.get_language_config('minimum_version')}"

            },

            'dependencies': {

                dep: 'latest' for dep in self.doc_generator.get_language_config('dependencies')

            }

        }

    

    def generate_commander_help(self, command_name: str, command_data: Dict[str, Any]) -> str:

        """Generate Commander.js compatible help text."""

        base_help = self.doc_generator.generate_help_text(command_name, command_data)

        

        # Commander.js uses different format

        return base_help.replace('\n', '\\n').replace('"', '\\"')

    

    def supports_npm_scripts(self) -> bool:

        """Check if this generator should include npm scripts documentation."""

        sections = self.doc_generator.get_documentation_sections()

        return 'npm_scripts' in sections.get('include', [])





class EnhancedRustGenerator:

    """Example of how RustGenerator can leverage shared templates."""

    

    def __init__(self, config: Dict[str, Any]):

        self.config = config

        self.doc_generator = DocumentationGenerator('rust', config)

    

    def generate_cargo_toml_help(self) -> str:

        """Generate help text for Cargo.toml documentation."""

        if self.doc_generator.supports_feature('cargo_features'):

            return self.doc_generator.generate_custom_section(

                'cargo_features',

                """

## Cargo Features



This crate supports the following optional features:



{% for feature, desc in cargo_features.items() %}

- `{{ feature }}`: {{ desc }}

{% endfor %}



Enable features with: `cargo install {{ package_name }} --features feature1,feature2`

                """,

                cargo_features={

                    'async': 'Enable async/await support',

                    'tls': 'Enable TLS support for network operations',

                    'json': 'Enable JSON configuration format'

                }

            )

        return ""

    

    def generate_clap_derive_help(self, command_name: str, command_data: Dict[str, Any]) -> str:

        """Generate help text for Clap derive macros."""

        help_text = self.doc_generator.generate_help_text(command_name, command_data)

        

        # Format for Rust doc comments

        lines = help_text.split('\n')

        formatted_lines = [f'/// {line}' if line.strip() else '///' for line in lines]

        return '\n'.join(formatted_lines)





class SharedDocumentationDemo:

    """Demonstrates the benefits of using shared documentation templates."""

    

    def __init__(self):

        self.sample_config = {

            'display_name': 'Multi-Language CLI',

            'package_name': 'multi-cli',

            'command_name': 'multi',

            'version': '1.0.0',

            'description': 'A CLI that works across multiple languages',

            'cli': {

                'commands': {

                    'build': {

                        'desc': 'Build the project',

                        'args': [

                            {'name': 'target', 'desc': 'Build target', 'required': True}

                        ],

                        'options': [

                            {'name': 'release', 'desc': 'Build in release mode', 'type': 'flag'}

                        ]

                    }

                }

            }

        }

    

    def demonstrate_consistency(self):

        """Show how the same configuration generates consistent docs across languages."""

        languages = ['python', 'nodejs', 'typescript', 'rust']

        generators = []

        

        print("=== CONSISTENCY DEMONSTRATION ===\n")

        

        for language in languages:

            if language == 'python':

                generator = EnhancedPythonGenerator(self.sample_config)

            elif language == 'nodejs':

                generator = EnhancedNodeJSGenerator(self.sample_config)

            elif language == 'rust':

                generator = EnhancedRustGenerator(self.sample_config)

            else:

                # Fallback to base generator

                generator = DocumentationGenerator(language, self.sample_config)

            

            generators.append((language, generator))

            

            # Show README excerpt for each language

            if hasattr(generator, 'generate_readme'):

                readme = generator.generate_readme()

                installation_section = self.extract_section(readme, "## Installation")

                print(f"--- {language.upper()} Installation Section ---")

                print(installation_section[:200] + "...")

                print()

    

    def extract_section(self, text: str, section_header: str) -> str:

        """Extract a specific section from markdown text."""

        lines = text.split('\n')

        in_section = False

        section_lines = []

        

        for line in lines:

            if line.startswith(section_header):

                in_section = True

                section_lines.append(line)

            elif in_section and line.startswith('## '):

                break

            elif in_section:

                section_lines.append(line)

        

        return '\n'.join(section_lines)

    

    def demonstrate_customization(self):

        """Show how language-specific customizations work."""

        print("=== CUSTOMIZATION DEMONSTRATION ===\n")

        

        for language in ['python', 'nodejs', 'rust']:

            doc_gen = DocumentationGenerator(language, self.sample_config)

            

            print(f"--- {language.upper()} Customizations ---")

            print(f"Package Manager: {doc_gen.get_language_config('package_manager')}")

            print(f"Test Command: {doc_gen.get_language_config('test_command')}")

            print(f"Dependencies: {doc_gen.get_language_config('dependencies')}")

            print(f"Virtual Env Support: {doc_gen.supports_feature('virtual_env')}")

            print()





def main():

    """Run the integration demonstration."""

    demo = SharedDocumentationDemo()

    demo.demonstrate_consistency()

    demo.demonstrate_customization()

    

    print("=== INTEGRATION BENEFITS ===")

    print("✅ Consistent documentation across all languages")

    print("✅ Single source of truth for common patterns") 

    print("✅ Language-specific adaptations automatically applied")

    print("✅ Easy maintenance - update patterns in one place")

    print("✅ Extensible - add new languages by updating config")

    print("✅ Reusable - templates work for any CLI configuration")





if __name__ == '__main__':

    main()