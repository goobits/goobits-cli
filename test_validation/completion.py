"""
Shell completion engine for Test Python CLI
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
        script = '''#!/bin/bash
# Bash completion for testcli

_testcli_completions()
{
    local cur prev words cword
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"

    # Global options
    local global_opts="--help -h --version"

    # Subcommands
    local subcommands=" greet"

    case $COMP_CWORD in
        1)
            COMPREPLY=($(compgen -W "$subcommands $global_opts" -- "$cur"))
            ;;
        *)
            case "${words[1]}" in                greet)
                    local greet_opts="--help -h ----loud"
                    COMPREPLY=($(compgen -W "$greet_opts" -- "$cur"))
                    ;;            esac
            ;;
    esac
}

complete -F _testcli_completions testcli
'''
        return script

    def generate_zsh_completion(self) -> str:
        """Generate zsh completion script."""
        script = f'''#compdef testcli
# Zsh completion for testcli

_testcli() {
    local context state line

    _arguments -C \\
        '(--help -h){--help,-h}[Show help information]' \\
        '(--version)--version[Show version information]' \\
        '1: :_testcli_commands' \\
        '*::arg:->args'

    case $state in
        args)
            case $words[1] in                greet)
                    _arguments \\
                        '(--help -h){--help,-h}[Show help information]' \\                        '(----loud){----loud}[Greet loudly]' \\                    ;;            esac
            ;;
    esac
}

_testcli_commands() {
    local commands
    commands=(        'greet:Greet someone'    )
    _describe 'commands' commands
}

_testcli "$@"
'''
        return script

    def generate_fish_completion(self) -> str:
        """Generate fish completion script."""
        script = f'''# Fish completion for testcli

# Global options
complete -c testcli -f
complete -c testcli -s h -l help -d "Show help information"
complete -c testcli -l version -d "Show version information"

# Subcommandscomplete -c testcli -n "__fish_use_subcommand" -a "greet" -d "Greet someone"complete -c testcli -n "__fish_seen_subcommand_from greet" -l --loud -d "Greet loudly"'''
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
            filename = f'testcli.{shell}'
            if shell == 'bash':
                filename = f'testcli'

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