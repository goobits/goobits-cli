```
================================================================================
                          📍 PROJECT CODEMAP
================================================================================

PROJECT SUMMARY
---------------
  Name:         Goobits CLI Framework
  Type:         Multi-language CLI generator
  Language:     Python (core), Node.js, TypeScript, Rust (targets)
  Framework:    typer (framework CLI), rich-click (generated Python CLIs), Commander.js (Node.js/TS), Clap (Rust)
  Entry Point:  goobits_cli.generated_cli:cli_entry (self-hosted)
  
  Total Files:  400+ files across core, templates, and tests
  Total LOC:    ~15,000+ lines including templates

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
├── src/goobits_cli/           [Core framework - 8.8K+ LOC]
│   ├── main.py               [CLI entry point - build/init/serve]
│   ├── builder.py            [Routes to language generators]
│   ├── schemas.py            [YAML config validation (Pydantic)]
│   ├── generators/ [4]       [Language-specific generators]
│   │   ├── python.py        [Python/Click generator]
│   │   ├── nodejs.py        [Node.js/Commander generator]
│   │   ├── typescript.py    [TypeScript generator]
│   │   └── rust.py          [Rust/Clap generator]
│   ├── templates/            [Jinja2 templates by language]
│   │   ├── *.py.j2          [Python CLI templates]
│   │   ├── nodejs/          [Node.js templates & package.json]
│   │   ├── typescript/      [TS templates & build configs]
│   │   └── rust/            [Rust templates & Cargo.toml]
│   ├── universal/           [Universal Template System v2.0]
│   │   ├── template_engine.py [Cross-language template engine]
│   │   ├── renderers/       [Language-specific renderers]
│   │   ├── interactive/     [Interactive mode components]
│   │   ├── plugins/         [Plugin system & marketplace]
│   │   ├── performance/     [Performance monitoring]
│   │   └── completion/      [Dynamic completion system]
│   └── shared/              [Cross-language utilities]
├── src/tests/ [29]          [Comprehensive test suite]
│   ├── unit/                [Unit tests by component]
│   ├── integration/         [Cross-language integration]
│   ├── e2e/                 [End-to-end CLI testing]
│   └── performance/         [Real performance benchmarks]
├── performance/             [Performance validation suite]
├── docs/                    [Architecture & usage guides]
├── shared/                  [Shared schemas & components]
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
  • typer         - Python CLI framework (framework itself)
  • rich-click    - Enhanced Click for generated Python CLIs
  • pydantic      - YAML config validation
  • jinja2        - Template rendering
  • pyyaml        - YAML parsing

DEVELOPMENT:
  • pytest       - Test framework (696 tests)
  • mypy         - Type checking
  • ruff         - Python linting  
  • coverage     - Test coverage analysis

Generated CLIs Use:
  • Python: rich-click, pydantic, rich (terminal UI)
  • Node.js: commander, chalk, inquirer
  • TypeScript: clap-like libs, type definitions

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

To use Universal Templates:
  Flag: goobits build --universal-templates
  Files: universal/template_engine.py, universal/renderers/

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
  • Initialize:  goobits init
  • Serve PyPI:  goobits serve
  • Upgrade:     goobits upgrade
  • Universal:   goobits build --universal-templates

Development:
  • Install:     ./setup.sh install --dev
  • Test:        pytest src/tests/
  • Coverage:    pytest --cov=goobits_cli
  • Type check:  mypy src/goobits_cli/
  • Lint:        ruff check src/

================================================================================

⚠️ GOTCHAS & NOTES
------------------

• Self-hosting: goobits generates its own CLI from goobits.yaml
• All 4 languages work end-to-end with production quality
• Universal templates (--universal-templates) are v2.0 system
• Performance: Generated CLIs <100ms startup target met
• Interactive mode available for all generated CLIs
• Rust support fully operational with Clap framework
• Test coverage: 696 tests, all passing
• Generated CLIs use hook system: hooks.py/js/ts/rs for logic

================================================================================
```