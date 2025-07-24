"""Formatting utilities for CLI generation."""
from typing import List, Tuple
import unicodedata


def align_examples(examples: List[Tuple[str, str]]) -> List[str]:
    """
    Align example descriptions to start at the same column.
    
    Args:
        examples: List of (command, description) tuples
        
    Returns:
        List of formatted example lines
    """
    if not examples:
        return []
    
    # Find the longest command length
    max_cmd_length = max(len(cmd) for cmd, _ in examples)
    
    # Format each example with aligned descriptions
    formatted_examples = []
    for cmd, desc in examples:
        # Calculate padding needed
        padding = " " * (max_cmd_length - len(cmd) + 2)
        # Format the line
        formatted_line = f"{cmd}{padding}{desc}"
        formatted_examples.append(formatted_line)
    
    return formatted_examples


def format_multiline_text(text: str, indent: int = 0) -> str:
    """
    Format multiline text with proper indentation.
    
    Args:
        text: The text to format
        indent: Number of spaces to indent each line
        
    Returns:
        Formatted text with proper indentation
    """
    if not text:
        return ""
    
    lines = text.strip().split('\n')
    indent_str = " " * indent
    
    # Process each line
    formatted_lines = []
    for line in lines:
        # Preserve empty lines
        if not line.strip():
            formatted_lines.append("")
        else:
            formatted_lines.append(f"{indent_str}{line}")
    
    return '\n'.join(formatted_lines)


def align_setup_steps(text: str) -> str:
    """
    Align setup steps so that colons line up vertically.
    
    Args:
        text: The setup guide text to format
        
    Returns:
        Formatted text with aligned colons
    """
    if not text:
        return ""
    
    lines = text.strip().split('\n')
    processed_lines = []
    
    # Find lines with colons and calculate max position
    colon_lines = []
    max_colon_pos = 0
    
    for line in lines:
        # Check if line contains a colon that should be aligned
        # Skip lines that are indented (sub-steps) or empty
        if ':' in line and not line.strip().startswith(' ') and line.strip():
            colon_pos = line.find(':')
            colon_lines.append((line, colon_pos))
            max_colon_pos = max(max_colon_pos, colon_pos)
    
    # Process all lines
    for line in lines:
        if not line.strip():
            # Preserve empty lines
            processed_lines.append(line)
        elif ':' in line and not line.strip().startswith(' '):
            # This is a main step with a colon - align it
            colon_pos = line.find(':')
            if colon_pos < max_colon_pos:
                # Add padding before the colon
                padding = ' ' * (max_colon_pos - colon_pos)
                line = line[:colon_pos] + padding + line[colon_pos:]
            processed_lines.append(line)
        else:
            # This is a sub-step or line without colon - keep as is
            processed_lines.append(line)
    
    return '\n'.join(processed_lines)


def escape_for_docstring(text: str) -> str:
    """
    Escape text for use in Python docstrings.
    
    Args:
        text: The text to escape
        
    Returns:
        Escaped text safe for docstrings
    """
    # Escape triple quotes
    text = text.replace('"""', r'\"\"\"')
    # Escape backslashes (but not for intended escape sequences)
    text = text.replace('\\', '\\\\')
    # Then restore intended escape sequences
    text = text.replace('\\\\b', '\\b')
    text = text.replace('\\\\n', '\\n')
    text = text.replace('\\\\t', '\\t')
    
    return text


def get_icon_width(icon: str) -> int:
    """
    Calculate the display width of an icon/emoji in terminal columns.
    
    Icons with variation selectors or multiple code points need extra spacing.
    
    Args:
        icon: The icon/emoji string
        
    Returns:
        Width indicator (1 for normal, 2 for complex icons)
    """
    if not icon:
        return 0
    
    # Count the number of actual characters (not bytes)
    char_count = len(icon)
    
    # Check if it contains variation selectors or combining characters
    has_variation_selector = '\uFE0F' in icon or '\uFE0E' in icon
    has_combining = any(unicodedata.category(c) in ['Mn', 'Mc', 'Me'] for c in icon)
    
    # Only return 2 for icons with multiple code points or special modifiers
    # This handles cases like ℹ️ (info + VS16) and ⚙️ (gear + VS16)
    if char_count > 1 or has_variation_selector or has_combining:
        return 2
    
    return 1


def format_icon_spacing(icon: str) -> str:
    """
    Add appropriate spacing after an icon based on its display width.
    
    Args:
        icon: The icon/emoji string
        
    Returns:
        Icon with appropriate spacing
    """
    if not icon:
        return ""
    
    width = get_icon_width(icon)
    
    # Add one space for single-width icons, two spaces for double-width
    if width == 2:
        return icon + "  "
    else:
        return icon + " "