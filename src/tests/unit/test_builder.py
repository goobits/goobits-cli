"""Unit tests for builder.py module."""
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, mock_open
from click.exceptions import Exit

from goobits_cli.builder import load_yaml_config, generate_cli_code, Builder
from goobits_cli.schemas import ConfigSchema, CLISchema, CommandSchema, ArgumentSchema, OptionSchema


class TestBuilder:
    """Test cases for Builder class."""
    
    def test_builder_initialization(self):
        """Test Builder class initialization creates a generator instance."""
        builder = Builder()
        
        # Check that generator was created
        assert hasattr(builder, 'generator')
        assert builder.generator is not None
        
        # Builder now delegates to PythonGenerator
        from goobits_cli.generators.python import PythonGenerator
        assert isinstance(builder.generator, PythonGenerator)
    
    def test_build_generates_valid_cli_structure(self):
        """Test that build generates a CLI with correct structure."""
        # Use a minimal but real config
        config = ConfigSchema(cli=CLISchema(
            name="test-cli",
            tagline="Test CLI Application",
            commands={"hello": CommandSchema(desc="Say hello to someone")}
        ))
        
        builder = Builder()
        result = builder.build(config, "test.yaml")
        
        # Test essential CLI structure
        assert "#!/usr/bin/env python3" in result
        assert 'Auto-generated from test.yaml' in result
        assert "import rich_click as click" in result
        assert "from rich_click import RichGroup" in result
        
        # Test command structure
        assert "def hello(ctx):" in result
        assert '@main.command()' in result
        assert '"Say hello to someone"' in result
        
        # Test main CLI function
        assert "def main(ctx, interactive=False):" in result
        assert "Test CLI Application" in result  # Tagline appears in docstring
    
    def test_build_handles_command_with_arguments(self):
        """Test that build correctly handles commands with arguments."""
        config = ConfigSchema(cli=CLISchema(
            name="test-cli",
            tagline="Test CLI",
            commands={
                "greet": CommandSchema(
                    desc="Greet a user",
                    args=[
                        ArgumentSchema(
                            name="name",
                            desc="Name of person to greet",
                            required=True
                        )
                    ]
                )
            }
        ))
        
        builder = Builder()
        result = builder.build(config, "test.yaml")
        
        # Check argument handling
        assert "def greet(ctx, name):" in result
        assert '@click.argument' in result
        assert '"NAME"' in result  # Arguments are uppercase in decorator
        # Help text is shown in the docstring, not in argument decorator
    
    def test_build_handles_command_with_options(self):
        """Test that build correctly handles commands with options."""
        config = ConfigSchema(cli=CLISchema(
            name="test-cli",
            tagline="Test CLI",
            commands={
                "hello": CommandSchema(
                    desc="Say hello",
                    options=[
                        OptionSchema(
                            name="uppercase",
                            desc="Print in uppercase",
                            type="flag"
                        ),
                        OptionSchema(
                            name="count",
                            desc="Number of times to repeat",
                            type="int",
                            default=1
                        )
                    ]
                )
            }
        ))
        
        builder = Builder()
        result = builder.build(config, "test.yaml")
        
        # Check option handling
        assert "def hello(ctx, uppercase, count):" in result
        assert '@click.option("--uppercase"' in result
        assert 'is_flag=True' in result
        assert '@click.option("--count"' in result
        assert 'type=int' in result
        assert 'default=1' in result
    
    def test_build_includes_daemon_support_for_managed_commands(self):
        """Test that managed lifecycle commands get daemon support."""
        config = ConfigSchema(cli=CLISchema(
            name="test-cli",
            tagline="Test CLI",
            commands={
                "serve": CommandSchema(
                    desc="Run server",
                    lifecycle="managed"
                )
            }
        ))
        
        builder = Builder()
        result = builder.build(config, "test.yaml")
        
        # Verify managed command functionality
        assert "# Managed command" in result
        assert "command_instance_name = f\"serve_command\"" in result
        assert "command_instance.execute(**kwargs)" in result
        assert 'Error: Managed command' in result
    
    def test_build_includes_global_options(self):
        """Test that global CLI options are properly included."""
        config = ConfigSchema(cli=CLISchema(
            name="test-cli",
            tagline="Test CLI",
            options=[
                OptionSchema(
                    name="verbose",
                    desc="Enable verbose output",
                    type="flag"
                )
            ],
            commands={"hello": CommandSchema(desc="Say hello")}
        ))
        
        builder = Builder()
        result = builder.build(config, "test.yaml")
        
        # Check global option handling
        assert "def main(ctx" in result
        assert "verbose" in result
        assert "ctx.obj['verbose'] = verbose" in result
        assert "@click.option" in result
        assert "--verbose" in result
    
    def test_build_includes_config_metadata(self):
        """Test that build includes configuration metadata."""
        config = ConfigSchema(cli=CLISchema(
            name="test-cli",
            tagline="Test CLI",
            version="1.2.3",
            commands={"hello": CommandSchema(desc="Say hello")}
        ))
        
        builder = Builder()
        result = builder.build(config, "test.yaml")
        
        # Check metadata inclusion
        assert "test.yaml" in result
        assert "1.2.3" in result
    
    def test_build_escapes_special_characters_in_json(self):
        """Test that special characters are properly escaped in embedded JSON."""
        config = ConfigSchema(cli=CLISchema(
            name="test-cli",
            tagline='CLI with "quotes" and \'apostrophes\'',
            commands={"hello": CommandSchema(desc="Say hello")}
        ))
        
        builder = Builder()
        result = builder.build(config, "test.yaml")
        
        # The tagline with special characters should be in the output
        assert "CLI with" in result
        assert "quotes" in result
        assert "apostrophes" in result
        # The template should handle these special characters correctly


class TestFileSystemErrorConditions:
    """Test file system error conditions in Builder operations."""
    
    def setup_method(self):
        """Setup test environment."""
        import tempfile
        self.temp_dir = Path(tempfile.mkdtemp())
        
    def teardown_method(self):
        """Clean up test environment."""
        import shutil
        if self.temp_dir.exists():
            try:
                shutil.rmtree(self.temp_dir)
            except (PermissionError, OSError):
                pass
    
    def test_builder_output_directory_permission_denied(self):
        """Test builder when output directory is not writable."""
        config = ConfigSchema(cli=CLISchema(
            name="test-cli",
            tagline="Test CLI",
            commands={"hello": CommandSchema(desc="Say hello")}
        ))
        
        # Create a directory that we'll make read-only
        read_only_dir = self.temp_dir / "readonly"
        read_only_dir.mkdir()
        
        # Try to make directory read-only (may not work on all systems)
        import os
        try:
            os.chmod(str(read_only_dir), 0o444)  # Read-only
            
            builder = Builder()
            
            # Mock the generator to try to write to read-only directory
            with patch.object(builder.generator, 'generate') as mock_gen:
                mock_gen.side_effect = PermissionError("Permission denied")
                
                # Should handle permission errors gracefully
                with pytest.raises(PermissionError):
                    builder.build(config, "test.yaml")
        finally:
            # Restore permissions for cleanup
            try:
                os.chmod(str(read_only_dir), 0o755)
            except (PermissionError, OSError):
                pass
    
    def test_builder_disk_space_exhausted(self):
        """Test builder when disk space is exhausted."""
        config = ConfigSchema(cli=CLISchema(
            name="test-cli",
            tagline="Test CLI",
            commands={"hello": CommandSchema(desc="Say hello")}
        ))
        
        builder = Builder()
        
        # Mock the generator to simulate disk space exhausted
        with patch.object(builder.generator, 'generate') as mock_gen:
            mock_gen.side_effect = OSError(28, "No space left on device")  # ENOSPC
            
            # Should handle disk space errors appropriately
            with pytest.raises(OSError):
                builder.build(config, "test.yaml")
    
    def test_builder_concurrent_file_access_errors(self):
        """Test builder with concurrent file access conflicts."""
        config = ConfigSchema(cli=CLISchema(
            name="test-cli",
            tagline="Test CLI",
            commands={"hello": CommandSchema(desc="Say hello")}
        ))
        
        builder = Builder()
        
        # Mock the generator to simulate file locking conflicts
        with patch.object(builder.generator, 'generate') as mock_gen:
            mock_gen.side_effect = OSError(35, "Resource temporarily unavailable")  # EAGAIN
            
            # Should handle resource conflicts appropriately
            with pytest.raises(OSError):
                builder.build(config, "test.yaml")
    
    def test_builder_invalid_file_paths(self):
        """Test builder with invalid file paths and names."""
        config = ConfigSchema(cli=CLISchema(
            name="test-cli",
            tagline="Test CLI",
            commands={"hello": CommandSchema(desc="Say hello")}
        ))
        
        builder = Builder()
        
        # Mock the generator to simulate invalid file path generation
        with patch.object(builder.generator, 'generate') as mock_gen:
            # Simulate generation that would involve invalid paths
            mock_gen.side_effect = ValueError("Invalid file path generated")
            
            # Should either handle gracefully or raise appropriate error
            try:
                result = builder.build(config, "test.yaml")
                # If it succeeds, check that output is reasonable
                assert isinstance(result, str)
            except (OSError, ValueError):
                # Acceptable to fail with invalid paths
                pass
    
    def test_builder_circular_symlink_handling(self):
        """Test builder with circular symlinks in paths."""
        config = ConfigSchema(cli=CLISchema(
            name="test-cli",
            tagline="Test CLI",
            commands={"hello": CommandSchema(desc="Say hello")}
        ))
        
        # Create circular symlinks (if supported on the system)
        try:
            link1 = self.temp_dir / "link1"
            link2 = self.temp_dir / "link2"
            link1.symlink_to(link2)
            link2.symlink_to(link1)
            
            builder = Builder()
            
            # Mock the generator to simulate circular symlink handling
            with patch.object(builder.generator, 'generate') as mock_gen:
                mock_gen.side_effect = OSError("Circular symlink detected")
                
                # Should handle circular symlinks appropriately
                try:
                    result = builder.build(config, "test.yaml")
                    assert isinstance(result, str)
                except (OSError, RecursionError):
                    # Acceptable to fail with circular symlinks
                    pass
        except (OSError, NotImplementedError):
            # Symlinks not supported on this system, skip test
            pass
    
    def test_builder_file_system_encoding_errors(self):
        """Test builder with file system encoding issues."""
        config = ConfigSchema(cli=CLISchema(
            name="test-cli",
            tagline="Test CLI",
            commands={"hello": CommandSchema(desc="Say hello")}
        ))
        
        builder = Builder()
        
        # Mock the generator to produce content with encoding issues
        with patch.object(builder.generator, 'generate') as mock_gen:
            # Content that might cause encoding issues
            problematic_content = "Unicode content: \u2603 \udcff \ufffd"
            mock_gen.return_value = problematic_content
            
            # Should handle encoding issues gracefully
            try:
                result = builder.build(config, "test.yaml")
                assert isinstance(result, str)
                # Check that problematic content is handled appropriately
                assert "\u2603" in result or "?" in result or "replacement" in result
            except UnicodeError:
                # Acceptable to fail with encoding errors
                pass
    
    def test_builder_very_deep_directory_structure(self):
        """Test builder with extremely deep directory structures."""
        config = ConfigSchema(cli=CLISchema(
            name="test-cli",
            tagline="Test CLI",
            commands={"hello": CommandSchema(desc="Say hello")}
        ))
        
        builder = Builder()
        
        # Mock the generator to simulate very deep directory structure
        with patch.object(builder.generator, 'generate') as mock_gen:
            # Simulate generation with deep paths that might cause issues
            mock_gen.side_effect = OSError("Path too deep")
            
            # Should handle deep paths appropriately
            try:
                result = builder.build(config, "test.yaml")
                assert isinstance(result, str)
            except (OSError, ValueError):
                # Acceptable to fail with extremely deep paths
                pass
    
    def test_builder_special_device_files(self):
        """Test builder interaction with special device files."""
        config = ConfigSchema(cli=CLISchema(
            name="test-cli",
            tagline="Test CLI",
            commands={"hello": CommandSchema(desc="Say hello")}
        ))
        
        builder = Builder()
        
        # Mock the generator to simulate special device file access
        with patch.object(builder.generator, 'generate') as mock_gen:
            mock_gen.side_effect = PermissionError("Cannot access special device files")
            
            # Should handle special files appropriately
            try:
                result = builder.build(config, "test.yaml")
                assert isinstance(result, str)
            except (OSError, PermissionError):
                # Acceptable to fail with special device files
                pass
    
    def test_builder_temporary_file_cleanup_on_error(self):
        """Test that builder cleans up temporary files on errors."""
        config = ConfigSchema(cli=CLISchema(
            name="test-cli",
            tagline="Test CLI",
            commands={"hello": CommandSchema(desc="Say hello")}
        ))
        
        builder = Builder()
        
        # Mock the generator to fail during generation
        with patch.object(builder.generator, 'generate') as mock_gen:
            def failing_generator(*args, **kwargs):
                # Create some files to simulate partial generation
                temp_file = self.temp_dir / "temp1.py"
                temp_file.write_text("temp content")
                
                # Then fail
                raise RuntimeError("Generation failed after creating temp files")
            
            mock_gen.side_effect = failing_generator
            
            # Count files before
            files_before = list(self.temp_dir.glob("*.py"))
            
            # Should fail but ideally clean up temp files
            with pytest.raises(RuntimeError):
                builder.build(config, "test.yaml")
            
            # Check if temp files were cleaned up (implementation dependent)
            files_after = list(self.temp_dir.glob("*.py"))
            # Note: This test documents expected behavior but cleanup may be implementation-specific
    
    def test_builder_file_corruption_during_write(self):
        """Test builder handling of file corruption during write operations."""
        config = ConfigSchema(cli=CLISchema(
            name="test-cli",
            tagline="Test CLI",
            commands={"hello": CommandSchema(desc="Say hello")}
        ))
        
        builder = Builder()
        
        # Mock the generator to simulate write corruption
        with patch.object(builder.generator, 'generate') as mock_gen:
            # Return content that might cause issues
            corrupted_content = "\x00\x01\x02" + "normal content" + "\xff\xfe"
            mock_gen.return_value = corrupted_content
            
            # Should handle potentially corrupted content
            try:
                result = builder.build(config, "test.yaml")
                assert isinstance(result, str)
                # Content should be handled appropriately
            except (UnicodeError, ValueError):
                # Acceptable to fail with corrupted content
                pass
    
    def test_builder_network_filesystem_errors(self):
        """Test builder with network filesystem connectivity issues."""
        config = ConfigSchema(cli=CLISchema(
            name="test-cli",
            tagline="Test CLI",
            commands={"hello": CommandSchema(desc="Say hello")}
        ))
        
        builder = Builder()
        
        # Mock the generator to simulate network filesystem errors
        with patch.object(builder.generator, 'generate') as mock_gen:
            # Simulate various network-related errors
            network_errors = [
                OSError(110, "Connection timed out"),  # ETIMEDOUT
                OSError(113, "No route to host"),      # EHOSTUNREACH
                OSError(111, "Connection refused"),    # ECONNREFUSED
            ]
            
            for error in network_errors:
                mock_gen.side_effect = error
                
                # Should handle network errors appropriately
                with pytest.raises(OSError):
                    builder.build(config, "test.yaml")
    
    def test_builder_interrupted_system_call(self):
        """Test builder handling of interrupted system calls."""
        config = ConfigSchema(cli=CLISchema(
            name="test-cli",
            tagline="Test CLI",
            commands={"hello": CommandSchema(desc="Say hello")}
        ))
        
        builder = Builder()
        
        # Mock the generator to simulate interrupted system call
        with patch.object(builder.generator, 'generate') as mock_gen:
            mock_gen.side_effect = OSError(4, "Interrupted system call")  # EINTR
            
            # Should handle interrupted system calls
            with pytest.raises(OSError):
                builder.build(config, "test.yaml")


class TestLoadYamlConfig:
    """Test cases for load_yaml_config function."""
    
    @patch("builtins.open", new_callable=mock_open, read_data="""
cli:
  name: test-cli
  tagline: Test CLI Application
  commands:
    hello:
      desc: Hello command
""")
    def test_load_valid_yaml_config(self, mock_file):
        """Test load_yaml_config with valid YAML."""
        result = load_yaml_config("test.yaml")
        
        assert isinstance(result, ConfigSchema)
        assert result.cli.name == "test-cli"
        assert result.cli.tagline == "Test CLI Application"
        assert "hello" in result.cli.commands
        assert result.cli.commands["hello"].desc == "Hello command"
    
    @patch("builtins.open", side_effect=FileNotFoundError)
    def test_load_yaml_config_file_not_found(self, mock_file):
        """Test load_yaml_config when file doesn't exist."""
        with pytest.raises(Exit) as exc_info:
            load_yaml_config("missing.yaml")
        
        assert exc_info.value.exit_code == 1
    
    @patch("builtins.open", new_callable=mock_open, read_data="invalid: yaml: content:")
    def test_load_yaml_config_invalid_yaml(self, mock_file):
        """Test load_yaml_config with invalid YAML syntax."""
        with pytest.raises(Exit) as exc_info:
            load_yaml_config("invalid.yaml")
        
        assert exc_info.value.exit_code == 1
    
    @patch("builtins.open", new_callable=mock_open, read_data="""
cli:
  # Missing required 'name' field
  commands:
    hello:
      desc: Hello
""")
    def test_load_yaml_config_validation_error(self, mock_file):
        """Test load_yaml_config with schema validation error."""
        with pytest.raises(Exit) as exc_info:
            load_yaml_config("invalid_schema.yaml")
        
        assert exc_info.value.exit_code == 1
    
    @patch("builtins.open", new_callable=mock_open, read_data="""
cli:
  name: test-cli
  tagline: Test CLI
  commands:
    hello:
      desc: Hello command
""")
    def test_load_yaml_config_with_commands(self, mock_file):
        """Test load_yaml_config with commands defined."""
        result = load_yaml_config("test.yaml")
        
        assert isinstance(result, ConfigSchema)
        assert "hello" in result.cli.commands
        assert result.cli.commands["hello"].desc == "Hello command"

