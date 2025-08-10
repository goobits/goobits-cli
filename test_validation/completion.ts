/**
 * Shell completion engine for Test TypeScript CLI
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
# Bash completion for testcli

_testcli_completions()
{
    local cur prev words cword
    COMPREPLY=()
    cur="\${COMP_WORDS[COMP_CWORD]}"
    prev="\${COMP_WORDS[COMP_CWORD-1]}"
    
    # Global options
    local global_opts="--help -h --version"
    
    # Subcommands
    local subcommands=" greet"
    
    case \${COMP_CWORD} in
        1)
            COMPREPLY=($(compgen -W "$subcommands $global_opts" -- "$cur"))
            ;;
        *)
            case "\${words[1]}" in
                greet)
                    local greet_opts="--help -h ----loud"
                    COMPREPLY=($(compgen -W "$greet_opts" -- "$cur"))
                    ;;
            esac
            ;;
    esac
}

complete -F _testcli_completions testcli
`;
    }

    public generateZshCompletion(): string {
        return `#compdef testcli
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
            case $words[1] in
                greet)
                    _arguments \\
                        '(--help -h){--help,-h}[Show help information]' \\
                        '(----loud){----loud}[Greet loudly]' \\
                    ;;
            esac
            ;;
    esac
}

_testcli_commands() {
    local commands
    commands=(
        'greet:Greet someone'
    )
    _describe 'commands' commands
}

_testcli "$@"
`;
    }

    public generateFishCompletion(): string {
        return `# Fish completion for testcli

# Global options
complete -c testcli -f
complete -c testcli -s h -l help -d "Show help information"
complete -c testcli -l version -d "Show version information"

# Subcommands
complete -c testcli -n "__fish_use_subcommand" -a "greet" -d "Greet someone"
complete -c testcli -n "__fish_seen_subcommand_from greet" -l --loud -d "Greet loudly"
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
                filename = 'testcli';
                break;
            case 'zsh':
                script = this.generateZshCompletion();
                completionDir = path.join(os.homedir(), '.zsh', 'completions');
                filename = 'testcli.zsh';
                break;
            case 'fish':
                script = this.generateFishCompletion();
                completionDir = path.join(os.homedir(), '.config', 'fish', 'completions');
                filename = 'testcli.fish';
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