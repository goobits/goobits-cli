#!/usr/bin/env python3


# Now import heavy dependencies only if needed

import json

import shutil

import subprocess

# Use cached subprocess for better performance
from .universal.performance.subprocess_cache import run_cached

from pathlib import Path

from typing import Optional

import typer

# Import centralized logging
from .logger import setup_logging, get_logger, set_context, clear_context

# Shared lazy imports
from .shared.lazy_imports import (
    lazy_import_jinja2_environment,
    lazy_import_jinja2_filesystem_loader,
    lazy_import_yaml,
    lazy_import_toml,
    lazy_import_pydantic_validation_error,
    lazy_import_deepcopy,
)

# Main-specific lazy imports
GoobitsConfigSchema = None
serve_packages = None


def _lazy_imports():
    """Load heavy dependencies only when needed."""
    # Use shared lazy import utilities
    global yaml, toml, Environment, FileSystemLoader, ValidationError, deepcopy
    global GoobitsConfigSchema, serve_packages
    
    yaml = lazy_import_yaml()
    toml = lazy_import_toml()
    Environment = lazy_import_jinja2_environment()
    FileSystemLoader = lazy_import_jinja2_filesystem_loader()
    ValidationError = lazy_import_pydantic_validation_error()
    deepcopy = lazy_import_deepcopy()
    
    # Main-specific imports
    if GoobitsConfigSchema is None:
        from .schemas import GoobitsConfigSchema as _GoobitsConfigSchema
        GoobitsConfigSchema = _GoobitsConfigSchema
    
    if serve_packages is None:
        from .pypi_server import serve_packages as _serve_packages
        serve_packages = _serve_packages


from .__version__ import __version__  # noqa: E402


# Default cache time-to-live in seconds (1 hour)

DEFAULT_CACHE_TTL = 3600


def version_callback(value: bool):

    if value:

        typer.echo(f"goobits-cli {__version__}")

        raise typer.Exit()


def generate_help_from_yaml() -> tuple[str, str]:
    """Generate help text and version from goobits.yaml configuration."""
    try:
        # Try to load the self-hosting goobits.yaml
        goobits_yaml_path = Path.cwd() / "goobits.yaml"
        if not goobits_yaml_path.exists():
            # Fallback to default help if no goobits.yaml found
            return "Build professional command-line tools with YAML configuration", __version__
        
        config = load_goobits_config(goobits_yaml_path)
        
        # Extract help components
        cli_config = config.cli if config.cli else None
        if not cli_config:
            return config.description or "Build professional command-line tools with YAML configuration", __version__
        
        # Start with tagline/description
        help_parts = []
        if cli_config.tagline:
            help_parts.append(cli_config.tagline)
        elif cli_config.description:
            help_parts.append(cli_config.description)
        else:
            help_parts.append("Build professional command-line tools with YAML configuration")
        
        # Add header sections if available
        if cli_config.header_sections:
            help_parts.append("")  # Empty line before sections
            
            for section in cli_config.header_sections:
                # Process colors in section title
                section_title = process_yaml_colors(section.title)
                help_parts.append(section_title)
                
                # Add section items
                for item in section.items:
                    item_desc = process_yaml_colors(item.desc)
                    help_parts.append(f"   {item.item} - {item_desc}")
                
                help_parts.append("")  # Empty line after each section
        
        # Add footer note if available
        if cli_config.footer_note:
            help_parts.append(process_yaml_colors(cli_config.footer_note))
        
        # Get version from YAML config or fallback to package version
        version = cli_config.version if cli_config.version else __version__
        
        return "\n".join(help_parts).rstrip(), version
        
    except Exception:
        # If anything fails, use fallback help
        return "Build professional command-line tools with YAML configuration", __version__


def generate_plain_help_from_yaml() -> str:
    """Generate plain text help for Typer (no Rich markup)."""
    try:
        # Try to load the self-hosting goobits.yaml
        goobits_yaml_path = Path.cwd() / "goobits.yaml"
        if not goobits_yaml_path.exists():
            # Fallback to default help if no goobits.yaml found
            return "Build professional command-line tools with YAML configuration"
        
        config = load_goobits_config(goobits_yaml_path)
        
        # Extract help components
        cli_config = config.cli if config.cli else None
        if not cli_config:
            return config.description or "Build professional command-line tools with YAML configuration"
        
        # Start with tagline/description (plain text)
        help_parts = []
        if cli_config.tagline:
            help_parts.append(cli_config.tagline)
        elif cli_config.description:
            help_parts.append(cli_config.description)
        else:
            help_parts.append("Build professional command-line tools with YAML configuration")
        
        # Add header sections if available (plain text)
        if cli_config.header_sections:
            help_parts.append("")  # Empty line before sections
            
            for section in cli_config.header_sections:
                # Plain text section title (remove Rich markup)
                section_title = section.title
                import re
                section_title = re.sub(r'\[[^]]*\]([^[]*)\[/[^]]*\]', r'\1', section_title)
                section_title = re.sub(r'\[#[0-9a-fA-F]{6}\]([^[]*)\[/#[0-9a-fA-F]{6}\]', r'\1', section_title)
                help_parts.append(section_title)
                
                # Add section items (plain text)
                for item in section.items:
                    item_text = item.item
                    item_text = re.sub(r'\[[^]]*\]([^[]*)\[/[^]]*\]', r'\1', item_text)
                    item_text = re.sub(r'\[#[0-9a-fA-F]{6}\]([^[]*)\[/#[0-9a-fA-F]{6}\]', r'\1', item_text)
                    help_parts.append(f"   {item_text} - {item.desc}")
                
                help_parts.append("")  # Empty line after each section
        
        # Add footer note if available (plain text)
        if cli_config.footer_note:
            footer_text = cli_config.footer_note
            import re
            footer_text = re.sub(r'\[[^]]*\]([^[]*)\[/[^]]*\]', r'\1', footer_text)
            footer_text = re.sub(r'\[#[0-9a-fA-F]{6}\]([^[]*)\[/#[0-9a-fA-F]{6}\]', r'\1', footer_text)
            help_parts.append(footer_text)
        
        return "\n".join(help_parts).rstrip()
        
    except Exception:
        # If anything fails, use fallback help
        return "Build professional command-line tools with YAML configuration"


def process_yaml_colors(text: str) -> str:
    """Process YAML color syntax for terminal display using Rich markup."""
    if not text:
        return text
    
    import re
    
    # Convert hex colors to rich markup
    # Dracula color palette
    dracula_colors = {
        '#f8f8f2': 'bright_white',    # Foreground (white)
        '#6272a4': 'white',           # Comment (lighter gray) 
        '#8be9fd': 'cyan',            # Cyan
        '#50fa7b': 'bright_green',    # Green
        '#ffb86c': 'orange',          # Orange
        '#ff79c6': 'magenta',         # Pink
        '#bd93f9': 'bright_magenta',  # Purple
        '#ff5555': 'bright_red',      # Red
        '#f1fa8c': 'yellow',          # Yellow
    }
    
    # Process hex color tags: [#ff79c6]text[/#ff79c6] -> [magenta]text[/magenta]
    def replace_hex_color(match):
        hex_color = '#' + match.group(1).lower()
        content = match.group(2)
        if hex_color in dracula_colors:
            rich_color = dracula_colors[hex_color]
            return f"[{rich_color}]{content}[/{rich_color}]"
        else:
            return content
    
    # Replace hex color tags with rich markup
    text = re.sub(r'\[#([0-9a-fA-F]{6})\]([^[\]]*)\[/#[0-9a-fA-F]{6}\]', replace_hex_color, text)
    
    # Process numbered color tags (legacy support)
    color_map = {
        '0': 'bright_white',    # White (foreground)
        '1': 'bright_red',      # Red
        '2': 'bright_green',    # Green 
        '3': 'yellow',          # Yellow
        '4': 'cyan',            # Cyan
        '5': 'bright_magenta',  # Purple
        '6': 'magenta',         # Pink
        '7': 'white',           # Comment (lighter gray)
    }
    
    def replace_numbered_color(match):
        color_num = match.group(1)
        content = match.group(2)
        if color_num in color_map:
            rich_color = color_map[color_num]
            return f"[{rich_color}]{content}[/{rich_color}]"
        else:
            return content
    
    # Replace numbered color tags: [color(2)]text[/color(2)] -> [bright_green]text[/bright_green]
    text = re.sub(r'\[color\((\d+)\)\]([^[\]]*)\[/color\(\d+\)\]', replace_numbered_color, text)
    
    return text


app = typer.Typer(
    name="goobits"
)


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        callback=version_callback,
        is_eager=True,
        help="Show version and exit",
    ),
    help: Optional[bool] = typer.Option(
        None,
        "--help",
        "-h",
        is_eager=True,
        help="Show help and exit",
    )
):
    # Get dynamic help text and version from YAML
    dynamic_help, yaml_version = generate_help_from_yaml()
    
    # This will be the help text for this callback
    ctx.info_name = "goobits"
    
    # Initialize centralized logging early
    setup_logging()

    # Set global context
    set_context(framework_version=__version__)

    # If --help is provided or no command is provided, show help with dynamic content
    if help or ctx.invoked_subcommand is None:
        from rich.console import Console
        from rich.markup import escape
        
        console = Console()
        
        # Create custom help with dynamic content and version
        # Disable highlighting to prevent version number fragmentation (3.0.2 splitting)
        console.print(f"Usage: {ctx.info_name} {yaml_version} [OPTIONS] COMMAND [ARGS]...", highlight=False)
        console.print()
        console.print(f" {dynamic_help}")
        console.print()
        
        # Show the standard options and commands from the app
        help_text = ctx.get_help()
        # Extract and show just the options and commands sections
        lines = help_text.split('\n')
        in_options_or_commands = False
        for line in lines:
            if '─ Options ─' in line or '─ Commands ─' in line:
                in_options_or_commands = True
            if in_options_or_commands:
                console.print(escape(line))
        raise typer.Exit()


def load_goobits_config(file_path: Path) -> "GoobitsConfigSchema":
    """Load and validate goobits.yaml configuration file."""
    _lazy_imports()

    try:

        with open(file_path, "r") as f:

            data = yaml.safe_load(f)

        config = GoobitsConfigSchema(**data)

        return config

    except FileNotFoundError:

        typer.echo(f"Error: File '{file_path}' not found.", err=True)

        raise typer.Exit(1)

    except yaml.YAMLError as e:
        # Extract line number and provide helpful context
        error_msg = str(e)
        if hasattr(e, "problem_mark"):
            mark = e.problem_mark
            error_msg = (
                f"\n❌ YAML Parsing Error at line {mark.line + 1}, column {mark.column + 1}:\n"
                f"   {e.problem}\n"
            )
            if e.context:
                error_msg += f"   Context: {e.context}\n"

            # Try to show the problematic line
            try:
                with open(file_path, "r") as f:
                    lines = f.readlines()
                    if 0 <= mark.line < len(lines):
                        error_msg += (
                            f"\n   Line {mark.line + 1}: {lines[mark.line].rstrip()}\n"
                        )
                        error_msg += "   " + " " * mark.column + "^\n"
            except (AttributeError, IndexError):
                # Ignore errors when trying to format YAML error details
                pass

            error_msg += "\n💡 Tip: Check that indentation is consistent (use 2 spaces, not tabs)"
        else:
            error_msg = f"\n❌ YAML Parsing Error: {e}\n"
            error_msg += "\n💡 Tip: Validate your YAML at https://yamlchecker.com/"

        typer.echo(error_msg, err=True)
        raise typer.Exit(1)

    except ValidationError as e:
        # Format validation errors more helpfully
        error_msg = "\n❌ Configuration Validation Errors:\n"

        for error in e.errors():
            field_path = ".".join(str(x) for x in error["loc"])
            error_type = error["type"]
            msg = error["msg"]

            error_msg += f"\n   • Field '{field_path}': {msg}\n"

            # Add helpful suggestions based on error type
            if "missing" in error_type:
                error_msg += "     💡 Add this required field to your configuration\n"
            elif "choice" in error_type or "enum" in error_type:
                if "ctx" in error and "enum_values" in error["ctx"]:
                    valid_values = error["ctx"]["enum_values"]
                    error_msg += (
                        f"     💡 Valid values: {', '.join(map(str, valid_values))}\n"
                    )
            elif "type" in error_type:
                error_msg += (
                    f"     💡 Expected type: {error_type.replace('type_error.', '')}\n"
                )

        error_msg += (
            "\n📖 See examples at: https://github.com/goobits/goobits-cli#quick-start\n"
        )

        typer.echo(error_msg, err=True)
        raise typer.Exit(1)


def normalize_dependencies_for_template(
    config: "GoobitsConfigSchema",
) -> "GoobitsConfigSchema":
    """Normalize dependencies for template rendering with enhanced data."""
    _lazy_imports()

    # Create a copy to avoid modifying the original

    normalized_config = deepcopy(config)

    # The DependenciesSchema validator already normalizes the dependencies,

    # so we just need to ensure they're properly formatted for the template

    return normalized_config


def dependency_to_dict(dep):
    """Convert DependencyItem to dict for JSON serialization."""

    if isinstance(dep, str):

        return {"name": dep, "type": "command"}

    elif hasattr(dep, "model_dump"):

        return dep.model_dump()

    elif hasattr(dep, "dict"):

        return dep.dict()

    elif isinstance(dep, dict):

        return dep

    else:

        return {"name": str(dep), "type": "command"}


def dependencies_to_json(deps):
    """Convert list of dependencies to JSON string."""

    return json.dumps([dependency_to_dict(dep) for dep in deps])


def extract_version_from_pyproject(project_dir: Path) -> str:
    """Extract version from pyproject.toml."""
    _lazy_imports()

    pyproject_path = project_dir / "pyproject.toml"

    if not pyproject_path.exists():

        return "unknown"

    try:

        with open(pyproject_path, "r") as f:

            data = toml.load(f)

        # Try different locations for version

        if (
            "tool" in data
            and "poetry" in data["tool"]
            and "version" in data["tool"]["poetry"]
        ):

            return data["tool"]["poetry"]["version"]

        elif "project" in data and "version" in data["project"]:

            return data["project"]["version"]

        else:

            return "unknown"

    except Exception:

        return "unknown"


def generate_setup_script(config: "GoobitsConfigSchema", project_dir: Path) -> str:
    """Generate setup.sh script from goobits configuration."""
    _lazy_imports()

    template_dir = Path(__file__).parent / "templates"

    env = Environment(
        loader=FileSystemLoader(template_dir), trim_blocks=True, lstrip_blocks=True
    )

    # Add custom filters

    env.filters["dependency_to_dict"] = dependency_to_dict

    env.filters["dependencies_to_json"] = dependencies_to_json

    template = env.get_template("setup_template.sh.j2")

    # Extract version from pyproject.toml

    version = extract_version_from_pyproject(project_dir)

    # Convert goobits config to template variables

    template_vars = {
        "package_name": config.package_name,
        "command_name": config.command_name,
        "display_name": config.display_name,
        "description": config.description,
        "version": version,
        "python": {
            "minimum_version": config.python.minimum_version,
            "maximum_version": config.python.maximum_version,
        },
        "dependencies": {
            "required": config.dependencies.required,
            "optional": config.dependencies.optional,
        },
        "installation": {
            "pypi_name": (
                config.installation.pypi_name
                if hasattr(config, "installation") and config.installation
                else config.package_name
            ),
            "development_path": (
                config.installation.development_path
                if hasattr(config, "installation") and config.installation
                else "."
            ),
            "extras": (
                config.installation.extras
                if hasattr(config, "installation") and config.installation
                else {}
            ),
        },
        "shell_integration": {
            "enabled": (
                config.shell_integration.enabled
                if hasattr(config, "shell_integration")
                and config.shell_integration
                and hasattr(config.shell_integration, "enabled")
                else False
            ),
            "alias": (
                config.shell_integration.alias
                if hasattr(config, "shell_integration")
                and config.shell_integration
                and hasattr(config.shell_integration, "alias")
                else config.command_name
            ),
        },
        "validation": {
            "check_api_keys": (
                config.validation.check_api_keys
                if hasattr(config, "validation")
                and config.validation
                and hasattr(config.validation, "check_api_keys")
                else False
            ),
            "check_disk_space": (
                config.validation.check_disk_space
                if hasattr(config, "validation")
                and config.validation
                and hasattr(config.validation, "check_disk_space")
                else True
            ),
            "minimum_disk_space_mb": (
                config.validation.minimum_disk_space_mb
                if hasattr(config, "validation")
                and config.validation
                and hasattr(config.validation, "minimum_disk_space_mb")
                else 100
            ),
        },
        "messages": {
            "install_success": (
                config.messages.install_success
                if hasattr(config, "messages")
                and config.messages
                and hasattr(config.messages, "install_success")
                else f"✅ {config.display_name} installed successfully!"
            ),
            "install_dev_success": (
                config.messages.install_dev_success
                if hasattr(config, "messages")
                and config.messages
                and hasattr(config.messages, "install_dev_success")
                else f"✅ {config.display_name} installed in development mode!"
            ),
            "upgrade_success": (
                config.messages.upgrade_success
                if hasattr(config, "messages")
                and config.messages
                and hasattr(config.messages, "upgrade_success")
                else f"✅ {config.display_name} upgraded successfully!"
            ),
            "uninstall_success": (
                config.messages.uninstall_success
                if hasattr(config, "messages")
                and config.messages
                and hasattr(config.messages, "uninstall_success")
                else f"✅ {config.display_name} uninstalled successfully!"
            ),
        },
        "cache_ttl": DEFAULT_CACHE_TTL,
    }

    script = template.render(**template_vars)

    return script


def backup_file(file_path: Path, create_backup: bool = False) -> Optional[Path]:
    """Create a backup of a file if it exists and backup is requested."""

    if create_backup and file_path.exists():

        backup_path = file_path.with_suffix(file_path.suffix + ".bak")

        shutil.copy2(file_path, backup_path)

        return backup_path

    return None


def update_pyproject_toml(
    project_dir: Path,
    package_name: str,
    command_name: str,
    cli_filename: str = "generated_cli.py",
    create_backup: bool = False,
) -> bool:
    """Update pyproject.toml to use the generated CLI."""
    _lazy_imports()

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

        with open(pyproject_path, "r") as f:

            data = toml.load(f)

        # Update the entry points

        # Remove .py extension from filename for module import

        cli_module_name = cli_filename.replace(".py", "")

        if (
            "tool" in data
            and "poetry" in data["tool"]
            and "scripts" in data["tool"]["poetry"]
        ):

            # Poetry format

            data["tool"]["poetry"]["scripts"][
                command_name
            ] = f"{package_name}.{cli_module_name}:cli_entry"

            typer.echo(f"✅ Updated Poetry entry point for '{command_name}'")

        elif "project" in data and "scripts" in data["project"]:

            # PEP 621 format
            # Convert package name hyphens to underscores for Python module naming
            module_name = package_name.replace("-", "_")
            data["project"]["scripts"][
                command_name
            ] = f"{module_name}.{cli_module_name}:cli_entry"

            typer.echo(f"✅ Updated PEP 621 entry point for '{command_name}'")

        else:

            # Create project.scripts section if it doesn't exist

            if "project" not in data:

                data["project"] = {}

            if "scripts" not in data["project"]:

                data["project"]["scripts"] = {}

            # Convert package name hyphens to underscores for Python module naming
            module_name = package_name.replace("-", "_")
            data["project"]["scripts"][
                command_name
            ] = f"{module_name}.{cli_module_name}:cli_entry"

            typer.echo(f"✅ Created entry point for '{command_name}'")

        # Add package-data configuration for setup.sh

        if "project" in data:  # PEP 621 format

            if "tool" not in data:

                data["tool"] = {}

            if "setuptools" not in data["tool"]:

                data["tool"]["setuptools"] = {}

            if "package-data" not in data["tool"]["setuptools"]:

                data["tool"]["setuptools"]["package-data"] = {}

            # Add setup.sh to package-data
            # Convert package name hyphens to underscores for Python module naming
            module_name = package_name.replace("-", "_")

            if module_name not in data["tool"]["setuptools"]["package-data"]:

                data["tool"]["setuptools"]["package-data"][module_name] = ["setup.sh"]

                typer.echo(f"✅ Added setup.sh to package-data for '{module_name}'")

            else:

                existing = data["tool"]["setuptools"]["package-data"][module_name]

                if isinstance(existing, list) and "setup.sh" not in existing:

                    existing.append("setup.sh")

                    typer.echo(
                        f"✅ Added setup.sh to existing package-data for '{module_name}'"
                    )

                elif isinstance(existing, str) and existing != "setup.sh":

                    # Convert single string to list and add setup.sh

                    data["tool"]["setuptools"]["package-data"][module_name] = [
                        existing,
                        "setup.sh",
                    ]

                    typer.echo(
                        f"✅ Added setup.sh to existing package-data for '{module_name}'"
                    )

                elif "setup.sh" in existing or existing == "setup.sh":

                    typer.echo(
                        f"ℹ️  setup.sh already in package-data for '{module_name}'"
                    )

        elif "tool" in data and "poetry" in data["tool"]:

            # Poetry format - handle includes differently

            if "packages" not in data["tool"]["poetry"]:

                data["tool"]["poetry"]["packages"] = []

            # Poetry uses include for additional files

            if "include" not in data["tool"]["poetry"]:

                data["tool"]["poetry"]["include"] = []

            # Add setup.sh to includes if not already present

            setup_include = {"path": "setup.sh", "format": "sdist"}

            if setup_include not in data["tool"]["poetry"]["include"]:

                data["tool"]["poetry"]["include"].append(setup_include)

                typer.echo(f"✅ Added setup.sh to Poetry includes for '{package_name}'")

            else:

                typer.echo(
                    f"ℹ️  setup.sh already in Poetry includes for '{package_name}'"
                )

        # Write back the modified pyproject.toml

        with open(pyproject_path, "w") as f:

            toml.dump(data, f)

        return True

    except Exception as e:

        typer.echo(f"❌ Error updating pyproject.toml: {e}", err=True)

        return False




# Import build command from cli_commands module
from .cli_commands.build import build_command

# Register the build command with the app
app.command(name="build")(build_command)


# Import validate command from cli_commands module
from .cli_commands.validate import validate_command

# Register the validate command with the app
app.command(name="validate")(validate_command)


# Import init command from cli_commands module
from .cli_commands.init import init_command

# Register the init command with the app
app.command(name="init")(init_command)


# Import serve command from cli_commands module
from .cli_commands.serve import serve_command

# Register the serve command with the app
app.command(name="serve")(serve_command)


# Import upgrade command from cli_commands module
from .cli_commands.upgrade import upgrade_command

# Register the upgrade command with the app
app.command(name="upgrade")(upgrade_command)


# Import migrate command from cli_commands module
from .cli_commands.migrate import migrate_command

# Register the migrate command with the app
app.command(name="migrate")(migrate_command)


def run_app():
    """Run the CLI app with enhanced spacing for better terminal presentation."""
    import sys
    
    # Check if this is a help command (which already has good spacing)
    is_help_command = (
        '--help' in sys.argv or 
        '-h' in sys.argv or
        len(sys.argv) == 1  # Just 'goobits' with no args shows help
    )
    
    # Add spacing before command output (except for help commands or redirected output)
    if sys.stdout.isatty() and not is_help_command:
        print()  # Empty line before
    
    try:
        app()
    finally:
        # Add spacing after command output (except for help commands or redirected output)  
        if sys.stdout.isatty() and not is_help_command:
            print()  # Empty line after


if __name__ == "__main__":
    run_app()
