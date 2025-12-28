"""

Rust-specific utilities for interactive mode in Goobits CLI Framework.

This module provides Rust-specific functionality for enhanced interactive

modes, including command parsing, tab completion, and integration with

Rust's ecosystem.

"""

import json
import re
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from .base import InteractiveEngine


@dataclass
class RustCommand:
    """Represents a parsed Rust command with proper type information."""

    name: str

    args: List[str]

    options: Dict[str, Any]

    flags: List[str]

    def to_clap_args(self) -> List[str]:
        """Convert to clap-compatible argument list."""

        result = [self.name]

        # Add flags first

        for flag in self.flags:
            result.append(f"--{flag}")

        # Add options

        for key, value in self.options.items():
            result.extend([f"--{key}", str(value)])

        # Add positional arguments

        result.extend(self.args)

        return result


@dataclass
class CargoInfo:
    """Information about the current Cargo project."""

    name: str

    version: str

    dependencies: List[str]

    features: List[str]

    bin_name: Optional[str] = None


class RustCommandParser:
    """

    Rust-specific command parser with proper error handling and type conversion.

    Handles Rust-style command parsing with Result-type error handling patterns

    and integration with Clap-style argument parsing.

    """

    def __init__(self):
        self.type_converters = {
            "String": str,
            "i32": int,
            "i64": int,
            "f32": float,
            "f64": float,
            "bool": lambda x: x.lower() in ("true", "1", "yes", "on"),
            "PathBuf": Path,
        }

    def parse_command(
        self, line: str, command_schema: Dict[str, Any]
    ) -> Tuple[Optional[RustCommand], Optional[str]]:
        """

        Parse a command line with Rust-specific type conversion and error handling.

        Args:

            line: Command line to parse

            command_schema: Schema defining expected arguments and options

        Returns:

            Tuple of (RustCommand, Optional[error_message])

        """

        parts = line.strip().split()

        if not parts:
            return None, "Empty command"

        command_name = parts[0]

        remaining_parts = parts[1:]

        try:
            # Parse options and flags

            options = {}

            flags = []

            args = []

            i = 0

            while i < len(remaining_parts):
                part = remaining_parts[i]

                if part.startswith("--"):
                    option_name = part[2:]

                    # Check if it's a flag or option with value

                    option_def = self._find_option_definition(
                        option_name, command_schema
                    )

                    if option_def and option_def.get("type") in ["bool", "flag"]:
                        flags.append(option_name)

                        i += 1

                    else:
                        # Option with value

                        if i + 1 < len(remaining_parts):
                            option_value = remaining_parts[i + 1]

                            # Type conversion

                            if option_def:
                                rust_type = option_def.get("rust_type", "String")

                                try:
                                    converted_value = self._convert_value(
                                        option_value, rust_type
                                    )

                                    options[option_name] = converted_value

                                except ValueError as e:
                                    return (
                                        None,
                                        f"Invalid value for --{option_name}: {e}",
                                    )

                            else:
                                options[option_name] = option_value

                            i += 2

                        else:
                            return None, f"Option --{option_name} requires a value"

                elif part.startswith("-") and len(part) == 2:
                    # Short option

                    short_name = part[1]

                    option_def = self._find_short_option_definition(
                        short_name, command_schema
                    )

                    if option_def:
                        if option_def.get("type") in ["bool", "flag"]:
                            flags.append(option_def["name"])

                            i += 1

                        else:
                            if i + 1 < len(remaining_parts):
                                option_value = remaining_parts[i + 1]

                                rust_type = option_def.get("rust_type", "String")

                                try:
                                    converted_value = self._convert_value(
                                        option_value, rust_type
                                    )

                                    options[option_def["name"]] = converted_value

                                except ValueError as e:
                                    return None, f"Invalid value for -{short_name}: {e}"

                                i += 2

                            else:
                                return None, f"Option -{short_name} requires a value"

                    else:
                        return None, f"Unknown short option: -{short_name}"

                else:
                    # Positional argument

                    args.append(part)

                    i += 1

            # Validate required arguments

            required_args = command_schema.get("arguments", [])

            required_count = sum(
                1 for arg in required_args if arg.get("required", True)
            )

            if len(args) < required_count:
                return (
                    None,
                    f"Command {command_name} requires at least {required_count} arguments, got {len(args)}",
                )

            # Type convert positional arguments

            converted_args = []

            for i, arg_value in enumerate(args):
                if i < len(required_args):
                    arg_def = required_args[i]

                    rust_type = arg_def.get("rust_type", "String")

                    try:
                        converted_value = self._convert_value(arg_value, rust_type)

                        converted_args.append(converted_value)

                    except ValueError as e:
                        return (
                            None,
                            f"Invalid value for argument {arg_def['name']}: {e}",
                        )

                else:
                    converted_args.append(arg_value)

            return (
                RustCommand(
                    name=command_name, args=converted_args, options=options, flags=flags
                ),
                None,
            )

        except Exception as e:
            return None, f"Parse error: {e}"

    def _find_option_definition(
        self, option_name: str, schema: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Find option definition in command schema."""

        for option in schema.get("options", []):
            if option["name"] == option_name:
                return dict(option)

        return None

    def _find_short_option_definition(
        self, short: str, schema: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Find option definition by short name."""

        for option in schema.get("options", []):
            if option.get("short") == short:
                return dict(option)

        return None

    def _convert_value(self, value: str, rust_type: str) -> Any:
        """Convert string value to appropriate Rust type."""

        base_type = rust_type.split("<")[0].split("::")[
            -1
        ]  # Handle Option<T> and paths

        if base_type in self.type_converters:
            converter = self.type_converters[base_type]

            return converter(value)

        else:
            return value  # Default to string


class RustCompletionProvider:
    """

    Provides tab completion for Rust CLI commands with cargo integration.

    Includes completion for:

    - Command names and subcommands

    - Option names and values

    - File paths and Rust-specific paths

    - Cargo commands and crate names

    """

    def __init__(self, cli_schema: Dict[str, Any]):
        self.cli_schema = cli_schema

        self.cargo_info = self._get_cargo_info()

        self.crate_cache: Optional[List[str]] = None

    def get_completions(self, text: str, line: str) -> List[str]:
        """

        Get tab completions for the current input.

        Args:

            text: The text being completed

            line: The full command line

        Returns:

            List of completion suggestions

        """

        parts = line.split()

        if not parts or (len(parts) == 1 and not line.endswith(" ")):
            # Complete command names

            return self._complete_commands(text)

        command_name = parts[0]

        command_schema = self._find_command_schema(command_name)

        if not command_schema:
            return []

        # Check if we're completing an option value

        if len(parts) >= 2 and parts[-2].startswith("-"):
            option_name = parts[-2].lstrip("-")

            return self._complete_option_value(option_name, text, command_schema)

        # Check if we're completing an option name

        if text.startswith("-"):
            return self._complete_option_names(text, command_schema)

        # Complete positional arguments or subcommands

        return self._complete_arguments(text, parts[1:], command_schema)

    def _complete_commands(self, text: str) -> List[str]:
        """Complete command names."""

        commands = []

        # Add CLI commands

        for command in self.cli_schema.get("commands", {}).keys():
            if command.startswith(text):
                commands.append(command)

        # Add built-in commands

        builtins = ["help", "exit", "quit", "history", "cargo"]

        for builtin in builtins:
            if builtin.startswith(text):
                commands.append(builtin)

        return sorted(commands)

    def _complete_option_names(
        self, text: str, command_schema: Dict[str, Any]
    ) -> List[str]:
        """Complete option names for a command."""

        options = []

        for option in command_schema.get("options", []):
            long_form = f"--{option['name']}"

            if long_form.startswith(text):
                options.append(long_form)

            if "short" in option:
                short_form = f"-{option['short']}"

                if short_form.startswith(text):
                    options.append(short_form)

        return sorted(options)

    def _complete_option_value(
        self, option_name: str, text: str, command_schema: Dict[str, Any]
    ) -> List[str]:
        """Complete values for a specific option."""

        option_def = None

        for opt in command_schema.get("options", []):
            if opt["name"] == option_name or opt.get("short") == option_name:
                option_def = opt

                break

        if not option_def:
            return []

        # Handle different option types

        option_type = option_def.get("type", "string")

        if "choices" in option_def:
            # Predefined choices

            return [
                choice for choice in option_def["choices"] if choice.startswith(text)
            ]

        elif option_type in ["path", "file", "directory"]:
            # File/directory completion

            return self._complete_paths(text, option_type)

        elif option_type == "bool":
            # Boolean completion

            return [val for val in ["true", "false"] if val.startswith(text.lower())]

        elif option_name in ["crate", "dependency"]:
            # Crate name completion

            return self._complete_crate_names(text)

        return []

    def _complete_arguments(
        self, text: str, current_args: List[str], command_schema: Dict[str, Any]
    ) -> List[str]:
        """Complete positional arguments."""

        arguments = command_schema.get("arguments", [])

        arg_index = len(current_args) - (1 if text else 0)

        if arg_index < len(arguments):
            arg_def = arguments[arg_index]

            arg_type = arg_def.get("type", "string")

            if "choices" in arg_def:
                return [
                    choice for choice in arg_def["choices"] if choice.startswith(text)
                ]

            elif arg_type in ["path", "file", "directory"]:
                return self._complete_paths(text, arg_type)

        # Check for subcommands

        subcommands = command_schema.get("subcommands", [])

        if subcommands:
            return [sub["name"] for sub in subcommands if sub["name"].startswith(text)]

        return []

    def _complete_paths(self, text: str, path_type: str) -> List[str]:
        """Complete file and directory paths."""

        try:
            if not text or text == ".":
                base_path = Path(".")

                prefix = ""

            else:
                path = Path(text)

                if text.endswith("/") or path.is_dir():
                    base_path = path

                    prefix = text

                else:
                    base_path = path.parent

                    prefix = str(path.parent) + "/" if path.parent != Path(".") else ""

            completions = []

            for item in base_path.iterdir():
                item_name = prefix + item.name

                if path_type == "directory" and not item.is_dir():
                    continue

                elif path_type == "file" and not item.is_file():
                    continue

                if item_name.startswith(text):
                    if item.is_dir():
                        completions.append(item_name + "/")

                    else:
                        completions.append(item_name)

            return sorted(completions)

        except (OSError, PermissionError):
            return []

    def _complete_crate_names(self, text: str) -> List[str]:
        """Complete crate names from crates.io (cached)."""

        if self.crate_cache is None:
            try:
                # Use cargo search to get popular crates (limited)

                result = subprocess.run(
                    ["cargo", "search", "--limit", "20", text or "a"],
                    capture_output=True,
                    text=True,
                    timeout=3,
                )

                if result.returncode == 0:
                    crates = []

                    for line in result.stdout.split("\n"):
                        if " = " in line:
                            crate_name = line.split(" = ")[0].strip()

                            crates.append(crate_name)

                    self.crate_cache = crates

                else:
                    self.crate_cache = []

            except (subprocess.TimeoutExpired, FileNotFoundError):
                self.crate_cache = []

        return [crate for crate in self.crate_cache if crate.startswith(text)]

    def _find_command_schema(self, command_name: str) -> Optional[Dict[str, Any]]:
        """Find command schema by name."""

        command = self.cli_schema.get("commands", {}).get(command_name)
        return dict(command) if command is not None else None

    def _get_cargo_info(self) -> Optional[CargoInfo]:
        """Get information about the current Cargo project."""

        try:
            result = subprocess.run(
                ["cargo", "metadata", "--format-version", "1"],
                capture_output=True,
                text=True,
                timeout=5,
            )

            if result.returncode == 0:
                metadata = json.loads(result.stdout)

                package = metadata.get("packages", [{}])[0]

                return CargoInfo(
                    name=package.get("name", ""),
                    version=package.get("version", ""),
                    dependencies=[
                        dep["name"] for dep in package.get("dependencies", [])
                    ],
                    features=list(package.get("features", {}).keys()),
                )

        except (subprocess.TimeoutExpired, json.JSONDecodeError, FileNotFoundError):
            pass

        return None


class RustHistoryManager:
    """

    Advanced history management for Rust interactive mode.

    Features:

    - Persistent history with configurable location

    - Smart deduplication

    - Search and filtering capabilities

    - Integration with rustyline editor

    """

    def __init__(self, history_file: Optional[str] = None):
        """

        Initialize history manager.

        Args:

            history_file: Path to history file. If None, uses default location.

        """

        self.history_file = self._get_history_file(history_file)

        self.max_entries = 1000

        self.history: List[str] = []

        # Load existing history

        self.load_history()

    def _get_history_file(self, custom_path: Optional[str]) -> Path:
        """Get the history file path."""

        if custom_path:
            return Path(custom_path)

        # Use XDG base directory or fallback

        config_dir = Path.home() / ".config" / "goobits-cli"

        config_dir.mkdir(parents=True, exist_ok=True)

        return config_dir / "rust_interactive_history.txt"

    def load_history(self):
        """Load history from file."""

        if self.history_file.exists():
            try:
                with open(self.history_file, encoding="utf-8") as f:
                    self.history = [line.strip() for line in f.readlines()]

                    # Keep only last max_entries

                    if len(self.history) > self.max_entries:
                        self.history = self.history[-self.max_entries :]

            except (OSError, UnicodeDecodeError) as e:
                print(f"Warning: Could not load history from {self.history_file}: {e}")

    def save_history(self):
        """Save history to file."""

        try:
            self.history_file.parent.mkdir(parents=True, exist_ok=True)

            with open(self.history_file, "w", encoding="utf-8") as f:
                for entry in self.history[-self.max_entries :]:
                    f.write(f"{entry}\n")

        except OSError as e:
            print(f"Warning: Could not save history to {self.history_file}: {e}")

    def add_entry(self, command: str):
        """

        Add a command to history with smart deduplication.

        Args:

            command: Command to add to history

        """

        command = command.strip()

        if not command or command.startswith(" "):
            return  # Skip empty commands or commands starting with space

        # Remove previous occurrence of the same command

        if command in self.history:
            self.history.remove(command)

        # Add to end

        self.history.append(command)

        # Trim if too long

        if len(self.history) > self.max_entries:
            self.history = self.history[-self.max_entries :]

    def search_history(
        self, pattern: str, case_sensitive: bool = False
    ) -> List[tuple[int, str]]:
        """

        Search history for commands matching pattern.

        Args:

            pattern: Search pattern (supports regex)

            case_sensitive: Whether search should be case sensitive

        Returns:

            List of (index, command) tuples

        """

        flags = 0 if case_sensitive else re.IGNORECASE

        try:
            regex = re.compile(pattern, flags)

            results = []

            for i, cmd in enumerate(self.history):
                if regex.search(cmd):
                    results.append((i, cmd))

            return results

        except re.error:
            # If regex is invalid, fall back to simple string matching

            pattern_lower = pattern.lower() if not case_sensitive else pattern

            results = []

            for i, cmd in enumerate(self.history):
                cmd_compare = cmd.lower() if not case_sensitive else cmd

                if pattern_lower in cmd_compare:
                    results.append((i, cmd))

            return results

    def get_recent_commands(self, count: int = 10) -> List[str]:
        """Get the most recent commands."""

        return self.history[-count:] if count <= len(self.history) else self.history[:]

    def clear_history(self):
        """Clear all history."""

        self.history.clear()

        if self.history_file.exists():
            try:
                self.history_file.unlink()

            except OSError:
                pass


class RustExpressionEvaluator:
    """

    Advanced Rust expression evaluator with compilation and execution.

    Features:

    - Compile and execute Rust expressions

    - Support for imports and dependencies

    - Error reporting with line numbers

    - Caching for repeated expressions

    """

    def __init__(self):
        self.temp_dir = Path("/tmp/rust_eval")

        self.temp_dir.mkdir(exist_ok=True)

        self.expression_cache = {}

        self.default_imports = [
            "use std::collections::*;",
            "use std::io::*;",
            "use std::fs::*;",
            "use std::path::*;",
        ]

    def evaluate_expression(
        self, expression: str, with_output: bool = True, timeout_seconds: int = 10
    ) -> dict:
        """

        Evaluate a Rust expression.

        Args:

            expression: Rust code to evaluate

            with_output: Whether to capture output

            timeout_seconds: Execution timeout

        Returns:

            Dictionary with 'success', 'output', 'error', and 'compile_time' keys

        """

        import hashlib
        import tempfile
        import time

        # Create hash for caching

        expr_hash = hashlib.md5(expression.encode()).hexdigest()

        start_time = time.time()

        # Generate the full program

        program = self._generate_program(expression)

        # Create temporary files

        with tempfile.NamedTemporaryFile(mode="w", suffix=".rs", delete=False) as f:
            f.write(program)

            rust_file = Path(f.name)

        try:
            # Compile

            compile_result = self._compile_expression(rust_file, timeout_seconds)

            compile_time = time.time() - start_time

            if not compile_result["success"]:
                return {
                    "success": False,
                    "output": "",
                    "error": compile_result["error"],
                    "compile_time": compile_time,
                }

            # Execute if compilation succeeded

            if with_output:
                exec_result = self._execute_binary(
                    compile_result["binary_path"], timeout_seconds
                )

                return {
                    "success": exec_result["success"],
                    "output": exec_result["output"],
                    "error": exec_result["error"],
                    "compile_time": compile_time,
                }

            else:
                return {
                    "success": True,
                    "output": "",
                    "error": "",
                    "compile_time": compile_time,
                }

        finally:
            # Cleanup

            rust_file.unlink(missing_ok=True)

            if "binary_path" in locals():
                Path(compile_result.get("binary_path", "")).unlink(missing_ok=True)

    def _generate_program(self, expression: str) -> str:
        """Generate a complete Rust program from an expression."""

        # Check if it's a complete program or just an expression

        if "fn main" in expression:
            # It's already a complete program

            imports = "\n".join(self.default_imports)

            return f"{imports}\n\n{expression}"

        # Wrap in main function

        imports = "\n".join(self.default_imports)

        # Handle different types of expressions

        if expression.strip().endswith(";") or any(
            keyword in expression for keyword in ["let", "if", "for", "while", "match"]
        ):
            # Statement(s)

            main_body = expression

        else:
            # Expression - print the result

            main_body = f'println!("{{}}", ({expression}));'

        return f"""{imports}

fn main() -> Result<(), Box<dyn std::error::Error>> {{

    {main_body}

    Ok(())

}}"""

    def _compile_expression(self, rust_file: Path, timeout_seconds: int) -> dict:
        """Compile the Rust file."""

        binary_path = rust_file.with_suffix("")

        try:
            result = subprocess.run(
                ["rustc", str(rust_file), "-o", str(binary_path), "--edition=2021"],
                capture_output=True,
                text=True,
                timeout=timeout_seconds,
            )

            if result.returncode == 0:
                return {"success": True, "binary_path": str(binary_path), "error": ""}

            else:
                return {"success": False, "binary_path": "", "error": result.stderr}

        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "binary_path": "",
                "error": f"Compilation timed out after {timeout_seconds} seconds",
            }

        except FileNotFoundError:
            return {
                "success": False,
                "binary_path": "",
                "error": "rustc not found. Make sure Rust is installed.",
            }

    def _execute_binary(self, binary_path: str, timeout_seconds: int) -> dict:
        """Execute the compiled binary."""

        try:
            result = subprocess.run(
                [binary_path], capture_output=True, text=True, timeout=timeout_seconds
            )

            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr if result.returncode != 0 else "",
            }

        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "output": "",
                "error": f"Execution timed out after {timeout_seconds} seconds",
            }

        except Exception as e:
            return {"success": False, "output": "", "error": f"Execution failed: {e}"}

    def validate_syntax(self, code: str) -> dict:
        """

        Validate Rust syntax without compilation.

        Args:

            code: Rust code to validate

        Returns:

            Dictionary with 'valid' and 'errors' keys

        """

        # Use rustc with --parse-only flag for syntax checking

        program = self._generate_program(code)

        with tempfile.NamedTemporaryFile(mode="w", suffix=".rs", delete=False) as f:
            f.write(program)

            rust_file = Path(f.name)

        try:
            result = subprocess.run(
                ["rustc", str(rust_file), "--parse-only"],
                capture_output=True,
                text=True,
                timeout=5,
            )

            return {
                "valid": result.returncode == 0,
                "errors": result.stderr if result.returncode != 0 else "",
            }

        except subprocess.TimeoutExpired:
            return {"valid": False, "errors": "Syntax checking timed out"}

        except FileNotFoundError:
            return {"valid": False, "errors": "rustc not found"}

        finally:
            rust_file.unlink(missing_ok=True)


class RustDocumentationHelper:
    """

    Helper for accessing Rust documentation and help system.

    Features:

    - Integration with rustdoc

    - Standard library documentation

    - Crate documentation lookup

    - Function signature help

    """

    def __init__(self):
        self.std_docs_cache = {}

        self.crate_docs_cache = {}

    def get_std_doc(self, item: str) -> Optional[str]:
        """Get documentation for a standard library item."""

        if item in self.std_docs_cache:
            return str(self.std_docs_cache[item])

        try:
            # Try to get documentation using rustdoc

            result = subprocess.run(
                ["rustc", "--explain", item], capture_output=True, text=True, timeout=5
            )

            if result.returncode == 0 and result.stdout.strip():
                doc = result.stdout.strip()

                self.std_docs_cache[item] = doc

                return doc

        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass

        return None

    def search_documentation(self, query: str) -> List[dict]:
        """

        Search for documentation matching the query.

        Args:

            query: Search term

        Returns:

            List of documentation entries

        """

        results = []

        # Search common standard library items

        std_items = [
            ("Vec", "Dynamic array type"),
            ("HashMap", "Hash map implementation"),
            ("String", "UTF-8 encoded string"),
            ("Option", "Optional value type"),
            ("Result", "Error handling type"),
            ("Iterator", "Iterator trait"),
            ("Clone", "Cloning trait"),
            ("Debug", "Debugging trait"),
        ]

        for item, description in std_items:
            if query.lower() in item.lower() or query.lower() in description.lower():
                results.append(
                    {"name": item, "description": description, "type": "std"}
                )

        return results

    def get_function_signature(self, function_name: str) -> Optional[str]:
        """Get function signature and basic documentation."""

        # This is a simplified version - in practice, you'd integrate with rust-analyzer or similar

        signatures = {
            "println!": "println!(format_str, args...) - Print to stdout with newline",
            "print!": "print!(format_str, args...) - Print to stdout without newline",
            "vec!": "vec![elements...] - Create a vector with initial elements",
            "format!": "format!(format_str, args...) - Create a formatted string",
        }

        return signatures.get(function_name)


class RustInteractiveEngine(InteractiveEngine):
    """

    Enhanced Rust-specific interactive engine with advanced features.

    Provides:

    - Rust-specific command parsing with Result error handling

    - Integration with cargo commands and crate ecosystem

    - Advanced tab completion for Rust ecosystem

    - Memory-safe implementation patterns

    - Rustyline integration with custom keybindings

    - History management with persistence

    - Rust expression evaluation and compilation

    """

    def __init__(self, cli_config: Dict[str, Any]):
        super().__init__(cli_config)

        self.rust_parser = RustCommandParser()

        self.completion_provider = RustCompletionProvider(cli_config)

        self.cargo_info = self.completion_provider.cargo_info

        self.history_manager = RustHistoryManager()

        self.expression_evaluator = RustExpressionEvaluator()

        self.documentation_helper = RustDocumentationHelper()

        # Register Rust-specific commands

        self._register_rust_commands()

        self._setup_advanced_features()

    def _register_rust_commands(self):
        """Register Rust and cargo-specific commands."""

        from .base import InteractiveCommand

        self.register_command(
            InteractiveCommand(
                name="cargo",
                description="Run cargo commands",
                handler=self.handle_cargo_command,
            )
        )

        self.register_command(
            InteractiveCommand(
                name="rustc",
                description="Compile Rust expression",
                handler=self.handle_rustc_command,
            )
        )

        self.register_command(
            InteractiveCommand(
                name="check",
                description="Run cargo check",
                handler=self.handle_check_command,
            )
        )

        self.register_command(
            InteractiveCommand(
                name="test",
                description="Run cargo test",
                handler=self.handle_test_command,
            )
        )

        self.register_command(
            InteractiveCommand(
                name="build",
                description="Run cargo build",
                handler=self.handle_build_command,
            )
        )

        if self.cargo_info:
            self.register_command(
                InteractiveCommand(
                    name="info",
                    description="Show project information",
                    handler=self.handle_info_command,
                )
            )

    def _setup_advanced_features(self):
        """Setup advanced Rust-specific features."""

        # Register additional enhanced commands

        from .base import InteractiveCommand

        self.register_command(
            InteractiveCommand(
                name="eval",
                description="Evaluate Rust expressions with compilation",
                handler=self.handle_eval_command,
            )
        )

        self.register_command(
            InteractiveCommand(
                name="doc",
                description="Search Rust documentation",
                handler=self.handle_doc_command,
            )
        )

        self.register_command(
            InteractiveCommand(
                name="validate",
                description="Validate Rust syntax without execution",
                handler=self.handle_validate_command,
            )
        )

        self.register_command(
            InteractiveCommand(
                name="search-history",
                description="Search command history with regex",
                handler=self.handle_search_history_command,
            )
        )

        self.register_command(
            InteractiveCommand(
                name="crate",
                description="Search and manage crate information",
                handler=self.handle_crate_command,
            )
        )

    def handle_cli_command(self, command: Dict[str, Any], args: List[str]):
        """Handle CLI commands with Rust-specific parsing."""

        # Convert args back to command line for parsing

        line = " ".join([command["name"]] + [str(arg) for arg in args])

        rust_command, error = self.rust_parser.parse_command(line, command)

        if error or rust_command is None:
            print(f"Error: {error or 'Unknown error'}")

            return

        try:
            # Call the appropriate hook function

            hook_name = command.get(
                "hook_name", f"on_{command['name'].replace('-', '_')}"
            )

            print(f"Executing {hook_name} with parsed arguments:")

            print(f"  Command: {rust_command.name}")

            print(f"  Args: {rust_command.args}")

            print(f"  Options: {rust_command.options}")

            print(f"  Flags: {rust_command.flags}")

            # In a real implementation, this would call the actual hook

            print(f"Hook function '{hook_name}' would be called here")

        except Exception as e:
            print(f"Error executing command: {e}")

    def handle_cargo_command(self, args: List[str]):
        """Handle cargo commands."""

        if not args:
            print("Available cargo commands: build, test, check, run, clean, doc")

            return

        try:
            cmd = ["cargo"] + args

            print(f"Running: {' '.join(cmd)}")

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            if result.stdout:
                print(result.stdout)

            if result.stderr:
                print(result.stderr)

            if result.returncode != 0:
                print(f"Command failed with exit code {result.returncode}")

        except subprocess.TimeoutExpired:
            print("Command timed out")

        except FileNotFoundError:
            print("Cargo not found. Make sure Rust is installed.")

        except Exception as e:
            print(f"Error running cargo command: {e}")

    def handle_rustc_command(self, args: List[str]):
        """Handle Rust expression compilation."""

        if not args:
            print("Usage: rustc <expression>")

            print("Example: rustc 'println!(\"Hello, world!\");'")

            return

        expression = " ".join(args)

        # Create a temporary Rust program

        program = f"""

fn main() {{

    {expression}

}}

"""

        try:
            import os
            import tempfile

            with tempfile.NamedTemporaryFile(mode="w", suffix=".rs", delete=False) as f:
                f.write(program)

                temp_file = f.name

            try:
                # Compile and run

                result = subprocess.run(
                    ["rustc", temp_file, "-o", temp_file + ".exe"],
                    capture_output=True,
                    text=True,
                    timeout=10,
                )

                if result.returncode == 0:
                    # Run the compiled program

                    run_result = subprocess.run(
                        [temp_file + ".exe"], capture_output=True, text=True, timeout=5
                    )

                    if run_result.stdout:
                        print(run_result.stdout)

                    if run_result.stderr:
                        print(f"Runtime error: {run_result.stderr}")

                else:
                    print(f"Compilation error: {result.stderr}")

            finally:
                # Clean up

                for ext in ["", ".exe"]:
                    try:
                        os.unlink(temp_file + ext)

                    except OSError:
                        pass

        except Exception as e:
            print(f"Error compiling Rust expression: {e}")

    def handle_check_command(self, args: List[str]):
        """Handle cargo check command."""

        self.handle_cargo_command(["check"] + args)

    def handle_test_command(self, args: List[str]):
        """Handle cargo test command."""

        self.handle_cargo_command(["test"] + args)

    def handle_build_command(self, args: List[str]):
        """Handle cargo build command."""

        self.handle_cargo_command(["build"] + args)

    def handle_info_command(self, args: List[str]):
        """Handle project info command."""

        if self.cargo_info:
            print(f"Project: {self.cargo_info.name}")

            print(f"Version: {self.cargo_info.version}")

            print(f"Dependencies: {', '.join(self.cargo_info.dependencies)}")

            print(f"Features: {', '.join(self.cargo_info.features)}")

        else:
            print("No Cargo project information available")

    def get_completions(self, text: str, state: int) -> Optional[str]:
        """Get enhanced tab completions with Rust-specific features."""

        if state == 0:
            # Generate completions - simplified for now
            if not text:
                self.completions = list(self.commands.keys())
            else:
                self.completions = [
                    cmd for cmd in self.commands.keys() if cmd.startswith(text)
                ]

        try:
            return self.completions[state]
        except (IndexError, AttributeError):
            return None

    def handle_eval_command(self, args: List[str]):
        """Handle Rust expression evaluation."""

        if not args:
            print("Usage: eval <rust-expression>")

            print("Examples:")

            print("  eval '2 + 2'")

            print("  eval 'println!(\"Hello, World!\");'")

            print("  eval 'let x = vec![1, 2, 3]; println!(\"{:?}\", x);'")

            return

        # Check for options

        no_run = "--no-run" in args or "-n" in args

        args = [arg for arg in args if not arg.startswith("-")]

        expression = " ".join(args)

        print(f"Evaluating: {expression}")

        result = self.expression_evaluator.evaluate_expression(expression, not no_run)

        if result["success"]:
            if result["output"]:
                print("Output:")

                print(result["output"])

            print(f"✅ Success (compiled in {result['compile_time']:.2f}s)")

        else:
            print("❌ Error:")

            print(result["error"])

    def handle_doc_command(self, args: List[str]):
        """Handle documentation search."""

        if not args:
            print("Usage: doc <search-term>")

            print("Examples:")

            print("  doc Vec")

            print("  doc HashMap")

            print("  doc Iterator")

            return

        query = " ".join(args)

        results = self.documentation_helper.search_documentation(query)

        if results:
            print(f"Documentation results for '{query}':")

            for result in results:
                print(f"  {result['name']}: {result['description']}")

                # Try to get detailed documentation

                detailed = self.documentation_helper.get_std_doc(result["name"])

                if detailed:
                    print(f"    {detailed[:100]}...")

        else:
            print(f"No documentation found for '{query}'")

            # Try function signature lookup

            signature = self.documentation_helper.get_function_signature(query)

            if signature:
                print(f"Function signature: {signature}")

    def handle_validate_command(self, args: List[str]):
        """Handle syntax validation."""

        if not args:
            print("Usage: validate <rust-code>")

            print("Example: validate 'let x: i32 = 42;'")

            return

        code = " ".join(args)

        result = self.expression_evaluator.validate_syntax(code)

        if result["valid"]:
            print("✅ Syntax is valid")

        else:
            print("❌ Syntax errors:")

            print(result["errors"])

    def handle_search_history_command(self, args: List[str]):
        """Handle history search."""

        if not args:
            print("Usage: search-history <pattern>")

            print("Examples:")

            print("  search-history cargo")

            print("  search-history 'test.*debug'")

            return

        pattern = " ".join(args)

        case_sensitive = "--case-sensitive" in args or "-c" in args

        if case_sensitive:
            pattern = " ".join(
                [arg for arg in args if arg not in ["--case-sensitive", "-c"]]
            )

        results = self.history_manager.search_history(pattern, case_sensitive)

        if results:
            print(f"History search results for '{pattern}':")

            for index, command in results[-20:]:  # Show last 20 results
                print(f"  {index:4d}  {command}")

        else:
            print(f"No history entries found matching '{pattern}'")

    def handle_crate_command(self, args: List[str]):
        """Handle crate information and search."""

        if not args:
            print("Usage: crate <search-term>")

            print("Examples:")

            print("  crate serde")

            print("  crate tokio")

            return

        query = args[0]

        # Use the completion provider's crate search

        crates = self.completion_provider._complete_crate_names(query)

        if crates:
            print(f"Crates matching '{query}':")

            for crate in crates[:10]:  # Limit to top 10
                print(f"  {crate}")

        else:
            print(f"No crates found matching '{query}'")

        # If we have cargo info, also show project dependencies

        if self.cargo_info and query.lower() in [
            dep.lower() for dep in self.cargo_info.dependencies
        ]:
            print(f"\n'{query}' is a dependency in the current project")

    def run(self):
        """

        Enhanced run method with history integration.

        This method would be called by the actual Rust interactive implementation

        to integrate with rustyline and provide the enhanced features.

        """

        print("Enhanced Rust Interactive Mode")

        print("Features:")

        print("- Advanced tab completion")

        print("- Persistent history with search")

        print("- Rust expression evaluation")

        print("- Documentation integration")

        print("- Cargo project integration")

        print()

        # This is a placeholder - the actual implementation would use rustyline

        # and integrate with the Rust template

        super().run()


def create_rust_interactive_engine(cli_config: Dict[str, Any]) -> RustInteractiveEngine:
    """

    Factory function to create a Rust interactive engine.

    Args:

        cli_config: CLI configuration dictionary

    Returns:

        Configured RustInteractiveEngine instance

    """

    return RustInteractiveEngine(cli_config)
