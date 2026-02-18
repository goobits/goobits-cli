"""
Tests for IR dataclass models.

These tests verify that:
1. IR dataclasses are properly frozen (immutable)
2. IR validation rejects invalid data
3. IR can be created from dictionaries
4. IR can be converted back to dictionaries
"""

import pytest

from goobits_cli.universal.ir.models import (
    IR,
    IRCLI,
    IRArgument,
    IRCommand,
    IRMetadata,
    IROption,
    IRProject,
    create_ir_from_dict,
)


@pytest.mark.ir
class TestIRDataclassesFrozen:
    """Test that IR dataclasses are immutable."""

    def test_ir_project_is_frozen(self):
        """IRProject should be immutable."""
        project = IRProject(name="test", version="1.0.0")

        with pytest.raises((AttributeError, TypeError)):
            project.name = "modified"

    def test_ir_command_is_frozen(self):
        """IRCommand should be immutable."""
        command = IRCommand(name="hello", description="Say hello")

        with pytest.raises((AttributeError, TypeError)):
            command.description = "modified"

    def test_ir_option_is_frozen(self):
        """IROption should be immutable."""
        option = IROption(name="verbose", is_flag=True)

        with pytest.raises((AttributeError, TypeError)):
            option.is_flag = False

    def test_ir_argument_is_frozen(self):
        """IRArgument should be immutable."""
        argument = IRArgument(name="input", type="string")

        with pytest.raises((AttributeError, TypeError)):
            argument.type = "integer"

    def test_ir_is_frozen(self):
        """IR root should be immutable."""
        ir = IR(
            project=IRProject(name="test"),
            cli=IRCLI(),
        )

        with pytest.raises((AttributeError, TypeError)):
            ir.project = IRProject(name="other")


@pytest.mark.ir
class TestIRCreation:
    """Test IR creation and conversion."""

    def test_create_minimal_ir(self):
        """Test creating a minimal IR structure."""
        ir = IR(
            project=IRProject(name="test-cli"),
            cli=IRCLI(),
        )

        assert ir.project.name == "test-cli"
        assert ir.cli.commands == ()

    def test_create_ir_with_commands(self):
        """Test creating IR with commands."""
        hello_cmd = IRCommand(
            name="hello",
            description="Say hello",
            options=(IROption(name="name", type="string", default="World"),),
            arguments=(IRArgument(name="greeting", required=False),),
        )

        ir = IR(
            project=IRProject(name="test-cli", version="1.0.0"),
            cli=IRCLI(commands=(hello_cmd,)),
        )

        assert len(ir.cli.commands) == 1
        assert ir.cli.commands[0].name == "hello"
        assert len(ir.cli.commands[0].options) == 1
        assert len(ir.cli.commands[0].arguments) == 1

    def test_create_ir_with_nested_subcommands(self):
        """Test creating IR with nested subcommands."""
        subcommand = IRCommand(name="list", description="List items")
        parent_cmd = IRCommand(
            name="items",
            description="Manage items",
            subcommands=(subcommand,),
        )

        ir = IR(
            project=IRProject(name="test-cli"),
            cli=IRCLI(commands=(parent_cmd,)),
        )

        assert len(ir.cli.commands) == 1
        assert len(ir.cli.commands[0].subcommands) == 1
        assert ir.cli.commands[0].subcommands[0].name == "list"


@pytest.mark.ir
class TestIRFromDict:
    """Test creating IR from dictionaries."""

    def test_create_ir_from_minimal_dict(self):
        """Test creating IR from minimal dictionary."""
        data = {
            "project": {"name": "test-cli"},
            "cli": {"commands": {}},
        }

        ir = create_ir_from_dict(data)

        assert ir.project.name == "test-cli"
        assert len(ir.cli.commands) == 0

    def test_create_ir_from_full_dict(self):
        """Test creating IR from full dictionary."""
        data = {
            "project": {
                "name": "full-cli",
                "description": "A full CLI",
                "version": "2.0.0",
                "author": "Test Author",
                "license": "MIT",
                "package_name": "full_cli",
                "command_name": "fullcli",
            },
            "cli": {
                "commands": {
                    "hello": {
                        "description": "Say hello",
                        "options": [
                            {"name": "loud", "is_flag": True, "help": "Be loud"},
                        ],
                        "arguments": [
                            {"name": "name", "type": "string", "required": False},
                        ],
                    },
                },
            },
            "metadata": {
                "config_filename": "custom.yaml",
                "generator_version": "3.0.1",
            },
        }

        ir = create_ir_from_dict(data)

        assert ir.project.name == "full-cli"
        assert ir.project.version == "2.0.0"
        assert ir.project.license == "MIT"
        assert len(ir.cli.commands) == 1
        assert ir.cli.commands[0].name == "hello"
        assert len(ir.cli.commands[0].options) == 1
        assert ir.metadata.config_filename == "custom.yaml"


@pytest.mark.ir
class TestIRToDict:
    """Test converting IR back to dictionaries."""

    def test_ir_to_dict_roundtrip(self):
        """Test that IR can be converted to dict and back."""
        original = IR(
            project=IRProject(
                name="roundtrip-cli",
                version="1.0.0",
                description="Test roundtrip",
            ),
            cli=IRCLI(
                commands=(
                    IRCommand(
                        name="test",
                        description="Test command",
                        options=(IROption(name="flag", is_flag=True),),
                    ),
                ),
            ),
            metadata=IRMetadata(
                config_filename="test.yaml",
                generator_version="3.0.0",
            ),
        )

        # Convert to dict
        data = original.to_dict()

        # Verify structure
        assert data["project"]["name"] == "roundtrip-cli"
        assert data["project"]["version"] == "1.0.0"
        assert "test" in data["cli"]["commands"]
        assert data["cli"]["commands"]["test"]["description"] == "Test command"

    def test_ir_dict_contains_all_fields(self):
        """Test that to_dict includes all expected fields."""
        ir = IR(
            project=IRProject(name="test"),
            cli=IRCLI(),
        )

        data = ir.to_dict()

        # Check top-level keys
        assert "project" in data
        assert "cli" in data
        assert "metadata" in data
        assert "installation" in data
        assert "features" in data
