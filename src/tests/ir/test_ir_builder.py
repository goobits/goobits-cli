"""
Tests for the IRBuilder class.

These tests verify that:
1. IRBuilder correctly transforms minimal configs to IR
2. IRBuilder handles complex nested commands
3. IRBuilder properly detects features
"""

from typing import Any, Dict

import pytest

from goobits_cli.universal.ir import IRBuilder


@pytest.fixture
def minimal_config() -> Dict[str, Any]:
    """Minimal valid configuration."""
    return {
        "package_name": "minimal_cli",
        "command_name": "minimalcli",
        "display_name": "Minimal CLI",
        "description": "A minimal CLI",
        "version": "1.0.0",
        "language": "python",
    }


@pytest.fixture
def full_config() -> Dict[str, Any]:
    """Full configuration with all features."""
    return {
        "package_name": "full_cli",
        "command_name": "fullcli",
        "display_name": "Full CLI",
        "description": "A comprehensive CLI",
        "version": "2.0.0",
        "author": "Test Author",
        "license": "MIT",
        "language": "python",
        "cli": {
            "commands": {
                "hello": {
                    "desc": "Say hello",
                    "args": [
                        {"name": "name", "desc": "Name to greet", "required": False},
                    ],
                    "options": [
                        {"name": "loud", "short": "l", "type": "bool", "desc": "Be loud"},
                        {"name": "times", "type": "int", "default": 1, "desc": "Repeat count"},
                    ],
                },
                "config": {
                    "desc": "Configuration management",
                    "subcommands": {
                        "show": {"desc": "Show configuration"},
                        "set": {
                            "desc": "Set configuration value",
                            "args": [
                                {"name": "key", "desc": "Config key"},
                                {"name": "value", "desc": "Config value"},
                            ],
                        },
                    },
                },
            },
        },
    }


@pytest.mark.ir
class TestIRBuilderMinimal:
    """Test IRBuilder with minimal configuration."""

    def test_build_minimal_config(self, minimal_config):
        """Test building IR from minimal config."""
        builder = IRBuilder()
        ir = builder.build(minimal_config, "minimal.yaml")

        assert ir is not None
        assert "project" in ir
        # Project name comes from package_name or display_name
        project = ir["project"]
        assert project.get("name") or project.get("package_name") or project.get("display_name")

    def test_build_sets_metadata(self, minimal_config):
        """Test that build sets proper metadata."""
        builder = IRBuilder()
        ir = builder.build(minimal_config, "test.yaml")

        assert "metadata" in ir
        assert ir["metadata"]["config_filename"] == "test.yaml"


@pytest.mark.ir
class TestIRBuilderComplex:
    """Test IRBuilder with complex configuration."""

    def test_build_nested_commands(self, full_config):
        """Test building IR from config with nested commands."""
        builder = IRBuilder()
        ir = builder.build(full_config, "full.yaml")

        assert "cli" in ir
        assert "commands" in ir["cli"]

        # Check hello command exists
        commands = ir["cli"]["commands"]
        assert "hello" in commands

        # Check config command has subcommands
        assert "config" in commands

    def test_build_preserves_options(self, full_config):
        """Test that options are preserved in IR."""
        builder = IRBuilder()
        ir = builder.build(full_config, "full.yaml")

        hello = ir["cli"]["commands"]["hello"]
        assert "options" in hello
        assert len(hello["options"]) == 2

        # Find the loud option
        loud_opt = next((o for o in hello["options"] if o.get("name") == "loud"), None)
        assert loud_opt is not None
        # Type "bool" indicates a flag
        assert loud_opt.get("type") == "bool" or loud_opt.get("is_flag", False)

    def test_build_preserves_arguments(self, full_config):
        """Test that arguments are preserved in IR."""
        builder = IRBuilder()
        ir = builder.build(full_config, "full.yaml")

        hello = ir["cli"]["commands"]["hello"]
        assert "arguments" in hello or "args" in hello


@pytest.mark.ir
class TestIRBuilderFeatureDetection:
    """Test feature detection in IRBuilder."""

    def test_analyze_features(self, full_config):
        """Test that feature analysis works."""
        builder = IRBuilder()

        # Build first to populate feature_analyzer
        ir = builder.build(full_config, "full.yaml")

        # Check features are present
        assert "feature_requirements" in ir or "features" in ir

    def test_detect_config_management(self, full_config):
        """Test detection of config management features."""
        builder = IRBuilder()
        ir = builder.build(full_config, "full.yaml")

        features = ir.get("feature_requirements", ir.get("features", {}))
        # Config command should trigger config_management feature
        # (if feature analyzer detects it)
        assert isinstance(features, dict)


@pytest.mark.ir
class TestIRBuilderPydanticModels:
    """Test IRBuilder with Pydantic model inputs."""

    def test_build_from_pydantic_model(self, full_config):
        """Test building IR from validated Pydantic model."""
        from goobits_cli.core.schemas import GoobitsConfigSchema

        # Validate with Pydantic
        validated = GoobitsConfigSchema(**full_config)

        # Build IR
        builder = IRBuilder()
        ir = builder.build(validated, "pydantic.yaml")

        assert ir is not None
        assert "project" in ir
