#!/usr/bin/env python3
"""
Template Rendering Performance Benchmark
Analyzes Universal Template System performance across languages
"""

import json
import shutil
import statistics
import subprocess
import sys
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import yaml

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False


@dataclass
class TemplateRenderingResult:
    """Results from template rendering benchmark"""
    language: str
    template_system: str  # Always "universal"
    complexity: str      # "simple", "medium", "complex", "extreme"
    command_count: int
    render_time_ms: float
    build_success: bool
    generated_files: int
    total_size_kb: float
    error_message: Optional[str] = None
    iteration: int = 0


@dataclass
class TemplatePerformanceProfile:
    """Complete template performance profile"""
    language: str
    template_system: str
    complexity_results: Dict[str, List[TemplateRenderingResult]]
    average_render_time_ms: float
    median_render_time_ms: float
    min_render_time_ms: float
    max_render_time_ms: float
    success_rate: float
    scaling_factor: float  # How performance scales with complexity
    recommendations: List[str]


class TemplateBenchmark:
    """Comprehensive template rendering performance benchmark"""
    
    def __init__(self, 
                 iterations: int = 3,
                 output_dir: Path = Path("template_benchmark_results")):
        self.iterations = iterations
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        if RICH_AVAILABLE:
            self.console = Console()
        else:
            self.console = None
        
        # Test complexity configurations
        self.complexity_configs = {
            "simple": {
                "command_count": 5,
                "options_per_command": 2,
                "subcommand_probability": 0.0,
                "description_length": "short"
            },
            "medium": {
                "command_count": 25, 
                "options_per_command": 5,
                "subcommand_probability": 0.2,
                "description_length": "medium"
            },
            "complex": {
                "command_count": 75,
                "options_per_command": 8,
                "subcommand_probability": 0.3,
                "description_length": "long"
            },
            "extreme": {
                "command_count": 150,
                "options_per_command": 12,
                "subcommand_probability": 0.4,
                "description_length": "very_long"
            }
        }
        
        # Languages to test
        self.languages = ["python", "nodejs", "typescript"]
        
        # Results storage
        self.results: List[TemplateRenderingResult] = []
        self.profiles: Dict[str, TemplatePerformanceProfile] = {}
    
    def create_test_configuration(self, 
                                 language: str, 
                                 complexity: str, 
                                 template_system: str) -> Tuple[Path, Dict[str, Any]]:
        """Create test CLI configuration for benchmarking"""
        
        config = self.complexity_configs[complexity]
        test_dir = Path(tempfile.mkdtemp(prefix=f"template_bench_{language}_{complexity}_{template_system}_"))
        
        # Base CLI configuration
        cli_config = {
            "package_name": f"template-bench-{complexity}",
            "command_name": f"template-bench-{complexity}",
            "display_name": f"Template Benchmark - {complexity.title()}",
            "description": f"Template rendering benchmark for {complexity} configuration using {template_system} templates",
            "language": language,
            
            # Language-specific settings
            "python": {"minimum_version": "3.8"},
            
            # Dependencies
            "dependencies": {
                "required": self._get_language_dependencies(language),
                "optional": []
            },
            
            # Installation
            "installation": {
                "pypi_name": f"template-bench-{complexity}",
                "development_path": str(test_dir)
            },
            
            # CLI configuration
            "cli": {
                "name": f"template-bench-{complexity}",
                "help": f"Template benchmark CLI - {complexity} configuration",
                "version_flag": True,
                "commands": []
            }
        }
        
        # Generate commands based on complexity
        commands = self._generate_commands(config)
        cli_config["cli"]["commands"] = commands
        
        # Add performance features for complex configurations
        if complexity in ["complex", "extreme"]:
            cli_config["cli"]["performance"] = {
                "lazy_loading": True,
                "caching": True,
                "startup_optimization": True
            }
        
        # Save configuration
        config_file = test_dir / "goobits.yaml"
        with open(config_file, 'w') as f:
            yaml.dump(cli_config, f, default_flow_style=False, indent=2)
        
        return test_dir, cli_config
    
    def _get_language_dependencies(self, language: str) -> List[str]:
        """Get language-specific dependencies"""
        deps = {
            "python": ["click>=8.0", "rich>=12.0", "pyyaml"],
            "nodejs": ["commander", "chalk", "js-yaml"],
            "typescript": ["commander", "chalk", "js-yaml", "@types/node"]
        }
        return deps.get(language, [])
    
    def _generate_commands(self, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate commands based on complexity configuration"""
        commands = []
        
        description_templates = {
            "short": "Command {i}",
            "medium": "Command {i} - A test command with moderate documentation",
            "long": "Command {i} - A comprehensive test command with detailed documentation that explains the purpose, usage patterns, and various options available to users",
            "very_long": "Command {i} - An extremely detailed test command with comprehensive documentation that includes extensive explanations of the purpose, detailed usage patterns, complete option descriptions, example usage scenarios, troubleshooting information, and best practices for optimal performance"
        }
        
        desc_template = description_templates[config["description_length"]]
        
        for i in range(config["command_count"]):
            command = {
                "name": f"cmd-{i:03d}",
                "help": desc_template.format(i=i),
                "options": []
            }
            
            # Add options
            for j in range(config["options_per_command"]):
                option = {
                    "name": f"--option-{j}",
                    "help": f"Option {j} for command {i}",
                    "type": "str" if j % 3 == 0 else "int" if j % 3 == 1 else "bool"
                }
                
                # Add choices for some options
                if j % 5 == 0 and option["type"] == "str":
                    option["choices"] = [f"choice-{k}" for k in range(3)]
                
                command["options"].append(option)
            
            # Add subcommands based on probability
            import random
            if random.random() < config["subcommand_probability"]:
                command["subcommands"] = []
                subcommand_count = min(3, max(1, i // 10))
                
                for k in range(subcommand_count):
                    subcommand = {
                        "name": f"sub-{k}",
                        "help": f"Subcommand {k} of command {i}",
                        "options": [
                            {
                                "name": f"--sub-opt-{k}",
                                "help": f"Sub option {k}",
                                "type": "str"
                            }
                        ]
                    }
                    command["subcommands"].append(subcommand)
            
            commands.append(command)
        
        return commands
    
    def benchmark_template_rendering(self, 
                                   language: str, 
                                   template_system: str,
                                   complexity: str) -> List[TemplateRenderingResult]:
        """Benchmark template rendering for specific configuration"""
        
        if self.console:
            self.console.print(f"[blue]⚙️ Benchmarking {language} {template_system} templates ({complexity})[/blue]")
        
        results = []
        
        for iteration in range(self.iterations):
            # Create test configuration
            test_dir, cli_config = self.create_test_configuration(language, complexity, template_system)
            
            try:
                # Measure template rendering time
                start_time = time.perf_counter()
                
                # Build CLI using goobits (universal templates are now default)
                cmd = [sys.executable, "-m", "goobits_cli.main", "build"]
                cmd.extend([str(test_dir / "goobits.yaml"), "--output-dir", str(test_dir)])
                
                process = subprocess.run(
                    cmd,
                    cwd=test_dir,
                    capture_output=True,
                    text=True,
                    timeout=120  # 2 minute timeout
                )
                
                end_time = time.perf_counter()
                render_time = (end_time - start_time) * 1000  # Convert to ms
                
                # Analyze generated files
                generated_files = 0
                total_size = 0
                
                if process.returncode == 0:
                    for file_path in test_dir.rglob("*"):
                        if file_path.is_file() and not file_path.name.endswith(('.yaml', '.yml')):
                            generated_files += 1
                            total_size += file_path.stat().st_size
                
                result = TemplateRenderingResult(
                    language=language,
                    template_system=template_system,
                    complexity=complexity,
                    command_count=cli_config["cli"]["commands"].__len__(),
                    render_time_ms=render_time,
                    build_success=process.returncode == 0,
                    generated_files=generated_files,
                    total_size_kb=total_size / 1024,
                    error_message=process.stderr if process.returncode != 0 else None,
                    iteration=iteration
                )
                
                results.append(result)
                
                if self.console:
                    status = "✅" if result.build_success else "❌"
                    self.console.print(f"   {status} Iteration {iteration + 1}: {render_time:.1f}ms")
                    
            except subprocess.TimeoutExpired:
                result = TemplateRenderingResult(
                    language=language,
                    template_system=template_system,
                    complexity=complexity,
                    command_count=cli_config["cli"]["commands"].__len__(),
                    render_time_ms=120000,  # Timeout time
                    build_success=False,
                    generated_files=0,
                    total_size_kb=0,
                    error_message="Template rendering timed out",
                    iteration=iteration
                )
                results.append(result)
                
                if self.console:
                    self.console.print(f"   ⏰ Iteration {iteration + 1}: Timeout")
                    
            except Exception as e:
                result = TemplateRenderingResult(
                    language=language,
                    template_system=template_system,
                    complexity=complexity,
                    command_count=cli_config["cli"]["commands"].__len__(),
                    render_time_ms=float('inf'),
                    build_success=False,
                    generated_files=0,
                    total_size_kb=0,
                    error_message=str(e),
                    iteration=iteration
                )
                results.append(result)
                
                if self.console:
                    self.console.print(f"   ❌ Iteration {iteration + 1}: Error - {e}")
            
            finally:
                # Cleanup test directory
                shutil.rmtree(test_dir, ignore_errors=True)
        
        self.results.extend(results)
        return results
    
    def run_comprehensive_benchmark(self) -> Dict[str, Any]:
        """Run comprehensive template rendering benchmarks"""
        
        if self.console:
            self.console.print(Panel.fit(
                "[bold blue]🏗️ Template Rendering Performance Benchmark[/bold blue]\n"
                f"Languages: {', '.join(self.languages)}\n"
                f"Template System: Universal (production-ready)\n"
                f"Complexity Levels: {', '.join(self.complexity_configs.keys())}\n"
                f"Iterations: {self.iterations}",
                title="Template Benchmark Suite"
            ))
        
        # Calculate total tests
        total_tests = len(self.languages) * len(self.complexity_configs)  # Only universal system
        completed_tests = 0
        
        if self.console:
            progress = Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TextColumn("[progress.percentage]{task.percentage:>3.0f}%")
            )
            progress_task = progress.add_task("Running template benchmarks...", total=total_tests)
            progress.start()
        else:
            progress = None
        
        try:
            # Run benchmarks with thread pool for parallel execution
            with ThreadPoolExecutor(max_workers=2) as executor:  # Limit to avoid resource conflicts
                futures = []
                
                for language in self.languages:
                    # Only benchmark universal template system (legacy removed)
                    for complexity in self.complexity_configs.keys():
                        future = executor.submit(
                            self.benchmark_template_rendering,
                            language, "universal", complexity
                        )
                        futures.append((future, f"{language}_universal_{complexity}"))
                
                # Collect results
                for future, test_name in futures:
                    try:
                        results = future.result(timeout=180)  # 3 minute timeout
                        completed_tests += 1
                        
                        if progress:
                            progress.update(progress_task, 
                                          description=f"Completed {test_name}",
                                          advance=1)
                        else:
                            print(f"✓ Completed {test_name} ({completed_tests}/{total_tests})")
                            
                    except Exception as e:
                        if self.console:
                            self.console.print(f"[red]❌ Failed {test_name}: {e}[/red]")
                        completed_tests += 1
                        if progress:
                            progress.advance(progress_task)
        
        finally:
            if progress:
                progress.stop()
        
        # Analyze results
        analysis = self._analyze_template_performance()
        
        if self.console:
            self.console.print(f"\n[green]🏁 Template benchmark completed![/green]")
            self.console.print(f"[blue]📊 Collected {len(self.results)} measurements[/blue]")
        
        return analysis
    
    def _analyze_template_performance(self) -> Dict[str, Any]:
        """Analyze template rendering performance results"""
        analysis = {
            "summary": {
                "total_measurements": len(self.results),
                "languages_tested": len(set(r.language for r in self.results)),
                "template_systems_tested": len(set(r.template_system for r in self.results)),
                "complexity_levels": len(set(r.complexity for r in self.results))
            },
            "performance_comparison": {},
            "universal_performance": {},
            "scaling_analysis": {},
            "recommendations": []
        }
        
        # Group results by language and template system
        for language in self.languages:
            lang_results = [r for r in self.results if r.language == language]
            if not lang_results:
                continue
            
            # All results are universal system now
            universal_results = [r for r in lang_results if r.template_system == "universal"]
            
            # Calculate performance metrics for universal system
            analysis["performance_comparison"][language] = {
                "universal": self._calculate_performance_metrics(universal_results)
            }
            
            # Universal system performance analysis
            if universal_results:
                successful_results = [r for r in universal_results if r.build_success]
                if successful_results:
                    universal_avg = statistics.mean([r.render_time_ms for r in successful_results])
                    analysis["universal_performance"][language] = {
                        "avg_render_time_ms": universal_avg,
                        "total_builds": len(universal_results),
                        "successful_builds": len(successful_results),
                        "success_rate_pct": (len(successful_results) / len(universal_results)) * 100
                    }
        
        # Scaling analysis
        analysis["scaling_analysis"] = self._analyze_scaling_performance()
        
        # Generate recommendations
        analysis["recommendations"] = self._generate_template_recommendations(analysis)
        
        return analysis
    
    def _calculate_performance_metrics(self, results: List[TemplateRenderingResult]) -> Dict[str, Any]:
        """Calculate performance metrics for a set of results"""
        if not results:
            return {"status": "no_data"}
        
        successful_results = [r for r in results if r.build_success]
        if not successful_results:
            return {"status": "all_failed", "failure_count": len(results)}
        
        times = [r.render_time_ms for r in successful_results]
        
        return {
            "total_tests": len(results),
            "successful_tests": len(successful_results),
            "success_rate": len(successful_results) / len(results),
            "average_ms": statistics.mean(times),
            "median_ms": statistics.median(times),
            "min_ms": min(times),
            "max_ms": max(times),
            "std_dev_ms": statistics.stdev(times) if len(times) > 1 else 0,
            "total_files_generated": sum(r.generated_files for r in successful_results),
            "total_size_kb": sum(r.total_size_kb for r in successful_results)
        }
    
    def _analyze_scaling_performance(self) -> Dict[str, Any]:
        """Analyze how performance scales with complexity"""
        scaling = {}
        
        for language in self.languages:
            for template_system in ["universal"]:  # Legacy removed
                key = f"{language}_{template_system}"
                
                # Get results for each complexity level
                complexity_performance = {}
                for complexity in self.complexity_configs.keys():
                    results = [r for r in self.results 
                             if r.language == language 
                             and r.template_system == template_system 
                             and r.complexity == complexity 
                             and r.build_success]
                    
                    if results:
                        avg_time = statistics.mean([r.render_time_ms for r in results])
                        complexity_performance[complexity] = {
                            "avg_time_ms": avg_time,
                            "command_count": results[0].command_count
                        }
                
                if len(complexity_performance) >= 2:
                    # Calculate scaling factor
                    complexities = list(complexity_performance.keys())
                    times = [complexity_performance[c]["avg_time_ms"] for c in complexities]
                    commands = [complexity_performance[c]["command_count"] for c in complexities]
                    
                    # Simple linear scaling analysis
                    if len(times) > 1:
                        scaling_factor = (times[-1] - times[0]) / (commands[-1] - commands[0])
                        scaling[key] = {
                            "complexity_performance": complexity_performance,
                            "scaling_factor_ms_per_command": scaling_factor,
                            "scaling_quality": "linear" if scaling_factor < 5 else "super_linear"
                        }
        
        return scaling
    
    def _generate_template_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate template performance recommendations"""
        recommendations = []
        
        # Universal Template Performance comparison
        universal_performance = analysis.get("universal_performance", {})
        
        for language, comparison in universal_performance.items():
            # Analyze absolute performance metrics
            startup_time = comparison.get("startup_time_ms", 0)
            memory_usage = comparison.get("memory_usage_mb", 0)
            
            # Flag slow startup times (>100ms is poor for CLI tools)
            if startup_time > 100:
                recommendations.append(f"{language}: Slow startup time ({startup_time:.1f}ms). Consider lazy loading or reducing imports.")
            
            # Flag high memory usage (>50MB is excessive for CLI tools)  
            if memory_usage > 50:
                recommendations.append(f"{language}: High memory usage ({memory_usage:.1f}MB). Consider memory optimization.")
                
            # Flag good performance for positive reinforcement
            if startup_time <= 50 and memory_usage <= 20:
                recommendations.append(f"{language}: Excellent performance - {startup_time:.1f}ms startup, {memory_usage:.1f}MB memory.")
        
        # Scaling analysis
        scaling_analysis = analysis.get("scaling_analysis", {})
        poor_scaling = [key for key, data in scaling_analysis.items() 
                       if data.get("scaling_factor_ms_per_command", 0) > 10]
        
        if poor_scaling:
            recommendations.append(f"Poor scaling detected in: {', '.join(poor_scaling)}. Consider template optimization for large CLIs.")
        
        # Performance comparison
        perf_comparison = analysis.get("performance_comparison", {})
        slow_configs = []
        
        for language, systems in perf_comparison.items():
            for system, metrics in systems.items():
                if isinstance(metrics, dict) and metrics.get("average_ms", 0) > 5000:  # 5 second threshold
                    slow_configs.append(f"{language} {system}")
        
        if slow_configs:
            recommendations.append(f"Slow template rendering in: {', '.join(slow_configs)}. Review template complexity.")
        
        # Success rate issues
        low_success_configs = []
        for language, systems in perf_comparison.items():
            for system, metrics in systems.items():
                if isinstance(metrics, dict) and metrics.get("success_rate", 1.0) < 0.8:
                    low_success_configs.append(f"{language} {system}")
        
        if low_success_configs:
            recommendations.append(f"Low success rate in: {', '.join(low_success_configs)}. Check for template errors.")
        
        if not recommendations:
            recommendations.append("✅ Template rendering performance looks good across all configurations!")
        
        return recommendations
    
    def generate_benchmark_report(self, analysis: Dict[str, Any]) -> str:
        """Generate comprehensive template benchmark report"""
        report_lines = [
            "# Template Rendering Performance Benchmark Report",
            f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}",
            f"Iterations per test: {self.iterations}",
            ""
        ]
        
        # Executive Summary
        summary = analysis.get("summary", {})
        report_lines.extend([
            "## 📊 Executive Summary",
            f"- **Total Measurements**: {summary.get('total_measurements', 0)}",
            f"- **Languages Tested**: {summary.get('languages_tested', 0)}",
            f"- **Template Systems**: Universal Template Performance",
            f"- **Complexity Levels**: {summary.get('complexity_levels', 0)}",
            ""
        ])
        
        # Performance Comparison Table
        report_lines.extend([
            "## ⚡ Performance Comparison",
            "",
            "| Language | Template System | Avg Time (ms) | Success Rate | Files Generated |",
            "|----------|-----------------|---------------|--------------|-----------------|"
        ])
        
        perf_comparison = analysis.get("performance_comparison", {})
        for language, systems in perf_comparison.items():
            for system, metrics in systems.items():
                if isinstance(metrics, dict) and "average_ms" in metrics:
                    report_lines.append(
                        f"| {language.title()} | {system.title()} | "
                        f"{metrics['average_ms']:.1f} | {metrics['success_rate']:.1%} | "
                        f"{metrics.get('total_files_generated', 0)} |"
                    )
        
        report_lines.extend(["", ""])
        
        # Universal Template Performance Analysis
        universal_performance = analysis.get("universal_performance", {})
        if universal_performance:
            report_lines.extend(["## 🔄 Universal Template Performance Comparison", ""])
            
            for language, comparison in universal_performance.items():
                perf_diff = comparison.get("performance_difference_pct", 0)
                status = "🚀" if perf_diff < 0 else "⚠️" if perf_diff > 25 else "✅"
                
                report_lines.extend([
                    f"### {language.title()}",
                    f"- **Universal**: {comparison.get('universal_avg_ms', 0):.1f}ms",
                    f"- **Legacy**: {comparison.get('legacy_avg_ms', 0):.1f}ms",
                    f"- **Difference**: {perf_diff:+.1f}% {status}",
                    ""
                ])
        
        # Scaling Analysis
        scaling_analysis = analysis.get("scaling_analysis", {})
        if scaling_analysis:
            report_lines.extend(["## 📈 Performance Scaling Analysis", ""])
            
            for config, scaling_data in scaling_analysis.items():
                scaling_factor = scaling_data.get("scaling_factor_ms_per_command", 0)
                scaling_quality = scaling_data.get("scaling_quality", "unknown")
                
                report_lines.extend([
                    f"### {config.replace('_', ' ').title()}",
                    f"- **Scaling Factor**: {scaling_factor:.2f}ms per command",
                    f"- **Scaling Quality**: {scaling_quality.replace('_', ' ').title()}",
                    ""
                ])
        
        # Recommendations
        recommendations = analysis.get("recommendations", [])
        if recommendations:
            report_lines.extend(["## 💡 Performance Recommendations", ""])
            for i, rec in enumerate(recommendations, 1):
                report_lines.append(f"{i}. {rec}")
            report_lines.append("")
        
        # Raw Data
        report_lines.extend([
            "## 📄 Raw Benchmark Data",
            "```json"
        ])
        
        # Export results as JSON
        results_data = {
            "results": [asdict(r) for r in self.results],
            "analysis": analysis,
            "configuration": {
                "iterations": self.iterations,
                "complexity_configs": self.complexity_configs
            }
        }
        
        report_lines.append(json.dumps(results_data, indent=2))
        report_lines.extend(["```", ""])
        
        return "\n".join(report_lines)
    
    def save_results(self, analysis: Dict[str, Any]):
        """Save benchmark results to files"""
        # Save benchmark report
        report = self.generate_benchmark_report(analysis)
        report_file = self.output_dir / "template_benchmark_report.md"
        with open(report_file, 'w') as f:
            f.write(report)
        
        # Save raw results as JSON
        results_file = self.output_dir / "template_benchmark_results.json"
        results_data = {
            "results": [asdict(r) for r in self.results],
            "analysis": analysis
        }
        with open(results_file, 'w') as f:
            json.dump(results_data, f, indent=2)
        
        # Save CSV for analysis
        csv_file = self.output_dir / "template_benchmark.csv"
        with open(csv_file, 'w') as f:
            f.write("language,template_system,complexity,command_count,render_time_ms,build_success,generated_files,total_size_kb,iteration\n")
            for result in self.results:
                f.write(f"{result.language},{result.template_system},{result.complexity},"
                       f"{result.command_count},{result.render_time_ms},{result.build_success},"
                       f"{result.generated_files},{result.total_size_kb},{result.iteration}\n")
        
        if self.console:
            self.console.print(f"\n[green]📁 Template benchmark results saved to {self.output_dir}[/green]")


def main():
    """Main entry point for template benchmarking"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Template Rendering Performance Benchmark")
    parser.add_argument("--iterations", type=int, default=3, help="Number of test iterations")
    parser.add_argument("--output-dir", type=Path, default=Path("template_benchmark_results"),
                       help="Output directory")
    parser.add_argument("--complexity", choices=["simple", "medium", "complex", "extreme", "all"],
                       default="all", help="Complexity level to test")
    parser.add_argument("--language", choices=["python", "nodejs", "typescript", "all"],
                       default="all", help="Language to test")
    
    args = parser.parse_args()
    
    # Create benchmark
    benchmark = TemplateBenchmark(
        iterations=args.iterations,
        output_dir=args.output_dir
    )
    
    # Filter languages if specified
    if args.language != "all":
        benchmark.languages = [args.language]
    
    # Filter complexity if specified  
    if args.complexity != "all":
        benchmark.complexity_configs = {args.complexity: benchmark.complexity_configs[args.complexity]}
    
    # Run benchmark
    analysis = benchmark.run_comprehensive_benchmark()
    
    # Save results
    benchmark.save_results(analysis)
    
    # Check for performance issues
    recommendations = analysis.get("recommendations", [])
    performance_issues = [r for r in recommendations if "slower" in r or "Poor scaling" in r or "Slow template" in r]
    
    if performance_issues:
        print(f"\n⚠️ {len(performance_issues)} performance issues detected")
        return 1
    else:
        print(f"\n✅ Template rendering performance is acceptable across all configurations")
        return 0


if __name__ == "__main__":
    exit(main())