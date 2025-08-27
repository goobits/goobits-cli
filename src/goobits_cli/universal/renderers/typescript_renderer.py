"""

TypeScript Renderer for Universal Template System



This renderer generates TypeScript CLI implementations using universal components

with proper type safety, interfaces, and TypeScript-specific conventions.

"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import re

# Lazy import for version to avoid early import overhead
_version = None


def _get_version():
    global _version
    if _version is None:
        try:
            from ... import __version__ as v

            _version = v
        except ImportError:
            _version = "3.0.0"
    return _version


# Lazy import Jinja2 to avoid startup overhead
_jinja2 = None


def _get_jinja2():
    global _jinja2
    if _jinja2 is None:
        import jinja2 as j2

        _jinja2 = j2
    return _jinja2


from ..template_engine import LanguageRenderer


class TypeScriptRenderer(LanguageRenderer):
    """

    TypeScript-specific renderer for the Universal Template System.



    Generates TypeScript CLI implementations with:

    - Type safety through interfaces and TypeScript types

    - Commander.js framework integration with typed options

    - Proper TypeScript naming conventions (PascalCase/camelCase)

    - TypeScript-specific imports and module system

    - Build configuration for TypeScript compilation

    """

    def _get_version(self) -> str:
        """Get current version for generator metadata."""
        return _get_version()

    def __init__(self):
        """Initialize the TypeScript renderer."""

        # Setup Jinja2 environment with custom filters and Unicode support
        jinja2 = _get_jinja2()
        self._env = jinja2.Environment(
            trim_blocks=True,
            lstrip_blocks=True,
            autoescape=False,
            # Enable optimized Unicode handling
            finalize=lambda x: x if x is not None else "",
        )

        self._add_custom_filters()

    @property
    def language(self) -> str:
        """Return the language name."""

        return "typescript"

    @property
    def file_extensions(self) -> Dict[str, str]:
        """Return mapping of component types to file extensions for TypeScript."""

        return {
            "ts": "typescript",
            "d.ts": "declaration",
            "js": "javascript",  # For config files
            "json": "json",
            "logger": "ts",
        }

    def get_template_context(self, ir: Dict[str, Any]) -> Dict[str, Any]:
        """

        Transform IR into TypeScript-specific template context.



        Args:

            ir: Intermediate representation from UniversalTemplateEngine



        Returns:

            TypeScript-enhanced template context

        """

        # Start with base IR context and set language

        context = ir.copy()
        context["language"] = "typescript"
        
        # Add commander.js structure (same as Node.js)
        context["commander_commands"] = self._build_commander_structure(
            ir.get("cli", {})
        )

        # Add TypeScript-specific transformations

        context["typescript"] = {
            "interfaces": self._generate_interfaces(ir),
            "type_mappings": self._get_type_mappings(),
            "imports": self._generate_imports(ir),
            "exports": self._generate_exports(ir),
            "main_entry": "index.ts",
            "bin_entry": "bin/index.js",
            "package_config": {
                "dependencies": {},  # Dependencies are handled in package_config.j2 template
                "devDependencies": {
                    "typescript": "^5.0.0",
                    "@types/node": "^18.0.0",
                    "ts-node": "^10.0.0",
                },
            },
        }

        # Transform CLI schema for TypeScript

        if "cli" in ir:

            context["cli"]["typescript"] = self._transform_cli_schema(ir["cli"])

        # Add TypeScript build configuration

        context["build_config"] = self._generate_build_config(ir)

        # Convert names to TypeScript conventions

        context = self._apply_naming_conventions(context)

        # Add TypeScript-specific metadata with defensive defaults

        context["metadata"] = {
            **{
                k: v
                for k, v in context.get("metadata", {}).items()
                if not isinstance(v, str) or not v.startswith("{{")
            },
            "timestamp": datetime.now().isoformat(),
            "generator_version": self._get_version(),
            "package_name": context["project"].get("package_name", "cli"),
            "command_name": context["project"].get("command_name", "cli"),
        }

        # Add datetime module for template generation headers
        context["datetime"] = datetime

        return context

    def get_custom_filters(self) -> Dict[str, callable]:
        """Return TypeScript-specific Jinja2 filters."""

        return {
            "ts_type": self._ts_type_filter,
            "ts_interface": self._ts_interface_filter,
            "ts_import": self._ts_import_filter,
            "ts_commander_option": self._ts_commander_option_filter,
            "camelCase": self._camel_case_filter,
            "PascalCase": self._pascal_case_filter,
            "pascal_case": self._pascal_case_filter,
            "ts_safe_name": self._ts_safe_name_filter,
            "ts_optional": self._ts_optional_filter,
            "ts_array_type": self._ts_array_type_filter,
            "ts_function_signature": self._ts_function_signature_filter,
            "js_string": self._js_string_filter,
        }

    def render_component(
        self, component_name: str, template_content: str, context: Dict[str, Any]
    ) -> str:
        """

        Render a component template for TypeScript.



        Args:

            component_name: Name of the component

            template_content: Universal template content

            context: TypeScript-specific template context



        Returns:

            Rendered TypeScript code

        """

        # Create template from content

        template = self._env.from_string(template_content)

        # Add component-specific context

        render_context = context.copy()

        render_context["component_name"] = component_name

        # Apply TypeScript-specific processing based on component type

        if component_name == "command_handler":

            render_context = self._enhance_command_context(render_context)

        elif component_name == "config_manager":

            render_context = self._enhance_config_context(render_context)

        elif component_name == "completion_engine":

            render_context = self._enhance_completion_context(render_context)

        return template.render(**render_context)

    def get_output_structure(self, ir: Dict[str, Any]) -> Dict[str, str]:
        """

        Define the output file structure for TypeScript CLIs.



        Args:

            ir: Intermediate representation



        Returns:

            Mapping of component names to output file paths

        """

        # Use user-defined paths if specified, otherwise use defaults
        cli_path = ir["project"].get("cli_path") or "cli.ts"
        hooks_path = ir["project"].get("cli_hooks_path") or "cli_hooks.ts"
        types_path = ir["project"].get("cli_types_path") or "cli_types.d.ts"

        # TypeScript generates 4 files (cli, hooks, types, setup.sh)
        output = {
            "typescript_cli_consolidated": cli_path,  # TypeScript with everything embedded
            "hooks_template": hooks_path,  # RENAMED from src/hooks.ts to cli_hooks.ts
            "typescript_types": types_path,  # RENAMED from types.d.ts to cli_types.d.ts
            "setup_script": "setup.sh",  # Smart setup with package.json/tsconfig merging
        }

        return output

    def _add_custom_filters(self) -> None:
        """Add TypeScript-specific filters to Jinja2 environment."""

        for name, filter_func in self.get_custom_filters().items():

            self._env.filters[name] = filter_func

    def _generate_interfaces(self, ir: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate TypeScript interfaces from CLI schema."""

        interfaces = []

        # Generate global options interface

        if "cli" in ir and "global_options" in ir["cli"]:

            interfaces.append(
                {
                    "name": "GlobalOptions",
                    "properties": self._extract_properties_from_options(
                        ir["cli"]["global_options"]
                    ),
                }
            )

        # Generate command interfaces from root_command subcommands

        if (
            "cli" in ir
            and "root_command" in ir["cli"]
            and "subcommands" in ir["cli"]["root_command"]
        ):

            for command in ir["cli"]["root_command"]["subcommands"]:

                cmd_name = command.get("name", "Command")

                interface_name = f"{self._pascal_case_filter(cmd_name)}Options"

                properties = {}

                # Add options as properties

                for option in command.get("options", []):

                    prop_name = option.get("name", "option")

                    prop_type = self._ts_type_filter(option.get("type", "string"))

                    is_required = option.get("required", False)

                    properties[prop_name] = {
                        "type": prop_type,
                        "required": is_required,
                        "optional": not is_required,  # Add optional field for template compatibility
                    }

                interfaces.append({"name": interface_name, "properties": properties})

        # Generate common interfaces

        interfaces.extend(
            [
                {
                    "name": "CommandArgs",
                    "properties": {
                        "commandName": {
                            "type": "string",
                            "required": True,
                            "optional": False,
                        },
                        "[key: string]": {
                            "type": "any",
                            "required": False,
                            "optional": True,
                        },
                    },
                },
                {
                    "name": "HookFunction",
                    "properties": {
                        "(args: CommandArgs)": {
                            "type": "Promise<any> | any",
                            "required": True,
                            "optional": False,
                        }
                    },
                },
            ]
        )

        return interfaces

    def _extract_properties_from_options(
        self, options: List[Dict[str, Any]]
    ) -> Dict[str, Dict[str, Any]]:
        """Extract properties from options list for interface generation."""

        properties = {}

        for option in options:

            prop_name = option.get("name", "option")

            prop_type = self._ts_type_filter(option.get("type", "string"))

            is_required = option.get("required", False)

            properties[prop_name] = {
                "type": prop_type,
                "required": is_required,
                "optional": not is_required,  # Add optional field for template compatibility
            }

        return properties

    def _get_type_mappings(self) -> Dict[str, str]:
        """Get mapping from generic types to TypeScript types."""

        return {
            "str": "string",
            "string": "string",
            "int": "number",
            "integer": "number",
            "float": "number",
            "number": "number",
            "bool": "boolean",
            "boolean": "boolean",
            "flag": "boolean",
            "list": "any[]",
            "array": "any[]",
            "dict": "Record<string, any>",
            "object": "Record<string, any>",
            "any": "any",
            "void": "void",
            "null": "null",
            "undefined": "undefined",
        }

    def _generate_imports(self, ir: Dict[str, Any]) -> List[str]:
        """Generate TypeScript import statements."""

        imports = [
            "import { Command } from 'commander';",
            "import * as path from 'path';",
            "import * as fs from 'fs';",
        ]

        # Add conditional imports based on features used

        if self._uses_child_process(ir):

            imports.append("import { spawn, execSync } from 'child_process';")

        if self._uses_async_features(ir):

            imports.append("import { promisify } from 'util';")

        return imports

    def _generate_exports(self, ir: Dict[str, Any]) -> List[str]:
        """Generate TypeScript export statements."""

        exports = []

        # Export main CLI function

        exports.append("export { program, cliEntry };")

        # Export interfaces if needed

        if self._needs_interface_exports(ir):

            exports.append("export type { CommandArgs, HookFunction, GlobalOptions };")

        return exports

    def _transform_cli_schema(self, cli_schema: Dict[str, Any]) -> Dict[str, Any]:
        """Transform CLI schema for TypeScript-specific rendering."""

        transformed = cli_schema.copy()

        # Convert command names to TypeScript-safe identifiers

        if "commands" in transformed:

            for cmd_name, cmd_data in transformed["commands"].items():

                # Add TypeScript-specific metadata

                cmd_data["typescript"] = {
                    "interface_name": f"{self._pascal_case_filter(cmd_name)}Options",
                    "hook_name": f"on{self._pascal_case_filter(cmd_name)}",
                    "safe_name": self._ts_safe_name_filter(cmd_name),
                }

                # Transform options with TypeScript types

                if "options" in cmd_data:

                    for option in cmd_data["options"]:

                        option["typescript_type"] = self._ts_type_filter(
                            option.get("type", "string")
                        )

        return transformed

    def _generate_build_config(self, ir: Dict[str, Any]) -> Dict[str, Any]:
        """Generate simple TypeScript build configuration."""

        return {
            "tsconfig": {
                "compilerOptions": {
                    "target": "ES2020",
                    "module": "CommonJS",
                    "moduleResolution": "node",
                    "outDir": "./dist",
                    "strict": True,
                    "esModuleInterop": True,
                    "skipLibCheck": True,
                    "declaration": True,
                    "sourceMap": True,
                }
            }
        }

    def _apply_naming_conventions(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Apply TypeScript naming conventions throughout the context."""

        # Convert project names to appropriate cases

        if "project" in context:

            project = context["project"]

            # Keep original names but add TypeScript variants

            project["typescript"] = {
                "class_name": self._pascal_case_filter(project.get("name", "")),
                "variable_name": self._camel_case_filter(project.get("name", "")),
                "type_name": self._pascal_case_filter(project.get("name", "")) + "CLI",
            }

        return context

    def _enhance_command_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance context for command handler component."""

        enhanced = context.copy()

        # Add Commander.js specific helpers

        enhanced["commander"] = {
            "option_builders": self._generate_commander_options(context),
            "argument_builders": self._generate_commander_arguments(context),
            "action_handlers": self._generate_action_handlers(context),
        }

        return enhanced

    def _enhance_config_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance context for config manager component."""

        enhanced = context.copy()

        # Add configuration interfaces and validation

        enhanced["config"] = {
            "interface": self._generate_config_interface(context),
            "validation": self._generate_config_validation(context),
            "defaults": self._generate_config_defaults(context),
        }

        return enhanced

    def _enhance_completion_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance context for completion engine component."""

        enhanced = context.copy()

        # Add shell completion specific data

        enhanced["completion"] = {
            "completers": self._generate_completers(context),
            "shell_scripts": self._generate_shell_scripts(context),
        }

        return enhanced

    # Filter implementations

    def _ts_type_filter(self, type_str: str) -> str:
        """Convert generic types to TypeScript types."""

        if type_str is None or type_str == "":

            return "any"

        mappings = self._get_type_mappings()

        return mappings.get(str(type_str).lower(), "any")

    def _ts_interface_filter(self, name: str) -> str:
        """Generate interface name (PascalCase)."""

        return self._pascal_case_filter(name)

    def _ts_import_filter(self, module: str, items: Optional[List[str]] = None) -> str:
        """Generate TypeScript import statement."""

        if items:

            import_list = ", ".join(items)

            return f"import {{ {import_list} }} from '{module}';"

        else:

            return f"import * as {self._camel_case_filter(module)} from '{module}';"

    def _ts_commander_option_filter(self, option: Dict[str, Any]) -> str:
        """Generate typed Commander.js .option() call."""

        name = option.get("name", "")

        short = option.get("short", "")

        desc = option.get("description", "")

        type_str = option.get("type", "string")

        # Build flag string

        flags = f"--{name}"

        if short:

            flags = f"-{short}, {flags}"

        # Add value placeholder for non-boolean types

        if type_str != "flag" and type_str != "boolean":

            flags += f" <{self._ts_type_filter(type_str)}>"

        return f".option('{flags}', '{desc}')"

    def _build_commander_structure(self, cli_schema: Dict[str, Any]) -> Dict[str, Any]:
        """Build Commander.js specific command structure."""
        root_command = cli_schema.get("root_command", {})
        
        commander_data = {
            "root_command": {
                "name": root_command.get("name", "cli"),
                "description": root_command.get("description", "CLI application"),
                "version": root_command.get("version", self._get_version()),
                "options": [],
                "commands": [],
            },
            "subcommands": [],
        }
        
        # Convert options to Commander format
        for option in root_command.get("options", []):
            commander_option = {
                "flags": self._build_option_flags(option),
                "description": option.get("description", ""),
                "default": option.get("default"),
                "type": self._js_type_from_option(option),
            }
            commander_data["root_command"]["options"].append(commander_option)
        
        # Convert commands to Commander format
        for command in root_command.get("subcommands", []):
            commander_cmd = {
                "name": command.get("name", "command"),
                "description": command.get("description", ""),
                "arguments": [
                    self._build_commander_argument(arg)
                    for arg in command.get("arguments", [])
                ],
                "options": [
                    self._build_commander_option(opt)
                    for opt in command.get("options", [])
                ],
                "hook_name": command.get(
                    "hook_name", f"on_{command.get('name', 'command')}"
                ),
                "subcommands": command.get("subcommands", []),
            }
            commander_data["subcommands"].append(commander_cmd)
        
        return commander_data
    
    def _build_option_flags(self, option: Dict[str, Any]) -> str:
        """Build option flags for Commander.js."""
        name = option.get("name", "option")
        short = option.get("short")
        type_str = option.get("type", "string")
        
        if short:
            flags = f"-{short}, --{name}"
        else:
            flags = f"--{name}"
        
        # Add value placeholder for non-boolean types
        if type_str not in ("boolean", "flag"):
            flags += f" <{name}>"
        
        return flags
    
    def _js_type_from_option(self, option: Dict[str, Any]) -> str:
        """Convert option type to JavaScript type."""
        type_str = option.get("type", "string")
        type_mapping = {
            "string": "String",
            "number": "Number",
            "integer": "Number",
            "boolean": "Boolean",
            "flag": "Boolean",
            "array": "Array",
        }
        return type_mapping.get(type_str, "String")
    
    def _build_commander_argument(self, arg: Dict[str, Any]) -> Dict[str, Any]:
        """Build Commander.js argument structure."""
        return {
            "pattern": f"<{arg.get('name', 'arg')}>",
            "description": arg.get("description", ""),
            "type": arg.get("type", "string"),
        }
    
    def _build_commander_option(self, opt: Dict[str, Any]) -> Dict[str, Any]:
        """Build Commander.js option structure."""
        return {
            "flags": self._build_option_flags(opt),
            "description": opt.get("description", ""),
            "default": opt.get("default"),
            "type": self._js_type_from_option(opt),
        }

    def _camel_case_filter(self, text: str) -> str:
        """Convert text to camelCase."""

        if not text:

            return text

        words = re.split(r"[-_\s]+", text.lower())

        return words[0] + "".join(word.capitalize() for word in words[1:])

    def _pascal_case_filter(self, text: str) -> str:
        """Convert text to PascalCase."""

        if not text:

            return text

        words = re.split(r"[-_\s]+", text.lower())

        return "".join(word.capitalize() for word in words)

    def _ts_safe_name_filter(self, name: str) -> str:
        """Convert name to TypeScript-safe identifier."""

        ts_reserved_words = {
            "abstract",
            "any",
            "as",
            "asserts",
            "async",
            "await",
            "bigint",
            "boolean",
            "break",
            "case",
            "catch",
            "class",
            "const",
            "constructor",
            "continue",
            "debugger",
            "declare",
            "default",
            "delete",
            "do",
            "else",
            "enum",
            "export",
            "extends",
            "false",
            "finally",
            "for",
            "from",
            "function",
            "get",
            "if",
            "implements",
            "import",
            "in",
            "infer",
            "instanceof",
            "interface",
            "is",
            "keyof",
            "let",
            "module",
            "namespace",
            "never",
            "new",
            "null",
            "number",
            "object",
            "of",
            "package",
            "private",
            "protected",
            "public",
            "readonly",
            "require",
            "return",
            "set",
            "static",
            "string",
            "super",
            "switch",
            "symbol",
            "this",
            "throw",
            "true",
            "try",
            "type",
            "typeof",
            "undefined",
            "unique",
            "unknown",
            "var",
            "void",
            "while",
            "with",
            "yield",
        }

        # Replace invalid characters with underscore

        safe = re.sub(r"[^a-zA-Z0-9_]", "_", name)

        # Ensure doesn't start with number

        if safe and safe[0].isdigit():

            safe = "_" + safe

        # Check for reserved words

        if safe.lower() in ts_reserved_words:

            safe = "_" + safe

        return safe or "_unnamed"

    def _ts_optional_filter(self, arg: Any) -> str:
        """Return optional modifier for TypeScript property."""

        # Handle different input types

        if isinstance(arg, dict):

            # Check if it's a property definition with optional field

            if "optional" in arg:

                return "?" if arg["optional"] else ""

            # Check if it's an option definition with required field

            elif "required" in arg:

                return "" if arg.get("required", True) else "?"

            else:

                # Default to required

                return ""

        elif hasattr(arg, "optional"):

            # Handle object with optional attribute

            return "?" if getattr(arg, "optional", False) else ""

        else:

            # For any other type, assume it's required

            return ""

    def _ts_array_type_filter(self, item_type: str) -> str:
        """Convert to TypeScript array type."""

        ts_type = self._ts_type_filter(item_type)

        return f"{ts_type}[]"

    def _ts_function_signature_filter(self, params, return_type: str = "void") -> str:
        """Generate TypeScript function signature."""

        param_strs = []

        # Handle different input formats

        if isinstance(params, dict) and ("arguments" in params or "options" in params):

            # Command data structure with arguments and options

            # Add arguments as positional parameters

            for arg in params.get("arguments", []):

                name = arg.get("name", "arg")

                type_str = self._ts_type_filter(arg.get("type", "any"))

                optional = "" if arg.get("required", True) else "?"

                param_strs.append(f"{name}{optional}: {type_str}")

            # Add options as a typed object if there are any

            if params.get("options"):

                param_strs.append(
                    "options?: any"
                )  # Could be more specific based on option types

        elif isinstance(params, list):

            # Direct list of parameters

            for param in params:

                name = param.get("name", "arg")

                type_str = self._ts_type_filter(param.get("type", "any"))

                optional = "" if param.get("required", True) else "?"

                param_strs.append(f"{name}{optional}: {type_str}")

        params_str = ", ".join(param_strs)

        return_ts_type = self._ts_type_filter(return_type)

        return f"({params_str}): {return_ts_type}"

    # Helper methods for context generation

    def _generate_global_options_interface(self, options: List[Dict[str, Any]]) -> str:
        """Generate interface for global options."""

        if not options:

            return "interface GlobalOptions {}"

        properties = []

        for option in options:

            name = self._camel_case_filter(option.get("name", ""))

            type_str = self._ts_optional_filter(
                option.get("type", "string"), option.get("required", False)
            )

            properties.append(f"  {name}: {type_str};")

        return "interface GlobalOptions {\n" + "\n".join(properties) + "\n}"

    def _generate_command_interface(self, cmd_data: Dict[str, Any]) -> str:
        """Generate interface for command options."""

        properties = ["  debug?: boolean;"]  # Always include debug option

        if "options" in cmd_data:

            for option in cmd_data["options"]:

                name = self._camel_case_filter(option.get("name", ""))

                type_str = self._ts_optional_filter(
                    option.get("type", "string"), option.get("required", False)
                )

                properties.append(f"  {name}: {type_str};")

        interface_name = cmd_data.get("typescript", {}).get(
            "interface_name", "CommandOptions"
        )

        return f"interface {interface_name} {{\n" + "\n".join(properties) + "\n}"

    def _generate_config_interface(self, context: Dict[str, Any]) -> str:
        """Generate configuration interface."""

        # Basic config interface - can be extended based on needs

        return """interface ConfigOptions {

  debug?: boolean;

  configPath?: string;

  [key: string]: any;

}"""

    def _generate_config_validation(self, context: Dict[str, Any]) -> str:
        """Generate configuration validation logic."""

        return """function validateConfig(config: any): ConfigOptions {

  // Add validation logic here

  return config as ConfigOptions;

}"""

    def _generate_config_defaults(self, context: Dict[str, Any]) -> str:
        """Generate default configuration values."""

        return """const DEFAULT_CONFIG: Partial<ConfigOptions> = {

  debug: false

};"""

    def _generate_commander_options(self, context: Dict[str, Any]) -> List[str]:
        """Generate Commander.js option builders."""

        # This would generate the .option() calls for Commander.js

        return []

    def _generate_commander_arguments(self, context: Dict[str, Any]) -> List[str]:
        """Generate Commander.js argument builders."""

        # This would generate the .argument() calls for Commander.js

        return []

    def _generate_action_handlers(self, context: Dict[str, Any]) -> List[str]:
        """Generate Commander.js action handlers."""

        # This would generate the .action() callbacks

        return []

    def _generate_completers(self, context: Dict[str, Any]) -> List[str]:
        """Generate completion functions."""

        return []

    def _generate_shell_scripts(self, context: Dict[str, Any]) -> Dict[str, str]:
        """Generate shell completion scripts."""

        return {}

    # Feature detection helpers

    def _uses_child_process(self, ir: Dict[str, Any]) -> bool:
        """Check if CLI uses child process functionality."""

        # Could check for spawn/exec usage in commands

        return True  # Default to including for CLI tools

    def _uses_async_features(self, ir: Dict[str, Any]) -> bool:
        """Check if CLI uses async/await features."""

        return True  # Most modern CLIs are async

    def _needs_interface_exports(self, ir: Dict[str, Any]) -> bool:
        """Check if interfaces should be exported."""

        return True  # Default to exporting for TypeScript libraries

    def _has_interactive_features(self, cli_schema: Dict[str, Any]) -> bool:
        """Check if CLI has interactive mode features."""

        features = cli_schema.get("features", {})

        interactive_mode = features.get("interactive_mode", {})

        return interactive_mode.get("enabled", False)

    def _js_string_filter(self, value: str) -> str:
        """
        Escape string for JavaScript/TypeScript while preserving Unicode characters.

        Only escapes necessary characters for JavaScript/TypeScript string literals:
        - Backslashes (must be first to avoid double-escaping)
        - Quote characters that would break string literals
        - Control characters that would break JavaScript parsing

        Unicode characters (like Chinese, Arabic, emoji, etc.) are preserved as-is
        since JavaScript/TypeScript natively supports UTF-8.
        """

        if not isinstance(value, str):

            return str(value)

        # Only escape characters that would break JavaScript/TypeScript syntax
        # Order matters: backslash first to avoid double-escaping
        escaped = value.replace("\\", "\\\\")  # Escape backslashes first
        escaped = escaped.replace('"', '\\"')  # Escape double quotes
        escaped = escaped.replace("'", "\\'")  # Escape single quotes
        escaped = escaped.replace("\n", "\\n")  # Escape newlines
        escaped = escaped.replace("\r", "\\r")  # Escape carriage returns
        escaped = escaped.replace("\t", "\\t")  # Escape tabs

        # Do NOT escape Unicode characters - they should be preserved
        return escaped
