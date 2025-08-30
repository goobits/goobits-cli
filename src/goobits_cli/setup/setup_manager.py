"""
Setup Manager
=============

Core setup and installation management system extracted from setup templates.
Provides installation, upgrade, and dependency management with cross-platform support.
"""

import os
import sys
import subprocess
import shutil
from typing import Dict, List, Optional, Any, Union
from enum import Enum
from dataclasses import dataclass, field
from pathlib import Path

from .system_detection import SystemDetector, Platform, PackageManagerRegistry


class InstallationMethod(Enum):
    """Installation methods for different languages."""
    # Python
    PIP = "pip"
    PIPX = "pipx"
    PIP_DEV = "pip_dev"
    
    # Node.js/TypeScript
    NPM = "npm"
    YARN = "yarn"
    PNPM = "pnpm"
    NPM_GLOBAL = "npm_global"
    
    # Rust
    CARGO = "cargo"
    CARGO_INSTALL = "cargo_install"
    
    # System
    SYSTEM = "system"
    MANUAL = "manual"


@dataclass
class InstallationConfig:
    """Configuration for installation process."""
    method: InstallationMethod
    package_name: str
    command_name: str
    development_mode: bool = False
    user_install: bool = True
    global_install: bool = False
    extras: List[str] = field(default_factory=list)
    system_packages: List[str] = field(default_factory=list)
    environment_vars: Dict[str, str] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'method': self.method.value,
            'package_name': self.package_name,
            'command_name': self.command_name,
            'development_mode': self.development_mode,
            'user_install': self.user_install,
            'global_install': self.global_install,
            'extras': self.extras,
            'system_packages': self.system_packages,
            'environment_vars': self.environment_vars
        }


@dataclass
class InstallationResult:
    """Result of installation operation."""
    success: bool
    method_used: InstallationMethod
    stdout: str = ""
    stderr: str = ""
    return_code: int = 0
    packages_installed: List[str] = field(default_factory=list)
    error_message: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'success': self.success,
            'method_used': self.method_used.value,
            'stdout': self.stdout,
            'stderr': self.stderr,
            'return_code': self.return_code,
            'packages_installed': self.packages_installed,
            'error_message': self.error_message
        }


class SetupManager:
    """
    Core setup manager for installation and dependency management.
    
    Handles installation workflows across Python, Node.js, TypeScript, and Rust
    with platform-specific optimizations and fallback strategies.
    """
    
    def __init__(self, system_detector: Optional[SystemDetector] = None):
        """
        Initialize setup manager.
        
        Args:
            system_detector: System detection instance
        """
        self.detector = system_detector or SystemDetector()
        self.package_registry = PackageManagerRegistry(self.detector)
        
        # Environment information
        self.python_env = self.detector.detect_python_environment()
        self.nodejs_env = self.detector.detect_nodejs_environment()
        self.rust_env = self.detector.detect_rust_environment()
    
    def validate_environment(self, language: str) -> Dict[str, Any]:
        """
        Validate environment for specific language.
        
        Args:
            language: Target language (python, nodejs, typescript, rust)
            
        Returns:
            Validation results
        """
        validation = {
            'valid': False,
            'language': language,
            'missing_tools': [],
            'recommendations': [],
            'environment_info': {}
        }
        
        if language == 'python':
            validation['environment_info'] = self.python_env
            
            if not self.python_env['python3_available']:
                validation['missing_tools'].append('python3')
                validation['recommendations'].append('Install Python 3.8+ from python.org')
            
            if not self.python_env['pip_available']:
                validation['missing_tools'].append('pip')
                validation['recommendations'].append('Install pip package manager')
            
            validation['valid'] = (
                self.python_env['python3_available'] and 
                self.python_env['pip_available']
            )
            
        elif language in ['nodejs', 'typescript']:
            validation['environment_info'] = self.nodejs_env
            
            if not self.nodejs_env['node_available']:
                validation['missing_tools'].append('node')
                validation['recommendations'].append('Install Node.js from nodejs.org')
            
            if not self.nodejs_env['npm_available']:
                validation['missing_tools'].append('npm')
                validation['recommendations'].append('Install npm (usually comes with Node.js)')
            
            validation['valid'] = (
                self.nodejs_env['node_available'] and 
                self.nodejs_env['npm_available']
            )
            
            if language == 'typescript' and validation['valid']:
                # Additional TypeScript checks could go here
                pass
                
        elif language == 'rust':
            validation['environment_info'] = self.rust_env
            
            if not self.rust_env['rustc_available']:
                validation['missing_tools'].append('rustc')
                validation['recommendations'].append('Install Rust from rustup.rs')
            
            if not self.rust_env['cargo_available']:
                validation['missing_tools'].append('cargo')
                validation['recommendations'].append('Install Cargo (usually comes with Rust)')
            
            validation['valid'] = (
                self.rust_env['rustc_available'] and 
                self.rust_env['cargo_available']
            )
        
        return validation
    
    def determine_installation_method(self, language: str, config: Dict[str, Any]) -> InstallationMethod:
        """
        Determine best installation method for language and config.
        
        Args:
            language: Target language
            config: Installation configuration
            
        Returns:
            Recommended installation method
        """
        if language == 'python':
            # Check if development mode
            if config.get('development_mode', False):
                return InstallationMethod.PIP_DEV
            
            # Prefer pipx if available for CLI tools
            if self.python_env['pipx_available']:
                return InstallationMethod.PIPX
            
            # Fallback to pip
            return InstallationMethod.PIP
            
        elif language in ['nodejs', 'typescript']:
            # Check for global installation preference
            if config.get('global_install', False):
                return InstallationMethod.NPM_GLOBAL
            
            # Prefer yarn if available
            if self.nodejs_env['yarn_available']:
                return InstallationMethod.YARN
            
            # Use pnpm if available and preferred
            if self.nodejs_env['pnpm_available'] and config.get('prefer_pnpm', False):
                return InstallationMethod.PNPM
            
            # Default to npm
            return InstallationMethod.NPM
            
        elif language == 'rust':
            # For Rust CLI tools, prefer cargo install
            return InstallationMethod.CARGO_INSTALL
        
        return InstallationMethod.MANUAL
    
    def install_system_dependencies(self, packages: List[str]) -> bool:
        """
        Install system-level dependencies.
        
        Args:
            packages: List of system packages to install
            
        Returns:
            True if successful
        """
        if not packages:
            return True
        
        return self.package_registry.install_packages(packages)
    
    def install_package(self, config: InstallationConfig) -> InstallationResult:
        """
        Install a package using specified configuration.
        
        Args:
            config: Installation configuration
            
        Returns:
            Installation result
        """
        result = InstallationResult(
            success=False,
            method_used=config.method
        )
        
        try:
            # Install system dependencies first
            if config.system_packages:
                if not self.install_system_dependencies(config.system_packages):
                    result.error_message = "Failed to install system dependencies"
                    return result
            
            # Set environment variables
            env = os.environ.copy()
            env.update(config.environment_vars)
            
            # Build command based on method
            cmd = self._build_install_command(config)
            if not cmd:
                result.error_message = f"Unsupported installation method: {config.method}"
                return result
            
            # Execute installation
            process = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                env=env,
                timeout=300  # 5 minute timeout
            )
            
            result.stdout = process.stdout
            result.stderr = process.stderr
            result.return_code = process.returncode
            result.success = process.returncode == 0
            
            if not result.success:
                result.error_message = f"Installation failed with code {process.returncode}"
            else:
                result.packages_installed = [config.package_name]
            
        except subprocess.TimeoutExpired:
            result.error_message = "Installation timed out"
        except Exception as e:
            result.error_message = f"Installation error: {str(e)}"
        
        return result
    
    def _build_install_command(self, config: InstallationConfig) -> Optional[List[str]]:
        """Build installation command based on method and config."""
        method = config.method
        
        if method == InstallationMethod.PIP:
            cmd = ['pip', 'install']
            if config.user_install:
                cmd.append('--user')
            if config.extras:
                package_spec = f"{config.package_name}[{','.join(config.extras)}]"
            else:
                package_spec = config.package_name
            cmd.append(package_spec)
            return cmd
            
        elif method == InstallationMethod.PIPX:
            cmd = ['pipx', 'install']
            if config.extras:
                package_spec = f"{config.package_name}[{','.join(config.extras)}]"
            else:
                package_spec = config.package_name
            cmd.append(package_spec)
            return cmd
            
        elif method == InstallationMethod.PIP_DEV:
            cmd = ['pip', 'install', '-e']
            if config.extras:
                package_spec = f".[{','.join(config.extras)}]"
            else:
                package_spec = "."
            cmd.append(package_spec)
            return cmd
            
        elif method == InstallationMethod.NPM:
            cmd = ['npm', 'install']
            if config.global_install:
                cmd.append('-g')
            cmd.append(config.package_name)
            return cmd
            
        elif method == InstallationMethod.NPM_GLOBAL:
            return ['npm', 'install', '-g', config.package_name]
            
        elif method == InstallationMethod.YARN:
            cmd = ['yarn']
            if config.global_install:
                cmd.extend(['global', 'add'])
            else:
                cmd.append('add')
            cmd.append(config.package_name)
            return cmd
            
        elif method == InstallationMethod.PNPM:
            cmd = ['pnpm']
            if config.global_install:
                cmd.extend(['add', '-g'])
            else:
                cmd.append('add')
            cmd.append(config.package_name)
            return cmd
            
        elif method == InstallationMethod.CARGO_INSTALL:
            return ['cargo', 'install', config.package_name]
            
        elif method == InstallationMethod.CARGO:
            return ['cargo', 'build', '--release']
        
        return None
    
    def upgrade_package(self, config: InstallationConfig) -> InstallationResult:
        """
        Upgrade a package.
        
        Args:
            config: Installation configuration
            
        Returns:
            Upgrade result
        """
        result = InstallationResult(
            success=False,
            method_used=config.method
        )
        
        try:
            cmd = self._build_upgrade_command(config)
            if not cmd:
                result.error_message = f"Unsupported upgrade method: {config.method}"
                return result
            
            process = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            result.stdout = process.stdout
            result.stderr = process.stderr
            result.return_code = process.returncode
            result.success = process.returncode == 0
            
            if not result.success:
                result.error_message = f"Upgrade failed with code {process.returncode}"
            
        except Exception as e:
            result.error_message = f"Upgrade error: {str(e)}"
        
        return result
    
    def _build_upgrade_command(self, config: InstallationConfig) -> Optional[List[str]]:
        """Build upgrade command based on method."""
        method = config.method
        
        if method == InstallationMethod.PIP:
            return ['pip', 'install', '--upgrade', config.package_name]
        elif method == InstallationMethod.PIPX:
            return ['pipx', 'upgrade', config.package_name]
        elif method == InstallationMethod.NPM:
            return ['npm', 'update', config.package_name]
        elif method == InstallationMethod.NPM_GLOBAL:
            return ['npm', 'update', '-g', config.package_name]
        elif method == InstallationMethod.YARN:
            return ['yarn', 'upgrade', config.package_name]
        elif method == InstallationMethod.CARGO_INSTALL:
            return ['cargo', 'install', '--force', config.package_name]
        
        return None
    
    def uninstall_package(self, config: InstallationConfig) -> InstallationResult:
        """
        Uninstall a package.
        
        Args:
            config: Installation configuration
            
        Returns:
            Uninstall result
        """
        result = InstallationResult(
            success=False,
            method_used=config.method
        )
        
        try:
            cmd = self._build_uninstall_command(config)
            if not cmd:
                result.error_message = f"Unsupported uninstall method: {config.method}"
                return result
            
            process = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            result.stdout = process.stdout
            result.stderr = process.stderr
            result.return_code = process.returncode
            result.success = process.returncode == 0
            
            if not result.success:
                result.error_message = f"Uninstall failed with code {process.returncode}"
            
        except Exception as e:
            result.error_message = f"Uninstall error: {str(e)}"
        
        return result
    
    def _build_uninstall_command(self, config: InstallationConfig) -> Optional[List[str]]:
        """Build uninstall command based on method."""
        method = config.method
        
        if method == InstallationMethod.PIP:
            return ['pip', 'uninstall', '-y', config.package_name]
        elif method == InstallationMethod.PIPX:
            return ['pipx', 'uninstall', config.package_name]
        elif method == InstallationMethod.NPM:
            return ['npm', 'uninstall', config.package_name]
        elif method == InstallationMethod.NPM_GLOBAL:
            return ['npm', 'uninstall', '-g', config.package_name]
        elif method == InstallationMethod.YARN:
            return ['yarn', 'remove', config.package_name]
        elif method == InstallationMethod.CARGO_INSTALL:
            return ['cargo', 'uninstall', config.package_name]
        
        return None
    
    def get_manager_info(self) -> Dict[str, Any]:
        """Get setup manager information and capabilities."""
        return {
            'platform': self.detector.get_platform().value,
            'available_methods': {
                'python': [
                    InstallationMethod.PIP.value if self.python_env['pip_available'] else None,
                    InstallationMethod.PIPX.value if self.python_env['pipx_available'] else None,
                    InstallationMethod.PIP_DEV.value if self.python_env['pip_available'] else None
                ],
                'nodejs': [
                    InstallationMethod.NPM.value if self.nodejs_env['npm_available'] else None,
                    InstallationMethod.YARN.value if self.nodejs_env['yarn_available'] else None,
                    InstallationMethod.PNPM.value if self.nodejs_env['pnpm_available'] else None
                ],
                'rust': [
                    InstallationMethod.CARGO.value if self.rust_env['cargo_available'] else None,
                    InstallationMethod.CARGO_INSTALL.value if self.rust_env['cargo_available'] else None
                ]
            },
            'system_info': self.detector.get_system_info(),
            'package_managers': [
                pm.to_dict() for pm in self.detector.get_available_package_managers()
            ]
        }