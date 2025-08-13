"""

Plugin Marketplace Integration System

Provides secure plugin discovery, installation, and management

"""



import asyncio

import hashlib

import json

import time

from dataclasses import dataclass

from enum import Enum

from pathlib import Path

from typing import Dict, List, Optional, Any, Union

import aiohttp

import aiofiles

from urllib.parse import urljoin





class PluginSecurityLevel(Enum):

    """Security levels for plugins"""

    VERIFIED = "verified"  # Official or verified plugins

    COMMUNITY = "community"  # Community-reviewed plugins

    EXPERIMENTAL = "experimental"  # Unverified plugins





class PluginLanguage(Enum):

    """Supported plugin languages"""

    PYTHON = "python"

    NODEJS = "nodejs"

    TYPESCRIPT = "typescript"

    RUST = "rust"





@dataclass

class PluginInfo:

    """Plugin information from marketplace"""

    name: str

    version: str

    author: str

    description: str

    language: PluginLanguage

    security_level: PluginSecurityLevel

    download_url: str

    checksum: str

    size: int

    rating: float

    downloads: int

    tags: List[str]

    dependencies: List[str]

    min_goobits_version: str

    homepage: Optional[str] = None

    repository: Optional[str] = None

    license: Optional[str] = None





@dataclass

class PluginReview:

    """User review for a plugin"""

    author: str

    rating: int

    title: str

    comment: str

    date: str

    verified_purchase: bool





class MarketplaceAPIClient:

    """Client for interacting with the plugin marketplace API"""

    

    def __init__(self, base_url: str = "https://api.goobits.marketplace", 

                 api_key: Optional[str] = None):

        self.base_url = base_url

        self.api_key = api_key

        self.session: Optional[aiohttp.ClientSession] = None

        

    async def __aenter__(self):

        headers = {}

        if self.api_key:

            headers["Authorization"] = f"Bearer {self.api_key}"

            

        self.session = aiohttp.ClientSession(

            headers=headers,

            timeout=aiohttp.ClientTimeout(total=30)

        )

        return self

    

    async def __aexit__(self, exc_type, exc_val, exc_tb):

        if self.session:

            await self.session.close()

    

    async def search_plugins(self, query: str = "", 

                           language: Optional[PluginLanguage] = None,

                           security_level: Optional[PluginSecurityLevel] = None,

                           tags: Optional[List[str]] = None,

                           limit: int = 20,

                           offset: int = 0) -> List[PluginInfo]:

        """Search for plugins in the marketplace"""

        if not self.session:

            raise RuntimeError("Client not initialized. Use async context manager.")

            

        params = {

            "query": query,

            "limit": limit,

            "offset": offset

        }

        

        if language:

            params["language"] = language.value

        if security_level:

            params["security_level"] = security_level.value

        if tags:

            params["tags"] = ",".join(tags)

            

        url = urljoin(self.base_url, "/plugins/search")

        

        async with self.session.get(url, params=params) as response:

            response.raise_for_status()

            data = await response.json()

            

            return [

                PluginInfo(

                    name=plugin["name"],

                    version=plugin["version"],

                    author=plugin["author"],

                    description=plugin["description"],

                    language=PluginLanguage(plugin["language"]),

                    security_level=PluginSecurityLevel(plugin["security_level"]),

                    download_url=plugin["download_url"],

                    checksum=plugin["checksum"],

                    size=plugin["size"],

                    rating=plugin["rating"],

                    downloads=plugin["downloads"],

                    tags=plugin["tags"],

                    dependencies=plugin["dependencies"],

                    min_goobits_version=plugin["min_goobits_version"],

                    homepage=plugin.get("homepage"),

                    repository=plugin.get("repository"),

                    license=plugin.get("license")

                )

                for plugin in data["plugins"]

            ]

    

    async def get_plugin_info(self, name: str) -> PluginInfo:

        """Get detailed information about a specific plugin"""

        if not self.session:

            raise RuntimeError("Client not initialized. Use async context manager.")

            

        url = urljoin(self.base_url, f"/plugins/{name}")

        

        async with self.session.get(url) as response:

            response.raise_for_status()

            plugin = await response.json()

            

            return PluginInfo(

                name=plugin["name"],

                version=plugin["version"],

                author=plugin["author"],

                description=plugin["description"],

                language=PluginLanguage(plugin["language"]),

                security_level=PluginSecurityLevel(plugin["security_level"]),

                download_url=plugin["download_url"],

                checksum=plugin["checksum"],

                size=plugin["size"],

                rating=plugin["rating"],

                downloads=plugin["downloads"],

                tags=plugin["tags"],

                dependencies=plugin["dependencies"],

                min_goobits_version=plugin["min_goobits_version"],

                homepage=plugin.get("homepage"),

                repository=plugin.get("repository"),

                license=plugin.get("license")

            )

    

    async def get_plugin_reviews(self, name: str, 

                               limit: int = 10,

                               offset: int = 0) -> List[PluginReview]:

        """Get reviews for a plugin"""

        if not self.session:

            raise RuntimeError("Client not initialized. Use async context manager.")

            

        url = urljoin(self.base_url, f"/plugins/{name}/reviews")

        params = {"limit": limit, "offset": offset}

        

        async with self.session.get(url, params=params) as response:

            response.raise_for_status()

            data = await response.json()

            

            return [

                PluginReview(

                    author=review["author"],

                    rating=review["rating"],

                    title=review["title"],

                    comment=review["comment"],

                    date=review["date"],

                    verified_purchase=review["verified_purchase"]

                )

                for review in data["reviews"]

            ]

    

    async def download_plugin(self, plugin_info: PluginInfo, 

                            target_dir: Path) -> Path:

        """Download and verify a plugin"""

        if not self.session:

            raise RuntimeError("Client not initialized. Use async context manager.")

            

        # Create target directory

        target_dir.mkdir(parents=True, exist_ok=True)

        

        # Determine file extension based on language

        if plugin_info.language == PluginLanguage.PYTHON:

            filename = f"{plugin_info.name}-{plugin_info.version}.tar.gz"

        elif plugin_info.language in [PluginLanguage.NODEJS, PluginLanguage.TYPESCRIPT]:

            filename = f"{plugin_info.name}-{plugin_info.version}.tgz"

        elif plugin_info.language == PluginLanguage.RUST:

            filename = f"{plugin_info.name}-{plugin_info.version}.crate"

        else:

            filename = f"{plugin_info.name}-{plugin_info.version}.zip"

            

        target_file = target_dir / filename

        

        # Download plugin

        async with self.session.get(plugin_info.download_url) as response:

            response.raise_for_status()

            

            # Stream download with progress

            content = b""

            async for chunk in response.content.iter_chunked(8192):

                content += chunk

        

        # Verify checksum

        actual_checksum = hashlib.sha256(content).hexdigest()

        if actual_checksum != plugin_info.checksum:

            raise ValueError(f"Checksum mismatch for {plugin_info.name}. "

                           f"Expected: {plugin_info.checksum}, "

                           f"Got: {actual_checksum}")

        

        # Write to file

        async with aiofiles.open(target_file, "wb") as f:

            await f.write(content)

            

        return target_file

    

    async def publish_plugin(self, plugin_path: Path, 

                           manifest: Dict[str, Any]) -> str:

        """Publish a plugin to the marketplace"""

        if not self.session or not self.api_key:

            raise RuntimeError("API key required for publishing plugins")

            

        url = urljoin(self.base_url, "/plugins/publish")

        

        # Read plugin file

        async with aiofiles.open(plugin_path, "rb") as f:

            plugin_content = await f.read()

        

        # Create multipart form data

        data = aiohttp.FormData()

        data.add_field("manifest", json.dumps(manifest), 

                      content_type="application/json")

        data.add_field("plugin", plugin_content, 

                      filename=plugin_path.name,

                      content_type="application/octet-stream")

        

        async with self.session.post(url, data=data) as response:

            response.raise_for_status()

            result = await response.json()

            return result["plugin_id"]





class PluginSecurityScanner:

    """Scans plugins for security vulnerabilities"""

    

    def __init__(self):

        self.known_vulnerabilities = {}

        self.suspicious_patterns = [

            r"exec\s*\(",

            r"eval\s*\(",

            r"subprocess\.",

            r"os\.system",

            r"__import__",

            r"open\s*\(.+['\"]w",

            r"requests\.get\s*\(\s*input",

            r"urllib\.request\.urlopen"

        ]

    

    async def scan_plugin(self, plugin_path: Path) -> Dict[str, Any]:

        """Scan a plugin for security issues"""

        import re

        import tarfile

        import zipfile

        

        vulnerabilities = []

        warnings = []

        

        try:

            # Extract and scan plugin contents

            if plugin_path.suffix == ".gz":

                with tarfile.open(plugin_path, "r:gz") as tar:

                    for member in tar.getmembers():

                        if member.isfile() and member.name.endswith((".py", ".js", ".ts", ".rs")):

                            content = tar.extractfile(member).read().decode("utf-8")

                            issues = self._scan_content(content, member.name)

                            vulnerabilities.extend(issues["vulnerabilities"])

                            warnings.extend(issues["warnings"])

            

            elif plugin_path.suffix == ".zip":

                with zipfile.ZipFile(plugin_path, "r") as zip_file:

                    for filename in zip_file.namelist():

                        if filename.endswith((".py", ".js", ".ts", ".rs")):

                            content = zip_file.read(filename).decode("utf-8")

                            issues = self._scan_content(content, filename)

                            vulnerabilities.extend(issues["vulnerabilities"])

                            warnings.extend(issues["warnings"])

                            

        except Exception as e:

            vulnerabilities.append({

                "type": "scan_error",

                "message": f"Failed to scan plugin: {str(e)}",

                "severity": "high"

            })

        

        return {

            "vulnerabilities": vulnerabilities,

            "warnings": warnings,

            "risk_level": self._calculate_risk_level(vulnerabilities, warnings)

        }

    

    def _scan_content(self, content: str, filename: str) -> Dict[str, List[Dict]]:

        """Scan file content for security issues"""

        import re

        

        vulnerabilities = []

        warnings = []

        

        # Check for suspicious patterns

        for pattern in self.suspicious_patterns:

            matches = re.finditer(pattern, content, re.IGNORECASE)

            for match in matches:

                line_num = content[:match.start()].count("\n") + 1

                warnings.append({

                    "type": "suspicious_pattern",

                    "pattern": pattern,

                    "file": filename,

                    "line": line_num,

                    "context": content[max(0, match.start()-50):match.end()+50],

                    "severity": "medium"

                })

        

        # Check for hardcoded secrets

        secret_patterns = [

            (r"password\s*=\s*['\"][^'\"]+['\"]", "hardcoded_password"),

            (r"api_key\s*=\s*['\"][^'\"]+['\"]", "hardcoded_api_key"),

            (r"token\s*=\s*['\"][^'\"]+['\"]", "hardcoded_token"),

            (r"secret\s*=\s*['\"][^'\"]+['\"]", "hardcoded_secret")

        ]

        

        for pattern, vuln_type in secret_patterns:

            matches = re.finditer(pattern, content, re.IGNORECASE)

            for match in matches:

                line_num = content[:match.start()].count("\n") + 1

                vulnerabilities.append({

                    "type": vuln_type,

                    "file": filename,

                    "line": line_num,

                    "severity": "high"

                })

        

        return {"vulnerabilities": vulnerabilities, "warnings": warnings}

    

    def _calculate_risk_level(self, vulnerabilities: List[Dict], 

                            warnings: List[Dict]) -> str:

        """Calculate overall risk level"""

        high_vuln_count = sum(1 for v in vulnerabilities if v.get("severity") == "high")

        medium_vuln_count = sum(1 for v in vulnerabilities if v.get("severity") == "medium")

        warning_count = len(warnings)

        

        if high_vuln_count > 0:

            return "high"

        elif medium_vuln_count > 2 or warning_count > 5:

            return "medium"

        elif medium_vuln_count > 0 or warning_count > 0:

            return "low"

        else:

            return "safe"





class PluginInstaller:

    """Handles plugin installation and management"""

    

    def __init__(self, plugins_dir: Path):

        self.plugins_dir = plugins_dir

        self.plugins_dir.mkdir(parents=True, exist_ok=True)

        self.installed_plugins = self._load_installed_plugins()

    

    def _load_installed_plugins(self) -> Dict[str, Dict[str, Any]]:

        """Load information about installed plugins"""

        registry_file = self.plugins_dir / "registry.json"

        if registry_file.exists():

            with open(registry_file) as f:

                return json.load(f)

        return {}

    

    def _save_installed_plugins(self):

        """Save information about installed plugins"""

        registry_file = self.plugins_dir / "registry.json"

        with open(registry_file, "w") as f:

            json.dump(self.installed_plugins, f, indent=2)

    

    async def install_plugin(self, plugin_info: PluginInfo, 

                           force: bool = False) -> bool:

        """Install a plugin"""

        # Check if already installed

        if plugin_info.name in self.installed_plugins and not force:

            current_version = self.installed_plugins[plugin_info.name]["version"]

            if current_version == plugin_info.version:

                return False  # Already installed

        

        # Download plugin

        async with MarketplaceAPIClient() as client:

            plugin_file = await client.download_plugin(plugin_info, self.plugins_dir)

        

        # Security scan

        scanner = PluginSecurityScanner()

        scan_results = await scanner.scan_plugin(plugin_file)

        

        if scan_results["risk_level"] == "high":

            raise SecurityError(f"Plugin {plugin_info.name} failed security scan: "

                              f"{scan_results['vulnerabilities']}")

        

        # Install plugin based on language

        plugin_dir = self.plugins_dir / plugin_info.name

        if plugin_dir.exists():

            import shutil

            shutil.rmtree(plugin_dir)

        

        if plugin_info.language == PluginLanguage.PYTHON:

            await self._install_python_plugin(plugin_file, plugin_dir)

        elif plugin_info.language == PluginLanguage.NODEJS:

            await self._install_nodejs_plugin(plugin_file, plugin_dir)

        elif plugin_info.language == PluginLanguage.TYPESCRIPT:

            await self._install_typescript_plugin(plugin_file, plugin_dir)

        elif plugin_info.language == PluginLanguage.RUST:

            await self._install_rust_plugin(plugin_file, plugin_dir)

        

        # Update registry

        self.installed_plugins[plugin_info.name] = {

            "version": plugin_info.version,

            "language": plugin_info.language.value,

            "install_date": time.time(),

            "security_scan": scan_results,

            "dependencies": plugin_info.dependencies

        }

        self._save_installed_plugins()

        

        # Clean up downloaded file

        plugin_file.unlink()

        

        return True

    

    async def _install_python_plugin(self, plugin_file: Path, target_dir: Path):

        """Install a Python plugin"""

        import tarfile

        

        with tarfile.open(plugin_file, "r:gz") as tar:

            tar.extractall(target_dir)

    

    async def _install_nodejs_plugin(self, plugin_file: Path, target_dir: Path):

        """Install a Node.js plugin"""

        import tarfile

        

        with tarfile.open(plugin_file, "r:gz") as tar:

            tar.extractall(target_dir)

    

    async def _install_typescript_plugin(self, plugin_file: Path, target_dir: Path):

        """Install a TypeScript plugin"""

        await self._install_nodejs_plugin(plugin_file, target_dir)

    

    async def _install_rust_plugin(self, plugin_file: Path, target_dir: Path):

        """Install a Rust plugin"""

        import zipfile

        

        with zipfile.ZipFile(plugin_file, "r") as zip_file:

            zip_file.extractall(target_dir)

    

    async def uninstall_plugin(self, name: str) -> bool:

        """Uninstall a plugin"""

        if name not in self.installed_plugins:

            return False

        

        plugin_dir = self.plugins_dir / name

        if plugin_dir.exists():

            import shutil

            shutil.rmtree(plugin_dir)

        

        del self.installed_plugins[name]

        self._save_installed_plugins()

        return True

    

    async def update_plugin(self, name: str) -> bool:

        """Update a plugin to the latest version"""

        if name not in self.installed_plugins:

            return False

        

        async with MarketplaceAPIClient() as client:

            plugin_info = await client.get_plugin_info(name)

            

            current_version = self.installed_plugins[name]["version"]

            if plugin_info.version == current_version:

                return False  # Already up to date

            

            return await self.install_plugin(plugin_info, force=True)

    

    def list_installed_plugins(self) -> List[Dict[str, Any]]:

        """List all installed plugins"""

        return [

            {

                "name": name,

                **info

            }

            for name, info in self.installed_plugins.items()

        ]





class SecurityError(Exception):

    """Raised when a plugin fails security checks"""

    pass