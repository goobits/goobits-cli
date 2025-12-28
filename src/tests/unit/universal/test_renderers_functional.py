"""
Functional tests for Universal Template System Renderers.

Tests the actual rendering functionality, template context generation,
and language-specific code generation for Node.js and TypeScript renderers.
"""

import pytest

from goobits_cli.universal.renderers.nodejs_renderer import NodeJSRenderer
from goobits_cli.universal.renderers.typescript_renderer import TypeScriptRenderer


class TestNodeJSRendererFunctional:
    """Functional tests for NodeJSRenderer with real template rendering"""

    def setup_method(self):
        """Setup test environment"""
        self.renderer = NodeJSRenderer()

        # Create test intermediate representation
        self.test_ir = {
            "project": {
                "name": "Test CLI Tool",
                "description": "A comprehensive test CLI application",
                "version": "2.1.0",
                "author": "Test Author",
                "license": "MIT",
                "package_name": "test-cli-tool",
                "command_name": "testcli",
            },
            "cli": {
                "root_command": {
                    "name": "testcli",
                    "description": "Test CLI application for functionality testing",
                    "version": "2.1.0",
                    "arguments": [],
                    "options": [
                        {
                            "name": "verbose",
                            "short": "v",
                            "description": "Enable verbose output",
                            "type": "flag",
                            "default": False,
                            "required": False,
                        },
                        {
                            "name": "config",
                            "short": "c",
                            "description": "Configuration file path",
                            "type": "string",
                            "default": "config.json",
                            "required": False,
                        },
                    ],
                    "subcommands": [
                        {
                            "name": "build",
                            "description": "Build the project",
                            "arguments": [
                                {
                                    "name": "target",
                                    "description": "Build target directory",
                                    "type": "string",
                                    "required": True,
                                    "multiple": False,
                                }
                            ],
                            "options": [
                                {
                                    "name": "production",
                                    "short": "p",
                                    "description": "Production build",
                                    "type": "flag",
                                    "default": False,
                                    "required": False,
                                }
                            ],
                            "subcommands": [],
                            "hook_name": "on_build",
                        },
                        {
                            "name": "deploy",
                            "description": "Deploy the application",
                            "arguments": [],
                            "options": [
                                {
                                    "name": "environment",
                                    "short": "e",
                                    "description": "Deployment environment",
                                    "type": "string",
                                    "default": "staging",
                                    "required": False,
                                }
                            ],
                            "subcommands": [],
                            "hook_name": "on_deploy",
                        },
                    ],
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
                                "required": True,
                            }
                        ],
                        "options": [
                            {
                                "name": "production",
                                "short": "p",
                                "description": "Production build",
                                "type": "flag",
                            }
                        ],
                        "hook_name": "on_build",
                    },
                    "deploy": {
                        "name": "deploy",
                        "description": "Deploy the application",
                        "arguments": [],
                        "options": [
                            {
                                "name": "environment",
                                "short": "e",
                                "description": "Environment",
                                "type": "string",
                            }
                        ],
                        "hook_name": "on_deploy",
                    },
                },
                "features": {"interactive_mode": {"enabled": True}},
            },
            "installation": {
                "pypi_name": "test-cli-tool",
                "development_path": ".",
                "extras": {},
            },
            "dependencies": {
                "npm": ["lodash@4.17.21", "axios", "uuid@9.0.0"],
                "system": [],
                "python": [],
                "rust": [],
            },
            "metadata": {
                "generated_at": "2023-01-01T00:00:00Z",
                "generator_version": "1.0.0",
            },
        }

    def test_renderer_properties(self):
        """Test basic renderer properties"""
        assert self.renderer.language == "nodejs"

        extensions = self.renderer.file_extensions
        assert "js" in extensions
        assert "json" in extensions
        assert "md" in extensions

    def test_template_context_generation(self):
        """Test generating Node.js-specific template context"""
        context = self.renderer.get_template_context(self.test_ir)

        # Check basic context structure
        assert context["language"] == "nodejs"
        assert context["project"]["name"] == "Test CLI Tool"
        assert context["cli"]["root_command"]["name"] == "testcli"

        # Check Node.js specific additions
        assert "commander_commands" in context
        assert "npm_dependencies" in context
        assert "nodejs_imports" in context
        assert "hook_functions" in context
        assert "js_package_name" in context
        assert "js_command_name" in context
        assert "node_version" in context
        assert context["node_version"] == ">=14.0.0"

    def test_commander_structure_building(self):
        """Test building Commander.js command structure"""
        context = self.renderer.get_template_context(self.test_ir)
        commander = context["commander_commands"]

        # Check root command
        assert commander["root_command"]["name"] == "testcli"
        assert (
            commander["root_command"]["description"]
            == "Test CLI application for functionality testing"
        )
        assert commander["root_command"]["version"] == "2.1.0"

        # Check root options
        root_options = commander["root_command"]["options"]
        assert len(root_options) == 2

        verbose_option = next(opt for opt in root_options if "verbose" in opt["flags"])
        assert "-v" in verbose_option["flags"]
        assert "--verbose" in verbose_option["flags"]
        assert verbose_option["type"] == "boolean"

        # Check subcommands
        assert len(commander["subcommands"]) == 2

        build_cmd = next(
            cmd for cmd in commander["subcommands"] if cmd["name"] == "build"
        )
        assert build_cmd["description"] == "Build the project"
        assert len(build_cmd["arguments"]) == 1
        assert len(build_cmd["options"]) == 1
        assert build_cmd["hook_name"] == "on_build"

    def test_npm_dependencies_building(self):
        """Test building NPM dependencies"""
        context = self.renderer.get_template_context(self.test_ir)
        npm_deps = context["npm_dependencies"]

        # Should include framework dependencies
        assert "commander" in npm_deps
        assert "chalk" in npm_deps

        # Should include IR dependencies
        assert "lodash" in npm_deps
        assert "axios" in npm_deps
        assert "uuid" in npm_deps

        # Check version handling
        assert npm_deps["lodash"] == "^4.17.21"
        assert npm_deps["uuid"] == "^9.0.0"
        assert npm_deps["axios"] == "latest"  # No version specified

    def test_imports_generation(self):
        """Test generating ES module imports"""
        context = self.renderer.get_template_context(self.test_ir)
        imports = context["nodejs_imports"]

        # Should include framework imports
        assert "import { Command } from 'commander';" in imports
        assert "import chalk from 'chalk';" in imports

        # Should include interactive mode imports (since enabled) - using CommonJS for interactive mode
        # Note: The interactive mode template uses require() syntax, not import
        # So interactive imports won't be in the ES module imports list

        # Should include dependency imports
        assert "import lodash from 'lodash';" in imports
        assert "import axios from 'axios';" in imports
        assert "import uuid from 'uuid';" in imports

    def test_hook_functions_generation(self):
        """Test generating hook function definitions"""
        context = self.renderer.get_template_context(self.test_ir)
        hooks = context["hook_functions"]

        assert len(hooks) == 2

        build_hook = next(hook for hook in hooks if hook["command_name"] == "build")
        assert build_hook["name"] == "on_build"
        assert build_hook["js_name"] == "onBuild"
        assert build_hook["description"] == "Build the project"
        assert len(build_hook["arguments"]) == 1
        assert len(build_hook["options"]) == 1

        deploy_hook = next(hook for hook in hooks if hook["command_name"] == "deploy")
        assert deploy_hook["name"] == "on_deploy"
        assert deploy_hook["js_name"] == "onDeploy"
