//! demo-rust-cli
//!
//! A sample Rust CLI built with Goobits
//!
//! This library provides the core functionality for the demo_rust CLI tool.

#![warn(missing_docs)]
#![warn(clippy::all)]

/// Error types and handling
pub mod errors;

/// Configuration management
pub mod config;

/// Hook system for extensibility
pub mod hooks;

/// Command completion support
pub mod completion;

/// CLI command handlers
pub mod cli;

/// Structured logging functionality
pub mod logger;

// Re-export main types for convenience
pub use errors::{CliError, ExitCode, CliResult};
pub use config::Config;

/// Version information
pub const VERSION: &str = env!("CARGO_PKG_VERSION");

/// Package name
pub const PACKAGE_NAME: &str = env!("CARGO_PKG_NAME");

/// Package description
pub const DESCRIPTION: &str = env!("CARGO_PKG_DESCRIPTION");