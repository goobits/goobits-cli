"""
Setup Framework
===============

Public interface for the Setup framework extracted from setup templates.
Provides installation, upgrade, and dependency management systems with cross-platform
support for all languages.
"""

from .setup_framework import SetupFramework, SetupConfig
from .setup_manager import SetupManager, InstallationMethod
from .system_detection import SystemDetector, Platform, PackageManagerRegistry, SystemPackageManager
from .language_adapters import (
    PythonSetupAdapter,
    NodeJSSetupAdapter, 
    TypeScriptSetupAdapter,
    RustSetupAdapter
)
from .installation_runners import (
    InstallationRunner,
    PythonInstallationRunner,
    NodeJSInstallationRunner,
    TypeScriptInstallationRunner,
    RustInstallationRunner
)

__all__ = [
    'SetupFramework',
    'SetupConfig',
    'SetupManager', 
    'InstallationMethod',
    'SystemPackageManager',
    'SystemDetector',
    'Platform',
    'PackageManagerRegistry',
    'PythonSetupAdapter',
    'NodeJSSetupAdapter',
    'TypeScriptSetupAdapter', 
    'RustSetupAdapter',
    'InstallationRunner',
    'PythonInstallationRunner',
    'NodeJSInstallationRunner',
    'TypeScriptInstallationRunner',
    'RustInstallationRunner'
]