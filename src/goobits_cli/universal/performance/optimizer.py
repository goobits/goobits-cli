"""

CLI Performance Optimizer

Orchestrates all performance optimization components

"""



import asyncio

import os

import threading

import time

from pathlib import Path

from typing import Dict, List, Optional, Any, Callable

from contextlib import asynccontextmanager



from .lazy_loader import LazyLoader, LazyLoadingStrategy, PredictiveLoadingStrategy

from .monitor import PerformanceMonitor, StartupBenchmark, MemoryTracker

from .cache import CacheManager, TemplateCache, ComponentCache





class CLIOptimizer:

    """Main performance optimizer for CLI applications"""

    

    def __init__(self, 

                 cache_dir: Optional[Path] = None,

                 enable_monitoring: bool = True,

                 startup_target_ms: int = 100,

                 memory_target_mb: int = 50):

        

        self.cache_dir = cache_dir or Path.home() / ".goobits" / "cache"

        self.startup_target_ms = startup_target_ms

        self.memory_target_mb = memory_target_mb

        

        # Initialize components

        self.lazy_loader = LazyLoader(PredictiveLoadingStrategy())

        self.cache_manager = CacheManager(self.cache_dir)

        

        if enable_monitoring:

            self.monitor = PerformanceMonitor()

        else:

            self.monitor = None

        

        # Optimization settings

        self.optimization_enabled = True

        self.auto_preload = True

        self.aggressive_caching = False

        

        # Performance tracking

        self.startup_times: List[float] = []

        self.optimization_history: List[Dict[str, Any]] = []

    

    def start_optimization(self):

        """Start performance optimization"""

        if self.monitor:

            self.monitor.start_monitoring()

        

        # Register core components for lazy loading

        self._register_core_components()

        

        # Start background optimization tasks

        self._start_background_tasks()

    

    def _register_core_components(self):

        """Register core CLI components for lazy loading"""

        # Template engine

        self.lazy_loader.register(

            "template_engine",

            lambda: self._create_template_engine(),

            dependencies=[]

        )

        

        # Configuration manager

        self.lazy_loader.register(

            "config_manager",

            lambda: self._create_config_manager(),

            dependencies=[]

        )

        

        # Command parser

        self.lazy_loader.register(

            "command_parser",

            lambda: self._create_command_parser(),

            dependencies=["config_manager"]

        )

        

        # Plugin manager

        self.lazy_loader.register(

            "plugin_manager",

            lambda: self._create_plugin_manager(),

            dependencies=["config_manager"]

        )

    

    def _create_template_engine(self):

        """Create optimized template engine"""

        from ..template_engine import UniversalTemplateEngine

        

        engine = UniversalTemplateEngine(

            template_cache=self.cache_manager.template_cache

        )

        return engine

    

    def _create_config_manager(self):

        """Create configuration manager"""

        # This would be implemented based on actual config manager

        class ConfigManager:

            def __init__(self):

                self.config = {}

            

            def load_config(self, path: Path):

                pass

        

        return ConfigManager()

    

    def _create_command_parser(self):

        """Create command parser"""

        # This would be implemented based on actual parser

        class CommandParser:

            def __init__(self):

                pass

        

        return CommandParser()

    

    def _create_plugin_manager(self):

        """Create plugin manager"""

        # This would be implemented based on actual plugin manager

        class PluginManager:

            def __init__(self):

                pass

        

        return PluginManager()

    

    def _start_background_tasks(self):

        """Start background optimization tasks"""

        if self.auto_preload:

            # Start preloading thread

            preload_thread = threading.Thread(

                target=self._background_preload,

                daemon=True

            )

            preload_thread.start()

        

        # Start cache optimization thread

        cache_thread = threading.Thread(

            target=self._background_cache_optimization,

            daemon=True

        )

        cache_thread.start()

    

    def _background_preload(self):

        """Background preloading of components"""

        time.sleep(0.1)  # Let startup complete first

        

        try:

            # Preload components based on usage patterns

            self.lazy_loader.preload_components()

        except Exception as e:

            print(f"Background preload failed: {e}")

    

    def _background_cache_optimization(self):

        """Background cache optimization"""

        while self.optimization_enabled:

            try:

                time.sleep(300)  # Every 5 minutes

                self.cache_manager.optimize_caches()

            except Exception as e:

                import logging

                logging.debug(f"Cache optimization error (non-critical): {e}")

    

    @asynccontextmanager

    async def startup_optimization(self):

        """Context manager for optimizing startup"""

        if self.monitor:

            self.monitor.startup_benchmark.start()

        

        startup_start = time.perf_counter()

        

        try:

            yield self

        finally:

            startup_time = time.perf_counter() - startup_start

            self.startup_times.append(startup_time)

            

            if self.monitor:

                metrics = self.monitor.startup_benchmark.finish()

                

                # Record optimization results

                self.optimization_history.append({

                    "timestamp": time.time(),

                    "startup_time_ms": startup_time * 1000,

                    "target_met": startup_time * 1000 < self.startup_target_ms,

                    "memory_mb": metrics.memory_usage / 1024 / 1024,

                    "import_count": metrics.import_count,

                    "component_count": metrics.component_count

                })

                

                # Auto-adjust optimization strategies

                self._adjust_optimization_strategy(metrics)

    

    def _adjust_optimization_strategy(self, metrics):

        """Automatically adjust optimization strategy based on performance"""

        startup_ms = metrics.total_time * 1000

        

        if startup_ms > self.startup_target_ms * 1.5:

            # Performance is poor, enable aggressive optimization

            print(f"🚀 Enabling aggressive optimization (startup: {startup_ms:.2f}ms)")

            self.aggressive_caching = True

            

            # Switch to more aggressive lazy loading

            self.lazy_loader.strategy = LazyLoadingStrategy()

            

        elif startup_ms < self.startup_target_ms * 0.7:

            # Performance is good, can afford some preloading

            print(f"✨ Performance good, enabling predictive loading (startup: {startup_ms:.2f}ms)")

            self.lazy_loader.strategy = PredictiveLoadingStrategy(threshold=0.3)

        

        # Memory optimization

        memory_mb = metrics.memory_usage / 1024 / 1024

        if memory_mb > self.memory_target_mb * 1.2:

            print(f"💾 High memory usage ({memory_mb:.2f}MB), optimizing caches")

            self._optimize_memory_usage()

    

    def _optimize_memory_usage(self):

        """Optimize memory usage"""

        # Reduce cache sizes

        if hasattr(self.cache_manager.template_cache._cache, 'max_size'):

            current_size = self.cache_manager.template_cache._cache.max_size

            new_size = max(100, int(current_size * 0.8))

            self.cache_manager.template_cache._cache.max_size = new_size

        

        # Force garbage collection

        import gc

        collected = gc.collect()

        print(f"Collected {collected} objects through garbage collection")

    

    def optimize_command_execution(self, command_name: str):

        """Optimize a specific command execution"""

        def decorator(func: Callable):

            def wrapper(*args, **kwargs):

                if self.monitor:

                    with self.monitor.command_profiler.profile_command(command_name):

                        return func(*args, **kwargs)

                else:

                    return func(*args, **kwargs)

            return wrapper

        

        return decorator

    

    def get_optimization_report(self) -> Dict[str, Any]:

        """Generate comprehensive optimization report"""

        report = {

            "startup_performance": self._analyze_startup_performance(),

            "memory_usage": self._analyze_memory_usage(),

            "cache_performance": self.cache_manager.get_global_stats(),

            "component_loading": self.lazy_loader.get_load_stats(),

            "optimization_recommendations": self._generate_recommendations()

        }

        

        if self.monitor:

            report.update({

                "monitoring_data": self.monitor.create_dashboard_data(),

                "performance_history": self.optimization_history[-10:]  # Last 10 entries

            })

        

        return report

    

    def _analyze_startup_performance(self) -> Dict[str, Any]:

        """Analyze startup performance trends"""

        if not self.startup_times:

            return {"status": "No startup data available"}

        

        recent_times = self.startup_times[-10:]  # Last 10 startups

        avg_time = sum(recent_times) / len(recent_times)

        

        return {

            "average_startup_ms": avg_time * 1000,

            "target_ms": self.startup_target_ms,

            "target_met": avg_time * 1000 < self.startup_target_ms,

            "trend": "improving" if len(self.startup_times) > 1 and 

                    recent_times[-1] < recent_times[0] else "stable",

            "total_measurements": len(self.startup_times),

            "best_time_ms": min(self.startup_times) * 1000,

            "worst_time_ms": max(self.startup_times) * 1000

        }

    

    def _analyze_memory_usage(self) -> Dict[str, Any]:

        """Analyze memory usage patterns"""

        if not self.monitor:

            return {"status": "Monitoring disabled"}

        

        memory_stats = self.monitor.memory_tracker.stop()

        

        return {

            "current_mb": memory_stats.get("current_mb", 0),

            "peak_mb": memory_stats.get("peak_mb", 0),

            "target_mb": self.memory_target_mb,

            "target_met": memory_stats.get("peak_mb", 0) < self.memory_target_mb,

            "cache_memory_mb": self._estimate_cache_memory(),

            "optimization_active": self.aggressive_caching

        }

    

    def _estimate_cache_memory(self) -> float:

        """Estimate memory used by caches"""

        # This is a rough estimate

        stats = self.cache_manager.get_global_stats()

        

        template_size = stats.get("templates", {}).get("template_cache", {}).get("total_size", 0)

        component_size = stats.get("components", {}).get("component_cache", {}).get("total_size", 0)

        

        return (template_size + component_size) / 1024 / 1024  # Convert to MB

    

    def _generate_recommendations(self) -> List[str]:

        """Generate optimization recommendations"""

        recommendations = []

        

        # Startup performance recommendations

        if self.startup_times:

            avg_startup = sum(self.startup_times[-5:]) / min(5, len(self.startup_times))

            if avg_startup * 1000 > self.startup_target_ms:

                recommendations.append(

                    f"Startup time ({avg_startup*1000:.2f}ms) exceeds target. "

                    "Consider more aggressive lazy loading."

                )

        

        # Cache recommendations

        cache_stats = self.cache_manager.get_global_stats()

        template_hit_rate = cache_stats.get("templates", {}).get("template_cache", {}).get("hit_rate", 0)

        

        if template_hit_rate < 0.7:

            recommendations.append(

                f"Template cache hit rate is low ({template_hit_rate:.1%}). "

                "Consider increasing cache size or preloading templates."

            )

        

        # Component loading recommendations

        load_stats = self.lazy_loader.get_load_stats()

        if load_stats.get("average_load_time", 0) > 0.01:  # 10ms

            recommendations.append(

                "Component loading is slow. Consider component preloading or optimization."

            )

        

        # Memory recommendations

        if self.monitor:

            memory_stats = self.monitor.memory_tracker.stop()

            peak_mb = memory_stats.get("peak_mb", 0)

            if peak_mb > self.memory_target_mb:

                recommendations.append(

                    f"Memory usage ({peak_mb:.2f}MB) exceeds target ({self.memory_target_mb}MB). "

                    "Consider reducing cache sizes or enabling memory optimization."

                )

        

        return recommendations

    

    def enable_development_mode(self):

        """Enable development-friendly optimizations"""

        # Disable aggressive caching for development

        self.aggressive_caching = False

        

        # Enable auto-reloading for templates

        if hasattr(self.cache_manager.template_cache, '_env_cache'):

            for env in self.cache_manager.template_cache._env_cache.values():

                env.auto_reload = True

        

        print("🔧 Development mode enabled - optimizations adjusted for development")

    

    def enable_production_mode(self):

        """Enable production optimizations"""

        # Enable aggressive caching

        self.aggressive_caching = True

        

        # Disable auto-reloading

        if hasattr(self.cache_manager.template_cache, '_env_cache'):

            for env in self.cache_manager.template_cache._env_cache.values():

                env.auto_reload = False

        

        # Preload all critical components

        self.lazy_loader.preload_components()

        

        print("🚀 Production mode enabled - all optimizations active")

    

    def benchmark_performance(self, iterations: int = 5) -> Dict[str, Any]:

        """Run performance benchmark"""

        print(f"🔄 Running performance benchmark ({iterations} iterations)...")

        

        startup_times = []

        memory_usage = []

        

        for i in range(iterations):

            # Simulate startup

            start_time = time.perf_counter()

            

            # Clear caches to simulate clean startup

            self.cache_manager.clear_all_caches()

            self.lazy_loader.clear_all()

            

            # Re-register components

            self._register_core_components()

            

            # Measure startup time

            end_time = time.perf_counter()

            startup_time = end_time - start_time

            startup_times.append(startup_time)

            

            # Measure memory (rough estimate)

            import psutil

            memory_mb = psutil.Process().memory_info().rss / 1024 / 1024

            memory_usage.append(memory_mb)

            

            print(f"  Iteration {i+1}: {startup_time*1000:.2f}ms, {memory_mb:.2f}MB")

        

        # Calculate statistics

        avg_startup = sum(startup_times) / len(startup_times)

        avg_memory = sum(memory_usage) / len(memory_usage)

        

        benchmark_results = {

            "iterations": iterations,

            "startup_performance": {

                "average_ms": avg_startup * 1000,

                "min_ms": min(startup_times) * 1000,

                "max_ms": max(startup_times) * 1000,

                "target_met": avg_startup * 1000 < self.startup_target_ms

            },

            "memory_performance": {

                "average_mb": avg_memory,

                "min_mb": min(memory_usage),

                "max_mb": max(memory_usage),

                "target_met": avg_memory < self.memory_target_mb

            },

            "overall_grade": self._calculate_performance_grade(avg_startup, avg_memory)

        }

        

        print(f"\n📊 Benchmark Results:")

        print(f"  Startup: {avg_startup*1000:.2f}ms (target: {self.startup_target_ms}ms)")

        print(f"  Memory: {avg_memory:.2f}MB (target: {self.memory_target_mb}MB)")

        print(f"  Grade: {benchmark_results['overall_grade']}")

        

        return benchmark_results

    

    def _calculate_performance_grade(self, startup_time: float, memory_mb: float) -> str:

        """Calculate overall performance grade"""

        startup_score = 100 if startup_time * 1000 < self.startup_target_ms else 0

        memory_score = 100 if memory_mb < self.memory_target_mb else 0

        

        # Weight startup more heavily

        overall_score = (startup_score * 0.7) + (memory_score * 0.3)

        

        if overall_score >= 90:

            return "A+ (Excellent)"

        elif overall_score >= 80:

            return "A (Very Good)"

        elif overall_score >= 70:

            return "B (Good)"

        elif overall_score >= 60:

            return "C (Fair)"

        else:

            return "D (Needs Improvement)"

    

    def shutdown(self):

        """Shutdown optimizer and cleanup resources"""

        self.optimization_enabled = False

        

        if self.lazy_loader:

            self.lazy_loader.shutdown()

        

        if self.monitor:

            # Final report

            final_report = self.get_optimization_report()

            print("\n📈 Final Performance Report:")

            print(f"  Average Startup: {final_report['startup_performance'].get('average_startup_ms', 0):.2f}ms")

            

            cache_stats = final_report.get('cache_performance', {})

            if cache_stats:

                print(f"  Cache Hit Rate: {cache_stats.get('templates', {}).get('template_cache', {}).get('hit_rate', 0):.1%}")

        

        print("🏁 Performance optimizer shutdown complete")