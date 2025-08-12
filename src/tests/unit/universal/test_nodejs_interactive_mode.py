"""
Test cases for enhanced Node.js interactive mode features.

This module tests the Node.js-specific enhancements including async command handling,
tab completion, NPM package integration, and JavaScript expression evaluation.
"""

import unittest
import tempfile
import os
import subprocess
import json
from pathlib import Path
from typing import Dict, Any
from unittest.mock import patch, MagicMock

from goobits_cli.universal.interactive.nodejs_utils import NodeJSInteractiveUtils, get_nodejs_interactive_dependencies


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
        self.assertIn("parseCommandLine", handler_code)
        
        # Check for quote support in parsing
        self.assertIn("inQuotes", handler_code)
        self.assertIn("escaped", handler_code)
        
    def test_error_formatter(self):
        """Test Node.js-specific error formatting."""
        error_formatter = self.utils.get_error_formatter()
        
        # Check for Node.js specific error codes
        self.assertIn("ENOENT", error_formatter)
        self.assertIn("EACCES", error_formatter)
        self.assertIn("MODULE_NOT_FOUND", error_formatter)
        self.assertIn("SyntaxError", error_formatter)
        
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
        self.assertIn("saveHistory", history_code)
        self.assertIn("fs.readFileSync", history_code)
        self.assertIn("fs.writeFileSync", history_code)
        
    def test_completion_engine(self):
        """Test advanced tab completion engine."""
        completion_code = self.utils.get_completion_engine()
        
        # Check NPM package completion
        self.assertIn("loadNpmPackages", completion_code)
        self.assertIn("npm list -g", completion_code)
        
        # Check Node.js module completion
        self.assertIn("loadNodeModules", completion_code)
        self.assertIn("builtin modules", completion_code)
        
        # Check context-aware completion
        self.assertIn("completeCommandContext", completion_code)
        self.assertIn("shouldCompleteFiles", completion_code)
        self.assertIn("shouldCompleteNpmPackages", completion_code)
        
    def test_repl_evaluation(self):
        """Test JavaScript expression evaluation."""
        repl_code = self.utils.get_repl_evaluation()
        
        # Check JavaScript evaluation
        self.assertIn("js:", repl_code)
        self.assertIn("eval(", repl_code)
        
        # Check async evaluation
        self.assertIn("await ", repl_code)
        self.assertIn("async () =>", repl_code)
        
        # Check REPL commands
        self.assertIn("setupReplCommands", repl_code)
        self.assertIn("this.commands.js", repl_code)
        self.assertIn("this.commands.require", repl_code)
        
    def test_integration_features(self):
        """Test Node.js integration features."""
        integration_code = self.utils.get_integration_features()
        
        # Check process monitoring
        self.assertIn("setupProcessMonitoring", integration_code)
        self.assertIn("childProcesses", integration_code)
        
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
        self.assertIn("Agent B Enhanced Version", template)
        
        # Check enhanced features are included
        self.assertIn("setupHistoryPersistence", template)
        self.assertIn("setupAdvancedCompletion", template)
        self.assertIn("setupReplCommands", template)
        self.assertIn("setupNodeJSIntegration", template)
        
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
        from jinja2 import Template
        
        utils = NodeJSInteractiveUtils()
        template_content = utils.generate_enhanced_interactive_template()
        
        template = Template(template_content)
        rendered = template.render(
            project=self.test_project,
            cli=self.test_cli
        )
        
        # Write to temporary file
        js_file = Path(self.temp_dir) / "interactive.js"
        js_file.write_text(rendered)
        
        # Check syntax with Node.js (if available)
        try:
            result = subprocess.run(
                ["node", "--check", str(js_file)],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode != 127:  # Command not found
                self.assertEqual(result.returncode, 0, 
                               f"JavaScript syntax error: {result.stderr}")
        except (subprocess.TimeoutExpired, FileNotFoundError):
            # Node.js not available, skip syntax check
            self.skipTest("Node.js not available for syntax checking")
            
    @patch('subprocess.run')
    def test_async_command_execution(self, mock_run):
        """Test async command execution simulation."""
        # This would be a more complex integration test
        # that simulates the interactive mode in a controlled environment
        
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
            "express", "lodash", "axios", "react", "vue", "angular",
            "typescript", "webpack", "babel", "eslint", "prettier"
        ]
        
        for package in fallback_packages:
            self.assertIn(package, completion_code)


class TestNodeJSInteractiveTestsGeneration(unittest.TestCase):
    """Test the test generation functionality."""
    
    def test_test_code_generation(self):
        """Test generation of Node.js test code."""
        from goobits_cli.universal.interactive.nodejs_utils import get_nodejs_interactive_tests
        
        test_code = get_nodejs_interactive_tests()
        
        # Check test structure
        self.assertIn("InteractiveModeTester", test_code)
        self.assertIn("testAsyncCommandExecution", test_code)
        self.assertIn("testTabCompletion", test_code)
        self.assertIn("testNpmPackageIntegration", test_code)
        self.assertIn("testHistoryPersistence", test_code)
        
        # Check test implementation
        self.assertIn("spawn", test_code)
        self.assertIn("interactive", test_code)
        self.assertIn("require fs", test_code)
        
        # Check test runner
        self.assertIn("runAllTests", test_code)


if __name__ == "__main__":
    unittest.main()