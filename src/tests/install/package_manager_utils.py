"""Package manager utilities for installation testing.

This module provides specialized utilities for interacting with different
package managers (pip, npm, yarn, cargo, pipx) during installation testing.
"""

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class PackageManagerNotFoundError(Exception):
    """Raised when a required package manager is not available."""
    pass


class PackageInstallationError(Exception):
    """Raised when package installation fails."""
    pass


class PipManager:
    """Utility class for pip package manager interactions."""
    
    @staticmethod
    def is_available() -> bool:
        """Check if pip is available."""
        return shutil.which("pip") is not None
    
    @staticmethod
    def install_editable(package_path: str, timeout: int = 120) -> subprocess.CompletedProcess:
        """Install package in editable mode using pip."""
        cmd = ["pip", "install", "-e", "."]
        return subprocess.run(
            cmd, 
            cwd=package_path, 
            capture_output=True, 
            text=True, 
            timeout=timeout,
            check=True
        )
    
    @staticmethod
    def install_from_path(package_path: str, timeout: int = 120) -> subprocess.CompletedProcess:
        """Install package from path using pip."""
        cmd = ["pip", "install", "."]
        return subprocess.run(
            cmd, 
            cwd=package_path, 
            capture_output=True, 
            text=True, 
            timeout=timeout,
            check=True
        )
    
    @staticmethod
    def uninstall(package_name: str, timeout: int = 60) -> subprocess.CompletedProcess:
        """Uninstall package using pip."""
        cmd = ["pip", "uninstall", "-y", package_name]
        return subprocess.run(
            cmd, 
            capture_output=True, 
            text=True, 
            timeout=timeout,
            check=False  # Don't raise on failure during cleanup
        )
    
    @staticmethod
    def list_installed() -> List[str]:
        """Get list of installed packages."""
        try:
            result = subprocess.run(
                ["pip", "list", "--format=json"], 
                capture_output=True, 
                text=True, 
                check=True
            )
            packages = json.loads(result.stdout)
            return [pkg["name"] for pkg in packages]
        except (subprocess.CalledProcessError, json.JSONDecodeError):
            return []


class PipxManager:
    """Utility class for pipx package manager interactions."""
    
    @staticmethod
    def is_available() -> bool:
        """Check if pipx is available."""
        return shutil.which("pipx") is not None
    
    @staticmethod
    def install_from_path(package_path: str, timeout: int = 120) -> subprocess.CompletedProcess:
        """Install package from path using pipx."""
        cmd = ["pipx", "install", "."]
        return subprocess.run(
            cmd, 
            cwd=package_path, 
            capture_output=True, 
            text=True, 
            timeout=timeout,
            check=True
        )
    
    @staticmethod
    def uninstall(package_name: str, timeout: int = 60) -> subprocess.CompletedProcess:
        """Uninstall package using pipx."""
        cmd = ["pipx", "uninstall", package_name]
        return subprocess.run(
            cmd, 
            capture_output=True, 
            text=True, 
            timeout=timeout,
            check=False  # Don't raise on failure during cleanup
        )
    
    @staticmethod
    def list_installed() -> List[str]:
        """Get list of installed packages."""
        try:
            result = subprocess.run(
                ["pipx", "list", "--json"], 
                capture_output=True, 
                text=True, 
                check=True
            )
            data = json.loads(result.stdout)
            return list(data.get("venvs", {}).keys())
        except (subprocess.CalledProcessError, json.JSONDecodeError):
            return []


class NpmManager:
    """Utility class for npm package manager interactions."""
    
    @staticmethod
    def is_available() -> bool:
        """Check if npm is available."""
        return shutil.which("npm") is not None
    
    @staticmethod
    def install_dependencies(package_path: str, timeout: int = 300) -> subprocess.CompletedProcess:
        """Install package dependencies using npm."""
        cmd = ["npm", "install"]
        return subprocess.run(
            cmd, 
            cwd=package_path, 
            capture_output=True, 
            text=True, 
            timeout=timeout,
            check=True
        )
    
    @staticmethod
    def link_global(package_path: str, timeout: int = 120) -> subprocess.CompletedProcess:
        """Link package globally using npm."""
        cmd = ["npm", "link"]
        return subprocess.run(
            cmd, 
            cwd=package_path, 
            capture_output=True, 
            text=True, 
            timeout=timeout,
            check=True
        )
    
    @staticmethod
    def unlink_global(package_name: str, timeout: int = 60) -> subprocess.CompletedProcess:
        """Unlink global package using npm."""
        cmd = ["npm", "unlink", "-g", package_name]
        return subprocess.run(
            cmd, 
            capture_output=True, 
            text=True, 
            timeout=timeout,
            check=False  # Don't raise on failure during cleanup
        )
    
    @staticmethod
    def uninstall_global(package_name: str, timeout: int = 60) -> subprocess.CompletedProcess:
        """Uninstall global package using npm."""
        cmd = ["npm", "uninstall", "-g", package_name]
        return subprocess.run(
            cmd, 
            capture_output=True, 
            text=True, 
            timeout=timeout,
            check=False  # Don't raise on failure during cleanup
        )
    
    @staticmethod
    def run_script(script_name: str, package_path: str, timeout: int = 120) -> subprocess.CompletedProcess:
        """Run npm script."""
        cmd = ["npm", "run", script_name]
        return subprocess.run(
            cmd, 
            cwd=package_path, 
            capture_output=True, 
            text=True, 
            timeout=timeout,
            check=True
        )
    
    @staticmethod
    def list_global() -> List[str]:
        """Get list of globally installed packages."""
        try:
            result = subprocess.run(
                ["npm", "list", "-g", "--depth=0", "--json"], 
                capture_output=True, 
                text=True, 
                check=True
            )
            data = json.loads(result.stdout)
            return list(data.get("dependencies", {}).keys())
        except (subprocess.CalledProcessError, json.JSONDecodeError):
            return []


class YarnManager:
    """Utility class for yarn package manager interactions."""
    
    @staticmethod
    def is_available() -> bool:
        """Check if yarn is available."""
        return shutil.which("yarn") is not None
    
    @staticmethod
    def install_dependencies(package_path: str, timeout: int = 300) -> subprocess.CompletedProcess:
        """Install package dependencies using yarn."""
        cmd = ["yarn", "install"]
        return subprocess.run(
            cmd, 
            cwd=package_path, 
            capture_output=True, 
            text=True, 
            timeout=timeout,
            check=True
        )
    
    @staticmethod
    def global_add(package_path: str, timeout: int = 120) -> subprocess.CompletedProcess:
        """Add package globally using yarn."""
        cmd = ["yarn", "global", "add", f"file:{package_path}"]
        return subprocess.run(
            cmd, 
            capture_output=True, 
            text=True, 
            timeout=timeout,
            check=True
        )
    
    @staticmethod
    def global_remove(package_name: str, timeout: int = 60) -> subprocess.CompletedProcess:
        """Remove global package using yarn."""
        cmd = ["yarn", "global", "remove", package_name]
        return subprocess.run(
            cmd, 
            capture_output=True, 
            text=True, 
            timeout=timeout,
            check=False  # Don't raise on failure during cleanup
        )
    
    @staticmethod
    def run_script(script_name: str, package_path: str, timeout: int = 120) -> subprocess.CompletedProcess:
        """Run yarn script."""
        cmd = ["yarn", script_name]
        return subprocess.run(
            cmd, 
            cwd=package_path, 
            capture_output=True, 
            text=True, 
            timeout=timeout,
            check=True
        )
    
    @staticmethod
    def list_global() -> List[str]:
        """Get list of globally installed packages."""
        try:
            result = subprocess.run(
                ["yarn", "global", "list", "--json"], 
                capture_output=True, 
                text=True, 
                check=True
            )
            # Yarn outputs multiple JSON objects, we need the last one
            lines = result.stdout.strip().split('\n')
            for line in reversed(lines):
                try:
                    data = json.loads(line)
                    if data.get("type") == "list":
                        return [item["name"] for item in data.get("data", {}).get("body", [])]
                except json.JSONDecodeError:
                    continue
            return []
        except subprocess.CalledProcessError:
            return []


class CargoManager:
    """Utility class for cargo package manager interactions."""
    
    @staticmethod
    def is_available() -> bool:
        """Check if cargo is available."""
        return shutil.which("cargo") is not None
    
    @staticmethod
    def build(package_path: str, release: bool = False, timeout: int = 300) -> subprocess.CompletedProcess:
        """Build package using cargo."""
        cmd = ["cargo", "build"]
        if release:
            cmd.append("--release")
        return subprocess.run(
            cmd, 
            cwd=package_path, 
            capture_output=True, 
            text=True, 
            timeout=timeout,
            check=True
        )
    
    @staticmethod
    def install_from_path(package_path: str, timeout: int = 300) -> subprocess.CompletedProcess:
        """Install package from path using cargo."""
        cmd = ["cargo", "install", "--path", "."]
        return subprocess.run(
            cmd, 
            cwd=package_path, 
            capture_output=True, 
            text=True, 
            timeout=timeout,
            check=True
        )
    
    @staticmethod
    def uninstall(package_name: str, timeout: int = 60) -> subprocess.CompletedProcess:
        """Uninstall package using cargo."""
        cmd = ["cargo", "uninstall", package_name]
        return subprocess.run(
            cmd, 
            capture_output=True, 
            text=True, 
            timeout=timeout,
            check=False  # Don't raise on failure during cleanup
        )
    
    @staticmethod
    def check(package_path: str, timeout: int = 120) -> subprocess.CompletedProcess:
        """Check package for errors using cargo."""
        cmd = ["cargo", "check"]
        return subprocess.run(
            cmd, 
            cwd=package_path, 
            capture_output=True, 
            text=True, 
            timeout=timeout,
            check=True
        )
    
    @staticmethod
    def list_installed() -> List[str]:
        """Get list of installed packages."""
        try:
            # Get cargo install root
            result = subprocess.run(
                ["cargo", "install", "--list"], 
                capture_output=True, 
                text=True, 
                check=True
            )
            packages = []
            for line in result.stdout.split('\n'):
                line = line.strip()
                if line and not line.startswith(' '):
                    # Package names are at the start of lines
                    package_name = line.split()[0]
                    packages.append(package_name)
            return packages
        except subprocess.CalledProcessError:
            return []


class PackageManagerRegistry:
    """Registry for all package managers with unified interface."""
    
    managers = {
        "pip": PipManager,
        "pipx": PipxManager,
        "npm": NpmManager,
        "yarn": YarnManager,
        "cargo": CargoManager
    }
    
    @classmethod
    def get_manager(cls, name: str):
        """Get package manager by name."""
        if name not in cls.managers:
            raise ValueError(f"Unknown package manager: {name}")
        return cls.managers[name]
    
    @classmethod
    def get_available_managers(cls) -> Dict[str, bool]:
        """Get availability status of all package managers."""
        return {
            name: manager.is_available()
            for name, manager in cls.managers.items()
        }
    
    @classmethod
    def check_requirements(cls, required_managers: List[str]) -> Tuple[bool, List[str]]:
        """Check if required package managers are available."""
        missing = []
        for manager in required_managers:
            if manager not in cls.managers:
                missing.append(f"Unknown package manager: {manager}")
            elif not cls.managers[manager].is_available():
                missing.append(f"Package manager not available: {manager}")
        
        return len(missing) == 0, missing


def validate_installation_environment() -> Dict[str, any]:
    """Validate the installation testing environment."""
    available_managers = PackageManagerRegistry.get_available_managers()
    
    # Check Python environment
    python_info = {
        "version": sys.version,
        "executable": sys.executable,
        "virtual_env": os.environ.get("VIRTUAL_ENV"),
        "pip_available": available_managers.get("pip", False),
        "pipx_available": available_managers.get("pipx", False)
    }
    
    # Check Node.js environment
    nodejs_info = {
        "npm_available": available_managers.get("npm", False),
        "yarn_available": available_managers.get("yarn", False)
    }
    
    # Try to get Node.js version
    try:
        result = subprocess.run(
            ["node", "--version"], 
            capture_output=True, 
            text=True, 
            check=True
        )
        nodejs_info["version"] = result.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        nodejs_info["version"] = None
    
    # Check Rust environment
    rust_info = {
        "cargo_available": available_managers.get("cargo", False)
    }
    
    # Try to get Rust version
    try:
        result = subprocess.run(
            ["rustc", "--version"], 
            capture_output=True, 
            text=True, 
            check=True
        )
        rust_info["version"] = result.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        rust_info["version"] = None
    
    return {
        "python": python_info,
        "nodejs": nodejs_info,
        "rust": rust_info,
        "available_managers": available_managers
    }


def make_cli_executable(cli_path: Path, shebang: str = "#!/usr/bin/env python3"):
    """Make a CLI file executable with appropriate shebang."""
    # Read current content
    content = cli_path.read_text()
    
    # Add shebang if not present
    if not content.startswith("#!"):
        content = f"{shebang}\n{content}"
        cli_path.write_text(content)
    
    # Make executable
    cli_path.chmod(0o755)


def cleanup_global_packages(packages_to_clean: List[Dict[str, str]]):
    """Clean up globally installed packages across all package managers."""
    cleanup_results = []
    
    for package_info in packages_to_clean:
        manager_name = package_info.get("manager")
        package_name = package_info.get("name")
        
        if not manager_name or not package_name:
            continue
        
        try:
            manager = PackageManagerRegistry.get_manager(manager_name)
            
            if manager_name == "pip":
                result = manager.uninstall(package_name)
            elif manager_name == "pipx":
                result = manager.uninstall(package_name)
            elif manager_name == "npm":
                result = manager.uninstall_global(package_name)
            elif manager_name == "yarn":
                result = manager.global_remove(package_name)
            elif manager_name == "cargo":
                result = manager.uninstall(package_name)
            
            cleanup_results.append({
                "manager": manager_name,
                "package": package_name,
                "success": result.returncode == 0,
                "output": result.stdout if hasattr(result, 'stdout') else ""
            })
            
        except Exception as e:
            cleanup_results.append({
                "manager": manager_name,
                "package": package_name,
                "success": False,
                "error": str(e)
            })
    
    return cleanup_results