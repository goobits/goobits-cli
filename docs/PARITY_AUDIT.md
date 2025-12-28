# Parity Audit: Legacy vs Universal Renderers

**Status**: Complete
**Version**: 1.0.0
**Created**: Phase 0 of Universal-First Refactor

---

## Executive Summary

**Finding**: The legacy generators (`generation/renderers/`) are **thin wrappers** around the universal system (`universal/`). They already delegate core rendering to `UniversalTemplateEngine` and `*Renderer` classes.

**Risk Level**: LOW - Minimal feature gaps exist.

**Recommendation**: Proceed with refactor. Focus Phase 3 on edge case handling, not feature porting.

---

## Architecture Discovery

### Current Flow (Legacy Path)

```
build.py
  → generation/renderers/python.py (PythonGenerator)
    → universal/template_engine.py (UniversalTemplateEngine)
      → universal/ir/builder.py (IRBuilder)
      → universal/renderers/python_renderer.py (PythonRenderer)
        → Generated CLI code
```

### Key Insight

The legacy `PythonGenerator` (493 lines) imports and uses:
- `UniversalTemplateEngine`
- `PythonRenderer`
- `integrate_completion_system`
- `integrate_interactive_mode`
- `integrate_plugin_system`

**The legacy generator is an adapter, not an independent implementation.**

---

## Line Count Comparison

| Language | Legacy (generation/) | Universal (universal/) | Notes |
|----------|---------------------|------------------------|-------|
| Python | 493 | 1,019 | Universal is 2x larger |
| Node.js | 1,205 | 1,045 | Legacy has more wrapper code |
| TypeScript | 1,796 | 1,072 | Legacy has more wrapper code |
| Rust | 1,644 | 756 | Legacy has more wrapper code |
| **Total** | **5,138** | **3,892** | |

### Analysis

The legacy renderers are larger because they contain:
1. **E2E test compatibility code** (path detection, file writing)
2. **Config conversion logic** (ConfigSchema → GoobitsConfigSchema)
3. **Integration wrappers** (completion, interactive, plugins)
4. **Backward compatibility shims** (template_env attribute)

The universal renderers are smaller because they are **pure renderers** - they only transform IR to code.

---

## Feature Comparison by Language

### Python

| Feature | Legacy | Universal | Gap? |
|---------|--------|-----------|------|
| Click CLI generation | Delegates to Universal | ✓ | No |
| Rich-click styling | Delegates to Universal | ✓ | No |
| Hook system | Delegates to Universal | ✓ | No |
| Consolidation mode | ✓ (wrapper) | ✓ | No |
| E2E test path detection | ✓ | ✗ | **Move to orchestrator** |
| ConfigSchema conversion | ✓ | ✗ | **Move to orchestrator** |
| Interactive mode integration | ✓ (imports universal) | ✓ | No |
| Completion integration | ✓ (imports universal) | ✓ | No |
| Plugin integration | ✓ (imports universal) | ✓ | No |

### Node.js

| Feature | Legacy | Universal | Gap? |
|---------|--------|-----------|------|
| Commander.js generation | Delegates to Universal | ✓ | No |
| ES6 module output | Delegates to Universal | ✓ | No |
| Hook system | Delegates to Universal | ✓ | No |
| package.json handling | ✓ | ✓ | No |
| E2E test path detection | ✓ | ✗ | **Move to orchestrator** |

### TypeScript

| Feature | Legacy | Universal | Gap? |
|---------|--------|-----------|------|
| TypeScript generation | Delegates to Universal | ✓ | No |
| Type definitions | Delegates to Universal | ✓ | No |
| Hook system | Delegates to Universal | ✓ | No |
| tsconfig.json handling | ✓ | ✓ | No |
| E2E test path detection | ✓ | ✗ | **Move to orchestrator** |

### Rust

| Feature | Legacy | Universal | Gap? |
|---------|--------|-----------|------|
| Clap CLI generation | Delegates to Universal | ✓ | No |
| Cargo.toml handling | Delegates to Universal | ✓ | No |
| Hook system | Delegates to Universal | ✓ | No |
| E2E test path detection | ✓ | ✗ | **Move to orchestrator** |

---

## Identified Gaps (Phase 3 Work Items)

### Gap 1: E2E Test Path Detection

**Location**: `generation/renderers/python.py:131`

```python
if is_e2e_test_path(config_filename):
    # For E2E tests, use the simpler legacy approach
    cli_content = self._generate_cli(config, "test.yaml", version)
```

**Action**: Move `is_e2e_test_path()` check to orchestrator before calling renderer.

**Effort**: Low (move existing function)

---

### Gap 2: ConfigSchema Conversion

**Location**: `generation/renderers/python.py:183-200`

```python
if isinstance(config, ConfigSchema):
    goobits_config = GoobitsConfigSchema(
        package_name=getattr(config, "package_name", config.cli.name),
        # ... conversion logic
    )
```

**Action**: Move config normalization to orchestrator's `stages.py`.

**Effort**: Low (move existing logic)

---

### Gap 3: Integration Function Calls

**Location**: `generation/renderers/python.py:51-55`

```python
from ...universal.completion import integrate_completion_system
from ...universal.interactive import integrate_interactive_mode
from ...universal.plugins import integrate_plugin_system
```

**Action**: These are already in `universal/`. Ensure orchestrator calls them as needed.

**Effort**: Low (already implemented, just wire up)

---

### Gap 4: Backward Compatibility Attributes

**Location**: `generation/renderers/python.py:107`

```python
# Initialize template environment for backward compatibility with tests
self.template_env = Environment(loader=DictLoader({}))
```

**Action**: Determine if any tests rely on `generator.template_env`. If yes, add to universal renderer or mock in tests.

**Effort**: Low (likely removable, verify with tests)

---

## Non-Gaps (No Action Required)

### 1. Template Rendering

Both systems use Jinja2. Universal renderers have all necessary templates.

### 2. Hook Generation

Both systems generate identical hook invocation patterns. No divergence.

### 3. CLI Framework Integration

- Python: Both use Click via universal renderer
- Node.js: Both use Commander.js via universal renderer
- TypeScript: Both use Commander.js via universal renderer
- Rust: Both use Clap via universal renderer

### 4. File Output Structure

Universal renderers produce same file structure as legacy.

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| E2E tests fail after refactor | Medium | Medium | Add E2E tests in Phase 2 |
| ConfigSchema users break | Low | Low | Keep conversion in orchestrator |
| Integration features missing | Low | Low | Already use universal modules |
| Tests expect template_env | Low | Low | Check tests, remove or mock |

---

## Phase 3 Task List

Based on this audit, Phase 3 requires:

- [ ] Move `is_e2e_test_path()` check to orchestrator
- [ ] Move ConfigSchema → GoobitsConfigSchema conversion to stages.py
- [ ] Wire up integration calls (completion, interactive, plugins) in orchestrator
- [ ] Verify no tests depend on `generator.template_env`
- [ ] Run all E2E tests against universal-only path

**Estimated Effort**: 1-2 days (moved from 2-4 day estimate, most work already done)

---

## Known Issue: Circular Import

A circular import exists between `generation/` and `universal/` modules:

```
ir/builder.py
  → imports _safe_to_dict from generation/
    → generation/__init__.py imports renderers
      → renderers/nodejs.py imports from universal/renderers
        → universal/renderers imports from template_engine
          → template_engine imports from ir/builder
            → CIRCULAR!
```

**Impact**: `goobits build` fails with ImportError.

**Resolution**: Phase 1 will fix this by:
1. Moving `_safe_to_dict` to `core/utils.py` (breaking the cycle)
2. Removing cross-dependencies between `generation/` and `universal/`

**Downstream Note**: matilda-voice and matilda-brain have stale hook paths in their generated `cli.py` files (referencing `src/tts/` and `src/ttt/`). The goobits.yaml files have correct paths. Regeneration will fix this after Phase 1.

---

## Conclusion

The parity audit reveals that **the universal system is already feature-complete**. The legacy generators are thin adapters that:

1. Handle edge cases (E2E test paths, config conversion)
2. Wire up integrations (completion, interactive, plugins)
3. Provide backward compatibility shims

**All core rendering logic is already in the universal path.**

Phase 3 work is primarily about moving orchestration logic from the legacy generators into the new orchestrator, not about porting rendering features.
