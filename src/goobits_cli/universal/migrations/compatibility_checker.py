"""
Compatibility Checker for Universal Template System

This module provides tools to verify that the Universal Template System
generates output that is functionally equivalent to the legacy templates.
"""

import hashlib
import difflib
import tempfile
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
import typer
import yaml

from ...schemas import ConfigSchema, GoobitsConfigSchema
from ...generators.python import PythonGenerator
from ...generators.nodejs import NodeJSGenerator  
from ...generators.typescript import TypeScriptGenerator
from ...generators.rust import RustGenerator


@dataclass
class ComparisonResult:
    """Results of comparing legacy vs universal template output."""
    language: str
    template_name: str
    files_match: bool
    content_differences: List[str]
    functional_differences: List[str]
    similarity_score: float
    recommendations: List[str]


@dataclass
class OverallCompatibilityResult:
    """Overall compatibility assessment."""
    total_comparisons: int
    successful_matches: int
    partial_matches: int
    failures: int
    compatibility_score: float
    critical_issues: List[str]
    warnings: List[str]
    summary: str


class CompatibilityChecker:
    """
    Verifies that Universal Template System generates functionally
    equivalent output to legacy templates.
    """
    
    def __init__(self, test_configs: List[Path]):
        """
        Initialize the compatibility checker.
        
        Args:
            test_configs: List of test configuration files to use for comparison
        """
        self.test_configs = test_configs
        self.results: List[ComparisonResult] = []
        
        # Generator instances
        self.legacy_generators = {
            "python": PythonGenerator(use_universal_templates=False),
            "nodejs": NodeJSGenerator(use_universal_templates=False),
            "typescript": TypeScriptGenerator(use_universal_templates=False),
            "rust": RustGenerator(use_universal_templates=False),
        }
        
        self.universal_generators = {
            "python": PythonGenerator(use_universal_templates=True),
            "nodejs": NodeJSGenerator(use_universal_templates=True),
            "typescript": TypeScriptGenerator(use_universal_templates=True),
            "rust": RustGenerator(use_universal_templates=True),
        }
    
    def load_test_config(self, config_path: Path) -> GoobitsConfigSchema:
        """
        Load a test configuration file.
        
        Args:
            config_path: Path to configuration file
            
        Returns:
            Loaded configuration schema
        """
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            return GoobitsConfigSchema(**data)
        except Exception as e:
            typer.echo(f"Error loading config {config_path}: {e}", err=True)
            raise
    
    def generate_with_both_systems(self, config: GoobitsConfigSchema, 
                                  language: str) -> Tuple[Dict[str, str], Dict[str, str]]:
        """
        Generate CLI output using both legacy and universal systems.
        
        Args:
            config: Configuration to use for generation
            language: Target language
            
        Returns:
            Tuple of (legacy_files, universal_files)
        """
        legacy_files = {}
        universal_files = {}
        
        try:
            # Generate with legacy system
            legacy_generator = self.legacy_generators[language]
            legacy_files = legacy_generator.generate_all_files(config, "test.yaml", "1.0.0")
            
            # Generate with universal system
            universal_generator = self.universal_generators[language]
            universal_files = universal_generator.generate_all_files(config, "test.yaml", "1.0.0")
            
        except Exception as e:
            typer.echo(f"Error generating {language} files: {e}", err=True)
        
        return legacy_files, universal_files
    
    def compare_file_contents(self, legacy_content: str, 
                            universal_content: str) -> Tuple[float, List[str]]:
        """
        Compare two file contents and return similarity score and differences.
        
        Args:
            legacy_content: Content from legacy template
            universal_content: Content from universal template
            
        Returns:
            Tuple of (similarity_score, list_of_differences)
        """
        # Normalize whitespace and line endings
        legacy_lines = [line.strip() for line in legacy_content.split('\n') if line.strip()]
        universal_lines = [line.strip() for line in universal_content.split('\n') if line.strip()]
        
        # Calculate similarity using difflib
        matcher = difflib.SequenceMatcher(None, legacy_lines, universal_lines)
        similarity_score = matcher.ratio()
        
        # Get detailed differences
        differences = []
        diff = difflib.unified_diff(
            legacy_lines, universal_lines,
            fromfile='legacy', tofile='universal',
            lineterm='', n=3
        )
        
        for line in diff:
            differences.append(line)
        
        return similarity_score, differences
    
    def analyze_functional_differences(self, legacy_content: str, 
                                     universal_content: str, 
                                     language: str) -> List[str]:
        """
        Analyze functional differences between generated files.
        
        Args:
            legacy_content: Content from legacy template
            universal_content: Content from universal template  
            language: Programming language
            
        Returns:
            List of functional differences found
        """
        functional_diffs = []
        
        # Language-specific functional analysis
        if language == "python":
            functional_diffs.extend(self._analyze_python_functions(legacy_content, universal_content))
        elif language in ["nodejs", "typescript"]:
            functional_diffs.extend(self._analyze_js_functions(legacy_content, universal_content))
        elif language == "rust":
            functional_diffs.extend(self._analyze_rust_functions(legacy_content, universal_content))
        
        return functional_diffs
    
    def _analyze_python_functions(self, legacy: str, universal: str) -> List[str]:
        """Analyze Python-specific functional differences."""
        import re
        
        differences = []
        
        # Extract function signatures
        legacy_funcs = set(re.findall(r'def\s+(\w+)\s*\([^)]*\):', legacy))
        universal_funcs = set(re.findall(r'def\s+(\w+)\s*\([^)]*\):', universal))
        
        missing_functions = legacy_funcs - universal_funcs
        extra_functions = universal_funcs - legacy_funcs
        
        if missing_functions:
            differences.append(f"Missing functions in universal: {', '.join(missing_functions)}")
        if extra_functions:
            differences.append(f"Extra functions in universal: {', '.join(extra_functions)}")
        
        # Check imports
        legacy_imports = set(re.findall(r'^(?:import|from)\s+([^\s#]+)', legacy, re.MULTILINE))
        universal_imports = set(re.findall(r'^(?:import|from)\s+([^\s#]+)', universal, re.MULTILINE))
        
        missing_imports = legacy_imports - universal_imports
        if missing_imports:
            differences.append(f"Missing imports in universal: {', '.join(missing_imports)}")
        
        return differences
    
    def _analyze_js_functions(self, legacy: str, universal: str) -> List[str]:
        """Analyze JavaScript/TypeScript-specific functional differences."""
        import re
        
        differences = []
        
        # Extract function definitions
        func_patterns = [
            r'function\s+(\w+)\s*\(',
            r'const\s+(\w+)\s*=\s*(?:async\s*)?(?:function|\([^)]*\)\s*=>)',
            r'(\w+)\s*:\s*(?:async\s*)?function'
        ]
        
        legacy_funcs = set()
        universal_funcs = set()
        
        for pattern in func_patterns:
            legacy_funcs.update(re.findall(pattern, legacy))
            universal_funcs.update(re.findall(pattern, universal))
        
        missing_functions = legacy_funcs - universal_funcs
        if missing_functions:
            differences.append(f"Missing functions in universal: {', '.join(missing_functions)}")
        
        # Check requires/imports
        import_patterns = [
            r'require\([\'"]([^\'"]+)[\'"]\)',
            r'import.*from\s+[\'"]([^\'"]+)[\'"]'
        ]
        
        legacy_imports = set()
        universal_imports = set()
        
        for pattern in import_patterns:
            legacy_imports.update(re.findall(pattern, legacy))
            universal_imports.update(re.findall(pattern, universal))
        
        missing_imports = legacy_imports - universal_imports
        if missing_imports:
            differences.append(f"Missing imports in universal: {', '.join(missing_imports)}")
        
        return differences
    
    def _analyze_rust_functions(self, legacy: str, universal: str) -> List[str]:
        """Analyze Rust-specific functional differences."""
        import re
        
        differences = []
        
        # Extract function signatures
        legacy_funcs = set(re.findall(r'fn\s+(\w+)\s*\(', legacy))
        universal_funcs = set(re.findall(r'fn\s+(\w+)\s*\(', universal))
        
        missing_functions = legacy_funcs - universal_funcs
        if missing_functions:
            differences.append(f"Missing functions in universal: {', '.join(missing_functions)}")
        
        # Check use statements
        legacy_uses = set(re.findall(r'^use\s+([^;]+);', legacy, re.MULTILINE))
        universal_uses = set(re.findall(r'^use\s+([^;]+);', universal, re.MULTILINE))
        
        missing_uses = legacy_uses - universal_uses
        if missing_uses:
            differences.append(f"Missing use statements in universal: {', '.join(missing_uses)}")
        
        return differences
    
    def compare_generated_files(self, config: GoobitsConfigSchema, 
                               language: str) -> List[ComparisonResult]:
        """
        Compare generated files between legacy and universal systems.
        
        Args:
            config: Configuration to test with
            language: Target language
            
        Returns:
            List of comparison results for each file
        """
        results = []
        
        # Generate files with both systems
        legacy_files, universal_files = self.generate_with_both_systems(config, language)
        
        # Compare each file
        all_files = set(legacy_files.keys()) | set(universal_files.keys())
        
        for filename in all_files:
            legacy_content = legacy_files.get(filename, "")
            universal_content = universal_files.get(filename, "")
            
            # Check if files exist in both systems
            files_match = bool(legacy_content and universal_content)
            
            if not files_match:
                # File missing from one system
                if filename in legacy_files and filename not in universal_files:
                    result = ComparisonResult(
                        language=language,
                        template_name=filename,
                        files_match=False,
                        content_differences=[f"File missing from universal system: {filename}"],
                        functional_differences=[],
                        similarity_score=0.0,
                        recommendations=[f"Implement {filename} in universal templates"]
                    )
                elif filename in universal_files and filename not in legacy_files:
                    result = ComparisonResult(
                        language=language,
                        template_name=filename,
                        files_match=False,
                        content_differences=[f"Extra file in universal system: {filename}"],
                        functional_differences=[],
                        similarity_score=0.0,
                        recommendations=[f"Verify if {filename} is needed"]
                    )
                else:
                    result = ComparisonResult(
                        language=language,
                        template_name=filename,
                        files_match=False,
                        content_differences=["File missing from both systems"],
                        functional_differences=[],
                        similarity_score=0.0,
                        recommendations=["Investigation needed"]
                    )
            else:
                # Compare content
                similarity_score, content_diffs = self.compare_file_contents(
                    legacy_content, universal_content
                )
                
                # Analyze functional differences
                functional_diffs = self.analyze_functional_differences(
                    legacy_content, universal_content, language
                )
                
                # Generate recommendations
                recommendations = []
                if similarity_score < 0.8:
                    recommendations.append(f"Low similarity ({similarity_score:.2f}) - review differences")
                if functional_diffs:
                    recommendations.append("Functional differences found - verify compatibility")
                if similarity_score >= 0.95:
                    recommendations.append("High compatibility - safe to use universal template")
                
                result = ComparisonResult(
                    language=language,
                    template_name=filename,
                    files_match=True,
                    content_differences=content_diffs[:10],  # Limit to first 10 differences
                    functional_differences=functional_diffs,
                    similarity_score=similarity_score,
                    recommendations=recommendations
                )
            
            results.append(result)
        
        return results
    
    def run_full_compatibility_check(self) -> OverallCompatibilityResult:
        """
        Run full compatibility check across all test configurations and languages.
        
        Returns:
            Overall compatibility assessment
        """
        all_results = []
        
        for config_path in self.test_configs:
            typer.echo(f"Testing configuration: {config_path}")
            
            try:
                config = self.load_test_config(config_path)
                
                # Test each supported language
                for language in ["python", "nodejs", "typescript", "rust"]:
                    if hasattr(config, 'language') and config.language != language:
                        continue  # Skip if config specifies different language
                    
                    typer.echo(f"  Checking {language}...")
                    
                    try:
                        results = self.compare_generated_files(config, language)
                        all_results.extend(results)
                    except Exception as e:
                        typer.echo(f"    Error testing {language}: {e}", err=True)
                        # Add failure result
                        all_results.append(ComparisonResult(
                            language=language,
                            template_name="generation_failure",
                            files_match=False,
                            content_differences=[f"Generation failed: {e}"],
                            functional_differences=[],
                            similarity_score=0.0,
                            recommendations=["Fix generation error"]
                        ))
            
            except Exception as e:
                typer.echo(f"Error with config {config_path}: {e}", err=True)
                continue
        
        # Analyze overall results
        total_comparisons = len(all_results)
        successful_matches = len([r for r in all_results if r.files_match and r.similarity_score >= 0.95])
        partial_matches = len([r for r in all_results if r.files_match and 0.8 <= r.similarity_score < 0.95])
        failures = len([r for r in all_results if not r.files_match or r.similarity_score < 0.8])
        
        # Calculate overall compatibility score
        if total_comparisons > 0:
            compatibility_score = (successful_matches + 0.5 * partial_matches) / total_comparisons
        else:
            compatibility_score = 0.0
        
        # Identify critical issues
        critical_issues = []
        warnings = []
        
        for result in all_results:
            if not result.files_match:
                critical_issues.append(f"{result.language}: {result.template_name} - file missing")
            elif result.similarity_score < 0.5:
                critical_issues.append(f"{result.language}: {result.template_name} - low similarity ({result.similarity_score:.2f})")
            elif result.similarity_score < 0.8:
                warnings.append(f"{result.language}: {result.template_name} - moderate differences ({result.similarity_score:.2f})")
            
            if result.functional_differences:
                critical_issues.extend([f"{result.language}: {result.template_name} - {diff}" for diff in result.functional_differences])
        
        # Generate summary
        if compatibility_score >= 0.9:
            summary = "High compatibility - Universal Template System is ready for production use"
        elif compatibility_score >= 0.7:
            summary = "Good compatibility - Minor issues need to be addressed"
        elif compatibility_score >= 0.5:
            summary = "Moderate compatibility - Several issues require attention"
        else:
            summary = "Low compatibility - Major issues must be resolved before use"
        
        self.results = all_results
        
        return OverallCompatibilityResult(
            total_comparisons=total_comparisons,
            successful_matches=successful_matches,
            partial_matches=partial_matches,
            failures=failures,
            compatibility_score=compatibility_score,
            critical_issues=critical_issues,
            warnings=warnings,
            summary=summary
        )
    
    def generate_detailed_report(self) -> str:
        """
        Generate a detailed compatibility report.
        
        Returns:
            Formatted compatibility report
        """
        if not self.results:
            return "No compatibility check results available. Run run_full_compatibility_check() first."
        
        lines = [
            "# Universal Template System Compatibility Report",
            "=" * 60,
            "",
            "This report compares output from legacy templates with the",
            "Universal Template System to verify functional compatibility.",
            ""
        ]
        
        # Group results by language
        by_language = {}
        for result in self.results:
            if result.language not in by_language:
                by_language[result.language] = []
            by_language[result.language].append(result)
        
        # Summary for each language
        for language, results in sorted(by_language.items()):
            lines.extend([
                f"## {language.capitalize()} Results",
                ""
            ])
            
            successful = len([r for r in results if r.files_match and r.similarity_score >= 0.95])
            partial = len([r for r in results if r.files_match and 0.8 <= r.similarity_score < 0.95])
            failures = len(results) - successful - partial
            
            lines.extend([
                f"Total files compared: {len(results)}",
                f"Successful matches: {successful}",
                f"Partial matches: {partial}",
                f"Failures: {failures}",
                ""
            ])
            
            # Detailed results for each file
            for result in sorted(results, key=lambda r: r.template_name):
                status = "✅" if result.similarity_score >= 0.95 else "⚠️" if result.similarity_score >= 0.8 else "❌"
                lines.append(f"{status} {result.template_name} (similarity: {result.similarity_score:.3f})")
                
                if result.functional_differences:
                    for diff in result.functional_differences[:3]:  # Show first 3 differences
                        lines.append(f"    - {diff}")
                
                if result.recommendations:
                    for rec in result.recommendations[:2]:  # Show first 2 recommendations
                        lines.append(f"    💡 {rec}")
            
            lines.append("")
        
        return "\n".join(lines)


def compatibility_check_command(
    test_configs: List[Path] = typer.Argument(
        ...,
        help="Paths to test configuration files"
    ),
    output_file: Optional[Path] = typer.Option(
        None,
        "--output",
        help="Save detailed report to file"
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        help="Show detailed comparison results"
    )
):
    """
    Check compatibility between legacy and universal template systems.
    
    This command generates CLI output using both systems and compares them
    to verify that the Universal Template System produces functionally
    equivalent results.
    """
    typer.echo(f"Running compatibility check with {len(test_configs)} test configurations")
    
    # Verify test configs exist
    valid_configs = []
    for config_path in test_configs:
        if config_path.exists():
            valid_configs.append(config_path)
        else:
            typer.echo(f"Warning: Config file not found: {config_path}", err=True)
    
    if not valid_configs:
        typer.echo("Error: No valid test configuration files found", err=True)
        return 1
    
    # Run compatibility check
    checker = CompatibilityChecker(valid_configs)
    overall_result = checker.run_full_compatibility_check()
    
    # Display summary
    typer.echo(f"\n📊 Compatibility Check Results:")
    typer.echo(f"Total comparisons: {overall_result.total_comparisons}")
    typer.echo(f"Successful matches: {overall_result.successful_matches}")
    typer.echo(f"Partial matches: {overall_result.partial_matches}")
    typer.echo(f"Failures: {overall_result.failures}")
    typer.echo(f"Overall compatibility: {overall_result.compatibility_score:.1%}")
    typer.echo(f"\n{overall_result.summary}")
    
    # Show critical issues
    if overall_result.critical_issues:
        typer.echo(f"\n🚨 Critical Issues ({len(overall_result.critical_issues)}):")
        for issue in overall_result.critical_issues[:5]:  # Show first 5
            typer.echo(f"  • {issue}")
        if len(overall_result.critical_issues) > 5:
            typer.echo(f"  ... and {len(overall_result.critical_issues) - 5} more")
    
    # Show warnings
    if overall_result.warnings:
        typer.echo(f"\n⚠️  Warnings ({len(overall_result.warnings)}):")
        for warning in overall_result.warnings[:3]:  # Show first 3
            typer.echo(f"  • {warning}")
        if len(overall_result.warnings) > 3:
            typer.echo(f"  ... and {len(overall_result.warnings) - 3} more")
    
    # Generate detailed report if requested
    if output_file or verbose:
        detailed_report = checker.generate_detailed_report()
        
        if output_file:
            output_file.write_text(detailed_report, encoding='utf-8')
            typer.echo(f"\n📄 Detailed report saved to: {output_file}")
        
        if verbose:
            typer.echo("\n" + detailed_report)
    
    # Return appropriate exit code
    if overall_result.compatibility_score >= 0.9:
        return 0  # Success
    elif overall_result.compatibility_score >= 0.7:
        return 0  # Acceptable with warnings
    else:
        return 1  # Issues need to be resolved


if __name__ == "__main__":
    typer.run(compatibility_check_command)