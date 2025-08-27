/**
 * Shell completion engine for Test TypeScript
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
# Bash completion for testts

_testts_completions()
{
    local cur prev words cword
    COMPREPLY=()
    cur="\${COMP_WORDS[COMP_CWORD]}"
    prev="\${COMP_WORDS[COMP_CWORD-1]}"
    
    # Global options
    local global_opts="--help -h --version"
    
    # Subcommands
    local subcommands=" hello"
    
    case \${COMP_CWORD} in
        1)
            COMPREPLY=($(compgen -W "$subcommands $global_opts" -- "$cur"))
            ;;
        *)
            case "\${words[1]}" in                hello)
                    local hello_opts="--help -h"
                    COMPREPLY=($(compgen -W "$hello_opts" -- "$cur"))
                    ;;            esac
            ;;
    esac
}

complete -F _testts_completions testts
`;    }

    public generateZshCompletion(): string {        return `#compdef testts
# Zsh completion for testts

_testts() {
    local context state line
    
    _arguments -C \\
        '(--help -h){--help,-h}[Show help information]' \\
        '(--version)--version[Show version information]' \\
        '1: :_testts_commands' \\
        '*::arg:->args'
    
    case $state in
        args)
            case $words[1] in                hello)
                    _arguments \\
                        '(--help -h){--help,-h}[Show help information]' \\                        '1:name:_files'                    ;;            esac
            ;;
    esac
}

_testts_commands() {
    local commands
    commands=(        'hello:Say hello'    )
    _describe 'commands' commands
}

_testts "$@"
`;    }

    public generateFishCompletion(): string {        return `# Fish completion for testts

# Global options
complete -c testts -f
complete -c testts -s h -l help -d "Show help information"
complete -c testts -l version -d "Show version information"

# Subcommandscomplete -c testts -n "__fish_use_subcommand" -a "hello" -d "Say hello"`;    }

    public async installCompletion(shell: string | null = null): Promise<boolean> {
        shell = shell || path.basename(process.env.SHELL || 'bash');
        
        let script: string;
        let completionDir: string;
        let filename: string;
        
        switch (shell) {
            case 'bash':
                script = this.generateBashCompletion();
                completionDir = path.join(os.homedir(), '.bash_completion.d');
                filename = 'testts';
                break;
            case 'zsh':
                script = this.generateZshCompletion();
                completionDir = path.join(os.homedir(), '.zsh', 'completions');
                filename = 'testts.zsh';
                break;
            case 'fish':
                script = this.generateFishCompletion();
                completionDir = path.join(os.homedir(), '.config', 'fish', 'completions');
                filename = 'testts.fish';
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