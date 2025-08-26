#!/usr/bin/env python3
"""
Startup Time Validation Framework for Goobits CLI
Validates <100ms startup times with detailed analysis and optimization recommendations
"""

import json
import subprocess
import statistics
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List, Any

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.progress import Progress, SpinnerColumn, TextColumn
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False


@dataclass
class StartupMeasurement:
    """Individual startup time measurement"""
    command: str
    language: str
    configuration: str
    execution_time_ms: float
    success: bool
    stdout: str
    stderr: str
    return_code: int
    iteration: int
    timestamp: float
    metadata: Dict[str, Any] = None


@dataclass
class StartupProfile:
    """Complete startup performance profile"""
    test_name: str
    language: str
    configuration: str
    target_ms: float
    measurements: List[StartupMeasurement]
    average_ms: float
    median_ms: float
    min_ms: float
    max_ms: float
    std_dev_ms: float
    percentile_95_ms: float
    percentile_99_ms: float
    success_rate: float
    meets_target: bool
    optimization_score: float
    recommendations: List[str]


class StartupValidator:
    """Comprehensive startup time validation framework"""
    
    def __init__(self, 
                 target_ms: float = 100.0,
                 iterations: int = 10,
                 warmup_iterations: int = 2,
                 timeout_ms: float = 5000.0,
                 output_dir: Path = Path("startup_results")):
        
        self.target_ms = target_ms
        self.iterations = iterations
        self.warmup_iterations = warmup_iterations
        self.timeout_ms = timeout_ms
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Console setup
        if RICH_AVAILABLE:
            self.console = Console()
        else:
            self.console = None
        
        # Results storage
        self.profiles: List[StartupProfile] = []
        
        # Language-specific startup targets
        self.language_targets = {
            "python": 90.0,    # Python with Click
            "nodejs": 70.0,    # Node.js with Commander
            "typescript": 80.0, # TypeScript compiled
            "rust": 40.0       # Rust compiled (if supported)
        }
        
        # Test commands for validation
        self.test_commands = [
            "--version",
            "--help",
            "help"
        ]
    
    def measure_startup_time(self, 
                           cli_command: List[str], 
                           test_args: List[str] = None,
                           cwd: Path = None) -> StartupMeasurement:
        """Measure a single startup time"""
        test_args = test_args or ["--version"]
        full_command = cli_command + test_args
        
        try:
            start_time = time.perf_counter()
            
            process = subprocess.run(
                full_command,
                capture_output=True,
                text=True,
                timeout=self.timeout_ms / 1000,
                cwd=cwd
            )
            
            end_time = time.perf_counter()
            execution_time = (end_time - start_time) * 1000  # Convert to ms
            
            return StartupMeasurement(
                command=" ".join(full_command),
                language="unknown",  # To be set by caller
                configuration="default",  # To be set by caller
                execution_time_ms=execution_time,
                success=process.returncode == 0,
                stdout=process.stdout[:1000],  # Limit output size
                stderr=process.stderr[:1000],
                return_code=process.returncode,
                iteration=0,  # To be set by caller
                timestamp=time.time()
            )
        
        except subprocess.TimeoutExpired:
            return StartupMeasurement(
                command=" ".join(full_command),
                language="unknown",
                configuration="default",
                execution_time_ms=self.timeout_ms,
                success=False,
                stdout="",
                stderr="Command timed out",
                return_code=-1,
                iteration=0,
                timestamp=time.time()
            )
        
        except Exception as e:
            return StartupMeasurement(
                command=" ".join(full_command),
                language="unknown",
                configuration="default", 
                execution_time_ms=self.timeout_ms,
                success=False,
                stdout="",
                stderr=str(e),
                return_code=-1,
                iteration=0,
                timestamp=time.time()
            )
    
    def validate_cli_startup(self, 
                           cli_command: List[str],
                           language: str = "python",
                           configuration: str = "default",
                           test_name: str = None,
                           cwd: Path = None) -> StartupProfile:
        """Validate startup time for a CLI with multiple iterations"""
        
        test_name = test_name or f"{language}_{configuration}"
        target = self.language_targets.get(language, self.target_ms)
        
        if self.console:
            self.console.print(f"[blue]🚀 Validating startup time for {test_name}[/blue]")
            self.console.print(f"   Target: {target}ms, Iterations: {self.iterations}")
        
        all_measurements = []
        
        # Run warmup iterations (not counted in results)
        if self.warmup_iterations > 0:
            if self.console:
                self.console.print(f"[yellow]🔥 Running {self.warmup_iterations} warmup iterations...[/yellow]")
            
            for i in range(self.warmup_iterations):
                warmup = self.measure_startup_time(cli_command, ["--version"], cwd)
                if self.console and warmup.success:
                    self.console.print(f"   Warmup {i+1}: {warmup.execution_time_ms:.2f}ms")
        
        # Run actual measurements
        if self.console:
            progress = Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                transient=True
            )
            progress_task = progress.add_task(f"Measuring {test_name} startup times...", total=None)
            progress.start()
        else:
            progress = None
            progress_task = None
        
        try:
            # Test each command variant
            for test_cmd in self.test_commands:
                test_cmd_args = test_cmd.split() if isinstance(test_cmd, str) else test_cmd
                
                for iteration in range(self.iterations):
                    measurement = self.measure_startup_time(cli_command, test_cmd_args, cwd)
                    measurement.language = language
                    measurement.configuration = configuration
                    measurement.iteration = iteration
                    measurement.metadata = {"test_command": " ".join(test_cmd_args)}
                    
                    all_measurements.append(measurement)
                    
                    if progress:
                        progress.update(progress_task, 
                                      description=f"Measuring {test_name}: {measurement.execution_time_ms:.1f}ms")
        finally:
            if progress:
                progress.stop()
        
        # Filter successful measurements
        successful_measurements = [m for m in all_measurements if m.success]
        
        if not successful_measurements:
            if self.console:
                self.console.print(f"[red]❌ All startup measurements failed for {test_name}[/red]")
            return self._create_failed_profile(test_name, language, configuration, target, all_measurements)
        
        # Calculate statistics
        times = [m.execution_time_ms for m in successful_measurements]
        
        profile = StartupProfile(
            test_name=test_name,
            language=language,
            configuration=configuration,
            target_ms=target,
            measurements=all_measurements,
            average_ms=statistics.mean(times),
            median_ms=statistics.median(times),
            min_ms=min(times),
            max_ms=max(times),
            std_dev_ms=statistics.stdev(times) if len(times) > 1 else 0,
            percentile_95_ms=sorted(times)[int(len(times) * 0.95)] if times else 0,
            percentile_99_ms=sorted(times)[int(len(times) * 0.99)] if times else 0,
            success_rate=len(successful_measurements) / len(all_measurements),
            meets_target=statistics.mean(times) <= target,
            optimization_score=self._calculate_optimization_score(times, target),
            recommendations=[]
        )
        
        # Generate recommendations
        profile.recommendations = self._generate_startup_recommendations(profile)
        
        # Display results
        if self.console:
            status = "✅" if profile.meets_target else "❌"
            self.console.print(f"{status} {test_name}: {profile.average_ms:.2f}ms (target: {target}ms)")
            if not profile.meets_target:
                self.console.print(f"   Exceeds target by {profile.average_ms - target:.2f}ms")
        
        self.profiles.append(profile)
        return profile
    
    def _create_failed_profile(self, test_name: str, language: str, configuration: str, 
                              target: float, measurements: List[StartupMeasurement]) -> StartupProfile:
        """Create a profile for failed startup validation"""
        return StartupProfile(
            test_name=test_name,
            language=language,
            configuration=configuration,
            target_ms=target,
            measurements=measurements,
            average_ms=self.timeout_ms,
            median_ms=self.timeout_ms,
            min_ms=self.timeout_ms,
            max_ms=self.timeout_ms,
            std_dev_ms=0,
            percentile_95_ms=self.timeout_ms,
            percentile_99_ms=self.timeout_ms,
            success_rate=0.0,
            meets_target=False,
            optimization_score=0.0,
            recommendations=["All startup attempts failed - check CLI configuration and dependencies"]
        )
    
    def _calculate_optimization_score(self, times: List[float], target: float) -> float:
        """Calculate optimization score (0-100) based on startup performance"""
        if not times:
            return 0.0
        
        avg_time = statistics.mean(times)
        consistency = 1.0 - (statistics.stdev(times) / avg_time) if len(times) > 1 else 1.0
        
        # Base score: how well we meet the target
        if avg_time <= target * 0.5:
            base_score = 100  # Exceptional performance
        elif avg_time <= target * 0.7:
            base_score = 90   # Excellent performance
        elif avg_time <= target:
            base_score = 80   # Good performance, meets target
        elif avg_time <= target * 1.2:
            base_score = 60   # Acceptable, close to target
        elif avg_time <= target * 1.5:
            base_score = 40   # Poor, significantly over target
        else:
            base_score = 20   # Very poor performance
        
        # Consistency bonus (up to 20 points)
        consistency_bonus = consistency * 20
        
        # Fast startup bonus (if under 50ms)
        speed_bonus = max(0, (50 - avg_time) / 50 * 10) if avg_time < 50 else 0
        
        total_score = min(100, base_score + consistency_bonus + speed_bonus)
        return max(0, total_score)
    
    def _generate_startup_recommendations(self, profile: StartupProfile) -> List[str]:
        """Generate optimization recommendations based on startup profile"""
        recommendations = []
        
        # Target not met
        if not profile.meets_target:
            excess = profile.average_ms - profile.target_ms
            recommendations.append(f"Startup time exceeds target by {excess:.2f}ms. Consider optimization strategies.")
        
        # High startup time
        if profile.average_ms > 200:
            recommendations.append("Very high startup time. Implement lazy loading and reduce import overhead.")
        elif profile.average_ms > 150:
            recommendations.append("High startup time. Consider caching compiled templates and optimizing imports.")
        elif profile.average_ms > profile.target_ms * 1.2:
            recommendations.append("Moderately high startup time. Review initialization code for bottlenecks.")
        
        # High variability
        if profile.std_dev_ms > profile.average_ms * 0.2:
            recommendations.append("High startup time variability. Investigate non-deterministic initialization code.")
        
        # Low success rate
        if profile.success_rate < 0.9:
            recommendations.append("Low startup success rate. Check for intermittent errors or dependency issues.")
        
        # Language-specific recommendations
        if profile.language == "python":
            if profile.average_ms > 80:
                recommendations.append("Python: Consider using importlib for lazy imports and __pycache__ optimization.")
            if profile.std_dev_ms > 10:
                recommendations.append("Python: High variability suggests GIL contention or import races.")
        
        elif profile.language == "nodejs":
            if profile.average_ms > 60:
                recommendations.append("Node.js: Consider using require caching and reducing module resolution overhead.")
            if profile.average_ms > 100:
                recommendations.append("Node.js: Review for synchronous I/O operations during startup.")
        
        elif profile.language == "typescript":
            if profile.average_ms > 70:
                recommendations.append("TypeScript: Ensure proper compilation optimization and consider bundling.")
            if profile.average_ms > 120:
                recommendations.append("TypeScript: Review for excessive type checking during runtime.")
        
        # Performance-based recommendations
        if profile.optimization_score < 60:
            recommendations.append("Low optimization score. Implement comprehensive performance optimization.")
        elif profile.optimization_score < 80:
            recommendations.append("Moderate optimization score. Fine-tune initialization process.")
        
        # Excellent performance
        if profile.meets_target and profile.average_ms < profile.target_ms * 0.7:
            recommendations.append("Excellent startup performance! Consider this configuration as a benchmark.")
        
        return recommendations
    
    def validate_multiple_configurations(self, test_configs: List[Dict[str, Any]]) -> Dict[str, StartupProfile]:
        """Validate startup times for multiple CLI configurations"""
        results = {}
        
        if self.console:
            self.console.print(Panel.fit(
                f"[bold blue]🎯 Startup Validation Suite[/bold blue]\n"
                f"Target: <{self.target_ms}ms | Iterations: {self.iterations} | "
                f"Configurations: {len(test_configs)}",
                title="Goobits CLI Startup Validator"
            ))
        
        # Run validations in parallel where possible
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = {}
            
            for config in test_configs:
                config_name = config.get("name", "unknown")
                cli_command = config.get("command", [])
                language = config.get("language", "python")
                cwd = Path(config.get("cwd")) if config.get("cwd") else None
                
                future = executor.submit(
                    self.validate_cli_startup,
                    cli_command, language, config_name, config_name, cwd
                )
                futures[future] = config_name
            
            # Collect results
            for future in as_completed(futures):
                config_name = futures[future]
                try:
                    profile = future.result(timeout=120)  # 2 minute timeout
                    results[config_name] = profile
                except Exception as e:
                    if self.console:
                        self.console.print(f"[red]❌ Failed {config_name}: {e}[/red]")
        
        return results
    
    def generate_validation_report(self, profiles: Dict[str, StartupProfile] = None) -> str:
        """Generate comprehensive startup validation report"""
        profiles = profiles or {p.test_name: p for p in self.profiles}
        
        if not profiles:
            return "No startup profiles available for reporting."
        
        report_lines = [
            "# Startup Time Validation Report",
            f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}",
            f"Target: <{self.target_ms}ms startup time",
            f"Test iterations: {self.iterations} per configuration",
            ""
        ]
        
        # Executive Summary
        total_configs = len(profiles)
        passing_configs = len([p for p in profiles.values() if p.meets_target])
        overall_success_rate = passing_configs / total_configs if total_configs > 0 else 0
        
        report_lines.extend([
            "## 🎯 Executive Summary",
            f"- **Configurations Tested**: {total_configs}",
            f"- **Passed Target**: {passing_configs} / {total_configs} ({overall_success_rate:.1%})",
            f"- **Overall Status**: {'✅ PASS' if overall_success_rate >= 0.8 else '❌ FAIL'}",
            ""
        ])
        
        # Results Table
        report_lines.extend([
            "## 📊 Startup Time Results",
            "",
            "| Configuration | Language | Avg Time (ms) | Target (ms) | Status | Score | Success Rate |",
            "|---------------|----------|---------------|-------------|---------|-------|--------------|"
        ])
        
        for config_name, profile in profiles.items():
            status = "✅ PASS" if profile.meets_target else "❌ FAIL"
            report_lines.append(
                f"| {config_name} | {profile.language} | {profile.average_ms:.2f} | "
                f"{profile.target_ms:.0f} | {status} | {profile.optimization_score:.0f}/100 | "
                f"{profile.success_rate:.1%} |"
            )
        
        report_lines.extend(["", ""])
        
        # Performance Analysis
        if profiles:
            all_times = []
            for profile in profiles.values():
                if profile.success_rate > 0:
                    all_times.extend([m.execution_time_ms for m in profile.measurements if m.success])
            
            if all_times:
                report_lines.extend([
                    "## 📈 Performance Analysis",
                    f"- **Overall Average**: {statistics.mean(all_times):.2f}ms",
                    f"- **Overall Median**: {statistics.median(all_times):.2f}ms",
                    f"- **Fastest Startup**: {min(all_times):.2f}ms",
                    f"- **Slowest Startup**: {max(all_times):.2f}ms",
                    f"- **95th Percentile**: {sorted(all_times)[int(len(all_times) * 0.95)]:.2f}ms",
                    ""
                ])
        
        # Detailed Results
        for config_name, profile in profiles.items():
            report_lines.extend([
                f"## 🔍 {config_name} Detailed Results",
                f"- **Language**: {profile.language}",
                f"- **Average Startup**: {profile.average_ms:.2f}ms",
                f"- **Median Startup**: {profile.median_ms:.2f}ms",
                f"- **Range**: {profile.min_ms:.2f}ms - {profile.max_ms:.2f}ms",
                f"- **Standard Deviation**: {profile.std_dev_ms:.2f}ms",
                f"- **95th Percentile**: {profile.percentile_95_ms:.2f}ms",
                f"- **Success Rate**: {profile.success_rate:.1%}",
                f"- **Optimization Score**: {profile.optimization_score:.1f}/100",
                f"- **Meets Target**: {'✅ Yes' if profile.meets_target else '❌ No'}",
                ""
            ])
            
            # Recommendations
            if profile.recommendations:
                report_lines.extend(["**Recommendations:**", ""])
                for i, rec in enumerate(profile.recommendations, 1):
                    report_lines.append(f"{i}. {rec}")
                report_lines.append("")
        
        # Global Recommendations
        global_recommendations = self._generate_global_recommendations(profiles)
        if global_recommendations:
            report_lines.extend([
                "## 💡 Global Optimization Recommendations",
                ""
            ])
            for i, rec in enumerate(global_recommendations, 1):
                report_lines.append(f"{i}. {rec}")
            report_lines.append("")
        
        # Raw Data
        report_lines.extend([
            "## 📄 Raw Measurement Data",
            "```json"
        ])
        
        # Export all profiles as JSON
        profiles_data = {}
        for config_name, profile in profiles.items():
            profile_dict = asdict(profile)
            profiles_data[config_name] = profile_dict
        
        report_lines.append(json.dumps(profiles_data, indent=2))
        report_lines.extend(["```", ""])
        
        return "\n".join(report_lines)
    
    def _generate_global_recommendations(self, profiles: Dict[str, StartupProfile]) -> List[str]:
        """Generate global recommendations across all profiles"""
        recommendations = []
        
        if not profiles:
            return recommendations
        
        # Overall failure rate
        total_profiles = len(profiles)
        failed_profiles = [p for p in profiles.values() if not p.meets_target]
        failure_rate = len(failed_profiles) / total_profiles
        
        if failure_rate > 0.5:
            recommendations.append("More than 50% of configurations exceed startup targets. Consider framework-wide optimization.")
        elif failure_rate > 0.2:
            recommendations.append("Multiple configurations exceed startup targets. Review common initialization patterns.")
        
        # Language-specific issues
        lang_performance = {}
        for profile in profiles.values():
            if profile.language not in lang_performance:
                lang_performance[profile.language] = []
            lang_performance[profile.language].append(profile.average_ms)
        
        for language, times in lang_performance.items():
            avg_time = statistics.mean(times)
            target = self.language_targets.get(language, self.target_ms)
            
            if avg_time > target * 1.2:
                recommendations.append(f"{language.title()} shows consistently slow startup times. Implement {language}-specific optimizations.")
        
        # High variability
        all_std_devs = [p.std_dev_ms for p in profiles.values() if p.success_rate > 0]
        if all_std_devs and statistics.mean(all_std_devs) > 20:
            recommendations.append("High startup time variability across configurations. Investigate non-deterministic initialization.")
        
        # Success rate issues
        low_success_profiles = [p for p in profiles.values() if p.success_rate < 0.9]
        if len(low_success_profiles) > 0:
            recommendations.append(f"{len(low_success_profiles)} configurations show reliability issues. Review error handling and dependencies.")
        
        # Best practices
        excellent_profiles = [p for p in profiles.values() if p.optimization_score >= 90]
        if excellent_profiles:
            best_config = max(excellent_profiles, key=lambda p: p.optimization_score)
            recommendations.append(f"Configuration '{best_config.test_name}' shows excellent performance. Consider using as optimization template.")
        
        return recommendations
    
    def save_results(self, profiles: Dict[str, StartupProfile] = None):
        """Save validation results to files"""
        profiles = profiles or {p.test_name: p for p in self.profiles}
        
        # Save validation report
        report = self.generate_validation_report(profiles)
        report_file = self.output_dir / "startup_validation_report.md"
        with open(report_file, 'w') as f:
            f.write(report)
        
        # Save raw data as JSON
        profiles_data = {}
        for config_name, profile in profiles.items():
            profiles_data[config_name] = asdict(profile)
        
        json_file = self.output_dir / "startup_measurements.json"
        with open(json_file, 'w') as f:
            json.dump(profiles_data, f, indent=2)
        
        # Save CSV for analysis
        csv_file = self.output_dir / "startup_times.csv"
        with open(csv_file, 'w') as f:
            f.write("config,language,iteration,command,time_ms,success,meets_target\n")
            for config_name, profile in profiles.items():
                for measurement in profile.measurements:
                    f.write(f"{config_name},{measurement.language},{measurement.iteration},"
                           f"\"{measurement.command}\",{measurement.execution_time_ms},"
                           f"{measurement.success},{profile.meets_target}\n")
        
        if self.console:
            self.console.print(f"\n[green]📁 Validation results saved to {self.output_dir}[/green]")
            self.console.print(f"   📄 Report: {report_file}")
            self.console.print(f"   📊 Data: {json_file}")
            self.console.print(f"   📈 CSV: {csv_file}")


def main():
    """Main entry point for startup validation"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Goobits CLI Startup Time Validator")
    parser.add_argument("--command", nargs="+", help="CLI command to validate")
    parser.add_argument("--language", default="python", choices=["python", "nodejs", "typescript"],
                       help="CLI language")
    parser.add_argument("--config", default="default", help="Configuration name")
    parser.add_argument("--target", type=float, default=100.0, help="Startup time target in ms")
    parser.add_argument("--iterations", type=int, default=10, help="Number of test iterations")
    parser.add_argument("--warmup", type=int, default=2, help="Number of warmup iterations")
    parser.add_argument("--output-dir", type=Path, default=Path("startup_results"),
                       help="Output directory")
    parser.add_argument("--cwd", type=Path, help="Working directory for CLI execution")
    
    args = parser.parse_args()
    
    if not args.command:
        print("Please specify a command to validate with --command")
        return 1
    
    # Create validator
    validator = StartupValidator(
        target_ms=args.target,
        iterations=args.iterations,
        warmup_iterations=args.warmup,
        output_dir=args.output_dir
    )
    
    # Run validation
    profile = validator.validate_cli_startup(
        cli_command=args.command,
        language=args.language,
        configuration=args.config,
        test_name=args.config,
        cwd=args.cwd
    )
    
    # Save results
    validator.save_results()
    
    # Return appropriate exit code
    if profile.meets_target:
        print(f"✅ Startup validation PASSED: {profile.average_ms:.2f}ms < {profile.target_ms}ms")
        return 0
    else:
        print(f"❌ Startup validation FAILED: {profile.average_ms:.2f}ms > {profile.target_ms}ms")
        return 1


if __name__ == "__main__":
    exit(main())