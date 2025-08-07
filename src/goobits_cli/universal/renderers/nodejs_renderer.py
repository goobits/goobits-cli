"""
Node.js Renderer for Universal Template System

This module provides Node.js-specific rendering capabilities using Commander.js
framework for CLI generation. It converts universal component templates into
Node.js/JavaScript code with proper ES module support.
"""

import json
import re
from pathlib import Path
from typing import Dict, Any, List, Optional
import jinja2

from ..template_engine import LanguageRenderer


class NodeJSRenderer(LanguageRenderer):
    """
    Node.js/JavaScript renderer for the Universal Template System.
    
    Converts universal component templates into Node.js CLI implementations
    using Commander.js framework with ES module support.
    """
    
    def __init__(self):
        """Initialize the Node.js renderer with custom filters and context."""
        self._jinja_env = None
        
    @property
    def language(self) -> str:
        """Return the language name."""
        return "nodejs"
    
    @property
    def file_extensions(self) -> Dict[str, str]:
        """Return mapping of component types to file extensions."""
        return {
            "js": "javascript",
            "json": "json",
            "md": "markdown"
        }
    
    def get_template_context(self, ir: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform intermediate representation into Node.js-specific context.
        
        Args:
            ir: Intermediate representation from UniversalTemplateEngine
            
        Returns:
            Node.js-specific template context
        """
        # Base context with project information
        context = {
            "project": ir["project"],
            "cli": ir["cli"],
            "installation": ir["installation"],
            "dependencies": ir["dependencies"],
            "metadata": ir["metadata"],
        }
        
        # Node.js-specific additions
        context.update({
            # Commander.js specific structures
            "commander_commands": self._build_commander_structure(ir["cli"]),
            "npm_dependencies": self._build_npm_dependencies(ir),
            "nodejs_imports": self._build_imports(ir),
            "hook_functions": self._build_hook_functions(ir["cli"]),
            
            # JavaScript naming conventions
            "js_package_name": self._to_js_package_name(ir["project"]["package_name"]),
            "js_command_name": self._to_js_variable_name(ir["project"]["command_name"]),
            
            # Node.js-specific metadata
            "node_version": ">=14.0.0",
            "module_type": "module",  # Use ES modules
            "main_file": "index.js",
            "bin_file": "bin/cli.js",
        })
        
        return context
    
    def get_custom_filters(self) -> Dict[str, callable]:
        """
        Return Node.js-specific Jinja2 filters.
        
        Returns:
            Dictionary of filter functions
        """
        return {
            "js_type": self._js_type_filter,
            "camel_case": self._camel_case_filter,
            "js_require": self._js_require_filter,
            "commander_option": self._commander_option_filter,
            "js_variable": self._js_variable_filter,
            "js_string": self._js_string_filter,
            "npm_package_name": self._npm_package_name_filter,
            "hook_name": self._hook_name_filter,
            "commander_argument": self._commander_argument_filter,
            "js_comment": self._js_comment_filter,
        }
    
    def render_component(self, component_name: str, template_content: str, 
                        context: Dict[str, Any]) -> str:
        """
        Render a specific component template for Node.js.
        
        Args:
            component_name: Name of the component being rendered
            template_content: Universal template content
            context: Node.js-specific template context
            
        Returns:
            Rendered JavaScript code
        """
        # Create Jinja environment if not exists
        if self._jinja_env is None:
            self._jinja_env = jinja2.Environment(
                loader=jinja2.BaseLoader(),
                autoescape=False
            )
            # Add custom filters
            for filter_name, filter_func in self.get_custom_filters().items():
                self._jinja_env.filters[filter_name] = filter_func
        
        # Render the template
        template = self._jinja_env.from_string(template_content)
        rendered_content = template.render(**context)
        
        # Post-process for Node.js specific formatting
        return self._post_process_javascript(rendered_content)
    
    def get_output_structure(self, ir: Dict[str, Any]) -> Dict[str, str]:
        """
        Define the output file structure for Node.js CLI.
        
        Args:
            ir: Intermediate representation
            
        Returns:
            Dictionary mapping component names to output file paths
        """
        cli_name = ir.get("cli", {}).get("root_command", {}).get("name", "cli").replace("-", "_")
        
        output = {
            "command_handler": "cli.js",
            "hook_system": "src/hooks.js", 
            "config_manager": "lib/config.js",
            "completion_engine": "completion_engine.js",
            "error_handler": "lib/errors.js",
            # Additional Node.js specific files
            "package_config": "package.json",
            "main_entry": "index.js",
            "bin_entry": "bin/cli.js",
            "readme": "README.md",
            "gitignore": ".gitignore",
        }
        
        # Add interactive mode if enabled (use enhanced version for Node.js)
        if self._has_interactive_features(ir.get("cli", {})):
            output["interactive_mode"] = f"{cli_name}_interactive.js"
            output["interactive_mode_enhanced"] = f"{cli_name}_interactive_enhanced.js"
        
        return output
    
    # Private helper methods
    
    def _build_commander_structure(self, cli_schema: Dict[str, Any]) -> Dict[str, Any]:
        """
        Build Commander.js specific command structure.
        
        Args:
            cli_schema: CLI schema from IR
            
        Returns:
            Commander.js command structure
        """
        commander_data = {
            "root_command": {
                "name": cli_schema["root_command"]["name"],
                "description": cli_schema["root_command"]["description"],
                "version": cli_schema["root_command"]["version"],
                "options": [],
                "commands": [],
            },
            "subcommands": []
        }
        
        # Convert options to Commander format
        for option in cli_schema["root_command"]["options"]:
            commander_option = {
                "flags": self._build_option_flags(option),
                "description": option["description"],
                "default": option.get("default"),
                "type": self._js_type_from_option(option),
            }
            commander_data["root_command"]["options"].append(commander_option)
        
        # Convert commands to Commander format  
        for command in cli_schema["root_command"]["subcommands"]:
            commander_cmd = {
                "name": command["name"],
                "description": command["description"],
                "arguments": [self._build_commander_argument(arg) for arg in command["arguments"]],
                "options": [self._build_commander_option(opt) for opt in command["options"]],
                "hook_name": command["hook_name"],
                "subcommands": command.get("subcommands", []),
            }
            commander_data["subcommands"].append(commander_cmd)
        
        return commander_data
    
    def _build_npm_dependencies(self, ir: Dict[str, Any]) -> Dict[str, str]:
        """
        Build NPM dependencies from IR.
        
        Args:
            ir: Intermediate representation
            
        Returns:
            Dictionary of NPM package dependencies
        """
        dependencies = {
            "commander": "^11.1.0",
            "chalk": "^5.3.0",
        }
        
        # Add enhanced interactive mode dependencies if interactive features are enabled
        if self._has_interactive_features(ir.get("cli", {})):
            dependencies.update({
                "chalk": "^5.3.0",  # Already included but ensure version
                # Built-in modules don't need explicit dependencies:
                # readline, fs, path, os, child_process
            })
        
        # Add NPM dependencies from IR
        npm_deps = ir["dependencies"].get("npm", [])
        for dep in npm_deps:
            if "@" in dep:
                name, version = dep.rsplit("@", 1)
                dependencies[name] = f"^{version}"
            else:
                dependencies[dep] = "latest"
        
        return dependencies
    
    def _build_imports(self, ir: Dict[str, Any]) -> List[str]:
        """
        Build ES module imports for the CLI.
        
        Args:
            ir: Intermediate representation
            
        Returns:
            List of import statements
        """
        imports = [
            "import { Command } from 'commander';",
            "import chalk from 'chalk';",
            "import path from 'path';",
            "import fs from 'fs';",
            "import { spawn, execSync } from 'child_process';",
        ]
        
        # Add enhanced interactive mode imports if interactive features are enabled
        if self._has_interactive_features(ir.get("cli", {})):
            imports.extend([
                "import readline from 'readline';",
                "import os from 'os';",
            ])
        
        # Add conditional imports based on available dependencies
        npm_deps = ir["dependencies"].get("npm", [])
        for dep in npm_deps:
            dep_name = dep.split("@")[0] if "@" in dep else dep
            if dep_name not in ["commander", "chalk"]:
                imports.append(f"import {self._to_js_variable_name(dep_name)} from '{dep_name}';")
        
        return imports
    
    def _build_hook_functions(self, cli_schema: Dict[str, Any]) -> List[Dict[str, str]]:
        """
        Build hook function definitions from CLI schema.
        
        Args:
            cli_schema: CLI schema from IR
            
        Returns:
            List of hook function definitions
        """
        hooks = []
        
        # Generate hooks for each command
        for command in cli_schema["root_command"]["subcommands"]:
            hook = {
                "name": command["hook_name"],
                "js_name": self._hook_name_filter(command["name"]),
                "command_name": command["name"],
                "description": command["description"],
                "arguments": command["arguments"],
                "options": command["options"],
            }
            hooks.append(hook)
            
            # Handle nested subcommands recursively
            if command.get("subcommands"):
                hooks.extend(self._build_subcommand_hooks(command["subcommands"], command["name"]))
        
        return hooks
    
    def _build_subcommand_hooks(self, subcommands: List[Dict[str, Any]], parent_name: str) -> List[Dict[str, str]]:
        """Recursively build hooks for subcommands."""
        hooks = []
        for subcmd in subcommands:
            hook = {
                "name": subcmd["hook_name"],
                "js_name": self._hook_name_filter(f"{parent_name}_{subcmd['name']}"),
                "command_name": subcmd["name"],
                "parent_command": parent_name,
                "description": subcmd["description"],
                "arguments": subcmd["arguments"],
                "options": subcmd["options"],
            }
            hooks.append(hook)
            
            # Recursively handle nested subcommands
            if subcmd.get("subcommands"):
                hooks.extend(self._build_subcommand_hooks(subcmd["subcommands"], f"{parent_name}_{subcmd['name']}"))
        
        return hooks
    
    def _build_option_flags(self, option: Dict[str, Any]) -> str:
        """Build Commander.js option flags string."""
        flags = []
        if option.get("short"):
            flags.append(f"-{option['short']}")
        flags.append(f"--{option['name']}")
        
        flag_str = ", ".join(flags)
        
        # Add value placeholder for non-flag options
        if option["type"] != "flag":
            flag_str += f" <{option['name']}>"
        
        return flag_str
    
    def _build_commander_argument(self, arg: Dict[str, Any]) -> Dict[str, str]:
        """Build Commander.js argument definition."""
        if arg["required"]:
            arg_pattern = f"<{arg['name']}>"
        else:
            arg_pattern = f"[{arg['name']}]"
            
        if arg.get("multiple"):
            arg_pattern = arg_pattern.replace(">", "...>").replace("]", "...]")
        
        return {
            "pattern": arg_pattern,
            "description": arg["description"],
            "name": arg["name"],
            "type": arg["type"],
        }
    
    def _build_commander_option(self, option: Dict[str, Any]) -> Dict[str, str]:
        """Build Commander.js option definition."""
        return {
            "flags": self._build_option_flags(option),
            "description": option["description"],
            "default": option.get("default"),
            "type": self._js_type_from_option(option),
            "name": option["name"],
        }
    
    def _post_process_javascript(self, content: str) -> str:
        """
        Post-process JavaScript code for better formatting.
        
        Args:
            content: Raw rendered JavaScript
            
        Returns:
            Formatted JavaScript code
        """
        # Remove extra blank lines
        content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)
        
        # Ensure proper spacing around functions
        content = re.sub(r'}\n([a-zA-Z])', r'}\n\n\1', content)
        
        # Fix import formatting
        content = re.sub(r'import\s+{([^}]+)}\s+from', r'import { \1 } from', content)
        
        return content.strip() + '\n'
    
    # Filter functions
    
    def _js_type_filter(self, type_str: str) -> str:
        """Convert generic type to JavaScript type."""
        type_mapping = {
            "str": "String",
            "string": "String", 
            "int": "Number",
            "integer": "Number",
            "float": "Number",
            "bool": "Boolean",
            "boolean": "Boolean",
            "flag": "Boolean",
            "list": "Array",
            "array": "Array",
        }
        return type_mapping.get(type_str.lower(), "String")
    
    def _camel_case_filter(self, name: str) -> str:
        """Convert name to camelCase."""
        if not name:
            return ""
        
        # Handle kebab-case and snake_case
        parts = re.split(r'[-_]', name)
        if len(parts) == 1:
            return name
        
        # First part stays lowercase, rest are capitalized
        return parts[0].lower() + ''.join(word.capitalize() for word in parts[1:])
    
    def _js_require_filter(self, module: str) -> str:
        """Generate ES module import statement."""
        return f"import {self._to_js_variable_name(module)} from '{module}';"
    
    def _commander_option_filter(self, option: Dict[str, Any]) -> str:
        """Generate Commander.js .option() call."""
        # Handle different option structures
        if "flags" in option:
            # Commander option object
            flags = option["flags"]
            description = option.get("description", "")
            default_val = option.get("default")
        else:
            # Direct option dict
            flags = self._build_option_flags(option)
            description = option["description"]
            default_val = option.get("default")
        
        option_call = f".option('{flags}', '{description}'"
        
        # Add default value if present
        if default_val is not None:
            if isinstance(default_val, str):
                option_call += f", '{default_val}'"
            elif isinstance(default_val, bool):
                option_call += f", {str(default_val).lower()}"
            else:
                option_call += f", {default_val}"
        
        option_call += ")"
        return option_call
    
    def _js_variable_filter(self, name: str) -> str:
        """Convert name to valid JavaScript variable name."""
        return self._to_js_variable_name(name)
    
    def _js_string_filter(self, value: str) -> str:
        """Escape string for JavaScript."""
        if not isinstance(value, str):
            return str(value)
        
        return value.replace("'", "\\'").replace('"', '\\"').replace('\n', '\\n')
    
    def _npm_package_name_filter(self, name: str) -> str:
        """Convert to valid NPM package name."""
        return self._to_js_package_name(name)
    
    def _hook_name_filter(self, command_name: str) -> str:
        """Generate hook function name from command name."""
        # Handle cases where "on_" is already present in hook name
        if command_name.startswith('on_'):
            # Remove the on_ prefix and convert to camelCase
            parts = command_name[3:].replace('-', '_').split('_')
            return 'on' + ''.join(word.capitalize() for word in parts)
        else:
            # Convert command-name to onCommandName
            parts = command_name.replace('-', '_').split('_')
            return 'on' + ''.join(word.capitalize() for word in parts)
    
    def _commander_argument_filter(self, arg: Dict[str, Any]) -> str:
        """Generate Commander.js .argument() call."""
        # Handle different argument structures
        if "required" in arg:
            # Direct argument dict
            pattern = self._build_commander_argument(arg)["pattern"]
            description = arg["description"]
        else:
            # Commander argument object
            pattern = arg.get("pattern", f"<{arg.get('name', 'arg')}>")
            description = arg.get("description", "")
        
        return f".argument('{pattern}', '{description}')"
    
    def _js_comment_filter(self, text: str) -> str:
        """Format text as JavaScript comment."""
        if not text:
            return ""
        
        lines = text.split('\n')
        if len(lines) == 1:
            return f"// {lines[0]}"
        else:
            comment_lines = ["/**"] + [f" * {line}" for line in lines] + [" */"]
            return '\n'.join(comment_lines)
    
    # Utility methods
    
    def _to_js_variable_name(self, name: str) -> str:
        """Convert to valid JavaScript variable name."""
        # Replace invalid characters
        js_name = re.sub(r'[^a-zA-Z0-9_$]', '_', name)
        
        # Ensure it starts with letter or underscore
        if js_name and js_name[0].isdigit():
            js_name = '_' + js_name
        
        return js_name or 'default'
    
    def _to_js_package_name(self, name: str) -> str:
        """Convert to valid NPM package name (lowercase, hyphens allowed)."""
        return re.sub(r'[^a-z0-9\-_]', '-', name.lower()).strip('-')
    
    def _js_type_from_option(self, option: Dict[str, Any]) -> str:
        """Determine JavaScript type from option definition."""
        opt_type = option.get("type", "string").lower()
        
        if opt_type in ["flag", "boolean", "bool"]:
            return "boolean"
        elif opt_type in ["int", "integer", "number", "float"]:
            return "number"
        elif opt_type in ["list", "array"]:
            return "array"
        else:
            return "string"
    
    def _has_interactive_features(self, cli_schema: Dict[str, Any]) -> bool:
        """Check if CLI has interactive mode features."""
        features = cli_schema.get("features", {})
        interactive_mode = features.get("interactive_mode", {})
        return interactive_mode.get("enabled", False)