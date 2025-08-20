"""

Template Analysis Tool for Universal Template System



This module provides tools to analyze template differences and commonalities

across different programming languages in the Goobits CLI framework.

"""



import json

import difflib

from pathlib import Path

from typing import Dict, List, Tuple, Set, Optional, Any

from dataclasses import dataclass, asdict

import typer

import jinja2

from jinja2 import meta





@dataclass

class TemplateAnalysis:

    """Analysis results for a single template."""

    name: str

    language: str

    variables: Set[str]

    filters: Set[str]

    blocks: Set[str]

    macros: Set[str]

    includes: Set[str]

    extends: Optional[str]

    line_count: int

    complexity_score: float

    dependencies: Set[str]





@dataclass

class ComparisonResult:

    """Results of comparing templates across languages."""

    common_variables: Set[str]

    unique_variables: Dict[str, Set[str]]

    common_filters: Set[str]

    unique_filters: Dict[str, Set[str]]

    common_blocks: Set[str]

    unique_blocks: Dict[str, Set[str]]

    similarity_score: float

    recommendations: List[str]





class TemplateAnalyzer:

    """

    Analyzes templates to identify patterns, differences, and opportunities

    for universal template creation.

    """

    

    def __init__(self, templates_dir: Path):

        """

        Initialize the analyzer.

        

        Args:

            templates_dir: Path to templates directory containing language subdirs

        """

        self.templates_dir = templates_dir

        self.analyses: Dict[str, TemplateAnalysis] = {}

    def _get_template_name(self, template) -> str:
        """Get template name for sorting."""
        return template.name

        

        # Language-specific patterns

        self.language_patterns = {

            "python": {

                "import_patterns": [r"^import\s+", r"^from\s+.*\s+import"],

                "function_patterns": [r"def\s+\w+\(", r"class\s+\w+"],

                "comment_patterns": [r"#.*$", r'""".*?"""'],

                "extensions": [".py"],

            },

            "nodejs": {

                "import_patterns": [r"require\(", r"import.*from"],

                "function_patterns": [r"function\s+\w+", r"const\s+\w+\s*=", r"=>\s*{"],

                "comment_patterns": [r"//.*$", r"/\*.*?\*/"],

                "extensions": [".js"],

            },

            "typescript": {

                "import_patterns": [r"import.*from", r"import\s*{"],

                "function_patterns": [r"function\s+\w+", r"const\s+\w+\s*:", r"=>\s*{"],

                "comment_patterns": [r"//.*$", r"/\*.*?\*/"],

                "extensions": [".ts"],

            },

            "rust": {

                "import_patterns": [r"^use\s+", r"extern\s+crate"],

                "function_patterns": [r"fn\s+\w+", r"impl\s+", r"struct\s+"],

                "comment_patterns": [r"//.*$", r"/\*.*?\*/"],

                "extensions": [".rs"],

            }

        }

    

    def analyze_template(self, template_path: Path, language: str) -> TemplateAnalysis:

        """

        Analyze a single template file.

        

        Args:

            template_path: Path to the template file

            language: Programming language of the template

            

        Returns:

            TemplateAnalysis object with extracted information

        """

        try:

            content = template_path.read_text(encoding='utf-8')

        except Exception as e:

            typer.echo(f"Warning: Could not read {template_path}: {e}", err=True)

            return TemplateAnalysis(

                name=template_path.name,

                language=language,

                variables=set(),

                filters=set(),

                blocks=set(),

                macros=set(),

                includes=set(),

                extends=None,

                line_count=0,

                complexity_score=0.0,

                dependencies=set()

            )

        

        # Parse template using Jinja2

        env = jinja2.Environment()

        try:

            ast = env.parse(content)

            variables = meta.find_undeclared_variables(ast)

            referenced_templates = meta.find_referenced_templates(ast)

        except Exception as e:

            typer.echo(f"Warning: Could not parse template {template_path}: {e}", err=True)

            variables = set()

            referenced_templates = set()

        

        # Extract template elements

        analysis = TemplateAnalysis(

            name=template_path.name,

            language=language,

            variables=variables,

            filters=self._extract_filters(content),

            blocks=self._extract_blocks(content),

            macros=self._extract_macros(content),

            includes=self._extract_includes(content),

            extends=self._extract_extends(content),

            line_count=len(content.split('\n')),

            complexity_score=self._calculate_complexity(content, language),

            dependencies=referenced_templates

        )

        

        return analysis

    

    def _extract_filters(self, content: str) -> Set[str]:

        """Extract Jinja2 filters from template content."""

        import re

        filter_pattern = r'\|\s*(\w+)'

        filters = re.findall(filter_pattern, content)

        return set(filters)

    

    def _extract_blocks(self, content: str) -> Set[str]:

        """Extract Jinja2 blocks from template content."""

        import re

        block_pattern = r'\{%\s*block\s+(\w+)\s*%\}'

        blocks = re.findall(block_pattern, content)

        return set(blocks)

    

    def _extract_macros(self, content: str) -> Set[str]:

        """Extract Jinja2 macros from template content."""

        import re

        macro_pattern = r'\{%\s*macro\s+(\w+)'

        macros = re.findall(macro_pattern, content)

        return set(macros)

    

    def _extract_includes(self, content: str) -> Set[str]:

        """Extract Jinja2 includes from template content."""

        import re

        include_pattern = r'\{%\s*include\s+[\'"]([^\'"]+)[\'"]'

        includes = re.findall(include_pattern, content)

        return set(includes)

    

    def _extract_extends(self, content: str) -> Optional[str]:

        """Extract Jinja2 extends from template content."""

        import re

        extends_pattern = r'\{%\s*extends\s+[\'"]([^\'"]+)[\'"]'

        extends = re.search(extends_pattern, content)

        return extends.group(1) if extends else None

    

    def _calculate_complexity(self, content: str, language: str) -> float:

        """

        Calculate a complexity score for the template.

        

        Args:

            content: Template content

            language: Programming language

            

        Returns:

            Complexity score (higher = more complex)

        """

        score = 0.0

        

        # Base complexity from length

        lines = content.split('\n')

        score += len(lines) * 0.1

        

        # Jinja2 constructs add complexity

        import re

        

        # Control structures

        control_patterns = [

            r'\{%\s*for\s+',

            r'\{%\s*if\s+',

            r'\{%\s*elif\s+',

            r'\{%\s*else\s*%\}',

            r'\{%\s*endif\s*%\}',

            r'\{%\s*endfor\s*%\}',

        ]

        

        for pattern in control_patterns:

            matches = len(re.findall(pattern, content))

            score += matches * 2.0

        

        # Variable usage

        var_pattern = r'\{\{\s*[^}]+\s*\}\}'

        variables = len(re.findall(var_pattern, content))

        score += variables * 0.5

        

        # Filters add complexity

        filter_pattern = r'\|\s*\w+'

        filters = len(re.findall(filter_pattern, content))

        score += filters * 1.0

        

        # Language-specific complexity

        if language in self.language_patterns:

            patterns = self.language_patterns[language]

            

            for pattern_group in patterns.values():

                if isinstance(pattern_group, list):

                    for pattern in pattern_group:

                        matches = len(re.findall(pattern, content, re.MULTILINE))

                        score += matches * 0.3

        

        return round(score, 2)

    

    def analyze_all_templates(self) -> Dict[str, Dict[str, TemplateAnalysis]]:

        """

        Analyze all templates in the templates directory.

        

        Returns:

            Nested dict: {language: {template_name: analysis}}

        """

        results = {}

        

        # Find all language directories

        for lang_dir in self.templates_dir.iterdir():

            if lang_dir.is_dir() and lang_dir.name in self.language_patterns:

                language = lang_dir.name

                results[language] = {}

                

                # Analyze all templates in this language

                for template_file in lang_dir.glob("*.j2"):

                    analysis = self.analyze_template(template_file, language)

                    results[language][template_file.name] = analysis

                    

                    # Store for global access

                    key = f"{language}:{template_file.name}"

                    self.analyses[key] = analysis

        

        return results

    

    def compare_templates_across_languages(self, template_base_name: str) -> ComparisonResult:

        """

        Compare templates with the same base name across different languages.

        

        Args:

            template_base_name: Base name of template (e.g., "cli_template")

            

        Returns:

            ComparisonResult with comparison details

        """

        # Find matching templates across languages

        matching_templates = {}

        

        for key, analysis in self.analyses.items():

            language, template_name = key.split(':', 1)

            

            # Check if this template matches the base name

            if template_base_name in template_name.lower():

                matching_templates[language] = analysis

        

        if len(matching_templates) < 2:

            return ComparisonResult(

                common_variables=set(),

                unique_variables={},

                common_filters=set(),

                unique_filters={},

                common_blocks=set(),

                unique_blocks={},

                similarity_score=0.0,

                recommendations=["Not enough templates found for comparison"]

            )

        

        # Extract sets for comparison

        all_variables = [template.variables for template in matching_templates.values()]

        all_filters = [template.filters for template in matching_templates.values()]

        all_blocks = [template.blocks for template in matching_templates.values()]

        

        # Find commonalities and differences

        common_variables = set.intersection(*all_variables) if all_variables else set()

        common_filters = set.intersection(*all_filters) if all_filters else set()

        common_blocks = set.intersection(*all_blocks) if all_blocks else set()

        

        unique_variables = {}

        unique_filters = {}

        unique_blocks = {}

        

        for language, template in matching_templates.items():

            unique_variables[language] = template.variables - common_variables

            unique_filters[language] = template.filters - common_filters

            unique_blocks[language] = template.blocks - common_blocks

        

        # Calculate similarity score

        similarity_score = self._calculate_similarity_score(matching_templates)

        

        # Generate recommendations

        recommendations = self._generate_recommendations(

            matching_templates, common_variables, common_filters, common_blocks

        )

        

        return ComparisonResult(

            common_variables=common_variables,

            unique_variables=unique_variables,

            common_filters=common_filters,

            unique_filters=unique_filters,

            common_blocks=common_blocks,

            unique_blocks=unique_blocks,

            similarity_score=similarity_score,

            recommendations=recommendations

        )

    

    def _calculate_similarity_score(self, templates: Dict[str, TemplateAnalysis]) -> float:

        """

        Calculate a similarity score between templates.

        

        Args:

            templates: Dictionary of language to template analysis

            

        Returns:

            Similarity score between 0.0 and 1.0

        """

        if len(templates) < 2:

            return 0.0

        

        # Calculate based on common vs unique elements

        template_list = list(templates.values())

        total_score = 0.0

        comparisons = 0

        

        for i in range(len(template_list)):

            for j in range(i + 1, len(template_list)):

                t1, t2 = template_list[i], template_list[j]

                

                # Compare variables

                common_vars = len(t1.variables.intersection(t2.variables))

                total_vars = len(t1.variables.union(t2.variables))

                var_similarity = common_vars / total_vars if total_vars > 0 else 1.0

                

                # Compare filters

                common_filters = len(t1.filters.intersection(t2.filters))

                total_filters = len(t1.filters.union(t2.filters))

                filter_similarity = common_filters / total_filters if total_filters > 0 else 1.0

                

                # Compare blocks

                common_blocks = len(t1.blocks.intersection(t2.blocks))

                total_blocks = len(t1.blocks.union(t2.blocks))

                block_similarity = common_blocks / total_blocks if total_blocks > 0 else 1.0

                

                # Weighted average

                similarity = (var_similarity * 0.5 + filter_similarity * 0.3 + block_similarity * 0.2)

                total_score += similarity

                comparisons += 1

        

        return round(total_score / comparisons, 3) if comparisons > 0 else 0.0

    

    def _generate_recommendations(self, templates: Dict[str, TemplateAnalysis],

                                common_vars: Set[str], common_filters: Set[str],

                                common_blocks: Set[str]) -> List[str]:

        """Generate recommendations for template unification."""

        recommendations = []

        

        # Check if templates are similar enough for unification

        if len(common_vars) >= 5:

            recommendations.append(

                f"High variable overlap ({len(common_vars)} common variables) - good candidate for universal template"

            )

        

        if len(common_blocks) >= 2:

            recommendations.append(

                f"Common block structure ({len(common_blocks)} shared blocks) supports universal template"

            )

        

        # Check complexity differences

        complexities = [t.complexity_score for t in templates.values()]

        if max(complexities) - min(complexities) > 20:

            recommendations.append(

                "Large complexity differences - consider separate implementation paths"

            )

        

        # Check for language-specific patterns

        unique_patterns = {}

        for lang, template in templates.items():

            unique_count = len(template.variables) - len(common_vars)

            if unique_count > 5:

                unique_patterns[lang] = unique_count

        

        if unique_patterns:

            recommendations.append(

                f"Languages with many unique patterns: {', '.join(unique_patterns.keys())}"

            )

        

        return recommendations

    

    def generate_analysis_report(self, output_format: str = "text") -> str:

        """

        Generate a comprehensive analysis report.

        

        Args:

            output_format: Format for the report ("text", "json", "markdown")

            

        Returns:

            Formatted analysis report

        """

        if not self.analyses:

            return "No templates analyzed yet. Run analyze_all_templates() first."

        

        if output_format == "json":

            return self._generate_json_report()

        elif output_format == "markdown":

            return self._generate_markdown_report()

        else:

            return self._generate_text_report()

    

    def _generate_text_report(self) -> str:

        """Generate a text format report."""

        lines = [

            "# Template Analysis Report",

            "=" * 50,

            ""

        ]

        

        # Summary statistics

        languages = set(key.split(':', 1)[0] for key in self.analyses.keys())

        total_templates = len(self.analyses)

        

        lines.extend([

            f"Languages analyzed: {len(languages)} ({', '.join(sorted(languages))})",

            f"Total templates: {total_templates}",

            ""

        ])

        

        # Per-language breakdown

        for language in sorted(languages):

            lang_templates = [a for k, a in self.analyses.items() if k.startswith(f"{language}:")]

            

            lines.extend([

                f"## {language.capitalize()} Templates",

                f"Count: {len(lang_templates)}",

            ])

            

            if lang_templates:

                avg_complexity = sum(t.complexity_score for t in lang_templates) / len(lang_templates)

                lines.append(f"Average complexity: {avg_complexity:.2f}")

                

                # List templates with key metrics

                for template in sorted(lang_templates, key=self._get_template_name):

                    lines.append(f"  - {template.name}: {len(template.variables)} vars, "

                               f"{len(template.filters)} filters, complexity {template.complexity_score}")

            

            lines.append("")

        

        return "\n".join(lines)

    

    def _generate_json_report(self) -> str:

        """Generate a JSON format report."""

        report_data = {}

        

        for key, analysis in self.analyses.items():

            language, template_name = key.split(':', 1)

            

            if language not in report_data:

                report_data[language] = {}

            

            # Convert sets to lists for JSON serialization

            template_data = asdict(analysis)

            for field in ['variables', 'filters', 'blocks', 'macros', 'includes', 'dependencies']:

                if isinstance(template_data[field], set):

                    template_data[field] = list(template_data[field])

            

            report_data[language][template_name] = template_data

        

        return json.dumps(report_data, indent=2, sort_keys=True)

    

    def _generate_markdown_report(self) -> str:

        """Generate a Markdown format report."""

        lines = [

            "# Template Analysis Report",

            "",

            "This report analyzes templates across different programming languages",

            "in the Goobits CLI framework to identify opportunities for unification.",

            ""

        ]

        

        # Summary table

        languages = set(key.split(':', 1)[0] for key in self.analyses.keys())

        lines.extend([

            "## Summary",

            "",

            "| Language | Templates | Avg Complexity |",

            "|----------|-----------|----------------|"

        ])

        

        for language in sorted(languages):

            lang_templates = [a for k, a in self.analyses.items() if k.startswith(f"{language}:")]

            count = len(lang_templates)

            avg_complexity = sum(t.complexity_score for t in lang_templates) / count if count > 0 else 0

            

            lines.append(f"| {language.capitalize()} | {count} | {avg_complexity:.2f} |")

        

        lines.extend(["", "## Detailed Analysis", ""])

        

        # Detailed per-language sections

        for language in sorted(languages):

            lang_templates = [a for k, a in self.analyses.items() if k.startswith(f"{language}:")]

            

            lines.extend([

                f"### {language.capitalize()}",

                ""

            ])

            

            if lang_templates:

                lines.extend([

                    "| Template | Variables | Filters | Blocks | Complexity |",

                    "|----------|-----------|---------|--------|------------|"

                ])

                

                for template in sorted(lang_templates, key=self._get_template_name):

                    lines.append(

                        f"| {template.name} | {len(template.variables)} | "

                        f"{len(template.filters)} | {len(template.blocks)} | "

                        f"{template.complexity_score} |"

                    )

            

            lines.append("")

        

        return "\n".join(lines)





def analyze_templates_command(

    templates_dir: Path = typer.Argument(

        ..., 

        help="Path to templates directory"

    ),

    output_format: str = typer.Option(

        "text",

        "--format",

        help="Output format: text, json, or markdown"

    ),

    output_file: Optional[Path] = typer.Option(

        None,

        "--output",

        help="Save report to file"

    ),

    compare: Optional[str] = typer.Option(

        None,

        "--compare",

        help="Compare templates with this base name across languages"

    )

):

    """

    Analyze templates to identify patterns and opportunities for unification.

    

    This command analyzes all templates in the specified directory and generates

    a comprehensive report showing commonalities and differences across languages.

    """

    typer.echo(f"Analyzing templates in: {templates_dir}")

    

    if not templates_dir.exists():

        typer.echo(f"Error: Templates directory not found: {templates_dir}", err=True)

        return 1

    

    # Initialize analyzer

    analyzer = TemplateAnalyzer(templates_dir)

    

    # Analyze all templates

    results = analyzer.analyze_all_templates()

    

    total_templates = sum(len(templates) for templates in results.values())

    typer.echo(f"Analyzed {total_templates} templates across {len(results)} languages")

    

    # Generate comparison if requested

    if compare:

        typer.echo(f"\nComparing templates matching '{compare}':")

        comparison = analyzer.compare_templates_across_languages(compare)

        

        typer.echo(f"Similarity score: {comparison.similarity_score:.3f}")

        typer.echo(f"Common variables: {len(comparison.common_variables)}")

        typer.echo(f"Common filters: {len(comparison.common_filters)}")

        typer.echo(f"Common blocks: {len(comparison.common_blocks)}")

        

        if comparison.recommendations:

            typer.echo("\nRecommendations:")

            for rec in comparison.recommendations:

                typer.echo(f"  • {rec}")

    

    # Generate report

    report = analyzer.generate_analysis_report(output_format)

    

    if output_file:

        output_file.write_text(report, encoding='utf-8')

        typer.echo(f"Report saved to: {output_file}")

    else:

        typer.echo("\n" + report)

    

    return 0





if __name__ == "__main__":

    typer.run(analyze_templates_command)