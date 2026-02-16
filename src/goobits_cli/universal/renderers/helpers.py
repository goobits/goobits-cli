"""
Shared utility functions for language renderers.

This module provides common utilities used across multiple renderers,
following the DRY principle by centralizing shared functionality.
"""

import re
from typing import Dict

# Import case conversion functions from centralized utils
from goobits_cli.utils.strings import (
    to_camel_case,
    to_kebab_case,
    to_pascal_case,
    to_snake_case,
)

__all__ = [
    "escape_string",
    "indent",
    "to_snake_case",
    "to_camel_case",
    "to_pascal_case",
    "to_kebab_case",
    "format_docstring",
    "get_type_mapping",
]


def escape_string(s: str, language: str) -> str:
    """
    Escape a string for safe inclusion in generated code.

    Args:
        s: String to escape
        language: Target language ('python', 'nodejs', 'typescript', 'rust')

    Returns:
        Escaped string safe for the target language
    """
    if not s:
        return s

    if language == "python":
        # Python string escaping
        return s.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")
    elif language in ("nodejs", "typescript"):
        # JavaScript/TypeScript string escaping
        return (
            s.replace("\\", "\\\\")
            .replace('"', '\\"')
            .replace("'", "\\'")
            .replace("\n", "\\n")
            .replace("`", "\\`")
        )
    elif language == "rust":
        # Rust string escaping
        return s.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")
    else:
        # Default: basic escaping
        return s.replace("\\", "\\\\").replace('"', '\\"')


def indent(text: str, level: int = 1, spaces: int = 4) -> str:
    """
    Indent text by the specified number of levels.

    Args:
        text: Text to indent
        level: Number of indentation levels
        spaces: Spaces per indentation level

    Returns:
        Indented text
    """
    if not text:
        return text

    prefix = " " * (level * spaces)
    lines = text.split("\n")
    return "\n".join(prefix + line if line.strip() else line for line in lines)


# Note: to_snake_case, to_camel_case, to_pascal_case, to_kebab_case are now
# imported from goobits_cli.utils.strings to avoid code duplication


def format_docstring(text: str, language: str) -> str:
    """
    Format a docstring for the target language.

    Args:
        text: Documentation text
        language: Target language

    Returns:
        Formatted docstring
    """
    if not text:
        return ""

    if language == "python":
        # Python triple-quoted docstring
        escaped = text.replace('"""', '\\"\\"\\"')
        return f'"""{escaped}"""'
    elif language in ("nodejs", "typescript"):
        # JSDoc comment
        lines = text.split("\n")
        if len(lines) == 1:
            return f"/** {text} */"
        formatted_lines = ["/**"]
        for line in lines:
            formatted_lines.append(f" * {line}")
        formatted_lines.append(" */")
        return "\n".join(formatted_lines)
    elif language == "rust":
        # Rust doc comment
        lines = text.split("\n")
        return "\n".join(f"/// {line}" for line in lines)
    else:
        return text


def get_type_mapping(language: str) -> Dict[str, str]:
    """
    Get type mappings for the target language.

    Args:
        language: Target language

    Returns:
        Dictionary mapping generic types to language-specific types
    """
    mappings = {
        "python": {
            "string": "str",
            "integer": "int",
            "float": "float",
            "boolean": "bool",
            "array": "list",
            "object": "dict",
            "any": "Any",
            "void": "None",
            "file": "Path",
            "path": "Path",
        },
        "nodejs": {
            "string": "string",
            "integer": "number",
            "float": "number",
            "boolean": "boolean",
            "array": "Array",
            "object": "object",
            "any": "any",
            "void": "void",
            "file": "string",
            "path": "string",
        },
        "typescript": {
            "string": "string",
            "integer": "number",
            "float": "number",
            "boolean": "boolean",
            "array": "Array<T>",
            "object": "Record<string, unknown>",
            "any": "unknown",
            "void": "void",
            "file": "string",
            "path": "string",
        },
        "rust": {
            "string": "String",
            "integer": "i64",
            "float": "f64",
            "boolean": "bool",
            "array": "Vec<T>",
            "object": "HashMap<String, Value>",
            "any": "Value",
            "void": "()",
            "file": "PathBuf",
            "path": "PathBuf",
        },
    }
    return mappings.get(language, mappings["python"])


def map_type(generic_type: str, language: str) -> str:
    """
    Map a generic type to a language-specific type.

    Args:
        generic_type: Generic type name
        language: Target language

    Returns:
        Language-specific type
    """
    type_mapping = get_type_mapping(language)
    return type_mapping.get(generic_type.lower(), generic_type)


def safe_identifier(name: str, language: str) -> str:
    """
    Convert a name to a safe identifier for the target language.

    Args:
        name: Name to convert
        language: Target language

    Returns:
        Safe identifier for the target language
    """
    if not name:
        return "_unnamed"

    # Reserved words by language
    reserved = {
        "python": {
            "False",
            "None",
            "True",
            "and",
            "as",
            "assert",
            "async",
            "await",
            "break",
            "class",
            "continue",
            "def",
            "del",
            "elif",
            "else",
            "except",
            "finally",
            "for",
            "from",
            "global",
            "if",
            "import",
            "in",
            "is",
            "lambda",
            "nonlocal",
            "not",
            "or",
            "pass",
            "raise",
            "return",
            "try",
            "while",
            "with",
            "yield",
        },
        "nodejs": {
            "break",
            "case",
            "catch",
            "class",
            "const",
            "continue",
            "debugger",
            "default",
            "delete",
            "do",
            "else",
            "export",
            "extends",
            "finally",
            "for",
            "function",
            "if",
            "import",
            "in",
            "instanceof",
            "let",
            "new",
            "return",
            "super",
            "switch",
            "this",
            "throw",
            "try",
            "typeof",
            "var",
            "void",
            "while",
            "with",
            "yield",
        },
        "typescript": {
            "break",
            "case",
            "catch",
            "class",
            "const",
            "continue",
            "debugger",
            "default",
            "delete",
            "do",
            "else",
            "enum",
            "export",
            "extends",
            "finally",
            "for",
            "function",
            "if",
            "implements",
            "import",
            "in",
            "instanceof",
            "interface",
            "let",
            "new",
            "return",
            "super",
            "switch",
            "this",
            "throw",
            "try",
            "type",
            "typeof",
            "var",
            "void",
            "while",
            "with",
            "yield",
        },
        "rust": {
            "as",
            "break",
            "const",
            "continue",
            "crate",
            "dyn",
            "else",
            "enum",
            "extern",
            "false",
            "fn",
            "for",
            "if",
            "impl",
            "in",
            "let",
            "loop",
            "match",
            "mod",
            "move",
            "mut",
            "pub",
            "ref",
            "return",
            "self",
            "Self",
            "static",
            "struct",
            "super",
            "trait",
            "true",
            "type",
            "unsafe",
            "use",
            "where",
            "while",
        },
    }

    # Convert to appropriate case
    if language == "python":
        identifier = to_snake_case(name)
    elif language in ("nodejs", "typescript"):
        identifier = to_camel_case(name)
    elif language == "rust":
        identifier = to_snake_case(name)
    else:
        identifier = name

    # Replace invalid characters
    identifier = re.sub(r"[^a-zA-Z0-9_]", "_", identifier)

    # Ensure doesn't start with number
    if identifier and identifier[0].isdigit():
        identifier = "_" + identifier

    # Handle reserved words
    lang_reserved = reserved.get(language, set())
    if identifier in lang_reserved:
        identifier = identifier + "_"

    return identifier or "_unnamed"


__all__ = [
    "escape_string",
    "indent",
    "to_snake_case",
    "to_camel_case",
    "to_pascal_case",
    "format_docstring",
    "get_type_mapping",
    "map_type",
    "safe_identifier",
]
