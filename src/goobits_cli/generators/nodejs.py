"""Node.js CLI generator implementation."""

import json
from pathlib import Path
from typing import List, Optional, Union, Dict, Any
from jinja2 import Environment, FileSystemLoader, TemplateNotFound
import typer

from . import BaseGenerator
from ..schemas import ConfigSchema, GoobitsConfigSchema
from ..formatter import align_header_items, format_icon_spacing, align_setup_steps

# Universal Template System imports
try:
    from ..universal.template_engine import UniversalTemplateEngine, LanguageRenderer
    from ..universal.renderers.nodejs_renderer import NodeJSRenderer as UniversalNodeJSRenderer
    UNIVERSAL_TEMPLATES_AVAILABLE = True
except ImportError:
    UNIVERSAL_TEMPLATES_AVAILABLE = False
    UniversalTemplateEngine = None
    UniversalNodeJSRenderer = None

# Phase 2 shared components (to be created)
# from ..shared.components.validation_framework import ValidationRunner, ValidationMode
# from ..shared.components.validators import (
#     CommandValidator, ArgumentValidator, OptionValidator,
#     ConfigurationValidator, HookValidator
# )
try:
    from ..shared.components.doc_generator import DocumentationGenerator
except ImportError:
    # Phase 2 components not yet available
    DocumentationGenerator = None


class NodeJSGenerator(BaseGenerator):
    """CLI code generator for Node.js using Commander.js framework."""
    
    def __init__(self, use_universal_templates: bool = False):
        """Initialize the Node.js generator with Jinja2 environment.
        
        Args:
            use_universal_templates: If True, use Universal Template System
        """
        self.use_universal_templates = use_universal_templates and UNIVERSAL_TEMPLATES_AVAILABLE
        
        # Initialize Universal Template System if requested
        if self.use_universal_templates:
            try:
                self.universal_engine = UniversalTemplateEngine()
                self.nodejs_renderer = UniversalNodeJSRenderer()
                self.universal_engine.register_renderer(self.nodejs_renderer)
            except Exception as e:
                print(f"⚠️  Failed to initialize Universal Template System: {e}")
                print("   Falling back to legacy template system")
                self.use_universal_templates = False
                self.universal_engine = None
                self.nodejs_renderer = None
        
        # Set up Jinja2 environment for Node.js templates (legacy mode)
        template_dir = Path(__file__).parent.parent / "templates" / "nodejs"
        fallback_dir = Path(__file__).parent.parent / "templates"
        
        # Try nodejs subdirectory first, fallback to main templates
        if template_dir.exists():
            self.env = Environment(loader=FileSystemLoader([template_dir, fallback_dir]))
        else:
            # If nodejs subdirectory doesn't exist, use main templates dir
            self.env = Environment(loader=FileSystemLoader(fallback_dir))
            self.template_missing = True
        
        # Initialize shared components (Phase 2)
        # self.validation_runner = ValidationRunner()
        self.doc_generator = None  # Will be initialized per generation with config
        
        # Add custom filters (these may need Node.js specific versions later)
        def json_stringify(x):
            """Convert to JSON, handling Pydantic models."""
            if hasattr(x, 'model_dump'):
                return json.dumps(x.model_dump(), indent=2)
            elif hasattr(x, 'dict'):
                return json.dumps(x.dict(), indent=2)
            else:
                return json.dumps(x, indent=2)
        
        self.env.filters['json_stringify'] = json_stringify
        self.env.filters['escape_backticks'] = lambda x: x.replace('`', '\\`')
        self.env.filters['align_header_items'] = align_header_items
        self.env.filters['format_icon_spacing'] = format_icon_spacing
        self.env.filters['align_setup_steps'] = align_setup_steps
        
        # Initialize generated files storage
        self._generated_files = {}
    
    def _check_file_conflicts(self, target_files: dict) -> dict:
        """Check for file conflicts and adjust paths if needed."""
        import os
        
        adjusted_files = {}
        warnings = []
        
        for filepath, content in target_files.items():
            if filepath == "index.js" and os.path.exists(filepath):
                # index.js exists, generate cli.js instead
                new_filepath = "cli.js"
                adjusted_files[new_filepath] = content
                warnings.append(f"⚠️  Existing index.js detected. Generated cli.js instead.")
                warnings.append(f"   Import cli.js in your index.js with: import {{ cli }} from './cli.js'; cli();")
            elif filepath == "package.json" and os.path.exists(filepath):
                warnings.append(f"⚠️  Existing package.json detected. Review and merge dependencies manually.")
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
    
    def _validate_configuration(self, config: Union[ConfigSchema, GoobitsConfigSchema], 
                               cli_config: Optional[ConfigSchema]) -> None:
        """Validate configuration using shared validators when available.
        
        Args:
            config: The configuration object
            cli_config: The CLI configuration extracted from config
            
        Raises:
            ValueError: If configuration is invalid
        """
        # Phase 2: Use ConfigurationValidator when available
        # if self.validation_runner:
        #     validator = ConfigurationValidator()
        #     result = self.validation_runner.validate(validator, config)
        #     if not result.is_valid:
        #         raise ValueError(f"Configuration validation failed: {result.errors}")
        
        # Current validation logic
        if hasattr(config, 'package_name'):  # GoobitsConfigSchema
            if not cli_config:
                raise ValueError("No CLI configuration found")
        
        # Additional validations can be added here
        if cli_config:
            # Validate commands
            if hasattr(cli_config, 'commands') and cli_config.commands:
                for cmd_name, cmd_data in cli_config.commands.items():
                    # Phase 2: Use CommandValidator
                    # if self.validation_runner:
                    #     cmd_validator = CommandValidator()
                    #     cmd_result = self.validation_runner.validate(cmd_validator, cmd_data)
                    #     if not cmd_result.is_valid:
                    #         raise ValueError(f"Command '{cmd_name}' validation failed: {cmd_result.errors}")
                    
                    # Validate arguments
                    if hasattr(cmd_data, 'args') and cmd_data.args:
                        for arg in cmd_data.args:
                            # Phase 2: Use ArgumentValidator
                            pass
                    
                    # Validate options
                    if hasattr(cmd_data, 'options') and cmd_data.options:
                        for opt in cmd_data.options:
                            # Phase 2: Use OptionValidator
                            pass
    
    def generate(self, config: Union[ConfigSchema, GoobitsConfigSchema], 
                 config_filename: str, version: Optional[str] = None) -> str:
        """
        Generate Node.js CLI code from configuration.
        
        Args:
            config: The configuration object
            config_filename: Name of the configuration file
            version: Optional version string
            
        Returns:
            Generated Node.js CLI code
        """
        # Use Universal Template System if enabled
        if self.use_universal_templates:
            return self._generate_with_universal_templates(config, config_filename, version)
        
        # Fall back to legacy implementation
        return self._generate_legacy(config, config_filename, version)
    
    def _generate_with_universal_templates(self, config: Union[ConfigSchema, GoobitsConfigSchema], 
                                         config_filename: str, version: Optional[str] = None) -> str:
        """
        Generate using Universal Template System.
        
        Args:
            config: The configuration object
            config_filename: Name of the configuration file
            version: Optional version string
            
        Returns:
            Generated Node.js CLI code
        """
        try:
            # Ensure universal engine is available
            if not self.universal_engine:
                raise RuntimeError("Universal Template Engine not initialized")
            
            # Convert config to GoobitsConfigSchema if needed
            if isinstance(config, ConfigSchema):
                # Create minimal GoobitsConfigSchema for universal system
                goobits_config = GoobitsConfigSchema(
                    package_name=getattr(config, 'package_name', config.cli.name),
                    command_name=getattr(config, 'command_name', config.cli.name),
                    description=getattr(config, 'description', config.cli.description or config.cli.tagline),
                    cli=config,
                    installation=getattr(config, 'installation', None)
                )
            else:
                goobits_config = config
                
            # Generate using universal engine
            output_dir = Path(".")
            generated_files = self.universal_engine.generate_cli(
                goobits_config, "nodejs", output_dir
            )
            
            # Store generated files for later access
            self._generated_files = {}
            for file_path, content in generated_files.items():
                # Extract relative filename for compatibility
                relative_path = Path(file_path).name
                self._generated_files[relative_path] = content
            
            # Return main entry file for backward compatibility
            main_file = next((content for path, content in generated_files.items() 
                            if "index.js" in path or "cli.js" in path), "")
            
            if not main_file:
                # If no main file found, use the first available content
                main_file = next(iter(generated_files.values()), "")
                
            return main_file
            
        except Exception as e:
            # Fall back to legacy mode if universal templates fail
            print(f"⚠️  Universal Templates failed ({type(e).__name__}: {e}), falling back to legacy mode")
            # Disable universal templates for subsequent calls to avoid repeated failures
            self.use_universal_templates = False
            return self._generate_legacy(config, config_filename, version)
    
    def _generate_legacy(self, config: Union[ConfigSchema, GoobitsConfigSchema], 
                        config_filename: str, version: Optional[str] = None) -> str:
        """
        Generate using legacy template system.
        
        Args:
            config: The configuration object
            config_filename: Name of the configuration file
            version: Optional version string
            
        Returns:
            Generated Node.js CLI code
        """
        # Extract metadata using base class helper
        metadata = self._extract_config_metadata(config)
        cli_config = metadata['cli_config']
        
        # Validate configuration
        self._validate_configuration(config, cli_config)
        
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
        
        # Try to load Node.js specific template
        try:
            template = self.env.get_template("index.js.j2")
            code = template.render(**context)
            return code
        except TemplateNotFound:
            # Provide helpful error message with template content
            return self._generate_fallback_code(context)
    
    def get_output_files(self) -> List[str]:
        """Return list of files this generator creates."""
        return [
            "index.js",
            "src/hooks.js",
            "package.json",
            "setup.sh",
            "README.md",
            ".gitignore",
            "cli.js",
            "bin/cli.js",
            "lib/errors.js",
            "lib/config.js",
            "lib/completion.js",
            "lib/formatter.js",
            "lib/progress.js",
            "lib/prompts.js",
            "lib/plugin-manager.js",
            "completion_engine.js"
        ]
    
    def get_default_output_path(self, package_name: str) -> str:
        """Get the default output path for Node.js CLI."""
        return "index.js"  # Main entry point for ES modules
    
    def _generate_fallback_code(self, context: dict) -> str:
        """Generate a basic Node.js CLI when templates are missing."""
        cli_config = context['cli']
        package_name = context['package_name'] or 'my-cli'
        command_name = context['command_name'] or package_name
        description = context['description'] or 'A CLI tool'
        version = context['version']
        
        # Generate a basic Commander.js CLI using ES modules
        code = f'''/**
 * Generated by goobits-cli
 * 
 * Note: Node.js templates are not yet installed.
 * This is a basic CLI structure. To get full functionality,
 * ensure Node.js templates are installed in:
 * src/goobits_cli/templates/nodejs/
 */

import {{ Command }} from 'commander';
import chalk from 'chalk';

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
  .action(('''
                if cmd_data.args:
                    code += ', '.join(arg.name for arg in cmd_data.args) + ', '
                code += f'''options) => {{
    console.log('Executing {cmd_name} command...');
    console.log('This is a placeholder. Implement your logic here.');
  }});
'''
        
        code += '''
// Main CLI function
export function cli() {
  program.parse(process.argv);
  
  // Show help if no command provided
  if (!process.argv.slice(2).length) {
    program.outputHelp();
  }
}

// Export for use as a module
export default cli;
'''
        
        return code
    
    
    
    def generate_all_files(self, config: Union[ConfigSchema, GoobitsConfigSchema], 
                          config_filename: str, version: Optional[str] = None) -> Dict[str, str]:
        """
        Generate all files needed for the Node.js CLI.
        
        Args:
            config: The configuration object
            config_filename: Name of the configuration file
            version: Optional version string
            
        Returns:
            Dictionary mapping file paths to their contents
        """
        # Use Universal Template System if enabled
        if self.use_universal_templates:
            # Generate main file to populate _generated_files
            self.generate(config, config_filename, version)
            return self._generated_files.copy() if self._generated_files else {}
        
        # Legacy implementation - generate all files using legacy system
        return self._generate_all_files_legacy(config, config_filename, version)
    
    def _generate_all_files_legacy(self, config: Union[ConfigSchema, GoobitsConfigSchema], 
                                  config_filename: str, version: Optional[str] = None) -> Dict[str, str]:
        """
        Generate all files using legacy template system.
        
        Args:
            config: The configuration object
            config_filename: Name of the configuration file
            version: Optional version string
            
        Returns:
            Dictionary mapping file paths to their contents
        """
        # Extract metadata using base class helper
        metadata = self._extract_config_metadata(config)
        cli_config = metadata['cli_config']
        
        # Validate configuration
        self._validate_configuration(config, cli_config)
        
        # Initialize documentation generator for this generation
        try:
            config_dict = config.model_dump() if hasattr(config, 'model_dump') else config.dict()
            self.doc_generator = DocumentationGenerator('nodejs', config_dict)
        except Exception:
            # If initialization fails, doc_generator remains None and we use fallback methods
            pass
        
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
        
        # Generate main index.js file - CLI entry point
        try:
            template = self.env.get_template("index.js.j2")
            files['index.js'] = template.render(**context)
        except TemplateNotFound:
            files['index.js'] = self._generate_fallback_code(context)
        
        # Generate src/hooks.js file - user's business logic
        files['src/hooks.js'] = self._generate_simple_hooks(context)
        
        # Generate package.json
        try:
            template = self.env.get_template("package.json.j2")
            files['package.json'] = template.render(**context)
        except TemplateNotFound:
            files['package.json'] = self._generate_package_json(context)
        
        # Generate setup script
        try:
            template = self.env.get_template("setup.sh.j2")
            files['setup.sh'] = template.render(**context)
        except TemplateNotFound:
            files['setup.sh'] = self._generate_setup_script(context)
        
        # Generate helper library files
        helper_files = [
            'lib/errors.js',
            'lib/config.js',
            'lib/completion.js',
            'lib/formatter.js',
            'lib/progress.js',
            'lib/prompts.js',
            'lib/plugin-manager.js',
            'completion_engine.js'
        ]
        
        for helper_file in helper_files:
            try:
                template = self.env.get_template(f"{helper_file}.j2")
                files[helper_file] = template.render(**context)
            except TemplateNotFound:
                # Skip if template doesn't exist - these are optional helper files
                pass
        
        # Generate bin/cli.js if template exists
        try:
            template = self.env.get_template("bin/cli.js.j2")
            files['bin/cli.js'] = template.render(**context)
        except TemplateNotFound:
            pass
        
        # Generate cli.js as alternative entry point
        try:
            template = self.env.get_template("cli.js.j2")
            files['cli.js'] = template.render(**context)
        except TemplateNotFound:
            pass
        
        # Generate README.md
        files['README.md'] = self._generate_readme(context)
        
        # Generate .gitignore
        files['.gitignore'] = self._generate_gitignore()
        
        # Check for file conflicts and adjust if needed
        files = self._check_file_conflicts(files)
        
        return files
    
    def _generate_simple_hooks(self, context: dict) -> str:
        """Generate a simple hooks.js file similar to Python's app_hooks.py."""
        cli_config = context.get('cli')
        hooks_content = f'''/**
 * Hook functions for {context['display_name']}
 * Auto-generated from {context['file_name']}
 * 
 * Implement your business logic in these hook functions.
 * Each command will call its corresponding hook function.
 */

'''
        
        # Generate hook functions for each command
        if cli_config and hasattr(cli_config, 'commands'):
            for cmd_name, cmd_data in cli_config.commands.items():
                safe_cmd_name = cmd_name.replace('-', '_')
                hooks_content += f'''/**
 * Hook function for '{cmd_name}' command
 * @param {{Object}} args - Command arguments and options
 * @returns {{Promise<void>}}
 */
export async function on{safe_cmd_name.replace('_', '').title()}(args) {{
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
}}

'''
        
        # Add a catch-all hook for unhandled commands
        hooks_content += '''/**
 * Default hook for unhandled commands
 * @param {Object} args - Command arguments
 * @throws {Error} When no hook implementation is found
 */
export async function onUnknownCommand(args) {
    throw new Error(`No hook implementation found for command: ${args.commandName}`);
}
'''
        
        return hooks_content
    
    def _generate_setup_script(self, context: dict) -> str:
        """Generate setup.sh script for Node.js CLI."""
        return f'''#!/bin/bash
# Setup script for {context['display_name']}
# Auto-generated from {context['file_name']}

set -e

echo "🔧 Setting up {context['display_name']}..."

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js not found. Please install Node.js first:"
    echo "   https://nodejs.org/"
    exit 1
fi

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "❌ npm not found. Please install npm first."
    exit 1
fi

# Install dependencies
echo "📦 Installing dependencies..."
npm install

if [ $? -eq 0 ]; then
    echo "✅ Setup successful!"
    echo "📍 CLI location: index.js"
    echo ""
    echo "To install globally:"
    echo "   npm link"
    echo ""
    echo "To run locally:"
    echo "   node index.js --help"
else
    echo "❌ Setup failed!"
    exit 1
fi
'''
    
    def _generate_package_json(self, context: dict) -> str:
        """Generate minimal package.json from context."""
        # Use minimal fallback approach only
        package_data = {
            "name": context['package_name'],
            "version": context['version'],
            "description": context['description'],
            "main": "index.js",
            "bin": {
                context['command_name']: "./index.js"
            },
            "scripts": {
                "test": "echo \"Error: no test specified\" && exit 1",
                "start": "node index.js"
            },
            "keywords": ["cli"],
            "author": "",
            "license": "MIT",
            "type": "module",
            "dependencies": {
                "commander": "^11.1.0",
                "chalk": "^5.3.0"
            },
            "engines": {
                "node": ">=14.0.0"
            }
        }
        
        # Add any npm packages from installation extras
        if context.get('installation') and hasattr(context['installation'], 'extras'):
            if hasattr(context['installation'].extras, 'npm'):
                for package in context['installation'].extras.npm:
                    if '@' in package:
                        name, version = package.rsplit('@', 1)
                        package_data["dependencies"][name] = f"^{version}"
                    else:
                        package_data["dependencies"][package] = "latest"
        
        return json.dumps(package_data, indent=2)
    
    def _generate_readme(self, context: dict) -> str:
        """Generate README.md for the Node.js CLI."""
        # Use DocumentationGenerator if available
        if self.doc_generator and DocumentationGenerator:
            try:
                return self.doc_generator.generate_readme()
            except Exception:
                # Fallback to manual generation if doc_generator fails
                pass
        
        # Fallback to existing implementation
        return f"""# {context['display_name']}

{context['description']}

## Installation

### From npm (when published)
```bash
npm install -g {context['package_name']}
```

### For development
```bash
# Clone the repository
git clone <your-repo-url>
cd {context['package_name']}

# Install dependencies and link globally
npm install
npm link
```

## Usage

```bash
{context['command_name']} --help
```

## Commands

{self._generate_commands_documentation(context)}

## Development

To run in development mode:
```bash
# Install dependencies
npm install

# Run locally
node index.js --help
```

To implement command logic, edit the hook functions in `src/hooks.js`.

## License

MIT
"""
    
    def _generate_commands_documentation(self, context: dict) -> str:
        """Generate commands documentation for README."""
        cli_config = context.get('cli')
        if not cli_config or not hasattr(cli_config, 'commands'):
            return "No commands configured."
        
        commands_doc = []
        for cmd_name, cmd_data in cli_config.commands.items():
            cmd_desc = cmd_data.desc if hasattr(cmd_data, 'desc') else 'Command description'
            commands_doc.append(f"- `{cmd_name}` - {cmd_desc}")
            
            # Add subcommands if they exist
            if hasattr(cmd_data, 'subcommands') and cmd_data.subcommands:
                for sub_name, sub_data in cmd_data.subcommands.items():
                    sub_desc = sub_data.desc if hasattr(sub_data, 'desc') else 'Subcommand description'
                    commands_doc.append(f"  - `{cmd_name} {sub_name}` - {sub_desc}")
        
        return '\n'.join(commands_doc) if commands_doc else "No commands configured."
    
    def _generate_gitignore(self) -> str:
        """Generate .gitignore for Node.js project."""
        return """# Node.js
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*
lerna-debug.log*
.npm

# Environment variables
.env
.env.local
.env.development.local
.env.test.local
.env.production.local

# OS files
.DS_Store
Thumbs.db

# IDE files
.idea/
.vscode/
*.swp
*.swo

# Test coverage
coverage/
.nyc_output/

# Build outputs
dist/
build/

# Logs
logs/
*.log

# Config (keep local config private)
config.local.json
"""