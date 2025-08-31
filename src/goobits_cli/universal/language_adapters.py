"""
Language Adapters Base Classes
===============================

Base classes for language-specific code generation adapters.
Provides common interfaces for generating equivalent functionality across languages.
"""

from typing import Dict, Any
from abc import ABC, abstractmethod


class LanguageAdapter(ABC):
    """Base class for language-specific code generation adapters."""
    
    @abstractmethod
    def generate_imports(self, config: Dict[str, Any]) -> str:
        """Generate language-specific imports."""
        pass
    
    def generate_header_comment(self, config: Dict[str, Any]) -> str:
        """Generate header comment for generated code."""
        project_name = config.get('project', {}).get('name', 'Unknown Project')
        return f"""/**
 * Generated code for {project_name}
 * Created by Goobits CLI Framework
 */"""
    
    def generate_footer_comment(self, config: Dict[str, Any]) -> str:
        """Generate footer comment for generated code."""
        return ""
    
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """Validate adapter configuration."""
        return True
    
    def get_file_extension(self) -> str:
        """Get file extension for this language."""
        return ".txt"
    
    def format_code(self, code: str) -> str:
        """Format generated code according to language conventions."""
        return code.strip()


class PythonLanguageAdapter(LanguageAdapter):
    """Base Python language adapter."""
    
    def generate_header_comment(self, config: Dict[str, Any]) -> str:
        """Generate Python header comment."""
        project_name = config.get('project', {}).get('name', 'Unknown Project')
        return f'''"""
Generated code for {project_name}
Created by Goobits CLI Framework
"""'''
    
    def get_file_extension(self) -> str:
        """Get Python file extension."""
        return ".py"


class JavaScriptLanguageAdapter(LanguageAdapter):
    """Base JavaScript/Node.js language adapter."""
    
    def get_file_extension(self) -> str:
        """Get JavaScript file extension."""
        return ".js"


class TypeScriptLanguageAdapter(LanguageAdapter):
    """Base TypeScript language adapter."""
    
    def get_file_extension(self) -> str:
        """Get TypeScript file extension."""
        return ".ts"


class RustLanguageAdapter(LanguageAdapter):
    """Base Rust language adapter."""
    
    def get_file_extension(self) -> str:
        """Get Rust file extension."""
        return ".rs"
    
    def generate_header_comment(self, config: Dict[str, Any]) -> str:
        """Generate Rust header comment."""
        project_name = config.get('project', {}).get('name', 'Unknown Project')
        return f"""//! Generated code for {project_name}
//! Created by Goobits CLI Framework"""