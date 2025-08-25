# Changelog

All notable changes to the Goobits CLI Framework will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed
- Documentation sync and accuracy improvements

## [2.0.0] - 2024-12

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
- **Test suite stability** - all 696 tests passing

## [1.x] - Previous Versions

Previous versions focused on foundational Python implementation and initial multi-language support. See git history for detailed changes.