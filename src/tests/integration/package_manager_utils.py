"""Package manager utilities for installation testing.

This module provides specialized utilities for interacting with different
package managers (pip, npm, yarn, cargo, pipx) during installation testing.
"""

import json
import os
import shutil
import socket
import subprocess
import sys
import urllib.request
from pathlib import Path
from typing import Dict, List, Tuple


class PackageManagerNotFoundError(Exception):
    """Raised when a required package manager is not available."""
    pass


class PackageInstallationError(Exception):
    """Raised when package installation fails."""
    pass


class TestEnvironmentManager:
    """Manages test-scoped environments and PATH isolation."""
    
    @staticmethod
    def create_test_environment(project_dir: str, language: str) -> dict:
        """Create isolated environment for test execution."""
        test_env = os.environ.copy()
        project_path = Path(project_dir).resolve()
        
        if language == "python":
            venv_path = project_path / ".test_venv"
            if venv_path.exists():
                bin_path = venv_path / "bin"
                if not bin_path.exists():
                    bin_path = venv_path / "Scripts"  # Windows
                test_env['PATH'] = f"{bin_path}{os.pathsep}{test_env['PATH']}"
                test_env['VIRTUAL_ENV'] = str(venv_path)
                
        elif language in ["nodejs", "typescript"]:
            npm_prefix = project_path / ".npm_prefix"
            if npm_prefix.exists():
                bin_path = npm_prefix / "bin"
                test_env['PATH'] = f"{bin_path}{os.pathsep}{test_env['PATH']}"
                test_env['npm_config_prefix'] = str(npm_prefix)
                
        elif language == "rust":
            cargo_home = project_path / ".cargo_home"
            if cargo_home.exists():
                bin_path = cargo_home / "bin"
                test_env['PATH'] = f"{bin_path}{os.pathsep}{test_env['PATH']}"
                test_env['CARGO_HOME'] = str(cargo_home)
                test_env['CARGO_INSTALL_ROOT'] = str(cargo_home)
                
        return test_env
    
    @staticmethod
    def cleanup_test_environment(project_dir: str):
        """Clean up test-scoped environment files."""
        project_path = Path(project_dir)
        
        # Remove test virtual environments
        for env_dir in [".test_venv", ".npm_prefix", ".cargo_home"]:
            env_path = project_path / env_dir
            if env_path.exists():
                shutil.rmtree(env_path, ignore_errors=True)


class PipManager:
    """Utility class for pip package manager interactions."""
    
    @staticmethod
    def is_available() -> bool:
        """Check if pip is available."""
        try:
            subprocess.run(
                [sys.executable, "-m", "pip", "--version"],
                capture_output=True,
                text=True,
                timeout=30,
                check=True
            )
            return True
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
            return False
    
    @staticmethod
    def install_editable(package_path: str, timeout: int = 120) -> subprocess.CompletedProcess:
        """Install package in editable mode using pip."""
        cmd = [sys.executable, "-m", "pip", "install", "-e", "."]
        return subprocess.run(
            cmd, 
            cwd=package_path, 
            capture_output=True, 
            text=True, 
            timeout=timeout,
            check=True
        )
    
    @staticmethod
    def install_editable_scoped(project_dir: str, venv_path: str = None) -> subprocess.CompletedProcess:
        """Install package in editable mode within a scoped virtual environment."""
        if venv_path is None:
            venv_path = f"{project_dir}/.test_venv"
        
        project_path = Path(project_dir).resolve()
        venv_path = Path(venv_path).resolve()
        
        # Create virtual environment if it doesn't exist
        if not venv_path.exists():
            result = subprocess.run([sys.executable, "-m", "venv", str(venv_path)], 
                                  capture_output=True, text=True, timeout=60, check=False)
            if result.returncode != 0:
                raise RuntimeError(f"Failed to create venv: {result.stderr}")
        
        # Install in virtual environment
        pip_exe = venv_path / "bin" / "pip"
        if not pip_exe.exists():
            pip_exe = venv_path / "Scripts" / "pip.exe"  # Windows
        
        return subprocess.run([
            str(pip_exe), "install", "-e", "."
        ], cwd=str(project_path), capture_output=True, text=True, timeout=120, check=False)
    
    @staticmethod
    def install_from_path(package_path: str, timeout: int = 120) -> subprocess.CompletedProcess:
        """Install package from path using pip."""
        cmd = [sys.executable, "-m", "pip", "install", "."]
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
        cmd = [sys.executable, "-m", "pip", "uninstall", "-y", package_name]
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
                [sys.executable, "-m", "pip", "list", "--format=json"], 
                capture_output=True, 
                text=True, 
                timeout=30,
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
            check=False
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
            check=False
        )
    
    @staticmethod
    def install_with_prefix(project_dir: str, prefix_path: str = None) -> subprocess.CompletedProcess:
        """Install npm package with isolated prefix to avoid global pollution."""
        if prefix_path is None:
            prefix_path = f"{project_dir}/.npm_prefix"
        
        project_path = Path(project_dir).resolve()
        prefix_path = Path(prefix_path).resolve()
        
        # Create prefix directory
        prefix_path.mkdir(exist_ok=True)
        
        # Install dependencies first in the project directory
        subprocess.run([
            "npm", "install"
        ], cwd=str(project_path), capture_output=True, text=True, timeout=120, check=True)
        
        # Then install the package itself to the prefix
        env = os.environ.copy()
        env['npm_config_prefix'] = str(prefix_path)
        
        return subprocess.run([
            "npm", "install", "-g", str(project_path)
        ], capture_output=True, text=True, timeout=120, env=env, check=True)

    @staticmethod  
    def link_with_prefix(project_dir: str, prefix_path: str = None) -> subprocess.CompletedProcess:
        """Create local link without affecting global npm packages."""
        if prefix_path is None:
            prefix_path = f"{project_dir}/.npm_prefix"
            
        project_path = Path(project_dir).resolve()
        prefix_path = Path(prefix_path).resolve()
        
        # Create local symlink in prefix bin directory
        env = os.environ.copy()
        env['npm_config_prefix'] = str(prefix_path)
        
        return subprocess.run([
            "npm", "link", "--prefix", str(prefix_path)
        ], cwd=str(project_path), capture_output=True, text=True, timeout=60, env=env, check=True)
    
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
            check=False
        )
    
    @staticmethod
    def list_global() -> List[str]:
        """Get list of globally installed packages."""
        try:
            result = subprocess.run(
                ["npm", "list", "-g", "--depth=0", "--json"], 
                capture_output=True, 
                text=True, 
                timeout=30,
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
    def build(package_path: str, release: bool = False, offline: bool = False, timeout: int = 300) -> subprocess.CompletedProcess:
        """Build package using cargo."""
        cmd = ["cargo", "build"]
        if release:
            cmd.append("--release")
        if offline:
            cmd.append("--offline")
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
    def install_from_path_scoped(project_dir: str, cargo_home: str = None) -> subprocess.CompletedProcess:
        """Install package from path using cargo with scoped CARGO_HOME."""
        if cargo_home is None:
            cargo_home = f"{project_dir}/.cargo_home"
        
        project_path = Path(project_dir).resolve()
        cargo_home_path = Path(cargo_home).resolve()
        
        # Create cargo home directory
        cargo_home_path.mkdir(exist_ok=True)
        (cargo_home_path / "bin").mkdir(exist_ok=True)
        
        # Set scoped cargo environment
        env = os.environ.copy()
        env['CARGO_HOME'] = str(cargo_home_path)
        env['CARGO_INSTALL_ROOT'] = str(cargo_home_path)
        
        cmd = ["cargo", "install", "--path", ".", "--root", str(cargo_home_path)]
        return subprocess.run(
            cmd, 
            cwd=str(project_path), 
            capture_output=True, 
            text=True, 
            env=env,
            timeout=300,
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
    def check(package_path: str, offline: bool = False, timeout: int = 120) -> subprocess.CompletedProcess:
        """Check package for errors using cargo."""
        cmd = ["cargo", "check"]
        if offline:
            cmd.append("--offline")
        return subprocess.run(
            cmd, 
            cwd=package_path, 
            capture_output=True, 
            text=True, 
            timeout=timeout,
            check=True
        )
    
    @staticmethod
    def check_network_connectivity(timeout: int = 5) -> bool:
        """Check if crates.io is accessible."""
        try:
            # Try to connect to crates.io index repository
            response = urllib.request.urlopen(
                'https://index.crates.io/',
                timeout=timeout
            )
            return response.getcode() == 200
        except (urllib.error.URLError, socket.timeout, OSError):
            return False
    
    @staticmethod
    def try_build_with_fallback(package_path: str, release: bool = False, timeout: int = 300) -> subprocess.CompletedProcess:
        """Try to build with network, fall back to offline mode if network fails."""
        try:
            # First try normal build
            return CargoManager.build(package_path, release=release, timeout=timeout)
        except subprocess.CalledProcessError as e:
            # If build fails and it's due to network issues, try offline
            if "Could not connect" in e.stderr or "network" in e.stderr.lower():
                try:
                    return CargoManager.build(package_path, release=release, offline=True, timeout=timeout)
                except subprocess.CalledProcessError:
                    # If offline also fails, re-raise original error
                    raise e
            else:
                # If it's not a network error, re-raise
                raise e
    
    @staticmethod
    def list_installed() -> List[str]:
        """Get list of installed packages."""
        try:
            # Get cargo install root
            result = subprocess.run(
                ["cargo", "install", "--list"], 
                capture_output=True, 
                text=True, 
                timeout=30,
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
    def get_test_environment_manager(cls):
        """Get the test environment manager for scoped testing."""
        return TestEnvironmentManager
    
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


class TestPathManager:
    """Utility for managing PATH modifications during tests."""
    
    def __init__(self):
        self._path_additions = []
        self._original_path = os.environ.get('PATH', '')
    
    def add_to_path(self, path_dir: Path, reason: str = None):
        """
        Add directory to PATH with tracking for cleanup.
        
        Args:
            path_dir: Directory to add to PATH
            reason: Optional reason for logging
        """
        path_str = str(path_dir.resolve())
        
        if path_dir.exists() and path_str not in os.environ['PATH']:
            new_path = f"{path_str}{os.pathsep}{os.environ['PATH']}"
            os.environ['PATH'] = new_path
            self._path_additions.append(path_str)
            
            if reason:
                print(f"Added to PATH: {path_str} ({reason})")
    
    def add_scoped_venv_to_path(self, temp_dir: Path):
        """Add scoped Python virtual environment to PATH."""
        venv_bin = temp_dir / ".test_venv" / "bin"
        if not venv_bin.exists():
            venv_bin = temp_dir / ".test_venv" / "Scripts"  # Windows
        
        if venv_bin.exists():
            self.add_to_path(venv_bin, "scoped Python venv")
    
    def add_npm_prefix_to_path(self, temp_dir: Path):
        """Add npm prefix bin directory to PATH."""
        npm_prefix_bin = temp_dir / ".npm_prefix" / "bin"
        if npm_prefix_bin.exists():
            self.add_to_path(npm_prefix_bin, "npm prefix")
    
    def add_cargo_home_to_path(self, temp_dir: Path):
        """Add cargo home bin directory to PATH."""
        cargo_bin = temp_dir / ".cargo_home" / "bin"
        if cargo_bin.exists():
            self.add_to_path(cargo_bin, "cargo home")
    
    def cleanup(self):
        """Restore original PATH by removing all tracked additions."""
        os.environ['PATH'] = self._original_path
        self._path_additions.clear()
    
    def get_path_additions(self) -> List[str]:
        """Return list of directories added to PATH."""
        return self._path_additions.copy()