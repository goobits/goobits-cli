"""

High-Performance Caching System for CLI Framework

Provides template compilation caching and component caching

"""



import hashlib

import json

import pickle

import threading

import time

import weakref

from abc import ABC, abstractmethod

from collections import OrderedDict

from pathlib import Path

from typing import Any, Dict, Optional, TypeVar, Generic, Callable

import jinja2






T = TypeVar('T')





class CacheEntry(Generic[T]):

    """Individual cache entry with metadata"""

    

    def __init__(self, value: T, created_at: float, expires_at: Optional[float] = None,

                 access_count: int = 0, size: int = 0):

        self.value = value

        self.created_at = created_at

        self.expires_at = expires_at

        self.access_count = access_count

        self.last_accessed = created_at

        self.size = size

    

    def is_expired(self, current_time: Optional[float] = None) -> bool:

        """Check if the entry is expired"""

        if self.expires_at is None:

            return False

        

        if current_time is None:

            current_time = time.time()

        

        return current_time >= self.expires_at

    

    def access(self):

        """Record an access to this entry"""

        self.access_count += 1

        self.last_accessed = time.time()





class CacheStats:

    """Cache statistics tracking"""

    

    def __init__(self):

        self.hits = 0

        self.misses = 0

        self.evictions = 0

        self.total_size = 0

        self.max_size = 0

    

    @property

    def hit_rate(self) -> float:

        total = self.hits + self.misses

        return self.hits / total if total > 0 else 0.0

    

    def record_hit(self):

        self.hits += 1

    

    def record_miss(self):

        self.misses += 1

    

    def record_eviction(self):

        self.evictions += 1

    

    def update_size(self, size: int):

        self.total_size = size

        self.max_size = max(self.max_size, size)





class BaseCache(ABC, Generic[T]):

    """Abstract base class for caches"""

    

    def __init__(self, max_size: int = 1000, default_ttl: Optional[float] = None):

        self.max_size = max_size

        self.default_ttl = default_ttl

        self.stats = CacheStats()

        self._lock = threading.RLock()

    

    @abstractmethod

    def get(self, key: str) -> Optional[T]:

        """Get a value from cache"""

        pass

    

    @abstractmethod

    def put(self, key: str, value: T, ttl: Optional[float] = None) -> None:

        """Put a value in cache"""

        pass

    

    @abstractmethod

    def delete(self, key: str) -> bool:

        """Delete a value from cache"""

        pass

    

    @abstractmethod

    def clear(self) -> None:

        """Clear all cache entries"""

        pass

    

    @abstractmethod

    def size(self) -> int:

        """Get cache size"""

        pass

    

    def get_stats(self) -> Dict[str, Any]:

        """Get cache statistics"""

        with self._lock:

            return {

                "hits": self.stats.hits,

                "misses": self.stats.misses,

                "evictions": self.stats.evictions,

                "hit_rate": self.stats.hit_rate,

                "size": self.size(),

                "max_size": self.max_size,

                "total_size": self.stats.total_size,

                "peak_size": self.stats.max_size

            }





class MemoryCache(BaseCache[T]):

    """In-memory LRU cache with TTL support"""

    

    def __init__(self, max_size: int = 1000, default_ttl: Optional[float] = None):

        super().__init__(max_size, default_ttl)

        self._cache: OrderedDict[str, CacheEntry[T]] = OrderedDict()

    

    def get(self, key: str) -> Optional[T]:

        with self._lock:

            if key not in self._cache:

                self.stats.record_miss()

                return None

            

            entry = self._cache[key]

            

            # Check expiration

            if entry.is_expired():

                del self._cache[key]

                self.stats.record_miss()

                return None

            

            # Move to end (LRU)

            entry.access()

            self._cache.move_to_end(key)

            self.stats.record_hit()

            

            return entry.value

    

    def put(self, key: str, value: T, ttl: Optional[float] = None) -> None:

        with self._lock:

            current_time = time.time()

            

            # Calculate expiration

            if ttl is not None:

                expires_at = current_time + ttl

            elif self.default_ttl is not None:

                expires_at = current_time + self.default_ttl

            else:

                expires_at = None

            

            # Create entry

            entry = CacheEntry(

                value=value,

                created_at=current_time,

                expires_at=expires_at,

                size=self._estimate_size(value)

            )

            

            # Remove if already exists

            if key in self._cache:

                del self._cache[key]

            

            # Add new entry

            self._cache[key] = entry

            

            # Evict if necessary

            while len(self._cache) > self.max_size:

                oldest_key = next(iter(self._cache))

                del self._cache[oldest_key]

                self.stats.record_eviction()

            

            self.stats.update_size(len(self._cache))

    

    def delete(self, key: str) -> bool:

        with self._lock:

            if key in self._cache:

                del self._cache[key]

                self.stats.update_size(len(self._cache))

                return True

            return False

    

    def clear(self) -> None:

        with self._lock:

            self._cache.clear()

            self.stats.update_size(0)

    

    def size(self) -> int:

        with self._lock:

            return len(self._cache)

    

    def _estimate_size(self, value: Any) -> int:

        """Estimate the size of a cached value"""

        try:

            if isinstance(value, (str, bytes)):

                return len(value)

            elif isinstance(value, (list, tuple)):

                return sum(self._estimate_size(item) for item in value)

            elif isinstance(value, dict):

                return sum(self._estimate_size(k) + self._estimate_size(v) 

                          for k, v in value.items())

            else:

                return len(str(value))

        except Exception:

            return 100  # Default estimate

    

    def cleanup_expired(self) -> int:

        """Remove expired entries and return count removed"""

        with self._lock:

            current_time = time.time()

            expired_keys = [

                key for key, entry in self._cache.items()

                if entry.is_expired(current_time)

            ]

            

            for key in expired_keys:

                del self._cache[key]

            

            self.stats.update_size(len(self._cache))

            return len(expired_keys)





class PersistentCache(BaseCache[T]):

    """Persistent cache using disk storage"""

    

    def __init__(self, cache_dir: Path, max_size: int = 1000, 

                 default_ttl: Optional[float] = None):

        super().__init__(max_size, default_ttl)

        self.cache_dir = cache_dir

        self.cache_dir.mkdir(parents=True, exist_ok=True)

        self._memory_cache = MemoryCache(max_size // 4)  # Small memory cache

        self._index_file = self.cache_dir / "index.json"

        self._index = self._load_index()

    def _get_last_accessed_time(self, key: str) -> float:
        """Get last accessed time for cache key."""
        return self._index[key]["last_accessed"]

    def _load_index(self) -> Dict[str, Dict[str, Any]]:

        """Load cache index from disk"""

        if self._index_file.exists():

            try:

                with open(self._index_file) as f:

                    return json.load(f)

            except Exception:

                pass

        return {}

    

    def _save_index(self):

        """Save cache index to disk"""

        try:

            with open(self._index_file, 'w') as f:

                json.dump(self._index, f)

        except Exception:

            pass

    

    def _get_cache_file(self, key: str) -> Path:

        """Get cache file path for key"""

        key_hash = hashlib.md5(key.encode()).hexdigest()

        return self.cache_dir / f"{key_hash}.cache"

    

    def get(self, key: str) -> Optional[T]:

        # Try memory cache first

        value = self._memory_cache.get(key)

        if value is not None:

            self.stats.record_hit()

            return value

        

        with self._lock:

            if key not in self._index:

                self.stats.record_miss()

                return None

            

            entry_info = self._index[key]

            

            # Check expiration

            if entry_info.get("expires_at") and time.time() >= entry_info["expires_at"]:

                self.delete(key)

                self.stats.record_miss()

                return None

            

            # Load from disk

            cache_file = self._get_cache_file(key)

            if not cache_file.exists():

                del self._index[key]

                self._save_index()

                self.stats.record_miss()

                return None

            

            try:

                with open(cache_file, 'rb') as f:

                    value = pickle.load(f)

                

                # Update access info

                entry_info["access_count"] += 1

                entry_info["last_accessed"] = time.time()

                self._save_index()

                

                # Add to memory cache

                self._memory_cache.put(key, value)

                

                self.stats.record_hit()

                return value

                

            except Exception:

                self.delete(key)

                self.stats.record_miss()

                return None

    

    def put(self, key: str, value: T, ttl: Optional[float] = None) -> None:

        with self._lock:

            current_time = time.time()

            

            # Calculate expiration

            if ttl is not None:

                expires_at = current_time + ttl

            elif self.default_ttl is not None:

                expires_at = current_time + self.default_ttl

            else:

                expires_at = None

            

            # Save to disk

            cache_file = self._get_cache_file(key)

            try:

                with open(cache_file, 'wb') as f:

                    pickle.dump(value, f)

                

                # Update index

                self._index[key] = {

                    "created_at": current_time,

                    "expires_at": expires_at,

                    "access_count": 0,

                    "last_accessed": current_time,

                    "size": cache_file.stat().st_size

                }

                

                # Add to memory cache

                self._memory_cache.put(key, value, ttl)

                

                # Evict if necessary

                if len(self._index) > self.max_size:

                    self._evict_oldest()

                

                self._save_index()

                self.stats.update_size(len(self._index))

                

            except Exception:

                # Cleanup on error

                if cache_file.exists():

                    cache_file.unlink()

                if key in self._index:

                    del self._index[key]

    

    def delete(self, key: str) -> bool:

        with self._lock:

            if key not in self._index:

                return False

            

            # Remove from disk

            cache_file = self._get_cache_file(key)

            if cache_file.exists():

                cache_file.unlink()

            

            # Remove from index

            del self._index[key]

            self._save_index()

            

            # Remove from memory cache

            self._memory_cache.delete(key)

            

            self.stats.update_size(len(self._index))

            return True

    

    def clear(self) -> None:

        with self._lock:

            # Clear disk cache

            for cache_file in self.cache_dir.glob("*.cache"):

                cache_file.unlink()

            

            # Clear index

            self._index.clear()

            self._save_index()

            

            # Clear memory cache

            self._memory_cache.clear()

            

            self.stats.update_size(0)

    

    def size(self) -> int:

        with self._lock:

            return len(self._index)

    

    def _evict_oldest(self):

        """Evict the oldest entry"""

        if not self._index:

            return

        

        oldest_key = min(self._index.keys(), 

                        key=self._get_last_accessed_time)

        self.delete(oldest_key)

        self.stats.record_eviction()





class TemplateCache:

    """High-performance template compilation cache"""

    

    def __init__(self, cache_dir: Optional[Path] = None, max_templates: int = 500):

        if cache_dir:

            self._cache = PersistentCache(cache_dir / "templates", max_templates, 3600)  # 1 hour TTL

        else:

            self._cache = MemoryCache(max_templates, 3600)

        

        self._env_cache: Dict[str, jinja2.Environment] = {}

        self._template_mtimes: Dict[str, float] = {}

        

    def get_environment(self, template_dir: Path, **env_options) -> jinja2.Environment:

        """Get or create a Jinja2 environment with caching"""

        env_key = f"{template_dir}:{hash(frozenset(env_options.items()))}"

        

        if env_key not in self._env_cache:

            loader = jinja2.FileSystemLoader(str(template_dir))

            # Set default options for better template rendering
            default_options = {
                'trim_blocks': True,
                'lstrip_blocks': True
            }
            default_options.update(env_options)
            env = jinja2.Environment(loader=loader, **default_options)

            

            # Enable auto-reloading in development

            if env_options.get('auto_reload', False):

                env.auto_reload = True

            

            self._env_cache[env_key] = env

        

        return self._env_cache[env_key]

    

    def get_template(self, template_path: Path, **env_options) -> Optional[jinja2.Template]:

        """Get compiled template with caching"""

        # Generate cache key

        template_str = str(template_path.resolve())

        env_key = hash(frozenset(env_options.items()))

        cache_key = f"{template_str}:{env_key}"

        

        # Check if template file exists

        if not template_path.exists():

            return None

        

        # Check modification time

        current_mtime = template_path.stat().st_mtime

        cached_mtime = self._template_mtimes.get(cache_key)

        

        # Try to get from cache

        if cached_mtime == current_mtime:

            template = self._cache.get(cache_key)

            if template is not None:

                return template

        

        # Compile template

        try:

            template_dir = template_path.parent

            env = self.get_environment(template_dir, **env_options)

            template = env.get_template(template_path.name)

            

            # Cache compiled template

            self._cache.put(cache_key, template)

            self._template_mtimes[cache_key] = current_mtime

            

            return template

            

        except Exception as e:

            print(f"Failed to compile template {template_path}: {e}")

            return None

    

    def render_template(self, template_path: Path, context: Dict[str, Any],

                       **env_options) -> Optional[str]:

        """Render template with caching"""

        template = self.get_template(template_path, **env_options)

        if template is None:

            return None

        

        try:

            return template.render(context)

        except Exception as e:

            print(f"Failed to render template {template_path}: {e}")

            return None

    

    def invalidate_template(self, template_path: Path):

        """Invalidate cached template"""

        template_str = str(template_path.resolve())

        

        # Remove all cache entries for this template

        keys_to_remove = []

        for key in self._template_mtimes.keys():

            if key.startswith(template_str + ":"):

                keys_to_remove.append(key)

        

        for key in keys_to_remove:

            self._cache.delete(key)

            del self._template_mtimes[key]

    

    def clear_cache(self):

        """Clear all cached templates"""

        self._cache.clear()

        self._template_mtimes.clear()

        self._env_cache.clear()

    

    def get_stats(self) -> Dict[str, Any]:

        """Get cache statistics"""

        return {

            "template_cache": self._cache.get_stats(),

            "cached_templates": len(self._template_mtimes),

            "cached_environments": len(self._env_cache)

        }





class ComponentCache:

    """Cache for CLI components and their configurations"""

    

    def __init__(self, cache_dir: Optional[Path] = None, max_components: int = 200):

        if cache_dir:

            self._cache = PersistentCache(cache_dir / "components", max_components, 1800)  # 30 min TTL

        else:

            self._cache = MemoryCache(max_components, 1800)

        

        self._weak_refs: weakref.WeakValueDictionary = weakref.WeakValueDictionary()

    

    def get_component(self, component_id: str, loader: Callable[[], T]) -> T:

        """Get component with lazy loading and caching"""

        # Check weak references first (in-memory instances)

        if component_id in self._weak_refs:

            return self._weak_refs[component_id]

        

        # Check cache

        cached_component = self._cache.get(component_id)

        if cached_component is not None:

            self._weak_refs[component_id] = cached_component

            return cached_component

        

        # Load component

        component = loader()

        

        # Cache component

        self._cache.put(component_id, component)

        self._weak_refs[component_id] = component

        

        return component

    

    def invalidate_component(self, component_id: str):

        """Invalidate a cached component"""

        self._cache.delete(component_id)

        if component_id in self._weak_refs:

            del self._weak_refs[component_id]

    

    def preload_components(self, component_loaders: Dict[str, Callable[[], Any]]):

        """Preload components in background"""

        import concurrent.futures

        

        def load_component(item):

            component_id, loader = item

            try:

                return component_id, loader()

            except Exception as e:

                print(f"Failed to preload component {component_id}: {e}")

                return component_id, None

        

        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:

            futures = {

                executor.submit(load_component, item): item[0]

                for item in component_loaders.items()

            }

            

            for future in concurrent.futures.as_completed(futures):

                component_id, component = future.result()

                if component is not None:

                    self._cache.put(component_id, component)

                    self._weak_refs[component_id] = component

    

    def get_stats(self) -> Dict[str, Any]:

        """Get cache statistics"""

        return {

            "component_cache": self._cache.get_stats(),

            "weak_references": len(self._weak_refs)

        }





class CacheManager:

    """Manages all caches in the system"""

    

    def __init__(self, cache_dir: Optional[Path] = None):

        self.cache_dir = cache_dir

        if cache_dir:

            cache_dir.mkdir(parents=True, exist_ok=True)

        

        self.template_cache = TemplateCache(cache_dir)

        self.component_cache = ComponentCache(cache_dir)

        

        # Cleanup thread

        self._cleanup_thread = threading.Thread(target=self._periodic_cleanup, daemon=True)

        self._cleanup_thread.start()

    

    def _periodic_cleanup(self):

        """Periodically clean up expired cache entries"""

        while True:

            try:

                time.sleep(300)  # 5 minutes

                

                # Cleanup expired entries in persistent caches

                if hasattr(self.template_cache._cache, 'cleanup_expired'):

                    self.template_cache._cache.cleanup_expired()

                

                if hasattr(self.component_cache._cache, 'cleanup_expired'):

                    self.component_cache._cache.cleanup_expired()

                    

            except Exception:

                pass

    

    def get_global_stats(self) -> Dict[str, Any]:

        """Get statistics for all caches"""

        return {

            "templates": self.template_cache.get_stats(),

            "components": self.component_cache.get_stats()

        }

    

    def clear_all_caches(self):

        """Clear all caches"""

        self.template_cache.clear_cache()

        self.component_cache._cache.clear()

    

    def optimize_caches(self):

        """Run cache optimization"""

        # Force cleanup of expired entries

        if hasattr(self.template_cache._cache, 'cleanup_expired'):

            expired_count = self.template_cache._cache.cleanup_expired()

            print(f"Cleaned up {expired_count} expired template cache entries")

        

        if hasattr(self.component_cache._cache, 'cleanup_expired'):

            expired_count = self.component_cache._cache.cleanup_expired()

            print(f"Cleaned up {expired_count} expired component cache entries")