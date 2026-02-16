"""Unit tests for core error classes."""

from goobits_cli.core import errors
from goobits_cli.core.errors import (
    ConfigError,
    ConfigFileError,
    ConfigurationError,
    ConfigValidationError,
    DependencyError,
    GeneratorError,
    RenderError,
    TemplateError,
    ValidationError,
)


def test_generator_error_fields():
    err = GeneratorError("boom", error_code=9, details="extra")
    assert err.message == "boom"
    assert err.error_code == 9
    assert err.details == "extra"


def test_configuration_error_includes_field_details():
    err = ConfigurationError("bad config", field="cli.name", suggestion="set cli.name")
    assert err.error_code == 2
    assert err.field == "cli.name"
    assert err.suggestion == "set cli.name"
    assert "Field: cli.name" == err.details


def test_template_error_formats_details():
    err = TemplateError("bad template", template_name="cli.j2", line_number=42)
    assert err.error_code == 3
    assert "Template: cli.j2" in (err.details or "")
    assert "Line: 42" in (err.details or "")


def test_dependency_validation_and_render_errors():
    dep = DependencyError("missing", dependency="node", install_command="apt install nodejs")
    val = ValidationError("invalid", field="language", value="go", valid_options=["python", "nodejs"])
    ren = RenderError("render failed", language="python", component="cli")

    assert dep.error_code == 4
    assert dep.dependency == "node"
    assert "Dependency: node" == dep.details

    assert val.error_code == 2
    assert "Field: language" in (val.details or "")
    assert "Value: go" in (val.details or "")
    assert "Valid options: python, nodejs" in (val.details or "")

    assert ren.error_code == 5
    assert "Language: python" in (ren.details or "")
    assert "Component: cli" in (ren.details or "")


def test_config_errors_fields():
    base = ConfigError("bad", suggestion="fix", config_path="/tmp/a")
    file_err = ConfigFileError("missing", config_path="/tmp/cfg.json", suggestion="create file")
    val_err = ConfigValidationError("invalid", key="api.token", value="x", suggestion="set proper token")

    assert base.message == "bad"
    assert base.suggestion == "fix"
    assert str(base.config_path) == "/tmp/a"

    assert file_err.message == "missing"
    assert str(file_err.config_path) == "/tmp/cfg.json"

    assert val_err.key == "api.token"
    assert val_err.value == "x"
    assert val_err.suggestion == "set proper token"


def test_errors_module_exports_expected_symbols():
    expected = {
        "GeneratorError",
        "ConfigurationError",
        "TemplateError",
        "DependencyError",
        "ValidationError",
        "RenderError",
        "ConfigError",
        "ConfigFileError",
        "ConfigValidationError",
    }
    assert expected.issubset(set(errors.__all__))

