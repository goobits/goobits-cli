"""
Feature Detection for Universal Template Engine

This module provides feature detection capabilities for CLI configurations,
helping determine what dependencies, imports, and components are needed
for generated CLI applications across different languages.

The FeatureDetector analyzes goobits.yaml configurations to identify:
- UI complexity requirements (rich formatting vs basic)
- Interactive mode features
- Shell completion needs
- Complex argument patterns
- File operations
- Async capabilities
- Plugin systems
- Progress indicators
- Color support needs
"""

from typing import Dict, Any

# Import shared utility function
from ..generators import _safe_to_dict


class FeatureDetector:
    """
    Analyzes CLI configurations to detect feature requirements.
    
    This class contains all feature detection logic extracted from
    UniversalTemplateEngine to improve maintainability and separation
    of concerns. Methods analyze configuration dictionaries to determine
    what capabilities and dependencies are needed for generated CLIs.
    """

    @staticmethod
    def needs_rich_formatting(
        cli_config: Dict[str, Any], full_config: Dict[str, Any]
    ) -> bool:
        """
        Check if CLI needs rich formatting features.

        Conservative approach: prefer rich formatting if uncertain, but detect
        simple CLIs that can use basic Click for better performance.
        """
        # Always use rich for complex CLIs or when explicitly configured
        commands = cli_config.get("commands", {})

        # Simple CLI detection - if we have very basic commands with minimal options
        if len(commands) <= 2:
            for cmd in commands.values():
                cmd_dict = _safe_to_dict(cmd)
                # If command has no options and simple arguments, might not need rich
                options = cmd_dict.get("options", [])
                args = cmd_dict.get("args", [])
                if len(options) == 0 and len(args) <= 1:
                    continue
                else:
                    return True  # Complex enough to need rich
            # All commands are simple
            return False

        # Complex CLI - use rich formatting
        return len(commands) > 2

    @staticmethod
    def has_interactive_commands(cli_config: Dict[str, Any]) -> bool:
        """Check if CLI has interactive mode features."""
        features = cli_config.get("features", {})
        interactive_mode = features.get("interactive_mode", {})
        return interactive_mode.get("enabled", False)

    @staticmethod
    def has_completion_subcommands(cli_config: Dict[str, Any]) -> bool:
        """Check if CLI needs shell completion system."""
        completion = cli_config.get("completion", {})
        return completion.get("enabled", True)  # Default enabled

    @staticmethod
    def has_complex_arguments(cli_config: Dict[str, Any]) -> bool:
        """Check if CLI has complex argument parsing needs."""
        commands = cli_config.get("commands", {})

        for cmd in commands.values():
            cmd_dict = _safe_to_dict(cmd)

            # Check for complex argument patterns
            args = cmd_dict.get("args", [])
            options = cmd_dict.get("options", [])

            for arg in args:
                arg_dict = _safe_to_dict(arg)
                if arg_dict.get("nargs") or arg_dict.get("choices"):
                    return True

            for opt in options:
                opt_dict = _safe_to_dict(opt)
                if (
                    opt_dict.get("nargs")
                    or opt_dict.get("choices")
                    or opt_dict.get("type") in ["list", "dict", "json"]
                ):
                    return True

        return False

    @staticmethod
    def has_config_features(cli_config: Dict[str, Any]) -> bool:
        """Check if CLI uses configuration management."""
        commands = cli_config.get("commands", {})
        return any("config" in str(cmd_name).lower() for cmd_name in commands.keys())

    @staticmethod
    def has_async_features(cli_config: Dict[str, Any]) -> bool:
        """Check if CLI uses async features."""
        # For now, assume no async features unless explicitly marked
        features = cli_config.get("features", {})
        return features.get("async", {}).get("enabled", False)

    @staticmethod
    def has_plugin_features(cli_config: Dict[str, Any]) -> bool:
        """Check if CLI has plugin system."""
        features = cli_config.get("features", {})
        return features.get("plugins", {}).get("enabled", False)

    @staticmethod
    def needs_table_formatting(cli_config: Dict[str, Any]) -> bool:
        """Check if CLI needs table formatting capabilities."""
        commands = cli_config.get("commands", {})

        for cmd in commands.values():
            cmd_dict = _safe_to_dict(cmd)
            desc = str(cmd_dict.get("desc", cmd_dict.get("description", ""))).lower()

            # Look for table-related keywords
            table_keywords = [
                "table",
                "list",
                "show",
                "display",
                "view",
                "print",
                "format",
                "output",
                "report",
                "summary",
                "status",
                "info",
                "details",
            ]

            if any(keyword in desc for keyword in table_keywords):
                return True

            # Check options for table-like output formats
            options = cmd_dict.get("options", [])
            for opt in options:
                opt_dict = _safe_to_dict(opt)
                choices = opt_dict.get("choices", [])
                if any(
                    choice in ["table", "json", "csv", "yaml"] for choice in choices
                ):
                    return True

        return False

    @staticmethod
    def needs_progress_features(cli_config: Dict[str, Any]) -> bool:
        """Check if CLI needs progress bars, spinners, or loading indicators."""
        commands = cli_config.get("commands", {})

        for cmd in commands.values():
            cmd_dict = _safe_to_dict(cmd)
            desc = str(cmd_dict.get("desc", cmd_dict.get("description", ""))).lower()

            # Look for progress-related keywords
            progress_keywords = [
                "progress",
                "download",
                "upload",
                "install",
                "build",
                "compile",
                "process",
                "sync",
                "backup",
                "restore",
                "deploy",
                "migrate",
                "import",
                "export",
            ]

            if any(keyword in desc for keyword in progress_keywords):
                return True

            # Check for options that suggest long-running operations
            options = cmd_dict.get("options", [])
            for opt in options:
                opt_dict = _safe_to_dict(opt)
                opt_name = str(opt_dict.get("name", "")).lower()
                if opt_name in ["progress", "verbose", "quiet", "batch"]:
                    return True

        return False

    @staticmethod
    def needs_color_support(cli_config: Dict[str, Any]) -> bool:
        """Check if CLI explicitly needs color support."""
        # Check global color configuration
        if cli_config.get("colors") == False:
            return False  # Explicitly disabled

        commands = cli_config.get("commands", {})

        for cmd in commands.values():
            cmd_dict = _safe_to_dict(cmd)
            desc = str(cmd_dict.get("desc", cmd_dict.get("description", ""))).lower()

            # Look for visual/formatting keywords that benefit from colors
            color_keywords = ["error", "warning", "success", "status", "highlight"]
            if any(keyword in desc for keyword in color_keywords):
                return True

            # Check for color-related options
            options = cmd_dict.get("options", [])
            for opt in options:
                opt_dict = _safe_to_dict(opt)
                opt_name = str(opt_dict.get("name", "")).lower()
                if opt_name in ["color", "no-color", "colors"]:
                    return True

        # Default to supporting colors
        return cli_config.get("colors", True)

    @staticmethod
    def has_complex_types(cli_config: Dict[str, Any]) -> bool:
        """Check if CLI has complex type definitions (useful for TypeScript)."""
        commands = cli_config.get("commands", {})

        for cmd in commands.values():
            cmd_dict = _safe_to_dict(cmd)

            # Check arguments and options for complex types
            for items in [cmd_dict.get("args", []), cmd_dict.get("options", [])]:
                for item in items:
                    item_dict = _safe_to_dict(item)
                    item_type = item_dict.get("type", "string")

                    # Complex types that need TypeScript interfaces
                    complex_types = [
                        "object",
                        "dict",
                        "json",
                        "list",
                        "array",
                        "tuple",
                        "union",
                    ]
                    if item_type in complex_types:
                        return True

                    # Check for choices (enum-like types)
                    if item_dict.get("choices"):
                        return True

                    # Check for validation patterns
                    if item_dict.get("pattern") or item_dict.get("validator"):
                        return True

        return False

    @staticmethod
    def needs_file_operations(cli_config: Dict[str, Any]) -> bool:
        """Check if CLI needs file system operations."""
        commands = cli_config.get("commands", {})

        for cmd in commands.values():
            cmd_dict = _safe_to_dict(cmd)
            desc = str(cmd_dict.get("desc", cmd_dict.get("description", ""))).lower()

            # Look for file operation keywords
            file_keywords = [
                "file",
                "directory",
                "folder",
                "path",
                "read",
                "write",
                "create",
                "delete",
                "copy",
                "move",
                "rename",
                "save",
                "load",
                "import",
                "export",
                "backup",
            ]

            if any(keyword in desc for keyword in file_keywords):
                return True

            # Check arguments and options for file paths
            for items in [cmd_dict.get("args", []), cmd_dict.get("options", [])]:
                for item in items:
                    item_dict = _safe_to_dict(item)
                    item_type = item_dict.get("type", "")
                    item_name = str(item_dict.get("name", "")).lower()

                    if (
                        item_type in ["file", "path", "directory"]
                        or "file" in item_name
                        or "path" in item_name
                        or "dir" in item_name
                    ):
                        return True

        return False

    @staticmethod
    def has_nested_subcommands(cli_config: Dict[str, Any]) -> bool:
        """Check if CLI has nested subcommands (affects Commander.js setup complexity)."""
        commands = cli_config.get("commands", {})

        # Look for subcommands within commands
        for cmd in commands.values():
            cmd_dict = _safe_to_dict(cmd)
            if cmd_dict.get("subcommands") or cmd_dict.get("commands"):
                return True

        # Check if we have more than 3 top-level commands (suggests complexity)
        return len(commands) > 3

    @staticmethod
    def needs_commander_help_formatting(cli_config: Dict[str, Any]) -> bool:
        """Check if CLI needs enhanced Commander.js help formatting."""
        commands = cli_config.get("commands", {})

        # Check for complex help patterns that need custom formatting
        for cmd in commands.values():
            cmd_dict = _safe_to_dict(cmd)
            desc = str(cmd_dict.get("desc", cmd_dict.get("description", "")))

            # Look for multi-line descriptions or complex help text
            if len(desc) > 80 or "\n" in desc:
                return True

            # Check for complex command structure that benefits from custom help
            args = cmd_dict.get("args", [])
            options = cmd_dict.get("options", [])
            subcommands = cmd_dict.get("subcommands", {})

            if len(args) > 3 or len(options) > 5 or subcommands:
                return True

        # Check for header sections or command groups (indicates custom help)
        if cli_config.get("header_sections") or cli_config.get("command_groups"):
            return True

        return False