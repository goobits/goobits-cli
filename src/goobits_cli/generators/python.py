"""Python CLI generator implementation."""



import json

import sys

from pathlib import Path

from typing import List, Optional, Union, Dict

from jinja2 import Environment, FileSystemLoader

import typer



from . import BaseGenerator

from ..schemas import ConfigSchema, GoobitsConfigSchema

from ..formatter import (

    align_examples, format_multiline_text, escape_for_docstring,

    align_setup_steps, format_icon_spacing, align_header_items

)

from ..shared.components.doc_generator import DocumentationGenerator



# Universal Template System imports

try:

    from ..universal.template_engine import UniversalTemplateEngine, LanguageRenderer

    from ..universal.renderers.python_renderer import PythonRenderer

    UNIVERSAL_TEMPLATES_AVAILABLE = True

except ImportError:

    UNIVERSAL_TEMPLATES_AVAILABLE = False

    UniversalTemplateEngine = None

    PythonRenderer = None





# Custom Exception Classes for Better Error Handling

class PythonGeneratorError(Exception):

    """Base exception for Python generator errors."""

    def __init__(self, message: str, error_code: int = 1, details: Optional[str] = None):

        self.message = message

        self.error_code = error_code

        self.details = details

        super().__init__(self.message)





class ConfigurationError(PythonGeneratorError):

    """Configuration validation or loading error."""

    def __init__(self, message: str, field: Optional[str] = None, suggestion: Optional[str] = None):

        self.field = field

        self.suggestion = suggestion

        error_code = 2  # Configuration errors

        super().__init__(message, error_code, f"Field: {field}" if field else None)





class TemplateError(PythonGeneratorError):

    """Template rendering or loading error."""

    def __init__(self, message: str, template_name: Optional[str] = None, line_number: Optional[int] = None):

        self.template_name = template_name

        self.line_number = line_number

        error_code = 3  # Template errors

        details = f"Template: {template_name}" if template_name else None

        if line_number:

            details += f", Line: {line_number}" if details else f"Line: {line_number}"

        super().__init__(message, error_code, details)





class DependencyError(PythonGeneratorError):

    """Missing or incompatible dependency error."""

    def __init__(self, message: str, dependency: str, install_command: Optional[str] = None):

        self.dependency = dependency

        self.install_command = install_command

        error_code = 4  # Dependency errors

        super().__init__(message, error_code, f"Dependency: {dependency}")





class ValidationError(PythonGeneratorError):

    """Input validation error."""

    def __init__(self, message: str, field: str, value: Optional[str] = None, valid_options: Optional[List[str]] = None):

        self.field = field

        self.value = value

        self.valid_options = valid_options

        error_code = 2  # Validation errors

        details = f"Field: {field}"

        if value:

            details += f", Value: {value}"

        if valid_options:

            details += f", Valid options: {', '.join(valid_options)}"

        super().__init__(message, error_code, details)





class PythonGenerator(BaseGenerator):

    """CLI code generator for Python using Typer framework."""

    

    def __init__(self, use_universal_templates: bool = False, consolidate: bool = False):

        """Initialize the Python generator with Jinja2 environment.

        

        Args:

            use_universal_templates: If True, use Universal Template System with single-file output
            
            consolidate: Automatically enabled when using universal templates (legacy parameter)

        """

        self.use_universal_templates = use_universal_templates and UNIVERSAL_TEMPLATES_AVAILABLE
        
        # Universal templates always use single-file output (consolidation)
        self.consolidate = use_universal_templates or consolidate

        

        # Initialize Universal Template System if requested

        if self.use_universal_templates:

            try:

                self.universal_engine = UniversalTemplateEngine()

                self.python_renderer = PythonRenderer()

                self.universal_engine.register_renderer("python", self.python_renderer)

            except Exception as e:

                typer.echo(f"⚠️  Failed to initialize Universal Template System: {e}", err=True)

                typer.echo("   Falling back to legacy template system", err=True)

                self.use_universal_templates = False

                self.universal_engine = None

                self.python_renderer = None

        

        # Set up Jinja2 environment for legacy mode

        template_dir = Path(__file__).parent.parent / "templates"

        

        if not template_dir.exists():

            raise DependencyError(

                f"Template directory not found: {template_dir}",

                dependency="goobits-cli templates",

                install_command="pip install --upgrade goobits-cli"

            )

        

        try:

            self.env = Environment(loader=FileSystemLoader(template_dir))

        except Exception as e:

            raise DependencyError(

                f"Failed to initialize Jinja2 environment: {str(e)}",

                dependency="jinja2",

                install_command="pip install jinja2"

            ) from e

        

        # Add custom filters

        try:

            self.env.filters['align_examples'] = align_examples

            self.env.filters['format_multiline'] = format_multiline_text

            self.env.filters['escape_docstring'] = escape_for_docstring

            self.env.filters['align_setup_steps'] = align_setup_steps

            self.env.filters['format_icon'] = format_icon_spacing

            self.env.filters['align_header_items'] = align_header_items

        except Exception as e:

            raise DependencyError(

                f"Failed to register template filters: {str(e)}",

                dependency="goobits-cli formatter"

            ) from e

        

        # Initialize generated files storage

        self._generated_files = {}

        

        # Initialize shared components

        self.doc_generator = None  # Will be initialized when config is available

    

    def generate(self, config: Union[ConfigSchema, GoobitsConfigSchema], 

                 config_filename: str, version: Optional[str] = None) -> str:

        """

        Generate Python CLI code from configuration.

        

        Args:

            config: The configuration object

            config_filename: Name of the configuration file

            version: Optional version string

            

        Returns:

            Generated Python CLI code

        """

        # Use Universal Template System if enabled

        if self.use_universal_templates:

            return self._generate_with_universal_templates(config, config_filename, version)

        

        # Fall back to legacy implementation

        return self._generate_legacy(config, config_filename, version)

    

    def _generate_with_universal_templates(self, config: Union[ConfigSchema, GoobitsConfigSchema], 

                                         config_filename: str, version: Optional[str] = None) -> str:

        """

        Generate using Universal Template System.

        

        Args:

            config: The configuration object

            config_filename: Name of the configuration file

            version: Optional version string

            

        Returns:

            Generated Python CLI code

        """

        try:

            # Ensure universal engine is available

            if not self.universal_engine:

                raise RuntimeError("Universal Template Engine not initialized")

            

            # Convert config to GoobitsConfigSchema if needed

            if isinstance(config, ConfigSchema):

                # Create minimal GoobitsConfigSchema for universal system

                goobits_config = GoobitsConfigSchema(

                    package_name=getattr(config, 'package_name', config.cli.name),

                    command_name=getattr(config, 'command_name', config.cli.name),

                    description=getattr(config, 'description', config.cli.description or config.cli.tagline),

                    cli=config,

                    installation=getattr(config, 'installation', None)

                )

            else:

                goobits_config = config

                

            # Generate using universal engine

            output_dir = Path(".")

            generated_files = self.universal_engine.generate_cli(

                goobits_config, "python", output_dir, consolidate=self.consolidate

            )

            

            # Store generated files for later access

            self._generated_files = {}

            for file_path, content in generated_files.items():

                # Extract relative filename for compatibility

                relative_path = Path(file_path).name

                self._generated_files[relative_path] = content

            

            # Return main CLI file for backward compatibility

            main_cli_file = next((content for path, content in generated_files.items() 

                                if "cli.py" in path), "")

            

            if not main_cli_file:

                # If no main CLI file found, use the first available content

                main_cli_file = next(iter(generated_files.values()), "")

                

            return main_cli_file

            

        except Exception as e:

            # Fall back to legacy mode if universal templates fail

            typer.echo(f"⚠️  Universal Templates failed ({type(e).__name__}: {e}), falling back to legacy mode", err=True)

            # Disable universal templates for subsequent calls to avoid repeated failures

            self.use_universal_templates = False

            return self._generate_legacy(config, config_filename, version)

    

    def _generate_legacy(self, config: Union[ConfigSchema, GoobitsConfigSchema], 

                        config_filename: str, version: Optional[str] = None) -> str:

        """

        Generate using legacy template system.

        

        Args:

            config: The configuration object

            config_filename: Name of the configuration file

            version: Optional version string

            

        Returns:

            Generated Python CLI code

        """

        # Extract metadata using base class helper

        metadata = self._extract_config_metadata(config)

        cli_config = metadata['cli_config']

        

        # Initialize DocumentationGenerator with config

        config_dict = config.model_dump() if hasattr(config, 'model_dump') else config.dict()

        self.doc_generator = DocumentationGenerator(language='python', config=config_dict)

        

        # Validate configuration before building - only validate CLI for GoobitsConfigSchema

        try:

            if hasattr(config, 'package_name'):  # GoobitsConfigSchema

                if not cli_config:

                    raise ConfigurationError(

                        "No CLI configuration found in the project configuration.",

                        field="cli",

                        suggestion="Add a 'cli' section to your goobits.yaml file with at least one command."

                    )

            else:  # ConfigSchema

                self._validate_config(config)

        except (ConfigurationError, ValidationError):

            raise  # Re-raise our custom exceptions

        except Exception as e:

            # Wrap unexpected errors

            raise ConfigurationError(

                f"Unexpected error during configuration validation: {str(e)}",

                suggestion="Check your configuration file syntax and structure."

            ) from e

        

        # Serialize the CLI part of the config to a JSON string

        # We need to escape backslashes and quotes for embedding in Python code

        try:

            cli_dict = cli_config.model_dump()

            cli_config_json = json.dumps(cli_dict, indent=2, ensure_ascii=False)

            # Escape backslashes so they're preserved when Python interprets the string

            cli_config_json = cli_config_json.replace("\\", "\\\\")

            # Also escape any potential triple quotes

            cli_config_json = cli_config_json.replace("'''", "\\'\\'\\'")

        except Exception as e:

            raise ConfigurationError(

                f"Failed to serialize CLI configuration to JSON: {str(e)}",

                suggestion="Check for circular references or non-serializable objects in your configuration."

            ) from e

        

        # Prepare common template variables

        template_vars = {

            'cli': cli_config,

            'file_name': config_filename,

            'cli_config_json': cli_config_json,

            'package_name': metadata['package_name'],

            'command_name': metadata['command_name'],

            'display_name': metadata['display_name'],

            'installation': metadata['installation'],

            'hooks_path': metadata['hooks_path'],

            'version': version

        }

        

        # Generate all templates

        generated_files = {}

        

        # Main CLI template

        try:

            template = self.env.get_template("cli_template.py.j2")

            generated_files['cli.py'] = template.render(**template_vars)

        except Exception as e:

            raise TemplateError(

                f"Failed to render main CLI template: {str(e)}",

                template_name="cli_template.py.j2"

            ) from e

        

        # Helper templates

        helper_templates = [

            "config_manager.py.j2",

            "progress_helper.py.j2", 

            "prompts_helper.py.j2",

            "completion_engine.py.j2",

            "completion_helper.py.j2",

            "enhanced_interactive_mode.py.j2"

        ]

        

        for template_name in helper_templates:

            try:

                helper_template = self.env.get_template(template_name)

                output_name = template_name.replace('.j2', '')

                generated_files[output_name] = helper_template.render(**template_vars)

            except Exception as e:

                # If helper template fails, provide better error information

                typer.echo(f"⚠️  Warning: Could not generate {template_name}", err=True)

                typer.echo(f"   Reason: {str(e)}", err=True)

                typer.echo(f"   Impact: The generated CLI will work but without {output_name} functionality", err=True)

                typer.echo(f"   Solution: Check template syntax or report this issue", err=True)

        

        # Store generated files for later retrieval

        self._generated_files = generated_files

        

        # For backward compatibility, return the main CLI code

        return generated_files['cli.py']

    

    def generate_all_files(self, config, config_filename: str, version: Optional[str] = None) -> Dict[str, str]:

        """

        Generate all files needed for the Python CLI.

        

        Args:

            config: The configuration object

            config_filename: Name of the configuration file

            version: Optional version string

            

        Returns:

            Dictionary mapping file paths to their contents

        """

        try:

            # Generate main file first to populate _generated_files

            self.generate(config, config_filename, version)

            

            # For universal templates, files are already generated during generate() call

            if self.use_universal_templates and self._generated_files:

                return self._generated_files.copy()  # Return a copy to prevent external modification

            

            # For legacy mode, return the stored files

            return self._generated_files.copy() if self._generated_files else {}

        except Exception as e:

            # Wrap and re-raise any errors

            raise TemplateError(

                f"Failed to generate all files: {str(e)}"

            ) from e

    

    def get_output_files(self) -> List[str]:

        """Return list of files this generator creates."""

        return [

            "cli.py",

            "config_manager.py", 

            "progress_helper.py",

            "prompts_helper.py",

            "completion_engine.py",

            "completion_helper.py",

            "enhanced_interactive_mode.py"

        ]

    

    def get_default_output_path(self, package_name: str) -> str:

        """Get the default output path for Python CLI."""

        return "src/{package_name}/cli.py"

    

    def get_generated_files(self) -> dict:

        """Get all generated files from the last generate() call."""

        return getattr(self, '_generated_files', {})

    

    def _validate_config(self, config: ConfigSchema) -> None:

        """Validate configuration and provide helpful error messages."""

        cli = config.cli

        defined_commands = set(cli.commands.keys())

        

        # Validate command groups reference existing commands

        if cli.command_groups:

            for group in cli.command_groups:

                invalid_commands = set(group.commands) - defined_commands

                if invalid_commands:

                    raise ValidationError(

                        f"Command group '{group.name}' references non-existent commands: {', '.join(sorted(invalid_commands))}",

                        field=f"command_groups.{group.name}.commands",

                        value=str(list(invalid_commands)),

                        valid_options=list(defined_commands)

                    )

        

        # Validate command structure

        for cmd_name, cmd_data in cli.commands.items():

            if not cmd_data.desc:

                raise ValidationError(

                    f"Command '{cmd_name}' is missing required description",

                    field=f"commands.{cmd_name}.desc",

                    value="empty"

                )

            

            # Validate arguments

            if cmd_data.args:

                for arg in cmd_data.args:

                    if not arg.desc:

                        raise ValidationError(

                            f"Argument '{arg.name}' in command '{cmd_name}' is missing required description",

                            field=f"commands.{cmd_name}.args.{arg.name}.desc",

                            value="empty"

                        )

            

            # Validate options

            if cmd_data.options:

                valid_types = ['str', 'int', 'float', 'bool', 'flag']

                for opt in cmd_data.options:

                    if not opt.desc:

                        raise ValidationError(

                            f"Option '{opt.name}' in command '{cmd_name}' is missing required description",

                            field=f"commands.{cmd_name}.options.{opt.name}.desc",

                            value="empty"

                        )

                    if opt.type not in valid_types:

                        raise ValidationError(

                            f"Option '{opt.name}' in command '{cmd_name}' has invalid type '{opt.type}'",

                            field=f"commands.{cmd_name}.options.{opt.name}.type",

                            value=opt.type,

                            valid_options=valid_types

                        )