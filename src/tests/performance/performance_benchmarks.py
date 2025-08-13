#!/usr/bin/env python3
"""
Performance Benchmarking Suite for Phase 4E

This module provides detailed performance benchmarking for all advanced features
across all supported languages, measuring:
- CLI startup time with various feature configurations
- Memory usage during different operations
- Template rendering performance with large configurations
- Plugin system performance
- Interactive mode response time
- Completion system performance
"""

import os
import sys
import time
import json
import subprocess
import tempfile
import threading
import statistics
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Callable
from dataclasses import dataclass, asdict
from contextlib import contextmanager
from concurrent.futures import ThreadPoolExecutor, as_completed

import yaml
from rich.console import Console
from rich.progress import Progress, TaskID
from rich.table import Table

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from goobits_cli.builder import build_cli


@dataclass
class PerformanceMetric:
    """Performance metric data structure"""
    test_name: str
    language: str
    feature_set: str
    metric_type: str  # startup, memory, completion, rendering, etc.
    value: float
    unit: str
    timestamp: float
    iterations: int
    stddev: Optional[float] = None
    percentile_95: Optional[float] = None
    percentile_99: Optional[float] = None


@dataclass
class BenchmarkConfig:
    """Benchmark configuration"""
    name: str
    feature_enabled: Dict[str, bool]
    expected_performance: Dict[str, float]
    test_scenarios: List[str]


class PerformanceBenchmarkSuite:
    """Comprehensive performance benchmarking suite"""
    
    def __init__(self, iterations: int = 10):
        self.console = Console()
        self.iterations = iterations
        self.metrics: List[PerformanceMetric] = []
        self.languages = ["python", "nodejs", "typescript", "rust"]
        
        # Performance baselines and thresholds
        self.baselines = {
            "startup_time_ms": {"python": 80, "nodejs": 60, "typescript": 70, "rust": 30},
            "memory_usage_mb": {"python": 25, "nodejs": 35, "typescript": 40, "rust": 15},
            "completion_time_ms": {"python": 20, "nodejs": 15, "typescript": 25, "rust": 10},
            "template_render_ms": {"python": 50, "nodejs": 40, "typescript": 60, "rust": 20}
        }
        
        # Define benchmark configurations
        self.benchmark_configs = [
            BenchmarkConfig(
                name="minimal",
                feature_enabled={
                    "interactive": False,
                    "completion": False,
                    "plugins": False,
                    "performance_optimization": False
                },
                expected_performance={
                    "startup_time_ms": 50,
                    "memory_usage_mb": 20
                },
                test_scenarios=["basic_command", "help", "version"]
            ),
            BenchmarkConfig(
                name="standard",
                feature_enabled={
                    "interactive": True,
                    "completion": True,
                    "plugins": False,
                    "performance_optimization": True
                },
                expected_performance={
                    "startup_time_ms": 80,
                    "memory_usage_mb": 30
                },
                test_scenarios=["basic_command", "interactive_mode", "completion"]
            ),
            BenchmarkConfig(
                name="full_features",
                feature_enabled={
                    "interactive": True,
                    "completion": True,
                    "plugins": True,
                    "performance_optimization": True
                },
                expected_performance={
                    "startup_time_ms": 100,
                    "memory_usage_mb": 50
                },
                test_scenarios=["all_features", "plugin_operations", "heavy_completion"]
            )
        ]
    
    @contextmanager
    def measure_performance(self):
        """Context manager for performance measurement"""
        import psutil
        import threading
        
        start_time = time.perf_counter()
        start_memory = psutil.virtual_memory().used
        measurements = {"memory_peaks": []}
        stop_monitoring = threading.Event()
        
        def monitor_memory():
            while not stop_monitoring.wait(0.01):  # Sample every 10ms
                measurements["memory_peaks"].append(psutil.virtual_memory().used)
        
        monitor_thread = threading.Thread(target=monitor_memory)
        monitor_thread.start()
        
        try:
            yield measurements
        finally:
            stop_monitoring.set()
            monitor_thread.join()
            
            end_time = time.perf_counter()
            end_memory = psutil.virtual_memory().used
            
            measurements.update({
                "execution_time_ms": (end_time - start_time) * 1000,
                "memory_delta_mb": (end_memory - start_memory) / (1024 * 1024),
                "peak_memory_mb": (max(measurements["memory_peaks"]) - start_memory) / (1024 * 1024)
            })
    
    def create_benchmark_config(self, language: str, config: BenchmarkConfig) -> Path:
        """Create CLI configuration for specific benchmark"""
        test_dir = Path(tempfile.mkdtemp(prefix=f"bench_{language}_{config.name}_"))
        
        cli_config = {
            "name": f"benchmark-{config.name}",
            "version": "2.0.0-bench",
            "description": f"Performance benchmark for {config.name} configuration",
            "language": language,
            "setup": {
                "python_version": ">=3.8",
                "dependencies": {
                    "required": ["click>=8.0", "rich>=12.0"],
                    "optional": ["pytest", "pyyaml"]
                }
            },
            "installation": {
                "pypi_name": f"benchmark-{config.name}-{language}",
                "development_path": str(test_dir)
            },
            "cli": {
                "name": f"bench-{config.name}",
                "help": f"Benchmark CLI for {config.name} configuration",
                "version_flag": True,
                "config_file": f".bench-{config.name}.yaml"
            }
        }
        
        # Add features based on configuration
        if config.feature_enabled["interactive"]:
            cli_config["cli"]["interactive"] = {
                "enabled": True,
                "prompt": f"bench-{config.name}> ",
                "history_file": f".bench-{config.name}_history"
            }
        
        if config.feature_enabled["completion"]:
            cli_config["cli"]["completion"] = {
                "enabled": True,
                "dynamic": True,
                "cache_duration": 300
            }
        
        if config.feature_enabled["plugins"]:
            cli_config["cli"]["plugins"] = {
                "enabled": True,
                "directory": "plugins"
            }
        
        if config.feature_enabled["performance_optimization"]:
            cli_config["cli"]["performance"] = {
                "lazy_loading": True,
                "caching": True,
                "startup_optimization": True
            }
        
        # Add commands based on test scenarios
        commands = []
        
        if "basic_command" in config.test_scenarios:
            commands.append({
                "name": "basic",
                "help": "Basic command for testing",
                "arguments": [{"name": "input", "help": "Input parameter"}]
            })
        
        if "interactive_mode" in config.test_scenarios:
            commands.append({
                "name": "interactive",
                "help": "Test interactive mode",
                "options": [{"name": "--mode", "help": "Interaction mode"}]
            })
        
        if "completion" in config.test_scenarios or "heavy_completion" in config.test_scenarios:
            commands.extend([
                {
                    "name": "complete-test",
                    "help": "Completion testing command",
                    "options": [
                        {"name": "--type", "help": "Completion type", 
                         "choices": ["bash", "zsh", "fish", "powershell"]},
                        {"name": "--level", "help": "Completion level", "type": "int"}
                    ]
                }
            ])
        
        if "plugin_operations" in config.test_scenarios:
            commands.append({
                "name": "plugin",
                "help": "Plugin operations",
                "subcommands": [
                    {"name": "install", "help": "Install plugin", 
                     "arguments": [{"name": "name", "help": "Plugin name"}]},
                    {"name": "list", "help": "List plugins"},
                    {"name": "remove", "help": "Remove plugin",
                     "arguments": [{"name": "name", "help": "Plugin name"}]}
                ]
            })
        
        # Heavy command load for stress testing
        if "all_features" in config.test_scenarios:
            for i in range(20):  # Add many commands to stress test
                commands.append({
                    "name": f"stress-cmd-{i:02d}",
                    "help": f"Stress test command {i}",
                    "options": [
                        {"name": f"--option-{j}", "help": f"Option {j}"} 
                        for j in range(5)
                    ]
                })
        
        cli_config["cli"]["commands"] = commands
        
        # Save configuration
        config_file = test_dir / "goobits.yaml"
        with open(config_file, 'w') as f:
            yaml.dump(cli_config, f, default_flow_style=False)
        
        return test_dir
    
    def benchmark_startup_time(self, language: str, config: BenchmarkConfig) -> List[PerformanceMetric]:
        """Benchmark CLI startup time across multiple iterations"""
        test_dir = self.create_benchmark_config(language, config)
        
        # Build CLI
        try:
            build_cli(str(test_dir / "goobits.yaml"), str(test_dir))
        except Exception as e:
            self.console.print(f"❌ Failed to build {language} CLI for {config.name}: {e}")
            return []
        
        # Prepare command based on language
        if language == "python":
            cmd = ["python", str(test_dir / "cli.py")]
        elif language == "nodejs":
            cmd = ["node", str(test_dir / "cli.js")]
        elif language == "typescript":
            cmd = ["node", str(test_dir / "cli.js")]
        elif language == "rust":
            # Compile first
            subprocess.run(["cargo", "build", "--release"], cwd=test_dir, capture_output=True)
            cmd = [str(test_dir / "target" / "release" / f"bench-{config.name}")]
        
        startup_times = []
        memory_usages = []
        
        for iteration in range(self.iterations):
            try:
                with self.measure_performance() as metrics:
                    process = subprocess.run(cmd + ["--version"], 
                                           capture_output=True, 
                                           cwd=test_dir, 
                                           timeout=5)
                
                if process.returncode == 0:
                    startup_times.append(metrics["execution_time_ms"])
                    memory_usages.append(metrics["peak_memory_mb"])
                
            except Exception:
                continue  # Skip failed iterations
        
        results = []
        
        if startup_times:
            results.append(PerformanceMetric(
                test_name="startup_time",
                language=language,
                feature_set=config.name,
                metric_type="startup",
                value=statistics.mean(startup_times),
                unit="ms",
                timestamp=time.time(),
                iterations=len(startup_times),
                stddev=statistics.stdev(startup_times) if len(startup_times) > 1 else 0,
                percentile_95=sorted(startup_times)[int(len(startup_times) * 0.95)] if startup_times else 0,
                percentile_99=sorted(startup_times)[int(len(startup_times) * 0.99)] if startup_times else 0
            ))
        
        if memory_usages:
            results.append(PerformanceMetric(
                test_name="memory_usage",
                language=language,
                feature_set=config.name,
                metric_type="memory",
                value=statistics.mean(memory_usages),
                unit="MB",
                timestamp=time.time(),
                iterations=len(memory_usages),
                stddev=statistics.stdev(memory_usages) if len(memory_usages) > 1 else 0
            ))
        
        # Cleanup
        import shutil
        shutil.rmtree(test_dir, ignore_errors=True)
        
        return results
    
    def benchmark_template_rendering(self, language: str) -> List[PerformanceMetric]:
        """Benchmark template rendering performance with large configurations"""
        rendering_times = []
        
        # Create increasingly complex configurations
        complexity_levels = [10, 50, 100, 200]  # Number of commands
        
        for complexity in complexity_levels:
            test_dir = Path(tempfile.mkdtemp(prefix=f"template_bench_{language}_"))
            
            # Create complex configuration
            complex_config = {
                "name": f"complex-{complexity}",
                "version": "1.0.0",
                "language": language,
                "cli": {
                    "name": f"complex-{complexity}",
                    "commands": []
                }
            }
            
            # Generate many commands
            for i in range(complexity):
                command = {
                    "name": f"cmd-{i:03d}",
                    "help": f"Command {i} with extensive help documentation that includes multiple lines and detailed descriptions",
                    "options": [
                        {
                            "name": f"--option-{j}",
                            "help": f"Option {j} with detailed help text that explains the purpose and usage",
                            "type": "str" if j % 3 == 0 else "int" if j % 3 == 1 else "bool"
                        }
                        for j in range(min(10, i // 5 + 1))  # Variable option count
                    ]
                }
                
                if i % 5 == 0:  # Add subcommands to some commands
                    command["subcommands"] = [
                        {
                            "name": f"sub-{k}",
                            "help": f"Subcommand {k}",
                            "options": [{"name": f"--sub-opt-{k}", "help": f"Sub option {k}"}]
                        }
                        for k in range(min(3, i // 10 + 1))
                    ]
                
                complex_config["cli"]["commands"].append(command)
            
            config_file = test_dir / "goobits.yaml"
            with open(config_file, 'w') as f:
                yaml.dump(complex_config, f, default_flow_style=False)
            
            # Benchmark rendering
            try:
                with self.measure_performance() as metrics:
                    build_cli(str(config_file), str(test_dir))
                
                rendering_times.append({
                    "complexity": complexity,
                    "time_ms": metrics["execution_time_ms"],
                    "memory_mb": metrics["peak_memory_mb"]
                })
                
            except Exception as e:
                self.console.print(f"❌ Template rendering failed for complexity {complexity}: {e}")
            
            # Cleanup
            import shutil
            shutil.rmtree(test_dir, ignore_errors=True)
        
        # Create performance metrics
        results = []
        if rendering_times:
            avg_time = statistics.mean([r["time_ms"] for r in rendering_times])
            avg_memory = statistics.mean([r["memory_mb"] for r in rendering_times])
            
            results.extend([
                PerformanceMetric(
                    test_name="template_rendering",
                    language=language,
                    feature_set="complex_configs",
                    metric_type="rendering",
                    value=avg_time,
                    unit="ms",
                    timestamp=time.time(),
                    iterations=len(rendering_times)
                ),
                PerformanceMetric(
                    test_name="template_memory",
                    language=language,
                    feature_set="complex_configs",
                    metric_type="memory",
                    value=avg_memory,
                    unit="MB",
                    timestamp=time.time(),
                    iterations=len(rendering_times)
                )
            ])
        
        return results
    
    def benchmark_completion_system(self, language: str) -> List[PerformanceMetric]:
        """Benchmark dynamic completion system performance"""
        # Create test config with completion enabled
        config = BenchmarkConfig(
            name="completion_test",
            feature_enabled={
                "interactive": False,
                "completion": True,
                "plugins": False,
                "performance_optimization": True
            },
            expected_performance={"completion_time_ms": 30},
            test_scenarios=["heavy_completion"]
        )
        
        test_dir = self.create_benchmark_config(language, config)
        
        try:
            build_cli(str(test_dir / "goobits.yaml"), str(test_dir))
        except Exception as e:
            self.console.print(f"❌ Failed to build completion test CLI: {e}")
            return []
        
        # Prepare command
        if language == "python":
            cmd = ["python", str(test_dir / "cli.py")]
        elif language == "nodejs":
            cmd = ["node", str(test_dir / "cli.js")]
        elif language == "typescript":
            cmd = ["node", str(test_dir / "cli.js")]
        elif language == "rust":
            subprocess.run(["cargo", "build", "--release"], cwd=test_dir, capture_output=True)
            cmd = [str(test_dir / "target" / "release" / "bench-completion_test")]
        
        completion_times = []
        
        # Test different completion scenarios
        completion_tests = [
            ["completion", "--generate", "bash"],
            ["completion", "--generate", "zsh"],
            ["completion", "--generate", "fish"]
        ]
        
        for test_cmd in completion_tests:
            for iteration in range(self.iterations):
                try:
                    with self.measure_performance() as metrics:
                        process = subprocess.run(cmd + test_cmd,
                                               capture_output=True,
                                               cwd=test_dir,
                                               timeout=3)
                    
                    if process.returncode == 0:
                        completion_times.append(metrics["execution_time_ms"])
                
                except Exception:
                    continue
        
        # Cleanup
        import shutil
        shutil.rmtree(test_dir, ignore_errors=True)
        
        if completion_times:
            return [PerformanceMetric(
                test_name="completion_generation",
                language=language,
                feature_set="dynamic_completion",
                metric_type="completion",
                value=statistics.mean(completion_times),
                unit="ms",
                timestamp=time.time(),
                iterations=len(completion_times),
                stddev=statistics.stdev(completion_times) if len(completion_times) > 1 else 0
            )]
        
        return []
    
    def run_comprehensive_benchmarks(self) -> Dict[str, Any]:
        """Run comprehensive performance benchmarks across all languages and configurations"""
        self.console.print("[bold blue]🏃‍♂️ Running Comprehensive Performance Benchmarks[/bold blue]")
        
        total_tests = len(self.languages) * (len(self.benchmark_configs) + 2)  # +2 for template and completion benchmarks
        
        with Progress() as progress:
            main_task = progress.add_task("[green]Benchmark Progress", total=total_tests)
            
            with ThreadPoolExecutor(max_workers=2) as executor:  # Limit concurrent tests
                futures = []
                
                for language in self.languages:
                    # Startup benchmarks for each configuration
                    for config in self.benchmark_configs:
                        future = executor.submit(self.benchmark_startup_time, language, config)
                        futures.append((future, f"startup_{language}_{config.name}"))
                    
                    # Template rendering benchmark
                    future = executor.submit(self.benchmark_template_rendering, language)
                    futures.append((future, f"template_{language}"))
                    
                    # Completion system benchmark
                    future = executor.submit(self.benchmark_completion_system, language)
                    futures.append((future, f"completion_{language}"))
                
                # Collect results
                for future, test_name in futures:
                    try:
                        results = future.result(timeout=60)  # 60 second timeout per test
                        self.metrics.extend(results)
                        progress.update(main_task, description=f"[green]Completed {test_name}")
                    except Exception as e:
                        self.console.print(f"❌ Benchmark failed for {test_name}: {e}")
                    finally:
                        progress.advance(main_task)
        
        return self.analyze_benchmark_results()
    
    def analyze_benchmark_results(self) -> Dict[str, Any]:
        """Analyze benchmark results and generate insights"""
        analysis = {
            "summary": {
                "total_metrics": len(self.metrics),
                "languages_tested": len(set(m.language for m in self.metrics)),
                "test_configurations": len(set(m.feature_set for m in self.metrics))
            },
            "performance_by_language": {},
            "performance_by_feature": {},
            "threshold_analysis": {},
            "recommendations": []
        }
        
        # Group metrics by language
        for language in self.languages:
            lang_metrics = [m for m in self.metrics if m.language == language]
            if not lang_metrics:
                continue
                
            lang_analysis = {
                "startup_times": [m for m in lang_metrics if m.metric_type == "startup"],
                "memory_usage": [m for m in lang_metrics if m.metric_type == "memory"],
                "completion_times": [m for m in lang_metrics if m.metric_type == "completion"],
                "rendering_times": [m for m in lang_metrics if m.metric_type == "rendering"]
            }
            
            # Calculate averages
            for metric_type, metrics_list in lang_analysis.items():
                if metrics_list:
                    lang_analysis[f"avg_{metric_type}"] = statistics.mean([m.value for m in metrics_list])
            
            analysis["performance_by_language"][language] = lang_analysis
        
        # Threshold analysis
        for metric_type, thresholds in self.baselines.items():
            violations = []
            for language in self.languages:
                lang_metrics = [m for m in self.metrics 
                              if m.language == language and 
                              metric_type.replace("_", "").replace("ms", "").replace("mb", "") in m.test_name]
                
                if lang_metrics:
                    avg_value = statistics.mean([m.value for m in lang_metrics])
                    threshold = thresholds.get(language, 100)  # Default threshold
                    
                    if avg_value > threshold:
                        violations.append({
                            "language": language,
                            "metric": metric_type,
                            "value": avg_value,
                            "threshold": threshold,
                            "excess_percent": ((avg_value - threshold) / threshold) * 100
                        })
            
            if violations:
                analysis["threshold_analysis"][metric_type] = violations
        
        # Generate recommendations
        analysis["recommendations"] = self._generate_performance_recommendations(analysis)
        
        return analysis
    
    def _generate_performance_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate performance improvement recommendations"""
        recommendations = []
        
        threshold_violations = analysis.get("threshold_analysis", {})
        
        if "startup_time_ms" in threshold_violations:
            recommendations.append("Consider implementing lazy loading for CLI modules")
            recommendations.append("Review import statements for unnecessary dependencies")
            recommendations.append("Enable startup optimization flags in CLI configuration")
        
        if "memory_usage_mb" in threshold_violations:
            recommendations.append("Implement memory pooling for frequently used objects")
            recommendations.append("Review template caching strategies")
            recommendations.append("Consider using streaming for large configuration processing")
        
        if "completion_time_ms" in threshold_violations:
            recommendations.append("Implement completion result caching")
            recommendations.append("Optimize completion tree traversal algorithms")
            recommendations.append("Consider background completion pre-loading")
        
        if "template_render_ms" in threshold_violations:
            recommendations.append("Implement template compilation caching")
            recommendations.append("Optimize Jinja2 template rendering")
            recommendations.append("Consider template pre-compilation for production builds")
        
        # Language-specific recommendations
        perf_by_lang = analysis.get("performance_by_language", {})
        
        rust_metrics = perf_by_lang.get("rust", {})
        if rust_metrics and rust_metrics.get("avg_startup_times", 0) > 50:
            recommendations.append("Enable Rust release mode optimizations (--release)")
            recommendations.append("Consider using cargo-strip for binary size optimization")
        
        python_metrics = perf_by_lang.get("python", {})
        if python_metrics and python_metrics.get("avg_startup_times", 0) > 100:
            recommendations.append("Consider using Python import optimizations")
            recommendations.append("Implement Python bytecode caching (.pyc files)")
        
        nodejs_metrics = perf_by_lang.get("nodejs", {})
        if nodejs_metrics and nodejs_metrics.get("avg_memory_usage", 0) > 40:
            recommendations.append("Optimize Node.js memory usage with --max-old-space-size")
            recommendations.append("Consider using Node.js clustering for heavy workloads")
        
        if not recommendations:
            recommendations.append("All performance metrics within acceptable thresholds - excellent work!")
        
        return recommendations
    
    def generate_performance_report(self, analysis: Dict[str, Any]) -> str:
        """Generate comprehensive performance report"""
        report = []
        report.append("# Phase 4E - Performance Benchmarking Report")
        report.append(f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Iterations per test: {self.iterations}")
        report.append("")
        
        # Executive Summary
        report.append("## Executive Summary")
        report.append(f"- **Total Metrics Collected**: {analysis['summary']['total_metrics']}")
        report.append(f"- **Languages Tested**: {analysis['summary']['languages_tested']}")
        report.append(f"- **Configurations Tested**: {analysis['summary']['test_configurations']}")
        report.append("")
        
        # Performance by Language
        report.append("## Performance by Language")
        report.append("")
        
        # Create performance table
        table_header = "| Language | Avg Startup (ms) | Avg Memory (MB) | Avg Completion (ms) | Status |"
        table_separator = "|----------|------------------|-----------------|---------------------|--------|"
        report.extend([table_header, table_separator])
        
        for language in self.languages:
            lang_data = analysis["performance_by_language"].get(language, {})
            
            startup = lang_data.get("avg_startup_times", [])
            startup_avg = statistics.mean([m.value for m in startup]) if startup else 0
            
            memory = lang_data.get("avg_memory_usage", [])
            memory_avg = statistics.mean([m.value for m in memory]) if memory else 0
            
            completion = lang_data.get("avg_completion_times", [])
            completion_avg = statistics.mean([m.value for m in completion]) if completion else 0
            
            # Determine status
            status = "✅"
            if startup_avg > self.baselines["startup_time_ms"].get(language, 100):
                status = "⚠️"
            if memory_avg > self.baselines["memory_usage_mb"].get(language, 50):
                status = "⚠️"
            if completion_avg > self.baselines["completion_time_ms"].get(language, 30):
                status = "⚠️"
            
            report.append(f"| {language} | {startup_avg:.2f} | {memory_avg:.2f} | {completion_avg:.2f} | {status} |")
        
        report.append("")
        
        # Threshold Violations
        threshold_violations = analysis.get("threshold_analysis", {})
        if threshold_violations:
            report.append("## ⚠️ Performance Threshold Violations")
            report.append("")
            for metric_type, violations in threshold_violations.items():
                report.append(f"### {metric_type.replace('_', ' ').title()}")
                for violation in violations:
                    report.append(f"- **{violation['language']}**: {violation['value']:.2f} "
                                f"(threshold: {violation['threshold']:.2f}) "
                                f"- {violation['excess_percent']:.1f}% over threshold")
                report.append("")
        else:
            report.append("## ✅ All Performance Thresholds Met")
            report.append("No performance threshold violations detected across all languages and configurations.")
            report.append("")
        
        # Feature Set Performance Comparison
        report.append("## Performance by Feature Configuration")
        report.append("")
        
        for config in self.benchmark_configs:
            config_metrics = [m for m in self.metrics if m.feature_set == config.name]
            if config_metrics:
                report.append(f"### {config.name.title()} Configuration")
                
                startup_metrics = [m for m in config_metrics if m.metric_type == "startup"]
                if startup_metrics:
                    avg_startup = statistics.mean([m.value for m in startup_metrics])
                    report.append(f"- **Average Startup Time**: {avg_startup:.2f}ms")
                
                memory_metrics = [m for m in config_metrics if m.metric_type == "memory"]
                if memory_metrics:
                    avg_memory = statistics.mean([m.value for m in memory_metrics])
                    report.append(f"- **Average Memory Usage**: {avg_memory:.2f}MB")
                
                report.append("")
        
        # Recommendations
        report.append("## Performance Optimization Recommendations")
        report.append("")
        for i, rec in enumerate(analysis["recommendations"], 1):
            report.append(f"{i}. {rec}")
        
        report.append("")
        
        # Raw Data
        report.append("## Detailed Metrics (JSON)")
        report.append("```json")
        metrics_data = [asdict(m) for m in self.metrics]
        report.append(json.dumps({"metrics": metrics_data, "analysis": analysis}, indent=2))
        report.append("```")
        
        return "\n".join(report)


def main():
    """Main entry point for performance benchmarking"""
    console = Console()
    console.print("[bold blue]🏃‍♂️ Phase 4E - Performance Benchmarking Suite[/bold blue]")
    
    # Initialize benchmark suite
    benchmark_suite = PerformanceBenchmarkSuite(iterations=5)  # Reduced iterations for demo
    
    try:
        # Run benchmarks
        analysis = benchmark_suite.run_comprehensive_benchmarks()
        
        # Generate report
        report = benchmark_suite.generate_performance_report(analysis)
        
        # Save report
        report_file = Path("PHASE_4E_PERFORMANCE_REPORT.md")
        with open(report_file, 'w') as f:
            f.write(report)
        
        console.print(f"\n[bold blue]📊 Performance report saved to: {report_file.absolute()}[/bold blue]")
        
        # Check if performance meets standards
        threshold_violations = analysis.get("threshold_analysis", {})
        if threshold_violations:
            console.print(f"\n[bold yellow]⚠️ Performance thresholds exceeded in {len(threshold_violations)} categories[/bold yellow]")
            return 1
        else:
            console.print(f"\n[bold green]✅ All performance thresholds met - ready for production![/bold green]")
            return 0
        
    except Exception as e:
        console.print(f"\n[bold red]❌ Performance benchmarking failed: {e}[/bold red]")
        return 1


if __name__ == "__main__":
    sys.exit(main())