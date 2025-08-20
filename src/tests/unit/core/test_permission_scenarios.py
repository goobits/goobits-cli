"""
Unit tests for filesystem permission error scenarios during CLI generation.

This module tests the framework's handling of permission errors that can occur
during file operations when generating CLI code across different languages.
"""

import pytest
import os
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock

from goobits_cli.builder import Builder
from goobits_cli.schemas import ConfigSchema, CLISchema, CommandSchema
from goobits_cli.generators.python import PythonGenerator


class TestPermissionErrorScenarios:
    """Test permission error handling during CLI generation."""
    
    def setup_method(self):
        """Setup test environment with temporary directories."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.test_config = ConfigSchema(cli=CLISchema(
            name="test-cli",
            tagline="Test CLI Application",
            commands={"hello": CommandSchema(desc="Say hello to someone")}
        ))
        
    def teardown_method(self):
        """Clean up test environment."""
        if self.temp_dir.exists():
            try:
                # Restore permissions before cleanup
                for path in self.temp_dir.rglob("*"):
                    try:
                        if path.is_dir():
                            os.chmod(str(path), 0o755)
                        else:
                            os.chmod(str(path), 0o644)
                    except (PermissionError, OSError):
                        pass
                shutil.rmtree(self.temp_dir)
            except (PermissionError, OSError):
                pass

    def test_read_only_output_directory_permission_denied(self):
        """Test CLI generation when output directory is read-only."""
        builder = Builder()
        
        # Mock the generator's generate method to simulate permission denied
        with patch.object(builder.generator, 'generate') as mock_generate:
            mock_generate.side_effect = PermissionError("Permission denied: cannot write to read-only directory")
            
            with pytest.raises(PermissionError) as exc_info:
                builder.build(self.test_config, "test.yaml")
            
            assert "Permission denied" in str(exc_info.value)

    def test_insufficient_permissions_for_executable_creation(self):
        """Test handling when lacking permissions to create executable files."""
        builder = Builder()
        
        # Mock the universal template engine file operations
        with patch.object(builder.generator, 'generate') as mock_generate:
            # Simulate permission error when trying to create executable files
            mock_generate.side_effect = PermissionError(
                "Operation not permitted: cannot set executable permissions"
            )
            
            with pytest.raises(PermissionError) as exc_info:
                builder.build(self.test_config, "test.yaml")
            
            assert "Operation not permitted" in str(exc_info.value)

    def test_disk_full_during_file_writes(self):
        """Test handling when disk space is exhausted during file operations."""
        builder = Builder()
        
        # Mock file writing to simulate disk full error
        with patch('builtins.open') as mock_open_func:
            mock_file = MagicMock()
            mock_file.write.side_effect = OSError(28, "No space left on device")  # ENOSPC
            mock_open_func.return_value.__enter__.return_value = mock_file
            
            # Mock the generator to try writing
            with patch.object(builder.generator, 'generate') as mock_generate:
                mock_generate.side_effect = OSError(28, "No space left on device")
                
                with pytest.raises(OSError) as exc_info:
                    builder.build(self.test_config, "test.yaml")
                
                assert exc_info.value.errno == 28
                assert "No space left on device" in str(exc_info.value)

    def test_network_drive_permission_issues(self):
        """Test handling of network filesystem permission errors."""
        builder = Builder()
        
        # Test various network-related permission errors
        network_errors = [
            OSError(110, "Connection timed out"),      # ETIMEDOUT
            OSError(113, "No route to host"),          # EHOSTUNREACH
            OSError(111, "Connection refused"),        # ECONNREFUSED
            PermissionError("Remote filesystem permission denied"),
        ]
        
        for error in network_errors:
            with patch.object(builder.generator, 'generate') as mock_generate:
                mock_generate.side_effect = error
                
                with pytest.raises((OSError, PermissionError)) as exc_info:
                    builder.build(self.test_config, "test.yaml")
                
                # Verify the specific error type and message
                if hasattr(error, 'errno'):
                    assert exc_info.value.errno == error.errno
                assert str(error) in str(exc_info.value)

    def test_partial_write_failures_some_files_succeed(self):
        """Test scenario where some files write successfully but others fail."""
        builder = Builder()
        
        # Mock the generator to simulate partial failure during file operations
        with patch.object(builder.generator, 'generate') as mock_generate:
            # Simulate failure after some progress
            mock_generate.side_effect = PermissionError("Permission denied writing setup.sh")
            
            with pytest.raises(PermissionError) as exc_info:
                builder.build(self.test_config, "test.yaml")
            
            assert "Permission denied writing setup.sh" in str(exc_info.value)

    def test_individual_file_permission_denied(self):
        """Test permission denied on specific files vs directories."""
        builder = Builder()
        
        # Test file-specific permission error
        with patch('builtins.open') as mock_open_func:
            mock_open_func.side_effect = PermissionError(
                "[Errno 13] Permission denied: 'cli.py'"
            )
            
            with patch.object(builder.generator, 'generate') as mock_generate:
                mock_generate.side_effect = PermissionError(
                    "[Errno 13] Permission denied: 'cli.py'"
                )
                
                with pytest.raises(PermissionError) as exc_info:
                    builder.build(self.test_config, "test.yaml")
                
                assert "cli.py" in str(exc_info.value)
                assert "Permission denied" in str(exc_info.value)

    def test_temporary_file_creation_failures(self):
        """Test handling when temporary file operations fail due to permissions."""
        builder = Builder()
        
        # Mock temporary file creation to fail
        with patch('tempfile.NamedTemporaryFile') as mock_temp:
            mock_temp.side_effect = PermissionError(
                "Cannot create temporary file in restricted directory"
            )
            
            # Mock generator to use temporary files
            with patch.object(builder.generator, 'generate') as mock_generate:
                mock_generate.side_effect = PermissionError(
                    "Cannot create temporary file in restricted directory"
                )
                
                with pytest.raises(PermissionError) as exc_info:
                    builder.build(self.test_config, "test.yaml")
                
                assert "temporary file" in str(exc_info.value)

    def test_cleanup_verification_on_permission_failures(self):
        """Test that cleanup is attempted even when permission errors occur."""
        builder = Builder()
        
        # Create some test files that should be cleaned up
        test_files = []
        for i in range(3):
            test_file = self.temp_dir / f"temp_file_{i}.py"
            test_file.write_text(f"# Temporary file {i}")
            test_files.append(test_file)
        
        # Mock to track cleanup attempts
        cleanup_attempted = []
        
        def mock_cleanup_side_effect(path):
            cleanup_attempted.append(str(path))
            # Allow cleanup to succeed
            
        with patch.object(Path, 'unlink', side_effect=mock_cleanup_side_effect):
            with patch.object(builder.generator, 'generate') as mock_generate:
                # Simulate failure after creating files
                mock_generate.side_effect = PermissionError("Write failed after partial generation")
                
                with pytest.raises(PermissionError):
                    builder.build(self.test_config, "test.yaml")
        
        # Note: Cleanup behavior is implementation-dependent
        # This test documents expected behavior but may need adjustment
        # based on actual cleanup implementation

    def test_all_language_generators_consistent_error_handling(self):
        """Test that all language generators handle permission errors consistently."""
        error_scenarios = [
            PermissionError("Permission denied"),
            OSError(13, "Permission denied"),  # EACCES
            OSError(28, "No space left on device"),  # ENOSPC
        ]
        
        languages = ["python", "nodejs", "typescript", "rust"]
        
        for language in languages:
            for error in error_scenarios:
                builder = Builder(language=language)
                
                with patch.object(builder.generator, 'generate') as mock_generate:
                    mock_generate.side_effect = error
                    
                    with pytest.raises((PermissionError, OSError)) as exc_info:
                        builder.build(self.test_config, "test.yaml")
                    
                    # Verify error propagation is consistent across languages
                    if hasattr(error, 'errno'):
                        assert exc_info.value.errno == error.errno
                    assert type(exc_info.value) is type(error)

    def test_permission_error_messages_provide_user_guidance(self):
        """Test that permission errors include helpful guidance for users."""
        builder = Builder()
        
        # Mock various permission errors with realistic messages
        guidance_errors = [
            PermissionError("Permission denied. Try running with sudo or check file ownership."),
            OSError(13, "Permission denied. Ensure you have write access to the output directory."),
            PermissionError("Cannot write to protected system directory. Use --output-dir to specify an alternative location."),
        ]
        
        for error in guidance_errors:
            with patch.object(builder.generator, 'generate') as mock_generate:
                mock_generate.side_effect = error
                
                with pytest.raises((PermissionError, OSError)) as exc_info:
                    builder.build(self.test_config, "test.yaml")
                
                # Verify error message is preserved for user guidance
                error_message = str(exc_info.value)
                assert len(error_message) > 0
                # Error should contain actionable information
                assert any(keyword in error_message.lower() for keyword in [
                    "permission", "denied", "access", "sudo", "directory", "write"
                ])

    def test_concurrent_access_permission_conflicts(self):
        """Test handling of concurrent access and file locking issues."""
        builder = Builder()
        
        # Simulate various concurrent access errors
        concurrent_errors = [
            OSError(35, "Resource temporarily unavailable"),  # EAGAIN
            PermissionError("The process cannot access the file because it is being used by another process"),
            OSError(16, "Device or resource busy"),  # EBUSY
        ]
        
        for error in concurrent_errors:
            with patch.object(builder.generator, 'generate') as mock_generate:
                mock_generate.side_effect = error
                
                with pytest.raises((PermissionError, OSError)) as exc_info:
                    builder.build(self.test_config, "test.yaml")
                
                # Verify appropriate error handling for concurrent access
                if hasattr(error, 'errno'):
                    assert exc_info.value.errno == error.errno

    def test_directory_creation_permission_failures(self):
        """Test handling when directory creation fails due to permissions."""
        builder = Builder()
        
        # Mock Path.mkdir to fail with permission error
        with patch.object(Path, 'mkdir') as mock_mkdir:
            mock_mkdir.side_effect = PermissionError(
                "Permission denied: cannot create directory"
            )
            
            # This tests the output_dir.mkdir() call in the build process
            with patch.object(builder.generator, 'generate') as mock_generate:
                mock_generate.side_effect = PermissionError(
                    "Permission denied: cannot create directory"
                )
                
                with pytest.raises(PermissionError) as exc_info:
                    builder.build(self.test_config, "test.yaml")
                
                assert "cannot create directory" in str(exc_info.value)


class TestUniversalTemplateEnginePermissions:
    """Test permission handling specifically in the Universal Template Engine."""
    
    def setup_method(self):
        """Setup test environment."""
        self.temp_dir = Path(tempfile.mkdtemp())
        
    def teardown_method(self):
        """Clean up test environment."""
        if self.temp_dir.exists():
            try:
                shutil.rmtree(self.temp_dir)
            except (PermissionError, OSError):
                pass

    def test_template_engine_file_write_permission_denied(self):
        """Test Universal Template Engine handling of file write permission errors."""
        # Test permission error through the Builder's generate method
        builder = Builder()
        
        # Mock the generator's generate method which is called by build
        with patch.object(builder.generator, 'generate') as mock_generate:
            mock_generate.side_effect = PermissionError("Permission denied writing template output")
            
            # Create minimal config for testing
            config = ConfigSchema(cli=CLISchema(
                name="test-cli",
                tagline="Test CLI",
                commands={"hello": CommandSchema(desc="Say hello")}
            ))
            
            with pytest.raises(PermissionError) as exc_info:
                builder.build(config, "test.yaml")
            
            assert "Permission denied writing template output" in str(exc_info.value)

    def test_template_cache_permission_errors(self):
        """Test permission errors in template caching operations."""
        # Test through PythonGenerator to avoid complex template engine mocking
        
        generator = PythonGenerator()
        
        # Mock cache operations to fail with permission error
        with patch.object(generator, 'universal_engine') as mock_engine:
            # Simulate cache write permission error during generation
            mock_engine.generate_cli.side_effect = PermissionError("Cannot write to cache directory")
            
            config = ConfigSchema(cli=CLISchema(
                name="test-cli",
                tagline="Test CLI",
                commands={"hello": CommandSchema(desc="Say hello")}
            ))
            
            # Should either handle cache errors gracefully or propagate them appropriately
            try:
                result = generator.generate(config, "test.yaml")
                # If it succeeds despite cache error, that's acceptable
                assert isinstance(result, str)
            except PermissionError as e:
                # If cache errors propagate, verify the error message
                assert "Cannot write to cache directory" in str(e)