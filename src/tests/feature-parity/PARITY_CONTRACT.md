# Feature Parity Contract

This document defines the supported parity contract for the generated test CLIs.

## Scope

- Required parity targets: `python`, `nodejs`, `rust`
- Optional target: `typescript` (excluded from default parity runs until runnable JS output is guaranteed)

## Assertions

- Parity tests validate:
  - command availability
  - command argument/option behavior
  - file-side effects for file commands
  - hook execution for command handlers
- Parity tests do **not** require byte-identical help/error formatting across runtimes.

## Exit Code Policy

- Success: `0`
- Usage/config parse errors:
  - Python/Rust generally return `2`
  - Node may return `1` for parser errors depending on runtime/toolchain behavior
- Hook-driven command failures must propagate a non-zero exit code.

## Hook Naming Compatibility

The parity hook modules must support both:

- namespaced hooks: `on_config_get`, `on_file_create`, ...
- short hooks: `on_get`, `on_create`, ...

This keeps parity resilient to renderer naming differences while preserving behavior assertions.

## TypeScript Policy

- TypeScript parity is currently opt-in.
- Default parity runner excludes TypeScript until generated projects always produce a runnable JS entrypoint.
