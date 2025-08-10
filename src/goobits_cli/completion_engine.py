#!/usr/bin/env python3
"""
Universal completion engine for goobits-generated CLIs
Reads goobits.yaml at runtime and provides context-aware completions
"""

import os
import sys
import yaml
import json
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple


class CompletionEngine:
    """Universal completion engine that parses goobits.yaml at runtime"""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize completion engine with goobits.yaml path"""
        self.config_path = config_path or self._find_config()
        self.config = self._load_config()
        
    def _find_config(self) -> str:
        """Find goobits.yaml file in current directory or parent directories"""
        current = Path.cwd()
        
        # Search up the directory tree
        for parent in [current] + list(current.parents):
            config_file = parent / "goobits.yaml"
            if config_file.exists():
                return str(config_file)
                
        # Fallback to current directory
        return str(Path.cwd() / "goobits.yaml")
    
    def _load_config(self) -> Dict[str, Any]:
        """Load and parse goobits.yaml configuration"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
        except Exception:
            return {}
    
    def get_completions(self, shell: str, current_line: str, cursor_pos: Optional[int] = None) -> List[str]:
        """Get completions for the current shell context"""
        try:
            # Parse the command line
            tokens = self._parse_command_line(current_line, cursor_pos)
            
            # Special case: if the line ends with a space after an option, 
            # we should be completing the option value
            if current_line.endswith(' ') and len(tokens) > 0 and tokens[-1].startswith('-'):
                # Add empty token to represent the word being completed
                tokens.append('')
            
            context = self._analyze_context(tokens)
            
            # Generate completions based on context
            completions = self._generate_completions(context)
            
            return sorted(set(completions))
        except Exception:
            return []
    
    def _parse_command_line(self, line: str, cursor_pos: Optional[int] = None) -> List[str]:
        """Parse command line into tokens, handling quoted arguments"""
        if cursor_pos is None:
            cursor_pos = len(line)
            
        # Extract the relevant part of the line up to cursor
        relevant_line = line[:cursor_pos]
        
        # Simple tokenization (could be enhanced for complex cases)
        tokens = []
        current_token = ""
        in_quotes = False
        quote_char = None
        
        for char in relevant_line:
            if char in ['"', "'"] and not in_quotes:
                in_quotes = True
                quote_char = char
                current_token += char
            elif char == quote_char and in_quotes:
                in_quotes = False
                current_token += char
                quote_char = None
            elif char.isspace() and not in_quotes:
                if current_token:
                    tokens.append(current_token)
                    current_token = ""
            else:
                current_token += char
        
        # Add final token if exists
        if current_token:
            tokens.append(current_token)
            
        return tokens
    
    def _analyze_context(self, tokens: List[str]) -> Dict[str, Any]:
        """Analyze the current completion context"""
        if not tokens:
            return {"type": "command", "level": 0}
            
        # Skip the program name
        if len(tokens) > 0:
            tokens = tokens[1:]
            
        if not tokens:
            return {"type": "command", "level": 0}
            
        context = {
            "type": "unknown",
            "level": 0,
            "current_command": None,
            "subcommand": None,
            "last_token": tokens[-1] if tokens else "",
            "previous_token": tokens[-2] if len(tokens) > 1 else "",
        }
        
        # Determine command/subcommand context first
        cli_commands = self.config.get("cli", {}).get("commands", {})
        
        # Find the current command in the token list
        for i, token in enumerate(tokens):
            if token in cli_commands:
                context["current_command"] = token
                break
        
        # Check if we're completing an option
        if context["last_token"].startswith("-"):
            context["type"] = "option"
            return context
            
        # Check if previous token was an option that expects a value
        if context["previous_token"].startswith("-") and not context["last_token"].startswith("-"):
            context["type"] = "option_value"
            context["option"] = context["previous_token"]
            return context
        
        if len(tokens) == 1:
            # Completing top-level command
            context["type"] = "command"
            context["level"] = 0
            context["partial"] = tokens[0]
        elif len(tokens) >= 2 and tokens[0] in cli_commands:
            # We have a valid command, check for subcommands
            command_config = cli_commands[tokens[0]]
            context["current_command"] = tokens[0]
            
            if "subcommands" in command_config and len(tokens) == 2 and not tokens[1].startswith("-"):
                context["type"] = "subcommand"
                context["level"] = 1
                context["partial"] = tokens[1]
            elif "subcommands" in command_config and len(tokens) > 2 and tokens[1] in command_config["subcommands"]:
                context["type"] = "option" if context["type"] == "unknown" else context["type"]
                context["subcommand"] = tokens[1]
                context["level"] = 2
            else:
                # We're in option context for this command
                context["type"] = "option" if context["type"] == "unknown" else context["type"]
                context["level"] = 1
        elif len(tokens) >= 1:
            # First token is not a recognized command, treat as partial command
            context["type"] = "command"
            context["level"] = 0
            context["partial"] = tokens[0]
        
        return context
    
    def _generate_completions(self, context: Dict[str, Any]) -> List[str]:
        """Generate completions based on context"""
        completions = []
        
        if context["type"] == "command":
            completions.extend(self._get_command_completions(context))
        elif context["type"] == "subcommand":
            completions.extend(self._get_subcommand_completions(context))
        elif context["type"] == "option":
            completions.extend(self._get_option_completions(context))
        elif context["type"] == "option_value":
            completions.extend(self._get_option_value_completions(context))
            
        # Filter by partial match if applicable
        partial = context.get("partial", "")
        if partial:
            completions = [c for c in completions if c.startswith(partial)]
            
        return completions
    
    def _get_command_completions(self, context: Dict[str, Any]) -> List[str]:
        """Get top-level command completions"""
        commands = []
        
        # CLI commands from config
        cli_commands = self.config.get("cli", {}).get("commands", {})
        commands.extend(cli_commands.keys())
        
        # Built-in commands
        builtin_commands = ["help", "version"]
        
        # Check if upgrade is enabled
        cli_config = self.config.get("cli", {})
        if cli_config.get("enable_upgrade_command", True):
            builtin_commands.append("upgrade")
            
        commands.extend(builtin_commands)
        
        return commands
    
    def _get_subcommand_completions(self, context: Dict[str, Any]) -> List[str]:
        """Get subcommand completions"""
        command = context.get("current_command")
        if not command:
            return []
            
        cli_commands = self.config.get("cli", {}).get("commands", {})
        command_config = cli_commands.get(command, {})
        
        subcommands = command_config.get("subcommands", {})
        return list(subcommands.keys())
    
    def _get_option_completions(self, context: Dict[str, Any]) -> List[str]:
        """Get option completions for current command/subcommand"""
        options = []
        
        # Global options
        global_options = self.config.get("cli", {}).get("options", [])
        for opt in global_options:
            options.append(f"--{opt['name']}")
            if opt.get("short"):
                options.append(f"-{opt['short']}")
        
        # Command-specific options
        command = context.get("current_command")
        if command:
            cli_commands = self.config.get("cli", {}).get("commands", {})
            command_config = cli_commands.get(command, {})
            
            # Check if we're in a subcommand
            subcommand = context.get("subcommand")
            if subcommand and "subcommands" in command_config:
                command_config = command_config["subcommands"].get(subcommand, {})
            
            command_options = command_config.get("options", [])
            for opt in command_options:
                options.append(f"--{opt['name']}")
                if opt.get("short"):
                    options.append(f"-{opt['short']}")
        
        # Standard options
        options.extend(["--help", "-h", "--version", "-V"])
        
        return options
    
    def _get_option_value_completions(self, context: Dict[str, Any]) -> List[str]:
        """Get completions for option values"""
        option = context.get("option", "").lstrip("-")
        
        # Find option configuration
        option_config = self._find_option_config(option, context)
        if not option_config:
            return []
        
        option_type = option_config.get("type", "str")
        
        # Handle different option types
        if option_type == "choice" and "choices" in option_config:
            return option_config["choices"]
        elif option_type == "file" or option in ["config", "file", "input"]:
            return self._get_file_completions()
        elif option_type == "dir" or option in ["directory", "dir", "output-dir"]:
            return self._get_directory_completions()
        elif option_type == "bool" or option_type == "flag":
            return ["true", "false"]
            
        return []
    
    def _find_option_config(self, option_name: str, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Find configuration for a specific option"""
        # Check global options
        global_options = self.config.get("cli", {}).get("options", [])
        for opt in global_options:
            if opt["name"] == option_name or opt.get("short") == option_name:
                return opt
        
        # Check command-specific options
        command = context.get("current_command")
        if command:
            cli_commands = self.config.get("cli", {}).get("commands", {})
            command_config = cli_commands.get(command, {})
            
            # Check if we're in a subcommand
            subcommand = context.get("subcommand")
            if subcommand and "subcommands" in command_config:
                command_config = command_config["subcommands"].get(subcommand, {})
            
            command_options = command_config.get("options", [])
            for opt in command_options:
                if opt["name"] == option_name or opt.get("short") == option_name:
                    return opt
        
        return None
    
    def _get_file_completions(self) -> List[str]:
        """Get file completions for current directory"""
        try:
            files = []
            for item in os.listdir("."):
                if os.path.isfile(item):
                    files.append(item)
            return files
        except Exception:
            return []
    
    def _get_directory_completions(self) -> List[str]:
        """Get directory completions for current directory"""
        try:
            dirs = []
            for item in os.listdir("."):
                if os.path.isdir(item):
                    dirs.append(item + "/")
            return dirs
        except Exception:
            return []


def main():
    """Main completion function - called by CLIs with --completion"""
    if len(sys.argv) < 3:
        sys.exit(1)
        
    shell = sys.argv[1]
    current_line = sys.argv[2]
    cursor_pos = int(sys.argv[3]) if len(sys.argv) > 3 else None
    
    engine = CompletionEngine()
    completions = engine.get_completions(shell, current_line, cursor_pos)
    
    # Output completions one per line
    for completion in completions:
        print(completion)


if __name__ == "__main__":
    main()