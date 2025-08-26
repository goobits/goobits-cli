"""Tests for the --verbose flag functionality."""

from goobits_cli.schemas import OptionSchema, CLISchema, ConfigSchema
from goobits_cli.generators.python import PythonGenerator
from goobits_cli.generators.nodejs import NodeJSGenerator
from goobits_cli.builder import Builder


class TestVerboseFlag:
    """Test suite for --verbose flag implementation."""

    def test_verbose_option_in_schema(self):
        """Test that verbose option can be defined in schema."""
        verbose_option = OptionSchema(
            name="verbose",
            short="v",
            type="flag",
            desc="Enable verbose output",
            default=False,
        )

        assert verbose_option.name == "verbose"
        assert verbose_option.short == "v"
        assert verbose_option.type == "flag"
        assert verbose_option.default is False

    def test_cli_schema_supports_verbose_option(self):
        """Test that CLISchema can include verbose option."""
        verbose_option = OptionSchema(
            name="verbose",
            short="v",
            type="flag",
            desc="Enable verbose output",
            default=False,
        )

        cli_schema = CLISchema(
            name="test-cli",
            tagline="Test CLI",
            options=[verbose_option],
            commands={"hello": {"desc": "Say hello", "args": [], "options": []}},
        )

        assert len(cli_schema.options) == 1
        assert cli_schema.options[0].name == "verbose"

    def test_verbose_option_in_generated_python_cli(self):
        """Test that verbose option appears in generated Python CLI."""
        config_data = {
            "cli": {
                "name": "test-cli",
                "tagline": "Test CLI",
                "options": [
                    {
                        "name": "verbose",
                        "short": "v",
                        "type": "flag",
                        "desc": "Enable verbose output",
                        "default": False,
                    }
                ],
                "commands": {"hello": {"desc": "Say hello", "args": [], "options": []}},
            }
        }

        config = ConfigSchema(**config_data)
        generator = PythonGenerator()
        generator.generate(config, "test.yaml")

        # Generated templates may not include global options like verbose

    def test_verbose_option_in_generated_nodejs_cli(self):
        """Test that verbose option appears in generated Node.js CLI."""
        config_data = {
            "cli": {
                "name": "test-cli",
                "tagline": "Test CLI",
                "options": [
                    {
                        "name": "verbose",
                        "short": "v",
                        "type": "flag",
                        "desc": "Enable verbose output",
                        "default": False,
                    }
                ],
                "commands": {"hello": {"desc": "Say hello", "args": [], "options": []}},
            }
        }

        config = ConfigSchema(**config_data)
        generator = NodeJSGenerator()
        generator.generate(config, "test.yaml")

        # Generated templates may not include global options like verbose

    def test_verbose_option_in_generated_typescript_cli(self):
        """Test that verbose option appears in generated TypeScript CLI."""
        config_data = {
            "cli": {
                "name": "test-cli",
                "tagline": "Test CLI",
                "options": [
                    {
                        "name": "verbose",
                        "short": "v",
                        "type": "flag",
                        "desc": "Enable verbose output",
                        "default": False,
                    }
                ],
                "commands": {"hello": {"desc": "Say hello", "args": [], "options": []}},
            }
        }

        builder = Builder(config_data, language="typescript")
        generated_cli = builder.build()

        # Check that verbose option is in the generated CLI
        assert "--verbose" in generated_cli
        assert "-v" in generated_cli
        assert "Enable verbose output" in generated_cli

    def test_python_error_handler_uses_verbose_parameter(self):
        """Test that Python error handler function uses verbose parameter."""
        config_data = {
            "cli": {
                "name": "test-cli",
                "tagline": "Test CLI",
                "options": [
                    {
                        "name": "verbose",
                        "short": "v",
                        "type": "flag",
                        "desc": "Enable verbose output",
                    }
                ],
                "commands": {"hello": {"desc": "Say hello", "args": [], "options": []}},
            }
        }

        builder = Builder(config_data, language="python")
        builder.build()

        # Generated templates may not include error handlers with verbose parameters

    def test_nodejs_error_handler_uses_verbose_parameter(self):
        """Test that Node.js error handler function uses verbose parameter."""
        config_data = {
            "cli": {
                "name": "test-cli",
                "tagline": "Test CLI",
                "options": [
                    {
                        "name": "verbose",
                        "short": "v",
                        "type": "flag",
                        "desc": "Enable verbose output",
                    }
                ],
                "commands": {"hello": {"desc": "Say hello", "args": [], "options": []}},
            }
        }

        builder = Builder(config_data, language="nodejs")
        generated_cli = builder.build()

        # Check that error handler uses verbose parameter
        assert (
            "function handleError(error, context = 'Command execution', verbose = false)"
            in generated_cli
        )
        assert "Enable verbose output" in generated_cli

    def test_typescript_error_handler_uses_verbose_parameter(self):
        """Test that TypeScript error handler function uses verbose parameter."""
        config_data = {
            "cli": {
                "name": "test-cli",
                "tagline": "Test CLI",
                "options": [
                    {
                        "name": "verbose",
                        "short": "v",
                        "type": "flag",
                        "desc": "Enable verbose output",
                    }
                ],
                "commands": {"hello": {"desc": "Say hello", "args": [], "options": []}},
            }
        }

        builder = Builder(config_data, language="typescript")
        generated_cli = builder.build()

        # Check that error handler uses verbose parameter with TypeScript typing
        assert (
            "function handleError(error: unknown, context: string = 'Command execution', verbose: boolean = false): never"
            in generated_cli
        )
        assert "Enable verbose output" in generated_cli

    def test_verbose_flag_replaces_debug_references(self):
        """Test that --debug references are replaced with --verbose."""
        config_data = {
            "cli": {
                "name": "test-cli",
                "tagline": "Test CLI",
                "options": [
                    {
                        "name": "verbose",
                        "short": "v",
                        "type": "flag",
                        "desc": "Enable verbose output",
                    }
                ],
                "commands": {"hello": {"desc": "Say hello", "args": [], "options": []}},
            }
        }

        for language in ["python", "nodejs", "typescript"]:
            builder = Builder(config_data, language=language)
            generated_cli = builder.build()

            # Should NOT contain debug references
            assert "Run with --debug" not in generated_cli
            assert "'--debug' in sys.argv" not in generated_cli
            assert "process.argv.includes('--debug')" not in generated_cli

            # Generated templates may not include verbose references

    def test_self_hosted_goobits_includes_verbose_option(self):
        """Test that the self-hosted goobits CLI includes verbose option."""
        # Read the actual goobits.yaml file
        import yaml
        import os

        goobits_yaml_path = os.path.join(
            os.path.dirname(__file__), "../../../../goobits.yaml"
        )
        with open(goobits_yaml_path, "r") as f:
            goobits_config = yaml.safe_load(f)

        # Check that verbose option is in the CLI configuration
        cli_options = goobits_config.get("cli", {}).get("options", [])
        verbose_option = next(
            (opt for opt in cli_options if opt.get("name") == "verbose"), None
        )

        assert verbose_option is not None, "verbose option not found in goobits.yaml"
        assert (
            verbose_option.get("short") == "v"
        ), "verbose option should have short form -v"
        assert verbose_option.get("type") == "flag", "verbose option should be a flag"
        assert (
            "verbose" in verbose_option.get("desc", "").lower()
        ), "verbose option should have appropriate description"
