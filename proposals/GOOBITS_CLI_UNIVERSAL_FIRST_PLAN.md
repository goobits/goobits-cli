# Goobits CLI Universal-First Refactor Plan

**Status**: ✅ COMPLETED
**Owner**: Team Goobits CLI
**Completed**: December 2024

---

## Summary

This refactor successfully migrated goobits-cli to a Universal Template System architecture,
eliminating legacy generators and establishing a clean, maintainable codebase.

## Completed Work

### Phase 0: Alignment and Guardrails ✅
- [x] Created `docs/IR_SCHEMA.md` - Frozen IR dataclass specifications
- [x] Created `docs/RENDERER_CONTRACT.md` - LanguageRenderer interface contract
- [x] Created `docs/HOOK_CONTRACT.md` - Hook naming and parameter conventions
- [x] Created `docs/PARITY_AUDIT.md` - Gap analysis between old/new generators
- [x] Fixed downstream hook paths (matilda-voice, matilda-brain)

### Phase 1: Modularize Universal Core ✅
- [x] Created `universal/engine/orchestrator.py` - Central pipeline coordinator
- [x] Created `universal/engine/stages.py` - Pure pipeline functions
- [x] Created `universal/ir/models.py` - Frozen IR dataclasses
- [x] Created `universal/renderers/interface.py` - LanguageRenderer ABC
- [x] Created `universal/renderers/registry.py` - Dynamic renderer factory
- [x] Created `universal/integrations/` - Moved completion, interactive, plugins
- [x] Created `core/errors.py` - Consolidated exception classes
- [x] Deleted `universal/template_engine.py` - Superseded by Orchestrator

### Phase 2: Battle-Hardened Tests ✅
- [x] Created `tests/acceptance/` - Generation acceptance tests
- [x] Created `tests/performance/` - Performance regression tests
- [x] Created `tests/ir/` - IR model and builder tests
- [x] Created `tests/downstream/` - Downstream project validation
- [x] All tests passing (500+ tests)

### Phase 3: Universal Parity and Stabilization ✅
- [x] All language renderers at feature parity
- [x] Setup script generation working
- [x] Downstream projects validated (matilda, ears, voice, brain)

### Phase 4: Remove Legacy Generators ✅
- [x] Deleted `generation/` directory entirely
- [x] Updated `commands/build.py` to use Orchestrator
- [x] Removed all backward-compat generator classes
- [x] All imports now from `universal/` only

### Phase 5: Cleanup and Documentation ✅
- [x] Updated `CLAUDE.md` with new architecture
- [x] Dead code removed
- [x] Backward-compat stubs removed (engine/base.py, template_engine.py)
- [x] Test imports cleaned up (UniversalGenerator only)

---

## Final Architecture

```
src/goobits_cli/
├── universal/
│   ├── engine/
│   │   ├── orchestrator.py    # Entry point: coordinates pipeline
│   │   └── stages.py          # Pure functions: config→IR→artifacts
│   ├── ir/
│   │   ├── models.py          # Frozen IR dataclasses
│   │   ├── builder.py         # ConfigSchema → IR transformation
│   │   └── feature_analyzer.py # Feature detection
│   ├── renderers/
│   │   ├── interface.py       # LanguageRenderer ABC
│   │   ├── registry.py        # Language→Renderer factory
│   │   ├── python_renderer.py
│   │   ├── nodejs_renderer.py
│   │   ├── typescript_renderer.py
│   │   └── rust_renderer.py
│   ├── integrations/
│   │   ├── completion/        # Shell completion
│   │   ├── interactive/       # REPL mode
│   │   └── plugins/           # Plugin system
│   └── generator.py           # UniversalGenerator wrapper
├── core/
│   ├── config.py              # Config loading
│   ├── schemas.py             # Pydantic models
│   ├── errors.py              # All exceptions
│   └── logging.py             # Logging setup
└── commands/
    └── build.py               # Uses Orchestrator
```

---

## API Summary

```python
# Primary API
from goobits_cli.universal.generator import UniversalGenerator

generator = UniversalGenerator("python")  # or nodejs, typescript, rust
files = generator.generate_all_files(config, "goobits.yaml")

# Direct Orchestrator access
from goobits_cli.universal.engine.orchestrator import Orchestrator

orchestrator = Orchestrator()
files = orchestrator.generate_content(config, "python", "goobits.yaml")
```

---

## Metrics

- **Lines deleted**: ~15,000 (legacy generators + template_engine)
- **Test coverage**: 500+ tests passing
- **Performance**: <100ms CLI startup, <1s generation
- **Languages**: Python, Node.js, TypeScript, Rust (all production-ready)
