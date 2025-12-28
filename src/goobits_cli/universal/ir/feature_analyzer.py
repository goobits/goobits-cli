"""
Feature Analyzer for the Universal Template System.

This module analyzes Goobits configuration to determine which features
are required, enabling optimized CLI generation that excludes unused
dependencies and code.
"""

from typing import Dict, Any

from ...generation import _safe_to_dict
from ..utils import _safe_get_attr


class FeatureAnalyzer:
    """
    Analyzes configuration to determine required features for performance optimization.

    This class examines the configuration to determine which advanced features
    are actually needed, allowing generation of optimized CLI variants that
    exclude unused dependencies and code.
    """

    def analyze(self, config, config_filename: str = "goobits.yaml") -> Dict[str, Any]:
        """
        Analyze YAML config to determine required features for performance optimization.

        Args:
            config: Validated Goobits configuration
            config_filename: Name of the configuration file

        Returns:
            Dictionary with feature requirements analysis:
            {
                'rich_interface': bool,      # Needs rich_click formatting
                'interactive_mode': bool,    # Has interactive commands
                'completion_system': bool,   # Has completion subcommands
                'complex_parsing': bool,     # Has complex arguments/options
                'config_management': bool,   # Has config commands
                'async_features': bool,      # Uses async operations
                'plugin_system': bool        # Has plugin support
            }
        """
        config_dict = _safe_to_dict(config)
        cli_config = config_dict.get("cli", {})

        # Feature detection heuristics
        requirements = {
            "rich_interface": self._needs_rich_formatting(cli_config, config_dict),
            "interactive_mode": self._has_interactive_commands(cli_config),
            "completion_system": self._has_completion_subcommands(cli_config),
            "complex_parsing": self._has_complex_arguments(cli_config),
            "config_management": self._has_config_features(cli_config),
            "async_features": self._has_async_features(cli_config),
            "plugin_system": self._has_plugin_features(cli_config),
            # Enhanced granular feature detection
            "table_formatting": self._needs_table_formatting(cli_config),
            "progress_features": self._needs_progress_features(cli_config),
            "color_support": self._needs_color_support(cli_config),
            "complex_types": self._has_complex_types(cli_config),
            "file_operations": self._needs_file_operations(cli_config),
            # Node.js/TypeScript specific optimizations
            "subcommand_nesting": self._has_nested_subcommands(cli_config),
            "commander_help_formatting": self._needs_commander_help_formatting(
                cli_config
            ),
        }

        # CRITICAL FIX: rich_interface should be True if ANY rich-specific features are needed
        # This ensures CLIs that need table formatting, colors, or progress use rich_click
        rich_features = ["table_formatting", "progress_features", "color_support"]

        if any(requirements.get(feature, False) for feature in rich_features):
            requirements["rich_interface"] = True

        return requirements

    def _needs_rich_formatting(
        self, cli_config: Dict[str, Any], full_config: Dict[str, Any]
    ) -> bool:
        """
        Check if CLI needs rich formatting features.

        Conservative approach: prefer rich formatting if uncertain, but detect
        simple CLIs that can use basic Click for better performance.
        """
        # Always use rich for complex CLIs or when explicitly configured
        commands = cli_config.get("commands", {})

        # Simple heuristic: CLIs with <= 2 commands and no styling can use basic click
        if len(commands) <= 2:
            # Check if any commands have complex help, tables, colors, etc.
            for cmd in commands.values():
                cmd_dict = _safe_to_dict(cmd)
                desc = cmd_dict.get("desc", cmd_dict.get("description", ""))

                # Look for rich markup patterns
                if any(
                    marker in str(desc).lower()
                    for marker in [
                        "[bold]",
                        "[italic]",
                        "[green]",
                        "[red]",
                        "[yellow]",
                        "[blue]",
                        "[dim]",
                        "[bright]",
                        "table",
                        "progress",
                        "spinner",
                    ]
                ):
                    return True

                # Check for complex options that might benefit from rich display
                options = cmd_dict.get("options", [])
                if len(options) > 5:  # Many options look better with rich
                    return True

        # Check for header sections or footer notes (rich-specific features)
        if cli_config.get("header_sections") or cli_config.get("footer_note"):
            return True

        # Check for colors configuration
        if cli_config.get("colors", True) == False:
            return False  # Explicitly disabled

        # Default to rich for complex CLIs (> 2 commands)
        return len(commands) > 2

    def _has_interactive_commands(self, cli_config: Dict[str, Any]) -> bool:
        """Check if CLI has interactive mode features."""
        features = cli_config.get("features", {})
        interactive_mode = features.get("interactive_mode", {})
        return interactive_mode.get("enabled", False)

    def _has_completion_subcommands(self, cli_config: Dict[str, Any]) -> bool:
        """Check if CLI needs shell completion system."""
        completion = cli_config.get("completion", {})
        return completion.get("enabled", True)  # Default enabled

    def _has_complex_arguments(self, cli_config: Dict[str, Any]) -> bool:
        """Check if CLI has complex argument parsing needs."""
        commands = cli_config.get("commands", {})

        for cmd in commands.values():
            cmd_dict = _safe_to_dict(cmd)

            # Check for complex argument patterns
            args = cmd_dict.get("args", [])
            options = cmd_dict.get("options", [])

            # Complex if many arguments/options
            if len(args) > 3 or len(options) > 4:
                return True

            # Complex if has advanced types
            for arg in args:
                arg_dict = _safe_to_dict(arg)
                if arg_dict.get("type") in ["choice", "file", "path"]:
                    return True
                if arg_dict.get("multiple", False):
                    return True

            for opt in options:
                opt_dict = _safe_to_dict(opt)
                if opt_dict.get("type") in ["choice", "file", "path"]:
                    return True
                if opt_dict.get("multiple", False):
                    return True
                if opt_dict.get("choices"):
                    return True

        return False

    def _has_config_features(self, cli_config: Dict[str, Any]) -> bool:
        """Check if CLI uses configuration management."""
        commands = cli_config.get("commands", {})
        return any("config" in str(cmd_name).lower() for cmd_name in commands.keys())

    def _has_async_features(self, cli_config: Dict[str, Any]) -> bool:
        """Check if CLI uses async features."""
        # For now, assume no async features unless explicitly marked
        features = cli_config.get("features", {})
        return features.get("async", {}).get("enabled", False)

    def _has_plugin_features(self, cli_config: Dict[str, Any]) -> bool:
        """Check if CLI has plugin system."""
        features = cli_config.get("features", {})
        return features.get("plugins", {}).get("enabled", False)

    def _needs_table_formatting(self, cli_config: Dict[str, Any]) -> bool:
        """Check if CLI needs table formatting capabilities."""
        commands = cli_config.get("commands", {})

        for cmd in commands.values():
            cmd_dict = _safe_to_dict(cmd)
            desc = str(cmd_dict.get("desc", cmd_dict.get("description", ""))).lower()

            # Look for table-related keywords
            table_keywords = [
                "table",
                "list",
                "tabulate",
                "grid",
                "column",
                "row",
                "csv",
                "export",
            ]
            if any(keyword in desc for keyword in table_keywords):
                return True

            # Check options that suggest table output
            options = cmd_dict.get("options", [])
            for opt in options:
                opt_dict = _safe_to_dict(opt)
                opt_name = str(opt_dict.get("name", "")).lower()
                opt_desc = str(
                    opt_dict.get("desc", opt_dict.get("description", ""))
                ).lower()

                if any(
                    keyword in f"{opt_name} {opt_desc}" for keyword in table_keywords
                ):
                    return True

                # Format options often indicate table output
                if "format" in opt_name and opt_dict.get("choices", []):
                    choices = [str(c).lower() for c in opt_dict.get("choices", [])]
                    if any(fmt in choices for fmt in ["table", "csv", "json"]):
                        return True

        return False

    def _needs_progress_features(self, cli_config: Dict[str, Any]) -> bool:
        """Check if CLI needs progress bars, spinners, or loading indicators."""
        commands = cli_config.get("commands", {})

        for cmd in commands.values():
            cmd_dict = _safe_to_dict(cmd)
            desc = str(cmd_dict.get("desc", cmd_dict.get("description", ""))).lower()

            # Look for progress-related keywords
            progress_keywords = [
                "progress",
                "loading",
                "spinner",
                "wait",
                "processing",
                "download",
                "upload",
                "install",
                "build",
            ]
            if any(keyword in desc for keyword in progress_keywords):
                return True

            # Check for verbose/quiet options that suggest long-running operations
            options = cmd_dict.get("options", [])
            for opt in options:
                opt_dict = _safe_to_dict(opt)
                opt_name = str(opt_dict.get("name", "")).lower()

                if opt_name in ["verbose", "quiet", "progress", "no-progress"]:
                    return True

        return False

    def _needs_color_support(self, cli_config: Dict[str, Any]) -> bool:
        """Check if CLI explicitly needs color support."""
        # Check global color configuration
        if cli_config.get("colors") == False:
            return False  # Explicitly disabled

        commands = cli_config.get("commands", {})

        for cmd in commands.values():
            cmd_dict = _safe_to_dict(cmd)
            desc = str(cmd_dict.get("desc", cmd_dict.get("description", ""))).lower()

            # Look for color-related keywords
            color_keywords = ["color", "highlight", "syntax", "theme", "style"]
            if any(keyword in desc for keyword in color_keywords):
                return True

            # Check for color options
            options = cmd_dict.get("options", [])
            for opt in options:
                opt_dict = _safe_to_dict(opt)
                opt_name = str(opt_dict.get("name", "")).lower()

                if any(
                    keyword in opt_name
                    for keyword in ["color", "no-color", "theme", "style"]
                ):
                    return True

        # Default to True if not explicitly disabled
        return cli_config.get("colors", True)

    def _has_complex_types(self, cli_config: Dict[str, Any]) -> bool:
        """Check if CLI has complex type definitions (useful for TypeScript)."""
        commands = cli_config.get("commands", {})

        for cmd in commands.values():
            cmd_dict = _safe_to_dict(cmd)

            # Check arguments and options for complex types
            for items in [cmd_dict.get("args", []), cmd_dict.get("options", [])]:
                for item in items:
                    item_dict = _safe_to_dict(item)

                    # Complex types that benefit from TypeScript interfaces
                    if item_dict.get("type") in [
                        "choice",
                        "file",
                        "path",
                        "json",
                        "object",
                    ]:
                        return True
                    if item_dict.get("multiple", False):
                        return True
                    if item_dict.get("choices"):
                        return True

                    # Check for validation rules
                    if any(
                        key in item_dict
                        for key in ["min", "max", "pattern", "validate"]
                    ):
                        return True

        return False

    def _needs_file_operations(self, cli_config: Dict[str, Any]) -> bool:
        """Check if CLI needs file system operations."""
        commands = cli_config.get("commands", {})

        for cmd in commands.values():
            cmd_dict = _safe_to_dict(cmd)
            desc = str(cmd_dict.get("desc", cmd_dict.get("description", ""))).lower()

            # Look for file operation keywords
            file_keywords = [
                "file",
                "path",
                "directory",
                "folder",
                "read",
                "write",
                "copy",
                "move",
                "delete",
                "create",
                "save",
                "load",
                "import",
                "export",
            ]
            if any(keyword in desc for keyword in file_keywords):
                return True

            # Check for file/path type arguments/options
            for items in [cmd_dict.get("args", []), cmd_dict.get("options", [])]:
                for item in items:
                    item_dict = _safe_to_dict(item)
                    if item_dict.get("type") in ["file", "path"]:
                        return True

        return False

    def _has_nested_subcommands(self, cli_config: Dict[str, Any]) -> bool:
        """Check if CLI has nested subcommands (affects Commander.js setup complexity)."""
        commands = cli_config.get("commands", {})

        # Look for subcommands within commands
        for cmd in commands.values():
            cmd_dict = _safe_to_dict(cmd)
            if cmd_dict.get("subcommands") or cmd_dict.get("commands"):
                return True

        # Check if we have more than 3 top-level commands (suggests complexity)
        return len(commands) > 3

    def _needs_commander_help_formatting(self, cli_config: Dict[str, Any]) -> bool:
        """Check if CLI needs enhanced Commander.js help formatting."""
        commands = cli_config.get("commands", {})

        # Check for complex help patterns that need custom formatting
        for cmd in commands.values():
            cmd_dict = _safe_to_dict(cmd)
            desc = str(cmd_dict.get("desc", cmd_dict.get("description", "")))

            # Look for multi-line descriptions or complex help text
            if len(desc) > 80 or "\n" in desc:
                return True

            # Check for many options that would benefit from grouped help
            options = cmd_dict.get("options", [])
            if len(options) > 6:
                return True

            # Check for examples or usage patterns
            if any(
                keyword in desc.lower()
                for keyword in ["example", "usage", "note:", "warning:"]
            ):
                return True

        # Check for global help customization
        if cli_config.get("help_sections") or cli_config.get("examples"):
            return True

        return False
