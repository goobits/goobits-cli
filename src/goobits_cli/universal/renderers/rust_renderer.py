"""

Rust Renderer for Universal Template System



This renderer generates Rust CLI implementations using universal components

with proper type safety, structs, and Rust-specific conventions using clap.

"""

from typing import Dict, Any, List
from datetime import datetime
import re

try:
    from ... import __version__ as _version
except ImportError:
    _version = "3.0.0"  # Fallback version

import json

import jinja2

from datetime import datetime


from ..template_engine import LanguageRenderer


class RustRenderer(LanguageRenderer):
    """

    Rust-specific renderer for the Universal Template System.



    Generates Rust CLI implementations with:

    - Type safety through structs and Rust type system

    - clap framework integration with derive macros

    - Proper Rust naming conventions (snake_case for functions, PascalCase for types)

    - Cargo.toml configuration and proper module system

    - Error handling with Result types and anyhow/thiserror

    """

    def _get_version(self) -> str:
        """Get current version for generator metadata."""
        return _version

    def __init__(self):
        """Initialize the Rust renderer."""

        # Setup Jinja2 environment with custom filters

        self._env = jinja2.Environment(trim_blocks=True, lstrip_blocks=True)

        self._add_custom_filters()

    @property
    def language(self) -> str:
        """Return the language name."""

        return "rust"

    @property
    def file_extensions(self) -> Dict[str, str]:
        """Return mapping of component types to file extensions for Rust."""

        return {"rs": "rust", "toml": "toml", "md": "markdown", "logger": "rs"}

    def get_template_context(self, ir: Dict[str, Any]) -> Dict[str, Any]:
        """

        Transform IR into Rust-specific template context.



        Args:

            ir: Intermediate representation from UniversalTemplateEngine



        Returns:

            Rust-enhanced template context

        """

        # Start with base IR context and set language

        context = ir.copy()
        context["language"] = "rust"
        
        # Add clap structure (similar to commander_commands)
        context["clap_commands"] = self._build_clap_structure(
            ir.get("cli", {})
        )

        # Add Rust-specific transformations

        context["rust"] = {
            "structs": self._generate_structs(ir),
            "type_mappings": self._get_type_mappings(),
            "imports": self._generate_imports(ir),
            "dependencies": self._generate_dependencies(ir),
            "modules": self._generate_modules(ir),
        }

        # Transform CLI schema for Rust

        if "cli" in ir:

            context["cli"]["rust"] = self._transform_cli_schema(ir["cli"])

        # Add Cargo configuration

        context["cargo_config"] = self._generate_cargo_config(ir)

        # Convert names to Rust conventions

        context = self._apply_naming_conventions(context)

        # Add project dependencies in the format expected by the template
        rust_deps = ir.get("dependencies", {}).get("rust", [])
        if rust_deps:
            # Filter out dependencies that are already included in base template
            base_template_deps = {"serde", "serde_json", "serde_yaml", "clap", "anyhow", "thiserror"}
            filtered_deps = [dep for dep in rust_deps if dep not in base_template_deps]
            
            if filtered_deps:
                if "project" not in context:
                    context["project"] = {}
                if "dependencies" not in context["project"]:
                    context["project"]["dependencies"] = {}
                # Convert dependencies to the format expected by the template
                context["project"]["dependencies"]["required"] = [
                    {"name": dep, "version": "*"} for dep in filtered_deps
                ]

        # Add metadata

        context["metadata"] = {
            **{
                k: v
                for k, v in context.get("metadata", {}).items()
                if not isinstance(v, str) or not v.startswith("{{")
            },
            "timestamp": datetime.now().isoformat(),
            "generator_version": self._get_version(),
            "package_name": context["project"]
            .get("package_name", "cli")
            .replace("-", "_"),
            "command_name": context["project"].get("command_name", "cli"),
            "rust_edition": "2021",
        }

        # Add datetime module for template generation headers
        context["datetime"] = datetime

        return context

    def get_custom_filters(self) -> Dict[str, callable]:
        """Return Rust-specific Jinja2 filters."""

        return {
            "rust_type": self._rust_type_filter,
            "rust_struct": self._rust_struct_filter,
            "rust_import": self._rust_import_filter,
            "rust_clap_derive": self._rust_clap_derive_filter,
            "snake_case": self._snake_case_filter,
            "PascalCase": self._pascal_case_filter,
            "rust_safe_name": self._rust_safe_name_filter,
            "rust_optional": self._rust_optional_filter,
            "rust_vec_type": self._rust_vec_type_filter,
            "rust_function_signature": self._rust_function_signature_filter,
            "rust_string": self._rust_string_filter,
            "screaming_snake_case": self._screaming_snake_case_filter,
            "rust_escape": self._rust_escape_filter,
            "js_string": self._rust_string_filter,  # Reuse rust_string for JavaScript string formatting
        }

    def _add_custom_filters(self):
        """Add custom filters to the Jinja2 environment."""

        for name, filter_func in self.get_custom_filters().items():

            self._env.filters[name] = filter_func

    def get_output_structure(self, ir: Dict[str, Any]) -> Dict[str, str]:
        """

        Define the output file structure for Rust CLI.



        Args:

            ir: Intermediate representation



        Returns:

            Dictionary mapping component names to output file paths

        """

        ir.get("project", {}).get("package_name", "cli").replace("-", "_")

        cli_name = (
            ir.get("cli", {})
            .get("root_command", {})
            .get("name", "cli")
            .replace("-", "_")
        )

        # Generate 4 files: main.rs, hooks.rs, setup.sh, and Cargo.toml
        output = {
            "rust_cli_consolidated": "src/main.rs",  # Everything with inline modules
            "hooks_template": "src/hooks.rs",  # User hooks implementation
            "setup_script": "setup.sh",  # Smart setup with Cargo.toml merging
            "cargo_config": "Cargo.toml",  # Package manifest with dependencies
        }

        return output

    def render_component(
        self, component_name: str, template_content: str, context: Dict[str, Any]
    ) -> str:
        """

        Render a component template for Rust.



        Args:

            component_name: Name of the component

            template_content: Universal template content

            context: Rust-specific context



        Returns:

            Rendered Rust code

        """

        # Create Jinja2 environment with custom filters

        env = jinja2.Environment(
            loader=jinja2.BaseLoader(), trim_blocks=True, lstrip_blocks=True
        )

        # Add custom filters

        env.filters.update(self.get_custom_filters())

        # Render the template

        template = env.from_string(template_content)

        rendered_content = template.render(**context)

        # Post-process the rendered content

        return self._post_process_rust_code(rendered_content)

    def _generate_structs(self, ir: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate Rust structs from IR."""

        structs = []

        # Generate CLI args struct

        if "cli" in ir and "commands" in ir["cli"]:

            for cmd_name, cmd_data in ir["cli"]["commands"].items():

                struct_name = self._pascal_case_filter(f"{cmd_name}_args")

                fields = []

                # Add arguments as fields

                if "args" in cmd_data:

                    for arg in cmd_data["args"]:

                        field_type = self._rust_type_filter(arg.get("type", "String"))

                        if not arg.get("required", True):

                            field_type = f"Option<{field_type}>"

                        fields.append(
                            {
                                "name": self._snake_case_filter(arg["name"]),
                                "type": field_type,
                                "doc": arg.get("desc", ""),
                            }
                        )

                # Add options as fields

                if "options" in cmd_data:

                    for opt in cmd_data["options"]:

                        field_type = self._rust_type_filter(opt.get("type", "String"))

                        if opt.get("type") == "flag":

                            field_type = "bool"

                        elif not opt.get("required", False):

                            field_type = f"Option<{field_type}>"

                        fields.append(
                            {
                                "name": self._snake_case_filter(opt["name"]),
                                "type": field_type,
                                "doc": opt.get("desc", ""),
                            }
                        )

                structs.append(
                    {
                        "name": struct_name,
                        "fields": fields,
                        "derives": ["Debug", "Clone"],
                    }
                )

        return structs

    def _get_type_mappings(self) -> Dict[str, str]:
        """Get Rust type mappings."""

        return {
            "str": "String",
            "string": "String",
            "int": "i32",
            "integer": "i32",
            "float": "f64",
            "bool": "bool",
            "boolean": "bool",
            "flag": "bool",
            "list": "Vec<String>",
            "array": "Vec<String>",
            "dict": "std::collections::HashMap<String, String>",
            "object": "std::collections::HashMap<String, String>",
        }

    def _generate_imports(self, ir: Dict[str, Any]) -> List[str]:
        """Generate necessary imports for Rust code."""

        imports = [
            "use clap::{Arg, ArgMatches, Command, Parser};",
            "use std::collections::HashMap;",
            "use anyhow::{Result, anyhow};",
            "use serde::{Deserialize, Serialize};",
        ]

        # Add additional imports based on CLI features

        if "cli" in ir:

            cli_data = ir["cli"]

            # Check if we need async features

            if self._needs_async_features(cli_data):

                imports.append("use tokio;")

            # Check if we need file I/O

            if self._needs_file_io(cli_data):

                imports.extend(["use std::fs;", "use std::path::Path;"])

        return imports

    def _generate_dependencies(self, ir: Dict[str, Any]) -> Dict[str, str]:
        """Generate Cargo dependencies."""

        deps = {
            "clap": '{ version = "4.0", features = ["derive"] }',
            "serde": '{ version = "1.0", features = ["derive"] }',
            "serde_json": '"1.0"',
            "anyhow": '"1.0"',
            "thiserror": '"1.0"',
        }

        # Add dependencies from IR (from installation.extras.cargo)
        ir_dependencies = ir.get("dependencies", {})
        rust_deps = ir_dependencies.get("rust", [])
        # Dependencies that are already included in the base template
        base_template_deps = {"serde", "serde_json", "serde_yaml", "clap", "anyhow", "thiserror"}
        for dep_name in rust_deps:
            if dep_name not in deps and dep_name not in base_template_deps:  # Don't override existing or base deps
                deps[dep_name] = '"*"'  # Default to latest version

        # Add conditional dependencies

        if "cli" in ir:

            cli_data = ir["cli"]

            if self._needs_async_features(cli_data):

                deps["tokio"] = '{ version = "1.0", features = ["full"] }'

        return deps

    def _generate_modules(self, ir: Dict[str, Any]) -> List[str]:
        """Generate module declarations."""

        modules = ["mod hooks;"]

        # Add conditional modules based on features

        if "cli" in ir:

            cli_data = ir["cli"]

            if self._has_config_features(cli_data):

                modules.append("mod config;")

            if self._has_completion_features(cli_data):

                modules.append("mod completion;")

        return modules

    def _transform_cli_schema(self, cli_data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform CLI schema for Rust-specific needs."""

        rust_cli = {}

        if "commands" in cli_data:

            rust_cli["commands"] = {}

            for cmd_name, cmd_data in cli_data["commands"].items():

                rust_cmd = cmd_data.copy()

                rust_cmd["struct_name"] = self._pascal_case_filter(f"{cmd_name}_args")

                rust_cmd["function_name"] = self._snake_case_filter(
                    f"handle_{cmd_name}"
                )

                rust_cli["commands"][cmd_name] = rust_cmd

        return rust_cli

    def _generate_cargo_config(self, ir: Dict[str, Any]) -> Dict[str, Any]:
        """Generate Cargo.toml configuration."""

        package_name = ir.get("package_name", "my-cli").replace("-", "_")

        config = {
            "package": {
                "name": package_name,
                "version": ir.get("version", "0.1.0"),
                "description": ir.get("description", "A CLI tool"),
                "edition": "2021",
            },
            "dependencies": self._generate_dependencies(ir),
            "bin": [
                {"name": ir.get("command_name", package_name), "path": "src/main.rs"}
            ],
        }

        return config

    def _apply_naming_conventions(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Apply Rust naming conventions to context."""

        # Convert package names

        if "package_name" in context:

            context["rust_package_name"] = self._snake_case_filter(
                context["package_name"]
            )

        if "command_name" in context:

            context["rust_command_name"] = self._snake_case_filter(
                context["command_name"]
            )

        # Convert CLI commands

        if "cli" in context and "commands" in context["cli"]:

            for cmd_name, cmd_data in context["cli"]["commands"].items():

                cmd_data["rust_name"] = self._snake_case_filter(cmd_name)

                cmd_data["rust_struct"] = self._pascal_case_filter(f"{cmd_name}_args")

        return context

    def _post_process_rust_code(self, code: str) -> str:
        """Post-process generated Rust code."""

        # Remove excessive blank lines

        code = re.sub(r"\n\s*\n\s*\n", "\n\n", code)

        # Ensure proper spacing around use statements

        code = re.sub(r"(use [^;]+;)\n([^u\n])", r"\1\n\n\2", code)

        # Format function signatures properly

        code = re.sub(r"\)\s*->\s*([^{]+)\s*{", r") -> \1 {", code)

        return code.strip()

    # Filter functions

    def _rust_type_filter(self, python_type: str) -> str:
        """Convert Python/generic types to Rust types."""

        type_map = self._get_type_mappings()

        return type_map.get(python_type.lower(), "String")

    def _rust_struct_filter(self, name: str) -> str:
        """Convert name to Rust struct naming convention."""

        return self._pascal_case_filter(name)

    def _rust_import_filter(self, module: str) -> str:
        """Format Rust import statement."""

        return f"use {module};"

    def _rust_clap_derive_filter(self, derives: List[str]) -> str:
        """Format clap derive macro."""

        all_derives = ["Parser"] + derives

        return f"#[derive({', '.join(all_derives)})]"

    def _snake_case_filter(self, text: str) -> str:
        """Convert text to snake_case."""

        if not text:

            return text

        # Replace hyphens and spaces with underscores, then convert to lowercase

        text = re.sub(r"[-\s]+", "_", text)

        # Insert underscores before uppercase letters (camelCase -> snake_case)

        text = re.sub(r"([a-z])([A-Z])", r"\1_\2", text)

        return text.lower()

    def _pascal_case_filter(self, text: str) -> str:
        """Convert text to PascalCase."""

        if not text:

            return text

        # Split by various separators and capitalize each word

        words = re.split(r"[-_\s]+", text)

        return "".join(word.capitalize() for word in words if word)

    def _screaming_snake_case_filter(self, text: str) -> str:
        """Convert text to SCREAMING_SNAKE_CASE."""

        return self._snake_case_filter(text).upper()

    def _rust_safe_name_filter(self, name: str) -> str:
        """Convert name to safe Rust identifier."""

        # Rust keywords that need to be escaped

        rust_keywords = {
            "as",
            "break",
            "const",
            "continue",
            "crate",
            "else",
            "enum",
            "extern",
            "false",
            "fn",
            "for",
            "if",
            "impl",
            "in",
            "let",
            "loop",
            "match",
            "mod",
            "move",
            "mut",
            "pub",
            "ref",
            "return",
            "self",
            "Self",
            "static",
            "struct",
            "super",
            "trait",
            "true",
            "type",
            "unsafe",
            "use",
            "where",
            "while",
            "async",
            "await",
            "dyn",
        }

        safe_name = self._snake_case_filter(name)

        if safe_name in rust_keywords:

            return f"r#{safe_name}"

        return safe_name
    
    def _build_clap_structure(self, cli_schema: Dict[str, Any]) -> Dict[str, Any]:
        """Build Clap-specific command structure for Rust."""
        root_command = cli_schema.get("root_command", {})
        
        clap_data = {
            "root_command": {
                "name": root_command.get("name", "cli"),
                "description": root_command.get("description", "CLI application"),
                "version": root_command.get("version", self._get_version()),
                "options": [],
                "commands": [],
            },
            "subcommands": [],
        }
        
        # Convert commands to Clap format
        for command in root_command.get("subcommands", []):
            clap_cmd = {
                "name": command.get("name", "command"),
                "description": command.get("description", ""),
                "arguments": command.get("arguments", []),
                "options": command.get("options", []),
                "hook_name": command.get(
                    "hook_name", f"on_{command.get('name', 'command')}"
                ),
                "subcommands": command.get("subcommands", []),
            }
            clap_data["subcommands"].append(clap_cmd)
        
        return clap_data

    def _rust_optional_filter(self, rust_type: str) -> str:
        """Wrap Rust type in Option if needed."""

        return f"Option<{rust_type}>"

    def _rust_vec_type_filter(self, item_type: str) -> str:
        """Create Vec type with specified item type."""

        return f"Vec<{item_type}>"

    def _rust_function_signature_filter(
        self, name: str, args: List[Dict], return_type: str = "Result<()>"
    ) -> str:
        """Generate Rust function signature."""

        safe_name = self._rust_safe_name_filter(name)

        arg_list = ", ".join(f"{arg['name']}: {arg['type']}" for arg in args)

        return f"pub fn {safe_name}({arg_list}) -> {return_type}"

    def _rust_string_filter(self, text: str) -> str:
        """Format string for Rust string literal."""

        return json.dumps(text)  # JSON escaping works for Rust strings too

    def _rust_escape_filter(self, text: str) -> str:
        """Escape text for Rust string literal."""

        return (
            text.replace("\\", "\\\\")
            .replace('"', '\\"')
            .replace("\n", "\\n")
            .replace("\t", "\\t")
        )

    # Helper methods

    def _needs_async_features(self, cli_data: Dict[str, Any]) -> bool:
        """Check if CLI needs async features."""

        # For now, assume all CLIs might benefit from async

        return True

    def _needs_file_io(self, cli_data: Dict[str, Any]) -> bool:
        """Check if CLI needs file I/O capabilities."""

        # Check for file-related commands or options

        if "commands" in cli_data:

            for cmd_data in cli_data["commands"].values():

                if "args" in cmd_data:

                    for arg in cmd_data["args"]:

                        if "file" in arg.get("name", "").lower():

                            return True

                if "options" in cmd_data:

                    for opt in cmd_data["options"]:

                        if "file" in opt.get("name", "").lower():

                            return True

        return False

    def _has_config_features(self, cli_data: Dict[str, Any]) -> bool:
        """Check if CLI has configuration features."""

        # Look for config-related commands or global config

        return "config" in str(cli_data).lower()

    def _has_completion_features(self, cli_data: Dict[str, Any]) -> bool:
        """Check if CLI has shell completion features."""

        # Look for completion-related features

        features = cli_data.get("features", {})

        return features.get("completion", {}).get("enabled", False)

    def _has_interactive_features(self, cli_schema: Dict[str, Any]) -> bool:
        """Check if CLI has interactive mode features."""

        features = cli_schema.get("features", {})

        interactive_mode = features.get("interactive_mode", {})

        return interactive_mode.get("enabled", False)
