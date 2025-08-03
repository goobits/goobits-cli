"""End-to-end tests for Node.js CLI generation and execution.

These tests simulate the complete workflow:
1. Load Node.js YAML configuration
2. Generate Node.js CLI code through goobits
3. Write files to temporary directory
4. Execute generated CLI (if Node.js is available)
5. Verify output and behavior
"""
import pytest
import subprocess
import tempfile
import json
from pathlib import Path
import sys
import shutil
import os

from goobits_cli.main import load_goobits_config
from tests.helpers import generate_cli


class TestNodeJSE2E:
    """End-to-end tests for Node.js CLI generation and execution."""
    
    @pytest.fixture(scope="class")
    def nodejs_config(self):
        """Load the Node.js test YAML configuration."""
        config_path = Path(__file__).parent.parent / "integration" / "test_nodejs.yaml"
        return load_goobits_config(config_path)
    
    @pytest.fixture(scope="class")
    def generated_nodejs_files(self, nodejs_config):
        """Generate Node.js CLI files from test configuration."""
        return generate_cli(nodejs_config, "test_nodejs.yaml")
    
    @pytest.fixture(scope="class")
    def temp_nodejs_project(self, generated_nodejs_files):
        """Create temporary Node.js project with generated files."""
        with tempfile.TemporaryDirectory(prefix="nodejs_e2e_test_") as temp_dir:
            project_path = Path(temp_dir)
            
            # Write all generated files
            for filename, content in generated_nodejs_files.items():
                file_path = project_path / filename
                file_path.parent.mkdir(parents=True, exist_ok=True)
                file_path.write_text(content)
                
                # Make scripts executable
                if filename.endswith('.sh') or filename == 'index.js':
                    file_path.chmod(0o755)
            
            # Install npm dependencies if Node.js and npm are available
            if shutil.which("node") and shutil.which("npm"):
                result = subprocess.run(
                    ["npm", "install"],
                    cwd=str(project_path),
                    capture_output=True,
                    text=True
                )
                # Note: Don't fail if npm install fails - some tests check error conditions
                if result.returncode != 0:
                    print(f"Warning: npm install failed: {result.stderr}")
            
            yield project_path
    
    def test_generated_files_exist(self, temp_nodejs_project):
        """Test that all expected files are generated."""
        expected_files = ['index.js', 'package.json', 'setup.sh', 'README.md']
        
        for filename in expected_files:
            file_path = temp_nodejs_project / filename
            assert file_path.exists(), f"{filename} should exist"
            assert file_path.stat().st_size > 0, f"{filename} should not be empty"
    
    def test_package_json_is_valid(self, temp_nodejs_project):
        """Test that package.json is valid and contains expected fields."""
        package_json_path = temp_nodejs_project / "package.json"
        
        # Read and parse package.json
        with open(package_json_path) as f:
            package_data = json.load(f)
        
        # Verify structure
        assert package_data['name'] == 'nodejs-test-cli'
        assert package_data['version'] == '1.2.3'
        assert 'commander' in package_data['dependencies']
        assert 'bin' in package_data
        assert 'scripts' in package_data
    
    @pytest.mark.skipif(shutil.which('node') is None, reason="Node.js not installed")
    def test_nodejs_cli_help(self, temp_nodejs_project):
        """Test generated CLI help output with Node.js."""
        result = subprocess.run(
            ['node', 'index.js', '--help'],
            cwd=temp_nodejs_project,
            capture_output=True,
            text=True
        )
        
        # Check execution succeeded
        assert result.returncode == 0
        
        # Verify help content
        assert "NodeJSTestCLI" in result.stdout
        assert "A comprehensive Node.js CLI" in result.stdout
        assert "init" in result.stdout
        assert "deploy" in result.stdout
        assert "server" in result.stdout
        assert "database" in result.stdout
        assert "test" in result.stdout
    
    @pytest.mark.skipif(shutil.which('node') is None, reason="Node.js not installed")
    def test_nodejs_cli_version(self, temp_nodejs_project):
        """Test version flag with Node.js."""
        result = subprocess.run(
            ['node', 'index.js', '--version'],
            cwd=temp_nodejs_project,
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0
        assert "1.2.3" in result.stdout
    
    @pytest.mark.skipif(shutil.which('node') is None, reason="Node.js not installed")
    def test_nodejs_cli_command_help(self, temp_nodejs_project):
        """Test command-specific help with Node.js."""
        result = subprocess.run(
            ['node', 'index.js', 'deploy', '--help'],
            cwd=temp_nodejs_project,
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0
        assert "Deploy the application" in result.stdout
        assert "environment" in result.stdout
        assert "--force" in result.stdout
        assert "--dry-run" in result.stdout
    
    @pytest.mark.skipif(shutil.which('node') is None, reason="Node.js not installed")
    def test_nodejs_cli_subcommand_help(self, temp_nodejs_project):
        """Test subcommand help with Node.js."""
        result = subprocess.run(
            ['node', 'index.js', 'server', 'start', '--help'],
            cwd=temp_nodejs_project,
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0
        assert "Start the server" in result.stdout
        assert "--port" in result.stdout
        assert "--daemon" in result.stdout
    
    @pytest.mark.skipif(shutil.which('node') is None, reason="Node.js not installed")
    def test_nodejs_cli_missing_required_arg(self, temp_nodejs_project):
        """Test error handling for missing required arguments with Node.js."""
        result = subprocess.run(
            ['node', 'index.js', 'init'],  # Missing required 'name' argument
            cwd=temp_nodejs_project,
            capture_output=True,
            text=True
        )
        
        # Should fail
        assert result.returncode != 0
        assert "error" in result.stderr.lower() or "required" in result.stderr.lower()
    
    @pytest.mark.skipif(shutil.which('npm') is None, reason="npm not installed")
    def test_setup_script_execution(self, temp_nodejs_project):
        """Test setup.sh script execution."""
        setup_script = temp_nodejs_project / "setup.sh"
        
        # Make sure it's executable
        setup_script.chmod(0o755)
        
        # Test dry run (don't actually install)
        result = subprocess.run(
            ['bash', '-n', str(setup_script)],  # -n for syntax check only
            capture_output=True,
            text=True
        )
        
        # Should have valid bash syntax
        assert result.returncode == 0
    
    def test_readme_generation(self, temp_nodejs_project):
        """Test README.md content generation."""
        readme_path = temp_nodejs_project / "README.md"
        readme_content = readme_path.read_text()
        
        # Check structure
        assert "# NodeJSTestCLI" in readme_content
        assert "## Installation" in readme_content
        assert "## Usage" in readme_content
        assert "## Commands" in readme_content
        
        # Check basic structure
        assert "Installation" in readme_content
        assert "Usage" in readme_content
    
    @pytest.mark.skipif(shutil.which('node') is None, reason="Node.js not installed")
    def test_global_options_inheritance(self, temp_nodejs_project):
        """Test that global options work with commands."""
        result = subprocess.run(
            ['node', 'index.js', '--verbose', 'test', '--help'],
            cwd=temp_nodejs_project,
            capture_output=True,
            text=True
        )
        
        # Should succeed and show test command help
        assert result.returncode == 0
        assert "Run tests" in result.stdout
    
    def test_complex_yaml_to_nodejs_workflow(self):
        """Test the complete workflow with a complex YAML configuration."""
        # Create a complex YAML configuration
        complex_yaml = """
package_name: "complex-node-cli"
command_name: "complexnodecli"
display_name: "ComplexNodeCLI"
description: "Complex Node.js CLI for E2E testing"
language: nodejs

python:
  minimum_version: "3.8"

dependencies:
  core: []

installation:
  pypi_name: "complex-node-cli"
  github_repo: "example/complex-node-cli"

shell_integration:
  alias: "cnc"

validation:
  minimum_disk_space_mb: 100

messages:
  install_success: "ComplexNodeCLI installed successfully!"

cli:
  name: "ComplexNodeCLI"
  tagline: "Complex Node.js CLI for E2E testing"
  version: "3.0.0"
  options:
    - name: debug
      type: flag
      desc: "Enable debug mode"
  commands:
    api:
      desc: "API management"
      subcommands:
        generate:
          desc: "Generate API client"
          args:
            - name: spec
              desc: "OpenAPI spec file"
              required: true
          options:
            - name: output
              type: str
              desc: "Output directory"
              default: "./generated"
            - name: language
              type: str
              desc: "Target language"
              default: "typescript"
        validate:
          desc: "Validate API spec"
          args:
            - name: file
              desc: "Spec file to validate"
              required: true
"""
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Write YAML
            yaml_path = Path(temp_dir) / "complex.yaml"
            yaml_path.write_text(complex_yaml)
            
            # Load and generate
            config = load_goobits_config(yaml_path)
            output_files = generate_cli(config, "complex.yaml")
            
            # Write output files
            for filename, content in output_files.items():
                file_path = Path(temp_dir) / filename
                file_path.parent.mkdir(parents=True, exist_ok=True)
                file_path.write_text(content)
            
            # Verify generation
            assert (Path(temp_dir) / "index.js").exists()
            assert (Path(temp_dir) / "package.json").exists()
            
            # Test with Node.js if available
            if shutil.which('node') and shutil.which('npm'):
                # Install npm dependencies
                install_result = subprocess.run(
                    ['npm', 'install'],
                    cwd=temp_dir,
                    capture_output=True,
                    text=True
                )
                assert install_result.returncode == 0, f"npm install failed: {install_result.stderr}"
                
                # Test CLI execution
                result = subprocess.run(
                    ['node', 'index.js', 'api', 'generate', '--help'],
                    cwd=temp_dir,
                    capture_output=True,
                    text=True
                )
                
                assert result.returncode == 0
                assert "Generate API client" in result.stdout
                assert "spec" in result.stdout
                assert "--output" in result.stdout
    
    @pytest.mark.skipif(shutil.which('node') is None, reason="Node.js not installed")
    def test_command_execution_simulation(self, temp_nodejs_project):
        """Test that commands execute without errors (simulation mode)."""
        # Test simple command
        result = subprocess.run(
            ['node', 'index.js', 'test', 'unit'],
            cwd=temp_nodejs_project,
            capture_output=True,
            text=True
        )
        
        # Commands should execute (even if they just print messages)
        assert result.returncode == 0
        
        # Test command with options
        result = subprocess.run(
            ['node', 'index.js', 'server', 'start', '--port', '9000'],
            cwd=temp_nodejs_project,
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0
    
    def test_nodejs_vs_python_generation_difference(self):
        """Test that Node.js and Python generation produce different outputs."""
        # Create two configs, one for each language
        nodejs_yaml = """
package_name: "test-cli"
command_name: "testcli"
display_name: "TestCLI"
description: "Test CLI"
language: nodejs

python:
  minimum_version: "3.8"

dependencies:
  core: []

installation:
  pypi_name: "test-cli"
  github_repo: "example/test-cli"

shell_integration:
  alias: "tc"

validation:
  minimum_disk_space_mb: 100

messages:
  install_success: "TestCLI installed successfully!"

cli:
  name: "TestCLI"
  tagline: "Test CLI"
  commands:
    hello:
      desc: "Say hello"
"""
        
        python_yaml = """
package_name: "test-cli"
command_name: "testcli"
display_name: "TestCLI"
description: "Test CLI"

python:
  minimum_version: "3.8"

dependencies:
  core: []

installation:
  pypi_name: "test-cli"
  github_repo: "example/test-cli"

shell_integration:
  alias: "tc"

validation:
  minimum_disk_space_mb: 100

messages:
  install_success: "TestCLI installed successfully!"

cli:
  name: "TestCLI"
  tagline: "Test CLI"
  commands:
    hello:
      desc: "Say hello"
"""
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Generate Node.js version
            nodejs_yaml_path = Path(temp_dir) / "nodejs.yaml"
            nodejs_yaml_path.write_text(nodejs_yaml)
            nodejs_config = load_goobits_config(nodejs_yaml_path)
            nodejs_files = generate_cli(nodejs_config, "nodejs.yaml")
            
            # Generate Python version
            python_yaml_path = Path(temp_dir) / "python.yaml"
            python_yaml_path.write_text(python_yaml)
            python_config = load_goobits_config(python_yaml_path)
            python_files = generate_cli(python_config, "python.yaml")
            
            # Verify different outputs
            assert 'index.js' in nodejs_files
            assert 'package.json' in nodejs_files
            assert 'index.js' not in python_files
            assert 'package.json' not in python_files
            
            # Python should have different files
            assert len(python_files) >= 1  # At least the CLI script