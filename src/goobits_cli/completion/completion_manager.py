"""
Completion Manager
==================

Shell completion management system extracted from completion_manager.j2 template.
Provides multi-shell completion support with script generation and installation.
"""

import os
import sys
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Set, Any
from dataclasses import dataclass, field


class ShellType(Enum):
    """Supported shell types for completion."""
    BASH = "bash"
    ZSH = "zsh" 
    FISH = "fish"
    POWERSHELL = "powershell"
    
    @classmethod
    def detect_shell(cls) -> Optional['ShellType']:
        """Detect current shell from environment."""
        shell = os.environ.get('SHELL', '').lower()
        
        if 'bash' in shell:
            return cls.BASH
        elif 'zsh' in shell:
            return cls.ZSH
        elif 'fish' in shell:
            return cls.FISH
        elif 'powershell' in shell or 'pwsh' in shell:
            return cls.POWERSHELL
        
        return None
    
    def get_config_file(self) -> Optional[str]:
        """Get shell configuration file path."""
        home = Path.home()
        
        config_files = {
            self.BASH: [home / '.bashrc', home / '.bash_profile'],
            self.ZSH: [home / '.zshrc'],
            self.FISH: [home / '.config' / 'fish' / 'config.fish'],
            self.POWERSHELL: [home / 'Documents' / 'PowerShell' / 'profile.ps1']
        }
        
        for config_file in config_files.get(self, []):
            if config_file.exists():
                return str(config_file)
        
        # Return first option as default
        if self in config_files:
            return str(config_files[self][0])
        
        return None


@dataclass
class CompletionScript:
    """Represents a shell completion script."""
    shell: ShellType
    content: str
    install_path: Optional[str] = None
    source_line: Optional[str] = None
    
    def get_install_instructions(self) -> List[str]:
        """Get installation instructions for the completion script."""
        instructions = []
        
        if self.shell == ShellType.BASH:
            instructions.extend([
                "# Install bash completion:",
                f"# 1. Save the completion script to a file (e.g., ~/.local/share/bash-completion/completions/{self.get_script_name()})",
                "# 2. Source it in your ~/.bashrc or restart your shell",
                f"# echo 'source ~/.local/share/bash-completion/completions/{self.get_script_name()}' >> ~/.bashrc"
            ])
        elif self.shell == ShellType.ZSH:
            instructions.extend([
                "# Install zsh completion:",
                f"# 1. Add to your fpath before compinit in ~/.zshrc",
                f"# fpath=(~/.local/share/zsh/site-functions $fpath)",
                f"# 2. Save as ~/.local/share/zsh/site-functions/_{self.get_script_name()}",
                "# 3. Run 'autoload -U compinit && compinit'"
            ])
        elif self.shell == ShellType.FISH:
            instructions.extend([
                "# Install fish completion:",
                f"# Save to ~/.config/fish/completions/{self.get_script_name()}.fish",
                "# Fish will automatically load it on next shell start"
            ])
        elif self.shell == ShellType.POWERSHELL:
            instructions.extend([
                "# Install PowerShell completion:",
                "# Add to your PowerShell profile:",
                f"# . path/to/{self.get_script_name()}_completion.ps1"
            ])
        
        return instructions
    
    def get_script_name(self) -> str:
        """Get the base script name."""
        # Extract from install_path if available, otherwise use default
        if self.install_path:
            return Path(self.install_path).stem
        return "cli"


class CompletionInstaller:
    """Handles installation of completion scripts."""
    
    def __init__(self, cli_name: str):
        self.cli_name = cli_name
    
    def install_completion(self, script: CompletionScript, force: bool = False) -> bool:
        """
        Install a completion script.
        
        Args:
            script: Completion script to install
            force: Whether to overwrite existing files
            
        Returns:
            True if installation succeeded
        """
        install_path = self._get_install_path(script.shell)
        if not install_path:
            return False
        
        install_path = Path(install_path)
        
        # Create directory if it doesn't exist
        install_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Check if file already exists
        if install_path.exists() and not force:
            return False
        
        # Write completion script
        try:
            install_path.write_text(script.content)
            return True
        except (OSError, PermissionError):
            return False
    
    def _get_install_path(self, shell: ShellType) -> Optional[str]:
        """Get installation path for shell completion."""
        home = Path.home()
        
        paths = {
            ShellType.BASH: home / '.local' / 'share' / 'bash-completion' / 'completions' / self.cli_name,
            ShellType.ZSH: home / '.local' / 'share' / 'zsh' / 'site-functions' / f'_{self.cli_name}',
            ShellType.FISH: home / '.config' / 'fish' / 'completions' / f'{self.cli_name}.fish',
            ShellType.POWERSHELL: home / 'Documents' / 'PowerShell' / f'{self.cli_name}_completion.ps1'
        }
        
        return str(paths.get(shell)) if shell in paths else None
    
    def get_source_line(self, shell: ShellType) -> str:
        """Get line to add to shell config for sourcing completion."""
        install_path = self._get_install_path(shell)
        if not install_path:
            return ""
        
        if shell == ShellType.BASH:
            return f"source {install_path}"
        elif shell == ShellType.ZSH:
            return f"autoload -U compinit && compinit"
        elif shell == ShellType.FISH:
            return "# Fish auto-loads completions from ~/.config/fish/completions/"
        elif shell == ShellType.POWERSHELL:
            return f". {install_path}"
        
        return ""


class CompletionManager:
    """
    Advanced shell completion manager extracted from completion_manager.j2.
    
    Manages completion script generation, installation, and shell detection.
    """
    
    def __init__(self, cli_name: str, supported_shells: Optional[Set[ShellType]] = None):
        self.cli_name = cli_name
        self.supported_shells = supported_shells or {
            ShellType.BASH, ShellType.ZSH, ShellType.FISH, ShellType.POWERSHELL
        }
        self.installer = CompletionInstaller(cli_name)
    
    def generate_completion_scripts(self, 
                                  commands: Dict[str, Any],
                                  language: str = 'python') -> Dict[ShellType, CompletionScript]:
        """
        Generate completion scripts for all supported shells.
        
        Args:
            commands: CLI command structure
            language: Target language for completion generation
            
        Returns:
            Dictionary mapping shell types to completion scripts
        """
        scripts = {}
        
        for shell in self.supported_shells:
            script_content = self._generate_shell_script(shell, commands, language)
            
            scripts[shell] = CompletionScript(
                shell=shell,
                content=script_content,
                install_path=self.installer._get_install_path(shell),
                source_line=self.installer.get_source_line(shell)
            )
        
        return scripts
    
    def _generate_shell_script(self, shell: ShellType, commands: Dict[str, Any], language: str) -> str:
        """Generate completion script for specific shell."""
        if shell == ShellType.BASH:
            return self._generate_bash_completion(commands, language)
        elif shell == ShellType.ZSH:
            return self._generate_zsh_completion(commands, language)
        elif shell == ShellType.FISH:
            return self._generate_fish_completion(commands, language)
        elif shell == ShellType.POWERSHELL:
            return self._generate_powershell_completion(commands, language)
        else:
            return ""
    
    def _generate_bash_completion(self, commands: Dict[str, Any], language: str) -> str:
        """Generate bash completion script."""
        lines = [
            f"# Bash completion for {self.cli_name}",
            f"# Generated by Goobits CLI Framework",
            "",
            f"_{self.cli_name.replace('-', '_')}_completion() {{",
            "    local cur prev words cword",
            "    _init_completion || return",
            "",
            "    case $prev in"
        ]
        
        # Add command-specific completions
        for cmd_name, cmd_data in commands.items():
            lines.append(f"        {cmd_name})")
            lines.append(f"            COMPREPLY=($(compgen -W \"")
            
            # Add options
            options = []
            for opt in cmd_data.get('options', []):
                opt_name = opt.get('name', '')
                if opt_name.startswith('--'):
                    options.append(opt_name)
                elif opt_name.startswith('-'):
                    options.append(opt_name)
            
            if options:
                lines.append(' '.join(options) + "\" -- \"$cur\"))")
            else:
                lines.append("\" -- \"$cur\"))")
            
            lines.append("            return 0")
            lines.append("            ;;")
        
        lines.extend([
            "    esac",
            "",
            "    # Default command completion",
            f"    COMPREPLY=($(compgen -W \"{' '.join(commands.keys())}\" -- \"$cur\"))",
            "}",
            "",
            f"complete -F _{self.cli_name.replace('-', '_')}_completion {self.cli_name}"
        ])
        
        return '\n'.join(lines)
    
    def _generate_zsh_completion(self, commands: Dict[str, Any], language: str) -> str:
        """Generate zsh completion script."""
        lines = [
            f"#compdef {self.cli_name}",
            f"# Zsh completion for {self.cli_name}",
            f"# Generated by Goobits CLI Framework",
            "",
            f"_{self.cli_name.replace('-', '_')}() {{",
            "    local context curcontext=\"$curcontext\" state line",
            "    typeset -A opt_args",
            "",
            "    _arguments -C \\"
        ]
        
        # Add global options and commands
        cmd_list = list(commands.keys())
        if cmd_list:
            lines.append(f"        '1: :_command_names' \\")
            lines.append(f"        '*::arg:->args'")
        
        lines.extend([
            "",
            "    case $state in",
            "        args)",
            "            case $line[1] in"
        ])
        
        # Add command-specific completions
        for cmd_name, cmd_data in commands.items():
            lines.append(f"                {cmd_name})")
            lines.append("                    _arguments \\")
            
            for opt in cmd_data.get('options', []):
                opt_name = opt.get('name', '')
                opt_desc = opt.get('description', opt.get('desc', ''))
                if opt_name:
                    lines.append(f"                        '{opt_name}[{opt_desc}]' \\")
            
            lines.append("                    ;;")
        
        lines.extend([
            "            esac",
            "            ;;",
            "    esac",
            "}",
            "",
            f"_{self.cli_name.replace('-', '_')} \"$@\""
        ])
        
        return '\n'.join(lines)
    
    def _generate_fish_completion(self, commands: Dict[str, Any], language: str) -> str:
        """Generate fish completion script.""" 
        lines = [
            f"# Fish completion for {self.cli_name}",
            f"# Generated by Goobits CLI Framework",
            ""
        ]
        
        # Add command completions
        for cmd_name, cmd_data in commands.items():
            cmd_desc = cmd_data.get('description', cmd_data.get('desc', ''))
            lines.append(f"complete -c {self.cli_name} -f -a '{cmd_name}' -d '{cmd_desc}'")
            
            # Add option completions for this command
            for opt in cmd_data.get('options', []):
                opt_name = opt.get('name', '')
                opt_desc = opt.get('description', opt.get('desc', ''))
                
                if opt_name.startswith('--'):
                    lines.append(f"complete -c {self.cli_name} -f -l {opt_name[2:]} -d '{opt_desc}'")
                elif opt_name.startswith('-') and len(opt_name) == 2:
                    lines.append(f"complete -c {self.cli_name} -f -s {opt_name[1:]} -d '{opt_desc}'")
        
        return '\n'.join(lines)
    
    def _generate_powershell_completion(self, commands: Dict[str, Any], language: str) -> str:
        """Generate PowerShell completion script."""
        lines = [
            f"# PowerShell completion for {self.cli_name}",
            f"# Generated by Goobits CLI Framework",
            "",
            f"Register-ArgumentCompleter -Native -CommandName {self.cli_name} -ScriptBlock {{",
            "    param($wordToComplete, $commandAst, $cursorPosition)",
            "",
            "    $commands = @("
        ]
        
        # Add commands
        for cmd_name in commands.keys():
            lines.append(f"        '{cmd_name}'")
        
        lines.extend([
            "    )",
            "",
            "    $commands | Where-Object {",
            "        $_ -like \"$wordToComplete*\"",
            "    } | ForEach-Object {",
            "        New-Object System.Management.Automation.CompletionResult $_, $_, 'ParameterValue', $_",
            "    }",
            "}"
        ])
        
        return '\n'.join(lines)
    
    def detect_available_shells(self) -> List[ShellType]:
        """Detect which shells are available on the system."""
        available = []
        
        shell_commands = {
            ShellType.BASH: 'bash',
            ShellType.ZSH: 'zsh', 
            ShellType.FISH: 'fish',
            ShellType.POWERSHELL: 'pwsh'
        }
        
        for shell_type, command in shell_commands.items():
            if self._command_exists(command):
                available.append(shell_type)
        
        return available
    
    def _command_exists(self, command: str) -> bool:
        """Check if a command exists in PATH."""
        from shutil import which
        return which(command) is not None
    
    def install_completions(self, 
                          scripts: Dict[ShellType, CompletionScript],
                          shells: Optional[List[ShellType]] = None,
                          force: bool = False) -> Dict[ShellType, bool]:
        """
        Install completion scripts for specified shells.
        
        Args:
            scripts: Generated completion scripts
            shells: Shells to install for (None = all available)
            force: Whether to overwrite existing scripts
            
        Returns:
            Dictionary mapping shells to installation success
        """
        if shells is None:
            shells = self.detect_available_shells()
        
        results = {}
        
        for shell in shells:
            if shell in scripts:
                results[shell] = self.installer.install_completion(scripts[shell], force)
            else:
                results[shell] = False
        
        return results
    
    def get_installation_report(self, 
                              install_results: Dict[ShellType, bool],
                              scripts: Dict[ShellType, CompletionScript]) -> str:
        """Generate installation report."""
        lines = [
            f"Completion Installation Report for {self.cli_name}",
            "=" * 50,
            ""
        ]
        
        for shell, success in install_results.items():
            status = "✅ SUCCESS" if success else "❌ FAILED"
            lines.append(f"{shell.value.upper()}: {status}")
            
            if success and shell in scripts:
                script = scripts[shell]
                lines.extend([
                    f"  Install path: {script.install_path}",
                    f"  Instructions:"
                ])
                
                for instruction in script.get_install_instructions():
                    lines.append(f"    {instruction}")
            
            lines.append("")
        
        return '\n'.join(lines)