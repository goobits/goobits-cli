"""

Performance Monitoring Tools for CLI Framework

Provides benchmarking, profiling, and performance tracking

"""




import gc


import psutil



import threading

import time

from collections import defaultdict, deque

from contextlib import contextmanager

from dataclasses import dataclass, field


from typing import Any, Dict, List, Optional

import cProfile

import pstats

import tracemalloc

from io import StringIO





@dataclass

class PerformanceMetric:

    """Individual performance metric"""

    name: str

    value: float

    unit: str

    timestamp: float = field(default_factory=time.time)

    tags: Dict[str, str] = field(default_factory=dict)

    

    def __str__(self) -> str:

        tags_str = ", ".join(f"{k}={v}" for k, v in self.tags.items())

        return f"{self.name}: {self.value:.4f}{self.unit} [{tags_str}]"





@dataclass

class StartupMetrics:

    """Startup performance metrics"""

    total_time: float

    import_time: float

    initialization_time: float

    component_load_time: float

    template_load_time: float

    config_load_time: float

    memory_usage: int

    import_count: int

    component_count: int

    template_count: int

    

    def is_under_target(self, target_ms: int = 100) -> bool:

        """Check if startup is under target time"""

        return (self.total_time * 1000) < target_ms

    

    def __str__(self) -> str:

        return (f"Startup Metrics:\n"

                f"  Total: {self.total_time*1000:.2f}ms\n"

                f"  Import: {self.import_time*1000:.2f}ms ({self.import_count} modules)\n"

                f"  Init: {self.initialization_time*1000:.2f}ms\n"

                f"  Components: {self.component_load_time*1000:.2f}ms ({self.component_count} loaded)\n"

                f"  Templates: {self.template_load_time*1000:.2f}ms ({self.template_count} loaded)\n"

                f"  Config: {self.config_load_time*1000:.2f}ms\n"

                f"  Memory: {self.memory_usage/1024/1024:.2f}MB\n"

                f"  Target: {'✓' if self.is_under_target() else '✗'} <100ms")





class StartupBenchmark:

    """Benchmarks CLI startup performance"""

    

    def __init__(self):

        self.start_time: Optional[float] = None

        self.phases: Dict[str, float] = {}

        self.phase_stack: List[str] = []

        self.import_count = 0

        self.component_count = 0

        self.template_count = 0

        self.original_import = None

        

    def start(self):

        """Start benchmarking"""

        self.start_time = time.perf_counter()

        self.phases = {}

        self.phase_stack = []

        self._setup_import_tracking()

        tracemalloc.start()

    

    def _setup_import_tracking(self):

        """Setup import tracking to measure import overhead"""

        self.original_import = __builtins__.__import__

        

        def tracking_import(name, *args, **kwargs):

            self.import_count += 1

            return self.original_import(name, *args, **kwargs)

        

        __builtins__.__import__ = tracking_import

    

    @contextmanager

    def phase(self, name: str):

        """Context manager to measure a specific phase"""

        start_time = time.perf_counter()

        self.phase_stack.append(name)

        

        try:

            yield

        finally:

            end_time = time.perf_counter()

            phase_time = end_time - start_time

            self.phases[name] = phase_time

            self.phase_stack.pop()

    

    def add_component(self):

        """Track component loading"""

        self.component_count += 1

    

    def add_template(self):

        """Track template loading"""

        self.template_count += 1

    

    def finish(self) -> StartupMetrics:

        """Finish benchmarking and return metrics"""

        if not self.start_time:

            raise RuntimeError("Benchmark not started")

        

        total_time = time.perf_counter() - self.start_time

        

        # Restore original import

        if self.original_import:

            __builtins__.__import__ = self.original_import

        

        # Get memory usage

        current, peak = tracemalloc.get_traced_memory()

        tracemalloc.stop()

        

        return StartupMetrics(

            total_time=total_time,

            import_time=self.phases.get("import", 0),

            initialization_time=self.phases.get("initialization", 0),

            component_load_time=self.phases.get("component_loading", 0),

            template_load_time=self.phases.get("template_loading", 0),

            config_load_time=self.phases.get("config_loading", 0),

            memory_usage=current,

            import_count=self.import_count,

            component_count=self.component_count,

            template_count=self.template_count

        )





class MemoryTracker:

    """Tracks memory usage during CLI execution"""

    

    def __init__(self, sample_interval: float = 1.0):

        self.sample_interval = sample_interval

        self.samples: deque = deque(maxlen=1000)

        self.peak_memory = 0

        self.baseline_memory = 0

        self._tracking = False

        self._tracking_thread: Optional[threading.Thread] = None

        

    def start(self):

        """Start memory tracking"""

        if self._tracking:

            return

        

        self.baseline_memory = psutil.Process().memory_info().rss

        self.peak_memory = self.baseline_memory

        self._tracking = True

        

        self._tracking_thread = threading.Thread(target=self._track_memory, daemon=True)

        self._tracking_thread.start()

    

    def stop(self) -> Dict[str, Any]:

        """Stop memory tracking and return results"""

        self._tracking = False

        if self._tracking_thread:

            self._tracking_thread.join(timeout=1.0)

        

        if not self.samples:

            return {"error": "No samples collected"}

        

        memory_values = [sample[1] for sample in self.samples]

        return {

            "baseline_mb": self.baseline_memory / 1024 / 1024,

            "peak_mb": self.peak_memory / 1024 / 1024,

            "current_mb": memory_values[-1] / 1024 / 1024 if memory_values else 0,

            "average_mb": sum(memory_values) / len(memory_values) / 1024 / 1024,

            "samples_count": len(self.samples),

            "total_increase_mb": (self.peak_memory - self.baseline_memory) / 1024 / 1024

        }

    

    def _track_memory(self):

        """Background thread that tracks memory usage"""

        process = psutil.Process()

        

        while self._tracking:

            try:

                memory_info = process.memory_info()

                current_memory = memory_info.rss

                self.samples.append((time.time(), current_memory))

                

                if current_memory > self.peak_memory:

                    self.peak_memory = current_memory

                

                time.sleep(self.sample_interval)

            except Exception:

                break

    

    @contextmanager

    def measure_block(self, block_name: str):

        """Context manager to measure memory for a specific block"""

        gc.collect()  # Force garbage collection for accurate measurement

        start_memory = psutil.Process().memory_info().rss

        

        yield

        

        gc.collect()

        end_memory = psutil.Process().memory_info().rss

        increase = end_memory - start_memory

        

        print(f"Memory increase for {block_name}: {increase / 1024 / 1024:.2f}MB")





class CommandProfiler:

    """Profiles command execution for performance optimization"""

    

    def __init__(self):

        self.profiles: Dict[str, pstats.Stats] = {}

        self.execution_times: Dict[str, List[float]] = defaultdict(list)

    

    @contextmanager

    def profile_command(self, command_name: str):

        """Profile a command execution"""

        profiler = cProfile.Profile()

        start_time = time.perf_counter()

        

        profiler.enable()

        try:

            yield

        finally:

            profiler.disable()

            execution_time = time.perf_counter() - start_time

            

            # Store execution time

            self.execution_times[command_name].append(execution_time)

            

            # Store profiling data

            stats = pstats.Stats(profiler)

            if command_name in self.profiles:

                self.profiles[command_name].add(stats)

            else:

                self.profiles[command_name] = stats

    

    def get_command_stats(self, command_name: str) -> Optional[Dict[str, Any]]:

        """Get statistics for a command"""

        if command_name not in self.execution_times:

            return None

        

        times = self.execution_times[command_name]

        stats_data: Dict[str, Any] = {

            "execution_count": len(times),

            "avg_time": sum(times) / len(times),

            "min_time": min(times),

            "max_time": max(times),

            "total_time": sum(times)

        }

        

        if command_name in self.profiles:

            # Get top functions from profiler

            from contextlib import redirect_stdout
            
            stream = StringIO()
            
            with redirect_stdout(stream):
                self.profiles[command_name].sort_stats('cumulative').print_stats(10)

            stats_data["profile"] = stream.getvalue()

        

        return stats_data

    

    def get_all_stats(self) -> Dict[str, Dict[str, Any]]:

        """Get statistics for all commands"""

        return {

            cmd: stats

            for cmd in self.execution_times.keys()

            if (stats := self.get_command_stats(cmd)) is not None

        }





class PerformanceMonitor:

    """Main performance monitoring system"""

    

    def __init__(self):

        self.startup_benchmark = StartupBenchmark()

        self.memory_tracker = MemoryTracker()

        self.command_profiler = CommandProfiler()

        self.metrics: List[PerformanceMetric] = []

        self.regression_threshold = 0.1  # 10% regression threshold

        self.baseline_metrics: Dict[str, float] = {}

    

    def start_monitoring(self):

        """Start comprehensive monitoring"""

        self.startup_benchmark.start()

        self.memory_tracker.start()

    

    def record_metric(self, name: str, value: float, unit: str, 

                     tags: Optional[Dict[str, str]] = None):

        """Record a performance metric"""

        metric = PerformanceMetric(

            name=name,

            value=value,

            unit=unit,

            tags=tags or {}

        )

        self.metrics.append(metric)

        

        # Check for regression

        if name in self.baseline_metrics:

            baseline = self.baseline_metrics[name]

            if value > baseline * (1 + self.regression_threshold):

                print(f"⚠️  Performance regression detected in {name}: "

                      f"{value:.4f}{unit} vs baseline {baseline:.4f}{unit}")

    

    @contextmanager

    def measure_operation(self, operation_name: str, 

                         tags: Optional[Dict[str, str]] = None):

        """Context manager to measure an operation"""

        start_time = time.perf_counter()

        start_memory = psutil.Process().memory_info().rss

        

        try:

            yield

        finally:

            end_time = time.perf_counter()

            end_memory = psutil.Process().memory_info().rss

            

            execution_time = end_time - start_time

            memory_increase = end_memory - start_memory

            

            self.record_metric(f"{operation_name}_time", execution_time, "s", tags)

            if memory_increase > 0:

                self.record_metric(f"{operation_name}_memory", 

                                 memory_increase / 1024 / 1024, "MB", tags)

    

    def benchmark_startup(self) -> StartupMetrics:

        """Run startup benchmark"""

        from typing import cast
        result = self.startup_benchmark.finish()
        return cast(StartupMetrics, result)

    

    def analyze_memory_usage(self) -> Dict[str, Any]:

        """Analyze current memory usage"""

        result = self.memory_tracker.stop()
        return dict(result) if isinstance(result, dict) else {"error": "Could not get memory stats"}

    

    def detect_regressions(self, new_metrics: Dict[str, float]) -> List[str]:

        """Detect performance regressions"""

        regressions = []

        

        for metric_name, new_value in new_metrics.items():

            if metric_name in self.baseline_metrics:

                baseline = self.baseline_metrics[metric_name]

                if new_value > baseline * (1 + self.regression_threshold):

                    regression_pct = ((new_value - baseline) / baseline) * 100

                    regressions.append(

                        f"{metric_name}: {regression_pct:.1f}% regression "

                        f"({new_value:.4f} vs {baseline:.4f})"

                    )

        

        return regressions

    

    def set_baseline(self, metrics: Dict[str, float]):

        """Set baseline metrics for regression detection"""

        self.baseline_metrics.update(metrics)

    

    def generate_report(self) -> str:

        """Generate comprehensive performance report"""

        report = []

        report.append("=== Performance Report ===\n")

        

        # Startup metrics

        if hasattr(self.startup_benchmark, 'start_time') and self.startup_benchmark.start_time:

            startup_metrics = self.startup_benchmark.finish()

            report.append("Startup Performance:")

            report.append(str(startup_metrics))

            report.append("")

        

        # Memory usage

        memory_stats = self.memory_tracker.stop()

        if "error" not in memory_stats:

            report.append("Memory Usage:")

            report.append(f"  Peak: {memory_stats['peak_mb']:.2f}MB")

            report.append(f"  Average: {memory_stats['average_mb']:.2f}MB")

            report.append(f"  Total Increase: {memory_stats['total_increase_mb']:.2f}MB")

            report.append("")

        

        # Command performance

        command_stats = self.command_profiler.get_all_stats()

        if command_stats:

            report.append("Command Performance:")

            for cmd_name, stats in command_stats.items():

                report.append(f"  {cmd_name}:")

                report.append(f"    Executions: {stats['execution_count']}")

                report.append(f"    Avg Time: {stats['avg_time']*1000:.2f}ms")

                report.append(f"    Min/Max: {stats['min_time']*1000:.2f}ms / {stats['max_time']*1000:.2f}ms")

            report.append("")

        

        # Recent metrics

        if self.metrics:

            report.append("Recent Metrics:")

            for metric in self.metrics[-10:]:  # Last 10 metrics

                report.append(f"  {metric}")

            report.append("")

        

        # Regression analysis

        if self.baseline_metrics:

            current_metrics = {

                metric.name: metric.value 

                for metric in self.metrics[-len(self.baseline_metrics):]

                if metric.name in self.baseline_metrics

            }

            regressions = self.detect_regressions(current_metrics)

            if regressions:

                report.append("⚠️  Performance Regressions Detected:")

                for regression in regressions:

                    report.append(f"  {regression}")

                report.append("")

        

        return "\n".join(report)

    

    def start_session(self, session_name: str) -> str:

        """Start a monitoring session and return session ID"""

        session_id = f"{session_name}_{int(time.time())}"

        self.record_metric(f"session_start_{session_name}", time.time(), "timestamp", {"session_id": session_id})

        return session_id

    

    def end_session(self, session_id: str) -> Dict[str, Any]:

        """End a monitoring session and return collected metrics"""

        self.record_metric("session_end", time.time(), "timestamp", {"session_id": session_id})

        

        # Collect metrics for this session

        session_metrics = {}

        memory_stats = self.memory_tracker.stop()

        

        if "error" not in memory_stats:

            session_metrics.update({

                "memory_peak_mb": memory_stats.get("peak_mb", 0),

                "memory_avg_mb": memory_stats.get("average_mb", 0),

                "cpu_avg_percent": 0  # Placeholder - could be enhanced with actual CPU monitoring

            })

        

        return session_metrics

    

    def create_dashboard_data(self) -> Dict[str, Any]:

        """Create data for real-time performance dashboard"""

        recent_metrics = self.metrics[-100:] if self.metrics else []

        

        # Group metrics by name

        metric_groups = defaultdict(list)

        for metric in recent_metrics:

            metric_groups[metric.name].append({

                "value": metric.value,

                "timestamp": metric.timestamp,

                "tags": metric.tags

            })

        

        return {

            "startup_time": getattr(self.startup_benchmark, 'phases', {}).get('total', 0),

            "memory_usage": self.memory_tracker.peak_memory / 1024 / 1024,

            "command_stats": self.command_profiler.get_all_stats(),

            "recent_metrics": dict(metric_groups),

            "regression_count": len(self.detect_regressions({

                metric.name: metric.value for metric in recent_metrics

            }))

        }





class PerformanceOptimizer:

    """Automated performance optimization suggestions"""

    

    def __init__(self, monitor: PerformanceMonitor):

        self.monitor = monitor

        

    def analyze_startup_performance(self, metrics: StartupMetrics) -> List[str]:

        """Analyze startup performance and provide optimization suggestions"""

        suggestions = []

        

        if not metrics.is_under_target():

            suggestions.append(f"Startup time ({metrics.total_time*1000:.2f}ms) exceeds 100ms target")

            

            if metrics.import_time > 0.05:  # 50ms

                suggestions.append(f"Import time is high ({metrics.import_time*1000:.2f}ms). "

                                 "Consider lazy imports or reducing import count.")

            

            if metrics.component_load_time > 0.02:  # 20ms

                suggestions.append(f"Component loading is slow ({metrics.component_load_time*1000:.2f}ms). "

                                 "Consider lazy loading components.")

            

            if metrics.template_load_time > 0.02:  # 20ms

                suggestions.append(f"Template loading is slow ({metrics.template_load_time*1000:.2f}ms). "

                                 "Consider template caching or lazy loading.")

        

        if metrics.memory_usage > 50 * 1024 * 1024:  # 50MB

            suggestions.append(f"Memory usage is high ({metrics.memory_usage/1024/1024:.2f}MB). "

                             "Consider memory optimization.")

        

        return suggestions

    

    def analyze_command_performance(self, stats: Dict[str, Dict[str, Any]]) -> List[str]:

        """Analyze command performance and provide suggestions"""

        suggestions = []

        

        for cmd_name, cmd_stats in stats.items():

            if cmd_stats['avg_time'] > 1.0:  # 1 second

                suggestions.append(f"Command '{cmd_name}' is slow (avg: {cmd_stats['avg_time']*1000:.2f}ms). "

                                 "Consider optimization or async execution.")

            

            if cmd_stats['max_time'] > cmd_stats['avg_time'] * 3:

                suggestions.append(f"Command '{cmd_name}' has inconsistent performance. "

                                 f"Max time ({cmd_stats['max_time']*1000:.2f}ms) is much higher than average.")

        

        return suggestions