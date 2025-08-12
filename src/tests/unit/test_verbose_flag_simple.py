"""Simple functional tests for --verbose flag implementation.

NOTE: This file is NOT a duplicate of test_verbose_flag.py - they test different layers:
- test_verbose_flag.py: Tests the GENERATION PIPELINE (unit layer)
- test_verbose_flag_simple.py: Tests the ACTUAL TEMPLATE CONTENT (integration layer)

This file validates that the templates themselves contain the correct verbose flag code,
while test_verbose_flag.py validates that the generation system produces the templates correctly.
Both tests are necessary for complete coverage of the verbose flag feature.
"""
import pytest
import tempfile
import os
import yaml
from pathlib import Path

from goobits_cli.schemas import OptionSchema, CLISchema


class TestVerboseFlagSimple:
    """Simple test suite for --verbose flag functionality."""

    def test_verbose_option_schema_validation(self):
        """Test that verbose option schema validates correctly."""
        verbose_option = OptionSchema(
            name="verbose",
            short="v",
            type="flag",
            desc="Enable verbose output"
        )
        
        assert verbose_option.name == "verbose"
        assert verbose_option.short == "v"
        assert verbose_option.type == "flag"

    def test_verbose_in_self_hosted_config(self):
        """Test that verbose option exists in the self-hosted goobits.yaml."""
        # This tests the actual implementation
        goobits_yaml_path = Path(__file__).parent.parent.parent.parent / "goobits.yaml"
        
        with open(goobits_yaml_path, 'r') as f:
            config = yaml.safe_load(f)
        
        # Check that verbose option exists in CLI options
        cli_options = config.get('cli', {}).get('options', [])
        verbose_options = [opt for opt in cli_options if opt.get('name') == 'verbose']
        
        assert len(verbose_options) == 1, "Exactly one verbose option should exist"
        verbose_opt = verbose_options[0]
        
        assert verbose_opt.get('short') == 'v', "Verbose should have short form -v"
        assert verbose_opt.get('type') == 'flag', "Verbose should be a flag type"
        assert 'verbose' in verbose_opt.get('desc', '').lower(), "Description should mention verbose"

    def test_python_template_has_verbose_error_handler(self):
        """Test that Python template uses verbose parameter in error handler."""
        template_path = Path(__file__).parent.parent.parent / "goobits_cli" / "templates" / "cli_template.py.j2"
        
        with open(template_path, 'r') as f:
            template_content = f.read()
        
        # Check that error handler uses verbose parameter
        assert "def handle_cli_error(error: Exception, verbose: bool = False)" in template_content
        assert "Run with --verbose for full traceback" in template_content
        
        # Should not have old debug references
        assert "Run with --debug for" not in template_content

    def test_nodejs_template_has_verbose_error_handler(self):
        """Test that Node.js template uses verbose parameter in error handler.""" 
        template_path = Path(__file__).parent.parent.parent / "goobits_cli" / "templates" / "nodejs" / "cli.js.j2"
        
        with open(template_path, 'r') as f:
            template_content = f.read()
        
        # Check that error handler uses verbose parameter
        assert "function handleCLIError(error, verbose = false)" in template_content
        assert "Run with --verbose for full traceback" in template_content

    def test_typescript_template_has_verbose_error_handler(self):
        """Test that TypeScript template uses verbose parameter in error handler."""
        template_path = Path(__file__).parent.parent.parent / "goobits_cli" / "templates" / "typescript" / "cli.ts.j2"
        
        with open(template_path, 'r') as f:
            template_content = f.read()
        
        # Check that error handler uses verbose parameter with TypeScript typing
        assert "function handleCLIError(error: Error, verbose: boolean = false)" in template_content
        assert "Run with --verbose for full traceback" in template_content

    def test_universal_error_handler_supports_verbose(self):
        """Test that universal error handler supports verbose parameter."""
        template_path = Path(__file__).parent.parent.parent / "goobits_cli" / "universal" / "components" / "error_handler.j2"
        
        with open(template_path, 'r') as f:
            template_content = f.read()
        
        # Check that universal error handler supports verbose
        assert "verbose: bool = False" in template_content or "verbose=false" in template_content
        assert "Run with --verbose for more details" in template_content

    def test_generated_cli_includes_verbose_flag(self):
        """Test that the actual generated CLI includes --verbose flag."""
        # Read the generated CLI from the self-hosted build
        cli_path = Path(__file__).parent.parent.parent.parent / "cli.py"
        
        if cli_path.exists():
            with open(cli_path, 'r') as f:
                cli_content = f.read()
            
            # Check that the generated CLI has verbose support
            assert "def handle_cli_error(error: Exception, verbose: bool = False)" in cli_content
            assert "Run with --verbose for full traceback" in cli_content
        else:
            pytest.skip("Generated CLI not found - run 'goobits build' first")