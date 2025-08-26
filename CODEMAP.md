```
================================================================================
                          📍 PROJECT CODEMAP
================================================================================

PROJECT SUMMARY
---------------
  Name:         Goobits CLI Framework
  Type:         Multi-language CLI generator
  Language:     Python (core), Node.js, TypeScript, Rust (targets)
  Framework:    Click/rich-click (generated Python CLIs), Commander.js (Node.js/TS), Clap (Rust)
  Entry Point:  goobits_cli.generated_cli:cli_entry (self-hosted)
  
  Total Files:  4 generator files + __init__.py, 55 test files
  Total LOC:    ~60,000+ lines of Python code

================================================================================

🏗️ ARCHITECTURE OVERVIEW
------------------------

┌─────────────┐     ┌─────────────┐     ┌─────────────────┐
│    YAML     │────▶│  Generator  │────▶│   CLI Code      │
│ goobits.yaml│     │   Engine    │     │Python/JS/TS/Rust│
└─────────────┘     └─────────────┘     └─────────────────┘
        │                   │                    │
   Configuration        Template            Generated
   (User Input)        Processing           Applications
                      (Jinja2/Univ)

Key Patterns:
  • Generator Pattern: Language-specific code generators
  • Template Engine: Jinja2 + Universal template system
  • Plugin Architecture: Extensible command/feature system
  • Self-Hosting: goobits generates its own CLI

================================================================================

📁 DIRECTORY STRUCTURE
----------------------

[root]/
├── src/goobits_cli/           [Core framework - 60K+ LOC]
│   ├── main.py               [CLI entry point - build/init/serve]
│   ├── builder.py            [Routes to language generators]
│   ├── schemas.py            [YAML config validation (Pydantic)]
│   ├── generators/ [5]       [4 Language-specific generators + __init__.py]
│   │   ├── python.py        [Python/Click generator]
│   │   ├── nodejs.py        [Node.js/Commander generator]
│   │   ├── typescript.py    [TypeScript generator]
│   │   └── rust.py          [Rust/Clap generator]
│   ├── templates/            [Jinja2 templates by language]
│   │   ├── *.py.j2          [Python CLI templates]
│   │   ├── nodejs/          [Node.js templates & package.json]
│   │   ├── typescript/      [TS templates & build configs]
│   │   └── rust/            [Rust templates & Cargo.toml]
│   ├── universal/           [Universal Template System v3.0]
│   │   ├── template_engine.py [Cross-language template engine]
│   │   ├── renderers/       [Language-specific renderers]
│   │   ├── interactive/     [Interactive mode components]
│   │   ├── plugins/         [Plugin system & marketplace]
│   │   ├── performance/     [Performance monitoring]
│   │   └── completion/      [Dynamic completion system]
│   └── shared/              [Cross-language utilities]
├── src/tests/               [Comprehensive test suite - 55 test files]
│   ├── unit/                [Unit tests by component]
│   ├── integration/         [Cross-language integration]
│   ├── e2e/                 [End-to-end CLI testing]
│   └── performance/         [Real performance benchmarks]
├── performance/             [Performance validation suite]
├── docs/                    [Architecture & usage guides]
└── goobits.yaml            [Self-hosting configuration]

================================================================================

🔑 KEY FILES (Start Here)
-------------------------

ENTRY POINTS:
  • src/goobits_cli/main.py     - CLI commands (build/init/serve)
  • src/goobits_cli/builder.py  - Language routing & generation
  • goobits.yaml               - Self-hosting config example

CORE LOGIC:
  • src/goobits_cli/schemas.py  - YAML validation (Pydantic)
  • src/goobits_cli/generators/ - Language-specific generators
  • src/goobits_cli/universal/  - Universal template system

CONFIGURATION:
  • pyproject.toml             - Python dependencies & build
  • CLAUDE.md                  - Development instructions
  • setup.sh                   - Installation script

================================================================================

🔄 DATA FLOW
------------

1. CLI Input:
   [main.py] → [load_yaml_config] → [schemas.py validation]

2. Code Generation:
   [builder.py] → [language generator] → [templates/] → [output]

3. Universal System:
   [template_engine.py] → [renderers/] → [components/] → [output]

Key Relationships:
  • main.py depends on → builder.py, schemas.py
  • builder.py routes to → generators/{python,nodejs,typescript}.py
  • generators/ use → templates/[lang]/, shared/components/
  • universal/ provides → cross-language consistency

================================================================================

📦 DEPENDENCIES
---------------

PRODUCTION:
  • click         - Python CLI framework core
  • rich-click    - Enhanced Click for generated Python CLIs
  • rich          - Terminal UI components
  • jinja2        - Template rendering
  • pyyaml        - YAML parsing

DEVELOPMENT:
  • pytest       - Test framework
  • mypy         - Type checking
  • black        - Code formatting
  • flake8       - Python linting  
  • coverage     - Test coverage analysis

Generated CLIs Use:
  • Python: rich-click, pydantic, rich (terminal UI)
  • Node.js: commander, chalk, inquirer
  • TypeScript: commander, type definitions
  • Rust: clap, anyhow, colored

================================================================================

🎯 COMMON TASKS
---------------

To understand CLI generation:
  Start with: goobits.yaml → main.py → builder.py → generators/

To modify Python generation:
  Core files: generators/python.py, templates/*.py.j2
  Tests: src/tests/unit/test_*.py

To add new language support:
  1. Create generator in generators/[lang].py
  2. Add templates in templates/[lang]/
  3. Update builder.py routing
  4. Add tests in src/tests/
  5. Update schemas.py if needed

Universal Template System (Default):
  Core: universal/template_engine.py, universal/renderers/
  Provides consistent cross-language CLI generation

================================================================================

⚡ QUICK REFERENCE
-----------------

Naming Conventions:
  • Files:       snake_case.py, kebab-case.js
  • Classes:     PascalCase (schemas, generators)
  • Functions:   snake_case (Python), camelCase (JS/TS)
  • Templates:   snake_case.j2

CLI Commands:
  • Generate:    goobits build [config.yaml]
  • Initialize:  goobits init [project_name]
  • Validate:    python -m goobits_cli.main validate [config_path]
  • Migrate:     python -m goobits_cli.main migrate <path>
  • Serve PyPI:  goobits serve <directory>
  • Upgrade:     python -m goobits_cli.main upgrade

Development:
  • Install:     ./setup.sh install --dev
  • Test:        pytest src/tests/
  • Coverage:    pytest --cov=goobits_cli
  • Type check:  mypy src/goobits_cli/
  • Format:      black src/
  • Lint:        flake8 src/

================================================================================

⚠️ GOTCHAS & NOTES
------------------

• Self-hosting: goobits generates its own CLI from goobits.yaml
• All 4 languages work end-to-end with production quality
• Universal template system (always enabled for consistency)
• Performance: Generated CLIs <100ms startup target met
• Interactive mode available for all generated CLIs
• Rust support fully operational with Clap framework
• Test coverage: 55 test files, comprehensive coverage
• Generated CLIs use hook system: hooks.py/js/ts/rs for logic

================================================================================
```