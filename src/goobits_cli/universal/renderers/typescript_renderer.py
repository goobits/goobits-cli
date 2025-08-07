"""
TypeScript Renderer for Universal Template System

This renderer generates TypeScript CLI implementations using universal components
with proper type safety, interfaces, and TypeScript-specific conventions.
"""

from pathlib import Path
from typing import Dict, Any, List, Optional
import re
import jinja2

from ..template_engine import LanguageRenderer


class TypeScriptRenderer(LanguageRenderer):
    """
    TypeScript-specific renderer for the Universal Template System.
    
    Generates TypeScript CLI implementations with:
    - Type safety through interfaces and TypeScript types
    - Commander.js framework integration with typed options
    - Proper TypeScript naming conventions (PascalCase/camelCase)
    - TypeScript-specific imports and module system
    - Build configuration for TypeScript compilation
    """
    
    def __init__(self):
        """Initialize the TypeScript renderer."""
        # Setup Jinja2 environment with custom filters
        self._env = jinja2.Environment()
        self._add_custom_filters()
    
    @property
    def language(self) -> str:
        """Return the language name."""
        return "typescript"
    
    @property  
    def file_extensions(self) -> Dict[str, str]:
        """Return mapping of component types to file extensions for TypeScript."""
        return {
            "ts": "typescript",
            "d.ts": "declaration", 
            "js": "javascript",  # For config files
            "json": "json"
        }
    
    def get_template_context(self, ir: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform IR into TypeScript-specific template context.
        
        Args:
            ir: Intermediate representation from UniversalTemplateEngine
            
        Returns:
            TypeScript-enhanced template context
        """
        # Start with base IR context
        context = ir.copy()
        
        # Add TypeScript-specific transformations
        context['typescript'] = {
            'interfaces': self._generate_interfaces(ir),
            'type_mappings': self._get_type_mappings(),
            'imports': self._generate_imports(ir),
            'exports': self._generate_exports(ir)
        }
        
        # Transform CLI schema for TypeScript
        if 'cli' in ir:
            context['cli']['typescript'] = self._transform_cli_schema(ir['cli'])
        
        # Add TypeScript build configuration
        context['build_config'] = self._generate_build_config(ir)
        
        # Convert names to TypeScript conventions
        context = self._apply_naming_conventions(context)
        
        return context
    
    def get_custom_filters(self) -> Dict[str, callable]:
        """Return TypeScript-specific Jinja2 filters."""
        return {
            'ts_type': self._ts_type_filter,
            'ts_interface': self._ts_interface_filter,
            'ts_import': self._ts_import_filter,
            'ts_commander_option': self._ts_commander_option_filter,
            'camelCase': self._camel_case_filter,
            'PascalCase': self._pascal_case_filter,
            'ts_safe_name': self._ts_safe_name_filter,
            'ts_optional': self._ts_optional_filter,
            'ts_array_type': self._ts_array_type_filter,
            'ts_function_signature': self._ts_function_signature_filter
        }
    
    def render_component(self, component_name: str, template_content: str, 
                        context: Dict[str, Any]) -> str:
        """
        Render a component template for TypeScript.
        
        Args:
            component_name: Name of the component
            template_content: Universal template content
            context: TypeScript-specific template context
            
        Returns:
            Rendered TypeScript code
        """
        # Create template from content
        template = self._env.from_string(template_content)
        
        # Add component-specific context
        render_context = context.copy()
        render_context['component_name'] = component_name
        
        # Apply TypeScript-specific processing based on component type
        if component_name == 'command_handler':
            render_context = self._enhance_command_context(render_context)
        elif component_name == 'config_manager':
            render_context = self._enhance_config_context(render_context)
        elif component_name == 'completion_engine':
            render_context = self._enhance_completion_context(render_context)
        
        return template.render(**render_context)
    
    def get_output_structure(self, ir: Dict[str, Any]) -> Dict[str, str]:
        """
        Define the output file structure for TypeScript CLIs.
        
        Args:
            ir: Intermediate representation
            
        Returns:
            Mapping of component names to output file paths
        """
        cli_name = ir.get("cli", {}).get("root_command", {}).get("name", "cli").replace("-", "_")
        
        output = {
            # Main CLI files
            'command_handler': 'cli.ts',
            'hook_system': 'src/hooks.ts',
            'config_manager': 'lib/config.ts',
            'completion_engine': 'lib/completion.ts',
            'error_handler': 'lib/errors.ts',
            
            # Entry points
            'main_entry': 'index.ts',
            'binary_entry': 'bin/cli.ts',
            
            # Build and configuration files
            'package_config': 'package.json',
            'typescript_config': 'tsconfig.json',
            'typescript_build_config': 'tsconfig.build.json',
            'eslint_config': '.eslintrc.json',
            'prettier_config': '.prettierrc',
            'esbuild_config': 'esbuild.config.js',
            'rollup_config': 'rollup.config.js',
            'webpack_config': 'webpack.config.js',
            
            # Type definitions
            'cli_types': 'types/cli.d.ts',
            'error_types': 'types/errors.d.ts',
            'config_types': 'types/config.d.ts',
            'plugin_types': 'types/plugins.d.ts',
            
            # Helper libraries
            'progress_helper': 'lib/progress.ts',
            'prompts_helper': 'lib/prompts.ts',
            'daemon_helper': 'lib/daemon.ts',
            'decorators': 'lib/decorators.ts',
            
            # Test structure
            'test_setup': 'test/setup.ts',
            'test_config': 'test/jest.config.js',
            'cli_test': 'test/cli.test.ts',
            
            # Documentation
            'readme': 'README.md',
            'gitignore': '.gitignore'
        }
        
        # Add interactive mode if enabled
        if self._has_interactive_features(ir.get("cli", {})):
            output["interactive_mode"] = f"{cli_name}_interactive.ts"
        
        return output
    
    def _add_custom_filters(self) -> None:
        """Add TypeScript-specific filters to Jinja2 environment."""
        for name, filter_func in self.get_custom_filters().items():
            self._env.filters[name] = filter_func
    
    def _generate_interfaces(self, ir: Dict[str, Any]) -> Dict[str, str]:
        """Generate TypeScript interfaces from CLI schema."""
        interfaces = {}
        
        # Generate global options interface
        if 'cli' in ir and 'global_options' in ir['cli']:
            interfaces['GlobalOptions'] = self._generate_global_options_interface(
                ir['cli']['global_options']
            )
        
        # Generate command interfaces
        if 'cli' in ir and 'commands' in ir['cli']:
            for cmd_name, cmd_data in ir['cli']['commands'].items():
                interface_name = f"{self._pascal_case_filter(cmd_name)}Options"
                interfaces[interface_name] = self._generate_command_interface(cmd_data)
        
        # Generate common interfaces
        interfaces['CommandArgs'] = '''interface CommandArgs {
  commandName: string;
  [key: string]: any;
}'''
        
        interfaces['HookFunction'] = '''interface HookFunction {
  (args: CommandArgs): Promise<any> | any;
}'''
        
        return interfaces
    
    def _get_type_mappings(self) -> Dict[str, str]:
        """Get mapping from generic types to TypeScript types."""
        return {
            'str': 'string',
            'string': 'string', 
            'int': 'number',
            'integer': 'number',
            'float': 'number',
            'number': 'number',
            'bool': 'boolean',
            'boolean': 'boolean',
            'flag': 'boolean',
            'list': 'Array<any>',
            'array': 'Array<any>',
            'dict': 'Record<string, any>',
            'object': 'Record<string, any>',
            'any': 'any',
            'void': 'void',
            'null': 'null',
            'undefined': 'undefined'
        }
    
    def _generate_imports(self, ir: Dict[str, Any]) -> List[str]:
        """Generate TypeScript import statements."""
        imports = [
            "import { Command } from 'commander';",
            "import * as path from 'path';",
            "import * as fs from 'fs';"
        ]
        
        # Add conditional imports based on features used
        if self._uses_child_process(ir):
            imports.append("import { spawn, execSync } from 'child_process';")
        
        if self._uses_async_features(ir):
            imports.append("import { promisify } from 'util';")
        
        return imports
    
    def _generate_exports(self, ir: Dict[str, Any]) -> List[str]:
        """Generate TypeScript export statements."""
        exports = []
        
        # Export main CLI function
        exports.append("export { program, cliEntry };")
        
        # Export interfaces if needed
        if self._needs_interface_exports(ir):
            exports.append("export type { CommandArgs, HookFunction, GlobalOptions };")
        
        return exports
    
    def _transform_cli_schema(self, cli_schema: Dict[str, Any]) -> Dict[str, Any]:
        """Transform CLI schema for TypeScript-specific rendering."""
        transformed = cli_schema.copy()
        
        # Convert command names to TypeScript-safe identifiers
        if 'commands' in transformed:
            for cmd_name, cmd_data in transformed['commands'].items():
                # Add TypeScript-specific metadata
                cmd_data['typescript'] = {
                    'interface_name': f"{self._pascal_case_filter(cmd_name)}Options",
                    'hook_name': f"on{self._pascal_case_filter(cmd_name)}",
                    'safe_name': self._ts_safe_name_filter(cmd_name)
                }
                
                # Transform options with TypeScript types
                if 'options' in cmd_data:
                    for option in cmd_data['options']:
                        option['typescript_type'] = self._ts_type_filter(option.get('type', 'string'))
        
        return transformed
    
    def _generate_build_config(self, ir: Dict[str, Any]) -> Dict[str, Any]:
        """Generate TypeScript build configuration."""
        return {
            'target': 'ES2022',
            'module': 'NodeNext',
            'moduleResolution': 'NodeNext',
            'outDir': './dist',
            'strict': True,
            'esModuleInterop': True,
            'skipLibCheck': True,
            'declaration': True,
            'declarationMap': True,
            'sourceMap': True
        }
    
    def _apply_naming_conventions(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Apply TypeScript naming conventions throughout the context."""
        # Convert project names to appropriate cases
        if 'project' in context:
            project = context['project']
            # Keep original names but add TypeScript variants
            project['typescript'] = {
                'class_name': self._pascal_case_filter(project.get('name', '')),
                'variable_name': self._camel_case_filter(project.get('name', '')),
                'type_name': self._pascal_case_filter(project.get('name', '')) + 'CLI'
            }
        
        return context
    
    def _enhance_command_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance context for command handler component."""
        enhanced = context.copy()
        
        # Add Commander.js specific helpers
        enhanced['commander'] = {
            'option_builders': self._generate_commander_options(context),
            'argument_builders': self._generate_commander_arguments(context),
            'action_handlers': self._generate_action_handlers(context)
        }
        
        return enhanced
    
    def _enhance_config_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance context for config manager component."""
        enhanced = context.copy()
        
        # Add configuration interfaces and validation
        enhanced['config'] = {
            'interface': self._generate_config_interface(context),
            'validation': self._generate_config_validation(context),
            'defaults': self._generate_config_defaults(context)
        }
        
        return enhanced
    
    def _enhance_completion_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance context for completion engine component."""
        enhanced = context.copy()
        
        # Add shell completion specific data
        enhanced['completion'] = {
            'completers': self._generate_completers(context),
            'shell_scripts': self._generate_shell_scripts(context)
        }
        
        return enhanced
    
    # Filter implementations
    def _ts_type_filter(self, type_str: str) -> str:
        """Convert generic types to TypeScript types."""
        mappings = self._get_type_mappings()
        return mappings.get(type_str.lower(), 'any')
    
    def _ts_interface_filter(self, name: str) -> str:
        """Generate interface name (PascalCase)."""
        return self._pascal_case_filter(name)
    
    def _ts_import_filter(self, module: str, items: Optional[List[str]] = None) -> str:
        """Generate TypeScript import statement."""
        if items:
            import_list = ', '.join(items)
            return f"import {{ {import_list} }} from '{module}';"
        else:
            return f"import * as {self._camel_case_filter(module)} from '{module}';"
    
    def _ts_commander_option_filter(self, option: Dict[str, Any]) -> str:
        """Generate typed Commander.js .option() call."""
        name = option.get('name', '')
        short = option.get('short', '')
        desc = option.get('description', '')
        type_str = option.get('type', 'string')
        
        # Build flag string
        flags = f"--{name}"
        if short:
            flags = f"-{short}, {flags}"
        
        # Add value placeholder for non-boolean types
        if type_str != 'flag' and type_str != 'boolean':
            flags += f" <{self._ts_type_filter(type_str)}>"
        
        return f".option('{flags}', '{desc}')"
    
    def _camel_case_filter(self, text: str) -> str:
        """Convert text to camelCase."""
        if not text:
            return text
        words = re.split(r'[-_\s]+', text.lower())
        return words[0] + ''.join(word.capitalize() for word in words[1:])
    
    def _pascal_case_filter(self, text: str) -> str:
        """Convert text to PascalCase."""
        if not text:
            return text
        words = re.split(r'[-_\s]+', text.lower()) 
        return ''.join(word.capitalize() for word in words)
    
    def _ts_safe_name_filter(self, name: str) -> str:
        """Convert name to TypeScript-safe identifier."""
        # Replace invalid characters with underscore
        safe = re.sub(r'[^a-zA-Z0-9_]', '_', name)
        # Ensure doesn't start with number
        if safe and safe[0].isdigit():
            safe = '_' + safe
        return safe or '_unnamed'
    
    def _ts_optional_filter(self, type_str: str, required: bool = True) -> str:
        """Add optional modifier to TypeScript type if not required."""
        base_type = self._ts_type_filter(type_str)
        if not required:
            return f"{base_type} | undefined"
        return base_type
    
    def _ts_array_type_filter(self, item_type: str) -> str:
        """Convert to TypeScript array type."""
        ts_type = self._ts_type_filter(item_type)
        return f"Array<{ts_type}>"
    
    def _ts_function_signature_filter(self, params: List[Dict[str, Any]], return_type: str = 'void') -> str:
        """Generate TypeScript function signature."""
        param_strs = []
        for param in params:
            name = param.get('name', 'arg')
            type_str = self._ts_type_filter(param.get('type', 'any'))
            optional = '' if param.get('required', True) else '?'
            param_strs.append(f"{name}{optional}: {type_str}")
        
        params_str = ', '.join(param_strs)
        return_ts_type = self._ts_type_filter(return_type)
        return f"({params_str}): {return_ts_type}"
    
    # Helper methods for context generation
    def _generate_global_options_interface(self, options: List[Dict[str, Any]]) -> str:
        """Generate interface for global options."""
        if not options:
            return "interface GlobalOptions {}"
        
        properties = []
        for option in options:
            name = self._camel_case_filter(option.get('name', ''))
            type_str = self._ts_optional_filter(
                option.get('type', 'string'), 
                option.get('required', False)
            )
            properties.append(f"  {name}: {type_str};")
        
        return "interface GlobalOptions {\n" + "\n".join(properties) + "\n}"
    
    def _generate_command_interface(self, cmd_data: Dict[str, Any]) -> str:
        """Generate interface for command options."""
        properties = ["  debug?: boolean;"]  # Always include debug option
        
        if 'options' in cmd_data:
            for option in cmd_data['options']:
                name = self._camel_case_filter(option.get('name', ''))
                type_str = self._ts_optional_filter(
                    option.get('type', 'string'),
                    option.get('required', False)
                )
                properties.append(f"  {name}: {type_str};")
        
        interface_name = cmd_data.get('typescript', {}).get('interface_name', 'CommandOptions')
        return f"interface {interface_name} {{\n" + "\n".join(properties) + "\n}"
    
    def _generate_config_interface(self, context: Dict[str, Any]) -> str:
        """Generate configuration interface."""
        # Basic config interface - can be extended based on needs
        return """interface ConfigOptions {
  debug?: boolean;
  configPath?: string;
  [key: string]: any;
}"""
    
    def _generate_config_validation(self, context: Dict[str, Any]) -> str:
        """Generate configuration validation logic."""
        return """function validateConfig(config: any): ConfigOptions {
  // Add validation logic here
  return config as ConfigOptions;
}"""
    
    def _generate_config_defaults(self, context: Dict[str, Any]) -> str:
        """Generate default configuration values."""
        return """const DEFAULT_CONFIG: Partial<ConfigOptions> = {
  debug: false
};"""
    
    def _generate_commander_options(self, context: Dict[str, Any]) -> List[str]:
        """Generate Commander.js option builders."""
        # This would generate the .option() calls for Commander.js
        return []
    
    def _generate_commander_arguments(self, context: Dict[str, Any]) -> List[str]:
        """Generate Commander.js argument builders."""
        # This would generate the .argument() calls for Commander.js
        return []
    
    def _generate_action_handlers(self, context: Dict[str, Any]) -> List[str]:
        """Generate Commander.js action handlers."""
        # This would generate the .action() callbacks
        return []
    
    def _generate_completers(self, context: Dict[str, Any]) -> List[str]:
        """Generate completion functions."""
        return []
    
    def _generate_shell_scripts(self, context: Dict[str, Any]) -> Dict[str, str]:
        """Generate shell completion scripts."""
        return {}
    
    # Feature detection helpers
    def _uses_child_process(self, ir: Dict[str, Any]) -> bool:
        """Check if CLI uses child process functionality."""
        # Could check for spawn/exec usage in commands
        return True  # Default to including for CLI tools
    
    def _uses_async_features(self, ir: Dict[str, Any]) -> bool:
        """Check if CLI uses async/await features."""
        return True  # Most modern CLIs are async
    
    def _needs_interface_exports(self, ir: Dict[str, Any]) -> bool:
        """Check if interfaces should be exported."""
        return True  # Default to exporting for TypeScript libraries
    
    def _has_interactive_features(self, cli_schema: Dict[str, Any]) -> bool:
        """Check if CLI has interactive mode features."""
        features = cli_schema.get("features", {})
        interactive_mode = features.get("interactive_mode", {})
        return interactive_mode.get("enabled", False)