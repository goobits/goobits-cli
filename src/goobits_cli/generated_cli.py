#!/usr/bin/env python3
"""Auto-generated from goobits.yaml"""
import os
import sys
import importlib.util
from pathlib import Path
import rich_click as click
from rich_click import RichGroup, RichCommand

# Set up rich-click configuration globally
click.rich_click.USE_RICH_MARKUP = True  
click.rich_click.USE_MARKDOWN = False  # Disable markdown to avoid conflicts
click.rich_click.MARKUP_MODE = "rich"

# Environment variables for additional control
os.environ["RICH_CLICK_USE_RICH_MARKUP"] = "1"
os.environ["RICH_CLICK_FORCE_TERMINAL"] = "1"
click.rich_click.SHOW_ARGUMENTS = True
click.rich_click.GROUP_ARGUMENTS_OPTIONS = True
click.rich_click.SHOW_METAVARS_COLUMN = False
click.rich_click.APPEND_METAVARS_HELP = True
click.rich_click.STYLE_ERRORS_SUGGESTION = "#ff5555"
click.rich_click.ERRORS_SUGGESTION = "Try running the '--help' flag for more information."
click.rich_click.ERRORS_EPILOGUE = "To find out more, visit https://github.com/anthropics/claude-code"
click.rich_click.MAX_WIDTH = 120  # Set reasonable width
click.rich_click.WIDTH = 120  # Set consistent width
click.rich_click.COLOR_SYSTEM = "auto"
click.rich_click.SHOW_SUBCOMMAND_ALIASES = True
click.rich_click.ALIGN_OPTIONS_SWITCHES = True
click.rich_click.STYLE_OPTION = "#ff79c6"      # Dracula Pink - for option flags
click.rich_click.STYLE_SWITCH = "#50fa7b"      # Dracula Green - for switches
click.rich_click.STYLE_METAVAR = "#8BE9FD not bold"   # Light cyan - for argument types (OPTIONS, COMMAND)  
click.rich_click.STYLE_METAVAR_SEPARATOR = "#6272a4"  # Dracula Comment
click.rich_click.STYLE_HEADER_TEXT = "bold yellow"    # Bold yellow - for section headers
click.rich_click.STYLE_EPILOGUE_TEXT = "#6272a4"      # Dracula Comment
click.rich_click.STYLE_FOOTER_TEXT = "#6272a4"        # Dracula Comment
click.rich_click.STYLE_USAGE = "#BD93F9"              # Purple - for "Usage:" line
click.rich_click.STYLE_USAGE_COMMAND = "bold"         # Bold for main command name
click.rich_click.STYLE_DEPRECATED = "#ff5555"         # Dracula Red
click.rich_click.STYLE_HELPTEXT_FIRST_LINE = "#f8f8f2" # Dracula Foreground
click.rich_click.STYLE_HELPTEXT = "#B3B8C0"           # Light gray - for help descriptions
click.rich_click.STYLE_OPTION_DEFAULT = "#ffb86c"     # Dracula Orange
click.rich_click.STYLE_REQUIRED_SHORT = "#ff5555"     # Dracula Red
click.rich_click.STYLE_REQUIRED_LONG = "#ff5555"      # Dracula Red
click.rich_click.STYLE_OPTIONS_PANEL_BORDER = "dim"   # Dim for subtle borders
click.rich_click.STYLE_COMMANDS_PANEL_BORDER = "dim"  # Dim for subtle borders
click.rich_click.STYLE_COMMAND = "#50fa7b"            # Dracula Green - for command names in list
click.rich_click.STYLE_COMMANDS_TABLE_COLUMN_WIDTH_RATIO = (1, 3)  # Command:Description ratio (1/4 : 3/4)


# Command groups will be set after main function is defined


# Hooks system - try to import app_hooks module
app_hooks = None
try:
    # Try to import from the same directory as this script
    script_dir = Path(__file__).parent
    hooks_path = script_dir / "app_hooks.py"
    
    if hooks_path.exists():
        spec = importlib.util.spec_from_file_location("app_hooks", hooks_path)
        app_hooks = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(app_hooks)
    else:
        # Try to import from Python path
        import app_hooks
except (ImportError, FileNotFoundError):
    # No hooks module found, use default behavior
    pass

def load_plugins(cli_group):
    """Load plugins from the conventional plugin directory."""
    # Define plugin directories to search
    plugin_dirs = [
        # User-specific plugin directory
        Path.home() / ".config" / "goobits" / "Goobits CLI" / "plugins",
        # Local plugin directory (same as script)
        Path(__file__).parent / "plugins",
    ]
    
    for plugin_dir in plugin_dirs:
        if not plugin_dir.exists():
            continue
            
        # Add plugin directory to Python path
        sys.path.insert(0, str(plugin_dir))
        
        # Scan for plugin files
        for plugin_file in plugin_dir.glob("*.py"):
            if plugin_file.name.startswith("_"):
                continue
                
            # Skip core system files that aren't plugins
            if plugin_file.name in ["loader.py", "__init__.py"]:
                continue
                
            plugin_name = plugin_file.stem
            
            try:
                # Import the plugin module
                spec = importlib.util.spec_from_file_location(plugin_name, plugin_file)
                plugin_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(plugin_module)
                
                # Call register_plugin if it exists
                if hasattr(plugin_module, "register_plugin"):
                    plugin_module.register_plugin(cli_group)
                    click.echo(f"Loaded plugin: {plugin_name}", err=True)
            except Exception as e:
                click.echo(f"Failed to load plugin {plugin_name}: {e}", err=True)







def get_version():
    """Get version from pyproject.toml or __init__.py"""
    import re
    
    try:
        # Try to get version from pyproject.toml FIRST (most authoritative)
        toml_path = Path(__file__).parent.parent / "pyproject.toml"
        if toml_path.exists():
            content = toml_path.read_text()
            match = re.search(r'version\s*=\s*["\']([^"\']+)["\']', content)
            if match:
                return match.group(1)
    except Exception:
        pass
    
    try:
        # Fallback to __init__.py
        init_path = Path(__file__).parent / "__init__.py"
        if init_path.exists():
            content = init_path.read_text()
            match = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', content)
            if match:
                return match.group(1)
    except Exception:
        pass
        
    # Final fallback
    return "1.1.0"






  
    
  

  

  

  



class DefaultGroup(RichGroup):
    """Allow a default command to be invoked without being specified."""
    
    def __init__(self, *args, default=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.default_command = default
    
    def main(self, *args, **kwargs):
        """Override main to handle stdin input when no command is provided."""
        import sys
        import os
        import stat
        
        # Check if we need to inject the default command due to stdin input
        if len(sys.argv) == 1 and self.default_command:  # Only script name provided
            # Check if stdin is coming from a pipe or redirection
            has_stdin = False
            try:
                # Check if stdin is a pipe or file (not a terminal)
                stdin_stat = os.fstat(sys.stdin.fileno())
                has_stdin = stat.S_ISFIFO(stdin_stat.st_mode) or stat.S_ISREG(stdin_stat.st_mode)
            except:
                # Fallback to isatty check
                has_stdin = not sys.stdin.isatty()
            
            if has_stdin:
                # Inject the default command into sys.argv
                sys.argv.append(self.default_command)
        
        return super().main(*args, **kwargs)
    
    def resolve_command(self, ctx, args):
        import sys
        import os
        
        try:
            # Try normal command resolution first
            return super().resolve_command(ctx, args)
        except click.UsageError:
            # If no command found and we have a default, use it
            # Check if stdin is coming from a pipe or redirection
            has_stdin = False
            try:
                # Check if stdin is a pipe or file (not a terminal)
                stdin_stat = os.fstat(sys.stdin.fileno())
                # Use S_ISFIFO to check if it's a pipe, or S_ISREG to check if it's a regular file
                import stat
                has_stdin = stat.S_ISFIFO(stdin_stat.st_mode) or stat.S_ISREG(stdin_stat.st_mode)
            except Exception as e:
                # Fallback to isatty check
                has_stdin = not sys.stdin.isatty()
            
            is_help_request = any(arg in ['--help-all', '--help-json'] for arg in args)
            
            if self.default_command and not is_help_request:
                # Trigger default command if:
                # 1. We have args (existing behavior)
                # 2. We have stdin input (new behavior for pipes)
                if args or has_stdin:
                    cmd = self.commands.get(self.default_command)
                    if cmd:
                        # Return command name, command object, and all args
                        return self.default_command, cmd, args
            raise



@click.group(cls=DefaultGroup, default='build', context_settings={"help_option_names": ["-h", "--help"], "max_content_width": 120})

@click.version_option(version=get_version(), prog_name="Goobits CLI")
@click.pass_context


@click.option('--help-all', is_flag=True, is_eager=True, help='Show help for all commands.', hidden=True)

def main(ctx, help_all=False):
    """[bold color(6)]Goobits CLI v1.1.0[/bold color(6)] - Build professional command-line tools with YAML configuration

    
    \b
    [#B3B8C0]Transform simple YAML configuration into rich terminal applications with setup scripts, dependency management, and cross-platform compatibility.[/#B3B8C0]
    

    
    \b
    [bold yellow]Quick Start:[/bold yellow]
    mkdir my-cli && cd my-cli: [green]Create new project directory[/green]
    [green]goobits init               [/green] [italic][#B3B8C0]# Generate initial goobits.yaml[/#B3B8C0][/italic]
    [green]goobits build              [/green] [italic][#B3B8C0]# Create CLI and setup scripts[/#B3B8C0][/italic]
    ./setup.sh install --dev:  [green]Install for development[/green]
    
    \b
    [bold yellow]Core Commands:[/bold yellow]
    [green]build  [/green]  🔨 Generate CLI and setup scripts from goobits.yaml
    [green]serve  [/green]  🌐 Serve local PyPI-compatible package index
    [green]init   [/green]  🆕 Create initial goobits.yaml template
    
    \b
    [bold yellow]Development Workflow:[/bold yellow]
    1. Edit goobits.yaml: [green]Define your CLI structure[/green]
    2. goobits build:     [green]Generate implementation files[/green]
    3. Edit app_hooks.py: [green]Add your business logic[/green]
    
    \b
    """

    
    if help_all:
        # Print main help
        click.echo(ctx.get_help())
        click.echo() # Add a blank line for spacing

        # Get a list of all command names
        commands_to_show = sorted(ctx.command.list_commands(ctx))

        for cmd_name in commands_to_show:
            command = ctx.command.get_command(ctx, cmd_name)

            # Create a new context for the subcommand
            sub_ctx = click.Context(command, info_name=cmd_name, parent=ctx)

            # Print a separator and the subcommand's help
            click.echo("="*20 + f" HELP FOR: {cmd_name} " + "="*20)
            click.echo(sub_ctx.get_help())
            click.echo() # Add a blank line for spacing

        # Exit after printing all help
        ctx.exit()
    

    pass


# Set command groups after main function is defined
click.rich_click.COMMAND_GROUPS = {
    "main": [
        
        {
            "name": "Core Commands",
            "commands": ['build', 'init'],
        },
        
        {
            "name": "Development Tools",
            "commands": ['serve'],
        },
        
        {
            "name": "Utilities",
            "commands": ['upgrade', 'version', 'help'],
        },
        
    ]
}




@main.command()

@click.argument(
    "CONFIG_PATH",
    required=False
)


@click.option("-o", "--output-dir",
    type=str,
    help="📁 Output directory (defaults to same directory as config file)"
)

@click.option("--output",
    type=str,
    help="📝 Output filename for generated CLI (defaults to 'generated_cli.py')"
)

@click.option("--backup",
    is_flag=True,
    help="💾 Create backup files (.bak) when overwriting existing files"
)

def build(config_path, output_dir, output, backup):
    """🔨 Build CLI and setup scripts from goobits.yaml configuration"""
    # Check if hook function exists
    hook_name = f"on_build"
    if app_hooks and hasattr(app_hooks, hook_name):
        # Call the hook with all parameters
        hook_func = getattr(app_hooks, hook_name)
        
        result = hook_func(config_path, output_dir, output, backup)
        
        return result
    else:
        # Default placeholder behavior
        click.echo(f"Executing build command...")
        
        
        click.echo(f"  config_path: {config_path}")
        
        
        
        
        click.echo(f"  output-dir: {output_dir}")
        
        click.echo(f"  output: {output}")
        
        click.echo(f"  backup: {backup}")
        
        




@main.command()

@click.argument(
    "PROJECT_NAME",
    required=False
)


@click.option("-t", "--template",
    type=click.Choice(['basic', 'advanced', 'api-client', 'text-processor']),
    default="basic",
    help="🎯 Template type"
)

@click.option("--force",
    is_flag=True,
    help="🔥 Overwrite existing goobits.yaml file"
)

def init(project_name, template, force):
    """🆕 Create initial goobits.yaml template"""
    # Check if hook function exists
    hook_name = f"on_init"
    if app_hooks and hasattr(app_hooks, hook_name):
        # Call the hook with all parameters
        hook_func = getattr(app_hooks, hook_name)
        
        result = hook_func(project_name, template, force)
        
        return result
    else:
        # Default placeholder behavior
        click.echo(f"Executing init command...")
        
        
        click.echo(f"  project_name: {project_name}")
        
        
        
        
        click.echo(f"  template: {template}")
        
        click.echo(f"  force: {force}")
        
        




@main.command()

@click.argument(
    "DIRECTORY"
)


@click.option("--host",
    type=str,
    default="localhost",
    help="🌍 Host to bind the server to"
)

@click.option("-p", "--port",
    type=int,
    default=8080,
    help="🔌 Port to run the server on"
)

def serve(directory, host, port):
    """🌐 Serve local PyPI-compatible package index"""
    # Check if hook function exists
    hook_name = f"on_serve"
    if app_hooks and hasattr(app_hooks, hook_name):
        # Call the hook with all parameters
        hook_func = getattr(app_hooks, hook_name)
        
        result = hook_func(directory, host, port)
        
        return result
    else:
        # Default placeholder behavior
        click.echo(f"Executing serve command...")
        
        
        click.echo(f"  directory: {directory}")
        
        
        
        
        click.echo(f"  host: {host}")
        
        click.echo(f"  port: {port}")
        
        




@main.command()


@click.option("--source",
    type=str,
    default="pypi",
    help="Upgrade source: pypi, git, local"
)

@click.option("--version",
    type=str,
    help="Specific version to install"
)

@click.option("--pre",
    is_flag=True,
    help="Include pre-release versions"
)

@click.option("--dry-run",
    is_flag=True,
    help="Show what would be upgraded without doing it"
)

def upgrade(source, version, pre, dry_run):
    """🆙 Upgrade goobits-cli to the latest version"""
    # Check if hook function exists
    hook_name = f"on_upgrade"
    if app_hooks and hasattr(app_hooks, hook_name):
        # Call the hook with all parameters
        hook_func = getattr(app_hooks, hook_name)
        
        result = hook_func(source, version, pre, dry_run)
        
        return result
    else:
        # Default placeholder behavior
        click.echo(f"Executing upgrade command...")
        
        
        
        click.echo(f"  source: {source}")
        
        click.echo(f"  version: {version}")
        
        click.echo(f"  pre: {pre}")
        
        click.echo(f"  dry-run: {dry_run}")
        
        




def cli_entry():
    """Entry point for the CLI when installed via pipx."""
    # Load plugins before running the CLI
    load_plugins(main)
    main()

if __name__ == "__main__":
    cli_entry()