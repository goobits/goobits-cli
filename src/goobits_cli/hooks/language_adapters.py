"""
Language Adapters
================

Language-specific adapters extracted from hook_system.j2 template.
Each adapter generates hook system code for its target language.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List
from .hook_framework import HookConfig, HookDefinition, HookExecutionMode
from .template_generator import TemplateGenerator


class HookAdapter(ABC):
    """Base class for language-specific hook adapters."""
    
    def __init__(self, language: str):
        """Initialize adapter with target language."""
        self.language = language
        self.template_generator = TemplateGenerator()
    
    @abstractmethod
    def generate_code(self, config: HookConfig) -> str:
        """Generate hook system code for the language."""
        pass
    
    def generate_template(self, config: HookConfig) -> str:
        """Generate user hook template file."""
        template = self.template_generator.generate_template(config)
        return template.content


class PythonHookAdapter(HookAdapter):
    """Python hook system adapter."""
    
    def __init__(self):
        super().__init__('python')
    
    def generate_code(self, config: HookConfig) -> str:
        """Generate Python hook system code."""
        lines = [
            '"""',
            f'Hook system interface for {config.project_name}',
            '',
            'This module defines the interface between the generated CLI and user-defined hooks.',
            'Users should implement hook functions in cli_hooks.py to provide business logic.',
            '"""',
            '',
            'import importlib',
            'import inspect',
            'import sys',
            'from typing import Any, Callable, Dict, Optional',
            'from pathlib import Path',
            ''
        ]
        
        # Generate HookManager class
        lines.extend(self._generate_hook_manager_class(config))
        lines.append('')
        
        # Generate exception classes
        lines.extend(self._generate_exception_classes())
        lines.append('')
        
        # Generate global functions
        lines.extend(self._generate_global_functions())
        
        return '\n'.join(lines)
    
    def _generate_hook_manager_class(self, config: HookConfig) -> List[str]:
        """Generate HookManager class."""
        return [
            'class HookManager:',
            '    """Manages loading and execution of user-defined hooks."""',
            '    ',
            f'    def __init__(self, hooks_module_name: str = "{config.hook_file}"):',
            '        self.hooks_module_name = hooks_module_name',
            '        self.hooks_module = None',
            '        self.hooks_cache: Dict[str, Callable] = {}',
            '        self.load_hooks()',
            '    ',
            '    def load_hooks(self) -> None:',
            '        """Load the hooks module."""',
            '        try:',
            '            # Try to import the hooks module',
            '            self.hooks_module = importlib.import_module(self.hooks_module_name)',
            '            ',
            '            # Cache all hook functions',
            '            for name, obj in inspect.getmembers(self.hooks_module):',
            '                if (inspect.isfunction(obj) and ',
            '                    name.startswith(\'on_\') and ',
            '                    not name.startswith(\'_\')):',
            '                    self.hooks_cache[name] = obj',
            '                    ',
            '        except ImportError:',
            '            # Hooks module doesn\'t exist yet',
            '            self.hooks_module = None',
            '            self.hooks_cache = {}',
            '    ',
            '    def reload_hooks(self) -> None:',
            '        """Reload the hooks module (useful for development)."""',
            '        if self.hooks_module:',
            '            importlib.reload(self.hooks_module)',
            '        else:',
            '            self.load_hooks()',
            '    ',
            '    def has_hook(self, hook_name: str) -> bool:',
            '        """Check if a hook function exists."""',
            '        return hook_name in self.hooks_cache',
            '    ',
            '    def execute_hook(self, hook_name: str, *args, **kwargs) -> Any:',
            '        """',
            '        Execute a hook function.',
            '        ',
            '        Args:',
            '            hook_name: Name of the hook function',
            '            *args: Positional arguments to pass to the hook',
            '            **kwargs: Keyword arguments to pass to the hook',
            '            ',
            '        Returns:',
            '            The return value of the hook function',
            '            ',
            '        Raises:',
            '            HookNotFoundError: If the hook doesn\'t exist',
            '            Exception: Any exception raised by the hook',
            '        """',
            '        if not self.has_hook(hook_name):',
            '            raise HookNotFoundError(f"Hook \'{hook_name}\' not found")',
            '        ',
            '        hook_func = self.hooks_cache[hook_name]',
            '        ',
            '        try:',
            '            return hook_func(*args, **kwargs)',
            '        except Exception as e:',
            '            # Re-raise with additional context',
            '            raise HookExecutionError(f"Error executing hook \'{hook_name}\': {str(e)}") from e',
            '    ',
            '    def get_hook_signature(self, hook_name: str) -> Optional[inspect.Signature]:',
            '        """Get the signature of a hook function."""',
            '        if hook_name in self.hooks_cache:',
            '            return inspect.signature(self.hooks_cache[hook_name])',
            '        return None',
            '    ',
            '    def list_hooks(self) -> Dict[str, str]:',
            '        """',
            '        List all available hooks with their docstrings.',
            '        ',
            '        Returns:',
            '            Dictionary mapping hook names to their docstrings',
            '        """',
            '        hooks_info = {}',
            '        for name, func in self.hooks_cache.items():',
            '            docstring = inspect.getdoc(func) or "No description available"',
            '            hooks_info[name] = docstring',
            '        return hooks_info'
        ]
    
    def _generate_exception_classes(self) -> List[str]:
        """Generate exception classes."""
        return [
            'class HookNotFoundError(Exception):',
            '    """Raised when a requested hook function is not found."""',
            '    pass',
            '',
            'class HookExecutionError(Exception):',
            '    """Raised when a hook function execution fails."""',
            '    pass'
        ]
    
    def _generate_global_functions(self) -> List[str]:
        """Generate global convenience functions."""
        return [
            '# Global hook manager instance',
            '_hook_manager = None',
            '',
            'def get_hook_manager() -> HookManager:',
            '    """Get the global hook manager instance."""',
            '    global _hook_manager',
            '    if _hook_manager is None:',
            '        _hook_manager = HookManager()',
            '    return _hook_manager',
            '',
            'def execute_hook(hook_name: str, *args, **kwargs) -> Any:',
            '    """Convenience function to execute a hook."""',
            '    return get_hook_manager().execute_hook(hook_name, *args, **kwargs)',
            '',
            'def has_hook(hook_name: str) -> bool:',
            '    """Convenience function to check if a hook exists."""',
            '    return get_hook_manager().has_hook(hook_name)'
        ]


class NodeJSHookAdapter(HookAdapter):
    """Node.js hook system adapter."""
    
    def __init__(self):
        super().__init__('nodejs')
    
    def generate_code(self, config: HookConfig) -> str:
        """Generate Node.js hook system code."""
        lines = [
            '/**',
            f' * Hook system interface for {config.project_name}',
            ' * ',
            ' * This module defines the interface between the generated CLI and user-defined hooks.',
            ' * Users should implement hook functions in hooks.js to provide business logic.',
            ' */',
            '',
            'import fs from \'fs\';',
            'import path from \'path\';',
            ''
        ]
        
        # Generate HookManager class
        lines.extend(self._generate_hook_manager_class(config))
        lines.append('')
        
        # Generate exception classes
        lines.extend(self._generate_exception_classes())
        lines.append('')
        
        # Generate global functions and exports
        lines.extend(self._generate_global_functions_and_exports())
        
        return '\n'.join(lines)
    
    def _generate_hook_manager_class(self, config: HookConfig) -> List[str]:
        """Generate HookManager class for Node.js."""
        return [
            'class HookManager {',
            f'    constructor(hooksModulePath = \'./{config.hook_file}.js\') {{',
            '        this.hooksModulePath = hooksModulePath;',
            '        this.hooks = {};',
            '        // Don\'t call loadHooks in constructor since it\'s now async',
            '    }',
            '',
            '    async loadHooks() {',
            '        try {',
            '            // For ES modules, we can use dynamic import with a timestamp for cache busting',
            '            const timestamp = Date.now();',
            '            const hooksModule = await import(`${this.hooksModulePath}?t=${timestamp}`);',
            '            this.hooks = {};',
            '            ',
            '            // Cache all exported hook functions',
            '            for (const [name, func] of Object.entries(hooksModule)) {',
            '                if (typeof func === \'function\' && name.startsWith(\'on\')) {',
            '                    this.hooks[name] = func;',
            '                }',
            '            }',
            '        } catch (error) {',
            '            if (error.code === \'MODULE_NOT_FOUND\') {',
            '                // Hooks module doesn\'t exist yet',
            '                this.hooks = {};',
            '            } else {',
            '                console.warn(`Warning: Failed to load hooks: ${error.message}`);',
            '                this.hooks = {};',
            '            }',
            '        }',
            '    }',
            '',
            '    reloadHooks() {',
            '        this.loadHooks();',
            '    }',
            '',
            '    hasHook(hookName) {',
            '        return hookName in this.hooks;',
            '    }',
            '',
            '    async executeHook(hookName, ...args) {',
            '        if (!this.hasHook(hookName)) {',
            '            throw new HookNotFoundError(`Hook \'${hookName}\' not found`);',
            '        }',
            '',
            '        const hookFunc = this.hooks[hookName];',
            '',
            '        try {',
            '            const result = await hookFunc(...args);',
            '            return result;',
            '        } catch (error) {',
            '            throw new HookExecutionError(`Error executing hook \'${hookName}\': ${error.message}`);',
            '        }',
            '    }',
            '',
            '    listHooks() {',
            '        const hooksInfo = {};',
            '        for (const [name, func] of Object.entries(this.hooks)) {',
            '            // Try to extract function docstring/comments',
            '            const funcString = func.toString();',
            '            const commentMatch = funcString.match(/\\/\\*\\*([\\s\\S]*?)\\*\\//);',
            '            const description = commentMatch ? commentMatch[1].trim() : \'No description available\';',
            '            hooksInfo[name] = description;',
            '        }',
            '        return hooksInfo;',
            '    }',
            '}'
        ]
    
    def _generate_exception_classes(self) -> List[str]:
        """Generate exception classes for Node.js."""
        return [
            'class HookNotFoundError extends Error {',
            '    constructor(message) {',
            '        super(message);',
            '        this.name = \'HookNotFoundError\';',
            '    }',
            '}',
            '',
            'class HookExecutionError extends Error {',
            '    constructor(message) {',
            '        super(message);',
            '        this.name = \'HookExecutionError\';',
            '    }',
            '}'
        ]
    
    def _generate_global_functions_and_exports(self) -> List[str]:
        """Generate global functions and exports for Node.js."""
        return [
            '// Global hook manager instance',
            'let _hookManager = null;',
            '',
            'async function getHookManager() {',
            '    if (!_hookManager) {',
            '        _hookManager = new HookManager();',
            '        await _hookManager.loadHooks();',
            '    }',
            '    return _hookManager;',
            '}',
            '',
            'async function executeHook(hookName, ...args) {',
            '    const manager = await getHookManager();',
            '    return manager.executeHook(hookName, ...args);',
            '}',
            '',
            'async function hasHook(hookName) {',
            '    const manager = await getHookManager();',
            '    return manager.hasHook(hookName);',
            '}',
            '',
            'export {',
            '    HookManager,',
            '    HookNotFoundError,',
            '    HookExecutionError,',
            '    getHookManager,',
            '    executeHook,',
            '    hasHook',
            '};'
        ]


class TypeScriptHookAdapter(HookAdapter):
    """TypeScript hook system adapter."""
    
    def __init__(self):
        super().__init__('typescript')
    
    def generate_code(self, config: HookConfig) -> str:
        """Generate TypeScript hook system code."""
        lines = [
            '/**',
            f' * Hook system interface for {config.project_name}',
            ' * ',
            ' * This module defines the interface between the generated CLI and user-defined hooks.',
            ' * Users should implement hook functions in hooks.ts to provide business logic.',
            ' */',
            '',
            'import * as fs from \'fs\';',
            'import * as path from \'path\';',
            '',
            'type HookFunction = (...args: any[]) => Promise<any> | any;',
            ''
        ]
        
        # Generate HookManager class
        lines.extend(self._generate_hook_manager_class(config))
        lines.append('')
        
        # Generate exception classes
        lines.extend(self._generate_exception_classes())
        lines.append('')
        
        # Generate global functions and exports
        lines.extend(self._generate_global_functions_and_exports())
        
        return '\n'.join(lines)
    
    def _generate_hook_manager_class(self, config: HookConfig) -> List[str]:
        """Generate HookManager class for TypeScript."""
        return [
            'export class HookManager {',
            '    private hooksModulePath: string;',
            '    private hooks: Record<string, HookFunction> = {};',
            '',
            f'    constructor(hooksModulePath: string = \'./{config.hook_file}\') {{',
            '        this.hooksModulePath = hooksModulePath;',
            '        this.loadHooks();',
            '    }',
            '',
            '    public async loadHooks(): Promise<void> {',
            '        try {',
            '            // Dynamic import to support reloading',
            '            const hooksModule = await import(`${this.hooksModulePath}?t=${Date.now()}`);',
            '            this.hooks = {};',
            '            ',
            '            // Cache all exported hook functions',
            '            for (const [name, func] of Object.entries(hooksModule)) {',
            '                if (typeof func === \'function\' && name.startsWith(\'on\')) {',
            '                    this.hooks[name] = func as HookFunction;',
            '                }',
            '            }',
            '        } catch (error) {',
            '            if ((error as any).code === \'MODULE_NOT_FOUND\') {',
            '                // Hooks module doesn\'t exist yet',
            '                this.hooks = {};',
            '            } else {',
            '                console.warn(`Warning: Failed to load hooks: ${(error as Error).message}`);',
            '                this.hooks = {};',
            '            }',
            '        }',
            '    }',
            '',
            '    public async reloadHooks(): Promise<void> {',
            '        await this.loadHooks();',
            '    }',
            '',
            '    public hasHook(hookName: string): boolean {',
            '        return hookName in this.hooks;',
            '    }',
            '',
            '    public async executeHook(hookName: string, ...args: any[]): Promise<any> {',
            '        if (!this.hasHook(hookName)) {',
            '            throw new HookNotFoundError(`Hook \'${hookName}\' not found`);',
            '        }',
            '',
            '        const hookFunc = this.hooks[hookName];',
            '',
            '        try {',
            '            const result = await hookFunc(...args);',
            '            return result;',
            '        } catch (error) {',
            '            throw new HookExecutionError(`Error executing hook \'${hookName}\': ${(error as Error).message}`);',
            '        }',
            '    }',
            '',
            '    public listHooks(): Record<string, string> {',
            '        const hooksInfo: Record<string, string> = {};',
            '        for (const [name, func] of Object.entries(this.hooks)) {',
            '            // Try to extract function docstring/comments',
            '            const funcString = func.toString();',
            '            const commentMatch = funcString.match(/\\/\\*\\*([\\s\\S]*?)\\*\\//);',
            '            const description = commentMatch ? commentMatch[1].trim() : \'No description available\';',
            '            hooksInfo[name] = description;',
            '        }',
            '        return hooksInfo;',
            '    }',
            '}'
        ]
    
    def _generate_exception_classes(self) -> List[str]:
        """Generate exception classes for TypeScript."""
        return [
            'export class HookNotFoundError extends Error {',
            '    constructor(message: string) {',
            '        super(message);',
            '        this.name = \'HookNotFoundError\';',
            '    }',
            '}',
            '',
            'export class HookExecutionError extends Error {',
            '    constructor(message: string) {',
            '        super(message);',
            '        this.name = \'HookExecutionError\';',
            '    }',
            '}'
        ]
    
    def _generate_global_functions_and_exports(self) -> List[str]:
        """Generate global functions and exports for TypeScript."""
        return [
            '// Global hook manager instance',
            'let _hookManager: HookManager | null = null;',
            '',
            'export function getHookManager(): HookManager {',
            '    if (!_hookManager) {',
            '        _hookManager = new HookManager();',
            '    }',
            '    return _hookManager;',
            '}',
            '',
            'export async function executeHook(hookName: string, ...args: any[]): Promise<any> {',
            '    return getHookManager().executeHook(hookName, ...args);',
            '}',
            '',
            'export function hasHook(hookName: string): boolean {',
            '    return getHookManager().hasHook(hookName);',
            '}'
        ]


class RustHookAdapter(HookAdapter):
    """Rust hook system adapter."""
    
    def __init__(self):
        super().__init__('rust')
    
    def generate_code(self, config: HookConfig) -> str:
        """Generate Rust hook system code."""
        lines = [
            '//! Hook system interface',
            '//!',
            f'//! This module defines the hook execution system for {config.project_name}.',
            '//! Hook functions are defined in the hooks module.',
            '',
            'use clap::ArgMatches;',
            'use anyhow::{Result, anyhow};',
            'use std::collections::HashMap;',
            ''
        ]
        
        # Generate hook dispatcher
        lines.extend(self._generate_hook_dispatcher(config))
        lines.append('')
        
        # Generate HookManager struct
        lines.extend(self._generate_hook_manager())
        
        return '\n'.join(lines)
    
    def _generate_hook_dispatcher(self, config: HookConfig) -> List[str]:
        """Generate hook dispatcher function."""
        lines = [
            '/// Execute a hook by name',
            'pub fn execute_hook(hook_name: &str, matches: &ArgMatches) -> Result<()> {',
            '    match hook_name {'
        ]
        
        # Add cases for each hook
        for hook_def in config.commands:
            lines.append(f'        "{hook_def.hook_name}" => crate::hooks::{hook_def.hook_name}(matches),')
        
        lines.extend([
            '        _ => Err(anyhow!("Unknown hook: {}", hook_name)),',
            '    }',
            '}'
        ])
        
        return lines
    
    def _generate_hook_manager(self) -> List[str]:
        """Generate HookManager struct."""
        return [
            '/// Simple hook manager for compatibility',
            'pub struct HookManager;',
            '',
            'impl HookManager {',
            '    /// Create a new hook manager',
            '    pub fn new() -> Self {',
            '        Self',
            '    }',
            '    ',
            '    /// Execute a hook by name',
            '    pub fn execute_hook(&self, name: &str, matches: &ArgMatches) -> Result<()> {',
            '        execute_hook(name, matches)',
            '    }',
            '}',
            '',
            'impl Default for HookManager {',
            '    fn default() -> Self {',
            '        Self::new()',
            '    }',
            '}'
        ]