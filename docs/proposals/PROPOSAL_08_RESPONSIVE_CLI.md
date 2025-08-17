# Responsive CLI Design Proposal

## Problem
Rich-click doesn't handle small terminal windows well, causing:
- Box borders breaking mid-line
- Text wrapping issues
- Table columns becoming unreadable

## Solution 1: Dynamic Width Adjustment
```python
import shutil

def get_terminal_width():
    """Get terminal width with fallback."""
    try:
        width = shutil.get_terminal_size().columns
    except:
        width = 80  # Fallback
    return width

def format_for_width(width):
    """Adjust formatting based on terminal width."""
    if width < 60:
        # Minimal mode - no boxes, simplified text
        click.rich_click.SHOW_ARGUMENTS = False
        click.rich_click.MAX_WIDTH = width - 2
        click.rich_click.STYLE_OPTIONS_PANEL_BORDER = "none"
        click.rich_click.STYLE_COMMANDS_PANEL_BORDER = "none"
    elif width < 80:
        # Compact mode - simplified boxes
        click.rich_click.MAX_WIDTH = width - 4
        click.rich_click.STYLE_OPTIONS_PANEL_BORDER = "dim"
        click.rich_click.STYLE_COMMANDS_PANEL_BORDER = "dim"
    else:
        # Full mode - all features
        click.rich_click.MAX_WIDTH = min(120, width - 10)
```

## Solution 2: Simplified Help for Small Terminals
```python
def get_help_text(ctx):
    """Generate help text based on terminal size."""
    width = get_terminal_width()
    
    if width < 60:
        # Ultra-compact format
        return """
goobits - Build CLI tools with YAML

Commands:
  build  - Generate CLI from YAML
  init   - Create template
  serve  - Local package server

Use: goobits [command] --help
"""
    else:
        # Full rich format
        return full_help_text
```

## Solution 3: Progressive Enhancement
```python
# In cli.py or generated_cli.py
import os

# Check if we're in a small terminal or non-interactive environment
if os.environ.get('TERM') == 'dumb' or get_terminal_width() < 60:
    # Disable rich formatting entirely
    click.rich_click.USE_RICH_MARKUP = False
    click.rich_click.USE_MARKDOWN = False
    # Use plain click instead
```

## Solution 4: Environment Variable Override
Allow users to disable rich formatting:
```bash
export GOOBITS_SIMPLE_OUTPUT=1
goobits --help  # Shows plain text help
```

## Recommended Implementation
Combine solutions 1 and 4:
1. Auto-detect terminal width and adjust formatting
2. Provide environment variable for users who prefer plain output
3. Add a --plain flag for one-time plain output

## Code Changes Required

### In generated_cli.py or cli.py:
```python
import shutil
import os

# Check for plain output preference
USE_PLAIN = (
    os.environ.get('GOOBITS_SIMPLE_OUTPUT') == '1' or
    os.environ.get('NO_COLOR') == '1' or
    os.environ.get('TERM') == 'dumb'
)

# Get terminal width
try:
    TERM_WIDTH = shutil.get_terminal_size().columns
except:
    TERM_WIDTH = 80

# Configure rich-click based on environment
if USE_PLAIN or TERM_WIDTH < 50:
    # Disable rich formatting
    click.rich_click.USE_RICH_MARKUP = False
    click.rich_click.USE_MARKDOWN = False
elif TERM_WIDTH < 80:
    # Compact mode
    click.rich_click.MAX_WIDTH = TERM_WIDTH - 4
    click.rich_click.WIDTH = TERM_WIDTH - 4
    click.rich_click.SHOW_METAVARS_COLUMN = False
    click.rich_click.STYLE_OPTIONS_PANEL_BORDER = "none"
    click.rich_click.STYLE_COMMANDS_PANEL_BORDER = "none"
else:
    # Full rich mode (current settings)
    click.rich_click.MAX_WIDTH = min(120, TERM_WIDTH - 10)
    click.rich_click.WIDTH = min(120, TERM_WIDTH - 10)
```

## Benefits
1. **Graceful degradation** - Works in all terminal sizes
2. **User control** - Environment variables for preferences
3. **Accessibility** - Better for screen readers and minimal terminals
4. **Performance** - Faster rendering in simple mode