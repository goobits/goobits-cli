"""
Shell completion engine for Minimal Test CLI
"""

import os
import sys
from typing import List, Dict, Any

class CompletionEngine:
    """Handles shell completion for CLI commands."""

    def __init__(self, cli_schema: Dict[str, Any]):
        self.cli_schema = cli_schema

    def generate_bash_completion(self) -> str:
        """Generate bash completion script."""
        script = f'''#!/bin/bash
# Bash completion for Minimal Test CLI

_Minimal Test CLI_completions()
{
    local cur prev words cword
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"

    # Global options
    local global_opts="--help -h --version"

    # Subcommands
    local subcommands=" hello"

    case $COMP_CWORD in
        1)
            COMPREPLY=($(compgen -W "$subcommands $global_opts" -- "$cur"))
            ;;
        *)
            case "$words[1]" in                hello)
                    local hello_opts="--help -h --name"
                    COMPREPLY=($(compgen -W "$hello_opts" -- "$cur"))
                    ;;            esac
            ;;
    esac
}

complete -F _Minimal Test CLI_completions Minimal Test CLI
'''
        return script

    def generate_zsh_completion(self) -> str:
        """Generate zsh completion script."""
        script = f'''#compdef Minimal Test CLI
# Zsh completion for Minimal Test CLI

_Minimal Test CLI() {
    local context state line

    _arguments -C \\
        '(--help -h){--help,-h}[Show help information]' \\
        '(--version)--version[Show version information]' \\
        '1: :_Minimal Test CLI_commands' \\
        '*::arg:->args'

    case $state in
        args)
            case $words[1] in                hello)
                    _arguments \\
                        '(--help -h){--help,-h}[Show help information]' \\                        '(--name){--name}[Name to greet]' \\                    ;;            esac
            ;;
    esac
}

_Minimal Test CLI_commands() {
    local commands
    commands=(        'hello:Say hello to someone'    )
    _describe 'commands' commands
}

_Minimal Test CLI "$@"
'''
        return script

    def generate_fish_completion(self) -> str:
        """Generate fish completion script."""
        script = f'''# Fish completion for Minimal Test CLI

# Global options
complete -c Minimal Test CLI -f
complete -c Minimal Test CLI -s h -l help -d "Show help information"
complete -c Minimal Test CLI -l version -d "Show version information"

# Subcommandscomplete -c Minimal Test CLI -n "__fish_use_subcommand" -a "hello" -d "Say hello to someone"complete -c Minimal Test CLI -n "__fish_seen_subcommand_from hello" -l name -d "Name to greet"'''
        return script

    def install_completion(self, shell: str = None) -> bool:
        """Install completion script for the specified shell."""
        if shell is None:
            shell = os.environ.get('SHELL', '').split('/')[-1]

        if shell == 'bash':
            script = self.generate_bash_completion()
            completion_dir = os.path.expanduser('~/.bash_completion.d')
        elif shell == 'zsh':
            script = self.generate_zsh_completion()
            completion_dir = os.path.expanduser('~/.zsh/completions')
        elif shell == 'fish':
            script = self.generate_fish_completion()
            completion_dir = os.path.expanduser('~/.config/fish/completions')
        else:
            print(f"Unsupported shell: {shell}")
            return False

        try:
            os.makedirs(completion_dir, exist_ok=True)
            filename = f'Minimal Test CLI.{shell}'
            if shell == 'bash':
                filename = f'Minimal Test CLI'

            filepath = os.path.join(completion_dir, filename)
            with open(filepath, 'w') as f:
                f.write(script)

            print(f"Completion script installed: {filepath}")
            if shell == 'bash':
                print("Please restart your terminal or run: source ~/.bashrc")
            elif shell == 'zsh':
                print("Please restart your terminal or add to ~/.zshrc: fpath=(~/.zsh/completions $fpath)")

            return True
        except Exception as e:
            print(f"Failed to install completion: {e}")
            return False