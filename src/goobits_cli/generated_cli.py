#!/usr/bin/env python3
"""Auto-generated from goobits.yaml"""
import os
import sys
import logging
import importlib.util
from pathlib import Path
import rich_click as click
from rich_click import RichGroup, RichCommand
from typing import Optional, Dict, Any


# Enhanced Error Handling Classes
class CLIError(Exception):
    """Base exception for CLI errors."""
    def __init__(self, message: str, exit_code: int = 1, suggestion: Optional[str] = None):
        self.message = message
        self.exit_code = exit_code
        self.suggestion = suggestion
        super().__init__(self.message)


class ConfigError(CLIError):
    """Configuration-related error."""
    def __init__(self, message: str, suggestion: Optional[str] = None):
        super().__init__(message, exit_code=2, suggestion=suggestion)


class HookError(CLIError):
    """Hook execution error."""
    def __init__(self, message: str, hook_name: Optional[str] = None):
        self.hook_name = hook_name
        super().__init__(message, exit_code=3, suggestion=f"Check the '{hook_name}' function in your app_hooks.py file" if hook_name else None)


class DependencyError(CLIError):
    """Missing dependency error."""
    def __init__(self, message: str, dependency: str, install_command: Optional[str] = None):
        self.dependency = dependency
        self.install_command = install_command
        suggestion = f"Install with: {install_command}" if install_command else f"Install the '{dependency}' package"
        super().__init__(message, exit_code=4, suggestion=suggestion)


# Global error handler
def handle_cli_error(error: Exception, debug: bool = False) -> int:
    """Handle CLI errors with appropriate messages and exit codes."""
    if isinstance(error, CLIError):
        click.echo(f"❌ Error: {error.message}", err=True)
        if error.suggestion:
            click.echo(f"💡 Suggestion: {error.suggestion}", err=True)
        if debug:
            import traceback
            click.echo("\n🔍 Debug traceback:", err=True)
            click.echo(traceback.format_exc(), err=True)
        return error.exit_code
    else:
        # Unexpected errors
        click.echo(f"❌ Unexpected error: {str(error)}", err=True)
        click.echo("💡 This may be a bug. Please report it with the following details:", err=True)
        if debug:
            import traceback
            click.echo(traceback.format_exc(), err=True)
        else:
            click.echo(f"   Error type: {type(error).__name__}", err=True)
            click.echo(f"   Error message: {str(error)}", err=True)
            click.echo("   Run with --debug for full traceback", err=True)
        return 1


# Set up logging
logging.basicConfig(
    level=logging.WARNING,
    format='%(levelname)s: %(message)s',
    handlers=[
        logging.StreamHandler(sys.stderr)
    ]
)
logger = logging.getLogger(__name__)

# Import generated helper modules with enhanced error handling
_missing_dependencies = []

try:
    from .config_manager import get_config, load_config, get_config_value, set_config_value
    HAS_CONFIG_MANAGER = True
except ImportError as e:
    HAS_CONFIG_MANAGER = False
    logger.debug(f"Config manager not available: {e}")
    _missing_dependencies.append("config_manager")

try:
    from .progress_helper import (
        get_progress_helper, spinner, progress_bar, simple_progress,
        print_success, print_error, print_warning, print_info,
        with_spinner, with_progress
    )
    HAS_PROGRESS_HELPER = True
except ImportError as e:
    HAS_PROGRESS_HELPER = False
    logger.debug(f"Progress helper not available: {e}")
    _missing_dependencies.append("progress_helper")

try:
    from .prompts_helper import (
        get_prompts_helper, text, password, confirm, select, multiselect,
        integer, float_input, path
    )
    HAS_PROMPTS_HELPER = True
except ImportError as e:
    HAS_PROMPTS_HELPER = False
    logger.debug(f"Prompts helper not available: {e}")
    _missing_dependencies.append("prompts_helper")

try:
    from .completion_helper import (
        get_completion_helper, generate_completion_script, install_completion,
        get_install_instructions
    )
    HAS_COMPLETION_HELPER = True
except ImportError as e:
    HAS_COMPLETION_HELPER = False
    logger.debug(f"Completion helper not available: {e}")
    _missing_dependencies.append("completion_helper")

# Log missing dependencies for debugging
if _missing_dependencies:
    logger.debug(f"Missing helper modules: {', '.join(_missing_dependencies)}")

# Initialize global helpers with error handling
try:
    if HAS_CONFIG_MANAGER:
        config = get_config()
    else:
        config = None
except Exception as e:
    logger.warning(f"Failed to initialize config manager: {e}")
    config = None
    HAS_CONFIG_MANAGER = False

try:
    if HAS_PROGRESS_HELPER:
        progress = get_progress_helper()
    else:
        progress = None
except Exception as e:
    logger.warning(f"Failed to initialize progress helper: {e}")
    progress = None
    HAS_PROGRESS_HELPER = False

try:
    if HAS_PROMPTS_HELPER:
        prompts = get_prompts_helper()
    else:
        prompts = None
except Exception as e:
    logger.warning(f"Failed to initialize prompts helper: {e}")
    prompts = None
    HAS_PROMPTS_HELPER = False

try:
    if HAS_COMPLETION_HELPER:
        completion = get_completion_helper()
    else:
        completion = None
except Exception as e:
    logger.warning(f"Failed to initialize completion helper: {e}")
    completion = None
    HAS_COMPLETION_HELPER = False

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

# No hooks path configured, try default locations
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
        Path(__file__).parent / "setup.sh",  # Package directory (installed packages)
        Path(__file__).parent.parent / "setup.sh",  # Development mode 
        Path.home() / ".local" / "share" / "goobits-cli" / "setup.sh",  # User data
        # Remove Path.cwd() to prevent cross-contamination
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
        # Look in multiple possible locations
        possible_paths = [
            Path(__file__).parent.parent / "pyproject.toml",  # For flat structure
            Path(__file__).parent.parent.parent / "pyproject.toml",  # For src/ structure
        ]
        toml_path = None
        for path in possible_paths:
            if path.exists():
                toml_path = path
                break
        if toml_path:
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
    """🛠️  [bold color(6)]Goobits CLI v1.2.0[/bold color(6)] - Build professional command-line tools with YAML configuration

    
    \b
    [#B3B8C0]Transform simple YAML configuration into rich terminal applications with setup scripts, dependency management, and cross-platform compatibility.[/#B3B8C0]
    

    
    
    [bold yellow]🚀 Quick Start[/bold yellow]
    
    
    [green]   mkdir my-cli && cd my-cli  [/green] [italic][#B3B8C0]# Create new project directory[/#B3B8C0][/italic]
    
    
    [green]   goobits init               [/green] [italic][#B3B8C0]# Generate initial goobits.yaml[/#B3B8C0][/italic]
    
    
    [green]   goobits build              [/green] [italic][#B3B8C0]# Create CLI and setup scripts[/#B3B8C0][/italic]
    
    
    [green]   ./setup.sh install --dev   [/green] [italic][#B3B8C0]# Install for development[/#B3B8C0][/italic]
    
    [green] [/green]
    
    [bold yellow]💡 Core Commands[/bold yellow]
    
    
    [green]   build  [/green]  🔨 Generate CLI and setup scripts from goobits.yaml
    
    
    [green]   serve  [/green]  🌐 Serve local PyPI-compatible package index
    
    
    [green]   init   [/green]  🆕 Create initial goobits.yaml template
    
    [green] [/green]
    
    [bold yellow]🔧 Development Workflow[/bold yellow]
    
    
    [#B3B8C0]   1. Edit goobits.yaml: [/#B3B8C0][green]Define your CLI structure[/green]
    
    [#B3B8C0]   2. goobits build:     [/#B3B8C0][green]Generate implementation files[/green]
    
    [#B3B8C0]   3. Edit app_hooks.py: [/#B3B8C0][green]Add your business logic[/green]
    [green] [/green]
    
    
    
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

# Replace the version placeholder with dynamic version in the main command docstring



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
        
        
    
    















# Shell completion commands
@main.group()
def completion():
    """🔧 Shell completion management"""
    pass

# Internal completion command (hidden from help)
@main.command()
@click.argument('shell', type=click.Choice(['bash', 'zsh', 'fish']))
@click.argument('current_line')
@click.argument('cursor_pos', type=int, required=False)
@click.option('--debug', is_flag=True, help='Debug completion engine')
def _completion(shell, current_line, cursor_pos, debug):
    """Internal completion command - called by shell completion scripts"""
    try:
        # Import completion engine
        import os
        import sys
        from pathlib import Path
        
        # Add completion_engine to path
        engine_path = Path(__file__).parent / "completion_engine.py"
        
        if engine_path.exists():
            # Import and run the completion engine
            import importlib.util
            spec = importlib.util.spec_from_file_location("completion_engine", engine_path)
            completion_engine = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(completion_engine)
            
            # Get completions
            engine = completion_engine.CompletionEngine()
            completions = engine.get_completions(shell, current_line, cursor_pos)
            
            # Output completions
            for completion in completions:
                click.echo(completion)
                
        elif debug:
            click.echo("completion_engine.py not found", err=True)
            
    except Exception as e:
        if debug:
            click.echo(f"Completion error: {e}", err=True)
        # Silently fail in production to avoid breaking shell completion

# Add this command with underscore to hide it from help
_completion.hidden = True

@completion.command()
@click.argument('shell', type=click.Choice(['bash', 'zsh', 'fish']))
@click.option('--output', '-o', type=click.Path(), help='Output file path')
def generate(shell, output):
    """Generate shell completion script"""
    if not HAS_COMPLETION_HELPER:
        click.echo("❌ Completion helper not available. Missing completion_helper module.")
        return
    
    try:
        script_content = generate_completion_script(shell)
        
        if output:
            output_path = Path(output)
            output_path.write_text(script_content)
            click.echo(f"✅ {shell.title()} completion script saved to: {output_path}")
        else:
            click.echo(script_content)
    except Exception as e:
        click.echo(f"❌ Error generating {shell} completion: {e}")

@completion.command()
@click.argument('shell', type=click.Choice(['bash', 'zsh', 'fish']))
@click.option('--user', is_flag=True, default=True, help='Install for current user (default)')
@click.option('--system', is_flag=True, help='Install system-wide (requires sudo)')
def install(shell, user, system):
    """Install shell completion script"""
    if not HAS_COMPLETION_HELPER:
        click.echo("❌ Completion helper not available. Missing completion_helper module.")
        return
    
    try:
        user_install = not system
        success = install_completion(shell, user_install)
        
        if success:
            click.echo(f"✅ {shell.title()} completion installed successfully!")
            
            instructions = get_install_instructions(shell)
            if instructions and 'reload_cmd' in instructions:
                click.echo(f"💡 Reload your shell: {instructions['reload_cmd']}")
        else:
            click.echo(f"❌ Failed to install {shell} completion")
            
    except Exception as e:
        click.echo(f"❌ Error installing {shell} completion: {e}")

@completion.command()
@click.argument('shell', type=click.Choice(['bash', 'zsh', 'fish']))
def instructions(shell):
    """Show installation instructions for shell completion"""
    if not HAS_COMPLETION_HELPER:
        click.echo("❌ Completion helper not available. Missing completion_helper module.")
        return
    
    instructions = get_install_instructions(shell)
    if not instructions:
        click.echo(f"❌ No instructions available for {shell}")
        return
    
    click.echo(f"📋 {shell.title()} completion installation instructions:")
    click.echo()
    
    click.echo("🏠 User installation (recommended):")
    click.echo(f"   mkdir -p {Path(instructions['user_script_path']).parent}")
    click.echo(f"   goobits-cli completion generate {shell} > completion.{shell}")
    click.echo(f"   cp completion.{shell} {instructions['user_script_path']}")
    click.echo()
    
    click.echo("🌐 System-wide installation:")
    click.echo(f"   goobits-cli completion generate {shell} > completion.{shell}")
    click.echo(f"   {instructions['install_cmd']}")
    click.echo()
    
    click.echo("🔄 Reload shell:")
    click.echo(f"   {instructions['reload_cmd']}")

# Configuration management commands
@main.group()
def config():
    """⚙️ Configuration management"""
    pass

@config.command()
@click.argument('key', required=False)
def get(key):
    """Get configuration value"""
    if not HAS_CONFIG_MANAGER:
        click.echo("❌ Configuration manager not available.")
        return
    
    try:
        if key:
            value = get_config_value(key)
            if value is not None:
                click.echo(f"{key}: {value}")
            else:
                click.echo(f"❌ Configuration key '{key}' not found")
        else:
            # Show all configuration
            config_data = load_config()
            import json
            click.echo(json.dumps(config_data, indent=2))
    except Exception as e:
        click.echo(f"❌ Error getting configuration: {e}")

@config.command()
@click.argument('key')
@click.argument('value')
def set(key, value):
    """Set configuration value"""
    if not HAS_CONFIG_MANAGER:
        click.echo("❌ Configuration manager not available.")
        return
    
    try:
        # Try to parse value as JSON for complex types
        import json
        try:
            parsed_value = json.loads(value)
        except json.JSONDecodeError:
            parsed_value = value
        
        success = set_config_value(key, parsed_value)
        if success:
            click.echo(f"✅ Set {key} = {parsed_value}")
        else:
            click.echo(f"❌ Failed to set configuration value")
    except Exception as e:
        click.echo(f"❌ Error setting configuration: {e}")

@config.command()
def reset():
    """Reset configuration to defaults"""
    if not HAS_CONFIG_MANAGER:
        click.echo("❌ Configuration manager not available.")
        return
    
    try:
        if HAS_PROMPTS_HELPER:
            if confirm("Are you sure you want to reset all configuration to defaults?"):
                config.reset()
                click.echo("✅ Configuration reset to defaults")
            else:
                click.echo("❌ Reset cancelled")
        else:
            config.reset()
            click.echo("✅ Configuration reset to defaults")
    except Exception as e:
        click.echo(f"❌ Error resetting configuration: {e}")

@config.command()
def path():
    """Show configuration file path"""
    if not HAS_CONFIG_MANAGER:
        click.echo("❌ Configuration manager not available.")
        return
    
    try:
        config_path = config.get_config_path()
        click.echo(f"📁 Configuration file: {config_path}")
        
        # Check for RC files
        rc_file = config.find_rc_file()
        if rc_file:
            click.echo(f"📄 Active RC file: {rc_file}")
    except Exception as e:
        click.echo(f"❌ Error getting configuration path: {e}")

def cli_entry():
    """Entry point for the CLI when installed via pipx."""
    try:
        # Load plugins before running the CLI
        load_plugins(main)
        main()
    except KeyboardInterrupt:
        click.echo("\n⏹️  Operation cancelled by user", err=True)
        sys.exit(130)  # Standard exit code for Ctrl+C
    except Exception as e:
        # Get debug flag from command line args
        debug = '--debug' in sys.argv
        exit_code = handle_cli_error(e, debug)
        sys.exit(exit_code)

if __name__ == "__main__":
    cli_entry()