# Python Formatting Standardization Proposal

## Problem Statement

The goobits-cli codebase has inconsistent and excessive blank line usage:

| Issue | Impact |
|-------|--------|
| 45-55% of lines are blank in many files | Harder to read, more scrolling |
| 317 consecutive blank-line pairs in one file | Extreme waste of vertical space |
| Blank lines after every statement | Non-standard, confusing |
| Blank lines inside docstrings | Malformed documentation |

**Worst offenders:**
- `nodejs_utils.py`: 55% blank (1,379/2,515 lines), 317 consecutive pairs
- `nodejs_utils_simple.py`: 53% blank, 117 consecutive pairs
- `plugins/integration.py`: 52% blank, 102 consecutive pairs
- Many files at 45-50% blank

## Root Cause

The files appear to have been processed by a tool that added blank lines after every statement. This is not PEP 8 compliant and creates:
- Poor readability
- Difficult code navigation
- Inconsistent codebase

## Proposed Solution

### Phase 1: Configure Ruff as Primary Formatter

Ruff is already available (v0.14.10) and is 10-100x faster than Black while being compatible.

**Add to `pyproject.toml`:**

```toml
[tool.ruff]
line-length = 88
target-version = "py38"
src = ["src"]

[tool.ruff.lint]
select = ["E", "F", "W", "I", "UP", "B", "C4"]
ignore = ["E501"]  # Line length handled by formatter

[tool.ruff.format]
quote-style = "double"
indent-style = "space"
skip-magic-trailing-comma = false
line-ending = "auto"

# Key setting: enforce 2 blank lines between top-level definitions,
# 1 blank line between methods, 0 extra blank lines elsewhere
```

### Phase 2: Remove Excessive Blank Lines

Run a cleanup script to:
1. Remove consecutive blank lines (keep max 2)
2. Remove blank lines inside docstrings
3. Remove trailing blank lines after statements

**Script approach:**
```python
# Remove consecutive blank lines beyond PEP 8 requirements
def normalize_blank_lines(content: str) -> str:
    lines = content.split('\n')
    result = []
    blank_count = 0

    for line in lines:
        if line.strip() == '':
            blank_count += 1
            if blank_count <= 2:  # Allow max 2 consecutive
                result.append(line)
        else:
            blank_count = 0
            result.append(line)

    return '\n'.join(result)
```

### Phase 3: Run Ruff Format

```bash
# Format entire codebase
ruff format src/goobits_cli/

# Check without modifying (for CI)
ruff format --check src/goobits_cli/
```

### Phase 4: Update Dev Dependencies

**In `pyproject.toml`:**
```toml
[project.optional-dependencies]
dev = [
    # Replace black with ruff (ruff handles both linting and formatting)
    "ruff>=0.1.0",
    # ... other deps
]
```

### Phase 5: Add Pre-commit Hook (Optional)

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.0
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format
```

## Expected Results

| Metric | Before | After |
|--------|--------|-------|
| Average blank line ratio | ~45-55% | ~15-20% |
| Consecutive blank pairs | 317+ | 0 |
| Formatting consistency | Inconsistent | 100% |
| Lines of code (approx) | ~25,000 | ~18,000 |

## PEP 8 Blank Line Standards

For reference, standard Python formatting uses:
- **2 blank lines** between top-level class/function definitions
- **1 blank line** between method definitions in a class
- **0-1 blank lines** to separate logical sections within functions
- **0 blank lines** inside docstrings
- **0 blank lines** after every statement

## Implementation Steps

1. [ ] Add ruff configuration to pyproject.toml
2. [ ] Run blank-line normalization script on all files
3. [ ] Run `ruff format src/goobits_cli/`
4. [ ] Verify tests still pass
5. [ ] Update Makefile/CI to use ruff instead of black
6. [ ] Commit with message: "style: Standardize formatting with ruff, remove excessive blank lines"

## Risk Assessment

- **Low risk**: Ruff is compatible with Black's style
- **Test coverage**: 578 tests ensure functionality preserved
- **Git history**: Single commit for all formatting changes (easy to revert)

## Commands to Execute

```bash
# Step 1: Add ruff config (edit pyproject.toml)
# Step 2: Remove excessive blank lines
python3 scripts/normalize_blanks.py src/goobits_cli/

# Step 3: Format with ruff
ruff format src/goobits_cli/ src/tests/

# Step 4: Verify
pytest src/tests/

# Step 5: Commit
git add -A && git commit -m "style: Standardize formatting with ruff"
```
