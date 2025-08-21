#!/usr/bin/env python3
"""
THIS FILE IS AUTO-GENERATED - DO NOT EDIT MANUALLY

Generated from: test_python_2level.yaml
To regenerate: goobits build --universal-templates

Any manual changes will be lost on regeneration.
"""

import rich_click as click
from rich_click import RichGroup
import sys
import traceback
import inspect
import builtins
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

# Helper function to convert file path to Python import path
def _path_to_import_path(file_path: str, package_name: str = "nodejs_test_cli") -> tuple[str, str]:
    """Convert a file path like 'mypackage/cli/hooks.py' to import path 'mypackage.cli.hooks'"""
    # Remove .py extension
    clean_path = file_path.replace(".py", "")
    
    # Convert forward slashes to dots for Python import
    import_path = clean_path.replace("/", ".")
    
    # Remove 'src.' prefix if present
    if import_path.startswith("src."):
        import_path = import_path[4:]
    
    # Extract just the module name (e.g., 'hooks' from 'mypackage.cli.hooks')
    module_name = import_path.split(".")[-1]
    
    return import_path, module_name

# Robust hook discovery function with package-relative imports
def _find_and_import_hooks():
    """Find and import hooks using package-relative imports with filesystem fallback"""
    import importlib
    import importlib.util
    from pathlib import Path
    
# No hooks path configured, try default locations
    default_module_name = "app_hooks"
    
    # Strategy 1: Try package-relative import
    try:
        return importlib.import_module(f"nodejs_test_cli.{default_module_name}")
    except ImportError:
        pass
    
    # Strategy 2: Try relative import
    try:
        return importlib.import_module(f".{default_module_name}", package="nodejs_test_cli")
    except ImportError:
        pass
    
    # Strategy 3: Try direct import from Python path
    try:
        return importlib.import_module(default_module_name)
    except ImportError:
        pass
    
    # Strategy 4: File-based fallback for development
    try:
        cli_dir = Path(__file__).parent
        search_paths = [
            cli_dir / f"{default_module_name}.py",
            cli_dir.parent / f"{default_module_name}.py",
            cli_dir.parent.parent / f"{default_module_name}.py",
            cli_dir.parent.parent.parent / f"{default_module_name}.py",
        ]
        
        for hooks_file in search_paths:
            if hooks_file.exists():
                spec = importlib.util.spec_from_file_location(default_module_name, hooks_file)
                if spec and spec.loader:
                    hooks_module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(hooks_module)
                    return hooks_module
    except Exception:
        pass
    
    return None

hooks = _find_and_import_hooks()

def get_version():
    """Get version from package metadata or pyproject.toml"""
    # First try to get version from installed package metadata
    try:
        from importlib.metadata import version, PackageNotFoundError
        try:
            # Try the package name
            return version("nodejs-test-cli")
        except PackageNotFoundError:
            pass
    except ImportError:
        # Python < 3.8
        try:
            import pkg_resources
            return pkg_resources.get_distribution("nodejs-test-cli").version
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
        formatter.write_usage(f"nodejstestcli v{get_version()}", " ".join(pieces))
    
    def format_help(self, ctx, formatter):
        """Override to add spacing after help."""
        super().format_help(ctx, formatter)
        formatter.write("\n")

@click.group(cls=VersionedRichGroup)
@click.version_option(version=get_version(), prog_name=f"nodejstestcli v{get_version()}")
@click.option(
    "--verbose", "-v",
    help="Enable verbose error output and debugging information",
    is_flag=True,
    default=False
)
@click.option(
    "--verbose", "-v",
    help="Enable verbose logging",
    is_flag=True,)
@click.option(
    "--config", "-c",
    help="Path to configuration file",)
@click.option(
    "--interactive", "-i",
    help="None",
    is_flag=True,    default=False,)
@click.pass_context
def main(ctx, verbose, verbose, config, interactive):
    """A comprehensive Node.js CLI for testing all features.

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
    """Upgrade NodeJSTestCLI to the latest version"""
    import subprocess
    import shutil
    from pathlib import Path
    
    package_name = "nodejs-test-cli"
    command_name = "nodejstestcli"
    display_name = "NodeJSTestCLI"
    
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
    "--template", "-t",
    help="Project template to use",
    default='default')
@click.option(
    "--skip-install",
    help="Skip npm install",
    is_flag=True)
@click.pass_context
def init(ctx, name, template, skip_install):
    """Initialize a new project"""
    
    # Enhanced error handling for Python CLI
    verbose_path = ['verbose']
    current_ctx = ctx
    verbose = False
    
    # Navigate up the context chain to find verbose flag
    while current_ctx:
        if hasattr(current_ctx, 'params') and 'verbose' in current_ctx.params:
            verbose = current_ctx.params['verbose']
            break
        current_ctx = current_ctx.parent
    
    try:
        if hooks is None:
            # Provide helpful error with search paths
            package_name = "nodejs-test-cli"
            
            error_msg = f"Hook implementation not found. Expected: app_hooks.py"
            
            raise ConfigError(
                error_msg,
                suggestion=f"Create app_hooks.py with function: def on_init(...): pass"
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
        args = [name]
        options = {
'template': template,
'skip_install': skip_install}
        
        # Execute the hook function with signature-aware parameter filtering
        sig = inspect.signature(hook_function)
        expected_params = builtins.set(sig.parameters.keys())
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
            click.echo(f"Command 'init' failed with exit code {result}", err=True)
            sys.exit(result)
            
    except KeyboardInterrupt:
        click.echo("\\n⚠️  Command interrupted by user", err=True)
        sys.exit(130)
        
    except Exception as e:
        exit_code = handle_cli_error(e, verbose)
        sys.exit(exit_code)
@main.command()
@click.argument('ENVIRONMENT')
@click.option(
    "--force", "-f",
    help="Force deployment without confirmation",
    is_flag=True)
@click.option(
    "--dry-run",
    help="Simulate deployment without making changes",
    is_flag=True)
@click.pass_context
def deploy(ctx, environment, force, dry_run):
    """Deploy the application"""
    
    # Enhanced error handling for Python CLI
    verbose_path = ['verbose']
    current_ctx = ctx
    verbose = False
    
    # Navigate up the context chain to find verbose flag
    while current_ctx:
        if hasattr(current_ctx, 'params') and 'verbose' in current_ctx.params:
            verbose = current_ctx.params['verbose']
            break
        current_ctx = current_ctx.parent
    
    try:
        if hooks is None:
            # Provide helpful error with search paths
            package_name = "nodejs-test-cli"
            
            error_msg = f"Hook implementation not found. Expected: app_hooks.py"
            
            raise ConfigError(
                error_msg,
                suggestion=f"Create app_hooks.py with function: def on_deploy(...): pass"
            )
        
        hook_name = 'on_deploy'
        if not hasattr(hooks, hook_name):
            available_hooks = [name for name in dir(hooks) if not name.startswith('_') and callable(getattr(hooks, name))]
            raise ConfigError(
                f"Hook function '{hook_name}' not found in app_hooks.py",
                suggestion=f"Available functions: {', '.join(available_hooks) if available_hooks else 'none'}"
            )
        
        hook_function = getattr(hooks, hook_name)
        
        # Prepare arguments and options for the hook
        args = [environment]
        options = {
'force': force,
'dry_run': dry_run}
        
        # Execute the hook function with signature-aware parameter filtering
        sig = inspect.signature(hook_function)
        expected_params = builtins.set(sig.parameters.keys())
        accepts_kwargs = any(p.kind == p.VAR_KEYWORD for p in sig.parameters.values())
        
        # Build kwargs with parameters the function expects
        call_kwargs = {}
        
        # Add positional arguments as kwargs if function expects them
        if 'environment' in expected_params or accepts_kwargs:
            call_kwargs['environment'] = environment
        
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
            click.echo(f"Command 'deploy' failed with exit code {result}", err=True)
            sys.exit(result)
            
    except KeyboardInterrupt:
        click.echo("\\n⚠️  Command interrupted by user", err=True)
        sys.exit(130)
        
    except Exception as e:
        exit_code = handle_cli_error(e, verbose)
        sys.exit(exit_code)
@main.group()
@click.pass_context
def server(ctx):
    """Server management commands"""
    
    # This is a group command - subcommands will handle the actual logic
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())

@server.command()
@click.option(
    "--port", "-p",
    help="Port to listen on",
    default=8080)
@click.option(
    "--daemon", "-d",
    help="Run as daemon",
    is_flag=True)
@click.pass_context
def start(ctx, port, daemon):
    """Start the server"""
    
    # Enhanced error handling for Python CLI
    verbose_path = ['verbose']
    current_ctx = ctx
    verbose = False
    
    # Navigate up the context chain to find verbose flag
    while current_ctx:
        if hasattr(current_ctx, 'params') and 'verbose' in current_ctx.params:
            verbose = current_ctx.params['verbose']
            break
        current_ctx = current_ctx.parent
    
    try:
        if hooks is None:
            # Provide helpful error with search paths
            package_name = "nodejs-test-cli"
            
            error_msg = f"Hook implementation not found. Expected: app_hooks.py"
            
            raise ConfigError(
                error_msg,
                suggestion=f"Create app_hooks.py with function: def on_server_start(...): pass"
            )
        
        hook_name = 'on_server_start'
        if not hasattr(hooks, hook_name):
            available_hooks = [name for name in dir(hooks) if not name.startswith('_') and callable(getattr(hooks, name))]
            raise ConfigError(
                f"Hook function '{hook_name}' not found in app_hooks.py",
                suggestion=f"Available functions: {', '.join(available_hooks) if available_hooks else 'none'}"
            )
        
        hook_function = getattr(hooks, hook_name)
        
        # Prepare arguments and options for the hook
        args = []
        options = {
'port': port,
'daemon': daemon}
        
        # Execute the hook function with signature-aware parameter filtering
        sig = inspect.signature(hook_function)
        expected_params = builtins.set(sig.parameters.keys())
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
            click.echo(f"Command 'server start' failed with exit code {result}", err=True)
            sys.exit(result)
            
    except KeyboardInterrupt:
        click.echo("\\n⚠️  Command interrupted by user", err=True)
        sys.exit(130)
        
    except Exception as e:
        exit_code = handle_cli_error(e, verbose)
        sys.exit(exit_code)
@server.command()
@click.option(
    "--graceful",
    help="Graceful shutdown",
    is_flag=True)
@click.pass_context
def stop(ctx, graceful):
    """Stop the server"""
    
    # Enhanced error handling for Python CLI
    verbose_path = ['verbose']
    current_ctx = ctx
    verbose = False
    
    # Navigate up the context chain to find verbose flag
    while current_ctx:
        if hasattr(current_ctx, 'params') and 'verbose' in current_ctx.params:
            verbose = current_ctx.params['verbose']
            break
        current_ctx = current_ctx.parent
    
    try:
        if hooks is None:
            # Provide helpful error with search paths
            package_name = "nodejs-test-cli"
            
            error_msg = f"Hook implementation not found. Expected: app_hooks.py"
            
            raise ConfigError(
                error_msg,
                suggestion=f"Create app_hooks.py with function: def on_server_stop(...): pass"
            )
        
        hook_name = 'on_server_stop'
        if not hasattr(hooks, hook_name):
            available_hooks = [name for name in dir(hooks) if not name.startswith('_') and callable(getattr(hooks, name))]
            raise ConfigError(
                f"Hook function '{hook_name}' not found in app_hooks.py",
                suggestion=f"Available functions: {', '.join(available_hooks) if available_hooks else 'none'}"
            )
        
        hook_function = getattr(hooks, hook_name)
        
        # Prepare arguments and options for the hook
        args = []
        options = {
'graceful': graceful}
        
        # Execute the hook function with signature-aware parameter filtering
        sig = inspect.signature(hook_function)
        expected_params = builtins.set(sig.parameters.keys())
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
            click.echo(f"Command 'server stop' failed with exit code {result}", err=True)
            sys.exit(result)
            
    except KeyboardInterrupt:
        click.echo("\\n⚠️  Command interrupted by user", err=True)
        sys.exit(130)
        
    except Exception as e:
        exit_code = handle_cli_error(e, verbose)
        sys.exit(exit_code)
@server.command()
@click.argument('SERVICE', required=False)
@click.pass_context
def restart(ctx, service):
    """Restart the server"""
    
    # Enhanced error handling for Python CLI
    verbose_path = ['verbose']
    current_ctx = ctx
    verbose = False
    
    # Navigate up the context chain to find verbose flag
    while current_ctx:
        if hasattr(current_ctx, 'params') and 'verbose' in current_ctx.params:
            verbose = current_ctx.params['verbose']
            break
        current_ctx = current_ctx.parent
    
    try:
        if hooks is None:
            # Provide helpful error with search paths
            package_name = "nodejs-test-cli"
            
            error_msg = f"Hook implementation not found. Expected: app_hooks.py"
            
            raise ConfigError(
                error_msg,
                suggestion=f"Create app_hooks.py with function: def on_server_restart(...): pass"
            )
        
        hook_name = 'on_server_restart'
        if not hasattr(hooks, hook_name):
            available_hooks = [name for name in dir(hooks) if not name.startswith('_') and callable(getattr(hooks, name))]
            raise ConfigError(
                f"Hook function '{hook_name}' not found in app_hooks.py",
                suggestion=f"Available functions: {', '.join(available_hooks) if available_hooks else 'none'}"
            )
        
        hook_function = getattr(hooks, hook_name)
        
        # Prepare arguments and options for the hook
        args = [service]
        options = {
}
        
        # Execute the hook function with signature-aware parameter filtering
        sig = inspect.signature(hook_function)
        expected_params = builtins.set(sig.parameters.keys())
        accepts_kwargs = any(p.kind == p.VAR_KEYWORD for p in sig.parameters.values())
        
        # Build kwargs with parameters the function expects
        call_kwargs = {}
        
        # Add positional arguments as kwargs if function expects them
        if 'service' in expected_params or accepts_kwargs:
            call_kwargs['service'] = service
        
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
            click.echo(f"Command 'server restart' failed with exit code {result}", err=True)
            sys.exit(result)
            
    except KeyboardInterrupt:
        click.echo("\\n⚠️  Command interrupted by user", err=True)
        sys.exit(130)
        
    except Exception as e:
        exit_code = handle_cli_error(e, verbose)
        sys.exit(exit_code)
@main.group()
@click.pass_context
def database(ctx):
    """Database operations"""
    
    # This is a group command - subcommands will handle the actual logic
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())

@database.command()
@click.option(
    "--direction",
    help="Migration direction (up/down)",
    default='up')
@click.option(
    "--steps",
    help="Number of migrations to run")
@click.pass_context
def migrate(ctx, direction, steps):
    """Run database migrations"""
    
    # Enhanced error handling for Python CLI
    verbose_path = ['verbose']
    current_ctx = ctx
    verbose = False
    
    # Navigate up the context chain to find verbose flag
    while current_ctx:
        if hasattr(current_ctx, 'params') and 'verbose' in current_ctx.params:
            verbose = current_ctx.params['verbose']
            break
        current_ctx = current_ctx.parent
    
    try:
        if hooks is None:
            # Provide helpful error with search paths
            package_name = "nodejs-test-cli"
            
            error_msg = f"Hook implementation not found. Expected: app_hooks.py"
            
            raise ConfigError(
                error_msg,
                suggestion=f"Create app_hooks.py with function: def on_database_migrate(...): pass"
            )
        
        hook_name = 'on_database_migrate'
        if not hasattr(hooks, hook_name):
            available_hooks = [name for name in dir(hooks) if not name.startswith('_') and callable(getattr(hooks, name))]
            raise ConfigError(
                f"Hook function '{hook_name}' not found in app_hooks.py",
                suggestion=f"Available functions: {', '.join(available_hooks) if available_hooks else 'none'}"
            )
        
        hook_function = getattr(hooks, hook_name)
        
        # Prepare arguments and options for the hook
        args = []
        options = {
'direction': direction,
'steps': steps}
        
        # Execute the hook function with signature-aware parameter filtering
        sig = inspect.signature(hook_function)
        expected_params = builtins.set(sig.parameters.keys())
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
            click.echo(f"Command 'database migrate' failed with exit code {result}", err=True)
            sys.exit(result)
            
    except KeyboardInterrupt:
        click.echo("\\n⚠️  Command interrupted by user", err=True)
        sys.exit(130)
        
    except Exception as e:
        exit_code = handle_cli_error(e, verbose)
        sys.exit(exit_code)
@database.command()
@click.argument('DATASET', required=False)
@click.option(
    "--truncate",
    help="Truncate tables before seeding",
    is_flag=True)
@click.pass_context
def seed(ctx, dataset, truncate):
    """Seed the database"""
    
    # Enhanced error handling for Python CLI
    verbose_path = ['verbose']
    current_ctx = ctx
    verbose = False
    
    # Navigate up the context chain to find verbose flag
    while current_ctx:
        if hasattr(current_ctx, 'params') and 'verbose' in current_ctx.params:
            verbose = current_ctx.params['verbose']
            break
        current_ctx = current_ctx.parent
    
    try:
        if hooks is None:
            # Provide helpful error with search paths
            package_name = "nodejs-test-cli"
            
            error_msg = f"Hook implementation not found. Expected: app_hooks.py"
            
            raise ConfigError(
                error_msg,
                suggestion=f"Create app_hooks.py with function: def on_database_seed(...): pass"
            )
        
        hook_name = 'on_database_seed'
        if not hasattr(hooks, hook_name):
            available_hooks = [name for name in dir(hooks) if not name.startswith('_') and callable(getattr(hooks, name))]
            raise ConfigError(
                f"Hook function '{hook_name}' not found in app_hooks.py",
                suggestion=f"Available functions: {', '.join(available_hooks) if available_hooks else 'none'}"
            )
        
        hook_function = getattr(hooks, hook_name)
        
        # Prepare arguments and options for the hook
        args = [dataset]
        options = {
'truncate': truncate}
        
        # Execute the hook function with signature-aware parameter filtering
        sig = inspect.signature(hook_function)
        expected_params = builtins.set(sig.parameters.keys())
        accepts_kwargs = any(p.kind == p.VAR_KEYWORD for p in sig.parameters.values())
        
        # Build kwargs with parameters the function expects
        call_kwargs = {}
        
        # Add positional arguments as kwargs if function expects them
        if 'dataset' in expected_params or accepts_kwargs:
            call_kwargs['dataset'] = dataset
        
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
            click.echo(f"Command 'database seed' failed with exit code {result}", err=True)
            sys.exit(result)
            
    except KeyboardInterrupt:
        click.echo("\\n⚠️  Command interrupted by user", err=True)
        sys.exit(130)
        
    except Exception as e:
        exit_code = handle_cli_error(e, verbose)
        sys.exit(exit_code)
@database.command()
@click.option(
    "--output", "-o",
    help="Output file path",
    default='./backup.sql')
@click.option(
    "--compress",
    help="Compress the backup",
    is_flag=True)
@click.pass_context
def backup(ctx, output, compress):
    """Backup the database"""
    
    # Enhanced error handling for Python CLI
    verbose_path = ['verbose']
    current_ctx = ctx
    verbose = False
    
    # Navigate up the context chain to find verbose flag
    while current_ctx:
        if hasattr(current_ctx, 'params') and 'verbose' in current_ctx.params:
            verbose = current_ctx.params['verbose']
            break
        current_ctx = current_ctx.parent
    
    try:
        if hooks is None:
            # Provide helpful error with search paths
            package_name = "nodejs-test-cli"
            
            error_msg = f"Hook implementation not found. Expected: app_hooks.py"
            
            raise ConfigError(
                error_msg,
                suggestion=f"Create app_hooks.py with function: def on_database_backup(...): pass"
            )
        
        hook_name = 'on_database_backup'
        if not hasattr(hooks, hook_name):
            available_hooks = [name for name in dir(hooks) if not name.startswith('_') and callable(getattr(hooks, name))]
            raise ConfigError(
                f"Hook function '{hook_name}' not found in app_hooks.py",
                suggestion=f"Available functions: {', '.join(available_hooks) if available_hooks else 'none'}"
            )
        
        hook_function = getattr(hooks, hook_name)
        
        # Prepare arguments and options for the hook
        args = []
        options = {
'output': output,
'compress': compress}
        
        # Execute the hook function with signature-aware parameter filtering
        sig = inspect.signature(hook_function)
        expected_params = builtins.set(sig.parameters.keys())
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
            click.echo(f"Command 'database backup' failed with exit code {result}", err=True)
            sys.exit(result)
            
    except KeyboardInterrupt:
        click.echo("\\n⚠️  Command interrupted by user", err=True)
        sys.exit(130)
        
    except Exception as e:
        exit_code = handle_cli_error(e, verbose)
        sys.exit(exit_code)
@main.command()
@click.argument('PATTERN', required=False)
@click.option(
    "--coverage",
    help="Generate coverage report",
    is_flag=True)
@click.option(
    "--watch", "-w",
    help="Watch files for changes",
    is_flag=True)
@click.option(
    "--bail",
    help="Stop on first test failure",
    is_flag=True)
@click.pass_context
def test(ctx, pattern, coverage, watch, bail):
    """Run tests"""
    
    # Enhanced error handling for Python CLI
    verbose_path = ['verbose']
    current_ctx = ctx
    verbose = False
    
    # Navigate up the context chain to find verbose flag
    while current_ctx:
        if hasattr(current_ctx, 'params') and 'verbose' in current_ctx.params:
            verbose = current_ctx.params['verbose']
            break
        current_ctx = current_ctx.parent
    
    try:
        if hooks is None:
            # Provide helpful error with search paths
            package_name = "nodejs-test-cli"
            
            error_msg = f"Hook implementation not found. Expected: app_hooks.py"
            
            raise ConfigError(
                error_msg,
                suggestion=f"Create app_hooks.py with function: def on_test(...): pass"
            )
        
        hook_name = 'on_test'
        if not hasattr(hooks, hook_name):
            available_hooks = [name for name in dir(hooks) if not name.startswith('_') and callable(getattr(hooks, name))]
            raise ConfigError(
                f"Hook function '{hook_name}' not found in app_hooks.py",
                suggestion=f"Available functions: {', '.join(available_hooks) if available_hooks else 'none'}"
            )
        
        hook_function = getattr(hooks, hook_name)
        
        # Prepare arguments and options for the hook
        args = [pattern]
        options = {
'coverage': coverage,
'watch': watch,
'bail': bail}
        
        # Execute the hook function with signature-aware parameter filtering
        sig = inspect.signature(hook_function)
        expected_params = builtins.set(sig.parameters.keys())
        accepts_kwargs = any(p.kind == p.VAR_KEYWORD for p in sig.parameters.values())
        
        # Build kwargs with parameters the function expects
        call_kwargs = {}
        
        # Add positional arguments as kwargs if function expects them
        if 'pattern' in expected_params or accepts_kwargs:
            call_kwargs['pattern'] = pattern
        
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
            click.echo(f"Command 'test' failed with exit code {result}", err=True)
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