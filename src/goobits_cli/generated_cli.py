#!/usr/bin/env python3
"""
THIS FILE IS AUTO-GENERATED - DO NOT EDIT MANUALLY

Generated from: goobits.yaml
To regenerate: goobits build --universal-templates

Any manual changes will be lost on regeneration.
"""

import rich_click as click
from rich_click import RichGroup
import sys
import traceback
import inspect
# Enhanced Error Handling Classes
class CLIError(Exception):
    """Base exception for CLI errors."""
    def __init__(self, message: str, exit_code: int = 1, suggestion: str = None):
        self.message = message
        self.exit_code = exit_code
        self.suggestion = suggestion
        super().__init__(self.message)

class ConfigError(CLIError):
    """Configuration-related error."""
    def __init__(self, message: str, suggestion: str = None):
        super().__init__(message, exit_code=2, suggestion=suggestion)

class HookError(CLIError):
    """Hook execution error."""
    def __init__(self, message: str, hook_name: str = None):
        self.hook_name = hook_name
        super().__init__(message, exit_code=3, suggestion=f"Check the '{hook_name}' function in your app_hooks.py file" if hook_name else None)

# Global error handler
def handle_cli_error(error: Exception, verbose: bool = False) -> int:
    """Handle CLI errors with appropriate messages and exit codes."""
    if isinstance(error, CLIError):
        click.echo(f"❌ Error: {error.message}", err=True)
        if error.suggestion:
            click.echo(f"💡 Suggestion: {error.suggestion}", err=True)
        if verbose and hasattr(error, '__cause__') and error.__cause__:
            click.echo(f"Details: {traceback.format_exc()}", err=True)
        return error.exit_code
    else:
        click.echo(f"❌ Unexpected error: {str(error)}", err=True)
        if verbose:
            click.echo(f"Details: {traceback.format_exc()}", err=True)
        return 1

# Set up rich-click configuration globally
click.rich_click.USE_RICH_MARKUP = True
click.rich_click.USE_MARKDOWN = False  # Disable markdown to avoid conflicts
click.rich_click.MARKUP_MODE = "rich"

# Import hooks module with enhanced error handling
try:
    import app_hooks as hooks
except ImportError:
    hooks = None

class VersionedRichGroup(RichGroup):
    def format_usage(self, ctx, formatter):
        """Override to include version in usage."""
        pieces = self.collect_usage_pieces(ctx)
        formatter.write_usage("goobits v1.2.1", " ".join(pieces))

@click.group(cls=VersionedRichGroup)
@click.version_option(version="1.2.1", prog_name="goobits v1.2.1")
@click.option(
    "--verbose", "-v",
    help="Enable verbose error output and debugging information",
    is_flag=True,
    default=False
)
@click.pass_context
def main(ctx, verbose):
    """Build professional command-line tools with YAML configuration

    \b
    [italic #B3B8C0]Transform simple YAML configuration into rich terminal applications with setup scripts, dependency management, and cross-platform compatibility.[/italic #B3B8C0]
    
    [bold yellow]🚀 Quick Start[/bold yellow]
    
    [green]   mkdir my-cli && cd my-cli  [/green] [italic][#B3B8C0]# Create new project directory[/#B3B8C0][/italic]
    
    [green]   goobits init  [/green] [italic][#B3B8C0]# Generate initial goobits.yaml[/#B3B8C0][/italic]
    
    [green]   goobits build  [/green] [italic][#B3B8C0]# Create CLI and setup scripts[/#B3B8C0][/italic]
    
    [green]   ./setup.sh install --dev  [/green] [italic][#B3B8C0]# Install for development[/#B3B8C0][/italic]
    
    [dim] [/dim]
    
    [bold yellow]💡 Core Commands[/bold yellow]
    
    [green]   build  [/green]  🔨 Generate CLI and setup scripts from goobits.yaml
    
    [green]   serve  [/green]  🌐 Serve local PyPI-compatible package index
    
    [green]   init  [/green]  🆕 Create initial goobits.yaml template
    
    [dim] [/dim]
    
    [bold yellow]🔧 Development Workflow[/bold yellow]
    
    [#B3B8C0]   1. Edit goobits.yaml: [/#B3B8C0][green]Define your CLI structure[/green]
    
    [#B3B8C0]   2. goobits build: [/#B3B8C0][green]Generate implementation files[/green]
    
    [#B3B8C0]   3. Edit app_hooks.py: [/#B3B8C0][green]Add your business logic[/green]
    
    [dim] [/dim]
    
    📚 For detailed help on a command, run: [color(2)]goobits [COMMAND][/color(2)] [#ff79c6]--help[/#ff79c6]
    """
    pass
@main.command()
@click.argument('CONFIG_PATH', required=False)
@click.option(
    "--output-dir", "-o",
    help="📁 Output directory (defaults to same directory as config file)",)
@click.option(
    "--output",
    help="📝 Output filename for generated CLI (defaults to 'generated_cli.py')",)
@click.option(
    "--backup",
    help="💾 Create backup files (.bak) when overwriting existing files",
    is_flag=True,)
@click.option(
    "--universal-templates",
    help="🧪 Use Universal Template System (experimental)",
    is_flag=True,)
@click.pass_context
def build(ctx, config_path, output_dir, output, backup, universal_templates):
    """Build CLI and setup scripts from goobits.yaml configuration"""

    # Enhanced error handling for Python CLI
    verbose = ctx.parent.params.get('verbose', False) if ctx.parent else False

    try:
        if hooks is None:
            raise ConfigError(
                "Hook implementation not found. Please create 'app_hooks.py' with your command implementations.",
                suggestion="Create app_hooks.py with function: def on_build(...): pass"
            )

        hook_name = 'on_build'
        if not hasattr(hooks, hook_name):
            available_hooks = [name for name in dir(hooks) if not name.startswith('_') and callable(getattr(hooks, name))]
            raise ConfigError(
                f"Hook function '{hook_name}' not found in app_hooks.py",
                suggestion=f"Available functions: {', '.join(available_hooks) if available_hooks else 'none'}"
            )

        hook_function = getattr(hooks, hook_name)

        # Prepare arguments and options for the hook
        args = [config_path]
        options = {            'output-dir': output_dir,            'output': output,            'backup': backup,            'universal-templates': universal_templates        }

        # Execute the hook function with proper signature detection
        sig = inspect.signature(hook_function)
        params = list(sig.parameters.keys())

        # Call function with appropriate arguments
        try:
            if len(params) == 0:
                result = hook_function()
            elif len(params) == 1 and any(keyword in params[0].lower() for keyword in ['args', 'arguments']):
                result = hook_function(args)
            elif len(params) == 1 and any(keyword in params[0].lower() for keyword in ['opts', 'options']):
                result = hook_function(options)
            else:
                # Try calling with individual arguments and options
                if args and options:
                    result = hook_function(*args, **options)
                elif args:
                    result = hook_function(*args)
                elif options:
                    result = hook_function(**options)
                else:
                    result = hook_function()
        except TypeError as te:
            raise HookError(
                f"Hook function signature mismatch: {te}",
                hook_name=hook_name
            )

        # Handle return codes
        if isinstance(result, int) and result != 0:
            click.echo(f"Command 'build' failed with exit code {result}", err=True)
            sys.exit(result)

    except KeyboardInterrupt:
        click.echo("\\n⚠️  Command interrupted by user", err=True)
        sys.exit(130)

    except Exception as e:
        exit_code = handle_cli_error(e, verbose)
        sys.exit(exit_code)
@main.command()
@click.argument('PROJECT_NAME', required=False)
@click.option(
    "--template", "-t",
    help="🎯 Template type",    default='basic',)
@click.option(
    "--force",
    help="🔥 Overwrite existing goobits.yaml file",
    is_flag=True,)
@click.pass_context
def init(ctx, project_name, template, force):
    """Create initial goobits.yaml template"""

    # Enhanced error handling for Python CLI
    verbose = ctx.parent.params.get('verbose', False) if ctx.parent else False

    try:
        if hooks is None:
            raise ConfigError(
                "Hook implementation not found. Please create 'app_hooks.py' with your command implementations.",
                suggestion="Create app_hooks.py with function: def on_init(...): pass"
            )

        hook_name = 'on_init'
        if not hasattr(hooks, hook_name):
            available_hooks = [name for name in dir(hooks) if not name.startswith('_') and callable(getattr(hooks, name))]
            raise ConfigError(
                f"Hook function '{hook_name}' not found in app_hooks.py",
                suggestion=f"Available functions: {', '.join(available_hooks) if available_hooks else 'none'}"
            )

        hook_function = getattr(hooks, hook_name)

        # Prepare arguments and options for the hook
        args = [project_name]
        options = {            'template': template,            'force': force        }

        # Execute the hook function with proper signature detection
        sig = inspect.signature(hook_function)
        params = list(sig.parameters.keys())

        # Call function with appropriate arguments
        try:
            if len(params) == 0:
                result = hook_function()
            elif len(params) == 1 and any(keyword in params[0].lower() for keyword in ['args', 'arguments']):
                result = hook_function(args)
            elif len(params) == 1 and any(keyword in params[0].lower() for keyword in ['opts', 'options']):
                result = hook_function(options)
            else:
                # Try calling with individual arguments and options
                if args and options:
                    result = hook_function(*args, **options)
                elif args:
                    result = hook_function(*args)
                elif options:
                    result = hook_function(**options)
                else:
                    result = hook_function()
        except TypeError as te:
            raise HookError(
                f"Hook function signature mismatch: {te}",
                hook_name=hook_name
            )

        # Handle return codes
        if isinstance(result, int) and result != 0:
            click.echo(f"Command 'init' failed with exit code {result}", err=True)
            sys.exit(result)

    except KeyboardInterrupt:
        click.echo("\\n⚠️  Command interrupted by user", err=True)
        sys.exit(130)

    except Exception as e:
        exit_code = handle_cli_error(e, verbose)
        sys.exit(exit_code)
@main.command()
@click.argument('DIRECTORY')
@click.option(
    "--host",
    help="🌍 Host to bind the server to",    default='localhost',)
@click.option(
    "--port", "-p",
    help="🔌 Port to run the server on",    default=8080,)
@click.pass_context
def serve(ctx, directory, host, port):
    """Serve local PyPI-compatible package index"""

    # Enhanced error handling for Python CLI
    verbose = ctx.parent.params.get('verbose', False) if ctx.parent else False

    try:
        if hooks is None:
            raise ConfigError(
                "Hook implementation not found. Please create 'app_hooks.py' with your command implementations.",
                suggestion="Create app_hooks.py with function: def on_serve(...): pass"
            )

        hook_name = 'on_serve'
        if not hasattr(hooks, hook_name):
            available_hooks = [name for name in dir(hooks) if not name.startswith('_') and callable(getattr(hooks, name))]
            raise ConfigError(
                f"Hook function '{hook_name}' not found in app_hooks.py",
                suggestion=f"Available functions: {', '.join(available_hooks) if available_hooks else 'none'}"
            )

        hook_function = getattr(hooks, hook_name)

        # Prepare arguments and options for the hook
        args = [directory]
        options = {            'host': host,            'port': port        }

        # Execute the hook function with proper signature detection
        sig = inspect.signature(hook_function)
        params = list(sig.parameters.keys())

        # Call function with appropriate arguments
        try:
            if len(params) == 0:
                result = hook_function()
            elif len(params) == 1 and any(keyword in params[0].lower() for keyword in ['args', 'arguments']):
                result = hook_function(args)
            elif len(params) == 1 and any(keyword in params[0].lower() for keyword in ['opts', 'options']):
                result = hook_function(options)
            else:
                # Try calling with individual arguments and options
                if args and options:
                    result = hook_function(*args, **options)
                elif args:
                    result = hook_function(*args)
                elif options:
                    result = hook_function(**options)
                else:
                    result = hook_function()
        except TypeError as te:
            raise HookError(
                f"Hook function signature mismatch: {te}",
                hook_name=hook_name
            )

        # Handle return codes
        if isinstance(result, int) and result != 0:
            click.echo(f"Command 'serve' failed with exit code {result}", err=True)
            sys.exit(result)

    except KeyboardInterrupt:
        click.echo("\\n⚠️  Command interrupted by user", err=True)
        sys.exit(130)

    except Exception as e:
        exit_code = handle_cli_error(e, verbose)
        sys.exit(exit_code)
if __name__ == "__main__":
    main()

def cli_entry():
    """Entry point for the CLI."""
    try:
        main()
    finally:
        # Ensure clean exit with trailing newline
        print()
