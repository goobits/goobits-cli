"""

Base classes for interactive mode support in Goobits CLI Framework.



This module provides abstract base classes and utilities for implementing

interactive modes across different programming languages.

"""



from abc import ABC, abstractmethod

from typing import Dict, List, Optional, Callable, Any

from dataclasses import dataclass

import shlex

import sys





@dataclass

class InteractiveCommand:

    """Represents a command available in interactive mode."""

    name: str

    description: str

    handler: Callable

    arguments: Optional[List[Dict[str, Any]]] = None

    options: Optional[List[Dict[str, Any]]] = None

    aliases: Optional[List[str]] = None





class InteractiveEngine(ABC):

    """

    Abstract base class for interactive mode engines.

    

    This class provides the foundation for implementing interactive

    modes in different programming languages while maintaining a

    consistent interface.

    """

    

    def __init__(self, cli_config: Dict[str, Any]):

        """

        Initialize the interactive engine.

        

        Args:

            cli_config: CLI configuration dictionary containing commands,

                       options, and metadata.

        """

        self.cli_config = cli_config

        self.commands: Dict[str, InteractiveCommand] = {}

        self.command_history: List[str] = []

        self.prompt = f"{cli_config['root_command']['name']}> "

        self.intro = (

            f"Welcome to {cli_config['root_command']['name']} interactive mode. "

            "Type 'help' for commands, 'exit' to quit."

        )

        

        # Register built-in commands

        self._register_builtin_commands()

        

        # Register CLI commands

        self._register_cli_commands()

    

    def _register_builtin_commands(self):

        """Register built-in commands like help, exit, etc."""

        self.register_command(InteractiveCommand(

            name="help",

            description="Show available commands",

            handler=self.handle_help,

            aliases=["?", "h"]

        ))

        

        self.register_command(InteractiveCommand(

            name="exit",

            description="Exit interactive mode",

            handler=self.handle_exit,

            aliases=["quit", "q"]

        ))

        

        self.register_command(InteractiveCommand(

            name="history",

            description="Show command history",

            handler=self.handle_history

        ))

    

    def _register_cli_commands(self):

        """Register commands from CLI configuration."""

        root_command = self.cli_config.get('root_command', {})

        for command in root_command.get('subcommands', []):

            self.register_command(InteractiveCommand(

                name=command['name'],

                description=command.get('description', ''),

                handler=lambda args, cmd=command: self.handle_cli_command(cmd, args),

                arguments=command.get('arguments', []),

                options=command.get('options', [])

            ))

    

    def register_command(self, command: InteractiveCommand):

        """

        Register a command in the interactive engine.

        

        Args:

            command: The command to register.

        """

        self.commands[command.name] = command

        

        # Register aliases

        if command.aliases:

            for alias in command.aliases:

                self.commands[alias] = command

    

    def parse_line(self, line: str) -> tuple[str, List[str]]:

        """

        Parse a command line into command and arguments.

        

        Args:

            line: The input line to parse.

            

        Returns:

            Tuple of (command_name, arguments)

        """

        if not line.strip():

            return '', []

        

        try:

            parts = shlex.split(line)

        except ValueError:

            # Handle unclosed quotes or other parsing errors

            parts = line.split()

        

        if not parts:

            return '', []

        

        return parts[0], parts[1:]

    

    def get_completions(self, text: str, state: int) -> Optional[str]:

        """

        Get tab completions for the given text.

        

        Args:

            text: The text to complete.

            state: The state of completion (for iterating through options).

            

        Returns:

            A completion option or None.

        """

        if state == 0:

            # Generate completions

            if not text:

                self.completions = list(self.commands.keys())

            else:

                self.completions = [

                    cmd for cmd in self.commands.keys()

                    if cmd.startswith(text)

                ]

        

        try:

            return self.completions[state]

        except IndexError:

            return None

    

    def handle_help(self, args: List[str]):

        """Handle the help command."""

        if args:

            # Show help for specific command

            cmd_name = args[0]

            if cmd_name in self.commands:

                command = self.commands[cmd_name]

                print(f"\n{command.name}: {command.description}")

                

                if command.arguments:

                    print("\nArguments:")

                    for arg in command.arguments:

                        required = "required" if arg.get('required', True) else "optional"

                        print(f"  {arg['name']}: {arg.get('description', '')} ({required})")

                

                if command.options:

                    print("\nOptions:")

                    for opt in command.options:

                        short = f", -{opt['short']}" if opt.get('short') else ""

                        print(f"  --{opt['name']}{short}: {opt.get('description', '')}")

            else:

                print(f"Unknown command: {cmd_name}")

        else:

            # Show all commands

            print("\nAvailable commands:")

            

            # Group commands to avoid showing aliases multiple times

            shown = set()

            for name, command in sorted(self.commands.items()):

                if command.name not in shown:

                    print(f"  {command.name:15} {command.description}")

                    shown.add(command.name)

            print()

    

    def handle_exit(self, args: List[str]):

        """Handle the exit command."""

        print("Goodbye!")

        return True  # Signal to exit

    

    def handle_history(self, args: List[str]):

        """Handle the history command."""

        if not self.command_history:

            print("No command history available.")

        else:

            for i, cmd in enumerate(self.command_history, 1):

                print(f"{i:4d}  {cmd}")

    

    @abstractmethod

    def handle_cli_command(self, command: Dict[str, Any], args: List[str]):

        """

        Handle a CLI command in interactive mode.

        

        This method should be implemented by subclasses to execute

        the actual command logic.

        

        Args:

            command: The command configuration.

            args: The command arguments.

        """

        pass

    

    @abstractmethod

    def run(self):

        """

        Run the interactive loop.

        

        This method should be implemented by subclasses to provide

        the actual REPL functionality.

        """

        pass

    

    def execute_command(self, line: str) -> bool:

        """

        Execute a command line.

        

        Args:

            line: The command line to execute.

            

        Returns:

            True if the interactive loop should exit, False otherwise.

        """

        command_name, args = self.parse_line(line)

        

        if not command_name:

            return False

        

        if command_name in self.commands:

            command = self.commands[command_name]

            try:

                result = command.handler(args)

                return result is True  # Exit if handler returns True

            except Exception as e:

                print(f"Error executing command: {e}")

        else:

            print(f"Unknown command: {command_name}")

            print("Type 'help' for available commands")

        

        return False

    

    def add_to_history(self, line: str):

        """Add a command to the history."""

        if line.strip() and not line.startswith('help'):

            self.command_history.append(line)





class InteractiveRenderer:

    """

    Helper class for rendering interactive mode templates.

    

    This class provides utilities for language-specific renderers

    to generate interactive mode code.

    """

    

    @staticmethod

    def get_prompt_format(cli_name: str) -> str:

        """Get the prompt format for the interactive mode."""

        return f"{cli_name}> "

    

    @staticmethod

    def get_intro_message(project_name: str) -> str:

        """Get the intro message for interactive mode."""

        return (

            f"Welcome to {project_name} interactive mode. "

            "Type 'help' for commands, 'exit' to quit."

        )

    

    @staticmethod

    def format_command_name(name: str, language: str) -> str:

        """

        Format command name for the target language.

        

        Args:

            name: The command name.

            language: The target language.

            

        Returns:

            Formatted command name.

        """

        if language in ['python', 'rust']:

            return name.replace('-', '_')

        elif language in ['nodejs', 'typescript']:

            # JavaScript typically uses camelCase

            parts = name.split('-')

            if len(parts) > 1:

                return parts[0] + ''.join(p.title() for p in parts[1:])

            return name

        return name

    

    @staticmethod

    def get_interactive_dependencies(language: str) -> Dict[str, List[str]]:

        """

        Get the dependencies required for interactive mode.

        

        Args:

            language: The target language.

            

        Returns:

            Dictionary of dependency types and their packages.

        """

        dependencies = {

            'python': {

                'builtin': ['cmd', 'shlex', 'readline'],

                'external': []

            },

            'nodejs': {

                'builtin': ['readline'],

                'external': []

            },

            'typescript': {

                'builtin': ['readline'],

                'external': ['@types/node']

            },

            'rust': {

                'builtin': [],

                'external': ['rustyline']

            }

        }

        

        return dependencies.get(language, {'builtin': [], 'external': []})


class BasicREPL(InteractiveEngine):
    """
    Basic REPL implementation with enhanced features.
    
    This class extends InteractiveEngine to provide:
    - Multi-line command support with continuation
    - Smart completion integration
    - Enhanced command history
    - Performance optimization for <50ms startup overhead
    """
    
    def __init__(self, cli_config: Dict[str, Any], smart_completion_enabled: bool = True):
        """
        Initialize the BasicREPL.
        
        Args:
            cli_config: CLI configuration dictionary
            smart_completion_enabled: Enable smart completion integration
        """
        super().__init__(cli_config)
        
        # REPL-specific features
        self.smart_completion_enabled = smart_completion_enabled
        self.continuation_prompt = "... "
        self.multi_line_buffer = ""
        self.max_history = 100
        
        # Lazy import smart completion for performance
        self._smart_completion_engine = None
        
        # Setup readline-like features if available
        self._setup_readline()
    
    def _setup_readline(self):
        """Setup readline functionality for enhanced input."""
        try:
            import readline
            import atexit
            
            # Configure history
            readline.set_completer_delims(' \t\n`!@#$%^&*()=+[{]}\\|;:\'",<>?')
            readline.set_completer(self._readline_completer)
            readline.parse_and_bind("tab: complete")
            
            # Load history from file
            history_file = f".{self.cli_config.get('root_command', {}).get('name', 'cli')}_history"
            try:
                readline.read_history_file(history_file)
            except FileNotFoundError:
                pass
            
            # Save history on exit
            atexit.register(lambda: self._save_history(history_file))
            
        except ImportError:
            # No readline available (Windows, some minimal Python installs)
            pass
    
    def _save_history(self, filename: str):
        """Save command history to file."""
        try:
            import readline
            # Keep only last max_history items
            readline.set_history_length(self.max_history)
            readline.write_history_file(filename)
        except (ImportError, OSError):
            pass
    
    def _readline_completer(self, text: str, state: int) -> Optional[str]:
        """Readline-compatible completer that integrates smart completion."""
        if state == 0:
            # First call - generate completions
            if self.smart_completion_enabled and self._smart_completion_engine:
                try:
                    # Get full line from readline
                    import readline
                    full_line = readline.get_line_buffer()
                    
                    # Use smart completion engine
                    import asyncio
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    
                    completions = loop.run_until_complete(
                        self._smart_completion_engine.get_smart_completions(
                            text, full_line, "python"
                        )
                    )
                    loop.close()
                    
                    self._current_completions = completions
                except Exception:
                    # Fallback to basic completion
                    self._current_completions = self.get_basic_completions(text)
            else:
                self._current_completions = self.get_basic_completions(text)
        
        try:
            return self._current_completions[state]
        except IndexError:
            return None
    
    def get_basic_completions(self, text: str) -> List[str]:
        """Get basic completions without smart features."""
        completions = []
        
        # Command name completion
        for cmd_name in self.commands:
            if cmd_name.startswith(text):
                completions.append(cmd_name)
        
        return completions
    
    def _get_smart_completion_engine(self):
        """Lazy initialization of smart completion engine for performance."""
        if not self._smart_completion_engine and self.smart_completion_enabled:
            try:
                from ..completion.smart_completion import get_smart_completion_registry
                self._smart_completion_engine = get_smart_completion_registry()
            except ImportError:
                # Fallback if smart completion not available
                self.smart_completion_enabled = False
        
        return self._smart_completion_engine
    
    def parse_multi_line_input(self, line: str) -> tuple[str, bool]:
        """
        Parse input for multi-line commands.
        
        Args:
            line: Input line
        
        Returns:
            Tuple of (complete_command, is_continuation)
        """
        # Check for line continuation (ends with backslash)
        if line.rstrip().endswith('\\'):
            # Add to buffer without the backslash
            self.multi_line_buffer += line.rstrip()[:-1] + " "
            return "", True
        
        # Complete command
        if self.multi_line_buffer:
            complete_command = self.multi_line_buffer + line
            self.multi_line_buffer = ""
            return complete_command, False
        
        return line, False
    
    def run(self):
        """Run the REPL loop with enhanced features."""
        print(self.intro)
        
        # Initialize smart completion engine if enabled
        if self.smart_completion_enabled:
            self._get_smart_completion_engine()
        
        try:
            while True:
                try:
                    # Use appropriate prompt
                    current_prompt = self.continuation_prompt if self.multi_line_buffer else self.prompt
                    
                    # Get input
                    line = input(current_prompt).strip()
                    
                    # Handle empty input
                    if not line and not self.multi_line_buffer:
                        continue
                    
                    # Parse for multi-line support
                    complete_command, is_continuation = self.parse_multi_line_input(line)
                    
                    if is_continuation:
                        continue
                    
                    # Execute command
                    if complete_command.strip():
                        self.add_to_history(complete_command)
                        should_exit = self.execute_command(complete_command)
                        if should_exit:
                            break
                
                except KeyboardInterrupt:
                    # Handle Ctrl+C gracefully
                    print("\nKeyboardInterrupt (use 'exit' to quit)")
                    self.multi_line_buffer = ""  # Clear any partial input
                    continue
                
                except EOFError:
                    # Handle Ctrl+D
                    print("\nGoodbye!")
                    break
        
        except Exception as e:
            print(f"REPL error: {e}")
    
    def handle_cli_command(self, command: Dict[str, Any], args: List[str]):
        """
        Handle CLI command execution in REPL mode.
        
        This is a basic implementation - subclasses should override
        for language-specific command handling.
        """
        print(f"Executing command: {command['name']} with args: {args}")
        hook_name = command.get('hook_name', f"on_{command['name'].replace('-', '_')}")
        print(f"Hook function: {hook_name}")
        print("To implement custom behavior, add the hook function to your hooks file.")


def create_basic_repl(cli_config: Dict[str, Any], **kwargs) -> BasicREPL:
    """
    Factory function to create a BasicREPL instance.
    
    Args:
        cli_config: CLI configuration dictionary
        **kwargs: Additional configuration options
        
    Returns:
        Configured BasicREPL instance
    """
    smart_completion = kwargs.get('smart_completion', True)
    
    # Check if REPL is enabled in config
    features = cli_config.get('features', {})
    interactive_config = features.get('interactive_mode', {})
    repl_enabled = interactive_config.get('repl', False)
    
    if not repl_enabled:
        # Return standard interactive engine
        return BasicREPL(cli_config, smart_completion_enabled=False)
    
    return BasicREPL(cli_config, smart_completion_enabled=smart_completion)