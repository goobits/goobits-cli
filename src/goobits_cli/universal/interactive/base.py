"""

Base classes for interactive mode support in Goobits CLI Framework.



This module provides abstract base classes and utilities for implementing

interactive modes across different programming languages.

"""



from abc import ABC, abstractmethod

from typing import Dict, List, Optional, Callable, Any, Union

from dataclasses import dataclass

import shlex

import sys

import time





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


class SessionREPL(BasicREPL):
    """
    Enhanced REPL with session management capabilities.
    
    Extends BasicREPL to add:
    - Session save/load/list operations
    - Command history persistence
    - Automatic session management
    - Performance metrics tracking
    """
    
    def __init__(self, cli_config: Dict[str, Any], session_config: Optional[Dict[str, Any]] = None, **kwargs):
        """
        Initialize SessionREPL.
        
        Args:
            cli_config: CLI configuration dictionary
            session_config: Session management configuration
            **kwargs: Additional configuration options
        """
        super().__init__(cli_config, **kwargs)
        
        # Session management setup
        self.session_config = session_config or {}
        self.session_manager = None
        self.current_session_name = None
        self.session_auto_save = self.session_config.get('auto_save', False)
        
        # Enhanced command history with metadata
        from .session_manager import CommandHistory
        self.session_history = CommandHistory(max_entries=self.session_config.get('max_history', 1000))
        
        # Track command timing for performance metrics
        self.command_start_time = None
        
        # Initialize session manager lazily for performance
        self._session_manager_initialized = False
        
        # Register session commands
        self._register_session_commands()
    
    def _initialize_session_manager(self):
        """Lazy initialization of session manager."""
        if self._session_manager_initialized:
            return
        
        try:
            from .session_manager import create_session_manager
            cli_name = self.cli_config.get('root_command', {}).get('name', 'cli')
            self.session_manager = create_session_manager(cli_name, self.session_config)
            self._session_manager_initialized = True
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Failed to initialize session manager: {e}")
            self.session_manager = None
    
    def _register_session_commands(self):
        """Register session management commands."""
        self.register_command(InteractiveCommand(
            name="save-session",
            description="Save current session with a name",
            handler=self.handle_save_session,
            arguments=[{"name": "session_name", "description": "Name for the session", "required": True}]
        ))
        
        self.register_command(InteractiveCommand(
            name="load-session", 
            description="Load a previously saved session",
            handler=self.handle_load_session,
            arguments=[{"name": "session_name", "description": "Name of session to load", "required": True}]
        ))
        
        self.register_command(InteractiveCommand(
            name="list-sessions",
            description="List all available sessions",
            handler=self.handle_list_sessions
        ))
        
        self.register_command(InteractiveCommand(
            name="delete-session",
            description="Delete a saved session",
            handler=self.handle_delete_session,
            arguments=[{"name": "session_name", "description": "Name of session to delete", "required": True}]
        ))
        
        self.register_command(InteractiveCommand(
            name="session-stats",
            description="Show session statistics",
            handler=self.handle_session_stats
        ))
    
    def handle_save_session(self, args: List[str]):
        """Handle save-session command."""
        if not args:
            print("Usage: save-session <session_name>")
            return
        
        self._initialize_session_manager()
        if not self.session_manager:
            print("Session management not available")
            return
        
        session_name = args[0]
        
        # Add current session metadata
        metadata = {
            'saved_at': time.time(),
            'current_session': self.current_session_name
        }
        
        success = self.session_manager.save_session(
            session_name, 
            self.session_history, 
            metadata
        )
        
        if success:
            print(f"Session '{session_name}' saved successfully")
            self.current_session_name = session_name
        else:
            print(f"Failed to save session '{session_name}'")
    
    def handle_load_session(self, args: List[str]):
        """Handle load-session command."""
        if not args:
            print("Usage: load-session <session_name>")
            return
        
        self._initialize_session_manager()
        if not self.session_manager:
            print("Session management not available")
            return
        
        session_name = args[0]
        result = self.session_manager.load_session(session_name)
        
        if result:
            command_history, metadata = result
            self.session_history = command_history
            self.current_session_name = session_name
            
            # Update command history for readline
            try:
                import readline
                readline.clear_history()
                for entry in command_history.get_recent_commands(50):
                    readline.add_history(entry.command)
            except ImportError:
                pass
            
            session_meta = metadata.get('session_metadata', {})
            command_count = session_meta.get('command_count', 0)
            print(f"Session '{session_name}' loaded successfully ({command_count} commands)")
        else:
            print(f"Failed to load session '{session_name}' or session not found")
    
    def handle_list_sessions(self, args: List[str]):
        """Handle list-sessions command."""
        self._initialize_session_manager()
        if not self.session_manager:
            print("Session management not available")
            return
        
        sessions = self.session_manager.list_sessions()
        
        if not sessions:
            print("No saved sessions found")
            return
        
        print("\nAvailable sessions:")
        print(f"{'Name':<20} {'Commands':<10} {'Success Rate':<12} {'Last Modified':<20}")
        print("-" * 65)
        
        for session in sessions:
            from datetime import datetime
            last_mod = datetime.fromtimestamp(session['last_modified']).strftime('%Y-%m-%d %H:%M')
            success_rate = f"{session['success_rate']:.1%}"
            current = " (current)" if session['name'] == self.current_session_name else ""
            
            print(f"{session['name']:<20} {session['command_count']:<10} {success_rate:<12} {last_mod:<20}{current}")
        print()
    
    def handle_delete_session(self, args: List[str]):
        """Handle delete-session command."""
        if not args:
            print("Usage: delete-session <session_name>")
            return
        
        self._initialize_session_manager()
        if not self.session_manager:
            print("Session management not available")
            return
        
        session_name = args[0]
        
        # Confirm deletion
        try:
            response = input(f"Delete session '{session_name}'? (y/N): ").strip().lower()
            if response not in ('y', 'yes'):
                print("Deletion cancelled")
                return
        except (EOFError, KeyboardInterrupt):
            print("\nDeletion cancelled")
            return
        
        success = self.session_manager.delete_session(session_name)
        
        if success:
            print(f"Session '{session_name}' deleted")
            if self.current_session_name == session_name:
                self.current_session_name = None
        else:
            print(f"Failed to delete session '{session_name}'")
    
    def handle_session_stats(self, args: List[str]):
        """Handle session-stats command."""
        self._initialize_session_manager()
        if not self.session_manager:
            print("Session management not available")
            return
        
        # Get storage stats
        storage_stats = self.session_manager.get_session_stats()
        
        # Get current session stats
        history_stats = self.session_history.get_statistics()
        
        print("\nSession Statistics:")
        print(f"  Current session: {self.current_session_name or 'unsaved'}")
        print(f"  Commands in session: {history_stats['total_commands']}")
        print(f"  Success rate: {history_stats['success_rate']:.1%}")
        print(f"  Average duration: {history_stats['avg_duration_ms']:.1f}ms")
        
        if history_stats['most_common_commands']:
            print("  Most used commands:")
            for cmd, count in history_stats['most_common_commands']:
                print(f"    {cmd}: {count}")
        
        print(f"\nStorage Statistics:")
        print(f"  Total saved sessions: {storage_stats['total_sessions']}")
        print(f"  Storage size: {storage_stats['storage_size_mb']:.2f} MB")
        print(f"  Storage directory: {storage_stats['directory']}")
        print(f"  Max sessions: {storage_stats['max_sessions']}")
    
    def add_to_history(self, line: str):
        """Override to add command to both histories."""
        super().add_to_history(line)
        
        # Add to session history with timing if available
        duration_ms = None
        if self.command_start_time:
            duration_ms = int((time.time() - self.command_start_time) * 1000)
            self.command_start_time = None
        
        self.session_history.add_command(
            command=line,
            success=True,  # We'll update this if needed
            duration_ms=duration_ms
        )
    
    def execute_command(self, line: str) -> bool:
        """Override to track command timing and success."""
        self.command_start_time = time.time()
        
        try:
            result = super().execute_command(line)
            return result
        except Exception as e:
            # Mark last command as failed
            if self.session_history.entries:
                self.session_history.entries[-1].success = False
            raise
    
    def run(self):
        """Override run to add session auto-save."""
        # Initialize session manager
        self._initialize_session_manager()
        
        # Try to auto-load last session if configured
        if self.session_config.get('auto_load_last', False) and self.session_manager:
            sessions = self.session_manager.list_sessions()
            if sessions:
                # Load most recently modified session
                last_session = sessions[0]
                result = self.session_manager.load_session(last_session['name'])
                if result:
                    command_history, metadata = result
                    self.session_history = command_history
                    self.current_session_name = last_session['name']
                    print(f"Auto-loaded session: {last_session['name']}")
        
        try:
            super().run()
        finally:
            # Auto-save session on exit if configured
            if (self.session_auto_save and 
                self.session_manager and 
                self.session_history.entries and
                self.current_session_name):
                
                print(f"\nAuto-saving session '{self.current_session_name}'...")
                success = self.session_manager.save_session(
                    self.current_session_name,
                    self.session_history
                )
                if not success:
                    print("Warning: Failed to auto-save session")


class VariableREPL(SessionREPL):
    """
    Enhanced REPL with variable management capabilities.
    
    Extends SessionREPL to add:
    - Variable storage and retrieval (set, get, unset)  
    - Type inference and validation
    - Command substitution with $variable_name
    - Variable persistence across sessions
    - Variable completion and help
    """
    
    def __init__(self, cli_config: Dict[str, Any], variable_config: Optional[Dict[str, Any]] = None, **kwargs):
        """
        Initialize VariableREPL.
        
        Args:
            cli_config: CLI configuration dictionary
            variable_config: Variable system configuration
            **kwargs: Additional configuration options passed to SessionREPL
        """
        super().__init__(cli_config, **kwargs)
        
        # Variable system setup
        self.variable_config = variable_config or {}
        self.variables_enabled = self.variable_config.get('enabled', True)
        self.variable_substitution_enabled = self.variable_config.get('substitution', True)
        
        # Initialize variable store if enabled
        if self.variables_enabled:
            from .variable_store import VariableStore
            max_vars = self.variable_config.get('max_variables', 100)
            self.variable_store = VariableStore(max_variables=max_vars)
            
            # Register variable commands
            self._register_variable_commands()
        else:
            self.variable_store = None
    
    def _register_variable_commands(self):
        """Register variable management commands."""
        if not self.variables_enabled:
            return
        
        self.register_command(InteractiveCommand(
            name="set",
            description="Set a variable with automatic type inference",
            handler=self.handle_set_variable,
            arguments=[
                {"name": "assignment", "description": "Variable assignment (name=value)", "required": True}
            ]
        ))
        
        self.register_command(InteractiveCommand(
            name="vars",
            description="List all variables with their types and values",
            handler=self.handle_list_variables,
            aliases=["list-vars", "variables"]
        ))
        
        self.register_command(InteractiveCommand(
            name="unset",
            description="Remove a variable",
            handler=self.handle_unset_variable,
            arguments=[
                {"name": "variable_name", "description": "Name of variable to remove", "required": True}
            ]
        ))
        
        self.register_command(InteractiveCommand(
            name="var-stats",
            description="Show variable store statistics",
            handler=self.handle_variable_stats
        ))
    
    def handle_set_variable(self, args: List[str]):
        """Handle the set command for variables."""
        if not self.variables_enabled or not self.variable_store:
            print("Variable system is not enabled")
            return
        
        if not args:
            print("Usage: set variable_name=value")
            print("Examples:")
            print("  set name=\"John Doe\"")
            print("  set count=42")
            print("  set debug=true")
            print("  set servers=[\"web1\", \"web2\", \"web3\"]")
            return
        
        # Join args to handle spaces in assignment
        assignment = " ".join(args)
        
        # Parse assignment
        if '=' not in assignment:
            print("Error: Assignment must be in format variable_name=value")
            return
        
        parts = assignment.split('=', 1)
        if len(parts) != 2:
            print("Error: Invalid assignment format")
            return
        
        var_name = parts[0].strip()
        var_value = parts[1].strip()
        
        if not var_name:
            print("Error: Variable name cannot be empty")
            return
        
        # Set variable with type inference
        success = self.variable_store.set_variable(var_name, var_value)
        if success:
            variable = self.variable_store.get_variable(var_name)
            if variable:
                from .variable_store import TypeInferenceEngine
                display_value = TypeInferenceEngine.format_value_for_display(variable.value, variable.var_type)
                print(f"Variable set: {var_name} = {display_value} ({variable.var_type.value})")
        else:
            print(f"Failed to set variable: {var_name}")
    
    def handle_list_variables(self, args: List[str]):
        """Handle the vars command to list variables."""
        if not self.variables_enabled or not self.variable_store:
            print("Variable system is not enabled")
            return
        
        variables = self.variable_store.list_variables()
        
        if not variables:
            print("No variables defined")
            return
        
        print("\nDefined variables:")
        
        # Calculate column widths for nice formatting
        max_name_len = max(len(var.name) for var in variables)
        max_type_len = max(len(var.var_type.value) for var in variables)
        
        name_width = max(max_name_len, 8) + 2
        type_width = max(max_type_len, 4) + 2
        
        # Header
        print(f"{'Name':<{name_width}} {'Type':<{type_width}} Value")
        print("-" * (name_width + type_width + 20))
        
        # Variables
        from .variable_store import TypeInferenceEngine
        for var in variables:
            display_value = TypeInferenceEngine.format_value_for_display(var.value, var.var_type)
            # Truncate long values
            if len(display_value) > 40:
                display_value = display_value[:37] + "..."
            
            print(f"{var.name:<{name_width}} {var.var_type.value:<{type_width}} {display_value}")
        
        print()
    
    def handle_unset_variable(self, args: List[str]):
        """Handle the unset command."""
        if not self.variables_enabled or not self.variable_store:
            print("Variable system is not enabled")
            return
        
        if not args:
            print("Usage: unset variable_name")
            return
        
        var_name = args[0]
        success = self.variable_store.unset_variable(var_name)
        
        if success:
            print(f"Variable unset: {var_name}")
        else:
            print(f"Variable not found: {var_name}")
    
    def handle_variable_stats(self, args: List[str]):
        """Handle the var-stats command."""
        if not self.variables_enabled or not self.variable_store:
            print("Variable system is not enabled")
            return
        
        stats = self.variable_store.get_statistics()
        
        print("\nVariable Store Statistics:")
        print(f"  Total variables: {stats['total_variables']}")
        print(f"  Usage: {stats['usage_percentage']:.1f}% of {stats['max_variables']} max")
        print(f"  Memory usage estimate: {stats['memory_usage_estimate']} bytes")
        
        if stats['types_distribution']:
            print("  Type distribution:")
            for var_type, count in stats['types_distribution'].items():
                print(f"    {var_type}: {count}")
        
        print()
    
    def execute_command(self, line: str) -> bool:
        """Override to add variable substitution."""
        # Apply variable substitution if enabled
        if (self.variables_enabled and 
            self.variable_substitution_enabled and 
            self.variable_store and 
            '$' in line):
            
            original_line = line
            line = self.variable_store.substitute_variables(line)
            
            if line != original_line:
                # Show substitution result for transparency
                print(f"Expanded: {line}")
        
        return super().execute_command(line)
    
    def get_basic_completions(self, text: str) -> List[str]:
        """Override to add variable name completion."""
        completions = super().get_basic_completions(text)
        
        # Add variable completions for $var_name patterns
        if (self.variables_enabled and 
            self.variable_store and 
            text.startswith('$')):
            
            var_prefix = text[1:]  # Remove $
            var_completions = self.variable_store.get_completions_for_prefix(var_prefix)
            completions.extend(f"${name}" for name in var_completions)
        
        return completions
    
    def handle_save_session(self, args: List[str]):
        """Override to include variable store in session save."""
        if not args:
            print("Usage: save-session <session_name>")
            return
        
        self._initialize_session_manager()
        if not self.session_manager:
            print("Session management not available")
            return
        
        session_name = args[0]
        
        # Add current session metadata
        metadata = {
            'saved_at': time.time(),
            'current_session': self.current_session_name,
            'variables_enabled': self.variables_enabled
        }
        
        # Include variable store if enabled
        variable_store = self.variable_store if self.variables_enabled else None
        
        success = self.session_manager.save_session(
            session_name,
            self.session_history,
            metadata,
            variable_store
        )
        
        if success:
            var_count = len(self.variable_store.variables) if variable_store else 0
            var_info = f" ({var_count} variables)" if var_count > 0 else ""
            print(f"Session '{session_name}' saved successfully{var_info}")
            self.current_session_name = session_name
        else:
            print(f"Failed to save session '{session_name}'")
    
    def handle_load_session(self, args: List[str]):
        """Override to load variable store from session."""
        if not args:
            print("Usage: load-session <session_name>")
            return
        
        self._initialize_session_manager()
        if not self.session_manager:
            print("Session management not available")
            return
        
        session_name = args[0]
        result = self.session_manager.load_session(session_name)
        
        if result:
            command_history, metadata, variable_store = result
            self.session_history = command_history
            self.current_session_name = session_name
            
            # Load variable store if present and variables are enabled
            if variable_store and self.variables_enabled:
                self.variable_store = variable_store
                var_count = len(variable_store.variables)
                var_info = f" ({var_count} variables loaded)"
            else:
                var_info = ""
            
            # Update command history for readline
            try:
                import readline
                readline.clear_history()
                for entry in command_history.get_recent_commands(50):
                    readline.add_history(entry.command)
            except ImportError:
                pass
            
            session_meta = metadata.get('session_metadata', {})
            command_count = session_meta.get('command_count', 0)
            print(f"Session '{session_name}' loaded successfully ({command_count} commands){var_info}")
        else:
            print(f"Failed to load session '{session_name}' or session not found")


class PipelineREPL(VariableREPL):
    """
    Advanced REPL with pipeline processing capabilities.
    
    Extends VariableREPL to add:
    - Unix-style pipeline operations (command1 | command2 | command3)
    - Pipeline template definitions and execution
    - Data streaming and transformation between commands
    - Pipeline session persistence and management
    """
    
    def __init__(self, cli_config: Dict[str, Any], pipeline_config: Optional[Dict[str, Any]] = None, **kwargs):
        """
        Initialize PipelineREPL.
        
        Args:
            cli_config: CLI configuration dictionary
            pipeline_config: Pipeline system configuration
            **kwargs: Additional configuration options passed to VariableREPL
        """
        super().__init__(cli_config, **kwargs)
        
        # Pipeline system setup
        self.pipeline_config = pipeline_config or {}
        self.pipelines_enabled = self.pipeline_config.get('enabled', True)
        self.pipeline_templates_enabled = self.pipeline_config.get('pipeline_templates', True)
        
        # Initialize pipeline processor if enabled
        if self.pipelines_enabled:
            from .pipeline_processor import create_pipeline_processor
            self.pipeline_processor = create_pipeline_processor(
                cli_config, 
                self.variable_store,
                timeout=self.pipeline_config.get('timeout', 60)
            )
            
            if self.pipeline_processor:
                # Register pipeline commands
                self._register_pipeline_commands()
        else:
            self.pipeline_processor = None
    
    def _register_pipeline_commands(self):
        """Register pipeline management commands."""
        if not self.pipelines_enabled or not self.pipeline_processor:
            return
        
        self.register_command(InteractiveCommand(
            name="pipeline",
            description="Define a reusable pipeline template",
            handler=self.handle_pipeline_definition,
            arguments=[
                {"name": "definition", "description": "Pipeline definition (name { commands })", "required": True}
            ]
        ))
        
        self.register_command(InteractiveCommand(
            name="run",
            description="Execute a pipeline template",
            handler=self.handle_run_pipeline,
            arguments=[
                {"name": "pipeline_name", "description": "Name of pipeline template to run", "required": True},
                {"name": "parameters", "description": "Template parameters (key=value)", "required": False}
            ]
        ))
        
        self.register_command(InteractiveCommand(
            name="pipelines",
            description="List all available pipeline templates",
            handler=self.handle_list_pipelines,
            aliases=["list-pipelines"]
        ))
        
        self.register_command(InteractiveCommand(
            name="pipeline-stats",
            description="Show pipeline execution statistics",
            handler=self.handle_pipeline_stats
        ))
    
    def handle_pipeline_definition(self, args: List[str]):
        """Handle pipeline template definition."""
        if not self.pipelines_enabled or not self.pipeline_processor:
            print("Pipeline system is not enabled")
            return
        
        if not args:
            print("Usage: pipeline name { command1 | command2 | command3 }")
            print("       pipeline name(param1,param2) { command1 --arg $param1 | command2 }")
            print("Examples:")
            print("  pipeline greet_users { list-users | greet --style casual }")
            print("  pipeline process_data(format) { load-data | transform --format $format | save-output }")
            return
        
        definition = " ".join(args)
        
        # Parse pipeline definition
        match = re.match(r'(\w+)(?:\(([^)]*)\))?\s*\{\s*([^}]+)\s*\}', definition)
        if not match:
            print("Error: Invalid pipeline definition format")
            print("Expected: pipeline_name { commands } or pipeline_name(params) { commands }")
            return
        
        pipeline_name = match.group(1)
        parameters_str = match.group(2) or ""
        commands = match.group(3)
        
        # Parse parameters
        parameters = []
        if parameters_str:
            parameters = [p.strip() for p in parameters_str.split(',') if p.strip()]
        
        # Define the pipeline template
        success = self.pipeline_processor.define_pipeline_template(
            pipeline_name, 
            commands,
            parameters
        )
        
        if success:
            param_info = f" with parameters: {', '.join(parameters)}" if parameters else ""
            print(f"Pipeline template '{pipeline_name}' defined successfully{param_info}")
        else:
            print(f"Failed to define pipeline template '{pipeline_name}'")
    
    def handle_run_pipeline(self, args: List[str]):
        """Handle pipeline template execution."""
        if not self.pipelines_enabled or not self.pipeline_processor:
            print("Pipeline system is not enabled")
            return
        
        if not args:
            print("Usage: run pipeline_name [param1=value1] [param2=value2]")
            print("Example: run greet_users style=formal")
            return
        
        pipeline_name = args[0]
        
        # Parse parameter values
        parameter_values = {}
        for arg in args[1:]:
            if '=' in arg:
                key, value = arg.split('=', 1)
                parameter_values[key.strip()] = value.strip()
        
        # Execute pipeline template
        import asyncio
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            success, message = loop.run_until_complete(
                self.pipeline_processor.execute_pipeline_template(pipeline_name, parameter_values)
            )
            
            if success:
                print(message)
            else:
                print(f"Error: {message}")
            
        except Exception as e:
            print(f"Pipeline execution error: {e}")
        finally:
            loop.close()
    
    def handle_list_pipelines(self, args: List[str]):
        """Handle listing pipeline templates."""
        if not self.pipelines_enabled or not self.pipeline_processor:
            print("Pipeline system is not enabled")
            return
        
        templates = self.pipeline_processor.list_pipeline_templates()
        
        if not templates:
            print("No pipeline templates defined")
            print("Use 'pipeline name { commands }' to define a template")
            return
        
        print("\nAvailable pipeline templates:")
        print(f"{'Name':<20} {'Commands':<10} {'Parameters':<15} {'Usage':<8} {'Description':<30}")
        print("-" * 85)
        
        for template in templates:
            params = ", ".join(template['parameters']) if template['parameters'] else "none"
            if len(params) > 12:
                params = params[:9] + "..."
            
            description = template['description'] or ""
            if len(description) > 27:
                description = description[:24] + "..."
            
            print(f"{template['name']:<20} {template['command_count']:<10} {params:<15} {template['usage_count']:<8} {description:<30}")
        
        print(f"\nTotal: {len(templates)} templates")
        print("Use 'run template_name' to execute a template")
    
    def handle_pipeline_stats(self, args: List[str]):
        """Handle pipeline statistics display."""
        if not self.pipelines_enabled or not self.pipeline_processor:
            print("Pipeline system is not enabled")
            return
        
        stats = self.pipeline_processor.get_execution_statistics()
        
        print("\nPipeline Execution Statistics:")
        print(f"  Total executions: {stats['total_executions']}")
        print(f"  Success rate: {stats['success_rate']:.1%}")
        print(f"  Active pipelines: {stats['active_count']}")
        print(f"  Total templates: {stats['total_templates']}")
        
        if stats['most_used_template']:
            print(f"  Most used template: {stats['most_used_template']}")
        
        if stats['recent_executions']:
            print("\n  Recent executions:")
            for exec_info in stats['recent_executions']:
                status = "✓" if exec_info['success'] else "✗"
                commands = " | ".join(exec_info['commands'])
                if len(commands) > 40:
                    commands = commands[:37] + "..."
                print(f"    {status} {commands}")
        
        print()
    
    def execute_command(self, line: str) -> bool:
        """Override to detect and handle pipeline commands."""
        # Check if this is a pipeline command (contains |)
        if (self.pipelines_enabled and 
            self.pipeline_processor and 
            '|' in line and 
            not line.strip().startswith('"') and
            not line.strip().startswith("'")):
            
            # Execute as pipeline
            import asyncio
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                success, output = loop.run_until_complete(
                    self.pipeline_processor.execute_pipeline(line)
                )
                
                if success:
                    print(output)
                else:
                    print(f"Pipeline error: {output}")
                
                return False  # Don't exit REPL
                
            except Exception as e:
                print(f"Pipeline execution error: {e}")
                return False
            finally:
                loop.close()
        
        # Not a pipeline, use standard command execution
        return super().execute_command(line)
    
    def get_basic_completions(self, text: str) -> List[str]:
        """Override to add pipeline-specific completions."""
        completions = super().get_basic_completions(text)
        
        # Add pipeline template completions for run command
        if (self.pipelines_enabled and 
            self.pipeline_processor and 
            text.startswith('run ')):
            
            templates = self.pipeline_processor.list_pipeline_templates()
            template_names = [template['name'] for template in templates]
            
            # Filter templates that match the current text after 'run '
            prefix = text[4:]  # Remove 'run ' prefix
            matching_templates = [name for name in template_names if name.startswith(prefix)]
            completions.extend(f"run {name}" for name in matching_templates)
        
        return completions
    
    def handle_save_session(self, args: List[str]):
        """Override to include pipeline templates in session save."""
        if not args:
            print("Usage: save-session <session_name>")
            return
        
        # Save the session using parent method first
        super().handle_save_session(args)
        
        # Add pipeline templates to session if available
        if (self.pipelines_enabled and 
            self.pipeline_processor and 
            self.current_session_name == args[0]):
            
            templates = self.pipeline_processor.list_pipeline_templates()
            if templates:
                print(f"Session includes {len(templates)} pipeline templates")
    
    def handle_load_session(self, args: List[str]):
        """Override to restore pipeline templates from session."""
        # Load session using parent method first
        super().handle_load_session(args)
        
        # For now, pipeline templates are not persisted with sessions
        # This would be a future enhancement to save/load pipeline templates
        # with session data


def create_basic_repl(cli_config: Dict[str, Any], **kwargs) -> Union[BasicREPL, SessionREPL, VariableREPL, PipelineREPL]:
    """
    Factory function to create a REPL instance (basic, with sessions, variables, or pipelines).
    
    Args:
        cli_config: CLI configuration dictionary
        **kwargs: Additional configuration options
        
    Returns:
        Configured REPL instance (BasicREPL, SessionREPL, VariableREPL, or PipelineREPL)
    """
    smart_completion = kwargs.get('smart_completion', True)
    
    # Check if REPL is enabled in config
    features = cli_config.get('features', {})
    interactive_config = features.get('interactive_mode', {})
    repl_enabled = interactive_config.get('repl', False)
    
    if not repl_enabled:
        # Return standard interactive engine
        return BasicREPL(cli_config, smart_completion_enabled=False)
    
    # Check feature availability
    variables_enabled = interactive_config.get('variables', False)
    session_enabled = interactive_config.get('session_persistence', False)
    pipelines_enabled = interactive_config.get('pipelines', False)
    
    # Build configurations
    session_config = None
    if session_enabled:
        session_config = {
            'auto_save': interactive_config.get('auto_save', False),
            'max_sessions': interactive_config.get('max_sessions', 20),
            'session_directory': interactive_config.get('session_directory'),
            'auto_load_last': interactive_config.get('auto_load_last', False),
            'max_history': interactive_config.get('max_history', 1000)
        }
    
    variable_config = None
    if variables_enabled:
        variable_config = {
            'enabled': True,
            'substitution': interactive_config.get('variable_expansion', True),
            'max_variables': interactive_config.get('max_variables', 100)
        }
    
    pipeline_config = None
    if pipelines_enabled:
        pipeline_config = {
            'enabled': True,
            'pipeline_templates': interactive_config.get('pipeline_templates', True),
            'timeout': interactive_config.get('pipeline_timeout', 60)
        }
    
    # Return the most advanced REPL type based on enabled features
    if pipelines_enabled:
        # Return PipelineREPL with full feature set (includes variables and sessions)
        return PipelineREPL(
            cli_config,
            pipeline_config=pipeline_config,
            variable_config=variable_config,
            session_config=session_config,
            smart_completion_enabled=smart_completion
        )
    
    elif variables_enabled:
        # Return VariableREPL with variables and optionally sessions
        return VariableREPL(
            cli_config,
            variable_config=variable_config,
            session_config=session_config,
            smart_completion_enabled=smart_completion
        )
    
    elif session_enabled:
        # Return SessionREPL with session management only
        return SessionREPL(cli_config, session_config, smart_completion_enabled=smart_completion)
    
    return BasicREPL(cli_config, smart_completion_enabled=smart_completion)