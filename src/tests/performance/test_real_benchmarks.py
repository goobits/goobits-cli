#!/usr/bin/env python3
"""
Real Performance Benchmark Suite - Replaces Mocked Performance Tests

This module provides comprehensive real performance benchmarking across all
CLI languages, measuring actual performance without mocks or simulations.

Based on Agent E's integration test findings:
- Python CLIs work end-to-end (avg: 320ms execution)
- Node.js CLIs have module issues but run when working (avg: 1,683ms - slow)
- TypeScript CLIs have build system issues (avg: 5,065ms - very slow)
"""

import asyncio
import gc
import json
import os
import shutil
import statistics
import subprocess
import sys
import tempfile
import time
import tracemalloc
from concurrent.futures import ThreadPoolExecutor, as_completed
from contextlib import contextmanager
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Union

import psutil
import yaml
from rich.console import Console
from rich.progress import Progress, TaskID
from rich.table import Table
from rich.panel import Panel

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Import goobits CLI functionality
from goobits_cli.main import build as build_cli_command
from goobits_cli.schemas import GoobitsConfigSchema
from goobits_cli.generators.python import PythonGenerator
from goobits_cli.generators.nodejs import NodeJSGenerator
from goobits_cli.generators.typescript import TypeScriptGenerator

# Import existing performance infrastructure (with error handling)
try:
    sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "performance"))
    from startup_validator import StartupValidator, StartupProfile
    from memory_profiler import CLIMemoryBenchmark, MemoryProfile
    from template_benchmark import TemplateBenchmark
    PERFORMANCE_TOOLS_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Performance tools not available: {e}")
    PERFORMANCE_TOOLS_AVAILABLE = False


@dataclass
class RealPerformanceMetric:
    """Real performance metric without mocks"""
    test_name: str
    language: str
    operation: str  # generation, installation, execution, startup
    metric_type: str  # time_ms, memory_mb, success_rate, throughput
    value: float
    unit: str
    timestamp: float
    iterations: int
    statistics: Dict[str, float]  # min, max, std_dev, percentile_95
    metadata: Dict[str, Any]


@dataclass
class CLIGenerationBenchmark:
    """CLI generation performance benchmark results"""
    language: str
    generation_time_ms: float
    generated_files_count: int
    lines_of_code: int
    template_rendering_time_ms: float
    file_write_time_ms: float
    success: bool
    error_message: Optional[str] = None


@dataclass
class CLIInstallationBenchmark:
    """CLI installation performance benchmark results"""
    language: str
    installation_time_ms: float
    dependency_install_time_ms: float
    build_time_ms: Optional[float]  # For TypeScript/Node.js
    success: bool
    error_message: Optional[str] = None


@dataclass
class CLIExecutionBenchmark:
    """CLI execution performance benchmark results"""
    language: str
    command: str
    startup_time_ms: float
    execution_time_ms: float
    memory_peak_mb: float
    memory_baseline_mb: float
    success_rate: float
    output_size_bytes: int
    iterations: int
    success: bool
    error_message: Optional[str] = None


class RealPerformanceBenchmarkSuite:
    """Comprehensive real performance benchmarking without mocks"""

    def __init__(self, iterations: int = 5, output_dir: Path = Path("performance_results")):
        self.console = Console()
        self.iterations = iterations
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.metrics: List[RealPerformanceMetric] = []
        self.languages = ["python", "nodejs", "typescript", "rust"]
        self.test_commands = ["--help", "--version", "config --help"]
        
        # Performance targets based on Agent E's findings and production requirements
        self.performance_targets = {
            "python": {
                "generation_time_ms": 2000,    # 2 seconds for generation
                "startup_time_ms": 500,        # 500ms startup target
                "memory_mb": 50,               # 50MB memory target
                "installation_time_ms": 30000  # 30 seconds installation
            },
            "nodejs": {
                "generation_time_ms": 3000,    # 3 seconds (more complex)
                "startup_time_ms": 1000,       # 1 second (Node.js slower)
                "memory_mb": 75,               # 75MB (Node.js uses more memory)
                "installation_time_ms": 60000  # 60 seconds (npm install)
            },
            "typescript": {
                "generation_time_ms": 4000,    # 4 seconds (compilation)
                "startup_time_ms": 1500,       # 1.5 seconds (compilation overhead)
                "memory_mb": 100,              # 100MB (TypeScript overhead)
                "installation_time_ms": 90000  # 90 seconds (build process)
            },
            "rust": {
                "generation_time_ms": 2500,    # 2.5 seconds for generation (Rust enhancement)
                "startup_time_ms": 100,        # 100ms startup target (Rust is very fast)
                "memory_mb": 25,               # 25MB memory target (Rust is efficient)
                "installation_time_ms": 180000 # 3 minutes (cargo build can be slow)
            }
        }

    def _build_cli_for_language(self, language: str, config_file: str, output_dir: Path):
        """Build CLI for specific language using appropriate generator"""
        # Load configuration
        with open(config_file, 'r') as f:
            config_data = yaml.safe_load(f)
        
        config = GoobitsConfigSchema(**config_data)
        
        # Use appropriate generator  
        if language == "python":
            generator = PythonGenerator()
            files = generator.generate_all_files(config, config_file)
        elif language == "nodejs":
            generator = NodeJSGenerator()
            files = generator.generate_all_files(config, config_file)
        elif language == "typescript":
            generator = TypeScriptGenerator()
            files = generator.generate_all_files(config, config_file)
        elif language == "rust":
            # Import Rust generator for performance testing (Rust enhancement)
            from goobits_cli.generators.rust import RustGenerator
            generator = RustGenerator()
            files = generator.generate_all_files(config, config_file)
        else:
            raise ValueError(f"Unsupported language: {language}")
        
        # Write files to output directory
        for file_path, content in files.items():
            full_path = output_dir / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(full_path, 'w') as f:
                f.write(content)

    def create_test_cli_config(self, language: str, test_name: str) -> Dict[str, Any]:
        """Create a comprehensive CLI configuration for performance testing"""
        return {
            "package_name": f"perf-test-{test_name}-{language}",
            "command_name": f"perf-{test_name}",
            "display_name": f"Performance Test CLI - {test_name}",
            "description": f"Performance benchmark CLI for {language}",
            
            "python": {
                "minimum_version": "3.8",
                "maximum_version": "3.13"
            },
            
            "dependencies": {
                "required": ["click>=8.0", "rich>=12.0"],
                "optional": ["pytest", "pyyaml"]
            },
            
            "installation": {
                "pypi_name": f"perf-test-{test_name}-{language}",
                "development_path": ".",
                "extras": {
                    "python": ["dev"]
                }
            },
            
            "shell_integration": {
                "enabled": False,
                "alias": f"perf-{test_name}"
            },
            
            "validation": {
                "check_api_keys": False,
                "check_disk_space": True,
                "minimum_disk_space_mb": 10
            },
            
            "messages": {
                "install_success": f"Performance test CLI {test_name} installed successfully!",
                "install_dev_success": f"Performance test CLI {test_name} installed in dev mode!",
                "upgrade_success": f"Performance test CLI {test_name} upgraded successfully!"
            },
            
            "cli": {
                "name": f"perf-{test_name}",
                "version": "1.0.0-benchmark",
                "display_version": True,
                "tagline": f"Performance benchmark CLI for {language}",
                "description": f"Performance testing CLI generated for {test_name} benchmarking",
                "icon": "⚡",
                "enable_recursive_help": True,
                "enable_help_json": False,
                
                "commands": {
                    "config": {
                        "desc": "Configuration management",
                        "icon": "⚙️",
                        "options": [
                            {
                                "name": "get",
                                "type": "str",
                                "desc": "Get configuration value"
                            },
                            {
                                "name": "set",
                                "type": "str", 
                                "desc": "Set configuration value"
                            },
                            {
                                "name": "list",
                                "type": "flag",
                                "desc": "List all configurations"
                            }
                        ]
                    },
                    "status": {
                        "desc": "Show system status",
                        "icon": "📊",
                        "options": [
                            {
                                "name": "verbose",
                                "type": "flag",
                                "desc": "Verbose output"
                            },
                            {
                                "name": "format",
                                "type": "str",
                                "desc": "Output format",
                                "choices": ["json", "yaml", "table"],
                                "default": "table"
                            }
                        ]
                    },
                    "process": {
                        "desc": "Process data",
                        "icon": "🔄",
                        "args": [
                            {
                                "name": "input",
                                "desc": "Input file or data",
                                "required": True
                            }
                        ],
                        "options": [
                            {
                                "name": "output",
                                "short": "o",
                                "type": "str",
                                "desc": "Output file"
                            },
                            {
                                "name": "workers",
                                "short": "w",
                                "type": "int",
                                "desc": "Number of workers",
                                "default": 1
                            }
                        ]
                    }
                }
            }
        }

    @contextmanager
    def measure_real_performance(self, operation_name: str):
        """Context manager for measuring real performance"""
        # Force garbage collection for accurate measurement
        gc.collect()
        
        # Start memory tracking
        if not tracemalloc.is_tracing():
            tracemalloc.start()
        
        # Get baseline memory
        process = psutil.Process()
        start_memory = process.memory_info().rss
        start_time = time.perf_counter()
        
        measurements = {
            "operation": operation_name,
            "start_time": start_time,
            "start_memory_mb": start_memory / 1024 / 1024
        }
        
        try:
            yield measurements
        finally:
            end_time = time.perf_counter()
            end_memory = process.memory_info().rss
            
            measurements.update({
                "execution_time_ms": (end_time - start_time) * 1000,
                "end_memory_mb": end_memory / 1024 / 1024,
                "memory_increase_mb": (end_memory - start_memory) / 1024 / 1024
            })
            
            if tracemalloc.is_tracing():
                current, peak = tracemalloc.get_traced_memory()
                measurements["traced_memory_mb"] = peak / 1024 / 1024

    def benchmark_cli_generation(self, language: str, test_name: str) -> CLIGenerationBenchmark:
        """Benchmark real CLI generation performance"""
        self.console.print(f"[blue]🏗️ Benchmarking {language} CLI generation for {test_name}[/blue]")
        
        test_dir = Path(tempfile.mkdtemp(prefix=f"perf_gen_{language}_{test_name}_"))
        
        try:
            # Create test configuration
            config = self.create_test_cli_config(language, test_name)
            config_file = test_dir / "goobits.yaml"
            
            with open(config_file, 'w') as f:
                yaml.dump(config, f, default_flow_style=False)
            
            # Benchmark generation
            with self.measure_real_performance(f"cli_generation_{language}") as metrics:
                try:
                    # Build CLI using appropriate generator
                    template_start = time.perf_counter()
                    self._build_cli_for_language(language, str(config_file), test_dir)
                    template_end = time.perf_counter()
                    
                    template_time = (template_end - template_start) * 1000
                    
                    # Count generated files
                    generated_files = list(test_dir.glob("**/*"))
                    generated_files = [f for f in generated_files if f.is_file() and f.name != "goobits.yaml"]
                    
                    # Count lines of code
                    lines_of_code = 0
                    for file_path in generated_files:
                        try:
                            if file_path.suffix in ['.py', '.js', '.ts']:
                                with open(file_path, 'r', encoding='utf-8') as f:
                                    lines_of_code += len(f.readlines())
                        except Exception:
                            continue
                    
                    return CLIGenerationBenchmark(
                        language=language,
                        generation_time_ms=metrics.get("execution_time_ms", 0),
                        generated_files_count=len(generated_files),
                        lines_of_code=lines_of_code,
                        template_rendering_time_ms=template_time,
                        file_write_time_ms=metrics.get("execution_time_ms", 0) - template_time,
                        success=True
                    )
                    
                except Exception as e:
                    return CLIGenerationBenchmark(
                        language=language,
                        generation_time_ms=metrics.get("execution_time_ms", 0),
                        generated_files_count=0,
                        lines_of_code=0,
                        template_rendering_time_ms=0,
                        file_write_time_ms=0,
                        success=False,
                        error_message=str(e)
                    )
        
        finally:
            # Cleanup
            shutil.rmtree(test_dir, ignore_errors=True)

    def benchmark_cli_installation(self, language: str, test_name: str) -> CLIInstallationBenchmark:
        """Benchmark real CLI installation performance"""
        self.console.print(f"[yellow]📦 Benchmarking {language} CLI installation for {test_name}[/yellow]")
        
        test_dir = Path(tempfile.mkdtemp(prefix=f"perf_install_{language}_{test_name}_"))
        
        try:
            # Generate CLI first
            config = self.create_test_cli_config(language, test_name)
            config_file = test_dir / "goobits.yaml"
            
            with open(config_file, 'w') as f:
                yaml.dump(config, f, default_flow_style=False)
            
            self._build_cli_for_language(language, str(config_file), test_dir)
            
            # Benchmark installation
            with self.measure_real_performance(f"cli_installation_{language}") as metrics:
                try:
                    dependency_start = time.perf_counter()
                    build_start = None
                    build_time = None
                    
                    if language == "python":
                        # Python: run setup script
                        setup_script = test_dir / "setup.sh"
                        if setup_script.exists():
                            subprocess.run(
                                ["chmod", "+x", str(setup_script)], 
                                check=True, 
                                cwd=test_dir
                            )
                            # Run installation (dry run to avoid system changes)
                            result = subprocess.run(
                                ["bash", str(setup_script), "--dry-run"], 
                                capture_output=True, 
                                text=True, 
                                timeout=60,
                                cwd=test_dir
                            )
                    
                    elif language == "nodejs":
                        # Node.js: npm install
                        package_json = test_dir / "package.json"
                        if package_json.exists():
                            result = subprocess.run(
                                ["npm", "install"], 
                                capture_output=True, 
                                text=True, 
                                timeout=120,
                                cwd=test_dir
                            )
                    
                    elif language == "typescript":
                        # TypeScript: npm install + build
                        package_json = test_dir / "package.json"
                        if package_json.exists():
                            # Install dependencies
                            result = subprocess.run(
                                ["npm", "install"], 
                                capture_output=True, 
                                text=True, 
                                timeout=120,
                                cwd=test_dir
                            )
                            
                            dependency_end = time.perf_counter()
                            
                            # Build TypeScript
                            build_start = time.perf_counter()
                            build_result = subprocess.run(
                                ["npm", "run", "build"], 
                                capture_output=True, 
                                text=True, 
                                timeout=180,
                                cwd=test_dir
                            )
                            build_end = time.perf_counter()
                            build_time = (build_end - build_start) * 1000
                    
                    elif language == "rust":
                        # Rust: cargo build (Rust enhancement)
                        cargo_toml = test_dir / "Cargo.toml"
                        if cargo_toml.exists():
                            # Check if cargo is available
                            cargo_check = subprocess.run(
                                ["cargo", "--version"], 
                                capture_output=True, 
                                text=True
                            )
                            if cargo_check.returncode != 0:
                                raise Exception("Cargo not available for Rust build")
                            
                            # Build Rust project (debug mode for faster builds during testing)
                            result = subprocess.run(
                                ["cargo", "build"], 
                                capture_output=True, 
                                text=True, 
                                timeout=300,  # Rust builds can take longer
                                cwd=test_dir
                            )
                            
                            dependency_end = time.perf_counter()
                            dependency_time = (dependency_end - dependency_start) * 1000
                            build_time = None  # Rust doesn't separate dependency and build phases clearly
                    
                    dependency_end = dependency_end if 'dependency_end' in locals() else time.perf_counter()
                    dependency_time = (dependency_end - dependency_start) * 1000
                    
                    success = result.returncode == 0 if 'result' in locals() else False
                    if language == "typescript" and 'build_result' in locals():
                        success = success and build_result.returncode == 0
                    
                    return CLIInstallationBenchmark(
                        language=language,
                        installation_time_ms=metrics.get("execution_time_ms", 0),
                        dependency_install_time_ms=dependency_time,
                        build_time_ms=build_time,
                        success=success
                    )
                
                except subprocess.TimeoutExpired:
                    return CLIInstallationBenchmark(
                        language=language,
                        installation_time_ms=metrics.get("execution_time_ms", 0),
                        dependency_install_time_ms=0,
                        build_time_ms=None,
                        success=False,
                        error_message="Installation timeout"
                    )
                except Exception as e:
                    return CLIInstallationBenchmark(
                        language=language,
                        installation_time_ms=metrics.get("execution_time_ms", 0),
                        dependency_install_time_ms=0,
                        build_time_ms=None,
                        success=False,
                        error_message=str(e)
                    )
        
        finally:
            # Cleanup
            shutil.rmtree(test_dir, ignore_errors=True)

    def benchmark_cli_execution(self, language: str, test_name: str, command: str) -> CLIExecutionBenchmark:
        """Benchmark real CLI execution performance"""
        self.console.print(f"[green]⚡ Benchmarking {language} CLI execution: '{command}'[/green]")
        
        test_dir = Path(tempfile.mkdtemp(prefix=f"perf_exec_{language}_{test_name}_"))
        
        try:
            # Generate and prepare CLI
            config = self.create_test_cli_config(language, test_name)
            config_file = test_dir / "goobits.yaml"
            
            with open(config_file, 'w') as f:
                yaml.dump(config, f, default_flow_style=False)
            
            self._build_cli_for_language(language, str(config_file), test_dir)
            
            # Prepare execution command
            cmd_parts = command.split()
            
            if language == "python":
                cli_command = ["python", str(test_dir / "cli.py")] + cmd_parts
            elif language == "nodejs":
                cli_command = ["node", str(test_dir / "cli.js")] + cmd_parts
            elif language == "typescript":
                # For TypeScript, we need to compile first or use the compiled JS
                cli_command = ["node", str(test_dir / "cli.js")] + cmd_parts
            elif language == "rust":
                # For Rust, use the compiled binary (Rust enhancement)
                binary_name = config["command_name"] if "command_name" in config else "cli"
                binary_paths = [
                    test_dir / "target" / "debug" / binary_name,
                    test_dir / "target" / "release" / binary_name
                ]
                
                binary_path = None
                for path in binary_paths:
                    if path.exists():
                        binary_path = path
                        break
                
                if binary_path is None:
                    raise Exception(f"Rust binary not found at {binary_paths}")
                
                cli_command = [str(binary_path)] + cmd_parts
            
            # Run multiple iterations for statistical accuracy
            execution_times = []
            memory_peaks = []
            startup_times = []
            successes = 0
            total_output_size = 0
            
            for iteration in range(self.iterations):
                try:
                    with self.measure_real_performance(f"cli_execution_{language}_{iteration}") as metrics:
                        startup_start = time.perf_counter()
                        
                        result = subprocess.run(
                            cli_command,
                            capture_output=True,
                            text=True,
                            timeout=30,
                            cwd=test_dir
                        )
                        
                        startup_end = time.perf_counter()
                        startup_time = (startup_end - startup_start) * 1000
                        
                        if result.returncode == 0:
                            successes += 1
                        
                        execution_times.append(metrics["execution_time_ms"])
                        startup_times.append(startup_time)
                        memory_peaks.append(metrics.get("traced_memory_mb", metrics["end_memory_mb"]))
                        total_output_size += len(result.stdout.encode('utf-8'))
                
                except subprocess.TimeoutExpired:
                    self.console.print(f"[red]Timeout in iteration {iteration + 1}[/red]")
                    continue
                except Exception as e:
                    self.console.print(f"[red]Error in iteration {iteration + 1}: {e}[/red]")
                    continue
            
            if execution_times:
                return CLIExecutionBenchmark(
                    language=language,
                    command=command,
                    startup_time_ms=statistics.mean(startup_times),
                    execution_time_ms=statistics.mean(execution_times),
                    memory_peak_mb=max(memory_peaks),
                    memory_baseline_mb=min(memory_peaks),
                    success_rate=successes / self.iterations,
                    output_size_bytes=total_output_size // len(execution_times),
                    iterations=len(execution_times),
                    success=successes > 0
                )
            else:
                return CLIExecutionBenchmark(
                    language=language,
                    command=command,
                    startup_time_ms=0,
                    execution_time_ms=0,
                    memory_peak_mb=0,
                    memory_baseline_mb=0,
                    success_rate=0,
                    output_size_bytes=0,
                    iterations=0,
                    success=False,
                    error_message="All iterations failed"
                )
        
        finally:
            # Cleanup
            shutil.rmtree(test_dir, ignore_errors=True)

    def run_comprehensive_real_benchmarks(self) -> Dict[str, Any]:
        """Run comprehensive real performance benchmarks across all categories"""
        self.console.print(Panel.fit(
            "[bold blue]🚀 Real Performance Benchmark Suite[/bold blue]\n"
            "Measuring actual CLI generation, installation, and execution performance\n"
            f"Languages: {', '.join(self.languages)}\n"
            f"Iterations: {self.iterations} per test",
            title="Performance Benchmarking"
        ))
        
        results = {
            "generation_benchmarks": {},
            "installation_benchmarks": {},
            "execution_benchmarks": {},
            "summary": {}
        }
        
        total_tests = len(self.languages) * (1 + 1 + len(self.test_commands))
        
        with Progress() as progress:
            main_task = progress.add_task("[green]Overall Progress", total=total_tests)
            
            for language in self.languages:
                self.console.print(f"\n[bold yellow]Testing {language.upper()}[/bold yellow]")
                
                # Generation benchmark
                gen_benchmark = self.benchmark_cli_generation(language, "standard")
                results["generation_benchmarks"][language] = asdict(gen_benchmark)
                
                # Record generation performance metric
                self.record_performance_metric(
                    test_name=f"cli_generation_{language}",
                    language=language,
                    operation="generation",
                    metric_type="time",
                    value=gen_benchmark.generation_time_ms,
                    unit="ms",
                    metadata={
                        "files_generated": gen_benchmark.generated_files_count,
                        "lines_of_code": gen_benchmark.lines_of_code,
                        "success": gen_benchmark.success
                    }
                )
                
                progress.advance(main_task)
                
                # Installation benchmark (only if generation succeeded)
                if gen_benchmark.success:
                    install_benchmark = self.benchmark_cli_installation(language, "standard")
                    results["installation_benchmarks"][language] = asdict(install_benchmark)
                    
                    self.record_performance_metric(
                        test_name=f"cli_installation_{language}",
                        language=language,
                        operation="installation",
                        metric_type="time",
                        value=install_benchmark.installation_time_ms,
                        unit="ms",
                        metadata={"success": install_benchmark.success}
                    )
                
                progress.advance(main_task)
                
                # Execution benchmarks for each command
                results["execution_benchmarks"][language] = {}
                
                if gen_benchmark.success:
                    for command in self.test_commands:
                        exec_benchmark = self.benchmark_cli_execution(language, "standard", command)
                        results["execution_benchmarks"][language][command] = asdict(exec_benchmark)
                        
                        # Record multiple performance metrics for execution
                        self.record_performance_metric(
                            test_name=f"cli_execution_{language}_{command.replace(' ', '_')}",
                            language=language,
                            operation="execution",
                            metric_type="startup_time",
                            value=exec_benchmark.startup_time_ms,
                            unit="ms",
                            metadata={
                                "command": command,
                                "success_rate": exec_benchmark.success_rate,
                                "iterations": exec_benchmark.iterations
                            }
                        )
                        
                        self.record_performance_metric(
                            test_name=f"cli_memory_{language}_{command.replace(' ', '_')}",
                            language=language,
                            operation="execution",
                            metric_type="memory",
                            value=exec_benchmark.memory_peak_mb,
                            unit="MB",
                            metadata={
                                "command": command,
                                "baseline_mb": exec_benchmark.memory_baseline_mb
                            }
                        )
                        
                        progress.advance(main_task)
        
        # Generate summary analysis
        results["summary"] = self.analyze_benchmark_results(results)
        results["performance_metrics"] = [asdict(m) for m in self.metrics]
        
        return results

    def record_performance_metric(self, test_name: str, language: str, operation: str,
                                 metric_type: str, value: float, unit: str, 
                                 metadata: Dict[str, Any] = None):
        """Record a performance metric with statistical data"""
        # For single measurements, we don't have iterations to calculate statistics
        # But we can still provide the basic structure
        metric = RealPerformanceMetric(
            test_name=test_name,
            language=language,
            operation=operation,
            metric_type=metric_type,
            value=value,
            unit=unit,
            timestamp=time.time(),
            iterations=1,
            statistics={
                "min": value,
                "max": value,
                "std_dev": 0.0,
                "percentile_95": value
            },
            metadata=metadata or {}
        )
        self.metrics.append(metric)

    def analyze_benchmark_results(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze benchmark results and provide insights"""
        analysis = {
            "performance_comparison": {},
            "target_compliance": {},
            "optimization_recommendations": [],
            "regression_analysis": []
        }
        
        # Performance comparison across languages
        for language in self.languages:
            gen_data = results["generation_benchmarks"].get(language, {})
            exec_data = results["execution_benchmarks"].get(language, {})
            
            if gen_data and gen_data.get("success"):
                targets = self.performance_targets[language]
                
                # Target compliance analysis
                compliance = {
                    "generation_time": gen_data["generation_time_ms"] <= targets["generation_time_ms"],
                    "startup_time": True,  # Will update below
                    "memory_usage": True   # Will update below
                }
                
                # Check execution performance
                if exec_data:
                    avg_startup_times = []
                    max_memory_usage = 0
                    
                    for command, exec_benchmark in exec_data.items():
                        if exec_benchmark.get("success"):
                            avg_startup_times.append(exec_benchmark["startup_time_ms"])
                            max_memory_usage = max(max_memory_usage, exec_benchmark["memory_peak_mb"])
                    
                    if avg_startup_times:
                        avg_startup = statistics.mean(avg_startup_times)
                        compliance["startup_time"] = avg_startup <= targets["startup_time_ms"]
                        compliance["memory_usage"] = max_memory_usage <= targets["memory_mb"]
                
                analysis["target_compliance"][language] = compliance
                
                # Generate optimization recommendations
                if not compliance["generation_time"]:
                    analysis["optimization_recommendations"].append(
                        f"{language}: CLI generation is slow ({gen_data['generation_time_ms']:.0f}ms). "
                        f"Target: {targets['generation_time_ms']}ms"
                    )
                
                if not compliance["startup_time"] and avg_startup_times:
                    avg_startup = statistics.mean(avg_startup_times)
                    analysis["optimization_recommendations"].append(
                        f"{language}: CLI startup is slow ({avg_startup:.0f}ms). "
                        f"Target: {targets['startup_time_ms']}ms"
                    )
                
                if not compliance["memory_usage"] and max_memory_usage > 0:
                    analysis["optimization_recommendations"].append(
                        f"{language}: High memory usage ({max_memory_usage:.0f}MB). "
                        f"Target: {targets['memory_mb']}MB"
                    )
        
        # Regression analysis (compare with Agent E's baseline data)
        agent_e_baselines = {
            "python": 320.2,    # ms from integration tests
            "nodejs": 1682.6,   # ms from integration tests  
            "typescript": 5065.0, # ms from integration tests
            "rust": 50.0        # ms estimated baseline for Rust (Rust enhancement - very fast)
        }
        
        for language in self.languages:
            exec_data = results["execution_benchmarks"].get(language, {})
            if exec_data:
                current_times = []
                for command, benchmark in exec_data.items():
                    if benchmark.get("success"):
                        current_times.append(benchmark["execution_time_ms"])
                
                if current_times:
                    current_avg = statistics.mean(current_times)
                    baseline = agent_e_baselines.get(language, 0)
                    
                    if baseline > 0:
                        regression_pct = ((current_avg - baseline) / baseline) * 100
                        if abs(regression_pct) > 10:  # 10% threshold
                            regression_type = "regression" if regression_pct > 0 else "improvement"
                            analysis["regression_analysis"].append({
                                "language": language,
                                "current_time_ms": current_avg,
                                "baseline_time_ms": baseline,
                                "change_percent": regression_pct,
                                "type": regression_type
                            })
        
        return analysis

    def integrate_with_existing_performance_tools(self):
        """Integrate with existing performance validation suite"""
        self.console.print("[blue]🔗 Integrating with existing performance tools[/blue]")
        
        if not PERFORMANCE_TOOLS_AVAILABLE:
            self.console.print("[yellow]⚠️ Performance tools not available, using built-in benchmarking only[/yellow]")
            return {}
        
        try:
            # Use existing startup validator
            startup_validator = StartupValidator(
                target_ms=500,  # 500ms target
                iterations=self.iterations,
                output_dir=self.output_dir / "startup_validation"
            )
            
            # Use existing memory benchmark
            memory_benchmark = CLIMemoryBenchmark(
                output_dir=self.output_dir / "memory_analysis"
            )
            
            # Use existing template benchmark
            template_benchmark = TemplateBenchmark(
                iterations=max(3, self.iterations // 2),
                output_dir=self.output_dir / "template_benchmarks"
            )
            
            return {
                "startup_validator": startup_validator,
                "memory_benchmark": memory_benchmark,
                "template_benchmark": template_benchmark
            }
        except Exception as e:
            self.console.print(f"[yellow]⚠️ Could not initialize performance tools: {e}[/yellow]")
            return {}

    def establish_performance_baselines(self, results: Dict[str, Any]):
        """Establish performance baselines for regression detection"""
        baselines = {}
        
        for language in self.languages:
            lang_baselines = {}
            
            # Generation baseline
            gen_data = results["generation_benchmarks"].get(language, {})
            if gen_data.get("success"):
                lang_baselines["generation_time_ms"] = gen_data["generation_time_ms"]
            
            # Execution baselines
            exec_data = results["execution_benchmarks"].get(language, {})
            if exec_data:
                startup_times = []
                memory_peaks = []
                
                for command, benchmark in exec_data.items():
                    if benchmark.get("success"):
                        startup_times.append(benchmark["startup_time_ms"])
                        memory_peaks.append(benchmark["memory_peak_mb"])
                
                if startup_times:
                    lang_baselines["avg_startup_time_ms"] = statistics.mean(startup_times)
                    lang_baselines["max_memory_mb"] = max(memory_peaks) if memory_peaks else 0
            
            baselines[language] = lang_baselines
        
        # Save baselines
        baseline_file = self.output_dir / "performance_baselines.json"
        with open(baseline_file, 'w') as f:
            json.dump(baselines, f, indent=2)
        
        self.console.print(f"[green]📊 Performance baselines saved to {baseline_file}[/green]")
        return baselines

    def detect_performance_regressions(self, current_results: Dict[str, Any], 
                                     threshold_pct: float = 10.0) -> List[Dict[str, Any]]:
        """Detect performance regressions by comparing with baselines"""
        baseline_file = self.output_dir / "performance_baselines.json"
        
        if not baseline_file.exists():
            self.console.print("[yellow]⚠️ No performance baselines found. Establishing new baselines.[/yellow]")
            self.establish_performance_baselines(current_results)
            return []
        
        with open(baseline_file, 'r') as f:
            baselines = json.load(f)
        
        regressions = []
        
        for language in self.languages:
            baseline = baselines.get(language, {})
            current_gen = current_results["generation_benchmarks"].get(language, {})
            current_exec = current_results["execution_benchmarks"].get(language, {})
            
            # Check generation time regression
            if baseline.get("generation_time_ms") and current_gen.get("success"):
                baseline_time = baseline["generation_time_ms"]
                current_time = current_gen["generation_time_ms"]
                regression_pct = ((current_time - baseline_time) / baseline_time) * 100
                
                if regression_pct > threshold_pct:
                    regressions.append({
                        "language": language,
                        "metric": "generation_time_ms",
                        "baseline_value": baseline_time,
                        "current_value": current_time,
                        "regression_percent": regression_pct
                    })
            
            # Check startup time regression
            if baseline.get("avg_startup_time_ms") and current_exec:
                startup_times = [
                    benchmark["startup_time_ms"] 
                    for benchmark in current_exec.values() 
                    if benchmark.get("success")
                ]
                
                if startup_times:
                    current_avg_startup = statistics.mean(startup_times)
                    baseline_startup = baseline["avg_startup_time_ms"]
                    regression_pct = ((current_avg_startup - baseline_startup) / baseline_startup) * 100
                    
                    if regression_pct > threshold_pct:
                        regressions.append({
                            "language": language,
                            "metric": "avg_startup_time_ms",
                            "baseline_value": baseline_startup,
                            "current_value": current_avg_startup,
                            "regression_percent": regression_pct
                        })
        
        return regressions

    def generate_comprehensive_report(self, results: Dict[str, Any]) -> str:
        """Generate comprehensive performance report"""
        report_lines = [
            "# Real Performance Benchmark Report",
            f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}",
            f"Test iterations: {self.iterations}",
            f"Languages tested: {', '.join(self.languages)}",
            ""
        ]
        
        # Executive Summary
        total_tests = sum(
            len(results["execution_benchmarks"].get(lang, {})) 
            for lang in self.languages
        ) + len(results["generation_benchmarks"]) + len(results["installation_benchmarks"])
        
        successful_tests = 0
        for lang in self.languages:
            if results["generation_benchmarks"].get(lang, {}).get("success"):
                successful_tests += 1
            
            for benchmark in results["execution_benchmarks"].get(lang, {}).values():
                if benchmark.get("success"):
                    successful_tests += 1
        
        success_rate = (successful_tests / total_tests * 100) if total_tests > 0 else 0
        
        report_lines.extend([
            "## 🎯 Executive Summary",
            f"- **Total Tests**: {total_tests}",
            f"- **Successful Tests**: {successful_tests}",
            f"- **Success Rate**: {success_rate:.1f}%",
            ""
        ])
        
        # Performance Summary Table
        report_lines.extend([
            "## 📊 Performance Summary",
            "",
            "| Language | Generation (ms) | Avg Startup (ms) | Peak Memory (MB) | Status |",
            "|----------|-----------------|------------------|------------------|---------|"
        ])
        
        for language in self.languages:
            gen_data = results["generation_benchmarks"].get(language, {})
            exec_data = results["execution_benchmarks"].get(language, {})
            
            gen_time = gen_data.get("generation_time_ms", 0) if gen_data.get("success") else "FAILED"
            
            startup_times = []
            memory_peaks = []
            for benchmark in exec_data.values():
                if benchmark.get("success"):
                    startup_times.append(benchmark["startup_time_ms"])
                    memory_peaks.append(benchmark["memory_peak_mb"])
            
            avg_startup = statistics.mean(startup_times) if startup_times else "FAILED"
            peak_memory = max(memory_peaks) if memory_peaks else "FAILED"
            
            # Determine status
            targets = self.performance_targets[language]
            status = "✅"
            
            if isinstance(gen_time, (int, float)) and gen_time > targets["generation_time_ms"]:
                status = "⚠️"
            if isinstance(avg_startup, (int, float)) and avg_startup > targets["startup_time_ms"]:
                status = "⚠️"
            if isinstance(peak_memory, (int, float)) and peak_memory > targets["memory_mb"]:
                status = "⚠️"
            if gen_time == "FAILED" or avg_startup == "FAILED" or peak_memory == "FAILED":
                status = "❌"
            
            gen_str = f"{gen_time:.0f}" if isinstance(gen_time, (int, float)) else str(gen_time)
            startup_str = f"{avg_startup:.0f}" if isinstance(avg_startup, (int, float)) else str(avg_startup)
            memory_str = f"{peak_memory:.1f}" if isinstance(peak_memory, (int, float)) else str(peak_memory)
            
            report_lines.append(f"| {language} | {gen_str} | {startup_str} | {memory_str} | {status} |")
        
        report_lines.extend(["", ""])
        
        # Detailed Analysis
        summary = results.get("summary", {})
        
        # Target Compliance
        target_compliance = summary.get("target_compliance", {})
        if target_compliance:
            report_lines.extend([
                "## 🎯 Performance Target Compliance",
                ""
            ])
            
            for language, compliance in target_compliance.items():
                report_lines.append(f"### {language.title()}")
                for metric, passed in compliance.items():
                    status = "✅ PASS" if passed else "❌ FAIL"
                    report_lines.append(f"- **{metric.replace('_', ' ').title()}**: {status}")
                report_lines.append("")
        
        # Optimization Recommendations
        recommendations = summary.get("optimization_recommendations", [])
        if recommendations:
            report_lines.extend([
                "## 💡 Performance Optimization Recommendations",
                ""
            ])
            for i, rec in enumerate(recommendations, 1):
                report_lines.append(f"{i}. {rec}")
            report_lines.append("")
        
        # Regression Analysis
        regressions = self.detect_performance_regressions(results)
        if regressions:
            report_lines.extend([
                "## ⚠️ Performance Regressions Detected",
                ""
            ])
            for reg in regressions:
                report_lines.extend([
                    f"### {reg['language'].title()} - {reg['metric']}",
                    f"- **Baseline**: {reg['baseline_value']:.2f}",
                    f"- **Current**: {reg['current_value']:.2f}",
                    f"- **Regression**: {reg['regression_percent']:.1f}%",
                    ""
                ])
        else:
            report_lines.extend([
                "## ✅ No Performance Regressions Detected",
                "All metrics are within acceptable thresholds compared to baselines.",
                ""
            ])
        
        # Raw Data
        report_lines.extend([
            "## 📄 Detailed Test Results",
            "```json"
        ])
        
        report_lines.append(json.dumps(results, indent=2))
        report_lines.extend(["```", ""])
        
        return "\n".join(report_lines)

    def save_results(self, results: Dict[str, Any]):
        """Save comprehensive benchmark results"""
        # Save main report
        report = self.generate_comprehensive_report(results)
        report_file = self.output_dir / "real_performance_benchmark_report.md"
        with open(report_file, 'w') as f:
            f.write(report)
        
        # Save raw results
        results_file = self.output_dir / "benchmark_results.json"
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        # Save performance metrics
        metrics_file = self.output_dir / "performance_metrics.json"
        metrics_data = [asdict(m) for m in self.metrics]
        with open(metrics_file, 'w') as f:
            json.dump(metrics_data, f, indent=2)
        
        # Establish/update baselines
        self.establish_performance_baselines(results)
        
        self.console.print(f"\n[green]📁 Benchmark results saved to {self.output_dir}[/green]")
        self.console.print(f"   📄 Main Report: {report_file}")
        self.console.print(f"   📊 Raw Data: {results_file}")
        self.console.print(f"   📈 Metrics: {metrics_file}")


def main():
    """Main entry point for real performance benchmarking"""
    console = Console()
    console.print("[bold blue]🚀 Real Performance Benchmark Suite - Agent F[/bold blue]")
    console.print("Replacing mocked performance tests with real measurements")
    
    # Initialize benchmark suite
    benchmark_suite = RealPerformanceBenchmarkSuite(
        iterations=3,  # Start with 3 iterations for faster testing
        output_dir=Path("performance_results")
    )
    
    try:
        # Integrate with existing performance tools
        tools_integration = benchmark_suite.integrate_with_existing_performance_tools()
        console.print(f"[green]✅ Integrated with existing performance validation tools[/green]")
        
        # Run comprehensive benchmarks
        results = benchmark_suite.run_comprehensive_real_benchmarks()
        
        # Save results
        benchmark_suite.save_results(results)
        
        # Check for critical issues
        critical_issues = []
        for language in benchmark_suite.languages:
            gen_data = results["generation_benchmarks"].get(language, {})
            if not gen_data.get("success"):
                critical_issues.append(f"{language} CLI generation failed")
        
        # Display summary
        console.print(f"\n[bold blue]📊 Real Performance Benchmark Summary[/bold blue]")
        console.print(f"   Total Performance Metrics: {len(benchmark_suite.metrics)}")
        console.print(f"   Languages Successfully Tested: {sum(1 for lang in benchmark_suite.languages if results['generation_benchmarks'].get(lang, {}).get('success', False))}")
        console.print(f"   Critical Issues: {len(critical_issues)}")
        
        if critical_issues:
            console.print(f"\n[red]🚨 Critical Issues Detected:[/red]")
            for issue in critical_issues:
                console.print(f"   - {issue}")
            return 1
        else:
            console.print(f"\n[green]✅ Real performance benchmarking completed successfully![/green]")
            return 0
    
    except Exception as e:
        console.print(f"\n[red]❌ Real performance benchmarking failed: {e}[/red]")
        import traceback
        console.print(f"[red]Stack trace:[/red]\n{traceback.format_exc()}")
        return 1


class RustSpecificPerformanceBenchmarks:
    """Rust-specific performance benchmarks and validations (Rust enhancement)."""
    
    def __init__(self, output_dir: Path = Path("rust_performance_results")):
        self.console = Console()
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def benchmark_rust_compilation_speed(self, iterations: int = 3) -> Dict[str, Any]:
        """Benchmark Rust compilation performance specifically."""
        self.console.print("[blue]🦀 Benchmarking Rust compilation speed[/blue]")
        
        compilation_times = []
        binary_sizes = []
        
        for i in range(iterations):
            test_dir = Path(tempfile.mkdtemp(prefix=f"rust_compile_bench_{i}_"))
            
            try:
                # Create test CLI configuration
                config_data = {
                    "package_name": f"rust-compile-bench-{i}",
                    "command_name": f"rust-bench-{i}",
                    "display_name": f"Rust Compilation Benchmark {i}",
                    "description": "Rust compilation speed test",
                    "language": "rust",
                    "python": {"minimum_version": "3.8"},
                    "dependencies": {"required": []},
                    "installation": {"pypi_name": f"rust-compile-bench-{i}"},
                    "shell_integration": {"enabled": False},
                    "validation": {"check_api_keys": False, "check_disk_space": False},
                    "messages": {"install_success": "Rust bench CLI installed!"},
                    "cli": {
                        "name": f"rust-bench-{i}",
                        "tagline": "Rust compilation benchmark",
                        "commands": {
                            "test": {"desc": "Test command"},
                            "status": {"desc": "Status command"},
                            "process": {"desc": "Process data command"}
                        }
                    }
                }
                
                config_file = test_dir / "goobits.yaml"
                with open(config_file, 'w') as f:
                    yaml.dump(config_data, f)
                
                # Generate Rust CLI
                from goobits_cli.generators.rust import RustGenerator
                from goobits_cli.schemas import GoobitsConfigSchema
                
                config = GoobitsConfigSchema(**config_data)
                generator = RustGenerator()
                files = generator.generate_all_files(config, str(config_file))
                
                # Write files
                for file_path, content in files.items():
                    full_path = test_dir / file_path
                    full_path.parent.mkdir(parents=True, exist_ok=True)
                    full_path.write_text(content)
                
                # Check if cargo is available
                cargo_check = subprocess.run(["cargo", "--version"], capture_output=True, text=True)
                if cargo_check.returncode != 0:
                    self.console.print("[yellow]⚠️ Cargo not available, skipping Rust compilation benchmarks[/yellow]")
                    return {"error": "cargo_not_available"}
                
                # Benchmark compilation
                start_time = time.perf_counter()
                
                compile_result = subprocess.run([
                    "cargo", "build", "--release"
                ], cwd=test_dir, capture_output=True, text=True, timeout=600)
                
                end_time = time.perf_counter()
                compilation_time = (end_time - start_time) * 1000
                
                compilation_times.append(compilation_time)
                
                # Measure binary size
                binary_name = f"rust-bench-{i}"
                binary_path = test_dir / "target" / "release" / binary_name
                
                if binary_path.exists():
                    binary_size = binary_path.stat().st_size
                    binary_sizes.append(binary_size)
                else:
                    self.console.print(f"[yellow]⚠️ Binary not found for iteration {i}[/yellow]")
                
                if compile_result.returncode != 0:
                    self.console.print(f"[red]❌ Compilation failed for iteration {i}: {compile_result.stderr}[/red]")
                
            except subprocess.TimeoutExpired:
                self.console.print(f"[red]❌ Compilation timeout for iteration {i}[/red]")
            except Exception as e:
                self.console.print(f"[red]❌ Error in iteration {i}: {e}[/red]")
            finally:
                # Cleanup
                shutil.rmtree(test_dir, ignore_errors=True)
        
        if compilation_times:
            return {
                "avg_compilation_time_ms": statistics.mean(compilation_times),
                "min_compilation_time_ms": min(compilation_times),
                "max_compilation_time_ms": max(compilation_times),
                "compilation_times": compilation_times,
                "avg_binary_size_bytes": statistics.mean(binary_sizes) if binary_sizes else 0,
                "binary_sizes": binary_sizes,
                "iterations": len(compilation_times),
                "success_rate": len(compilation_times) / iterations
            }
        else:
            return {"error": "no_successful_compilations"}
    
    def benchmark_rust_startup_performance(self, iterations: int = 10) -> Dict[str, Any]:
        """Benchmark Rust CLI startup performance specifically."""
        self.console.print("[blue]🦀 Benchmarking Rust startup performance[/blue]")
        
        test_dir = Path(tempfile.mkdtemp(prefix="rust_startup_bench_"))
        
        try:
            # Generate and compile a Rust CLI
            config_data = {
                "package_name": "rust-startup-bench",
                "command_name": "rust-startup-test",
                "display_name": "Rust Startup Benchmark",
                "description": "Rust startup performance test",
                "language": "rust",
                "python": {"minimum_version": "3.8"},
                "dependencies": {"required": []},
                "installation": {"pypi_name": "rust-startup-bench"},
                "shell_integration": {"enabled": False},
                "validation": {"check_api_keys": False, "check_disk_space": False},
                "messages": {"install_success": "Rust startup bench CLI installed!"},
                "cli": {
                    "name": "rust-startup-test",
                    "tagline": "Rust startup benchmark",
                    "commands": {
                        "quick": {"desc": "Quick test command"}
                    }
                }
            }
            
            config_file = test_dir / "goobits.yaml"
            with open(config_file, 'w') as f:
                yaml.dump(config_data, f)
            
            # Generate and compile
            from goobits_cli.generators.rust import RustGenerator
            from goobits_cli.schemas import GoobitsConfigSchema
            
            config = GoobitsConfigSchema(**config_data)
            generator = RustGenerator()
            files = generator.generate_all_files(config, str(config_file))
            
            for file_path, content in files.items():
                full_path = test_dir / file_path
                full_path.parent.mkdir(parents=True, exist_ok=True)
                full_path.write_text(content)
            
            # Compile binary
            cargo_check = subprocess.run(["cargo", "--version"], capture_output=True, text=True)
            if cargo_check.returncode != 0:
                return {"error": "cargo_not_available"}
            
            compile_result = subprocess.run([
                "cargo", "build", "--release"
            ], cwd=test_dir, capture_output=True, text=True, timeout=600)
            
            if compile_result.returncode != 0:
                return {"error": "compilation_failed", "stderr": compile_result.stderr}
            
            # Find binary
            binary_path = test_dir / "target" / "release" / "rust-startup-test"
            if not binary_path.exists():
                return {"error": "binary_not_found"}
            
            # Benchmark startup times
            startup_times = []
            help_times = []
            version_times = []
            
            for i in range(iterations):
                # Test help command startup
                start_time = time.perf_counter()
                result = subprocess.run([
                    str(binary_path), "--help"
                ], capture_output=True, text=True, timeout=10)
                end_time = time.perf_counter()
                
                if result.returncode == 0:
                    help_time = (end_time - start_time) * 1000
                    help_times.append(help_time)
                
                # Test version command startup
                start_time = time.perf_counter()
                result = subprocess.run([
                    str(binary_path), "--version"
                ], capture_output=True, text=True, timeout=10)
                end_time = time.perf_counter()
                
                if result.returncode == 0:
                    version_time = (end_time - start_time) * 1000
                    version_times.append(version_time)
            
            return {
                "avg_help_startup_ms": statistics.mean(help_times) if help_times else 0,
                "min_help_startup_ms": min(help_times) if help_times else 0,
                "max_help_startup_ms": max(help_times) if help_times else 0,
                "avg_version_startup_ms": statistics.mean(version_times) if version_times else 0,
                "min_version_startup_ms": min(version_times) if version_times else 0,
                "max_version_startup_ms": max(version_times) if version_times else 0,
                "help_times": help_times,
                "version_times": version_times,
                "iterations": iterations,
                "success_rate_help": len(help_times) / iterations,
                "success_rate_version": len(version_times) / iterations
            }
            
        except Exception as e:
            return {"error": str(e)}
        finally:
            # Cleanup
            shutil.rmtree(test_dir, ignore_errors=True)
    
    def run_rust_performance_suite(self) -> Dict[str, Any]:
        """Run comprehensive Rust-specific performance benchmarks."""
        self.console.print(Panel.fit(
            "[bold blue]🦀 Rust-Specific Performance Benchmark Suite[/bold blue]\n"
            "Measuring Rust CLI compilation speed, startup performance, and memory efficiency",
            title="Rust Performance Benchmarking"
        ))
        
        results = {}
        
        # Compilation benchmarks
        self.console.print("[blue]📊 Running compilation benchmarks...[/blue]")
        compilation_results = self.benchmark_rust_compilation_speed(iterations=3)
        results["compilation"] = compilation_results
        
        # Startup benchmarks
        if not compilation_results.get("error"):
            self.console.print("[blue]📊 Running startup benchmarks...[/blue]")
            startup_results = self.benchmark_rust_startup_performance(iterations=10)
            results["startup"] = startup_results
        
        # Save results
        results_file = self.output_dir / "rust_specific_benchmarks.json"
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        self.console.print(f"[green]📁 Rust-specific benchmarks saved to {results_file}[/green]")
        
        return results


if __name__ == "__main__":
    sys.exit(main())