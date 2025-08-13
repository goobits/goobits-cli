"""

Universal completion system for Goobits CLI Framework.



This module provides dynamic, context-aware completion capabilities

that work across all supported languages (Python, Node.js, TypeScript, Rust).

"""



from .registry import DynamicCompletionRegistry, CompletionProvider, CompletionContext

from .providers import (

    FilePathCompletionProvider,

    EnvironmentVariableProvider, 

    ConfigKeyProvider,

    HistoryProvider

)



__all__ = [

    'DynamicCompletionRegistry',

    'CompletionProvider', 

    'CompletionContext',

    'FilePathCompletionProvider',

    'EnvironmentVariableProvider',

    'ConfigKeyProvider',

    'HistoryProvider'

]