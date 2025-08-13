#!/usr/bin/env python3
"""
Phase 4E - Final Integration Testing and Comprehensive Benchmarking Suite

This module provides comprehensive end-to-end testing and benchmarking for all
Phase 4 Advanced Features across all supported languages (Python, Node.js, TypeScript, Rust).

Features tested:
- Interactive mode functionality
- Dynamic completion system
- Plugin installation and management
- Performance optimization
- Cross-language feature parity
- Memory usage and startup time benchmarking
"""

import os
import sys
import time
import json
import subprocess
import tempfile
import shutil
import threading
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from contextlib import contextmanager

import pytest
import yaml
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, TaskID

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import subprocess
from goobits_cli.schemas import GoobitsConfigSchema


@dataclass
class BenchmarkResult:
    """Benchmark result data structure"""
    language: str
    test_name: str
    startup_time_ms: float
    memory_usage_mb: float
    completion_time_ms: float
    feature_count: int
    success: bool
    error_message: Optional[str] = None


@dataclass
class IntegrationTestResult:
    """Integration test result data structure"""
    language: str
    feature: str
    test_case: str
    success: bool
    execution_time_ms: float
    output: Optional[str] = None
    error_message: Optional[str] = None


class Phase4ETestSuite:
    """Main test suite for Phase 4E integration testing and benchmarking"""
    
    def __init__(self, test_dir: Optional[Path] = None):
        self.console = Console()
        self.test_dir = test_dir or Path(tempfile.mkdtemp(prefix="phase4e_test_"))
        self.benchmark_results: List[BenchmarkResult] = []
        self.integration_results: List[IntegrationTestResult] = []
        self.languages = ["python", "nodejs", "typescript", "rust"]
        
        # Performance thresholds
        self.STARTUP_TIME_THRESHOLD_MS = 100
        self.MEMORY_USAGE_THRESHOLD_MB = 50
        self.COMPLETION_TIME_THRESHOLD_MS = 50
        
    def setup_test_environment(self):
        """Setup isolated test environment for each language"""
        self.console.print("[bold blue]Setting up Phase 4E test environment...[/bold blue]")
        
        # Create test directory structure
        for lang in self.languages:
            lang_dir = self.test_dir / f"test_{lang}"
            lang_dir.mkdir(parents=True, exist_ok=True)
            
            # Create test configurations for each language
            self._create_test_config(lang, lang_dir)
            
    def _create_test_config(self, language: str, output_dir: Path):
        """Create comprehensive test configuration for each language"""
        config = {
            "name": f"phase4e-test-{language}",
            "version": "2.0.0",
            "description": f"Phase 4E comprehensive test CLI for {language}",
            "language": language,
            "setup": {
                "python_version": ">=3.8",
                "dependencies": {
                    "required": ["click>=8.0", "rich>=12.0"],
                    "optional": ["pytest", "pyyaml"]
                }
            },
            "installation": {
                "pypi_name": f"phase4e-test-{language}",
                "development_path": str(output_dir),
                "extras": {
                    f"{language}": ["dev", "test"] if language == "python" else [],
                    "apt": ["git"] if language in ["rust", "nodejs"] else []
                }
            },
            "cli": {
                "name": f"phase4e-{language}",
                "help": "Phase 4E comprehensive test CLI with all advanced features",
                "version_flag": True,
                "config_file": f".phase4e-{language}.yaml",
                "plugins": {
                    "enabled": True,
                    "directory": "plugins",
                    "marketplace_url": "https://github.com/goobits/plugins"
                },
                "interactive": {
                    "enabled": True,
                    "prompt": f"phase4e-{language}> ",
                    "history_file": f".phase4e-{language}_history"
                },
                "completion": {
                    "enabled": True,
                    "dynamic": True,
                    "cache_duration": 300
                },
                "performance": {
                    "lazy_loading": True,
                    "caching": True,
                    "startup_optimization": True
                },
                "commands": [
                    {
                        "name": "test-basic",
                        "help": "Basic command test",
                        "arguments": [
                            {"name": "input", "help": "Input parameter", "required": True}
                        ]
                    },
                    {
                        "name": "test-interactive",
                        "help": "Interactive mode test command",
                        "options": [
                            {"name": "--mode", "help": "Interactive mode", "default": "repl"}
                        ]
                    },
                    {
                        "name": "test-completion",
                        "help": "Dynamic completion test",
                        "options": [
                            {"name": "--complete", "help": "Test completion", "choices": ["bash", "zsh", "fish"]}
                        ]
                    },
                    {
                        "name": "plugin",
                        "help": "Plugin management",
                        "subcommands": [
                            {
                                "name": "install",
                                "help": "Install plugin",
                                "arguments": [
                                    {"name": "name", "help": "Plugin name", "required": True}
                                ]
                            },
                            {
                                "name": "list",
                                "help": "List installed plugins"
                            },
                            {
                                "name": "remove",
                                "help": "Remove plugin",
                                "arguments": [
                                    {"name": "name", "help": "Plugin name", "required": True}
                                ]
                            }
                        ]
                    },
                    {
                        "name": "benchmark",
                        "help": "Performance benchmark test",
                        "options": [
                            {"name": "--iterations", "help": "Number of iterations", "type": "int", "default": 100}
                        ]
                    }
                ]
            }
        }
        
        # Save configuration
        config_file = output_dir / "goobits.yaml"
        with open(config_file, 'w') as f:
            yaml.dump(config, f, default_flow_style=False)
            
        return config_file
    
    @contextmanager
    def measure_time(self):
        """Context manager for measuring execution time"""
        start = time.perf_counter()
        yield lambda: (time.perf_counter() - start) * 1000  # Return ms
        
    def measure_memory_usage(self, process: subprocess.Popen) -> float:
        """Measure memory usage of a process in MB"""
        try:
            import psutil
            p = psutil.Process(process.pid)
            return p.memory_info().rss / (1024 * 1024)  # Convert to MB
        except ImportError:
            # Fallback if psutil not available
            return 0.0
        except:
            return 0.0
    
    def test_cli_generation(self, language: str) -> bool:
        """Test CLI generation for a specific language"""
        lang_dir = self.test_dir / f"test_{language}"
        config_file = lang_dir / "goobits.yaml"
        
        try:
            with self.measure_time() as get_time:
                # Build CLI using subprocess to call the goobits build command
                result = subprocess.run([
                    sys.executable, "-m", "goobits_cli.main", "build", 
                    str(config_file), "--output-dir", str(lang_dir)
                ], capture_output=True, text=True, timeout=30)
            
            generation_time = get_time()
            success = result.returncode == 0
            if success:
                self.console.print(f"✅ {language} CLI generated in {generation_time:.2f}ms")
            else:
                self.console.print(f"❌ {language} CLI generation failed: {result.stderr}")
            return success
            
        except Exception as e:
            self.console.print(f"❌ {language} CLI generation failed: {e}")
            return False
    
    def test_cli_startup_time(self, language: str) -> BenchmarkResult:
        """Measure CLI startup time and basic functionality"""
        lang_dir = self.test_dir / f"test_{language}"
        
        if language == "python":
            cmd = ["python", str(lang_dir / "cli.py"), "--version"]
        elif language == "nodejs":
            cmd = ["node", str(lang_dir / "cli.js"), "--version"]
        elif language == "typescript":
            cmd = ["node", str(lang_dir / "cli.js"), "--version"]  # Compiled
        elif language == "rust":
            # First compile
            subprocess.run(["cargo", "build", "--release"], cwd=lang_dir, capture_output=True)
            cmd = [str(lang_dir / "target" / "release" / f"phase4e-{language}"), "--version"]
        
        try:
            with self.measure_time() as get_time:
                process = subprocess.Popen(cmd, stdout=subprocess.PIPE, 
                                         stderr=subprocess.PIPE, cwd=lang_dir)
                memory_usage = self.measure_memory_usage(process)
                stdout, stderr = process.communicate(timeout=5)
                
            startup_time = get_time()
            success = process.returncode == 0
            
            return BenchmarkResult(
                language=language,
                test_name="startup_time",
                startup_time_ms=startup_time,
                memory_usage_mb=memory_usage,
                completion_time_ms=0,  # N/A for startup test
                feature_count=1,
                success=success,
                error_message=stderr.decode() if stderr and not success else None
            )
            
        except Exception as e:
            return BenchmarkResult(
                language=language,
                test_name="startup_time",
                startup_time_ms=999999,  # Indicate failure
                memory_usage_mb=0,
                completion_time_ms=0,
                feature_count=0,
                success=False,
                error_message=str(e)
            )
    
    def test_interactive_mode(self, language: str) -> IntegrationTestResult:
        """Test interactive mode functionality"""
        lang_dir = self.test_dir / f"test_{language}"
        
        # Create test script for interactive mode
        test_commands = [
            "test-basic hello",
            "test-interactive --mode repl",
            "help",
            "exit"
        ]
        
        if language == "python":
            cmd = ["python", str(lang_dir / "cli.py")]
        elif language == "nodejs":
            cmd = ["node", str(lang_dir / "cli.js")]
        elif language == "typescript":
            cmd = ["node", str(lang_dir / "cli.js")]
        elif language == "rust":
            cmd = [str(lang_dir / "target" / "release" / f"phase4e-{language}")]
        
        try:
            with self.measure_time() as get_time:
                process = subprocess.Popen(cmd + ["--interactive"], 
                                         stdin=subprocess.PIPE,
                                         stdout=subprocess.PIPE,
                                         stderr=subprocess.PIPE,
                                         text=True, cwd=lang_dir)
                
                # Send test commands
                input_data = "\n".join(test_commands) + "\n"
                stdout, stderr = process.communicate(input=input_data, timeout=10)
            
            execution_time = get_time()
            success = "Interactive mode" in stdout or process.returncode == 0
            
            return IntegrationTestResult(
                language=language,
                feature="interactive_mode",
                test_case="basic_interaction",
                success=success,
                execution_time_ms=execution_time,
                output=stdout[:500] if stdout else None,  # Truncate output
                error_message=stderr if stderr and not success else None
            )
            
        except Exception as e:
            return IntegrationTestResult(
                language=language,
                feature="interactive_mode",
                test_case="basic_interaction",
                success=False,
                execution_time_ms=0,
                error_message=str(e)
            )
    
    def test_dynamic_completion(self, language: str) -> IntegrationTestResult:
        """Test dynamic completion system"""
        lang_dir = self.test_dir / f"test_{language}"
        
        if language == "python":
            cmd = ["python", str(lang_dir / "cli.py")]
        elif language == "nodejs":
            cmd = ["node", str(lang_dir / "cli.js")]
        elif language == "typescript":
            cmd = ["node", str(lang_dir / "cli.js")]
        elif language == "rust":
            cmd = [str(lang_dir / "target" / "release" / f"phase4e-{language}")]
        
        try:
            with self.measure_time() as get_time:
                # Test completion generation
                process = subprocess.run(cmd + ["completion", "--generate", "bash"], 
                                       capture_output=True, text=True, 
                                       cwd=lang_dir, timeout=5)
            
            completion_time = get_time()
            success = process.returncode == 0 and ("complete" in process.stdout or 
                                                  "completion" in process.stdout)
            
            return IntegrationTestResult(
                language=language,
                feature="dynamic_completion",
                test_case="bash_completion",
                success=success,
                execution_time_ms=completion_time,
                output=process.stdout[:200] if process.stdout else None,
                error_message=process.stderr if process.stderr and not success else None
            )
            
        except Exception as e:
            return IntegrationTestResult(
                language=language,
                feature="dynamic_completion", 
                test_case="bash_completion",
                success=False,
                execution_time_ms=0,
                error_message=str(e)
            )
    
    def test_plugin_system(self, language: str) -> IntegrationTestResult:
        """Test plugin installation and management"""
        lang_dir = self.test_dir / f"test_{language}"
        
        # Create a simple test plugin
        plugin_dir = lang_dir / "plugins" / "test_plugin"
        plugin_dir.mkdir(parents=True, exist_ok=True)
        
        if language == "python":
            plugin_content = '''
def execute(args):
    """Test plugin execution"""
    print("Test plugin executed successfully")
    return True
'''
            (plugin_dir / "plugin.py").write_text(plugin_content)
            cmd = ["python", str(lang_dir / "cli.py")]
        elif language == "nodejs":
            plugin_content = '''
module.exports = {
    execute: function(args) {
        console.log("Test plugin executed successfully");
        return true;
    }
};
'''
            (plugin_dir / "plugin.js").write_text(plugin_content)
            cmd = ["node", str(lang_dir / "cli.js")]
        elif language == "typescript":
            plugin_content = '''
export function execute(args: any): boolean {
    console.log("Test plugin executed successfully");
    return true;
}
'''
            (plugin_dir / "plugin.ts").write_text(plugin_content)
            cmd = ["node", str(lang_dir / "cli.js")]
        elif language == "rust":
            # Simplified rust plugin test
            cmd = [str(lang_dir / "target" / "release" / f"phase4e-{language}")]
        
        try:
            with self.measure_time() as get_time:
                # Test plugin listing
                process = subprocess.run(cmd + ["plugin", "list"], 
                                       capture_output=True, text=True, 
                                       cwd=lang_dir, timeout=5)
            
            execution_time = get_time()
            success = process.returncode == 0
            
            return IntegrationTestResult(
                language=language,
                feature="plugin_system",
                test_case="plugin_list",
                success=success,
                execution_time_ms=execution_time,
                output=process.stdout[:200] if process.stdout else None,
                error_message=process.stderr if process.stderr and not success else None
            )
            
        except Exception as e:
            return IntegrationTestResult(
                language=language,
                feature="plugin_system",
                test_case="plugin_list", 
                success=False,
                execution_time_ms=0,
                error_message=str(e)
            )
    
    def run_comprehensive_tests(self) -> Dict[str, Any]:
        """Run comprehensive test suite for all languages"""
        self.console.print("[bold green]🚀 Starting Phase 4E Comprehensive Integration Testing[/bold green]")
        
        # Setup test environment
        self.setup_test_environment()
        
        results = {
            "test_summary": {
                "total_languages": len(self.languages),
                "total_tests": 0,
                "passed_tests": 0,
                "failed_tests": 0,
                "benchmarks": [],
                "integrations": []
            },
            "language_results": {}
        }
        
        with Progress() as progress:
            main_task = progress.add_task("[green]Overall Progress", 
                                        total=len(self.languages) * 5)  # 5 tests per language
            
            for language in self.languages:
                self.console.print(f"\n[bold cyan]Testing {language.upper()}[/bold cyan]")
                
                lang_results = {
                    "generation": False,
                    "startup_benchmark": None,
                    "interactive_test": None,
                    "completion_test": None,
                    "plugin_test": None
                }
                
                # 1. Test CLI Generation
                progress.update(main_task, description=f"[green]Generating {language} CLI")
                lang_results["generation"] = self.test_cli_generation(language)
                progress.advance(main_task)
                results["test_summary"]["total_tests"] += 1
                
                if lang_results["generation"]:
                    results["test_summary"]["passed_tests"] += 1
                    
                    # 2. Startup Time Benchmark
                    progress.update(main_task, description=f"[green]Benchmarking {language} startup")
                    benchmark = self.test_cli_startup_time(language)
                    lang_results["startup_benchmark"] = benchmark
                    self.benchmark_results.append(benchmark)
                    progress.advance(main_task)
                    results["test_summary"]["total_tests"] += 1
                    
                    if benchmark.success:
                        results["test_summary"]["passed_tests"] += 1
                    else:
                        results["test_summary"]["failed_tests"] += 1
                    
                    # 3. Interactive Mode Test
                    progress.update(main_task, description=f"[green]Testing {language} interactive mode")
                    interactive_test = self.test_interactive_mode(language)
                    lang_results["interactive_test"] = interactive_test
                    self.integration_results.append(interactive_test)
                    progress.advance(main_task)
                    results["test_summary"]["total_tests"] += 1
                    
                    if interactive_test.success:
                        results["test_summary"]["passed_tests"] += 1
                    else:
                        results["test_summary"]["failed_tests"] += 1
                    
                    # 4. Dynamic Completion Test
                    progress.update(main_task, description=f"[green]Testing {language} completion")
                    completion_test = self.test_dynamic_completion(language)
                    lang_results["completion_test"] = completion_test  
                    self.integration_results.append(completion_test)
                    progress.advance(main_task)
                    results["test_summary"]["total_tests"] += 1
                    
                    if completion_test.success:
                        results["test_summary"]["passed_tests"] += 1
                    else:
                        results["test_summary"]["failed_tests"] += 1
                    
                    # 5. Plugin System Test
                    progress.update(main_task, description=f"[green]Testing {language} plugins")
                    plugin_test = self.test_plugin_system(language)
                    lang_results["plugin_test"] = plugin_test
                    self.integration_results.append(plugin_test)
                    progress.advance(main_task)
                    results["test_summary"]["total_tests"] += 1
                    
                    if plugin_test.success:
                        results["test_summary"]["passed_tests"] += 1
                    else:
                        results["test_summary"]["failed_tests"] += 1
                else:
                    results["test_summary"]["failed_tests"] += 1
                    # Skip remaining tests if generation failed
                    progress.advance(main_task, 4)
                    results["test_summary"]["total_tests"] += 4
                    results["test_summary"]["failed_tests"] += 4
                
                results["language_results"][language] = lang_results
        
        # Add benchmark and integration results to summary
        results["test_summary"]["benchmarks"] = [asdict(b) for b in self.benchmark_results]
        results["test_summary"]["integrations"] = [asdict(i) for i in self.integration_results]
        
        return results
    
    def analyze_performance_regression(self, baseline_file: Optional[str] = None) -> Dict[str, Any]:
        """Analyze performance regression against baseline"""
        regression_analysis = {
            "baseline_comparison": {},
            "performance_metrics": {},
            "threshold_violations": [],
            "recommendations": []
        }
        
        # Current performance metrics
        current_metrics = {}
        for result in self.benchmark_results:
            if result.success:
                current_metrics[result.language] = {
                    "startup_time_ms": result.startup_time_ms,
                    "memory_usage_mb": result.memory_usage_mb
                }
        
        # Check against thresholds
        for lang, metrics in current_metrics.items():
            if metrics["startup_time_ms"] > self.STARTUP_TIME_THRESHOLD_MS:
                regression_analysis["threshold_violations"].append({
                    "language": lang,
                    "metric": "startup_time",
                    "value": metrics["startup_time_ms"],
                    "threshold": self.STARTUP_TIME_THRESHOLD_MS,
                    "severity": "critical" if metrics["startup_time_ms"] > 200 else "warning"
                })
            
            if metrics["memory_usage_mb"] > self.MEMORY_USAGE_THRESHOLD_MB:
                regression_analysis["threshold_violations"].append({
                    "language": lang,
                    "metric": "memory_usage",
                    "value": metrics["memory_usage_mb"],
                    "threshold": self.MEMORY_USAGE_THRESHOLD_MB,
                    "severity": "warning"
                })
        
        regression_analysis["performance_metrics"] = current_metrics
        
        # Generate recommendations
        if regression_analysis["threshold_violations"]:
            regression_analysis["recommendations"].extend([
                "Consider implementing lazy loading for heavy modules",
                "Review dependency tree for unnecessary imports",
                "Enable startup optimization flags",
                "Consider compilation optimizations for Rust/TypeScript"
            ])
        else:
            regression_analysis["recommendations"].append(
                "All performance metrics within acceptable thresholds"
            )
        
        return regression_analysis
    
    def generate_comprehensive_report(self, results: Dict[str, Any]) -> str:
        """Generate comprehensive test report"""
        self.console.print("\n[bold blue]📊 Generating Comprehensive Test Report[/bold blue]")
        
        # Performance regression analysis
        regression_analysis = self.analyze_performance_regression()
        
        report = []
        report.append("# Phase 4E - Final Integration Testing and Benchmarking Report")
        report.append(f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # Executive Summary
        report.append("## Executive Summary")
        total_tests = results["test_summary"]["total_tests"]
        passed_tests = results["test_summary"]["passed_tests"]
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        report.append(f"- **Total Tests Executed**: {total_tests}")
        report.append(f"- **Tests Passed**: {passed_tests}")
        report.append(f"- **Tests Failed**: {results['test_summary']['failed_tests']}")
        report.append(f"- **Success Rate**: {success_rate:.1f}%")
        report.append(f"- **Languages Tested**: {', '.join(self.languages)}")
        report.append("")
        
        # Performance Summary
        report.append("## Performance Summary")
        report.append("")
        
        # Create performance table
        perf_table = "| Language | Startup Time (ms) | Memory Usage (MB) | Status |\n"
        perf_table += "|----------|-------------------|-------------------|--------|\n"
        
        for result in self.benchmark_results:
            if result.success:
                startup_status = "✅" if result.startup_time_ms <= self.STARTUP_TIME_THRESHOLD_MS else "⚠️"
                memory_status = "✅" if result.memory_usage_mb <= self.MEMORY_USAGE_THRESHOLD_MB else "⚠️"
                status = startup_status if startup_status == memory_status else "⚠️"
                
                perf_table += f"| {result.language} | {result.startup_time_ms:.2f} | {result.memory_usage_mb:.2f} | {status} |\n"
            else:
                perf_table += f"| {result.language} | Failed | Failed | ❌ |\n"
        
        report.append(perf_table)
        report.append("")
        
        # Feature Testing Results
        report.append("## Feature Testing Results")
        report.append("")
        
        for language in self.languages:
            lang_results = results["language_results"].get(language, {})
            report.append(f"### {language.upper()}")
            report.append("")
            
            # Generation status
            gen_status = "✅ Passed" if lang_results.get("generation") else "❌ Failed"
            report.append(f"- **CLI Generation**: {gen_status}")
            
            # Feature tests
            for feature in ["interactive_test", "completion_test", "plugin_test"]:
                test_result = lang_results.get(feature)
                if test_result:
                    status = "✅ Passed" if test_result.success else "❌ Failed"
                    time_info = f" ({test_result.execution_time_ms:.2f}ms)"
                    report.append(f"- **{feature.replace('_', ' ').title()}**: {status}{time_info}")
                    if not test_result.success and test_result.error_message:
                        report.append(f"  - Error: {test_result.error_message[:100]}...")
                else:
                    report.append(f"- **{feature.replace('_', ' ').title()}**: ❌ Skipped")
            
            report.append("")
        
        # Performance Regression Analysis
        report.append("## Performance Regression Analysis")
        report.append("")
        
        if regression_analysis["threshold_violations"]:
            report.append("### ⚠️ Threshold Violations")
            for violation in regression_analysis["threshold_violations"]:
                report.append(f"- **{violation['language']}** {violation['metric']}: "
                            f"{violation['value']:.2f} (threshold: {violation['threshold']}) "
                            f"- {violation['severity'].upper()}")
            report.append("")
        else:
            report.append("### ✅ All Performance Thresholds Met")
            report.append("No performance regressions detected.")
            report.append("")
        
        # Recommendations
        report.append("## Recommendations")
        report.append("")
        for i, rec in enumerate(regression_analysis["recommendations"], 1):
            report.append(f"{i}. {rec}")
        
        report.append("")
        
        # Version 2.0 Readiness Assessment
        report.append("## Version 2.0 Readiness Assessment")
        report.append("")
        
        readiness_criteria = [
            ("Interactive Mode", all(r.success for r in self.integration_results if r.feature == "interactive_mode")),
            ("Dynamic Completion", all(r.success for r in self.integration_results if r.feature == "dynamic_completion")),
            ("Plugin System", all(r.success for r in self.integration_results if r.feature == "plugin_system")),
            ("Performance Targets", len(regression_analysis["threshold_violations"]) == 0),
            ("Cross-Language Parity", success_rate >= 95)
        ]
        
        all_ready = True
        for criterion, met in readiness_criteria:
            status = "✅" if met else "❌"
            report.append(f"- {criterion}: {status}")
            all_ready = all_ready and met
        
        report.append("")
        if all_ready:
            report.append("### 🎉 Ready for Version 2.0 Release!")
        else:
            report.append("### ⚠️ Additional work needed before Version 2.0 release")
        
        # Detailed Results Appendix
        report.append("")
        report.append("## Detailed Results (JSON)")
        report.append("```json")
        report.append(json.dumps({
            "summary": results["test_summary"],
            "regression_analysis": regression_analysis
        }, indent=2))
        report.append("```")
        
        return "\n".join(report)
    
    def cleanup(self):
        """Cleanup test environment"""
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir, ignore_errors=True)


def main():
    """Main entry point for Phase 4E testing"""
    console = Console()
    console.print("[bold green]🚀 Phase 4E - Final Integration Testing & Benchmarking[/bold green]")
    
    # Initialize test suite
    suite = Phase4ETestSuite()
    
    try:
        # Run comprehensive tests
        results = suite.run_comprehensive_tests()
        
        # Generate and display report
        report = suite.generate_comprehensive_report(results)
        
        # Save report
        report_file = Path("PHASE_4E_INTEGRATION_REPORT.md")
        with open(report_file, 'w') as f:
            f.write(report)
        
        console.print(f"\n[bold blue]📋 Report saved to: {report_file.absolute()}[/bold blue]")
        
        # Display summary
        total_tests = results["test_summary"]["total_tests"]
        passed_tests = results["test_summary"]["passed_tests"]
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        if success_rate >= 95:
            console.print(f"\n[bold green]✅ SUCCESS: {success_rate:.1f}% pass rate - Ready for Version 2.0![/bold green]")
        else:
            console.print(f"\n[bold yellow]⚠️ WARNING: {success_rate:.1f}% pass rate - Additional work needed[/bold yellow]")
        
        return 0 if success_rate >= 95 else 1
        
    except Exception as e:
        console.print(f"\n[bold red]❌ Test suite failed: {e}[/bold red]")
        return 1
    finally:
        # Cleanup
        suite.cleanup()


if __name__ == "__main__":
    sys.exit(main())