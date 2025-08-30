"""
Discovery Engine
===============

Hook discovery and loading system extracted from hook_system.j2.
Provides dynamic module resolution and hook function discovery.
"""

import importlib
import importlib.util
import inspect
import sys
from pathlib import Path
from typing import Dict, Any, Optional, List, Callable, Union
from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class HookModule:
    """Represents a loaded hook module."""
    name: str
    module: Any
    path: Optional[Path] = None
    hooks: Dict[str, Callable] = None
    
    def __post_init__(self):
        if self.hooks is None:
            self.hooks = {}


class ModuleResolver:
    """
    Module resolution system extracted from hook_system.j2.
    
    Handles finding and loading hook modules from various search paths.
    """
    
    def __init__(self, search_paths: List[str] = None):
        """Initialize module resolver."""
        self.search_paths = search_paths or ['.', 'hooks', 'src']
    
    def resolve_module_path(self, module_name: str, language: str) -> Optional[Path]:
        """
        Resolve module path for given module name and language.
        
        Args:
            module_name: Name of module to find
            language: Target language (affects file extensions)
            
        Returns:
            Path to module file or None if not found
        """
        extensions = self._get_extensions_for_language(language)
        
        for search_path in self.search_paths:
            search_dir = Path(search_path)
            
            for ext in extensions:
                # Try direct module file
                module_file = search_dir / f"{module_name}{ext}"
                if module_file.exists() and module_file.is_file():
                    return module_file
                
                # Try module directory with __init__ file
                module_dir = search_dir / module_name
                init_file = module_dir / f"__init__{ext}"
                if init_file.exists() and init_file.is_file():
                    return init_file
        
        return None
    
    def _get_extensions_for_language(self, language: str) -> List[str]:
        """Get file extensions for language."""
        extensions = {
            'python': ['.py'],
            'nodejs': ['.js', '.mjs'],
            'typescript': ['.ts', '.js'],
            'rust': ['.rs']
        }
        return extensions.get(language, ['.py'])
    
    def find_all_modules(self, language: str, pattern: str = "*hooks*") -> List[Path]:
        """Find all modules matching pattern."""
        extensions = self._get_extensions_for_language(language)
        found_modules = []
        
        for search_path in self.search_paths:
            search_dir = Path(search_path)
            if not search_dir.exists():
                continue
                
            for ext in extensions:
                # Find files matching pattern
                for file_path in search_dir.glob(f"*{ext}"):
                    if pattern.replace("*", "") in file_path.name:
                        found_modules.append(file_path)
        
        return found_modules


class HookLoader:
    """
    Hook loading system extracted from hook_system.j2.
    
    Handles dynamic loading of hook modules and extraction of hook functions.
    """
    
    def __init__(self, language: str):
        """Initialize hook loader."""
        self.language = language
        self.resolver = ModuleResolver()
        self._loaded_modules: Dict[str, HookModule] = {}
    
    def load_module(self, module_name: str, module_path: Optional[Path] = None) -> Optional[HookModule]:
        """
        Load a hook module.
        
        Args:
            module_name: Name of module to load
            module_path: Optional explicit path to module
            
        Returns:
            Loaded HookModule or None if loading failed
        """
        # Check cache first
        if module_name in self._loaded_modules:
            return self._loaded_modules[module_name]
        
        # Resolve path if not provided
        if module_path is None:
            module_path = self.resolver.resolve_module_path(module_name, self.language)
        
        if module_path is None:
            return None
        
        try:
            # Load module based on language
            if self.language == 'python':
                module = self._load_python_module(module_name, module_path)
            elif self.language in ('nodejs', 'typescript'):
                module = self._load_js_module(module_name, module_path)
            elif self.language == 'rust':
                module = self._load_rust_module(module_name, module_path)
            else:
                return None
            
            # Create hook module wrapper
            hook_module = HookModule(
                name=module_name,
                module=module,
                path=module_path
            )
            
            # Extract hook functions
            hook_module.hooks = self._extract_hooks(module)
            
            # Cache the loaded module
            self._loaded_modules[module_name] = hook_module
            
            return hook_module
            
        except Exception as e:
            # Log error but don't fail completely
            return None
    
    def _load_python_module(self, module_name: str, module_path: Path):
        """Load Python module."""
        spec = importlib.util.spec_from_file_location(module_name, module_path)
        if spec is None or spec.loader is None:
            raise ImportError(f"Cannot load module {module_name}")
        
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    
    def _load_js_module(self, module_name: str, module_path: Path):
        """Load JavaScript/TypeScript module (placeholder - would use Node.js integration)."""
        # In a real implementation, this would interface with Node.js
        # For now, return a placeholder
        return type('JSModule', (), {
            '__name__': module_name,
            '__file__': str(module_path)
        })()
    
    def _load_rust_module(self, module_name: str, module_path: Path):
        """Load Rust module (placeholder - would use Rust integration)."""
        # In a real implementation, this would interface with Rust
        # For now, return a placeholder
        return type('RustModule', (), {
            '__name__': module_name,
            '__file__': str(module_path)
        })()
    
    def _extract_hooks(self, module) -> Dict[str, Callable]:
        """Extract hook functions from loaded module."""
        hooks = {}
        
        if self.language == 'python':
            # Extract Python hook functions
            for name, obj in inspect.getmembers(module):
                if (inspect.isfunction(obj) and 
                    name.startswith('on_') and 
                    not name.startswith('_')):
                    hooks[name] = obj
        
        elif self.language in ('nodejs', 'typescript'):
            # Extract JavaScript/TypeScript hook functions
            # This would be implemented with Node.js integration
            for attr_name in dir(module):
                if attr_name.startswith('on_'):
                    attr_value = getattr(module, attr_name)
                    if callable(attr_value):
                        hooks[attr_name] = attr_value
        
        elif self.language == 'rust':
            # Extract Rust hook functions
            # This would be implemented with Rust integration
            for attr_name in dir(module):
                if attr_name.startswith('on_'):
                    attr_value = getattr(module, attr_name)
                    if callable(attr_value):
                        hooks[attr_name] = attr_value
        
        return hooks
    
    def reload_module(self, module_name: str) -> Optional[HookModule]:
        """Reload a module."""
        # Remove from cache
        if module_name in self._loaded_modules:
            del self._loaded_modules[module_name]
        
        # Load again
        return self.load_module(module_name)
    
    def get_loaded_modules(self) -> Dict[str, HookModule]:
        """Get all loaded modules."""
        return self._loaded_modules.copy()
    
    def clear_cache(self) -> None:
        """Clear module cache."""
        self._loaded_modules.clear()


class DiscoveryEngine:
    """
    Hook discovery engine extracted from hook_system.j2.
    
    Orchestrates module resolution and hook loading for the hook system.
    """
    
    def __init__(self, language: str, search_paths: List[str] = None):
        """Initialize discovery engine."""
        self.language = language
        self.resolver = ModuleResolver(search_paths)
        self.loader = HookLoader(language)
    
    def discover_hooks(self, module_names: List[str] = None) -> Dict[str, Callable]:
        """
        Discover all hook functions.
        
        Args:
            module_names: Optional list of specific modules to load
            
        Returns:
            Dictionary mapping hook names to hook functions
        """
        all_hooks = {}
        
        if module_names:
            # Load specific modules
            for module_name in module_names:
                hook_module = self.loader.load_module(module_name)
                if hook_module:
                    all_hooks.update(hook_module.hooks)
        else:
            # Auto-discover hook modules
            hook_files = self.resolver.find_all_modules(self.language, "*hook*")
            
            for hook_file in hook_files:
                module_name = hook_file.stem
                hook_module = self.loader.load_module(module_name, hook_file)
                if hook_module:
                    all_hooks.update(hook_module.hooks)
        
        return all_hooks
    
    def find_hook(self, hook_name: str, module_names: List[str] = None) -> Optional[Callable]:
        """
        Find a specific hook function.
        
        Args:
            hook_name: Name of hook to find
            module_names: Optional list of modules to search
            
        Returns:
            Hook function or None if not found
        """
        hooks = self.discover_hooks(module_names)
        return hooks.get(hook_name)
    
    def validate_hook_signature(self, hook_func: Callable, expected_args: List[str]) -> bool:
        """
        Validate that hook function has expected signature.
        
        Args:
            hook_func: Hook function to validate
            expected_args: List of expected argument names
            
        Returns:
            True if signature matches expectations
        """
        if self.language == 'python':
            try:
                sig = inspect.signature(hook_func)
                params = list(sig.parameters.keys())
                
                # Allow for flexible signatures (more params ok, fewer not ok)
                return len(params) >= len(expected_args)
            except Exception:
                return False
        
        # For other languages, assume valid for now
        # Real implementation would check function signatures
        return True
    
    def get_hook_metadata(self, hook_func: Callable) -> Dict[str, Any]:
        """
        Get metadata about a hook function.
        
        Args:
            hook_func: Hook function to analyze
            
        Returns:
            Dictionary with metadata
        """
        metadata = {
            'name': getattr(hook_func, '__name__', 'unknown'),
            'doc': None,
            'signature': None,
            'async': False
        }
        
        if self.language == 'python':
            metadata['doc'] = inspect.getdoc(hook_func)
            try:
                metadata['signature'] = str(inspect.signature(hook_func))
            except Exception:
                pass
            metadata['async'] = inspect.iscoroutinefunction(hook_func)
        
        return metadata
    
    def list_available_hooks(self, module_names: List[str] = None) -> Dict[str, Dict[str, Any]]:
        """
        List all available hooks with their metadata.
        
        Args:
            module_names: Optional list of modules to search
            
        Returns:
            Dictionary mapping hook names to their metadata
        """
        hooks = self.discover_hooks(module_names)
        hook_info = {}
        
        for hook_name, hook_func in hooks.items():
            hook_info[hook_name] = self.get_hook_metadata(hook_func)
        
        return hook_info