# Advanced Interactive Mode - Core Data Structures

Based on deep analysis of the existing codebase patterns, here are the core data structures needed for implementation:

## Core Data Structures

### REPLContext
```python
from dataclasses import dataclass
from typing import Dict, List, Optional, Any, Union
from datetime import datetime

@dataclass
class REPLContext:
    """Context information for REPL operations."""
    
    # Current state
    current_command: str = ""
    cursor_position: int = 0
    input_buffer: str = ""
    
    # Command context
    partial_command: Optional[str] = None
    command_args: List[str] = None
    current_option: Optional[str] = None
    
    # History context  
    history_index: int = -1
    last_results: List[Any] = None
    
    # Session context
    session_name: Optional[str] = None
    session_start: datetime = None
    
    # Variable context
    variables: Dict[str, Any] = None
    templates: Dict[str, str] = None

@dataclass  
class REPLState:
    """Complete REPL state for session persistence."""
    
    # Session metadata
    session_name: str
    created_at: datetime
    last_modified: datetime
    version: str = "1.0"
    
    # User state
    variables: Dict[str, Any]
    templates: Dict[str, str]
    configuration: Dict[str, Any]
    
    # History and results
    command_history: List[str]
    execution_results: List[Dict[str, Any]]
    
    # Advanced state (configurable)
    pipeline_cache: Optional[Dict[str, Any]] = None
    completion_cache: Optional[Dict[str, Any]] = None
    debug_snapshots: Optional[List[Dict[str, Any]]] = None
```

### Variable System
```python
from enum import Enum
from typing import Union, get_type_hints

class VariableType(Enum):
    """Supported variable types with validation."""
    STRING = "string"
    NUMBER = "number" 
    BOOLEAN = "boolean"
    ARRAY = "array"
    OBJECT = "object"
    CONFIG = "config"  # Special type for config file objects

@dataclass
class Variable:
    """Typed variable with validation."""
    
    name: str
    value: Any
    type: VariableType
    declared_type: Optional[str] = None  # For optional type declarations
    readonly: bool = False
    source: str = "user"  # user, system, config, pipeline
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
    
    def validate_assignment(self, new_value: Any) -> bool:
        """Validate if new value is compatible with variable type."""
        # Type validation logic based on existing Pydantic patterns
        pass
```

### Pipeline System  
```python
@dataclass
class PipelineStep:
    """Single step in a pipeline."""
    
    command: str
    args: List[str] = None
    options: Dict[str, Any] = None
    expected_input_type: Optional[str] = None
    expected_output_type: Optional[str] = None

@dataclass
class Pipeline:
    """Command pipeline with validation and execution context."""
    
    name: str
    steps: List[PipelineStep]
    created_at: datetime
    
    # Error handling configuration  
    error_strategy: str = "interactive"  # interactive, stop, continue
    retry_attempts: int = 1
    timeout_seconds: Optional[int] = None
    
    # State management
    intermediate_results: List[Any] = None
    current_step: int = 0
    
    def validate(self) -> 'ValidationResult':
        """Validate pipeline before execution."""
        # Pipeline validation logic
        pass
```

### Completion System Extensions
```python  
@dataclass
class CompletionContext:
    """Extended completion context building on existing system."""
    
    # Existing context from current completion system
    command: str
    argument: Optional[str] = None
    option: Optional[str] = None
    
    # Advanced context
    variable_scope: Dict[str, Variable] = None
    pipeline_step: Optional[int] = None
    history_matches: List[str] = None
    
    # User behavior learning
    usage_patterns: Dict[str, int] = None
    recent_completions: List[str] = None

class SmartCompletionEngine:
    """Enhanced completion engine building on existing DynamicCompletionRegistry."""
    
    def __init__(self, registry: 'DynamicCompletionRegistry'):
        self.registry = registry
        self.learning_cache = {}
        self.fuzzy_matcher = FuzzyMatcher()
    
    def complete_with_context(
        self, 
        input_text: str, 
        context: REPLContext, 
        completion_context: CompletionContext
    ) -> List['Completion']:
        """Context-aware completion with learning."""
        # Leverage existing completion providers
        # Add fuzzy matching and learning
        pass
```

## Integration with Existing Systems

### Security Integration
```python
class SecureVariableStore:
    """Secure variable storage building on existing patterns."""
    
    def __init__(self):
        # Use existing input sanitization patterns from subprocess_cache.py
        self.sanitizer = InputSanitizer()
        self.validator = VariableValidator()
    
    def set_variable(self, name: str, value: Any, context: REPLContext) -> bool:
        """Set variable with security validation."""
        # Apply existing security patterns
        sanitized_name = self.sanitizer.sanitize_identifier(name)
        validated_value = self.validator.validate_value(value)
        # Store securely
        pass
```

### Error Handling Integration
```python
class InteractiveModeError(Exception):
    """Interactive mode specific errors building on existing CLIError."""
    
    def __init__(
        self, 
        message: str, 
        error_type: str = "interactive",
        recovery_suggestions: List[str] = None,
        context: REPLContext = None
    ):
        self.error_type = error_type
        self.recovery_suggestions = recovery_suggestions or []
        self.context = context
        super().__init__(message)

class VariableError(InteractiveModeError):
    """Variable-related errors."""
    pass

class PipelineError(InteractiveModeError):  
    """Pipeline execution errors with recovery options."""
    
    def __init__(self, message: str, step: int, partial_results: List[Any] = None):
        self.step = step
        self.partial_results = partial_results
        suggestions = [
            "Retry with corrected syntax",
            "Skip this step and continue", 
            "Debug step execution",
            "Abort pipeline"
        ]
        super().__init__(message, "pipeline", suggestions)
```

### Performance Integration
```python
class InteractivePerformanceManager:
    """Performance management for interactive features."""
    
    def __init__(self):
        # Build on existing performance patterns
        self.cache = SessionSubprocessCache()  # Reuse existing cache
        self.budget = PerformanceBudget(
            startup_ms=50,
            completion_ms=10, 
            command_ms=100
        )
    
    @performance_monitor
    def execute_with_budget(self, operation: str, func: callable) -> Any:
        """Execute operation within performance budget."""
        # Use existing performance monitoring patterns
        pass
```

## Implementation Priority

### Phase 1: Foundation (Week 1)
- `REPLContext` and `REPLState` - session management
- `SmartCompletionEngine` - enhanced completion
- Basic `Variable` system with type inference

### Phase 2: Advanced Features (Week 2)  
- `Pipeline` system with error recovery
- `SecureVariableStore` with validation
- Session persistence and restoration

### Phase 3: Optimization (Week 3)
- Performance budgeting and monitoring
- Learning algorithms for completion
- Advanced debugging integration

### Phase 4: Polish (Week 4)
- Rich output formatting
- Cross-language consistency validation
- Comprehensive testing and documentation

These data structures leverage existing patterns while adding the sophisticated functionality needed for advanced interactive mode.