"""
Variable management system for REPL mode in Goobits CLI Framework.

Provides a comprehensive variable storage, type inference, and substitution system
that integrates with the existing session management. Features include:
- Automatic type detection and validation
- Variable persistence across sessions
- Safe command substitution with security measures
- Performance-optimized operations (<10ms per operation)
"""

import json
import re
import time
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, asdict
from threading import Lock
import logging
from enum import Enum

logger = logging.getLogger(__name__)


class VariableType(Enum):
    """Supported variable types with automatic inference."""

    STRING = "string"
    NUMBER = "number"
    BOOLEAN = "boolean"
    ARRAY = "array"
    OBJECT = "object"


@dataclass
class Variable:
    """Represents a stored variable with metadata."""

    name: str
    value: Any
    var_type: VariableType
    created_at: float
    last_modified: float
    description: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "name": self.name,
            "value": self.value,
            "type": self.var_type.value,
            "created_at": self.created_at,
            "last_modified": self.last_modified,
            "description": self.description,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Variable":
        """Create from dictionary loaded from JSON."""
        return cls(
            name=data["name"],
            value=data["value"],
            var_type=VariableType(data["type"]),
            created_at=data["created_at"],
            last_modified=data["last_modified"],
            description=data.get("description"),
        )


class TypeInferenceEngine:
    """
    Automatic type detection and validation engine.

    Features:
    - Smart parsing of common types (numbers, booleans, JSON)
    - Type validation and conversion
    - Security-focused parsing (no code execution)
    - Performance-optimized (<5ms per inference)
    """

    # Compiled regex patterns for performance
    _NUMBER_PATTERN = re.compile(r"^-?(?:0|[1-9]\d*)(?:\.\d+)?(?:[eE][+-]?\d+)?$")
    _BOOLEAN_PATTERN = re.compile(r"^(?:true|false|yes|no|on|off|1|0)$", re.IGNORECASE)
    _JSON_ARRAY_PATTERN = re.compile(r"^\[.*\]$")
    _JSON_OBJECT_PATTERN = re.compile(r"^\{.*\}$")

    # Boolean value mappings
    _TRUE_VALUES = {"true", "yes", "on", "1"}
    _FALSE_VALUES = {"false", "no", "off", "0"}

    @classmethod
    def infer_type_and_parse(cls, raw_value: str) -> Tuple[Any, VariableType]:
        """
        Infer type and parse value from string input.

        Args:
            raw_value: Raw string value to parse

        Returns:
            Tuple of (parsed_value, variable_type)
        """
        raw_value = raw_value.strip()

        if not raw_value:
            return "", VariableType.STRING

        # Try number parsing
        if cls._NUMBER_PATTERN.match(raw_value):
            try:
                if "." in raw_value or "e" in raw_value.lower():
                    return float(raw_value), VariableType.NUMBER
                else:
                    return int(raw_value), VariableType.NUMBER
            except ValueError:
                pass

        # Try boolean parsing
        if cls._BOOLEAN_PATTERN.match(raw_value):
            lower_val = raw_value.lower()
            if lower_val in cls._TRUE_VALUES:
                return True, VariableType.BOOLEAN
            elif lower_val in cls._FALSE_VALUES:
                return False, VariableType.BOOLEAN

        # Try JSON array parsing
        if cls._JSON_ARRAY_PATTERN.match(raw_value):
            try:
                parsed = json.loads(raw_value)
                if isinstance(parsed, list):
                    return parsed, VariableType.ARRAY
            except json.JSONDecodeError:
                pass

        # Try JSON object parsing
        if cls._JSON_OBJECT_PATTERN.match(raw_value):
            try:
                parsed = json.loads(raw_value)
                if isinstance(parsed, dict):
                    return parsed, VariableType.OBJECT
            except json.JSONDecodeError:
                pass

        # Default to string (with quote removal if present)
        if (raw_value.startswith('"') and raw_value.endswith('"')) or (
            raw_value.startswith("'") and raw_value.endswith("'")
        ):
            return raw_value[1:-1], VariableType.STRING

        return raw_value, VariableType.STRING

    @classmethod
    def validate_type(cls, value: Any, expected_type: VariableType) -> bool:
        """
        Validate that a value matches the expected type.

        Args:
            value: Value to validate
            expected_type: Expected variable type

        Returns:
            True if value matches expected type
        """
        if expected_type == VariableType.STRING:
            return isinstance(value, str)
        elif expected_type == VariableType.NUMBER:
            return isinstance(value, (int, float))
        elif expected_type == VariableType.BOOLEAN:
            return isinstance(value, bool)
        elif expected_type == VariableType.ARRAY:
            return isinstance(value, list)
        elif expected_type == VariableType.OBJECT:
            return isinstance(value, dict)
        return False

    @classmethod
    def format_value_for_display(cls, value: Any, var_type: VariableType) -> str:
        """
        Format a value for user-friendly display.

        Args:
            value: Value to format
            var_type: Variable type

        Returns:
            Formatted string representation
        """
        if var_type == VariableType.STRING:
            return f'"{value}"'
        elif var_type == VariableType.ARRAY:
            return json.dumps(value, separators=(",", ":"))
        elif var_type == VariableType.OBJECT:
            return json.dumps(value, separators=(",", ":"))
        else:
            return str(value)


class VariableStore:
    """
    Thread-safe variable storage and retrieval system.

    Features:
    - Thread-safe variable operations
    - Type validation and inference
    - Variable limits and cleanup
    - Command substitution support
    - Performance optimization (<10ms operations)
    """

    def __init__(self, max_variables: int = 100):
        """
        Initialize the variable store.

        Args:
            max_variables: Maximum number of variables to store
        """
        self.variables: Dict[str, Variable] = {}
        self.max_variables = max_variables
        self._lock = Lock()
        self._substitution_pattern = re.compile(r"\$([a-zA-Z_][a-zA-Z0-9_]*)")

        logger.debug(f"VariableStore initialized with max_variables={max_variables}")

    def set_variable(
        self, name: str, raw_value: str, description: Optional[str] = None
    ) -> bool:
        """
        Set a variable with automatic type inference.

        Args:
            name: Variable name (must be valid identifier)
            raw_value: Raw string value to parse and store
            description: Optional description

        Returns:
            True if variable was set successfully
        """
        if not self._is_valid_variable_name(name):
            logger.warning(f"Invalid variable name: {name}")
            return False

        try:
            # Parse value with type inference
            parsed_value, var_type = TypeInferenceEngine.infer_type_and_parse(raw_value)

            with self._lock:
                current_time = time.time()

                # Check if we're at the limit (but allow updates to existing variables)
                if (
                    len(self.variables) >= self.max_variables
                    and name not in self.variables
                ):
                    logger.warning(f"Variable limit reached ({self.max_variables})")
                    return False

                # Create or update variable
                if name in self.variables:
                    # Update existing
                    existing = self.variables[name]
                    existing.value = parsed_value
                    existing.var_type = var_type
                    existing.last_modified = current_time
                    if description is not None:
                        existing.description = description
                else:
                    # Create new
                    self.variables[name] = Variable(
                        name=name,
                        value=parsed_value,
                        var_type=var_type,
                        created_at=current_time,
                        last_modified=current_time,
                        description=description,
                    )

                logger.debug(
                    f"Variable set: {name} = {parsed_value} ({var_type.value})"
                )
                return True

        except Exception as e:
            logger.error(f"Failed to set variable {name}: {e}")
            return False

    def get_variable(self, name: str) -> Optional[Variable]:
        """
        Get a variable by name.

        Args:
            name: Variable name

        Returns:
            Variable object or None if not found
        """
        with self._lock:
            return self.variables.get(name)

    def get_variable_value(self, name: str) -> Optional[Any]:
        """
        Get a variable's value directly.

        Args:
            name: Variable name

        Returns:
            Variable value or None if not found
        """
        variable = self.get_variable(name)
        return variable.value if variable else None

    def unset_variable(self, name: str) -> bool:
        """
        Remove a variable from the store.

        Args:
            name: Variable name to remove

        Returns:
            True if variable was removed, False if not found
        """
        with self._lock:
            if name in self.variables:
                del self.variables[name]
                logger.debug(f"Variable unset: {name}")
                return True
            return False

    def list_variables(self) -> List[Variable]:
        """
        Get a list of all variables sorted by name.

        Returns:
            List of Variable objects
        """
        with self._lock:
            return sorted(self.variables.values(), key=lambda v: v.name)

    def clear_variables(self) -> int:
        """
        Clear all variables.

        Returns:
            Number of variables that were cleared
        """
        with self._lock:
            count = len(self.variables)
            self.variables.clear()
            logger.debug(f"Cleared {count} variables")
            return count

    def get_variable_names(self) -> List[str]:
        """
        Get list of all variable names for completion.

        Returns:
            List of variable names
        """
        with self._lock:
            return sorted(self.variables.keys())

    def substitute_variables(self, command_line: str) -> str:
        """
        Substitute variables in a command line with their values.

        Args:
            command_line: Command line containing $variable patterns

        Returns:
            Command line with variables substituted
        """
        if "$" not in command_line:
            return command_line

        def substitute_match(match):
            var_name = match.group(1)
            variable = self.get_variable(var_name)

            if variable is None:
                logger.warning(f"Undefined variable in substitution: {var_name}")
                return match.group(0)  # Return original $var_name

            # Handle different types appropriately for command line
            if variable.var_type == VariableType.ARRAY:
                # Expand arrays as space-separated values
                return " ".join(str(item) for item in variable.value)
            elif variable.var_type == VariableType.OBJECT:
                # JSON encode objects
                return json.dumps(variable.value, separators=(",", ":"))
            elif variable.var_type == VariableType.STRING:
                # Quote strings if they contain spaces
                value_str = str(variable.value)
                if " " in value_str or '"' in value_str:
                    # Escape quotes and wrap in quotes
                    return f'"{value_str.replace('"', '\\"')}"'
                return value_str
            else:
                return str(variable.value)

        try:
            result = self._substitution_pattern.sub(substitute_match, command_line)
            logger.debug(f"Variable substitution: '{command_line}' -> '{result}'")
            return result
        except Exception as e:
            logger.error(f"Error in variable substitution: {e}")
            return command_line  # Return original on error

    def get_completions_for_prefix(self, prefix: str) -> List[str]:
        """
        Get variable names that start with the given prefix.

        Args:
            prefix: Prefix to match (without $)

        Returns:
            List of matching variable names
        """
        with self._lock:
            return [name for name in self.variables.keys() if name.startswith(prefix)]

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about the variable store.

        Returns:
            Dictionary with store statistics
        """
        with self._lock:
            if not self.variables:
                return {
                    "total_variables": 0,
                    "types_distribution": {},
                    "memory_usage_estimate": 0,
                    "max_variables": self.max_variables,
                }

            type_counts = {}
            total_size = 0

            for var in self.variables.values():
                var_type_str = var.var_type.value
                type_counts[var_type_str] = type_counts.get(var_type_str, 0) + 1

                # Rough memory estimate
                if var.var_type == VariableType.STRING:
                    total_size += len(str(var.value))
                elif var.var_type in (VariableType.ARRAY, VariableType.OBJECT):
                    total_size += len(json.dumps(var.value))
                else:
                    total_size += 50  # Rough estimate for numbers/booleans

            return {
                "total_variables": len(self.variables),
                "types_distribution": type_counts,
                "memory_usage_estimate": total_size,
                "max_variables": self.max_variables,
                "usage_percentage": (len(self.variables) / self.max_variables) * 100,
            }

    def to_dict(self) -> Dict[str, Any]:
        """Convert variable store to dictionary for serialization."""
        with self._lock:
            return {
                "variables": {
                    name: var.to_dict() for name, var in self.variables.items()
                },
                "max_variables": self.max_variables,
                "version": "1.0",
            }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "VariableStore":
        """Create variable store from dictionary."""
        store = cls(max_variables=data.get("max_variables", 100))

        variables_data = data.get("variables", {})
        for name, var_data in variables_data.items():
            try:
                variable = Variable.from_dict(var_data)
                store.variables[name] = variable
            except Exception as e:
                logger.warning(f"Failed to load variable {name}: {e}")

        return store

    @staticmethod
    def _is_valid_variable_name(name: str) -> bool:
        """
        Check if a variable name is valid.

        Args:
            name: Variable name to validate

        Returns:
            True if name is a valid identifier
        """
        if not name or not isinstance(name, str):
            return False

        # Must start with letter or underscore
        if not (name[0].isalpha() or name[0] == "_"):
            return False

        # Rest must be alphanumeric or underscore
        return all(c.isalnum() or c == "_" for c in name[1:])
