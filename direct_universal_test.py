#!/usr/bin/env python3
"""
Auto-generated from goobits.yaml
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

# Import hooks module with enhanced error handling
try:
    import app_hooks as hooks
except ImportError:
    hooks = None

@click.group(cls=RichGroup)
@click.version_option(version="1.0.0")
@click.option(
    "--verbose", "-v",
    help="Enable verbose error output and debugging information",
    is_flag=True,
    default=False
)
@click.pass_context
def main(ctx, verbose):
    """Build professional command-line tools with YAML configuration
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