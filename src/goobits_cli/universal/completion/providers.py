"""
Context-aware completion providers for Goobits CLI Framework.

Provides intelligent completion for files, environment variables, 
configuration keys, and command history.
"""

import os
import glob
import json
import yaml
from pathlib import Path
from typing import List, Dict, Set, Optional, Any
import logging

from .registry import CompletionProvider, CompletionContext

logger = logging.getLogger(__name__)


class FilePathCompletionProvider(CompletionProvider):
    """
    Intelligent file path completion with context-aware filtering.
    
    Features:
    - Smart file type filtering based on command context
    - Directory navigation completion
    - Hidden file handling
    - Cross-platform path handling
    """
    
    def __init__(self, priority: int = 80):
        """Initialize with high priority for file completions."""
        super().__init__(priority)
        
        # File type filters based on context
        self.file_filters = {
            'config': ['.yaml', '.yml', '.json', '.toml', '.ini'],
            'source': ['.py', '.js', '.ts', '.rs', '.go', '.java', '.cpp', '.c'],
            'data': ['.csv', '.json', '.xml', '.sqlite', '.db'],
            'document': ['.md', '.txt', '.pdf', '.doc', '.docx'],
            'image': ['.png', '.jpg', '.jpeg', '.gif', '.svg'],
            'archive': ['.zip', '.tar', '.gz', '.bz2', '.7z']
        }
        
        # Commands that typically expect files
        self.file_commands = {
            'cat', 'less', 'more', 'head', 'tail', 'edit', 'vi', 'vim',
            'nano', 'code', 'open', 'cp', 'mv', 'rm', 'chmod', 'chown',
            'diff', 'grep', 'find', 'locate', 'file', 'stat'
        }
    
    def can_provide(self, context: CompletionContext) -> bool:
        """Check if we should provide file path completions."""
        # Always provide if current word looks like a path
        if ('/' in context.current_word or 
            context.current_word.startswith('.') or
            context.current_word.startswith('~')):
            return True
        
        # Provide if command typically expects files
        if context.current_command in self.file_commands:
            return True
        
        # Provide if previous argument suggests file input
        if context.args:
            prev_args = ' '.join(context.args[-2:]).lower()
            if any(keyword in prev_args for keyword in 
                   ['file', 'path', 'input', 'output', 'config', 'load', 'save']):
                return True
        
        # Check metadata for file context
        return context.metadata.get('is_file_context', False)
    
    async def provide_completions(self, context: CompletionContext) -> List[str]:
        """Provide file path completions."""
        try:
            current_word = context.current_word
            
            # Handle empty input - show current directory
            if not current_word:
                return await self._complete_directory(context.cwd)
            
            # Expand user home directory
            if current_word.startswith('~'):
                current_word = str(Path(current_word).expanduser())
            
            # Handle absolute vs relative paths
            if current_word.startswith('/'):
                base_path = Path('/')
                pattern = current_word[1:]
            else:
                base_path = context.cwd
                pattern = current_word
            
            # Split path into directory and filename parts
            if '/' in pattern:
                dir_part, file_part = pattern.rsplit('/', 1)
                search_dir = base_path / dir_part
                prefix = f"{pattern[:len(pattern)-len(file_part)]}"
            else:
                search_dir = base_path
                file_part = pattern
                prefix = ""
            
            if not search_dir.exists():
                return []
            
            # Get completions from directory
            completions = []
            
            try:
                for item in search_dir.iterdir():
                    name = item.name
                    
                    # Skip hidden files unless explicitly requested
                    if name.startswith('.') and not file_part.startswith('.'):
                        continue
                    
                    # Filter by partial match
                    if not name.startswith(file_part):
                        continue
                    
                    # Build completion string
                    completion = prefix + name
                    
                    # Add trailing slash for directories
                    if item.is_dir():
                        completion += '/'
                    
                    completions.append(completion)
                
                # Apply context-specific filtering
                filtered = self._apply_context_filtering(context, completions)
                
                # Sort: directories first, then files
                return sorted(filtered, key=lambda x: (not x.endswith('/'), x.lower()))
                
            except PermissionError:
                logger.debug(f"Permission denied accessing {search_dir}")
                return []
            
        except Exception as e:
            logger.error(f"Error in file path completion: {e}")
            return []
    
    async def _complete_directory(self, directory: Path) -> List[str]:
        """Complete contents of a directory."""
        completions = []
        
        try:
            for item in directory.iterdir():
                name = item.name
                
                # Skip hidden files by default
                if name.startswith('.'):
                    continue
                
                if item.is_dir():
                    completions.append(name + '/')
                else:
                    completions.append(name)
            
            return sorted(completions, key=lambda x: (not x.endswith('/'), x.lower()))
            
        except (PermissionError, OSError):
            return []
    
    def _apply_context_filtering(self, context: CompletionContext, completions: List[str]) -> List[str]:
        """Apply context-specific file filtering."""
        # If no context hints, return all completions
        command = context.current_command.lower()
        args_text = ' '.join(context.args).lower()
        
        # Determine expected file types from context
        expected_types = set()
        
        if 'config' in command or 'config' in args_text:
            expected_types.update(self.file_filters['config'])
        
        if any(lang in command for lang in ['python', 'node', 'npm', 'cargo', 'rust']):
            expected_types.update(self.file_filters['source'])
        
        if 'data' in args_text or command in ['load', 'import', 'export']:
            expected_types.update(self.file_filters['data'])
        
        # If no specific type expected, return all
        if not expected_types:
            return completions
        
        # Filter files by expected types (keep all directories)
        filtered = []
        for completion in completions:
            if completion.endswith('/'):  # Directory
                filtered.append(completion)
            else:
                # Check if file extension matches expected types
                for ext in expected_types:
                    if completion.lower().endswith(ext.lower()):
                        filtered.append(completion)
                        break
        
        return filtered


class EnvironmentVariableProvider(CompletionProvider):
    """
    Environment variable completion with expansion support.
    
    Features:
    - Smart variable name completion
    - Value expansion hints
    - Context-aware variable suggestions
    """
    
    def __init__(self, priority: int = 70):
        """Initialize with medium-high priority."""
        super().__init__(priority)
        
        # Common environment variables that might be useful
        self.common_vars = {
            'PATH', 'HOME', 'USER', 'SHELL', 'PWD', 'OLDPWD',
            'LANG', 'LC_ALL', 'TERM', 'EDITOR', 'PAGER',
            'PYTHONPATH', 'NODE_PATH', 'CARGO_HOME', 'RUSTUP_HOME',
            'GOOBITS_CONFIG', 'GOOBITS_HOME'
        }
    
    def can_provide(self, context: CompletionContext) -> bool:
        """Check if we should provide environment variable completions."""
        word = context.current_word
        
        # Direct variable reference
        if word.startswith('$') or word.startswith('${'):
            return True
        
        # Environment-related commands
        env_commands = {'env', 'export', 'set', 'unset', 'printenv'}
        if context.current_command in env_commands:
            return True
        
        # Check for environment context in arguments
        if any('env' in arg.lower() for arg in context.args):
            return True
        
        return False
    
    async def provide_completions(self, context: CompletionContext) -> List[str]:
        """Provide environment variable completions."""
        try:
            word = context.current_word
            completions = []
            
            # Handle different variable syntax formats
            if word.startswith('${'):
                # ${VAR} format
                prefix = '${'
                var_part = word[2:]
                suffix = '}'
            elif word.startswith('$'):
                # $VAR format  
                prefix = '$'
                var_part = word[1:]
                suffix = ''
            else:
                # Plain variable name
                prefix = ''
                var_part = word
                suffix = ''
            
            # Get matching environment variables
            available_vars = set(context.env.keys()) | self.common_vars
            
            for var in available_vars:
                if var.startswith(var_part.upper()):
                    completion = prefix + var + suffix
                    completions.append(completion)
            
            # Sort by relevance - common vars first
            def sort_key(var):
                clean_var = var.replace('$', '').replace('{', '').replace('}', '')
                is_common = clean_var in self.common_vars
                return (not is_common, clean_var)
            
            return sorted(completions, key=sort_key)
            
        except Exception as e:
            logger.error(f"Error in environment variable completion: {e}")
            return []


class ConfigKeyProvider(CompletionProvider):
    """
    Configuration key completion for YAML/JSON config files.
    
    Features:
    - Context-aware key suggestions
    - Nested key path completion
    - Multi-format support (YAML, JSON, TOML)
    """
    
    def __init__(self, priority: int = 60):
        """Initialize with medium priority."""
        super().__init__(priority)
        
        # Common configuration keys
        self.common_keys = {
            'name', 'version', 'description', 'author', 'license',
            'dependencies', 'scripts', 'commands', 'options',
            'language', 'runtime', 'build', 'test', 'deploy'
        }
    
    def can_provide(self, context: CompletionContext) -> bool:
        """Check if we should provide config key completions."""
        # Check if we're in a configuration context
        if context.config:
            return True
        
        # Check for config-related commands or arguments
        config_indicators = {'config', 'set', 'get', 'key', 'value'}
        if (context.current_command in config_indicators or
            any(indicator in arg.lower() for arg in context.args for indicator in config_indicators)):
            return True
        
        return False
    
    async def provide_completions(self, context: CompletionContext) -> List[str]:
        """Provide configuration key completions."""
        try:
            completions = []
            current_word = context.current_word
            
            # If we have loaded configuration, use its keys
            if context.config:
                completions.extend(self._get_config_keys(context.config, current_word))
            
            # Add common configuration keys
            for key in self.common_keys:
                if key.startswith(current_word.lower()):
                    completions.append(key)
            
            # Remove duplicates and sort
            unique_completions = sorted(set(completions))
            
            return unique_completions
            
        except Exception as e:
            logger.error(f"Error in config key completion: {e}")
            return []
    
    def _get_config_keys(self, config: Dict[str, Any], prefix: str = "") -> List[str]:
        """Extract keys from configuration dictionary."""
        keys = []
        
        for key, value in config.items():
            if not prefix or key.startswith(prefix):
                keys.append(key)
                
                # For nested dictionaries, add dot-notation keys
                if isinstance(value, dict) and prefix:
                    nested_keys = self._get_nested_keys(value, f"{key}.")
                    keys.extend(nested_keys)
        
        return keys
    
    def _get_nested_keys(self, config: Dict[str, Any], prefix: str) -> List[str]:
        """Get nested configuration keys with dot notation."""
        keys = []
        
        for key, value in config.items():
            full_key = prefix + key
            keys.append(full_key)
            
            if isinstance(value, dict):
                nested = self._get_nested_keys(value, full_key + ".")
                keys.extend(nested)
        
        return keys


class HistoryProvider(CompletionProvider):
    """
    Command history completion with intelligent ranking.
    
    Features:
    - Recent command suggestions
    - Frequency-based ranking
    - Context-aware history filtering
    """
    
    def __init__(self, priority: int = 40):
        """Initialize with lower priority (used as fallback)."""
        super().__init__(priority)
        self.max_suggestions = 10
    
    def can_provide(self, context: CompletionContext) -> bool:
        """Check if we should provide history completions."""
        # Always provide history as a fallback
        return bool(context.history)
    
    async def provide_completions(self, context: CompletionContext) -> List[str]:
        """Provide command history completions."""
        try:
            if not context.history:
                return []
            
            current_word = context.current_word
            completions = []
            
            # Filter history for matching commands
            for cmd in reversed(context.history):  # Most recent first
                if cmd.startswith(current_word) and cmd != current_word:
                    if cmd not in completions:  # Avoid duplicates
                        completions.append(cmd)
                    
                    # Limit number of suggestions
                    if len(completions) >= self.max_suggestions:
                        break
            
            return completions
            
        except Exception as e:
            logger.error(f"Error in history completion: {e}")
            return []


# Convenience function to setup default providers
def setup_default_providers() -> List[CompletionProvider]:
    """Setup and return default completion providers."""
    providers = [
        FilePathCompletionProvider(priority=80),
        EnvironmentVariableProvider(priority=70), 
        ConfigKeyProvider(priority=60),
        HistoryProvider(priority=40)
    ]
    
    return providers