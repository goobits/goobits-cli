"""

Performance Optimization System for Goobits CLI Framework

Provides lazy loading, caching, and performance monitoring

"""

from .lazy_loader import LazyLoader, LoadingStrategy

from .monitor import PerformanceMonitor, StartupBenchmark, MemoryTracker

from .cache import TemplateCache, ComponentCache

from .optimizer import CLIOptimizer


__all__ = [
    "LazyLoader",
    "LoadingStrategy",
    "PerformanceMonitor",
    "StartupBenchmark",
    "MemoryTracker",
    "TemplateCache",
    "ComponentCache",
    "CLIOptimizer",
]
