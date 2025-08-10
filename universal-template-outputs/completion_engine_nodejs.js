/**
 * Shell completion engine for Test CLI
 */

const fs = require('fs');
const path = require('path');
const os = require('os');

class CompletionEngine {
    constructor(cliSchema) {
        this.cliSchema = cliSchema;
    }

    generateBashCompletion() {
        return `#!/bin/bash
# Bash completion for test-cli

_test_cli_completions()
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
            case "\${words[1]}" in
                hello)
                    local hello_opts="--help -h --uppercase -u"
                    COMPREPLY=($(compgen -W "$hello_opts" -- "$cur"))
                    ;;
            esac
            ;;
    esac
}

complete -F _test_cli_completions test-cli
`;
    }

    generateZshCompletion() {
        return `#compdef test-cli
# Zsh completion for test-cli

_test_cli() {
    local context state line
    
    _arguments -C \\
        '(--help -h){--help,-h}[Show help information]' \\
        '(--version)--version[Show version information]' \\
        '1: :_test_cli_commands' \\
        '*::arg:->args'
    
    case $state in
        args)
            case $words[1] in
                hello)
                    _arguments \\
                        '(--help -h){--help,-h}[Show help information]' \\
                        '(--uppercase -u){--uppercase,-u}[Convert to uppercase]' \\
                        '1:name:_files'
                    ;;
            esac
            ;;
    esac
}

_test_cli_commands() {
    local commands
    commands=(
        'hello:Say hello'
    )
    _describe 'commands' commands
}

_test_cli "$@"
`;
    }

    generateFishCompletion() {
        return `# Fish completion for test-cli

# Global options
complete -c test-cli -f
complete -c test-cli -s h -l help -d "Show help information"
complete -c test-cli -l version -d "Show version information"

# Subcommands
complete -c test-cli -n "__fish_use_subcommand" -a "hello" -d "Say hello"
complete -c test-cli -n "__fish_seen_subcommand_from hello" -l uppercase -s u -d "Convert to uppercase"
`;
    }

    async installCompletion(shell = null) {
        shell = shell || path.basename(process.env.SHELL || 'bash');
        
        let script, completionDir, filename;
        
        switch (shell) {
            case 'bash':
                script = this.generateBashCompletion();
                completionDir = path.join(os.homedir(), '.bash_completion.d');
                filename = 'test-cli';
                break;
            case 'zsh':
                script = this.generateZshCompletion();
                completionDir = path.join(os.homedir(), '.zsh', 'completions');
                filename = 'test-cli.zsh';
                break;
            case 'fish':
                script = this.generateFishCompletion();
                completionDir = path.join(os.homedir(), '.config', 'fish', 'completions');
                filename = 'test-cli.fish';
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