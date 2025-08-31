"""
Completion Engine
=================

Completion logic and generation engine extracted from completion_engine.j2 template.
Provides intelligent completion suggestions with context awareness.
"""

from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum


class CompletionType(Enum):
    """Types of completions available."""
    COMMAND = "command"
    OPTION = "option"  
    ARGUMENT = "argument"
    FILE = "file"
    DIRECTORY = "directory"
    CUSTOM = "custom"


@dataclass
class CompletionContext:
    """Context information for completion generation."""
    current_word: str = ""
    previous_word: str = ""
    command_line: str = ""
    cursor_position: int = 0
    words: List[str] = field(default_factory=list)
    current_command: Optional[str] = None
    available_options: Set[str] = field(default_factory=set)
    used_options: Set[str] = field(default_factory=set)
    
    def get_unused_options(self) -> Set[str]:
        """Get options that haven't been used yet."""
        return self.available_options - self.used_options
    
    def is_option_context(self) -> bool:
        """Check if we're in an option completion context."""
        return self.current_word.startswith('-') or self.previous_word.startswith('-')
    
    def get_command_chain(self) -> List[str]:
        """Get the chain of commands/subcommands."""
        chain = []
        for word in self.words:
            if not word.startswith('-') and word != self.current_word:
                chain.append(word)
        return chain[1:]  # Skip the CLI name itself


@dataclass
class CompletionResult:
    """Result of completion generation."""
    completions: List[str] = field(default_factory=list)
    completion_type: CompletionType = CompletionType.COMMAND
    description: Optional[str] = None
    has_space: bool = True
    prefix: str = ""
    
    def filter_completions(self, prefix: str) -> 'CompletionResult':
        """Filter completions by prefix."""
        filtered = [c for c in self.completions if c.startswith(prefix)]
        return CompletionResult(
            completions=filtered,
            completion_type=self.completion_type,
            description=self.description,
            has_space=self.has_space,
            prefix=prefix
        )
    
    def add_completion(self, completion: str) -> None:
        """Add a completion to the result."""
        if completion not in self.completions:
            self.completions.append(completion)


class CompletionProvider:
    """Base class for completion providers."""
    
    def __init__(self, name: str):
        self.name = name
    
    def can_provide(self, context: CompletionContext) -> bool:
        """Check if this provider can provide completions for the context."""
        return False
    
    def provide_completions(self, context: CompletionContext) -> CompletionResult:
        """Provide completions for the given context."""
        return CompletionResult()


class CommandCompletionProvider(CompletionProvider):
    """Provides command and subcommand completions."""
    
    def __init__(self, commands: Dict[str, Any]):
        super().__init__("commands")
        self.commands = commands
    
    def can_provide(self, context: CompletionContext) -> bool:
        """Can provide if we're not in an option context."""
        return not context.is_option_context()
    
    def provide_completions(self, context: CompletionContext) -> CompletionResult:
        """Provide command completions."""
        chain = context.get_command_chain()
        
        # Navigate to the right level in the command tree
        current_commands = self.commands
        for cmd in chain:
            if cmd in current_commands:
                subcommands = current_commands[cmd].get('subcommands', {})
                if subcommands:
                    current_commands = subcommands
                else:
                    break
            else:
                break
        
        completions = list(current_commands.keys())
        
        return CompletionResult(
            completions=completions,
            completion_type=CompletionType.COMMAND,
            description="Available commands"
        )


class OptionCompletionProvider(CompletionProvider):
    """Provides option completions."""
    
    def __init__(self, commands: Dict[str, Any]):
        super().__init__("options")
        self.commands = commands
    
    def can_provide(self, context: CompletionContext) -> bool:
        """Can provide if current word starts with - or previous word needs an argument."""
        return (context.current_word.startswith('-') or 
                self._previous_option_needs_value(context.previous_word))
    
    def provide_completions(self, context: CompletionContext) -> CompletionResult:
        """Provide option completions."""
        if not context.current_command:
            return CompletionResult()
        
        # Find the command in the tree
        cmd_data = self._find_command_data(context.current_command, context.get_command_chain())
        if not cmd_data:
            return CompletionResult()
        
        options = []
        for opt in cmd_data.get('options', []):
            opt_name = opt.get('name', '')
            if opt_name and opt_name not in context.used_options:
                options.append(opt_name)
        
        # Filter by current prefix if it starts with -
        if context.current_word.startswith('-'):
            options = [opt for opt in options if opt.startswith(context.current_word)]
        
        return CompletionResult(
            completions=options,
            completion_type=CompletionType.OPTION,
            description="Available options"
        )
    
    def _find_command_data(self, command: str, chain: List[str]) -> Optional[Dict[str, Any]]:
        """Find command data in the command tree."""
        current = self.commands.get(command)
        if not current:
            return None
        
        for cmd in chain:
            subcommands = current.get('subcommands', {})
            if cmd in subcommands:
                current = subcommands[cmd]
            else:
                break
        
        return current
    
    def _previous_option_needs_value(self, word: str) -> bool:
        """Check if the previous word is an option that needs a value."""
        # This is a simplified check - in reality you'd look up the option definition
        return word.startswith('-') and not word.startswith('--help') and not word.startswith('--version')


class FileCompletionProvider(CompletionProvider):
    """Provides file and directory completions."""
    
    def __init__(self):
        super().__init__("files")
    
    def can_provide(self, context: CompletionContext) -> bool:
        """Can provide file completions for file-related options or arguments."""
        # Simplified - would normally check option types
        return ('file' in context.current_word.lower() or 
                'path' in context.current_word.lower() or
                context.current_word.startswith('./') or
                context.current_word.startswith('/'))
    
    def provide_completions(self, context: CompletionContext) -> CompletionResult:
        """Provide file/directory completions."""
        from pathlib import Path
        
        current_word = context.current_word
        if not current_word:
            current_word = "./"
        
        try:
            path = Path(current_word).expanduser()
            if path.is_dir():
                base_path = path
                prefix = ""
            else:
                base_path = path.parent
                prefix = path.name
            
            completions = []
            for item in base_path.iterdir():
                if item.name.startswith(prefix):
                    name = str(item.relative_to(base_path))
                    if item.is_dir():
                        name += "/"
                    completions.append(name)
            
            return CompletionResult(
                completions=sorted(completions),
                completion_type=CompletionType.FILE,
                description="Files and directories",
                has_space=False
            )
        
        except (OSError, PermissionError):
            return CompletionResult()


class CompletionEngine:
    """
    Advanced completion engine extracted from completion_engine.j2.
    
    Provides intelligent, context-aware completions for CLI commands.
    """
    
    def __init__(self, commands: Dict[str, Any]):
        self.commands = commands
        self.providers: List[CompletionProvider] = []
        self._register_default_providers()
    
    def _register_default_providers(self):
        """Register default completion providers."""
        self.providers = [
            CommandCompletionProvider(self.commands),
            OptionCompletionProvider(self.commands),
            FileCompletionProvider()
        ]
    
    def add_provider(self, provider: CompletionProvider):
        """Add a custom completion provider."""
        self.providers.append(provider)
    
    def generate_completions(self, 
                           command_line: str,
                           cursor_position: Optional[int] = None) -> CompletionResult:
        """
        Generate completions for a command line.
        
        Args:
            command_line: The current command line
            cursor_position: Position of cursor (None = end of line)
            
        Returns:
            CompletionResult with appropriate completions
        """
        context = self._build_context(command_line, cursor_position)
        
        # Try each provider in order
        for provider in self.providers:
            if provider.can_provide(context):
                result = provider.provide_completions(context)
                if result.completions:
                    # Filter by current word if needed
                    if context.current_word and not context.current_word.startswith('-'):
                        result = result.filter_completions(context.current_word)
                    return result
        
        return CompletionResult()
    
    def _build_context(self, command_line: str, cursor_position: Optional[int]) -> CompletionContext:
        """Build completion context from command line."""
        if cursor_position is None:
            cursor_position = len(command_line)
        
        # Parse the command line
        words = self._parse_command_line(command_line)
        
        # Find current and previous word
        current_word = ""
        previous_word = ""
        
        # Simple word detection based on cursor position
        line_to_cursor = command_line[:cursor_position]
        words_to_cursor = self._parse_command_line(line_to_cursor)
        
        if words_to_cursor:
            if line_to_cursor.endswith(' '):
                current_word = ""
                previous_word = words_to_cursor[-1] if words_to_cursor else ""
            else:
                current_word = words_to_cursor[-1]
                previous_word = words_to_cursor[-2] if len(words_to_cursor) > 1 else ""
        
        # Determine current command
        current_command = None
        if len(words) > 1:
            current_command = words[1]  # First word after CLI name
        
        # Find available and used options
        available_options = set()
        used_options = set()
        
        if current_command and current_command in self.commands:
            cmd_data = self.commands[current_command]
            for opt in cmd_data.get('options', []):
                opt_name = opt.get('name', '')
                if opt_name:
                    available_options.add(opt_name)
        
        # Find used options in the command line
        for word in words:
            if word.startswith('-') and word in available_options:
                used_options.add(word)
        
        return CompletionContext(
            current_word=current_word,
            previous_word=previous_word,
            command_line=command_line,
            cursor_position=cursor_position,
            words=words,
            current_command=current_command,
            available_options=available_options,
            used_options=used_options
        )
    
    def _parse_command_line(self, command_line: str) -> List[str]:
        """Parse command line into words, respecting quotes."""
        import shlex
        try:
            return shlex.split(command_line)
        except ValueError:
            # Fallback for incomplete quotes
            return command_line.split()
    
    def complete_bash(self, command_line: str) -> List[str]:
        """Generate completions in bash format."""
        result = self.generate_completions(command_line)
        return result.completions
    
    def complete_zsh(self, command_line: str) -> List[Tuple[str, str]]:
        """Generate completions in zsh format (value, description)."""
        result = self.generate_completions(command_line)
        description = result.description or ""
        return [(comp, description) for comp in result.completions]
    
    def complete_fish(self, command_line: str) -> List[Dict[str, str]]:
        """Generate completions in fish format."""
        result = self.generate_completions(command_line)
        return [
            {
                'completion': comp,
                'description': result.description or ""
            }
            for comp in result.completions
        ]
    
    def get_completion_stats(self) -> Dict[str, Any]:
        """Get statistics about completion capabilities."""
        stats = {
            'total_commands': len(self.commands),
            'providers': len(self.providers),
            'provider_names': [p.name for p in self.providers],
            'supports_subcommands': any(
                'subcommands' in cmd_data 
                for cmd_data in self.commands.values()
                if isinstance(cmd_data, dict)
            )
        }
        
        # Count total options
        total_options = 0
        for cmd_data in self.commands.values():
            if isinstance(cmd_data, dict):
                total_options += len(cmd_data.get('options', []))
        
        stats['total_options'] = total_options
        return stats