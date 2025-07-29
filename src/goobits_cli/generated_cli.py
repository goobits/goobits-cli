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
    # Try to import from the project root directory
    script_dir = Path(__file__).parent.parent.parent
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

# Built-in commands

def builtin_upgrade_command(check_only=False, pre=False, version=None, dry_run=False):
    """Built-in upgrade function for Goobits CLI Framework - uses enhanced setup.sh script."""
    import subprocess
    import sys
    from pathlib import Path

    if check_only:
        print(f"Checking for updates to Goobits CLI Framework...")
        print("Update check not yet implemented. Run without --check to upgrade.")
        return

    if dry_run:
        print("Dry run - would execute: pipx upgrade goobits-cli")
        return

    # Find the setup.sh script - look in common locations
    setup_script = None
    search_paths = [
        Path.cwd() / "setup.sh",  # Current directory
        Path(__file__).parent.parent / "setup.sh",  # Package directory
        Path.home() / ".local" / "share" / "goobits-cli" / "setup.sh",  # User data
    ]
    
    for path in search_paths:
        if path.exists():
            setup_script = path
            break
    
    if setup_script is None:
        # Fallback to basic upgrade if setup.sh not found
        print(f"Enhanced setup script not found. Using basic upgrade for Goobits CLI Framework...")
        import shutil
        
        package_name = "goobits-cli"
        pypi_name = "goobits-cli"
        
        if shutil.which("pipx"):
            result = subprocess.run(["pipx", "list"], capture_output=True, text=True)
            if package_name in result.stdout or pypi_name in result.stdout:
                cmd = ["pipx", "upgrade", pypi_name]
            else:
                cmd = [sys.executable, "-m", "pip", "install", "--upgrade", pypi_name]
        else:
            cmd = [sys.executable, "-m", "pip", "install", "--upgrade", pypi_name]
        
        result = subprocess.run(cmd)
        if result.returncode == 0:
            print(f"✅ Goobits CLI Framework upgraded successfully!")
            print(f"Run 'goobits --version' to verify the new version.")
        else:
            print(f"❌ Upgrade failed with exit code {result.returncode}")
            sys.exit(1)
        return

    # Use the enhanced setup.sh script
    result = subprocess.run([str(setup_script), "upgrade"])
    sys.exit(result.returncode)


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
    return "1.2.0"






  
    
  

  

  



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
            except Exception:
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
    """[bold color(6)]Goobits CLI v1.2.0[/bold color(6)] - Build professional command-line tools with YAML configuration

    
    \b
    [#B3B8C0]Transform simple YAML configuration into rich terminal applications with setup scripts, dependency management, and cross-platform compatibility.[/#B3B8C0]
    

    
    \b
    [bold yellow]Quick Start:[/bold yellow]mkdir my-cli && cd my-cli: [green]Create new project directory[/green][green]goobits init               [/green] [italic][#B3B8C0]# Generate initial goobits.yaml[/#B3B8C0][/italic][green]goobits build              [/green] [italic][#B3B8C0]# Create CLI and setup scripts[/#B3B8C0][/italic]./setup.sh install --dev:  [green]Install for development[/green]
    \b
    [bold yellow]Core Commands:[/bold yellow][green]build  [/green]  🔨 Generate CLI and setup scripts from goobits.yaml[green]serve  [/green]  🌐 Serve local PyPI-compatible package index[green]init   [/green]  🆕 Create initial goobits.yaml template
    \b
    [bold yellow]Development Workflow:[/bold yellow]1. Edit goobits.yaml: [green]Define your CLI structure[/green]2. goobits build:     [green]Generate implementation files[/green]3. Edit app_hooks.py: [green]Add your business logic[/green]
    \b
       [#B3B8C0]📚 For detailed help on a command, run: [color(2)]goobits [COMMAND][/color(2)] [#ff79c6]--help[/#ff79c6][/#B3B8C0]
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
    
    
    # Store global options in context for use by commands
    

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
        
    ]
}


# Built-in upgrade command (enabled by default)

@main.command()
@click.option('--check', is_flag=True, help='Check for updates without installing')
@click.option('--version', type=str, help='Install specific version')
@click.option('--pre', is_flag=True, help='Include pre-release versions')
@click.option('--dry-run', is_flag=True, help='Show what would be done without doing it')
def upgrade(check, version, pre, dry_run):
    """Upgrade Goobits CLI Framework to the latest version."""
    builtin_upgrade_command(check_only=check, version=version, pre=pre, dry_run=dry_run)




@main.command()
@click.pass_context

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

def build(ctx, config_path, output_dir, output, backup):
    """🔨 Build CLI and setup scripts from goobits.yaml configuration"""
    
    # Check for built-in commands first
    
    # Built-in commands (build, init)
    try:
        from pathlib import Path
        import sys
        
        # Add the parent directory to sys.path to find goobits_cli
        parent_dir = Path(__file__).parent.parent.parent
        if str(parent_dir) not in sys.path:
            sys.path.insert(0, str(parent_dir))
        
        
        from goobits_cli.main import build
        
        # Use current directory's goobits.yaml if no config path specified
        config_file = Path(config_path) if config_path else Path("goobits.yaml")
        output_dir_path = Path(output_dir) if output_dir else None
        
        build(config_file, output_dir_path, output, backup)
        click.echo("✅ Build completed successfully!")
        click.echo("   - Generated setup.sh")
        click.echo("   - Updated CLI files")
        
        
            
    except ImportError as e:
        click.echo(f"❌ Build error: Could not import framework functions: {e}")
        return False
    except Exception as e:
        click.echo(f"❌ Build error: {e}")
        return False
    
    return True
    
    




@main.command()
@click.pass_context

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

def init(ctx, project_name, template, force):
    """🆕 Create initial goobits.yaml template"""
    
    # Check for built-in commands first
    
    # Built-in commands (build, init)
    try:
        from pathlib import Path
        import sys
        
        # Add the parent directory to sys.path to find goobits_cli
        parent_dir = Path(__file__).parent.parent.parent
        if str(parent_dir) not in sys.path:
            sys.path.insert(0, str(parent_dir))
        
        
        from goobits_cli.main import init
        
        init(project_name, template, force)
        click.echo("✅ Init completed successfully!")
        click.echo("   - Created goobits.yaml")
        
        
            
    except ImportError as e:
        click.echo(f"❌ Init error: Could not import framework functions: {e}")
        return False
    except Exception as e:
        click.echo(f"❌ Init error: {e}")
        return False
    
    return True
    
    




@main.command()
@click.pass_context

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

def serve(ctx, directory, host, port):
    """🌐 Serve local PyPI-compatible package index"""
    
    # Check for built-in commands first
    
    # Standard command - use the existing hook pattern
    hook_name = f"on_serve"
    if app_hooks and hasattr(app_hooks, hook_name):
        # Call the hook with all parameters
        hook_func = getattr(app_hooks, hook_name)
        
        # Prepare arguments including global options
        kwargs = {}
        kwargs['command_name'] = 'serve'  # Pass command name for all commands
        
        
        kwargs['directory'] = directory
        
        
        
        
        
        
        
        kwargs['host'] = host
        
        
        
        
        kwargs['port'] = port
        
        
        
        # Add global options from context
        
        
        result = hook_func(**kwargs)
        return result
    else:
        # Default placeholder behavior
        click.echo(f"Executing serve command...")
        
        
        click.echo(f"  directory: {directory}")
        
        
        
        
        click.echo(f"  host: {host}")
        
        click.echo(f"  port: {port}")
        
        
    
    















def cli_entry():
    """Entry point for the CLI when installed via pipx."""
    # Load plugins before running the CLI
    load_plugins(main)
    main()

if __name__ == "__main__":
    cli_entry()