"""
Installation Runners
====================

Installation execution runners for different languages and package managers.
Handles the actual execution of installation, upgrade, and uninstall operations.
"""

import subprocess
import logging
from typing import Dict, Any, List, Optional, Union
from abc import ABC, abstractmethod

from .setup_manager import InstallationConfig, InstallationResult, InstallationMethod
from .system_detection import SystemDetector

logger = logging.getLogger(__name__)


class InstallationRunner(ABC):
    """Abstract base class for installation runners."""
    
    def __init__(self, detector: Optional[SystemDetector] = None):
        """Initialize runner with system detector."""
        self.detector = detector or SystemDetector()
    
    @abstractmethod
    def install(self, config: InstallationConfig) -> InstallationResult:
        """Install package with given configuration."""
        pass
    
    @abstractmethod
    def upgrade(self, config: InstallationConfig) -> InstallationResult:
        """Upgrade package with given configuration."""
        pass
    
    @abstractmethod
    def uninstall(self, config: InstallationConfig) -> InstallationResult:
        """Uninstall package with given configuration."""
        pass
    
    def validate_environment(self) -> bool:
        """Validate that environment supports this runner."""
        return True


class PythonInstallationRunner(InstallationRunner):
    """Installation runner for Python packages."""
    
    def validate_environment(self) -> bool:
        """Validate Python environment."""
        python_env = self.detector.detect_python_environment()
        return python_env['python3_available'] and python_env['pip_available']
    
    def install(self, config: InstallationConfig) -> InstallationResult:
        """Install Python package."""
        if config.method == InstallationMethod.PIPX:
            return self._pipx_install(config)
        elif config.method == InstallationMethod.PIP_DEV:
            return self._pip_dev_install(config)
        else:  # PIP
            return self._pip_install(config)
    
    def _pip_install(self, config: InstallationConfig) -> InstallationResult:
        """Install using pip."""
        cmd = ['pip', 'install']
        
        if config.user_install:
            cmd.append('--user')
        
        # Add extras
        if config.extras:
            package_spec = f"{config.package_name}[{','.join(config.extras)}]"
        else:
            package_spec = config.package_name
        
        cmd.append(package_spec)
        
        return self._execute_command(cmd, config.method)
    
    def _pipx_install(self, config: InstallationConfig) -> InstallationResult:
        """Install using pipx."""
        cmd = ['pipx', 'install']
        
        if config.extras:
            package_spec = f"{config.package_name}[{','.join(config.extras)}]"
        else:
            package_spec = config.package_name
        
        cmd.append(package_spec)
        
        return self._execute_command(cmd, config.method)
    
    def _pip_dev_install(self, config: InstallationConfig) -> InstallationResult:
        """Install in development mode."""
        cmd = ['pip', 'install', '-e']
        
        if config.extras:
            package_spec = f".[{','.join(config.extras)}]"
        else:
            package_spec = "."
        
        cmd.append(package_spec)
        
        return self._execute_command(cmd, config.method)
    
    def upgrade(self, config: InstallationConfig) -> InstallationResult:
        """Upgrade Python package."""
        if config.method == InstallationMethod.PIPX:
            cmd = ['pipx', 'upgrade', config.package_name]
        else:  # PIP
            cmd = ['pip', 'install', '--upgrade', config.package_name]
            if config.user_install:
                cmd.insert(-1, '--user')
        
        return self._execute_command(cmd, config.method)
    
    def uninstall(self, config: InstallationConfig) -> InstallationResult:
        """Uninstall Python package."""
        if config.method == InstallationMethod.PIPX:
            cmd = ['pipx', 'uninstall', config.package_name]
        else:  # PIP
            cmd = ['pip', 'uninstall', '-y', config.package_name]
        
        return self._execute_command(cmd, config.method)
    
    def _execute_command(self, cmd: List[str], method: InstallationMethod) -> InstallationResult:
        """Execute command and return result."""
        try:
            process = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            return InstallationResult(
                success=process.returncode == 0,
                method_used=method,
                stdout=process.stdout,
                stderr=process.stderr,
                return_code=process.returncode,
                error_message=None if process.returncode == 0 else f"Command failed: {' '.join(cmd)}"
            )
            
        except Exception as e:
            return InstallationResult(
                success=False,
                method_used=method,
                error_message=f"Execution error: {str(e)}"
            )


class NodeJSInstallationRunner(InstallationRunner):
    """Installation runner for Node.js packages."""
    
    def validate_environment(self) -> bool:
        """Validate Node.js environment."""
        nodejs_env = self.detector.detect_nodejs_environment()
        return nodejs_env['node_available'] and nodejs_env['npm_available']
    
    def install(self, config: InstallationConfig) -> InstallationResult:
        """Install Node.js package."""
        if config.method == InstallationMethod.YARN:
            return self._yarn_install(config)
        elif config.method == InstallationMethod.PNPM:
            return self._pnpm_install(config)
        elif config.method == InstallationMethod.NPM_GLOBAL:
            return self._npm_global_install(config)
        else:  # NPM
            return self._npm_install(config)
    
    def _npm_install(self, config: InstallationConfig) -> InstallationResult:
        """Install using npm."""
        cmd = ['npm', 'install', config.package_name]
        return self._execute_command(cmd, config.method)
    
    def _npm_global_install(self, config: InstallationConfig) -> InstallationResult:
        """Install using npm globally."""
        cmd = ['npm', 'install', '-g', config.package_name]
        return self._execute_command(cmd, config.method)
    
    def _yarn_install(self, config: InstallationConfig) -> InstallationResult:
        """Install using yarn."""
        if config.global_install:
            cmd = ['yarn', 'global', 'add', config.package_name]
        else:
            cmd = ['yarn', 'add', config.package_name]
        return self._execute_command(cmd, config.method)
    
    def _pnpm_install(self, config: InstallationConfig) -> InstallationResult:
        """Install using pnpm."""
        if config.global_install:
            cmd = ['pnpm', 'add', '-g', config.package_name]
        else:
            cmd = ['pnpm', 'add', config.package_name]
        return self._execute_command(cmd, config.method)
    
    def upgrade(self, config: InstallationConfig) -> InstallationResult:
        """Upgrade Node.js package."""
        if config.method == InstallationMethod.YARN:
            cmd = ['yarn', 'upgrade', config.package_name]
        elif config.method == InstallationMethod.PNPM:
            cmd = ['pnpm', 'update', config.package_name]
        else:  # NPM
            cmd = ['npm', 'update', config.package_name]
        
        return self._execute_command(cmd, config.method)
    
    def uninstall(self, config: InstallationConfig) -> InstallationResult:
        """Uninstall Node.js package."""
        if config.method == InstallationMethod.YARN:
            cmd = ['yarn', 'remove', config.package_name]
        elif config.method == InstallationMethod.PNPM:
            cmd = ['pnpm', 'remove', config.package_name]
        else:  # NPM
            cmd = ['npm', 'uninstall', config.package_name]
        
        return self._execute_command(cmd, config.method)
    
    def _execute_command(self, cmd: List[str], method: InstallationMethod) -> InstallationResult:
        """Execute command and return result."""
        try:
            process = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            return InstallationResult(
                success=process.returncode == 0,
                method_used=method,
                stdout=process.stdout,
                stderr=process.stderr,
                return_code=process.returncode,
                error_message=None if process.returncode == 0 else f"Command failed: {' '.join(cmd)}"
            )
            
        except Exception as e:
            return InstallationResult(
                success=False,
                method_used=method,
                error_message=f"Execution error: {str(e)}"
            )


class TypeScriptInstallationRunner(NodeJSInstallationRunner):
    """Installation runner for TypeScript packages (extends Node.js)."""
    
    def install(self, config: InstallationConfig) -> InstallationResult:
        """Install TypeScript package with build step."""
        # First try to build if tsconfig.json exists
        self._build_typescript()
        
        # Then install as Node.js package
        return super().install(config)
    
    def _build_typescript(self) -> bool:
        """Build TypeScript project if needed."""
        try:
            from pathlib import Path
            if Path('tsconfig.json').exists():
                # Try to build with tsc
                result = subprocess.run(
                    ['npx', 'tsc'],
                    capture_output=True,
                    text=True,
                    timeout=120
                )
                return result.returncode == 0
        except Exception:
            pass
        return True


class RustInstallationRunner(InstallationRunner):
    """Installation runner for Rust packages."""
    
    def validate_environment(self) -> bool:
        """Validate Rust environment."""
        rust_env = self.detector.detect_rust_environment()
        return rust_env['rustc_available'] and rust_env['cargo_available']
    
    def install(self, config: InstallationConfig) -> InstallationResult:
        """Install Rust package."""
        if config.development_mode:
            return self._cargo_build_install(config)
        else:
            return self._cargo_install(config)
    
    def _cargo_install(self, config: InstallationConfig) -> InstallationResult:
        """Install using cargo install."""
        cmd = ['cargo', 'install', config.package_name]
        return self._execute_command(cmd, config.method)
    
    def _cargo_build_install(self, config: InstallationConfig) -> InstallationResult:
        """Build and install from source."""
        # First build
        build_result = self._execute_command(['cargo', 'build', '--release'], config.method)
        if not build_result.success:
            return build_result
        
        # Then install from current directory
        cmd = ['cargo', 'install', '--path', '.']
        return self._execute_command(cmd, config.method)
    
    def upgrade(self, config: InstallationConfig) -> InstallationResult:
        """Upgrade Rust package."""
        cmd = ['cargo', 'install', '--force', config.package_name]
        return self._execute_command(cmd, config.method)
    
    def uninstall(self, config: InstallationConfig) -> InstallationResult:
        """Uninstall Rust package."""
        cmd = ['cargo', 'uninstall', config.package_name]
        return self._execute_command(cmd, config.method)
    
    def _execute_command(self, cmd: List[str], method: InstallationMethod) -> InstallationResult:
        """Execute command and return result."""
        try:
            process = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=600  # Rust builds can take longer
            )
            
            return InstallationResult(
                success=process.returncode == 0,
                method_used=method,
                stdout=process.stdout,
                stderr=process.stderr,
                return_code=process.returncode,
                error_message=None if process.returncode == 0 else f"Command failed: {' '.join(cmd)}"
            )
            
        except Exception as e:
            return InstallationResult(
                success=False,
                method_used=method,
                error_message=f"Execution error: {str(e)}"
            )