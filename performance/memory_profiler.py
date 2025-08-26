#!/usr/bin/env python3
"""
Memory Usage Profiler for Goobits CLI Framework
Provides detailed memory analysis, leak detection, and optimization recommendations
"""

import gc
import json
import subprocess
import threading
import time
import tracemalloc
import weakref
from collections import defaultdict, deque
from contextlib import contextmanager
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List, Any, Optional

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.progress import Progress
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False


@dataclass
class MemorySnapshot:
    """Memory usage snapshot at a point in time"""
    timestamp: float
    rss_mb: float  # Resident Set Size
    vms_mb: float  # Virtual Memory Size
    percent: float  # Memory percentage
    available_mb: float  # Available memory
    phase: str  # What phase of execution
    metadata: Dict[str, Any] = None


@dataclass
class MemoryAllocation:
    """Individual memory allocation tracking"""
    filename: str
    lineno: int
    size_mb: float
    count: int
    traceback: List[str]


@dataclass
class MemoryProfile:
    """Complete memory profile for a CLI execution"""
    command: str
    language: str
    configuration: str
    peak_memory_mb: float
    baseline_memory_mb: float
    memory_increase_mb: float
    execution_time_ms: float
    snapshots: List[MemorySnapshot]
    allocations: List[MemoryAllocation]
    leak_detected: bool = False
    optimization_score: float = 0.0


class MemoryProfiler:
    """Comprehensive memory profiling for CLI applications"""
    
    def __init__(self, 
                 sample_interval: float = 0.01,  # 10ms sampling
                 max_snapshots: int = 10000,
                 track_allocations: bool = True):
        self.sample_interval = sample_interval
        self.max_snapshots = max_snapshots
        self.track_allocations = track_allocations
        
        # Console setup
        if RICH_AVAILABLE:
            self.console = Console()
        else:
            self.console = None
        
        # Profiling state
        self.is_profiling = False
        self.snapshots: deque = deque(maxlen=max_snapshots)
        self.baseline_memory = 0
        self.peak_memory = 0
        self.current_phase = "initialization"
        
        # Memory leak detection
        self.object_counts: Dict[type, int] = {}
        self.weak_refs: List[weakref.ref] = []
        
        # Thread management
        self.profiling_thread: Optional[threading.Thread] = None
        self.stop_event = threading.Event()
        
    @contextmanager
    def profile_memory(self, command: str, phase: str = "execution"):
        """Context manager for memory profiling"""
        self.start_profiling(command, phase)
        try:
            yield self
        finally:
            self.stop_profiling()
    
    def start_profiling(self, command: str, phase: str = "execution"):
        """Start memory profiling"""
        if not PSUTIL_AVAILABLE:
            print("⚠️ psutil not available - memory profiling disabled")
            return
        
        self.current_command = command
        self.current_phase = phase
        self.is_profiling = True
        self.stop_event.clear()
        
        # Start tracemalloc for allocation tracking
        if self.track_allocations and not tracemalloc.is_tracing():
            tracemalloc.start()
        
        # Get baseline memory
        process = psutil.Process()
        memory_info = process.memory_info()
        self.baseline_memory = memory_info.rss / 1024 / 1024  # MB
        self.peak_memory = self.baseline_memory
        
        # Start profiling thread
        self.profiling_thread = threading.Thread(
            target=self._profiling_loop,
            daemon=True
        )
        self.profiling_thread.start()
        
        if self.console:
            self.console.print(f"[green]🔍 Started memory profiling for: {command}[/green]")
    
    def stop_profiling(self) -> MemoryProfile:
        """Stop profiling and return results"""
        if not self.is_profiling:
            return None
        
        self.is_profiling = False
        self.stop_event.set()
        
        # Wait for profiling thread to finish
        if self.profiling_thread:
            self.profiling_thread.join(timeout=1.0)
        
        # Collect final snapshot
        if PSUTIL_AVAILABLE:
            self._take_snapshot("final")
        
        # Analyze allocations
        allocations = []
        if self.track_allocations and tracemalloc.is_tracing():
            current, peak = tracemalloc.get_traced_memory()
            stats = tracemalloc.take_snapshot().statistics('lineno')
            
            for stat in stats[:20]:  # Top 20 allocations
                allocations.append(MemoryAllocation(
                    filename=stat.traceback.format()[-1] if stat.traceback else "unknown",
                    lineno=stat.traceback[0].lineno if stat.traceback else 0,
                    size_mb=stat.size / 1024 / 1024,
                    count=stat.count,
                    traceback=stat.traceback.format() if stat.traceback else []
                ))
            
            tracemalloc.stop()
        
        # Create memory profile
        profile = MemoryProfile(
            command=getattr(self, 'current_command', 'unknown'),
            language="python",  # Default, can be overridden
            configuration="default",
            peak_memory_mb=self.peak_memory,
            baseline_memory_mb=self.baseline_memory,
            memory_increase_mb=self.peak_memory - self.baseline_memory,
            execution_time_ms=0,  # To be filled by caller
            snapshots=list(self.snapshots),
            allocations=allocations,
            leak_detected=self._detect_memory_leaks(),
            optimization_score=self._calculate_optimization_score()
        )
        
        if self.console:
            self.console.print(f"[blue]📊 Memory profiling completed[/blue]")
            self.console.print(f"  Peak: {profile.peak_memory_mb:.2f}MB")
            self.console.print(f"  Increase: {profile.memory_increase_mb:.2f}MB")
            if profile.leak_detected:
                self.console.print(f"  [red]⚠️ Memory leak detected![/red]")
        
        return profile
    
    def _profiling_loop(self):
        """Background memory profiling loop"""
        while not self.stop_event.wait(self.sample_interval):
            if not self.is_profiling:
                break
            self._take_snapshot(self.current_phase)
    
    def _take_snapshot(self, phase: str):
        """Take a memory snapshot"""
        if not PSUTIL_AVAILABLE:
            return
        
        try:
            process = psutil.Process()
            memory_info = process.memory_info()
            virtual_memory = psutil.virtual_memory()
            
            current_memory = memory_info.rss / 1024 / 1024  # MB
            
            snapshot = MemorySnapshot(
                timestamp=time.time(),
                rss_mb=current_memory,
                vms_mb=memory_info.vms / 1024 / 1024,
                percent=process.memory_percent(),
                available_mb=virtual_memory.available / 1024 / 1024,
                phase=phase
            )
            
            self.snapshots.append(snapshot)
            
            # Update peak memory
            if current_memory > self.peak_memory:
                self.peak_memory = current_memory
                
        except Exception:
            pass  # Ignore errors in profiling thread
    
    @contextmanager
    def phase(self, phase_name: str):
        """Context manager to mark profiling phases"""
        old_phase = self.current_phase
        self.current_phase = phase_name
        try:
            yield
        finally:
            self.current_phase = old_phase
    
    def track_object(self, obj: Any, name: str = None):
        """Track an object for leak detection"""
        obj_type = type(obj)
        self.object_counts[obj_type] = self.object_counts.get(obj_type, 0) + 1
        
        # Store weak reference to track if object is properly garbage collected
        weak_ref = weakref.ref(obj)
        self.weak_refs.append(weak_ref)
    
    def _detect_memory_leaks(self) -> bool:
        """Detect potential memory leaks"""
        # Force garbage collection
        collected = gc.collect()
        
        # Check if tracked objects were properly cleaned up
        alive_refs = [ref for ref in self.weak_refs if ref() is not None]
        leak_percentage = len(alive_refs) / len(self.weak_refs) if self.weak_refs else 0
        
        # Consider it a leak if more than 50% of objects are still alive
        return leak_percentage > 0.5
    
    def _calculate_optimization_score(self) -> float:
        """Calculate memory optimization score (0-100)"""
        if not self.snapshots:
            return 0.0
        
        # Factors for scoring:
        # 1. Peak memory usage (lower is better)
        # 2. Memory stability (less variation is better)  
        # 3. Memory cleanup (final < peak is better)
        
        memory_values = [s.rss_mb for s in self.snapshots]
        
        if len(memory_values) < 2:
            return 50.0  # Neutral score
        
        # Peak memory factor (50MB is considered good baseline)
        peak_factor = max(0, 100 - (self.peak_memory - 50))
        peak_factor = max(0, min(100, peak_factor))
        
        # Stability factor (low standard deviation is good)
        import statistics
        std_dev = statistics.stdev(memory_values)
        stability_factor = max(0, 100 - (std_dev * 10))  # Scale std dev
        stability_factor = max(0, min(100, stability_factor))
        
        # Cleanup factor (memory should decrease toward end)
        final_memory = memory_values[-1]
        cleanup_factor = 100 if final_memory <= self.baseline_memory * 1.1 else 50
        
        # Weighted average
        score = (peak_factor * 0.5) + (stability_factor * 0.3) + (cleanup_factor * 0.2)
        return min(100.0, max(0.0, score))
    
    def analyze_snapshots(self) -> Dict[str, Any]:
        """Analyze memory snapshots for patterns"""
        if not self.snapshots:
            return {"error": "No snapshots available"}
        
        memory_values = [s.rss_mb for s in self.snapshots]
        timestamps = [s.timestamp for s in self.snapshots]
        
        import statistics
        
        analysis = {
            "total_snapshots": len(self.snapshots),
            "duration_seconds": timestamps[-1] - timestamps[0] if len(timestamps) > 1 else 0,
            "memory_stats": {
                "min_mb": min(memory_values),
                "max_mb": max(memory_values),
                "avg_mb": statistics.mean(memory_values),
                "median_mb": statistics.median(memory_values),
                "std_dev_mb": statistics.stdev(memory_values) if len(memory_values) > 1 else 0
            },
            "peak_memory_mb": self.peak_memory,
            "baseline_memory_mb": self.baseline_memory,
            "memory_increase_mb": self.peak_memory - self.baseline_memory,
            "phases": self._analyze_phases(),
            "trends": self._analyze_trends(memory_values, timestamps)
        }
        
        return analysis
    
    def _analyze_phases(self) -> Dict[str, Any]:
        """Analyze memory usage by phases"""
        phase_data = defaultdict(list)
        
        for snapshot in self.snapshots:
            phase_data[snapshot.phase].append(snapshot.rss_mb)
        
        phase_analysis = {}
        for phase, values in phase_data.items():
            if values:
                import statistics
                phase_analysis[phase] = {
                    "count": len(values),
                    "avg_mb": statistics.mean(values),
                    "min_mb": min(values),
                    "max_mb": max(values),
                    "increase_mb": max(values) - min(values) if len(values) > 1 else 0
                }
        
        return phase_analysis
    
    def _analyze_trends(self, memory_values: List[float], timestamps: List[float]) -> Dict[str, Any]:
        """Analyze memory usage trends"""
        if len(memory_values) < 3:
            return {"trend": "insufficient_data"}
        
        # Calculate memory growth rate
        time_span = timestamps[-1] - timestamps[0]
        memory_change = memory_values[-1] - memory_values[0]
        growth_rate = memory_change / time_span if time_span > 0 else 0
        
        # Detect patterns
        trends = {
            "growth_rate_mb_per_sec": growth_rate,
            "overall_trend": "increasing" if growth_rate > 0.1 else "decreasing" if growth_rate < -0.1 else "stable",
            "volatility": "high" if max(memory_values) - min(memory_values) > 20 else "low",
            "final_vs_baseline": memory_values[-1] / memory_values[0] if memory_values[0] > 0 else 1.0
        }
        
        # Check for memory spikes
        import statistics
        mean_memory = statistics.mean(memory_values)
        spikes = [v for v in memory_values if v > mean_memory * 1.5]
        trends["spike_count"] = len(spikes)
        trends["max_spike_mb"] = max(spikes) if spikes else 0
        
        return trends
    
    def generate_memory_report(self, profile: MemoryProfile) -> str:
        """Generate comprehensive memory analysis report"""
        report_lines = [
            "# Memory Profile Report",
            f"Command: {profile.command}",
            f"Language: {profile.language}",
            f"Configuration: {profile.configuration}",
            f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}",
            ""
        ]
        
        # Memory Summary
        report_lines.extend([
            "## 📊 Memory Usage Summary",
            f"- **Peak Memory**: {profile.peak_memory_mb:.2f}MB",
            f"- **Baseline Memory**: {profile.baseline_memory_mb:.2f}MB", 
            f"- **Memory Increase**: {profile.memory_increase_mb:.2f}MB",
            f"- **Optimization Score**: {profile.optimization_score:.1f}/100",
            f"- **Memory Leak Detected**: {'Yes' if profile.leak_detected else 'No'}",
            ""
        ])
        
        # Analysis
        analysis = self.analyze_snapshots()
        if "memory_stats" in analysis:
            stats = analysis["memory_stats"]
            report_lines.extend([
                "## 📈 Statistical Analysis",
                f"- **Average Memory**: {stats['avg_mb']:.2f}MB",
                f"- **Median Memory**: {stats['median_mb']:.2f}MB",
                f"- **Memory Range**: {stats['min_mb']:.2f}MB - {stats['max_mb']:.2f}MB",
                f"- **Standard Deviation**: {stats['std_dev_mb']:.2f}MB",
                f"- **Total Snapshots**: {analysis['total_snapshots']}",
                f"- **Profiling Duration**: {analysis['duration_seconds']:.2f}s",
                ""
            ])
        
        # Phase Analysis
        if "phases" in analysis:
            report_lines.extend(["## 🔄 Memory Usage by Phase", ""])
            for phase, data in analysis["phases"].items():
                report_lines.extend([
                    f"### {phase.title()} Phase",
                    f"- Average: {data['avg_mb']:.2f}MB",
                    f"- Range: {data['min_mb']:.2f}MB - {data['max_mb']:.2f}MB",
                    f"- Memory Increase: {data['increase_mb']:.2f}MB",
                    ""
                ])
        
        # Trends
        if "trends" in analysis:
            trends = analysis["trends"]
            report_lines.extend([
                "## 📊 Memory Trends",
                f"- **Overall Trend**: {trends['overall_trend'].title()}",
                f"- **Growth Rate**: {trends['growth_rate_mb_per_sec']:.3f}MB/sec",
                f"- **Volatility**: {trends['volatility'].title()}",
                f"- **Final vs Baseline**: {trends['final_vs_baseline']:.2f}x",
                ""
            ])
            
            if trends["spike_count"] > 0:
                report_lines.extend([
                    f"- **Memory Spikes**: {trends['spike_count']} detected",
                    f"- **Largest Spike**: {trends['max_spike_mb']:.2f}MB",
                    ""
                ])
        
        # Top Allocations
        if profile.allocations:
            report_lines.extend(["## 🔍 Top Memory Allocations", ""])
            for i, alloc in enumerate(profile.allocations[:10], 1):
                report_lines.extend([
                    f"### {i}. {alloc.size_mb:.2f}MB ({alloc.count} allocations)",
                    f"**Location**: {alloc.filename}:{alloc.lineno}",
                    ""
                ])
        
        # Recommendations
        recommendations = self._generate_memory_recommendations(profile, analysis)
        if recommendations:
            report_lines.extend(["## 💡 Optimization Recommendations", ""])
            for i, rec in enumerate(recommendations, 1):
                report_lines.append(f"{i}. {rec}")
            report_lines.append("")
        
        # Raw Data
        report_lines.extend([
            "## 📄 Raw Profile Data",
            "```json"
        ])
        
        profile_dict = asdict(profile)
        # Convert snapshots to dict for JSON serialization
        profile_dict["snapshots"] = [asdict(s) for s in profile.snapshots]
        profile_dict["allocations"] = [asdict(a) for a in profile.allocations]
        
        report_lines.append(json.dumps(profile_dict, indent=2))
        report_lines.extend(["```", ""])
        
        return "\n".join(report_lines)
    
    def _generate_memory_recommendations(self, profile: MemoryProfile, analysis: Dict[str, Any]) -> List[str]:
        """Generate memory optimization recommendations"""
        recommendations = []
        
        # High memory usage
        if profile.peak_memory_mb > 100:
            recommendations.append(f"High peak memory usage ({profile.peak_memory_mb:.1f}MB). Consider implementing memory pooling or reducing object creation.")
        
        # Large memory increase
        if profile.memory_increase_mb > 50:
            recommendations.append(f"Large memory increase during execution (+{profile.memory_increase_mb:.1f}MB). Review for memory leaks or unnecessary allocations.")
        
        # Memory leaks
        if profile.leak_detected:
            recommendations.append("Memory leak detected. Review object lifecycle management and ensure proper cleanup.")
        
        # Volatility
        trends = analysis.get("trends", {})
        if trends.get("volatility") == "high":
            recommendations.append("High memory volatility detected. Consider implementing more consistent memory usage patterns.")
        
        # Growth rate
        growth_rate = trends.get("growth_rate_mb_per_sec", 0)
        if growth_rate > 1.0:
            recommendations.append(f"High memory growth rate ({growth_rate:.2f}MB/s). Implement memory cleanup during execution.")
        
        # Spikes
        spike_count = trends.get("spike_count", 0)
        if spike_count > 3:
            recommendations.append(f"Multiple memory spikes detected ({spike_count}). Investigate sudden memory allocations.")
        
        # Top allocations
        if profile.allocations:
            large_allocs = [a for a in profile.allocations if a.size_mb > 10]
            if large_allocs:
                recommendations.append(f"Large memory allocations detected. Review top {len(large_allocs)} allocation sources.")
        
        # Low optimization score
        if profile.optimization_score < 60:
            recommendations.append("Low memory optimization score. Consider implementing caching, object reuse, or lazy loading.")
        
        # Final cleanup
        final_vs_baseline = trends.get("final_vs_baseline", 1.0)
        if final_vs_baseline > 1.2:
            recommendations.append("Memory not properly cleaned up after execution. Ensure proper resource disposal.")
        
        if not recommendations:
            recommendations.append("Memory usage appears optimal. Good job!")
        
        return recommendations


class CLIMemoryBenchmark:
    """Benchmark memory usage across different CLI configurations"""
    
    def __init__(self, output_dir: Path = Path("memory_results")):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        if RICH_AVAILABLE:
            self.console = Console()
        else:
            self.console = None
        
        self.profiles: List[MemoryProfile] = []
    
    def benchmark_cli_memory(self, 
                           cli_command: List[str], 
                           language: str = "python",
                           configuration: str = "default",
                           iterations: int = 3) -> MemoryProfile:
        """Benchmark memory usage of a CLI command"""
        
        profiler = MemoryProfiler(sample_interval=0.005)  # 5ms sampling for CLI
        profiles = []
        
        for iteration in range(iterations):
            if self.console:
                self.console.print(f"[blue]🔄 Memory benchmark iteration {iteration + 1}/{iterations}[/blue]")
            
            try:
                with profiler.profile_memory(" ".join(cli_command), "cli_execution"):
                    start_time = time.perf_counter()
                    
                    # Execute CLI command
                    process = subprocess.run(
                        cli_command,
                        capture_output=True,
                        text=True,
                        timeout=30
                    )
                    
                    end_time = time.perf_counter()
                
                profile = profiler.stop_profiling()
                if profile:
                    profile.execution_time_ms = (end_time - start_time) * 1000
                    profile.language = language
                    profile.configuration = configuration
                    profiles.append(profile)
                
            except Exception as e:
                if self.console:
                    self.console.print(f"[red]❌ Iteration {iteration + 1} failed: {e}[/red]")
                continue
        
        # Return best profile (lowest memory usage)
        if profiles:
            best_profile = min(profiles, key=lambda p: p.peak_memory_mb)
            self.profiles.append(best_profile)
            return best_profile
        
        return None
    
    def benchmark_multiple_configs(self, test_configs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Benchmark multiple CLI configurations"""
        results = {}
        
        for config in test_configs:
            config_name = config.get("name", "unknown")
            cli_command = config.get("command", [])
            language = config.get("language", "python")
            
            if self.console:
                self.console.print(f"\n[green]🧪 Testing configuration: {config_name}[/green]")
            
            profile = self.benchmark_cli_memory(
                cli_command=cli_command,
                language=language,
                configuration=config_name,
                iterations=config.get("iterations", 3)
            )
            
            if profile:
                results[config_name] = profile
            else:
                if self.console:
                    self.console.print(f"[red]❌ Failed to profile {config_name}[/red]")
        
        return results
    
    def generate_comparison_report(self, profiles: Dict[str, MemoryProfile]) -> str:
        """Generate memory comparison report across configurations"""
        if not profiles:
            return "No memory profiles available for comparison."
        
        report_lines = [
            "# Memory Usage Comparison Report",
            f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}",
            f"Configurations Tested: {len(profiles)}",
            ""
        ]
        
        # Summary Table
        report_lines.extend([
            "## 📊 Memory Usage Summary",
            "",
            "| Configuration | Peak Memory (MB) | Memory Increase (MB) | Optimization Score | Leak Detected |",
            "|---------------|------------------|---------------------|-------------------|---------------|"
        ])
        
        for config_name, profile in profiles.items():
            leak_status = "⚠️ Yes" if profile.leak_detected else "✅ No"
            score_status = f"{profile.optimization_score:.1f}/100"
            
            report_lines.append(
                f"| {config_name} | {profile.peak_memory_mb:.2f} | "
                f"{profile.memory_increase_mb:.2f} | {score_status} | {leak_status} |"
            )
        
        report_lines.extend(["", ""])
        
        # Best and Worst Performers
        best_memory = min(profiles.values(), key=lambda p: p.peak_memory_mb)
        worst_memory = max(profiles.values(), key=lambda p: p.peak_memory_mb)
        
        report_lines.extend([
            "## 🏆 Performance Rankings",
            f"**Best Memory Usage**: {best_memory.configuration} ({best_memory.peak_memory_mb:.2f}MB)",
            f"**Highest Memory Usage**: {worst_memory.configuration} ({worst_memory.peak_memory_mb:.2f}MB)",
            f"**Memory Difference**: {worst_memory.peak_memory_mb - best_memory.peak_memory_mb:.2f}MB",
            ""
        ])
        
        # Detailed Analysis
        for config_name, profile in profiles.items():
            report_lines.extend([
                f"## 📈 {config_name} Configuration",
                f"- **Peak Memory**: {profile.peak_memory_mb:.2f}MB",
                f"- **Execution Time**: {profile.execution_time_ms:.2f}ms",
                f"- **Optimization Score**: {profile.optimization_score:.1f}/100",
                f"- **Memory Efficiency**: {profile.execution_time_ms / profile.peak_memory_mb:.2f}ms/MB",
                ""
            ])
        
        # Recommendations
        recommendations = self._generate_comparison_recommendations(profiles)
        if recommendations:
            report_lines.extend(["## 💡 Optimization Recommendations", ""])
            for i, rec in enumerate(recommendations, 1):
                report_lines.append(f"{i}. {rec}")
        
        return "\n".join(report_lines)
    
    def _generate_comparison_recommendations(self, profiles: Dict[str, MemoryProfile]) -> List[str]:
        """Generate recommendations based on profile comparison"""
        recommendations = []
        
        if not profiles:
            return recommendations
        
        memory_values = [p.peak_memory_mb for p in profiles.values()]
        avg_memory = sum(memory_values) / len(memory_values)
        max_memory = max(memory_values)
        min_memory = min(memory_values)
        
        # High variation in memory usage
        if max_memory - min_memory > 20:
            recommendations.append(f"High memory usage variation ({max_memory - min_memory:.1f}MB difference). Standardize configurations for consistency.")
        
        # High average memory
        if avg_memory > 75:
            recommendations.append(f"Average memory usage is high ({avg_memory:.1f}MB). Consider implementing memory optimization across all configurations.")
        
        # Memory leaks
        leaky_configs = [name for name, profile in profiles.items() if profile.leak_detected]
        if leaky_configs:
            recommendations.append(f"Memory leaks detected in: {', '.join(leaky_configs)}. Investigate object lifecycle management.")
        
        # Low optimization scores
        low_score_configs = [name for name, profile in profiles.items() if profile.optimization_score < 60]
        if low_score_configs:
            recommendations.append(f"Low optimization scores in: {', '.join(low_score_configs)}. Review memory management practices.")
        
        return recommendations


def main():
    """Main entry point for memory profiling"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Goobits CLI Memory Profiler")
    parser.add_argument("--command", nargs="+", help="CLI command to profile")
    parser.add_argument("--language", default="python", choices=["python", "nodejs", "typescript"],
                       help="CLI language")
    parser.add_argument("--config", default="default", help="Configuration name")
    parser.add_argument("--iterations", type=int, default=3, help="Number of test iterations")
    parser.add_argument("--output-dir", type=Path, default=Path("memory_results"),
                       help="Output directory")
    
    args = parser.parse_args()
    
    if not args.command:
        print("Please specify a command to profile with --command")
        return 1
    
    # Create benchmark
    benchmark = CLIMemoryBenchmark(args.output_dir)
    
    # Run memory benchmark
    profile = benchmark.benchmark_cli_memory(
        cli_command=args.command,
        language=args.language,
        configuration=args.config,
        iterations=args.iterations
    )
    
    if profile:
        # Generate report
        profiler = MemoryProfiler()
        report = profiler.generate_memory_report(profile)
        
        # Save report
        report_file = args.output_dir / f"memory_profile_{args.config}.md"
        with open(report_file, 'w') as f:
            f.write(report)
        
        if benchmark.console:
            benchmark.console.print(f"[green]📁 Memory profile saved to {report_file}[/green]")
        else:
            print(f"📁 Memory profile saved to {report_file}")
        
        return 0
    else:
        print("❌ Memory profiling failed")
        return 1


if __name__ == "__main__":
    exit(main())