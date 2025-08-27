/**
 * Shell completion engine for Nested Command Demo
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

    public generateBashCompletion(): string {        return `#!/bin/bash
# Bash completion for demo

_demo_completions()
{
    local cur prev words cword
    COMPREPLY=()
    cur="\${COMP_WORDS[COMP_CWORD]}"
    prev="\${COMP_WORDS[COMP_CWORD-1]}"
    
    # Global options
    local global_opts="--help -h --version"
    
    # Subcommands
    local subcommands=" simple database api"
    
    case \${COMP_CWORD} in
        1)
            COMPREPLY=($(compgen -W "$subcommands $global_opts" -- "$cur"))
            ;;
        *)
            case "\${words[1]}" in                simple)
                    local simple_opts="--help -h --verbose"
                    COMPREPLY=($(compgen -W "$simple_opts" -- "$cur"))
                    ;;                database)
                    local database_opts="--help -h"
                    COMPREPLY=($(compgen -W "$database_opts" -- "$cur"))
                    ;;                api)
                    local api_opts="--help -h"
                    COMPREPLY=($(compgen -W "$api_opts" -- "$cur"))
                    ;;            esac
            ;;
    esac
}

complete -F _demo_completions demo
`;    }

    public generateZshCompletion(): string {        return `#compdef demo
# Zsh completion for demo

_demo() {
    local context state line
    
    _arguments -C \\
        '(--help -h){--help,-h}[Show help information]' \\
        '(--version)--version[Show version information]' \\
        '1: :_demo_commands' \\
        '*::arg:->args'
    
    case $state in
        args)
            case $words[1] in                simple)
                    _arguments \\
                        '(--help -h){--help,-h}[Show help information]' \\                        '(--verbose){--verbose}[Verbose output]' \\                        '1:message:_files'                    ;;                database)
                    _arguments \\
                        '(--help -h){--help,-h}[Show help information]' \\                    ;;                api)
                    _arguments \\
                        '(--help -h){--help,-h}[Show help information]' \\                    ;;            esac
            ;;
    esac
}

_demo_commands() {
    local commands
    commands=(        'simple:Simple command that works today'        'database:Database operations'        'api:API management'    )
    _describe 'commands' commands
}

_demo "$@"
`;    }

    public generateFishCompletion(): string {        return `# Fish completion for demo

# Global options
complete -c demo -f
complete -c demo -s h -l help -d "Show help information"
complete -c demo -l version -d "Show version information"

# Subcommandscomplete -c demo -n "__fish_use_subcommand" -a "simple" -d "Simple command that works today"complete -c demo -n "__fish_seen_subcommand_from simple" -l verbose -d "Verbose output"complete -c demo -n "__fish_use_subcommand" -a "database" -d "Database operations"complete -c demo -n "__fish_use_subcommand" -a "api" -d "API management"`;    }

    public async installCompletion(shell: string | null = null): Promise<boolean> {
        shell = shell || path.basename(process.env.SHELL || 'bash');
        
        let script: string;
        let completionDir: string;
        let filename: string;
        
        switch (shell) {
            case 'bash':
                script = this.generateBashCompletion();
                completionDir = path.join(os.homedir(), '.bash_completion.d');
                filename = 'demo';
                break;
            case 'zsh':
                script = this.generateZshCompletion();
                completionDir = path.join(os.homedir(), '.zsh', 'completions');
                filename = 'demo.zsh';
                break;
            case 'fish':
                script = this.generateFishCompletion();
                completionDir = path.join(os.homedir(), '.config', 'fish', 'completions');
                filename = 'demo.fish';
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