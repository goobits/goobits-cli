"""

Python Language Renderer for Universal Template System



This module provides Python-specific rendering capabilities for the Goobits

Universal Template System, generating Click-based CLI implementations.

"""



import re


import tempfile


from datetime import datetime

from pathlib import Path

from typing import Dict, Any, List

import jinja2



from ..template_engine import LanguageRenderer





class PythonRenderer(LanguageRenderer):

    """

    Python language renderer using Click framework.

    

    Generates Python CLI implementations with:

    - Click decorators for commands, options, and arguments

    - Rich-click integration for enhanced terminal UI

    - Python naming conventions (snake_case)

    - Type annotations and proper imports

    - Hook system integration

    """
    
    def __init__(self, consolidate: bool = False):
        """Initialize Python renderer with optional consolidation mode."""
        self.consolidate = consolidate

    

    @property

    def language(self) -> str:

        """Return the language name."""

        return "python"

    

    @property

    def file_extensions(self) -> Dict[str, str]:

        """Return mapping of component types to file extensions."""

        return {

            "command_handler": "py",

            "config_manager": "py", 

            "completion_engine": "py",

            "error_handler": "py",

            "hook_system": "py"

        }

    

    def get_template_context(self, ir: Dict[str, Any]) -> Dict[str, Any]:

        """

        Transform IR into Python-specific template context.

        

        Args:

            ir: Intermediate representation

            

        Returns:

            Python-specific template context

        """

        # Start with the base IR and add defensive defaults

        context = ir.copy()

        

        # Ensure installation field has defensive defaults

        if "installation" not in context:

            context["installation"] = {}

        

        # Preserve extras while setting defensive defaults

        original_installation = context["installation"]

        context["installation"] = {

            "pypi_name": original_installation.get("pypi_name", context.get("project", {}).get("package_name", "cli_app")),

            **original_installation

        }

        

        # Ensure core fields have defensive defaults

        if "project" in context:

            context["project"] = {

                "name": context["project"].get("name", "Unknown CLI"),

                "description": context["project"].get("description", "A CLI application"),

                "version": context["project"].get("version") or "1.0.0",

                "author": context["project"].get("author", ""),

                "license": context["project"].get("license", ""),

                "package_name": context["project"].get("package_name", "cli_app"),

                "command_name": context["project"].get("command_name", "cli"),

                **{k: v for k, v in context["project"].items() if k not in ["name", "description", "version", "author", "license", "package_name", "command_name"]}

            }

        

        # Add Python-specific context

        context.update({

            "language": "python",

            "framework": "click",

            "imports": self._get_python_imports(ir),

            "types": self._get_python_types(),

            "naming": {

                "snake_case": True,

                "function_prefix": "",

                "class_suffix": "",

            },

            "click_config": {

                "use_rich_click": True,

                "context_settings": {

                    "help_option_names": ["-h", "--help"],

                    "max_content_width": 120

                },

                "show_arguments": True,

                "group_arguments_options": True,

            },

            "metadata": {

                **{k: v for k, v in context.get("metadata", {}).items() if not isinstance(v, str) or not v.startswith("{{")},

                "timestamp": datetime.now().isoformat(),

                "generator_version": "2.0.0-beta.2",

                "package_name": context["project"]["package_name"].replace("-", "_"),

                "command_name": context["project"]["command_name"],

            },

            "config_filename": context.get("metadata", {}).get("config_filename", "goobits.yaml"),

            "consolidation_mode": self.consolidate,

            # Make datetime available to templates
            "datetime": datetime

        })

        

        # Ensure CLI field has defensive defaults

        if "cli" not in context:

            context["cli"] = {}

        

        # Add defensive defaults for CLI options

        if "options" not in context["cli"]:

            context["cli"]["options"] = []

        

        # Ensure root_command structure exists with defensive defaults

        if "root_command" not in context["cli"]:

            context["cli"]["root_command"] = {}

        

        if "subcommands" not in context["cli"]["root_command"]:

            context["cli"]["root_command"]["subcommands"] = []

        

        # Transform CLI structure for Python/Click

        if "cli" in context:

            context["cli"] = self._transform_cli_for_python(context["cli"])
            
            # Ensure command_hierarchy is present in CLI section for template compatibility
            if "command_hierarchy" not in context["cli"]:
                context["cli"]["command_hierarchy"] = {
                    "groups": [],
                    "leaves": [],
                    "max_depth": 0,
                    "flat_commands": []
                }

        
        # Ensure command_hierarchy is present for template compatibility

        if "command_hierarchy" not in context:

            context["command_hierarchy"] = {

                "groups": [],

                "leaves": [],

                "max_depth": 0,

                "flat_commands": []

            }

        

        return context

    

    def get_custom_filters(self) -> Dict[str, callable]:

        """

        Return Python-specific Jinja2 filters.

        

        Returns:

            Dictionary of filter functions

        """

        return {

            "python_type": self._python_type_filter,

            "python_function_name": self._python_function_name_filter,

            "python_variable_name": self._python_variable_name_filter,

            "python_import_path": self._python_import_path_filter,

            "click_decorator": self._click_decorator_filter,

            "click_argument": self._click_argument_filter,

            "click_option": self._click_option_filter,

            "python_repr": self._python_repr_filter,

            "snake_case": self._snake_case_filter,

            "python_docstring": self._python_docstring_filter,

            "js_string": self._js_string_filter,  # For compatibility with universal templates

        }

    

    def _has_interactive_features(self, cli_schema: Dict[str, Any]) -> bool:

        """Check if CLI has interactive mode features."""

        features = cli_schema.get("features", {})

        interactive_mode = features.get("interactive_mode", {})

        return interactive_mode.get("enabled", False)

    

    def render_component(self, component_name: str, template_content: str, 

                        context: Dict[str, Any]) -> str:

        """

        Render a component template for Python.

        

        Args:

            component_name: Name of the component

            template_content: Universal template content

            context: Python-specific context

            

        Returns:

            Rendered Python code

        """

        # Create Jinja2 environment with custom filters

        env = jinja2.Environment(

            loader=jinja2.BaseLoader(),

            trim_blocks=True,

            lstrip_blocks=True

        )

        

        # Add built-in filters
        def to_json_string(value) -> str:
            """Convert value to JSON string representation."""
            return str(value) if value is not None else 'null'

        env.filters['repr'] = repr
        env.filters['tojson'] = to_json_string

        

        # Add custom filters

        env.filters.update(self.get_custom_filters())

        

        # Render the template

        template = env.from_string(template_content)

        rendered_content = template.render(**context)

        

        # Post-process the rendered content

        rendered_content = self._post_process_python_code(rendered_content)

        

        return rendered_content

    


    

    def consolidate_files(self, files: Dict[str, str], output_dir: Path) -> Dict[str, str]:
        """
        Consolidate multiple Python files into a single executable using Shiv.
        
        Args:
            files: Dictionary mapping file paths to file contents
            output_dir: Output directory path
            
        Returns:
            Dictionary with consolidated files (cli.py + setup.sh)
        """
        if not files:
            return files
            
        # Separate Python files from non-Python files (like setup.sh)
        python_files = {}
        non_python_files = {}
        
        for file_path, content in files.items():
            if file_path.endswith('.py'):
                python_files[file_path] = content
            else:
                non_python_files[file_path] = content
        
        # If there's only one Python file or no Python files, no consolidation needed
        if len(python_files) <= 1:
            return files
        
        # Create a temporary directory for consolidation
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Write all Python files to the temporary directory
            for file_path, content in python_files.items():
                # Get just the filename for temp directory
                filename = Path(file_path).name
                temp_file = temp_path / filename
                temp_file.write_text(content, encoding='utf-8')
            
            # Find the main CLI file (usually cli.py)
            main_file = None
            main_file_path = None
            for file_path in python_files:
                filename = Path(file_path).name
                if filename == 'cli.py':
                    main_file = temp_path / filename
                    main_file_path = file_path
                    break
            
            if not main_file:
                # If no cli.py found, use the first Python file
                first_py_file = list(python_files.keys())[0]
                main_file = temp_path / Path(first_py_file).name
                main_file_path = first_py_file
            
            if main_file and main_file.exists():
                # Shiv-based consolidation: create self-contained zipapp
                try:
                    # Install dependencies for the consolidated package
                    import subprocess
                    
                    # Create setup.py for proper package structure
                    setup_py_content = f'''
from setuptools import setup, find_packages

setup(
    name="{Path(main_file_path).stem}",
    version="1.0.0",
    packages=find_packages(),
    entry_points={{
        'console_scripts': [
            '{Path(main_file_path).stem}={Path(main_file_path).stem}:cli',
        ],
    }},
    install_requires=[
        "click",
        "rich-click", 
    ],
)
'''
                    setup_file = temp_path / "setup.py"
                    setup_file.write_text(setup_py_content, encoding='utf-8')
                    
                    # Create __init__.py to make it a proper package
                    init_file = temp_path / "__init__.py"
                    init_file.write_text("# Package marker", encoding='utf-8')
                    
                    # Create shiv executable
                    shiv_file = temp_path / f"{Path(main_file_path).stem}.pyz"
                    
                    # Run Shiv to create consolidated executable
                    shiv_result = subprocess.run([
                        'python3', '-m', 'shiv',
                        '--site-packages', str(temp_path),
                        '--compressed',
                        '--output-file', str(shiv_file),
                        '--entry-point', f'{Path(main_file_path).stem}:cli'
                    ], capture_output=True, text=True, cwd=temp_path)
                    
                    if shiv_result.returncode == 0 and shiv_file.exists():
                        # Read the Shiv executable 
                        shiv_content = shiv_file.read_text(encoding='utf-8', errors='ignore')
                        
                        # Create consolidated files dictionary  
                        consolidated_files = {main_file_path: shiv_content}
                        
                        # Add non-Python files back
                        consolidated_files.update(non_python_files)
                        
                        print(f"✅ Consolidated {len(python_files)} Python files into single executable using Shiv")
                        return consolidated_files
                    else:
                        print(f"⚠️ Shiv consolidation failed: {shiv_result.stderr}")
                        print("Falling back to simple file combination...")
                        
                        # Fallback to simple combination
                        combined_content = []
                        combined_content.append('#!/usr/bin/env python3')
                        combined_content.append('"""')
                        combined_content.append('Consolidated CLI - Generated by Goobits Universal Template System')
                        combined_content.append('"""')
                        combined_content.append('')
                        
                        # Add all Python file contents
                        for file_path, content in python_files.items():
                            filename = Path(file_path).stem
                            combined_content.append(f'# === {filename}.py ===')
                            # Split content into lines to preserve proper line structure
                            if content:
                                content_lines = content.splitlines()
                                # Fix any problematic line combinations where docstrings are merged with code
                                fixed_lines = []
                                for line in content_lines:
                                    if '"""' in line and 'return' in line:
                                        # Find the pattern: """...""" followed by code
                                        # Look for the last """ which should be the closing docstring
                                        triple_quote_positions = []
                                        start = 0
                                        while True:
                                            pos = line.find('"""', start)
                                            if pos == -1:
                                                break
                                            triple_quote_positions.append(pos)
                                            start = pos + 3
                                        
                                        if len(triple_quote_positions) >= 2:
                                            # We have opening and closing quotes
                                            closing_pos = triple_quote_positions[-1] + 3
                                            docstring_part = line[:closing_pos]
                                            remainder = line[closing_pos:].strip()
                                            fixed_lines.append(docstring_part)
                                            if remainder:
                                                # Preserve original indentation for the remainder
                                                original_indent = len(line) - len(line.lstrip())
                                                fixed_lines.append(' ' * original_indent + remainder)
                                        else:
                                            # Fallback: just add the line as-is
                                            fixed_lines.append(line)
                                    else:
                                        fixed_lines.append(line)
                                combined_content.extend(fixed_lines)
                            combined_content.append('')
                        
                        # Remove duplicate imports and fix basic issues
                        final_content = '\n'.join(combined_content)
                        final_content = final_content.replace('📁', '[folder]')
                        final_content = final_content.replace('📝', '[file]')
                        final_content = final_content.replace('💾', '[backup]')
                        final_content = final_content.replace('🧪', '[experimental]')
                        final_content = final_content.replace('🎯', '[template]')
                        final_content = final_content.replace('🔥', '[force]')
                        final_content = final_content.replace('🌍', '[host]')
                        final_content = final_content.replace('🔌', '[port]')
                        
                        consolidated_files = {main_file_path: final_content}
                        consolidated_files.update(non_python_files)
                        
                        print(f"✅ Consolidated {len(python_files)} Python files into single file (fallback mode)")
                        return consolidated_files
                    
                except Exception as e:
                    print(f"⚠️  Consolidation failed: {e}, returning original files")
                    return files
        
        return files

    def get_output_structure(self, ir: Dict[str, Any]) -> Dict[str, str]:
        """
        Define output file structure for Python CLIs.
        
        Returns proper Python package structure with:
        - pyproject.toml (package metadata and dependencies)
        - src/package_name/__init__.py (package marker)
        - src/package_name/cli.py (main CLI module)
        
        Args:
            ir: Intermediate representation
            
        Returns:
            Dictionary mapping component names to output file paths
        """
        package_name = ir["project"]["package_name"].replace("-", "_")
        
        # Use cli_output_path if specified in the config
        if "cli_output_path" in ir["project"] and ir["project"]["cli_output_path"]:
            cli_path = ir["project"]["cli_output_path"]
            # Handle any template variables in the path
            cli_path = cli_path.format(package_name=package_name)
        else:
            # Default Python package structure
            cli_path = f"src/{package_name}/cli.py"
        
        return {
            "command_handler": cli_path,
            "pyproject_toml": "pyproject.toml",
            "package_init": f"src/{package_name}/__init__.py",
            # setup.sh is handled by the main build system
        }

    

    def _get_python_imports(self, ir: Dict[str, Any]) -> List[str]:

        """Generate required Python imports based on IR."""

        imports = [

            "import sys",

            "import os",

            "from pathlib import Path",

            "from typing import Optional, Dict, Any, List",

            "import rich_click as click",

            "from rich_click import RichGroup, RichCommand",

        ]

        

        # Add conditional imports based on features

        cli_schema = ir.get("cli", {})

        

        if self._has_config_features(cli_schema):

            imports.append("import json")

            imports.append("import configparser")

        

        if self._has_async_features(cli_schema):

            imports.append("import asyncio")

        

        if self._has_completion_features(cli_schema):

            imports.append("import subprocess")

        

        if self._has_interactive_features(cli_schema):

            imports.append("import cmd")

            imports.append("import shlex")

            imports.append("import readline")

        

        return imports

    

    def _get_python_types(self) -> Dict[str, str]:

        """Map generic types to Python/Click types."""

        return {

            "string": "str",

            "integer": "int", 

            "float": "float",

            "boolean": "bool",

            "flag": "bool",

            "path": "click.Path",

            "file": "click.File",

            "choice": "click.Choice",

            "uuid": "str",  # Can be enhanced with UUID validation

            "email": "str",  # Can be enhanced with email validation

            "url": "str",    # Can be enhanced with URL validation

        }

    

    def _transform_cli_for_python(self, cli_schema: Dict[str, Any]) -> Dict[str, Any]:

        """Transform CLI schema for Python-specific rendering."""

        transformed = cli_schema.copy()

        

        # Transform root command

        if "root_command" in transformed:

            transformed["root_command"] = self._transform_command_for_python(

                transformed["root_command"]

            )

        

        # Transform all commands

        if "commands" in transformed:

            transformed_commands = {}

            for cmd_name, cmd_data in transformed["commands"].items():

                transformed_commands[cmd_name] = self._transform_command_for_python(cmd_data)

            transformed["commands"] = transformed_commands

        

        return transformed

    

    def _transform_command_for_python(self, command: Dict[str, Any]) -> Dict[str, Any]:

        """Transform a single command for Python rendering."""

        transformed = command.copy()

        

        # Transform function name (handle case where 'name' might not be present)

        command_name = command.get("name", "unnamed_command")

        transformed["python_name"] = self._snake_case_filter(command_name)

        

        # Transform arguments

        if "arguments" in transformed:

            transformed["arguments"] = [

                self._transform_argument_for_python(arg)

                for arg in transformed["arguments"]

            ]

        

        # Transform options

        if "options" in transformed:

            transformed["options"] = [

                self._transform_option_for_python(opt)

                for opt in transformed["options"]

            ]

        

        # Transform subcommands recursively

        if "subcommands" in transformed:

            transformed["subcommands"] = [

                self._transform_command_for_python(subcmd)

                for subcmd in transformed["subcommands"]

            ]

        

        return transformed

    

    def _transform_argument_for_python(self, argument: Dict[str, Any]) -> Dict[str, Any]:

        """Transform argument for Python Click."""

        transformed = argument.copy()

        transformed["python_name"] = self._python_variable_name_filter(argument["name"])

        transformed["python_type"] = self._python_type_filter(argument.get("type", "string"))

        transformed["click_decorator"] = self._click_argument_filter(argument)

        return transformed

    

    def _transform_option_for_python(self, option: Dict[str, Any]) -> Dict[str, Any]:

        """Transform option for Python Click."""

        transformed = option.copy()

        transformed["python_name"] = self._python_variable_name_filter(option["name"])

        transformed["python_type"] = self._python_type_filter(option.get("type", "string"))

        transformed["click_decorator"] = self._click_option_filter(option)

        return transformed

    

    def _has_config_features(self, cli_schema: Dict[str, Any]) -> bool:

        """Check if CLI uses configuration features."""

        # Look for config-related commands or global config options

        commands = cli_schema.get("commands", {})

        return "config" in commands or any(

            "config" in cmd.get("name", "").lower() 

            for cmd in commands.values()

        )

    

    def _has_async_features(self, cli_schema: Dict[str, Any]) -> bool:

        """Check if CLI uses async features."""

        # For now, assume no async features unless explicitly marked

        return False

    

    def _has_completion_features(self, cli_schema: Dict[str, Any]) -> bool:

        """Check if CLI uses shell completion."""

        return cli_schema.get("completion", {}).get("enabled", True)

    

    def _post_process_python_code(self, code: str) -> str:

        """Post-process rendered Python code for formatting."""

        # Remove excessive blank lines

        code = re.sub(r'\n\s*\n\s*\n', '\n\n', code)

        

        # Ensure proper indentation (basic cleanup)

        lines = code.split('\n')

        processed_lines = []

        for line in lines:

            if line.strip():  # Non-empty line

                processed_lines.append(line.rstrip())  # Remove trailing whitespace

            else:  # Empty line

                processed_lines.append('')

        

        return '\n'.join(processed_lines)

    

    # Filter implementations

    

    def _python_type_filter(self, type_str: str) -> str:

        """Convert generic type to Python/Click type."""

        type_map = self._get_python_types()

        return type_map.get(type_str, "str")

    

    def _python_function_name_filter(self, name: str) -> str:

        """Convert name to Python function name (snake_case)."""

        return self._snake_case_filter(name)

    

    def _python_variable_name_filter(self, name: str) -> str:

        """Convert name to Python variable name (snake_case)."""

        return self._snake_case_filter(name)

    

    def _python_import_path_filter(self, module_path: str) -> str:

        """Generate Python import statement."""

        return f"from {module_path} import *"

    

    def _click_decorator_filter(self, option_or_arg: Dict[str, Any]) -> str:

        """Generate Click decorator for option or argument."""

        if option_or_arg.get("type") == "argument":

            return self._click_argument_filter(option_or_arg)

        else:

            return self._click_option_filter(option_or_arg)

    

    def _click_argument_filter(self, argument: Dict[str, Any]) -> str:

        """Generate Click argument decorator."""

        # Convert name to uppercase and replace hyphens with underscores for Click

        name = argument["name"].upper().replace("-", "_")

        

        parts = [f'"{name}"']

        

        # Handle multiple values

        if argument.get("multiple", False):

            parts.append("nargs=-1")

        

        # Handle required

        if not argument.get("required", True):

            parts.append("required=False")

        

        # Handle type

        arg_type = argument.get("type", "string")

        if arg_type != "string":

            click_type = self._python_type_filter(arg_type)

            if click_type != "str":

                parts.append(f"type={click_type}")

        

        decorator_args = ", ".join(parts)

        return f"@click.argument({decorator_args})"

    

    def _click_option_filter(self, option: Dict[str, Any]) -> str:

        """Generate Click option decorator."""

        name = option["name"]

        short = option.get("short")

        

        # Build option names

        option_names = [f'"--{name}"']

        if short:

            option_names.insert(0, f'"-{short}"')

        

        parts = [", ".join(option_names)]

        

        # Add help text

        if "description" in option:

            parts.append(f'help="{option["description"]}"')

        

        # Handle type

        opt_type = option.get("type", "string")

        if opt_type == "flag" or opt_type == "boolean" or opt_type == "bool":

            parts.append("is_flag=True")

        elif opt_type != "string":

            click_type = self._python_type_filter(opt_type)

            if click_type != "str":

                parts.append(f"type={click_type}")

        

        # Handle default value

        if "default" in option and option["default"] is not None:

            default_repr = self._python_repr_filter(option["default"])

            parts.append(f"default={default_repr}")

        

        # Handle multiple

        if option.get("multiple", False):

            parts.append("multiple=True")

        

        # Handle required

        if option.get("required", False):

            parts.append("required=True")

        

        decorator_args = ",\n    ".join(parts)

        return f"@click.option(\n    {decorator_args}\n)"

    

    def _python_repr_filter(self, value: Any) -> str:

        """Convert value to Python repr string."""

        return repr(value)

    

    def _snake_case_filter(self, name: str) -> str:

        """Convert name to snake_case."""

        # Replace hyphens with underscores

        name = name.replace("-", "_")

        

        # Convert CamelCase to snake_case

        name = re.sub(r'([A-Z]+)([A-Z][a-z])', r'\1_\2', name)

        name = re.sub(r'([a-z\d])([A-Z])', r'\1_\2', name)

        

        # Convert to lowercase and clean up

        name = name.lower()

        name = re.sub(r'_+', '_', name)  # Remove multiple underscores

        name = name.strip('_')  # Remove leading/trailing underscores

        

        return name

    

    def _python_docstring_filter(self, text: str) -> str:

        """Format text as Python docstring."""

        if not text:

            return '""""""'

        

        # Clean up the text

        text = text.strip()

        

        # Use triple quotes for multi-line docstrings

        if '\n' in text:

            return f'"""\n    {text}\n    """'

        else:

            return f'"""{text}"""'

    

    def _js_string_filter(self, value: str) -> str:

        """Escape string for JavaScript (compatibility with universal templates)."""

        if not isinstance(value, str):

            return str(value)

        

        return value.replace("'", "\\'").replace('"', '\\"').replace('\n', '\\n')