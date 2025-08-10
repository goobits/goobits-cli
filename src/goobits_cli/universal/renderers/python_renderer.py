"""
Python Language Renderer for Universal Template System

This module provides Python-specific rendering capabilities for the Goobits
Universal Template System, generating Click-based CLI implementations.
"""

import re
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
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
        # Start with the base IR
        context = ir.copy()
        
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
                **context.get("metadata", {}),
                "timestamp": datetime.now().isoformat(),
                "generator_version": "1.4.0",  # TODO: Get from version file
            }
        })
        
        # Transform CLI structure for Python/Click
        if "cli" in context:
            context["cli"] = self._transform_cli_for_python(context["cli"])
        
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
        env.filters['repr'] = repr
        env.filters['tojson'] = lambda x: str(x) if x is not None else 'null'
        
        # Add custom filters
        env.filters.update(self.get_custom_filters())
        
        # Render the template
        template = env.from_string(template_content)
        rendered_content = template.render(**context)
        
        # Post-process the rendered content
        rendered_content = self._post_process_python_code(rendered_content)
        
        return rendered_content
    
    def get_output_structure(self, ir: Dict[str, Any]) -> Dict[str, str]:
        """
        Define output file structure for Python CLIs.
        
        Args:
            ir: Intermediate representation
            
        Returns:
            Dictionary mapping component names to output file paths
        """
        package_name = ir["project"]["package_name"].replace("-", "_")
        cli_name = ir.get("cli", {}).get("root_command", {}).get("name", "cli").replace("-", "_")
        
        output = {
            "command_handler": f"{package_name}/cli.py",
            "config_manager": f"{package_name}/config.py",
            "completion_engine": f"{package_name}/completion.py",
            "error_handler": f"{package_name}/errors.py",
            "hook_system": "hooks.py",  # User-implementable hook template
        }
        
        # Add interactive mode if enabled
        if self._has_interactive_features(ir.get("cli", {})):
            output["interactive_mode"] = f"{package_name}/{cli_name}_interactive.py"
        
        return output
    
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
        if opt_type == "flag" or opt_type == "boolean":
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