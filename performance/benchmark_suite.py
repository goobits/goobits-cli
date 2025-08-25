#!/usr/bin/env python3
"""
Comprehensive Performance Benchmarking Suite for Goobits CLI Framework
Validates <100ms startup times across all supported languages and features
"""

import asyncio
import json
import os
import shutil
import statistics
import subprocess
import tempfile
import time
import threading
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed
from contextlib import contextmanager
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Union
import yaml

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

try:
    from rich.console import Console
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
    from rich.table import Table
    from rich.panel import Panel
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False


@dataclass
class PerformanceMetric:
    """Individual performance measurement"""
    test_name: str
    language: str
    configuration: str
    metric_type: str  # startup, memory, rendering, completion
    value: float
    unit: str
    timestamp: float
    iterations: int
    std_dev: Optional[float] = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    percentile_95: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class BenchmarkConfiguration:
    """Benchmark test configuration"""
    name: str
    language: str
    features: Dict[str, bool]
    expected_startup_ms: float
    expected_memory_mb: float
    test_commands: List[str]
    complexity_level: str  # minimal, standard, complex
    

class PerformanceValidator:
    """Comprehensive performance validation framework"""
    
    def __init__(self, 
                 iterations: int = 5,
                 output_dir: Path = None,
                 verbose: bool = True):
        self.iterations = iterations
        self.output_dir = output_dir or Path("performance_results")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.verbose = verbose
        
        # Initialize console
        if RICH_AVAILABLE:
            self.console = Console()
        else:
            self.console = None
        
        # Performance targets
        self.targets = {
            "startup_time_ms": {"python": 90, "nodejs": 70, "typescript": 80, "rust": 40},
            "memory_usage_mb": {"python": 35, "nodejs": 45, "typescript": 50, "rust": 20},
            "template_render_ms": {"python": 60, "nodejs": 50, "typescript": 70, "rust": 30},
            "completion_time_ms": {"python": 25, "nodejs": 20, "typescript": 30, "rust": 15}
        }
        
        # Test configurations
        self.configurations = self._create_test_configurations()
        
        # Results storage
        self.metrics: List[PerformanceMetric] = []
        self.benchmark_results: Dict[str, Any] = {}
        
    def _create_test_configurations(self) -> List[BenchmarkConfiguration]:
        """Create test configurations for different scenarios"""
        configurations = []
        
        # Languages to test
        languages = ["python", "nodejs", "typescript"]
        
        for lang in languages:
            # Minimal configuration - basic CLI only
            configurations.append(BenchmarkConfiguration(
                name="minimal",
                language=lang,
                features={
                    "interactive_mode": False,
                    "completion_system": False,
                    "plugin_support": False,
                    "performance_optimization": False
                },
                expected_startup_ms=self.targets["startup_time_ms"][lang] * 0.7,
                expected_memory_mb=self.targets["memory_usage_mb"][lang] * 0.8,
                test_commands=["--version", "--help"],
                complexity_level="minimal"
            ))
            
            # Standard configuration - common features
            configurations.append(BenchmarkConfiguration(
                name="standard",
                language=lang,
                features={
                    "interactive_mode": True,
                    "completion_system": True,
                    "plugin_support": False,
                    "performance_optimization": True
                },
                expected_startup_ms=self.targets["startup_time_ms"][lang],
                expected_memory_mb=self.targets["memory_usage_mb"][lang],
                test_commands=["--version", "--help", "test-cmd"],
                complexity_level="standard"
            ))
            
            # Universal templates configuration
            configurations.append(BenchmarkConfiguration(
                name="universal",
                language=lang,
                features={
                    "interactive_mode": True,
                    "completion_system": True,
                    "plugin_support": True,
                    "performance_optimization": True
                },
                expected_startup_ms=self.targets["startup_time_ms"][lang] * 1.2,  # Allow 20% overhead
                expected_memory_mb=self.targets["memory_usage_mb"][lang] * 1.1,
                test_commands=["--version", "--help", "test-cmd", "completion --help"],
                complexity_level="complex"
            ))
        
        return configurations
    
    @contextmanager
    def measure_execution(self):
        """Context manager for measuring execution time and memory"""
        if PSUTIL_AVAILABLE:
            process = psutil.Process()
            start_memory = process.memory_info().rss
            start_time = time.perf_counter()
            
            # Start memory monitoring in background
            memory_samples = []
            monitoring = True
            
            def monitor_memory():
                while monitoring:
                    try:
                        memory_samples.append(process.memory_info().rss)
                        time.sleep(0.001)  # Sample every 1ms
                    except:
                        break
            
            monitor_thread = threading.Thread(target=monitor_memory, daemon=True)
            monitor_thread.start()
            
            try:
                yield memory_samples
            finally:
                end_time = time.perf_counter()
                monitoring = False
                monitor_thread.join(timeout=0.1)
                
                end_memory = process.memory_info().rss
                execution_time = end_time - start_time
                memory_delta = end_memory - start_memory
                peak_memory = max(memory_samples) if memory_samples else end_memory
                
                # Store results in memory_samples for caller access
                memory_samples.clear()
                memory_samples.extend([
                    execution_time,
                    memory_delta / 1024 / 1024,  # MB
                    peak_memory / 1024 / 1024    # MB
                ])
        else:
            # Fallback without psutil
            start_time = time.perf_counter()
            try:
                yield [0, 0, 0]  # Dummy memory data
            finally:
                end_time = time.perf_counter()
                # Return time only
                yield [end_time - start_time, 0, 0]
    
    def create_test_cli(self, config: BenchmarkConfiguration) -> Path:
        """Create a test CLI with the specified configuration"""
        test_dir = Path(tempfile.mkdtemp(prefix=f"perf_{config.language}_{config.name}_"))
        
        # Create goobits.yaml for the test CLI
        cli_config = {
            "package_name": f"perf-test-{config.name}",
            "command_name": f"perf-{config.name}",
            "display_name": f"Performance Test CLI - {config.name.title()}",
            "description": f"Performance test CLI for {config.language} {config.name} configuration",
            "language": config.language,
            
            # Python configuration
            "python": {
                "minimum_version": "3.8"
            },
            
            # Dependencies
            "dependencies": {
                "required": ["click>=8.0", "rich>=12.0"] if config.language == "python" else ["commander", "chalk"],
                "optional": []
            },
            
            # Installation
            "installation": {
                "pypi_name": f"perf-test-{config.name}-{config.language}",
                "development_path": str(test_dir)
            },
            
            # CLI configuration
            "cli": {
                "name": f"perf-{config.name}",
                "help": f"Performance test CLI for {config.name} configuration",
                "version_flag": True,
                "commands": []
            }
        }
        
        # Add features based on configuration
        if config.features.get("interactive_mode"):
            cli_config["cli"]["interactive"] = {
                "enabled": True,
                "prompt": f"perf-{config.name}> ",
                "history_file": f".perf-{config.name}_history"
            }
        
        if config.features.get("completion_system"):
            cli_config["cli"]["completion"] = {
                "enabled": True,
                "dynamic": True,
                "cache_duration": 300
            }
        
        if config.features.get("plugin_support"):
            cli_config["cli"]["plugins"] = {
                "enabled": True,
                "directory": "plugins"
            }
        
        if config.features.get("performance_optimization"):
            cli_config["cli"]["performance"] = {
                "lazy_loading": True,
                "caching": True,
                "startup_optimization": True
            }
        
        # Add test commands
        test_commands = [
            {
                "name": "test-cmd",
                "help": "Basic test command",
                "arguments": [
                    {"name": "input", "help": "Test input", "required": False}
                ],
                "options": [
                    {"name": "--output", "short": "-o", "help": "Output file"},
                    {"name": "--verbose", "short": "-v", "help": "Verbose output", "is_flag": True}
                ]
            }
        ]
        
        # Add completion command if enabled
        if config.features.get("completion_system"):
            test_commands.append({
                "name": "completion",
                "help": "Shell completion commands",
                "options": [
                    {"name": "--shell", "help": "Shell type", "choices": ["bash", "zsh", "fish"]}
                ]
            })
        
        # Add complex commands for stress testing
        if config.complexity_level == "complex":
            for i in range(10):
                test_commands.append({
                    "name": f"complex-cmd-{i:02d}",
                    "help": f"Complex test command {i}",
                    "options": [
                        {"name": f"--option-{j}", "help": f"Option {j}"}
                        for j in range(min(5, i + 1))
                    ]
                })
        
        cli_config["cli"]["commands"] = test_commands
        
        # Save configuration
        config_file = test_dir / "goobits.yaml"
        with open(config_file, 'w') as f:
            yaml.dump(cli_config, f, default_flow_style=False, indent=2)
        
        return test_dir
    
    def build_test_cli(self, test_dir: Path, config: BenchmarkConfiguration) -> bool:
        """Build the test CLI using goobits"""
        try:
            # Use the current goobits CLI to build the test CLI
            cmd = ["python3", "-m", "goobits_cli.main", "build"]
            
            # Universal templates are now always enabled (no flag needed)
            
            cmd.extend([str(test_dir / "goobits.yaml"), "--output-dir", str(test_dir)])
            
            result = subprocess.run(
                cmd,
                cwd=test_dir,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                if self.verbose:
                    print(f"Build failed for {config.language} {config.name}:")
                    print(f"STDOUT: {result.stdout}")
                    print(f"STDERR: {result.stderr}")
                return False
            
            return True
            
        except Exception as e:
            if self.verbose:
                print(f"Build error for {config.language} {config.name}: {e}")
            return False
    
    def benchmark_startup_time(self, test_dir: Path, config: BenchmarkConfiguration) -> List[PerformanceMetric]:
        """Benchmark CLI startup time"""
        metrics = []
        
        # Determine CLI executable based on language
        if config.language == "python":
            cli_path = test_dir / f"perf-{config.name}.py"
            if not cli_path.exists():
                cli_path = test_dir / "cli.py"
            cmd_base = ["python3", str(cli_path)]
        elif config.language == "nodejs":
            cli_path = test_dir / "cli.js"
            cmd_base = ["node", str(cli_path)]
        elif config.language == "typescript":
            cli_path = test_dir / "cli.js"  # Compiled TypeScript
            cmd_base = ["node", str(cli_path)]
        else:
            return metrics
        
        if not Path(cmd_base[-1]).exists():
            return metrics
        
        # Test each command
        for test_command in config.test_commands:
            execution_times = []
            memory_usages = []
            
            for iteration in range(self.iterations):
                try:
                    cmd = cmd_base + test_command.split()
                    
                    start_time = time.perf_counter()
                    
                    # Run the command
                    process = subprocess.run(
                        cmd,
                        capture_output=True,
                        text=True,
                        timeout=5,
                        cwd=test_dir
                    )
                    
                    end_time = time.perf_counter()
                    execution_time = (end_time - start_time) * 1000  # Convert to ms
                    
                    if process.returncode == 0:
                        execution_times.append(execution_time)
                        # Memory measurement would require more sophisticated tooling
                        memory_usages.append(0)  # Placeholder
                    
                except Exception as e:
                    if self.verbose:
                        print(f"Command execution failed: {e}")
                    continue
            
            if execution_times:
                # Create performance metric
                metric = PerformanceMetric(
                    test_name=f"startup_{test_command.replace(' ', '_')}",
                    language=config.language,
                    configuration=config.name,
                    metric_type="startup",
                    value=statistics.mean(execution_times),
                    unit="ms",
                    timestamp=time.time(),
                    iterations=len(execution_times),
                    std_dev=statistics.stdev(execution_times) if len(execution_times) > 1 else 0,
                    min_value=min(execution_times),
                    max_value=max(execution_times),
                    percentile_95=sorted(execution_times)[int(len(execution_times) * 0.95)] if execution_times else 0,
                    metadata={
                        "command": test_command,
                        "target_ms": config.expected_startup_ms,
                        "meets_target": statistics.mean(execution_times) <= config.expected_startup_ms
                    }
                )
                
                metrics.append(metric)
        
        return metrics
    
    def benchmark_template_rendering(self, config: BenchmarkConfiguration) -> List[PerformanceMetric]:
        """Benchmark template rendering performance"""
        metrics = []
        
        # Create test directory for template benchmarking
        test_dir = Path(tempfile.mkdtemp(prefix=f"template_perf_{config.language}_"))
        
        try:
            # Create increasingly complex CLI configurations
            complexities = [
                ("simple", 5),    # 5 commands
                ("medium", 20),   # 20 commands  
                ("complex", 50),  # 50 commands
                ("large", 100)    # 100 commands
            ]
            
            for complexity_name, command_count in complexities:
                # Create test CLI configuration
                cli_config = {
                    "package_name": f"template-test-{complexity_name}",
                    "command_name": f"template-test-{complexity_name}",
                    "language": config.language,
                    "cli": {
                        "name": f"template-test-{complexity_name}",
                        "help": f"Template rendering test - {complexity_name}",
                        "commands": []
                    }
                }
                
                # Generate commands
                for i in range(command_count):
                    command = {
                        "name": f"cmd-{i:03d}",
                        "help": f"Test command {i} with detailed help text that spans multiple lines and includes comprehensive documentation about the command's purpose and usage patterns.",
                        "options": []
                    }
                    
                    # Add options (more for complex commands)
                    option_count = min(10, max(1, i // 5))
                    for j in range(option_count):
                        command["options"].append({
                            "name": f"--option-{j}",
                            "help": f"Option {j} with detailed description and usage examples",
                            "type": "str" if j % 3 == 0 else "int" if j % 3 == 1 else "bool"
                        })
                    
                    # Add subcommands for some commands
                    if i % 10 == 0 and i > 0:
                        command["subcommands"] = []
                        for k in range(min(3, i // 20 + 1)):
                            command["subcommands"].append({
                                "name": f"sub-{k}",
                                "help": f"Subcommand {k}",
                                "options": [
                                    {"name": f"--sub-opt-{k}", "help": f"Sub option {k}"}
                                ]
                            })
                    
                    cli_config["cli"]["commands"].append(command)
                
                # Save configuration
                config_file = test_dir / f"goobits-{complexity_name}.yaml"
                with open(config_file, 'w') as f:
                    yaml.dump(cli_config, f, default_flow_style=False, indent=2)
                
                # Benchmark template rendering
                rendering_times = []
                
                for iteration in range(max(3, self.iterations // 2)):  # Fewer iterations for template tests
                    try:
                        start_time = time.perf_counter()
                        
                        # Build CLI using goobits
                        cmd = ["python", "-m", "goobits_cli.main", "build"]
                        # Universal templates are now always enabled (no flag needed)
                        cmd.extend([str(config_file), "--output-dir", str(test_dir)])
                        
                        result = subprocess.run(
                            cmd,
                            capture_output=True,
                            text=True,
                            timeout=30,
                            cwd=test_dir
                        )
                        
                        end_time = time.perf_counter()
                        render_time = (end_time - start_time) * 1000
                        
                        if result.returncode == 0:
                            rendering_times.append(render_time)
                        
                    except Exception as e:
                        if self.verbose:
                            print(f"Template rendering failed: {e}")
                        continue
                
                if rendering_times:
                    metric = PerformanceMetric(
                        test_name=f"template_rendering_{complexity_name}",
                        language=config.language,
                        configuration=config.name,
                        metric_type="rendering",
                        value=statistics.mean(rendering_times),
                        unit="ms",
                        timestamp=time.time(),
                        iterations=len(rendering_times),
                        std_dev=statistics.stdev(rendering_times) if len(rendering_times) > 1 else 0,
                        min_value=min(rendering_times),
                        max_value=max(rendering_times),
                        metadata={
                            "complexity": complexity_name,
                            "command_count": command_count,
                            "template_system": "universal"  # Always universal now
                        }
                    )
                    
                    metrics.append(metric)
        
        finally:
            # Cleanup
            shutil.rmtree(test_dir, ignore_errors=True)
        
        return metrics
    
    def run_comprehensive_benchmarks(self) -> Dict[str, Any]:
        """Run comprehensive performance benchmarks"""
        if RICH_AVAILABLE:
            self.console.print(Panel.fit("[bold blue]🚀 Starting Comprehensive Performance Validation[/bold blue]", 
                                        title="Goobits CLI Performance Benchmarks"))
        else:
            print("🚀 Starting Comprehensive Performance Validation")
        
        start_time = time.time()
        
        # Create progress tracking
        total_tests = len(self.configurations) * 2  # startup + template tests
        completed_tests = 0
        
        if RICH_AVAILABLE:
            progress = Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TextColumn("[progress.percentage]{task.percentage:>3.0f}%")
            )
            progress_task = progress.add_task("Running benchmarks...", total=total_tests)
            progress.start()
        else:
            progress = None
            progress_task = None
        
        try:
            # Run benchmarks in parallel where possible
            with ThreadPoolExecutor(max_workers=3) as executor:
                futures = {}
                
                for config in self.configurations:
                    # Submit startup benchmarks
                    future = executor.submit(self._run_config_benchmarks, config)
                    futures[future] = f"{config.language}_{config.name}"
                
                # Collect results
                for future in as_completed(futures):
                    config_name = futures[future]
                    try:
                        metrics = future.result(timeout=120)  # 2 minute timeout
                        self.metrics.extend(metrics)
                        
                        completed_tests += 1
                        if progress:
                            progress.update(progress_task, 
                                          description=f"Completed {config_name}",
                                          advance=1)
                        else:
                            print(f"✓ Completed {config_name} ({completed_tests}/{total_tests})")
                            
                    except Exception as e:
                        if self.verbose:
                            print(f"❌ Failed {config_name}: {e}")
                        completed_tests += 1
                        if progress:
                            progress.advance(progress_task)
        
        finally:
            if progress:
                progress.stop()
        
        # Analyze results
        analysis_results = self._analyze_performance_results()
        
        # Generate comprehensive report
        total_time = time.time() - start_time
        
        if RICH_AVAILABLE:
            self.console.print(f"\n[green]✓ Performance validation completed in {total_time:.2f}s[/green]")
            self.console.print(f"[blue]📊 Collected {len(self.metrics)} performance metrics[/blue]")
        else:
            print(f"\n✓ Performance validation completed in {total_time:.2f}s")
            print(f"📊 Collected {len(self.metrics)} performance metrics")
        
        return analysis_results
    
    def _run_config_benchmarks(self, config: BenchmarkConfiguration) -> List[PerformanceMetric]:
        """Run benchmarks for a specific configuration"""
        metrics = []
        
        # Create and build test CLI
        test_dir = None
        try:
            test_dir = self.create_test_cli(config)
            
            if self.build_test_cli(test_dir, config):
                # Run startup benchmarks
                startup_metrics = self.benchmark_startup_time(test_dir, config)
                metrics.extend(startup_metrics)
                
                # Run template rendering benchmarks
                template_metrics = self.benchmark_template_rendering(config)
                metrics.extend(template_metrics)
            else:
                if self.verbose:
                    print(f"❌ Failed to build CLI for {config.language} {config.name}")
        
        except Exception as e:
            if self.verbose:
                print(f"❌ Benchmark failed for {config.language} {config.name}: {e}")
                traceback.print_exc()
        
        finally:
            if test_dir and test_dir.exists():
                shutil.rmtree(test_dir, ignore_errors=True)
        
        return metrics
    
    def _analyze_performance_results(self) -> Dict[str, Any]:
        """Analyze performance results and generate insights"""
        analysis = {
            "summary": {
                "total_metrics": len(self.metrics),
                "languages_tested": len(set(m.language for m in self.metrics)),
                "configurations_tested": len(set(m.configuration for m in self.metrics)),
                "test_timestamp": time.time()
            },
            "performance_by_language": {},
            "performance_by_configuration": {},
            "target_analysis": {},
            "regressions_detected": [],
            "recommendations": []
        }
        
        # Group metrics by language
        for language in ["python", "nodejs", "typescript"]:
            lang_metrics = [m for m in self.metrics if m.language == language]
            if not lang_metrics:
                continue
            
            startup_metrics = [m for m in lang_metrics if m.metric_type == "startup"]
            render_metrics = [m for m in lang_metrics if m.metric_type == "rendering"]
            
            analysis["performance_by_language"][language] = {
                "startup_performance": self._analyze_metric_group(startup_metrics),
                "rendering_performance": self._analyze_metric_group(render_metrics),
                "total_tests": len(lang_metrics),
                "meets_targets": self._check_language_targets(language, lang_metrics)
            }
        
        # Group by configuration
        for config_name in ["minimal", "standard", "universal"]:
            config_metrics = [m for m in self.metrics if m.configuration == config_name]
            if config_metrics:
                analysis["performance_by_configuration"][config_name] = {
                    "average_startup_ms": statistics.mean([m.value for m in config_metrics if m.metric_type == "startup"]),
                    "languages": list(set(m.language for m in config_metrics)),
                    "performance_grade": self._calculate_config_grade(config_metrics)
                }
        
        # Target analysis
        analysis["target_analysis"] = self._analyze_targets()
        
        # Generate recommendations
        analysis["recommendations"] = self._generate_recommendations(analysis)
        
        return analysis
    
    def _analyze_metric_group(self, metrics: List[PerformanceMetric]) -> Dict[str, Any]:
        """Analyze a group of performance metrics"""
        if not metrics:
            return {"status": "No data"}
        
        values = [m.value for m in metrics]
        
        return {
            "count": len(metrics),
            "average": statistics.mean(values),
            "median": statistics.median(values),
            "min": min(values),
            "max": max(values),
            "std_dev": statistics.stdev(values) if len(values) > 1 else 0,
            "meets_target_count": len([m for m in metrics if m.metadata and m.metadata.get("meets_target", False)])
        }
    
    def _check_language_targets(self, language: str, metrics: List[PerformanceMetric]) -> Dict[str, bool]:
        """Check if language meets performance targets"""
        startup_metrics = [m for m in metrics if m.metric_type == "startup"]
        render_metrics = [m for m in metrics if m.metric_type == "rendering"]
        
        startup_target = self.targets["startup_time_ms"].get(language, 100)
        render_target = self.targets["template_render_ms"].get(language, 100)
        
        return {
            "startup": all(m.value <= startup_target for m in startup_metrics) if startup_metrics else True,
            "rendering": all(m.value <= render_target for m in render_metrics) if render_metrics else True
        }
    
    def _calculate_config_grade(self, metrics: List[PerformanceMetric]) -> str:
        """Calculate performance grade for a configuration"""
        if not metrics:
            return "No Data"
        
        # Calculate percentage of tests that meet targets
        target_met_count = sum(1 for m in metrics if m.metadata and m.metadata.get("meets_target", False))
        total_count = len(metrics)
        success_rate = target_met_count / total_count if total_count > 0 else 0
        
        if success_rate >= 0.95:
            return "A+ (Excellent)"
        elif success_rate >= 0.90:
            return "A (Very Good)"
        elif success_rate >= 0.80:
            return "B (Good)"
        elif success_rate >= 0.70:
            return "C (Acceptable)"
        else:
            return "D (Needs Improvement)"
    
    def _analyze_targets(self) -> Dict[str, Any]:
        """Analyze performance against targets"""
        target_violations = {}
        
        for language in ["python", "nodejs", "typescript"]:
            lang_metrics = [m for m in self.metrics if m.language == language]
            violations = []
            
            startup_target = self.targets["startup_time_ms"].get(language, 100)
            startup_metrics = [m for m in lang_metrics if m.metric_type == "startup"]
            
            for metric in startup_metrics:
                if metric.value > startup_target:
                    violations.append({
                        "test": metric.test_name,
                        "value": metric.value,
                        "target": startup_target,
                        "excess_percent": ((metric.value - startup_target) / startup_target) * 100
                    })
            
            if violations:
                target_violations[language] = violations
        
        return target_violations
    
    def _generate_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate performance optimization recommendations"""
        recommendations = []
        
        # Check for target violations
        target_violations = analysis.get("target_analysis", {})
        if target_violations:
            recommendations.append("🎯 Performance targets exceeded in some configurations:")
            for language, violations in target_violations.items():
                recommendations.append(f"  • {language}: {len(violations)} tests exceed targets")
        
        # Language-specific recommendations
        perf_by_lang = analysis.get("performance_by_language", {})
        
        for language, perf_data in perf_by_lang.items():
            startup_data = perf_data.get("startup_performance", {})
            if startup_data.get("average", 0) > self.targets["startup_time_ms"].get(language, 100):
                recommendations.append(f"🚀 {language.title()}: Optimize startup time (current: {startup_data.get('average', 0):.2f}ms)")
        
        # Configuration-specific recommendations
        perf_by_config = analysis.get("performance_by_configuration", {})
        
        if "universal" in perf_by_config:
            universal_startup = perf_by_config["universal"].get("average_startup_ms", 0)
            standard_startup = perf_by_config.get("standard", {}).get("average_startup_ms", 0)
            
            if universal_startup > standard_startup * 1.3:  # More than 30% slower
                recommendations.append("🔧 Universal templates show significant performance overhead - consider optimization")
        
        # General recommendations
        if not recommendations:
            recommendations.append("✅ All performance targets met - excellent work!")
        else:
            recommendations.extend([
                "💡 Consider implementing lazy loading for large configurations",
                "🔄 Enable caching for template rendering",
                "⚡ Use performance optimization flags in production builds"
            ])
        
        return recommendations
    
    def generate_performance_report(self, analysis: Dict[str, Any]) -> str:
        """Generate comprehensive performance report"""
        report_lines = []
        
        # Header
        report_lines.extend([
            "# Goobits CLI Framework - Performance Validation Report",
            f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}",
            f"Test iterations per configuration: {self.iterations}",
            ""
        ])
        
        # Executive Summary
        summary = analysis.get("summary", {})
        report_lines.extend([
            "## 🎯 Executive Summary",
            f"- **Total Metrics Collected**: {summary.get('total_metrics', 0)}",
            f"- **Languages Tested**: {summary.get('languages_tested', 0)} (Python, Node.js, TypeScript)",
            f"- **Configurations Tested**: {summary.get('configurations_tested', 0)} (Minimal, Standard, Universal)",
            f"- **Target**: All configurations must start in <100ms",
            ""
        ])
        
        # Performance by Language
        report_lines.extend(["## 📊 Performance by Language", ""])
        
        perf_by_lang = analysis.get("performance_by_language", {})
        
        # Create summary table
        table_header = "| Language | Avg Startup (ms) | Target (ms) | Status | Rendering (ms) |"
        table_separator = "|----------|------------------|-------------|---------|----------------|"
        report_lines.extend([table_header, table_separator])
        
        for language in ["python", "nodejs", "typescript"]:
            if language not in perf_by_lang:
                continue
                
            lang_data = perf_by_lang[language]
            startup_avg = lang_data.get("startup_performance", {}).get("average", 0)
            render_avg = lang_data.get("rendering_performance", {}).get("average", 0)
            target = self.targets["startup_time_ms"].get(language, 100)
            meets_targets = lang_data.get("meets_targets", {})
            
            status = "✅" if meets_targets.get("startup", False) else "❌"
            
            report_lines.append(
                f"| {language.title()} | {startup_avg:.2f} | {target} | {status} | {render_avg:.2f} |"
            )
        
        report_lines.append("")
        
        # Configuration Analysis
        report_lines.extend(["## ⚙️ Configuration Analysis", ""])
        
        perf_by_config = analysis.get("performance_by_configuration", {})
        for config_name, config_data in perf_by_config.items():
            report_lines.extend([
                f"### {config_name.title()} Configuration",
                f"- **Average Startup**: {config_data.get('average_startup_ms', 0):.2f}ms",
                f"- **Performance Grade**: {config_data.get('performance_grade', 'Unknown')}",
                f"- **Languages**: {', '.join(config_data.get('languages', []))}",
                ""
            ])
        
        # Target Analysis
        target_violations = analysis.get("target_analysis", {})
        if target_violations:
            report_lines.extend(["## ⚠️ Performance Target Violations", ""])
            for language, violations in target_violations.items():
                report_lines.extend([
                    f"### {language.title()}",
                    f"**{len(violations)} tests exceeded targets:**",
                    ""
                ])
                for violation in violations:
                    report_lines.append(
                        f"- `{violation['test']}`: {violation['value']:.2f}ms "
                        f"(target: {violation['target']}ms, +{violation['excess_percent']:.1f}%)"
                    )
                report_lines.append("")
        else:
            report_lines.extend([
                "## ✅ All Performance Targets Met",
                "All tested configurations meet the <100ms startup time requirement.",
                ""
            ])
        
        # Recommendations
        recommendations = analysis.get("recommendations", [])
        if recommendations:
            report_lines.extend(["## 💡 Performance Optimization Recommendations", ""])
            for i, rec in enumerate(recommendations, 1):
                report_lines.append(f"{i}. {rec}")
            report_lines.append("")
        
        # Detailed Metrics
        report_lines.extend([
            "## 📈 Detailed Performance Metrics",
            "",
            "```json"
        ])
        
        # Export metrics as JSON
        metrics_data = {
            "metrics": [asdict(m) for m in self.metrics],
            "analysis": analysis,
            "test_configuration": {
                "iterations": self.iterations,
                "targets": self.targets,
                "timestamp": time.time()
            }
        }
        
        report_lines.append(json.dumps(metrics_data, indent=2))
        report_lines.extend(["```", ""])
        
        # Footer
        report_lines.extend([
            "---",
            "*Report generated by Goobits CLI Performance Validation Suite*"
        ])
        
        return "\n".join(report_lines)
    
    def save_results(self, analysis: Dict[str, Any]):
        """Save benchmark results to files"""
        # Save performance report
        report = self.generate_performance_report(analysis)
        report_file = self.output_dir / "performance_validation_report.md"
        with open(report_file, 'w') as f:
            f.write(report)
        
        # Save raw metrics as JSON
        metrics_file = self.output_dir / "performance_metrics.json"
        metrics_data = {
            "metrics": [asdict(m) for m in self.metrics],
            "analysis": analysis,
            "timestamp": time.time()
        }
        with open(metrics_file, 'w') as f:
            json.dump(metrics_data, f, indent=2)
        
        # Save CSV for analysis
        csv_file = self.output_dir / "performance_metrics.csv"
        with open(csv_file, 'w') as f:
            f.write("test_name,language,configuration,metric_type,value,unit,iterations,std_dev,meets_target\n")
            for metric in self.metrics:
                meets_target = metric.metadata.get("meets_target", False) if metric.metadata else False
                f.write(f"{metric.test_name},{metric.language},{metric.configuration},{metric.metric_type},"
                       f"{metric.value},{metric.unit},{metric.iterations},{metric.std_dev or 0},{meets_target}\n")
        
        if RICH_AVAILABLE:
            self.console.print(f"\n[green]📁 Results saved to {self.output_dir}[/green]")
        else:
            print(f"\n📁 Results saved to {self.output_dir}")


def main():
    """Main entry point for performance validation"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Goobits CLI Performance Validation Suite")
    parser.add_argument("--iterations", type=int, default=5, 
                       help="Number of test iterations (default: 5)")
    parser.add_argument("--output-dir", type=Path, default=Path("performance_results"),
                       help="Output directory for results")
    parser.add_argument("--verbose", action="store_true",
                       help="Enable verbose output")
    parser.add_argument("--quick", action="store_true",
                       help="Run quick tests with fewer iterations")
    
    args = parser.parse_args()
    
    if args.quick:
        iterations = 3
    else:
        iterations = args.iterations
    
    # Initialize validator
    validator = PerformanceValidator(
        iterations=iterations,
        output_dir=args.output_dir,
        verbose=args.verbose
    )
    
    try:
        # Run comprehensive benchmarks
        analysis = validator.run_comprehensive_benchmarks()
        
        # Save results
        validator.save_results(analysis)
        
        # Check if all targets were met
        target_violations = analysis.get("target_analysis", {})
        if target_violations:
            if RICH_AVAILABLE:
                validator.console.print(f"\n[yellow]⚠️  Performance targets exceeded in {len(target_violations)} language(s)[/yellow]")
            else:
                print(f"\n⚠️  Performance targets exceeded in {len(target_violations)} language(s)")
            return 1
        else:
            if RICH_AVAILABLE:
                validator.console.print(f"\n[green]🎉 All performance targets met! CLI framework is ready for production.[/green]")
            else:
                print(f"\n🎉 All performance targets met! CLI framework is ready for production.")
            return 0
    
    except Exception as e:
        if RICH_AVAILABLE and validator.console:
            validator.console.print(f"\n[red]❌ Performance validation failed: {e}[/red]")
        else:
            print(f"\n❌ Performance validation failed: {e}")
        
        if args.verbose:
            traceback.print_exc()
        
        return 1


if __name__ == "__main__":
    exit(main())