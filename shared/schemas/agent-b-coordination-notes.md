# Agent B Coordination Notes
Operational Patterns - Integration Dependencies

## Overview
This document outlines specific coordination requirements between Agent B (Operational Patterns) and Agent A (Code Structure Patterns), along with dependencies on shared systems and potential integration challenges.

## Dependencies on Agent A Patterns

### 1. Command Definition Integration
**Dependency**: Operational features need access to command metadata

**Required Information from Command Structure:**
```yaml
command_metadata:
  name: string                    # For error messages and logging
  description: string             # For help generation
  aliases: string[]               # For completion and error suggestions
  hidden: boolean                # For filtering from help/completion
  parent_command: string         # For error context hierarchy
  global_options: Option[]       # Available in all subcommands
  command_specific_options: Option[]
```

**Integration Points:**
- Error messages include current command name and path
- Configuration precedence may differ per command
- Completion engines need full command hierarchy
- Hook execution context includes command information

### 2. Option Definition Integration  
**Dependency**: Type validation and environment variable mapping require option schema

**Required Information from Options:**
```yaml
option_schema:
  name: string                   # For environment variable naming
  short: string                  # For completion
  type: OptionType              # For validation and coercion
  default: any                  # For config fallback
  required: boolean             # For validation
  choices: any[]                # For completion and validation
  env_var: string               # Override default env var naming
  description: string           # For error messages and help
```

**Integration Points:**
- Environment variable names generated from option definitions
- Configuration validation uses option type constraints
- Error messages reference option names and expected types
- Completion systems use option metadata for suggestions

### 3. Hook System Integration
**Dependency**: Operational patterns may trigger or be triggered by hooks

**Required Hook Information:**
```yaml
hook_registry:
  available_hooks: string[]         # What hooks exist
  hook_phases:
    - pre_command                   # Before command execution
    - post_command                  # After successful execution
    - on_error                      # When command fails
    - on_config_load                # When loading configuration
    - on_completion                 # During completion generation
```

**Integration Points:**
- Error handlers call `on_error` hooks with error context
- Configuration loaders call `on_config_load` hooks
- Completion engines call `on_completion` hooks for dynamic values
- Hook failures must use standard error handling patterns

### 4. Plugin System Integration
**Dependency**: Plugin commands need same operational features

**Required Plugin Information:**
```yaml
plugin_commands:
  command_name: string
  plugin_source: string           # Which plugin provides this command
  inherits_global_options: boolean
  custom_options: Option[]
  supports_completion: boolean
```

**Integration Points:**
- Plugin commands get same error handling as built-in commands
- Plugin options use same validation and environment variable patterns
- Plugin completion integrates with main completion system
- Plugin configuration follows same precedence rules

## Shared Interface Requirements

### 1. Command Registry Interface
**Purpose**: Centralized access to command information for operational features

```typescript
interface CommandRegistry {
  getCommand(name: string): Command | null;
  getAllCommands(): Command[];
  getCommandPath(name: string): string[];        // ["parent", "child"] for nested
  isCommandHidden(name: string): boolean;
  getCommandOptions(name: string): Option[];
  getGlobalOptions(): Option[];
}
```

**Used By:**
- Error handlers (command context in error messages)
- Completion engines (available commands and options)
- Configuration systems (command-specific config sections)
- Help generators (command information display)

### 2. Type Information Interface
**Purpose**: Access to option type definitions for validation and completion

```typescript
interface TypeRegistry {
  getOptionType(command: string, option: string): OptionType;
  validateOptionValue(command: string, option: string, value: any): ValidationResult;
  getOptionChoices(command: string, option: string): string[];
  generateEnvironmentVariableName(command: string, option: string): string;
}
```

**Used By:**
- Configuration validators (type checking config values)
- Environment variable processors (naming and coercion)
- Completion engines (choice value suggestions)
- Error formatters (type-specific error messages)

### 3. Hook Registry Interface
**Purpose**: Coordinated hook execution across command and operational systems

```typescript
interface HookRegistry {
  hasHook(name: string): boolean;
  executeHook(name: string, context: HookContext): Promise<HookResult>;
  registerOperationalHook(name: string, handler: HookHandler): void;
}
```

**Used By:**
- Error handling (on_error hooks)
- Configuration loading (on_config_load hooks)
- Completion generation (on_complete hooks)
- Progress indicators (on_progress hooks)

## Coordination Challenges and Solutions

### Challenge 1: Command Context Propagation
**Problem**: Operational features need to know which command is currently executing

**Solution**: 
- Establish a command context object that flows through all operations
- Include command name, subcommand path, parsed options, and raw arguments
- Pass context to all operational functions (error handlers, config loaders, etc.)

```yaml
command_context:
  command_name: string
  subcommand_path: string[]
  parsed_options: Record<string, any>
  raw_arguments: string[]
  environment: Record<string, string>
  working_directory: string
```

### Challenge 2: Dynamic Command Registration
**Problem**: Plugins can register commands at runtime, after operational systems initialize

**Solution**:
- Use event-driven registration system
- Operational systems listen for command registration events
- Re-initialize completion and help systems when commands change
- Cache operational data but invalidate when command registry changes

### Challenge 3: Cross-Language Type Compatibility
**Problem**: Type validation rules must work consistently across all 4 languages

**Solution**:
- Define type validation in language-neutral schemas (YAML/JSON)
- Generate language-specific validation code from schemas
- Use common test cases to verify type handling consistency
- Document type mapping edge cases and language-specific behaviors

### Challenge 4: Error Context Consistency
**Problem**: Error handling needs consistent context regardless of where error occurs

**Solution**:
- Standardize error context structure across all operational patterns
- Ensure command execution pipeline preserves context through all layers
- Include command context in all error types
- Test error context preservation in integration tests

## Implementation Coordination

### Phase 1: Interface Definition
**Agent A Tasks:**
- Define CommandRegistry interface
- Implement command metadata access methods
- Create TypeRegistry with option information
- Define HookRegistry interface

**Agent B Tasks:**
- Define error context structure
- Create operational pattern interfaces
- Design configuration precedence system
- Plan environment variable naming strategy

**Shared Tasks:**
- Define command context structure
- Establish hook naming conventions
- Create shared testing utilities
- Design plugin integration points

### Phase 2: Core Integration
**Agent A Tasks:**
- Implement command and type registries
- Add hook execution infrastructure
- Create command context propagation
- Add plugin command registration

**Agent B Tasks:**
- Implement error handling with command context
- Add configuration system with type validation
- Create environment variable processing
- Build completion engine with command awareness

**Integration Points:**
- Test command context flow through error scenarios
- Validate type consistency across languages
- Verify plugin command operational features
- Test completion with complex command hierarchies

### Phase 3: Advanced Features
**Agent A Tasks:**
- Add command groups and categorization
- Implement dynamic command loading
- Add command deprecation and migration
- Create command aliasing system

**Agent B Tasks:**
- Add error recovery strategies
- Implement progress indicators
- Add advanced completion features
- Create monitoring and debugging tools

**Integration Points:**
- Test operational features with grouped commands
- Validate error recovery with dynamic commands
- Verify completion with aliased commands
- Test monitoring across command execution paths

## Testing Coordination

### Unit Testing
**Agent A Responsibilities:**
- Test command registration and retrieval
- Test option parsing and validation
- Test hook registration and execution
- Test plugin command integration

**Agent B Responsibilities:**
- Test error handling with mock command context
- Test configuration loading and validation
- Test environment variable processing
- Test completion generation

**Shared Responsibilities:**
- Test interface compatibility between agents
- Test error propagation through full stack
- Test configuration precedence with various option types
- Test completion accuracy with real command definitions

### Integration Testing
**Required Test Scenarios:**
- Complete command execution with all operational features
- Error scenarios that span command and operational systems
- Plugin commands with full operational feature support
- Configuration loading with complex command hierarchies
- Completion generation for nested commands with type constraints

### Cross-Platform Testing
**Coordination Requirements:**
- Use same command definitions across all platforms
- Test operational features on all supported platforms
- Verify error message consistency across platforms
- Test file path handling in configuration and completion

## File Organization for Coordination

### Shared Schemas
```
shared/schemas/
├── command-structure.yaml      # Agent A - command definitions
├── hook-interface.yaml         # Agent A - hook system
├── error-codes.yaml           # Agent B - error handling
├── option-types.yaml          # Agent B - type definitions
└── integration-interfaces.yaml # Shared - interface definitions
```

### Shared Components
```
shared/components/
├── command-context/           # Shared context structure
├── type-validation/           # Shared validation utilities  
├── hook-execution/           # Shared hook infrastructure
└── testing-utilities/        # Shared test helpers
```

### Language-Specific Integration
```
src/templates/{language}/
├── command-registry.{ext}     # Command access implementation
├── type-registry.{ext}        # Type information access
├── hook-registry.{ext}        # Hook execution system
└── operational-integration.{ext} # Bridge operational and command systems
```

## Success Criteria

### Functional Integration
- [ ] Error messages include accurate command context
- [ ] Configuration validation uses command option types
- [ ] Environment variables map correctly to command options
- [ ] Completion works for all command types (simple, nested, plugin)
- [ ] Hook execution integrates smoothly with operational patterns

### Performance Integration  
- [ ] Command context propagation adds minimal overhead
- [ ] Type validation caching improves repeated operations
- [ ] Completion generation responds quickly for large command sets
- [ ] Error handling doesn't significantly slow command execution

### Maintainability Integration
- [ ] Changes to command structure don't break operational features
- [ ] New option types automatically work with all operational patterns
- [ ] Plugin commands get operational features without extra configuration
- [ ] Testing can isolate command vs operational issues

This coordination approach ensures that operational patterns integrate seamlessly with command structures while maintaining the independence and testability of both agent's work.