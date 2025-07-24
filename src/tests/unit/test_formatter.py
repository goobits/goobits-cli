"""Unit tests for formatter.py module."""
import pytest
from unittest.mock import Mock
from goobits_cli.formatter import (
    align_examples,
    format_multiline_text,
    align_setup_steps,
    escape_for_docstring,
    get_icon_width,
    format_icon_spacing,
    align_header_items
)


class TestAlignExamples:
    """Test cases for align_examples function."""
    
    def test_empty_list(self):
        """Test align_examples with empty list."""
        result = align_examples([])
        assert result == []
    
    def test_single_example(self):
        """Test align_examples with single example."""
        examples = [("command", "description")]
        result = align_examples(examples)
        assert result == ["command  description"]
    
    def test_multiple_examples_same_length(self):
        """Test align_examples with commands of same length."""
        examples = [("cmd1", "desc1"), ("cmd2", "desc2")]
        result = align_examples(examples)
        expected = ["cmd1  desc1", "cmd2  desc2"]
        assert result == expected
    
    def test_multiple_examples_different_lengths(self):
        """Test align_examples with commands of different lengths."""
        examples = [("short", "short command"), ("very_long_command", "long command")]
        result = align_examples(examples)
        expected = [
            "short              short command",
            "very_long_command  long command"
        ]
        assert result == expected
    
    def test_empty_descriptions(self):
        """Test align_examples with empty descriptions."""
        examples = [("cmd1", ""), ("cmd2", "desc")]
        result = align_examples(examples)
        expected = ["cmd1  ", "cmd2  desc"]
        assert result == expected


class TestFormatMultilineText:
    """Test cases for format_multiline_text function."""
    
    def test_empty_text(self):
        """Test format_multiline_text with empty string."""
        result = format_multiline_text("")
        assert result == ""
    
    def test_none_text(self):
        """Test format_multiline_text with None."""
        result = format_multiline_text(None)
        assert result == ""
    
    def test_single_line_no_indent(self):
        """Test format_multiline_text with single line and no indent."""
        result = format_multiline_text("Hello world")
        assert result == "Hello world"
    
    def test_single_line_with_indent(self):
        """Test format_multiline_text with single line and indent."""
        result = format_multiline_text("Hello world", indent=4)
        assert result == "    Hello world"
    
    def test_multiline_no_indent(self):
        """Test format_multiline_text with multiple lines and no indent."""
        text = "Line 1\nLine 2\nLine 3"
        result = format_multiline_text(text)
        assert result == "Line 1\nLine 2\nLine 3"
    
    def test_multiline_with_indent(self):
        """Test format_multiline_text with multiple lines and indent."""
        text = "Line 1\nLine 2\nLine 3"
        result = format_multiline_text(text, indent=2)
        expected = "  Line 1\n  Line 2\n  Line 3"
        assert result == expected
    
    def test_multiline_with_empty_lines(self):
        """Test format_multiline_text preserving empty lines."""
        text = "Line 1\n\nLine 3"
        result = format_multiline_text(text, indent=2)
        expected = "  Line 1\n\n  Line 3"
        assert result == expected
    
    def test_text_with_leading_trailing_whitespace(self):
        """Test format_multiline_text strips leading/trailing whitespace."""
        text = "  \n  Line 1\n  Line 2\n  \n"
        result = format_multiline_text(text, indent=2)
        expected = "  Line 1\n    Line 2"
        assert result == expected


class TestAlignSetupSteps:
    """Test cases for align_setup_steps function."""
    
    def test_empty_text(self):
        """Test align_setup_steps with empty string."""
        result = align_setup_steps("")
        assert result == ""
    
    def test_none_text(self):
        """Test align_setup_steps with None."""
        result = align_setup_steps(None)
        assert result == ""
    
    def test_no_colons(self):
        """Test align_setup_steps with text containing no colons."""
        text = "Step 1\nStep 2\nStep 3"
        result = align_setup_steps(text)
        assert result == text
    
    def test_single_colon_line(self):
        """Test align_setup_steps with single line containing colon."""
        text = "Step 1: Description"
        result = align_setup_steps(text)
        assert result == "Step 1: Description"
    
    def test_multiple_aligned_colons(self):
        """Test align_setup_steps with already aligned colons."""
        text = "Step 1: Description\nStep 2: Another description"
        result = align_setup_steps(text)
        assert result == text
    
    def test_multiple_unaligned_colons(self):
        """Test align_setup_steps with unaligned colons."""
        text = "Short: Description\nVery long step: Another description"
        result = align_setup_steps(text)
        expected = "Short         : Description\nVery long step: Another description"
        assert result == expected
    
    def test_with_indented_substeps(self):
        """Test align_setup_steps preserving indented substeps."""
        text = "Step 1: Description\n  Substep 1\n  Substep 2\nStep 2: Another"
        result = align_setup_steps(text)
        expected = "Step 1: Description\n  Substep 1\n  Substep 2\nStep 2: Another"
        assert result == expected
    
    def test_with_empty_lines(self):
        """Test align_setup_steps preserving empty lines."""
        text = "Step 1: Description\n\nStep 2: Another"
        result = align_setup_steps(text)
        expected = "Step 1: Description\n\nStep 2: Another"
        assert result == expected


class TestEscapeForDocstring:
    """Test cases for escape_for_docstring function."""
    
    def test_no_escaping_needed(self):
        """Test escape_for_docstring with text needing no escaping."""
        text = "Simple text with no special characters"
        result = escape_for_docstring(text)
        assert result == text
    
    def test_escape_triple_quotes(self):
        """Test escape_for_docstring with triple quotes."""
        text = 'Text with """ triple quotes'
        result = escape_for_docstring(text)
        expected = 'Text with \\\\"\\\\"\\\\" triple quotes'
        assert result == expected
    
    def test_escape_backslashes(self):
        """Test escape_for_docstring with backslashes."""
        text = "Text with \\ backslashes"
        result = escape_for_docstring(text)
        expected = "Text with \\\\ backslashes"
        assert result == expected
    
    def test_preserve_escape_sequences(self):
        """Test escape_for_docstring preserving intended escape sequences."""
        text = "Text with \\n newline \\t tab \\b backspace"
        result = escape_for_docstring(text)
        expected = "Text with \\n newline \\t tab \\b backspace"
        assert result == expected
    
    def test_complex_escaping(self):
        """Test escape_for_docstring with complex escaping scenarios."""
        text = 'Complex """ text with \\n and \\ backslash'
        result = escape_for_docstring(text)
        expected = 'Complex \\\\"\\\\"\\\\" text with \\n and \\\\ backslash'
        assert result == expected


class TestGetIconWidth:
    """Test cases for get_icon_width function."""
    
    def test_empty_string(self):
        """Test get_icon_width with empty string."""
        result = get_icon_width("")
        assert result == 0
    
    def test_single_character(self):
        """Test get_icon_width with single ASCII character."""
        result = get_icon_width("A")
        assert result == 1
    
    def test_simple_emoji(self):
        """Test get_icon_width with simple emoji."""
        result = get_icon_width("😀")
        assert result == 1
    
    def test_emoji_with_variation_selector(self):
        """Test get_icon_width with emoji containing variation selector."""
        # Info icon with variation selector (U+2139 + U+FE0F)
        icon = "ℹ️"
        result = get_icon_width(icon)
        assert result == 2
    
    def test_multi_codepoint_emoji(self):
        """Test get_icon_width with multi-codepoint emoji."""
        # Family emoji (multiple codepoints)
        icon = "👨‍👩‍👧‍👦"
        result = get_icon_width(icon)
        assert result == 2
    
    def test_gear_with_variation_selector(self):
        """Test get_icon_width with gear emoji and variation selector."""
        # Gear icon with variation selector (U+2699 + U+FE0F)  
        icon = "⚙️"
        result = get_icon_width(icon)
        assert result == 2


class TestFormatIconSpacing:
    """Test cases for format_icon_spacing function."""
    
    def test_empty_string(self):
        """Test format_icon_spacing with empty string."""
        result = format_icon_spacing("")
        assert result == ""
    
    def test_single_width_icon(self):
        """Test format_icon_spacing with single-width icon."""
        result = format_icon_spacing("A")
        assert result == "A "
    
    def test_double_width_icon(self):
        """Test format_icon_spacing with double-width icon."""
        # Using info icon with variation selector
        icon = "ℹ️"
        result = format_icon_spacing(icon)
        assert result == "ℹ️  "
    
    def test_simple_emoji(self):
        """Test format_icon_spacing with simple emoji."""
        result = format_icon_spacing("😀")
        assert result == "😀 "


class TestAlignHeaderItems:
    """Test cases for align_header_items function."""
    
    def test_empty_list(self):
        """Test align_header_items with empty list."""
        result = align_header_items([])
        assert result == []
    
    def test_dict_items(self):
        """Test align_header_items with dictionary items."""
        items = [
            {"item": "short", "desc": "Short description"},
            {"item": "very_long_item", "desc": "Long description"}
        ]
        result = align_header_items(items)
        
        assert len(result) == 2
        assert result[0]["item_aligned"] == "short           "
        assert result[1]["item_aligned"] == "very_long_item  "
        assert result[0]["desc"] == "Short description"
        assert result[1]["desc"] == "Long description"
    
    def test_object_items_with_dict_method(self):
        """Test align_header_items with Pydantic-like objects."""
        mock_item1 = Mock()
        mock_item1.dict.return_value = {"item": "cmd1", "desc": "Description 1"}
        
        mock_item2 = Mock()
        mock_item2.dict.return_value = {"item": "command2", "desc": "Description 2"}
        
        items = [mock_item1, mock_item2]
        result = align_header_items(items)
        
        assert len(result) == 2
        assert result[0]["item_aligned"] == "cmd1      "
        assert result[1]["item_aligned"] == "command2  "
    
    def test_object_items_with_dict_attr(self):
        """Test align_header_items with regular objects."""
        class MockItem:
            def __init__(self, item, desc):
                self.item = item
                self.desc = desc
        
        items = [
            MockItem("abc", "Description 1"),
            MockItem("abcdef", "Description 2")
        ]
        result = align_header_items(items)
        
        assert len(result) == 2
        assert result[0]["item_aligned"] == "abc     "
        assert result[1]["item_aligned"] == "abcdef  "
    
    def test_mixed_item_types(self):
        """Test align_header_items with mixed item types."""
        class MockItem:
            def __init__(self, item, desc):
                self.item = item
                self.desc = desc
        
        items = [
            {"item": "dict_item", "desc": "Dict description"},
            MockItem("obj_item", "Object description")
        ]
        result = align_header_items(items)
        
        assert len(result) == 2
        assert result[0]["item_aligned"] == "dict_item  "
        assert result[1]["item_aligned"] == "obj_item   "
    
    def test_single_item(self):
        """Test align_header_items with single item."""
        items = [{"item": "single", "desc": "Single item"}]
        result = align_header_items(items)
        
        assert len(result) == 1
        assert result[0]["item_aligned"] == "single  "
        assert result[0]["desc"] == "Single item"