"""
Session management system for REPL mode in Goobits CLI Framework.

Provides persistent sessions that can save/restore REPL state including
command history, timestamps, and execution metadata. Built on the same
patterns as the subprocess cache system for consistency and reliability.
"""

import json
import time
import hashlib
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
from dataclasses import dataclass, asdict, field
from threading import Lock
import logging
import os
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class CommandEntry:
    """Represents a single command in session history."""
    
    command: str
    timestamp: float
    success: bool = True
    duration_ms: Optional[int] = None
    output_preview: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'command': self.command,
            'timestamp': self.timestamp,
            'success': self.success,
            'duration_ms': self.duration_ms,
            'output_preview': self.output_preview[:100] if self.output_preview else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CommandEntry':
        """Create from dictionary loaded from JSON."""
        return cls(
            command=data['command'],
            timestamp=data['timestamp'],
            success=data.get('success', True),
            duration_ms=data.get('duration_ms'),
            output_preview=data.get('output_preview')
        )


@dataclass
class SessionMetadata:
    """Metadata for a session."""
    
    session_name: str
    cli_name: str
    creation_date: float
    last_modified: float
    command_count: int = 0
    success_rate: float = 1.0
    total_duration_ms: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SessionMetadata':
        """Create from dictionary loaded from JSON."""
        return cls(**data)


class CommandHistory:
    """
    Enhanced command history tracking with metadata.
    
    Features:
    - Command execution tracking with timestamps
    - Success/failure status recording
    - Performance metrics (duration)
    - Memory-efficient circular buffer for large histories
    - Smart serialization for persistence
    """
    
    def __init__(self, max_entries: int = 1000):
        """
        Initialize command history.
        
        Args:
            max_entries: Maximum number of commands to keep in memory
        """
        self.entries: List[CommandEntry] = []
        self.max_entries = max_entries
        self._lock = Lock()
        
    def add_command(
        self,
        command: str,
        success: bool = True,
        duration_ms: Optional[int] = None,
        output_preview: Optional[str] = None
    ):
        """
        Add a command to the history.
        
        Args:
            command: The command that was executed
            success: Whether the command succeeded
            duration_ms: How long the command took to execute
            output_preview: First few lines of output for context
        """
        with self._lock:
            entry = CommandEntry(
                command=command.strip(),
                timestamp=time.time(),
                success=success,
                duration_ms=duration_ms,
                output_preview=output_preview
            )
            
            self.entries.append(entry)
            
            # Maintain circular buffer
            if len(self.entries) > self.max_entries:
                self.entries.pop(0)
    
    def get_recent_commands(self, count: int = 10) -> List[CommandEntry]:
        """Get the most recent commands."""
        with self._lock:
            return self.entries[-count:]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about command history."""
        with self._lock:
            if not self.entries:
                return {
                    'total_commands': 0,
                    'success_rate': 0.0,
                    'avg_duration_ms': 0.0,
                    'most_common_commands': []
                }
            
            total_commands = len(self.entries)
            successful_commands = sum(1 for entry in self.entries if entry.success)
            success_rate = successful_commands / total_commands
            
            # Calculate average duration (only for commands with timing data)
            timed_commands = [e for e in self.entries if e.duration_ms is not None]
            avg_duration = (
                sum(e.duration_ms for e in timed_commands) / len(timed_commands)
                if timed_commands else 0.0
            )
            
            # Find most common commands
            command_counts = {}
            for entry in self.entries:
                cmd_base = entry.command.split()[0] if entry.command.split() else ""
                command_counts[cmd_base] = command_counts.get(cmd_base, 0) + 1
            
            most_common = sorted(
                command_counts.items(),
                key=lambda x: x[1],
                reverse=True
            )[:5]
            
            return {
                'total_commands': total_commands,
                'success_rate': success_rate,
                'avg_duration_ms': avg_duration,
                'most_common_commands': most_common
            }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        with self._lock:
            return {
                'entries': [entry.to_dict() for entry in self.entries],
                'max_entries': self.max_entries
            }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CommandHistory':
        """Create from dictionary loaded from JSON."""
        history = cls(max_entries=data.get('max_entries', 1000))
        history.entries = [
            CommandEntry.from_dict(entry_data)
            for entry_data in data.get('entries', [])
        ]
        return history


class SessionManager:
    """
    Session management system following subprocess cache patterns.
    
    Features:
    - JSON-based session persistence with smart serialization
    - Session discovery and listing with metadata
    - TTL-based cleanup and compression
    - Thread-safe operations
    - Graceful error handling and recovery
    - Cross-platform storage location handling
    """
    
    def __init__(
        self,
        cli_name: str,
        session_directory: Optional[str] = None,
        max_sessions: int = 20,
        auto_cleanup: bool = True
    ):
        """
        Initialize the session manager.
        
        Args:
            cli_name: Name of the CLI (for namespacing sessions)
            session_directory: Custom directory for session storage
            max_sessions: Maximum number of sessions to keep
            auto_cleanup: Whether to automatically clean up old sessions
        """
        self.cli_name = cli_name
        self.max_sessions = max_sessions
        self.auto_cleanup = auto_cleanup
        self._lock = Lock()
        
        # Setup session directory
        if session_directory:
            self.session_dir = Path(session_directory).expanduser()
        else:
            # Use standard location: ~/.goobits/sessions/<cli_name>/
            home = Path.home()
            self.session_dir = home / ".goobits" / "sessions" / cli_name
        
        # Create directory if it doesn't exist
        try:
            self.session_dir.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            logger.warning(f"Could not create session directory {self.session_dir}: {e}")
            # Fallback to temp directory
            import tempfile
            self.session_dir = Path(tempfile.gettempdir()) / "goobits_sessions" / cli_name
            self.session_dir.mkdir(parents=True, exist_ok=True)
        
        logger.debug(f"Session manager initialized for {cli_name}, directory: {self.session_dir}")
    
    def _get_session_file(self, session_name: str) -> Path:
        """Get the file path for a session."""
        # Sanitize session name for filesystem safety
        safe_name = "".join(c for c in session_name if c.isalnum() or c in "._-")[:50]
        if not safe_name:
            safe_name = "default"
        
        return self.session_dir / f"{safe_name}.json"
    
    def _cleanup_old_sessions(self):
        """Clean up old sessions to maintain max_sessions limit."""
        if not self.auto_cleanup:
            return
        
        try:
            session_files = list(self.session_dir.glob("*.json"))
            if len(session_files) <= self.max_sessions:
                return
            
            # Sort by modification time and remove oldest
            session_files.sort(key=lambda f: f.stat().st_mtime)
            files_to_remove = session_files[:-self.max_sessions]
            
            for file_path in files_to_remove:
                try:
                    file_path.unlink()
                    logger.debug(f"Removed old session: {file_path.name}")
                except OSError as e:
                    logger.warning(f"Could not remove old session {file_path}: {e}")
        
        except Exception as e:
            logger.warning(f"Error during session cleanup: {e}")
    
    def save_session(
        self,
        session_name: str,
        command_history: CommandHistory,
        metadata: Optional[Dict[str, Any]] = None,
        variable_store: Optional['VariableStore'] = None
    ) -> bool:
        """
        Save a session to persistent storage.
        
        Args:
            session_name: Name of the session
            command_history: Command history to save
            metadata: Additional metadata to include
            variable_store: Variable store to save (optional)
            
        Returns:
            True if saved successfully, False otherwise
        """
        session_file = self._get_session_file(session_name)
        
        try:
            with self._lock:
                # Create session metadata
                stats = command_history.get_statistics()
                session_metadata = SessionMetadata(
                    session_name=session_name,
                    cli_name=self.cli_name,
                    creation_date=time.time(),
                    last_modified=time.time(),
                    command_count=stats['total_commands'],
                    success_rate=stats['success_rate'],
                    total_duration_ms=int(stats.get('avg_duration_ms', 0) * stats['total_commands'])
                )
                
                # Prepare session data
                session_data = {
                    'metadata': session_metadata.to_dict(),
                    'command_history': command_history.to_dict(),
                    'custom_metadata': metadata or {},
                    'version': '1.0'
                }
                
                # Add variable store data if provided
                if variable_store is not None:
                    session_data['variable_store'] = variable_store.to_dict()
                
                # Write to file with atomic operation
                temp_file = session_file.with_suffix('.tmp')
                with open(temp_file, 'w', encoding='utf-8') as f:
                    json.dump(session_data, f, indent=2, ensure_ascii=False)
                
                # Atomic move
                temp_file.replace(session_file)
                
                logger.info(f"Session '{session_name}' saved successfully")
                
                # Cleanup old sessions
                self._cleanup_old_sessions()
                
                return True
        
        except Exception as e:
            logger.error(f"Failed to save session '{session_name}': {e}")
            # Clean up temp file if it exists
            temp_file = session_file.with_suffix('.tmp')
            if temp_file.exists():
                try:
                    temp_file.unlink()
                except:
                    pass
            return False
    
    def load_session(self, session_name: str) -> Optional[tuple[CommandHistory, Dict[str, Any], Optional['VariableStore']]]:
        """
        Load a session from persistent storage.
        
        Args:
            session_name: Name of the session to load
            
        Returns:
            Tuple of (CommandHistory, metadata, variable_store) or None if not found
        """
        session_file = self._get_session_file(session_name)
        
        if not session_file.exists():
            logger.warning(f"Session '{session_name}' not found")
            return None
        
        try:
            with self._lock:
                with open(session_file, 'r', encoding='utf-8') as f:
                    session_data = json.load(f)
                
                # Validate session data
                if 'command_history' not in session_data:
                    logger.error(f"Invalid session file: {session_file}")
                    return None
                
                # Load command history
                command_history = CommandHistory.from_dict(session_data['command_history'])
                
                # Load variable store if present
                variable_store = None
                if 'variable_store' in session_data:
                    try:
                        # Import here to avoid circular imports
                        from .variable_store import VariableStore
                        variable_store = VariableStore.from_dict(session_data['variable_store'])
                    except Exception as e:
                        logger.warning(f"Failed to load variable store for session '{session_name}': {e}")
                
                # Load metadata
                metadata = {
                    'session_metadata': session_data.get('metadata', {}),
                    'custom_metadata': session_data.get('custom_metadata', {}),
                    'version': session_data.get('version', '1.0')
                }
                
                logger.info(f"Session '{session_name}' loaded successfully")
                return command_history, metadata, variable_store
        
        except Exception as e:
            logger.error(f"Failed to load session '{session_name}': {e}")
            return None
    
    def list_sessions(self) -> List[Dict[str, Any]]:
        """
        List all available sessions with metadata.
        
        Returns:
            List of session information dictionaries
        """
        sessions = []
        
        try:
            session_files = list(self.session_dir.glob("*.json"))
            
            for session_file in session_files:
                try:
                    with open(session_file, 'r', encoding='utf-8') as f:
                        session_data = json.load(f)
                    
                    metadata = session_data.get('metadata', {})
                    session_info = {
                        'name': session_file.stem,
                        'cli_name': metadata.get('cli_name', 'unknown'),
                        'creation_date': metadata.get('creation_date', 0),
                        'last_modified': metadata.get('last_modified', 0),
                        'command_count': metadata.get('command_count', 0),
                        'success_rate': metadata.get('success_rate', 0.0),
                        'file_size_bytes': session_file.stat().st_size
                    }
                    
                    sessions.append(session_info)
                
                except Exception as e:
                    logger.warning(f"Could not read session file {session_file}: {e}")
            
            # Sort by last modified (most recent first)
            sessions.sort(key=lambda s: s['last_modified'], reverse=True)
        
        except Exception as e:
            logger.error(f"Failed to list sessions: {e}")
        
        return sessions
    
    def delete_session(self, session_name: str) -> bool:
        """
        Delete a session from persistent storage.
        
        Args:
            session_name: Name of the session to delete
            
        Returns:
            True if deleted successfully, False otherwise
        """
        session_file = self._get_session_file(session_name)
        
        if not session_file.exists():
            logger.warning(f"Session '{session_name}' not found")
            return False
        
        try:
            with self._lock:
                session_file.unlink()
                logger.info(f"Session '{session_name}' deleted successfully")
                return True
        
        except Exception as e:
            logger.error(f"Failed to delete session '{session_name}': {e}")
            return False
    
    def session_exists(self, session_name: str) -> bool:
        """Check if a session exists."""
        return self._get_session_file(session_name).exists()
    
    def get_session_stats(self) -> Dict[str, Any]:
        """Get overall session storage statistics."""
        try:
            session_files = list(self.session_dir.glob("*.json"))
            total_size = sum(f.stat().st_size for f in session_files)
            
            return {
                'total_sessions': len(session_files),
                'storage_size_bytes': total_size,
                'storage_size_mb': total_size / (1024 * 1024),
                'directory': str(self.session_dir),
                'max_sessions': self.max_sessions
            }
        
        except Exception as e:
            logger.error(f"Failed to get session stats: {e}")
            return {
                'total_sessions': 0,
                'storage_size_bytes': 0,
                'storage_size_mb': 0.0,
                'directory': str(self.session_dir),
                'max_sessions': self.max_sessions
            }


# Global session manager instance
_session_manager: Optional[SessionManager] = None


def get_session_manager(cli_name: str, **kwargs) -> SessionManager:
    """Get the global session manager instance."""
    global _session_manager
    if _session_manager is None or _session_manager.cli_name != cli_name:
        _session_manager = SessionManager(cli_name, **kwargs)
    return _session_manager


def create_session_manager(cli_name: str, config: Optional[Dict[str, Any]] = None) -> SessionManager:
    """
    Factory function to create a SessionManager instance from configuration.
    
    Args:
        cli_name: Name of the CLI
        config: Configuration dictionary with session settings
        
    Returns:
        Configured SessionManager instance
    """
    if not config:
        config = {}
    
    # Extract configuration
    session_dir = config.get('session_directory')
    max_sessions = config.get('max_sessions', 20)
    auto_cleanup = config.get('auto_cleanup', True)
    
    return SessionManager(
        cli_name=cli_name,
        session_directory=session_dir,
        max_sessions=max_sessions,
        auto_cleanup=auto_cleanup
    )