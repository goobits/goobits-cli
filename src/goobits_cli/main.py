#!/usr/bin/env python3
import yaml
import toml
import shutil
import subprocess
import re
from copy import deepcopy
from pathlib import Path
from typing import Optional
import typer
from jinja2 import Environment, FileSystemLoader
from pydantic import ValidationError

from .schemas import ConfigSchema, GoobitsConfigSchema
from .builder import generate_cli_code
from .pypi_server import serve_packages
from .__version__ import __version__

# Default cache time-to-live in seconds (1 hour)
DEFAULT_CACHE_TTL = 3600

def version_callback(value: bool):
    if value:
        typer.echo(f"goobits-cli {__version__}")
        raise typer.Exit()

app = typer.Typer(name="goobits", help="Unified CLI for Goobits projects")

@app.callback()
def main(
    version: Optional[bool] = typer.Option(None, "--version", callback=version_callback, is_eager=True, help="Show version and exit")
):
    """Goobits CLI Framework - Build professional command-line tools with YAML configuration."""
    pass


def load_goobits_config(file_path: Path) -> GoobitsConfigSchema:
    """Load and validate goobits.yaml configuration file."""
    try:
        with open(file_path, 'r') as f:
            data = yaml.safe_load(f)
        
        config = GoobitsConfigSchema(**data)
        return config
    except FileNotFoundError:
        typer.echo(f"Error: File '{file_path}' not found.", err=True)
        raise typer.Exit(1)
    except yaml.YAMLError as e:
        typer.echo(f"Error parsing YAML: {e}", err=True)
        raise typer.Exit(1)
    except ValidationError as e:
        typer.echo(f"Error validating configuration: {e}", err=True)
        raise typer.Exit(1)


def normalize_dependencies_for_template(config: GoobitsConfigSchema) -> GoobitsConfigSchema:
    """Normalize dependencies for template rendering with enhanced data."""
    # Create a copy to avoid modifying the original
    normalized_config = deepcopy(config)
    
    # The DependenciesSchema validator already normalizes the dependencies,
    # so we just need to ensure they're properly formatted for the template
    
    return normalized_config


def dependency_to_dict(dep):
    """Convert DependencyItem to dict for JSON serialization."""
    if isinstance(dep, str):
        return {'name': dep, 'type': 'command'}
    elif hasattr(dep, 'model_dump'):
        return dep.model_dump()
    elif hasattr(dep, 'dict'):
        return dep.dict()
    elif isinstance(dep, dict):
        return dep
    else:
        return {'name': str(dep), 'type': 'command'}

def dependencies_to_json(deps):
    """Convert list of dependencies to JSON string."""
    import json
    return json.dumps([dependency_to_dict(dep) for dep in deps])

def extract_version_from_pyproject(project_dir: Path) -> str:
    """Extract version from pyproject.toml."""
    pyproject_path = project_dir / "pyproject.toml"
    
    if not pyproject_path.exists():
        return "unknown"
    
    try:
        with open(pyproject_path, 'r') as f:
            data = toml.load(f)
        
        # Try different locations for version
        if 'tool' in data and 'poetry' in data['tool'] and 'version' in data['tool']['poetry']:
            return data['tool']['poetry']['version']
        elif 'project' in data and 'version' in data['project']:
            return data['project']['version']
        else:
            return "unknown"
            
    except Exception:
        return "unknown"


def generate_setup_script(config: GoobitsConfigSchema, project_dir: Path) -> str:
    """Generate setup.sh script from goobits configuration."""
    template_dir = Path(__file__).parent / "templates"
    env = Environment(loader=FileSystemLoader(template_dir))
    
    # Add custom filters
    env.filters['dependency_to_dict'] = dependency_to_dict
    env.filters['dependencies_to_json'] = dependencies_to_json
    
    template = env.get_template("setup_template.sh.j2")
    
    # Extract version from pyproject.toml
    version = extract_version_from_pyproject(project_dir)
    
    # Convert goobits config to template variables
    template_vars = {
        'package_name': config.package_name,
        'command_name': config.command_name,
        'display_name': config.display_name,
        'description': config.description,
        'version': version,
        'python': {
            'minimum_version': config.python.minimum_version,
            'maximum_version': config.python.maximum_version,
        },
        'dependencies': {
            'required': config.dependencies.required,
            'optional': config.dependencies.optional,
        },
        'installation': {
            'pypi_name': config.installation.pypi_name,
            'development_path': config.installation.development_path,
            'extras': config.installation.extras,
        },
        'shell_integration': {
            'enabled': config.shell_integration.enabled,
            'alias': config.shell_integration.alias,
        },
        'validation': {
            'check_api_keys': config.validation.check_api_keys,
            'check_disk_space': config.validation.check_disk_space,
            'minimum_disk_space_mb': config.validation.minimum_disk_space_mb,
        },
        'messages': {
            'install_success': config.messages.install_success,
            'install_dev_success': config.messages.install_dev_success,
            'upgrade_success': config.messages.upgrade_success,
            'uninstall_success': config.messages.uninstall_success,
        },
        'cache_ttl': DEFAULT_CACHE_TTL,
    }
    
    script = template.render(**template_vars)
    return script


def backup_file(file_path: Path, create_backup: bool = False) -> Optional[Path]:
    """Create a backup of a file if it exists and backup is requested."""
    if create_backup and file_path.exists():
        backup_path = file_path.with_suffix(file_path.suffix + '.bak')
        shutil.copy2(file_path, backup_path)
        return backup_path
    return None


def update_pyproject_toml(project_dir: Path, package_name: str, command_name: str, cli_filename: str = "generated_cli.py", create_backup: bool = False) -> bool:
    """Update pyproject.toml to use the generated CLI."""
    pyproject_path = project_dir / "pyproject.toml"
    
    if not pyproject_path.exists():
        typer.echo("⚠️  No pyproject.toml found, skipping entry point update", err=True)
        return False
    
    try:
        # Backup pyproject.toml if requested
        backup_path = backup_file(pyproject_path, create_backup)
        if backup_path:
            typer.echo(f"📋 Created backup: {backup_path}")
        
        # Read pyproject.toml
        with open(pyproject_path, 'r') as f:
            data = toml.load(f)
        
        # Update the entry points
        # Remove .py extension from filename for module import
        cli_module_name = cli_filename.replace('.py', '')
        
        if 'tool' in data and 'poetry' in data['tool'] and 'scripts' in data['tool']['poetry']:
            # Poetry format
            data['tool']['poetry']['scripts'][command_name] = f"{package_name}.{cli_module_name}:cli_entry"
            typer.echo(f"✅ Updated Poetry entry point for '{command_name}'")
        elif 'project' in data and 'scripts' in data['project']:
            # PEP 621 format
            data['project']['scripts'][command_name] = f"{package_name}.{cli_module_name}:cli_entry"
            typer.echo(f"✅ Updated PEP 621 entry point for '{command_name}'")
        else:
            # Create project.scripts section if it doesn't exist
            if 'project' not in data:
                data['project'] = {}
            if 'scripts' not in data['project']:
                data['project']['scripts'] = {}
            data['project']['scripts'][command_name] = f"{package_name}.{cli_module_name}:cli_entry"
            typer.echo(f"✅ Created entry point for '{command_name}'")
        
        # Add package-data configuration for setup.sh
        if 'project' in data:  # PEP 621 format
            if 'tool' not in data:
                data['tool'] = {}
            if 'setuptools' not in data['tool']:
                data['tool']['setuptools'] = {}
            if 'package-data' not in data['tool']['setuptools']:
                data['tool']['setuptools']['package-data'] = {}
            
            # Add setup.sh to package-data
            if package_name not in data['tool']['setuptools']['package-data']:
                data['tool']['setuptools']['package-data'][package_name] = ["setup.sh"]
                typer.echo(f"✅ Added setup.sh to package-data for '{package_name}'")
            else:
                existing = data['tool']['setuptools']['package-data'][package_name]
                if isinstance(existing, list) and "setup.sh" not in existing:
                    existing.append("setup.sh")
                    typer.echo(f"✅ Added setup.sh to existing package-data for '{package_name}'")
                elif isinstance(existing, str) and existing != "setup.sh":
                    # Convert single string to list and add setup.sh
                    data['tool']['setuptools']['package-data'][package_name] = [existing, "setup.sh"]
                    typer.echo(f"✅ Added setup.sh to existing package-data for '{package_name}'")
                elif "setup.sh" in existing or existing == "setup.sh":
                    typer.echo(f"ℹ️  setup.sh already in package-data for '{package_name}'")
        
        elif 'tool' in data and 'poetry' in data['tool']:
            # Poetry format - handle includes differently
            if 'packages' not in data['tool']['poetry']:
                data['tool']['poetry']['packages'] = []
            
            # Poetry uses include for additional files
            if 'include' not in data['tool']['poetry']:
                data['tool']['poetry']['include'] = []
            
            # Add setup.sh to includes if not already present
            setup_include = {"path": "setup.sh", "format": "sdist"}
            if setup_include not in data['tool']['poetry']['include']:
                data['tool']['poetry']['include'].append(setup_include)
                typer.echo(f"✅ Added setup.sh to Poetry includes for '{package_name}'")
            else:
                typer.echo(f"ℹ️  setup.sh already in Poetry includes for '{package_name}'")
        
        # Write back the modified pyproject.toml
        with open(pyproject_path, 'w') as f:
            toml.dump(data, f)
        
        return True
        
    except Exception as e:
        typer.echo(f"❌ Error updating pyproject.toml: {e}", err=True)
        return False


@app.command()
def build(
    config_path: Optional[Path] = typer.Argument(
        None,
        help="Path to goobits.yaml file (defaults to ./goobits.yaml)"
    ),
    output_dir: Optional[Path] = typer.Option(
        None,
        "--output-dir", "-o",
        help="Output directory (defaults to same directory as config file)"
    ),
    output: Optional[str] = typer.Option(
        None,
        "--output",
        help="Output filename for generated CLI (defaults to 'generated_cli.py')"
    ),
    backup: bool = typer.Option(
        False,
        "--backup",
        help="Create backup files (.bak) when overwriting existing files"
    ),
    universal_templates: bool = typer.Option(
        False,
        "--universal-templates",
        help="Use Universal Template System (experimental)"
    )
):
    """
    Build CLI and setup scripts from goobits.yaml configuration.
    
    This command reads a goobits.yaml file and generates:
    - CLI script: Generated from goobits.yaml (default: generated_cli.py)
    - setup.sh: Project setup script
    
    Use --output to specify a custom CLI filename (e.g., --output cli.py)
    """
    # Determine config file path
    if config_path is None:
        config_path = Path.cwd() / "goobits.yaml"
    
    config_path = Path(config_path).resolve()
    
    if not config_path.exists():
        typer.echo(f"Error: Configuration file '{config_path}' not found.", err=True)
        raise typer.Exit(1)
    
    # Determine output directory
    if output_dir is None:
        output_dir = config_path.parent
    else:
        output_dir = Path(output_dir).resolve()
    
    # Ensure output directory exists
    output_dir.mkdir(parents=True, exist_ok=True)
    
    typer.echo(f"Loading configuration from: {config_path}")
    
    # Show backup status
    if not backup:
        typer.echo("💡 Backups disabled (use --backup to create .bak files)")
        typer.echo("💡 Ensure your changes are committed to git before proceeding")
    
    # Show universal templates status
    if universal_templates:
        typer.echo("🧪 Using Universal Template System (experimental)")
    else:
        typer.echo("📝 Using legacy template system")
    
    # Load goobits configuration
    goobits_config = load_goobits_config(config_path)
    
    # Detect language from configuration
    language = goobits_config.language
    typer.echo(f"Detected language: {language}")
    
    typer.echo("Generating CLI script...")
    
    # Generate cli.py if CLI configuration exists
    if goobits_config.cli:
        # Extract version from pyproject.toml if available
        pyproject_path = output_dir / "pyproject.toml"
        version = None
        if pyproject_path.exists():
            version = extract_version_from_pyproject(output_dir)
        
        # Route to different generators based on language
        if language == "nodejs":
            from goobits_cli.generators.nodejs import NodeJSGenerator
            generator = NodeJSGenerator(use_universal_templates=universal_templates)
            
            # Node.js generates multiple files
            all_files = generator.generate_all_files(goobits_config, config_path.name, version)
        elif language == "typescript":
            from goobits_cli.generators.typescript import TypeScriptGenerator
            generator = TypeScriptGenerator(use_universal_templates=universal_templates)
            
            # TypeScript generates multiple files
            all_files = generator.generate_all_files(goobits_config, config_path.name, version)
        else:
            # Use Python generator (default)
            from goobits_cli.generators.python import PythonGenerator  
            generator = PythonGenerator(use_universal_templates=universal_templates)
            
            # Python now also generates multiple files
            all_files = generator.generate_all_files(goobits_config, config_path.name, version)
        
        # Handle multi-file generation for all languages
        if language in ["python", "nodejs", "typescript"]:
            # Write all generated files
            executable_files = all_files.pop('__executable__', [])
            for file_path, content in all_files.items():
                full_path = output_dir / file_path
                
                # Ensure parent directories exist
                full_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Backup existing file if requested
                backup_path = backup_file(full_path, backup)
                if backup_path:
                    typer.echo(f"📋 Backed up existing file: {backup_path}")
                
                # Write file
                with open(full_path, 'w') as f:
                    f.write(content)
                
                # Make files executable as needed
                if file_path.startswith('bin/') or file_path in executable_files or file_path == 'setup.sh':
                    full_path.chmod(0o755)
                
                typer.echo(f"✅ Generated: {full_path}")
            
            # All languages now use multi-file generation
        
        
        # Extract package name and filename for pyproject.toml update (Python only)
        if language == "python":
            # Use configured output path for Python
            cli_output_path = goobits_config.cli_output_path.format(
                package_name=goobits_config.package_name.replace('goobits-', '')
            )
            
            # Extract the actual module name from the CLI output path
            # e.g., "src/ttt/cli.py" -> "ttt"
            cli_path_parts = Path(cli_output_path).parts
            if 'src' in cli_path_parts:
                src_index = cli_path_parts.index('src')
                if src_index + 1 < len(cli_path_parts):
                    module_name = cli_path_parts[src_index + 1]
                else:
                    # Fallback to package name conversion
                    module_name = goobits_config.package_name.replace('-', '_')
            else:
                # Fallback to package name conversion
                module_name = goobits_config.package_name.replace('-', '_')
        
            # Extract the full module path relative to the package root
            cli_path_obj = Path(cli_output_path)
            cli_path_parts = cli_path_obj.parts
            
            # Find the path relative to the package directory
            if 'src' in cli_path_parts:
                src_index = cli_path_parts.index('src')
                if src_index + 2 < len(cli_path_parts):  # src/package/...
                    # Get all parts after src/package/ up to filename
                    relative_parts = cli_path_parts[src_index + 2:]  # Everything after src/package/
                    # Join directory parts with dots, then add filename without .py
                    if len(relative_parts) > 1:
                        dir_parts = relative_parts[:-1]  # All but filename
                        filename_part = relative_parts[-1].replace('.py', '')
                        full_module_path = '.'.join(dir_parts) + '.' + filename_part
                    else:
                        # Just a filename
                        full_module_path = relative_parts[0].replace('.py', '')
                else:
                    # Fallback to just filename
                    full_module_path = cli_path_obj.name.replace('.py', '')
            else:
                # Fallback to just filename  
                full_module_path = cli_path_obj.name.replace('.py', '')
            
            # Update pyproject.toml to use the generated CLI
            if update_pyproject_toml(output_dir, module_name, goobits_config.command_name, full_module_path + '.py', backup):
                typer.echo(f"✅ Updated {output_dir}/pyproject.toml to use generated CLI")
                typer.echo("\n💡 Remember to reinstall the package for changes to take effect:")
                typer.echo("   ./setup.sh install --dev")
            else:
                typer.echo("⚠️  Could not update pyproject.toml automatically")
                typer.echo(f"   Please update your entry points to use: {module_name}.{full_module_path}:cli_entry")
    else:
        typer.echo("⚠️  No CLI configuration found, skipping cli.py generation")
    
    # Generate setup.sh (Python only - Node.js generates its own)
    if language == "python":
        typer.echo("Generating setup script...")
        # Normalize dependencies for backward compatibility
        normalized_config = normalize_dependencies_for_template(goobits_config)
        setup_script = generate_setup_script(normalized_config, output_dir)
        
        setup_output_path = output_dir / "setup.sh"
        with open(setup_output_path, 'w') as f:
            f.write(setup_script)
        
        # Make setup.sh executable
        setup_output_path.chmod(0o755)
        
        typer.echo(f"✅ Generated setup script: {setup_output_path}")
    
    # Copy setup.sh to package source directory for package-data inclusion (Python only)
    if language == "python" and goobits_config.cli:  # Only copy if CLI is configured
        # Find the package source directory
        cli_output_path = goobits_config.cli_output_path.format(
            package_name=goobits_config.package_name.replace('goobits-', '')
        )
        cli_path_parts = Path(cli_output_path).parts
        
        # Determine package source directory
        package_src_dir = None
        if 'src' in cli_path_parts:
            src_index = cli_path_parts.index('src')
            if src_index + 1 < len(cli_path_parts):
                package_src_dir = output_dir / "src" / cli_path_parts[src_index + 1]
        
        if package_src_dir and package_src_dir.exists():
            # Copy setup.sh to package source directory
            package_setup_path = package_src_dir / "setup.sh"
            try:
                shutil.copy2(setup_output_path, package_setup_path)
                typer.echo(f"✅ Copied setup.sh to package directory: {package_setup_path}")
            except Exception as e:
                typer.echo(f"⚠️  Could not copy setup.sh to package directory: {e}")
        else:
            typer.echo("ℹ️  Package source directory not found, setup.sh not copied to package")
    
    typer.echo("🎉 Build completed successfully!")


@app.command()
def init(
    project_name: Optional[str] = typer.Argument(None, help="Name of the project (optional)"),
    template: str = typer.Option("basic", "--template", "-t", help="Template type (basic, advanced, api-client, text-processor)"),
    force: bool = typer.Option(False, "--force", help="Overwrite existing goobits.yaml file")
):
    """
    Create initial goobits.yaml template.
    
    This command generates a starter goobits.yaml configuration file
    to help you get started with building your CLI application.
    
    Templates:
        basic: Simple CLI with one command
        advanced: Multi-command CLI with options and subcommands
        api-client: Template for API client tools
        text-processor: Template for text processing utilities
    
    Examples:
        goobits init my-awesome-tool
        goobits init --template advanced
        goobits init my-api-client --template api-client
    """
    config_path = Path("./goobits.yaml")
    
    if config_path.exists() and not force:
        typer.echo(f"Error: {config_path} already exists. Use --force to overwrite.", err=True)
        raise typer.Exit(1)
    
    # Determine project name
    if not project_name:
        project_name = Path.cwd().name
    
    # Generate template based on type
    templates = {
        "basic": generate_basic_template(project_name),
        "advanced": generate_advanced_template(project_name),
        "api-client": generate_api_client_template(project_name),
        "text-processor": generate_text_processor_template(project_name)
    }
    
    if template not in templates:
        typer.echo(f"Error: Unknown template '{template}'. Available: {', '.join(templates.keys())}", err=True)
        raise typer.Exit(1)
    
    # Write template
    with open(config_path, 'w') as f:
        f.write(templates[template])
    
    typer.echo(f"✅ Created {config_path} using '{template}' template")
    typer.echo(f"📝 Project: {project_name}")
    typer.echo("")
    typer.echo("Next steps:")
    typer.echo("  1. Edit goobits.yaml to customize your CLI")
    typer.echo("  2. Run: goobits build")
    typer.echo("  3. Run: ./setup.sh install --dev")


def generate_basic_template(project_name: str) -> str:
    return f'''# Basic Goobits CLI Configuration
package_name: {project_name}
command_name: {project_name.replace('-', '_')}
display_name: "{project_name.replace('-', ' ').title()}"
description: "A CLI tool built with Goobits"

# Language selection (python, nodejs, or typescript)
language: python

python:
  minimum_version: "3.8"

dependencies:
  required:
    - pipx

cli:
  name: {project_name.replace('-', '_')}
  tagline: "Your awesome CLI tool"
  commands:
    hello:
      desc: "Say hello"
      is_default: true
      args:
        - name: name
          desc: "Name to greet"
          required: false
      options:
        - name: greeting
          short: g
          desc: "Custom greeting"
          default: "Hello"
'''

def generate_advanced_template(project_name: str) -> str:
    return f'''# Advanced Goobits CLI Configuration
package_name: {project_name}
command_name: {project_name.replace('-', '_')}
display_name: "{project_name.replace('-', ' ').title()}"
description: "An advanced CLI tool built with Goobits"

# Language selection (python, nodejs, or typescript)
language: python

python:
  minimum_version: "3.8"

dependencies:
  required:
    - pipx
    - git
  optional:
    - curl

cli:
  name: {project_name.replace('-', '_')}
  tagline: "Advanced CLI with multiple commands"
  command_groups:
    - name: "Core Commands"
      commands: ["process", "convert"]
    - name: "Utilities"
      commands: ["status", "config"]
  
  commands:
    process:
      desc: "Process input data"
      is_default: true
      args:
        - name: input
          desc: "Input to process"
          nargs: "*"
      options:
        - name: output
          short: o
          desc: "Output file"
        - name: format
          short: f
          choices: ["json", "yaml", "text"]
          default: "text"
    
    convert:
      desc: "Convert between formats"
      args:
        - name: source
          desc: "Source file"
          required: true
      options:
        - name: target
          short: t
          desc: "Target format"
          required: true
    
    status:
      desc: "Show system status"
    
    config:
      desc: "Manage configuration"
      subcommands:
        show:
          desc: "Show current configuration"
        set:
          desc: "Set configuration value"
          args:
            - name: key
              desc: "Configuration key"
            - name: value
              desc: "Configuration value"
'''

def generate_api_client_template(project_name: str) -> str:
    return f'''# API Client Goobits CLI Configuration
package_name: {project_name}
command_name: {project_name.replace('-', '_')}
display_name: "{project_name.replace('-', ' ').title()}"
description: "API client CLI tool built with Goobits"

# Language selection (python, nodejs, or typescript)
language: python

python:
  minimum_version: "3.8"

dependencies:
  required:
    - pipx
    - curl
  optional:
    - jq

cli:
  name: {project_name.replace('-', '_')}
  tagline: "API client for your service"
  commands:
    get:
      desc: "GET request to API endpoint"
      is_default: true
      args:
        - name: endpoint
          desc: "API endpoint path"
          required: true
      options:
        - name: api-key
          desc: "API key for authentication"
        - name: format
          short: f
          choices: ["json", "yaml", "table"]
          default: "json"
        - name: output
          short: o
          desc: "Save output to file"
    
    post:
      desc: "POST request to API endpoint"
      args:
        - name: endpoint
          desc: "API endpoint path"
          required: true
      options:
        - name: data
          short: d
          desc: "JSON data to send"
        - name: file
          desc: "Read data from file"
        - name: api-key
          desc: "API key for authentication"
    
    config:
      desc: "Manage API configuration"
      subcommands:
        set-key:
          desc: "Set API key"
          args:
            - name: key
              desc: "API key value"
        show:
          desc: "Show current configuration"
'''

def generate_text_processor_template(project_name: str) -> str:
    return f'''# Text Processor Goobits CLI Configuration
package_name: {project_name}
command_name: {project_name.replace('-', '_')}
display_name: "{project_name.replace('-', ' ').title()}"
description: "Text processing CLI tool built with Goobits"

# Language selection (python, nodejs, or typescript)
language: python

python:
  minimum_version: "3.8"

dependencies:
  required:
    - pipx
  optional:
    - pandoc

cli:
  name: {project_name.replace('-', '_')}
  tagline: "Process text files with ease"
  commands:
    process:
      desc: "Process text input"
      is_default: true
      args:
        - name: text
          desc: "Text to process (or read from stdin)"
          nargs: "*"
      options:
        - name: uppercase
          short: u
          type: flag
          desc: "Convert to uppercase"
        - name: lowercase
          short: l
          type: flag
          desc: "Convert to lowercase"
        - name: output
          short: o
          desc: "Output file"
        - name: format
          short: f
          choices: ["text", "json", "markdown"]
          default: "text"
    
    count:
      desc: "Count words, lines, characters"
      args:
        - name: files
          desc: "Files to count"
          nargs: "*"
      options:
        - name: words
          short: w
          type: flag
          desc: "Count words"
        - name: lines
          short: l
          type: flag
          desc: "Count lines"
        - name: chars
          short: c
          type: flag
          desc: "Count characters"
'''

@app.command()
def serve(
    directory: Path = typer.Argument(..., help="Directory containing packages to serve."),
    host: str = typer.Option("localhost", help="Host to bind the server to."),
    port: int = typer.Option(8080, help="Port to run the server on.")
):
    """
    Serve a local PyPI-compatible package index.
    
    This command starts a simple HTTP server that serves Python packages
    (.whl and .tar.gz files) in a PyPI-compatible format. This is useful
    for testing package dependencies in Docker environments.
    
    The server will automatically generate an index.html file listing all
    available packages and serve them at the specified host and port.
    
    Examples:
        goobits serve ./packages
        goobits serve /path/to/packages --host 0.0.0.0 --port 9000
    """
    directory = Path(directory).resolve()
    
    if not directory.exists():
        typer.echo(f"Error: Directory '{directory}' does not exist.", err=True)
        raise typer.Exit(1)
    
    if not directory.is_dir():
        typer.echo(f"Error: '{directory}' is not a directory.", err=True)
        raise typer.Exit(1)
    
    typer.echo(f"Starting PyPI server at http://{host}:{port}")
    typer.echo(f"Serving packages from: {directory}")
    typer.echo()
    typer.echo("Press Ctrl+C to stop the server")
    typer.echo()
    
    try:
        serve_packages(directory, host, port)
    except KeyboardInterrupt:
        typer.echo("\n👋 Server stopped by user")
    except OSError as e:
        if e.errno == 48:  # Address already in use
            typer.echo(f"❌ Error: Port {port} is already in use. Try a different port with --port.", err=True)
        else:
            typer.echo(f"❌ Error starting server: {e}", err=True)
        raise typer.Exit(1)
    except Exception as e:
        typer.echo(f"❌ Unexpected error: {e}", err=True)
        raise typer.Exit(1)


@app.command()
def upgrade(
    source: str = typer.Option("pypi", help="Upgrade source: pypi, git, local"),
    version: Optional[str] = typer.Option(None, help="Specific version to install"),
    pre_release: bool = typer.Option(False, "--pre", help="Include pre-release versions"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show what would be upgraded without doing it")
):
    """
    Upgrade goobits-cli to the latest version.
    
    This command uses pipx to safely upgrade goobits-cli in its isolated environment.
    Multiple upgrade sources are supported for flexibility.
    
    Sources:
        pypi: Upgrade from PyPI (default)
        git: Upgrade from GitHub repository
        local: Upgrade from current directory (for development)
    
    Examples:
        goobits upgrade                    # Upgrade from PyPI
        goobits upgrade --version 1.2.0    # Upgrade to specific version
        goobits upgrade --source git       # Upgrade from latest git
        goobits upgrade --dry-run          # See what would be upgraded
    """
    # Check if pipx is available
    try:
        result = subprocess.run(["pipx", "--version"], capture_output=True, text=True, check=True)
        typer.echo(f"Using pipx version: {result.stdout.strip()}")
    except (subprocess.CalledProcessError, FileNotFoundError):
        typer.echo("❌ Error: pipx is required for upgrades but not found.", err=True)
        typer.echo("Install pipx: https://pypa.github.io/pipx/installation/", err=True)
        raise typer.Exit(1)
    
    # Get current version
    current_version = __version__
    typer.echo(f"Current version: {current_version}")
    
    # Build upgrade command based on source
    if source == "pypi":
        if version:
            cmd = ["pipx", "install", f"goobits-cli=={version}", "--force"]
            target_desc = f"version {version} from PyPI"
        else:
            cmd = ["pipx", "upgrade", "goobits-cli"]
            if pre_release:
                cmd.extend(["--pip-args", "--pre"])
            target_desc = "latest version from PyPI"
    elif source == "git":
        git_url = "git+https://github.com/goobits/goobits-cli.git"
        if version:
            git_url += f"@{version}"
        cmd = ["pipx", "install", git_url, "--force"]
        target_desc = f"version {version if version else 'latest'} from Git"
    elif source == "local":
        cmd = ["pipx", "install", ".", "--force", "--editable"]
        target_desc = "local development version"
    else:
        typer.echo(f"❌ Error: Unknown source '{source}'. Use: pypi, git, local", err=True)
        raise typer.Exit(1)
    
    typer.echo(f"Planning to upgrade to: {target_desc}")
    
    if dry_run:
        typer.echo(f"Dry run - would execute: {' '.join(cmd)}")
        return
    
    # Confirm upgrade
    if not typer.confirm(f"Upgrade goobits-cli to {target_desc}?"):
        typer.echo("Upgrade cancelled.")
        return
    
    # Execute upgrade
    typer.echo("🔄 Upgrading goobits-cli...")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        # Show success message
        typer.echo("✅ Upgrade completed successfully!")
        
        # Try to get new version
        try:
            version_result = subprocess.run(["goobits", "--version"], capture_output=True, text=True, check=True)
            new_version = version_result.stdout.strip().split()[-1]
            if new_version != current_version:
                typer.echo(f"📈 Upgraded from {current_version} → {new_version}")
            else:
                typer.echo(f"Already at latest version: {current_version}")
        except Exception:
            typer.echo("New version information not available")
        
        if result.stdout:
            typer.echo("\nInstall output:")
            typer.echo(result.stdout)
            
    except subprocess.CalledProcessError as e:
        typer.echo(f"❌ Upgrade failed: {e}", err=True)
        if e.stderr:
            typer.echo(f"Error details: {e.stderr}", err=True)
        
        # Suggest troubleshooting
        typer.echo("\n💡 Troubleshooting:")
        typer.echo("- Ensure pipx is up to date: pipx upgrade pipx")
        typer.echo("- Check network connection for PyPI/Git access")
        typer.echo("- Try: pipx reinstall goobits-cli")
        
        raise typer.Exit(1)
    except Exception as e:
        typer.echo(f"❌ Unexpected error during upgrade: {e}", err=True)
        raise typer.Exit(1)


if __name__ == "__main__":
    app()