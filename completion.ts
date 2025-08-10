/**
 * Shell completion engine for Test String Escape CLI
 */

import * as fs from 'fs';
import * as path from 'path';
import * as os from 'os';

interface CliSchema {
    root_command: {
        name: string;
        subcommands: Array<{
            name: string;
            description: string;
            options: Array<{
                name: string;
                short?: string;
                description: string;
            }>;
            arguments: Array<{
                name: string;
                description: string;
            }>;
        }>;
    };
}

export class CompletionEngine {
    constructor(private cliSchema: CliSchema) {}

    public generateBashCompletion(): string {
        return `#!/bin/bash
# Bash completion for Test CLI

_Test CLI_completions()
{
    local cur prev words cword
    COMPREPLY=()
    cur="\${COMP_WORDS[COMP_CWORD]}"
    prev="\${COMP_WORDS[COMP_CWORD-1]}"
    
    # Global options
    local global_opts="--help -h --version"
    
    # Subcommands
    local subcommands=" deploy status"
    
    case \${COMP_CWORD} in
        1)
            COMPREPLY=($(compgen -W "$subcommands $global_opts" -- "$cur"))
            ;;
        *)
            case "\${words[1]}" in
                deploy)
                    local deploy_opts="--help -h --force -f --timeout"
                    COMPREPLY=($(compgen -W "$deploy_opts" -- "$cur"))
                    ;;
                status)
                    local status_opts="--help -h --format"
                    COMPREPLY=($(compgen -W "$status_opts" -- "$cur"))
                    ;;
            esac
            ;;
    esac
}

complete -F _Test CLI_completions Test CLI
`;
    }

    public generateZshCompletion(): string {
        return `#compdef Test CLI
# Zsh completion for Test CLI

_Test CLI() {
    local context state line
    
    _arguments -C \\
        '(--help -h){--help,-h}[Show help information]' \\
        '(--version)--version[Show version information]' \\
        '1: :_Test CLI_commands' \\
        '*::arg:->args'
    
    case $state in
        args)
            case $words[1] in
                deploy)
                    _arguments \\
                        '(--help -h){--help,-h}[Show help information]' \\
                        '(--force -f){--force,-f}[Force deployment even if there are warnings (use '--force' flag)]' \\
                        '(--timeout){--timeout}[Timeout in seconds (e.g., '--timeout 300')]' \\
                        '1:environment:_files'
                    ;;
                status)
                    _arguments \\
                        '(--help -h){--help,-h}[Show help information]' \\
                        '(--format){--format}[Output format: 'json', "yaml", or 'table']' \\
                    ;;
            esac
            ;;
    esac
}

_Test CLI_commands() {
    local commands
    commands=(
        'deploy:Deploy the application with 'production' or "staging" environment'
        'status:Check application status including 'health' checks and "performance" metrics'
    )
    _describe 'commands' commands
}

_Test CLI "$@"
`;
    }

    public generateFishCompletion(): string {
        return `# Fish completion for Test CLI

# Global options
complete -c Test CLI -f
complete -c Test CLI -s h -l help -d "Show help information"
complete -c Test CLI -l version -d "Show version information"

# Subcommands
complete -c Test CLI -n "__fish_use_subcommand" -a "deploy" -d "Deploy the application with 'production' or "staging" environment"
complete -c Test CLI -n "__fish_seen_subcommand_from deploy" -l force -s f -d "Force deployment even if there are warnings (use '--force' flag)"
complete -c Test CLI -n "__fish_seen_subcommand_from deploy" -l timeout -d "Timeout in seconds (e.g., '--timeout 300')"
complete -c Test CLI -n "__fish_use_subcommand" -a "status" -d "Check application status including 'health' checks and "performance" metrics"
complete -c Test CLI -n "__fish_seen_subcommand_from status" -l format -d "Output format: 'json', "yaml", or 'table'"
`;
    }

    public async installCompletion(shell: string | null = null): Promise<boolean> {
        shell = shell || path.basename(process.env.SHELL || 'bash');
        
        let script: string;
        let completionDir: string;
        let filename: string;
        
        switch (shell) {
            case 'bash':
                script = this.generateBashCompletion();
                completionDir = path.join(os.homedir(), '.bash_completion.d');
                filename = 'Test CLI';
                break;
            case 'zsh':
                script = this.generateZshCompletion();
                completionDir = path.join(os.homedir(), '.zsh', 'completions');
                filename = 'Test CLI.zsh';
                break;
            case 'fish':
                script = this.generateFishCompletion();
                completionDir = path.join(os.homedir(), '.config', 'fish', 'completions');
                filename = 'Test CLI.fish';
                break;
            default:
                console.error(`Unsupported shell: ${shell}`);
                return false;
        }
        
        try {
            if (!fs.existsSync(completionDir)) {
                fs.mkdirSync(completionDir, { recursive: true });
            }
            
            const filepath = path.join(completionDir, filename);
            fs.writeFileSync(filepath, script);
            
            console.log(`Completion script installed: ${filepath}`);
            
            if (shell === 'bash') {
                console.log('Please restart your terminal or run: source ~/.bashrc');
            } else if (shell === 'zsh') {
                console.log('Please restart your terminal or add to ~/.zshrc: fpath=(~/.zsh/completions $fpath)');
            }
            
            return true;
        } catch (error) {
            console.error(`Failed to install completion: ${(error as Error).message}`);
            return false;
        }
    }
}