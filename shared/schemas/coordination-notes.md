# Coordination Notes - Agent A to Agent B

## Overview
This document outlines coordination points between Agent A (Code Structure) and Agent B (Operational Patterns).

## Shared Dependencies

### 1. Command Context
The command structure schemas define what information is available to operational features:
- Command name and description (for error messages)
- Option values (for config defaults)
- Global flags (for debug mode, verbosity)

### 2. Hook System Integration
Operational patterns often need to call hooks:
- **Error handling**: May call `on_error` hooks
- **Config loading**: May call `on_config_load` hooks
- **Completion**: May call `on_complete_*` hooks

### 3. Exit Code Coordination
Commands return values that operational patterns convert to exit codes:
- Python: `return False` → exit(1)
- Node.js: `return false` → process.exit(1)
- TypeScript: `Result.failure()` → process.exit(1)
- Rust: `Err(_)` → exit code 1

## Areas Requiring Coordination

### 1. Error Context
When operational patterns handle errors, they need:
- Current command name (from command structure)
- Hook function that failed (from hook registry)
- Parameter values (from command args/options)

**Recommendation**: Error handlers should receive a context object with:
```yaml
error_context:
  command: string
  subcommand?: string
  hook_name?: string
  args: object
  error: Error
```

### 2. Configuration Defaults
Command options often have defaults that should be:
- Overridable by config files
- Overridable by environment variables

**Recommendation**: Priority order should be:
1. Command line argument (highest)
2. Environment variable
3. Config file
4. Command option default (lowest)

### 3. Shell Completion
Completion needs to know:
- All command names and aliases
- Option names and types
- Argument expectations (required, variadic)
- Choice constraints

**Recommendation**: Command structure should expose a "schema export" that completion can consume.

### 4. Plugin Commands
Plugins can register new commands that need:
- Same error handling
- Same config access
- Same completion support

**Recommendation**: Plugin-registered commands should go through the same command structure validation.

## Interface Points

### 1. Command Registry
Both agents need access to:
```yaml
command_registry:
  get_command(name: string): Command
  get_all_commands(): Command[]
  get_command_path(name: string): string[]  # For nested commands
```

### 2. Hook Registry
Operational features need to check/call hooks:
```yaml
hook_registry:
  has_hook(name: string): boolean
  call_hook(name: string, args: object): Result
  get_hook_names(): string[]
```

### 3. Type Information
For validation and completion:
```yaml
type_info:
  get_option_type(command: string, option: string): Type
  get_argument_type(command: string, arg: string): Type
  get_choices(command: string, param: string): string[]
```

## Potential Conflicts

### 1. Global Options
- Agent A defines global options on the main command
- Agent B needs these available in all subcommands
- Solution: Ensure context passing includes global options

### 2. Hidden Commands
- Agent A supports hidden commands (like `_completion`)
- Agent B's help system should respect visibility
- Solution: Add `is_visible()` check to command registry

### 3. Command Aliases
- Agent A allows command aliases
- Agent B's completion needs to handle all aliases
- Solution: Expand aliases in completion engine

## Recommendations for Agent B

1. **Use Command Registry**: Don't parse commands directly; use the registry
2. **Respect Hook Conventions**: Always check for hooks before default behavior
3. **Preserve Context**: Pass full command context through operational flows
4. **Handle Missing Commands**: Gracefully handle plugin/dynamic commands

## Testing Coordination

Both agents should test:
- Command with all operational features (completion, config, etc.)
- Operational features with all command types (simple, nested, plugin)
- Error paths through both command and operational code

## File Organization

Suggested shared structure:
```
shared/
  schemas/
    command-structure.yaml     # Agent A
    hook-interface.yaml        # Agent A
    error-handling.yaml        # Agent B
    config-management.yaml     # Agent B
  interfaces/
    registries.yaml            # Shared interfaces
    contexts.yaml              # Shared context types
```