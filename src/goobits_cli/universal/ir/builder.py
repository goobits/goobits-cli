"""
Intermediate Representation (IR) Builder for the Universal Template System.

This module converts Goobits configuration into a language-agnostic
intermediate representation that can be consumed by any language renderer.
"""

from typing import Any, Dict, List

from ...core.utils import safe_get_attr as _safe_get_attr
from ...core.utils import safe_to_dict as _safe_to_dict
from ..command_hierarchy import CommandFlattener, HierarchyBuilder
from .feature_analyzer import FeatureAnalyzer


class IRBuilder:
    """
    Builds intermediate representation from Goobits configuration.

    The IR is a normalized, language-agnostic format that contains all
    information needed to generate CLI implementations for any supported
    programming language.
    """

    def __init__(self):
        """Initialize the IR builder."""
        self.feature_analyzer = FeatureAnalyzer()

    def build(self, config, config_filename: str = "goobits.yaml") -> Dict[str, Any]:
        """
        Convert Goobits configuration to intermediate representation.

        This method extracts and normalizes all information from the configuration
        into a language-agnostic format that can be consumed by any renderer.

        Args:
            config: Validated Goobits configuration
            config_filename: Name of the configuration file

        Returns:
            Intermediate representation as dictionary
        """
        # Convert config to dict for safe access
        config_dict = _safe_to_dict(config)

        cli_config = config_dict.get("cli", {})
        cli_schema = self._extract_config_schema(cli_config)

        # Analyze feature requirements for performance optimization
        feature_requirements = self.feature_analyzer.analyze(config, config_filename)

        ir = {
            "project": {
                "name": _safe_get_attr(
                    config, "display_name", _safe_get_attr(config, "command_name")
                ),
                "description": _safe_get_attr(config, "description"),
                "version": (
                    (lambda v: v if v is not None else "1.0.0")(
                        _safe_get_attr(
                            _safe_get_attr(config, "cli", {}), "version", "1.0.0"
                        )
                    )
                    if _safe_get_attr(config, "cli")
                    else "1.0.0"
                ),
                "author": _safe_get_attr(config, "author"),
                "license": _safe_get_attr(config, "license"),
                "package_name": _safe_get_attr(config, "package_name"),
                "command_name": _safe_get_attr(config, "command_name"),
                "cli_path": _safe_get_attr(config, "cli_path"),
                "cli_hooks_path": _safe_get_attr(config, "cli_hooks_path"),
                "hooks_path": _safe_get_attr(config, "hooks_path"),
            },
            "cli": cli_schema,
            "installation": {
                "pypi_name": _safe_get_attr(
                    _safe_get_attr(config, "installation", {}),
                    "pypi_name",
                    _safe_get_attr(config, "package_name"),
                ),
                "setup_path": _safe_get_attr(
                    _safe_get_attr(config, "installation", {}), "setup_path"
                ),
                "development_path": _safe_get_attr(
                    _safe_get_attr(config, "installation", {}), "development_path", "."
                ),
                "extras": _safe_to_dict(
                    _safe_get_attr(
                        _safe_get_attr(config, "installation", {}), "extras", {}
                    )
                ),
            },
            "dependencies": self._extract_dependencies(config),
            "features": _safe_to_dict(_safe_get_attr(config, "features", {})),
            # Add feature requirements for conditional template generation
            "feature_requirements": feature_requirements,
            "metadata": {
                "generated_at": "{{ timestamp }}",  # Will be replaced during rendering
                "generator_version": "{{ version }}",  # Will be replaced during rendering
                "source_config": _safe_to_dict(config),
                "config_filename": config_filename,
            },
        }

        return ir

    def _extract_config_schema(self, cli_config: Any) -> Dict[str, Any]:
        """
        Extract normalized CLI schema from configuration.

        Args:
            cli_config: CLI configuration section

        Returns:
            Normalized CLI schema
        """
        # Convert cli_config to dict for safe access
        cli_dict = _safe_to_dict(cli_config)

        schema = {
            "root_command": {
                "name": cli_dict.get("name", ""),
                "description": cli_dict.get("description", cli_dict.get("tagline", "")),
                "version": (lambda v: v if v is not None else "1.0.0")(
                    cli_dict.get("version", "1.0.0")
                ),
                "arguments": [],
                "options": [],
                "subcommands": [],
            },
            "commands": {},
            "global_options": [],
            "completion": {
                "enabled": True,  # Default to enabled
                "shells": ["bash", "zsh", "fish"],
            },
            # Preserve custom help sections
            "tagline": _safe_get_attr(
                cli_config,
                "tagline",
                _safe_get_attr(cli_config, "description", "No description"),
            ),
            "description": _safe_get_attr(cli_config, "description", "No description"),
            "header_sections": _safe_get_attr(cli_config, "header_sections", []),
            "footer_note": _safe_get_attr(cli_config, "footer_note"),
            "version": _safe_get_attr(cli_config, "version", "1.0.0"),
        }

        # Extract arguments (CLI root rarely has arguments in current schema)

        if "args" in cli_dict and cli_dict["args"]:
            for arg in cli_dict["args"]:
                schema["root_command"]["arguments"].append(
                    {
                        "name": _safe_get_attr(arg, "name"),
                        "description": _safe_get_attr(arg, "desc"),
                        "type": _safe_get_attr(arg, "type", "string"),
                        "required": _safe_get_attr(arg, "required", True),
                        "multiple": _safe_get_attr(arg, "nargs") == "*",
                        "nargs": _safe_get_attr(arg, "nargs"),
                    }
                )

        # Extract options

        if "options" in cli_dict and cli_dict["options"]:
            for opt in cli_dict["options"]:
                option_data = {
                    "name": _safe_get_attr(opt, "name"),
                    "short": _safe_get_attr(opt, "short"),
                    "description": _safe_get_attr(opt, "desc"),
                    "type": _safe_get_attr(opt, "type", "str"),
                    "default": _safe_get_attr(opt, "default"),
                    "required": False,  # Global options typically not required
                    "multiple": _safe_get_attr(opt, "multiple", False),
                }

                schema["root_command"]["options"].append(option_data)

        # Extract subcommands

        if "commands" in cli_dict and cli_dict["commands"]:
            commands = cli_dict["commands"]

            if isinstance(commands, dict):
                # Old format: {"hello": {...}}
                for cmd_name, cmd in commands.items():
                    cmd_dict = _safe_to_dict(cmd)

                    command_data = {
                        "name": cmd_name,
                        "description": cmd_dict.get(
                            "description", cmd_dict.get("desc", "")
                        ),
                        "arguments": [],
                        "options": [],
                        "subcommands": [],
                        "hook_name": f"on_{cmd_name.replace('-', '_')}",
                    }

                    # Extract command arguments
                    if "args" in cmd_dict and cmd_dict["args"]:
                        for arg in cmd_dict["args"]:
                            arg_dict = _safe_to_dict(arg)
                            command_data["arguments"].append(
                                {
                                    "name": arg_dict.get("name", ""),
                                    "description": arg_dict.get(
                                        "desc", arg_dict.get("description", "")
                                    ),
                                    "type": arg_dict.get("type", "string"),
                                    "required": arg_dict.get("required", False),
                                    "default": arg_dict.get("default"),
                                }
                            )

                    # Extract command options
                    if "options" in cmd_dict and cmd_dict["options"]:
                        for opt in cmd_dict["options"]:
                            opt_dict = _safe_to_dict(opt)
                            command_data["options"].append(
                                {
                                    "name": opt_dict.get("name", ""),
                                    "description": opt_dict.get(
                                        "desc", opt_dict.get("description", "")
                                    ),
                                    "type": opt_dict.get("type", "string"),
                                    "required": opt_dict.get("required", False),
                                    "short": opt_dict.get("short"),
                                    "default": opt_dict.get("default"),
                                    "multiple": opt_dict.get("multiple", False),
                                }
                            )

                    # Handle nested subcommands
                    if "subcommands" in cmd_dict and cmd_dict["subcommands"]:
                        command_data["subcommands"] = self._extract_subcommands_dict(
                            cmd_dict["subcommands"]
                        )

                    schema["root_command"]["subcommands"].append(command_data)
                    schema["commands"][cmd_name] = command_data

            elif isinstance(commands, list):
                # New format: [{"name": "hello", ...}]
                for cmd in commands:
                    cmd_dict = _safe_to_dict(cmd)
                    cmd_name = cmd_dict.get("name", "unknown")

                    command_data = {
                        "name": cmd_name,
                        "description": cmd_dict.get(
                            "description", cmd_dict.get("desc", "")
                        ),
                        "arguments": [],
                        "options": [],
                        "subcommands": [],
                        "hook_name": f"on_{cmd_name.replace('-', '_')}",
                    }

                    # Extract command arguments

                    if "args" in cmd_dict and cmd_dict["args"]:
                        for arg in cmd_dict["args"]:
                            command_data["arguments"].append(
                                {
                                    "name": _safe_get_attr(arg, "name"),
                                    "description": _safe_get_attr(
                                        arg, "desc"
                                    ),  # Note: ArgumentSchema uses 'desc'
                                    "type": _safe_get_attr(arg, "type", "string"),
                                    "required": _safe_get_attr(arg, "required", True),
                                    "multiple": _safe_get_attr(arg, "nargs") == "*",
                                    "nargs": _safe_get_attr(arg, "nargs"),
                                }
                            )

                    # Extract command options

                    if "options" in cmd_dict and cmd_dict["options"]:
                        for opt in cmd_dict["options"]:
                            command_data["options"].append(
                                {
                                    "name": _safe_get_attr(opt, "name"),
                                    "short": _safe_get_attr(opt, "short"),
                                    "description": _safe_get_attr(
                                        opt, "desc"
                                    ),  # Note: OptionSchema uses 'desc'
                                    "type": _safe_get_attr(opt, "type", "str"),
                                    "default": _safe_get_attr(opt, "default"),
                                    "required": False,  # Options are typically not required
                                    "multiple": _safe_get_attr(opt, "multiple", False),
                                }
                            )

                    # Handle nested subcommands recursively

                    if "subcommands" in cmd_dict and cmd_dict["subcommands"]:
                        command_data["subcommands"] = self._extract_subcommands_dict(
                            cmd_dict["subcommands"]
                        )

                    schema["root_command"]["subcommands"].append(command_data)

                    schema["commands"][cmd_name] = command_data

        # Build command hierarchy for nested command support
        if schema["commands"]:
            flattener = CommandFlattener()
            hierarchy_builder = HierarchyBuilder()

            # Extract flat commands from nested structure
            flat_commands = flattener.flatten_commands(schema["commands"])

            # Build hierarchical structure for template rendering
            command_hierarchy = hierarchy_builder.build_hierarchy(flat_commands)

            # Add hierarchy to schema for template access
            schema["command_hierarchy"] = {
                "groups": [
                    self._serialize_command_group(group)
                    for group in command_hierarchy.groups
                ],
                "leaves": [
                    self._serialize_flat_command(leaf)
                    for leaf in command_hierarchy.leaves
                ],
                "max_depth": command_hierarchy.max_depth,
                "flat_commands": [
                    self._serialize_flat_command(cmd) for cmd in flat_commands
                ],
            }
        else:
            schema["command_hierarchy"] = {
                "groups": [],
                "leaves": [],
                "max_depth": 0,
                "flat_commands": [],
            }

        return schema

    def _serialize_command_group(self, group) -> Dict[str, Any]:
        """Serialize CommandGroup for template rendering."""
        return {
            "name": group.name,
            "path": group.path,
            "description": group.description,
            "arguments": group.arguments,
            "options": group.options,
            "hook_name": group.hook_name,
            "subcommands": [
                self._serialize_command_node(node) for node in group.subcommands
            ],
            "depth": group.depth,
            "parent_path": group.path[:-1] if group.path else [],
            "click_decorator": self._get_click_decorator(group.path),
        }

    def _serialize_flat_command(self, command) -> Dict[str, Any]:
        """Serialize FlatCommand for template rendering."""
        return {
            "name": command.name,
            "path": command.path,
            "description": command.description,
            "arguments": command.arguments,
            "options": command.options,
            "hook_name": command.hook_name,
            "is_group": command.is_group,
            "parent_path": command.parent_path,
            "depth": command.depth,
            "click_decorator": self._get_click_decorator(command.path),
        }

    def _serialize_command_node(self, node) -> Dict[str, Any]:
        """Serialize CommandNode for template rendering."""
        return {
            "command": self._serialize_flat_command(node.command),
            "children": [
                self._serialize_command_node(child) for child in node.children
            ],
            "is_leaf": node.is_leaf,
        }

    def _get_click_decorator(self, command_path: List[str]) -> str:
        """Generate Click decorator for command path."""
        if len(command_path) <= 1:
            return "main"
        else:
            parent_path = command_path[:-1]
            return ".".join(parent_path).replace("-", "_")

    def _extract_subcommands_dict(
        self, commands: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Extract subcommands from dictionary format (used by CLISchema).

        Args:
            commands: Dictionary of command configurations

        Returns:
            List of normalized subcommand schemas
        """

        subcommands = []

        for cmd_name, cmd in commands.items():
            command_data = {
                "name": cmd_name,
                "description": _safe_get_attr(cmd, "desc"),
                "arguments": [],
                "options": [],
                "subcommands": [],
                "hook_name": f"on_{cmd_name.replace('-', '_')}",
            }

            # Extract arguments and options similar to main commands
            # Handle both dict and object cases
            if isinstance(cmd, dict):
                # Subcommands come as dictionaries
                args = cmd.get("args", [])
                options = cmd.get("options", [])
            else:
                # Main commands come as objects
                args = getattr(cmd, "args", []) if hasattr(cmd, "args") else []
                options = getattr(cmd, "options", []) if hasattr(cmd, "options") else []

            if args:
                for arg in args:
                    # Handle both dict and object arg formats
                    if isinstance(arg, dict):
                        arg_name = arg.get("name")
                        arg_desc = arg.get("desc", "")
                        arg_type = arg.get("type", "string")
                        arg_required = arg.get("required", True)
                        arg_nargs = arg.get("nargs")
                    else:
                        arg_name = _safe_get_attr(arg, "name")
                        arg_desc = _safe_get_attr(arg, "desc")
                        arg_type = _safe_get_attr(arg, "type", "string")
                        arg_required = _safe_get_attr(arg, "required", True)
                        arg_nargs = _safe_get_attr(arg, "nargs")

                    command_data["arguments"].append(
                        {
                            "name": arg_name,
                            "description": arg_desc,
                            "type": arg_type,
                            "required": arg_required,
                            "multiple": arg_nargs == "*",
                            "nargs": arg_nargs,
                        }
                    )

            # Options handling (already extracted above for dict case)
            if not isinstance(cmd, dict) and hasattr(cmd, "options") and cmd.options:
                options = cmd.options

            if options:
                for opt in options:
                    # Handle both dict and object option formats
                    if isinstance(opt, dict):
                        opt_name = opt.get("name")
                        opt_short = opt.get("short")
                        opt_desc = opt.get("desc", "")
                        opt_type = opt.get("type", "str")
                        opt_default = opt.get("default")
                        opt_multiple = opt.get("multiple", False)
                    else:
                        opt_name = _safe_get_attr(opt, "name")
                        opt_short = _safe_get_attr(opt, "short")
                        opt_desc = _safe_get_attr(opt, "desc")
                        opt_type = _safe_get_attr(opt, "type", "str")
                        opt_default = _safe_get_attr(opt, "default")
                        opt_multiple = _safe_get_attr(opt, "multiple", False)

                    command_data["options"].append(
                        {
                            "name": opt_name,
                            "short": opt_short,
                            "description": opt_desc,
                            "type": opt_type,
                            "default": opt_default,
                            "required": False,
                            "multiple": opt_multiple,
                        }
                    )

            # Recursively handle nested subcommands
            if isinstance(cmd, dict):
                nested_subcommands = cmd.get("subcommands")
            else:
                nested_subcommands = (
                    getattr(cmd, "subcommands", None)
                    if hasattr(cmd, "subcommands")
                    else None
                )

            if nested_subcommands:
                command_data["subcommands"] = self._extract_subcommands_dict(
                    nested_subcommands
                )

            subcommands.append(command_data)

        return subcommands

    def _extract_subcommands(self, commands: List[Any]) -> List[Dict[str, Any]]:
        """
        Recursively extract subcommands.

        Args:
            commands: List of command configurations

        Returns:
            List of normalized subcommand schemas
        """

        subcommands = []

        for cmd in commands:
            command_data = {
                "name": _safe_get_attr(cmd, "name"),
                "description": _safe_get_attr(cmd, "description"),
                "arguments": [],
                "options": [],
                "subcommands": [],
                "hook_name": f"on_{_safe_get_attr(cmd, 'name', '').replace('-', '_')}",
            }

            # Extract arguments and options similar to main commands

            if hasattr(cmd, "arguments") and cmd.arguments:
                for arg in cmd.arguments:
                    command_data["arguments"].append(
                        {
                            "name": _safe_get_attr(arg, "name"),
                            "description": _safe_get_attr(arg, "description"),
                            "type": _safe_get_attr(arg, "type", "string"),
                            "required": _safe_get_attr(arg, "required", True),
                            "multiple": _safe_get_attr(arg, "multiple", False),
                        }
                    )

            # Options handling
            options = []
            if not isinstance(cmd, dict) and hasattr(cmd, "options") and cmd.options:
                options = cmd.options

            if options:
                for opt in options:
                    command_data["options"].append(
                        {
                            "name": _safe_get_attr(opt, "name"),
                            "short": _safe_get_attr(opt, "short"),
                            "description": _safe_get_attr(opt, "description"),
                            "type": _safe_get_attr(opt, "type", "string"),
                            "default": _safe_get_attr(opt, "default"),
                            "required": _safe_get_attr(opt, "required", False),
                            "multiple": _safe_get_attr(opt, "multiple", False),
                        }
                    )

            # Recursively handle nested subcommands

            if hasattr(cmd, "commands") and cmd.commands:
                command_data["subcommands"] = self._extract_subcommands(cmd.commands)

            subcommands.append(command_data)

        return subcommands

    def _extract_dependencies(self, config) -> Dict[str, List[str]]:
        """
        Extract and normalize dependency information.

        Args:
            config: Goobits configuration

        Returns:
            Normalized dependencies by type
        """

        dependencies = {
            "python": [],
            "system": [],
            "npm": [],
            "rust": [],
        }

        # Extract from dependencies section

        dependencies_obj = _safe_get_attr(config, "dependencies")
        if dependencies_obj:
            # Handle required dependencies

            if _safe_get_attr(dependencies_obj, "required"):
                for dep in _safe_get_attr(dependencies_obj, "required", []):
                    if hasattr(dep, "name"):  # DependencyItem object
                        dep_name = _safe_get_attr(dep, "name")
                        dep_type = _safe_get_attr(dep, "type", "python")

                        # Only add to Python dependencies if it's not a system command
                        if dep_type != "command":
                            dependencies["python"].append(dep_name)
                        else:
                            # System commands go to system dependencies
                            dependencies["system"].append(dep_name)

                    else:  # String
                        # Assume strings are Python dependencies
                        dependencies["python"].append(dep)

            # Handle optional dependencies

            if _safe_get_attr(dependencies_obj, "optional"):
                for dep in _safe_get_attr(dependencies_obj, "optional", []):
                    if hasattr(dep, "name"):  # DependencyItem object
                        dep_name = _safe_get_attr(dep, "name")
                        dep_type = _safe_get_attr(dep, "type", "python")

                        # Only add to Python dependencies if it's not a system command
                        if dep_type != "command":
                            dependencies["python"].append(dep_name)
                        else:
                            # System commands go to system dependencies
                            dependencies["system"].append(dep_name)

                    else:  # String
                        # Assume strings are Python dependencies
                        dependencies["python"].append(dep)

        # Extract from installation extras

        installation_obj = _safe_get_attr(config, "installation")
        if installation_obj:
            extras_obj = _safe_get_attr(installation_obj, "extras")

            if extras_obj:
                # Convert Pydantic model to dict if necessary
                extras = _safe_to_dict(extras_obj)

                # Python extras from installation.extras.python are handled separately
                # in pyproject.toml optional-dependencies and are not added here.

                apt_extras = extras.get("apt", [])
                if apt_extras:
                    dependencies["system"].extend(apt_extras)

                npm_extras = extras.get("npm", [])
                if npm_extras:
                    dependencies["npm"].extend(npm_extras)

                cargo_extras = extras.get("cargo", [])
                if cargo_extras:
                    dependencies["rust"].extend(cargo_extras)

        # Extract Rust crates

        if hasattr(config, "rust_crates") and config.rust_crates:
            dependencies["rust"].extend(config.rust_crates.keys())

        return dependencies
