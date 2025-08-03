"""Test utility functions for creating test configurations."""
from goobits_cli.schemas import (
    GoobitsConfigSchema, CLISchema, CommandSchema, ArgumentSchema, OptionSchema,
    PythonConfigSchema, DependenciesSchema, InstallationSchema, 
    ShellIntegrationSchema, ValidationSchema, MessagesSchema
)


def create_test_goobits_config(
    package_name: str,
    cli: CLISchema,
    language: str = "nodejs"
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
            pypi_name=package_name,
            github_repo=f"example/{package_name}"
        ),
        shell_integration=ShellIntegrationSchema(
            alias=package_name.replace("-", "")
        ),
        validation=ValidationSchema(),
        messages=MessagesSchema()
    )