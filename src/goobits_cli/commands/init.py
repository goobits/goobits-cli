"""Init command handler for goobits CLI."""

from pathlib import Path
from typing import Optional

import typer

from .utils import _lazy_imports


def generate_basic_template(project_name: str) -> str:
    """Generate basic CLI template."""
    return f"""# Basic Goobits CLI Configuration

package_name: {project_name}

command_name: {project_name.replace("-", "_")}

display_name: "{project_name.replace("-", " ").title()}"

description: "A CLI tool built with Goobits"

# Language selection (python, nodejs, typescript, or rust)

language: python

# CLI generation configuration
cli_path: "src/{project_name.replace("-", "_")}/cli.py"
cli_hooks: "cli_hooks.py"

python:

  minimum_version: "3.8"

dependencies:

  required:

    - pipx

cli:

  name: {project_name.replace("-", "_")}

  tagline: "Your awesome CLI tool"

  commands:

    hello:

      desc: "Say hello"

      is_default: true

      args:

        - name: name

          desc: "Name to greet"

          required: false

      options:

        - name: greeting

          short: g

          desc: "Custom greeting"

          default: "Hello"

"""


def generate_advanced_template(project_name: str) -> str:
    """Generate advanced CLI template."""
    return f"""# Advanced Goobits CLI Configuration

package_name: {project_name}

command_name: {project_name.replace("-", "_")}

display_name: "{project_name.replace("-", " ").title()}"

description: "An advanced CLI tool built with Goobits"

# Language selection (python, nodejs, typescript, or rust)

language: python

# CLI generation configuration
cli_path: "src/{project_name.replace("-", "_")}/cli.py"
cli_hooks: "cli_hooks.py"

python:

  minimum_version: "3.8"

dependencies:

  required:

    - pipx

    - git

  optional:

    - curl

cli:

  name: {project_name.replace("-", "_")}

  tagline: "Advanced CLI with multiple commands"

  command_groups:

    - name: "Core Commands"

      commands: ["process", "convert"]

    - name: "Utilities"

      commands: ["status", "config"]

  commands:

    process:

      desc: "Process input data"

      is_default: true

      args:

        - name: input

          desc: "Input to process"

          nargs: "*"

      options:

        - name: output

          short: o

          desc: "Output file"

        - name: format

          short: f

          choices: ["json", "yaml", "text"]

          default: "text"

    convert:

      desc: "Convert between formats"

      args:

        - name: source

          desc: "Source file"

          required: true

      options:

        - name: target

          short: t

          desc: "Target format"

          required: true

    status:

      desc: "Show system status"

    config:

      desc: "Manage configuration"

      subcommands:

        show:

          desc: "Show current configuration"

        set:

          desc: "Set configuration value"

          args:

            - name: key

              desc: "Configuration key"

            - name: value

              desc: "Configuration value"

"""


def generate_api_client_template(project_name: str) -> str:
    """Generate API client CLI template."""
    return f"""# API Client Goobits CLI Configuration

package_name: {project_name}

command_name: {project_name.replace("-", "_")}

display_name: "{project_name.replace("-", " ").title()}"

description: "API client CLI tool built with Goobits"

# Language selection (python, nodejs, typescript, or rust)

language: python

# CLI generation configuration
cli_path: "src/{project_name.replace("-", "_")}/cli.py"
cli_hooks: "cli_hooks.py"

python:

  minimum_version: "3.8"

dependencies:

  required:

    - pipx

    - curl

  optional:

    - jq

cli:

  name: {project_name.replace("-", "_")}

  tagline: "API client for your service"

  commands:

    get:

      desc: "GET request to API endpoint"

      is_default: true

      args:

        - name: endpoint

          desc: "API endpoint path"

          required: true

      options:

        - name: api-key

          desc: "API key for authentication"

        - name: format

          short: f

          choices: ["json", "yaml", "table"]

          default: "json"

        - name: output

          short: o

          desc: "Save output to file"

    post:

      desc: "POST request to API endpoint"

      args:

        - name: endpoint

          desc: "API endpoint path"

          required: true

      options:

        - name: data

          short: d

          desc: "JSON data to send"

        - name: file

          desc: "Read data from file"

        - name: api-key

          desc: "API key for authentication"

    config:

      desc: "Manage API configuration"

      subcommands:

        set-key:

          desc: "Set API key"

          args:

            - name: key

              desc: "API key value"

        show:

          desc: "Show current configuration"

"""


def generate_text_processor_template(project_name: str) -> str:
    """Generate text processor CLI template."""
    return f"""# Text Processor Goobits CLI Configuration

package_name: {project_name}

command_name: {project_name.replace("-", "_")}

display_name: "{project_name.replace("-", " ").title()}"

description: "Text processing CLI tool built with Goobits"

# Language selection (python, nodejs, typescript, or rust)

language: python

# CLI generation configuration
cli_path: "src/{project_name.replace("-", "_")}/cli.py"
cli_hooks: "cli_hooks.py"

python:

  minimum_version: "3.8"

dependencies:

  required:

    - pipx

  optional:

    - pandoc

cli:

  name: {project_name.replace("-", "_")}

  tagline: "Process text files with ease"

  commands:

    process:

      desc: "Process text input"

      is_default: true

      args:

        - name: text

          desc: "Text to process (or read from stdin)"

          nargs: "*"

      options:

        - name: uppercase

          short: u

          type: flag

          desc: "Convert to uppercase"

        - name: lowercase

          short: l

          type: flag

          desc: "Convert to lowercase"

        - name: output

          short: o

          desc: "Output file"

        - name: format

          short: f

          choices: ["text", "json", "markdown"]

          default: "text"

    count:

      desc: "Count words, lines, characters"

      args:

        - name: files

          desc: "Files to count"

          nargs: "*"

      options:

        - name: words

          short: w

          type: flag

          desc: "Count words"

        - name: lines

          short: l

          type: flag

          desc: "Count lines"

        - name: chars

          short: c

          type: flag

          desc: "Count characters"

"""


def init_command(
    project_name: Optional[str] = typer.Argument(
        None, help="Name of the project (optional)"
    ),
    template: str = typer.Option(
        "basic",
        "--template",
        "-t",
        help="Template type (basic, advanced, api-client, text-processor)",
    ),
    force: bool = typer.Option(
        False, "--force", help="Overwrite existing goobits.yaml file"
    ),
):
    """
    Create initial goobits.yaml template.

    This command generates a starter goobits.yaml configuration file
    to help you get started with building your CLI application.

    Templates:
        basic: Simple CLI with one command
        advanced: Multi-command CLI with options and subcommands
        api-client: Template for API client tools
        text-processor: Template for text processing utilities

    Examples:
        goobits init my-awesome-tool
        goobits init --template advanced
        goobits init my-api-client --template api-client
    """
    _lazy_imports()

    config_path = Path("./goobits.yaml")

    if config_path.exists() and not force:
        typer.echo(
            f"Error: {config_path} already exists. Use --force to overwrite.", err=True
        )

        raise typer.Exit(1)

    # Determine project name

    if not project_name:
        project_name = Path.cwd().name

    # Generate template based on type

    templates = {
        "basic": generate_basic_template(project_name),
        "advanced": generate_advanced_template(project_name),
        "api-client": generate_api_client_template(project_name),
        "text-processor": generate_text_processor_template(project_name),
    }

    if template not in templates:
        typer.echo(
            f"Error: Unknown template '{template}'. Available: {', '.join(templates.keys())}",
            err=True,
        )

        raise typer.Exit(1)

    # Write template

    with open(config_path, "w") as f:
        f.write(templates[template])

    typer.echo(f"\u2705 Created {config_path} using '{template}' template")

    typer.echo(f"\U0001f4dd Project: {project_name}")

    typer.echo("")

    typer.echo("Next steps:")

    typer.echo("  1. Edit goobits.yaml to customize your CLI")

    typer.echo("  2. Run: goobits build")

    typer.echo("  3. Run: ./setup.sh install --dev")
