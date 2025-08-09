# Proposal: Achieving Full Language Parity for goobits-cli

## Executive Summary

The goobits-cli framework currently supports four target languages (Python, Node.js, TypeScript, and Rust), but only Python has a complete reference implementation. JavaScript/TypeScript templates are minimal placeholders (~30 lines), while Rust is approximately 80% complete but missing critical features like completion and config command groups. This proposal outlines a comprehensive strategy to achieve full feature parity across all languages while maximizing template reuse and minimizing code duplication.

### Key Goals
- **Complete Feature Parity**: All languages support the same CLI capabilities
- **Template Unification**: Shared templates reduce maintenance burden by 70%
- **Parallel Development**: Multiple teams can work simultaneously
- **Quality Assurance**: Comprehensive testing ensures consistency

## Current State Analysis

### Implementation Status by Language

#### Python (100% - Reference Implementation)
- ✅ Full CLI structure with rich-click integration
- ✅ Complete hook system (app_hooks.py)
- ✅ Built-in commands (upgrade, daemon, completion, config, plugins)
- ✅ Helper modules (progress, prompts, config manager)
- ✅ Completion engine with shell support
- ✅ Error handling with custom exception classes
- ✅ Plugin system with dynamic loading
- ✅ Installation management (setup.sh)

#### JavaScript/TypeScript (~5% - Placeholder Only)
- ❌ Basic 30-line placeholder template
- ❌ No command generation logic
- ❌ No hook system implementation
- ❌ No built-in commands
- ❌ No helper modules
- ❌ No completion support
- ❌ No error handling
- ❌ No plugin system

#### Rust (~80% - Mostly Complete)
- ✅ Full CLI structure with clap
- ✅ Hook system implementation
- ✅ Basic error handling
- ✅ Plugin system framework
- ✅ Styling module
- ❌ Missing completion command group
- ❌ Missing config command group
- ❌ No progress/prompt helpers
- ❌ Incomplete built-in commands

### File Structure Comparison

```
Python (Reference):
├── cli.py                    # Main CLI definition
├── app_hooks.py             # User hooks
├── builtin_commands.py      # Built-in commands
├── completion_engine.py     # Shell completions
├── config_manager.py        # Config management
├── progress_helper.py       # Progress indicators
├── prompts_helper.py        # Interactive prompts
├── completion_helper.py     # Completion utilities
└── setup.sh                 # Installation script

JavaScript/TypeScript (Current):
├── cli.js/ts               # 30-line placeholder
└── (nothing else)

Rust (Current):
├── main.rs                  # CLI entry point
├── lib.rs                   # Library exports
├── commands.rs              # Command definitions
├── config.rs                # Config structures
├── hooks.rs                 # Hook system
├── errors.rs                # Error handling
├── plugins.rs               # Plugin system
├── styling.rs               # Terminal styling
├── utils.rs                 # Utilities
└── completion_engine.rs     # Partial completion
```

## Solution Architecture

### Phase 1: Universal Template System

Create language-agnostic templates that generate consistent output across all languages:

#### 1.1 Core Templates (Shared)
```
templates/universal/
├── cli_structure.j2         # Main CLI framework
├── command_definition.j2    # Command parsing logic
├── hook_system.j2          # Hook integration
├── error_handling.j2       # Error classes/types
├── builtin_commands.j2     # Standard commands
└── helpers/
    ├── progress.j2         # Progress indicators
    ├── prompts.j2          # User prompts
    └── config.j2           # Config management
```

#### 1.2 Language Adapters
```
templates/adapters/
├── python_adapter.j2       # Python-specific syntax
├── javascript_adapter.j2   # JS/Node syntax
├── typescript_adapter.j2   # TS types & syntax
└── rust_adapter.j2         # Rust syntax & traits
```

### Phase 2: Feature Implementation Matrix

| Feature | Python | JavaScript | TypeScript | Rust |
|---------|--------|------------|------------|------|
| CLI Structure | ✅ | 🔨 Phase 2A | 🔨 Phase 2A | ✅ |
| Command Parsing | ✅ | 🔨 Phase 2A | 🔨 Phase 2A | ✅ |
| Hook System | ✅ | 🔨 Phase 2B | 🔨 Phase 2B | ✅ |
| Error Handling | ✅ | 🔨 Phase 2B | 🔨 Phase 2B | ✅ |
| Completion | ✅ | 🔨 Phase 3A | 🔨 Phase 3A | 🔨 Phase 3B |
| Config Commands | ✅ | 🔨 Phase 3A | 🔨 Phase 3A | 🔨 Phase 3B |
| Progress Helper | ✅ | 🔨 Phase 4 | 🔨 Phase 4 | 🔨 Phase 4 |
| Prompt Helper | ✅ | 🔨 Phase 4 | 🔨 Phase 4 | 🔨 Phase 4 |
| Plugin System | ✅ | 🔨 Phase 5 | 🔨 Phase 5 | ✅ |

### Phase 3: Template Unification Strategy

#### 3.1 Shared Logic Templates
Create templates that contain business logic independent of language syntax:

```jinja
{# templates/universal/command_logic.j2 #}
{% macro generate_command_structure(command, language) %}
  {% if language == 'python' %}
    @click.command()
    {% for arg in command.arguments %}
    @click.argument('{{ arg.name }}', type={{ python_type(arg.type) }})
    {% endfor %}
    {% for opt in command.options %}
    @click.option('--{{ opt.long }}', '-{{ opt.short }}', 
                  type={{ python_type(opt.type) }},
                  help='{{ opt.help }}')
    {% endfor %}
  {% elif language in ['javascript', 'typescript'] %}
    .command('{{ command.name }}')
    .description('{{ command.description }}')
    {% for arg in command.arguments %}
    .argument('<{{ arg.name }}>', '{{ arg.description }}')
    {% endfor %}
    {% for opt in command.options %}
    .option('-{{ opt.short }}, --{{ opt.long }}', '{{ opt.help }}')
    {% endfor %}
  {% elif language == 'rust' %}
    #[derive(Args)]
    struct {{ command.name | capitalize }}Args {
        {% for arg in command.arguments %}
        /// {{ arg.description }}
        {{ arg.name }}: {{ rust_type(arg.type) }},
        {% endfor %}
        {% for opt in command.options %}
        /// {{ opt.help }}
        #[arg(short = '{{ opt.short }}', long = "{{ opt.long }}")]
        {{ opt.name | snake_case }}: {{ rust_type(opt.type) }},
        {% endfor %}
    }
  {% endif %}
{% endmacro %}
```

#### 3.2 Language-Specific Wrappers
Minimal language-specific templates that import shared logic:

```jinja
{# templates/python/cli.py.j2 #}
{% import 'universal/command_logic.j2' as cmd_logic %}
#!/usr/bin/env python3
import click
{{ cmd_logic.generate_imports('python') }}

{{ cmd_logic.generate_command_structure(cli, 'python') }}
```

## Implementation Phases

### Phase 1: Template Infrastructure (Week 1)
**Owner**: Infrastructure Team
- [ ] Create universal template directory structure
- [ ] Implement language adapter system
- [ ] Build template testing framework
- [ ] Create template documentation

### Phase 2A: JavaScript/TypeScript Core (Week 2)
**Owner**: JS/TS Team
- [ ] Implement CLI structure generation
- [ ] Add command parsing logic
- [ ] Create package.json generation
- [ ] Implement basic error handling

### Phase 2B: JavaScript/TypeScript Integration (Week 3)
**Owner**: JS/TS Team
- [ ] Implement hook system
- [ ] Add error handling classes
- [ ] Create test infrastructure
- [ ] Add build system support

### Phase 3A: JavaScript/TypeScript Advanced (Week 4)
**Owner**: JS/TS Team
- [ ] Implement completion engine
- [ ] Add config command group
- [ ] Create shell completion scripts
- [ ] Add interactive features

### Phase 3B: Rust Completion Features (Week 4)
**Owner**: Rust Team
- [ ] Complete completion engine
- [ ] Implement config command group
- [ ] Add missing built-in commands
- [ ] Create shell integration

### Phase 4: Helper Modules (Week 5)
**Owner**: Cross-Language Team
- [ ] Progress indicators (all languages)
- [ ] Interactive prompts (all languages)
- [ ] Config management (all languages)
- [ ] Shared utility functions

### Phase 5: Plugin System (Week 6)
**Owner**: Architecture Team
- [ ] Complete JS/TS plugin system
- [ ] Standardize plugin interfaces
- [ ] Create plugin documentation
- [ ] Add example plugins

### Phase 6: Testing & Documentation (Week 7)
**Owner**: QA Team
- [ ] End-to-end testing suite
- [ ] Cross-language validation
- [ ] Performance benchmarks
- [ ] Complete documentation

## Specific Deliverables

### JavaScript/TypeScript Implementation

#### Core CLI Template (cli.js/ts.j2)
```javascript
#!/usr/bin/env node
const { Command } = require('commander');
const chalk = require('chalk');
const ora = require('ora');
const prompts = require('prompts');

// Import generated components
const { commands } = require('./commands');
const { builtinCommands } = require('./builtin-commands');
const { hookRegistry } = require('./hooks');
const { errorHandler } = require('./errors');
const { completionEngine } = require('./completion');
const { configManager } = require('./config');
const { pluginManager } = require('./plugins');

// Create main program
const program = new Command();

// Configure CLI
program
  .name('{{ command_name }}')
  .description('{{ description }}')
  .version('{{ version }}')
  .hook('preAction', (thisCommand, actionCommand) => {
    hookRegistry.execute('preCommand', { command: actionCommand });
  })
  .hook('postAction', (thisCommand, actionCommand) => {
    hookRegistry.execute('postCommand', { command: actionCommand });
  });

// Register all commands
commands.forEach(cmd => program.addCommand(cmd));
builtinCommands.forEach(cmd => program.addCommand(cmd));

// Error handling
program.exitOverride();
process.on('unhandledRejection', errorHandler.handle);

// Parse and execute
try {
  program.parse(process.argv);
} catch (error) {
  errorHandler.handle(error);
}
```

#### Hook System Implementation
```javascript
// hooks.js
class HookRegistry {
  constructor() {
    this.hooks = new Map();
    this.loadUserHooks();
  }

  loadUserHooks() {
    try {
      const userHooks = require('./app-hooks');
      Object.entries(userHooks).forEach(([name, handler]) => {
        this.register(name, handler);
      });
    } catch (error) {
      // User hooks are optional
    }
  }

  register(name, handler) {
    if (!this.hooks.has(name)) {
      this.hooks.set(name, []);
    }
    this.hooks.get(name).push(handler);
  }

  async execute(name, context) {
    const handlers = this.hooks.get(name) || [];
    for (const handler of handlers) {
      await handler(context);
    }
  }
}
```

### Rust Completion Implementation

#### Completion Engine
```rust
// completion_engine.rs
use clap::Command;
use clap_complete::{generate, Generator, Shell};

pub struct CompletionEngine {
    app: Command,
    shell: Shell,
}

impl CompletionEngine {
    pub fn new(app: Command) -> Self {
        Self {
            app,
            shell: Shell::from_env().unwrap_or(Shell::Bash),
        }
    }

    pub fn generate_completion(&mut self, shell: Option<Shell>) {
        let target_shell = shell.unwrap_or(self.shell);
        let app_name = self.app.get_name().to_string();
        
        generate(target_shell, &mut self.app, app_name, &mut std::io::stdout());
    }

    pub fn install_completion(&self) -> Result<(), Box<dyn std::error::Error>> {
        let completion_dir = self.get_completion_dir()?;
        let completion_file = completion_dir.join(format!("_{}", self.app.get_name()));
        
        // Generate and write completion file
        let mut file = std::fs::File::create(&completion_file)?;
        self.generate_completion_to_file(&mut file)?;
        
        println!("Completion installed to: {}", completion_file.display());
        Ok(())
    }
}
```

#### Config Command Group
```rust
// commands/config.rs
use clap::{Args, Subcommand};
use crate::config::ConfigManager;

#[derive(Subcommand)]
pub enum ConfigCommands {
    /// Get a configuration value
    Get {
        /// Configuration key
        key: String,
    },
    /// Set a configuration value
    Set {
        /// Configuration key
        key: String,
        /// Configuration value
        value: String,
    },
    /// List all configuration values
    List,
    /// Reset configuration to defaults
    Reset {
        /// Confirm reset without prompting
        #[arg(long)]
        force: bool,
    },
}

pub fn handle_config_command(cmd: ConfigCommands) -> Result<(), Box<dyn std::error::Error>> {
    let mut config = ConfigManager::load()?;
    
    match cmd {
        ConfigCommands::Get { key } => {
            match config.get(&key) {
                Some(value) => println!("{}: {}", key, value),
                None => eprintln!("Configuration key '{}' not found", key),
            }
        }
        ConfigCommands::Set { key, value } => {
            config.set(key, value);
            config.save()?;
            println!("Configuration updated");
        }
        ConfigCommands::List => {
            config.list();
        }
        ConfigCommands::Reset { force } => {
            if force || confirm_reset()? {
                config.reset();
                config.save()?;
                println!("Configuration reset to defaults");
            }
        }
    }
    
    Ok(())
}
```

## Validation Criteria

### Functional Requirements
1. **Command Generation**: All languages must generate identical CLI interfaces from the same YAML
2. **Hook Execution**: Business logic hooks must work consistently across languages
3. **Error Handling**: Similar error messages and exit codes across implementations
4. **Built-in Commands**: upgrade, daemon, completion, config, and plugin commands in all languages
5. **Shell Completion**: Bash, Zsh, and Fish completion scripts for all implementations

### Non-Functional Requirements
1. **Performance**: CLI startup time < 100ms for all languages
2. **Size**: Compiled binaries < 10MB (Rust), NPM packages < 5MB
3. **Dependencies**: Minimal external dependencies
4. **Testing**: 90%+ code coverage for generated code
5. **Documentation**: Language-specific guides for each implementation

### Testing Strategy
```yaml
# test-parity.yaml
test_suite:
  - name: "Command Generation"
    input: "sample-cli.yaml"
    validate:
      - commands_match: true
      - options_match: true
      - help_text_similar: 95%
  
  - name: "Hook Execution"
    hooks:
      - on_hello: "return greeting"
    validate:
      - output_matches: true
      - exit_code: 0
  
  - name: "Error Handling"
    scenario: "missing_required_arg"
    validate:
      - error_message_similar: 90%
      - exit_code: 1
```

## Risk Mitigation

### Technical Risks

1. **Language Feature Disparity**
   - *Risk*: Some languages lack features (e.g., decorators in Rust)
   - *Mitigation*: Use language-appropriate patterns (derive macros for Rust, decorators for Python)

2. **Dependency Management**
   - *Risk*: Different package managers behave differently
   - *Mitigation*: Standardize installation scripts and provide clear documentation

3. **Platform Compatibility**
   - *Risk*: Shell completion works differently on Windows
   - *Mitigation*: Provide PowerShell completion scripts for Windows users

### Process Risks

1. **Parallel Development Conflicts**
   - *Risk*: Teams working on different languages create incompatible solutions
   - *Mitigation*: Weekly sync meetings and shared design documents

2. **Template Complexity**
   - *Risk*: Universal templates become too complex
   - *Mitigation*: Regular refactoring and clear separation of concerns

3. **Testing Coverage**
   - *Risk*: Difficult to test all language combinations
   - *Mitigation*: Automated matrix testing with GitHub Actions

## Success Metrics

1. **Feature Parity**: 100% of Python features available in all languages
2. **Code Reuse**: 70% of template code is shared across languages
3. **User Satisfaction**: 90% of users report consistent experience across languages
4. **Maintenance Effort**: 50% reduction in time to add new features
5. **Bug Reports**: < 5% of bugs are language-specific

## Timeline

- **Week 1**: Template infrastructure and design finalization
- **Weeks 2-3**: JavaScript/TypeScript implementation
- **Week 4**: Rust completion and advanced features
- **Week 5**: Cross-language helper modules
- **Week 6**: Plugin system standardization
- **Week 7**: Testing, documentation, and release preparation
- **Week 8**: Release and monitoring

## Conclusion

Achieving full language parity for goobits-cli is essential for its adoption as a universal CLI framework. By implementing a systematic approach with universal templates, parallel development tracks, and comprehensive testing, we can deliver consistent, high-quality CLI generation across Python, JavaScript, TypeScript, and Rust. This investment will reduce long-term maintenance costs and provide users with a truly language-agnostic CLI development experience.