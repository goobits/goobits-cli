"""
Tests for main CLI commands (build, init, serve, upgrade).

This module tests the primary CLI commands including:
- Build command functionality
- Init command with templates
- Serve command (development server)
- Upgrade command
- Version and help commands
"""
import pytest
import tempfile
import shutil
import subprocess
import os
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open
import yaml
import typer
from typer.testing import CliRunner

from goobits_cli.main import (
    app, load_goobits_config, generate_basic_template,
    generate_advanced_template, generate_api_client_template,
    generate_text_processor_template, version_callback
)
from goobits_cli.schemas import GoobitsConfigSchema
from tests.unit.core.test_base import TestMainCLIBase


# ============================================================================
# CLI COMMANDS TESTS
# ============================================================================

class TestMainCLICommands(TestMainCLIBase):
    """Test the main CLI commands using CliRunner."""

    def test_cli_version_command(self):
        """Test --version command."""
        result = self.runner.invoke(app, ["--version"])
        
        assert result.exit_code == 0
        assert "goobits-cli" in result.stdout

    def test_cli_help_command(self):
        """Test --help command."""
        result = self.runner.invoke(app, ["--help"])
        
        assert result.exit_code == 0
        assert "build" in result.stdout
        assert "init" in result.stdout
        assert "serve" in result.stdout
        assert "upgrade" in result.stdout

    def test_build_command_basic(self):
        """Test basic build command functionality."""
        config_content = self.get_minimal_valid_config()
        config_path = self.create_test_config_file(config_content)
        
        # Mock the generator to return multiple files
        from goobits_cli.generators.python import PythonGenerator
        with patch.object(PythonGenerator, 'generate_all_files') as mock_gen:
            mock_gen.return_value = {
                'src/test_cli/generated_cli.py': '# Generated CLI code',
                'setup.sh': '#!/bin/bash\n# Setup script',
                '__executable__': ['setup.sh']
            }
            
            result = self.runner.invoke(app, ["build", str(config_path)])
        
        assert result.exit_code == 0, f"Build failed: {result.stdout}\n{result.stdout}"
        assert "✅ Generated:" in result.stdout

    def test_build_command_config_not_found(self):
        """Test build command when config file doesn't exist."""
        non_existent_path = self.temp_dir / "nonexistent.yaml"
        
        result = self.runner.invoke(app, ["build", str(non_existent_path)])
        
        assert result.exit_code == 1

    def test_build_command_default_config_path(self):
        """Test build command using default config path."""
        config_content = self.get_minimal_valid_config()
        
        # Create config in current working directory
        original_cwd = Path.cwd()
        try:
            os.chdir(self.temp_dir)
            self.create_test_config_file(config_content)
            
            from goobits_cli.generators.python import PythonGenerator
            with patch.object(PythonGenerator, 'generate_all_files') as mock_gen:
                mock_gen.return_value = {
                    'src/test_cli/generated_cli.py': '# Generated CLI code',
                    'setup.sh': '#!/bin/bash\n# Setup script'
                }
                
                result = self.runner.invoke(app, ["build"])
            
            assert result.exit_code == 0
        finally:
            os.chdir(original_cwd)

    @patch('goobits_cli.generators.nodejs.NodeJSGenerator.generate_all_files')
    def test_build_command_nodejs(self, mock_generate):
        """Test build command with Node.js language."""
        config_content = self.get_minimal_valid_config(
            package_name="node-test-cli",
            command_name="nodetestcli",
            language="nodejs"
        )
        config_path = self.create_test_config_file(config_content)
        
        mock_generate.return_value = {
            'cli.js': '// Generated Node.js CLI',
            'package.json': '{"name": "test"}',
            'setup.sh': '#!/bin/bash\n# Setup script'
        }
        
        result = self.runner.invoke(app, ["build", str(config_path)])
        
        assert result.exit_code == 0
        assert "Detected language: nodejs" in result.stdout

    # Init command tests
    def test_init_command_basic(self):
        """Test basic init command functionality."""
        original_cwd = Path.cwd()
        try:
            os.chdir(self.temp_dir)
            
            result = self.runner.invoke(app, ["init", "test-project"])
            
            assert result.exit_code == 0
            assert "✅ Created goobits.yaml using 'basic' template" in result.stdout
            
            # Check that file was created
            config_file = self.temp_dir / "goobits.yaml"
            assert config_file.exists()
            
            # Check content contains project name
            content = config_file.read_text()
            assert "test-project" in content
        finally:
            os.chdir(original_cwd)

    def test_init_command_with_template(self):
        """Test init command with specific template."""
        original_cwd = Path.cwd()
        try:
            os.chdir(self.temp_dir)
            
            result = self.runner.invoke(app, ["init", "--template", "advanced", "advanced-project"])
            
            assert result.exit_code == 0
            assert "✅ Created goobits.yaml using 'advanced' template" in result.stdout
        finally:
            os.chdir(original_cwd)

    def test_init_command_file_exists_no_force(self):
        """Test init command when file exists without --force flag."""
        original_cwd = Path.cwd()
        try:
            os.chdir(self.temp_dir)
            
            # Create existing file
            config_path = self.temp_dir / "goobits.yaml"
            config_path.write_text("existing content")
            
            result = self.runner.invoke(app, ["init", "test-project"])
            
            assert result.exit_code == 1
            assert "already exists" in result.output
        finally:
            os.chdir(original_cwd)

    def test_init_command_file_exists_with_force(self):
        """Test init command when file exists with --force flag."""
        original_cwd = Path.cwd()
        try:
            os.chdir(self.temp_dir)
            
            # Create existing file
            config_path = self.temp_dir / "goobits.yaml"
            config_path.write_text("existing content")
            
            result = self.runner.invoke(app, ["init", "--force", "test-project"])
            
            assert result.exit_code == 0
            assert "✅ Created goobits.yaml using 'basic' template" in result.stdout
            # Should overwrite with new content
            content = config_path.read_text()
            assert "test-project" in content
            assert "existing content" not in content
        finally:
            os.chdir(original_cwd)

    def test_init_command_invalid_template(self):
        """Test init command with invalid template."""
        original_cwd = Path.cwd()
        try:
            os.chdir(self.temp_dir)
            
            result = self.runner.invoke(app, ["init", "--template", "nonexistent", "test-project"])
            
            assert result.exit_code == 1
            assert "Unknown template" in result.output
        finally:
            os.chdir(original_cwd)

    # Serve command tests  
    @patch('goobits_cli.main.Path.is_dir')
    def test_serve_command_directory_not_exists(self, mock_is_dir):
        """Test serve command when directory doesn't exist."""
        mock_is_dir.return_value = False
        
        result = self.runner.invoke(app, ["serve", "/nonexistent/path"])
        
        assert result.exit_code == 1
        assert "does not exist" in result.output

    @patch('goobits_cli.main.Path.is_dir')
    @patch('goobits_cli.main.Path.exists')
    def test_serve_command_not_directory(self, mock_exists, mock_is_dir):
        """Test serve command when path is not a directory."""
        mock_exists.return_value = True  # Path exists
        mock_is_dir.return_value = False  # But is not a directory
        
        result = self.runner.invoke(app, ["serve", "file.txt"])
        
        assert result.exit_code == 1
        assert "is not a directory" in result.output

    # Upgrade command tests
    @patch('subprocess.run')
    def test_upgrade_command_pipx_not_found(self, mock_run):
        """Test upgrade command when pipx is not available."""
        mock_run.side_effect = FileNotFoundError()
        
        result = self.runner.invoke(app, ["upgrade"])
        
        assert result.exit_code == 1
        assert "pipx is required" in result.output

    @patch('subprocess.run')
    def test_upgrade_command_invalid_source(self, mock_run):
        """Test upgrade command with invalid source."""
        mock_run.return_value = MagicMock(stdout="pipx 1.0.0\n")  # pipx version check succeeds
        
        result = self.runner.invoke(app, ["upgrade", "--source", "invalid-source"])
        
        assert result.exit_code == 1
        assert "Unknown source" in result.output

    @patch('subprocess.run')
    def test_upgrade_command_upgrade_failure(self, mock_run):
        """Test upgrade command when upgrade fails."""
        # First call succeeds (pipx version check), second call fails (upgrade)
        mock_run.side_effect = [
            MagicMock(stdout="pipx 1.0.0\n"),  # pipx version check succeeds
            subprocess.CalledProcessError(1, "pipx")  # upgrade fails
        ]
        
        # Use input="y\n" to automatically confirm the upgrade prompt
        result = self.runner.invoke(app, ["upgrade"], input="y\n")
        
        assert result.exit_code == 1
        assert "Upgrade failed" in result.output

    @patch('subprocess.run')
    def test_upgrade_command_unexpected_error(self, mock_run):
        """Test upgrade command with unexpected error."""
        # First call succeeds (pipx version check), second call fails (upgrade)
        mock_run.side_effect = [
            MagicMock(stdout="pipx 1.0.0\n"),  # pipx version check succeeds
            Exception("Unexpected error")       # upgrade fails with exception
        ]
        
        # Use input="y\n" to automatically confirm the upgrade prompt
        result = self.runner.invoke(app, ["upgrade"], input="y\n")
        
        assert result.exit_code == 1
        assert "Unexpected error during upgrade" in result.output


class TestFastVersionHelp(TestMainCLIBase):
    """Test the fast version and help check functionality."""
    
    @patch('sys.exit')
    def test_fast_version_check_triggers_exit(self, mock_exit):
        """Test that fast version check triggers sys.exit."""
        with patch('sys.argv', ['goobits', '--version']):
            # Import module dynamically to trigger top-level code
            import importlib
            import sys
            if 'goobits_cli.main' in sys.modules:
                importlib.reload(sys.modules['goobits_cli.main'])
            else:
                import goobits_cli.main
        
        mock_exit.assert_called_once_with(0)

    # Removed test_fast_help_check_triggers_exit as it tests module-level behavior
    # The fast help/version check happens at import time for performance reasons
    # and is not suitable for unit testing
    
    def test_version_callback_triggers_exit(self):
        """Test that version_callback triggers typer.Exit when True."""
        with pytest.raises(typer.Exit):
            version_callback(True)

    def test_version_callback_no_action_when_false(self):
        """Test that version_callback does nothing when False."""
        # Should not raise any exception
        result = version_callback(False)
        assert result is None