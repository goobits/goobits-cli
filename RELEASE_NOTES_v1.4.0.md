# Release Notes: goobits-cli v1.4.0

**Release Date:** 2025-08-04

This is a landmark release for `goobits-cli`, transforming it from a Python-specific tool into a true multi-language CLI generator.

## ✨ New Features

### 🚀 Node.js and TypeScript Support
- **Native Generation:** You can now generate complete, idiomatic Node.js and TypeScript CLI projects by setting `language: nodejs` or `language: typescript` in your `goobits.yaml`.
- **Ecosystem First:** Generated projects include a `package.json`, `setup.sh`, and use Commander.js for a best-in-class developer experience.
- **Full-Featured:** Supports advanced features like interactive prompts (`inquirer`), progress spinners (`ora`), and modern TypeScript configuration.
- **Comprehensive Guide:** See the [Node.js & TypeScript Guide](docs/nodejs_guide.md) for full details.

### 🦀 Rust Support
- **High-Performance CLIs:** Generate fast, memory-safe CLIs in Rust by setting `language: rust`.
- **Cargo Integration:** Automatically generates a `Cargo.toml` file with your specified dependencies from `rust_crates`.
- **Idiomatic Code:** Uses modern Rust patterns with `clap` for argument parsing and `anyhow` for error handling.
- **Comprehensive Guide:** See the [Rust Guide](docs/rust_guide.md) for full details.

## 🔧 Improvements
- **Solidified Generator Architecture:** The underlying generator system has been refactored and tested to reliably support multiple languages.
- **End-to-End Testing:** New E2E tests have been added for all supported languages, ensuring generated projects compile and run correctly.
- **Feature Parity:** All generators now support advanced features like configuration management, plugin systems, and error handling.
- **Enhanced Error Handling:** Comprehensive error types, user-friendly messages, and proper exit codes across all languages.

## 📚 Documentation
- **Comprehensive Guides:** New detailed guides for [Node.js/TypeScript](docs/nodejs_guide.md) and [Rust](docs/rust_guide.md) developers.
- **Updated README:** The main README now showcases multi-language capabilities with examples for each language.

## 🐛 Bug Fixes
- Fixed template rendering issues in generator fallback code
- Resolved dependency version conflicts in generated projects
- Corrected file path handling for cross-platform compatibility

## 💔 Breaking Changes
None - This release maintains full backward compatibility with existing Python projects.

## 🎯 What's Next
- Dynamic tab completion for generated CLIs
- Additional language support (Go, Java)
- Cloud deployment templates

---

Thank you to all contributors who made this multi-language vision a reality! 🎉