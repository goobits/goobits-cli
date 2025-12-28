# Goobits CLI Universal-First Refactor Plan

**Status**: Draft (breaking changes allowed, staged removal of legacy)
**Owner**: Team Goobits CLI
**Audience**: Engineering
**Version**: 2.0 (revised for DRY/SOLID compliance)

---

## Goals

- [ ] Make the Universal Template System the single generation path
- [ ] Improve maintainability by splitting the universal core into focused modules
- [ ] Maintain performance targets (<100ms startup, <1s generation)
- [ ] Add reliable, functional tests before removing legacy generators
- [ ] Ensure DRY/SOLID compliance throughout

## Non-Goals

- Backward compatibility guarantees
- Preserving current class/module layout
- Keeping legacy generators once parity is achieved

## Guiding Principles

- One pipeline: `config → IR → renderer → artifacts`
- Small, testable modules with explicit contracts
- Single Responsibility: each file does one thing
- Dependency Inversion: depend on abstractions, not concrete classes
- No mixed architectures once parity is proven

---

## Target Architecture

```
src/goobits_cli/
├── universal/
│   ├── engine/
│   │   ├── __init__.py
│   │   ├── orchestrator.py      # Entry point: coordinates stages
│   │   └── stages.py            # Pure functions: config→IR, IR→artifacts
│   ├── ir/
│   │   ├── __init__.py
│   │   ├── models.py            # IR dataclasses (frozen, validated)
│   │   ├── builder.py           # ConfigSchema → IR transformation
│   │   └── analyzers.py         # Feature detection plugins
│   ├── renderers/
│   │   ├── __init__.py
│   │   ├── interface.py         # LanguageRenderer ABC (thin)
│   │   ├── registry.py          # Language→Renderer factory
│   │   ├── helpers.py           # Shared utilities (escape, format)
│   │   ├── python.py
│   │   ├── nodejs.py
│   │   ├── typescript.py
│   │   └── rust.py
│   ├── templates/
│   │   ├── __init__.py
│   │   └── loader.py            # Jinja2 loading + cache
│   └── integrations/
│       ├── __init__.py
│       ├── completion.py        # Shell completion
│       ├── interactive.py       # REPL mode
│       └── plugins.py           # Plugin loading
├── core/
│   ├── __init__.py
│   ├── config.py                # Config loading/normalization
│   ├── schemas.py               # Pydantic models
│   ├── errors.py                # Unified exceptions
│   └── logging.py               # Logging setup
├── validation/
│   └── framework.py             # ValidationResult + validators
└── commands/
    └── build.py                 # Uses orchestrator via registry
```

---

## Phase 0: Alignment and Guardrails

**Priority**: Critical
**Duration**: 1-2 days
**Blocking**: Must complete before Phase 1

### Documentation Deliverables

- [ ] Create `docs/IR_SCHEMA.md`
  - [ ] Define all IR dataclasses (Command, Option, Argument, Subcommand)
  - [ ] Specify frozen fields and validation rules
  - [ ] Mark as FROZEN before Phase 1

- [ ] Create `docs/RENDERER_CONTRACT.md`
  - [ ] Define `LanguageRenderer` interface
  - [ ] Specify input: `IR` object
  - [ ] Specify output: `List[Artifact]` with (path, content, metadata)
  - [ ] Mark as FROZEN before Phase 1

- [ ] Create `docs/HOOK_CONTRACT.md`
  - [ ] Define hook naming: `on_{command_name}`
  - [ ] Define parameter passing: `(command_name: str, **kwargs)`
  - [ ] Define return expectations: `None` or result dict
  - [ ] Mark as FROZEN before Phase 1

### Parity Audit

- [ ] Create `docs/PARITY_AUDIT.md`
  - [ ] Compare `generation/renderers/python.py` vs `universal/renderers/python_renderer.py`
  - [ ] Compare `generation/renderers/nodejs.py` vs `universal/renderers/nodejs_renderer.py`
  - [ ] Compare `generation/renderers/typescript.py` vs `universal/renderers/typescript_renderer.py`
  - [ ] Compare `generation/renderers/rust.py` vs `universal/renderers/rust_renderer.py`
  - [ ] Document all gaps to port in Phase 3

### Performance Baseline

- [ ] Create `performance/baseline.py`
  - [ ] Measure current generation time per language
  - [ ] Measure current CLI startup time per language
  - [ ] Measure current memory usage
  - [ ] Store as baseline for regression detection

### Downstream Pre-work

- [ ] Fix stale hook path in matilda-voice
  - [ ] Edit `goobits.yaml`: `hooks_path: src/tts/app_hooks.py` → `src/matilda_voice/app_hooks.py`
  - [ ] Run `goobits build` to regenerate

- [ ] Fix stale hook path in matilda-brain
  - [ ] Edit `goobits.yaml`: `hooks_path: src/ttt/app_hooks.py` → `src/matilda_brain/app_hooks.py`
  - [ ] Run `goobits build` to regenerate

### Phase 0 Gate

```
[ ] docs/IR_SCHEMA.md exists and marked FROZEN
[ ] docs/RENDERER_CONTRACT.md exists and marked FROZEN
[ ] docs/HOOK_CONTRACT.md exists and marked FROZEN
[ ] docs/PARITY_AUDIT.md completed with gap list
[ ] performance/baseline.py runs successfully
[ ] Downstream hook paths fixed
```

---

## Phase 1: Modularize Universal Core

**Priority**: Critical
**Duration**: 3-5 days
**Blocking**: Must complete before Phase 2

### Create Engine Module

- [ ] Create `universal/engine/orchestrator.py`
  - [ ] Extract entry point logic from `template_engine.py`
  - [ ] Single responsibility: coordinate stages, handle errors
  - [ ] Depend on abstractions only (use registry)

- [ ] Create `universal/engine/stages.py`
  - [ ] Pure function: `parse_config(yaml_path) -> ConfigSchema`
  - [ ] Pure function: `build_ir(config) -> IR`
  - [ ] Pure function: `render(ir, language) -> List[Artifact]`
  - [ ] Pure function: `write_artifacts(artifacts) -> None`

- [ ] Update `universal/engine/__init__.py`
  - [ ] Export: `Orchestrator`, `parse_config`, `build_ir`, `render`

### Create IR Module

- [ ] Create `universal/ir/models.py`
  - [ ] Dataclass: `IRCommand(name, description, options, arguments, subcommands)`
  - [ ] Dataclass: `IROption(name, type, default, required, help)`
  - [ ] Dataclass: `IRArgument(name, type, nargs, help)`
  - [ ] Dataclass: `IR(commands, metadata, features)`
  - [ ] All classes frozen (`@dataclass(frozen=True)`)

- [ ] Rename `universal/ir/feature_analyzer.py` → `universal/ir/analyzers.py`
  - [ ] Update all imports

- [ ] Update `universal/ir/__init__.py`
  - [ ] Export: `IR`, `IRCommand`, `IROption`, `IRArgument`, `IRBuilder`, `FeatureAnalyzer`

### Refactor Renderers (DRY/SOLID)

- [ ] Create `universal/renderers/interface.py`
  - [ ] Move `LanguageRenderer` ABC from `engine/base.py`
  - [ ] Keep interface thin: `render(ir) -> List[Artifact]` only
  - [ ] Add `language` property

- [ ] Create `universal/renderers/helpers.py`
  - [ ] Extract common utilities from renderers
  - [ ] Function: `escape_string(s, language) -> str`
  - [ ] Function: `format_code(code, language) -> str`
  - [ ] Function: `indent(text, level) -> str`

- [ ] Create `universal/renderers/registry.py`
  ```python
  RENDERER_REGISTRY = {
      "python": "universal.renderers.python:PythonRenderer",
      "nodejs": "universal.renderers.nodejs:NodeJSRenderer",
      "typescript": "universal.renderers.typescript:TypeScriptRenderer",
      "rust": "universal.renderers.rust:RustRenderer",
  }

  def get_renderer(language: str) -> LanguageRenderer: ...
  ```

- [ ] Rename renderer files (remove `_renderer` suffix for consistency)
  - [ ] `python_renderer.py` → `python.py`
  - [ ] `nodejs_renderer.py` → `nodejs.py`
  - [ ] `typescript_renderer.py` → `typescript.py`
  - [ ] `rust_renderer.py` → `rust.py`

- [ ] Update all renderers to use `helpers.py`

- [ ] Delete `universal/engine/base.py` (moved to `renderers/interface.py`)

### Create Templates Module

- [ ] Create `universal/templates/__init__.py`

- [ ] Create `universal/templates/loader.py`
  - [ ] Extract template loading from `template_engine.py`
  - [ ] Implement Jinja2 environment caching
  - [ ] Function: `load_template(name) -> Template`
  - [ ] Function: `get_template_dir(language) -> Path`

### Create Integrations Module

- [ ] Create `universal/integrations/__init__.py`

- [ ] Create `universal/integrations/completion.py`
  - [ ] Move core logic from `universal/completion/integration.py`

- [ ] Create `universal/integrations/interactive.py`
  - [ ] Move core logic from `universal/interactive/interactive.py`

- [ ] Create `universal/integrations/plugins.py`
  - [ ] Move core logic from `universal/plugins/integration.py`

- [ ] Delete old directories (same commit to avoid duplication)
  - [ ] Delete `universal/completion/` (after moving)
  - [ ] Delete `universal/interactive/` (after moving)
  - [ ] Delete `universal/plugins/integration.py` (keep manager, marketplace)

### Create Core Errors

- [ ] Create `core/errors.py`
  - [ ] Move from `generation/__init__.py`:
    - [ ] `GeneratorError`
    - [ ] `ConfigurationError`
    - [ ] `TemplateError`
    - [ ] `ValidationError`
    - [ ] `RenderError`

- [ ] Update `core/__init__.py`
  - [ ] Export all error classes

### Reduce template_engine.py

- [ ] Refactor `universal/template_engine.py`
  - [ ] Remove code moved to `engine/`, `ir/`, `templates/`
  - [ ] Keep only as thin wrapper for backward compatibility (if needed)
  - [ ] Target: <200 lines or delete entirely

### Phase 1 Gate

```
[ ] universal/engine/orchestrator.py exists and functional
[ ] universal/engine/stages.py exists with pure functions
[ ] universal/ir/models.py defines all IR types
[ ] universal/renderers/interface.py contains thin ABC
[ ] universal/renderers/registry.py implements factory pattern
[ ] universal/renderers/helpers.py contains shared utilities
[ ] universal/templates/loader.py handles template caching
[ ] universal/integrations/ contains completion, interactive, plugins
[ ] core/errors.py contains all exceptions
[ ] Old completion/, interactive/ directories deleted
[ ] template_engine.py reduced or deleted
[ ] All existing tests still pass
```

---

## Phase 2: Battle-Hardened Tests

**Priority**: High
**Duration**: 3-4 days
**Blocking**: Must complete before Phase 4

### Acceptance Tests

- [ ] Create `tests/acceptance/__init__.py`

- [ ] Create `tests/acceptance/conftest.py`
  - [ ] Fixture: `temp_project_dir`
  - [ ] Fixture: `sample_goobits_yaml`
  - [ ] Helper: `run_generated_cli(command)`

- [ ] Create `tests/acceptance/test_python_generation.py`
  - [ ] Test: generate CLI from sample config
  - [ ] Test: run `--help` command
  - [ ] Test: run `--version` command
  - [ ] Test: compare output against golden file
  - [ ] Test: hook invocation works

- [ ] Create `tests/acceptance/test_nodejs_generation.py`
  - [ ] Same tests as Python

- [ ] Create `tests/acceptance/test_typescript_generation.py`
  - [ ] Same tests as Python

- [ ] Create `tests/acceptance/test_rust_generation.py`
  - [ ] Same tests as Python
  - [ ] Test: `cargo build` succeeds

- [ ] Create `tests/acceptance/golden/`
  - [ ] `python_cli.py.golden`
  - [ ] `nodejs_cli.mjs.golden`
  - [ ] `typescript_cli.ts.golden`
  - [ ] `rust_main.rs.golden`

### Performance Tests

- [ ] Create `tests/performance/__init__.py`

- [ ] Create `tests/performance/test_generation_time.py`
  - [ ] Test: Python generation ≤1s
  - [ ] Test: Node.js generation ≤1s
  - [ ] Test: TypeScript generation ≤1s
  - [ ] Test: Rust generation ≤1s

- [ ] Create `tests/performance/test_startup_time.py`
  - [ ] Test: Python CLI startup ≤100ms
  - [ ] Test: Node.js CLI startup ≤100ms
  - [ ] Test: TypeScript CLI startup ≤100ms
  - [ ] Test: Rust CLI startup ≤100ms

- [ ] Create `tests/performance/test_memory.py`
  - [ ] Test: Generation memory ≤5MB

### IR Tests

- [ ] Create `tests/ir/__init__.py`

- [ ] Create `tests/ir/test_ir_models.py`
  - [ ] Test: IR dataclasses are frozen
  - [ ] Test: IR validation rejects invalid data

- [ ] Create `tests/ir/test_ir_builder.py`
  - [ ] Test: minimal config → valid IR
  - [ ] Test: complex nested commands → valid IR
  - [ ] Test: plugin features → valid IR

### Downstream Validation Tests

- [ ] Create `tests/downstream/__init__.py`

- [ ] Create `tests/downstream/test_matilda.py`
  - [ ] Test: `/workspace/matilda/goobits.yaml` generates successfully
  - [ ] Test: Generated CLI imports correctly

- [ ] Create `tests/downstream/test_ears.py`
  - [ ] Test: `/workspace/matilda-ears/goobits.yaml` generates successfully

- [ ] Create `tests/downstream/test_voice.py`
  - [ ] Test: `/workspace/matilda-voice/goobits.yaml` generates successfully

- [ ] Create `tests/downstream/test_brain.py`
  - [ ] Test: `/workspace/matilda-brain/goobits.yaml` generates successfully

### Test Configuration

- [ ] Update `pytest.ini`
  - [ ] Add marker: `acceptance`
  - [ ] Add marker: `performance`
  - [ ] Add marker: `ir`
  - [ ] Add marker: `downstream`

### Phase 2 Gate

```
[ ] tests/acceptance/test_python_generation.py passes
[ ] tests/acceptance/test_nodejs_generation.py passes
[ ] tests/acceptance/test_typescript_generation.py passes
[ ] tests/acceptance/test_rust_generation.py passes
[ ] tests/performance/* all pass
[ ] tests/ir/* all pass
[ ] tests/downstream/* all pass
```

---

## Phase 3: Universal Parity and Stabilization

**Priority**: High
**Duration**: 2-4 days
**Blocking**: Must complete before Phase 4

### Port Missing Features (from PARITY_AUDIT.md)

- [ ] Review `docs/PARITY_AUDIT.md` gap list

- [ ] Update `universal/renderers/python.py`
  - [ ] Port each gap identified for Python
  - [ ] Verify with acceptance test

- [ ] Update `universal/renderers/nodejs.py`
  - [ ] Port each gap identified for Node.js
  - [ ] Verify with acceptance test

- [ ] Update `universal/renderers/typescript.py`
  - [ ] Port each gap identified for TypeScript
  - [ ] Verify with acceptance test

- [ ] Update `universal/renderers/rust.py`
  - [ ] Port each gap identified for Rust
  - [ ] Verify with acceptance test

- [ ] Update `universal/ir/builder.py`
  - [ ] Add any missing IR transformations

### Verify Setup Script Generation

- [ ] Confirm setup.sh templates work via universal path
- [ ] Test installation with generated setup.sh

### Verify Integrations

- [ ] Test completion integration
- [ ] Test interactive mode
- [ ] Test plugin loading

### Full Downstream Validation

- [ ] Validate matilda
  ```bash
  cd /workspace/matilda
  goobits build
  ./setup.sh install --dev
  ./test.py
  ```

- [ ] Validate matilda-ears
  ```bash
  cd /workspace/matilda-ears
  goobits build
  ./setup.sh install --dev
  ./test.py
  ```

- [ ] Validate matilda-voice
  ```bash
  cd /workspace/matilda-voice
  goobits build
  ./setup.sh install --dev
  ./test.sh
  ```

- [ ] Validate matilda-brain
  ```bash
  cd /workspace/matilda-brain
  goobits build
  ./setup.sh install --dev
  ./run-tests.sh unit
  ```

### Phase 3 Gate

```
[ ] All gaps from PARITY_AUDIT.md resolved
[ ] All acceptance tests pass
[ ] All performance tests pass
[ ] matilda: goobits build + tests pass
[ ] matilda-ears: goobits build + tests pass
[ ] matilda-voice: goobits build + tests pass
[ ] matilda-brain: goobits build + tests pass
```

---

## Phase 4: Remove Legacy Generators

**Priority**: High
**Duration**: 1 day
**Risk**: High (point of no return)

### Pre-Flight Check

- [ ] Verify all Phase 2 gates pass
- [ ] Verify all Phase 3 gates pass
- [ ] Create backup branch: `git checkout -b backup/pre-legacy-removal`

### Update Build Command

- [ ] Edit `commands/build.py`
  - [ ] Remove all imports from `goobits_cli.generation.*`
  - [ ] Import: `from universal.renderers.registry import get_renderer`
  - [ ] Replace generator instantiation with registry lookup
  - [ ] Update method calls if signatures differ

### Delete Legacy Files

- [ ] Delete `generation/renderers/python.py` (20.5K)
- [ ] Delete `generation/renderers/nodejs.py` (34.8K)
- [ ] Delete `generation/renderers/typescript.py` (53.7K)
- [ ] Delete `generation/renderers/rust.py` (50.9K)
- [ ] Delete `generation/renderers/__init__.py`
- [ ] Delete `generation/builder.py` (6.7K)
- [ ] Delete `generation/__init__.py` (11.9K) - after moving exceptions
- [ ] Delete `generation/` directory

### Update Package Exports

- [ ] Edit `__init__.py`
  - [ ] Remove `generation` exports
  - [ ] Add `universal.engine` exports

- [ ] Edit `main.py`
  - [ ] Remove any `generation` references

### Verify

- [ ] Run full test suite: `pytest`
- [ ] Run acceptance tests: `pytest -m acceptance`
- [ ] Run performance tests: `pytest -m performance`
- [ ] Run downstream tests: `pytest -m downstream`

### Phase 4 Gate

```
[ ] generation/ directory deleted
[ ] commands/build.py uses universal.renderers.registry
[ ] All tests pass
[ ] No imports from goobits_cli.generation anywhere
```

---

## Phase 5: Cleanup and Documentation

**Priority**: Medium
**Duration**: 2-3 days

### Dead Code Removal

- [ ] Run `make dead-code` to detect unused code
- [ ] Delete unused utilities in `universal/`
- [ ] Delete unused templates
- [ ] Delete `universal/utils.py` if consolidated elsewhere

### Remove Deprecated Files

- [ ] Delete `universal/template_engine.py` (if not needed)
- [ ] Delete any remaining old integration files
- [ ] Clean up `shared/` directory

### Documentation Updates

- [ ] Create `docs/ARCHITECTURE.md`
  - [ ] Diagram: config → IR → renderer → artifacts
  - [ ] Module responsibilities
  - [ ] Extension points

- [ ] Create `docs/ADDING_LANGUAGE.md`
  - [ ] Step 1: Create renderer class
  - [ ] Step 2: Add to registry
  - [ ] Step 3: Create templates
  - [ ] Step 4: Add tests

- [ ] Create `docs/MIGRATION_V4.md`
  - [ ] Breaking changes
  - [ ] Upgrade steps
  - [ ] Troubleshooting

- [ ] Update `README.md`
  - [ ] New architecture overview
  - [ ] Updated examples

- [ ] Update `CLAUDE.md`
  - [ ] New code generation flow
  - [ ] New file structure

- [ ] Update `CODEMAP.md`
  - [ ] Reflect new directory structure

### Phase 5 Gate

```
[ ] make dead-code reports no issues
[ ] docs/ARCHITECTURE.md exists
[ ] docs/ADDING_LANGUAGE.md exists
[ ] docs/MIGRATION_V4.md exists
[ ] README.md updated
[ ] CLAUDE.md updated
```

---

## Performance Requirements

| Metric | Target | Test |
|--------|--------|------|
| Generation time | ≤1s per language | `tests/performance/test_generation_time.py` |
| CLI startup | ≤100ms cold | `tests/performance/test_startup_time.py` |
| Memory usage | ≤5MB | `tests/performance/test_memory.py` |

Performance tests fail the build on regression.

---

## Go/No-Go Criteria

### Go Requirements

- [ ] Universal pipeline passes acceptance tests for all 4 languages
- [ ] Performance budgets met (≤1s generation, ≤100ms startup, ≤5MB memory)
- [ ] IR schema doc exists and frozen
- [ ] Renderer interface doc exists and frozen
- [ ] Hook contract doc exists and frozen
- [ ] Feature parity audit completed and all gaps addressed
- [ ] All 4 downstream projects pass tests after `goobits build`
- [ ] No legacy generators remain in any code path

### No-Go Conditions

- Any acceptance test failing
- Any performance regression >20%
- Downstream project tests failing
- Undocumented breaking changes in hook contract

---

## Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Universal core becomes god-object | Medium | High | Enforce module boundaries, keep orchestrator thin |
| Regressions during parity phase | Medium | High | Acceptance + golden tests before deleting legacy |
| Performance regressions | Low | Medium | Baseline tests, targeted profiling |
| Downstream projects break | Medium | High | Test all 4 projects in Phase 3 gate |
| Hook contract changes break users | Low | Critical | Freeze contract in Phase 0, document in HOOK_CONTRACT.md |

---

## File Summary by Phase

| Phase | Create | Edit | Delete | Move/Rename |
|-------|--------|------|--------|-------------|
| 0 | 5 docs, 1 script | 2 downstream configs | 0 | 0 |
| 1 | 12 modules | 6 | 4 dirs | 5 |
| 2 | 20+ tests | 1 | 0 | 0 |
| 3 | 0-2 | 4-6 | 0 | 0 |
| 4 | 0 | 3 | 8 files, 1 dir | 0 |
| 5 | 3 docs | 3 | 2-5 | 0 |
| **Total** | ~43 | ~21 | ~18 | 5 |

---

## Deliverables

- [ ] Universal pipeline as the single source of truth
- [ ] Fully modularized universal core (DRY/SOLID compliant)
- [ ] Registry-based renderer loading (Dependency Inversion)
- [ ] Separated interface/helpers in renderers (Single Responsibility)
- [ ] Acceptance + performance tests guarding behavior and speed
- [ ] Clean removal of legacy generators
- [ ] Updated documentation for new architecture
