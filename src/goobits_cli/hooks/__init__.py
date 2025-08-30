"""
Hook Framework
=============

Public interface for the Hook framework extracted from hook_system.j2 template.
Provides hook loading, discovery, execution, and template generation for all languages.
"""

from .hook_framework import HookFramework, HookConfig, HookDefinition
from .discovery_engine import DiscoveryEngine, HookLoader, ModuleResolver
from .execution_pipeline import ExecutionPipeline, HookExecutor, ErrorHandler
from .template_generator import TemplateGenerator, HookTemplate
from .language_adapters import (
    PythonHookAdapter,
    NodeJSHookAdapter,
    TypeScriptHookAdapter,
    RustHookAdapter
)

__all__ = [
    'HookFramework',
    'HookConfig',
    'HookDefinition',
    'DiscoveryEngine',
    'HookLoader',
    'ModuleResolver',
    'ExecutionPipeline', 
    'HookExecutor',
    'ErrorHandler',
    'TemplateGenerator',
    'HookTemplate',
    'PythonHookAdapter',
    'NodeJSHookAdapter',
    'TypeScriptHookAdapter',
    'RustHookAdapter'
]