#!/usr/bin/env python3
"""Auto-generated from test_config_complex.yaml"""
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
click.rich_click.ERRORS_EPILOGUE = "To find out more, visit https://github.com/your-org/your-project"
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
    """Built-in upgrade function for Complex Test CLI - uses enhanced setup.sh script."""
    import subprocess
    import sys
    from pathlib import Path

    if check_only:
        print(f"Checking for updates to Complex Test CLI...")
        print("Update check not yet implemented. Run without --check to upgrade.")
        return

    if dry_run:
        print("Dry run - would execute: pipx upgrade complex-test-cli")
        return

    # Find the setup.sh script - look in common locations
    setup_script = None
    search_paths = [
        Path(__file__).parent / "setup.sh",  # Package directory (installed packages)
        Path(__file__).parent.parent / "setup.sh",  # Development mode 
        Path.home() / ".local" / "share" / "complex-test-cli" / "setup.sh",  # User data
        # Remove Path.cwd() to prevent cross-contamination
    ]
    
    for path in search_paths:
        if path.exists():
            setup_script = path
            break
    
    if setup_script is None:
        # Fallback to basic upgrade if setup.sh not found
        print(f"Enhanced setup script not found. Using basic upgrade for Complex Test CLI...")
        import shutil
        
        package_name = "complex-test-cli"
        pypi_name = "complex-test-cli"
        
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
            print(f"✅ Complex Test CLI upgraded successfully!")
            print(f"Run 'complex-test --version' to verify the new version.")
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
        Path.home() / ".config" / "complex-test-cli" / "plugins",
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
    return "2.0.0"



def start_interactive_mode(ctx, param, value):
    """Callback for --interactive option."""
    if not value or ctx.resilient_parsing:
        return
    
    try:
        # Try to import interactive mode module
        import importlib.util
        import os
        
        # Get the directory where this CLI script is located
        cli_dir = Path(__file__).parent
        interactive_file = cli_dir / "enhanced_interactive_mode.py"
        
        if interactive_file.exists():
            spec = importlib.util.spec_from_file_location("enhanced_interactive_mode", interactive_file)
            interactive_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(interactive_module)
            interactive_module.start_enhanced_interactive()
            # If we get here, interactive mode completed successfully, exit cleanly
            import sys
            sys.exit(0)
        else:
            click.echo("❌ Interactive mode not available. enhanced_interactive_mode.py not found.")
            ctx.exit(1)
    except SystemExit:
        # Interactive mode exited, let it pass through
        import sys
        sys.exit(0)
    except Exception as e:
        click.echo(f"❌ Error starting interactive mode: {e}")
        ctx.exit(1)




  

  





@click.group(cls=RichGroup, context_settings={"help_option_names": ["-h", "--help"], "max_content_width": 120})

@click.version_option(version=get_version(), prog_name="Complex Test CLI")
@click.pass_context


@click.option('--interactive', is_flag=True, is_eager=True, callback=start_interactive_mode, help='Launch interactive mode for running commands interactively.')

def main(ctx):
    """[bold color(6)]Complex Test CLI v2.0.0[/bold color(6)] - Advanced CLI with multiple features

    
    \b
    [#B3B8C0]Complex CLI for comprehensive validation testing[/#B3B8C0]
    

    
    
    """
    
    
    # Store global options in context for use by commands
    

    pass

# Replace the version placeholder with dynamic version in the main command docstring




# Built-in upgrade command (enabled by default)

@main.command()
@click.option('--check', is_flag=True, help='Check for updates without installing')
@click.option('--version', type=str, help='Install specific version')
@click.option('--pre', is_flag=True, help='Include pre-release versions')
@click.option('--dry-run', is_flag=True, help='Show what would be done without doing it')
def upgrade(check, version, pre, dry_run):
    """Upgrade Complex Test CLI to the latest version."""
    builtin_upgrade_command(check_only=check, version=version, pre=pre, dry_run=dry_run)




@main.command()
@click.pass_context


@click.option("-i", "--input",
    type=str,
    help="Input file path"
)

@click.option("-o", "--output",
    type=str,
    default="output.txt",
    help="Output file path"
)

@click.option("--format",
    type=click.Choice(['json', 'xml', 'csv']),
    default="json",
    help="Output format"
)

@click.option("--threads",
    type=int,
    default=4,
    help="Number of threads"
)

@click.option("--enable-cache",
    is_flag=True,
    help="Enable caching"
)

def process(ctx, input, output, format, threads, enable_cache):
    """Process data with various options"""
    
    # Check for built-in commands first
    
    # Standard command - use the existing hook pattern
    hook_name = f"on_process"
    if app_hooks and hasattr(app_hooks, hook_name):
        # Call the hook with all parameters
        hook_func = getattr(app_hooks, hook_name)
        
        # Prepare arguments including global options
        kwargs = {}
        kwargs['command_name'] = 'process'  # Pass command name for all commands
        
        
        
        
        
        
        kwargs['input'] = input
        
        
        
        
        kwargs['output'] = output
        
        
        
        
        kwargs['format'] = format
        
        
        
        
        kwargs['threads'] = threads
        
        
        
        
        kwargs['enable_cache'] = enable_cache
        
        
        
        # Add global options from context
        
        
        result = hook_func(**kwargs)
        return result
    else:
        # Default placeholder behavior
        click.echo(f"Executing process command...")
        
        
        
        click.echo(f"  input: {input}")
        
        click.echo(f"  output: {output}")
        
        click.echo(f"  format: {format}")
        
        click.echo(f"  threads: {threads}")
        
        click.echo(f"  enable-cache: {enable_cache}")
        
        
    
    




@main.group()
def server():
    """Server management commands"""
    pass


@server.command()
@click.pass_context


@click.option("-p", "--port",
    type=int,
    default=8080,
    help="Server port"
)

@click.option("--host",
    type=str,
    default="localhost",
    help="Server host"
)

def start(ctx, port, host):
    """Start the server"""
    # Check if hook function exists
    hook_name = f"on_server_start"
    if app_hooks and hasattr(app_hooks, hook_name):
        # Call the hook with all parameters
        hook_func = getattr(app_hooks, hook_name)
        
        # Prepare arguments including global options
        kwargs = {}
        kwargs['command_name'] = 'start'  # Pass command name for all commands
        
        
        
        kwargs['port'] = port
        
        kwargs['host'] = host
        
        
        
        # Add global options from context
        
        
        result = hook_func(**kwargs)
        return result
    else:
        # Default placeholder behavior
        click.echo(f"Executing start command...")
        
        
        
        click.echo(f"  port: {port}")
        
        click.echo(f"  host: {host}")
        
        

@server.command()
@click.pass_context


def stop(ctx):
    """Stop the server"""
    # Check if hook function exists
    hook_name = f"on_server_stop"
    if app_hooks and hasattr(app_hooks, hook_name):
        # Call the hook with all parameters
        hook_func = getattr(app_hooks, hook_name)
        
        # Prepare arguments including global options
        kwargs = {}
        kwargs['command_name'] = 'stop'  # Pass command name for all commands
        
        
        
        # Add global options from context
        
        
        result = hook_func(**kwargs)
        return result
    else:
        # Default placeholder behavior
        click.echo(f"Executing stop command...")
        
        

@server.command()
@click.pass_context


def status(ctx):
    """Check server status"""
    # Check if hook function exists
    hook_name = f"on_server_status"
    if app_hooks and hasattr(app_hooks, hook_name):
        # Call the hook with all parameters
        hook_func = getattr(app_hooks, hook_name)
        
        # Prepare arguments including global options
        kwargs = {}
        kwargs['command_name'] = 'status'  # Pass command name for all commands
        
        
        
        # Add global options from context
        
        
        result = hook_func(**kwargs)
        return result
    else:
        # Default placeholder behavior
        click.echo(f"Executing status command...")
        
        














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
    click.echo(f"   complex-test-cli completion generate {shell} > completion.{shell}")
    click.echo(f"   cp completion.{shell} {instructions['user_script_path']}")
    click.echo()
    
    click.echo("🌐 System-wide installation:")
    click.echo(f"   complex-test-cli completion generate {shell} > completion.{shell}")
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