# Proposal: Goobits Testing Framework

> **📋 Status: DRAFT - Not yet implemented**  
> This proposal is under consideration and has not been implemented.

**Status**: Draft Proposal  
**Date**: 2025-01-24  
**Version**: 1.0  

## Problem Statement

CLI testing across goobits projects is inconsistent and time-consuming:
- Each project uses different testing approaches
- Common CLI patterns (exit codes, file creation, output validation) require repetitive boilerplate
- No standardized way to validate CLI behavior
- Manual testing is error-prone and doesn't scale

## Proposed Solution

Add `goobits test` command that reads `goobits-test.yaml` files to validate CLI behavior using 6 core expectations.

### Design Principles
1. **YAML Configuration**: Define tests declaratively without code
2. **Core Expectations**: Focus on 6 essential validations that cover 90% of CLI testing
3. **Separate Concerns**: Keep testing config separate from CLI definition
4. **Framework Integration**: Generate standard test files (pytest, bats) when needed

## Core Expectations

Six essential validations that cover 90% of CLI testing needs:

### 1. Exit Code (`exit`)
```yaml
exit: 0           # Must exit with code 0
exit: [0, 1]      # Either code acceptable
```

### 2. Standard Output (`stdout_contains`)
```yaml
stdout_contains: ["Success", "completed"]
stdout_contains: "Generated output.txt"
```

### 3. Error Output (`stderr_contains`)
```yaml
stderr_contains: ["Error", "not found"]
```

### 4. File Creation (`files_created`)
```yaml
files_created: ["output.txt", "log.txt"]
```

### 5. File Size (`file_size`)
```yaml
file_size: 
  "output.txt": ">1000"     # At least 1000 bytes
  "image.png": "<50000"     # Less than 50KB
```

### 6. Performance (`time`)
```yaml
time: "<5s"       # Must complete within 5 seconds
```

## Configuration Format

```yaml
# goobits-test.yaml
test_suites:
  basic:
    - name: "help_command"
      run: "my-cli --help"
      expect:
        exit: 0
        stdout_contains: ["Usage"]
        time: "<2s"
        
    - name: "file_processing"
      run: "my-cli process input.txt --output result.txt"
      expect:
        exit: 0
        files_created: ["result.txt"]
        file_size: { "result.txt": ">100" }
```

## Commands

```bash
goobits test                    # Run all tests
goobits test --suite basic      # Run specific suite  
goobits test --verbose          # Show detailed output
goobits test --ci               # CI-optimized output
```

## Implementation

### File Structure (~800 lines total)
```
src/goobits_cli/
├── main.py                 (+50 lines - add test command)
├── testing/
│   ├── config.py          (150 lines - YAML parsing)
│   ├── runner.py          (200 lines - test execution)  
│   ├── expectations.py    (250 lines - core validators)
│   └── generators.py      (200 lines - pytest generation)
└── schemas.py             (+100 lines - TestConfig schema)
```

### Integration: Separate Configuration File
- **goobits.yaml**: CLI definition (unchanged)
- **goobits-test.yaml**: Test configuration (new)

**Benefits**: Clean separation, optional adoption, focused files

### MVP Implementation (~400 lines)
1. Add `goobits test` command
2. YAML parser for test configuration  
3. Six core expectation validators
4. Basic test runner with results

**Estimated Time**: 1-2 days

## Example: TTT Testing

```yaml
# ttt/goobits-test.yaml
test_suites:
  basic:
    - name: "help_works"
      run: "tts --help"
      expect:
        exit: 0
        stdout_contains: ["Usage"]
        
    - name: "generates_audio"
      run: 'tts "hello" --output test.wav'
      expect:
        exit: 0
        files_created: ["test.wav"]
        file_size: { "test.wav": ">1000" }
        time: "<10s"
        
    - name: "handles_errors"
      run: 'tts "" --output empty.wav'
      expect:
        exit: 1
        stderr_contains: ["Error"]
```

**Output:**
```bash
$ goobits test
✅ basic/help_works (0.1s)
✅ basic/generates_audio (2.3s) - Created test.wav (4.2KB)
✅ basic/handles_errors (0.1s)
📊 3/3 passed (2.5s total)
```

## Benefits

- **Standardized Testing**: Same approach across all goobits projects
- **Low Barrier**: Write tests in YAML, not code
- **Real Validation**: Tests actual CLI behavior, not just mocks
- **Quick Feedback**: Fast test execution for development workflow

## Next Steps

1. Build MVP with 6 core expectations (~400 lines)
2. Test with TTT project as validation
3. Iterate based on real usage
4. Add to goobits-cli as `goobits test` command

**Decision needed**: Proceed with MVP implementation?