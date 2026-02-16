"""Contract tests for generated main CLI filenames per language."""

from goobits_cli.core.schemas import CLISchema, GoobitsConfigSchema
from goobits_cli.universal.generator import UniversalGenerator
from tests.helpers.generated_paths import find_main_cli_path


def _make_config(language: str) -> GoobitsConfigSchema:
    return GoobitsConfigSchema(
        package_name=f"contract-{language}-cli",
        command_name=f"contract{language}cli",
        display_name=f"Contract {language.title()} CLI",
        description=f"Filename contract test for {language}",
        language=language,
        cli=CLISchema(
            name=f"contract-{language}",
            tagline="Filename contract test",
            commands={"status": {"desc": "Show status"}},
        ),
    )


def test_generated_main_cli_filename_contract_python():
    files = UniversalGenerator("python").generate_all_files(_make_config("python"), "test.yaml")
    main_path = find_main_cli_path(files, "python")
    assert main_path == "src/contract_python_cli/cli.py"


def test_generated_main_cli_filename_contract_nodejs():
    files = UniversalGenerator("nodejs").generate_all_files(_make_config("nodejs"), "test.yaml")
    main_path = find_main_cli_path(files, "nodejs")
    assert main_path == "src/contract_nodejs_cli/cli.js"


def test_generated_main_cli_filename_contract_typescript():
    files = UniversalGenerator("typescript").generate_all_files(_make_config("typescript"), "test.yaml")
    main_path = find_main_cli_path(files, "typescript")
    assert main_path == "src/contract_typescript_cli/cli.ts"


def test_generated_main_cli_filename_contract_rust():
    files = UniversalGenerator("rust").generate_all_files(_make_config("rust"), "test.yaml")
    main_path = find_main_cli_path(files, "rust")
    assert main_path == "src/contract_rust_cli/cli.rs"

