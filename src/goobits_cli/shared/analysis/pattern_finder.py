#!/usr/bin/env python3
"""
Pattern Analyzer for Goobits CLI Multi-Language Templates

This module analyzes templates across Python, Node.js, TypeScript, and Rust
to identify common patterns that can be extracted into shared components.
"""

from pathlib import Path
from typing import Dict, List, Set, Any
from dataclasses import dataclass, field
import json


@dataclass
class Pattern:
    """Represents a common pattern found across implementations"""

    name: str
    category: str
    languages: Set[str] = field(default_factory=set)
    variations: Dict[str, str] = field(default_factory=dict)
    frequency: int = 0
    examples: Dict[str, List[str]] = field(default_factory=dict)
    extractable: bool = True
    notes: str = ""


class PatternAnalyzer:
    """Analyzes template directories to find common patterns across languages"""

    def __init__(
        self, base_path: str = "/workspace/goobits-cli/src/goobits_cli/templates"
    ):
        self.base_path = Path(base_path)
        self.languages = {
            "python": self.base_path,
            "nodejs": self.base_path / "nodejs",
            "typescript": self.base_path / "typescript",
            "rust": self.base_path / "rust",
        }
        self.patterns: Dict[str, Pattern] = {}
        self.pattern_categories: Dict[str, List["Pattern"]] = {
            "code_structure": [],
            "operational": [],
            "documentation": [],
            "test": [],
        }

    def analyze_all(self) -> Dict[str, Any]:
        """Run complete analysis on all template directories"""
        print("🔍 Starting pattern analysis across all languages...\n")

        # Analyze each pattern type
        self._analyze_command_patterns()
        self._analyze_error_patterns()
        self._analyze_option_patterns()
        self._analyze_config_patterns()
        self._analyze_hook_patterns()
        self._analyze_doc_patterns()
        self._analyze_test_patterns()
        self._analyze_completion_patterns()
        self._analyze_styling_patterns()
        self._analyze_plugin_patterns()

        # Categorize patterns
        self._categorize_patterns()

        # Generate report
        return self._generate_report()

    def _analyze_command_patterns(self):
        """Analyze command structure patterns"""
        print("📌 Analyzing command patterns...")

        # Command definition pattern
        pattern = Pattern(
            name="command_definition",
            category="code_structure",
            notes="All languages define commands with name, description, handler",
        )

        # Check each language
        if (self.languages["python"] / "cli_template.py.j2").exists():
            pattern.languages.add("python")
            pattern.variations["python"] = "@click.command()"
            pattern.examples["python"] = [
                "@click.command()\ndef command_name():\n    '''Description'''"
            ]

        if (self.languages["nodejs"] / "cli.js.j2").exists():
            pattern.languages.add("nodejs")
            pattern.variations["nodejs"] = "program.command()"
            pattern.examples["nodejs"] = [
                "program.command('name')\n  .description('desc')\n  .action(handler)"
            ]

        if (self.languages["typescript"] / "cli.ts.j2").exists():
            pattern.languages.add("typescript")
            pattern.variations["typescript"] = "program.command()"
            pattern.examples["typescript"] = [
                "program.command('name')\n  .description('desc')\n  .action(handler)"
            ]

        if (self.languages["rust"] / "main.rs.j2").exists():
            pattern.languages.add("rust")
            pattern.variations["rust"] = "Command::new()"
            pattern.examples["rust"] = [
                'Command::new("name")\n    .about("description")\n    .arg(...)'
            ]

        if len(pattern.languages) == 4:
            self.patterns["command_definition"] = pattern

        # Subcommand pattern
        subcommand_pattern = Pattern(
            name="subcommand_structure",
            category="code_structure",
            notes="All languages support nested subcommands",
        )

        for lang in ["python", "nodejs", "typescript", "rust"]:
            subcommand_pattern.languages.add(lang)

        self.patterns["subcommand_structure"] = subcommand_pattern

    def _analyze_error_patterns(self):
        """Analyze error handling patterns"""
        print("📌 Analyzing error patterns...")

        pattern = Pattern(
            name="error_handling",
            category="operational",
            notes="All languages have error handling mechanisms",
        )

        pattern.languages = {"python", "nodejs", "typescript", "rust"}
        pattern.variations = {
            "python": "try/except with click.echo",
            "nodejs": "try/catch with console.error",
            "typescript": "try/catch with typed errors",
            "rust": "Result<T, E> with ? operator",
        }

        self.patterns["error_handling"] = pattern

        # Exit code pattern
        exit_pattern = Pattern(
            name="exit_codes",
            category="operational",
            notes="Standardized exit codes across all languages",
        )
        exit_pattern.languages = {"python", "nodejs", "typescript", "rust"}
        exit_pattern.examples = {
            "python": ["sys.exit(1)"],
            "nodejs": ["process.exit(1)"],
            "typescript": ["process.exit(1)"],
            "rust": ["std::process::exit(1)"],
        }
        self.patterns["exit_codes"] = exit_pattern

    def _analyze_option_patterns(self):
        """Analyze option/argument patterns"""
        print("📌 Analyzing option patterns...")

        # Option definition pattern
        pattern = Pattern(
            name="option_definition",
            category="code_structure",
            notes="All languages support options with types, defaults, and help text",
        )

        pattern.languages = {"python", "nodejs", "typescript", "rust"}
        pattern.variations = {
            "python": "@click.option('--name', type=str, default='', help='Help text')",
            "nodejs": ".option('-n, --name <value>', 'Help text', 'default')",
            "typescript": ".option('-n, --name <value>', 'Help text', 'default')",
            "rust": "Arg::new('name').long('name').help('Help text').default_value('default')",
        }

        self.patterns["option_definition"] = pattern

        # Required vs optional pattern
        req_pattern = Pattern(
            name="required_optional_args",
            category="code_structure",
            notes="All languages distinguish between required and optional arguments",
        )
        req_pattern.languages = {"python", "nodejs", "typescript", "rust"}
        self.patterns["required_optional_args"] = req_pattern

    def _analyze_config_patterns(self):
        """Analyze configuration patterns"""
        print("📌 Analyzing configuration patterns...")

        pattern = Pattern(
            name="config_management",
            category="operational",
            notes="All languages support configuration files and environment variables",
        )

        # Check for config patterns
        pattern.languages = {"python", "nodejs", "typescript", "rust"}
        pattern.variations = {
            "python": "ConfigParser/json with ~/.config",
            "nodejs": "JSON/YAML config files",
            "typescript": "Typed config interfaces",
            "rust": "Config struct with serde",
        }

        self.patterns["config_management"] = pattern

        # Environment variable pattern
        env_pattern = Pattern(
            name="env_var_handling",
            category="operational",
            notes="All languages read environment variables",
        )
        env_pattern.languages = {"python", "nodejs", "typescript", "rust"}
        self.patterns["env_var_handling"] = env_pattern

    def _analyze_hook_patterns(self):
        """Analyze hook/callback patterns"""
        print("📌 Analyzing hook patterns...")

        pattern = Pattern(
            name="hook_system",
            category="code_structure",
            notes="All languages implement a hook system for user logic",
        )

        pattern.languages = {"python", "nodejs", "typescript", "rust"}
        pattern.variations = {
            "python": "def on_command_name(*args, **kwargs)",
            "nodejs": "export async function onCommandName(args)",
            "typescript": "export async function onCommandName(args: Args)",
            "rust": "pub fn on_command_name(args: &Args) -> Result<()>",
        }

        self.patterns["hook_system"] = pattern

        # Async pattern
        async_pattern = Pattern(
            name="async_support",
            category="code_structure",
            notes="Node.js/TypeScript use async/await, Rust uses tokio, Python uses sync",
        )
        async_pattern.languages = {"nodejs", "typescript", "rust"}
        async_pattern.extractable = False  # Language-specific
        self.patterns["async_support"] = async_pattern

    def _analyze_doc_patterns(self):
        """Analyze documentation patterns"""
        print("📌 Analyzing documentation patterns...")

        # Help text pattern
        pattern = Pattern(
            name="help_text_generation",
            category="documentation",
            notes="All languages auto-generate help text from command definitions",
        )
        pattern.languages = {"python", "nodejs", "typescript", "rust"}
        self.patterns["help_text_generation"] = pattern

        # Examples pattern
        examples_pattern = Pattern(
            name="command_examples",
            category="documentation",
            notes="All languages support showing command examples",
        )
        examples_pattern.languages = {"python", "nodejs", "typescript", "rust"}
        self.patterns["command_examples"] = examples_pattern

        # Version display
        version_pattern = Pattern(
            name="version_display",
            category="documentation",
            notes="All languages show version information",
        )
        version_pattern.languages = {"python", "nodejs", "typescript", "rust"}
        self.patterns["version_display"] = version_pattern

    def _analyze_test_patterns(self):
        """Analyze test patterns"""
        print("📌 Analyzing test patterns...")

        # Test structure pattern
        pattern = Pattern(
            name="test_structure",
            category="test",
            notes="All languages have test templates",
        )

        # Check for test files
        if (self.languages["python"] / "test_cli.py.j2").exists():
            pattern.languages.add("python")
            pattern.variations["python"] = "pytest"

        if (self.languages["nodejs"] / "test").exists():
            pattern.languages.add("nodejs")
            pattern.variations["nodejs"] = "jest/mocha"

        if (self.languages["typescript"] / "test").exists():
            pattern.languages.add("typescript")
            pattern.variations["typescript"] = "jest with TypeScript"

        if (self.languages["rust"] / "tests.rs.j2").exists():
            pattern.languages.add("rust")
            pattern.variations["rust"] = "#[cfg(test)] mod tests"

        if len(pattern.languages) >= 3:  # Most languages have tests
            self.patterns["test_structure"] = pattern

        # CLI testing pattern
        cli_test_pattern = Pattern(
            name="cli_testing",
            category="test",
            notes="Testing CLI commands with arguments",
        )
        cli_test_pattern.languages = {"python", "nodejs", "typescript", "rust"}
        self.patterns["cli_testing"] = cli_test_pattern

    def _analyze_completion_patterns(self):
        """Analyze shell completion patterns"""
        print("📌 Analyzing completion patterns...")

        pattern = Pattern(
            name="shell_completion",
            category="operational",
            notes="Shell completion support across languages",
        )

        # Check for completion files
        for lang, path in self.languages.items():
            if lang == "python" and (path / "completion_engine.py.j2").exists():
                pattern.languages.add("python")
            elif lang == "nodejs" and (path / "completion_engine.js.j2").exists():
                pattern.languages.add("nodejs")
            elif lang == "typescript" and (path / "completion_engine.ts.j2").exists():
                pattern.languages.add("typescript")
            elif lang == "rust" and (path / "completion_engine.rs.j2").exists():
                pattern.languages.add("rust")

        if len(pattern.languages) >= 3:
            self.patterns["shell_completion"] = pattern

    def _analyze_styling_patterns(self):
        """Analyze terminal styling patterns"""
        print("📌 Analyzing styling patterns...")

        pattern = Pattern(
            name="terminal_styling",
            category="operational",
            notes="All languages support colored output and formatting",
        )

        pattern.languages = {"python", "nodejs", "typescript", "rust"}
        pattern.variations = {
            "python": "click.style() and rich",
            "nodejs": "chalk library",
            "typescript": "chalk with types",
            "rust": "colored crate",
        }

        self.patterns["terminal_styling"] = pattern

        # Progress indicators
        progress_pattern = Pattern(
            name="progress_indicators",
            category="operational",
            notes="Progress bars and spinners",
        )
        progress_pattern.languages = {"python", "nodejs", "typescript", "rust"}
        self.patterns["progress_indicators"] = progress_pattern

    def _analyze_plugin_patterns(self):
        """Analyze plugin system patterns"""
        print("📌 Analyzing plugin patterns...")

        pattern = Pattern(
            name="plugin_system",
            category="code_structure",
            notes="Plugin loading and management",
        )

        # Check which languages have plugin support
        if (self.languages["python"] / "plugin_loader.py.j2").exists():
            pattern.languages.add("python")
        if (self.languages["nodejs"] / "commands/builtin/plugin.js.j2").exists():
            pattern.languages.add("nodejs")
        if (self.languages["typescript"] / "lib/plugins.ts.j2").exists():
            pattern.languages.add("typescript")
        if (self.languages["rust"] / "plugins.rs.j2").exists():
            pattern.languages.add("rust")

        if len(pattern.languages) >= 2:
            self.patterns["plugin_system"] = pattern

    def _categorize_patterns(self):
        """Categorize patterns for parallel work"""
        for name, pattern in self.patterns.items():
            if pattern.category in self.pattern_categories:
                self.pattern_categories[pattern.category].append(pattern)

    def _generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive pattern inventory report"""
        report: Dict[str, Any] = {
            "summary": {
                "total_patterns": len(self.patterns),
                "extractable_patterns": sum(
                    1 for p in self.patterns.values() if p.extractable
                ),
                "languages_analyzed": 4,
                "categories": {
                    cat: len(patterns)
                    for cat, patterns in self.pattern_categories.items()
                },
            },
            "patterns": {},
            "categories": {},
            "boundaries": self._define_boundaries(),
        }

        # Add pattern details
        for name, pattern in self.patterns.items():
            report["patterns"][name] = {
                "name": pattern.name,
                "category": pattern.category,
                "languages": list(pattern.languages),
                "is_universal": len(pattern.languages) == 4,
                "extractable": pattern.extractable,
                "variations": pattern.variations,
                "notes": pattern.notes,
            }

        # Add categorized patterns for parallel work
        for category, patterns in self.pattern_categories.items():
            report["categories"][category] = [p.name for p in patterns]

        return report

    def _define_boundaries(self) -> Dict[str, Any]:
        """Define clear boundaries for parallel work"""
        return {
            "agent_a_code_structure": [
                "command_definition",
                "subcommand_structure",
                "option_definition",
                "required_optional_args",
                "hook_system",
                "plugin_system",
            ],
            "agent_b_operational": [
                "error_handling",
                "exit_codes",
                "config_management",
                "env_var_handling",
                "shell_completion",
                "terminal_styling",
                "progress_indicators",
            ],
            "agent_c_documentation": [
                "help_text_generation",
                "command_examples",
                "version_display",
            ],
            "agent_d_test": ["test_structure", "cli_testing"],
            "notes": {
                "safe_parallel": "Each agent can work on their assigned patterns without conflicts",
                "dependencies": "Config patterns may affect command patterns - coordinate if needed",
                "shared_files": "No direct file conflicts expected between agents",
            },
        }

    def print_report(self, report: Dict[str, Any]):
        """Print formatted report to console"""
        print("\n" + "=" * 60)
        print("🎯 PATTERN ANALYSIS REPORT")
        print("=" * 60 + "\n")

        # Summary
        print("📊 SUMMARY")
        print(f"  Total Patterns Found: {report['summary']['total_patterns']}")
        print(f"  Extractable Patterns: {report['summary']['extractable_patterns']}")
        print(f"  Languages Analyzed: {report['summary']['languages_analyzed']}")
        print("\n  Category Breakdown:")
        for cat, count in report["summary"]["categories"].items():
            print(f"    - {cat}: {count} patterns")

        # Universal patterns
        print("\n\n🌍 UNIVERSAL PATTERNS (Found in ALL 4 languages)")
        print("-" * 60)
        universal_patterns = [
            p for name, p in report["patterns"].items() if p["is_universal"]
        ]
        for pattern in universal_patterns:
            print(f"\n  📦 {pattern['name']}")
            print(f"     Category: {pattern['category']}")
            print(f"     Extractable: {'✅' if pattern['extractable'] else '❌'}")
            if pattern["notes"]:
                print(f"     Notes: {pattern['notes']}")
            if pattern["variations"]:
                print("     Variations:")
                for lang, var in pattern["variations"].items():
                    print(f"       - {lang}: {var}")

        # Non-universal patterns
        print("\n\n🔧 LANGUAGE-SPECIFIC PATTERNS")
        print("-" * 60)
        specific_patterns = [
            p for name, p in report["patterns"].items() if not p["is_universal"]
        ]
        for pattern in specific_patterns:
            print(f"\n  📦 {pattern['name']}")
            print(f"     Languages: {', '.join(pattern['languages'])}")
            print(f"     Category: {pattern['category']}")
            if pattern["notes"]:
                print(f"     Notes: {pattern['notes']}")

        # Work boundaries
        print("\n\n🚧 PARALLEL WORK BOUNDARIES")
        print("-" * 60)
        for agent, patterns in report["boundaries"].items():
            if agent.startswith("agent_"):
                agent_name = agent.replace("_", " ").title()
                print(f"\n  {agent_name}:")
                for pattern in patterns:
                    print(f"    - {pattern}")

        print("\n  ℹ️  Notes:")
        for key, value in report["boundaries"]["notes"].items():
            print(f"    - {key}: {value}")

        print("\n" + "=" * 60 + "\n")

    def save_report(
        self, report: Dict[str, Any], filename: str = "pattern_inventory.md"
    ):
        """Save report as markdown file"""
        output_path = Path(__file__).parent / filename

        with open(output_path, "w") as f:
            f.write("# Pattern Inventory Report\n\n")
            f.write("## Summary\n\n")
            f.write(
                f"- **Total Patterns Found**: {report['summary']['total_patterns']}\n"
            )
            f.write(
                f"- **Extractable Patterns**: {report['summary']['extractable_patterns']}\n"
            )
            f.write(
                f"- **Languages Analyzed**: {report['summary']['languages_analyzed']}\n\n"
            )

            f.write("### Category Breakdown\n\n")
            for cat, count in report["summary"]["categories"].items():
                f.write(f"- **{cat}**: {count} patterns\n")

            f.write("\n## Universal Patterns\n\n")
            f.write("Patterns found in ALL 4 languages:\n\n")

            universal_patterns = [
                p for name, p in report["patterns"].items() if p["is_universal"]
            ]
            for pattern in universal_patterns:
                f.write(f"### {pattern['name']}\n\n")
                f.write(f"- **Category**: {pattern['category']}\n")
                f.write(
                    f"- **Extractable**: {'✅ Yes' if pattern['extractable'] else '❌ No'}\n"
                )
                if pattern["notes"]:
                    f.write(f"- **Notes**: {pattern['notes']}\n")
                if pattern["variations"]:
                    f.write("\n**Variations**:\n\n")
                    for lang, var in pattern["variations"].items():
                        f.write(f"- **{lang}**: `{var}`\n")
                f.write("\n")

            f.write("\n## Language-Specific Patterns\n\n")
            specific_patterns = [
                p for name, p in report["patterns"].items() if not p["is_universal"]
            ]
            for pattern in specific_patterns:
                f.write(f"### {pattern['name']}\n\n")
                f.write(f"- **Languages**: {', '.join(pattern['languages'])}\n")
                f.write(f"- **Category**: {pattern['category']}\n")
                if pattern["notes"]:
                    f.write(f"- **Notes**: {pattern['notes']}\n")
                f.write("\n")

            f.write("\n## Parallel Work Assignment\n\n")
            for agent, patterns in report["boundaries"].items():
                if agent.startswith("agent_"):
                    agent_name = (
                        agent.replace("_", " ").replace("agent ", "Agent ").title()
                    )
                    f.write(f"### {agent_name}\n\n")
                    for pattern in patterns:
                        f.write(f"- {pattern}\n")
                    f.write("\n")

            f.write("### Notes\n\n")
            for key, value in report["boundaries"]["notes"].items():
                f.write(f"- **{key.replace('_', ' ').title()}**: {value}\n")

        print(f"✅ Report saved to: {output_path}")


if __name__ == "__main__":
    analyzer = PatternAnalyzer()
    report = analyzer.analyze_all()

    # Print to console
    analyzer.print_report(report)

    # Save as markdown
    analyzer.save_report(report)

    # Also save as JSON for programmatic access
    json_path = Path(__file__).parent / "pattern_inventory.json"
    with open(json_path, "w") as f:
        json.dump(report, f, indent=2)
    print(f"✅ JSON report saved to: {json_path}")
