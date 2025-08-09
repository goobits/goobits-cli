# PROPOSAL_04: Goobits Universal CLI DSL

> **📋 Status: DRAFT - Not yet implemented**  
> This proposal is under consideration and has not been implemented.
> Note: Depends on Rust implementation (PROPOSAL_03) being completed first.

**Status**: Draft Proposal  
**Author**: Development Team  
**Date**: 2025-01-24  
**Version**: 2.0  
**Prerequisite**: See PROPOSAL_03_RUST.md

## Executive Summary

This proposal extends PROPOSAL_03_RUST to create a **Universal CLI DSL** that generates native CLIs for multiple programming languages. This builds directly on the Rust implementation proven in Phase 1.

**Note**: This proposal assumes successful completion of PROPOSAL_03_RUST as validation.

## Schema Evolution from PROPOSAL_03_RUST

### Multi-Target Extension

Building on the Rust proposal's `language: rust` approach, extend to support multiple simultaneous targets:

```yaml
# Evolution from PROPOSAL_03_RUST single language
targets: [rust, python]  # Generate both from same config

# Rest remains identical to current schema
package_name: goobits-tts
command_name: tts
description: "Multi-provider text-to-speech with voice cloning"

cli:
  commands:
    speak:
      desc: "Speak text aloud"
      # ... same as current goobits.yaml
```

### Real Project Migration Path

Using existing goobits-tts as concrete example (not hypothetical):

**Current goobits-tts/goobits.yaml:**
```yaml
package_name: "goobits-tts"
command_name: "tts"
# ... existing 300+ lines
```

**Universal goobits-tts/goobits.yaml:**
```yaml
targets: [python, rust]  # Only change needed
package_name: "goobits-tts" 
command_name: "tts"
# ... rest stays identical
```

## Implementation Strategy

### Phase 2A: Add Go Target (Build on Rust Success)

**Prerequisite**: PROPOSAL_03_RUST implementation completed and validated with claude-usage project.

**Goal**: Extend proven Rust generator pattern to support Go with Cobra framework.

**Timeline**: 1-2 weeks after Rust validation

**Scope**: 
- Add Go generator using same template pattern as Rust implementation
- Generate Cobra-based CLI alongside existing Python/Rust outputs
- Validate with one real project (likely goobits-cli self-hosting)

### Phase 2B: Multi-Target Architecture

**Goal**: Generate multiple languages simultaneously from single YAML config.

**Implementation**:
```yaml
# Simple extension of PROPOSAL_03_RUST approach
targets: [rust, python, go]  # Instead of language: rust

# Generated structure (extends PROPOSAL_03_RUST pattern):
goobits-tts/
├── goobits.yaml           # Source config
├── outputs/
│   ├── rust/              # From PROPOSAL_03_RUST
│   │   ├── Cargo.toml
│   │   └── src/main.rs
│   ├── python/            # Current implementation  
│   │   └── src/tts/cli.py
│   └── go/                # New target
│       ├── go.mod
│       └── cmd/root.go
└── shared_hooks/
    ├── app_hooks.py       # Existing Python hooks
    ├── app_hooks.rs       # From PROPOSAL_03_RUST  
    └── app_hooks.go       # New Go hooks
```

### Validation Strategy

**Real Project Testing** (not hypothetical examples):
1. **goobits-tts**: Multi-provider TTS with complex CLI structure
2. **goobits-stt**: Speech-to-text with server modes  
3. **claude-usage**: High-performance Rust tool (from PROPOSAL_03_RUST)
4. **goobits-cli**: Self-hosting - generate goobits-cli itself in multiple languages

### Success Criteria

**Technical Validation**:
- All existing Python projects generate working Rust/Go equivalents
- Generated binaries pass same integration tests as Python versions
- Performance improvements measurable (2-10x faster startup)

**Adoption Validation**:
- At least 2 real projects successfully migrate to multi-target
- Community feedback validates approach
- No critical blockers for enterprise adoption

## Key Differentiators from PROPOSAL_03_RUST

### 1. Multi-Target Generation
- **Rust Proposal**: Single language (`language: rust`)  
- **Universal Proposal**: Multiple simultaneous targets (`targets: [rust, python, go]`)

### 2. Strategic Positioning  
- **Rust Proposal**: Feature addition to goobits-cli
- **Universal Proposal**: Platform transformation for multi-language teams

### 3. Market Expansion
- **Rust Proposal**: Access Rust CLI developer community
- **Universal Proposal**: Universal CLI generation platform across all languages

## Dependencies and Prerequisites

**Critical Dependencies**:
1. **PROPOSAL_03_RUST completion**: Must validate Rust generation works with real projects
2. **Community validation**: Rust implementation gets positive feedback
3. **Resource commitment**: Multi-language support requires sustained development effort

**Go/No-Go Decision Point**: Only proceed if PROPOSAL_03_RUST demonstrates:
- Technical feasibility with complex real projects  
- Community interest and adoption
- Clear performance/distribution benefits

## Timeline (Post-PROPOSAL_03_RUST)

**Phase 2A: Go Generator** (Month 1-2)
- [ ] Add Go/Cobra generator using proven Rust template pattern
- [ ] Validate with goobits-cli self-hosting

**Phase 2B: Multi-Target Architecture** (Month 3-4)  
- [ ] Extend schema: `targets: [rust, python, go]`
- [ ] Generate all targets simultaneously
- [ ] Migrate goobits-tts and goobits-stt

**Phase 2C: Platform Features** (Month 5-6)
- [ ] Cross-language hook interface standardization
- [ ] Advanced type mapping system
- [ ] Enterprise deployment features

## Risk Mitigation

**Primary Risk**: Over-engineering before market validation

**Mitigation**: This proposal is contingent on PROPOSAL_03_RUST success. If Rust adoption is low, abandon universal approach and focus on Python+Rust only.

**Secondary Risk**: Maintenance burden across multiple languages

**Mitigation**: Build on proven patterns from PROPOSAL_03_RUST. Don't add languages without strong demand.

## Conclusion

PROPOSAL_02_UNIVERSAL extends the proven foundation of PROPOSAL_03_RUST into a comprehensive multi-language platform. 

**Key Insight**: This is not a alternative to the Rust proposal - it's the natural evolution after Rust validation proves the concept works.

**Recommendation**: Implement PROPOSAL_03_RUST first. Only proceed with PROPOSAL_02_UNIVERSAL if Rust implementation succeeds and community validates demand for multi-language generation.