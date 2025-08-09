#!/usr/bin/env python3
"""
Cross-Language Integration Testing Suite for Goobits CLI Framework

This module provides comprehensive integration testing across all supported languages
(Python, Node.js, TypeScript) to validate:
- Universal Template System integration
- Cross-language consistency
- Performance validation
- System integration health

Agent D - Phase 2 Task: Cross-Language Integration Testing
"""

import json
import os
import tempfile
import time
import yaml
import subprocess
import shutil
import statistics
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from unittest.mock import Mock, patch
import pytest

# Import framework components
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "goobits_cli"))

from goobits_cli.schemas import GoobitsConfigSchema
from goobits_cli.generators.python import PythonGenerator
from goobits_cli.generators.nodejs import NodeJSGenerator
from goobits_cli.generators.typescript import TypeScriptGenerator

# Performance validation framework imports
try:
    from goobits_cli.universal.performance.monitor import PerformanceMonitor
    from goobits_cli.universal.performance.optimizer import PerformanceOptimizer
    PERFORMANCE_FRAMEWORK_AVAILABLE = True
except ImportError as e:
    # print(f"Performance framework import failed: {e}")
    PERFORMANCE_FRAMEWORK_AVAILABLE = False
    PerformanceMonitor = None
    PerformanceOptimizer = None


class IntegrationTestResult:
    """Structured result for integration tests."""
    
    def __init__(self, test_name: str, language: str):
        self.test_name = test_name
        self.language = language
        self.success = False
        self.error_message = ""
        self.warnings = []
        self.performance_metrics = {}
        self.generated_files = []
        self.execution_time_ms = 0.0
        
    def to_dict(self) -> dict:
        """Convert result to dictionary for reporting."""
        return {
            "test_name": self.test_name,
            "language": self.language,
            "success": self.success,
            "error_message": self.error_message,
            "warnings": self.warnings,
            "performance_metrics": self.performance_metrics,
            "generated_files": self.generated_files,
            "execution_time_ms": self.execution_time_ms
        }


class CrossLanguageIntegrationTester:
    """Comprehensive cross-language integration testing framework."""
    
    def __init__(self):
        self.supported_languages = ["python", "nodejs", "typescript"]
        self.test_results = []
        self.performance_metrics = {}
        self.temp_dirs = []
        
        # Performance monitoring setup
        if PERFORMANCE_FRAMEWORK_AVAILABLE:
            self.performance_monitor = PerformanceMonitor()
            self.performance_optimizer = PerformanceOptimizer()
        else:
            self.performance_monitor = None
            self.performance_optimizer = None
    
    def cleanup(self):
        """Clean up temporary directories."""
        for temp_dir in self.temp_dirs:
            try:
                shutil.rmtree(temp_dir, ignore_errors=True)
            except Exception:
                pass
        self.temp_dirs.clear()
    
    def create_test_config(self, language: str, test_name: str = "integration_test") -> GoobitsConfigSchema:
        """Create a standardized test configuration for the specified language."""
        config_data = {
            "package_name": f"{test_name}-{language}",
            "command_name": f"{test_name.replace('-', '_')}_{language}",
            "display_name": f"{test_name.title()} {language.title()} CLI",
            "description": f"Integration test CLI for {language}",
            "language": language,
            
            "python": {
                "minimum_version": "3.8"
            },
            
            "dependencies": {
                "required": ["pipx"] if language == "python" else ["node", "npm"],
                "optional": []
            },
            
            "installation": {
                "pypi_name": f"{test_name}-{language}",
                "development_path": "."
            },
            
            "shell_integration": {
                "enabled": False,
                "alias": f"{test_name.replace('-', '_')}_{language}"
            },
            
            "validation": {
                "check_api_keys": False,
                "check_disk_space": True,
                "minimum_disk_space_mb": 100
            },
            
            "messages": {
                "install_success": "Installation completed successfully!",
                "install_dev_success": "Development installation completed successfully!",
                "upgrade_success": "Upgrade completed successfully!",
                "uninstall_success": "Uninstall completed successfully!"
            },
            
            "cli": {
                "name": f"{test_name}_{language}",
                "tagline": f"Integration test CLI for {language}",
                "commands": {
                    "hello": {
                        "desc": "Say hello to someone",
                        "is_default": True,
                        "args": [
                            {
                                "name": "name",
                                "desc": "Name to greet",
                                "required": False
                            }
                        ],
                        "options": [
                            {
                                "name": "greeting",
                                "short": "g",
                                "desc": "Custom greeting message",
                                "default": "Hello"
                            },
                            {
                                "name": "uppercase",
                                "short": "u",
                                "type": "flag",
                                "desc": "Convert output to uppercase"
                            }
                        ]
                    },
                    "count": {
                        "desc": "Count items or words",
                        "args": [
                            {
                                "name": "items",
                                "desc": "Items to count",
                                "nargs": "*"
                            }
                        ],
                        "options": [
                            {
                                "name": "type",
                                "short": "t",
                                "choices": ["words", "chars", "lines"],
                                "default": "words",
                                "desc": "Type of counting to perform"
                            }
                        ]
                    },
                    "config": {
                        "desc": "Manage configuration",
                        "subcommands": {
                            "show": {
                                "desc": "Show current configuration"
                            },
                            "set": {
                                "desc": "Set configuration value",
                                "args": [
                                    {
                                        "name": "key",
                                        "desc": "Configuration key"
                                    },
                                    {
                                        "name": "value",
                                        "desc": "Configuration value"
                                    }
                                ]
                            }
                        }
                    }
                }
            }
        }
        
        return GoobitsConfigSchema(**config_data)
    
    def test_generator_instantiation(self) -> List[IntegrationTestResult]:
        """Test that all generators can be instantiated successfully."""
        results = []
        
        for language in self.supported_languages:
            result = IntegrationTestResult("generator_instantiation", language)
            start_time = time.time()
            
            try:
                if language == "python":
                    generator = PythonGenerator(use_universal_templates=False)
                    assert generator is not None
                    assert hasattr(generator, 'generate')
                    result.warnings.append("Legacy mode - universal templates disabled")
                    
                    # Test universal template instantiation
                    try:
                        universal_generator = PythonGenerator(use_universal_templates=True)
                        if universal_generator.use_universal_templates:
                            result.warnings.append("Universal templates available and enabled")
                        else:
                            result.warnings.append("Universal templates fell back to legacy mode")
                    except Exception as e:
                        result.warnings.append(f"Universal templates not available: {e}")
                
                elif language == "nodejs":
                    generator = NodeJSGenerator(use_universal_templates=False)
                    assert generator is not None
                    assert hasattr(generator, 'generate')
                    result.warnings.append("Legacy mode - universal templates disabled")
                    
                    # Test universal template instantiation
                    try:
                        universal_generator = NodeJSGenerator(use_universal_templates=True)
                        if universal_generator.use_universal_templates:
                            result.warnings.append("Universal templates available and enabled")
                        else:
                            result.warnings.append("Universal templates fell back to legacy mode")
                    except Exception as e:
                        result.warnings.append(f"Universal templates not available: {e}")
                
                elif language == "typescript":
                    generator = TypeScriptGenerator(use_universal_templates=False)
                    assert generator is not None
                    assert hasattr(generator, 'generate')
                    result.warnings.append("Legacy mode - universal templates disabled")
                    
                    # Test universal template instantiation
                    try:
                        universal_generator = TypeScriptGenerator(use_universal_templates=True)
                        if universal_generator.use_universal_templates:
                            result.warnings.append("Universal templates available and enabled")
                        else:
                            result.warnings.append("Universal templates fell back to legacy mode")
                    except Exception as e:
                        result.warnings.append(f"Universal templates not available: {e}")
                
                result.success = True
                
            except Exception as e:
                result.error_message = f"Failed to instantiate {language} generator: {str(e)}"
                result.success = False
            
            result.execution_time_ms = (time.time() - start_time) * 1000
            results.append(result)
        
        return results
    
    def test_universal_template_integration(self) -> List[IntegrationTestResult]:
        """Test Universal Template System integration across all languages."""
        results = []
        
        for language in self.supported_languages:
            result = IntegrationTestResult("universal_template_integration", language)
            start_time = time.time()
            
            try:
                config = self.create_test_config(language, "universal_test")
                
                # Test with universal templates enabled
                if language == "python":
                    generator = PythonGenerator(use_universal_templates=True)
                elif language == "nodejs":
                    generator = NodeJSGenerator(use_universal_templates=True)
                elif language == "typescript":
                    generator = TypeScriptGenerator(use_universal_templates=True)
                
                # Generate CLI code
                generated_code = generator.generate(config, f"test_{language}.yaml", "1.0.0")
                
                # Validate generation
                if not generated_code or len(generated_code.strip()) < 100:
                    result.error_message = f"Generated code too short for {language}: {len(generated_code)} characters"
                    result.success = False
                else:
                    result.success = True
                    
                    # Check if universal templates were actually used
                    if hasattr(generator, 'use_universal_templates') and generator.use_universal_templates:
                        result.warnings.append("Universal templates were used successfully")
                    else:
                        result.warnings.append("Fell back to legacy templates")
                    
                    # Verify language-specific characteristics
                    if language == "python" and "typer" in generated_code.lower():
                        result.warnings.append("Generated Python code uses Typer framework")
                    elif language == "nodejs" and "commander" in generated_code.lower():
                        result.warnings.append("Generated Node.js code uses Commander framework")  
                    elif language == "typescript" and "commander" in generated_code.lower():
                        result.warnings.append("Generated TypeScript code uses Commander framework")
                
            except Exception as e:
                result.error_message = f"Universal template integration failed for {language}: {str(e)}"
                result.success = False
            
            result.execution_time_ms = (time.time() - start_time) * 1000
            results.append(result)
        
        return results
    
    def test_multi_file_generation(self) -> List[IntegrationTestResult]:
        """Test multi-file generation capabilities across languages."""
        results = []
        
        for language in self.supported_languages:
            result = IntegrationTestResult("multi_file_generation", language)
            start_time = time.time()
            
            try:
                config = self.create_test_config(language, "multi_file_test")
                
                if language == "python":
                    generator = PythonGenerator(use_universal_templates=False)
                elif language == "nodejs":
                    generator = NodeJSGenerator(use_universal_templates=False)
                elif language == "typescript":
                    generator = TypeScriptGenerator(use_universal_templates=False)
                
                # Test multi-file generation
                all_files = generator.generate_all_files(config, f"test_{language}.yaml", "1.0.0")
                
                if not all_files or len(all_files) < 2:
                    result.error_message = f"Multi-file generation failed for {language}: only {len(all_files)} files generated"
                    result.success = False
                else:
                    result.success = True
                    result.generated_files = list(all_files.keys())
                    result.warnings.append(f"Generated {len(all_files)} files: {', '.join(all_files.keys())}")
                    
                    # Validate file contents
                    empty_files = [name for name, content in all_files.items() if not content or len(content.strip()) < 10]
                    if empty_files:
                        result.warnings.append(f"Warning: Empty or very small files: {', '.join(empty_files)}")
                
            except Exception as e:
                result.error_message = f"Multi-file generation failed for {language}: {str(e)}"
                result.success = False
            
            result.execution_time_ms = (time.time() - start_time) * 1000
            results.append(result)
        
        return results
    
    def test_performance_integration(self) -> List[IntegrationTestResult]:
        """Test performance framework integration with generators."""
        results = []
        
        # Alternative performance testing when full framework isn't available
        if not PERFORMANCE_FRAMEWORK_AVAILABLE:
            return self._test_basic_performance_metrics()
        
        for language in self.supported_languages:
            result = IntegrationTestResult("performance_integration", language)
            start_time = time.time()
            
            try:
                config = self.create_test_config(language, "performance_test")
                
                # Start performance monitoring
                monitor_session = self.performance_monitor.start_session(f"{language}_generation")
                
                if language == "python":
                    generator = PythonGenerator(use_universal_templates=True)
                elif language == "nodejs":
                    generator = NodeJSGenerator(use_universal_templates=True)
                elif language == "typescript":
                    generator = TypeScriptGenerator(use_universal_templates=True)
                
                # Generate with performance monitoring
                generation_start = time.time()
                generated_code = generator.generate(config, f"perf_test_{language}.yaml", "1.0.0")
                generation_time = (time.time() - generation_start) * 1000
                
                # Stop monitoring and collect metrics
                metrics = self.performance_monitor.end_session(monitor_session)
                
                # Validate performance requirements (Agent B's <100ms startup requirement)
                if generation_time < 100:
                    result.warnings.append(f"Generation time {generation_time:.2f}ms meets <100ms requirement")
                else:
                    result.warnings.append(f"Generation time {generation_time:.2f}ms exceeds 100ms target")
                
                result.performance_metrics = {
                    "generation_time_ms": generation_time,
                    "memory_usage_mb": metrics.get("memory_peak_mb", 0),
                    "cpu_usage_percent": metrics.get("cpu_avg_percent", 0)
                }
                
                result.success = True
                
            except Exception as e:
                result.error_message = f"Performance integration failed for {language}: {str(e)}"
                result.success = False
            
            result.execution_time_ms = (time.time() - start_time) * 1000
            results.append(result)
        
        return results
    
    def _test_basic_performance_metrics(self) -> List[IntegrationTestResult]:
        """Basic performance testing when full framework isn't available."""
        results = []
        
        for language in self.supported_languages:
            result = IntegrationTestResult("performance_integration", language)
            start_time = time.time()
            
            try:
                config = self.create_test_config(language, "performance_test")
                
                # Basic performance test - measure generation time
                generation_start = time.time()
                
                if language == "python":
                    generator = PythonGenerator(use_universal_templates=False)
                elif language == "nodejs":
                    generator = NodeJSGenerator(use_universal_templates=False)
                elif language == "typescript":
                    generator = TypeScriptGenerator(use_universal_templates=False)
                
                # Generate CLI and measure time
                generated_code = generator.generate(config, f"perf_test_{language}.yaml", "1.0.0")
                generation_time = (time.time() - generation_start) * 1000
                
                # Basic validation
                if not generated_code or len(generated_code.strip()) < 50:
                    result.error_message = f"Performance test failed - no code generated for {language}"
                    result.success = False
                else:
                    result.success = True
                    result.performance_metrics = {
                        "generation_time_ms": generation_time,
                        "memory_usage_mb": 0,  # Not measuring without framework
                        "cpu_usage_percent": 0
                    }
                    
                    # Validate performance requirements (Agent B's <100ms startup requirement)
                    if generation_time < 100:
                        result.warnings.append(f"Generation time {generation_time:.2f}ms meets <100ms requirement")
                    else:
                        result.warnings.append(f"Generation time {generation_time:.2f}ms exceeds 100ms target")
                
            except Exception as e:
                result.error_message = f"Basic performance test failed for {language}: {str(e)}"
                result.success = False
            
            result.execution_time_ms = (time.time() - start_time) * 1000
            results.append(result)
        
        return results
    
    def test_cross_language_consistency(self) -> List[IntegrationTestResult]:
        """Test that equivalent configurations generate consistent functionality across languages."""
        results = []
        
        # Generate same config for all languages
        base_config_data = {
            "package_name": "consistency-test",
            "command_name": "consistency_test", 
            "display_name": "Consistency Test CLI",
            "description": "Test CLI for cross-language consistency",
            
            "python": {"minimum_version": "3.8"},
            "dependencies": {"required": [], "optional": []},
            "installation": {"pypi_name": "consistency-test", "development_path": "."},
            
            "shell_integration": {"enabled": False, "alias": "consistency_test"},
            "validation": {"check_api_keys": False, "check_disk_space": True, "minimum_disk_space_mb": 100},
            "messages": {
                "install_success": "Installation completed successfully!",
                "install_dev_success": "Development installation completed successfully!",
                "upgrade_success": "Upgrade completed successfully!",
                "uninstall_success": "Uninstall completed successfully!"
            },
            
            "cli": {
                "name": "consistency_test",
                "tagline": "Cross-language consistency test",
                "commands": {
                    "test": {
                        "desc": "Run consistency test",
                        "is_default": True,
                        "args": [{"name": "input", "desc": "Test input", "required": False}],
                        "options": [
                            {"name": "format", "short": "f", "choices": ["json", "text"], "default": "text", "desc": "Output format"},
                            {"name": "verbose", "short": "v", "type": "flag", "desc": "Verbose output"}
                        ]
                    }
                }
            }
        }
        
        generated_outputs = {}
        
        for language in self.supported_languages:
            result = IntegrationTestResult("cross_language_consistency", language)
            start_time = time.time()
            
            try:
                # Create language-specific config
                config_data = base_config_data.copy()
                config_data["language"] = language
                config = GoobitsConfigSchema(**config_data)
                
                # Generate CLI
                if language == "python":
                    generator = PythonGenerator(use_universal_templates=False)
                elif language == "nodejs":
                    generator = NodeJSGenerator(use_universal_templates=False)
                elif language == "typescript":
                    generator = TypeScriptGenerator(use_universal_templates=False)
                
                generated_code = generator.generate(config, f"consistency_{language}.yaml", "1.0.0")
                generated_outputs[language] = generated_code
                
                # Basic validation
                if not generated_code or len(generated_code.strip()) < 50:
                    result.error_message = f"Generated code too short for {language}"
                    result.success = False
                else:
                    result.success = True
                    
                    # Check for expected command structure patterns
                    code_lower = generated_code.lower()
                    if "test" not in code_lower:
                        result.warnings.append("'test' command not found in generated code")
                    if "format" not in code_lower and "fmt" not in code_lower:
                        result.warnings.append("'format' option not found in generated code")
                    if "verbose" not in code_lower:
                        result.warnings.append("'verbose' option not found in generated code")
                
            except Exception as e:
                result.error_message = f"Consistency test failed for {language}: {str(e)}"
                result.success = False
            
            result.execution_time_ms = (time.time() - start_time) * 1000
            results.append(result)
        
        # Cross-language comparison
        comparison_result = IntegrationTestResult("cross_language_consistency", "comparison")
        start_time = time.time()
        
        try:
            successful_languages = [lang for lang in self.supported_languages 
                                  if lang in generated_outputs and generated_outputs[lang]]
            
            if len(successful_languages) < 2:
                comparison_result.error_message = "Not enough successful generations for comparison"
                comparison_result.success = False
            else:
                # Analyze consistency
                code_lengths = [len(generated_outputs[lang]) for lang in successful_languages]
                avg_length = statistics.mean(code_lengths)
                length_variance = statistics.variance(code_lengths) if len(code_lengths) > 1 else 0
                
                comparison_result.performance_metrics = {
                    "languages_compared": len(successful_languages),
                    "avg_code_length": avg_length,
                    "length_variance": length_variance,
                    "length_coefficient_variation": (length_variance ** 0.5) / avg_length if avg_length > 0 else 0
                }
                
                if comparison_result.performance_metrics["length_coefficient_variation"] < 0.5:
                    comparison_result.warnings.append("Code lengths are reasonably consistent across languages")
                else:
                    comparison_result.warnings.append("Significant code length variation across languages")
                
                comparison_result.success = True
        
        except Exception as e:
            comparison_result.error_message = f"Cross-language comparison failed: {str(e)}"
            comparison_result.success = False
        
        comparison_result.execution_time_ms = (time.time() - start_time) * 1000
        results.append(comparison_result)
        
        return results
    
    def test_regression_validation(self) -> List[IntegrationTestResult]:
        """Test that existing functionality still works after Phase 1 integrations."""
        results = []
        
        for language in self.supported_languages:
            result = IntegrationTestResult("regression_validation", language)
            start_time = time.time()
            
            try:
                config = self.create_test_config(language, "regression_test")
                
                # Test legacy mode (should always work)
                if language == "python":
                    legacy_generator = PythonGenerator(use_universal_templates=False)
                elif language == "nodejs":
                    legacy_generator = NodeJSGenerator(use_universal_templates=False)
                elif language == "typescript":
                    legacy_generator = TypeScriptGenerator(use_universal_templates=False)
                
                legacy_code = legacy_generator.generate(config, f"regression_{language}.yaml", "1.0.0")
                
                if not legacy_code or len(legacy_code.strip()) < 100:
                    result.error_message = f"Legacy mode regression failure for {language}: generated {len(legacy_code)} characters"
                    result.success = False
                else:
                    result.success = True
                    result.warnings.append(f"Legacy mode works: {len(legacy_code)} characters generated")
                    
                    # Test key functionality patterns
                    code_lower = legacy_code.lower()
                    expected_patterns = {
                        "python": ["typer", "def", "import"],
                        "nodejs": ["commander", "program", "require"],
                        "typescript": ["commander", "program", "import"]
                    }
                    
                    missing_patterns = []
                    for pattern in expected_patterns.get(language, []):
                        if pattern not in code_lower:
                            missing_patterns.append(pattern)
                    
                    if missing_patterns:
                        result.warnings.append(f"Missing expected patterns: {', '.join(missing_patterns)}")
                    else:
                        result.warnings.append(f"All expected patterns found for {language}")
                
            except Exception as e:
                result.error_message = f"Regression validation failed for {language}: {str(e)}"
                result.success = False
            
            result.execution_time_ms = (time.time() - start_time) * 1000
            results.append(result)
        
        return results
    
    def run_comprehensive_integration_tests(self) -> Dict[str, Any]:
        """Run all integration tests and compile results."""
        print("🚀 Starting comprehensive cross-language integration testing...")
        
        all_results = []
        
        # Test 1: Generator Instantiation
        print("\n1️⃣ Testing generator instantiation...")
        instantiation_results = self.test_generator_instantiation()
        all_results.extend(instantiation_results)
        
        # Test 2: Universal Template Integration
        print("\n2️⃣ Testing Universal Template System integration...")
        universal_results = self.test_universal_template_integration()
        all_results.extend(universal_results)
        
        # Test 3: Multi-file Generation
        print("\n3️⃣ Testing multi-file generation...")
        multi_file_results = self.test_multi_file_generation()
        all_results.extend(multi_file_results)
        
        # Test 4: Performance Integration (using Agent B's framework)
        print("\n4️⃣ Testing performance framework integration...")
        performance_results = self.test_performance_integration()
        all_results.extend(performance_results)
        
        # Test 5: Cross-language Consistency
        print("\n5️⃣ Testing cross-language consistency...")
        consistency_results = self.test_cross_language_consistency()
        all_results.extend(consistency_results)
        
        # Test 6: Regression Validation
        print("\n6️⃣ Testing regression validation...")
        regression_results = self.test_regression_validation()
        all_results.extend(regression_results)
        
        # Compile comprehensive report
        return self._compile_integration_report(all_results)
    
    def _compile_integration_report(self, results: List[IntegrationTestResult]) -> Dict[str, Any]:
        """Compile comprehensive integration test report."""
        
        # Group results by test type and language
        test_groups = {}
        language_stats = {lang: {"passed": 0, "failed": 0, "warnings": 0} for lang in self.supported_languages}
        language_stats["comparison"] = {"passed": 0, "failed": 0, "warnings": 0}  # For cross-language tests
        
        for result in results:
            test_type = result.test_name
            if test_type not in test_groups:
                test_groups[test_type] = []
            test_groups[test_type].append(result)
            
            # Update language statistics
            lang = result.language
            if result.success:
                language_stats[lang]["passed"] += 1
            else:
                language_stats[lang]["failed"] += 1
            if result.warnings:
                language_stats[lang]["warnings"] += len(result.warnings)
        
        # Calculate overall statistics
        total_tests = len(results)
        passed_tests = sum(1 for r in results if r.success)
        failed_tests = total_tests - passed_tests
        total_warnings = sum(len(r.warnings) for r in results)
        
        # Performance analysis
        performance_results = [r for r in results if "performance" in r.test_name]
        avg_generation_time = 0
        if performance_results:
            generation_times = [r.performance_metrics.get("generation_time_ms", 0) for r in performance_results]
            valid_times = [t for t in generation_times if t > 0]
            avg_generation_time = statistics.mean(valid_times) if valid_times else 0
        
        # System health score calculation
        health_score = self._calculate_system_health_score(results)
        
        # Production readiness assessment
        production_ready, readiness_issues = self._assess_production_readiness(results)
        
        report = {
            "summary": {
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": failed_tests,
                "success_rate": (passed_tests / total_tests * 100) if total_tests > 0 else 0,
                "total_warnings": total_warnings,
                "avg_generation_time_ms": avg_generation_time,
                "system_health_score": health_score,
                "production_ready": production_ready
            },
            
            "language_statistics": language_stats,
            
            "test_results_by_type": {
                test_type: [r.to_dict() for r in group_results]
                for test_type, group_results in test_groups.items()
            },
            
            "performance_analysis": {
                "performance_framework_available": PERFORMANCE_FRAMEWORK_AVAILABLE,
                "meets_100ms_requirement": avg_generation_time < 100 if avg_generation_time > 0 else "unknown",
                "avg_generation_time_ms": avg_generation_time,
                "performance_results": [r.to_dict() for r in performance_results]
            },
            
            "integration_health": {
                "universal_templates_working": any(
                    "universal templates were used successfully" in " ".join(r.warnings).lower()
                    for r in results if r.test_name == "universal_template_integration"
                ),
                "multi_file_generation_working": all(
                    r.success for r in results if r.test_name == "multi_file_generation"
                ),
                "cross_language_consistency": all(
                    r.success for r in results if r.test_name == "cross_language_consistency"
                ),
                "regression_tests_passed": all(
                    r.success for r in results if r.test_name == "regression_validation"
                )
            },
            
            "production_readiness": {
                "ready": production_ready,
                "blocking_issues": readiness_issues,
                "recommendations": self._get_recommendations(results)
            },
            
            "detailed_results": [r.to_dict() for r in results]
        }
        
        return report
    
    def _calculate_system_health_score(self, results: List[IntegrationTestResult]) -> float:
        """Calculate overall system health score (0-100)."""
        if not results:
            return 0.0
        
        # Base score from test success rate
        passed_tests = sum(1 for r in results if r.success)
        base_score = (passed_tests / len(results)) * 70  # 70% weight for basic functionality
        
        # Bonus points for advanced features
        bonus_points = 0
        
        # Universal templates working (+10 points)
        universal_working = any(
            "universal templates were used successfully" in " ".join(r.warnings).lower()
            for r in results if r.test_name == "universal_template_integration"
        )
        if universal_working:
            bonus_points += 10
        
        # Performance requirements met (+10 points)
        performance_results = [r for r in results if "performance" in r.test_name]
        if performance_results:
            avg_gen_time = statistics.mean([
                r.performance_metrics.get("generation_time_ms", 1000) 
                for r in performance_results
            ])
            if avg_gen_time < 100:
                bonus_points += 10
        
        # Cross-language consistency (+10 points)
        consistency_passed = all(
            r.success for r in results if r.test_name == "cross_language_consistency"
        )
        if consistency_passed:
            bonus_points += 10
        
        return min(100.0, base_score + bonus_points)
    
    def _assess_production_readiness(self, results: List[IntegrationTestResult]) -> Tuple[bool, List[str]]:
        """Assess if the system is ready for production."""
        blocking_issues = []
        
        # Critical requirements
        failed_core_tests = [r for r in results if not r.success and r.test_name in [
            "generator_instantiation", "regression_validation"
        ]]
        if failed_core_tests:
            blocking_issues.append(f"Core functionality failures: {len(failed_core_tests)} tests failed")
        
        # Performance requirements
        performance_results = [r for r in results if "performance" in r.test_name and r.success]
        if performance_results:
            avg_gen_time = statistics.mean([
                r.performance_metrics.get("generation_time_ms", 1000) 
                for r in performance_results
            ])
            if avg_gen_time > 200:  # More lenient than 100ms for production assessment
                blocking_issues.append(f"Performance requirement not met: {avg_gen_time:.1f}ms > 200ms")
        
        # Language support
        supported_langs = set()
        for result in results:
            if result.success and result.language in self.supported_languages:
                supported_langs.add(result.language)
        
        if len(supported_langs) < len(self.supported_languages):
            missing_langs = set(self.supported_languages) - supported_langs
            blocking_issues.append(f"Incomplete language support: {', '.join(missing_langs)} not working")
        
        return len(blocking_issues) == 0, blocking_issues
    
    def _get_recommendations(self, results: List[IntegrationTestResult]) -> List[str]:
        """Generate recommendations based on test results."""
        recommendations = []
        
        # Check for universal template issues
        universal_results = [r for r in results if r.test_name == "universal_template_integration"]
        if universal_results and not all(r.success for r in universal_results):
            recommendations.append("Fix Universal Template System integration issues")
        
        # Performance recommendations
        performance_results = [r for r in results if "performance" in r.test_name and r.success]
        if performance_results:
            avg_gen_time = statistics.mean([
                r.performance_metrics.get("generation_time_ms", 0) 
                for r in performance_results
            ])
            if avg_gen_time > 100:
                recommendations.append(f"Optimize generation performance (current: {avg_gen_time:.1f}ms)")
        
        # Warning accumulation
        total_warnings = sum(len(r.warnings) for r in results)
        if total_warnings > len(results) * 2:  # More than 2 warnings per test on average
            recommendations.append("Address accumulated warnings to improve system stability")
        
        # Cross-language consistency
        consistency_results = [r for r in results if r.test_name == "cross_language_consistency"]
        if consistency_results:
            comparison_result = next((r for r in consistency_results if r.language == "comparison"), None)
            if comparison_result and comparison_result.success:
                cv = comparison_result.performance_metrics.get("length_coefficient_variation", 0)
                if cv > 0.5:
                    recommendations.append("Improve cross-language code generation consistency")
        
        if not recommendations:
            recommendations.append("System is functioning well - consider adding more integration tests")
        
        return recommendations


class TestCrossLanguageIntegration:
    """Pytest test class for cross-language integration testing."""
    
    @classmethod
    def setup_class(cls):
        """Set up test class."""
        cls.integration_tester = CrossLanguageIntegrationTester()
        
    @classmethod
    def teardown_class(cls):
        """Clean up test class."""
        cls.integration_tester.cleanup()
    
    def test_all_generators_instantiate(self):
        """Test that all generators can be instantiated."""
        results = self.integration_tester.test_generator_instantiation()
        
        # All generators should instantiate successfully
        failed_results = [r for r in results if not r.success]
        assert not failed_results, f"Generator instantiation failed: {[r.error_message for r in failed_results]}"
    
    def test_universal_templates_integration(self):
        """Test Universal Template System integration."""
        results = self.integration_tester.test_universal_template_integration()
        
        # At least some generators should work (allow graceful fallback)
        successful_results = [r for r in results if r.success]
        assert len(successful_results) >= 1, "No generators worked with universal templates"
    
    def test_multi_file_generation(self):
        """Test multi-file generation across languages."""
        results = self.integration_tester.test_multi_file_generation()
        
        # All languages should support multi-file generation
        failed_results = [r for r in results if not r.success]
        assert not failed_results, f"Multi-file generation failed: {[r.error_message for r in failed_results]}"
    
    def test_cross_language_consistency(self):
        """Test cross-language consistency."""
        results = self.integration_tester.test_cross_language_consistency()
        
        # All individual language tests should pass
        language_results = [r for r in results if r.language != "comparison"]
        failed_results = [r for r in language_results if not r.success]
        assert not failed_results, f"Cross-language consistency failed: {[r.error_message for r in failed_results]}"
    
    def test_regression_validation(self):
        """Test that existing functionality still works."""
        results = self.integration_tester.test_regression_validation()
        
        # All regression tests must pass
        failed_results = [r for r in results if not r.success]
        assert not failed_results, f"Regression validation failed: {[r.error_message for r in failed_results]}"
    
    def test_system_integration_health(self):
        """Test overall system integration health."""
        report = self.integration_tester.run_comprehensive_integration_tests()
        
        # System health score should be reasonable
        health_score = report["summary"]["system_health_score"]
        assert health_score >= 70.0, f"System health score too low: {health_score}%"
        
        # Success rate should be high
        success_rate = report["summary"]["success_rate"]
        assert success_rate >= 80.0, f"Test success rate too low: {success_rate}%"


if __name__ == "__main__":
    # Run integration tests standalone
    tester = CrossLanguageIntegrationTester()
    try:
        report = tester.run_comprehensive_integration_tests()
        
        print("\n" + "="*80)
        print("🏁 CROSS-LANGUAGE INTEGRATION TEST REPORT")
        print("="*80)
        
        print(f"\n📊 SUMMARY:")
        print(f"   Total Tests: {report['summary']['total_tests']}")
        print(f"   Passed: {report['summary']['passed_tests']}")
        print(f"   Failed: {report['summary']['failed_tests']}")
        print(f"   Success Rate: {report['summary']['success_rate']:.1f}%")
        print(f"   System Health Score: {report['summary']['system_health_score']:.1f}/100")
        print(f"   Production Ready: {'✅' if report['summary']['production_ready'] else '❌'}")
        
        if report['summary']['avg_generation_time_ms'] > 0:
            print(f"   Avg Generation Time: {report['summary']['avg_generation_time_ms']:.1f}ms")
        
        print(f"\n🎯 INTEGRATION HEALTH:")
        health = report['integration_health']
        print(f"   Universal Templates: {'✅' if health['universal_templates_working'] else '❌'}")
        print(f"   Multi-file Generation: {'✅' if health['multi_file_generation_working'] else '❌'}")
        print(f"   Cross-language Consistency: {'✅' if health['cross_language_consistency'] else '❌'}")
        print(f"   Regression Tests: {'✅' if health['regression_tests_passed'] else '❌'}")
        
        if not report['summary']['production_ready']:
            print(f"\n🚫 BLOCKING ISSUES:")
            for issue in report['production_readiness']['blocking_issues']:
                print(f"   - {issue}")
        
        print(f"\n💡 RECOMMENDATIONS:")
        for rec in report['production_readiness']['recommendations']:
            print(f"   - {rec}")
        
        # Save detailed report
        report_path = Path(__file__).parent / "integration_test_report.json"
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"\n📄 Detailed report saved to: {report_path}")
        
    finally:
        tester.cleanup()