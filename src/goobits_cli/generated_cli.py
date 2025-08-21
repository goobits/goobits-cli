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

# Helper function to convert file path to Python import path
def _path_to_import_path(file_path: str, package_name: str = "goobits-cli") -> tuple[str, str]:
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
    
# Using configured hooks path: app_hooks.py
    configured_path = "app_hooks.py"
    import_path, module_name = _path_to_import_path(configured_path)
    
    # Strategy 1: Try package-relative import (works from any directory when installed)
    try:
        return importlib.import_module(import_path)
    except ImportError:
        pass
    
    # Strategy 2: Try relative import from current package
    try:
        if "." in import_path:
            # Try importing from the base package
            package_parts = import_path.split(".")
            if len(package_parts) >= 2:
                relative_import = ".".join(package_parts[1:])  # Remove package name
                return importlib.import_module(f".{relative_import}", package="goobits-cli")
        else:
            # Direct relative import
            return importlib.import_module(f".{module_name}", package="goobits-cli")
    except ImportError:
        pass
    
    # Strategy 3: Try direct module name import (for simple cases)
    try:
        return importlib.import_module(module_name)
    except ImportError:
        pass
    
    # Strategy 4: File-based import as fallback (development mode)
    try:
        # Look for the file relative to the CLI script location
        cli_dir = Path(__file__).parent
        
        # Try multiple possible locations relative to CLI
        search_paths = [
            cli_dir / configured_path,                    # Same directory as CLI
            cli_dir.parent / configured_path,             # Parent of CLI directory  
            cli_dir.parent.parent / configured_path,      # Two levels up (src structure)
            cli_dir.parent.parent.parent / configured_path, # Three levels up (deep structure)
        ]
        
        for hooks_file in search_paths:
            if hooks_file.exists():
                spec = importlib.util.spec_from_file_location(module_name, hooks_file)
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
            return version("goobits-cli")
        except PackageNotFoundError:
            pass
    except ImportError:
        # Python < 3.8
        try:
            import pkg_resources
            return pkg_resources.get_distribution("goobits-cli").version
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
        formatter.write_usage(f"goobits v{get_version()}", " ".join(pieces))
    
    def format_help(self, ctx, formatter):
        """Override to add spacing after help."""
        super().format_help(ctx, formatter)
        formatter.write("\n")

@click.group(cls=VersionedRichGroup)
@click.version_option(version=get_version(), prog_name=f"goobits v{get_version()}")
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
    
[green]   mkdir my-cli && cd my-cli  [/green]   [italic][#B3B8C0]# Create new project directory[/#B3B8C0][/italic]
    
[green]   goobits init               [/green]   [italic][#B3B8C0]# Generate initial goobits.yaml[/#B3B8C0][/italic]
    
[green]   goobits build              [/green]   [italic][#B3B8C0]# Create CLI and setup scripts[/#B3B8C0][/italic]
    
[green]   ./setup.sh install --dev   [/green]   [italic][#B3B8C0]# Install for development[/#B3B8C0][/italic]
    
    [dim] [/dim]
    
    [bold yellow]💡 Core Commands[/bold yellow]
    
[green]   build[/green]   🔨 Generate CLI and setup scripts from goobits.yaml
    
[green]   serve[/green]   🌐 Serve local PyPI-compatible package index
    
[green]   init [/green]   🆕 Create initial goobits.yaml template
    
    [dim] [/dim]
    
    [bold yellow]🔧 Development Workflow[/bold yellow]
    
[#B3B8C0]   1. Edit goobits.yaml:  [/#B3B8C0]   [green]Define your CLI structure[/green]
    
[#B3B8C0]   2. goobits build:      [/#B3B8C0]   [green]Generate implementation files[/green]
    
[#B3B8C0]   3. Edit app_hooks.py:  [/#B3B8C0]   [green]Add your business logic[/green]
    
    [dim] [/dim]
    
    📚 For detailed help on a command, run: [color(2)]goobits [COMMAND][/color(2)] [#ff79c6]--help[/#ff79c6]
    """
    pass

# Built-in upgrade command
@main.command()
@click.option('--check', is_flag=True, help='Check for updates without installing')
@click.option('--version', type=str, help='Install specific version')
@click.option('--pre', is_flag=True, help='Include pre-release versions')
@click.option('--dry-run', is_flag=True, help='Show what would be done without doing it')
def upgrade(check, version, pre, dry_run):
    """Upgrade Goobits CLI Framework to the latest version"""
    import subprocess
    import shutil
    from pathlib import Path
    
    package_name = "goobits-cli"
    command_name = "goobits"
    display_name = "Goobits CLI Framework"
    
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
@click.argument('CONFIG_PATH', required=False)
@click.option(
    "--output-dir", "-o",
    help="📁 Output directory (defaults to same directory as config file)")
@click.option(
    "--output",
    help="📝 Output filename for generated CLI (defaults to 'generated_cli.py')")
@click.option(
    "--backup",
    help="💾 Create backup files (.bak) when overwriting existing files",
    is_flag=True)
@click.option(
    "--universal-templates",
    help="🧪 Use Universal Template System (experimental)",
    is_flag=True)
@click.pass_context
def build(ctx, config_path, output_dir, output, backup, universal_templates):
    """Build CLI and setup scripts from goobits.yaml configuration"""    # Enhanced error handling for Python CLI
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
            package_name = "goobits-cli"
            
            error_msg = f"Hook implementation not found. Expected: app_hooks.py"
            
            raise ConfigError(
                error_msg,
                suggestion=f"Create app_hooks.py with function: def on_build(...): pass"
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
        options = {            'output_dir': output_dir,            'output': output,            'backup': backup,            'universal_templates': universal_templates        }
        
        # Execute the hook function with signature-aware parameter filtering
        sig = inspect.signature(hook_function)
        expected_params = set(sig.parameters.keys())
        accepts_kwargs = any(p.kind == p.VAR_KEYWORD for p in sig.parameters.values())
        
        # Build kwargs with parameters the function expects
        call_kwargs = {}
        
        # Add positional arguments as kwargs if function expects them
        if 'config_path' in expected_params or accepts_kwargs:
            call_kwargs['config_path'] = config_path
        
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
    help="🎯 Template type",
    default='basic')
@click.option(
    "--force",
    help="🔥 Overwrite existing goobits.yaml file",
    is_flag=True)
@click.pass_context
def init(ctx, project_name, template, force):
    """Create initial goobits.yaml template"""    # Enhanced error handling for Python CLI
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
            package_name = "goobits-cli"
            
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
        args = [project_name]
        options = {            'template': template,            'force': force        }
        
        # Execute the hook function with signature-aware parameter filtering
        sig = inspect.signature(hook_function)
        expected_params = set(sig.parameters.keys())
        accepts_kwargs = any(p.kind == p.VAR_KEYWORD for p in sig.parameters.values())
        
        # Build kwargs with parameters the function expects
        call_kwargs = {}
        
        # Add positional arguments as kwargs if function expects them
        if 'project_name' in expected_params or accepts_kwargs:
            call_kwargs['project_name'] = project_name
        
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
@click.argument('DIRECTORY')
@click.option(
    "--host",
    help="🌍 Host to bind the server to",
    default='localhost')
@click.option(
    "--port", "-p",
    help="🔌 Port to run the server on",
    default=8080)
@click.pass_context
def serve(ctx, directory, host, port):
    """Serve local PyPI-compatible package index"""    # Enhanced error handling for Python CLI
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
            package_name = "goobits-cli"
            
            error_msg = f"Hook implementation not found. Expected: app_hooks.py"
            
            raise ConfigError(
                error_msg,
                suggestion=f"Create app_hooks.py with function: def on_serve(...): pass"
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
        
        # Execute the hook function with signature-aware parameter filtering
        sig = inspect.signature(hook_function)
        expected_params = set(sig.parameters.keys())
        accepts_kwargs = any(p.kind == p.VAR_KEYWORD for p in sig.parameters.values())
        
        # Build kwargs with parameters the function expects
        call_kwargs = {}
        
        # Add positional arguments as kwargs if function expects them
        if 'directory' in expected_params or accepts_kwargs:
            call_kwargs['directory'] = directory
        
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