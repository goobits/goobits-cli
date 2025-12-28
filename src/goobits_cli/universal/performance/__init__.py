"""

Performance Optimization System for Goobits CLI Framework

Provides lazy loading, caching, and performance monitoring

"""

from .cache import ComponentCache, TemplateCache
from .lazy_loader import LazyLoader, LoadingStrategy
from .monitor import MemoryTracker, PerformanceMonitor, StartupBenchmark
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
