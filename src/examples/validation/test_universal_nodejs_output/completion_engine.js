/**
 * Shell completion engine for Test Universal CLI
 */

const fs = require('fs');
const path = require('path');
const os = require('os');

class CompletionEngine {
    constructor(cliSchema) {
        this.cliSchema = cliSchema;
    }

    generateBashCompletion() {        return `#!/bin/bash
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
    local subcommands=" hello"
    
    case \${COMP_CWORD} in
        1)
            COMPREPLY=($(compgen -W "$subcommands $global_opts" -- "$cur"))
            ;;
        *)
            case "\${words[1]}" in                hello)
                    local hello_opts="--help -h --greeting -g"
                    COMPREPLY=($(compgen -W "$hello_opts" -- "$cur"))
                    ;;            esac
            ;;
    esac
}

complete -F _Test CLI_completions Test CLI
`;    }

    generateZshCompletion() {        return `#compdef Test CLI
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
            case $words[1] in                hello)
                    _arguments \\
                        '(--help -h){--help,-h}[Show help information]' \\                        '(--greeting -g){--greeting,-g}[Custom greeting message]' \\                        '1:name:_files'                    ;;            esac
            ;;
    esac
}

_Test CLI_commands() {
    local commands
    commands=(        'hello:Say hello to someone'    )
    _describe 'commands' commands
}

_Test CLI "$@"
`;    }

    generateFishCompletion() {        return `# Fish completion for Test CLI

# Global options
complete -c Test CLI -f
complete -c Test CLI -s h -l help -d "Show help information"
complete -c Test CLI -l version -d "Show version information"

# Subcommandscomplete -c Test CLI -n "__fish_use_subcommand" -a "hello" -d "Say hello to someone"complete -c Test CLI -n "__fish_seen_subcommand_from hello" -l greeting -s g -d "Custom greeting message"`;    }

    async installCompletion(shell = null) {
        shell = shell || path.basename(process.env.SHELL || 'bash');
        
        let script, completionDir, filename;
        
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
            console.error(`Failed to install completion: ${error.message}`);
            return false;
        }
    }
}

module.exports = { CompletionEngine };