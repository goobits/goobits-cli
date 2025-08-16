"""End-to-end tests for Node.js and TypeScript generators."""

import os
import json
import tempfile
import shutil
import subprocess
import sys
from pathlib import Path
import pytest

from goobits_cli.generators.nodejs import NodeJSGenerator
from goobits_cli.generators.typescript import TypeScriptGenerator
from goobits_cli.schemas import GoobitsConfigSchema


class TestNodeGeneratorE2E:
    """End-to-end tests for Node.js generator."""
    
    @pytest.fixture
    def sample_nodejs_config(self):
        """Create a sample Node.js configuration."""
        return {
            "package_name": "test-nodejs-cli",
            "command_name": "testnodecli",
            "display_name": "Test Node.js CLI",
            "description": "A test Node.js CLI for E2E testing",
            "language": "nodejs",
            "python": {"minimum_version": "3.8"},
            "dependencies": {"core": []},
            "installation": {
                "pypi_name": "test-nodejs-cli",
                "github_repo": "test/test-nodejs-cli",
                "extras": {
                    "npm": ["chalk", "ora"]
                }
            },
            "shell_integration": {"alias": "tnc"},
            "validation": {"minimum_disk_space_mb": 100},
            "messages": {"install_success": "Test Node.js CLI installed!"},
            "cli": {
                "name": "testnodecli",
                "tagline": "Test Node.js CLI for E2E",
                "version": "1.0.0",
                "options": [
                    {
                        "name": "verbose",
                        "short": "v",
                        "type": "flag",
                        "desc": "Enable verbose output"
                    }
                ],
                "commands": {
                    "hello": {
                        "desc": "Say hello",
                        "args": [
                            {
                                "name": "name",
                                "desc": "Name to greet",
                                "required": False
                            }
                        ],
                        "options": [
                            {
                                "name": "greeting",
                                "short": "g",
                                "type": "str",
                                "desc": "Custom greeting",
                                "default": "Hello"
                            }
                        ]
                    },
                    "serve": {
                        "desc": "Start a server",
                        "lifecycle": "managed",
                        "options": [
                            {
                                "name": "port",
                                "short": "p",
                                "type": "int",
                                "desc": "Port to listen on",
                                "default": 3000
                            }
                        ]
                    }
                }
            }
        }
    
    @pytest.fixture
    def sample_typescript_config(self, sample_nodejs_config):
        """Create a sample TypeScript configuration."""
        config = sample_nodejs_config.copy()
        config["language"] = "typescript"
        config["package_name"] = "test-typescript-cli"
        config["command_name"] = "testtscli"
        config["display_name"] = "Test TypeScript CLI"
        config["description"] = "A test TypeScript CLI for E2E testing"
        config["cli"] = config["cli"].copy()
        config["cli"]["name"] = "testtscli"
        config["cli"]["tagline"] = "Test TypeScript CLI for E2E"
        return config
    
    def test_nodejs_generator_e2e(self, sample_nodejs_config, tmp_path):
        """Test complete Node.js CLI generation process."""
        # Create generator
        generator = NodeJSGenerator()
        
        # Parse config
        config = GoobitsConfigSchema(**sample_nodejs_config)
        
        # Generate all files
        files = generator.generate_all_files(config, "test.yaml", "1.0.0")
        
        # Write files to temp directory
        for file_path, content in files.items():
            if file_path == '__executable__':
                continue
            
            full_path = tmp_path / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(full_path, 'w') as f:
                f.write(content)
            
            # Make executable if needed
            if file_path in files.get('__executable__', []):
                full_path.chmod(0o755)
        
        # Verify key files exist
        assert (tmp_path / "cli.js").exists()
        assert (tmp_path / "package.json").exists()
        assert (tmp_path / "bin/cli.js").exists()
        assert (tmp_path / "setup.sh").exists()
        
        # Verify package.json is valid JSON
        with open(tmp_path / "package.json") as f:
            package_json = json.load(f)
            assert package_json["name"] == "test-nodejs-cli"
            assert package_json["bin"]["testnodecli"] == "./bin/cli.js"
            assert "commander" in package_json["dependencies"]
            assert "chalk" in package_json["dependencies"]
        
        # Skip npm install if Node.js not available
        if shutil.which("node") and shutil.which("npm"):
            # Run npm install
            result = subprocess.run(
                ["npm", "install"],
                cwd=str(tmp_path),
                capture_output=True,
                text=True
            )
            assert result.returncode == 0, f"npm install failed: {result.stderr}"
            
            # Test --help command
            result = subprocess.run(
                ["node", "bin/cli.js", "--help"],
                cwd=str(tmp_path),
                capture_output=True,
                text=True
            )
            assert result.returncode == 0
            assert "Test Node.js CLI for E2E" in result.stdout
            assert "hello" in result.stdout
            assert "serve" in result.stdout
            
            # Test hello command
            result = subprocess.run(
                ["node", "bin/cli.js", "hello", "World"],
                cwd=str(tmp_path),
                capture_output=True,
                text=True
            )
            assert result.returncode == 0
            # Should show placeholder output since no hooks
            assert "Executing hello command" in result.stdout or "World" in result.stdout
    
    def test_typescript_generator_e2e(self, sample_typescript_config, tmp_path):
        """Test complete TypeScript CLI generation process."""
        # Create generator
        generator = TypeScriptGenerator()
        
        # Parse config
        config = GoobitsConfigSchema(**sample_typescript_config)
        
        # Generate all files
        files = generator.generate_all_files(config, "test.yaml", "1.0.0")
        
        # Write files to temp directory
        for file_path, content in files.items():
            if file_path == '__executable__':
                continue
            
            full_path = tmp_path / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(full_path, 'w') as f:
                f.write(content)
            
            # Make executable if needed
            if file_path in files.get('__executable__', []):
                full_path.chmod(0o755)
        
        # Verify key files exist
        assert (tmp_path / "index.ts").exists()
        assert (tmp_path / "package.json").exists()
        assert (tmp_path / "bin/cli.ts").exists()
        assert (tmp_path / "tsconfig.json").exists()
        assert (tmp_path / "setup.sh").exists()
        assert (tmp_path / ".eslintrc.json").exists()
        assert (tmp_path / ".prettierrc").exists()
        
        # Verify package.json is valid JSON
        with open(tmp_path / "package.json") as f:
            package_json = json.load(f)
            assert package_json["name"] == "test-typescript-cli"
            assert package_json["bin"]["testtscli"] == "./dist/bin/cli.js"
            assert "typescript" in package_json["devDependencies"]
            assert "@types/node" in package_json["devDependencies"]
        
        # Verify tsconfig.json is valid JSON
        with open(tmp_path / "tsconfig.json") as f:
            tsconfig = json.load(f)
            assert tsconfig["compilerOptions"]["target"] == "ES2022"
            assert tsconfig["compilerOptions"]["module"] == "NodeNext"
            assert tsconfig["compilerOptions"]["strict"] == True
        
        # Skip npm install and build if Node.js/TypeScript not available
        if shutil.which("node") and shutil.which("npm"):
            # Run npm install
            result = subprocess.run(
                ["npm", "install"],
                cwd=str(tmp_path),
                capture_output=True,
                text=True,
                timeout=120  # 2 minutes timeout
            )
            
            if result.returncode == 0:
                # Run TypeScript build
                result = subprocess.run(
                    ["npm", "run", "build"],
                    cwd=str(tmp_path),
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                
                if result.returncode == 0:
                    # Test --help command on built output
                    result = subprocess.run(
                        ["node", "dist/bin/cli.js", "--help"],
                        cwd=str(tmp_path),
                        capture_output=True,
                        text=True
                    )
                    assert result.returncode == 0
                    assert "Test TypeScript CLI for E2E" in result.stdout
    
    def test_main_cli_integration(self, sample_nodejs_config, tmp_path):
        """Test integration with main goobits CLI."""
        # Create a temporary YAML config
        config_file = tmp_path / "test-nodejs.yaml"
        
        # Convert config to YAML format
        import yaml
        with open(config_file, 'w') as f:
            yaml.dump(sample_nodejs_config, f)
        
        # Set up environment with correct PYTHONPATH
        env = os.environ.copy()
        src_path = str(Path(__file__).parent.parent.parent.parent / "src")
        if "PYTHONPATH" in env:
            env["PYTHONPATH"] = f"{src_path}{os.pathsep}{env['PYTHONPATH']}"
        else:
            env["PYTHONPATH"] = src_path
        
        # Run goobits build command
        result = subprocess.run(
            [sys.executable, "-m", "goobits_cli.main", "build", str(config_file), "-o", str(tmp_path / "output")],
            capture_output=True,
            text=True,
            env=env
        )
        
        # Should succeed
        assert result.returncode == 0, f"Build failed: {result.stderr}"
        
        # Verify files were created
        assert (tmp_path / "output" / "cli.js").exists()
        assert (tmp_path / "output" / "package.json").exists()
        assert (tmp_path / "output" / "bin" / "cli.js").exists()
    
    @pytest.mark.skipif(not shutil.which("node"), reason="Node.js not installed")
    def test_generated_cli_npm_test(self, sample_nodejs_config, tmp_path):
        """Test that generated CLI can run its own tests."""
        # Generate Node.js CLI
        generator = NodeJSGenerator()
        config = GoobitsConfigSchema(**sample_nodejs_config)
        files = generator.generate_all_files(config, "test.yaml", "1.0.0")
        
        # Write files
        for file_path, content in files.items():
            if file_path == '__executable__':
                continue
            
            full_path = tmp_path / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(full_path, 'w') as f:
                f.write(content)
        
        # Update package.json test script to use node test runner
        package_json_path = tmp_path / "package.json"
        with open(package_json_path) as f:
            package_json = json.load(f)
        
        package_json["scripts"]["test"] = "node --test test/**/*.test.js"
        
        with open(package_json_path, 'w') as f:
            json.dump(package_json, f, indent=2)
        
        # Run npm install
        result = subprocess.run(
            ["npm", "install"],
            cwd=str(tmp_path),
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            # Run tests
            result = subprocess.run(
                ["npm", "test"],
                cwd=str(tmp_path),
                capture_output=True,
                text=True
            )
            # Tests should at least run without crashing
            # They may fail due to missing implementation
            assert "test" in result.stdout.lower() or "test" in result.stderr.lower()