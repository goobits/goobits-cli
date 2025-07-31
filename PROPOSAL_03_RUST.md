# Proposal: Multi-Language Support - Rust CLI Generation

**Status**: Draft Proposal  
**Date**: 2025-01-24  
**Version**: 1.0  

## Problem Statement

Goobits-cli currently only supports Python CLI generation, limiting its appeal to the broader CLI development community:
- High-performance CLI tools often require Rust for speed and efficiency
- Single binary distribution is preferred for many use cases
- Rust CLI ecosystem is large and growing rapidly
- Existing Rust projects (like claude-usage) cannot easily adopt goobits workflow

## Proposed Solution

Extend goobits-cli to support multi-language CLI generation, starting with Rust as the first additional language.

### Design Principles
1. **Same YAML Config**: Identical `goobits.yaml` format across all languages
2. **Language-Specific Templates**: Each language has optimized code generation
3. **Unified Tooling**: Same `goobits build`, `goobits test` commands work for all languages
4. **Native Ecosystem Integration**: Generated code follows language best practices

## Technical Specification

### Configuration Format

```yaml
# goobits.yaml
language: rust  # New field: python (default), rust
package_name: my-cli
command_name: my-cli
description: "A high-performance CLI tool"

dependencies:
  rust_crates:
    - clap = { version = "4.0", features = ["derive"] }
    - serde = { version = "1.0", features = ["derive"] }
    - tokio = { version = "1", features = ["rt-multi-thread"] }

cli:
  commands:
    process:
      desc: "Process input data"
      args:
        - name: input
          desc: "Input file path"
          required: true
      options:
        - name: output
          short: o
          desc: "Output file path"
        - name: verbose
          short: v
          type: flag
          desc: "Enable verbose output"
```

### Generated Rust Structure

```
my-cli/
├── goobits.yaml         # Same configuration format
├── Cargo.toml           # Generated Rust manifest
├── src/
│   ├── main.rs          # Generated CLI entry point  
│   ├── lib.rs           # Generated library code
│   └── commands/
│       └── process.rs   # Generated command implementations
├── setup.sh             # Rust-specific installation script
└── README.md            # Generated documentation
```

### Example Generated Code

**Cargo.toml:**
```toml
[package]
name = "my-cli"
version = "1.0.0"
edition = "2021"
description = "A high-performance CLI tool"

[[bin]]
name = "my-cli"
path = "src/main.rs"

[dependencies]
clap = { version = "4.0", features = ["derive"] }
serde = { version = "1.0", features = ["derive"] }
tokio = { version = "1", features = ["rt-multi-thread"] }
```

**src/main.rs:**
```rust
use clap::{Parser, Subcommand};

#[derive(Parser)]
#[command(name = "my-cli")]
#[command(about = "A high-performance CLI tool")]
struct Cli {
    #[command(subcommand)]
    command: Commands,
}

#[derive(Subcommand)]
enum Commands {
    Process {
        /// Input file path
        input: String,
        
        /// Output file path
        #[arg(short = 'o', long)]
        output: Option<String>,
        
        /// Enable verbose output
        #[arg(short = 'v', long)]
        verbose: bool,
    },
}

fn main() {
    let cli = Cli::parse();
    
    match cli.command {
        Commands::Process { input, output, verbose } => {
            commands::process::run(input, output, verbose);
        }
    }
}

mod commands {
    pub mod process {
        pub fn run(input: String, output: Option<String>, verbose: bool) {
            // Hook system - calls external implementation if available
            println!("Processing {} -> {:?}", input, output);
        }
    }
}
```

## Implementation Plan

### File Structure (~1,200 lines)
```
src/goobits_cli/
├── main.py                     (+100 lines - language detection)
├── generators/
│   ├── __init__.py            (20 lines)
│   ├── python.py              (existing - refactored)
│   └── rust.py                (400 lines - Rust generation)
├── templates/
│   └── rust/
│       ├── main.rs.j2         (200 lines)
│       ├── Cargo.toml.j2      (80 lines)
│       ├── lib.rs.j2          (150 lines)
│       └── setup.sh.j2        (120 lines)
└── schemas.py                 (+150 lines - Rust config validation)
```

### Implementation Phases

#### Phase 1: Core Rust Support (MVP)
- [ ] Add `language` field to goobits.yaml schema
- [ ] Create Rust code generator and templates
- [ ] Support basic CLI structure with clap
- [ ] Generate Cargo.toml and setup.sh
- [ ] Test with simple CLI project

**Estimated Time**: 3-4 days  
**Lines of Code**: ~800

#### Phase 2: Advanced Features
- [ ] Hook system for Rust (external crate integration)
- [ ] Async command support with tokio
- [ ] Error handling with anyhow/thiserror
- [ ] Configuration file support (TOML/YAML)
- [ ] Testing framework integration

**Estimated Time**: 2-3 days  
**Lines of Code**: ~400

#### Phase 3: Testing Integration
- [ ] Extend goobits testing framework for Rust
- [ ] Cargo test integration
- [ ] Binary execution testing
- [ ] Performance benchmarking support

**Estimated Time**: 2 days  
**Lines of Code**: ~300

## Language Detection Strategy

### Automatic Detection
```bash
goobits build                    # Auto-detects from goobits.yaml
goobits init my-cli --rust       # Shorthand for language selection
goobits init my-cli --language rust  # Explicit language selection
```

### Configuration Validation
```python
# Enhanced schema validation
class GoobitsConfigSchema(BaseModel):
    language: Literal["python", "rust"] = "python"
    
    # Language-specific dependencies
    dependencies: Optional[Dependencies] = None
    rust_crates: Optional[Dict[str, str]] = None
    
    @validator('rust_crates')
    def validate_rust_dependencies(cls, v, values):
        if values.get('language') == 'rust' and not v:
            raise ValueError("Rust projects should specify rust_crates")
        return v
```

## Commands Integration

### Enhanced Init Command
```bash
# Create Python CLI (default)
goobits init my-python-cli

# Create Rust CLI
goobits init my-rust-cli --language rust
goobits init my-rust-cli --rust  # Shorthand

# Templates by language
goobits init --template basic --language rust
goobits init --template performance --language rust  # New Rust-specific template
```

### Build Command Enhancement
```bash
# Auto-detects language from goobits.yaml
goobits build

# Language-specific outputs
# Python: generates .py files, setup.sh with pip
# Rust: generates .rs files, Cargo.toml, setup.sh with cargo
```

## Real-World Example: claude-usage Integration

### Current claude-usage Structure
```
claude-usage/
├── Cargo.toml          # Manual maintenance
├── src/
│   ├── main.rs         # Manual CLI definition
│   ├── analyzer.rs     # Business logic
│   └── ...
```

### With Goobits Integration
```yaml
# claude-usage/goobits.yaml
language: rust
package_name: claude-usage
command_name: claude-usage
description: "Fast Claude usage analysis across multiple VMs"

dependencies:
  rust_crates:
    serde: { version = "1.0", features = ["derive"] }
    clap: { version = "4.0", features = ["derive"] }
    tokio: { version = "1", features = ["rt-multi-thread"] }
    chrono: { version = "0.4", features = ["serde"] }

cli:
  commands:
    daily:
      desc: "Daily usage analysis with project breakdown"
      options:
        - name: limit
          short: l
          type: usize
          desc: "Limit to last N days"
          default: 30
        - name: json
          type: flag
          desc: "Output as JSON"
        - name: exclude-vms
          type: flag
          desc: "Exclude VM instances"
    
    monthly:
      desc: "Monthly usage aggregation"
      options:
        - name: limit
          short: l
          type: usize
          desc: "Limit to last N months"
        - name: json
          type: flag
          desc: "Output as JSON"
    
    live:
      desc: "Real-time usage monitoring"
      options:
        - name: snapshot
          type: flag
          desc: "One-time snapshot view"
        - name: json
          type: flag
          desc: "Output as JSON"
```

**Benefits for claude-usage:**
- Standardized configuration management
- Consistent CLI patterns with other goobits projects
- Integrated testing framework
- Automatic documentation generation
- Same development workflow as Python projects

## Benefits Analysis

### For Goobits Ecosystem
- **Expanded Market**: Access to Rust CLI developer community
- **Performance Story**: "Generate high-performance CLIs in any language"
- **Differentiation**: First YAML-driven multi-language CLI generator
- **Future Growth**: Foundation for Go, TypeScript, other languages

### For Developers
- **Performance**: Rust CLIs are 10-100x faster than Python equivalents
- **Distribution**: Single binary deployment, no runtime dependencies
- **Memory Safety**: Rust's safety guarantees for system-level tools
- **Ecosystem**: Access to Rust's excellent CLI libraries (clap, serde, tokio)

### For Existing Rust Projects
- **Standardization**: Consistent CLI patterns and configuration
- **Reduced Boilerplate**: Auto-generated CLI structure and argument parsing
- **Integrated Testing**: Same testing framework as Python projects
- **Documentation**: Auto-generated README and help text

## Migration Strategy

### Backward Compatibility
- All existing Python projects continue working unchanged
- `language: python` is default, no migration required
- Same `goobits build`, `goobits test` commands work for all languages

### Gradual Adoption
1. **Release**: Ship Rust support as optional feature
2. **Validate**: Test with claude-usage and other Rust projects
3. **Iterate**: Improve based on real-world usage
4. **Expand**: Add more languages based on community demand

## Success Metrics

### Technical Metrics
- **Generation Speed**: Rust CLI generation completes in <5 seconds
- **Code Quality**: Generated Rust code passes clippy with zero warnings
- **Performance**: Generated CLIs achieve expected performance improvements
- **Compatibility**: Works across Linux, macOS, Windows

### Adoption Metrics
- **Community Interest**: 5+ Rust projects adopt goobits within 6 months
- **Performance Validation**: Generated CLIs show 10x+ speed improvements
- **Developer Feedback**: Positive reception from Rust CLI developer community

## Alternative Approaches Considered

### 1. Separate Tool for Rust
**Pros**: Focused implementation, no complexity in goobits-cli  
**Cons**: Fragmented ecosystem, duplicated effort  
**Decision**: Multi-language support provides better developer experience

### 2. Plugin-Based Architecture
**Pros**: Extensible to any language  
**Cons**: More complex implementation, slower development  
**Decision**: Built-in support for proven languages, plugin system later if needed

### 3. Code Generation Library
**Pros**: Could be used by other tools  
**Cons**: Over-engineering for current needs  
**Decision**: Integrate directly into goobits-cli, extract library later if valuable

## Risks and Mitigation

### Risk: Maintenance Burden
**Mitigation**: Start with Rust only, add languages based on proven demand

### Risk: Language-Specific Complexity
**Mitigation**: Follow each language's best practices, leverage existing libraries

### Risk: Template Maintenance
**Mitigation**: Automated testing for generated code across multiple languages

### Risk: Community Fragmentation
**Mitigation**: Maintain unified documentation and shared testing framework

## Next Steps

1. **Community Validation**: Gather feedback from Rust CLI developers
2. **Prototype**: Build basic Rust generation with claude-usage as test case
3. **Validate**: Ensure generated code meets Rust community standards
4. **Iterate**: Refine based on real-world usage patterns
5. **Document**: Create comprehensive Rust-specific documentation
6. **Release**: Ship as part of goobits-cli v1.3.0

---

**Decision needed**: Proceed with Rust support implementation?