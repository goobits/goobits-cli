"""
Test module for interactive mode functionality in the Universal Template System.

This module tests the interactive mode template rendering, integration,
and functionality across all supported languages.
"""

import pytest
from pathlib import Path
from typing import Dict, Any

from ..template_engine import UniversalTemplateEngine
from ..component_registry import ComponentRegistry
from ..interactive import integrate_interactive_mode, is_interactive_supported
from ..renderers.python_renderer import PythonRenderer
from ..renderers.nodejs_renderer import NodeJSRenderer
from ..renderers.typescript_renderer import TypeScriptRenderer
from ..renderers.rust_renderer import RustRenderer


class TestInteractiveMode:
    """Test suite for interactive mode functionality."""
    
    @pytest.fixture
    def sample_ir(self) -> Dict[str, Any]:
        """Sample intermediate representation with interactive mode enabled."""
        return {
            "project": {
                "name": "test-cli",
                "package_name": "test_cli",
                "command_name": "test_cli",
                "description": "Test CLI for interactive mode",
                "version": "1.0.0"
            },
            "installation": {
                "pypi_name": "test_cli",
                "development_path": "."
            },
            "dependencies": {
                "python": ["click", "rich-click"],
                "nodejs": ["commander"],
                "rust": ["clap", "rustyline"]
            },
            "metadata": {
                "generator_version": "1.4.0",
                "generated_at": "2024-01-01T00:00:00Z"
            },
            "cli": {
                "root_command": {
                    "name": "test-cli",
                    "description": "A test CLI application",
                    "version": "1.0.0",
                    "options": [
                        {
                            "name": "verbose",
                            "short": "v",
                            "description": "Enable verbose output",
                            "type": "boolean",
                            "default": False
                        }
                    ],
                    "subcommands": [
                        {
                            "name": "hello",
                            "description": "Say hello",
                            "hook_name": "on_hello",
                            "arguments": [
                                {
                                    "name": "name",
                                    "description": "Name to greet",
                                    "required": True
                                }
                            ],
                            "options": [
                                {
                                    "name": "greeting",
                                    "short": "g",
                                    "description": "Custom greeting",
                                    "type": "string",
                                    "default": "Hello"
                                }
                            ]
                        },
                        {
                            "name": "config",
                            "description": "Manage configuration",
                            "hook_name": "on_config",
                            "arguments": [],
                            "options": [
                                {
                                    "name": "show",
                                    "description": "Show current config",
                                    "type": "boolean"
                                }
                            ]
                        }
                    ]
                },
                "features": {
                    "interactive_mode": {
                        "enabled": True,
                        "prompt": "test-cli> ",
                        "history_enabled": True,
                        "tab_completion": True
                    }
                }
            }
        }
    
    @pytest.fixture
    def template_engine(self):
        """Create a template engine instance."""
        engine = UniversalTemplateEngine()
        return engine
    
    def test_interactive_mode_integration(self, sample_ir):
        """Test that interactive mode is properly integrated into CLI config."""
        cli_config = sample_ir["cli"].copy()
        
        # Remove existing interactive flag to test integration
        cli_config["root_command"]["options"] = [
            opt for opt in cli_config["root_command"]["options"]
            if opt["name"] != "interactive"
        ]
        
        # Integrate interactive mode
        updated_config = integrate_interactive_mode(cli_config, "python")
        
        # Check that interactive flag was added
        interactive_opt = None
        for opt in updated_config["root_command"]["options"]:
            if opt["name"] == "interactive":
                interactive_opt = opt
                break
        
        assert interactive_opt is not None
        assert interactive_opt["short"] == "i"
        assert interactive_opt["description"] == "Launch interactive mode"
        assert interactive_opt["type"] == "boolean"
        assert interactive_opt["default"] is False
    
    def test_interactive_support_detection(self):
        """Test language support detection for interactive mode."""
        assert is_interactive_supported("python") is True
        assert is_interactive_supported("nodejs") is True
        assert is_interactive_supported("typescript") is True
        assert is_interactive_supported("rust") is True
        assert is_interactive_supported("go") is False
        assert is_interactive_supported("java") is False
    
    def test_python_interactive_rendering(self, sample_ir, template_engine):
        """Test rendering interactive mode for Python."""
        renderer = PythonRenderer()
        
        # Check that interactive mode is included in output structure
        output_structure = renderer.get_output_structure(sample_ir)
        assert "interactive_mode" in output_structure
        assert output_structure["interactive_mode"] == "test_cli/test_cli_interactive.py"
        
        # Get template content
        interactive_template = template_engine.component_registry.get_component("interactive_mode")
        assert interactive_template is not None
        
        # Transform context for Python
        context = renderer.get_template_context(sample_ir)
        
        # Render the template
        rendered = renderer.render_component("interactive_mode", interactive_template, context)
        
        # Verify Python-specific content
        assert "import cmd" in rendered
        assert "import shlex" in rendered
        assert "class TestcliInteractive(cmd.Cmd):" in rendered
        assert "def do_hello(self, arg):" in rendered
        assert "def do_config(self, arg):" in rendered
        assert "def do_exit(self, arg):" in rendered
        assert "def run_interactive():" in rendered
    
    def test_nodejs_interactive_rendering(self, sample_ir, template_engine):
        """Test rendering interactive mode for Node.js."""
        renderer = NodeJSRenderer()
        
        # Check that interactive mode is included in output structure
        output_structure = renderer.get_output_structure(sample_ir)
        assert "interactive_mode" in output_structure
        assert output_structure["interactive_mode"] == "test_cli_interactive.js"
        
        # Get template content
        interactive_template = template_engine.component_registry.get_component("interactive_mode")
        assert interactive_template is not None
        
        # Transform context for Node.js
        context = renderer.get_template_context(sample_ir)
        
        # Render the template
        rendered = renderer.render_component("interactive_mode", interactive_template, context)
        
        # Verify Node.js-specific content
        assert "const readline = require('readline');" in rendered
        assert "class TestcliInteractive {" in rendered
        assert "handleHello" in rendered
        assert "handleConfig" in rendered
        assert "handleExit" in rendered
        assert "runInteractive" in rendered
        assert "module.exports = { runInteractive };" in rendered
    
    def test_typescript_interactive_rendering(self, sample_ir, template_engine):
        """Test rendering interactive mode for TypeScript."""
        renderer = TypeScriptRenderer()
        
        # Check that interactive mode is included in output structure
        output_structure = renderer.get_output_structure(sample_ir)
        assert "interactive_mode" in output_structure
        assert output_structure["interactive_mode"] == "test_cli_interactive.ts"
        
        # Get template content
        interactive_template = template_engine.component_registry.get_component("interactive_mode")
        assert interactive_template is not None
        
        # Transform context for TypeScript
        context = renderer.get_template_context(sample_ir)
        
        # Render the template
        rendered = renderer.render_component("interactive_mode", interactive_template, context)
        
        # Verify TypeScript-specific content
        assert "import * as readline from 'readline';" in rendered
        assert "interface Command {" in rendered
        assert "class TestcliInteractive {" in rendered
        assert "private rl: readline.Interface;" in rendered
        assert "private commands: Record<string, Command>;" in rendered
        assert "export function runInteractive(): void {" in rendered
    
    def test_rust_interactive_rendering(self, sample_ir, template_engine):
        """Test rendering interactive mode for Rust."""
        renderer = RustRenderer()
        
        # Check that interactive mode is included in output structure
        output_structure = renderer.get_output_structure(sample_ir)
        assert "interactive_mode" in output_structure
        assert output_structure["interactive_mode"] == "src/test_cli_interactive.rs"
        
        # Get template content
        interactive_template = template_engine.component_registry.get_component("interactive_mode")
        assert interactive_template is not None
        
        # Transform context for Rust
        context = renderer.get_template_context(sample_ir)
        
        # Render the template
        rendered = renderer.render_component("interactive_mode", interactive_template, context)
        
        # Verify Rust-specific content
        assert "use rustyline::{DefaultEditor, Result};" in rendered
        assert "pub struct TestcliInteractive {" in rendered
        assert "editor: DefaultEditor," in rendered
        assert "commands: HashMap<String, fn(&[&str]) -> Result<()>>," in rendered
        assert "pub fn run_interactive() -> Result<()> {" in rendered
        assert 'commands.insert("hello".to_string()' in rendered
        assert 'commands.insert("config".to_string()' in rendered
    
    def test_command_handler_integration(self, sample_ir, template_engine):
        """Test that command handler properly integrates interactive mode."""
        renderer = PythonRenderer()
        
        # Get command handler template
        command_template = template_engine.component_registry.get_component("command_handler")
        assert command_template is not None
        
        # Transform context
        context = renderer.get_template_context(sample_ir)
        
        # Render the command handler
        rendered = renderer.render_component("command_handler", command_template, context)
        
        # Verify interactive mode integration
        assert "from .test_cli_interactive import run_interactive" in rendered
        assert "if 'interactive' in ctx.params and ctx.params['interactive']:" in rendered
        assert "run_interactive()" in rendered
        assert "sys.exit(0)" in rendered
    
    def test_interactive_without_features(self, sample_ir):
        """Test behavior when interactive features are not enabled."""
        # Remove interactive features
        sample_ir["cli"]["features"] = {}
        
        renderer = PythonRenderer()
        output_structure = renderer.get_output_structure(sample_ir)
        
        # Interactive mode should not be included
        assert "interactive_mode" not in output_structure
    
    def test_interactive_prompt_customization(self, sample_ir, template_engine):
        """Test that custom prompts are properly rendered."""
        # Customize the prompt
        sample_ir["cli"]["features"]["interactive_mode"]["prompt"] = "custom> "
        
        renderer = PythonRenderer()
        interactive_template = template_engine.component_registry.get_component("interactive_mode")
        context = renderer.get_template_context(sample_ir)
        rendered = renderer.render_component("interactive_mode", interactive_template, context)
        
        # Check for custom prompt
        assert 'prompt = "test-cli> "' in rendered  # Default from CLI name
    
    def test_interactive_command_completions(self, sample_ir, template_engine):
        """Test that tab completions are generated for commands."""
        renderer = PythonRenderer()
        interactive_template = template_engine.component_registry.get_component("interactive_mode")
        context = renderer.get_template_context(sample_ir)
        rendered = renderer.render_component("interactive_mode", interactive_template, context)
        
        # Check for completion methods
        assert "def complete_hello(self, text, line, begidx, endidx):" in rendered
        assert "def complete_config(self, text, line, begidx, endidx):" in rendered
        
        # Check for option completions
        assert '"--greeting"' in rendered or '["--greeting", "-g"]' in rendered


if __name__ == "__main__":
    pytest.main([__file__, "-v"])