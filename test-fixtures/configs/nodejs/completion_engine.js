/**
 * Shell completion engine for Test Node.js CLI
 */

const fs = require('fs');
const path = require('path');
const os = require('os');

class CompletionEngine {
    constructor(cliSchema) {
        this.cliSchema = cliSchema;
    }

    generateBashCompletion() {        return `#!/bin/bash
# Bash completion for testnode

_testnode_completions()
{
    local cur prev words cword
    COMPREPLY=()
    cur="\${COMP_WORDS[COMP_CWORD]}"
    prev="\${COMP_WORDS[COMP_CWORD-1]}"
    
    # Global options
    local global_opts="--help -h --version"
    
    # Subcommands
    local subcommands=" hello build serve"
    
    case \${COMP_CWORD} in
        1)
            COMPREPLY=($(compgen -W "$subcommands $global_opts" -- "$cur"))
            ;;
        *)
            case "\${words[1]}" in                hello)
                    local hello_opts="--help -h"
                    COMPREPLY=($(compgen -W "$hello_opts" -- "$cur"))
                    ;;                build)
                    local build_opts="--help -h"
                    COMPREPLY=($(compgen -W "$build_opts" -- "$cur"))
                    ;;                serve)
                    local serve_opts="--help -h"
                    COMPREPLY=($(compgen -W "$serve_opts" -- "$cur"))
                    ;;            esac
            ;;
    esac
}

complete -F _testnode_completions testnode
`;    }

    generateZshCompletion() {        return `#compdef testnode
# Zsh completion for testnode

_testnode() {
    local context state line
    
    _arguments -C \\
        '(--help -h){--help,-h}[Show help information]' \\
        '(--version)--version[Show version information]' \\
        '1: :_testnode_commands' \\
        '*::arg:->args'
    
    case $state in
        args)
            case $words[1] in                hello)
                    _arguments \\
                        '(--help -h){--help,-h}[Show help information]' \\                    ;;                build)
                    _arguments \\
                        '(--help -h){--help,-h}[Show help information]' \\                    ;;                serve)
                    _arguments \\
                        '(--help -h){--help,-h}[Show help information]' \\                    ;;            esac
            ;;
    esac
}

_testnode_commands() {
    local commands
    commands=(        'hello:Say hello'        'build:Build something'        'serve:Start server'    )
    _describe 'commands' commands
}

_testnode "$@"
`;    }

    generateFishCompletion() {        return `# Fish completion for testnode

# Global options
complete -c testnode -f
complete -c testnode -s h -l help -d "Show help information"
complete -c testnode -l version -d "Show version information"

# Subcommandscomplete -c testnode -n "__fish_use_subcommand" -a "hello" -d "Say hello"complete -c testnode -n "__fish_use_subcommand" -a "build" -d "Build something"complete -c testnode -n "__fish_use_subcommand" -a "serve" -d "Start server"`;    }

    async installCompletion(shell = null) {
        shell = shell || path.basename(process.env.SHELL || 'bash');
        
        let script, completionDir, filename;
        
        switch (shell) {
            case 'bash':
                script = this.generateBashCompletion();
                completionDir = path.join(os.homedir(), '.bash_completion.d');
                filename = 'testnode';
                break;
            case 'zsh':
                script = this.generateZshCompletion();
                completionDir = path.join(os.homedir(), '.zsh', 'completions');
                filename = 'testnode.zsh';
                break;
            case 'fish':
                script = this.generateFishCompletion();
                completionDir = path.join(os.homedir(), '.config', 'fish', 'completions');
                filename = 'testnode.fish';
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