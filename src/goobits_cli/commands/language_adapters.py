"""
Language Adapters
=================

Language-specific adapters extracted from command_handler.j2 template.
Generate CLI command code for Python, Node.js, TypeScript, and Rust.
"""

from abc import ABC, abstractmethod
from .command_framework import CommandConfig, Command, Argument, Option, ArgumentType, OptionType


class BaseCommandAdapter(ABC):
    """Base class for language-specific command adapters."""
    
    @abstractmethod
    def generate_code(self, config: CommandConfig) -> str:
        """Generate CLI command code for the target language."""
        pass
    
    def _format_description(self, text: str) -> str:
        """Format description text for the target language."""
        return text.replace('"', '\\"').replace("'", "\\'")


class PythonCommandAdapter(BaseCommandAdapter):
    """Python CLI adapter using Click framework."""
    
    def generate_code(self, config: CommandConfig) -> str:
        """Generate Python Click CLI code."""
        code = self._generate_imports(config)
        code += "\n\n"
        code += self._generate_main_cli(config)
        code += "\n\n"
        code += self._generate_commands(config)
        code += "\n\n"
        code += self._generate_main_function(config)
        
        return code
    
    def _generate_imports(self, config: CommandConfig) -> str:
        """Generate Python imports."""
        imports = [
            "import sys",
            "import os",
            "from pathlib import Path",
            "import click",
            "from typing import Optional, List, Dict, Any"
        ]
        
        if config.hook_file:
            imports.append("import importlib.util")
            imports.append("import traceback")
        
        return "\n".join(imports)
    
    def _generate_main_cli(self, config: CommandConfig) -> str:
        """Generate main CLI group."""
        code = "@click.group()\n"
        
        # Add global options
        for option in config.global_options:
            code += self._generate_option_decorator(option)
        
        code += f"@click.pass_context\n"
        code += f"def cli(ctx, **kwargs):\n"
        code += f'    """{self._format_description(f"{config.project_name} CLI")}"""\n'
        code += f"    ctx.ensure_object(dict)\n"
        code += f"    ctx.obj.update(kwargs)\n"
        
        if config.hook_file:
            code += f"    ctx.obj['hook_file'] = '{config.hook_file}'\n"
        
        return code
    
    def _generate_commands(self, config: CommandConfig) -> str:
        """Generate all command functions."""
        code = ""
        
        for cmd_name, command in config.commands.items():
            code += self._generate_command(command, config)
            code += "\n\n"
        
        return code.rstrip()
    
    def _generate_command(self, command: Command, config: CommandConfig) -> str:
        """Generate a single command function."""
        code = f"@cli.command('{command.name}')\n"
        
        # Add arguments
        for arg in command.arguments:
            code += self._generate_argument_decorator(arg)
        
        # Add options  
        for option in command.options:
            code += self._generate_option_decorator(option)
        
        code += "@click.pass_context\n"
        code += f"def {command.name.replace('-', '_')}(ctx, **kwargs):\n"
        code += f'    """{self._format_description(command.description)}"""\n'
        
        # Hook execution
        if config.hook_file:
            code += "    try:\n"
            code += f"        hook_func = load_hook('{command.hook_name}', ctx.obj.get('hook_file', ''))\n"
            code += "        if hook_func:\n"
            code += "            result = hook_func(**kwargs)\n"
            code += "            if result is not None:\n"
            code += "                click.echo(result)\n"
            code += "        else:\n"
            code += f"            click.echo(f'Hook function {command.hook_name} not found', err=True)\n"
            code += "            sys.exit(1)\n"
            code += "    except Exception as e:\n"
            code += "        click.echo(f'Error executing command: {e}', err=True)\n"
            code += "        sys.exit(1)\n"
        else:
            code += f"    click.echo('Command {command.name} executed with: {{kwargs}}')\n"
        
        return code
    
    def _generate_argument_decorator(self, arg: Argument) -> str:
        """Generate Click argument decorator."""
        decorator = f"@click.argument('{arg.name}'"
        
        if arg.type != ArgumentType.STRING:
            type_map = {
                ArgumentType.INTEGER: "int",
                ArgumentType.FLOAT: "float", 
                ArgumentType.PATH: "click.Path()",
                ArgumentType.EMAIL: "str",
                ArgumentType.URL: "str"
            }
            if arg.type in type_map:
                decorator += f", type={type_map[arg.type]}"
        
        if not arg.required:
            decorator += ", required=False"
        
        if arg.multiple:
            decorator += ", nargs=-1"
        
        decorator += ")\n"
        return decorator
    
    def _generate_option_decorator(self, option: Option) -> str:
        """Generate Click option decorator."""
        short_flag = f", '-{option.short}'" if option.short else ""
        decorator = f"@click.option('--{option.name}'{short_flag}"
        
        # Type handling
        if option.type == OptionType.BOOLEAN:
            decorator += ", is_flag=True"
        elif option.type == OptionType.CHOICE and option.choices:
            choices_str = ", ".join([f"'{c}'" for c in option.choices])
            decorator += f", type=click.Choice([{choices_str}])"
        elif option.type != OptionType.STRING:
            type_map = {
                OptionType.INTEGER: "int",
                OptionType.FLOAT: "float",
                OptionType.PATH: "click.Path()",
                OptionType.FILE: "click.Path(exists=True, file_okay=True, dir_okay=False)",
                OptionType.DIRECTORY: "click.Path(exists=True, file_okay=False, dir_okay=True)"
            }
            if option.type in type_map:
                decorator += f", type={type_map[option.type]}"
        
        # Default value
        if option.default is not None:
            if isinstance(option.default, str):
                decorator += f", default='{option.default}'"
            else:
                decorator += f", default={option.default}"
        
        # Required flag
        if option.required:
            decorator += ", required=True"
        
        # Multiple values
        if option.multiple:
            decorator += ", multiple=True"
        
        # Help text
        decorator += f", help='{self._format_description(option.description)}'"
        
        decorator += ")\n"
        return decorator
    
    def _generate_main_function(self, config: CommandConfig) -> str:
        """Generate main function and hook loading utilities."""
        code = ""
        
        if config.hook_file:
            code += "def load_hook(hook_name: str, hook_file: str):\n"
            code += "    \"\"\"Load hook function from hook file.\"\"\"\n"
            code += "    if not hook_file or not os.path.exists(hook_file):\n"
            code += "        return None\n"
            code += "    \n"
            code += "    try:\n"
            code += "        spec = importlib.util.spec_from_file_location('cli_hooks', hook_file)\n"
            code += "        if not spec or not spec.loader:\n"
            code += "            return None\n"
            code += "        \n"
            code += "        module = importlib.util.module_from_spec(spec)\n"
            code += "        spec.loader.exec_module(module)\n"
            code += "        \n"
            code += "        return getattr(module, hook_name, None)\n"
            code += "    except Exception as e:\n"
            code += "        click.echo(f'Error loading hook {hook_name}: {e}', err=True)\n"
            code += "        return None\n"
            code += "\n\n"
        
        code += "if __name__ == '__main__':\n"
        code += "    cli()\n"
        
        return code


class NodeJSCommandAdapter(BaseCommandAdapter):
    """Node.js CLI adapter using Commander.js framework."""
    
    def generate_code(self, config: CommandConfig) -> str:
        """Generate Node.js Commander CLI code."""
        code = self._generate_imports(config)
        code += "\n\n"
        code += self._generate_main_program(config)
        code += "\n\n"
        code += self._generate_commands(config)
        code += "\n\n"
        code += self._generate_utilities(config)
        code += "\n\n"
        code += self._generate_execution(config)
        
        return code
    
    def _generate_imports(self, config: CommandConfig) -> str:
        """Generate Node.js imports."""
        imports = [
            "import { Command } from 'commander';",
            "import * as fs from 'fs';",
            "import * as path from 'path';"
        ]
        
        if config.hook_file:
            imports.append("import { fileURLToPath } from 'url';")
        
        return "\n".join(imports)
    
    def _generate_main_program(self, config: CommandConfig) -> str:
        """Generate main Commander program."""
        code = "const program = new Command();\n\n"
        code += f"program\n"
        code += f"  .name('{config.command_name}')\n"
        code += f"  .description('{self._format_description(config.project_name + ' CLI')}')\n"
        code += f"  .version('1.0.0');\n"
        
        # Add global options
        for option in config.global_options:
            code += self._generate_global_option(option)
        
        return code
    
    def _generate_commands(self, config: CommandConfig) -> str:
        """Generate all command definitions."""
        code = ""
        
        for cmd_name, command in config.commands.items():
            code += self._generate_command(command, config)
            code += "\n"
        
        return code.rstrip()
    
    def _generate_command(self, command: Command, config: CommandConfig) -> str:
        """Generate a single command definition."""
        code = f"program\n"
        code += f"  .command('{command.name}')\n"
        code += f"  .description('{self._format_description(command.description)}')\n"
        
        # Add arguments
        for arg in command.arguments:
            code += self._generate_argument(arg)
        
        # Add options
        for option in command.options:
            code += self._generate_option(option)
        
        # Add action handler
        code += f"  .action(async (...args) => {{\n"
        code += f"    try {{\n"
        
        if config.hook_file:
            code += f"      const hookFunc = await loadHook('{command.hook_name}', '{config.hook_file}');\n"
            code += f"      if (hookFunc) {{\n"
            code += f"        const options = args[args.length - 1];\n"
            code += f"        const result = await hookFunc(args.slice(0, -1), options);\n"
            code += f"        if (result !== undefined) {{\n"
            code += f"          console.log(result);\n"
            code += f"        }}\n"
            code += f"      }} else {{\n"
            code += f"        console.error(`Hook function {command.hook_name} not found`);\n"
            code += f"        process.exit(1);\n"
            code += f"      }}\n"
        else:
            code += f"      console.log('Command {command.name} executed with:', args);\n"
        
        code += f"    }} catch (error) {{\n"
        code += f"      console.error('Error executing command:', error.message);\n"
        code += f"      process.exit(1);\n"
        code += f"    }}\n"
        code += f"  }});\n"
        
        return code
    
    def _generate_argument(self, arg: Argument) -> str:
        """Generate Commander argument."""
        if arg.required:
            if arg.multiple:
                return f"  .argument('<{arg.name}...>', '{self._format_description(arg.description)}')\n"
            else:
                return f"  .argument('<{arg.name}>', '{self._format_description(arg.description)}')\n"
        else:
            if arg.multiple:
                return f"  .argument('[{arg.name}...]', '{self._format_description(arg.description)}')\n"
            else:
                return f"  .argument('[{arg.name}]', '{self._format_description(arg.description)}')\n"
    
    def _generate_option(self, option: Option) -> str:
        """Generate Commander option."""
        short_flag = f"-{option.short}, " if option.short else ""
        flag = f"{short_flag}--{option.name}"
        
        if option.type == OptionType.BOOLEAN:
            return f"  .option('{flag}', '{self._format_description(option.description)}')\n"
        else:
            value_placeholder = f"<{option.name}>"
            option_line = f"  .option('{flag} {value_placeholder}', '{self._format_description(option.description)}'"
            
            if option.default is not None:
                if isinstance(option.default, str):
                    option_line += f", '{option.default}'"
                else:
                    option_line += f", {str(option.default).lower()}"
            
            option_line += ")\n"
            return option_line
    
    def _generate_global_option(self, option: Option) -> str:
        """Generate global option."""
        return self._generate_option(option)
    
    def _generate_utilities(self, config: CommandConfig) -> str:
        """Generate utility functions."""
        code = ""
        
        if config.hook_file:
            code += "async function loadHook(hookName, hookFile) {\n"
            code += "  if (!hookFile || !fs.existsSync(hookFile)) {\n"
            code += "    return null;\n"
            code += "  }\n"
            code += "  \n"
            code += "  try {\n"
            code += "    const hookModule = await import(path.resolve(hookFile));\n"
            code += "    return hookModule[hookName] || hookModule.default?.[hookName];\n"
            code += "  } catch (error) {\n"
            code += "    console.error(`Error loading hook ${hookName}:`, error.message);\n"
            code += "    return null;\n"
            code += "  }\n"
            code += "}\n"
        
        return code
    
    def _generate_execution(self, config: CommandConfig) -> str:
        """Generate program execution."""
        return "program.parse();"


class TypeScriptCommandAdapter(BaseCommandAdapter):
    """TypeScript CLI adapter using Commander.js with type safety."""
    
    def generate_code(self, config: CommandConfig) -> str:
        """Generate TypeScript Commander CLI code."""
        code = self._generate_imports(config)
        code += "\n\n"
        code += self._generate_types(config)
        code += "\n\n"
        code += self._generate_main_program(config)
        code += "\n\n"
        code += self._generate_commands(config)
        code += "\n\n"
        code += self._generate_utilities(config)
        code += "\n\n"
        code += self._generate_execution(config)
        
        return code
    
    def _generate_imports(self, config: CommandConfig) -> str:
        """Generate TypeScript imports."""
        imports = [
            "import { Command, Option } from 'commander';",
            "import * as fs from 'fs';",
            "import * as path from 'path';"
        ]
        
        if config.hook_file:
            imports.append("import { fileURLToPath } from 'url';")
        
        return "\n".join(imports)
    
    def _generate_types(self, config: CommandConfig) -> str:
        """Generate TypeScript type definitions."""
        code = "interface CommandOptions {\n"
        
        # Collect all unique options
        all_options = set()
        for option in config.global_options:
            all_options.add((option.name, self._get_ts_type(option.type), not option.required))
        
        for command in config.commands.values():
            for option in command.options:
                all_options.add((option.name, self._get_ts_type(option.type), not option.required))
        
        for name, ts_type, optional in sorted(all_options):
            optional_marker = "?" if optional else ""
            code += f"  {name}{optional_marker}: {ts_type};\n"
        
        code += "}\n\n"
        
        if config.hook_file:
            code += "type HookFunction = (...args: any[]) => Promise<any> | any;\n\n"
            code += "interface HookModule {\n"
            code += "  [key: string]: HookFunction;\n"
            code += "}\n"
        
        return code
    
    def _get_ts_type(self, option_type: OptionType) -> str:
        """Get TypeScript type for option type."""
        type_map = {
            OptionType.STRING: "string",
            OptionType.INTEGER: "number",
            OptionType.FLOAT: "number",
            OptionType.BOOLEAN: "boolean",
            OptionType.CHOICE: "string",
            OptionType.PATH: "string",
            OptionType.FILE: "string",
            OptionType.DIRECTORY: "string"
        }
        return type_map.get(option_type, "string")
    
    def _generate_main_program(self, config: CommandConfig) -> str:
        """Generate main Commander program with types."""
        code = "const program = new Command();\n\n"
        code += f"program\n"
        code += f"  .name('{config.command_name}')\n"
        code += f"  .description('{self._format_description(config.project_name + ' CLI')}')\n"
        code += f"  .version('1.0.0');\n"
        
        # Add global options
        for option in config.global_options:
            code += self._generate_global_option(option)
        
        return code
    
    def _generate_commands(self, config: CommandConfig) -> str:
        """Generate all command definitions."""
        code = ""
        
        for cmd_name, command in config.commands.items():
            code += self._generate_command(command, config)
            code += "\n"
        
        return code.rstrip()
    
    def _generate_command(self, command: Command, config: CommandConfig) -> str:
        """Generate a single command definition."""
        code = f"program\n"
        code += f"  .command('{command.name}')\n"
        code += f"  .description('{self._format_description(command.description)}')\n"
        
        # Add arguments
        for arg in command.arguments:
            code += self._generate_argument(arg)
        
        # Add options
        for option in command.options:
            code += self._generate_option(option)
        
        # Add typed action handler
        code += f"  .action(async (...args: any[]) => {{\n"
        code += f"    try {{\n"
        
        if config.hook_file:
            code += f"      const hookFunc = await loadHook('{command.hook_name}', '{config.hook_file}');\n"
            code += f"      if (hookFunc) {{\n"
            code += f"        const options: CommandOptions = args[args.length - 1];\n"
            code += f"        const result = await hookFunc(args.slice(0, -1), options);\n"
            code += f"        if (result !== undefined) {{\n"
            code += f"          console.log(result);\n"
            code += f"        }}\n"
            code += f"      }} else {{\n"
            code += f"        console.error(`Hook function {command.hook_name} not found`);\n"
            code += f"        process.exit(1);\n"
            code += f"      }}\n"
        else:
            code += f"      console.log('Command {command.name} executed with:', args);\n"
        
        code += f"    }} catch (error: any) {{\n"
        code += f"      console.error('Error executing command:', error.message);\n"
        code += f"      process.exit(1);\n"
        code += f"    }}\n"
        code += f"  }});\n"
        
        return code
    
    def _generate_argument(self, arg: Argument) -> str:
        """Generate Commander argument."""
        if arg.required:
            if arg.multiple:
                return f"  .argument('<{arg.name}...>', '{self._format_description(arg.description)}')\n"
            else:
                return f"  .argument('<{arg.name}>', '{self._format_description(arg.description)}')\n"
        else:
            if arg.multiple:
                return f"  .argument('[{arg.name}...]', '{self._format_description(arg.description)}')\n"
            else:
                return f"  .argument('[{arg.name}]', '{self._format_description(arg.description)}')\n"
    
    def _generate_option(self, option: Option) -> str:
        """Generate Commander option."""
        short_flag = f"-{option.short}, " if option.short else ""
        flag = f"{short_flag}--{option.name}"
        
        if option.type == OptionType.BOOLEAN:
            return f"  .option('{flag}', '{self._format_description(option.description)}')\n"
        else:
            value_placeholder = f"<{option.name}>"
            option_line = f"  .option('{flag} {value_placeholder}', '{self._format_description(option.description)}'"
            
            if option.default is not None:
                if isinstance(option.default, str):
                    option_line += f", '{option.default}'"
                else:
                    option_line += f", {str(option.default).lower()}"
            
            option_line += ")\n"
            return option_line
    
    def _generate_global_option(self, option: Option) -> str:
        """Generate global option."""
        return self._generate_option(option)
    
    def _generate_utilities(self, config: CommandConfig) -> str:
        """Generate utility functions."""
        code = ""
        
        if config.hook_file:
            code += "async function loadHook(hookName: string, hookFile: string): Promise<HookFunction | null> {\n"
            code += "  if (!hookFile || !fs.existsSync(hookFile)) {\n"
            code += "    return null;\n"
            code += "  }\n"
            code += "  \n"
            code += "  try {\n"
            code += "    const hookModule: HookModule = await import(path.resolve(hookFile));\n"
            code += "    return hookModule[hookName] || (hookModule as any).default?.[hookName] || null;\n"
            code += "  } catch (error: any) {\n"
            code += "    console.error(`Error loading hook ${hookName}:`, error.message);\n"
            code += "    return null;\n"
            code += "  }\n"
            code += "}\n"
        
        return code
    
    def _generate_execution(self, config: CommandConfig) -> str:
        """Generate program execution."""
        return "program.parse();"


class RustCommandAdapter(BaseCommandAdapter):
    """Rust CLI adapter using Clap framework."""
    
    def generate_code(self, config: CommandConfig) -> str:
        """Generate Rust Clap CLI code."""
        code = self._generate_imports(config)
        code += "\n\n"
        code += self._generate_structs(config)
        code += "\n\n"
        code += self._generate_main_function(config)
        code += "\n\n"
        code += self._generate_command_handlers(config)
        
        return code
    
    def _generate_imports(self, config: CommandConfig) -> str:
        """Generate Rust imports."""
        imports = [
            "use clap::{Parser, Subcommand, Args};",
            "use std::process;",
            "use std::path::PathBuf;"
        ]
        
        if config.hook_file:
            imports.extend([
                "use std::collections::HashMap;",
                "use anyhow::{Result, Context};"
            ])
        
        return "\n".join(imports)
    
    def _generate_structs(self, config: CommandConfig) -> str:
        """Generate Clap derive structs."""
        code = "#[derive(Parser)]\n"
        code += "#[command(name = \"{}\")]\n".format(config.command_name)
        code += "#[command(about = \"{}\", long_about = None)]\n".format(self._format_description(config.project_name + " CLI"))
        code += "struct Cli {\n"
        
        # Add global options
        for option in config.global_options:
            code += self._generate_global_option_field(option)
        
        code += "    #[command(subcommand)]\n"
        code += "    command: Commands,\n"
        code += "}\n\n"
        
        # Generate subcommands enum
        code += "#[derive(Subcommand)]\n"
        code += "enum Commands {\n"
        
        for cmd_name, command in config.commands.items():
            struct_name = self._to_pascal_case(command.name)
            code += f"    /// {self._format_description(command.description)}\n"
            code += f"    {struct_name}({struct_name}Args),\n"
        
        code += "}\n\n"
        
        # Generate command arg structs
        for cmd_name, command in config.commands.items():
            code += self._generate_command_struct(command)
            code += "\n"
        
        return code.rstrip()
    
    def _generate_command_struct(self, command: Command) -> str:
        """Generate Clap Args struct for a command."""
        struct_name = f"{self._to_pascal_case(command.name)}Args"
        
        code = "#[derive(Args)]\n"
        code += f"struct {struct_name} {{\n"
        
        # Add arguments
        for arg in command.arguments:
            code += self._generate_argument_field(arg)
        
        # Add options
        for option in command.options:
            code += self._generate_option_field(option)
        
        code += "}\n"
        return code
    
    def _generate_argument_field(self, arg: Argument) -> str:
        """Generate Clap argument field."""
        rust_type = self._get_rust_type(arg.type, arg.multiple, arg.required)
        
        field = f"    /// {self._format_description(arg.description)}\n"
        
        if arg.multiple:
            field += f"    #[arg(required = {str(arg.required).lower()})]\n"
        elif not arg.required:
            field += f"    #[arg(required = false)]\n"
        
        field += f"    {arg.name.replace('-', '_')}: {rust_type},\n"
        return field
    
    def _generate_option_field(self, option: Option) -> str:
        """Generate Clap option field."""
        rust_type = self._get_rust_type(option.type, option.multiple, not option.required)
        
        field = f"    /// {self._format_description(option.description)}\n"
        field += f"    #[arg(long"
        
        if option.short:
            field += f", short = '{option.short}'"
        
        if option.default is not None:
            if isinstance(option.default, str):
                field += f", default_value = \"{option.default}\""
            elif isinstance(option.default, bool):
                field += f", default_value_t = {str(option.default).lower()}"
            else:
                field += f", default_value_t = {option.default}"
        
        field += ")]\n"
        field += f"    {option.name.replace('-', '_')}: {rust_type},\n"
        return field
    
    def _generate_global_option_field(self, option: Option) -> str:
        """Generate global option field."""
        return self._generate_option_field(option)
    
    def _get_rust_type(self, arg_type, multiple: bool, optional: bool) -> str:
        """Get Rust type for argument/option."""
        base_type_map = {
            ArgumentType.STRING: "String",
            ArgumentType.INTEGER: "i32",
            ArgumentType.FLOAT: "f64",
            ArgumentType.BOOLEAN: "bool",
            ArgumentType.PATH: "PathBuf",
            ArgumentType.EMAIL: "String",
            ArgumentType.URL: "String",
            OptionType.STRING: "String",
            OptionType.INTEGER: "i32",
            OptionType.FLOAT: "f64",
            OptionType.BOOLEAN: "bool",
            OptionType.CHOICE: "String",
            OptionType.PATH: "PathBuf",
            OptionType.FILE: "PathBuf",
            OptionType.DIRECTORY: "PathBuf"
        }
        
        base_type = base_type_map.get(arg_type, "String")
        
        if multiple:
            rust_type = f"Vec<{base_type}>"
        else:
            rust_type = base_type
        
        if optional and not multiple:
            rust_type = f"Option<{rust_type}>"
        
        return rust_type
    
    def _generate_main_function(self, config: CommandConfig) -> str:
        """Generate main function."""
        code = "fn main() {\n"
        code += "    let cli = Cli::parse();\n\n"
        
        code += "    let result = match cli.command {\n"
        
        for cmd_name, command in config.commands.items():
            struct_name = self._to_pascal_case(command.name)
            handler_name = f"handle_{command.name.replace('-', '_')}"
            
            if config.hook_file:
                code += f"        Commands::{struct_name}(args) => {handler_name}(args, \"{config.hook_file}\"),\n"
            else:
                code += f"        Commands::{struct_name}(args) => {handler_name}(args),\n"
        
        code += "    };\n\n"
        
        code += "    if let Err(err) = result {\n"
        code += "        eprintln!(\"Error: {}\", err);\n"
        code += "        process::exit(1);\n"
        code += "    }\n"
        code += "}\n"
        
        return code
    
    def _generate_command_handlers(self, config: CommandConfig) -> str:
        """Generate command handler functions."""
        code = ""
        
        for cmd_name, command in config.commands.items():
            struct_name = f"{self._to_pascal_case(command.name)}Args"
            handler_name = f"handle_{command.name.replace('-', '_')}"
            
            if config.hook_file:
                code += f"fn {handler_name}(args: {struct_name}, hook_file: &str) -> Result<()> {{\n"
                code += f"    // Execute hook function '{command.hook_name}'\n"
                code += f"    println!(\"Executing {command.name} with hook file: {{}}\", hook_file);\n"
                code += f"    println!(\"Args: {{:#?}}\", args);\n"
                code += f"    Ok(())\n"
            else:
                code += f"fn {handler_name}(args: {struct_name}) -> Result<(), Box<dyn std::error::Error>> {{\n"
                code += f"    println!(\"Executing {command.name}\");\n"
                code += f"    println!(\"Args: {{:#?}}\", args);\n"
                code += f"    Ok(())\n"
            
            code += "}\n\n"
        
        return code.rstrip()
    
    def _to_pascal_case(self, snake_str: str) -> str:
        """Convert snake_case or kebab-case to PascalCase."""
        components = snake_str.replace('-', '_').split('_')
        return ''.join(word.capitalize() for word in components)
    
    def _format_description(self, text: str) -> str:
        """Override to handle Rust string escaping."""
        return text.replace('"', '\\"')