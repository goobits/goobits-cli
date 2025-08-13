"""

Template Migration Tool for Universal Template System



This module provides tools to migrate existing language-specific templates

to the Universal Template System format.

"""



import re

import shutil

from pathlib import Path

from typing import Dict, List, Optional, Tuple, Set

import typer

import jinja2

from jinja2.exceptions import TemplateError





class TemplateMigrator:

    """

    Converts existing language-specific templates to universal format.

    

    This class analyzes existing templates and attempts to create

    universal templates that can work across multiple languages.

    """

    

    def __init__(self, templates_dir: Path):

        """

        Initialize the migrator.

        

        Args:

            templates_dir: Path to existing templates directory

        """

        self.templates_dir = templates_dir

        self.universal_dir = templates_dir.parent / "universal" / "components"

        self.migration_report = []

        

        # Language-specific template mappings

        self.language_mappings = {

            "python": {

                "cli_template.py.j2": "command_handler.j2",

                "config_manager.py.j2": "config_manager.j2",

                "completion_engine.py.j2": "completion_engine.j2",

                "progress_helper.py.j2": None,  # Language-specific

                "prompts_helper.py.j2": None,   # Language-specific

            },

            "nodejs": {

                "index.js.j2": "command_handler.j2",

                "completion_engine.js.j2": "completion_engine.j2",

                "package.json.j2": None,  # Language-specific

            },

            "typescript": {

                "index.ts.j2": "command_handler.j2", 

                "completion_engine.ts.j2": "completion_engine.j2",

                "tsconfig.json.j2": None,  # Language-specific

            },

            "rust": {

                "main.rs.j2": "command_handler.j2",

                "lib.rs.j2": "command_handler.j2",

                "Cargo.toml.j2": None,  # Language-specific

            }

        }

    

    def analyze_templates(self) -> Dict[str, any]:

        """

        Analyze existing templates to identify common patterns.

        

        Returns:

            Analysis report with common patterns and differences

        """

        analysis = {

            "languages": [],

            "common_components": set(),

            "language_specific": {},

            "patterns": {},

            "compatibility": {}

        }

        

        # Find all language directories

        for lang_dir in self.templates_dir.glob("*"):

            if lang_dir.is_dir() and lang_dir.name in self.language_mappings:

                language = lang_dir.name

                analysis["languages"].append(language)

                analysis["language_specific"][language] = []

                

                # Analyze templates in this language

                for template_file in lang_dir.glob("*.j2"):

                    template_name = template_file.name

                    

                    # Check if this maps to a universal component

                    mapping = self.language_mappings[language].get(template_name)

                    if mapping:

                        analysis["common_components"].add(mapping)

                    else:

                        analysis["language_specific"][language].append(template_name)

                    

                    # Analyze template content for patterns

                    try:

                        content = template_file.read_text(encoding='utf-8')

                        patterns = self._extract_patterns(content, language)

                        

                        if template_name not in analysis["patterns"]:

                            analysis["patterns"][template_name] = {}

                        analysis["patterns"][template_name][language] = patterns

                        

                    except Exception as e:

                        self.migration_report.append(

                            f"Warning: Could not analyze {template_file}: {e}"

                        )

        

        return analysis

    

    def _extract_patterns(self, content: str, language: str) -> Dict[str, any]:

        """

        Extract common patterns from template content.

        

        Args:

            content: Template content

            language: Programming language

            

        Returns:

            Dictionary of extracted patterns

        """

        patterns = {

            "variables": set(),

            "filters": set(),

            "blocks": set(),

            "imports": [],

            "functions": [],

            "language_specific": []

        }

        

        # Extract Jinja2 variables

        var_pattern = r'\{\{\s*([^}]+)\s*\}\}'

        variables = re.findall(var_pattern, content)

        for var in variables:

            # Clean up variable (remove filters, etc.)

            clean_var = var.split('|')[0].strip()

            patterns["variables"].add(clean_var)

        

        # Extract filters

        filter_pattern = r'\|\s*(\w+)'

        filters = re.findall(filter_pattern, content)

        patterns["filters"].update(filters)

        

        # Extract blocks

        block_pattern = r'\{%\s*block\s+(\w+)\s*%\}'

        blocks = re.findall(block_pattern, content)

        patterns["blocks"].update(blocks)

        

        # Language-specific patterns

        if language == "python":

            # Extract imports

            import_pattern = r'^import\s+(\S+)|^from\s+(\S+)\s+import'

            imports = re.findall(import_pattern, content, re.MULTILINE)

            patterns["imports"] = [imp[0] or imp[1] for imp in imports]

            

            # Extract function definitions

            func_pattern = r'^def\s+(\w+)'

            functions = re.findall(func_pattern, content, re.MULTILINE)

            patterns["functions"] = functions

            

        elif language in ["nodejs", "typescript"]:

            # Extract require/import statements

            require_pattern = r'require\([\'"]([^\'"]+)[\'"]\)|import.*from\s+[\'"]([^\'"]+)[\'"]'

            imports = re.findall(require_pattern, content)

            patterns["imports"] = [imp[0] or imp[1] for imp in imports]

            

            # Extract function definitions

            func_pattern = r'function\s+(\w+)|const\s+(\w+)\s*='

            functions = re.findall(func_pattern, content)

            patterns["functions"] = [func[0] or func[1] for func in functions]

            

        elif language == "rust":

            # Extract use statements

            use_pattern = r'^use\s+([^;]+);'

            imports = re.findall(use_pattern, content, re.MULTILINE)

            patterns["imports"] = imports

            

            # Extract function definitions

            func_pattern = r'fn\s+(\w+)'

            functions = re.findall(func_pattern, content)

            patterns["functions"] = functions

        

        return patterns

    

    def create_universal_template(self, component_name: str, 

                                 language_templates: Dict[str, Path]) -> Optional[str]:

        """

        Create a universal template from language-specific templates.

        

        Args:

            component_name: Name of the universal component

            language_templates: Mapping of language to template file path

            

        Returns:

            Universal template content or None if creation fails

        """

        if not language_templates:

            return None

            

        # Analyze all language templates to find commonalities

        common_patterns = {}

        all_variables = set()

        all_blocks = set()

        

        for language, template_path in language_templates.items():

            try:

                content = template_path.read_text(encoding='utf-8')

                patterns = self._extract_patterns(content, language)

                common_patterns[language] = patterns

                all_variables.update(patterns["variables"])

                all_blocks.update(patterns["blocks"])

            except Exception as e:

                self.migration_report.append(

                    f"Warning: Could not read {template_path}: {e}"

                )

                continue

        

        # Create universal template structure

        universal_content = self._generate_universal_template(

            component_name, common_patterns, all_variables, all_blocks

        )

        

        return universal_content

    

    def _generate_universal_template(self, component_name: str,

                                   patterns: Dict[str, Dict],

                                   variables: Set[str],

                                   blocks: Set[str]) -> str:

        """

        Generate universal template content.

        

        Args:

            component_name: Name of the component

            patterns: Extracted patterns from language templates

            variables: All variables found

            blocks: All blocks found

            

        Returns:

            Universal template content

        """

        template_lines = [

            f"{{# Universal Template: {component_name} #}}",

            "",

            "{% set lang = language | default('python') %}",

            ""

        ]

        

        # Add language-specific sections

        if "command_handler" in component_name:

            template_lines.extend([

                "{% if lang == 'python' %}",

                "{% include 'python/command_handler_impl.j2' %}",

                "{% elif lang == 'nodejs' %}",

                "{% include 'nodejs/command_handler_impl.j2' %}",

                "{% elif lang == 'typescript' %}",

                "{% include 'typescript/command_handler_impl.j2' %}",

                "{% elif lang == 'rust' %}",

                "{% include 'rust/command_handler_impl.j2' %}",

                "{% endif %}"

            ])

        else:

            # Generic component structure

            template_lines.extend([

                "{% block header %}",

                "  {# Language-specific header #}",

                "  {% if lang == 'python' %}",

                "    {# Python header #}",

                "  {% elif lang in ['nodejs', 'typescript'] %}",

                "    {# JavaScript/TypeScript header #}",

                "  {% elif lang == 'rust' %}",

                "    {# Rust header #}",

                "  {% endif %}",

                "{% endblock %}",

                "",

                "{% block main_content %}",

                "  {# Main component logic #}",

                "  {% for command in cli.commands %}",

                "    {# Process commands #}",

                "  {% endfor %}",

                "{% endblock %}",

                "",

                "{% block footer %}",

                "  {# Language-specific footer #}",

                "{% endblock %}"

            ])

        

        return "\n".join(template_lines)

    

    def migrate_all_templates(self, dry_run: bool = False) -> bool:

        """

        Migrate all eligible templates to universal format.

        

        Args:

            dry_run: If True, don't write files, just report what would be done

            

        Returns:

            True if migration successful, False otherwise

        """

        try:

            # Analyze existing templates

            analysis = self.analyze_templates()

            

            self.migration_report.append(f"Found {len(analysis['languages'])} languages")

            self.migration_report.append(f"Identified {len(analysis['common_components'])} common components")

            

            if not dry_run:

                # Ensure universal components directory exists

                self.universal_dir.mkdir(parents=True, exist_ok=True)

            

            # Migrate common components

            for component_name in analysis["common_components"]:

                # Find all language templates for this component

                language_templates = {}

                

                for language in analysis["languages"]:

                    lang_dir = self.templates_dir / language

                    

                    # Find template that maps to this component

                    for template_name, mapped_component in self.language_mappings[language].items():

                        if mapped_component == component_name:

                            template_path = lang_dir / template_name

                            if template_path.exists():

                                language_templates[language] = template_path

                

                if language_templates:

                    # Create universal template

                    universal_content = self.create_universal_template(

                        component_name, language_templates

                    )

                    

                    if universal_content and not dry_run:

                        universal_path = self.universal_dir / component_name

                        universal_path.write_text(universal_content, encoding='utf-8')

                        self.migration_report.append(f"Created universal template: {universal_path}")

                    elif dry_run:

                        self.migration_report.append(f"Would create: {component_name}")

            

            return True

            

        except Exception as e:

            self.migration_report.append(f"Migration failed: {e}")

            return False

    

    def generate_migration_report(self) -> str:

        """

        Generate a comprehensive migration report.

        

        Returns:

            Migration report as formatted string

        """

        report_lines = [

            "# Template Migration Report",

            "",

            "## Migration Summary",

        ]

        

        report_lines.extend(self.migration_report)

        

        return "\n".join(report_lines)





def migrate_templates_command(

    templates_dir: Path = typer.Argument(

        ..., 

        help="Path to templates directory"

    ),

    dry_run: bool = typer.Option(

        False,

        "--dry-run",

        help="Show what would be migrated without making changes"

    ),

    output_report: Optional[Path] = typer.Option(

        None,

        "--report",

        help="Save migration report to file"

    )

):

    """

    Migrate existing templates to Universal Template System format.

    

    This command analyzes existing language-specific templates and creates

    universal templates that can work across multiple programming languages.

    """

    typer.echo(f"Starting template migration from: {templates_dir}")

    

    if dry_run:

        typer.echo("🔍 Dry run mode - no files will be modified")

    

    # Initialize migrator

    migrator = TemplateMigrator(templates_dir)

    

    # Run migration

    success = migrator.migrate_all_templates(dry_run=dry_run)

    

    # Generate report

    report = migrator.generate_migration_report()

    

    if output_report:

        output_report.write_text(report, encoding='utf-8')

        typer.echo(f"📄 Migration report saved to: {output_report}")

    else:

        typer.echo(report)

    

    if success:

        typer.echo("✅ Migration completed successfully")

        return 0

    else:

        typer.echo("❌ Migration failed")

        return 1





if __name__ == "__main__":

    typer.run(migrate_templates_command)