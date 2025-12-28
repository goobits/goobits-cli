"""Test configuration templates for installation testing.

This module provides predefined test configurations for different installation
scenarios and edge cases.
"""

from typing import Dict, List

from goobits_cli.core.schemas import GoobitsConfigSchema


class TestConfigTemplates:
    """Collection of test configuration templates."""

    @staticmethod
    def minimal_config(
        language: str, package_name: str = "test-minimal-cli"
    ) -> GoobitsConfigSchema:
        """Create a minimal test configuration."""
        config_data = {
            "package_name": package_name,
            "command_name": package_name.replace("_", "-"),
            "display_name": f"Test Minimal {language.title()} CLI",
            "description": f"Minimal test CLI for {language} installation testing",
            "language": language,
            "version": "0.1.0",
            "author": "Test Author",
            "email": "test@example.com",
            "license": "MIT",
            "homepage": "https://github.com/test/test-cli",
            "repository": "https://github.com/test/test-cli",
            "keywords": ["test", "minimal", language],
            "installation": {"pypi_name": package_name, "development_path": "."},
            "python": {"minimum_version": "3.8", "maximum_version": "3.13"},
            "dependencies": {"required": [], "optional": []},
            "shell_integration": {
                "enabled": False,
                "alias": package_name.replace("_", "-"),
            },
            "validation": {
                "check_api_keys": False,
                "check_disk_space": False,
                "minimum_disk_space_mb": 1,
            },
            "messages": {
                "install_success": "Installation completed successfully!",
                "install_dev_success": "Development installation completed successfully!",
                "upgrade_success": "Upgrade completed successfully!",
                "uninstall_success": "Uninstall completed successfully!",
            },
            "cli": {
                "name": f"TestMinimal{language.title()}CLI",
                "version": "0.1.0",
                "tagline": f"Minimal {language} CLI",
                "commands": {"hello": {"desc": "Say hello"}},
            },
        }

        return GoobitsConfigSchema(**config_data)

    @staticmethod
    def complex_config(
        language: str, package_name: str = "test-complex-cli"
    ) -> GoobitsConfigSchema:
        """Create a complex test configuration with multiple commands and options."""
        config_data = {
            "package_name": package_name,
            "command_name": package_name.replace("_", "-"),
            "display_name": f"Test Complex {language.title()} CLI",
            "description": f"Complex test CLI for {language} installation testing with multiple features",
            "language": language,
            "version": "1.0.0",
            "author": "Complex Test Author",
            "email": "complex.test@example.com",
            "license": "MIT",
            "homepage": "https://github.com/test/complex-test-cli",
            "repository": "https://github.com/test/complex-test-cli",
            "keywords": ["test", "complex", "multi-feature", language],
            "installation": {
                "pypi_name": package_name,
                "development_path": ".",
                "extras": {
                    "python": ["dev", "test"] if language == "python" else None,
                    "npm": (
                        ["typescript", "@types/node"]
                        if language in ["nodejs", "typescript"]
                        else None
                    ),
                    "apt": ["git"] if language == "python" else None,
                },
            },
            "python": {"minimum_version": "3.8", "maximum_version": "3.13"},
            "dependencies": {"required": [], "optional": []},
            "shell_integration": {
                "enabled": True,
                "alias": package_name.replace("_", "-"),
            },
            "validation": {
                "check_api_keys": False,
                "check_disk_space": True,
                "minimum_disk_space_mb": 100,
            },
            "messages": {
                "install_success": "Installation completed successfully!",
                "install_dev_success": "Development installation completed successfully!",
                "upgrade_success": "Upgrade completed successfully!",
                "uninstall_success": "Uninstall completed successfully!",
            },
            "cli": {
                "name": f"TestComplex{language.title()}CLI",
                "version": "1.0.0",
                "display_version": True,
                "tagline": f"A complex {language} CLI with multiple features",
                "description": f"This CLI demonstrates complex features in {language}",
                "icon": "🚀",
                "commands": {
                    "greet": {
                        "desc": "Greet someone with customizable options",
                        "args": [
                            {
                                "name": "name",
                                "desc": "Name of the person to greet",
                                "required": True,
                            }
                        ],
                        "options": [
                            {
                                "name": "uppercase",
                                "short": "u",
                                "type": "bool",
                                "desc": "Print greeting in uppercase",
                                "default": False,
                            },
                            {
                                "name": "repeat",
                                "short": "r",
                                "type": "int",
                                "desc": "Number of times to repeat greeting",
                                "default": 1,
                            },
                            {
                                "name": "prefix",
                                "short": "p",
                                "type": "str",
                                "desc": "Prefix for the greeting",
                                "default": "Hello",
                            },
                        ],
                    },
                    "calculate": {
                        "desc": "Perform basic calculations",
                        "args": [
                            {
                                "name": "operation",
                                "desc": "Mathematical operation",
                                "choices": ["add", "subtract", "multiply", "divide"],
                                "required": True,
                            },
                            {
                                "name": "numbers",
                                "desc": "Numbers to operate on",
                                "nargs": "+",
                                "required": True,
                            },
                        ],
                        "options": [
                            {
                                "name": "precision",
                                "type": "int",
                                "desc": "Decimal precision for results",
                                "default": 2,
                            }
                        ],
                    },
                    "config": {
                        "desc": "Configuration management",
                        "subcommands": {
                            "show": {"desc": "Show current configuration"},
                            "set": {
                                "desc": "Set configuration value",
                                "args": [
                                    {
                                        "name": "key",
                                        "desc": "Configuration key",
                                        "required": True,
                                    },
                                    {
                                        "name": "value",
                                        "desc": "Configuration value",
                                        "required": True,
                                    },
                                ],
                            },
                            "reset": {
                                "desc": "Reset configuration to defaults",
                                "options": [
                                    {
                                        "name": "confirm",
                                        "type": "bool",
                                        "desc": "Confirm reset operation",
                                        "default": False,
                                    }
                                ],
                            },
                        },
                    },
                    "file": {
                        "desc": "File operations",
                        "subcommands": {
                            "read": {
                                "desc": "Read file content",
                                "args": [
                                    {
                                        "name": "filepath",
                                        "desc": "Path to file to read",
                                        "required": True,
                                    }
                                ],
                                "options": [
                                    {
                                        "name": "lines",
                                        "short": "n",
                                        "type": "int",
                                        "desc": "Number of lines to read",
                                        "default": None,
                                    }
                                ],
                            },
                            "write": {
                                "desc": "Write content to file",
                                "args": [
                                    {
                                        "name": "filepath",
                                        "desc": "Path to file to write",
                                        "required": True,
                                    },
                                    {
                                        "name": "content",
                                        "desc": "Content to write",
                                        "required": True,
                                    },
                                ],
                                "options": [
                                    {
                                        "name": "append",
                                        "short": "a",
                                        "type": "bool",
                                        "desc": "Append to file instead of overwriting",
                                        "default": False,
                                    }
                                ],
                            },
                        },
                    },
                },
                "options": [
                    {
                        "name": "verbose",
                        "short": "v",
                        "type": "bool",
                        "desc": "Enable verbose output",
                        "default": False,
                    },
                    {
                        "name": "config-file",
                        "short": "c",
                        "type": "str",
                        "desc": "Path to configuration file",
                        "default": None,
                    },
                ],
            },
        }

        return GoobitsConfigSchema(**config_data)

    @staticmethod
    def dependency_heavy_config(
        language: str, package_name: str = "test-deps-cli"
    ) -> GoobitsConfigSchema:
        """Create a configuration with multiple dependencies."""
        config_data = {
            "package_name": package_name,
            "command_name": package_name.replace("_", "-"),
            "display_name": f"Test Dependencies {language.title()} CLI",
            "description": f"Test CLI with dependencies for {language} installation testing",
            "language": language,
            "version": "0.5.0",
            "author": "Deps Test Author",
            "email": "deps.test@example.com",
            "license": "MIT",
            "homepage": "https://github.com/test/deps-test-cli",
            "repository": "https://github.com/test/deps-test-cli",
            "keywords": ["test", "dependencies", language],
            "installation": {
                "pypi_name": package_name,
                "development_path": ".",
                "extras": {
                    "python": (
                        ["requests", "pyyaml", "click", "rich"]
                        if language == "python"
                        else None
                    ),
                    "npm": (
                        ["axios", "yaml", "commander", "chalk"]
                        if language in ["nodejs", "typescript"]
                        else None
                    ),
                    "apt": (
                        ["curl", "jq"]
                        if language in ["python", "nodejs", "typescript"]
                        else None
                    ),
                    "cargo": ["serde", "tokio"] if language == "rust" else None,
                },
            },
            "python": {"minimum_version": "3.8", "maximum_version": "3.13"},
            "dependencies": {
                "required": [
                    {
                        "name": "curl",
                        "type": "command",
                        "description": "Required for HTTP requests",
                    }
                ],
                "optional": [
                    {
                        "name": "jq",
                        "type": "command",
                        "description": "JSON processing utility",
                    }
                ],
            },
            "shell_integration": {
                "enabled": True,
                "alias": package_name.replace("_", "-"),
            },
            "validation": {
                "check_api_keys": True,
                "check_disk_space": True,
                "minimum_disk_space_mb": 500,
            },
            "messages": {
                "install_success": "Installation completed successfully!",
                "install_dev_success": "Development installation completed successfully!",
                "upgrade_success": "Upgrade completed successfully!",
                "uninstall_success": "Uninstall completed successfully!",
            },
            "cli": {
                "name": f"TestDeps{language.title()}CLI",
                "version": "0.5.0",
                "tagline": f"A dependency-heavy {language} CLI",
                "description": f"This CLI tests dependency management in {language}",
                "commands": {
                    "fetch": {
                        "desc": "Fetch data from URL",
                        "args": [
                            {"name": "url", "desc": "URL to fetch", "required": True}
                        ],
                        "options": [
                            {
                                "name": "output",
                                "short": "o",
                                "type": "str",
                                "desc": "Output file path",
                                "default": None,
                            },
                            {
                                "name": "format",
                                "short": "f",
                                "type": "str",
                                "desc": "Output format",
                                "choices": ["json", "yaml", "text"],
                                "default": "json",
                            },
                        ],
                    },
                    "process": {
                        "desc": "Process data files",
                        "args": [
                            {
                                "name": "input_files",
                                "desc": "Input files to process",
                                "nargs": "+",
                                "required": True,
                            }
                        ],
                        "options": [
                            {
                                "name": "output-dir",
                                "type": "str",
                                "desc": "Output directory",
                                "default": "./output",
                            }
                        ],
                    },
                },
            },
        }

        return GoobitsConfigSchema(**config_data)

    @staticmethod
    def edge_case_config(
        language: str, package_name: str = "test-edge-cli"
    ) -> GoobitsConfigSchema:
        """Create a configuration with edge cases and special characters."""
        config_data = {
            "package_name": package_name,
            "command_name": package_name.replace("_", "-"),
            "display_name": f"Test Edge Cases {language.title()} CLI",
            "description": f"Test CLI with edge cases for {language} installation testing",
            "language": language,
            "version": "0.0.1-alpha.1",
            "author": "Edge Case Test Author",
            "email": "edge.test@example.com",
            "license": "Apache-2.0",
            "homepage": "https://github.com/test/edge-case-cli",
            "repository": "https://github.com/test/edge-case-cli",
            "keywords": ["test", "edge-cases", "special-chars", language],
            "installation": {"pypi_name": package_name, "development_path": "."},
            "python": {"minimum_version": "3.9", "maximum_version": "3.12"},
            "dependencies": {"required": [], "optional": []},
            "shell_integration": {
                "enabled": False,
                "alias": package_name.replace("_", "-"),
            },
            "validation": {
                "check_api_keys": False,
                "check_disk_space": False,
                "minimum_disk_space_mb": 1,
            },
            "messages": {
                "install_success": "Installation completed successfully!",
                "install_dev_success": "Development installation completed successfully!",
                "upgrade_success": "Upgrade completed successfully!",
                "uninstall_success": "Uninstall completed successfully!",
            },
            "cli": {
                "name": f"TestEdge{language.title()}CLI",
                "version": "0.0.1-alpha.1",
                "tagline": f"Edge case testing for {language}",
                "description": f"This CLI tests edge cases and special scenarios in {language}",
                "commands": {
                    "test-special-chars": {
                        "desc": "Test command with special characters: !@#$%^&*()",
                        "args": [
                            {
                                "name": "input-with-dashes",
                                "desc": "Input argument with dashes",
                                "required": False,
                            }
                        ],
                        "options": [
                            {
                                "name": "special-option",
                                "type": "str",
                                "desc": "Option with special characters: áéíóú ñ 中文 🎉",
                                "default": "default-value",
                            }
                        ],
                    },
                    "unicode-test": {
                        "desc": "Test Unicode support: 🚀 🎯 ⚡ 🔥 💡",
                        "options": [
                            {
                                "name": "emoji-flag",
                                "type": "bool",
                                "desc": "Enable emoji output 😊",
                                "default": False,
                            }
                        ],
                    },
                },
            },
        }

        return GoobitsConfigSchema(**config_data)

    @staticmethod
    def get_all_templates() -> Dict[str, callable]:
        """Get all available test configuration templates."""
        return {
            "minimal": TestConfigTemplates.minimal_config,
            "complex": TestConfigTemplates.complex_config,
            "dependency_heavy": TestConfigTemplates.dependency_heavy_config,
            "edge_case": TestConfigTemplates.edge_case_config,
        }

    @staticmethod
    def get_template_for_scenario(
        scenario: str, language: str, package_name: str = None
    ) -> GoobitsConfigSchema:
        """Get a test configuration for a specific scenario."""
        templates = TestConfigTemplates.get_all_templates()

        if scenario not in templates:
            raise ValueError(
                f"Unknown scenario: {scenario}. Available: {list(templates.keys())}"
            )

        if package_name is None:
            package_name = f"test-{scenario}-{language}-cli"

        return templates[scenario](language, package_name)


class TestScenarioRunner:
    """Helper class for running test scenarios with different configurations."""

    @staticmethod
    def get_test_matrix() -> List[Dict[str, str]]:
        """Get test matrix of language/scenario combinations."""
        languages = ["python", "nodejs", "typescript", "rust"]
        scenarios = ["minimal", "complex", "dependency_heavy", "edge_case"]

        matrix = []
        for language in languages:
            for scenario in scenarios:
                matrix.append(
                    {
                        "language": language,
                        "scenario": scenario,
                        "test_id": f"{language}_{scenario}",
                    }
                )

        return matrix

    @staticmethod
    def get_critical_test_matrix() -> List[Dict[str, str]]:
        """Get a reduced test matrix for critical scenarios only."""
        languages = ["python", "nodejs", "typescript", "rust"]
        critical_scenarios = ["minimal", "complex"]

        matrix = []
        for language in languages:
            for scenario in critical_scenarios:
                matrix.append(
                    {
                        "language": language,
                        "scenario": scenario,
                        "test_id": f"{language}_{scenario}_critical",
                    }
                )

        return matrix

    @staticmethod
    def get_language_specific_matrix(language: str) -> List[Dict[str, str]]:
        """Get test matrix for a specific language."""
        scenarios = ["minimal", "complex", "dependency_heavy", "edge_case"]

        matrix = []
        for scenario in scenarios:
            matrix.append(
                {
                    "language": language,
                    "scenario": scenario,
                    "test_id": f"{language}_{scenario}",
                }
            )

        return matrix
