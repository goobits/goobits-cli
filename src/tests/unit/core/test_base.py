"""
Base test class for main CLI functionality.

This module provides the shared TestMainCLIBase class that contains
common setup, teardown, and helper methods used by multiple test modules.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from typer.testing import CliRunner


class TestMainCLIBase:
    """Base test class with shared setup and helper methods."""

    def setup_method(self):
        """Set up test environment."""
        self.runner = CliRunner()
        self.temp_dir = Path(tempfile.mkdtemp())

    def teardown_method(self):
        """Clean up test environment."""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    def create_test_config_file(
        self, content: str, filename: str = "goobits.yaml"
    ) -> Path:
        """Create a test configuration file."""
        config_path = self.temp_dir / filename
        with open(config_path, "w") as f:
            f.write(content)
        return config_path

    def get_minimal_valid_config(
        self,
        package_name="test-cli",
        command_name="testcli",
        language="python",
        include_cli=True,
    ):
        """Get minimal valid config with all required fields."""
        config = f"""
package_name: {package_name}
command_name: {command_name}
display_name: "Test CLI"
description: "A test CLI"
language: {language}

python:
  minimum_version: "3.8"

dependencies:
  required:
    - pipx

installation:
  pypi_name: "{package_name}"

shell_integration:
  enabled: false
  alias: "{command_name}"

validation:
  check_api_keys: false
  check_disk_space: true
  minimum_disk_space_mb: 100

messages:
  install_success: "Installation completed successfully!"
"""
        if include_cli:
            config += f"""
cli:
  name: {command_name}
  tagline: "Test CLI tool"
  commands:
    hello:
      desc: "Say hello"
      is_default: true
"""
        return config

    @pytest.fixture
    def basic_config_content(self):
        """Basic valid goobits.yaml content."""
        return """
package_name: test-cli
command_name: testcli
display_name: "Test CLI"
description: "A test CLI"
language: python

python:
  minimum_version: "3.8"

dependencies:
  required:
    - pipx

installation:
  pypi_name: "test-cli"

shell_integration:
  enabled: false
  alias: "testcli"

validation:
  check_api_keys: false
  check_disk_space: true
  minimum_disk_space_mb: 100

messages:
  install_success: "Installation completed successfully!"

cli:
  name: testcli
  tagline: "Test CLI tool"
  commands:
    hello:
      desc: "Say hello"
      is_default: true
      args:
        - name: name
          desc: "Name to greet"
          required: false
"""

    @pytest.fixture
    def nodejs_config_content(self):
        """Node.js goobits.yaml content."""
        return """
package_name: node-test-cli
command_name: nodetestcli  
display_name: "Node Test CLI"
description: "A Node.js test CLI"
language: nodejs

python:
  minimum_version: "3.8"

dependencies:
  required:
    - node
    - npm

installation:
  pypi_name: "node-test-cli"

shell_integration:
  enabled: false
  alias: "nodetestcli"

validation:
  check_api_keys: false
  check_disk_space: true
  minimum_disk_space_mb: 100

messages:
  install_success: "Installation completed successfully!"

cli:
  name: nodetestcli
  tagline: "Node.js Test CLI tool"  
  commands:
    hello:
      desc: "Say hello"
      is_default: true
"""
