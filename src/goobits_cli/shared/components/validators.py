"""Specific validators for Goobits CLI configurations.

This module implements validators based on the schemas created by Agents A and B,
providing comprehensive validation for command structures, hooks, options,
error codes, types, and more.
"""

import re
import sys
from pathlib import Path
from typing import Any, Dict, List

try:
    from .validation_framework import (
        BaseValidator, ValidationContext, ValidationResult, ValidationMode
    )
except ImportError:
    # Handle direct execution
    from validation_framework import (
        BaseValidator, ValidationContext, ValidationResult, ValidationMode
    )

# Import schemas for validation
sys.path.append(str(Path(__file__).parent.parent.parent / "src"))
try:
    from goobits_cli.schemas import (
        CommandSchema, ArgumentSchema, OptionSchema, GoobitsConfigSchema,
        CLISchema, CommandGroupSchema
    )
except ImportError:
    # Fallback for standalone usage
    CommandSchema = ArgumentSchema = OptionSchema = None
    GoobitsConfigSchema = CLISchema = CommandGroupSchema = None


class CommandValidator(BaseValidator):
    """Validates command names, descriptions, and structure based on Agent A's command-structure.yaml."""
    
    def __init__(self):
        super().__init__("CommandValidator")
        
    def validate(self, context: ValidationContext) -> ValidationResult:
        result = ValidationResult()
        
        # Get CLI configuration
        cli_config = self.get_field_value(context.config, 'cli', {})
        if not cli_config:
            result.add_error("No CLI configuration found", "cli")
            return result
            
        commands = self.get_field_value(cli_config, 'commands', {})
        if not commands:
            result.add_warning("No commands defined", "cli.commands")
            return result
            
        # Validate each command
        for cmd_name, cmd_config in commands.items():
            self._validate_command(cmd_name, cmd_config, f"cli.commands.{cmd_name}", 
                                 result, context)
            
        # Validate command groups if present
        command_groups = self.get_field_value(cli_config, 'command_groups', [])
        self._validate_command_groups(command_groups, commands, result)
        
        # Validate default command logic
        self._validate_default_commands(commands, result)
        
        return result
    
    def _validate_command(self, name: str, config: Any, field_path: str, 
                         result: ValidationResult, context: ValidationContext) -> None:
        """Validate a single command definition."""
        
        # Validate command name (continue validation even if name is invalid)
        name_is_valid = self.validate_identifier(name, field_path, result, 
                                      allow_hyphens=True, language=context.language)
        
        # Continue validation even if command name is invalid to collect all errors
            
        # Check for command name conventions
        if len(name) > 30:
            result.add_warning(
                f"Command name '{name}' is quite long ({len(name)} characters)",
                field_path,
                "Consider using a shorter, more memorable name"
            )
        
        # Validate required fields
        desc = self.get_field_value(config, 'desc')
        if not desc:
            result.add_error("Command description is required", f"{field_path}.desc")
        elif len(desc) < 10:
            result.add_warning(
                f"Command description is very short: '{desc}'",
                f"{field_path}.desc",
                "Consider adding more detail to help users understand the command"
            )
        elif len(desc) > 200:
            result.add_warning(
                f"Command description is very long ({len(desc)} characters)",
                f"{field_path}.desc", 
                "Consider moving detailed explanations to help text or documentation"
            )
        
        # Validate icon format if present
        icon = self.get_field_value(config, 'icon')
        if icon and not self._is_valid_icon(icon):
            result.add_warning(
                f"Icon '{icon}' may not display correctly",
                f"{field_path}.icon",
                "Use standard emoji or Unicode symbols"
            )
        
        # Validate lifecycle setting
        lifecycle = self.get_field_value(config, 'lifecycle', 'standard')
        if lifecycle not in ['standard', 'managed']:
            result.add_error(
                f"Invalid lifecycle '{lifecycle}'. Must be 'standard' or 'managed'",
                f"{field_path}.lifecycle"
            )
        
        # Validate subcommands recursively
        subcommands = self.get_field_value(config, 'subcommands', {})
        for sub_name, sub_config in subcommands.items():
            self._validate_command(sub_name, sub_config, 
                                 f"{field_path}.subcommands.{sub_name}", 
                                 result, context)
    
    def _validate_command_groups(self, groups: List[Any], commands: Dict[str, Any], 
                                result: ValidationResult) -> None:
        """Validate command groups structure."""
        if not groups:
            return
            
        group_names = set()
        all_grouped_commands = set()
        
        for i, group in enumerate(groups):
            group_name = self.get_field_value(group, 'name')
            group_commands = self.get_field_value(group, 'commands', [])
            
            field_path = f"cli.command_groups[{i}]"
            
            # Validate group name
            if not group_name:
                result.add_error("Command group name is required", f"{field_path}.name")
                continue
                
            if group_name in group_names:
                result.add_error(
                    f"Duplicate command group name: '{group_name}'",
                    f"{field_path}.name"
                )
            group_names.add(group_name)
            
            # Validate group commands exist
            for cmd_name in group_commands:
                if cmd_name not in commands:
                    result.add_error(
                        f"Command '{cmd_name}' in group '{group_name}' does not exist",
                        f"{field_path}.commands"
                    )
                all_grouped_commands.add(cmd_name)
        
        # Check for ungrouped commands
        ungrouped = set(commands.keys()) - all_grouped_commands
        if ungrouped and len(ungrouped) > 3:  # Only warn if many ungrouped commands
            result.add_warning(
                f"Commands not in any group: {', '.join(sorted(ungrouped))}",
                "cli.command_groups",
                "Consider organizing commands into logical groups"
            )
    
    def _validate_default_commands(self, commands: Dict[str, Any], result: ValidationResult) -> None:
        """Validate default command logic."""
        default_commands = []
        for cmd_name, config in commands.items():
            if self.get_field_value(config, 'is_default', False):
                default_commands.append(cmd_name)
        
        if len(default_commands) > 1:
            result.add_error(
                f"Multiple default commands defined: {', '.join(default_commands)}",
                "cli.commands",
                "Only one command should have is_default: true"
            )
    
    def _is_valid_icon(self, icon: str) -> bool:
        """Check if icon appears to be a valid Unicode emoji or symbol."""
        if not icon:
            return False
        # Basic check for emoji/Unicode symbols
        return len(icon.encode('utf-8')) != len(icon) or any(ord(c) > 127 for c in icon)


class ArgumentValidator(BaseValidator):
    """Validates argument definitions and requirements."""
    
    def __init__(self):
        super().__init__("ArgumentValidator")
        self.dependencies.add("CommandValidator")
        
    def validate(self, context: ValidationContext) -> ValidationResult:
        result = ValidationResult()
        
        cli_config = self.get_field_value(context.config, 'cli', {})
        commands = self.get_field_value(cli_config, 'commands', {})
        
        for cmd_name, cmd_config in commands.items():
            args = self.get_field_value(cmd_config, 'args', [])
            self._validate_command_arguments(args, f"cli.commands.{cmd_name}.args", 
                                           result, context)
            
            # Recursively validate subcommands
            subcommands = self.get_field_value(cmd_config, 'subcommands', {})
            for sub_name, sub_config in subcommands.items():
                sub_args = self.get_field_value(sub_config, 'args', [])
                self._validate_command_arguments(
                    sub_args, 
                    f"cli.commands.{cmd_name}.subcommands.{sub_name}.args",
                    result, context
                )
        
        return result
    
    def _validate_command_arguments(self, args: List[Any], field_path: str, 
                                  result: ValidationResult, context: ValidationContext) -> None:
        """Validate arguments for a specific command."""
        if not args:
            return
            
        seen_names = set()
        has_optional = False
        has_variadic = False
        
        for i, arg in enumerate(args):
            arg_path = f"{field_path}[{i}]"
            
            # Validate argument name
            name = self.get_field_value(arg, 'name')
            if not name:
                result.add_error("Argument name is required", f"{arg_path}.name")
                continue
                
            if name in seen_names:
                result.add_error(
                    f"Duplicate argument name: '{name}'",
                    f"{arg_path}.name"
                )
                continue
            seen_names.add(name)
            
            if not self.validate_identifier(name, f"{arg_path}.name", result, 
                                          allow_hyphens=False, language=context.language):
                continue
            
            # Validate description
            desc = self.get_field_value(arg, 'desc')
            if not desc:
                result.add_error("Argument description is required", f"{arg_path}.desc")
            elif len(desc) < 5:
                result.add_warning(
                    f"Argument description is very short: '{desc}'",
                    f"{arg_path}.desc"
                )
            
            # Validate argument order and requirements
            required = self.get_field_value(arg, 'required', True)
            nargs = self.get_field_value(arg, 'nargs')
            
            if not required:
                has_optional = True
            elif required and has_optional:
                result.add_error(
                    f"Required argument '{name}' cannot come after optional arguments",
                    f"{arg_path}.required",
                    "Move required arguments before optional ones"
                )
            
            # Validate nargs patterns
            if nargs:
                if nargs in ['*', '+'] and has_variadic:
                    result.add_error(
                        f"Only one variadic argument allowed, but '{name}' uses '{nargs}'",
                        f"{arg_path}.nargs"
                    )
                elif nargs in ['*', '+']:
                    has_variadic = True
                    if i < len(args) - 1:  # Not the last argument
                        result.add_error(
                            f"Variadic argument '{name}' must be the last argument",
                            f"{arg_path}.nargs"
                        )
                elif nargs == '?':
                    if not required:
                        result.add_warning(
                            f"Argument '{name}' is both optional and uses '?'",
                            f"{arg_path}.nargs",
                            "Consider using required=false instead of nargs='?'"
                        )
                elif isinstance(nargs, int) and nargs < 0:
                    result.add_error(
                        f"Invalid nargs value: {nargs}. Must be positive integer, '?', '*', or '+'",
                        f"{arg_path}.nargs"
                    )
            
            # Validate choices
            choices = self.get_field_value(arg, 'choices')
            if choices:
                if not isinstance(choices, list) or len(choices) == 0:
                    result.add_error(
                        "Argument choices must be a non-empty list",
                        f"{arg_path}.choices"
                    )
                elif len(choices) == 1:
                    result.add_warning(
                        f"Argument '{name}' has only one choice: {choices[0]}",
                        f"{arg_path}.choices",
                        "Consider using a default value instead"
                    )
                elif len(set(choices)) != len(choices):
                    result.add_warning(
                        f"Argument '{name}' has duplicate choices",
                        f"{arg_path}.choices"
                    )


class HookValidator(BaseValidator):
    """Validates hook function signatures and interfaces based on Agent A's hook-interface.yaml."""
    
    def __init__(self):
        super().__init__("HookValidator") 
        self.dependencies.add("CommandValidator")
        
    def validate(self, context: ValidationContext) -> ValidationResult:
        result = ValidationResult()
        
        cli_config = self.get_field_value(context.config, 'cli', {})
        commands = self.get_field_value(cli_config, 'commands', {})
        
        # Check for hook file existence if specified
        hooks_path = self.get_field_value(context.config, 'hooks_path')
        if hooks_path and context.working_dir:
            full_path = Path(context.working_dir) / hooks_path
            if not full_path.exists():
                result.add_warning(
                    f"Hooks file not found: {hooks_path}",
                    "hooks_path",
                    "Hook file will be created during generation"
                )
        
        # Validate hook naming conventions
        self._validate_hook_naming(commands, result, context)
        
        # Validate hook parameter patterns
        self._validate_hook_parameters(commands, result, context)
        
        return result
    
    def _validate_hook_naming(self, commands: Dict[str, Any], result: ValidationResult, 
                            context: ValidationContext) -> None:
        """Validate hook naming conventions."""
        expected_hooks = set()
        
        def collect_hooks(cmds: Dict[str, Any], prefix: str = ""):
            for cmd_name, cmd_config in cmds.items():
                # Generate expected hook name
                if prefix:
                    hook_name = f"on_{prefix}_{cmd_name}"
                else:
                    hook_name = f"on_{cmd_name}"
                
                expected_hooks.add(hook_name)
                
                # Check for naming convention compliance
                if not self._is_valid_hook_name(hook_name, context.language):
                    result.add_warning(
                        f"Hook name '{hook_name}' may not follow {context.language} conventions",
                        f"commands.{cmd_name}",
                        self._suggest_hook_name(hook_name, context.language)
                    )
                
                # Recursively check subcommands
                subcommands = self.get_field_value(cmd_config, 'subcommands', {})
                if subcommands:
                    sub_prefix = f"{prefix}_{cmd_name}" if prefix else cmd_name
                    collect_hooks(subcommands, sub_prefix)
        
        collect_hooks(commands)
        
        # Store expected hooks for other validators
        context.shared_data['expected_hooks'] = expected_hooks
    
    def _validate_hook_parameters(self, commands: Dict[str, Any], result: ValidationResult,
                                context: ValidationContext) -> None:
        """Validate hook parameter patterns."""
        
        def validate_command_params(cmd_name: str, cmd_config: Any, hook_name: str):
            # Get arguments and options that will be passed to hook
            args = self.get_field_value(cmd_config, 'args', [])
            options = self.get_field_value(cmd_config, 'options', [])
            
            # Validate parameter count
            total_params = len(args) + len(options)
            if total_params > 20:
                result.add_warning(
                    f"Command '{cmd_name}' has many parameters ({total_params})",
                    f"commands.{cmd_name}",
                    "Consider grouping related options or using configuration files"
                )
            
            # Language-specific parameter validation
            self._validate_language_specific_params(hook_name, args, options, result, context)
        
        for cmd_name, cmd_config in commands.items():
            hook_name = f"on_{cmd_name}"
            validate_command_params(cmd_name, cmd_config, hook_name)
    
    def _is_valid_hook_name(self, hook_name: str, language: str) -> bool:
        """Check if hook name follows language conventions."""
        if language == "python":
            return re.match(r'^[a-z_][a-z0-9_]*$', hook_name) is not None
        elif language in ["nodejs", "typescript"]:
            # camelCase conversion
            camel_case = self._to_camel_case(hook_name)
            return re.match(r'^[a-z][a-zA-Z0-9]*$', camel_case) is not None
        elif language == "rust":
            return re.match(r'^[a-z_][a-z0-9_]*$', hook_name) is not None
        return True
    
    def _suggest_hook_name(self, hook_name: str, language: str) -> str:
        """Suggest proper hook name for language."""
        if language in ["nodejs", "typescript"]:
            return f"Use camelCase: '{self._to_camel_case(hook_name)}'"
        return f"Use snake_case: '{hook_name.lower().replace('-', '_')}'"
    
    def _to_camel_case(self, snake_str: str) -> str:
        """Convert snake_case to camelCase."""
        components = snake_str.split('_')
        return components[0] + ''.join(word.capitalize() for word in components[1:])
    
    def _validate_language_specific_params(self, hook_name: str, args: List[Any], 
                                         options: List[Any], result: ValidationResult,
                                         context: ValidationContext) -> None:
        """Validate language-specific parameter patterns."""
        if context.language == "rust":
            # Rust prefers borrowing references
            if len(args) + len(options) > 10:
                result.add_info(
                    f"Hook '{hook_name}' has many parameters - consider using a struct",
                    suggestion="Group related parameters into a configuration struct"
                )
        elif context.language == "typescript":
            # TypeScript benefits from typed interfaces
            result.add_info(
                f"Hook '{hook_name}' will have TypeScript interface generated",
                suggestion="Parameter types will be inferred from option definitions"
            )


class OptionValidator(BaseValidator):
    """Validates option definitions and defaults."""
    
    def __init__(self):
        super().__init__("OptionValidator")
        self.dependencies.add("TypeValidator")  # Will be created next
        
    def validate(self, context: ValidationContext) -> ValidationResult:
        result = ValidationResult()
        
        cli_config = self.get_field_value(context.config, 'cli', {})
        commands = self.get_field_value(cli_config, 'commands', {})
        
        # Validate global options
        global_options = self.get_field_value(cli_config, 'options', [])
        self._validate_options(global_options, "cli.options", result, context)
        
        # Validate command options
        for cmd_name, cmd_config in commands.items():
            options = self.get_field_value(cmd_config, 'options', [])
            self._validate_options(options, f"cli.commands.{cmd_name}.options", 
                                 result, context)
            
            # Validate subcommand options
            subcommands = self.get_field_value(cmd_config, 'subcommands', {})
            for sub_name, sub_config in subcommands.items():
                sub_options = self.get_field_value(sub_config, 'options', [])
                self._validate_options(
                    sub_options, 
                    f"cli.commands.{cmd_name}.subcommands.{sub_name}.options",
                    result, context
                )
        
        return result
    
    def _validate_options(self, options: List[Any], field_path: str, 
                         result: ValidationResult, context: ValidationContext) -> None:
        """Validate a list of options."""
        if not options:
            return
            
        seen_names = set()
        seen_short = set()
        
        for i, option in enumerate(options):
            option_path = f"{field_path}[{i}]"
            
            # Validate option name
            name = self.get_field_value(option, 'name')
            if not name:
                result.add_error("Option name is required", f"{option_path}.name")
                continue
                
            if name in seen_names:
                result.add_error(
                    f"Duplicate option name: '{name}'",
                    f"{option_path}.name"
                )
                continue
            seen_names.add(name)
            
            # Validate name format
            if not re.match(r'^[a-z][a-z0-9-]*[a-z0-9]$', name) and len(name) > 1:
                result.add_warning(
                    f"Option name '{name}' should use lowercase with hyphens",
                    f"{option_path}.name",
                    f"Consider '{name.lower().replace('_', '-')}'"
                )
            
            # Validate short option
            short = self.get_field_value(option, 'short')
            if short:
                if len(short) != 1:
                    result.add_error(
                        f"Short option must be single character, got: '{short}'",
                        f"{option_path}.short"
                    )
                elif short in seen_short:
                    result.add_error(
                        f"Duplicate short option: '{short}'",
                        f"{option_path}.short"
                    )
                elif not short.isalpha():
                    result.add_warning(
                        f"Short option '{short}' is not a letter",
                        f"{option_path}.short",
                        "Use alphabetic characters for better compatibility"
                    )
                seen_short.add(short)
            
            # Validate description
            desc = self.get_field_value(option, 'desc')
            if not desc:
                result.add_error("Option description is required", f"{option_path}.desc")
            elif len(desc) < 5:
                result.add_warning(
                    f"Option description is very short: '{desc}'",
                    f"{option_path}.desc"
                )
            
            # Validate type
            option_type = self.get_field_value(option, 'type', 'str')
            self._validate_option_type(option_type, option_path, result, context)
            
            # Validate default value
            default = self.get_field_value(option, 'default')
            if default is not None:
                self._validate_default_value(default, option_type, option_path, result)
            
            # Validate choices
            choices = self.get_field_value(option, 'choices')
            if choices is not None:  # Check for existence, not truthiness
                self._validate_option_choices(choices, default, option_type, 
                                            option_path, result)
            
            # Validate multiple flag
            multiple = self.get_field_value(option, 'multiple', False)
            if multiple and option_type == 'flag':
                result.add_error(
                    "Flag options cannot have multiple=true",
                    f"{option_path}.multiple"
                )
    
    def _validate_option_type(self, option_type: str, field_path: str, 
                            result: ValidationResult, context: ValidationContext) -> None:
        """Validate option type."""
        valid_types = {
            'str', 'string', 'int', 'integer', 'float', 'number',
            'bool', 'boolean', 'flag', 'choice', 'file', 'dir', 'path'
        }
        
        if option_type not in valid_types:
            result.add_error(
                f"Invalid option type: '{option_type}'",
                f"{field_path}.type",
                f"Valid types: {', '.join(sorted(valid_types))}"
            )
        
        # Language-specific type warnings
        if context.language == "rust" and option_type in ['integer', 'number']:
            result.add_info(
                f"Type '{option_type}' will be mapped to i32 in Rust",
                f"{field_path}.type",
                "Use 'int' for consistency or specify bit width if needed"
            )
    
    def _validate_default_value(self, default: Any, option_type: str, 
                              field_path: str, result: ValidationResult) -> None:
        """Validate default value matches option type."""
        if option_type in ['flag', 'bool', 'boolean']:
            if not isinstance(default, bool):
                result.add_error(
                    f"Default value for boolean option must be true/false, got: {default}",
                    f"{field_path}.default"
                )
        elif option_type in ['int', 'integer']:
            if not isinstance(default, int):
                try:
                    int(default)
                except (ValueError, TypeError):
                    result.add_error(
                        f"Default value for integer option must be a number, got: {default}",
                        f"{field_path}.default"
                    )
        elif option_type in ['float', 'number']:
            if not isinstance(default, (int, float)):
                try:
                    float(default)
                except (ValueError, TypeError):
                    result.add_error(
                        f"Default value for numeric option must be a number, got: {default}",
                        f"{field_path}.default"
                    )
    
    def _validate_option_choices(self, choices: Any, default: Any, option_type: str,
                               field_path: str, result: ValidationResult) -> None:
        """Validate option choices."""
        choices_are_valid = True
        
        if not isinstance(choices, list):
            result.add_error(
                "Option choices must be a list",
                f"{field_path}.choices"
            )
            choices_are_valid = False
            
        elif len(choices) == 0:
            result.add_error(
                "Option choices cannot be empty",
                f"{field_path}.choices"
            )
            choices_are_valid = False
            
        # Only perform these checks if choices are valid
        if choices_are_valid and isinstance(choices, list):
            if len(choices) == 1:
                result.add_warning(
                    "Option has only one choice - consider using a default value instead",
                    f"{field_path}.choices"
                )
            
            # Check for duplicates
            if len(set(choices)) != len(choices):
                result.add_warning(
                    "Option choices contain duplicates",
                    f"{field_path}.choices"
                )
                
            # Check if default is in choices
            if default is not None and default not in choices:
                result.add_error(
                    f"Default value '{default}' is not in choices: {choices}",
                    f"{field_path}.default"
                )
        # If choices are invalid but we still have a default, validate that the default concept makes sense
        elif default is not None and not choices_are_valid:
            # Still report default validation issue even with invalid choices
            result.add_error(
                f"Default value '{default}' cannot be validated against invalid choices",
                f"{field_path}.default"
            )


class ErrorCodeValidator(BaseValidator):
    """Validates error codes and exit codes based on Agent B's error-codes.yaml."""
    
    def __init__(self):
        super().__init__("ErrorCodeValidator")
        
    def validate(self, context: ValidationContext) -> ValidationResult:
        result = ValidationResult()
        
        # Define standard exit codes from the schema
        standard_exit_codes = {
            0: "SUCCESS",
            1: "GENERAL_ERROR", 
            2: "MISUSE",
            3: "CONFIG_ERROR",
            4: "HOOK_ERROR",
            5: "PLUGIN_ERROR",
            6: "DEPENDENCY_ERROR",
            7: "NETWORK_ERROR",
            70: "SOFTWARE_ERROR",
            77: "PERMISSION_ERROR",
            78: "OS_FILE_MISSING",
            130: "CANCELLED"
        }
        
        # Check if configuration uses any error handling
        self._validate_error_patterns(context.config, result, context)
        
        # Provide guidance on error handling
        if context.mode == ValidationMode.DEV:
            result.add_info(
                "Consider implementing structured error handling",
                suggestion="Use standard exit codes for consistent CLI behavior"
            )
            
            # Add standard exit codes to shared data for other validators
            context.shared_data['standard_exit_codes'] = standard_exit_codes
        
        return result
    
    def _validate_error_patterns(self, config: Any, result: ValidationResult,
                               context: ValidationContext) -> None:
        """Validate error handling patterns in configuration."""
        
        # Check for error-related configuration
        validation_config = self.get_field_value(config, 'validation', {})
        if validation_config:
            # Validate validation settings
            if 'check_disk_space' in validation_config:
                min_space = self.get_field_value(validation_config, 'minimum_disk_space_mb', 100)
                if min_space < 10:
                    result.add_warning(
                        f"Minimum disk space ({min_space}MB) is very low",
                        "validation.minimum_disk_space_mb",
                        "Consider at least 50MB for typical CLI operations"
                    )
                elif min_space > 1000:
                    result.add_warning(
                        f"Minimum disk space ({min_space}MB) is quite high",
                        "validation.minimum_disk_space_mb",
                        "Most CLIs don't need more than 100MB"
                    )


class TypeValidator(BaseValidator):
    """Validates option types and constraints based on Agent B's option-types.yaml."""
    
    def __init__(self):
        super().__init__("TypeValidator")
        
    def validate(self, context: ValidationContext) -> ValidationResult:
        result = ValidationResult()
        
        # Type mapping for different languages from the schema
        type_mappings = {
            'string': {
                'python': 'str',
                'nodejs': 'String', 
                'typescript': 'string',
                'rust': 'String'
            },
            'integer': {
                'python': 'int',
                'nodejs': 'Number',
                'typescript': 'number', 
                'rust': 'i32'
            },
            'float': {
                'python': 'float',
                'nodejs': 'Number',
                'typescript': 'number',
                'rust': 'f64'
            },
            'boolean': {
                'python': 'bool',
                'nodejs': 'Boolean',
                'typescript': 'boolean',
                'rust': 'bool'
            }
        }
        
        # Store type mappings for other validators
        context.shared_data['type_mappings'] = type_mappings
        
        # Validate type consistency
        self._validate_type_consistency(context.config, result, context, type_mappings)
        
        return result
    
    def _validate_type_consistency(self, config: Any, result: ValidationResult,
                                 context: ValidationContext, type_mappings: Dict[str, Dict[str, str]]) -> None:
        """Validate type consistency across the configuration."""
        
        # Get all options from CLI config
        cli_config = self.get_field_value(config, 'cli', {})
        if not cli_config:
            return
            
        options = []
        
        # Collect global options
        global_options = self.get_field_value(cli_config, 'options', [])
        options.extend(global_options)
        
        # Collect command options
        commands = self.get_field_value(cli_config, 'commands', {})
        for cmd_name, cmd_config in commands.items():
            cmd_options = self.get_field_value(cmd_config, 'options', [])
            options.extend(cmd_options)
        
        # Validate each option type
        for option in options:
            option_type = self.get_field_value(option, 'type', 'str')
            self._validate_single_type(option_type, option, result, context, type_mappings)
    
    def _validate_single_type(self, option_type: str, option: Any, result: ValidationResult,
                            context: ValidationContext, type_mappings: Dict[str, Dict[str, str]]) -> None:
        """Validate a single option type."""
        
        # Normalize type name
        normalized_type = self._normalize_type(option_type)
        
        if normalized_type not in type_mappings:
            return  # Let OptionValidator handle invalid types
            
        # Check language-specific considerations
        target_type = type_mappings[normalized_type].get(context.language)
        if not target_type:
            result.add_warning(
                f"Type '{option_type}' may not be well supported in {context.language}",
                suggestion="Consider using standard types like string, integer, boolean"
            )
        
        # Validate constraints based on type
        self._validate_type_constraints(normalized_type, option, result)
    
    def _normalize_type(self, type_name: str) -> str:
        """Normalize type names to standard forms."""
        type_map = {
            'str': 'string',
            'int': 'integer', 
            'bool': 'boolean',
            'number': 'float'
        }
        return type_map.get(type_name.lower(), type_name.lower())
    
    def _validate_type_constraints(self, type_name: str, option: Any, result: ValidationResult) -> None:
        """Validate type-specific constraints."""
        
        if type_name == 'integer':
            # Check for reasonable integer constraints
            default = self.get_field_value(option, 'default')
            if isinstance(default, int):
                if default < -2147483648 or default > 2147483647:
                    result.add_warning(
                        f"Default integer value {default} may not fit in 32-bit integers",
                        suggestion="Consider using string type for very large numbers"
                    )
        
        elif type_name == 'string':
            # Check for string length considerations
            choices = self.get_field_value(option, 'choices', [])
            if choices:
                max_len = max(len(str(choice)) for choice in choices) if choices else 0
                if max_len > 100:
                    result.add_warning(
                        f"Choice values are very long (max {max_len} characters)",
                        suggestion="Consider using shorter identifiers with descriptions"
                    )


class ConfigValidator(BaseValidator):
    """Validates configuration values and formats."""
    
    def __init__(self):
        super().__init__("ConfigValidator")
        
    def validate(self, context: ValidationContext) -> ValidationResult:
        result = ValidationResult()
        
        # Validate basic configuration structure
        self._validate_basic_structure(context.config, result)
        
        # Validate language-specific configuration
        self._validate_language_config(context.config, result, context)
        
        # Validate installation configuration
        self._validate_installation_config(context.config, result)
        
        # Validate paths and file references
        self._validate_paths(context.config, result, context)
        
        return result
    
    def _validate_basic_structure(self, config: Any, result: ValidationResult) -> None:
        """Validate basic configuration structure."""
        
        required_fields = ['package_name', 'command_name', 'display_name', 'description']
        for field in required_fields:
            value = self.get_field_value(config, field)
            if not value:
                result.add_error(f"Required field '{field}' is missing", field)
            elif not isinstance(value, str) or len(value.strip()) == 0:
                result.add_error(f"Field '{field}' must be a non-empty string", field)
        
        # Validate package name format
        package_name = self.get_field_value(config, 'package_name', '')
        if package_name and not re.match(r'^[a-z][a-z0-9-]*[a-z0-9]$', package_name):
            result.add_error(
                f"Package name '{package_name}' should use lowercase letters, numbers, and hyphens only",
                'package_name',
                "Example: 'my-awesome-cli'"
            )
        
        # Validate command name
        command_name = self.get_field_value(config, 'command_name', '')
        if command_name and not re.match(r'^[a-z][a-z0-9-]*[a-z0-9]$', command_name):
            result.add_error(
                f"Command name '{command_name}' should use lowercase letters, numbers, and hyphens only",
                'command_name'
            )
    
    def _validate_language_config(self, config: Any, result: ValidationResult,
                                context: ValidationContext) -> None:
        """Validate language-specific configuration."""
        
        language = self.get_field_value(config, 'language', 'python')
        valid_languages = ['python', 'nodejs', 'typescript', 'rust']
        
        if language not in valid_languages:
            result.add_error(
                f"Invalid language '{language}'. Must be one of: {', '.join(valid_languages)}",
                'language'
            )
            return
        
        # Validate Python configuration
        if language == 'python':
            python_config = self.get_field_value(config, 'python', {})
            if python_config:
                min_version = self.get_field_value(python_config, 'minimum_version', '3.8')
                max_version = self.get_field_value(python_config, 'maximum_version', '3.13')
                
                try:
                    min_parts = [int(x) for x in min_version.split('.')]
                    max_parts = [int(x) for x in max_version.split('.')]
                    
                    if min_parts >= max_parts:
                        result.add_error(
                            f"Minimum Python version {min_version} >= maximum version {max_version}",
                            'python.minimum_version'
                        )
                except ValueError:
                    result.add_error(
                        "Python version must be in format 'major.minor'",
                        'python.minimum_version'
                    )
    
    def _validate_installation_config(self, config: Any, result: ValidationResult) -> None:
        """Validate installation configuration."""
        
        installation = self.get_field_value(config, 'installation', {})
        if not installation:
            result.add_error("Installation configuration is required", 'installation')
            return
        
        # Validate required installation fields
        pypi_name = self.get_field_value(installation, 'pypi_name')
        if not pypi_name:
            result.add_error("PyPI package name is required", 'installation.pypi_name')
        elif not re.match(r'^[a-zA-Z0-9]([a-zA-Z0-9._-]*[a-zA-Z0-9])?$', pypi_name):
            result.add_error(
                f"PyPI name '{pypi_name}' contains invalid characters",
                'installation.pypi_name',
                "Use letters, numbers, hyphens, underscores, and dots only"
            )
        
        # Validate extras configuration
        extras = self.get_field_value(installation, 'extras', {})
        if extras:
            self._validate_extras(extras, result)
    
    def _validate_extras(self, extras: Any, result: ValidationResult) -> None:
        """Validate extras configuration."""
        
        valid_extra_types = ['python', 'npm', 'apt', 'cargo']
        
        for extra_type, packages in extras.items():
            if extra_type not in valid_extra_types:
                result.add_warning(
                    f"Unknown extra type '{extra_type}'",
                    f'installation.extras.{extra_type}',
                    f"Valid types: {', '.join(valid_extra_types)}"
                )
                continue
            
            if not isinstance(packages, list):
                result.add_error(
                    f"Extras '{extra_type}' must be a list",
                    f'installation.extras.{extra_type}'
                )
                continue
            
            # Validate package names based on type
            for package in packages:
                self._validate_package_name(extra_type, package, result)
    
    def _validate_package_name(self, package_type: str, package_name: str, result: ValidationResult) -> None:
        """Validate individual package names."""
        
        if not isinstance(package_name, str) or not package_name.strip():
            result.add_error(
                f"Package name in {package_type} extras cannot be empty",
                f'installation.extras.{package_type}'
            )
            return
        
        if package_type == 'python':
            # Python package names (extras)
            if not re.match(r'^[a-zA-Z][a-zA-Z0-9_-]*$', package_name):
                result.add_warning(
                    f"Python extra '{package_name}' may not be valid",
                    f'installation.extras.{package_type}'
                )
        elif package_type == 'npm':
            # NPM package names
            if package_name.startswith('@') and '/' in package_name:
                # Scoped package
                scope, name = package_name[1:].split('/', 1)
                if not re.match(r'^[a-z0-9-~][a-z0-9-._~]*$', scope):
                    result.add_warning(
                        f"NPM scope '{scope}' may not be valid",
                        f'installation.extras.{package_type}'
                    )
    
    def _validate_paths(self, config: Any, result: ValidationResult, context: ValidationContext) -> None:
        """Validate file paths and references."""
        
        # Validate CLI output path - now required
        cli_output_path = self.get_field_value(config, 'cli_output_path')
        if not cli_output_path:
            result.add_error(
                "cli_output_path is required to prevent root directory pollution",
                'cli_output_path',
                "Specify explicit output path like 'src/my_package/cli.py'"
            )
        else:
            if not cli_output_path.endswith('.py'):
                result.add_warning(
                    f"CLI output path '{cli_output_path}' should end with .py",
                    'cli_output_path'
                )
            
            # Prevent root directory generation
            path_obj = Path(cli_output_path)
            if len(path_obj.parts) == 1:  # File directly in root
                result.add_error(
                    f"CLI output path '{cli_output_path}' cannot be in root directory",
                    'cli_output_path',
                    "Use subdirectory like 'src/my_package/cli.py'"
                )
            
            # Check if directory exists (if working directory is available)
            if context.working_dir:
                full_path = Path(context.working_dir) / cli_output_path
                parent_dir = full_path.parent
                if not parent_dir.exists():
                    result.add_warning(
                        f"Output directory does not exist: {parent_dir}",
                        'cli_output_path',
                        "Directory will be created during generation"
                    )


class CompletionValidator(BaseValidator):
    """Validates shell completion patterns."""
    
    def __init__(self):
        super().__init__("CompletionValidator")
        self.dependencies.add("CommandValidator")
        self.dependencies.add("OptionValidator")
        
    def validate(self, context: ValidationContext) -> ValidationResult:
        result = ValidationResult()
        
        # Check for completion-friendly patterns
        cli_config = self.get_field_value(context.config, 'cli', {})
        commands = self.get_field_value(cli_config, 'commands', {})
        
        # Analyze command structure for completion
        self._analyze_completion_patterns(commands, result)
        
        # Provide completion optimization suggestions
        if context.is_dev_mode():
            self._suggest_completion_optimizations(commands, result, context)
        
        return result
    
    def _analyze_completion_patterns(self, commands: Dict[str, Any], result: ValidationResult) -> None:
        """Analyze command patterns for shell completion optimization."""
        
        total_commands = len(commands)
        commands_with_choices = 0
        commands_with_files = 0
        
        for cmd_name, cmd_config in commands.items():
            options = self.get_field_value(cmd_config, 'options', [])
            
            for option in options:
                # Count options with choices (good for completion)
                if self.get_field_value(option, 'choices'):
                    commands_with_choices += 1
                
                # Count file/directory options (need path completion)
                option_type = self.get_field_value(option, 'type', 'str')
                if option_type in ['file', 'dir', 'path']:
                    commands_with_files += 1
        
        # Provide completion insights
        if commands_with_choices > 0:
            result.add_info(
                f"{commands_with_choices} options have predefined choices (good for completion)"
            )
        
        if commands_with_files > 0:
            result.add_info(
                f"{commands_with_files} options use file/directory completion"
            )
        
        if total_commands > 20:
            result.add_info(
                f"Large number of commands ({total_commands}) - consider command grouping for better completion"
            )
    
    def _suggest_completion_optimizations(self, commands: Dict[str, Any], result: ValidationResult,
                                        context: ValidationContext) -> None:
        """Suggest completion optimizations."""
        
        # Suggest adding choices for common patterns
        for cmd_name, cmd_config in commands.items():
            options = self.get_field_value(cmd_config, 'options', [])
            
            for option in options:
                name = self.get_field_value(option, 'name', '')
                option_type = self.get_field_value(option, 'type', 'str')
                choices = self.get_field_value(option, 'choices')
                
                # Suggest choices for common option patterns
                if not choices and option_type == 'str':
                    if any(keyword in name.lower() for keyword in ['format', 'type', 'mode', 'level']):
                        result.add_info(
                            f"Option '{name}' might benefit from predefined choices",
                            suggestion="Add choices array for better shell completion"
                        )