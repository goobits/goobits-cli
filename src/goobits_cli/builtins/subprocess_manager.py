"""
Subprocess Manager
=================

Platform-specific subprocess execution extracted from builtin_manager.j2.
Provides cross-platform subprocess management for builtin commands.
"""

import subprocess
import sys
import shutil
import os
import platform
from pathlib import Path
from typing import List, Dict, Any, Optional, Union, Tuple
from dataclasses import dataclass
from enum import Enum


class ProcessStatus(Enum):
    """Process execution status."""
    SUCCESS = "success"
    FAILED = "failed"
    TIMEOUT = "timeout"
    INTERRUPTED = "interrupted"


@dataclass
class ProcessResult:
    """Result of subprocess execution."""
    status: ProcessStatus
    return_code: int
    stdout: str
    stderr: str
    command: List[str]
    execution_time: float = 0.0
    
    @property
    def success(self) -> bool:
        """Check if process executed successfully."""
        return self.status == ProcessStatus.SUCCESS and self.return_code == 0
    
    @property
    def failed(self) -> bool:
        """Check if process failed."""
        return not self.success


class PlatformManager:
    """
    Platform-specific utilities extracted from builtin_manager.j2.
    
    Handles cross-platform differences in command execution,
    path handling, and system detection.
    """
    
    @staticmethod
    def get_platform() -> str:
        """Get current platform identifier."""
        return platform.system().lower()
    
    @staticmethod
    def is_windows() -> bool:
        """Check if running on Windows."""
        return platform.system() == 'Windows'
    
    @staticmethod
    def is_macos() -> bool:
        """Check if running on macOS."""
        return platform.system() == 'Darwin'
    
    @staticmethod
    def is_linux() -> bool:
        """Check if running on Linux."""
        return platform.system() == 'Linux'
    
    @staticmethod
    def get_shell() -> str:
        """Get current shell."""
        if PlatformManager.is_windows():
            return os.environ.get('COMSPEC', 'cmd.exe')
        else:
            return os.environ.get('SHELL', '/bin/bash')
    
    @staticmethod
    def get_config_dir(app_name: str) -> Path:
        """Get platform-appropriate configuration directory."""
        if PlatformManager.is_windows():
            base = Path(os.environ.get('APPDATA', Path.home() / 'AppData' / 'Roaming'))
        elif PlatformManager.is_macos():
            base = Path.home() / 'Library' / 'Application Support'
        else:  # Linux and other Unix-like
            base = Path(os.environ.get('XDG_CONFIG_HOME', Path.home() / '.config'))
        
        return base / app_name
    
    @staticmethod
    def get_cache_dir(app_name: str) -> Path:
        """Get platform-appropriate cache directory."""
        if PlatformManager.is_windows():
            base = Path(os.environ.get('LOCALAPPDATA', Path.home() / 'AppData' / 'Local'))
        elif PlatformManager.is_macos():
            base = Path.home() / 'Library' / 'Caches'
        else:  # Linux and other Unix-like
            base = Path(os.environ.get('XDG_CACHE_HOME', Path.home() / '.cache'))
        
        return base / app_name
    
    @staticmethod
    def which(command: str) -> Optional[str]:
        """Find executable in PATH."""
        return shutil.which(command)
    
    @staticmethod
    def is_executable_available(command: str) -> bool:
        """Check if executable is available in PATH."""
        return PlatformManager.which(command) is not None


class SubprocessManager:
    """
    Subprocess execution manager extracted from builtin_manager.j2.
    
    Provides unified interface for running subprocess commands
    with proper error handling, output capture, and platform support.
    """
    
    def __init__(self, timeout: Optional[float] = None, cwd: Optional[Path] = None):
        """Initialize subprocess manager."""
        self.timeout = timeout
        self.cwd = cwd
        self.platform = PlatformManager()
    
    def run(self, command: List[str], 
            capture_output: bool = True,
            text: bool = True, 
            input_data: Optional[str] = None,
            env: Optional[Dict[str, str]] = None,
            shell: bool = False,
            timeout: Optional[float] = None) -> ProcessResult:
        """
        Run a subprocess command with comprehensive error handling.
        
        Args:
            command: Command and arguments to execute
            capture_output: Whether to capture stdout/stderr
            text: Whether to return text (vs bytes)
            input_data: Data to send to stdin
            env: Environment variables
            shell: Whether to use shell execution
            timeout: Command timeout in seconds
            
        Returns:
            ProcessResult with execution details
        """
        import time
        start_time = time.time()
        
        try:
            # Prepare command
            if isinstance(command, str):
                command = [command] if not shell else command
            
            # Use instance timeout if not provided
            if timeout is None:
                timeout = self.timeout
            
            # Execute subprocess
            result = subprocess.run(
                command,
                capture_output=capture_output,
                text=text,
                input=input_data,
                env=env,
                shell=shell,
                timeout=timeout,
                cwd=self.cwd
            )
            
            execution_time = time.time() - start_time
            
            return ProcessResult(
                status=ProcessStatus.SUCCESS if result.returncode == 0 else ProcessStatus.FAILED,
                return_code=result.returncode,
                stdout=result.stdout or "",
                stderr=result.stderr or "",
                command=command,
                execution_time=execution_time
            )
            
        except subprocess.TimeoutExpired as e:
            execution_time = time.time() - start_time
            return ProcessResult(
                status=ProcessStatus.TIMEOUT,
                return_code=-1,
                stdout=e.stdout or "",
                stderr=e.stderr or "",
                command=command,
                execution_time=execution_time
            )
            
        except KeyboardInterrupt:
            execution_time = time.time() - start_time
            return ProcessResult(
                status=ProcessStatus.INTERRUPTED,
                return_code=-2,
                stdout="",
                stderr="Process interrupted by user",
                command=command,
                execution_time=execution_time
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            return ProcessResult(
                status=ProcessStatus.FAILED,
                return_code=-1,
                stdout="",
                stderr=str(e),
                command=command,
                execution_time=execution_time
            )
    
    def run_interactive(self, command: List[str], 
                       env: Optional[Dict[str, str]] = None,
                       shell: bool = False) -> ProcessResult:
        """
        Run command with interactive I/O (inherit stdio).
        
        Args:
            command: Command and arguments to execute
            env: Environment variables
            shell: Whether to use shell execution
            
        Returns:
            ProcessResult with execution details
        """
        import time
        start_time = time.time()
        
        try:
            result = subprocess.run(
                command,
                env=env,
                shell=shell,
                cwd=self.cwd,
                # Inherit stdio for interactive commands
                stdin=sys.stdin,
                stdout=sys.stdout,
                stderr=sys.stderr
            )
            
            execution_time = time.time() - start_time
            
            return ProcessResult(
                status=ProcessStatus.SUCCESS if result.returncode == 0 else ProcessStatus.FAILED,
                return_code=result.returncode,
                stdout="",  # Not captured in interactive mode
                stderr="",  # Not captured in interactive mode
                command=command,
                execution_time=execution_time
            )
            
        except KeyboardInterrupt:
            execution_time = time.time() - start_time
            return ProcessResult(
                status=ProcessStatus.INTERRUPTED,
                return_code=-2,
                stdout="",
                stderr="Process interrupted by user", 
                command=command,
                execution_time=execution_time
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            return ProcessResult(
                status=ProcessStatus.FAILED,
                return_code=-1,
                stdout="",
                stderr=str(e),
                command=command,
                execution_time=execution_time
            )
    
    def detect_package_manager(self, language: str) -> Optional[str]:
        """
        Detect available package manager for a language.
        
        Args:
            language: Programming language (python, nodejs, rust)
            
        Returns:
            Package manager name or None if not found
        """
        managers_by_language = {
            'python': ['pipx', 'pip'],
            'nodejs': ['yarn', 'npm'],
            'typescript': ['yarn', 'npm'],
            'rust': ['cargo']
        }
        
        candidates = managers_by_language.get(language, [])
        
        for manager in candidates:
            if self.platform.is_executable_available(manager):
                return manager
        
        return None
    
    def get_python_executable(self) -> str:
        """Get appropriate Python executable."""
        # Try to use the same Python that's running this script
        return sys.executable
    
    def check_pipx_installation(self, package_name: str) -> bool:
        """Check if package is installed via pipx."""
        if not self.platform.is_executable_available('pipx'):
            return False
        
        result = self.run(['pipx', 'list'], capture_output=True)
        return result.success and package_name in result.stdout
    
    def get_npm_global_packages(self) -> List[str]:
        """Get list of globally installed npm packages."""
        if not self.platform.is_executable_available('npm'):
            return []
        
        result = self.run(['npm', 'list', '-g', '--depth=0'], capture_output=True)
        if not result.success:
            return []
        
        packages = []
        for line in result.stdout.splitlines():
            if '├──' in line or '└──' in line:
                # Extract package name from tree output
                package_line = line.split('──')[-1].strip()
                package_name = package_line.split('@')[0]
                packages.append(package_name)
        
        return packages
    
    def build_upgrade_command(self, language: str, package_name: str, 
                            version: Optional[str] = None,
                            pre_release: bool = False,
                            force: bool = False) -> List[str]:
        """
        Build upgrade command for specified language and package manager.
        
        Args:
            language: Target language
            package_name: Name of package to upgrade
            version: Specific version to install
            pre_release: Whether to include pre-release versions
            force: Whether to force reinstallation
            
        Returns:
            Command list ready for execution
        """
        package_manager = self.detect_package_manager(language)
        
        if language == 'python':
            if package_manager == 'pipx':
                if version:
                    cmd = ['pipx', 'install', f'{package_name}=={version}']
                    if force:
                        cmd.append('--force')
                else:
                    cmd = ['pipx', 'upgrade', package_name]
                    if pre_release:
                        cmd.extend(['--pip-args', '--pre'])
            else:  # pip
                cmd = [self.get_python_executable(), '-m', 'pip', 'install', '--upgrade']
                if version:
                    cmd.append(f'{package_name}=={version}')
                else:
                    cmd.append(package_name)
                    if pre_release:
                        cmd.append('--pre')
                        
        elif language in ('nodejs', 'typescript'):
            if package_manager == 'yarn':
                cmd = ['yarn', 'global', 'add']
                if version:
                    cmd.append(f'{package_name}@{version}')
                else:
                    cmd.append(package_name)
                    if pre_release:
                        cmd.append('--tag=beta')
            else:  # npm
                cmd = ['npm', 'install', '-g']
                if version:
                    cmd.append(f'{package_name}@{version}')
                else:
                    cmd.append(package_name)
                    if pre_release:
                        cmd.extend(['--tag', 'beta'])
                        
        elif language == 'rust':
            cmd = ['cargo', 'install']
            if version:
                cmd.extend(['--version', version])
            if force:
                cmd.append('--force')
            cmd.append(package_name)
            
        else:
            raise ValueError(f"Unsupported language: {language}")
        
        return cmd
    
    def check_latest_version(self, language: str, package_name: str) -> Optional[str]:
        """
        Check latest version of a package.
        
        Args:
            language: Target language
            package_name: Package name to check
            
        Returns:
            Latest version string or None if unavailable
        """
        try:
            if language == 'python':
                result = self.run([
                    self.get_python_executable(), '-m', 'pip', 'index', 'versions', package_name
                ], capture_output=True)
                
                if result.success and 'Available versions:' in result.stdout:
                    # Parse pip index output for latest version
                    for line in result.stdout.splitlines():
                        if 'Available versions:' in line:
                            versions = line.split(':')[-1].strip().split(',')
                            if versions:
                                return versions[0].strip()
                                
            elif language in ('nodejs', 'typescript'):
                result = self.run(['npm', 'view', package_name, 'version'], capture_output=True)
                if result.success:
                    return result.stdout.strip()
                    
            elif language == 'rust':
                result = self.run(['cargo', 'search', package_name, '--limit', '1'], capture_output=True)
                if result.success and '=' in result.stdout:
                    # Parse cargo search output
                    for line in result.stdout.splitlines():
                        if package_name in line and '=' in line:
                            version_part = line.split('=')[-1].strip().strip('"')
                            return version_part
                            
        except Exception:
            pass
            
        return None