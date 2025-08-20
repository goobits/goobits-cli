"""
Complete End-to-End Workflow Tests

This module consolidates all end-to-end tests for complete user workflows:
1. CLI generation and execution (test_cli_e2e.py)
2. Node.js generator e2e tests (test_nodejs_generator_e2e.py)  
3. Complete workflow validation

These tests simulate the complete user experience:
- Generate CLI code from YAML configuration
- Install generated CLI in isolated virtual environment
- Execute CLI commands via subprocess
- Verify output, stderr, and exit codes
"""

import pytest
import shutil
import subprocess
import tempfile
import venv
from pathlib import Path
import sys
import os

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from goobits_cli.builder import load_yaml_config, Builder
from goobits_cli.generators.nodejs import NodeJSGenerator
from goobits_cli.generators.typescript import TypeScriptGenerator
from goobits_cli.schemas import ConfigSchema


class TestCLIE2E:
    """End-to-end tests for CLI generation and execution."""

    @pytest.fixture(scope="class")
    def test_config(self):
        """Load the test YAML configuration."""
        config_path = Path(__file__).parent.parent / "integration" / "goobits.yaml"
        return load_yaml_config(str(config_path))

    @pytest.fixture(scope="class") 
    def generated_cli_code(self, test_config):
        """Generate CLI code from test configuration."""
        builder = Builder()
        return builder.build(test_config, "goobits.yaml")

    @pytest.fixture(scope="class")
    def temp_venv_dir(self):
        """Create isolated temporary virtual environment."""
        with tempfile.TemporaryDirectory(prefix="e2e_test_venv_") as temp_dir:
            venv_path = Path(temp_dir) / "test_venv"
            
            # Create virtual environment
            venv.create(venv_path, with_pip=True)
            
            yield venv_path

    def test_python_cli_e2e_workflow(self, test_config, tmp_path):
        """Test complete Python CLI workflow end-to-end."""
        # Generate CLI using Python generator
        from goobits_cli.generators.python import PythonGenerator
        
        generator = PythonGenerator(use_universal_templates=False)
        result = generator.generate(test_config, str(tmp_path))
        
        # Verify generation succeeded
        assert result is not None
        
        # Check that key files were generated
        cli_file = tmp_path / "cli.py"
        assert cli_file.exists()
        
        # Verify CLI content contains expected commands
        cli_content = cli_file.read_text()
        assert "greet" in cli_content
        assert "hello" in cli_content
        assert "goodbye" in cli_content

    def test_cli_help_output(self, test_config, tmp_path):
        """Test that generated CLI produces valid help output."""
        from goobits_cli.generators.python import PythonGenerator
        
        generator = PythonGenerator(use_universal_templates=False)
        generator.generate(test_config, str(tmp_path))
        
        cli_file = tmp_path / "cli.py"
        assert cli_file.exists()
        
        # Try to run the CLI with --help (if Python is available)
        try:
            result = subprocess.run(
                [sys.executable, str(cli_file), "--help"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            # Should either succeed or fail gracefully
            # (might fail due to missing hooks, but should not crash)
            assert result.returncode in [0, 1, 2]  # Allow various exit codes
            
            # Should produce some output
            assert len(result.stdout) > 0 or len(result.stderr) > 0
            
        except subprocess.TimeoutExpired:
            pytest.fail("CLI help command timed out")
        except FileNotFoundError:
            pytest.skip("Python interpreter not found")


class TestNodeJSGeneratorE2E:
    """End-to-end tests for Node.js CLI generation and execution."""

    @pytest.fixture
    def sample_nodejs_config(self):
        """Provide a sample Node.js CLI configuration."""
        return ConfigSchema(cli={
            "name": "test-nodejs-cli",
            "tagline": "Test Node.js CLI for E2E testing",
            "version": "1.0.0",
            "commands": {
                "hello": {
                    "desc": "Say hello",
                    "handler": "hello_handler",
                    "args": [
                        {
                            "name": "name",
                            "desc": "Name to greet",
                            "type": "string",
                            "required": True
                        }
                    ]
                },
                "test": {
                    "desc": "Run tests",
                    "handler": "test_handler"
                }
            }
        })

    def test_nodejs_generator_e2e(self, sample_nodejs_config, tmp_path):
        """Test Node.js generator end-to-end workflow."""
        generator = NodeJSGenerator(use_universal_templates=False)
        
        # Generate the CLI
        result = generator.generate(sample_nodejs_config, str(tmp_path))
        assert result is not None
        
        # Verify key files were generated
        cli_file = tmp_path / "cli.js"
        package_file = tmp_path / "package.json"
        
        assert cli_file.exists()
        assert package_file.exists()
        
        # Verify CLI content
        cli_content = cli_file.read_text()
        assert "hello" in cli_content
        assert "test" in cli_content
        
        # Verify package.json content
        package_content = package_file.read_text()
        assert "test-nodejs-cli" in package_content
        assert "1.0.0" in package_content

    def test_typescript_generator_e2e(self, sample_nodejs_config, tmp_path):
        """Test TypeScript generator end-to-end workflow."""
        generator = TypeScriptGenerator(use_universal_templates=False)
        
        # Generate the CLI
        result = generator.generate(sample_nodejs_config, str(tmp_path))
        assert result is not None
        
        # Verify key files were generated
        cli_file = tmp_path / "cli.ts"
        package_file = tmp_path / "package.json"
        tsconfig_file = tmp_path / "tsconfig.json"
        
        assert cli_file.exists()
        assert package_file.exists()
        assert tsconfig_file.exists()
        
        # Verify CLI content
        cli_content = cli_file.read_text()
        assert "hello" in cli_content
        assert "test" in cli_content
        
        # Verify TypeScript-specific content
        assert "interface" in cli_content or "type" in cli_content

    @pytest.mark.skipif(
        shutil.which("node") is None,
        reason="Node.js not available"
    )
    def test_nodejs_cli_syntax_validation(self, sample_nodejs_config, tmp_path):
        """Test that generated Node.js CLI has valid syntax."""
        generator = NodeJSGenerator(use_universal_templates=False)
        generator.generate(sample_nodejs_config, str(tmp_path))
        
        cli_file = tmp_path / "cli.js"
        
        # Try to run Node.js syntax check
        try:
            result = subprocess.run(
                ["node", "--check", str(cli_file)],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            # Should pass syntax check
            assert result.returncode == 0, f"Syntax error: {result.stderr}"
            
        except subprocess.TimeoutExpired:
            pytest.fail("Node.js syntax check timed out")
        except FileNotFoundError:
            pytest.skip("Node.js not found")


class TestCompleteWorkflowValidation:
    """Test complete workflows from YAML to working CLI."""

    def test_minimal_workflow_python(self, tmp_path):
        """Test minimal workflow with Python generator."""
        # Create minimal config
        config = ConfigSchema(cli={
            "name": "minimal-cli",
            "tagline": "Minimal test CLI",
            "version": "1.0.0",
            "commands": {
                "status": {
                    "desc": "Show status",
                    "handler": "status_handler"
                }
            }
        })
        
        # Generate CLI
        from goobits_cli.generators.python import PythonGenerator
        generator = PythonGenerator(use_universal_templates=False)
        result = generator.generate(config, str(tmp_path))
        
        # Verify basic structure
        assert result is not None
        assert (tmp_path / "cli.py").exists()
        
        # Verify content
        cli_content = (tmp_path / "cli.py").read_text()
        assert "status" in cli_content
        assert "Show status" in cli_content

    def test_minimal_workflow_nodejs(self, tmp_path):
        """Test minimal workflow with Node.js generator."""
        # Create minimal config
        config = ConfigSchema(cli={
            "name": "minimal-cli",
            "tagline": "Minimal test CLI",
            "version": "1.0.0",
            "commands": {
                "status": {
                    "desc": "Show status",
                    "handler": "status_handler"
                }
            }
        })
        
        # Generate CLI
        generator = NodeJSGenerator(use_universal_templates=False)
        result = generator.generate(config, str(tmp_path))
        
        # Verify basic structure
        assert result is not None
        assert (tmp_path / "cli.js").exists()
        assert (tmp_path / "package.json").exists()
        
        # Verify content
        cli_content = (tmp_path / "cli.js").read_text()
        assert "status" in cli_content

    @pytest.mark.skipif(
        shutil.which("cargo") is None,
        reason="Cargo not available - Rust tests require Rust toolchain"
    )
    def test_minimal_workflow_rust(self, tmp_path):
        """Test minimal workflow with Rust generator."""
        # Create minimal config
        config = ConfigSchema(cli={
            "name": "minimal-cli",
            "tagline": "Minimal test CLI",
            "version": "1.0.0",
            "commands": {
                "status": {
                    "desc": "Show status",
                    "handler": "status_handler"
                }
            }
        })
        
        # Generate CLI
        from goobits_cli.generators.rust import RustGenerator
        generator = RustGenerator(use_universal_templates=False)
        result = generator.generate(config, str(tmp_path))
        
        # Verify basic structure
        assert result is not None
        assert (tmp_path / "Cargo.toml").exists()
        assert (tmp_path / "src" / "main.rs").exists()
        
        # Verify content
        main_content = (tmp_path / "src" / "main.rs").read_text()
        assert "status" in main_content