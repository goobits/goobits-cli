# Archived Proposals

This directory contains proposals that have been superseded by newer, more comprehensive proposals or have been incorporated into the main implementation roadmap.

## Archived Proposals

### PROPOSAL_03_RUST.md
**Superseded by:** PROPOSAL_06_UNIFIED_IMPLEMENTATION.md  
**Reason:** The original Rust proposal attempted to add Rust support without completing the foundation work. PROPOSAL_06 takes a more pragmatic approach of completing all language implementations before adding new ones.

### PROPOSAL_04_UNIVERSAL.md
**Superseded by:** PROPOSAL_06_UNIFIED_IMPLEMENTATION.md  
**Reason:** This proposal was too ambitious, attempting to create a universal template system before basic features were working across languages. The concepts were incorporated into Phase 3 of PROPOSAL_06.

### PROPOSAL_05_LANGUAGE_PARITY.md
**Superseded by:** PROPOSAL_06_UNIFIED_IMPLEMENTATION.md  
**Reason:** While this proposal correctly identified the need for language parity, it lacked implementation details. PROPOSAL_06 provides a concrete roadmap with specific milestones.

### PROPOSAL_UNIVERSAL_TEMPLATES.md
**Superseded by:** PROPOSAL_06_UNIFIED_IMPLEMENTATION.md  
**Reason:** The universal template concepts were valid but premature. These ideas were incorporated into Phase 3 of the unified implementation roadmap.

### PROPOSAL_RUST_GENERATOR_FIX.md
**Status:** Deferred pending v2.0 release  
**Reason:** Rust support has been removed from v2.0 scope after discovering fundamental architectural issues (57+ compilation errors). This proposal documents lessons learned for future Rust implementation attempts. The test-driven approach outlined here will guide future Rust development post-v2.0.

## Note on Proposal Evolution

These archived proposals represent important steps in the project's evolution. Each contributed valuable insights that informed the current implementation strategy. They are preserved here for historical reference and to understand the project's development journey.

For the current implementation roadmap, see:
- `/PROPOSAL_06_UNIFIED_IMPLEMENTATION.md` - Active master roadmap
- `/docs/IMPLEMENTATION_STATUS.md` - Current implementation status