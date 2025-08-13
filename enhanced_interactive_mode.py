# Enhanced Interactive Mode with Dynamic Completion and Plugin Support
# Generated from: 

import os
import sys
import asyncio
import readline
import shlex
from typing import List, Dict, Any, Optional, Callable
from pathlib import Path
import logging
import typer

# Enhanced imports for completion and plugin systems
try:
    from goobits_cli.universal.completion import get_completion_registry
    from goobits_cli.universal.completion.integration import setup_completion_for_language
    from goobits_cli.universal.plugins import get_plugin_manager
    from goobits_cli.universal.plugins.integration import get_plugin_command_manager
    ENHANCED_FEATURES_AVAILABLE = True
except ImportError:
    ENHANCED_FEATURES_AVAILABLE = False
    logging.warning("Enhanced completion and plugin features not available")

logger = logging.getLogger(__name__)


class EnhancedInteractive:
    """
    Enhanced interactive mode with dynamic completion and plugin support.
    
    Features:
    - Dynamic contextual completion
    - Plugin command integration
    - Advanced history management
    - Multi-language support
    """
    
    def __init__(self):
        """Initialize enhanced interactive mode."""
        self.running = False
        self.history = []
        self.commands = {}
        
        # Enhanced features initialization
        if ENHANCED_FEATURES_AVAILABLE:
            self._setup_enhanced_features()
        else:
            self._setup_basic_features()
        
        # Setup command handlers
        self._setup_builtin_commands()
        
    def _setup_enhanced_features(self) -> None:
        """Setup enhanced completion and plugin features."""
        try:
            # Setup dynamic completion
            self.completion_integrator = setup_completion_for_language('python')
            
            # Setup plugin command manager  
            self.plugin_manager = get_plugin_command_manager()
            
            # Setup readline with enhanced completion
            self._setup_enhanced_readline()
            
            # Load and activate plugins
            asyncio.run(self._load_plugins())
            
            logger.info("Enhanced features initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to setup enhanced features: {e}")
            self._setup_basic_features()
    
    def _setup_basic_features(self) -> None:
        """Setup basic interactive features."""
        # Basic readline setup
        try:
            import readline
            readline.set_completer(self._basic_completer)
            readline.parse_and_bind("tab: complete")
        except ImportError:
            pass
    
    def _setup_enhanced_readline(self) -> None:
        """Setup readline with enhanced completion."""
        try:
            import readline
            
            # Create completion function
            completion_func = self.completion_integrator.create_completion_function()
            
            # Enhanced completion function that combines plugin and dynamic completion
            def enhanced_completer(text: str, state: int) -> Optional[str]:
                try:
                    # First try plugin completions
                    if hasattr(self, 'plugin_completions'):
                        plugin_results = self.plugin_completions.get(text, [])
                        if plugin_results and state < len(plugin_results):
                            return plugin_results[state]
                    
                    # Then try dynamic completion
                    return completion_func(text, state)
                    
                except Exception as e:
                    logger.debug(f"Completion error: {e}")
                    return None
            
            readline.set_completer(enhanced_completer)
            readline.parse_and_bind("tab: complete")
            
            # Enhanced readline settings
            readline.parse_and_bind("set completion-ignore-case on")
            readline.parse_and_bind("set show-all-if-ambiguous on")
            readline.parse_and_bind("set menu-complete-display-prefix on")
            
        except ImportError:
            logger.warning("readline not available, completion disabled")
    
    def _basic_completer(self, text: str, state: int) -> Optional[str]:
        """Basic completion function."""
        options = list(self.commands.keys())
        matches = [opt for opt in options if opt.startswith(text)]
        
        try:
            return matches[state]
        except IndexError:
            return None
    
    async def _load_plugins(self) -> None:
        """Load and register plugin commands."""
        try:
            # Register plugin commands
            plugin_commands = await self.plugin_manager.register_plugin_commands()
            
            # Add plugin commands to our command registry
            for command_name, plugin_info in plugin_commands.items():
                self.commands[command_name] = {
                    'handler': self._execute_plugin_command,
                    'plugin_info': plugin_info,
                    'description': f'Plugin command from {plugin_info.name}'
                }
            
            logger.info(f"Loaded {len(plugin_commands)} plugin commands")
            
        except Exception as e:
            logger.error(f"Error loading plugins: {e}")
    
    def _setup_builtin_commands(self) -> None:
        """Setup built-in interactive commands."""
        self.commands.update({
            'help': {
                'handler': self._cmd_help,
                'description': 'Show available commands'
            },
            'exit': {
                'handler': self._cmd_exit,
                'description': 'Exit interactive mode'
            },
            'quit': {
                'handler': self._cmd_exit,
                'description': 'Exit interactive mode'
            },
            'history': {
                'handler': self._cmd_history,
                'description': 'Show command history'
            },
            'clear': {
                'handler': self._cmd_clear,
                'description': 'Clear the screen'
            },
            'plugins': {
                'handler': self._cmd_plugins,
                'description': 'Manage plugins'
            },
            'completion': {
                'handler': self._cmd_completion,
                'description': 'Manage completion settings'
            }
        })
    
    async def run(self) -> None:
        """Run the enhanced interactive mode."""
        typer.echo(f"🚀 Welcome to  Enhanced Interactive Mode!")
        typer.echo("📝 Type 'help' for available commands, 'exit' to quit.")
        
        if ENHANCED_FEATURES_AVAILABLE:
            typer.echo("✨ Enhanced features: Dynamic completion and plugin support enabled")
        
        typer.echo()
        
        self.running = True
        
        while self.running:
            try:
                # Enhanced prompt with context
                prompt = self._get_enhanced_prompt()
                user_input = input(prompt).strip()
                
                if not user_input:
                    continue
                
                # Add to history
                self.history.append(user_input)
                
                # Parse and execute command
                await self._execute_command(user_input)
                
            except KeyboardInterrupt:
                typer.echo("\n⚠️  Use 'exit' to quit.")
            except EOFError:
                typer.echo("\n👋 Goodbye!")
                break
            except Exception as e:
                typer.echo(f"❌ Error: {e}")
    
    def _get_enhanced_prompt(self) -> str:
        """Get enhanced prompt with context information."""
        base_prompt = f"> "
        
        if ENHANCED_FEATURES_AVAILABLE:
            # Add context indicators
            cwd = Path.cwd().name
            return f"[{cwd}] {base_prompt}"
        
        return base_prompt
    
    async def _execute_command(self, user_input: str) -> None:
        """Execute a command with enhanced features."""
        try:
            # Parse command and arguments
            parts = shlex.split(user_input)
            command = parts[0]
            args = parts[1:] if len(parts) > 1 else []
            
            # Check if it's a registered command
            if command in self.commands:
                cmd_info = self.commands[command]
                handler = cmd_info['handler']
                
                # Execute handler
                if asyncio.iscoroutinefunction(handler):
                    await handler(args, cmd_info)
                else:
                    handler(args, cmd_info)
            else:
                # Try to execute as system command or show error
                typer.echo(f"❌ Unknown command: {command}")
                typer.echo("💡 Type 'help' to see available commands")
                
        except Exception as e:
            typer.echo(f"❌ Command execution error: {e}")
    
    async def _execute_plugin_command(self, args: List[str], cmd_info: Dict[str, Any]) -> None:
        """Execute a plugin-provided command."""
        try:
            plugin_info = cmd_info['plugin_info']
            typer.echo(f"🔌 Executing plugin command from {plugin_info.name}")
            
            # In a real implementation, this would delegate to the plugin's command handler
            typer.echo(f"⚠️  Plugin command execution not fully implemented")
            typer.echo(f"   Plugin: {plugin_info.name}")
            typer.echo(f"   Args: {args}")
            
        except Exception as e:
            typer.echo(f"❌ Plugin command error: {e}")
    
    def _cmd_help(self, args: List[str], cmd_info: Dict[str, Any]) -> None:
        """Show help information."""
        typer.echo("📚 Available Commands:")
        typer.echo()
        
        # Group commands by type
        builtin_commands = {}
        plugin_commands = {}
        
        for cmd_name, info in self.commands.items():
            if 'plugin_info' in info:
                plugin_commands[cmd_name] = info
            else:
                builtin_commands[cmd_name] = info
        
        # Show built-in commands
        if builtin_commands:
            typer.echo("🏠 Built-in Commands:")
            for cmd_name, info in builtin_commands.items():
                desc = info.get('description', 'No description')
                typer.echo(f"   {cmd_name:<15} - {desc}")
            typer.echo()
        
        # Show plugin commands
        if plugin_commands:
            typer.echo("🔌 Plugin Commands:")
            for cmd_name, info in plugin_commands.items():
                desc = info.get('description', 'No description')
                plugin_name = info['plugin_info'].name
                typer.echo(f"   {cmd_name:<15} - {desc} [{plugin_name}]")
            typer.echo()
        
        if ENHANCED_FEATURES_AVAILABLE:
            typer.echo("✨ Enhanced Features:")
            typer.echo("   - Dynamic contextual completion (Tab)")
            typer.echo("   - Plugin command support")
            typer.echo("   - Advanced history management")
    
    def _cmd_exit(self, args: List[str], cmd_info: Dict[str, Any]) -> None:
        """Exit interactive mode."""
        typer.echo("👋 Goodbye!")
        self.running = False
    
    def _cmd_history(self, args: List[str], cmd_info: Dict[str, Any]) -> None:
        """Show command history."""
        if not self.history:
            typer.echo("📝 No command history")
            return
        
        typer.echo("📝 Command History:")
        for i, cmd in enumerate(self.history[-10:], 1):  # Show last 10 commands
            typer.echo(f"   {i:2}. {cmd}")
    
    def _cmd_clear(self, args: List[str], cmd_info: Dict[str, Any]) -> None:
        """Clear the screen."""
        os.system('clear' if os.name == 'posix' else 'cls')
    
    async def _cmd_plugins(self, args: List[str], cmd_info: Dict[str, Any]) -> None:
        """Manage plugins."""
        if not ENHANCED_FEATURES_AVAILABLE:
            typer.echo("❌ Plugin features not available")
            return
        
        if not args:
            # List plugins
            try:
                manager = get_plugin_manager()
                plugins = manager.list_plugins()
                
                if not plugins:
                    typer.echo("🔌 No plugins installed")
                    return
                
                typer.echo("🔌 Installed Plugins:")
                for plugin in plugins:
                    status_icon = "✅" if plugin.status.value == 'enabled' else "❌"
                    typer.echo(f"   {status_icon} {plugin.name} v{plugin.version} - {plugin.description}")
                
            except Exception as e:
                typer.echo(f"❌ Error listing plugins: {e}")
        
        elif args[0] == 'install':
            if len(args) < 2:
                typer.echo("❌ Usage: plugins install <plugin_source>")
                return
            
            try:
                manager = get_plugin_manager()
                success = await manager.install_plugin(args[1])
                if success:
                    typer.echo(f"✅ Plugin installed successfully")
                    # Reload plugin commands
                    await self._load_plugins()
                else:
                    typer.echo(f"❌ Plugin installation failed")
            except Exception as e:
                typer.echo(f"❌ Error installing plugin: {e}")
        
        elif args[0] == 'enable':
            if len(args) < 2:
                typer.echo("❌ Usage: plugins enable <plugin_name>")
                return
            
            try:
                manager = get_plugin_manager()
                success = await manager.enable_plugin(args[1])
                if success:
                    typer.echo(f"✅ Plugin enabled successfully")
                    await self._load_plugins()
                else:
                    typer.echo(f"❌ Plugin enable failed")
            except Exception as e:
                typer.echo(f"❌ Error enabling plugin: {e}")
        
        else:
            typer.echo("❌ Unknown plugin command. Available: list, install, enable")
    
    def _cmd_completion(self, args: List[str], cmd_info: Dict[str, Any]) -> None:
        """Manage completion settings."""
        if not ENHANCED_FEATURES_AVAILABLE:
            typer.echo("❌ Enhanced completion not available")
            return
        
        if not args:
            # Show completion status
            registry = get_completion_registry()
            stats = registry.get_statistics()
            
            typer.echo("🎯 Completion System Status:")
            typer.echo(f"   Enabled: {stats['enabled']}")
            typer.echo(f"   Providers: {stats['providers_count']}")
            typer.echo(f"   Cache size: {stats['cache_size']}")
            
        elif args[0] == 'clear':
            registry = get_completion_registry()
            registry.clear_cache()
            typer.echo("✅ Completion cache cleared")
        
        else:
            typer.echo("❌ Unknown completion command. Available: status, clear")


def start_enhanced_interactive():
    """Start the enhanced interactive mode."""
    interactive = EnhancedInteractive()
    asyncio.run(interactive.run())


if __name__ == "__main__":
    start_enhanced_interactive()