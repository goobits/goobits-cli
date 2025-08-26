"""
Pytest configuration file for goobits-cli tests.

This file provides shared test utilities, fixtures, and helper functions
used across the test suite. It merges functionality from the original
helpers.py and test_helpers.py files.
"""

import pytest
from typing import Dict, Optional
from goobits_cli.schemas import (
    GoobitsConfigSchema,
    CLISchema,
    CommandSchema,
    ArgumentSchema,
    OptionSchema,
    PythonConfigSchema,
    DependenciesSchema,
    InstallationSchema,
    ShellIntegrationSchema,
    ValidationSchema,
    MessagesSchema,
)
from goobits_cli.generators.nodejs import NodeJSGenerator
from goobits_cli.generators.python import PythonGenerator
from goobits_cli.generators.typescript import TypeScriptGenerator
from goobits_cli.generators.rust import RustGenerator


def determine_language(config: GoobitsConfigSchema) -> str:
    """Determine the target language from configuration."""
    return config.language


def generate_cli(
    config: GoobitsConfigSchema, filename: str, version: Optional[str] = None
) -> Dict[str, str]:
    """Generate CLI files based on the configuration language.

    Returns a dictionary mapping file paths to their contents.
    For Python, returns a single-entry dict with the CLI script.
    For Node.js/TypeScript/Rust, returns multiple files.
    """
    language = determine_language(config)

    if language == "nodejs":
        generator = NodeJSGenerator()
        return generator.generate_all_files(config, filename, version)
    elif language == "typescript":
        generator = TypeScriptGenerator()
        return generator.generate_all_files(config, filename, version)
    elif language == "rust":
        generator = RustGenerator()
        return generator.generate_all_files(config, filename, version)
    else:
        # Default to Python
        generator = PythonGenerator()
        cli_code = generator.generate(config, filename, version)
        return {"cli.py": cli_code}  # Single file for Python


def create_test_goobits_config(
    package_name: str, cli: CLISchema, language: str = "nodejs"
) -> GoobitsConfigSchema:
    """Create a minimal GoobitsConfigSchema for testing.

    Args:
        package_name: Package name
        cli: CLI schema configuration
        language: Target language (nodejs or python)

    Returns:
        GoobitsConfigSchema instance
    """
    return GoobitsConfigSchema(
        package_name=package_name,
        command_name=package_name,
        display_name=package_name.replace("-", " ").title(),
        description=f"{package_name} CLI",
        language=language,
        cli=cli,
        python=PythonConfigSchema(),
        dependencies=DependenciesSchema(core=[]),
        installation=InstallationSchema(
            pypi_name=package_name, github_repo=f"example/{package_name}"
        ),
        shell_integration=ShellIntegrationSchema(alias=package_name.replace("-", "")),
        validation=ValidationSchema(),
        messages=MessagesSchema(),
    )


# Pytest fixtures for commonly used test configurations


@pytest.fixture
def basic_cli_schema():
    """Provide a basic CLI schema for testing."""
    return CLISchema(
        commands=[
            CommandSchema(
                name="test",
                description="Test command",
                arguments=[
                    ArgumentSchema(
                        name="input",
                        description="Input file",
                        type="string",
                        required=True,
                    )
                ],
                options=[
                    OptionSchema(
                        name="--verbose",
                        short="-v",
                        description="Enable verbose output",
                        type="boolean",
                        default=False,
                    )
                ],
            )
        ]
    )


@pytest.fixture
def nodejs_test_config(basic_cli_schema):
    """Provide a Node.js test configuration."""
    return create_test_goobits_config(
        package_name="test-nodejs-cli", cli=basic_cli_schema, language="nodejs"
    )


@pytest.fixture
def python_test_config(basic_cli_schema):
    """Provide a Python test configuration."""
    return create_test_goobits_config(
        package_name="test-python-cli", cli=basic_cli_schema, language="python"
    )


@pytest.fixture
def typescript_test_config(basic_cli_schema):
    """Provide a TypeScript test configuration."""
    return create_test_goobits_config(
        package_name="test-typescript-cli", cli=basic_cli_schema, language="typescript"
    )


@pytest.fixture
def python_generator():
    """Provide a Python generator instance."""
    return PythonGenerator()


@pytest.fixture
def nodejs_generator():
    """Provide a Node.js generator instance."""
    return NodeJSGenerator()


@pytest.fixture
def typescript_generator():
    """Provide a TypeScript generator instance."""
    return TypeScriptGenerator()


# Note: YAML test integration has been removed in favor of keeping
# feature parity tests as a separate, purpose-built system.
# Use 'make test-parity' to run cross-language CLI validation tests.
