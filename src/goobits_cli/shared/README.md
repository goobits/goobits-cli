# Shared Documentation Templates

This directory contains shared documentation patterns and templates extracted from all language generators (Python, Node.js, TypeScript, and Rust).

## Overview

The shared documentation system provides:

1. **Universal Templates** - Common documentation patterns that work across all languages
2. **Language Customizations** - Language-specific overrides and configurations  
3. **Documentation Generator** - Python utility for generating consistent documentation
4. **Template Macros** - Reusable components for help text, error messages, etc.

## Directory Structure

```
shared/
├── components/
│   └── doc_generator.py          # Documentation generation utility
├── templates/
│   ├── readme_template.md.j2     # Universal README template
│   ├── help_text_template.j2     # Help text formatting macros
│   ├── installation_template.md.j2 # Installation guide template
│   └── language_customizations.yaml # Language-specific overrides
└── README.md                     # This file
```

## Usage

### Using the Documentation Generator

```python
from goobits_cli.shared.components.doc_generator import DocumentationGenerator

# Create generator for specific language
generator = DocumentationGenerator(
    language='python',  # or 'nodejs', 'typescript', 'rust'
    config=config_data  # Your goobits.yaml configuration
)

# Generate documentation
readme_content = generator.generate_readme()
install_guide = generator.generate_installation_guide()
help_text = generator.generate_help_text('build', command_data)
```

### Using Templates Directly

```python
from jinja2 import Environment, FileSystemLoader

# Set up Jinja2 environment
env = Environment(loader=FileSystemLoader('shared/templates'))

# Render README template
template = env.get_template('readme_template.md.j2')
content = template.render(
    language='python',
    display_name='My CLI',
    package_name='my-cli',
    # ... other template variables
)
```

### Language-Specific Features

```python
generator = DocumentationGenerator('rust', config)

# Check if language supports a feature
if generator.supports_feature('virtual_env'):
    # Include virtual environment instructions

# Get language-specific configuration
package_manager = generator.get_language_config('package_manager')
# Returns 'cargo' for Rust, 'npm' for Node.js/TypeScript, 'pipx' for Python

# Get documentation sections to include
sections = generator.get_documentation_sections()
# Returns {'include': [...], 'exclude': [...]}
```

## Templates

### README Template (`readme_template.md.j2`)

Generates consistent README.md files with:

- **Installation Instructions** - Package manager specific commands
- **Usage Examples** - Command documentation with arguments and options  
- **Configuration** - Language-specific config file locations
- **Development** - Build, test, and run instructions
- **Architecture** - Dependencies and project structure
- **Shell Completions** - Installation instructions for command completion

**Key Features:**
- Adapts to target language automatically
- Includes language-specific dependencies and tools
- Generates command usage examples from CLI configuration
- Platform-specific installation instructions

### Help Text Template (`help_text_template.j2`)

Provides macros for consistent help text formatting:

```jinja2
{%- from 'help_text_template.j2' import command_description, format_arguments, format_options -%}

{{ command_description(cmd_data) }}
{{ format_arguments(cmd_data.args) }}  
{{ format_options(cmd_data.options) }}
```

**Available Macros:**
- `command_description()` - Format command description with optional icon
- `command_usage()` - Generate usage line with arguments and options
- `format_arguments()` - Format argument list with types and descriptions
- `format_options()` - Format option list with short flags and defaults
- `format_examples()` - Format command examples consistently
- `error_*()` - Error message templates
- `language_specific_help()` - Apply language-specific formatting

### Installation Template (`installation_template.md.j2`)

Generates comprehensive installation guides with:

- **Quick Installation** - One-command installation for each package manager
- **Source Installation** - Step-by-step build from source instructions
- **Development Setup** - Development environment configuration
- **Platform Instructions** - Linux, macOS, Windows specific steps
- **Troubleshooting** - Common issues and solutions
- **Shell Completions** - Completion setup for all supported shells

### Language Customizations (`language_customizations.yaml`)

Defines language-specific configurations:

```yaml
languages:
  python:
    package_manager: "pipx"
    package_command: "pipx install"
    test_command: "pytest"
    dependencies: ["click", "rich", "pydantic"]
    minimum_version: "3.8"
    
  nodejs:
    package_manager: "npm"  
    package_command: "npm install -g"
    test_command: "npm test"
    dependencies: ["commander", "chalk", "inquirer"]
    minimum_version: "14.0.0"
```

**Configuration Sections:**
- `languages` - Per-language tool configuration
- `platforms` - Platform-specific installation methods
- `error_templates` - Language-specific error message patterns
- `help_formatting` - Help text formatting preferences
- `completion_support` - Shell completion capabilities
- `documentation_sections` - Sections to include/exclude per language

## Integration with Language Generators

### In Python Generator

```python
from goobits_cli.shared.components.doc_generator import DocumentationGenerator

class PythonGenerator:
    def generate_readme(self):
        doc_gen = DocumentationGenerator('python', self.config)
        return doc_gen.generate_readme()
        
    def generate_help_text(self, cmd_name, cmd_data):
        doc_gen = DocumentationGenerator('python', self.config)
        return doc_gen.generate_help_text(cmd_name, cmd_data)
```

### In Node.js/TypeScript Generators

```python
class NodeJSGenerator:
    def generate_readme(self):
        doc_gen = DocumentationGenerator('nodejs', self.config)
        content = doc_gen.generate_readme()
        
        # Add Node.js specific sections
        if doc_gen.supports_feature('npm_scripts'):
            custom_section = doc_gen.generate_custom_section(
                'npm_scripts',
                "## NPM Scripts\n\n{{ npm_scripts_template }}"
            )
            content += custom_section
            
        return content
```

### In Rust Generator

```python
class RustGenerator:
    def generate_cargo_help(self, cmd_name, cmd_data):
        doc_gen = DocumentationGenerator('rust', self.config)
        
        # Use Rust-specific error formatting
        if some_error:
            error_msg = doc_gen.generate_error_message(
                'missing_dependency', 
                dependency='serde'
            )
```

## Customization

### Adding New Language Support

1. **Update `language_customizations.yaml`:**
```yaml
languages:
  go:
    package_manager: "go"
    package_command: "go install"
    test_command: "go test"
    dependencies: ["cobra", "viper"]
    minimum_version: "1.19"
```

2. **Update templates with conditional blocks:**
```jinja2
{% elif language == 'go' %}
```bash
go install {{ package_name }}@latest
```
{% endif %}
```

3. **Add platform-specific instructions:**
```yaml
platforms:
  linux:
    go:
      install_method: "apt install golang"
```

### Adding New Template Macros

Add to `help_text_template.j2`:

```jinja2
{% macro format_config_options(config_options) -%}
{% if config_options %}
Configuration Options:
{% for opt in config_options %}
- `{{ opt.key }}`: {{ opt.description }}{% if opt.default %} (default: {{ opt.default }}){% endif %}
{% endfor %}
{% endif %}
{%- endmacro %}
```

### Extending the Documentation Generator

```python
class CustomDocumentationGenerator(DocumentationGenerator):
    def generate_api_docs(self):
        """Generate API documentation for library CLIs."""
        template = self.jinja_env.get_template('api_docs_template.md.j2')
        context = self._get_template_context()
        return template.render(**context)
```

## Benefits

1. **Consistency** - All language generators produce similar documentation
2. **Maintenance** - Update documentation patterns in one place
3. **Language Features** - Automatically adapt to language-specific tools and conventions
4. **Extensibility** - Easy to add new languages or documentation sections
5. **Reusability** - Templates and macros can be used across different contexts

## Future Enhancements

- **Theme Support** - Multiple documentation themes/styles
- **Internationalization** - Multi-language documentation support
- **Interactive Docs** - Generate interactive documentation websites
- **Auto-Updates** - Keep documentation in sync with CLI changes
- **Integration Tests** - Validate generated documentation accuracy