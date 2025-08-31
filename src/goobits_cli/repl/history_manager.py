"""
History Manager
===============

Command history management system extracted from repl_loop.j2 template.
Provides persistent command history with search, filtering, and storage capabilities.
"""

from pathlib import Path
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from datetime import datetime


@dataclass
class HistoryEntry:
    """Single command history entry."""
    command: str
    timestamp: datetime
    success: bool = True
    execution_time: float = 0.0
    output: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'command': self.command,
            'timestamp': self.timestamp.isoformat(),
            'success': self.success,
            'execution_time': self.execution_time,
            'output': self.output
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'HistoryEntry':
        """Create from dictionary during deserialization."""
        return cls(
            command=data['command'],
            timestamp=datetime.fromisoformat(data['timestamp']),
            success=data.get('success', True),
            execution_time=data.get('execution_time', 0.0),
            output=data.get('output')
        )


class HistoryManager:
    """
    Enhanced command history manager extracted from repl_loop.j2.
    
    Provides persistent command history with search capabilities,
    duplicate filtering, and configurable storage options.
    """
    
    def __init__(self, cli_name: str, max_entries: int = 1000, enable_persistence: bool = True):
        self.cli_name = cli_name
        self.max_entries = max_entries
        self.enable_persistence = enable_persistence
        
        self._history: List[HistoryEntry] = []
        self._history_file = Path.home() / f'.{cli_name}_repl_history'
        self._session_start = datetime.now()
        
        if enable_persistence:
            self._load_history()
    
    def add_command(self, 
                   command: str, 
                   success: bool = True,
                   execution_time: float = 0.0,
                   output: Optional[str] = None) -> None:
        """Add a command to the history."""
        if not command.strip():
            return
        
        # Skip duplicates of the last command
        if self._history and self._history[-1].command == command.strip():
            return
        
        entry = HistoryEntry(
            command=command.strip(),
            timestamp=datetime.now(),
            success=success,
            execution_time=execution_time,
            output=output
        )
        
        self._history.append(entry)
        
        # Trim history if it exceeds max entries
        if len(self._history) > self.max_entries:
            self._history = self._history[-self.max_entries:]
        
        # Save to disk if persistence enabled
        if self.enable_persistence:
            self._save_history()
    
    def get_history(self, limit: Optional[int] = None) -> List[HistoryEntry]:
        """Get command history, optionally limited to recent entries."""
        history = self._history
        if limit:
            history = history[-limit:]
        return history.copy()
    
    def search_history(self, query: str, case_sensitive: bool = False) -> List[HistoryEntry]:
        """Search command history for matching entries."""
        if not query:
            return self.get_history()
        
        if not case_sensitive:
            query = query.lower()
        
        matches = []
        for entry in self._history:
            command = entry.command if case_sensitive else entry.command.lower()
            if query in command:
                matches.append(entry)
        
        return matches
    
    def get_recent_commands(self, count: int = 10) -> List[str]:
        """Get recent command strings (for readline-style completion)."""
        recent = self._history[-count:] if len(self._history) >= count else self._history
        return [entry.command for entry in recent]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get history statistics."""
        if not self._history:
            return {
                'total_commands': 0,
                'session_commands': 0,
                'success_rate': 0.0,
                'avg_execution_time': 0.0
            }
        
        session_commands = [
            entry for entry in self._history 
            if entry.timestamp >= self._session_start
        ]
        
        successful_commands = [entry for entry in self._history if entry.success]
        total_execution_time = sum(entry.execution_time for entry in self._history)
        
        return {
            'total_commands': len(self._history),
            'session_commands': len(session_commands),
            'success_rate': len(successful_commands) / len(self._history) * 100,
            'avg_execution_time': total_execution_time / len(self._history) if self._history else 0,
            'most_used_commands': self._get_most_used_commands(5)
        }
    
    def _get_most_used_commands(self, count: int) -> List[Dict[str, Any]]:
        """Get the most frequently used commands."""
        command_counts = {}
        for entry in self._history:
            # Get the first word (command name) for counting
            cmd_name = entry.command.split()[0] if entry.command.split() else entry.command
            command_counts[cmd_name] = command_counts.get(cmd_name, 0) + 1
        
        # Sort by count and return top N
        sorted_commands = sorted(command_counts.items(), key=lambda x: x[1], reverse=True)
        return [
            {'command': cmd, 'count': count} 
            for cmd, count in sorted_commands[:count]
        ]
    
    def clear_history(self, confirm: bool = False) -> bool:
        """Clear all command history."""
        if not confirm:
            return False
        
        self._history.clear()
        
        if self.enable_persistence and self._history_file.exists():
            try:
                self._history_file.unlink()
                return True
            except OSError:
                return False
        
        return True
    
    def export_history(self, output_file: Path, format: str = 'text') -> bool:
        """Export history to a file."""
        try:
            if format == 'text':
                with open(output_file, 'w') as f:
                    for entry in self._history:
                        f.write(f"{entry.timestamp.strftime('%Y-%m-%d %H:%M:%S')} - {entry.command}\\n")
            elif format == 'json':
                import json
                with open(output_file, 'w') as f:
                    history_data = [entry.to_dict() for entry in self._history]
                    json.dump(history_data, f, indent=2)
            else:
                return False
            
            return True
        except (OSError, IOError):
            return False
    
    def _load_history(self) -> None:
        """Load command history from disk."""
        if not self._history_file.exists():
            return
        
        try:
            # Try loading as JSON first (enhanced format)
            with open(self._history_file, 'r') as f:
                content = f.read().strip()
                # JSON format only
                import json
                history_data = json.loads(content)
                self._history = [HistoryEntry.from_dict(entry) for entry in history_data]
                    
        except (OSError, IOError, ValueError, json.JSONDecodeError):
            # If loading fails, start with empty history
            self._history = []
    
    def _save_history(self) -> None:
        """Save command history to disk."""
        if not self.enable_persistence:
            return
        
        try:
            # Save in JSON format for enhanced features
            import json
            history_data = [entry.to_dict() for entry in self._history]
            
            # Ensure parent directory exists
            self._history_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self._history_file, 'w') as f:
                json.dump(history_data, f, indent=2)
                
        except (OSError, IOError, json.JSONEncodeError):
            # Fallback to simple text format
            try:
                with open(self._history_file, 'w') as f:
                    for entry in self._history:
                        f.write(f"{entry.command}\\n")
            except (OSError, IOError):
                pass  # Give up on persistence if all methods fail
    
    def get_completion_suggestions(self, current_input: str) -> List[str]:
        """Get command completion suggestions based on history."""
        if not current_input:
            return self.get_recent_commands(5)
        
        suggestions = []
        current_lower = current_input.lower()
        
        # Look for commands that start with the current input
        seen = set()
        for entry in reversed(self._history):
            if entry.command.lower().startswith(current_lower):
                if entry.command not in seen:
                    suggestions.append(entry.command)
                    seen.add(entry.command)
                    
                if len(suggestions) >= 10:  # Limit suggestions
                    break
        
        return suggestions
    
    def __len__(self) -> int:
        """Get the number of entries in history."""
        return len(self._history)
    
    def __bool__(self) -> bool:
        """Check if history has any entries."""
        return bool(self._history)