/**
 * Shell completion engine for Demo TypeScript CLI
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
# Bash completion for demo_ts

_demo_ts_completions()
{
    local cur prev words cword
    COMPREPLY=()
    cur="\${COMP_WORDS[COMP_CWORD]}"
    prev="\${COMP_WORDS[COMP_CWORD-1]}"
    
    # Global options
    local global_opts="--help -h --version"
    
    # Subcommands
    local subcommands=" greet info"
    
    case \${COMP_CWORD} in
        1)
            COMPREPLY=($(compgen -W "$subcommands $global_opts" -- "$cur"))
            ;;
        *)
            case "\${words[1]}" in                greet)
                    local greet_opts="--help -h --style -s --count -c --uppercase -u --language -l"
                    COMPREPLY=($(compgen -W "$greet_opts" -- "$cur"))
                    ;;                info)
                    local info_opts="--help -h --format -f --verbose -v --sections -s"
                    COMPREPLY=($(compgen -W "$info_opts" -- "$cur"))
                    ;;            esac
            ;;
    esac
}

complete -F _demo_ts_completions demo_ts
`;    }

    public generateZshCompletion(): string {        return `#compdef demo_ts
# Zsh completion for demo_ts

_demo_ts() {
    local context state line
    
    _arguments -C \\
        '(--help -h){--help,-h}[Show help information]' \\
        '(--version)--version[Show version information]' \\
        '1: :_demo_ts_commands' \\
        '*::arg:->args'
    
    case $state in
        args)
            case $words[1] in                greet)
                    _arguments \\
                        '(--help -h){--help,-h}[Show help information]' \\                        '(--style -s){--style,-s}[Greeting style]' \\                        '(--count -c){--count,-c}[Repeat greeting N times]' \\                        '(--uppercase -u){--uppercase,-u}[Convert to uppercase]' \\                        '(--language -l){--language,-l}[Language code]' \\                        '1:name:_files' \\                        '2:message:_files'                    ;;                info)
                    _arguments \\
                        '(--help -h){--help,-h}[Show help information]' \\                        '(--format -f){--format,-f}[Output format]' \\                        '(--verbose -v){--verbose,-v}[Show detailed information]' \\                        '(--sections -s){--sections,-s}[Comma-separated sections to show]' \\                    ;;            esac
            ;;
    esac
}

_demo_ts_commands() {
    local commands
    commands=(        'greet:Greet someone with style'        'info:Display system and environment information'    )
    _describe 'commands' commands
}

_demo_ts "$@"
`;    }

    public generateFishCompletion(): string {        return `# Fish completion for demo_ts

# Global options
complete -c demo_ts -f
complete -c demo_ts -s h -l help -d "Show help information"
complete -c demo_ts -l version -d "Show version information"

# Subcommandscomplete -c demo_ts -n "__fish_use_subcommand" -a "greet" -d "Greet someone with style"complete -c demo_ts -n "__fish_seen_subcommand_from greet" -l style -s s -d "Greeting style"complete -c demo_ts -n "__fish_seen_subcommand_from greet" -l count -s c -d "Repeat greeting N times"complete -c demo_ts -n "__fish_seen_subcommand_from greet" -l uppercase -s u -d "Convert to uppercase"complete -c demo_ts -n "__fish_seen_subcommand_from greet" -l language -s l -d "Language code"complete -c demo_ts -n "__fish_use_subcommand" -a "info" -d "Display system and environment information"complete -c demo_ts -n "__fish_seen_subcommand_from info" -l format -s f -d "Output format"complete -c demo_ts -n "__fish_seen_subcommand_from info" -l verbose -s v -d "Show detailed information"complete -c demo_ts -n "__fish_seen_subcommand_from info" -l sections -s s -d "Comma-separated sections to show"`;    }

    public async installCompletion(shell: string | null = null): Promise<boolean> {
        shell = shell || path.basename(process.env.SHELL || 'bash');
        
        let script: string;
        let completionDir: string;
        let filename: string;
        
        switch (shell) {
            case 'bash':
                script = this.generateBashCompletion();
                completionDir = path.join(os.homedir(), '.bash_completion.d');
                filename = 'demo_ts';
                break;
            case 'zsh':
                script = this.generateZshCompletion();
                completionDir = path.join(os.homedir(), '.zsh', 'completions');
                filename = 'demo_ts.zsh';
                break;
            case 'fish':
                script = this.generateFishCompletion();
                completionDir = path.join(os.homedir(), '.config', 'fish', 'completions');
                filename = 'demo_ts.fish';
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