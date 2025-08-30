"""
Template Generator
=================

Template generation system extracted from hook_system.j2.
Provides language-specific hook template generation for user hook files.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List
from dataclasses import dataclass
from .hook_framework import HookConfig, HookDefinition


@dataclass
class HookTemplate:
    """Represents a generated hook template."""
    content: str
    filename: str
    language: str
    encoding: str = "utf-8"


class TemplateGenerator:
    """
    Template generator extracted from hook_system.j2.
    
    Generates user hook files with language-specific templates
    containing function stubs for all defined commands.
    """
    
    def __init__(self):
        """Initialize template generator."""
        self._generators = {}
        self._register_generators()
    
    def _register_generators(self) -> None:
        """Register language-specific template generators."""
        self._generators = {
            'python': self._generate_python_template,
            'nodejs': self._generate_nodejs_template,
            'typescript': self._generate_typescript_template,
            'rust': self._generate_rust_template
        }
    
    def generate_template(self, config: HookConfig) -> HookTemplate:
        """
        Generate hook template for specified language.
        
        Args:
            config: Hook configuration
            
        Returns:
            Generated hook template
            
        Raises:
            ValueError: If language is not supported
        """
        if config.language not in self._generators:
            supported = ', '.join(self._generators.keys())
            raise ValueError(f"Unsupported language: {config.language}. Supported: {supported}")
        
        generator = self._generators[config.language]
        content = generator(config)
        
        # Get appropriate filename
        filename = self._get_template_filename(config)
        
        return HookTemplate(
            content=content,
            filename=filename,
            language=config.language
        )
    
    def _get_template_filename(self, config: HookConfig) -> str:
        """Get appropriate template filename for language."""
        return f"{config.hook_file}{config.hook_file_extension}"
    
    def _generate_python_template(self, config: HookConfig) -> str:
        """Generate Python hook template."""
        lines = [
            '"""',
            f'Hook implementations for {config.project_name}',
            '',
            'This file contains the business logic for your CLI commands.',
            'Implement the hook functions below to handle your CLI commands.',
            '',
            'Each command in your CLI corresponds to a hook function named \'on_<command_name>\'.',
            'Command names with hyphens are converted to underscores.',
            '',
            'Example:',
            '- Command \'hello-world\' -> Hook function \'on_hello_world\'',
            '- Command \'status\' -> Hook function \'on_status\'',
            '"""',
            '',
            '# Import any modules you need here',
            'import sys',
            'import os',
            ''
        ]
        
        # Generate hook functions
        for hook_def in config.commands:
            lines.extend(self._generate_python_hook_function(hook_def))
            lines.append('')
        
        lines.extend([
            '# Add any utility functions or classes here',
            ''
        ])
        
        return '\n'.join(lines)
    
    def _generate_python_hook_function(self, hook_def: HookDefinition) -> List[str]:
        """Generate Python hook function."""
        # Build function signature
        signature_parts = [hook_def.hook_name + '(']
        args = hook_def.get_signature_args()
        
        if args:
            # Format arguments with proper indentation
            if len(args) == 1:
                signature_parts[0] += args[0] + '):'
            else:
                signature_parts[0] += ''
                for i, arg in enumerate(args):
                    indent = '    ' if i == 0 else '    '
                    comma = ',' if i < len(args) - 1 else ''
                    signature_parts.append(f'{indent}{arg}{comma}')
                signature_parts.append('):')
        else:
            signature_parts[0] += '):'
        
        lines = [
            f'def {signature_parts[0]}' if len(signature_parts) == 1 else f'def {signature_parts[0]}',
        ]
        
        if len(signature_parts) > 1:
            lines.extend(signature_parts[1:])
        
        lines.extend([
            '    """',
            f'    {hook_def.description}',
            '    """',
            '    # Add your business logic here',
            f'    print(f"Hook {hook_def.hook_name} called")',
            '    ',
            '    # Return 0 for success, non-zero for error',
            '    return 0'
        ])
        
        return lines
    
    def _generate_nodejs_template(self, config: HookConfig) -> str:
        """Generate Node.js hook template."""
        lines = [
            '/**',
            f' * Hook implementations for {config.project_name}',
            ' * ',
            ' * This file contains the business logic for your CLI commands.',
            ' * Implement the hook functions below to handle your CLI commands.',
            ' * ',
            ' * Each command in your CLI corresponds to a hook function named \'on<CommandName>\'.',
            ' * Command names with hyphens are converted to camelCase.',
            ' * ',
            ' * Example:',
            ' * - Command \'hello-world\' -> Hook function \'onHelloWorld\'',
            ' * - Command \'status\' -> Hook function \'onStatus\'',
            ' */',
            '',
            '// Import any modules you need here',
            'import fs from \'fs\';',
            'import path from \'path\';',
            ''
        ]
        
        # Generate hook functions
        for hook_def in config.commands:
            lines.extend(self._generate_nodejs_hook_function(hook_def))
            lines.append('')
        
        lines.extend([
            '// Add any utility functions or classes here',
            ''
        ])
        
        return '\n'.join(lines)
    
    def _generate_nodejs_hook_function(self, hook_def: HookDefinition) -> List[str]:
        """Generate Node.js hook function."""
        # Convert snake_case to camelCase for JS
        func_name = hook_def.hook_name
        if func_name.startswith('on_'):
            # Convert on_hello_world to onHelloWorld
            parts = func_name.split('_')
            func_name = parts[0] + ''.join(word.capitalize() for word in parts[1:])
        
        # Build parameter list
        params = []
        
        # Add positional arguments
        for arg in hook_def.arguments:
            params.append(arg['name'])
        
        # Add options object if there are options
        if hook_def.options:
            params.append('options')
        
        param_str = ', '.join(params)
        
        lines = [
            '/**',
            f' * {hook_def.description}',
            ' */',
            f'export async function {func_name}({param_str}) {{',
            '    // Add your business logic here',
            f'    console.log(\'Hook {func_name} called\');',
            ''
        ]
        
        if hook_def.arguments:
            arg_names = [arg['name'] for arg in hook_def.arguments]
            lines.append(f'    console.log(\'Arguments:\', {{ {", ".join(arg_names)} }});')
        
        if hook_def.options:
            lines.append('    console.log(\'Options:\', options);')
        
        lines.extend([
            '    ',
            '    // You can return a value or throw an error',
            '    // Returning nothing is equivalent to success',
            '}'
        ])
        
        return lines
    
    def _generate_typescript_template(self, config: HookConfig) -> str:
        """Generate TypeScript hook template."""
        lines = [
            '/**',
            f' * Hook implementations for {config.project_name}',
            ' * ',
            ' * This file contains the business logic for your CLI commands.',
            ' * Implement the hook functions below to handle your CLI commands.',
            ' * ',
            ' * Each command in your CLI corresponds to a hook function named \'on<CommandName>\'.',
            ' * Command names with hyphens are converted to camelCase.',
            ' * ',
            ' * Example:',
            ' * - Command \'hello-world\' -> Hook function \'onHelloWorld\'',
            ' * - Command \'status\' -> Hook function \'onStatus\'',
            ' */',
            '',
            '// Import any modules you need here',
            'import * as fs from \'fs\';',
            'import * as path from \'path\';',
            ''
        ]
        
        # Generate hook functions
        for hook_def in config.commands:
            lines.extend(self._generate_typescript_hook_function(hook_def))
            lines.append('')
        
        lines.extend([
            '// Add any utility functions or classes here',
            ''
        ])
        
        return '\n'.join(lines)
    
    def _generate_typescript_hook_function(self, hook_def: HookDefinition) -> List[str]:
        """Generate TypeScript hook function."""
        # Convert snake_case to camelCase for TS
        func_name = hook_def.hook_name
        if func_name.startswith('on_'):
            parts = func_name.split('_')
            func_name = parts[0] + ''.join(word.capitalize() for word in parts[1:])
        
        lines = [
            '/**',
            f' * {hook_def.description}',
            ' */'
        ]
        
        # Build typed parameter list
        param_parts = []
        
        # Add arguments with types
        for arg in hook_def.arguments:
            arg_type = 'string[]' if arg.get('multiple', False) else 'string'
            param_parts.append(f"    {arg['name']}: {arg_type}")
        
        # Add options object with typed properties
        if hook_def.options:
            options_props = []
            for opt in hook_def.options:
                opt_name = opt['name'].replace('-', '_')
                if opt.get('type') == 'boolean':
                    opt_type = 'boolean'
                elif opt.get('type') == 'integer':
                    opt_type = 'number'
                elif opt.get('type') == 'float':
                    opt_type = 'number'
                else:
                    opt_type = 'string'
                
                optional = '?' if not opt.get('required', False) else ''
                options_props.append(f'        {opt_name}{optional}: {opt_type};')
            
            if options_props:
                param_parts.append('    options: {')
                param_parts.extend(options_props)
                param_parts.append('    }')
        
        # Format function signature
        if param_parts:
            lines.append(f'export async function {func_name}(')
            lines.extend(param_parts)
            lines.append('): Promise<void> {')
        else:
            lines.append(f'export async function {func_name}(): Promise<void> {{')
        
        lines.extend([
            '    // Add your business logic here',
            f'    console.log(\'Hook {func_name} called\');',
            ''
        ])
        
        if hook_def.arguments:
            arg_names = [arg['name'] for arg in hook_def.arguments]
            lines.append(f'    console.log(\'Arguments:\', {{ {", ".join(arg_names)} }});')
        
        if hook_def.options:
            lines.append('    console.log(\'Options:\', options);')
        
        lines.extend([
            '    ',
            '    // You can return a value or throw an error',
            '    // Returning nothing is equivalent to success',
            '}'
        ])
        
        return lines
    
    def _generate_rust_template(self, config: HookConfig) -> str:
        """Generate Rust hook template."""
        lines = [
            '//! Hook implementations for ' + config.project_name,
            '//! ',
            '//! This file contains the business logic for your CLI commands.',
            '//! Implement the hook functions below to handle your CLI commands.',
            '//! ',
            '//! Each command in your CLI corresponds to a hook function.',
            '',
            'use clap::ArgMatches;',
            'use anyhow::{Result, anyhow};',
            ''
        ]
        
        # Generate hook functions
        for hook_def in config.commands:
            lines.extend(self._generate_rust_hook_function(hook_def))
            lines.append('')
        
        lines.extend([
            '// Add any utility functions or structures here',
            ''
        ])
        
        return '\n'.join(lines)
    
    def _generate_rust_hook_function(self, hook_def: HookDefinition) -> List[str]:
        """Generate Rust hook function."""
        lines = [
            f'/// Hook function for \'{hook_def.name}\' command',
            f'/// {hook_def.description}',
            f'pub fn {hook_def.hook_name}(matches: &ArgMatches) -> Result<()> {{',
            '    // Add your business logic here',
            f'    println!("Hook {hook_def.hook_name} called");',
            ''
        ]
        
        # Add argument extraction examples
        if hook_def.arguments:
            lines.append('    // Extract arguments')
            for arg in hook_def.arguments:
                arg_name = arg['name'].replace('-', '_')
                if arg.get('multiple', False):
                    lines.extend([
                        f'    if let Some({arg_name}_values) = matches.get_many::<String>("{arg["name"]}") {{',
                        f'        let {arg_name}: Vec<&String> = {arg_name}_values.collect();',
                        f'        println!("{arg["name"]}: {{:?}}", {arg_name});',
                        '    }'
                    ])
                else:
                    lines.extend([
                        f'    if let Some({arg_name}) = matches.get_one::<String>("{arg["name"]}") {{',
                        f'        println!("{arg["name"]}: {{}}", {arg_name});',
                        '    }'
                    ])
            lines.append('')
        
        # Add option extraction examples
        if hook_def.options:
            lines.append('    // Extract options')
            for opt in hook_def.options:
                opt_name = opt['name'].replace('-', '_')
                if opt.get('type') == 'boolean':
                    lines.extend([
                        f'    let {opt_name} = matches.get_flag("{opt["name"]}");',
                        f'    println!("{opt["name"]}: {{}}", {opt_name});'
                    ])
                else:
                    lines.extend([
                        f'    if let Some({opt_name}) = matches.get_one::<String>("{opt["name"]}") {{',
                        f'        println!("{opt["name"]}: {{}}", {opt_name});',
                        '    }'
                    ])
            lines.append('')
        
        lines.extend([
            '    // Return Ok(()) for success, Err(...) for error',
            '    Ok(())',
            '}'
        ])
        
        return lines
    
    def get_supported_languages(self) -> List[str]:
        """Get list of supported languages for template generation."""
        return list(self._generators.keys())