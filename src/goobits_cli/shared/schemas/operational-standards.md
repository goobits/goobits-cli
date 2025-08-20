# Operational Standards Documentation
Agent B - Operational Patterns

## Overview

This document outlines the operational standards extracted from the pattern analysis, covering runtime behavior, error handling, system operations, and cross-platform compatibility considerations.

## Operational Patterns Summary

### 1. Error Handling (`error_handling`)

**Common Behaviors:**
- Structured error hierarchies with specific error types for each category
- Consistent exit code mapping across all languages
- Rich error context preservation including command name, arguments, and stack traces
- User-friendly error messages with actionable suggestions
- Error recovery strategies for transient failures

**Cross-Platform Standards:**
- Exit codes follow BSD sysexits.h conventions
- Error messages are localization-ready
- File path errors handle platform-specific path separators
- Permission errors provide platform-appropriate guidance

**Language-Specific Optimizations:**
- Python: Exception hierarchy with click integration
- Node.js: Class-based errors with async/await support  
- TypeScript: Result pattern with type-safe error handling
- Rust: Enum-based errors with thiserror/anyhow integration

### 2. Exit Codes (`exit_codes`)

**Standardized Exit Codes:**
- 0: Success
- 1: General error  
- 2: Command misuse (invalid arguments/options)
- 3: Configuration error
- 4: Hook execution error
- 5: Plugin error
- 6: Dependency error
- 7: Network error
- 77: Permission denied
- 78: Command/file not found
- 70: Internal software error
- 130: User cancellation (Ctrl+C)

**Platform Considerations:**
- Windows: Compatible with cmd.exe and PowerShell
- Unix/Linux: Follows POSIX conventions
- macOS: Handles case-insensitive filesystem edge cases

### 3. Configuration Management (`config_management`)

**Common Behaviors:**
- Multi-format support (JSON, YAML, TOML)
- Hierarchical configuration search (current dir, user config, system config)
- Environment variable override capability
- Configuration validation with helpful error messages
- Atomic configuration updates (write to temp, then move)

**Configuration Precedence (highest to lowest):**
1. Command line arguments
2. Environment variables
3. Configuration file values  
4. Default values

**Platform-Specific Paths:**
- Windows: `%APPDATA%\{app-name}\config.json`
- macOS: `~/Library/Application Support/{app-name}/config.json`  
- Linux: `$XDG_CONFIG_HOME/{app-name}/config.json` or `~/.config/{app-name}/config.json`

### 4. Environment Variable Handling (`env_var_handling`)

**Naming Conventions:**
- Format: `{APP_NAME}_{OPTION_NAME}`
- Case conversion: UPPER_CASE
- Separator replacement: Hyphens become underscores
- Prefix patterns: Global vs app-specific vs command-specific

**Value Processing:**
- Boolean parsing: "true"/"false", "1"/"0", "yes"/"no"
- Array separator: Colon (`:`) for PATH-style lists
- Quote handling: Preserve quotes for complex values
- Type coercion: Same rules as command-line options

### 5. Shell Completion (`shell_completion`)

**Supported Shells:**
- Bash: Function-based completion with COMPREPLY
- Zsh: `_arguments` pattern with context-aware completion
- Fish: Declarative completion with subcommand support

**Completion Features:**
- Command and subcommand completion
- Option name completion (--flag, -f)
- Option value completion (for choice types)
- File/directory path completion
- Dynamic completion from runtime context

**Cross-Platform Considerations:**
- Installation paths vary by shell and OS
- User vs system-wide installation options
- Graceful fallback to basic file completion

### 6. Terminal Styling (`terminal_styling`)

**Color Standards:**
- Info: Blue (ℹ)
- Warning: Yellow (⚠)
- Error: Red (✗)
- Critical: Red Bold (💥)
- Success: Green (✓)

**Feature Detection:**
- Check terminal capabilities before using colors
- Respect NO_COLOR environment variable
- Graceful degradation to plain text
- Unicode symbol fallbacks for limited terminals

**Language Libraries:**
- Python: `rich` for advanced formatting, `click.style()` for basic
- Node.js/TypeScript: `chalk` for colors and styles
- Rust: `colored` crate for terminal styling

### 7. Progress Indicators (`progress_indicators`)

**Common Patterns:**
- Progress bars for long-running operations
- Spinners for indeterminate progress
- Step-by-step progress indicators
- Estimated time remaining for lengthy operations

**Behavior Standards:**
- Non-blocking: Don't interfere with user input
- Interruptible: Respect Ctrl+C and cleanup properly
- Terminal-aware: Adapt to terminal width
- Accessible: Provide text alternatives for screen readers

## Integration Points with Agent A

### Command Context Integration
Operational features need access to:
- Current command name (for error messages)
- Command hierarchy path (for nested commands)
- Global vs command-specific options
- Hidden command handling

### Hook System Coordination  
Operational patterns interact with hooks:
- Error handlers may call `on_error` hooks
- Configuration loading may call `on_config_load` hooks
- Completion may call `on_complete_*` hooks for dynamic values
- All hook failures should use consistent error handling

### Option Type Validation
Command options define types that operational systems use:
- Configuration validation uses same type rules as CLI parsing
- Environment variable coercion follows option type definitions
- Completion suggestions respect option types (choice values, file paths)
- Error messages include type-specific guidance

## Cross-Platform Compatibility Matrix

| Feature | Windows | macOS | Linux | Notes |
|---------|---------|--------|-------|-------|
| Exit Codes | ✓ | ✓ | ✓ | Standard across platforms |
| Config Paths | %APPDATA% | ~/Library/... | ~/.config/... | Platform-specific defaults |
| File Permissions | Limited | Full POSIX | Full POSIX | Different permission models |
| Terminal Colors | Limited | Full | Full | Windows needs fallbacks |
| Shell Completion | PowerShell | Bash/Zsh | Bash/Zsh/Fish | Different installation paths |
| Signal Handling | Limited | POSIX | POSIX | Windows uses different signals |

## Error Message Consistency

### Message Structure
```
[Symbol] [Severity]: [Clear Description]
[Context Information]
[Suggestions Section]
```

### Example Messages
```
✗ Error: Configuration file not found
  Looked for config in: ~/.config/myapp/config.json
  
  Suggestions:
    1. Create a configuration file with: myapp config init
    2. Specify a custom config with: --config /path/to/config.json
    3. Run with defaults using: --no-config
```

## Performance Considerations

### Startup Time Optimization
- Lazy load completion engines only when needed
- Cache configuration parsing results
- Minimize file system operations during initialization
- Use efficient data structures for large command hierarchies

### Memory Usage
- Stream large file operations instead of loading into memory
- Clean up temporary files and resources
- Use memory pools for frequently allocated objects
- Profile memory usage in long-running operations

### Network Operations
- Implement timeout and retry logic
- Use connection pooling for repeated requests
- Provide offline/degraded mode capabilities
- Cache network responses when appropriate

## Security Considerations

### Configuration Security
- Validate configuration file permissions (not world-writable)
- Sanitize configuration values before use
- Don't log sensitive configuration values
- Support configuration encryption for sensitive data

### Environment Variable Security
- Don't expose sensitive environment variables in error messages
- Clear sensitive variables from child process environments
- Validate environment variable values same as CLI options
- Log environment variable usage for security audits

### File System Security
- Validate file paths to prevent directory traversal
- Check file permissions before operations
- Use secure temporary file creation
- Clean up temporary files on exit

## Testing Standards

### Unit Testing Requirements
- Test each operational pattern in isolation
- Mock external dependencies (file system, network)
- Test error conditions and edge cases
- Verify cross-platform behavior differences

### Integration Testing
- Test operational patterns with real command structures
- Verify hook system integration
- Test configuration loading with various formats
- Validate completion system with complex command hierarchies

### End-to-End Testing
- Test complete user workflows including errors
- Verify behavior across different terminal environments
- Test installation and setup procedures
- Validate performance under realistic loads

## Monitoring and Observability

### Error Tracking
- Log all errors with sufficient context for debugging
- Track error frequency and patterns
- Correlate errors with user actions and system state
- Provide debugging modes for development

### Performance Monitoring
- Track command execution times
- Monitor configuration loading performance
- Measure completion response times  
- Profile memory usage patterns

### Usage Analytics (Optional)
- Track most-used commands and options
- Identify common error patterns
- Monitor feature adoption rates
- Gather performance benchmarks across platforms

## Migration Path from Current Implementation

### Phase 1: Error Code Standardization
- Map existing error codes to standard categories
- Update exit code usage across all languages
- Maintain backward compatibility for existing scripts

### Phase 2: Configuration Enhancement
- Add multi-format configuration support
- Implement hierarchical configuration search
- Add configuration validation and helpful error messages

### Phase 3: Completion System Improvement
- Enhance shell completion with context awareness
- Add completion for complex option types
- Improve completion installation process

### Phase 4: Advanced Features
- Add progress indicators for long operations
- Implement error recovery strategies
- Add monitoring and observability features

Each phase maintains backward compatibility while adding new operational capabilities.