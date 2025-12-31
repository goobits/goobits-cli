# Proposal 001: Unified Help Formatter System

**Status:** Phase 1 Complete, Phase 2-5 Pending
**Created:** 2024-12-30
**Author:** Claude Code

## Summary

Implement a unified help output formatting system that produces identical `--help` output across all 4 supported languages (Python, Node.js, TypeScript, Rust) while preserving native CLI framework functionality (Click, Commander, Clap).

## Problem Statement

Currently, goobits-cli generates CLIs using native frameworks for each language:

| Language | Framework | Help Style |
|----------|-----------|------------|
| Python | Click/rich-click | Rich formatted, colorful panels |
| Node.js | Commander.js | Plain, simple text |
| TypeScript | Commander.js | Same as Node.js |
| Rust | Clap | Structured, detailed |

**The problem:** The same `goobits.yaml` produces 4 different-looking CLIs. Users expect consistent branding and UX across their tooling, regardless of implementation language.

### Current Output Example

```bash
# Python (Click)
$ mycli --help
Usage: mycli [OPTIONS] COMMAND [ARGS]...

  My awesome CLI tool

Options:
  --version  Show version
  --help     Show this message and exit.

Commands:
  build  Build the project
```

```bash
# Rust (Clap)
$ mycli --help
My awesome CLI tool

Usage: mycli <COMMAND>

Commands:
  build  Build the project

Options:
  -h, --help     Print help
  -V, --version  Print version
```

## Solution

### Architecture

Create a single-source-of-truth format specification that generates consistent formatters for each language:

```
┌─────────────────────────────────────────────────────────┐
│  spec.py (HelpFormatSpec)                               │
│  - Section headers: USAGE, ARGUMENTS, OPTIONS, COMMANDS │
│  - Layout: column widths, indentation, spacing          │
│  - Colors: command=cyan, option=green, error=red        │
│  - Templates: usage line, option signatures, etc.       │
└─────────────────────────────────────────────────────────┘
                          │
          ┌───────────────┼───────────────┐
          ▼               ▼               ▼
    ┌──────────┐    ┌──────────┐    ┌──────────┐
    │ Python   │    │ Node/TS  │    │  Rust    │
    │ Click    │    │ Commander│    │  Clap    │
    │ formatter│    │ formatter│    │ formatter│
    └──────────┘    └──────────┘    └──────────┘
          │               │               │
          ▼               ▼               ▼
    ┌──────────┐    ┌──────────┐    ┌──────────┐
    │ Custom   │    │configure │    │ help_    │
    │ Help     │    │ Help()   │    │ template │
    │ Formatter│    │          │    │          │
    └──────────┘    └──────────┘    └──────────┘
```

### Key Design Decisions

1. **Keep native frameworks**: Still use Click, Commander, Clap under the hood
2. **Customize only output**: Override help formatters, not parsing/validation
3. **Single source of truth**: One spec, 4 formatters derived from it
4. **No runtime dependency**: Generated code is self-contained
5. **Preserve all features**: Tab completion, validation, etc. unchanged

### Unified Output Format

```
mycli v1.0.0

My awesome CLI tool

USAGE:
    mycli [OPTIONS] <COMMAND> [ARGS]

ARGUMENTS:
    <INPUT>              Input file to process
    [OUTPUT]             Output file (optional)

OPTIONS:
    -h, --help           Show this help message and exit
    -V, --version        Show version information
    -v, --verbose        Enable verbose output
    -o, --output <PATH>  Output directory

COMMANDS:
    build                Build the project
    init                 Initialize new project
    test                 Run tests
```

## Implementation

### Phase 1: Core Infrastructure ✅ COMPLETE

**Files Created:**
```
src/goobits_cli/universal/formatters/
├── __init__.py                    # Package exports
├── spec.py                        # HelpFormatSpec class (THE source of truth)
├── python_formatter.py            # PythonHelpFormatter (Click)
├── nodejs_formatter.py            # NodeJSHelpFormatter (Commander)
├── typescript_formatter.py        # TypeScriptHelpFormatter (Commander + types)
└── rust_formatter.py              # RustHelpFormatter (Clap)
```

**Files Modified:**
```
src/goobits_cli/universal/renderers/
├── python_renderer.py             # Added unified_formatter to context
├── nodejs_renderer.py             # Added unified_formatter to context
├── typescript_renderer.py         # Added unified_formatter to context
└── rust_renderer.py               # Added unified_formatter to context
```

**Tests Added:**
```
src/tests/unit/formatters/
├── __init__.py
└── test_unified_formatters.py     # 36 tests
```

**Stats:**
- New code: ~810 lines
- Tests: 36 new, 366 total passing
- Commit: `8d55e9c`

### Phase 2: Template Integration 🔲 PENDING

Update Jinja2 templates to embed formatter code:

```jinja2
{# In cli.py.j2 #}
{{ unified_formatter.code }}

@click.group(cls=GoobitsGroup)
def cli():
    ...
```

```jinja2
{# In cli.mjs.j2 #}
{{ unified_formatter.code }}

{{ unified_formatter.setup_call }}
```

```rust
// In cli.rs.j2
{{ unified_formatter.full_code }}

fn main() {
    let cmd = with_unified_help(Command::new("mycli"));
    ...
}
```

**Effort:** ~2-3 days

### Phase 3: End-to-End Validation 🔲 PENDING

Generate test CLIs and verify identical output:

```bash
# Generate in all languages
for lang in python nodejs typescript rust; do
    goobits build test.yaml --language $lang --output test-$lang/
done

# Compare help output
diff <(python test-python/cli.py --help) <(node test-nodejs/cli.mjs --help)
diff <(node test-nodejs/cli.mjs --help) <(./test-rust/target/release/cli --help)
```

**Effort:** ~1 day

### Phase 4: Customization Support 🔲 OPTIONAL

Allow users to customize format in `goobits.yaml`:

```yaml
# goobits.yaml
help_format:
  style: unified          # "unified" | "native"
  headers:
    usage: "HOW TO USE"
    options: "FLAGS"
    commands: "SUBCOMMANDS"
  layout:
    max_width: 120
    indent: 2
  colors:
    enabled: true
    command: blue
    option: green
```

**Effort:** ~1 day

### Phase 5: Documentation 🔲 PENDING

- Update CLAUDE.md with unified formatter section
- Add examples to user guide
- Document customization options

**Effort:** ~0.5 days

## Benefits

| Benefit | Impact |
|---------|--------|
| **Consistent UX** | Same help output regardless of language |
| **Brand consistency** | Professional, unified appearance |
| **Reduced maintenance** | Change format in one place |
| **Easy customization** | Single spec to modify |
| **Adding new languages** | Just write ~100 line formatter |

## Non-Goals

- Replace native frameworks (Click, Commander, Clap)
- Modify argument parsing behavior
- Change validation logic
- Affect tab completion
- Create runtime dependencies

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Framework updates break formatters | Version-pin frameworks, test on updates |
| Complex help formatting edge cases | Comprehensive test suite, fallback to native |
| Performance overhead | Formatters generate static code, no runtime cost |

## Success Criteria

1. ✅ All 4 language formatters generate syntactically valid code
2. 🔲 Generated CLIs produce identical `--help` output (modulo version numbers)
3. 🔲 All native features (completion, validation) still work
4. 🔲 No performance regression in CLI startup time
5. ✅ 100% test coverage for formatter logic

## Timeline

| Phase | Effort | Status |
|-------|--------|--------|
| 1. Core Infrastructure | 1 week | ✅ Complete |
| 2. Template Integration | 2-3 days | 🔲 Next |
| 3. E2E Validation | 1 day | 🔲 Pending |
| 4. Customization | 1 day | 🔲 Optional |
| 5. Documentation | 0.5 days | 🔲 Pending |
| **Total** | **~2 weeks** | **~50% complete** |

## References

- Click custom formatters: https://click.palletsprojects.com/en/8.1.x/api/#click.HelpFormatter
- Commander.js configureHelp: https://github.com/tj/commander.js#custom-help
- Clap help_template: https://docs.rs/clap/latest/clap/struct.Command.html#method.help_template
