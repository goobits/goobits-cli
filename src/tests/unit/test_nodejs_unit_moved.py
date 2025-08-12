"""Unit tests for Node.js language detection and generator selection.

These tests verify individual functions related to Node.js language
detection and generator selection logic.
"""
import pytest
from pathlib import Path
import tempfile
import shutil

from goobits_cli.main import load_goobits_config
from conftest import determine_language, generate_cli


class TestNodeJSUnitMoved:
    """Unit tests for Node.js language detection and generator selection."""
    
    @classmethod
    def setup_class(cls):
        """Set up test fixtures for the class."""
        # Create a test YAML file for Node.js in goobits.yaml format
        cls.test_yaml_content = """
package_name: "node-test-cli"
command_name: "nodetestcli"
display_name: "NodeTestCLI"
description: "A Node.js test CLI for unit tests."
language: nodejs

python:
  minimum_version: "3.8"

dependencies:
  core: []

installation:
  pypi_name: "node-test-cli"
  github_repo: "example/node-test-cli"

shell_integration:
  alias: "ntc"

validation:
  minimum_disk_space_mb: 100

messages:
  install_success: "NodeTestCLI installed successfully!"

cli:
  name: "NodeTestCLI"
  tagline: "A Node.js test CLI for unit tests."
  version: "1.0.0"
  commands:
    serve:
      desc: "Start the server"
      options:
        - name: port
          short: p
          type: int
          desc: "Port to listen on"
          default: 3000
        - name: host
          short: h
          type: str
          desc: "Host to bind to"
          default: "localhost"
    build:
      desc: "Build the project"
      args:
        - name: target
          desc: "Build target"
          required: true
      options:
        - name: minify
          type: flag
          desc: "Minify output"
        - name: watch
          short: w
          type: flag
          desc: "Watch for changes"
"""
        
        # Create temporary directory for tests
        cls.temp_dir = tempfile.mkdtemp(prefix="nodejs_unit_test_")
        cls.test_yaml_path = Path(cls.temp_dir) / "test_nodejs.yaml"
        
        # Write test YAML
        with open(cls.test_yaml_path, 'w') as f:
            f.write(cls.test_yaml_content)
    
    @classmethod
    def teardown_class(cls):
        """Clean up test fixtures."""
        if Path(cls.temp_dir).exists():
            shutil.rmtree(cls.temp_dir)
    
    def test_language_detection_nodejs(self):
        """Test that Node.js language is correctly detected from config."""
        config = load_goobits_config(self.test_yaml_path)
        language = determine_language(config)
        
        assert language == "nodejs"
    
    def test_nodejs_generator_selection(self):
        """Test that NodeJSGenerator is selected for Node.js language."""
        config = load_goobits_config(self.test_yaml_path)
        
        # The main generate_cli function should use NodeJSGenerator
        output_files = generate_cli(config, "test_nodejs.yaml")
        
        # Check that we get Node.js files, not Python files
        assert 'index.js' in output_files
        assert 'package.json' in output_files
        assert 'setup.sh' in output_files
        
        # Should NOT have Python files
        assert 'cli.py' not in output_files
        assert 'requirements.txt' not in output_files