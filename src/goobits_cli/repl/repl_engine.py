"""
REPL Engine
===========

Core REPL engine extracted from repl_loop.j2 template.
Provides command parsing, execution management, and session handling.
"""

import time
import shlex
from typing import Dict, List, Any, Optional, Callable, Tuple
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod


class REPLCommandType(Enum):
    """Types of REPL commands."""
    CLI_COMMAND = "cli"
    BUILTIN_COMMAND = "builtin"
    SYSTEM_COMMAND = "system"
    MULTI_LINE = "multiline"


@dataclass
class REPLCommand:
    """Parsed REPL command."""
    name: str
    args: List[str] = field(default_factory=list)
    kwargs: Dict[str, Any] = field(default_factory=dict)
    command_type: REPLCommandType = REPLCommandType.CLI_COMMAND
    raw_input: str = ""
    is_continuation: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for logging/debugging."""
        return {
            'name': self.name,
            'args': self.args,
            'kwargs': self.kwargs,
            'type': self.command_type.value,
            'raw_input': self.raw_input,
            'is_continuation': self.is_continuation
        }


class REPLSession:
    """
    REPL session manager extracted from repl_loop.j2.
    
    Manages session state, multi-line input, and command execution context.
    """
    
    def __init__(self, session_id: str, cli_config: Dict[str, Any]):
        self.session_id = session_id
        self.cli_config = cli_config
        self.variables: Dict[str, Any] = {}
        self.multi_line_buffer = ""
        self.is_multi_line_mode = False
        self.command_count = 0
        self.start_time = time.time()
        self.last_command_time = 0.0
        self.last_result = None
    
    def add_variable(self, name: str, value: Any) -> None:
        """Add a variable to the session context."""
        self.variables[name] = value
    
    def get_variable(self, name: str, default: Any = None) -> Any:
        """Get a variable from the session context."""
        return self.variables.get(name, default)
    
    def clear_variables(self) -> None:
        """Clear all session variables."""
        self.variables.clear()
    
    def get_session_info(self) -> Dict[str, Any]:
        """Get session information."""
        return {
            'session_id': self.session_id,
            'uptime': time.time() - self.start_time,
            'command_count': self.command_count,
            'variable_count': len(self.variables),
            'multi_line_mode': self.is_multi_line_mode,
            'last_command_time': self.last_command_time
        }


class CommandParser:
    """Enhanced command parser with multi-line support."""
    
    def __init__(self):
        self.continuation_char = '\\\\'
    
    def parse_command(self, input_line: str, session: REPLSession) -> Optional[REPLCommand]:
        """Parse a command line into a REPLCommand object."""
        if not input_line.strip():
            return None
        
        # Handle multi-line continuation
        if input_line.rstrip().endswith(self.continuation_char):
            # Remove continuation character and add to buffer
            session.multi_line_buffer += input_line.rstrip()[:-1] + ' '
            session.is_multi_line_mode = True
            return REPLCommand(
                name="",
                raw_input=input_line,
                is_continuation=True,
                command_type=REPLCommandType.MULTI_LINE
            )
        
        # If we were in multi-line mode, complete the command
        if session.is_multi_line_mode:
            full_command = session.multi_line_buffer + input_line
            session.multi_line_buffer = ""
            session.is_multi_line_mode = False
        else:
            full_command = input_line
        
        return self._parse_complete_command(full_command)
    
    def _parse_complete_command(self, command_line: str) -> REPLCommand:
        """Parse a complete command line."""
        command_line = command_line.strip()
        
        # Handle builtin commands
        if command_line.startswith(':'):
            return self._parse_builtin_command(command_line[1:])
        
        # Handle system commands
        if command_line.startswith('!'):
            return REPLCommand(
                name=command_line[1:],
                raw_input=command_line,
                command_type=REPLCommandType.SYSTEM_COMMAND
            )
        
        # Parse regular CLI command
        try:
            tokens = shlex.split(command_line)
        except ValueError:
            # Fallback to simple split if shlex fails
            tokens = command_line.split()
        
        if not tokens:
            return REPLCommand(name="", raw_input=command_line)
        
        command_name = tokens[0]
        args = []
        kwargs = {}
        
        # Parse arguments and options
        i = 1
        while i < len(tokens):
            token = tokens[i]
            
            if token.startswith('--'):
                # Long option
                if '=' in token:
                    key, value = token[2:].split('=', 1)
                    kwargs[key] = value
                else:
                    key = token[2:]
                    if i + 1 < len(tokens) and not tokens[i + 1].startswith('-'):
                        kwargs[key] = tokens[i + 1]
                        i += 1
                    else:
                        kwargs[key] = True
            elif token.startswith('-') and len(token) > 1:
                # Short option(s)
                for char in token[1:]:
                    if i + 1 < len(tokens) and not tokens[i + 1].startswith('-'):
                        kwargs[char] = tokens[i + 1]
                        i += 1
                        break
                    else:
                        kwargs[char] = True
            else:
                # Positional argument
                args.append(token)
            
            i += 1
        
        return REPLCommand(
            name=command_name,
            args=args,
            kwargs=kwargs,
            raw_input=command_line,
            command_type=REPLCommandType.CLI_COMMAND
        )
    
    def _parse_builtin_command(self, command_line: str) -> REPLCommand:
        """Parse builtin REPL commands (starting with :)."""
        tokens = command_line.split()
        if not tokens:
            return REPLCommand(name="", command_type=REPLCommandType.BUILTIN_COMMAND)
        
        return REPLCommand(
            name=tokens[0],
            args=tokens[1:],
            raw_input=f":{command_line}",
            command_type=REPLCommandType.BUILTIN_COMMAND
        )


class REPLEngine:
    """
    Enhanced REPL engine extracted from repl_loop.j2.
    
    Provides command parsing, execution, and session management
    with support for multi-line commands and smart completion.
    """
    
    def __init__(self, cli_config: Dict[str, Any]):
        self.cli_config = cli_config
        self.parser = CommandParser()
        self.builtin_commands: Dict[str, Callable] = {}
        self.hook_registry: Dict[str, Callable] = {}
        self.command_registry: Dict[str, Dict[str, Any]] = {}
        
        # Initialize command registry from CLI config
        self._build_command_registry()
        
        # Register default builtin commands
        self._register_builtin_commands()
    
    def create_session(self, session_id: Optional[str] = None) -> REPLSession:
        """Create a new REPL session."""
        if session_id is None:
            import uuid
            session_id = str(uuid.uuid4())[:8]
        
        return REPLSession(session_id, self.cli_config)
    
    def execute_command(self, command: REPLCommand, session: REPLSession) -> Tuple[bool, str, float]:
        """
        Execute a parsed command and return (success, output, execution_time).
        
        Args:
            command: Parsed command to execute
            session: Current REPL session
            
        Returns:
            Tuple of (success, output, execution_time_seconds)
        """
        if command.is_continuation:
            return True, "", 0.0
        
        start_time = time.time()
        session.command_count += 1
        
        try:
            if command.command_type == REPLCommandType.BUILTIN_COMMAND:
                return self._execute_builtin_command(command, session, start_time)
            elif command.command_type == REPLCommandType.SYSTEM_COMMAND:
                return self._execute_system_command(command, session, start_time)
            elif command.command_type == REPLCommandType.CLI_COMMAND:
                return self._execute_cli_command(command, session, start_time)
            else:
                return False, f"Unknown command type: {command.command_type}", 0.0
                
        except Exception as e:
            execution_time = time.time() - start_time
            session.last_command_time = execution_time
            return False, f"Error executing command: {e}", execution_time
    
    def _execute_builtin_command(self, command: REPLCommand, session: REPLSession, start_time: float) -> Tuple[bool, str, float]:
        """Execute a builtin REPL command."""
        if command.name in self.builtin_commands:
            try:
                result = self.builtin_commands[command.name](command, session)
                execution_time = time.time() - start_time
                session.last_command_time = execution_time
                session.last_result = result
                return True, str(result) if result is not None else "", execution_time
            except Exception as e:
                execution_time = time.time() - start_time
                session.last_command_time = execution_time
                return False, f"Error in builtin command '{command.name}': {e}", execution_time
        else:
            execution_time = time.time() - start_time
            session.last_command_time = execution_time
            return False, f"Unknown builtin command: {command.name}", execution_time
    
    def _execute_system_command(self, command: REPLCommand, session: REPLSession, start_time: float) -> Tuple[bool, str, float]:
        """Execute a system command."""
        try:
            import subprocess
            result = subprocess.run(
                command.name,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30  # 30 second timeout
            )
            
            execution_time = time.time() - start_time
            session.last_command_time = execution_time
            
            output = result.stdout
            if result.stderr:
                output += f"\\nSTDERR: {result.stderr}"
            
            return result.returncode == 0, output, execution_time
            
        except subprocess.TimeoutExpired:
            execution_time = time.time() - start_time
            session.last_command_time = execution_time
            return False, "Command timed out (30s limit)", execution_time
        except Exception as e:
            execution_time = time.time() - start_time
            session.last_command_time = execution_time
            return False, f"System command error: {e}", execution_time
    
    def _execute_cli_command(self, command: REPLCommand, session: REPLSession, start_time: float) -> Tuple[bool, str, float]:
        """Execute a CLI command via registered hooks."""
        if command.name not in self.command_registry:
            execution_time = time.time() - start_time
            session.last_command_time = execution_time
            return False, f"Unknown command: {command.name}", execution_time
        
        cmd_info = self.command_registry[command.name]
        hook_name = cmd_info.get('hook_name', f"on_{command.name.replace('-', '_')}")
        
        if hook_name in self.hook_registry:
            try:
                hook_func = self.hook_registry[hook_name]
                
                # Call hook function with appropriate arguments
                result = self._call_hook_function(hook_func, command, session)
                
                execution_time = time.time() - start_time
                session.last_command_time = execution_time
                session.last_result = result
                
                return True, str(result) if result is not None else f"Command '{command.name}' executed successfully", execution_time
                
            except Exception as e:
                execution_time = time.time() - start_time
                session.last_command_time = execution_time
                return False, f"Error executing '{command.name}': {e}", execution_time
        else:
            execution_time = time.time() - start_time
            session.last_command_time = execution_time
            return True, f"Command '{command.name}' executed (no hook registered)", execution_time
    
    def _call_hook_function(self, hook_func: Callable, command: REPLCommand, session: REPLSession) -> Any:
        """Call a hook function with appropriate arguments."""
        import inspect
        
        sig = inspect.signature(hook_func)
        params = list(sig.parameters.keys())
        
        # Try different calling conventions
        if len(params) == 0:
            return hook_func()
        elif len(params) == 1:
            # Pass command args as list
            return hook_func(command.args)
        elif len(params) == 2:
            # Pass args and kwargs separately
            return hook_func(command.args, command.kwargs)
        else:
            # Pass full context
            return hook_func(command.args, command.kwargs, session)
    
    def _build_command_registry(self) -> None:
        """Build command registry from CLI configuration."""
        root_command = self.cli_config.get('root_command', {})
        subcommands = root_command.get('subcommands', [])
        
        for cmd in subcommands:
            if isinstance(cmd, dict) and 'name' in cmd:
                self.command_registry[cmd['name']] = {
                    'description': cmd.get('description', ''),
                    'hook_name': cmd.get('hook_name', f"on_{cmd['name'].replace('-', '_')}"),
                    'arguments': cmd.get('arguments', []),
                    'options': cmd.get('options', [])
                }
    
    def _register_builtin_commands(self) -> None:
        """Register default builtin REPL commands."""
        self.builtin_commands.update({
            'help': self._builtin_help,
            'exit': self._builtin_exit,
            'quit': self._builtin_exit,
            'vars': self._builtin_vars,
            'clear': self._builtin_clear,
            'info': self._builtin_info,
            'set': self._builtin_set,
            'get': self._builtin_get
        })
    
    def register_hook(self, name: str, func: Callable) -> None:
        """Register a hook function for command execution."""
        self.hook_registry[name] = func
    
    def register_builtin_command(self, name: str, func: Callable) -> None:
        """Register a custom builtin command."""
        self.builtin_commands[name] = func
    
    def get_available_commands(self) -> List[Dict[str, str]]:
        """Get list of available commands with descriptions."""
        commands = []
        
        # CLI commands
        for name, info in self.command_registry.items():
            commands.append({
                'name': name,
                'type': 'cli',
                'description': info.get('description', 'No description')
            })
        
        # Builtin commands
        for name in self.builtin_commands.keys():
            commands.append({
                'name': f':{name}',
                'type': 'builtin',
                'description': f'Builtin REPL command: {name}'
            })
        
        return commands
    
    # Builtin command implementations
    def _builtin_help(self, command: REPLCommand, session: REPLSession) -> str:
        """Show help information."""
        help_lines = [
            "Available commands:",
            ""
        ]
        
        # Show CLI commands
        help_lines.append("CLI Commands:")
        for name, info in self.command_registry.items():
            help_lines.append(f"  {name:<20} {info.get('description', 'No description')}")
        
        help_lines.append("")
        help_lines.append("Builtin Commands (prefix with :):")
        builtin_descriptions = {
            'help': 'Show this help message',
            'exit': 'Exit the REPL',
            'quit': 'Exit the REPL', 
            'vars': 'Show session variables',
            'clear': 'Clear session variables',
            'info': 'Show session information',
            'set': 'Set a session variable',
            'get': 'Get a session variable'
        }
        
        for name in self.builtin_commands.keys():
            desc = builtin_descriptions.get(name, f'Builtin command: {name}')
            help_lines.append(f"  :{name:<19} {desc}")
        
        help_lines.extend([
            "",
            "Features:",
            "  Multi-line commands: End line with \\\\ to continue",
            "  System commands: Prefix with ! to run shell commands",
            "  Tab completion: Press TAB for command completion",
            "  Command history: Use UP/DOWN arrows to navigate history"
        ])
        
        return "\\n".join(help_lines)
    
    def _builtin_exit(self, command: REPLCommand, session: REPLSession) -> str:
        """Exit the REPL."""
        raise KeyboardInterrupt("REPL exit requested")
    
    def _builtin_vars(self, command: REPLCommand, session: REPLSession) -> str:
        """Show session variables."""
        if not session.variables:
            return "No session variables set"
        
        lines = ["Session Variables:"]
        for name, value in session.variables.items():
            value_str = str(value)[:100] + "..." if len(str(value)) > 100 else str(value)
            lines.append(f"  {name} = {value_str}")
        
        return "\\n".join(lines)
    
    def _builtin_clear(self, command: REPLCommand, session: REPLSession) -> str:
        """Clear session variables."""
        count = len(session.variables)
        session.clear_variables()
        return f"Cleared {count} session variables"
    
    def _builtin_info(self, command: REPLCommand, session: REPLSession) -> str:
        """Show session information."""
        info = session.get_session_info()
        lines = [
            f"Session ID: {info['session_id']}",
            f"Uptime: {info['uptime']:.1f} seconds",
            f"Commands executed: {info['command_count']}",
            f"Session variables: {info['variable_count']}",
            f"Multi-line mode: {info['multi_line_mode']}",
            f"Last command time: {info['last_command_time']:.3f} seconds"
        ]
        return "\\n".join(lines)
    
    def _builtin_set(self, command: REPLCommand, session: REPLSession) -> str:
        """Set a session variable."""
        if len(command.args) < 2:
            return "Usage: :set <name> <value>"
        
        name = command.args[0]
        value = ' '.join(command.args[1:])
        
        # Try to parse as different types
        try:
            if value.lower() in ('true', 'false'):
                value = value.lower() == 'true'
            elif value.isdigit():
                value = int(value)
            elif value.replace('.', '').replace('-', '').isdigit():
                value = float(value)
        except ValueError:
            pass  # Keep as string
        
        session.add_variable(name, value)
        return f"Set {name} = {value}"
    
    def _builtin_get(self, command: REPLCommand, session: REPLSession) -> str:
        """Get a session variable."""
        if len(command.args) != 1:
            return "Usage: :get <name>"
        
        name = command.args[0]
        value = session.get_variable(name)
        
        if value is None:
            return f"Variable '{name}' not set"
        
        return f"{name} = {value}"