"""
System Detection
================

System and platform detection utilities for cross-platform setup management.
Handles OS detection, package manager discovery, and environment validation.
"""

import sys
import platform
import subprocess
import shutil
from typing import Dict, List, Optional, Any
from enum import Enum
from dataclasses import dataclass


class Platform(Enum):
    """Supported platforms."""
    LINUX = "linux"
    MACOS = "macos" 
    WINDOWS = "windows"
    UNKNOWN = "unknown"


class SystemPackageManager(Enum):
    """System package managers."""
    APT = "apt"
    YUM = "yum"
    DNF = "dnf"
    PACMAN = "pacman"
    HOMEBREW = "brew"
    CHOCOLATEY = "choco"
    WINGET = "winget"
    UNKNOWN = "unknown"


@dataclass
class PackageManagerInfo:
    """Information about a package manager."""
    name: SystemPackageManager
    command: str
    available: bool = False
    version: Optional[str] = None
    install_cmd: str = ""
    update_cmd: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'name': self.name.value,
            'command': self.command,
            'available': self.available,
            'version': self.version,
            'install_cmd': self.install_cmd,
            'update_cmd': self.update_cmd
        }


class SystemDetector:
    """System detection and environment analysis."""
    
    def __init__(self):
        """Initialize system detector."""
        self.platform = self._detect_platform()
        self.package_managers = self._detect_package_managers()
        
    def _detect_platform(self) -> Platform:
        """Detect the current platform."""
        system = platform.system().lower()
        
        if system == "linux":
            return Platform.LINUX
        elif system == "darwin":
            return Platform.MACOS
        elif system in ["windows", "cygwin"]:
            return Platform.WINDOWS
        else:
            return Platform.UNKNOWN
    
    def _detect_package_managers(self) -> Dict[SystemPackageManager, PackageManagerInfo]:
        """Detect available package managers."""
        managers = {}
        
        # Define package managers with their commands
        pm_configs = {
            SystemPackageManager.APT: PackageManagerInfo(
                SystemPackageManager.APT, "apt",
                install_cmd="apt install -y",
                update_cmd="apt update"
            ),
            SystemPackageManager.YUM: PackageManagerInfo(
                SystemPackageManager.YUM, "yum",
                install_cmd="yum install -y",
                update_cmd="yum update"
            ),
            SystemPackageManager.DNF: PackageManagerInfo(
                SystemPackageManager.DNF, "dnf", 
                install_cmd="dnf install -y",
                update_cmd="dnf update"
            ),
            SystemPackageManager.PACMAN: PackageManagerInfo(
                SystemPackageManager.PACMAN, "pacman",
                install_cmd="pacman -S --noconfirm",
                update_cmd="pacman -Sy"
            ),
            SystemPackageManager.HOMEBREW: PackageManagerInfo(
                SystemPackageManager.HOMEBREW, "brew",
                install_cmd="brew install",
                update_cmd="brew update"
            ),
            SystemPackageManager.CHOCOLATEY: PackageManagerInfo(
                SystemPackageManager.CHOCOLATEY, "choco",
                install_cmd="choco install -y",
                update_cmd="choco upgrade all -y"
            ),
            SystemPackageManager.WINGET: PackageManagerInfo(
                SystemPackageManager.WINGET, "winget",
                install_cmd="winget install",
                update_cmd="winget upgrade --all"
            )
        }
        
        # Check availability
        for pm_type, info in pm_configs.items():
            info.available = shutil.which(info.command) is not None
            
            if info.available:
                try:
                    # Try to get version
                    result = subprocess.run(
                        [info.command, "--version"],
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    if result.returncode == 0:
                        info.version = result.stdout.strip().split('\n')[0]
                except (subprocess.TimeoutExpired, subprocess.SubprocessError):
                    pass
            
            managers[pm_type] = info
        
        return managers
    
    def get_platform(self) -> Platform:
        """Get detected platform."""
        return self.platform
    
    def get_available_package_managers(self) -> List[PackageManagerInfo]:
        """Get list of available package managers."""
        return [pm for pm in self.package_managers.values() if pm.available]
    
    def get_package_manager(self, pm_type: SystemPackageManager) -> Optional[PackageManagerInfo]:
        """Get specific package manager info."""
        return self.package_managers.get(pm_type)
    
    def get_preferred_package_manager(self) -> Optional[PackageManagerInfo]:
        """Get preferred package manager for current platform."""
        # Define preferences by platform
        preferences = {
            Platform.LINUX: [
                SystemPackageManager.APT,
                SystemPackageManager.DNF, 
                SystemPackageManager.YUM,
                SystemPackageManager.PACMAN
            ],
            Platform.MACOS: [
                SystemPackageManager.HOMEBREW
            ],
            Platform.WINDOWS: [
                SystemPackageManager.WINGET,
                SystemPackageManager.CHOCOLATEY
            ]
        }
        
        platform_prefs = preferences.get(self.platform, [])
        
        for pm_type in platform_prefs:
            pm_info = self.package_managers.get(pm_type)
            if pm_info and pm_info.available:
                return pm_info
        
        return None
    
    def detect_python_environment(self) -> Dict[str, Any]:
        """Detect Python environment details."""
        python_info = {
            'python3_available': False,
            'python_available': False,
            'pip_available': False,
            'pipx_available': False,
            'venv_available': False,
            'python_version': None,
            'pip_version': None,
            'pipx_version': None,
            'executable_paths': {}
        }
        
        # Check Python executables
        for python_cmd in ['python3', 'python']:
            if shutil.which(python_cmd):
                python_info[f'{python_cmd}_available'] = True
                python_info['executable_paths'][python_cmd] = shutil.which(python_cmd)
                
                try:
                    result = subprocess.run(
                        [python_cmd, '--version'],
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    if result.returncode == 0:
                        python_info['python_version'] = result.stdout.strip()
                        break
                except (subprocess.TimeoutExpired, subprocess.SubprocessError):
                    pass
        
        # Check pip
        if shutil.which('pip3') or shutil.which('pip'):
            python_info['pip_available'] = True
            pip_cmd = 'pip3' if shutil.which('pip3') else 'pip'
            python_info['executable_paths']['pip'] = shutil.which(pip_cmd)
            
            try:
                result = subprocess.run(
                    [pip_cmd, '--version'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    python_info['pip_version'] = result.stdout.strip()
            except (subprocess.TimeoutExpired, subprocess.SubprocessError):
                pass
        
        # Check pipx
        if shutil.which('pipx'):
            python_info['pipx_available'] = True
            python_info['executable_paths']['pipx'] = shutil.which('pipx')
            
            try:
                result = subprocess.run(
                    ['pipx', '--version'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    python_info['pipx_version'] = result.stdout.strip()
            except (subprocess.TimeoutExpired, subprocess.SubprocessError):
                pass
        
        # Check venv
        try:
            import venv
            python_info['venv_available'] = True
        except ImportError:
            pass
        
        return python_info
    
    def detect_nodejs_environment(self) -> Dict[str, Any]:
        """Detect Node.js environment details."""
        nodejs_info = {
            'node_available': False,
            'npm_available': False,
            'yarn_available': False,
            'pnpm_available': False,
            'node_version': None,
            'npm_version': None,
            'yarn_version': None,
            'pnpm_version': None,
            'executable_paths': {}
        }
        
        # Check Node.js
        if shutil.which('node'):
            nodejs_info['node_available'] = True
            nodejs_info['executable_paths']['node'] = shutil.which('node')
            
            try:
                result = subprocess.run(
                    ['node', '--version'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    nodejs_info['node_version'] = result.stdout.strip()
            except (subprocess.TimeoutExpired, subprocess.SubprocessError):
                pass
        
        # Check package managers
        for pm_name in ['npm', 'yarn', 'pnpm']:
            if shutil.which(pm_name):
                nodejs_info[f'{pm_name}_available'] = True
                nodejs_info['executable_paths'][pm_name] = shutil.which(pm_name)
                
                try:
                    result = subprocess.run(
                        [pm_name, '--version'],
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    if result.returncode == 0:
                        nodejs_info[f'{pm_name}_version'] = result.stdout.strip()
                except (subprocess.TimeoutExpired, subprocess.SubprocessError):
                    pass
        
        return nodejs_info
    
    def detect_rust_environment(self) -> Dict[str, Any]:
        """Detect Rust environment details."""
        rust_info = {
            'rustc_available': False,
            'cargo_available': False,
            'rustup_available': False,
            'rustc_version': None,
            'cargo_version': None,
            'rustup_version': None,
            'executable_paths': {}
        }
        
        # Check Rust tools
        for tool in ['rustc', 'cargo', 'rustup']:
            if shutil.which(tool):
                rust_info[f'{tool}_available'] = True
                rust_info['executable_paths'][tool] = shutil.which(tool)
                
                try:
                    result = subprocess.run(
                        [tool, '--version'],
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    if result.returncode == 0:
                        rust_info[f'{tool}_version'] = result.stdout.strip()
                except (subprocess.TimeoutExpired, subprocess.SubprocessError):
                    pass
        
        return rust_info
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get comprehensive system information."""
        return {
            'platform': self.platform.value,
            'python_version': sys.version,
            'architecture': platform.architecture(),
            'machine': platform.machine(),
            'processor': platform.processor(),
            'system': platform.system(),
            'release': platform.release(),
            'package_managers': {
                pm_type.value: pm_info.to_dict()
                for pm_type, pm_info in self.package_managers.items()
            },
            'python_env': self.detect_python_environment(),
            'nodejs_env': self.detect_nodejs_environment(),
            'rust_env': self.detect_rust_environment()
        }


class PackageManagerRegistry:
    """Registry for package manager operations."""
    
    def __init__(self, detector: Optional[SystemDetector] = None):
        """Initialize registry."""
        self.detector = detector or SystemDetector()
    
    def install_packages(self, packages: List[str], pm_type: Optional[SystemPackageManager] = None) -> bool:
        """Install system packages using appropriate package manager."""
        if not packages:
            return True
        
        # Get package manager
        if pm_type:
            pm_info = self.detector.get_package_manager(pm_type)
        else:
            pm_info = self.detector.get_preferred_package_manager()
        
        if not pm_info or not pm_info.available:
            return False
        
        try:
            # Update package lists first
            if pm_info.update_cmd:
                subprocess.run(
                    pm_info.update_cmd.split(),
                    check=True,
                    capture_output=True
                )
            
            # Install packages
            install_cmd = pm_info.install_cmd.split() + packages
            subprocess.run(install_cmd, check=True)
            
            return True
            
        except subprocess.CalledProcessError:
            return False
    
    def is_package_installed(self, package: str, pm_type: Optional[SystemPackageManager] = None) -> bool:
        """Check if a system package is installed."""
        if pm_type:
            pm_info = self.detector.get_package_manager(pm_type)
        else:
            pm_info = self.detector.get_preferred_package_manager()
        
        if not pm_info or not pm_info.available:
            return False
        
        # Simple heuristic - check if command exists
        return shutil.which(package) is not None