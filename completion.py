"""
Shell completion engine for Goobits CLI Framework
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
# Bash completion for Goobits CLI

_Goobits CLI_completions()
{
    local cur prev words cword
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"

    # Global options
    local global_opts="--help -h --version"

    # Subcommands
    local subcommands=" build init serve"

    case $COMP_CWORD in
        1)
            COMPREPLY=($(compgen -W "$subcommands $global_opts" -- "$cur"))
            ;;
        *)
            case "${words[1]}" in                build)
                    local build_opts="--help -h --output-dir -o --output --backup --universal-templates"
                    COMPREPLY=($(compgen -W "$build_opts" -- "$cur"))
                    ;;                init)
                    local init_opts="--help -h --template -t --force"
                    COMPREPLY=($(compgen -W "$init_opts" -- "$cur"))
                    ;;                serve)
                    local serve_opts="--help -h --host --port -p"
                    COMPREPLY=($(compgen -W "$serve_opts" -- "$cur"))
                    ;;            esac
            ;;
    esac
}

complete -F _Goobits CLI_completions Goobits CLI
'''
        return script

    def generate_zsh_completion(self) -> str:
        """Generate zsh completion script."""
        script = f'''#compdef Goobits CLI
# Zsh completion for Goobits CLI

_Goobits CLI() {
    local context state line

    _arguments -C \\
        '(--help -h){--help,-h}[Show help information]' \\
        '(--version)--version[Show version information]' \\
        '1: :_Goobits CLI_commands' \\
        '*::arg:->args'

    case $state in
        args)
            case $words[1] in                build)
                    _arguments \\
                        '(--help -h){--help,-h}[Show help information]' \\                        '(--output-dir -o){--output-dir,-o}[📁 Output directory (defaults to same directory as config file)]' \\                        '(--output){--output}[📝 Output filename for generated CLI (defaults to 'generated_cli.py')]' \\                        '(--backup){--backup}[💾 Create backup files (.bak) when overwriting existing files]' \\                        '(--universal-templates){--universal-templates}[🧪 Use Universal Template System (experimental)]' \\                        '1:config_path:_files'                    ;;                init)
                    _arguments \\
                        '(--help -h){--help,-h}[Show help information]' \\                        '(--template -t){--template,-t}[🎯 Template type]' \\                        '(--force){--force}[🔥 Overwrite existing goobits.yaml file]' \\                        '1:project_name:_files'                    ;;                serve)
                    _arguments \\
                        '(--help -h){--help,-h}[Show help information]' \\                        '(--host){--host}[🌍 Host to bind the server to]' \\                        '(--port -p){--port,-p}[🔌 Port to run the server on]' \\                        '1:directory:_files'                    ;;            esac
            ;;
    esac
}

_Goobits CLI_commands() {
    local commands
    commands=(        'build:Build CLI and setup scripts from goobits.yaml configuration'        'init:Create initial goobits.yaml template'        'serve:Serve local PyPI-compatible package index'    )
    _describe 'commands' commands
}

_Goobits CLI "$@"
'''
        return script

    def generate_fish_completion(self) -> str:
        """Generate fish completion script."""
        script = f'''# Fish completion for Goobits CLI

# Global options
complete -c Goobits CLI -f
complete -c Goobits CLI -s h -l help -d "Show help information"
complete -c Goobits CLI -l version -d "Show version information"

# Subcommandscomplete -c Goobits CLI -n "__fish_use_subcommand" -a "build" -d "Build CLI and setup scripts from goobits.yaml configuration"complete -c Goobits CLI -n "__fish_seen_subcommand_from build" -l output-dir -s o -d "📁 Output directory (defaults to same directory as config file)"complete -c Goobits CLI -n "__fish_seen_subcommand_from build" -l output -d "📝 Output filename for generated CLI (defaults to 'generated_cli.py')"complete -c Goobits CLI -n "__fish_seen_subcommand_from build" -l backup -d "💾 Create backup files (.bak) when overwriting existing files"complete -c Goobits CLI -n "__fish_seen_subcommand_from build" -l universal-templates -d "🧪 Use Universal Template System (experimental)"complete -c Goobits CLI -n "__fish_use_subcommand" -a "init" -d "Create initial goobits.yaml template"complete -c Goobits CLI -n "__fish_seen_subcommand_from init" -l template -s t -d "🎯 Template type"complete -c Goobits CLI -n "__fish_seen_subcommand_from init" -l force -d "🔥 Overwrite existing goobits.yaml file"complete -c Goobits CLI -n "__fish_use_subcommand" -a "serve" -d "Serve local PyPI-compatible package index"complete -c Goobits CLI -n "__fish_seen_subcommand_from serve" -l host -d "🌍 Host to bind the server to"complete -c Goobits CLI -n "__fish_seen_subcommand_from serve" -l port -s p -d "🔌 Port to run the server on"'''
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
            filename = f'Goobits CLI.{shell}'
            if shell == 'bash':
                filename = f'Goobits CLI'

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