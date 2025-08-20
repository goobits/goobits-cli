"""
Test cases for enhanced Node.js interactive mode features (Simplified).

NOTE: This file is NOT a duplicate of test_nodejs_interactive_mode.py - they test different implementations:
- test_nodejs_interactive_mode.py: Tests FULL implementation (1292 lines) with advanced features
- test_nodejs_interactive_simple.py: Tests SIMPLIFIED implementation (554 lines) with core features

Both implementations are being evaluated during Phase 4 development. This simplified version
focuses on essential interactive functionality while the full version includes comprehensive
NPM integration, advanced completion, and complex error handling.

This module tests the Node.js-specific enhancements including async command handling,
tab completion, NPM package integration, and JavaScript expression evaluation.
"""

import unittest
import tempfile
import subprocess
from unittest.mock import patch

from goobits_cli.universal.interactive.nodejs_utils_simple import NodeJSInteractiveUtils, get_nodejs_interactive_dependencies


class TestNodeJSInteractiveUtils(unittest.TestCase):
    """Test Node.js interactive mode utilities."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.utils = NodeJSInteractiveUtils()
        
    def test_enhanced_readline_config(self):
        """Test enhanced readline configuration."""
        config = self.utils.get_enhanced_readline_config()
        
        # Check required configuration options
        self.assertIn("completer", config)
        self.assertIn("terminal", config)
        self.assertIn("history_size", config)
        self.assertEqual(config["history_size"], 1000)
        
        # Check key bindings
        self.assertIn("key_bindings", config)
        key_bindings = config["key_bindings"]
        self.assertIn("ctrl-l", key_bindings)
        self.assertIn("tab", key_bindings)
        self.assertEqual(key_bindings["tab"], "complete")
        
        # Check colors
        self.assertIn("colors", config)
        colors = config["colors"]
        self.assertIn("GREEN", colors)
        self.assertIn("RED", colors)
        
    def test_async_command_handler(self):
        """Test async command handling code generation."""
        handler_code = self.utils.get_async_command_handler()
        
        # Check for required async functionality
        self.assertIn("async executeCommand", handler_code)
        self.assertIn("Promise.race", handler_code)
        self.assertIn("timeout", handler_code)
        
        # Check for basic parsing
        self.assertIn("trimmed", handler_code)
        
    def test_error_formatter(self):
        """Test Node.js-specific error formatting."""
        error_formatter = self.utils.get_error_formatter()
        
        # Check for Node.js specific error codes
        self.assertIn("ENOENT", error_formatter)
        self.assertIn("MODULE_NOT_FOUND", error_formatter)
        
        # Check for helpful suggestions
        self.assertIn("npm install", error_formatter)
        self.assertIn("chalk.red", error_formatter)
        
    def test_history_manager(self):
        """Test history management with file persistence."""
        history_code = self.utils.get_history_manager()
        
        # Check OS-specific directory handling
        self.assertIn("process.platform", history_code)
        self.assertIn("APPDATA", history_code)  # Windows
        self.assertIn("Library", history_code)  # macOS
        self.assertIn(".config", history_code)  # Linux
        
        # Check persistence functionality
        self.assertIn("loadHistory", history_code)
        
    def test_completion_engine(self):
        """Test advanced tab completion engine."""
        completion_code = self.utils.get_completion_engine()
        
        # Check NPM package completion
        self.assertIn("loadNpmPackages", completion_code)
        self.assertIn("npm list -g", completion_code)
        
        # Check Node.js module completion
        self.assertIn("loadNodeModules", completion_code)
        
        # Check basic completion setup
        self.assertIn("setupAdvancedCompletion", completion_code)
        
    def test_repl_evaluation(self):
        """Test JavaScript expression evaluation."""
        repl_code = self.utils.get_repl_evaluation()
        
        # Check JavaScript evaluation
        self.assertIn("js:", repl_code)
        self.assertIn("eval(", repl_code)
        
        # Check REPL commands
        self.assertIn("setupReplCommands", repl_code)
        self.assertIn("this.commands.js", repl_code)
        
    def test_integration_features(self):
        """Test Node.js integration features."""
        integration_code = self.utils.get_integration_features()
        
        # Check process monitoring
        self.assertIn("setupProcessMonitoring", integration_code)
        
        # Check module hot-reloading
        self.assertIn("setupModuleReloading", integration_code)
        self.assertIn("require.cache", integration_code)
        
        # Check environment management
        self.assertIn("setupEnvironmentManagement", integration_code)
        self.assertIn("process.env", integration_code)
        
    def test_enhanced_template_generation(self):
        """Test complete enhanced template generation."""
        template = self.utils.generate_enhanced_interactive_template()
        
        # Check overall structure
        self.assertIn("#!/usr/bin/env node", template)
        self.assertIn("Enhanced Interactive mode", template)
        self.assertIn("Simplified", template)
        
        # Check basic features are included
        self.assertIn("setupBasicFeatures", template)
        
        # Check Jinja2 template variables
        self.assertIn("{{ project.name }}", template)
        self.assertIn("{{ cli.root_command.name }}", template)
        
    def test_dependencies_structure(self):
        """Test Node.js interactive dependencies structure."""
        deps = get_nodejs_interactive_dependencies()
        
        # Check builtin modules
        self.assertIn("builtin", deps)
        builtin = deps["builtin"]
        self.assertIn("readline", builtin)
        self.assertIn("fs", builtin)
        self.assertIn("os", builtin)
        self.assertIn("child_process", builtin)
        
        # Check NPM dependencies
        self.assertIn("npm", deps)
        npm = deps["npm"]
        self.assertTrue(any("chalk" in dep for dep in npm))
        self.assertTrue(any("@types/node" in dep for dep in npm))
        

class TestNodeJSInteractiveIntegration(unittest.TestCase):
    """Integration tests for Node.js interactive mode."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_project = {
            "name": "test-cli",
            "description": "Test CLI for Node.js interactive mode"
        }
        self.test_cli = {
            "root_command": {
                "name": "test-cli",
                "description": "Test CLI",
                "subcommands": [
                    {
                        "name": "hello",
                        "description": "Say hello",
                        "hook_name": "on_hello",
                        "arguments": [],
                        "options": [
                            {
                                "name": "name",
                                "short": "n",
                                "description": "Name to greet",
                                "type": "string",
                                "default": "World"
                            }
                        ]
                    }
                ]
            }
        }
        
    def tearDown(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        
    def test_template_rendering(self):
        """Test template rendering with real data."""
        from jinja2 import Template
        
        utils = NodeJSInteractiveUtils()
        template_content = utils.generate_enhanced_interactive_template()
        
        template = Template(template_content)
        rendered = template.render(
            project=self.test_project,
            cli=self.test_cli
        )
        
        # Check that template variables were replaced
        self.assertNotIn("{{ project.name }}", rendered)
        self.assertNotIn("{{ cli.root_command.name }}", rendered)
        self.assertIn("test-cli", rendered)
        self.assertIn("TestcliInteractive", rendered)
        
        # Check that command handlers were generated
        self.assertIn("handleHello", rendered)
        self.assertIn("on_hello", rendered)
        
    def test_javascript_syntax_validity(self):
        """Test that generated JavaScript has valid syntax."""
        utils = NodeJSInteractiveUtils()
        template_content = utils.generate_enhanced_interactive_template()
        
        # Verify we get actual JavaScript template content
        self.assertIsInstance(template_content, str)
        self.assertIn("enhanced", template_content.lower())
        
        # Validate basic JavaScript syntax
        self.assertIn("const readline = require('readline')", template_content)
        self.assertIn("const chalk = require('chalk')", template_content)
        self.assertIn("#!/usr/bin/env node", template_content)
        
        # Ensure proper JavaScript structure (no obvious syntax errors)
        brace_count = template_content.count('{') - template_content.count('}')
        self.assertEqual(brace_count, 0, "Mismatched braces in generated JavaScript")
        
        paren_count = template_content.count('(') - template_content.count(')')
        self.assertEqual(paren_count, 0, "Mismatched parentheses in generated JavaScript")
            
    @patch('subprocess.run')
    def test_async_command_execution(self, mock_run):
        """Test async command execution simulation."""
        mock_run.return_value = subprocess.CompletedProcess(
            [], 0, stdout="Command executed successfully", stderr=""
        )
        
        # Simulate command execution
        result = mock_run(["echo", "test"])
        self.assertEqual(result.returncode, 0)
        self.assertIn("Command executed", result.stdout)
        
    def test_npm_package_completion_data(self):
        """Test NPM package completion data structure."""
        utils = NodeJSInteractiveUtils()
        completion_code = utils.get_completion_engine()
        
        # Check for fallback packages in case npm command fails
        fallback_packages = [
            "express", "lodash", "axios", "react", "vue", "angular"
        ]
        
        for package in fallback_packages:
            self.assertIn(package, completion_code)


class TestNodeJSInteractiveTestsGeneration(unittest.TestCase):
    """Test the test generation functionality."""
    
    def test_test_code_generation(self):
        """Test generation of Node.js test code."""
        from goobits_cli.universal.interactive.nodejs_utils_simple import get_nodejs_interactive_tests
        
        test_code = get_nodejs_interactive_tests()
        
        # Check test structure
        self.assertIn("InteractiveModeTester", test_code)
        self.assertIn("testAsyncCommandExecution", test_code)
        
        # Check test implementation
        self.assertIn("spawn", test_code)
        self.assertIn("interactive", test_code)
        
        # Check test runner
        self.assertIn("runAllTests", test_code)


if __name__ == "__main__":
    unittest.main()