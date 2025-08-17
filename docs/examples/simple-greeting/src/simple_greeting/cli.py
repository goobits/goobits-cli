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

# Import hooks module with enhanced error handling and path resolution
def _find_and_import_hooks():
    """Find and import hooks module from various possible locations."""
    import sys
    import os
    from pathlib import Path

    # Primary location from configuration (with backward compatibility)
    configured_hooks_path = "None"

    # Possible locations for hooks file (in order of preference)
    hook_locations = []

    # Add configured path first if available
    if configured_hooks_path:
        # Remove .py extension if present and convert to module name
        module_path = configured_hooks_path.replace('.py', '').replace('/', '.')
        hook_locations.append(configured_hooks_path.replace('.py', ''))

    # Add fallback locations
    hook_locations.extend([
        # Current directory (default)
        "app_hooks",
        # Common project patterns
        "cli/app_hooks",
        "src/app_hooks",
    ])

    # Add package-specific locations if available
    package_name = "simple-greeting"
    if package_name:
        hook_locations.extend([
            f"{package_name}/cli/app_hooks",
            f"{package_name}/app_hooks",
            f"src/{package_name}/app_hooks",
        ])

    # Ensure current working directory is in Python path for hooks
    current_dir = os.getcwd()
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)

    for location in hook_locations:
        try:
            # Handle nested module paths
            if "/" in location:
                # Add parent directory to path and import module
                parts = location.split("/")
                parent_dir = "/".join(parts[:-1])
                module_name = parts[-1]

                if parent_dir and os.path.exists(parent_dir):
                    abs_parent = os.path.abspath(parent_dir)
                    if abs_parent not in sys.path:
                        sys.path.insert(0, abs_parent)

                    imported = __import__(module_name)
                    # Verify it has expected hook functions
                    if hasattr(imported, 'on_build'):
                        return imported
            else:
                # Simple import from current directory
                imported = __import__(location)
                if hasattr(imported, 'on_build'):
                    return imported

        except ImportError:
            continue

    return None

hooks = _find_and_import_hooks()

def get_version():
    """Get version from package metadata or pyproject.toml"""
    # First try to get version from installed package metadata
    try:
        from importlib.metadata import version, PackageNotFoundError
        try:
            # Try the package name
            return version("simple-greeting")
        except PackageNotFoundError:
            pass
    except ImportError:
        # Python < 3.8
        try:
            import pkg_resources
            return pkg_resources.get_distribution("simple-greeting").version
        except:
            pass

    # Fallback to reading from pyproject.toml (development mode)
    import re
    from pathlib import Path

    try:
        # Try to get version from pyproject.toml FIRST (Python projects)
        possible_toml_paths = [
            Path(__file__).parent.parent / "pyproject.toml",  # For flat structure
            Path(__file__).parent.parent.parent / "pyproject.toml",  # For src/ structure
        ]
        for path in possible_toml_paths:
            if path.exists():
                content = path.read_text()
                match = re.search(r'version\s*=\s*["\']([^"\']+)["\']', content)
                if match:
                    return match.group(1)
    except Exception:
        pass

    try:
        # Try package.json for Node.js/TypeScript projects
        possible_json_paths = [
            Path(__file__).parent.parent / "package.json",
            Path(__file__).parent.parent.parent / "package.json",
        ]
        for path in possible_json_paths:
            if path.exists():
                import json
                with open(path) as f:
                    data = json.load(f)
                    if 'version' in data:
                        return data['version']
    except Exception:
        pass

    try:
        # Try Cargo.toml for Rust projects
        possible_cargo_paths = [
            Path(__file__).parent.parent / "Cargo.toml",
            Path(__file__).parent.parent.parent / "Cargo.toml",
        ]
        for path in possible_cargo_paths:
            if path.exists():
                content = path.read_text()
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
    return "1.0.0"

class VersionedRichGroup(RichGroup):
    def format_usage(self, ctx, formatter):
        """Override to include version in usage."""
        pieces = self.collect_usage_pieces(ctx)
        formatter.write_usage(f"greeting v{get_version()}", " ".join(pieces))

    def format_help(self, ctx, formatter):
        """Override to add spacing after help."""
        super().format_help(ctx, formatter)
        formatter.write("\n")

@click.group(cls=VersionedRichGroup)
@click.version_option(version=get_version(), prog_name=f"greeting v{get_version()}")
@click.option(
    "--verbose", "-v",
    help="Enable verbose error output and debugging information",
    is_flag=True,
    default=False
)
@click.pass_context
def main(ctx, verbose):
    """Generate friendly greetings

    \b
    [italic #B3B8C0]None[/italic #B3B8C0]

    """
    pass

# Built-in upgrade command
@main.command()
@click.option('--check', is_flag=True, help='Check for updates without installing')
@click.option('--version', type=str, help='Install specific version')
@click.option('--pre', is_flag=True, help='Include pre-release versions')
@click.option('--dry-run', is_flag=True, help='Show what would be done without doing it')
def upgrade(check, version, pre, dry_run):
    """Upgrade Simple Greeting CLI to the latest version"""
    import subprocess
    import shutil
    from pathlib import Path

    package_name = "simple-greeting"
    command_name = "greeting"
    display_name = "Simple Greeting CLI"

    # Get current version
    current_version = get_version()
    print(f"Current version: {current_version}")

    if check:
        print(f"Checking for updates to {display_name}...")
        try:
            import sys
            result = subprocess.run([
                sys.executable, '-m', 'pip', 'index', 'versions', package_name
            ], capture_output=True, text=True)
            if result.returncode == 0:
                print("Version check completed")
            else:
                print("Update check not available. Run without --check to upgrade.")
        except Exception:
            print("Update check not available. Run without --check to upgrade.")
        return

    # Detect installation method
    use_pipx = False
    if shutil.which("pipx"):
        result = subprocess.run(["pipx", "list"], capture_output=True, text=True)
        if package_name in result.stdout:
            use_pipx = True

    # Build the upgrade command
    if use_pipx:
        print(f"Upgrading {display_name} with pipx...")
        if version:
            cmd = ["pipx", "install", f"{package_name}=={version}", "--force"]
        else:
            cmd = ["pipx", "upgrade", package_name]
            if pre:
                cmd.extend(["--pip-args", "--pre"])
    else:
        print(f"Upgrading {display_name} with pip...")
        import sys
        cmd = [sys.executable, "-m", "pip", "install", "--upgrade"]
        if version:
            cmd.append(f"{package_name}=={version}")
        else:
            cmd.append(package_name)
            if pre:
                cmd.append("--pre")

    if dry_run:
        print(f"Dry run - would execute: {' '.join(cmd)}")
        return

    # Execute upgrade
    print("Upgrading...")
    result = subprocess.run(cmd)

    if result.returncode == 0:
        print(f"✅ {display_name} upgraded successfully!")
        print(f"Run '{command_name} --version' to verify the new version.")
    else:
        print(f"❌ Upgrade failed with exit code {result.returncode}")
        import sys
        sys.exit(1)
@main.command()
@click.argument('NAME')
@click.option(
    "--style", "-s",
    help="Greeting style",    default='casual',)
@click.option(
    "--repeat", "-r",
    help="Number of times to repeat greeting",    default=1,)
@click.pass_context
def hello(ctx, name, style, repeat):
    """Say hello to someone"""

    # Enhanced error handling for Python CLI
    verbose = ctx.parent.params.get('verbose', False) if ctx.parent else False

    try:
        if hooks is None:
            # Provide helpful error with search paths
            configured_path = "None"
            package_name = "simple-greeting"

            search_paths = []
            if configured_path:
                search_paths.append(f"./{configured_path}")

            search_paths.extend(["./app_hooks.py", "./cli/app_hooks.py", "./src/app_hooks.py"])
            if package_name:
                search_paths.extend([f"./{package_name}/cli/app_hooks.py", f"./{package_name}/app_hooks.py"])

            error_msg = f"Hook implementation not found. Searched in: {', '.join(search_paths)}"
            if configured_path:
                error_msg += f"\n💡 Configured cli_hooks: {configured_path}"

            raise ConfigError(
                error_msg,
                suggestion=f"Create app_hooks.py with function: def on_hello(...): pass"
            )

        hook_name = 'on_hello'
        if not hasattr(hooks, hook_name):
            available_hooks = [name for name in dir(hooks) if not name.startswith('_') and callable(getattr(hooks, name))]
            raise ConfigError(
                f"Hook function '{hook_name}' not found in app_hooks.py",
                suggestion=f"Available functions: {', '.join(available_hooks) if available_hooks else 'none'}"
            )

        hook_function = getattr(hooks, hook_name)

        # Prepare arguments and options for the hook
        args = [name]
        options = {            'style': style,            'repeat': repeat        }

        # Execute the hook function with signature-aware parameter filtering
        sig = inspect.signature(hook_function)
        expected_params = set(sig.parameters.keys())
        accepts_kwargs = any(p.kind == p.VAR_KEYWORD for p in sig.parameters.values())

        # Build kwargs with parameters the function expects
        call_kwargs = {}

        # Add positional arguments as kwargs if function expects them
        if 'name' in expected_params or accepts_kwargs:
            call_kwargs['name'] = name

        # Add options that the function expects or if it accepts **kwargs
        for param_name, param_value in options.items():
            if param_name in expected_params or accepts_kwargs:
                call_kwargs[param_name] = param_value

        # Call the hook function
        try:
            result = hook_function(**call_kwargs)
        except TypeError as te:
            raise HookError(
                f"Hook function signature mismatch: {te}",
                hook_name=hook_name
            )

        # Handle return codes
        if isinstance(result, int) and result != 0:
            click.echo(f"Command 'hello' failed with exit code {result}", err=True)
            sys.exit(result)

    except KeyboardInterrupt:
        click.echo("\\n⚠️  Command interrupted by user", err=True)
        sys.exit(130)

    except Exception as e:
        exit_code = handle_cli_error(e, verbose)
        sys.exit(exit_code)
@main.command()
@click.argument('NAME')
@click.option(
    "--polite", "-p",
    help="Use polite farewell",
    is_flag=True,)
@click.pass_context
def goodbye(ctx, name, polite):
    """Say goodbye to someone"""

    # Enhanced error handling for Python CLI
    verbose = ctx.parent.params.get('verbose', False) if ctx.parent else False

    try:
        if hooks is None:
            # Provide helpful error with search paths
            configured_path = "None"
            package_name = "simple-greeting"

            search_paths = []
            if configured_path:
                search_paths.append(f"./{configured_path}")

            search_paths.extend(["./app_hooks.py", "./cli/app_hooks.py", "./src/app_hooks.py"])
            if package_name:
                search_paths.extend([f"./{package_name}/cli/app_hooks.py", f"./{package_name}/app_hooks.py"])

            error_msg = f"Hook implementation not found. Searched in: {', '.join(search_paths)}"
            if configured_path:
                error_msg += f"\n💡 Configured cli_hooks: {configured_path}"

            raise ConfigError(
                error_msg,
                suggestion=f"Create app_hooks.py with function: def on_goodbye(...): pass"
            )

        hook_name = 'on_goodbye'
        if not hasattr(hooks, hook_name):
            available_hooks = [name for name in dir(hooks) if not name.startswith('_') and callable(getattr(hooks, name))]
            raise ConfigError(
                f"Hook function '{hook_name}' not found in app_hooks.py",
                suggestion=f"Available functions: {', '.join(available_hooks) if available_hooks else 'none'}"
            )

        hook_function = getattr(hooks, hook_name)

        # Prepare arguments and options for the hook
        args = [name]
        options = {            'polite': polite        }

        # Execute the hook function with signature-aware parameter filtering
        sig = inspect.signature(hook_function)
        expected_params = set(sig.parameters.keys())
        accepts_kwargs = any(p.kind == p.VAR_KEYWORD for p in sig.parameters.values())

        # Build kwargs with parameters the function expects
        call_kwargs = {}

        # Add positional arguments as kwargs if function expects them
        if 'name' in expected_params or accepts_kwargs:
            call_kwargs['name'] = name

        # Add options that the function expects or if it accepts **kwargs
        for param_name, param_value in options.items():
            if param_name in expected_params or accepts_kwargs:
                call_kwargs[param_name] = param_value

        # Call the hook function
        try:
            result = hook_function(**call_kwargs)
        except TypeError as te:
            raise HookError(
                f"Hook function signature mismatch: {te}",
                hook_name=hook_name
            )

        # Handle return codes
        if isinstance(result, int) and result != 0:
            click.echo(f"Command 'goodbye' failed with exit code {result}", err=True)
            sys.exit(result)

    except KeyboardInterrupt:
        click.echo("\\n⚠️  Command interrupted by user", err=True)
        sys.exit(130)

    except Exception as e:
        exit_code = handle_cli_error(e, verbose)
        sys.exit(exit_code)
@main.command()
@click.option(
    "--name", "-n",
    help="Your name",)
@click.option(
    "--role", "-r",
    help="Your role or title",    default='friend',)
@click.pass_context
def introduce(ctx, name, role):
    """Introduce yourself"""

    # Enhanced error handling for Python CLI
    verbose = ctx.parent.params.get('verbose', False) if ctx.parent else False

    try:
        if hooks is None:
            # Provide helpful error with search paths
            configured_path = "None"
            package_name = "simple-greeting"

            search_paths = []
            if configured_path:
                search_paths.append(f"./{configured_path}")

            search_paths.extend(["./app_hooks.py", "./cli/app_hooks.py", "./src/app_hooks.py"])
            if package_name:
                search_paths.extend([f"./{package_name}/cli/app_hooks.py", f"./{package_name}/app_hooks.py"])

            error_msg = f"Hook implementation not found. Searched in: {', '.join(search_paths)}"
            if configured_path:
                error_msg += f"\n💡 Configured cli_hooks: {configured_path}"

            raise ConfigError(
                error_msg,
                suggestion=f"Create app_hooks.py with function: def on_introduce(...): pass"
            )

        hook_name = 'on_introduce'
        if not hasattr(hooks, hook_name):
            available_hooks = [name for name in dir(hooks) if not name.startswith('_') and callable(getattr(hooks, name))]
            raise ConfigError(
                f"Hook function '{hook_name}' not found in app_hooks.py",
                suggestion=f"Available functions: {', '.join(available_hooks) if available_hooks else 'none'}"
            )

        hook_function = getattr(hooks, hook_name)

        # Prepare arguments and options for the hook
        args = []
        options = {            'name': name,            'role': role        }

        # Execute the hook function with signature-aware parameter filtering
        sig = inspect.signature(hook_function)
        expected_params = set(sig.parameters.keys())
        accepts_kwargs = any(p.kind == p.VAR_KEYWORD for p in sig.parameters.values())

        # Build kwargs with parameters the function expects
        call_kwargs = {}

        # Add positional arguments as kwargs if function expects them

        # Add options that the function expects or if it accepts **kwargs
        for param_name, param_value in options.items():
            if param_name in expected_params or accepts_kwargs:
                call_kwargs[param_name] = param_value

        # Call the hook function
        try:
            result = hook_function(**call_kwargs)
        except TypeError as te:
            raise HookError(
                f"Hook function signature mismatch: {te}",
                hook_name=hook_name
            )

        # Handle return codes
        if isinstance(result, int) and result != 0:
            click.echo(f"Command 'introduce' failed with exit code {result}", err=True)
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