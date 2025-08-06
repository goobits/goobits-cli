"""
Goobits CLI Shared Components

This package contains shared validation logic and components used across
all language generators.
"""

from .validation_framework import (
    ValidationContext,
    ValidationResult,
    ValidationMode,
    ValidationSeverity,
    ValidationMessage,
    ValidationRegistry,
    ValidationRunner,
    BaseValidator,
    validate_config,
    create_default_runner
)

from .validators import (
    CommandValidator,
    ArgumentValidator,
    HookValidator,
    OptionValidator,
    ErrorCodeValidator,
    TypeValidator,
    ConfigValidator,
    CompletionValidator
)

# Import documentation generator components
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent / 'templates'))

try:
    from ..templates.doc_generator import (
        DocumentationGenerator,
        DocumentationType,
        OutputFormat,
        DocumentationContext,
        DocumentationSection,
        LanguageAdapter,
        PythonAdapter,
        NodeJSAdapter,
        TypeScriptAdapter,
        RustAdapter,
        generate_documentation,
        create_readme_file
    )
    _doc_imports_available = True
except ImportError:
    _doc_imports_available = False

__all__ = [
    # Framework
    'ValidationContext',
    'ValidationResult', 
    'ValidationMode',
    'ValidationSeverity',
    'ValidationMessage',
    'ValidationRegistry',
    'ValidationRunner',
    'BaseValidator',
    'validate_config',
    'create_default_runner',
    
    # Validators
    'CommandValidator',
    'ArgumentValidator', 
    'HookValidator',
    'OptionValidator',
    'ErrorCodeValidator',
    'TypeValidator',
    'ConfigValidator',
    'CompletionValidator'
]

# Add documentation exports if available
if _doc_imports_available:
    __all__.extend([
        # Documentation Generator
        'DocumentationGenerator',
        'DocumentationType',
        'OutputFormat',
        'DocumentationContext',
        'DocumentationSection',
        'LanguageAdapter',
        'PythonAdapter',
        'NodeJSAdapter',
        'TypeScriptAdapter',
        'RustAdapter',
        'generate_documentation',
        'create_readme_file'
    ])