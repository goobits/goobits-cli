#!/usr/bin/env python3
import sys
import yaml
import toml
import shutil
from pathlib import Path
from typing import Optional, Dict, Any
import typer
from jinja2 import Environment, FileSystemLoader
from pydantic import ValidationError

from .schemas import ConfigSchema, GoobitsConfigSchema
from .builder import generate_cli_code
from .pypi_server import serve_packages

app = typer.Typer(name="goobits", help="Unified CLI for Goobits projects")


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


def generate_setup_script(config: GoobitsConfigSchema) -> str:
    """Generate setup.sh script from goobits configuration."""
    template_dir = Path(__file__).parent / "templates"
    env = Environment(loader=FileSystemLoader(template_dir))
    
    template = env.get_template("setup_template.sh.j2")
    
    # Convert goobits config to template variables
    template_vars = {
        'package_name': config.package_name,
        'command_name': config.command_name,
        'display_name': config.display_name,
        'description': config.description,
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
        'cache_ttl': 3600,  # Default cache TTL
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


def update_pyproject_toml(project_dir: Path, package_name: str, command_name: str, create_backup: bool = False) -> bool:
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
        if 'tool' in data and 'poetry' in data['tool'] and 'scripts' in data['tool']['poetry']:
            # Poetry format
            data['tool']['poetry']['scripts'][command_name] = f"{package_name}.generated_cli:cli_entry"
            typer.echo(f"✅ Updated Poetry entry point for '{command_name}'")
        elif 'project' in data and 'scripts' in data['project']:
            # PEP 621 format
            data['project']['scripts'][command_name] = f"{package_name}.generated_cli:cli_entry"
            typer.echo(f"✅ Updated PEP 621 entry point for '{command_name}'")
        else:
            # Create project.scripts section if it doesn't exist
            if 'project' not in data:
                data['project'] = {}
            if 'scripts' not in data['project']:
                data['project']['scripts'] = {}
            data['project']['scripts'][command_name] = f"{package_name}.generated_cli:cli_entry"
            typer.echo(f"✅ Created entry point for '{command_name}'")
        
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
    backup: bool = typer.Option(
        False,
        "--backup",
        help="Create backup files (.bak) when overwriting existing files"
    )
):
    """
    Build CLI and setup scripts from goobits.yaml configuration.
    
    This command reads a goobits.yaml file and generates:
    - cli.py: Project-specific CLI script
    - setup.sh: Project setup script
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
    
    # Load goobits configuration
    goobits_config = load_goobits_config(config_path)
    
    typer.echo("Generating CLI script...")
    
    # Generate cli.py if CLI configuration exists
    if goobits_config.cli:
        # Find the main package directory
        # Look for a directory with the same name as package_name (without 'goobits-' prefix)
        package_dir_name = goobits_config.package_name.replace('goobits-', '')
        
        # Try common locations
        possible_locations = [
            output_dir / package_dir_name,  # Direct package directory
            output_dir / 'src' / package_dir_name,  # src layout
            output_dir / 'lib' / package_dir_name,  # lib layout
        ]
        
        package_dir = None
        for location in possible_locations:
            if location.exists() and (location / '__init__.py').exists():
                package_dir = location
                break
        
        if not package_dir:
            # Try to find any Python package directory (but skip tests)
            for item in output_dir.iterdir():
                if item.is_dir() and item.name not in ['tests', 'test', '__pycache__', '.git', 'venv', '.venv']:
                    if (item / '__init__.py').exists():
                        package_dir = item
                        break
                    # Check src layout
                    for subitem in item.iterdir():
                        if subitem.is_dir() and (subitem / '__init__.py').exists() and subitem.name not in ['tests', 'test']:
                            package_dir = subitem
                            break
                    if package_dir:
                        break
        
        if not package_dir:
            typer.echo(f"❌ Could not find package directory. Expected: {package_dir_name}", err=True)
            raise typer.Exit(1)
        
        # Convert goobits config to legacy CLI schema format for compatibility
        legacy_config = ConfigSchema(cli=goobits_config.cli)
        cli_code = generate_cli_code(legacy_config, config_path.name)
        
        # Write to generated_cli.py inside the package directory
        cli_output_path = package_dir / "generated_cli.py"
        with open(cli_output_path, 'w') as f:
            f.write(cli_code)
        
        typer.echo(f"✅ Generated CLI script: {cli_output_path}")
        
        # Backup the original CLI file if it exists and backup is requested
        original_cli = package_dir / "cli.py"
        if original_cli.exists():
            backup_path = backup_file(original_cli, backup)
            if backup_path:
                typer.echo(f"📋 Backed up original CLI: {backup_path}")
        
        # Update pyproject.toml to use the generated CLI
        if update_pyproject_toml(output_dir, package_dir_name, goobits_config.command_name, backup):
            typer.echo("✅ Updated pyproject.toml to use generated CLI")
            typer.echo("\n💡 Remember to reinstall the package for changes to take effect:")
            typer.echo(f"   ./setup.sh install --dev")
        else:
            typer.echo("⚠️  Could not update pyproject.toml automatically")
            typer.echo(f"   Please update your entry points to use: {package_dir_name}.generated_cli:cli_entry")
    else:
        typer.echo("⚠️  No CLI configuration found, skipping cli.py generation")
    
    # Generate setup.sh
    typer.echo("Generating setup script...")
    setup_script = generate_setup_script(goobits_config)
    
    setup_output_path = output_dir / "setup.sh"
    with open(setup_output_path, 'w') as f:
        f.write(setup_script)
    
    # Make setup.sh executable
    setup_output_path.chmod(0o755)
    
    typer.echo(f"✅ Generated setup script: {setup_output_path}")
    typer.echo(f"🎉 Build completed successfully!")


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


if __name__ == "__main__":
    app()