"""
Command Hierarchy Builder for Nested Command Support

This module implements the flat generation + post-processing approach for
unlimited depth nested command support in the Goobits CLI Framework.
"""

from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Tuple


@dataclass
class FlatCommand:
    """
    Represents a single command in flattened form with full path context.
    """

    name: str
    path: List[str]  # Full path from root (e.g., ['api', 'v1', 'users', 'create'])
    description: str
    arguments: List[Dict[str, Any]]
    options: List[Dict[str, Any]]
    hook_name: str
    is_group: bool  # True if this command has subcommands
    parent_path: List[str]  # Path to parent (e.g., ['api', 'v1', 'users'])
    depth: int


@dataclass
class CommandHierarchy:
    """
    Represents the hierarchical structure of commands for template rendering.
    """

    groups: List["CommandGroup"]
    leaves: List[FlatCommand]
    max_depth: int


@dataclass
class CommandGroup:
    """
    Represents a command group (has subcommands).
    """

    name: str
    path: List[str]
    description: str
    arguments: List[Dict[str, Any]]
    options: List[Dict[str, Any]]
    hook_name: str
    subcommands: List["CommandNode"]
    depth: int


@dataclass
class CommandNode:
    """
    Represents either a leaf command or a group in the hierarchy.
    """

    command: FlatCommand
    children: List["CommandNode"]
    is_leaf: bool


class CommandFlattener:
    """
    Extracts all commands from nested structure into flat list with full paths.
    """

    def flatten_commands(self, commands_dict: Dict[str, Any]) -> List[FlatCommand]:
        """
        Extract all commands as flat list with full path context.

        Args:
            commands_dict: Nested commands dictionary from IR

        Returns:
            List of FlatCommand objects with full path information
        """
        flat_commands = []
        self._extract_commands_recursive(commands_dict, [], flat_commands)
        return flat_commands

    def _extract_commands_recursive(
        self,
        commands_dict: Dict[str, Any],
        parent_path: List[str],
        flat_commands: List[FlatCommand],
    ) -> None:
        """
        Recursively extract commands and build flat list.

        Args:
            commands_dict: Current level commands dictionary
            parent_path: Path to current level (e.g., ['api', 'v1'])
            flat_commands: Accumulator for flat commands
        """
        for cmd_name, cmd_data in commands_dict.items():
            current_path = parent_path + [cmd_name]

            # Determine if this is a group (has subcommands)
            has_subcommands = bool(cmd_data.get("subcommands"))

            # Generate hook name with smart abbreviation
            hook_name = self._generate_hook_name(current_path)

            # Create flat command
            flat_cmd = FlatCommand(
                name=cmd_name,
                path=current_path,
                description=cmd_data.get("description", ""),
                arguments=cmd_data.get("arguments", []),
                options=cmd_data.get("options", []),
                hook_name=hook_name,
                is_group=has_subcommands,
                parent_path=parent_path,
                depth=len(current_path),
            )

            flat_commands.append(flat_cmd)

            # Recursively process subcommands
            if has_subcommands:
                subcommands_data = cmd_data["subcommands"]

                # Handle both dictionary and list formats for subcommands
                if isinstance(subcommands_data, dict):
                    self._extract_commands_recursive(
                        subcommands_data, current_path, flat_commands
                    )
                elif isinstance(subcommands_data, list):
                    # Convert list format to dictionary format
                    subcommands_dict = {}
                    for subcmd in subcommands_data:
                        if isinstance(subcmd, dict) and "name" in subcmd:
                            subcommands_dict[subcmd["name"]] = subcmd

                    self._extract_commands_recursive(
                        subcommands_dict, current_path, flat_commands
                    )
                else:
                    print(
                        f"Warning: Unexpected subcommands format for {current_path}: {type(subcommands_data)}"
                    )
                    print(f"Content: {subcommands_data}")

    def _generate_hook_name(self, command_path: List[str]) -> str:
        """
        Generate hook name with intelligent abbreviation for deep paths.

        Strategy:
        - 1-2 levels: exact path (on_greet, on_database_users)
        - 3-4 levels: skip middle (on_api_users_create for api->v1->users->create)
        - 5+ levels: first + last 2 (on_api_permissions_grant for api->v1->users->permissions->grant)

        Args:
            command_path: Full command path list

        Returns:
            Hook name string
        """
        if len(command_path) <= 2:
            # Short paths: use exact match
            return f"on_{'_'.join(command_path)}"
        elif len(command_path) <= 4:
            # Medium paths: skip middle components
            if len(command_path) == 3:
                return f"on_{command_path[0]}_{command_path[2]}"
            else:  # length 4
                return f"on_{command_path[0]}_{command_path[2]}_{command_path[3]}"
        else:
            # Long paths: first + last 2 components
            return f"on_{command_path[0]}_{command_path[-2]}_{command_path[-1]}"


class HierarchyBuilder:
    """
    Builds Click-compatible command hierarchy from flat command list.
    """

    def build_hierarchy(self, flat_commands: List[FlatCommand]) -> CommandHierarchy:
        """
        Build hierarchical structure from flat commands for template rendering.

        Args:
            flat_commands: List of flat commands with path information

        Returns:
            CommandHierarchy ready for template rendering
        """
        if not flat_commands:
            return CommandHierarchy(groups=[], leaves=[], max_depth=0)

        # Separate groups and leaves
        groups = [cmd for cmd in flat_commands if cmd.is_group]
        leaves = [cmd for cmd in flat_commands if not cmd.is_group]

        # Calculate max depth
        max_depth = max(cmd.depth for cmd in flat_commands) if flat_commands else 0

        # Build group hierarchy
        command_groups = self._build_command_groups(groups, leaves)

        return CommandHierarchy(
            groups=command_groups, leaves=leaves, max_depth=max_depth
        )

    def _build_command_groups(
        self, groups: List[FlatCommand], leaves: List[FlatCommand]
    ) -> List[CommandGroup]:
        """
        Build command groups with their subcommand relationships.

        Args:
            groups: List of group commands
            leaves: List of leaf commands

        Returns:
            List of CommandGroup objects with subcommand relationships
        """
        command_groups = []

        # Sort groups by depth to process parents before children
        groups_by_depth = sorted(groups, key=lambda g: g.depth)

        for group in groups_by_depth:
            # Find direct subcommands for this group
            subcommands = self._find_direct_subcommands(group, groups + leaves)

            command_group = CommandGroup(
                name=group.name,
                path=group.path,
                description=group.description,
                arguments=group.arguments,
                options=group.options,
                hook_name=group.hook_name,
                subcommands=subcommands,
                depth=group.depth,
            )

            command_groups.append(command_group)

        return command_groups

    def _find_direct_subcommands(
        self, parent: FlatCommand, all_commands: List[FlatCommand]
    ) -> List[CommandNode]:
        """
        Find direct subcommands for a parent command.

        Args:
            parent: Parent command to find subcommands for
            all_commands: All available commands

        Returns:
            List of direct subcommands as CommandNode objects
        """
        subcommands = []

        for cmd in all_commands:
            # Check if this command is a direct child
            if len(cmd.path) == len(parent.path) + 1 and cmd.path[:-1] == parent.path:
                # Build command node
                children = []
                if cmd.is_group:
                    children = self._find_direct_subcommands(cmd, all_commands)

                command_node = CommandNode(
                    command=cmd, children=children, is_leaf=not cmd.is_group
                )

                subcommands.append(command_node)

        return subcommands


class HookNameResolver:
    """
    Intelligent hook discovery with multiple fallback strategies.
    """

    def __init__(self, hooks_module):
        """Initialize with hooks module."""
        self.hooks_module = hooks_module
        self.available_hooks = self._discover_available_hooks()

    def _discover_available_hooks(self) -> List[str]:
        """Discover all available hook functions in the module."""
        if not self.hooks_module:
            return []

        return [
            name
            for name in dir(self.hooks_module)
            if not name.startswith("_") and callable(getattr(self.hooks_module, name))
        ]

    def resolve_hook(self, command_path: List[str]) -> Tuple[Callable, str]:
        """
        Resolve hook function with fallback strategies.

        Args:
            command_path: Full command path

        Returns:
            Tuple of (hook_function, resolved_hook_name)

        Raises:
            AttributeError: If no hook found with any strategy
        """
        strategies = [
            self._exact_match,
            self._abbreviated_match,
            self._namespace_match,
            self._generic_fallback,
        ]

        for strategy in strategies:
            try:
                hook_func, hook_name = strategy(command_path)
                if hook_func:
                    return hook_func, hook_name
            except AttributeError:
                continue

        # No hook found with any strategy
        suggested_names = self._generate_hook_suggestions(command_path)
        raise AttributeError(
            f"No hook found for command path {' -> '.join(command_path)}. "
            f"Suggested hook names: {', '.join(suggested_names)}"
        )

    def _exact_match(self, command_path: List[str]) -> Tuple[Callable, str]:
        """Strategy 1: Exact path match."""
        hook_name = f"on_{'_'.join(command_path)}"
        if hasattr(self.hooks_module, hook_name):
            return getattr(self.hooks_module, hook_name), hook_name
        raise AttributeError(f"Exact match not found: {hook_name}")

    def _abbreviated_match(self, command_path: List[str]) -> Tuple[Callable, str]:
        """Strategy 2: Intelligent abbreviation."""
        flattener = CommandFlattener()
        hook_name = flattener._generate_hook_name(command_path)
        if hasattr(self.hooks_module, hook_name):
            return getattr(self.hooks_module, hook_name), hook_name
        raise AttributeError(f"Abbreviated match not found: {hook_name}")

    def _namespace_match(self, command_path: List[str]) -> Tuple[Callable, str]:
        """Strategy 3: Namespace separation."""
        hook_name = f"on_{'__'.join(command_path)}"
        if hasattr(self.hooks_module, hook_name):
            return getattr(self.hooks_module, hook_name), hook_name
        raise AttributeError(f"Namespace match not found: {hook_name}")

    def _generic_fallback(self, command_path: List[str]) -> Tuple[Callable, str]:
        """Strategy 4: Generic command handler."""
        hook_name = "on_command_executed"
        if hasattr(self.hooks_module, hook_name):
            return getattr(self.hooks_module, hook_name), hook_name
        raise AttributeError("Generic fallback not found: on_command_executed")

    def _generate_hook_suggestions(self, command_path: List[str]) -> List[str]:
        """Generate helpful hook name suggestions."""
        flattener = CommandFlattener()
        return [
            f"on_{'_'.join(command_path)}",  # Exact
            flattener._generate_hook_name(command_path),  # Abbreviated
            f"on_{'__'.join(command_path)}",  # Namespace
            "on_command_executed",  # Generic
        ]
