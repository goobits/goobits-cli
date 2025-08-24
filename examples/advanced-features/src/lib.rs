//! nested-demo
//!
//! Demonstration of deep nested command capabilities
//!
//! This library provides the core functionality for the demo CLI tool.

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

// Re-export main types for convenience
pub use errors::{CliError, ExitCode, CliResult};
pub use config::Config;

/// Version information
pub const VERSION: &str = env!("CARGO_PKG_VERSION");

/// Package name
pub const PACKAGE_NAME: &str = env!("CARGO_PKG_NAME");

/// Package description
pub const DESCRIPTION: &str = env!("CARGO_PKG_DESCRIPTION");