/**
 * Shell completion engine for Demo Node.js CLI
 */

const fs = require('fs');
const path = require('path');
const os = require('os');

class CompletionEngine {
    constructor(cliSchema) {
        this.cliSchema = cliSchema;
    }

    generateBashCompletion() {        return `#!/bin/bash
# Bash completion for demo_js

_demo_js_completions()
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

complete -F _demo_js_completions demo_js
`;    }

    generateZshCompletion() {        return `#compdef demo_js
# Zsh completion for demo_js

_demo_js() {
    local context state line
    
    _arguments -C \\
        '(--help -h){--help,-h}[Show help information]' \\
        '(--version)--version[Show version information]' \\
        '1: :_demo_js_commands' \\
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

_demo_js_commands() {
    local commands
    commands=(        'greet:Greet someone with style'        'info:Display system and environment information'    )
    _describe 'commands' commands
}

_demo_js "$@"
`;    }

    generateFishCompletion() {        return `# Fish completion for demo_js

# Global options
complete -c demo_js -f
complete -c demo_js -s h -l help -d "Show help information"
complete -c demo_js -l version -d "Show version information"

# Subcommandscomplete -c demo_js -n "__fish_use_subcommand" -a "greet" -d "Greet someone with style"complete -c demo_js -n "__fish_seen_subcommand_from greet" -l style -s s -d "Greeting style"complete -c demo_js -n "__fish_seen_subcommand_from greet" -l count -s c -d "Repeat greeting N times"complete -c demo_js -n "__fish_seen_subcommand_from greet" -l uppercase -s u -d "Convert to uppercase"complete -c demo_js -n "__fish_seen_subcommand_from greet" -l language -s l -d "Language code"complete -c demo_js -n "__fish_use_subcommand" -a "info" -d "Display system and environment information"complete -c demo_js -n "__fish_seen_subcommand_from info" -l format -s f -d "Output format"complete -c demo_js -n "__fish_seen_subcommand_from info" -l verbose -s v -d "Show detailed information"complete -c demo_js -n "__fish_seen_subcommand_from info" -l sections -s s -d "Comma-separated sections to show"`;    }

    async installCompletion(shell = null) {
        shell = shell || path.basename(process.env.SHELL || 'bash');
        
        let script, completionDir, filename;
        
        switch (shell) {
            case 'bash':
                script = this.generateBashCompletion();
                completionDir = path.join(os.homedir(), '.bash_completion.d');
                filename = 'demo_js';
                break;
            case 'zsh':
                script = this.generateZshCompletion();
                completionDir = path.join(os.homedir(), '.zsh', 'completions');
                filename = 'demo_js.zsh';
                break;
            case 'fish':
                script = this.generateFishCompletion();
                completionDir = path.join(os.homedir(), '.config', 'fish', 'completions');
                filename = 'demo_js.fish';
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
            console.error(`Failed to install completion: ${error.message}`);
            return false;
        }
    }
}

module.exports = { CompletionEngine };