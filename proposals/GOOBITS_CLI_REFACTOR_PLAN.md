Goobits CLI Refactor Proposal (Maintainability + Performance First)

Status: Draft (new, breaking changes allowed)
Owner: Team Goobits CLI
Audience: Engineering

Goals
- Maintainability: smaller modules, clear responsibility boundaries, no mega-classes.
- Performance: keep generated CLI startup under 100ms and generation under 1s for typical projects.
- Clarity: a single generation pipeline and a single validation framework.
- Cleanup: remove redundant tests and replace with battle-hardened, functional coverage.

Non-Goals
- Backward compatibility (explicitly allowed to break).
- Preserving legacy APIs or class shapes.
- Keeping existing test suite if it doesn't map to new behavior.

Principles
- One responsibility per module; no universal "god objects".
- Explicit data flow: config -> IR -> renderer -> output.
- No hidden dependencies (inject cache, loaders, templates).
- Delete low-value tests; replace with functional and performance tests.
- Favor data classes for IR and typed interfaces for adapters.

Current Pain Points (confirmed in codebase)
- UniversalTemplateEngine and ComponentRegistry are oversized and entangled.
- Generator code repeats lazy imports, config conversions, and path detection.
- ValidationResult is duplicated across shared components and test utilities.
- High cyclomatic complexity in main build path and setup script generation.

Proposed Architecture (Breaking)

Package layout (new)
src/goobits_cli/
  core/
    config/
      loader.py          # config loading + normalization
      schema.py          # pydantic schemas (or move existing here)
    errors.py            # unified exception hierarchy
    logging.py           # standardized logging and diagnostics
    paths.py             # path utilities (output dirs, templates)
  generation/
    engine.py            # orchestrator: config -> IR -> renderer -> artifacts
    ir/
      models.py          # dataclasses for IR
      builder.py         # build IR from config
      analyzers.py       # feature analysis (plugin-based)
    renderers/
      base.py            # renderer interface + shared utilities
      python.py
      nodejs.py
      typescript.py
      rust.py
    templates/
      loader.py          # template loading + cache strategy
  integrations/
    completion.py
    interactive.py
    plugins.py
  validation/
    framework.py         # unified ValidationResult + validators
  tests/
    acceptance/          # functional tests
    performance/         # perf regression tests

Phase 1: Delete and Consolidate (Break Everything Early)
Priority: Critical
- Remove UniversalTemplateEngine and ComponentRegistry; replace with:
  - generation/ir/builder.py for IR
  - generation/engine.py for orchestration
  - generation/templates/loader.py for template IO
- Remove generator-specific copies of:
  - lazy imports
  - config conversions
  - string utils (case conversion, JSON escape)
- Consolidate ValidationResult into validation/framework.py only.
- Delete duplicated helper utilities in generators once consolidated.

Phase 2: Generator Rewrite Around IR
Priority: High
- Build a single IR model for all languages (dataclasses).
- Implement LanguageRenderer interface for 4 languages.
- Renderer contract:
  - input: IR
  - output: list of artifacts (path + content + metadata)
- Move all language-specific conditional logic into renderers.
- Remove per-language generator classes if they only wrap rendering.

Phase 3: High-Complexity Function Refactor
Priority: High
- Split main build pipeline into:
  - config normalization
  - IR build
  - render
  - write artifacts
  - manifest updates
- Generate setup scripts via templates instead of hand-built strings.
- Ensure CLI build has no more than 10-15 branches per function.

Phase 4: Validation Framework Unification
Priority: Medium
- Single ValidationResult class, used by:
  - config validation
  - test validation
  - generator validation (if needed)
- Delete test_utils validation once integrated.
- Validate config only once; remove duplicated checks across generators.

Phase 5: Tests Rebuilt for Real Confidence
Priority: High
- Delete low-value unit tests that mirror implementation detail.
- Build acceptance tests that:
  - generate CLIs for each language
  - run key commands in generated CLIs
  - compare outputs to golden files
- Add a small set of property-based tests for config parsing and IR integrity.
- Add performance regressions:
  - generator runtime
  - generated CLI startup time
  - memory footprint

Performance Requirements
- CLI generation time: <= 1s for typical config
- Generated CLI startup: <= 100ms (cold)
- Startup memory: <= 5MB
- Automated performance tests fail on regressions.

Implementation Roadmap

Sprint 1: Architectural Skeleton
- Create new package layout under core/ and generation/.
- Implement IR dataclasses + builder (minimal).
- Implement a single renderer (Python) to validate pipeline.
- Delete UniversalTemplateEngine and ComponentRegistry to prevent backsliding.

Sprint 2: Renderer Parity
- Implement Node.js, TypeScript, Rust renderers on the new IR.
- Add shared rendering utilities (string utils, escaping, path ops).
- Remove old generators that duplicate rendering logic.

Sprint 3: Validation and Integration
- Replace all validation usage with validation/framework.py.
- Move integrations (interactive, completion, plugins) into integrations/ with clear APIs.
- Integrate plugin-based feature analyzers in IR stage.

Sprint 4: Tests Rebuilt
- Replace existing tests with acceptance + performance suites.
- Ensure each language has at least one end-to-end generation + run test.
- Add perf baselines and enforce budgets.

Sprint 5: Cleanup and Documentation
- Remove dead code and unused templates.
- Update docs to reflect new architecture.
- Add developer guide for extending renderers and IR.

Risks and Mitigations
- Risk: regressions from deleting legacy paths.
  Mitigation: new acceptance tests + golden outputs + perf gates.
- Risk: renderers diverge in behavior.
  Mitigation: single IR contract and shared rendering utilities.
- Risk: slow refactor pace.
  Mitigation: prioritize Python and Node.js renderers first.

Deliverables
- New generation pipeline (config -> IR -> renderer -> artifacts).
- Clean, minimal module boundaries.
- High-confidence acceptance/performance tests.
- Documented extension points for new features and languages.

Go/No-Go Criteria
- Python renderer can generate working CLI for sample configs.
- Node.js renderer parity on core features.
- Performance baseline enforced.
- Old generators removed to avoid mixed architectures.
