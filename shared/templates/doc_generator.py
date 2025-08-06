"""
Documentation generator for Goobits CLI configurations.

This module provides documentation generation capabilities for all supported
languages (Python, Node.js, TypeScript, Rust), creating README files, help text,
and usage examples from CLI configurations.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Union
from pathlib import Path
import textwrap
import re


class DocumentationType(Enum):
    """Types of documentation that can be generated."""
    README = "readme"
    HELP_TEXT = "help_text"
    USAGE_EXAMPLES = "usage_examples"
    API_REFERENCE = "api_reference"
    QUICK_START = "quick_start"
    COMMAND_REFERENCE = "command_reference"


class OutputFormat(Enum):
    """Output formats for documentation."""
    MARKDOWN = "markdown"
    PLAINTEXT = "plaintext"
    RST = "rst"
    HTML = "html"


@dataclass
class DocumentationSection:
    """A section of documentation with content and metadata."""
    title: str
    content: str
    order: int = 0
    subsections: List['DocumentationSection'] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_markdown(self, level: int = 1) -> str:
        """Convert section to Markdown format."""
        header = "#" * level
        lines = [f"{header} {self.title}", "", self.content]
        
        for subsection in self.subsections:
            lines.extend(["", subsection.to_markdown(level + 1)])
        
        return "\n".join(lines)
    
    def to_plaintext(self, indent: int = 0) -> str:
        """Convert section to plain text format."""
        indent_str = " " * indent
        lines = [
            f"{indent_str}{self.title}",
            f"{indent_str}{'-' * len(self.title)}",
            "",
            textwrap.indent(self.content, indent_str)
        ]
        
        for subsection in self.subsections:
            lines.extend(["", subsection.to_plaintext(indent + 2)])
        
        return "\n".join(lines)


@dataclass
class DocumentationContext:
    """Context passed to documentation generators."""
    config: Any  # The CLI configuration
    language: str = "python"
    output_format: OutputFormat = OutputFormat.MARKDOWN
    doc_type: DocumentationType = DocumentationType.README
    include_examples: bool = True
    include_api_reference: bool = True
    project_name: Optional[str] = None
    project_version: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def get_cli_name(self) -> str:
        """Get the CLI name from config."""
        if hasattr(self.config, 'cli') and hasattr(self.config.cli, 'name'):
            return self.config.cli.name
        elif isinstance(self.config, dict) and 'cli' in self.config:
            return self.config['cli'].get('name', 'cli')
        return self.project_name or "cli"
    
    def get_version(self) -> str:
        """Get version from config or context."""
        if hasattr(self.config, 'cli') and hasattr(self.config.cli, 'version'):
            return self.config.cli.version
        elif isinstance(self.config, dict) and 'cli' in self.config:
            return self.config['cli'].get('version', '0.1.0')
        return self.project_version or "0.1.0"


class LanguageAdapter(ABC):
    """Abstract base class for language-specific documentation adapters."""
    
    def __init__(self, language: str):
        self.language = language
    
    @abstractmethod
    def format_command_usage(self, command_name: str, command_config: Any) -> str:
        """Format command usage for the specific language."""
        pass
    
    @abstractmethod
    def format_installation_instructions(self, config: Any) -> str:
        """Format installation instructions for the specific language."""
        pass
    
    @abstractmethod
    def format_hook_example(self, command_name: str, command_config: Any) -> str:
        """Format hook implementation example for the specific language."""
        pass
    
    @abstractmethod
    def get_file_extension(self) -> str:
        """Get appropriate file extension for the language."""
        pass
    
    def format_option(self, option: Any) -> str:
        """Format a command-line option."""
        short = f"-{option.short}, " if hasattr(option, 'short') and option.short else ""
        name = option.name if hasattr(option, 'name') else str(option)
        return f"{short}--{name}"


class PythonAdapter(LanguageAdapter):
    """Python-specific documentation adapter."""
    
    def __init__(self):
        super().__init__("python")
    
    def format_command_usage(self, command_name: str, command_config: Any) -> str:
        """Format Python/Click command usage."""
        cli_name = command_name.split()[0]  # Get root CLI name
        usage = f"{cli_name} {command_name}"
        
        # Add arguments
        if hasattr(command_config, 'args') and command_config.args:
            for arg in command_config.args:
                arg_name = arg.name.upper() if hasattr(arg, 'name') else "ARG"
                required = getattr(arg, 'required', True)
                if required:
                    usage += f" {arg_name}"
                else:
                    usage += f" [{arg_name}]"
        
        # Add options hint
        if hasattr(command_config, 'options') and command_config.options:
            usage += " [OPTIONS]"
        
        return usage
    
    def format_installation_instructions(self, config: Any) -> str:
        """Format Python installation instructions."""
        instructions = []
        
        # Check for pypi_name in installation config
        if hasattr(config, 'installation') and hasattr(config.installation, 'pypi_name'):
            pypi_name = config.installation.pypi_name
            instructions.extend([
                "### Installation",
                "",
                "Install using pip:",
                "```bash",
                f"pip install {pypi_name}",
                "```",
                "",
                "Or install in development mode:",
                "```bash",
                f"pip install -e .",
                "```"
            ])
        else:
            instructions.extend([
                "### Installation",
                "",
                "Install using the setup script:",
                "```bash",
                "./setup.sh install",
                "```",
                "",
                "Or install in development mode:",
                "```bash",
                "./setup.sh install --dev",
                "```"
            ])
        
        return "\n".join(instructions)
    
    def format_hook_example(self, command_name: str, command_config: Any) -> str:
        """Format Python hook example."""
        hook_name = f"on_{command_name.replace('-', '_')}"
        
        example = f'''```python
# app_hooks.py

def {hook_name}(**kwargs):
    """Handle the {command_name} command."""
    # Access arguments and options through kwargs
'''
        
        # Add argument examples
        if hasattr(command_config, 'args') and command_config.args:
            for arg in command_config.args:
                arg_name = arg.name if hasattr(arg, 'name') else 'arg'
                example += f"    {arg_name} = kwargs.get('{arg_name}')\n"
        
        # Add option examples
        if hasattr(command_config, 'options') and command_config.options:
            for opt in command_config.options:
                opt_name = opt.name if hasattr(opt, 'name') else 'option'
                example += f"    {opt_name} = kwargs.get('{opt_name}')\n"
        
        example += '''    
    # Implement your logic here
    print(f"Executing {command_name}")
    return 0  # Return exit code
```'''
        
        return example
    
    def get_file_extension(self) -> str:
        return ".py"


class NodeJSAdapter(LanguageAdapter):
    """Node.js-specific documentation adapter."""
    
    def __init__(self):
        super().__init__("nodejs")
    
    def format_command_usage(self, command_name: str, command_config: Any) -> str:
        """Format Node.js/Commander command usage."""
        cli_name = command_name.split()[0]
        usage = f"node {cli_name}.js {command_name}"
        
        # Add arguments
        if hasattr(command_config, 'args') and command_config.args:
            for arg in command_config.args:
                arg_name = f"<{arg.name}>" if getattr(arg, 'required', True) else f"[{arg.name}]"
                usage += f" {arg_name}"
        
        # Add options hint
        if hasattr(command_config, 'options') and command_config.options:
            usage += " [options]"
        
        return usage
    
    def format_installation_instructions(self, config: Any) -> str:
        """Format Node.js installation instructions."""
        instructions = [
            "### Installation",
            "",
            "Install dependencies:",
            "```bash",
            "npm install",
            "```",
            "",
            "Link for global usage:",
            "```bash",
            "npm link",
            "```",
            "",
            "Or install globally from npm:",
            "```bash",
            f"npm install -g {config.cli.name if hasattr(config, 'cli') else 'your-cli'}",
            "```"
        ]
        
        return "\n".join(instructions)
    
    def format_hook_example(self, command_name: str, command_config: Any) -> str:
        """Format Node.js hook example."""
        hook_name = "on" + "".join(word.capitalize() for word in command_name.split("-"))
        
        example = f'''```javascript
// src/hooks.js

export async function {hook_name}(args) {{
    // Access arguments and options through args object
'''
        
        # Add argument examples
        if hasattr(command_config, 'args') and command_config.args:
            example += "    const { "
            arg_names = [arg.name for arg in command_config.args if hasattr(arg, 'name')]
            example += ", ".join(arg_names)
            example += " } = args;\n"
        
        example += '''    
    // Implement your logic here
    console.log(`Executing ${command_name}`);
    return 0; // Return exit code
}
```'''
        
        return example
    
    def get_file_extension(self) -> str:
        return ".js"


class TypeScriptAdapter(LanguageAdapter):
    """TypeScript-specific documentation adapter."""
    
    def __init__(self):
        super().__init__("typescript")
    
    def format_command_usage(self, command_name: str, command_config: Any) -> str:
        """Format TypeScript command usage."""
        cli_name = command_name.split()[0]
        usage = f"npx ts-node {cli_name}.ts {command_name}"
        
        # Add arguments
        if hasattr(command_config, 'args') and command_config.args:
            for arg in command_config.args:
                arg_name = f"<{arg.name}>" if getattr(arg, 'required', True) else f"[{arg.name}]"
                usage += f" {arg_name}"
        
        # Add options hint
        if hasattr(command_config, 'options') and command_config.options:
            usage += " [options]"
        
        return usage
    
    def format_installation_instructions(self, config: Any) -> str:
        """Format TypeScript installation instructions."""
        instructions = [
            "### Installation",
            "",
            "Install dependencies:",
            "```bash",
            "npm install",
            "```",
            "",
            "Build the project:",
            "```bash",
            "npm run build",
            "```",
            "",
            "Link for global usage:",
            "```bash",
            "npm link",
            "```"
        ]
        
        return "\n".join(instructions)
    
    def format_hook_example(self, command_name: str, command_config: Any) -> str:
        """Format TypeScript hook example."""
        hook_name = "on" + "".join(word.capitalize() for word in command_name.split("-"))
        
        example = f'''```typescript
// src/hooks.ts

interface {hook_name.capitalize()}Args {{
'''
        
        # Add argument types
        if hasattr(command_config, 'args') and command_config.args:
            for arg in command_config.args:
                if hasattr(arg, 'name'):
                    example += f"    {arg.name}: string;\n"
        
        # Add option types
        if hasattr(command_config, 'options') and command_config.options:
            for opt in command_config.options:
                if hasattr(opt, 'name'):
                    opt_type = "string"
                    if hasattr(opt, 'type'):
                        type_map = {'bool': 'boolean', 'int': 'number', 'float': 'number'}
                        opt_type = type_map.get(opt.type, 'string')
                    example += f"    {opt.name}?: {opt_type};\n"
        
        example += f'''}}

export async function {hook_name}(args: {hook_name.capitalize()}Args): Promise<number> {{
    // Implement your logic here
    console.log(`Executing {command_name}`);
    return 0; // Return exit code
}}
```'''
        
        return example
    
    def get_file_extension(self) -> str:
        return ".ts"


class RustAdapter(LanguageAdapter):
    """Rust-specific documentation adapter."""
    
    def __init__(self):
        super().__init__("rust")
    
    def format_command_usage(self, command_name: str, command_config: Any) -> str:
        """Format Rust/Clap command usage."""
        cli_name = command_name.split()[0]
        usage = f"{cli_name} {command_name}"
        
        # Add arguments
        if hasattr(command_config, 'args') and command_config.args:
            for arg in command_config.args:
                arg_name = arg.name.upper() if hasattr(arg, 'name') else "ARG"
                required = getattr(arg, 'required', True)
                if required:
                    usage += f" <{arg_name}>"
                else:
                    usage += f" [{arg_name}]"
        
        # Add options hint
        if hasattr(command_config, 'options') and command_config.options:
            usage += " [OPTIONS]"
        
        return usage
    
    def format_installation_instructions(self, config: Any) -> str:
        """Format Rust installation instructions."""
        cli_name = config.cli.name if hasattr(config, 'cli') else "your-cli"
        
        instructions = [
            "### Installation",
            "",
            "Build and install using Cargo:",
            "```bash",
            "cargo install --path .",
            "```",
            "",
            "Or build in release mode:",
            "```bash",
            "cargo build --release",
            f"# Binary will be at ./target/release/{cli_name}",
            "```"
        ]
        
        return "\n".join(instructions)
    
    def format_hook_example(self, command_name: str, command_config: Any) -> str:
        """Format Rust hook example."""
        hook_name = f"on_{command_name.replace('-', '_')}"
        struct_name = "".join(word.capitalize() for word in command_name.split("-")) + "Args"
        
        example = f'''```rust
// src/hooks.rs

use anyhow::Result;

#[derive(Debug)]
pub struct {struct_name} {{
'''
        
        # Add fields
        if hasattr(command_config, 'args') and command_config.args:
            for arg in command_config.args:
                if hasattr(arg, 'name'):
                    example += f"    pub {arg.name}: String,\n"
        
        if hasattr(command_config, 'options') and command_config.options:
            for opt in command_config.options:
                if hasattr(opt, 'name'):
                    opt_type = "String"
                    if hasattr(opt, 'type'):
                        type_map = {'bool': 'bool', 'int': 'i32', 'float': 'f64'}
                        opt_type = type_map.get(opt.type, 'String')
                    required = not getattr(opt, 'default', None) is None
                    if not required:
                        opt_type = f"Option<{opt_type}>"
                    example += f"    pub {opt.name}: {opt_type},\n"
        
        example += f'''}}

pub fn {hook_name}(args: &{struct_name}) -> Result<()> {{
    // Implement your logic here
    println!("Executing {command_name}");
    Ok(())
}}
```'''
        
        return example
    
    def get_file_extension(self) -> str:
        return ".rs"


class DocumentationGenerator:
    """Main documentation generator for Goobits CLI configurations."""
    
    def __init__(self):
        self.adapters: Dict[str, LanguageAdapter] = {
            "python": PythonAdapter(),
            "nodejs": NodeJSAdapter(),
            "typescript": TypeScriptAdapter(),
            "rust": RustAdapter()
        }
    
    def get_adapter(self, language: str) -> LanguageAdapter:
        """Get the appropriate language adapter."""
        adapter = self.adapters.get(language)
        if not adapter:
            raise ValueError(f"Unsupported language: {language}")
        return adapter
    
    def generate_readme(self, context: DocumentationContext) -> str:
        """Generate a complete README file."""
        sections = []
        
        # Title and description
        sections.append(self._generate_header_section(context))
        
        # Installation
        sections.append(self._generate_installation_section(context))
        
        # Quick start
        if context.include_examples:
            sections.append(self._generate_quick_start_section(context))
        
        # Command reference
        sections.append(self._generate_command_reference_section(context))
        
        # Configuration
        sections.append(self._generate_configuration_section(context))
        
        # Development
        if context.include_api_reference:
            sections.append(self._generate_development_section(context))
        
        # Combine sections based on output format
        if context.output_format == OutputFormat.MARKDOWN:
            return "\n\n".join(section.to_markdown() for section in sections)
        elif context.output_format == OutputFormat.PLAINTEXT:
            return "\n\n".join(section.to_plaintext() for section in sections)
        else:
            raise NotImplementedError(f"Output format {context.output_format} not implemented")
    
    def generate_help_text(self, context: DocumentationContext) -> str:
        """Generate command-line help text."""
        adapter = self.get_adapter(context.language)
        lines = []
        
        # Header
        cli_config = context.config.cli if hasattr(context.config, 'cli') else context.config.get('cli', {})
        name = cli_config.name if hasattr(cli_config, 'name') else cli_config.get('name', 'cli')
        tagline = cli_config.tagline if hasattr(cli_config, 'tagline') else cli_config.get('tagline', '')
        
        lines.extend([name.upper(), tagline, ""])
        
        # Usage
        lines.extend(["USAGE:", f"    {name} [COMMAND] [OPTIONS]", ""])
        
        # Commands
        if hasattr(cli_config, 'commands') or 'commands' in cli_config:
            lines.extend(["COMMANDS:"])
            commands = cli_config.commands if hasattr(cli_config, 'commands') else cli_config.get('commands', {})
            
            for cmd_name, cmd_config in commands.items():
                desc = cmd_config.desc if hasattr(cmd_config, 'desc') else cmd_config.get('desc', '')
                lines.append(f"    {cmd_name:<20} {desc}")
            lines.append("")
        
        # Global options
        if hasattr(cli_config, 'options') or 'options' in cli_config:
            lines.extend(["OPTIONS:"])
            options = cli_config.options if hasattr(cli_config, 'options') else cli_config.get('options', [])
            
            for opt in options:
                opt_str = adapter.format_option(opt)
                desc = opt.desc if hasattr(opt, 'desc') else opt.get('desc', '')
                lines.append(f"    {opt_str:<25} {desc}")
            lines.append("")
        
        return "\n".join(lines)
    
    def generate_usage_examples(self, context: DocumentationContext) -> str:
        """Generate usage examples for all commands."""
        adapter = self.get_adapter(context.language)
        sections = []
        
        cli_config = context.config.cli if hasattr(context.config, 'cli') else context.config.get('cli', {})
        cli_name = cli_config.name if hasattr(cli_config, 'name') else cli_config.get('name', 'cli')
        
        # Basic usage section
        basic_section = DocumentationSection(
            title="Basic Usage",
            content=f"```bash\n# Show help\n{cli_name} --help\n\n# Show version\n{cli_name} --version\n```"
        )
        sections.append(basic_section)
        
        # Command examples
        if hasattr(cli_config, 'commands') or 'commands' in cli_config:
            commands = cli_config.commands if hasattr(cli_config, 'commands') else cli_config.get('commands', {})
            
            for cmd_name, cmd_config in commands.items():
                usage = adapter.format_command_usage(cmd_name, cmd_config)
                example_content = f"```bash\n{usage}\n```"
                
                # Add specific examples if available
                if hasattr(cmd_config, 'examples'):
                    for example in cmd_config.examples:
                        example_content += f"\n\n```bash\n# {example.description}\n{example.command}\n```"
                
                cmd_section = DocumentationSection(
                    title=f"Command: {cmd_name}",
                    content=example_content
                )
                sections.append(cmd_section)
        
        if context.output_format == OutputFormat.MARKDOWN:
            return "\n\n".join(section.to_markdown(level=2) for section in sections)
        else:
            return "\n\n".join(section.to_plaintext() for section in sections)
    
    def _generate_header_section(self, context: DocumentationContext) -> DocumentationSection:
        """Generate the header section of documentation."""
        cli_config = context.config.cli if hasattr(context.config, 'cli') else context.config.get('cli', {})
        name = cli_config.name if hasattr(cli_config, 'name') else cli_config.get('name', 'CLI')
        tagline = cli_config.tagline if hasattr(cli_config, 'tagline') else cli_config.get('tagline', '')
        description = cli_config.description if hasattr(cli_config, 'description') else cli_config.get('description', '')
        
        content = tagline
        if description:
            content += f"\n\n{description}"
        
        return DocumentationSection(title=name, content=content, order=1)
    
    def _generate_installation_section(self, context: DocumentationContext) -> DocumentationSection:
        """Generate installation instructions section."""
        adapter = self.get_adapter(context.language)
        content = adapter.format_installation_instructions(context.config)
        
        return DocumentationSection(title="Installation", content=content, order=2)
    
    def _generate_quick_start_section(self, context: DocumentationContext) -> DocumentationSection:
        """Generate quick start section."""
        cli_name = context.get_cli_name()
        
        content = f"""1. Install the CLI (see Installation section)
2. Run `{cli_name} --help` to see available commands
3. Try a simple command: `{cli_name} <command>`
4. Configure settings: `{cli_name} config set <key> <value>`"""
        
        return DocumentationSection(title="Quick Start", content=content, order=3)
    
    def _generate_command_reference_section(self, context: DocumentationContext) -> DocumentationSection:
        """Generate command reference section."""
        cli_config = context.config.cli if hasattr(context.config, 'cli') else context.config.get('cli', {})
        
        section = DocumentationSection(title="Command Reference", content="", order=4)
        
        if hasattr(cli_config, 'commands') or 'commands' in cli_config:
            commands = cli_config.commands if hasattr(cli_config, 'commands') else cli_config.get('commands', {})
            
            for cmd_name, cmd_config in commands.items():
                cmd_section = self._generate_command_section(cmd_name, cmd_config, context)
                section.subsections.append(cmd_section)
        
        return section
    
    def _generate_command_section(self, cmd_name: str, cmd_config: Any, context: DocumentationContext) -> DocumentationSection:
        """Generate documentation for a single command."""
        adapter = self.get_adapter(context.language)
        
        desc = cmd_config.desc if hasattr(cmd_config, 'desc') else cmd_config.get('desc', '')
        content_lines = [desc, "", "**Usage:**", f"```\n{adapter.format_command_usage(cmd_name, cmd_config)}\n```"]
        
        # Arguments
        if hasattr(cmd_config, 'args') and cmd_config.args:
            content_lines.extend(["", "**Arguments:**"])
            for arg in cmd_config.args:
                arg_name = arg.name if hasattr(arg, 'name') else 'arg'
                arg_desc = arg.desc if hasattr(arg, 'desc') else ''
                required = "required" if getattr(arg, 'required', True) else "optional"
                content_lines.append(f"- `{arg_name}` ({required}): {arg_desc}")
        
        # Options
        if hasattr(cmd_config, 'options') and cmd_config.options:
            content_lines.extend(["", "**Options:**"])
            for opt in cmd_config.options:
                opt_str = adapter.format_option(opt)
                opt_desc = opt.desc if hasattr(opt, 'desc') else ''
                content_lines.append(f"- `{opt_str}`: {opt_desc}")
        
        # Hook example
        if context.include_examples:
            content_lines.extend(["", "**Hook Implementation:**", "", adapter.format_hook_example(cmd_name, cmd_config)])
        
        return DocumentationSection(
            title=cmd_name,
            content="\n".join(content_lines)
        )
    
    def _generate_configuration_section(self, context: DocumentationContext) -> DocumentationSection:
        """Generate configuration section."""
        content = """The CLI can be configured through:

1. **Configuration file**: `~/.config/{cli_name}/config.yaml`
2. **Environment variables**: `{CLI_NAME}_*`
3. **Command line options**: Override any configuration

### Configuration File Format

```yaml
# Example configuration
theme: dark
output_format: json
verbose: true
```

### Environment Variables

- `{CLI_NAME}_CONFIG_PATH`: Custom configuration file path
- `{CLI_NAME}_LOG_LEVEL`: Set logging level (DEBUG, INFO, WARN, ERROR)
""".format(
            cli_name=context.get_cli_name(),
            CLI_NAME=context.get_cli_name().upper()
        )
        
        return DocumentationSection(title="Configuration", content=content, order=5)
    
    def _generate_development_section(self, context: DocumentationContext) -> DocumentationSection:
        """Generate development/API reference section."""
        adapter = self.get_adapter(context.language)
        
        content = f"""### Hook System

The CLI uses a hook system for implementing command logic. Create hooks in:

- Python: `app_hooks.py`
- Node.js: `src/hooks.js`
- TypeScript: `src/hooks.ts`
- Rust: `src/hooks.rs`

### Adding New Commands

1. Update the `goobits.yaml` configuration file
2. Run `goobits build` to regenerate the CLI
3. Implement the hook for your new command

### Testing

Run tests with:
```bash
# Python
pytest

# Node.js/TypeScript
npm test

# Rust
cargo test
```"""
        
        return DocumentationSection(title="Development", content=content, order=6)


# Convenience functions
def generate_documentation(config: Any, language: str = "python", 
                         doc_type: DocumentationType = DocumentationType.README,
                         output_format: OutputFormat = OutputFormat.MARKDOWN) -> str:
    """Generate documentation for a CLI configuration."""
    generator = DocumentationGenerator()
    context = DocumentationContext(
        config=config,
        language=language,
        doc_type=doc_type,
        output_format=output_format
    )
    
    if doc_type == DocumentationType.README:
        return generator.generate_readme(context)
    elif doc_type == DocumentationType.HELP_TEXT:
        return generator.generate_help_text(context)
    elif doc_type == DocumentationType.USAGE_EXAMPLES:
        return generator.generate_usage_examples(context)
    else:
        raise NotImplementedError(f"Documentation type {doc_type} not implemented")


def create_readme_file(config: Any, language: str = "python", output_path: Optional[Path] = None) -> Path:
    """Create a README file for the CLI configuration."""
    content = generate_documentation(config, language, DocumentationType.README)
    
    if not output_path:
        output_path = Path("README.md")
    
    output_path.write_text(content)
    return output_path