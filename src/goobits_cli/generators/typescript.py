"""TypeScript CLI generator implementation."""

from pathlib import Path
from typing import Dict, List, Optional

from .nodejs import NodeJSGenerator
from ..schemas import ConfigSchema, GoobitsConfigSchema


class TypeScriptGenerator(NodeJSGenerator):
    """CLI code generator for TypeScript using Commander.js framework."""
    
    def __init__(self):
        """Initialize the TypeScript generator with TypeScript-specific templates."""
        super().__init__()
        
        # Override template directory to use TypeScript templates
        template_dir = Path(__file__).parent.parent / "templates" / "typescript"
        fallback_dir = Path(__file__).parent.parent / "templates"
        
        # Reinitialize environment with TypeScript templates
        from jinja2 import Environment, FileSystemLoader
        
        if template_dir.exists():
            self.env = Environment(loader=FileSystemLoader([template_dir, fallback_dir]))
            self.template_missing = False
        else:
            # If typescript subdirectory doesn't exist, fallback to nodejs templates
            nodejs_dir = Path(__file__).parent.parent / "templates" / "nodejs"
            if nodejs_dir.exists():
                self.env = Environment(loader=FileSystemLoader([nodejs_dir, fallback_dir]))
            else:
                self.env = Environment(loader=FileSystemLoader(fallback_dir))
            self.template_missing = True
        
        # Add TypeScript-specific filters
        self.env.filters['to_ts_type'] = self._to_typescript_type
        self.env.filters['json_stringify'] = lambda x: self._json_stringify(x)
        self.env.filters['escape_backticks'] = lambda x: x.replace('`', '\\`')
        self.env.filters['camelCase'] = self._to_camel_case
        self.env.filters['PascalCase'] = self._to_pascal_case
        self.env.filters['kebab-case'] = self._to_kebab_case
    
    def _to_typescript_type(self, python_type: str) -> str:
        """Convert Python type hints to TypeScript types."""
        type_map = {
            'str': 'string',
            'int': 'number',
            'float': 'number',
            'bool': 'boolean',
            'flag': 'boolean',
            'list': 'Array<any>',
            'dict': 'Record<string, any>',
            'any': 'any',
            'None': 'void',
        }
        return type_map.get(python_type, 'any')
    
    def _to_camel_case(self, text: str) -> str:
        """Convert text to camelCase."""
        if not text:
            return text
        # Split by various separators
        words = text.replace('-', '_').replace(' ', '_').split('_')
        # First word lowercase, rest title case
        return words[0].lower() + ''.join(word.capitalize() for word in words[1:])
    
    def _to_pascal_case(self, text: str) -> str:
        """Convert text to PascalCase."""
        if not text:
            return text
        # Split by various separators
        words = text.replace('-', '_').replace(' ', '_').split('_')
        # All words title case
        return ''.join(word.capitalize() for word in words)
    
    def _to_kebab_case(self, text: str) -> str:
        """Convert text to kebab-case."""
        if not text:
            return text
        # Replace underscores and spaces with hyphens, convert to lowercase
        return text.replace('_', '-').replace(' ', '-').lower()
    
    def _check_file_conflicts(self, target_files: dict) -> dict:
        """Check for file conflicts and adjust paths if needed."""
        import os
        
        adjusted_files = {}
        warnings = []
        
        for filepath, content in target_files.items():
            if filepath == "index.ts" and os.path.exists(filepath):
                # index.ts exists, generate cli.ts instead
                new_filepath = "cli.ts"
                adjusted_files[new_filepath] = content
                warnings.append(f"⚠️  Existing index.ts detected. Generated cli.ts instead.")
                warnings.append(f"   Import cli.ts in your index.ts with: import {{ cli }} from './cli.js'; cli();")
            elif filepath == "package.json" and os.path.exists(filepath):
                warnings.append(f"⚠️  Existing package.json detected. Review and merge dependencies manually.")
                adjusted_files[filepath] = content  # Still generate, but warn user
            elif filepath == "tsconfig.json" and os.path.exists(filepath):
                warnings.append(f"⚠️  Existing tsconfig.json detected. Review and merge settings manually.")
                adjusted_files[filepath] = content  # Still generate, but warn user
            else:
                adjusted_files[filepath] = content
        
        # Print warnings if any
        if warnings:
            print("\n🔍 File Conflict Detection:")
            for warning in warnings:
                print(f"   {warning}")
            print()
        
        return adjusted_files
    
    def get_output_files(self) -> List[str]:
        """Return list of files this generator creates."""
        return [
            "index.ts",
            "src/hooks.ts",
            "package.json",
            "tsconfig.json",
            "setup.sh",
            "README.md",
            ".gitignore"
        ]
    
    def get_default_output_path(self, package_name: str) -> str:
        """Get the default output path for TypeScript projects."""
        return f"index.ts"
    
    def generate_all_files(self, config, config_filename: str, version: Optional[str] = None) -> Dict[str, str]:
        """Generate all files for a TypeScript CLI project."""
        # Extract metadata using base class helper
        from typing import Union
        from ..schemas import ConfigSchema, GoobitsConfigSchema
        
        metadata = self._extract_config_metadata(config)
        cli_config = metadata['cli_config']
        
        # Validate configuration
        if hasattr(config, 'package_name'):  # GoobitsConfigSchema
            if not cli_config:
                raise ValueError("No CLI configuration found")
        
        # Prepare context for template rendering
        context = {
            'cli': cli_config,
            'file_name': config_filename,
            'package_name': metadata['package_name'],
            'command_name': metadata['command_name'],
            'display_name': metadata['display_name'],
            'description': getattr(config, 'description', cli_config.description if cli_config else ''),
            'version': version or (cli_config.version if cli_config and hasattr(cli_config, 'version') else '1.0.0'),
            'installation': metadata['installation'],
            'hooks_path': metadata['hooks_path'],
        }
        
        files = {}
        
        # Generate main index.ts file - CLI entry point (use minimal fallback)
        files['index.ts'] = self._generate_fallback_typescript_code(context)
        
        # Generate src/hooks.ts file - user's business logic (use minimal fallback)
        files['src/hooks.ts'] = self._generate_simple_hooks(context)
        
        # Generate package.json - use minimal fallback approach
        files['package.json'] = self._generate_typescript_package_json(context)
        
        # Generate tsconfig.json - use minimal fallback approach
        files['tsconfig.json'] = self._generate_tsconfig(context)
        
        # Generate setup script - use minimal fallback approach
        files['setup.sh'] = self._generate_typescript_setup_script(context)
        
        # Generate README.md
        files['README.md'] = self._generate_readme(config, is_typescript=True)
        
        # Generate .gitignore
        files['.gitignore'] = self._generate_gitignore(is_typescript=True)
        
        # Check for file conflicts and adjust if needed
        files = self._check_file_conflicts(files)
        
        return files
    
    def _generate_simple_hooks(self, context: dict) -> str:
        """Generate a simple hooks.ts file similar to Python's app_hooks.py."""
        cli_config = context.get('cli')
        hooks_content = f'''/**
 * Hook functions for {context['display_name']}
 * Auto-generated from {context['file_name']}
 * 
 * Implement your business logic in these hook functions.
 * Each command will call its corresponding hook function.
 */

export interface CommandArgs {{
  commandName: string;
  rawArgs?: Record<string, any>;
  [key: string]: any;
}}

/**
 * Hook function for unknown commands
 * @param args - Command arguments and options
 * @returns Promise<void>
 */
export async function onUnknownCommand(args: CommandArgs): Promise<void> {{
  console.log(`🤔 Unknown command: ${{args.commandName}}`);
  console.log('   Use --help to see available commands');
}}
'''
        
        # Generate hook functions for each command
        if cli_config and hasattr(cli_config, 'commands'):
            for cmd_name, cmd_data in cli_config.commands.items():
                safe_cmd_name = cmd_name.replace('-', '_')
                function_name = f"on{safe_cmd_name.replace('_', '').title()}"
                hooks_content += f'''
/**
 * Hook function for '{cmd_name}' command
 * @param args - Command arguments and options
 * @returns Promise<void>
 */
export async function {function_name}(args: CommandArgs): Promise<void> {{
    // TODO: Implement your '{cmd_name}' command logic here
    console.log('🚀 Executing {cmd_name} command...');
    console.log('   Command:', args.commandName);
    
    // Example: access raw arguments
    if (args.rawArgs) {{
        Object.entries(args.rawArgs).forEach(([key, value]) => {{
            console.log(`   ${{key}}: ${{value}}`);
        }});
    }}
    
    console.log('✅ {cmd_name} command completed successfully!');
}}'''
        
        return hooks_content
    
    
    def _generate_gitignore(self, is_typescript: bool = False) -> str:
        """Generate .gitignore file with TypeScript-specific patterns."""
        base_gitignore = super()._generate_gitignore()
        if is_typescript:
            typescript_ignores = '''
# TypeScript
dist/
*.tsbuildinfo
.eslintcache

# TypeScript test coverage
coverage/
.nyc_output/
'''
            return base_gitignore + typescript_ignores
        return base_gitignore
    
    def _generate_readme(self, config, is_typescript: bool = False) -> str:
        """Generate README with TypeScript-specific instructions."""
        # Convert config to dict format expected by parent
        context = {
            'package_name': getattr(config, 'package_name', 'generated-cli'),
            'command_name': getattr(config, 'command_name', 'generated-cli'),
            'display_name': getattr(config, 'display_name', 'Generated CLI'),
            'description': getattr(config, 'description', 'A CLI generated by goobits'),
        }
        readme = super()._generate_readme(context)
        
        if is_typescript:
            # Replace JavaScript references with TypeScript
            readme = readme.replace('JavaScript', 'TypeScript')
            readme = readme.replace('.js', '.ts')
            readme = readme.replace('node index.js', 'npm start')
            
            # Add TypeScript-specific sections
            typescript_section = '''
## Development

This CLI is written in TypeScript. To work on the source code:

1. Install dependencies: `npm install`
2. Build the project: `npm run build`
3. Run in development mode: `npm run dev`
4. Run tests: `npm test`
5. Type check: `npm run typecheck`
6. Lint: `npm run lint`
7. Format code: `npm run format`

The compiled JavaScript files are in the `dist/` directory.
'''
            # Insert before the License section if it exists
            if '## License' in readme:
                readme = readme.replace('## License', typescript_section + '\n## License')
            else:
                readme += typescript_section
        
        return readme
    
    def _generate_fallback_typescript_code(self, context: dict) -> str:
        """Generate fallback TypeScript code when templates are missing."""
        import json
        cli_config = context['cli']
        package_name = context['package_name'] or 'my-cli'
        command_name = context['command_name'] or package_name
        description = context['description'] or 'A CLI tool'
        version = context['version']
        
        # Generate a basic Commander.js CLI using ES modules
        code = f'''/**
 * Generated by goobits-cli
 * Auto-generated from {context['file_name']}
 */

import {{ Command }} from 'commander';
import * as hooks from './src/hooks.js';

const program = new Command();

program
  .name('{command_name}')
  .description('{description}')
  .version('{version}');

// Configuration from {context['file_name']}
const config = {json.dumps(cli_config.model_dump() if cli_config else {}, indent=2)};

'''
        
        # Add commands if available
        if cli_config and cli_config.commands:
            code += "// Commands\n"
            for cmd_name, cmd_data in cli_config.commands.items():
                safe_cmd_name = cmd_name.replace('-', '_')
                function_name = f"on{safe_cmd_name.replace('_', '').title()}"
                code += f'''
program
  .command('{cmd_name}')
  .description('{cmd_data.desc}')'''
                
                # Add arguments
                if cmd_data.args:
                    for arg in cmd_data.args:
                        if arg.required:
                            arg_str = f'<{arg.name}>'
                        else:
                            arg_str = f'[{arg.name}]'
                        code += f'''
  .argument('{arg_str}', '{arg.desc}')'''
                
                # Add options
                if cmd_data.options:
                    for opt in cmd_data.options:
                        flags = f'-{opt.short}, --{opt.name}'
                        if opt.type != 'flag':
                            flags += f' <{opt.type}>'
                        code += f'''
  .option('{flags}', '{opt.desc}')'''
                
                code += f'''
  .action(async ('''
                if cmd_data.args:
                    code += ', '.join(arg.name for arg in cmd_data.args) + ', '
                code += f'''options: any) => {{
    const args = {{
      commandName: '{cmd_name}',
      rawArgs: options,'''
                
                if cmd_data.args:
                    for arg in cmd_data.args:
                        code += f'''
      {arg.name},'''
                        
                code += f'''
    }};
    
    try {{
      await hooks.{function_name}(args);
    }} catch (error) {{
      console.error(`Error executing {cmd_name}:`, error);
      process.exit(1);
    }}
  }});
'''
        
        code += '''
// Main CLI function
export function cli(): void {
  program.parse(process.argv);
  
  // Show help if no command provided
  if (!process.argv.slice(2).length) {
    program.outputHelp();
  }
}

// Default export for compatibility
export default program;
'''
        
        return code
    
    def _generate_typescript_package_json(self, context: dict) -> str:
        """Generate TypeScript package.json when template is missing."""
        import json
        package_json = {
            "name": context.get('package_name', 'generated-cli'),
            "version": context.get('version', '1.0.0'),
            "description": context.get('description', 'A CLI tool'),
            "main": "dist/index.js",
            "types": "dist/index.d.ts",
            "bin": {
                context.get('command_name', 'cli'): "./dist/bin/cli.js"
            },
            "scripts": {
                "build": "tsc",
                "start": "ts-node index.ts",
                "test": "node --loader ts-node/esm --test test/**/*.test.ts"
            },
            "dependencies": {
                "commander": "^11.1.0",
                "chalk": "^5.3.0"
            },
            "devDependencies": {
                "typescript": "^5.3.0",
                "@types/node": "^20.0.0",
                "ts-node": "^10.9.0"
            },
            "type": "module"
        }
        return json.dumps(package_json, indent=2)
    
    def _generate_tsconfig(self, context: dict) -> str:
        """Generate tsconfig.json when template is missing."""
        import json
        tsconfig = {
            "compilerOptions": {
                "target": "ES2022",
                "module": "NodeNext",
                "moduleResolution": "NodeNext",
                "outDir": "./dist",
                "strict": True,
                "esModuleInterop": True,
                "skipLibCheck": True
            },
            "include": ["index.ts", "bin/**/*.ts", "lib/**/*.ts"],
            "exclude": ["node_modules", "dist"]
        }
        return json.dumps(tsconfig, indent=2)
    
    def _generate_typescript_setup_script(self, context: dict) -> str:
        """Generate TypeScript setup script when template is missing."""
        return '''#!/bin/bash
echo "Setting up TypeScript CLI..."
npm install
npm run build
echo "TypeScript CLI setup complete!"
'''