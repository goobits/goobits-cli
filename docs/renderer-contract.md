# Renderer Contract

**Status**: FROZEN (do not modify without migration plan)
**Version**: 1.0.0
**Created**: Phase 0 of Universal-First Refactor

---

## Overview

A **Renderer** transforms the language-agnostic IR (Intermediate Representation) into language-specific CLI code. Each supported language (Python, Node.js, TypeScript, Rust) has its own renderer implementation.

```
IR Dict → LanguageRenderer.render() → List[Artifact]
```

---

## Interface Definition

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

@dataclass(frozen=True)
class Artifact:
    """A single generated file."""
    path: str           # Relative path (e.g., "src/cli.py")
    content: str        # File contents
    executable: bool    # Whether to set executable permission
    metadata: Dict[str, Any]  # Additional metadata (optional)

class LanguageRenderer(ABC):
    """Abstract interface for language-specific renderers."""

    @property
    @abstractmethod
    def language(self) -> str:
        """
        Return the language identifier.

        Returns:
            One of: "python", "nodejs", "typescript", "rust"
        """
        pass

    @abstractmethod
    def render(self, ir: Dict[str, Any]) -> List[Artifact]:
        """
        Transform IR into generated code artifacts.

        Args:
            ir: Intermediate representation (see IR_SCHEMA.md)

        Returns:
            List of Artifact objects to write to disk

        Raises:
            RenderError: If rendering fails
        """
        pass
```

---

## Minimal Implementation

A conforming renderer must:

1. **Implement `language` property** returning one of: `"python"`, `"nodejs"`, `"typescript"`, `"rust"`

2. **Implement `render()` method** that:
   - Accepts an IR dict conforming to `IR_SCHEMA.md`
   - Returns a list of `Artifact` objects
   - Each artifact has a valid `path` and `content`

3. **Generate at minimum**:
   - CLI entry point file (e.g., `cli.py`, `cli.mjs`, `cli.ts`, `main.rs`)
   - Setup/installation script (`setup.sh`)

---

## Extended Interface (Optional)

Renderers MAY implement these additional methods for enhanced functionality:

```python
class LanguageRenderer(ABC):
    # ... required methods ...

    @property
    def file_extensions(self) -> Dict[str, str]:
        """
        Return mapping of component types to file extensions.

        Example:
            {"cli": "py", "hooks": "py", "config": "json"}
        """
        return {}

    def get_template_context(self, ir: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform IR into language-specific template context.

        Used when rendering Jinja2 templates. May add language-specific
        fields, transform naming conventions, etc.

        Args:
            ir: Intermediate representation

        Returns:
            Template context dict
        """
        return ir.copy()

    def get_custom_filters(self) -> Dict[str, callable]:
        """
        Return custom Jinja2 filters for this language.

        Example:
            {"to_snake_case": lambda s: s.lower().replace("-", "_")}
        """
        return {}

    def get_output_structure(self, ir: Dict[str, Any]) -> Dict[str, str]:
        """
        Define output file structure.

        Args:
            ir: Intermediate representation

        Returns:
            Dict mapping component names to output paths
            Example: {"cli": "src/my_cli/cli.py", "setup": "setup.sh"}
        """
        return {}
```

---

## Artifact Requirements

### Path Rules

- Paths are **relative** to the project root
- Use forward slashes (`/`) regardless of OS
- Do not include leading slash
- Valid: `src/cli.py`, `setup.sh`, `pkg/mod.rs`
- Invalid: `/src/cli.py`, `./src/cli.py`, `src\\cli.py`

### Content Rules

- Content must be valid source code for the target language
- Use appropriate line endings (LF for all languages)
- Include proper file headers with generation metadata
- Generated code should be formatted (or marked for formatting)

### Metadata Fields

Standard metadata fields (all optional):

```python
metadata = {
    "generated_by": "goobits-cli",
    "generator_version": "3.0.1",
    "timestamp": "2024-01-15T10:30:00Z",
    "source_config": "goobits.yaml",
    "language": "python",
    "component": "cli",  # cli, hooks, setup, types, etc.
}
```

---

## Error Handling

Renderers must raise `RenderError` (from `core.errors`) for rendering failures:

```python
from goobits_cli.core.errors import RenderError

class PythonRenderer(LanguageRenderer):
    def render(self, ir: Dict[str, Any]) -> List[Artifact]:
        if not ir.get("project", {}).get("command_name"):
            raise RenderError("Missing required field: project.command_name")

        # ... rendering logic ...
```

---

## Registry Pattern

Renderers are accessed through a registry factory:

```python
# universal/renderers/registry.py

RENDERER_REGISTRY = {
    "python": "goobits_cli.universal.renderers.python:PythonRenderer",
    "nodejs": "goobits_cli.universal.renderers.nodejs:NodeJSRenderer",
    "typescript": "goobits_cli.universal.renderers.typescript:TypeScriptRenderer",
    "rust": "goobits_cli.universal.renderers.rust:RustRenderer",
}

def get_renderer(language: str) -> LanguageRenderer:
    """
    Get renderer instance for the specified language.

    Args:
        language: One of "python", "nodejs", "typescript", "rust"

    Returns:
        LanguageRenderer instance

    Raises:
        ValueError: If language is not supported
    """
    if language not in RENDERER_REGISTRY:
        raise ValueError(f"Unsupported language: {language}")

    module_path, class_name = RENDERER_REGISTRY[language].rsplit(":", 1)
    module = importlib.import_module(module_path)
    renderer_class = getattr(module, class_name)
    return renderer_class()
```

---

## Expected Artifacts by Language

### Python

| Component | Path | Description |
|-----------|------|-------------|
| CLI | `src/{package}/cli.py` | Click-based CLI entry point |
| Hooks | `src/{package}/cli_hooks.py` | Hook function stubs (if not exists) |
| Setup | `setup.sh` | Installation script |

### Node.js

| Component | Path | Description |
|-----------|------|-------------|
| CLI | `cli.mjs` | Commander.js-based CLI |
| Hooks | `cli_hooks.mjs` | Hook function stubs |
| Setup | `setup.sh` | Installation script |
| Package | `package.json` | NPM package manifest (merge if exists) |

### TypeScript

| Component | Path | Description |
|-----------|------|-------------|
| CLI | `cli.ts` | Commander.js-based CLI |
| Hooks | `cli_hooks.ts` | Hook function stubs |
| Types | `cli_types.d.ts` | Type definitions |
| Setup | `setup.sh` | Installation script |
| Package | `package.json` | NPM package manifest |
| TSConfig | `tsconfig.json` | TypeScript config (if not exists) |

### Rust

| Component | Path | Description |
|-----------|------|-------------|
| CLI | `src/main.rs` | Clap-based CLI |
| Hooks | `src/cli_hooks.rs` | Hook function stubs |
| Setup | `setup.sh` | Installation script |
| Cargo | `Cargo.toml` | Cargo manifest (merge if exists) |

---

## Testing Requirements

Each renderer must have:

1. **Unit tests** validating:
   - `language` property returns correct value
   - `render()` produces valid artifacts for minimal IR
   - `render()` handles all IR fields correctly
   - Error cases raise `RenderError`

2. **Integration tests** validating:
   - Generated code compiles/parses
   - Generated CLI runs `--help` successfully
   - Hook invocation works

3. **Golden file tests** comparing:
   - Generated output against known-good reference files
   - Detect unintended changes to output format

---

## Migration Notes

- **v1.0.0**: Initial frozen contract
- Renderers implementing this contract are guaranteed compatibility with the orchestrator
- Breaking changes require version bump and migration guide
