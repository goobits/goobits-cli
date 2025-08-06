"""
Test suite for RustRenderer

This module tests the Rust-specific rendering capabilities of the Universal Template System.
"""

import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path
from typing import Dict, Any

from .rust_renderer import RustRenderer


class TestRustRenderer:
    """Test cases for RustRenderer"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.renderer = RustRenderer()
        self.sample_ir = {
            "project": {
                "name": "My CLI Tool",
                "description": "A sample CLI tool",
                "version": "1.0.0",
                "author": "Test Author",
                "package_name": "my-cli-tool",
                "command_name": "mycli",
            },
            "cli": {
                "root_command": {
                    "name": "mycli",
                    "description": "Sample CLI tool",
                    "version": "1.0.0",
                    "arguments": [
                        {
                            "name": "input-file",
                            "description": "Input file path",
                            "type": "string",
                            "required": True,
                        }
                    ],
                    "options": [
                        {
                            "name": "verbose",
                            "short": "v",
                            "description": "Enable verbose output",
                            "type": "flag",
                            "default": False,
                        },
                        {
                            "name": "output-format",
                            "description": "Output format",
                            "type": "string",
                            "default": "json",
                            "choices": ["json", "yaml", "text"],
                        }
                    ],
                    "subcommands": [],
                },
                "commands": {
                    "build": {
                        "name": "build",
                        "description": "Build the project",
                        "arguments": [
                            {
                                "name": "target",
                                "description": "Build target",
                                "type": "string",
                                "required": False,
                            }
                        ],
                        "options": [
                            {
                                "name": "release",
                                "description": "Build in release mode",
                                "type": "bool",
                                "default": False,
                            },
                            {
                                "name": "jobs",
                                "short": "j",
                                "description": "Number of parallel jobs",
                                "type": "int",
                                "default": 4,
                            }
                        ],
                        "subcommands": [],
                        "hook_name": "on_build",
                    }
                },
                "global_options": [],
                "completion": {
                    "enabled": True,
                    "shells": ["bash", "zsh", "fish"],
                }
            },
            "installation": {
                "pypi_name": "my-cli-tool",
                "development_path": ".",
                "extras": {},
            },
            "dependencies": {
                "python": [],
                "system": [],
                "npm": [],
                "rust": ["serde", "tokio"],
            },
            "metadata": {
                "generated_at": "2025-01-01T00:00:00Z",
                "generator_version": "1.0.0",
                "source_config": {},
            }
        }
    
    def test_language_property(self):
        """Test language property returns 'rust'"""
        assert self.renderer.language == "rust"
    
    def test_file_extensions(self):
        """Test file extensions mapping"""
        extensions = self.renderer.file_extensions
        assert "rs" in extensions
        assert "toml" in extensions
        assert extensions["rs"] == "rust"
        assert extensions["toml"] == "toml"
    
    def test_get_template_context(self):
        """Test template context generation"""
        context = self.renderer.get_template_context(self.sample_ir)
        
        # Check that original IR is preserved
        assert "project" in context
        assert "cli" in context
        
        # Check Rust-specific additions
        assert "rust" in context
        rust_info = context["rust"]
        assert rust_info["crate_name"] == "my_cli_tool"
        assert rust_info["struct_name"] == "Mycli"
        assert "imports" in rust_info
        assert "dependencies" in rust_info
        
        # Check CLI transformation
        cli = context["cli"]
        root_cmd = cli["root_command"]
        assert "rust_name" in root_cmd
        assert root_cmd["rust_name"] == "Mycli"
        
        # Check argument transformation
        assert len(root_cmd["arguments"]) == 1
        arg = root_cmd["arguments"][0]
        assert arg["rust_type"] == "String"
        assert arg["rust_name"] == "input_file"
        
        # Check option transformation
        assert len(root_cmd["options"]) == 2
        verbose_opt = root_cmd["options"][0]
        assert verbose_opt["rust_type"] == "bool"
        assert verbose_opt["rust_name"] == "verbose"
        
        format_opt = root_cmd["options"][1]
        assert format_opt["rust_type"] == "String"
        assert format_opt["rust_name"] == "output_format"
        
        # Check metadata
        assert context["metadata"]["language"] == "rust"
        assert context["metadata"]["framework"] == "clap"
    
    def test_custom_filters(self):
        """Test custom Jinja2 filters"""
        filters = self.renderer.get_custom_filters()
        
        # Check filter presence
        expected_filters = [
            "rust_type", "rust_struct_name", "rust_function_name",
            "rust_field_name", "rust_const_name", "clap_attribute",
            "rust_default", "escape_rust_string", "rust_doc_comment"
        ]
        
        for filter_name in expected_filters:
            assert filter_name in filters
            assert callable(filters[filter_name])
    
    def test_rust_type_conversion(self):
        """Test generic type to Rust type conversion"""
        test_cases = [
            ("string", "String"),
            ("int", "i32"),
            ("bool", "bool"),
            ("flag", "bool"),
            ("path", "std::path::PathBuf"),
            ("file", "std::path::PathBuf"),
            ("json", "serde_json::Value"),
            ("unknown", "String"),  # fallback
        ]
        
        for generic_type, expected_rust_type in test_cases:
            assert self.renderer._rust_type(generic_type) == expected_rust_type
    
    def test_naming_conventions(self):
        """Test Rust naming convention conversions"""
        # Snake case (functions, variables)
        assert self.renderer._to_snake_case("my-command") == "my_command"
        assert self.renderer._to_snake_case("MyCommand") == "my_command"
        assert self.renderer._to_snake_case("myCommand") == "my_command"
        assert self.renderer._to_snake_case("my_command") == "my_command"
        
        # Pascal case (structs, enums)
        assert self.renderer._to_pascal_case("my-command") == "MyCommand"
        assert self.renderer._to_pascal_case("my_command") == "MyCommand"
        assert self.renderer._to_pascal_case("myCommand") == "MyCommand"
        
        # Screaming snake case (constants)
        assert self.renderer._to_screaming_snake_case("my-command") == "MY_COMMAND"
        assert self.renderer._to_screaming_snake_case("MyCommand") == "MY_COMMAND"
    
    def test_clap_attribute_generation(self):
        """Test Clap attribute generation for options"""
        option = {
            "name": "output-format",
            "short": "o", 
            "description": "Output format choice",
            "type": "string",
            "default": "json",
            "choices": ["json", "yaml", "text"]
        }
        
        attr = self.renderer._clap_attribute(option)
        
        assert 'long = "output-format"' in attr
        assert "short = 'o'" in attr
        assert 'help = "Output format choice"' in attr
        assert 'default_value = "json"' in attr
        assert 'value_parser = clap::builder::PossibleValuesParser::new(["json", "yaml", "text"])' in attr
    
    def test_rust_defaults(self):
        """Test Rust default value formatting"""
        assert self.renderer._rust_default(True, "bool") == "true"
        assert self.renderer._rust_default(False, "flag") == "false"
        assert self.renderer._rust_default(42, "int") == "42"
        assert self.renderer._rust_default(3.14, "float") == "3.14"
        assert self.renderer._rust_default("hello", "string") == '"hello"'
    
    def test_string_escaping(self):
        """Test Rust string literal escaping"""
        test_cases = [
            ('hello world', 'hello world'),
            ('hello "world"', 'hello \\"world\\"'),
            ('line1\nline2', 'line1\\nline2'),
            ('tab\there', 'tab\\there'),
            ('back\\slash', 'back\\\\slash'),
        ]
        
        for input_str, expected in test_cases:
            assert self.renderer._escape_rust_string(input_str) == expected
    
    def test_doc_comment_generation(self):
        """Test Rust documentation comment generation"""
        single_line = "This is a description"
        expected_single = "/// This is a description"
        assert self.renderer._rust_doc_comment(single_line) == expected_single
        
        multi_line = "Line 1\nLine 2\nLine 3"
        expected_multi = "/// Line 1\n/// Line 2\n/// Line 3"
        assert self.renderer._rust_doc_comment(multi_line) == expected_multi
    
    def test_output_structure(self):
        """Test Rust CLI output file structure"""
        structure = self.renderer.get_output_structure(self.sample_ir)
        
        expected_files = {
            "command_handler": "src/main.rs",
            "config_manager": "src/config.rs",
            "error_handler": "src/errors.rs", 
            "hook_system": "src/hooks.rs",
            "completion_engine": "src/completion_engine.rs",
            "commands": "src/commands.rs",
            "utils": "src/utils.rs",
            "lib": "src/lib.rs",
            "cargo_manifest": "Cargo.toml",
            "setup_script": "setup.sh",
        }
        
        for component, expected_path in expected_files.items():
            assert component in structure
            assert structure[component] == expected_path
    
    def test_render_component(self):
        """Test component rendering with Rust context"""
        template_content = """
// Rust CLI for {{ project.name }}
use clap::Parser;

#[derive(Parser)]
#[command(name = "{{ project.command_name | rust_function_name }}")]
struct {{ project.command_name | rust_struct_name }} {
    /// {{ cli.root_command.options[0].description }}
    #[arg(long = "{{ cli.root_command.options[0].name }}"{% if cli.root_command.options[0].short %}, short = '{{ cli.root_command.options[0].short }}'{% endif %})]
    {{ cli.root_command.options[0].name | rust_field_name }}: {{ cli.root_command.options[0].type | rust_type }},
}
        """.strip()
        
        context = self.renderer.get_template_context(self.sample_ir)
        result = self.renderer.render_component("test_component", template_content, context)
        
        # Check that template was rendered with Rust-specific values
        assert "// Rust CLI for My CLI Tool" in result
        assert "struct Mycli {" in result
        assert "verbose: bool," in result
        assert 'long = "verbose"' in result
        assert "short = 'v'" in result
    
    def test_dependency_detection(self):
        """Test Rust dependency detection from IR"""
        context = self.renderer.get_template_context(self.sample_ir)
        deps = context["rust"]["dependencies"]
        
        # Check standard dependencies  
        assert "clap" in deps
        assert "anyhow" in deps
        assert "serde" in deps
        assert "serde_yaml" in deps
        
        # Check dependencies from IR
        assert "serde" in deps  # From IR dependencies.rust
        assert "tokio" in deps  # From IR dependencies.rust
    
    def test_import_generation(self):
        """Test Rust import generation"""
        context = self.renderer.get_template_context(self.sample_ir)
        imports = context["rust"]["imports"]
        
        # Check essential imports
        expected_imports = [
            "use anyhow::{Context, Result};",
            "use clap::{Parser, Subcommand, CommandFactory};",
            "use std::collections::HashMap;",
            "use serde::{Deserialize, Serialize};",
        ]
        
        for expected in expected_imports:
            assert expected in imports
    
    def test_command_transformation(self):
        """Test command transformation with Rust specifics"""
        context = self.renderer.get_template_context(self.sample_ir)
        build_cmd = context["cli"]["commands"]["build"]
        
        assert build_cmd["rust_name"] == "Build"
        assert build_cmd["rust_function"] == "build"
        
        # Check argument transformation
        target_arg = build_cmd["arguments"][0]
        assert target_arg["rust_type"] == "String"
        assert target_arg["rust_name"] == "target"
        
        # Check option transformation
        release_opt = build_cmd["options"][0]
        assert release_opt["rust_type"] == "bool"
        assert release_opt["rust_name"] == "release"
        
        jobs_opt = build_cmd["options"][1]
        assert jobs_opt["rust_type"] == "i32"
        assert jobs_opt["rust_name"] == "jobs"
    
    def test_post_processing(self):
        """Test post-processing of generated Rust code"""
        content_with_issues = """


        // Some code here
        let x = 5;    
        
        
        """
        
        processed = self.renderer._post_process_rust_code(content_with_issues)
        
        # Should remove leading/trailing empty lines and trailing whitespace
        lines = processed.split('\n')
        assert lines[0] == "        // Some code here"  # Leading whitespace preserved
        assert lines[1] == "        let x = 5;"  # Trailing whitespace removed but leading preserved
        assert len(lines) == 3  # Including final newline
        assert not lines[1].endswith("    ")  # Trailing whitespace removed


if __name__ == "__main__":
    pytest.main([__file__])