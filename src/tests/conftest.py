"""
Pytest configuration file for goobits-cli tests.

This file provides shared test utilities, fixtures, and helper functions
used across the test suite. It merges functionality from the original
helpers.py and test_helpers.py files.
"""

from typing import Dict, Optional

import pytest

from goobits_cli.core.schemas import (
    ArgumentSchema,
    CLISchema,
    CommandSchema,
    DependenciesSchema,
    GoobitsConfigSchema,
    InstallationSchema,
    MessagesSchema,
    OptionSchema,
    PythonConfigSchema,
    ShellIntegrationSchema,
    ValidationSchema,
)
from goobits_cli.universal.generator import UniversalGenerator


def determine_language(config: GoobitsConfigSchema) -> str:
    """Determine the target language from configuration."""
    return config.language


def generate_cli(
    config: GoobitsConfigSchema, filename: str, version: Optional[str] = None
) -> Dict[str, str]:
    """Generate CLI files based on the configuration language.

    Returns a dictionary mapping file paths to their contents.
    Uses the Universal Generator for all languages.
    """
    language = determine_language(config)
    generator = UniversalGenerator(language)
    return generator.generate_all_files(config, filename, version)


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
        name="test-cli",
        tagline="Test CLI for testing",
        commands={
            "test": CommandSchema(
                desc="Test command",
                args=[
                    ArgumentSchema(
                        name="input",
                        desc="Input file",
                        required=True,
                    )
                ],
                options=[
                    OptionSchema(
                        name="--verbose",
                        short="-v",
                        desc="Enable verbose output",
                        type="bool",
                        default=False,
                    )
                ],
            )
        },
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


@pytest.fixture
def rust_generator():
    """Provide a Rust generator instance."""
    return RustGenerator()


# Parameterized fixtures for consolidated cross-language tests


@pytest.fixture(params=["python", "nodejs", "typescript", "rust"])
def language_test_config(request, basic_cli_schema):
    """Provide a test configuration for each supported language.

    This parameterized fixture enables writing a single test that runs
    across all supported languages, reducing test duplication.
    """
    language = request.param
    package_name = f"test-{language}-cli"
    return create_test_goobits_config(
        package_name=package_name, cli=basic_cli_schema, language=language
    )


@pytest.fixture(
    params=["python", "nodejs", "typescript", "rust"]
)
def parameterized_generator(request):
    """Provide a generator instance with its language identifier.

    This parameterized fixture enables writing unified generator tests
    that validate common patterns across all language generators.

    Returns:
        tuple: (generator_instance, language_name)
    """
    language = request.param
    return UniversalGenerator(language), language


# Note: YAML test integration has been removed in favor of keeping
# feature parity tests as a separate, purpose-built system.
# Use 'make test-parity' to run cross-language CLI validation tests.
