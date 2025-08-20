"""

Lazy Loading System for CLI Components

Implements deferred loading to optimize startup time

"""



import abc

import asyncio

import functools

import importlib

import sys

import threading

import time

import weakref

from abc import ABC, abstractmethod

from concurrent.futures import ThreadPoolExecutor

from typing import Any, Callable, Dict, List, Optional, Set, TypeVar, Generic, Union

import inspect





T = TypeVar('T')





class LoadingStrategy(ABC):

    """Abstract base class for loading strategies"""

    

    @abstractmethod

    async def load(self, loader_func: Callable[[], T]) -> T:

        """Load a component using this strategy"""

        pass

    

    @abstractmethod

    def should_preload(self, component_name: str, usage_stats: Dict[str, Any]) -> bool:

        """Determine if a component should be preloaded"""

        pass





class EagerLoadingStrategy(LoadingStrategy):

    """Loads components immediately"""

    

    async def load(self, loader_func: Callable[[], T]) -> T:

        if asyncio.iscoroutinefunction(loader_func):

            return await loader_func()

        return loader_func()

    

    def should_preload(self, component_name: str, usage_stats: Dict[str, Any]) -> bool:

        return True





class LazyLoadingStrategy(LoadingStrategy):

    """Loads components only when needed"""

    

    async def load(self, loader_func: Callable[[], T]) -> T:

        if asyncio.iscoroutinefunction(loader_func):

            return await loader_func()

        return loader_func()

    

    def should_preload(self, component_name: str, usage_stats: Dict[str, Any]) -> bool:

        return False





class PredictiveLoadingStrategy(LoadingStrategy):

    """Loads components based on usage patterns"""

    

    def __init__(self, threshold: float = 0.5):

        self.threshold = threshold

    

    async def load(self, loader_func: Callable[[], T]) -> T:

        if asyncio.iscoroutinefunction(loader_func):

            return await loader_func()

        return loader_func()

    

    def should_preload(self, component_name: str, usage_stats: Dict[str, Any]) -> bool:

        usage_frequency = usage_stats.get(component_name, {}).get("frequency", 0)

        return usage_frequency > self.threshold





class PriorityLoadingStrategy(LoadingStrategy):

    """Loads high-priority components first"""

    

    def __init__(self, priority_components: Set[str]):

        self.priority_components = priority_components

    

    async def load(self, loader_func: Callable[[], T]) -> T:

        if asyncio.iscoroutinefunction(loader_func):

            return await loader_func()

        return loader_func()

    

    def should_preload(self, component_name: str, usage_stats: Dict[str, Any]) -> bool:

        return component_name in self.priority_components





class LazyProxy(Generic[T]):

    """Proxy object that loads the target only when accessed"""

    

    def __init__(self, loader_func: Callable[[], T], name: str = ""):

        self._loader_func = loader_func

        self._name = name

        self._target: Optional[T] = None

        self._loading = False

        self._load_lock = threading.Lock()

        self._load_time: Optional[float] = None

    

    def _load_target(self) -> T:

        """Load the target object if not already loaded"""

        if self._target is not None:

            return self._target

        

        with self._load_lock:

            if self._target is not None:

                return self._target

            

            if self._loading:

                # Avoid infinite recursion

                raise RuntimeError(f"Circular loading detected for {self._name}")

            

            self._loading = True

            try:

                start_time = time.perf_counter()

                self._target = self._loader_func()

                self._load_time = time.perf_counter() - start_time

                return self._target

            finally:

                self._loading = False

    

    def __getattr__(self, name: str) -> Any:

        target = self._load_target()

        return getattr(target, name)

    

    def __call__(self, *args: Any, **kwargs: Any) -> Any:

        target = self._load_target()

        return target(*args, **kwargs)

    

    def __repr__(self) -> str:

        if self._target is not None:

            return f"LazyProxy({repr(self._target)})"

        return f"LazyProxy(<unloaded: {self._name}>)"

    

    @property

    def is_loaded(self) -> bool:

        """Check if the target has been loaded"""

        return self._target is not None

    

    @property

    def load_time(self) -> Optional[float]:

        """Get the time it took to load the target"""

        return self._load_time





class AsyncLazyProxy(Generic[T]):

    """Async version of LazyProxy"""

    

    def __init__(self, loader_func: Callable[[], T], name: str = ""):

        self._loader_func = loader_func

        self._name = name

        self._target: Optional[T] = None

        self._loading = False

        self._load_lock = asyncio.Lock()

        self._load_time: Optional[float] = None

    

    async def _load_target(self) -> T:

        """Load the target object if not already loaded"""

        if self._target is not None:

            return self._target

        

        async with self._load_lock:

            if self._target is not None:

                return self._target

            

            if self._loading:

                raise RuntimeError(f"Circular loading detected for {self._name}")

            

            self._loading = True

            try:

                start_time = time.perf_counter()

                if asyncio.iscoroutinefunction(self._loader_func):

                    self._target = await self._loader_func()

                else:

                    self._target = self._loader_func()

                self._load_time = time.perf_counter() - start_time

                return self._target

            finally:

                self._loading = False

    

    async def __call__(self, *args: Any, **kwargs: Any) -> Any:

        target = await self._load_target()

        if asyncio.iscoroutinefunction(target):

            return await target(*args, **kwargs)

        return target(*args, **kwargs)

    

    def __getattr__(self, name: str) -> Any:

        # For sync access, we need to check if we're in an async context

        try:

            loop = asyncio.get_running_loop()

            # We're in async context, but this is sync access

            # Return a sync proxy that will raise an error

            return SyncAsyncProxy(self, name)

        except RuntimeError:

            # We're not in async context, need to create one

            return self._sync_load_and_get_attr(name)

    

    def _sync_load_and_get_attr(self, name: str) -> Any:

        """Synchronously load and get attribute (for sync context)"""

        async def _load_and_get():

            target = await self._load_target()

            return getattr(target, name)

        

        loop = asyncio.new_event_loop()

        try:

            return loop.run_until_complete(_load_and_get())

        finally:

            loop.close()

    

    @property

    def is_loaded(self) -> bool:

        return self._target is not None

    

    @property

    def load_time(self) -> Optional[float]:

        return self._load_time





class SyncAsyncProxy:

    """Proxy for sync access to async lazy proxy attributes"""

    

    def __init__(self, async_proxy: AsyncLazyProxy, attr_name: str):

        self._async_proxy = async_proxy

        self._attr_name = attr_name

    

    def __call__(self, *args: Any, **kwargs: Any) -> Any:

        async def _call():

            target = await self._async_proxy._load_target()

            attr = getattr(target, self._attr_name)

            if asyncio.iscoroutinefunction(attr):

                return await attr(*args, **kwargs)

            return attr(*args, **kwargs)

        

        try:

            loop = asyncio.get_running_loop()

            # We're in async context

            raise RuntimeError(f"Cannot call {self._attr_name} synchronously in async context. "

                             "Use 'await' with the async proxy.")

        except RuntimeError:

            # Create new event loop for sync context

            loop = asyncio.new_event_loop()

            try:

                return loop.run_until_complete(_call())

            finally:

                loop.close()





class LazyLoader:

    """Main lazy loading system for CLI components"""

    

    def __init__(self, strategy: Optional[LoadingStrategy] = None):

        self.strategy = strategy or LazyLoadingStrategy()

        self._components: Dict[str, LazyProxy] = {}

        self._async_components: Dict[str, AsyncLazyProxy] = {}

        self._usage_stats: Dict[str, Dict[str, Any]] = {}

        self._preload_executor = ThreadPoolExecutor(max_workers=2)

        self._component_dependencies: Dict[str, List[str]] = {}

        self._load_times: Dict[str, float] = {}

    

    def register(self, name: str, loader_func: Callable[[], T], 

                dependencies: Optional[List[str]] = None) -> LazyProxy[T]:

        """Register a component for lazy loading"""

        if dependencies:

            self._component_dependencies[name] = dependencies

        

        # Wrap loader to track usage

        def tracked_loader():

            self._track_usage(name)

            start_time = time.perf_counter()

            result = loader_func()

            load_time = time.perf_counter() - start_time

            self._load_times[name] = load_time

            return result

        

        proxy = LazyProxy(tracked_loader, name)

        self._components[name] = proxy

        return proxy

    

    def register_async(self, name: str, loader_func: Callable[[], T],

                      dependencies: Optional[List[str]] = None) -> AsyncLazyProxy[T]:

        """Register an async component for lazy loading"""

        if dependencies:

            self._component_dependencies[name] = dependencies

        

        async def tracked_loader():

            self._track_usage(name)

            start_time = time.perf_counter()

            if asyncio.iscoroutinefunction(loader_func):

                result = await loader_func()

            else:

                result = loader_func()

            load_time = time.perf_counter() - start_time

            self._load_times[name] = load_time

            return result

        

        proxy = AsyncLazyProxy(tracked_loader, name)

        self._async_components[name] = proxy

        return proxy

    

    def register_module(self, name: str, module_name: str,

                       attr_name: Optional[str] = None) -> LazyProxy:

        """Register a module or module attribute for lazy loading"""

        def load_module():

            module = importlib.import_module(module_name)

            if attr_name:

                return getattr(module, attr_name)

            return module

        

        return self.register(name, load_module)

    

    def register_class(self, name: str, class_path: str, 

                      *args, **kwargs) -> LazyProxy:

        """Register a class instance for lazy loading"""

        def load_class():

            module_name, class_name = class_path.rsplit('.', 1)

            module = importlib.import_module(module_name)

            cls = getattr(module, class_name)

            return cls(*args, **kwargs)

        

        return self.register(name, load_class)

    

    def _track_usage(self, name: str):

        """Track component usage for optimization"""

        if name not in self._usage_stats:

            self._usage_stats[name] = {

                "count": 0,

                "frequency": 0.0,

                "last_used": time.time()

            }

        

        stats = self._usage_stats[name]

        stats["count"] += 1

        stats["last_used"] = time.time()

        

        # Update frequency (simple moving average)

        total_components = len(self._components) + len(self._async_components)

        if total_components > 0:

            stats["frequency"] = stats["count"] / total_components

    

    def preload_components(self, component_names: Optional[List[str]] = None):

        """Preload components based on strategy"""

        if component_names is None:

            component_names = list(self._components.keys())

        

        for name in component_names:

            if (name in self._components and 

                self.strategy.should_preload(name, self._usage_stats)):

                

                # Preload in background

                def preload(component_name=name):

                    try:

                        self._components[component_name]._load_target()

                    except Exception as e:

                        print(f"Failed to preload {component_name}: {e}")

                

                self._preload_executor.submit(preload)

    

    async def preload_async_components(self, component_names: Optional[List[str]] = None):

        """Preload async components based on strategy"""

        if component_names is None:

            component_names = list(self._async_components.keys())

        

        tasks = []

        for name in component_names:

            if (name in self._async_components and 

                self.strategy.should_preload(name, self._usage_stats)):

                

                async def preload(component_name=name):

                    try:

                        await self._async_components[component_name]._load_target()

                    except Exception as e:

                        print(f"Failed to preload {component_name}: {e}")

                

                tasks.append(preload())

        

        if tasks:

            await asyncio.gather(*tasks, return_exceptions=True)

    

    def get_component(self, name: str) -> Optional[LazyProxy]:

        """Get a registered component"""

        return self._components.get(name)

    

    def get_async_component(self, name: str) -> Optional[AsyncLazyProxy]:

        """Get a registered async component"""

        return self._async_components.get(name)

    

    def is_loaded(self, name: str) -> bool:

        """Check if a component is loaded"""

        if name in self._components:

            return self._components[name].is_loaded

        elif name in self._async_components:

            return self._async_components[name].is_loaded

        return False

    

    def get_load_stats(self) -> Dict[str, Any]:

        """Get loading statistics"""

        return {

            "total_components": len(self._components) + len(self._async_components),

            "loaded_components": sum(1 for c in self._components.values() if c.is_loaded) +

                               sum(1 for c in self._async_components.values() if c.is_loaded),

            "usage_stats": self._usage_stats.copy(),

            "load_times": self._load_times.copy(),

            "average_load_time": sum(self._load_times.values()) / len(self._load_times) 

                               if self._load_times else 0

        }

    

    def unload_component(self, name: str):

        """Unload a component to free memory"""

        if name in self._components:

            # Create a new proxy with the same loader

            old_proxy = self._components[name]

            if hasattr(old_proxy, '_loader_func'):

                self._components[name] = LazyProxy(old_proxy._loader_func, name)

        elif name in self._async_components:

            old_proxy = self._async_components[name]

            if hasattr(old_proxy, '_loader_func'):

                self._async_components[name] = AsyncLazyProxy(old_proxy._loader_func, name)

    

    def clear_all(self):

        """Clear all registered components"""

        self._components.clear()

        self._async_components.clear()

        self._usage_stats.clear()

        self._component_dependencies.clear()

        self._load_times.clear()

    

    def shutdown(self):

        """Shutdown the loader and cleanup resources"""

        self._preload_executor.shutdown(wait=True)

        self.clear_all()





def lazy_property(func: Callable[[Any], T]) -> property:

    """Decorator to create a lazy property"""

    attr_name = f"_lazy_{func.__name__}"

    

    def getter(self):

        if not hasattr(self, attr_name):

            setattr(self, attr_name, func(self))

        return getattr(self, attr_name)

    

    def deleter(self):

        if hasattr(self, attr_name):

            delattr(self, attr_name)

    

    return property(getter, None, deleter)





def lazy_import(module_name: str, attr_name: Optional[str] = None):

    """Decorator for lazy imports"""

    def decorator(func):

        @functools.wraps(func)

        def wrapper(*args, **kwargs):

            module = importlib.import_module(module_name)

            if attr_name:

                imported_obj = getattr(module, attr_name)

            else:

                imported_obj = module

            return func(imported_obj, *args, **kwargs)

        return wrapper

    return decorator