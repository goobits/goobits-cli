# Goobits CLI Incremental Refactor Proposal

**Status**: Draft
**Approach**: Move + Refactor (preserve fine-tuned logic)
**Philosophy**: The code works. 534 tests pass. We reorganize, extract, and simplify - we don't rewrite.

---

## Goals

- **Reorganize**: Move files to logical locations, flatten deep nesting
- **Extract**: Pull duplicated code into shared modules (don't rewrite it)
- **Simplify**: Break large classes into focused modules (move methods, don't recreate)
- **Preserve**: Keep all fine-tuned logic, edge case handling, and battle-tested code

## Non-Goals

- Rewriting working code from scratch
- Changing APIs unless absolutely necessary
- Breaking changes to generated CLI output
- Maintaining backward compatibility shims (clean breaks only)

## Principles

1. **Move before modify** - `git mv` first, refactor second (preserves history)
2. **Extract, don't rewrite** - Copy working code to shared location, then delete duplicates
3. **Tests pass at every commit** - No "break everything then fix" phases
4. **One responsibility per PR** - Small, reviewable changes

---

## Current Structure → Target Structure

```
CURRENT                                    TARGET
src/goobits_cli/                          src/goobits_cli/
├── main.py (2100 lines!)                 ├── cli.py (thin entry point)
├── builder.py                            ├── core/
├── schemas.py                            │   ├── config.py (← schemas.py)
├── config_manager.py                     │   ├── loader.py (← config_manager.py)
├── logger.py                             │   ├── errors.py (← extracted)
├── formatter.py                          │   └── logging.py (← logger.py)
├── generators/                           ├── generation/
│   ├── python.py                         │   ├── engine.py (← builder.py core logic)
│   ├── nodejs.py                         │   ├── ir.py (← extracted from engine)
│   ├── typescript.py                     │   ├── renderers/
│   └── rust.py                           │   │   ├── base.py (← extracted shared code)
├── universal/                            │   │   ├── python.py (← generators/python.py)
│   ├── template_engine.py (1900 lines!)  │   │   ├── nodejs.py (← generators/nodejs.py)
│   ├── component_registry.py             │   │   ├── typescript.py (← generators/typescript.py)
│   ├── renderers/*.py                    │   │   └── rust.py (← generators/rust.py)
│   ├── interactive/                      │   └── templates/
│   ├── completion/                       │       └── loader.py (← component_registry.py)
│   ├── plugins/                          ├── features/
│   └── ...                               │   ├── interactive.py (← universal/interactive/)
├── shared/                               │   ├── completion.py (← universal/completion/)
│   ├── components/                       │   └── plugins.py (← universal/plugins/)
│   └── test_utils/                       ├── validation/
└── migrations/                           │   └── framework.py (← shared/components/ unified)
                                          └── utils/
                                              ├── strings.py (← extracted)
                                              ├── paths.py (← extracted)
                                              └── formatting.py (← formatter.py)
```

---

## Phase 1: Create Target Directories + Move Core Files

**PR 1.1: Create directory structure**
```bash
mkdir -p src/goobits_cli/{core,generation/renderers,features,validation,utils}
```

**PR 1.2: Move and rename core files**
```bash
git mv src/goobits_cli/schemas.py src/goobits_cli/core/config.py
git mv src/goobits_cli/config_manager.py src/goobits_cli/core/loader.py
git mv src/goobits_cli/logger.py src/goobits_cli/core/logging.py
git mv src/goobits_cli/formatter.py src/goobits_cli/utils/formatting.py
```

**PR 1.3: Update imports across codebase**
- Find all `from goobits_cli.schemas import` → `from goobits_cli.core.config import`
- Find all `from goobits_cli.config_manager import` → `from goobits_cli.core.loader import`
- Run tests to verify

**Gate**: All 534 tests still pass

---

## Phase 2: Extract Shared Utilities from Generators

**PR 2.1: Extract string utilities**

Create `src/goobits_cli/utils/strings.py` by MOVING (not rewriting) from generators:

```python
# utils/strings.py - Extracted from generators/nodejs.py:1381-1438, typescript.py:512-551

def to_camel_case(text: str) -> str:
    """Convert to camelCase. Moved from NodeJSGenerator._to_camelcase"""
    # COPY exact implementation from nodejs.py:1381-1403
    ...

def to_pascal_case(text: str) -> str:
    """Convert to PascalCase. Moved from TypeScriptGenerator._to_pascal_case"""
    # COPY exact implementation from typescript.py:526-538
    ...

def to_kebab_case(text: str) -> str:
    """Convert to kebab-case. Moved from NodeJSGenerator._to_kebabcase"""
    # COPY exact implementation from nodejs.py:1420-1438
    ...

def to_snake_case(text: str) -> str:
    """Convert to snake_case. Moved from RustGenerator._to_snake_case"""
    # COPY exact implementation from rust.py:661-670
    ...

def escape_javascript_string(value: str) -> str:
    """Escape for JS/TS. Moved from nodejs.py:158-187"""
    # COPY exact implementation
    ...

def escape_rust_string(text: str) -> str:
    """Escape for Rust. Moved from rust.py"""
    # COPY exact implementation
    ...

def json_stringify(obj) -> str:
    """JSON with Pydantic support. Moved from nodejs.py:141-156"""
    # COPY exact implementation
    ...
```

Then update generators to import from shared:
```python
# In generators/nodejs.py, replace methods with imports:
from goobits_cli.utils.strings import to_camel_case, to_kebab_case, escape_javascript_string
```

**PR 2.2: Extract path utilities**

Create `src/goobits_cli/utils/paths.py`:

```python
# utils/paths.py - Extracted from generators/*.py

def is_e2e_test_path(config_filename: str) -> bool:
    """Detect E2E test paths. Moved from python.py:125-135"""
    # COPY exact implementation from generators/python.py
    ...

def ensure_output_directory(path: Path) -> Path:
    """Create output directory. Moved from nodejs.py:428-436"""
    # COPY exact implementation
    ...
```

**PR 2.3: Extract config utilities**

Create `src/goobits_cli/utils/config.py`:

```python
# utils/config.py - Extracted from generators/*.py

def to_dict(obj) -> dict:
    """Convert Pydantic model to dict. Moved from nodejs.py:145-151"""
    if hasattr(obj, "model_dump"):
        return obj.model_dump()
    elif hasattr(obj, "dict"):
        return obj.dict()
    return obj

def convert_to_goobits_config(config, language: str) -> GoobitsConfigSchema:
    """Normalize config to GoobitsConfigSchema. Moved from python.py:188-220"""
    # COPY exact implementation
    ...
```

**Gate**: All 534 tests still pass after each PR

---

## Phase 3: Move Generators to New Location

**PR 3.1: Move generator files**
```bash
git mv src/goobits_cli/generators/python.py src/goobits_cli/generation/renderers/python.py
git mv src/goobits_cli/generators/nodejs.py src/goobits_cli/generation/renderers/nodejs.py
git mv src/goobits_cli/generators/typescript.py src/goobits_cli/generation/renderers/typescript.py
git mv src/goobits_cli/generators/rust.py src/goobits_cli/generation/renderers/rust.py
```

**PR 3.2: Create base renderer with shared code**

Extract common patterns into `src/goobits_cli/generation/renderers/base.py`:

```python
# base.py - Common renderer functionality

from abc import ABC, abstractmethod
from goobits_cli.utils.strings import to_camel_case, escape_javascript_string
from goobits_cli.utils.config import to_dict, convert_to_goobits_config

class LanguageRenderer(ABC):
    """Base class for language renderers. Extracted from template_engine.py:105-236"""

    @property
    @abstractmethod
    def language(self) -> str:
        pass

    def apply_integrations(self, config: GoobitsConfigSchema) -> GoobitsConfigSchema:
        """Apply interactive, completion, plugin integrations.

        Moved from generators/python.py:224-243 (identical in all 4 generators)
        """
        # COPY the integration logic that was duplicated 4 times
        ...

    def write_files(self, files: Dict[str, str], output_dir: Path) -> None:
        """Write generated files to disk.

        Moved from generators/nodejs.py:428-436 (identical in 3 generators)
        """
        # COPY the file writing logic
        ...
```

**PR 3.3: Update generator imports**
- Update all `from goobits_cli.generators.python import` → `from goobits_cli.generation.renderers.python import`
- Delete empty `generators/` directory

**Gate**: All 534 tests still pass

---

## Phase 4: Consolidate Template Engine (The Big One)

This is the largest file (1900 lines). We split it by MOVING methods, not rewriting.

**PR 4.1: Extract IR builder**

Create `src/goobits_cli/generation/ir.py` by moving methods from template_engine.py:

```python
# ir.py - Intermediate Representation builder
# Methods moved from UniversalTemplateEngine

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional

@dataclass
class CommandIR:
    """IR for a single command. Structure from template_engine.py"""
    name: str
    description: str
    arguments: List['ArgumentIR'] = field(default_factory=list)
    options: List['OptionIR'] = field(default_factory=list)
    subcommands: Dict[str, 'CommandIR'] = field(default_factory=dict)

@dataclass
class CLIIR:
    """Complete IR for CLI generation"""
    package_name: str
    command_name: str
    description: str
    language: str
    commands: Dict[str, CommandIR] = field(default_factory=dict)
    # ... other fields from template_engine.py

def build_ir(config: GoobitsConfigSchema) -> CLIIR:
    """Build IR from config.

    Moved from UniversalTemplateEngine._build_intermediate_representation (lines 715-880)
    """
    # MOVE the exact implementation from template_engine.py
    ...
```

**PR 4.2: Extract feature analyzer**

Create `src/goobits_cli/generation/analyzer.py`:

```python
# analyzer.py - Feature analysis
# Methods moved from UniversalTemplateEngine (lines 1708-2107)

def analyze_features(config: GoobitsConfigSchema, ir: CLIIR) -> Dict[str, bool]:
    """Analyze required features.

    Moved from UniversalTemplateEngine.analyze_feature_requirements
    """
    return {
        "rich_interface": _needs_rich_formatting(ir),
        "interactive_mode": _has_interactive_commands(ir),
        # ... all the feature checks, MOVED not rewritten
    }

# Move all the _needs_* and _has_* helper methods here
def _needs_rich_formatting(ir: CLIIR) -> bool:
    """Moved from template_engine.py:1833-1850"""
    ...
```

**PR 4.3: Extract template loader**

Create `src/goobits_cli/generation/templates/loader.py`:

```python
# loader.py - Template loading and caching
# Functionality moved from ComponentRegistry

from goobits_cli.universal.component_registry import ComponentRegistry  # Keep using it!

class TemplateLoader:
    """Simplified interface to ComponentRegistry.

    Wraps ComponentRegistry rather than replacing it - the registry logic is fine.
    """

    def __init__(self, components_dir: Path = None):
        # Reuse existing ComponentRegistry
        self._registry = ComponentRegistry(components_dir)

    def get_template(self, name: str) -> str:
        """Get template content by name."""
        return self._registry.get_component(name)

    def get_custom_filters(self) -> Dict[str, callable]:
        """Get Jinja filters."""
        return self._registry.get_custom_filters()
```

**PR 4.4: Slim down UniversalTemplateEngine**

After extracting IR, analyzer, and loader, the engine becomes a thin orchestrator:

```python
# template_engine.py - Now much smaller

from goobits_cli.generation.ir import build_ir, CLIIR
from goobits_cli.generation.analyzer import analyze_features
from goobits_cli.generation.templates.loader import TemplateLoader

class UniversalTemplateEngine:
    """Orchestrates CLI generation. Slimmed from 1900 to ~300 lines."""

    def __init__(self, ...):
        self.loader = TemplateLoader()
        # ... minimal init

    def generate(self, config: GoobitsConfigSchema) -> Dict[str, str]:
        """Main generation pipeline."""
        ir = build_ir(config)
        features = analyze_features(config, ir)
        renderer = self._get_renderer(config.language)
        return renderer.render(ir, features)
```

**Gate**: All 534 tests still pass

---

## Phase 5: Unify Validation Framework

**PR 5.1: Consolidate ValidationResult**

The `validation_framework.py` version is more complete. Keep it, delete the duplicate.

```python
# validation/framework.py - Keep existing, add compatibility

# Keep the existing ValidationResult from shared/components/validation_framework.py
# Add a simple adapter for test_utils usage:

class TestValidationResult(ValidationResult):
    """Compatibility layer for test utilities.

    Maps the test_utils.validation.ValidationResult interface to the main framework.
    """
    @property
    def passed(self) -> bool:
        return self.is_valid

    @property
    def errors(self) -> List[str]:
        return [m.message for m in self.get_errors()]
```

**PR 5.2: Update test_utils to use unified framework**
```python
# In shared/test_utils/validation.py, replace:
from goobits_cli.validation.framework import ValidationResult, TestValidationResult
# Delete the local ValidationResult class
```

**Gate**: All 534 tests still pass

---

## Phase 6: Consolidate Features (Interactive, Completion, Plugins)

**PR 6.1: Move and flatten interactive**
```bash
# Keep the core logic, flatten the structure
git mv src/goobits_cli/universal/interactive/interactive.py src/goobits_cli/features/interactive.py
# Merge other files into it or delete if unused
```

**PR 6.2: Move and flatten completion**
```bash
git mv src/goobits_cli/universal/completion/registry.py src/goobits_cli/features/completion.py
```

**PR 6.3: Move and flatten plugins**
```bash
git mv src/goobits_cli/universal/plugins/manager.py src/goobits_cli/features/plugins.py
```

**Gate**: All 534 tests still pass

---

## Phase 7: Split main.py (The 2100-Line Monster)

**PR 7.1: Extract CLI commands to separate module**

Create `src/goobits_cli/commands/` with one file per command:

```bash
# Create command modules by moving functions from main.py
mkdir -p src/goobits_cli/commands
```

```python
# commands/build.py - Move build() and helpers from main.py:632+
from goobits_cli.generation.engine import generate_cli

def build(config_path: str, ...):
    """Build command. Moved from main.py:632-780"""
    # MOVE exact implementation
    ...

# commands/init.py - Move init() from main.py
# commands/validate.py - Move validate() from main.py
# commands/upgrade.py - Move upgrade() from main.py
```

**PR 7.2: Slim main.py to entry point only**

```python
# main.py - Now just CLI definition and routing

import typer
from goobits_cli.commands import build, init, validate, upgrade

app = typer.Typer()

app.command()(build.build)
app.command()(init.init)
app.command()(validate.validate)
app.command()(upgrade.upgrade)

if __name__ == "__main__":
    app()
```

**Gate**: All 534 tests still pass

---

## Phase 8: Test Consolidation (Parallel with Above)

**PR 8.1: Add shared test fixtures to conftest.py**

```python
# tests/conftest.py - Add missing fixtures

GENERATORS = {
    "python": PythonRenderer,
    "nodejs": NodeJSRenderer,
    "typescript": TypeScriptRenderer,
    "rust": RustRenderer,
}

@pytest.fixture(params=list(GENERATORS.keys()))
def language(request):
    return request.param

@pytest.fixture
def renderer(language):
    return GENERATORS[language]()

@pytest.fixture
def sample_config(language):
    return create_test_config(language)
```

**PR 8.2: Parameterize generator tests**

```python
# tests/unit/generation/test_renderers.py - Unified tests

class TestRenderers:
    """Unified renderer tests using parameterization."""

    def test_initialization(self, renderer):
        """Replaces 4 separate initialization tests."""
        assert renderer is not None
        assert hasattr(renderer, "language")

    def test_basic_generation(self, renderer, sample_config, tmp_path):
        """Replaces 4 separate generation tests."""
        result = renderer.generate(sample_config, tmp_path)
        assert result is not None
```

**PR 8.3: Delete redundant test files**
```bash
# After parameterized tests work, delete the duplicates
rm tests/unit/generators/test_python_generator.py  # Covered by unified test
rm tests/unit/generators/test_nodejs_generator.py
rm tests/unit/generators/test_typescript_generator.py
rm tests/unit/generators/test_rust_generator.py
```

**Gate**: Test count may decrease, but coverage should remain same or increase

---

## Phase 9: Cleanup Empty Directories and Update Docs

**PR 9.1: Remove empty/deprecated directories**
```bash
rmdir src/goobits_cli/generators  # Now in generation/renderers/
rmdir src/goobits_cli/universal/interactive  # Now in features/
rmdir src/goobits_cli/universal/completion
rmdir src/goobits_cli/universal/plugins
# Keep universal/ only if still needed for templates
```

**PR 9.2: Update CLAUDE.md and README**
- Document new structure
- Update import examples
- Remove references to deleted paths

---

## Execution Order with Subagents

### Subagent 1: `structure-mover` (Phase 1-2)
```
Move core files to new locations and extract shared utilities.
Use git mv to preserve history. Update imports. Tests must pass after each step.
```

### Subagent 2: `generator-consolidator` (Phase 3)
```
Move generators to generation/renderers/. Create base.py with shared code.
Delete duplicated methods after extraction. Tests must pass.
```

### Subagent 3: `engine-splitter` (Phase 4)
```
Split UniversalTemplateEngine by moving methods to ir.py, analyzer.py, loader.py.
Keep engine as thin orchestrator. Do NOT rewrite - move code blocks exactly.
```

### Subagent 4: `validation-unifier` (Phase 5)
```
Keep validation_framework.py as source of truth.
Update test_utils to use it. Delete duplicate ValidationResult.
```

### Subagent 5: `main-splitter` (Phase 7)
```
Extract build(), init(), validate(), upgrade() to commands/ modules.
Keep exact implementations. Slim main.py to routing only.
```

### Subagent 6: `test-consolidator` (Phase 8)
```
Add parameterized fixtures to conftest.py.
Create unified test file. Delete redundant test files only after unified tests work.
```

---

## Safety Guarantees

1. **Git mv preserves history** - We can always trace where code came from
2. **Tests pass at every PR** - No "break then fix" phases
3. **Move before modify** - First relocate, then refactor (separate commits)
4. **Extract, don't rewrite** - Copy working code verbatim, then delete original
5. **One responsibility per PR** - Easy to review, easy to revert

---

## Expected Outcomes

| Metric | Before | After | How |
|--------|--------|-------|-----|
| main.py lines | 2100 | ~100 | Move to commands/ |
| template_engine.py lines | 1900 | ~300 | Extract ir.py, analyzer.py |
| Generator duplication | 4× same code | 1× in base.py | Extract shared methods |
| ValidationResult classes | 2 | 1 | Delete duplicate |
| Test files for generators | 4 separate | 1 unified | Parameterize |
| Directory depth | 4-5 levels | 2-3 levels | Flatten universal/ |

---

## File Movement Summary

| From | To | Action |
|------|-----|--------|
| `schemas.py` | `core/config.py` | git mv |
| `config_manager.py` | `core/loader.py` | git mv |
| `logger.py` | `core/logging.py` | git mv |
| `formatter.py` | `utils/formatting.py` | git mv |
| `generators/*.py` | `generation/renderers/*.py` | git mv |
| `universal/interactive/` | `features/interactive.py` | Merge + mv |
| `universal/completion/` | `features/completion.py` | Merge + mv |
| `universal/plugins/` | `features/plugins.py` | Merge + mv |
| Methods from template_engine.py | `generation/ir.py` | Extract (copy then delete) |
| Methods from template_engine.py | `generation/analyzer.py` | Extract |
| Functions from main.py | `commands/*.py` | Extract |
| Duplicate utils from generators | `utils/strings.py` | Extract |

---

## Ready to Execute?

This approach:
- **Preserves** all fine-tuned logic
- **Moves** rather than rewrites
- **Extracts** duplicates to shared locations
- **Keeps tests passing** at every step
- **Uses git mv** for history preservation

Subagents work in parallel where possible (e.g., test-consolidator can run alongside engine-splitter) with gates ensuring tests pass before proceeding.
