# Changelog

All notable changes to the Goobits CLI Framework will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Fixed
- README configuration example now includes required `cli.version` field to match schema requirements
- README development commands section reordered with `validate` command listed first as it's most commonly used
- pyproject.toml testpaths now correctly points to `src/tests/` instead of `tests/`
- CODEMAP.md generator file count corrected from "76 Python files" to "4 generator files + __init__.py"
- Completed comprehensive documentation accuracy review - all CLI commands, API references, configuration examples, and installation instructions verified against codebase
- README Quick Start examples corrected to include required arguments (`goobits init <project_name>` and `goobits build <config_path>`)
- README command documentation updated to show `upgrade` command exists in both generated CLI and development CLI
- README hook implementation section clarified that hook files are not auto-generated and must be created manually
- README command arguments changed from optional `[arg]` to required `<arg>` notation where appropriate

### Changed
- Documentation sync and accuracy improvements across all markdown files
- Corrected Universal Template System description from "default" to "optional via --universal-templates flag"
- Fixed README description of --universal-templates from "experimental" to "production-ready" to match goobits.yaml

### Known Issues  
- Performance tests failing due to missing universal_engine attribute in generators
- Generated CLI version shows "v2.0.0" while pyproject.toml shows "3.0.0-alpha.1"

## [3.0.0-alpha.1] - 2024-12

### 🚀 MAJOR RELEASE - Production Ready

This release delivers full multi-language support with unlimited nested commands and production-ready performance.

### Added
- **Unlimited nested commands** - Support for deep command hierarchies (6+ levels tested)
- **Full Rust support** with Clap framework integration
- **Universal Template System** for consistent cross-language generation
- **Interactive mode** for all generated CLIs
- **Shell completions** for bash, zsh, and fish
- **Performance optimization** achieving <100ms startup times

### Changed
- **Template system** unified across all languages
- **Hook signatures** standardized for better consistency
- **Setup scripts** enhanced with progress tracking and validation

### Fixed
- **Node.js dependency resolution** error messages
- **TypeScript compilation** configuration
- **Rust unused variable warnings** in generated code
- **Test suite stability** - comprehensive test coverage across 53 test files

## [1.x] - Previous Versions

Previous versions focused on foundational Python implementation and initial multi-language support. See git history for detailed changes.