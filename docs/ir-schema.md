# IR (Intermediate Representation) Schema

**Status**: FROZEN (do not modify without migration plan)
**Version**: 1.0.0
**Created**: Phase 0 of Universal-First Refactor

---

## Overview

The Intermediate Representation (IR) is a language-agnostic data structure that represents a CLI configuration. It serves as the bridge between `goobits.yaml` parsing and language-specific code generation.

```
goobits.yaml → IRBuilder.build() → IR Dict → LanguageRenderer → Generated Code
```

---

## Top-Level Structure

```python
IR = {
    "project": ProjectInfo,
    "cli": CLISchema,
    "installation": InstallationInfo,
    "dependencies": DependencyInfo,
    "features": FeatureFlags,
    "feature_requirements": FeatureRequirements,
    "metadata": GenerationMetadata,
}
```

---

## Type Definitions

### ProjectInfo

```python
@dataclass(frozen=True)
class ProjectInfo:
    name: str                    # Display name (e.g., "My CLI Tool")
    description: Optional[str]   # Project description
    version: str                 # Version string (default: "1.0.0")
    author: Optional[str]        # Author name
    license: Optional[str]       # License identifier (e.g., "MIT")
    package_name: str            # Python package name (e.g., "my-cli-tool")
    command_name: str            # CLI command name (e.g., "mycli")
    cli_path: Optional[str]      # Output path for generated CLI
    cli_hooks_path: Optional[str]  # Path to hooks file
```

### CLISchema

```python
@dataclass(frozen=True)
class CLISchema:
    root_command: RootCommand    # Root command definition
    commands: Dict[str, Command] # Named command lookup
    global_options: List[Option] # Options available on all commands
    completion: CompletionConfig # Shell completion settings
    tagline: str                 # Short description for help
    description: str             # Full description
    header_sections: List[dict]  # Custom help header sections
    footer_note: Optional[str]   # Footer text for help
    version: str                 # CLI version string
```

### RootCommand

```python
@dataclass(frozen=True)
class RootCommand:
    name: str                    # Command name
    description: str             # Command description
    version: str                 # Version string
    arguments: List[Argument]    # Positional arguments
    options: List[Option]        # Command options
    subcommands: List[Command]   # Child commands
```

### Command

```python
@dataclass(frozen=True)
class Command:
    name: str                    # Command name (e.g., "status")
    description: str             # Command description
    arguments: List[Argument]    # Positional arguments
    options: List[Option]        # Command options
    subcommands: List[Command]   # Nested subcommands (recursive)
    hook_name: str               # Hook function name (e.g., "on_status")
```

### Argument

```python
@dataclass(frozen=True)
class Argument:
    name: str                    # Argument name
    description: str             # Help text
    type: str                    # Type: "string", "int", "float", "bool", "path"
    required: bool               # Whether argument is required
    default: Optional[Any]       # Default value
    multiple: bool               # Accept multiple values
    nargs: Optional[str]         # Nargs specifier: "*", "+", "?"
```

### Option

```python
@dataclass(frozen=True)
class Option:
    name: str                    # Long option name (e.g., "verbose")
    short: Optional[str]         # Short option (e.g., "v")
    description: str             # Help text
    type: str                    # Type: "str", "int", "float", "bool", "choice"
    default: Optional[Any]       # Default value
    required: bool               # Whether option is required
    multiple: bool               # Accept multiple values
    choices: Optional[List[str]] # Valid choices (for type="choice")
```

### CompletionConfig

```python
@dataclass(frozen=True)
class CompletionConfig:
    enabled: bool                # Whether completion is enabled
    shells: List[str]            # Supported shells: ["bash", "zsh", "fish"]
```

### InstallationInfo

```python
@dataclass(frozen=True)
class InstallationInfo:
    pypi_name: str               # PyPI package name
    development_path: str        # Dev install path (default: ".")
    extras: Dict[str, List[str]] # Extra dependencies by category
```

### DependencyInfo

```python
@dataclass(frozen=True)
class DependencyInfo:
    python: List[str]            # Python package dependencies
    system: List[str]            # System package dependencies
    optional: Dict[str, List[str]]  # Optional dependency groups
```

### FeatureFlags

```python
@dataclass(frozen=True)
class FeatureFlags:
    interactive_mode: bool       # Enable interactive REPL
    shell_completion: bool       # Enable shell completion
    plugin_system: bool          # Enable plugin loading
    config_management: bool      # Enable config file support
```

### FeatureRequirements

```python
@dataclass(frozen=True)
class FeatureRequirements:
    needs_rich: bool             # Requires rich library
    needs_prompt_toolkit: bool   # Requires prompt_toolkit
    needs_config_manager: bool   # Requires config management
    needs_completion: bool       # Requires completion support
    complexity_score: int        # 0-100 complexity rating
```

### GenerationMetadata

```python
@dataclass(frozen=True)
class GenerationMetadata:
    generated_at: str            # ISO timestamp (filled at render time)
    generator_version: str       # goobits-cli version
    source_config: dict          # Original config (for debugging)
    config_filename: str         # Source filename
```

---

## Example IR Output

```python
{
    "project": {
        "name": "My CLI",
        "description": "A sample CLI tool",
        "version": "1.0.0",
        "author": "Developer",
        "license": "MIT",
        "package_name": "my-cli",
        "command_name": "mycli",
        "cli_path": "src/my_cli/cli.py",
        "cli_hooks_path": "src/my_cli/cli_hooks.py",
    },
    "cli": {
        "root_command": {
            "name": "mycli",
            "description": "A sample CLI tool",
            "version": "1.0.0",
            "arguments": [],
            "options": [
                {
                    "name": "verbose",
                    "short": "v",
                    "description": "Enable verbose output",
                    "type": "bool",
                    "default": False,
                    "required": False,
                    "multiple": False,
                }
            ],
            "subcommands": [
                {
                    "name": "status",
                    "description": "Show current status",
                    "arguments": [],
                    "options": [],
                    "subcommands": [],
                    "hook_name": "on_status",
                }
            ],
        },
        "commands": {
            "status": { ... }  # Same as above
        },
        "global_options": [],
        "completion": {
            "enabled": True,
            "shells": ["bash", "zsh", "fish"],
        },
        "tagline": "A sample CLI tool",
        "description": "A sample CLI tool for demonstration",
        "header_sections": [],
        "footer_note": None,
        "version": "1.0.0",
    },
    "installation": {
        "pypi_name": "my-cli",
        "development_path": ".",
        "extras": {
            "dev": ["pytest", "black"],
        },
    },
    "dependencies": {
        "python": ["click>=8.0.0", "rich>=10.0.0"],
        "system": [],
        "optional": {},
    },
    "features": {
        "interactive_mode": False,
        "shell_completion": True,
        "plugin_system": False,
        "config_management": False,
    },
    "feature_requirements": {
        "needs_rich": True,
        "needs_prompt_toolkit": False,
        "needs_config_manager": False,
        "needs_completion": True,
        "complexity_score": 25,
    },
    "metadata": {
        "generated_at": "2024-01-15T10:30:00Z",
        "generator_version": "3.0.1",
        "source_config": { ... },
        "config_filename": "goobits.yaml",
    },
}
```

---

## Validation Rules

1. **Required Fields**:
   - `project.package_name` must be non-empty
   - `project.command_name` must be non-empty
   - `cli.root_command.name` must be non-empty

2. **Type Constraints**:
   - `Option.type` must be one of: `"str"`, `"int"`, `"float"`, `"bool"`, `"choice"`, `"path"`
   - `Argument.type` must be one of: `"string"`, `"int"`, `"float"`, `"bool"`, `"path"`
   - `Command.hook_name` must match pattern: `on_[a-z_]+`

3. **Consistency**:
   - Every command in `cli.root_command.subcommands` must exist in `cli.commands`
   - `Option.choices` must be non-empty if `Option.type == "choice"`

---

## Migration Notes

- **v1.0.0**: Initial frozen schema
- Future versions must provide migration utilities in `migrations/`
