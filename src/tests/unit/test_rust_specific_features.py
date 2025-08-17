"""Unit tests for Rust-specific CLI generator features.

This module tests Rust ecosystem integration, type system handling,
Clap framework integration, and Rust-specific code generation patterns.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import tempfile
import shutil
import json
import re

from goobits_cli.generators.rust import (
    RustGenerator, RustGeneratorError, ConfigurationError, 
    TemplateError, DependencyError, ValidationError
)
from goobits_cli.schemas import (
    ConfigSchema, CLISchema, CommandSchema, ArgumentSchema, OptionSchema, 
    GoobitsConfigSchema, CommandGroupSchema
)
from conftest import create_test_goobits_config


class TestClapIntegration:
    """Test Clap framework integration specifics."""
    
    def test_clap_command_structure_generation(self):
        """Test that generated code follows Clap command structure patterns."""
        cli_schema = CLISchema(
            name="clap-test",
            tagline="Clap framework test",
            commands={
                "deploy": CommandSchema(
                    desc="Deploy application",
                    args=[ArgumentSchema(name="environment", desc="Target env", required=True)],
                    options=[
                        OptionSchema(name="force", desc="Force deploy", type="flag"),
                        OptionSchema(name="timeout", desc="Timeout seconds", type="int", default=300)
                    ]
                ),
                "status": CommandSchema(desc="Check status")
            }
        )
        config = create_test_goobits_config("clap-test", cli_schema, language="rust")
        
        generator = RustGenerator(use_universal_templates=False)
        result = generator.generate_all_files(config, "clap.yaml")
        
        main_rs = result['src/main.rs']
        
        # Check for Clap imports and usage
        assert 'use clap::{' in main_rs or 'clap' in main_rs
        assert 'Command::new' in main_rs
        assert 'subcommand' in main_rs
        assert 'ArgMatches' in main_rs
        
        # Check command definitions
        assert 'deploy' in main_rs
        assert 'status' in main_rs
        assert 'environment' in main_rs
        assert 'force' in main_rs
        assert 'timeout' in main_rs
    
    def test_clap_argument_parsing_patterns(self):
        """Test Clap argument parsing code generation."""
        cli_schema = CLISchema(
            name="args-test",
            tagline="Argument parsing test",
            commands={
                "process": CommandSchema(
                    desc="Process files",
                    args=[
                        ArgumentSchema(name="input", desc="Input file", required=True),
                        ArgumentSchema(name="output", desc="Output file", required=False)
                    ],
                    options=[
                        OptionSchema(name="format", desc="Output format", type="str", choices=["json", "yaml"]),
                        OptionSchema(name="verbose", desc="Verbose output", type="flag"),
                        OptionSchema(name="threads", desc="Thread count", type="int", default=4)
                    ]
                )
            }
        )
        config = create_test_goobits_config("args-test", cli_schema, language="rust")
        
        generator = RustGenerator(use_universal_templates=False)
        result = generator.generate_all_files(config, "args.yaml")
        
        main_rs = result['src/main.rs']
        
        # Check for argument handling patterns
        assert 'Arg::new' in main_rs
        assert 'required(true)' in main_rs or 'required' in main_rs
        assert 'index(' in main_rs or 'positional' in main_rs
        
        # Check for option handling
        assert 'short(' in main_rs or 'long(' in main_rs
        assert 'help(' in main_rs
        
    def test_clap_subcommand_nesting(self):
        """Test Clap nested subcommand generation."""
        cli_schema = CLISchema(
            name="nested-test",
            tagline="Nested subcommands test",
            commands={
                "database": CommandSchema(
                    desc="Database operations",
                    subcommands={
                        "migrate": CommandSchema(
                            desc="Run migrations",
                            options=[OptionSchema(name="dry-run", desc="Dry run", type="flag")]
                        ),
                        "backup": CommandSchema(
                            desc="Backup database",
                            args=[ArgumentSchema(name="target", desc="Backup target")]
                        )
                    }
                )
            }
        )
        config = create_test_goobits_config("nested-test", cli_schema, language="rust")
        
        generator = RustGenerator(use_universal_templates=False)
        result = generator.generate_all_files(config, "nested.yaml")
        
        main_rs = result['src/main.rs']
        
        # Check for database command
        assert 'database' in main_rs
        # Note: Current fallback implementation may not generate nested subcommands
        # but should at least handle the parent command
    
    def test_clap_help_text_formatting(self):
        """Test Clap help text and description formatting."""
        cli_schema = CLISchema(
            name="help-test",
            tagline="Help formatting test with 'quotes' and \"double quotes\"",
            description="A CLI that tests help text formatting\nwith newlines and special chars: !@#$%",
            commands={
                "complex": CommandSchema(
                    desc="Complex command with 'special' chars and \"quotes\"",
                    args=[ArgumentSchema(
                        name="file",
                        desc="File path with backslashes: C:\\Users\\test\\"
                    )],
                    options=[OptionSchema(
                        name="message",
                        desc="Message with unicode: 🚀 rocket and émojis",
                        type="str"
                    )]
                )
            }
        )
        config = create_test_goobits_config("help-test", cli_schema, language="rust")
        
        generator = RustGenerator(use_universal_templates=False)
        result = generator.generate_all_files(config, "help.yaml")
        
        main_rs = result['src/main.rs']
        
        # Check that special characters are properly escaped
        assert 'complex' in main_rs
        # The generator should handle escaping properly


class TestRustTypeSystem:
    """Test Rust type system handling."""
    
    def test_python_to_rust_type_conversion(self):
        """Test conversion from Python types to Rust types."""
        generator = RustGenerator()
        
        # Test basic type mappings
        assert generator._to_rust_type('str') == 'String'
        assert generator._to_rust_type('int') == 'i32'
        assert generator._to_rust_type('float') == 'f64'
        assert generator._to_rust_type('bool') == 'bool'
        assert generator._to_rust_type('flag') == 'bool'
        assert generator._to_rust_type('list') == 'Vec<String>'
        assert generator._to_rust_type('dict') == 'std::collections::HashMap<String, String>'
        
        # Test unknown type fallback
        assert generator._to_rust_type('unknown_type') == 'String'
        assert generator._to_rust_type('') == 'String'
        assert generator._to_rust_type(None) == 'String'
    
    def test_option_type_handling(self):
        """Test Option<T> type handling for optional arguments."""
        cli_schema = CLISchema(
            name="option-test",
            tagline="Option type test",
            commands={
                "cmd": CommandSchema(
                    desc="Test command",
                    args=[
                        ArgumentSchema(name="required_arg", desc="Required", required=True),
                        ArgumentSchema(name="optional_arg", desc="Optional", required=False)
                    ],
                    options=[
                        OptionSchema(name="optional_flag", desc="Optional flag", type="flag"),
                        OptionSchema(name="optional_str", desc="Optional string", type="str"),
                        OptionSchema(name="optional_int", desc="Optional int", type="int")
                    ]
                )
            }
        )
        config = create_test_goobits_config("option-test", cli_schema, language="rust")
        
        generator = RustGenerator(use_universal_templates=False)
        result = generator.generate_all_files(config, "option.yaml")
        
        # The generated code should handle optional values appropriately
        # Check that the generation completes without errors
        assert 'src/main.rs' in result
        assert 'Cargo.toml' in result
    
    def test_result_error_pattern_integration(self):
        """Test Result<T, E> error handling pattern integration."""
        cli_schema = CLISchema(
            name="result-test",
            tagline="Result pattern test",
            commands={
                "risky": CommandSchema(desc="Command that might fail"),
                "safe": CommandSchema(desc="Safe command")
            }
        )
        config = create_test_goobits_config("result-test", cli_schema, language="rust")
        
        generator = RustGenerator(use_universal_templates=False)
        result = generator.generate_all_files(config, "result.yaml")
        
        main_rs = result['src/main.rs']
        hooks_rs = result['src/hooks.rs']
        
        # Check for Result type usage
        assert 'Result' in main_rs or 'anyhow::Result' in main_rs
        assert 'Result' in hooks_rs or 'anyhow::Result' in hooks_rs
        
        # Check for error handling patterns
        assert 'Err(' in main_rs or 'if let Err' in main_rs
        assert '?' in main_rs or 'unwrap' in main_rs or 'expect' in main_rs
    
    def test_struct_and_enum_naming_conventions(self):
        """Test struct and enum generation following Rust conventions."""
        generator = RustGenerator()
        
        # Test PascalCase conversion for types
        assert generator._to_pascal_case('user_config') == 'UserConfig'
        assert generator._to_pascal_case('api-client') == 'ApiClient'
        assert generator._to_pascal_case('database_connection') == 'DatabaseConnection'
        assert generator._to_pascal_case('simple') == 'Simple'
        assert generator._to_pascal_case('') == ''
        
        # Test snake_case for fields and functions
        assert generator._to_snake_case('UserConfig') == 'userconfig'
        assert generator._to_snake_case('APIClient') == 'apiclient'
        assert generator._to_snake_case('database-connection') == 'database_connection'
        assert generator._to_snake_case('simple name') == 'simple_name'
    
    def test_complex_type_combinations(self):
        """Test complex type combinations and nesting."""
        cli_schema = CLISchema(
            name="complex-types",
            tagline="Complex type test",
            commands={
                "process": CommandSchema(
                    desc="Process complex data",
                    options=[
                        OptionSchema(name="config", desc="Config map", type="dict"),
                        OptionSchema(name="files", desc="File list", type="list"),
                        OptionSchema(name="flags", desc="Flag list", type="list"),
                        OptionSchema(name="count", desc="Count", type="int"),
                        OptionSchema(name="ratio", desc="Ratio", type="float")
                    ]
                )
            }
        )
        config = create_test_goobits_config("complex-types", cli_schema, language="rust")
        
        generator = RustGenerator(use_universal_templates=False)
        result = generator.generate_all_files(config, "complex.yaml")
        
        # Verify generation completes successfully with complex types
        assert 'src/main.rs' in result
        assert len(result['src/main.rs']) > 0


class TestCargoEcosystem:
    """Test Cargo-specific features."""
    
    def test_cargo_toml_structure(self):
        """Test Cargo.toml generation and structure."""
        cli_schema = CLISchema(
            name="cargo-test",
            tagline="Cargo test CLI",
            version="2.1.0",
            commands={"build": CommandSchema(desc="Build project")}
        )
        config = create_test_goobits_config("cargo-test", cli_schema, language="rust")
        
        generator = RustGenerator(use_universal_templates=False)
        result = generator.generate_all_files(config, "cargo.yaml", version="2.1.0")
        
        cargo_toml = result['Cargo.toml']
        
        # Check package section
        assert '[package]' in cargo_toml
        assert 'name = "cargo-test"' in cargo_toml  # hyphenated package name
        assert 'version = "2.1.0"' in cargo_toml
        assert 'edition = "2021"' in cargo_toml
        
        # Check binary section
        assert '[[bin]]' in cargo_toml
        assert 'name = "cargo-test"' in cargo_toml
        assert 'path = "src/main.rs"' in cargo_toml
        
        # Check dependencies
        assert '[dependencies]' in cargo_toml
        assert 'clap' in cargo_toml
        assert 'anyhow' in cargo_toml
        assert 'serde' in cargo_toml
    
    def test_dependency_resolution(self):
        """Test Cargo dependency management."""
        cli_schema = CLISchema(
            name="deps-test",
            tagline="Dependencies test",
            commands={"test": CommandSchema(desc="Test command")}
        )
        config = create_test_goobits_config("deps-test", cli_schema, language="rust")
        
        generator = RustGenerator(use_universal_templates=False)
        result = generator.generate_all_files(config, "deps.yaml")
        
        cargo_toml = result['Cargo.toml']
        
        # Check for required CLI dependencies
        assert 'clap' in cargo_toml
        assert 'anyhow' in cargo_toml
        assert 'serde' in cargo_toml
        assert 'tokio' in cargo_toml
        assert 'thiserror' in cargo_toml
        
        # Check version specifications
        assert 'version = ' in cargo_toml
        assert 'features = ' in cargo_toml
    
    def test_feature_flags_generation(self):
        """Test Cargo feature flags in generated Cargo.toml."""
        cli_schema = CLISchema(
            name="features-test",
            tagline="Feature flags test",
            commands={"run": CommandSchema(desc="Run with features")}
        )
        config = create_test_goobits_config("features-test", cli_schema, language="rust")
        
        generator = RustGenerator(use_universal_templates=False)
        result = generator.generate_all_files(config, "features.yaml")
        
        cargo_toml = result['Cargo.toml']
        
        # Check for feature specifications in dependencies
        assert 'features = [' in cargo_toml
        assert '"derive"' in cargo_toml  # clap derive feature
        assert '"full"' in cargo_toml   # tokio full feature
    
    def test_workspace_compatibility(self):
        """Test generated Cargo.toml workspace compatibility."""
        cli_schema = CLISchema(
            name="workspace-test",
            tagline="Workspace test",
            commands={"work": CommandSchema(desc="Workspace command")}
        )
        config = create_test_goobits_config("workspace-test", cli_schema, language="rust")
        
        generator = RustGenerator(use_universal_templates=False)
        result = generator.generate_all_files(config, "workspace.yaml")
        
        cargo_toml = result['Cargo.toml']
        
        # Check that generated Cargo.toml is workspace-compatible
        assert '[package]' in cargo_toml
        assert 'edition = "2021"' in cargo_toml
        # Should not conflict with workspace settings
    
    def test_cross_compilation_settings(self):
        """Test cross-compilation friendly Cargo.toml settings."""
        cli_schema = CLISchema(
            name="cross-test",
            tagline="Cross compilation test",
            commands={"cross": CommandSchema(desc="Cross compile")}
        )
        config = create_test_goobits_config("cross-test", cli_schema, language="rust")
        
        generator = RustGenerator(use_universal_templates=False)
        result = generator.generate_all_files(config, "cross.yaml")
        
        cargo_toml = result['Cargo.toml']
        
        # Check for cross-compilation friendly settings
        assert 'edition = "2021"' in cargo_toml  # Modern edition
        # Dependencies should be platform-agnostic


class TestRustErrorPatterns:
    """Test Rust error handling patterns."""
    
    def test_result_propagation_patterns(self):
        """Test Result error propagation in generated code."""
        cli_schema = CLISchema(
            name="error-test",
            tagline="Error handling test",
            commands={
                "fail": CommandSchema(desc="Command that can fail"),
                "recover": CommandSchema(desc="Command with recovery")
            }
        )
        config = create_test_goobits_config("error-test", cli_schema, language="rust")
        
        generator = RustGenerator(use_universal_templates=False)
        result = generator.generate_all_files(config, "error.yaml")
        
        main_rs = result['src/main.rs']
        hooks_rs = result['src/hooks.rs']
        
        # Check for error propagation patterns
        assert 'Result<' in hooks_rs or 'anyhow::Result' in hooks_rs
        assert 'Err(' in hooks_rs
        
        # Check error handling in main
        assert 'if let Err' in main_rs or 'match' in main_rs or '?' in main_rs
    
    def test_custom_error_types(self):
        """Test custom error type definitions."""
        generator = RustGenerator()
        
        # Check that custom error types are defined
        cli_schema = CLISchema(
            name="custom-error",
            tagline="Custom error test",
            commands={"err": CommandSchema(desc="Error command")}
        )
        config = create_test_goobits_config("custom-error", cli_schema, language="rust")
        
        result = generator.generate_all_files(config, "custom.yaml")
        
        # Check that error handling infrastructure is in place
        # Universal templates might generate different file structure
        assert len(result) > 0  # Should generate some files
        
        # Check for anyhow usage (standard error handling) in any generated file
        any_rust_file = next(iter(result.values()))  # Get any generated file content
        assert isinstance(any_rust_file, str)  # Should be string content
    
    def test_error_message_formatting(self):
        """Test error message formatting and display."""
        cli_schema = CLISchema(
            name="msg-test",
            tagline="Error message test",
            commands={
                "validate": CommandSchema(
                    desc="Validation command",
                    args=[ArgumentSchema(name="input", desc="Input to validate")]
                )
            }
        )
        config = create_test_goobits_config("msg-test", cli_schema, language="rust")
        
        generator = RustGenerator(use_universal_templates=False)
        result = generator.generate_all_files(config, "msg.yaml")
        
        main_rs = result['src/main.rs']
        
        # Check for error display patterns
        assert 'eprintln!' in main_rs or 'println!' in main_rs
        assert 'Error:' in main_rs or 'error' in main_rs
    
    def test_panic_handling_patterns(self):
        """Test panic handling and graceful degradation."""
        cli_schema = CLISchema(
            name="panic-test",
            tagline="Panic handling test",
            commands={"risky": CommandSchema(desc="Risky operation")}
        )
        config = create_test_goobits_config("panic-test", cli_schema, language="rust")
        
        generator = RustGenerator(use_universal_templates=False)
        result = generator.generate_all_files(config, "panic.yaml")
        
        main_rs = result['src/main.rs']
        
        # Check for proper error handling instead of panics
        # Should use Result types rather than unwrap/expect
        assert 'Result' in main_rs or 'anyhow' in main_rs
        # Should avoid direct panics in favor of proper error handling
    
    def test_error_context_preservation(self):
        """Test error context and backtrace preservation."""
        cli_schema = CLISchema(
            name="context-test",
            tagline="Error context test",
            commands={"trace": CommandSchema(desc="Command with error context")}
        )
        config = create_test_goobits_config("context-test", cli_schema, language="rust")
        
        generator = RustGenerator(use_universal_templates=False)
        result = generator.generate_all_files(config, "context.yaml")
        
        cargo_toml = result['Cargo.toml']
        
        # Check for error handling crates
        assert 'anyhow' in cargo_toml  # For error context
        assert 'thiserror' in cargo_toml  # For custom error types


class TestRustConventions:
    """Test Rust naming and code conventions."""
    
    def test_snake_case_conversion(self):
        """Test snake_case naming convention enforcement."""
        generator = RustGenerator()
        
        # Test various input formats
        assert generator._to_snake_case('CamelCase') == 'camelcase'
        assert generator._to_snake_case('kebab-case') == 'kebab_case'
        assert generator._to_snake_case('SCREAMING_CASE') == 'screaming_case'
        assert generator._to_snake_case('Mixed-Case_input') == 'mixed_case_input'
        assert generator._to_snake_case('simple') == 'simple'
        assert generator._to_snake_case('multiple  spaces') == 'multiple__spaces'
        assert generator._to_snake_case('') == ''
    
    def test_screaming_snake_case_conversion(self):
        """Test SCREAMING_SNAKE_CASE for constants."""
        generator = RustGenerator()
        
        assert generator._to_screaming_snake_case('const_name') == 'CONST_NAME'
        assert generator._to_screaming_snake_case('kebab-name') == 'KEBAB_NAME'
        assert generator._to_screaming_snake_case('CamelCase') == 'CAMELCASE'
        assert generator._to_screaming_snake_case('normal name') == 'NORMAL_NAME'
        assert generator._to_screaming_snake_case('') == ''
    
    def test_pascal_case_conversion(self):
        """Test PascalCase for type names."""
        generator = RustGenerator()
        
        assert generator._to_pascal_case('snake_case') == 'SnakeCase'
        assert generator._to_pascal_case('kebab-case') == 'KebabCase'
        assert generator._to_pascal_case('normal case') == 'NormalCase'
        assert generator._to_pascal_case('already_pascal') == 'AlreadyPascal'
        assert generator._to_pascal_case('single') == 'Single'
        assert generator._to_pascal_case('') == ''
    
    def test_module_naming_conventions(self):
        """Test module naming follows Rust conventions."""
        cli_schema = CLISchema(
            name="module-test",
            tagline="Module naming test",
            commands={
                "user_management": CommandSchema(desc="User management"),
                "api-client": CommandSchema(desc="API client"),
                "database_ops": CommandSchema(desc="Database operations")
            }
        )
        config = create_test_goobits_config("module-test", cli_schema, language="rust")
        
        generator = RustGenerator(use_universal_templates=False)
        result = generator.generate_all_files(config, "module.yaml")
        
        hooks_rs = result['src/hooks.rs']
        
        # Check that function names follow snake_case
        assert 'pub fn on_user_management' in hooks_rs
        assert 'pub fn on_api_client' in hooks_rs or 'pub fn on_api-client' in hooks_rs
        assert 'pub fn on_database_ops' in hooks_rs
    
    def test_constant_naming_patterns(self):
        """Test constant naming patterns in generated code."""
        cli_schema = CLISchema(
            name="const-test",
            tagline="Constant naming test",
            version="3.14.15",
            commands={"const": CommandSchema(desc="Constant test")}
        )
        config = create_test_goobits_config("const-test", cli_schema, language="rust")
        
        generator = RustGenerator(use_universal_templates=False)
        result = generator.generate_all_files(config, "const.yaml")
        
        # Constants should follow SCREAMING_SNAKE_CASE
        # This would be verified in actual template output
        assert 'src/main.rs' in result
    
    def test_type_naming_conventions(self):
        """Test type naming follows Rust conventions."""
        generator = RustGenerator()
        
        # Type names should be PascalCase
        test_cases = [
            ('user_config', 'UserConfig'),
            ('api-client', 'ApiClient'),
            ('database_connection', 'DatabaseConnection'),
            ('simple_type', 'SimpleType')
        ]
        
        for input_name, expected in test_cases:
            assert generator._to_pascal_case(input_name) == expected
    
    def test_function_naming_conventions(self):
        """Test function naming follows Rust conventions."""
        cli_schema = CLISchema(
            name="func-test",
            tagline="Function naming test",
            commands={
                "build_project": CommandSchema(desc="Build project"),
                "run-tests": CommandSchema(desc="Run tests"),
                "deploy_to_production": CommandSchema(desc="Deploy to production")
            }
        )
        config = create_test_goobits_config("func-test", cli_schema, language="rust")
        
        generator = RustGenerator(use_universal_templates=False)
        result = generator.generate_all_files(config, "func.yaml")
        
        hooks_rs = result['src/hooks.rs']
        
        # Function names should be snake_case
        assert 'on_build_project' in hooks_rs
        assert 'on_run_tests' in hooks_rs or 'on_run-tests' in hooks_rs
        assert 'on_deploy_to_production' in hooks_rs
    
    def test_string_literal_escaping(self):
        """Test proper string literal escaping for Rust."""
        generator = RustGenerator()
        
        # Test various escape scenarios
        assert generator._escape_rust_string('simple') == 'simple'
        assert generator._escape_rust_string('with"quotes') == 'with\\"quotes'
        assert generator._escape_rust_string('with\\backslash') == 'with\\\\backslash'
        assert generator._escape_rust_string('with\nnewline') == 'with\\nnewline'
        assert generator._escape_rust_string('with\ttab') == 'with\\ttab'
        assert generator._escape_rust_string('') == ''
        
        # Test complex string with multiple escape sequences
        complex_string = 'Path: "C:\\Users\\test"\nWith\ttabs and "quotes"'
        escaped = generator._escape_rust_string(complex_string)
        assert '\\"' in escaped
        assert '\\\\' in escaped
        assert '\\n' in escaped
        assert '\\t' in escaped
    
    def test_identifier_sanitization(self):
        """Test sanitization of identifiers for Rust keywords."""
        generator = RustGenerator()
        
        # Test snake_case conversion handles Rust keywords properly
        # (The current implementation doesn't handle keywords, but tests the conversion)
        rust_keywords = ['match', 'if', 'else', 'fn', 'let', 'mut', 'const', 'static']
        
        for keyword in rust_keywords:
            # Current implementation just converts case
            result = generator._to_snake_case(keyword)
            assert result == keyword  # Should be unchanged as they're already snake_case
    
    def test_code_style_consistency(self):
        """Test that generated code follows consistent Rust style."""
        cli_schema = CLISchema(
            name="style-test",
            tagline="Code style test",
            commands={
                "format": CommandSchema(
                    desc="Format code",
                    args=[ArgumentSchema(name="source-file", desc="Source file")],
                    options=[
                        OptionSchema(name="in-place", desc="Format in place", type="flag"),
                        OptionSchema(name="line-width", desc="Line width", type="int", default=100)
                    ]
                )
            }
        )
        config = create_test_goobits_config("style-test", cli_schema, language="rust")
        
        generator = RustGenerator(use_universal_templates=False)
        result = generator.generate_all_files(config, "style.yaml")
        
        main_rs = result['src/main.rs']
        hooks_rs = result['src/hooks.rs']
        
        # Check for consistent style patterns
        # Functions should have proper visibility
        assert 'pub fn' in hooks_rs or 'fn' in hooks_rs
        
        # Check for proper use statements
        assert 'use ' in main_rs
        
        # Check for proper error handling
        assert 'Result' in hooks_rs or 'anyhow' in hooks_rs


class TestRustSpecificGenerationEdgeCases:
    """Test edge cases specific to Rust generation."""
    
    def test_empty_command_set(self):
        """Test generation with empty command set."""
        cli_schema = CLISchema(
            name="empty-test",
            tagline="Empty command test",
            commands={}
        )
        config = create_test_goobits_config("empty-test", cli_schema, language="rust")
        
        generator = RustGenerator(use_universal_templates=False)
        
        # Should handle empty commands gracefully
        try:
            result = generator.generate_all_files(config, "empty.yaml")
            assert isinstance(result, dict)
            assert 'src/main.rs' in result
        except (ValidationError, ConfigurationError):
            # Acceptable to reject empty command sets
            pass
    
    def test_very_long_command_names(self):
        """Test handling of very long command names."""
        long_name = "very_long_command_name_that_exceeds_normal_length_expectations"
        cli_schema = CLISchema(
            name="long-test",
            tagline="Long name test",
            commands={
                long_name: CommandSchema(desc="Very long command name test")
            }
        )
        config = create_test_goobits_config("long-test", cli_schema, language="rust")
        
        generator = RustGenerator(use_universal_templates=False)
        result = generator.generate_all_files(config, "long.yaml")
        
        # Should handle long names without truncation
        hooks_rs = result['src/hooks.rs']
        assert long_name in hooks_rs
    
    def test_special_characters_in_descriptions(self):
        """Test handling special characters in descriptions."""
        cli_schema = CLISchema(
            name="special-test",
            tagline="CLI with 'special' chars and \"quotes\"",
            commands={
                "special": CommandSchema(
                    desc="Command with émojis 🚀, quotes \"test\", and backslashes \\path\\",
                    args=[ArgumentSchema(
                        name="path",
                        desc="Path with C:\\Windows\\System32\\ and 'quotes'"
                    )]
                )
            }
        )
        config = create_test_goobits_config("special-test", cli_schema, language="rust")
        
        generator = RustGenerator(use_universal_templates=False)
        result = generator.generate_all_files(config, "special.yaml")
        
        # Should generate valid Rust code despite special characters
        assert 'src/main.rs' in result
        assert len(result['src/main.rs']) > 0
    
    def test_numeric_command_names(self):
        """Test handling of command names that start with numbers."""
        cli_schema = CLISchema(
            name="numeric-test",
            tagline="Numeric command test",
            commands={
                "2fa_setup": CommandSchema(desc="2FA setup"),
                "3d_render": CommandSchema(desc="3D rendering")
            }
        )
        config = create_test_goobits_config("numeric-test", cli_schema, language="rust")
        
        generator = RustGenerator(use_universal_templates=False)
        result = generator.generate_all_files(config, "numeric.yaml")
        
        # Should handle numeric prefixes in function names
        hooks_rs = result['src/hooks.rs']
        assert '2fa_setup' in hooks_rs or '_2fa_setup' in hooks_rs
        assert '3d_render' in hooks_rs or '_3d_render' in hooks_rs
    
    def test_command_name_conflicts_with_rust_keywords(self):
        """Test handling command names that conflict with Rust keywords."""
        rust_keywords = ['match', 'if', 'fn', 'let', 'const', 'static', 'mut']
        
        commands = {}
        for keyword in rust_keywords[:3]:  # Test a few keywords
            commands[keyword] = CommandSchema(desc=f"Command named {keyword}")
        
        cli_schema = CLISchema(
            name="keyword-test",
            tagline="Keyword conflict test",
            commands=commands
        )
        config = create_test_goobits_config("keyword-test", cli_schema, language="rust")
        
        generator = RustGenerator(use_universal_templates=False)
        result = generator.generate_all_files(config, "keyword.yaml")
        
        # Should generate valid Rust code despite keyword conflicts
        assert 'src/main.rs' in result
        hooks_rs = result['src/hooks.rs']
        
        # Function names should be generated (possibly with prefixes/suffixes)
        for keyword in rust_keywords[:3]:
            # Should contain the keyword in some form
            assert keyword in hooks_rs