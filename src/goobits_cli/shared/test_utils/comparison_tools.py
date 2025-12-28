"""Cross-language comparison tools for testing CLI behavior consistency.



This module provides utilities to compare CLI outputs, file structures, and

behavior across different language implementations of the same CLI.

"""

import re

import difflib

from typing import Dict, List, Any, Set

from dataclasses import dataclass, field


@dataclass
class ComparisonResult:
    """Result of a cross-language comparison."""

    languages_compared: List[str]

    passed: bool

    summary: str

    differences: List[Dict[str, Any]] = field(default_factory=list)

    similarities: List[str] = field(default_factory=list)

    normalized_outputs: Dict[str, str] = field(default_factory=dict)

    def add_difference(self, category: str, description: str, details: Dict[str, Any]):
        """Add a difference to the comparison result."""

        self.differences.append(
            {"category": category, "description": description, "details": details}
        )

    def add_similarity(self, description: str):
        """Add a similarity to the comparison result."""

        self.similarities.append(description)

    def get_diff_summary(self) -> str:
        """Get a summary of differences found."""

        if not self.differences:

            return "No significant differences found."

        summary = f"Found {len(self.differences)} differences:\n"

        for diff in self.differences:

            summary += f"- {diff['category']}: {diff['description']}\n"

        return summary


class CrossLanguageComparator:
    """Tool for comparing CLI behavior across different language implementations."""

    def __init__(self):

        self.normalization_rules = self._load_normalization_rules()

    def _load_normalization_rules(self) -> Dict[str, List[Dict[str, str]]]:
        """Load language-specific normalization rules for output comparison."""

        return {
            "python": [
                {"pattern": r"rich_click\.", "replacement": ""},
                {"pattern": r"click\.", "replacement": ""},
                {"pattern": r"Usage: .+\.py", "replacement": "Usage: cli"},
                {"pattern": r"Error: ", "replacement": "Error: "},
            ],
            "nodejs": [
                {"pattern": r"node index\.js", "replacement": "cli"},
                {"pattern": r"Usage: node .+", "replacement": "Usage: cli"},
                {"pattern": r"error:", "replacement": "Error:"},
            ],
            "typescript": [
                {"pattern": r"node .+\.js", "replacement": "cli"},
                {"pattern": r"ts-node .+\.ts", "replacement": "cli"},
                {"pattern": r"Usage: .+", "replacement": "Usage: cli"},
                {"pattern": r"error:", "replacement": "Error:"},
            ],
            "rust": [
                {"pattern": r"error:", "replacement": "Error:"},
                {"pattern": r"Usage: .+", "replacement": "Usage: cli"},
                {"pattern": r"SUBCOMMANDS:", "replacement": "Commands:"},
                {"pattern": r"OPTIONS:", "replacement": "Options:"},
            ],
        }

    def compare_cli_outputs(
        self, outputs: Dict[str, str], command: List[str], comparison_type: str = "help"
    ) -> ComparisonResult:
        """Compare CLI outputs across different languages.



        Args:

            outputs: Dictionary mapping language to CLI output

            command: Command that was executed

            comparison_type: Type of comparison ('help', 'version', 'error')



        Returns:

            ComparisonResult with detailed comparison information

        """

        languages = list(outputs.keys())

        result = ComparisonResult(languages_compared=languages, passed=True, summary="")

        # Normalize outputs for comparison

        normalized_outputs = {}

        for language, output in outputs.items():

            normalized_outputs[language] = self.normalize_cli_output(output, language)

        result.normalized_outputs = normalized_outputs

        # Compare based on type

        if comparison_type == "help":

            self._compare_help_outputs(normalized_outputs, result)

        elif comparison_type == "version":

            self._compare_version_outputs(normalized_outputs, result)

        elif comparison_type == "error":

            self._compare_error_outputs(normalized_outputs, result)

        else:

            self._compare_generic_outputs(normalized_outputs, result)

        # Determine overall result

        result.passed = len(result.differences) == 0

        result.summary = (
            f"Compared {len(languages)} languages for command: {' '.join(command)}"
        )

        return result

    def normalize_cli_output(self, output: str, language: str) -> str:
        """Normalize CLI output for cross-language comparison.



        Args:

            output: Raw CLI output

            language: Source language



        Returns:

            Normalized output string

        """

        normalized = output

        # Apply language-specific normalization rules

        if language in self.normalization_rules:

            for rule in self.normalization_rules[language]:

                normalized = re.sub(rule["pattern"], rule["replacement"], normalized)

        # Common normalizations

        # Remove leading/trailing whitespace from lines

        lines = [line.strip() for line in normalized.split("\n")]

        normalized = "\n".join(lines)

        # Remove empty lines at start and end

        normalized = normalized.strip()

        # Normalize multiple spaces to single spaces

        normalized = re.sub(r" +", " ", normalized)

        # Normalize line endings

        normalized = normalized.replace("\r\n", "\n").replace("\r", "\n")

        return normalized

    def _compare_help_outputs(self, outputs: Dict[str, str], result: ComparisonResult):
        """Compare help command outputs."""

        # Check for common help sections

        help_sections = ["Usage:", "Options:", "Commands:", "Arguments:"]

        for section in help_sections:

            languages_with_section = []

            for language, output in outputs.items():

                if section in output:

                    languages_with_section.append(language)

            if languages_with_section:

                if len(languages_with_section) == len(outputs):

                    result.add_similarity(f"All languages include '{section}' section")

                else:

                    missing_languages = set(outputs.keys()) - set(
                        languages_with_section
                    )

                    result.add_difference(
                        "help_sections",
                        f"'{section}' section missing in some languages",
                        {
                            "present_in": languages_with_section,
                            "missing_in": list(missing_languages),
                        },
                    )

    def _compare_version_outputs(
        self, outputs: Dict[str, str], result: ComparisonResult
    ):
        """Compare version command outputs."""

        version_patterns = []

        for language, output in outputs.items():

            # Extract version numbers

            version_matches = re.findall(r"\d+\.\d+\.\d+", output)

            if version_matches:

                version_patterns.extend(version_matches)

        # Check if all languages report the same version

        unique_versions = set(version_patterns)

        if len(unique_versions) == 1:

            result.add_similarity(
                f"All languages report same version: {list(unique_versions)[0]}"
            )

        elif len(unique_versions) > 1:

            result.add_difference(
                "version_mismatch",
                "Different versions reported across languages",
                {"versions_found": list(unique_versions)},
            )

    def _compare_error_outputs(self, outputs: Dict[str, str], result: ComparisonResult):
        """Compare error message outputs."""

        # Check for common error indicators

        error_indicators = ["Error:", "error", "missing", "required", "invalid"]

        for indicator in error_indicators:

            languages_with_indicator = []

            for language, output in outputs.items():

                if indicator.lower() in output.lower():

                    languages_with_indicator.append(language)

            if len(languages_with_indicator) > 0:

                if len(languages_with_indicator) == len(outputs):

                    result.add_similarity(
                        f"All languages show error indicator: '{indicator}'"
                    )

                else:

                    missing_languages = set(outputs.keys()) - set(
                        languages_with_indicator
                    )

                    result.add_difference(
                        "error_indicators",
                        f"Error indicator '{indicator}' missing in some languages",
                        {
                            "present_in": languages_with_indicator,
                            "missing_in": list(missing_languages),
                        },
                    )

    def _compare_generic_outputs(
        self, outputs: Dict[str, str], result: ComparisonResult
    ):
        """Compare generic command outputs."""

        # Simple length comparison

        output_lengths = {lang: len(output) for lang, output in outputs.items()}

        min_length = min(output_lengths.values())

        max_length = max(output_lengths.values())

        # Flag significant length differences

        if max_length > min_length * 2:

            result.add_difference(
                "output_length",
                "Significant difference in output length",
                {"lengths": output_lengths},
            )

        else:

            result.add_similarity("Output lengths are similar across languages")

    def compare_file_structures(
        self, file_structures: Dict[str, Dict[str, str]]
    ) -> ComparisonResult:
        """Compare generated file structures across languages.



        Args:

            file_structures: Dict mapping language -> filename -> file content



        Returns:

            ComparisonResult comparing file structures

        """

        languages = list(file_structures.keys())

        result = ComparisonResult(
            languages_compared=languages,
            passed=True,
            summary=f"File structure comparison across {len(languages)} languages",
        )

        # Compare file counts

        file_counts = {lang: len(files) for lang, files in file_structures.items()}

        if len(set(file_counts.values())) == 1:

            result.add_similarity(
                f"All languages generate same number of files: {list(file_counts.values())[0]}"
            )

        else:

            result.add_difference(
                "file_count",
                "Different number of files generated",
                {"file_counts": file_counts},
            )

        # Compare common file types

        all_files = set()

        for files in file_structures.values():

            all_files.update(files.keys())

        common_extensions = self._get_file_extensions(all_files)

        for ext in common_extensions:

            languages_with_ext = []

            for language, files in file_structures.items():

                if any(f.endswith(ext) for f in files.keys()):

                    languages_with_ext.append(language)

            if len(languages_with_ext) > 1:

                result.add_similarity(f"Multiple languages generate {ext} files")

        # Compare specific expected files

        expected_files = ["README.md", "setup.sh"]

        for expected_file in expected_files:

            languages_with_file = []

            for language, files in file_structures.items():

                if expected_file in files:

                    languages_with_file.append(language)

            if languages_with_file:

                if len(languages_with_file) == len(file_structures):

                    result.add_similarity(f"All languages generate {expected_file}")

                else:

                    missing_languages = set(file_structures.keys()) - set(
                        languages_with_file
                    )

                    result.add_difference(
                        "missing_files",
                        f"{expected_file} missing in some languages",
                        {
                            "present_in": languages_with_file,
                            "missing_in": list(missing_languages),
                        },
                    )

        result.passed = len(result.differences) == 0

        return result

    def _get_file_extensions(self, filenames: Set[str]) -> Set[str]:
        """Extract unique file extensions from a set of filenames."""

        extensions = set()

        for filename in filenames:

            if "." in filename:

                ext = "." + filename.split(".")[-1]

                extensions.add(ext)

        return extensions

    def generate_detailed_diff(
        self, outputs: Dict[str, str], normalize: bool = True
    ) -> str:
        """Generate a detailed diff between CLI outputs.



        Args:

            outputs: Dictionary mapping language to output

            normalize: Whether to normalize outputs before diffing



        Returns:

            Detailed diff string

        """

        if len(outputs) != 2:

            raise ValueError("Detailed diff requires exactly 2 outputs")

        languages = list(outputs.keys())

        lang1, lang2 = languages[0], languages[1]

        output1 = outputs[lang1]

        output2 = outputs[lang2]

        if normalize:

            output1 = self.normalize_cli_output(output1, lang1)

            output2 = self.normalize_cli_output(output2, lang2)

        diff = difflib.unified_diff(
            output1.splitlines(keepends=True),
            output2.splitlines(keepends=True),
            fromfile=f"{lang1}_output",
            tofile=f"{lang2}_output",
            lineterm="",
        )

        return "".join(diff)


def normalize_cli_output(output: str, language: str) -> str:
    """Convenience function to normalize CLI output.



    Args:

        output: Raw CLI output

        language: Source language



    Returns:

        Normalized output

    """

    comparator = CrossLanguageComparator()

    return comparator.normalize_cli_output(output, language)


def compare_command_outputs(
    outputs: Dict[str, str], command: List[str], comparison_type: str = "help"
) -> ComparisonResult:
    """Convenience function to compare CLI outputs.



    Args:

        outputs: Dictionary mapping language to CLI output

        command: Command that was executed

        comparison_type: Type of comparison ('help', 'version', 'error')



    Returns:

        ComparisonResult

    """

    comparator = CrossLanguageComparator()

    return comparator.compare_cli_outputs(outputs, command, comparison_type)


def generate_diff_report(outputs: Dict[str, str], normalize: bool = True) -> str:
    """Generate a diff report between CLI outputs.



    Args:

        outputs: Dictionary mapping language to output

        normalize: Whether to normalize before diffing



    Returns:

        Diff report string

    """

    comparator = CrossLanguageComparator()

    return comparator.generate_detailed_diff(outputs, normalize)


def compare_file_structures(
    file_structures: Dict[str, Dict[str, str]],
) -> ComparisonResult:
    """Compare generated file structures across languages.



    Args:

        file_structures: Dict mapping language -> filename -> file content



    Returns:

        ComparisonResult

    """

    comparator = CrossLanguageComparator()

    return comparator.compare_file_structures(file_structures)


# Additional utility functions


def extract_command_help_sections(help_text: str) -> Dict[str, List[str]]:
    """Extract help sections from CLI help text.



    Args:

        help_text: CLI help output



    Returns:

        Dictionary mapping section name to lines in that section

    """

    sections = {}

    current_section = None

    current_lines = []

    for line in help_text.split("\n"):

        line = line.strip()

        # Check if this line starts a new section

        if line.endswith(":") and not line.startswith(" "):

            # Save previous section if exists

            if current_section:

                sections[current_section] = current_lines

            # Start new section

            current_section = line[:-1]  # Remove the colon

            current_lines = []

        elif current_section:

            if line:  # Skip empty lines

                current_lines.append(line)

    # Save the last section

    if current_section:

        sections[current_section] = current_lines

    return sections


def validate_cross_language_consistency(
    test_results: Dict[str, Dict[str, Any]],
) -> Dict[str, ComparisonResult]:
    """Validate consistency across language implementations.



    Args:

        test_results: Nested dict of language -> test_name -> test_result



    Returns:

        Dictionary mapping test_name to ComparisonResult

    """

    comparisons = {}

    # Get all test names

    all_test_names = set()

    for lang_results in test_results.values():

        all_test_names.update(lang_results.keys())

    # Compare each test across languages

    for test_name in all_test_names:

        test_outputs = {}

        for language, lang_results in test_results.items():

            if test_name in lang_results:

                test_outputs[language] = str(lang_results[test_name])

        if len(test_outputs) > 1:

            comparisons[test_name] = compare_command_outputs(
                test_outputs, [test_name], "generic"
            )

    return comparisons
