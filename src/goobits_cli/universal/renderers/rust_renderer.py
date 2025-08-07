"""
RustRenderer for Universal Template System

This module provides Rust-specific rendering capabilities for the Universal Template System,
generating Rust CLIs with Clap framework integration, proper Result types, and Rust
naming conventions.
"""

import re
from pathlib import Path
from typing import Dict, Any, List, Callable
import jinja2

from ..template_engine import LanguageRenderer


class RustRenderer(LanguageRenderer):
    """
    Rust-specific renderer for the Universal Template System.
    
    Generates Rust CLIs using the Clap framework with derive macros,
    proper error handling with Result types, and Rust naming conventions.
    """
    
    @property
    def language(self) -> str:
        """Return the language identifier"""
        return "rust"
    
    @property
    def file_extensions(self) -> Dict[str, str]:
        """Return mapping of component types to file extensions"""
        return {
            "rs": "rust",
            "toml": "toml",
        }
    
    def get_template_context(self, ir: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform intermediate representation into Rust-specific template context.
        
        Args:
            ir: Intermediate representation from UniversalTemplateEngine
            
        Returns:
            Rust-specific template context with type conversions and imports
        """
        context = ir.copy()
        
        # Add Rust-specific project information
        context["rust"] = {
            "crate_name": self._to_snake_case(ir["project"]["package_name"]),
            "struct_name": self._to_pascal_case(ir["project"]["command_name"]),
            "imports": self._get_rust_imports(ir),
            "dependencies": self._get_rust_dependencies(ir),
        }
        
        # Transform CLI schema with Rust types
        if "cli" in context:
            context["cli"] = self._transform_cli_schema(ir["cli"])
        
        # Add Rust-specific metadata
        if "metadata" not in context:
            context["metadata"] = {}
        context["metadata"]["language"] = "rust"
        context["metadata"]["framework"] = "clap"
        context["metadata"]["error_handling"] = "Result<T, E>"
        
        return context
    
    def get_custom_filters(self) -> Dict[str, Callable]:
        """
        Return custom Jinja2 filters for Rust code generation.
        
        Returns:
            Dictionary mapping filter names to filter functions
        """
        return {
            "rust_type": self._rust_type,
            "rust_struct_name": self._to_pascal_case,
            "rust_function_name": self._to_snake_case,
            "rust_field_name": self._to_snake_case,
            "rust_const_name": self._to_screaming_snake_case,
            "clap_attribute": self._clap_attribute,
            "rust_default": self._rust_default,
            "escape_rust_string": self._escape_rust_string,
            "rust_doc_comment": self._rust_doc_comment,
        }
    
    def render_component(self, component_name: str, template_content: str, 
                        context: Dict[str, Any]) -> str:
        """
        Render a component template with Rust-specific context and filters.
        
        Args:
            component_name: Name of the component being rendered
            template_content: Universal template content
            context: Rust-specific template context
            
        Returns:
            Rendered Rust code
        """
        # Create Jinja environment with Rust filters
        env = jinja2.Environment(
            loader=jinja2.DictLoader({component_name: template_content}),
            trim_blocks=True,
            lstrip_blocks=True,
            undefined=jinja2.StrictUndefined
        )
        
        # Add custom filters
        for filter_name, filter_func in self.get_custom_filters().items():
            env.filters[filter_name] = filter_func
        
        # Render the template
        template = env.get_template(component_name)
        rendered_content = template.render(**context)
        
        # Post-process the rendered content
        return self._post_process_rust_code(rendered_content)
    
    def get_output_structure(self, ir: Dict[str, Any]) -> Dict[str, str]:
        """
        Define the output file structure for Rust CLIs.
        
        Args:
            ir: Intermediate representation
            
        Returns:
            Dictionary mapping component names to output file paths
        """
        cli_name = ir.get("cli", {}).get("root_command", {}).get("name", "cli").replace("-", "_")
        
        output = {
            # Core Rust files
            "command_handler": "src/main.rs",
            "config_manager": "src/config.rs", 
            "error_handler": "src/errors.rs",
            "hook_system": "src/hooks.rs",
            "completion_engine": "src/completion_engine.rs",
            
            # Additional modules
            "commands": "src/commands.rs",
            "utils": "src/utils.rs",
            "lib": "src/lib.rs",
            
            # Build configuration
            "cargo_manifest": "Cargo.toml",
            
            # Installation script
            "setup_script": "setup.sh",
        }
        
        # Add interactive mode if enabled
        if self._has_interactive_features(ir.get("cli", {})):
            output["interactive_mode"] = f"src/{cli_name}_interactive.rs"
        
        return output
    
    def _transform_cli_schema(self, cli_schema: Dict[str, Any]) -> Dict[str, Any]:
        """Transform CLI schema with Rust-specific type information"""
        transformed = cli_schema.copy()
        
        # Transform root command
        if "root_command" in transformed:
            transformed["root_command"] = self._transform_command(transformed["root_command"])
        
        # Transform individual commands
        if "commands" in transformed:
            transformed_commands = {}
            for cmd_name, cmd_data in transformed["commands"].items():
                transformed_commands[cmd_name] = self._transform_command(cmd_data)
            transformed["commands"] = transformed_commands
        
        return transformed
    
    def _transform_command(self, command: Dict[str, Any]) -> Dict[str, Any]:
        """Transform a single command with Rust type information"""
        transformed = command.copy()
        
        # Transform arguments
        if "arguments" in transformed:
            transformed_args = []
            for arg in transformed["arguments"]:
                transformed_arg = arg.copy()
                transformed_arg["rust_type"] = self._rust_type(arg["type"])
                transformed_arg["rust_name"] = self._to_snake_case(arg["name"])
                transformed_args.append(transformed_arg)
            transformed["arguments"] = transformed_args
        
        # Transform options
        if "options" in transformed:
            transformed_options = []
            for opt in transformed["options"]:
                transformed_opt = opt.copy()
                transformed_opt["rust_type"] = self._rust_type(opt["type"])
                transformed_opt["rust_name"] = self._to_snake_case(opt["name"])
                transformed_opt["clap_attributes"] = self._generate_clap_attributes(opt)
                transformed_options.append(transformed_opt)
            transformed["options"] = transformed_options
        
        # Transform subcommands recursively
        if "subcommands" in transformed:
            transformed_subcommands = []
            for subcmd in transformed["subcommands"]:
                transformed_subcommands.append(self._transform_command(subcmd))
            transformed["subcommands"] = transformed_subcommands
        
        # Add Rust-specific naming
        transformed["rust_name"] = self._to_pascal_case(transformed["name"])
        transformed["rust_function"] = self._to_snake_case(transformed["name"])
        
        return transformed
    
    def _get_rust_imports(self, ir: Dict[str, Any]) -> List[str]:
        """Generate standard Rust imports for CLI applications"""
        imports = [
            "use anyhow::{Context, Result};",
            "use clap::{Parser, Subcommand, CommandFactory};",
            "use std::collections::HashMap;",
            "use std::process;",
            "use serde::{Deserialize, Serialize};",
        ]
        
        # Add conditional imports based on features
        if self._has_config_features(ir):
            imports.extend([
                "use serde_yaml;",
                "use serde_json;", 
                "use dirs;",
            ])
        
        if self._has_async_features(ir):
            imports.extend([
                "use tokio;",
                "use futures;",
            ])
        
        return imports
    
    def _get_rust_dependencies(self, ir: Dict[str, Any]) -> Dict[str, str]:
        """Generate Cargo.toml dependencies for the CLI"""
        deps = {
            "anyhow": "1.0",
            "clap": { "version": "4.0", "features": ["derive"] },
            "serde": { "version": "1.0", "features": ["derive"] },
            "serde_yaml": "0.9",
            "serde_json": "1.0",
            "dirs": "5.0",
        }
        
        # Add optional dependencies based on IR features
        if self._has_async_features(ir):
            deps.update({
                "tokio": { "version": "1.0", "features": ["full"] },
                "futures": "0.3",
            })
        
        if self._has_progress_features(ir):
            deps["indicatif"] = "0.17"
        
        if self._has_color_features(ir):
            deps["colored"] = "2.0"
        
        # Add dependencies from IR
        if "dependencies" in ir and "rust" in ir["dependencies"]:
            for dep in ir["dependencies"]["rust"]:
                if isinstance(dep, str):
                    deps[dep] = "*"
                elif isinstance(dep, dict):
                    deps.update(dep)
        
        return deps
    
    def _has_config_features(self, ir: Dict[str, Any]) -> bool:
        """Check if CLI needs configuration management features"""
        return True  # Most CLIs need config management
    
    def _has_async_features(self, ir: Dict[str, Any]) -> bool:
        """Check if CLI needs async features"""
        # Check if any commands suggest async operations
        cli = ir.get("cli", {})
        commands = cli.get("commands", {})
        
        for cmd_data in commands.values():
            if "async" in cmd_data.get("description", "").lower():
                return True
        
        return False
    
    def _has_progress_features(self, ir: Dict[str, Any]) -> bool:
        """Check if CLI needs progress bar features"""
        return True  # Most CLIs benefit from progress indicators
    
    def _has_color_features(self, ir: Dict[str, Any]) -> bool:
        """Check if CLI needs colored output features"""  
        return True  # Most CLIs benefit from colored output
    
    def _rust_type(self, generic_type: str) -> str:
        """Convert generic types to Rust types"""
        type_mapping = {
            "string": "String",
            "str": "String", 
            "int": "i32",
            "integer": "i32",
            "i32": "i32",
            "i64": "i64", 
            "float": "f64",
            "f64": "f64",
            "bool": "bool",
            "boolean": "bool",
            "flag": "bool",
            "path": "std::path::PathBuf",
            "file": "std::path::PathBuf",
            "dir": "std::path::PathBuf",
            "directory": "std::path::PathBuf",
            "url": "String",  # Could be url::Url with url crate
            "email": "String",
            "json": "serde_json::Value",
            "yaml": "serde_yaml::Value",
        }
        
        return type_mapping.get(generic_type.lower(), "String")
    
    def _to_snake_case(self, name: str) -> str:
        """Convert name to snake_case for Rust functions and variables"""
        # Handle kebab-case
        name = name.replace('-', '_')
        
        # Convert camelCase/PascalCase to snake_case
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
    
    def _to_pascal_case(self, name: str) -> str:
        """Convert name to PascalCase for Rust structs and enums"""
        # First convert camelCase to separate words
        s1 = re.sub('([a-z0-9])([A-Z])', r'\1_\2', name)
        # Split on common separators
        parts = re.split(r'[-_\s]+', s1)
        return ''.join(word.capitalize() for word in parts if word)
    
    def _to_screaming_snake_case(self, name: str) -> str:
        """Convert name to SCREAMING_SNAKE_CASE for Rust constants"""
        return self._to_snake_case(name).upper()
    
    def _clap_attribute(self, option: Dict[str, Any]) -> str:
        """Generate Clap #[arg(...)] attributes for options"""
        attrs = []
        
        # Long form
        attrs.append(f'long = "{option["name"]}"')
        
        # Short form if available
        if "short" in option and option["short"]:
            attrs.append(f'short = \'{option["short"]}\'')
        
        # Help text 
        if "description" in option:
            attrs.append(f'help = "{self._escape_rust_string(option["description"])}"')
        
        # Default value
        if "default" in option and option["default"] is not None:
            default_val = self._rust_default(option["default"], option["type"])
            if option["type"] in ["bool", "flag"]:
                attrs.append(f'default_value_t = {default_val}')
            else:
                attrs.append(f'default_value = "{option["default"]}"')
        
        # Value parser for choices
        if "choices" in option and option["choices"]:
            choices = ', '.join(f'"{choice}"' for choice in option["choices"])
            attrs.append(f'value_parser = clap::builder::PossibleValuesParser::new([{choices}])')
        
        return f'#[arg({", ".join(attrs)})]'
    
    def _generate_clap_attributes(self, option: Dict[str, Any]) -> List[str]:
        """Generate all Clap attributes for an option"""
        return [self._clap_attribute(option)]
    
    def _rust_default(self, value: Any, value_type: str) -> str:
        """Convert default value to Rust representation"""
        if value_type in ["bool", "flag", "boolean"]:
            return "true" if value else "false"
        elif value_type in ["int", "integer", "i32", "i64"]:
            return str(value)
        elif value_type in ["float", "f64"]:
            return str(float(value))
        else:
            return f'"{self._escape_rust_string(str(value))}"'
    
    def _escape_rust_string(self, text: str) -> str:
        """Escape string for use in Rust string literals"""
        return (text
                .replace('\\', '\\\\')
                .replace('"', '\\"')
                .replace('\n', '\\n')
                .replace('\r', '\\r')
                .replace('\t', '\\t'))
    
    def _rust_doc_comment(self, text: str) -> str:
        """Format text as Rust documentation comment"""
        lines = text.split('\n')
        return '\n'.join(f'/// {line}' for line in lines)
    
    def _post_process_rust_code(self, content: str) -> str:
        """Post-process generated Rust code for formatting and cleanup"""
        lines = content.split('\n')
        processed_lines = []
        
        for line in lines:
            # Remove trailing whitespace
            line = line.rstrip()
            
            # Skip completely empty lines at start/end
            if not processed_lines and not line.strip():
                continue
                
            processed_lines.append(line)
        
        # Remove trailing empty lines
        while processed_lines and not processed_lines[-1].strip():
            processed_lines.pop()
        
        return '\n'.join(processed_lines) + '\n' if processed_lines else ''
    
    def _has_interactive_features(self, cli_schema: Dict[str, Any]) -> bool:
        """Check if CLI has interactive mode features."""
        features = cli_schema.get("features", {})
        interactive_mode = features.get("interactive_mode", {})
        return interactive_mode.get("enabled", False)