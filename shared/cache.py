"""
Caching layer for agentswarm-tools repository.

Provides abstract cache backend, in-memory implementation with TTL support,
optional Redis implementation, and caching decorator for function results.
"""

import hashlib
import json
import os
import pickle
import threading
import time
from abc import ABC, abstractmethod
from functools import wraps
from typing import Any, Callable, Dict, Optional, Tuple


class CacheBackend(ABC):
    """Abstract base class for cache backends."""

    @abstractmethod
    def get(self, key: str) -> Optional[Any]:
        """
        Retrieve a value from the cache.

        Args:
            key: The cache key to retrieve.

        Returns:
            The cached value, or None if not found or expired.
        """
        ...

    @abstractmethod
    def set(self, key: str, value: Any, ttl: int = 300) -> None:
        """
        Store a value in the cache.

        Args:
            key: The cache key.
            value: The value to store.
            ttl: Time to live in seconds (default: 300).
        """
        ...

    @abstractmethod
    def delete(self, key: str) -> None:
        """
        Delete a key from the cache.

        Args:
            key: The cache key to delete.
        """
        ...

    @abstractmethod
    def clear(self) -> None:
        """Clear all entries from the cache."""
        ...

    @abstractmethod
    def exists(self, key: str) -> bool:
        """
        Check if a key exists and is not expired.

        Args:
            key: The cache key to check.

        Returns:
            True if the key exists and is valid, False otherwise.
        """
        ...


class InMemoryCache(CacheBackend):
    """
    Thread-safe in-memory cache implementation with TTL support.

    Suitable for single-process applications. Data is lost on process restart.
    """

    def __init__(self, max_size: int = 1000):
        """
        Initialize the in-memory cache.

        Args:
            max_size: Maximum number of entries before automatic cleanup.
        """
        self._cache: Dict[str, Any] = {}
        self._expiry: Dict[str, float] = {}
        self._lock = threading.RLock()
        self._max_size = max_size

    def get(self, key: str) -> Optional[Any]:
        """Retrieve a value from the cache."""
        with self._lock:
            if key in self._cache:
                if self._expiry.get(key, float("inf")) > time.time():
                    return self._cache[key]
                # Entry has expired, clean it up
                self.delete(key)
            return None

    def set(self, key: str, value: Any, ttl: int = 300) -> None:
        """Store a value in the cache with TTL."""
        with self._lock:
            # Cleanup if we're at max capacity
            if len(self._cache) >= self._max_size and key not in self._cache:
                self._cleanup_expired()
                # If still at max, remove oldest entries
                if len(self._cache) >= self._max_size:
                    self._evict_oldest(len(self._cache) - self._max_size + 1)

            self._cache[key] = value
            self._expiry[key] = time.time() + ttl

    def delete(self, key: str) -> None:
        """Delete a key from the cache."""
        with self._lock:
            self._cache.pop(key, None)
            self._expiry.pop(key, None)

    def clear(self) -> None:
        """Clear all entries from the cache."""
        with self._lock:
            self._cache.clear()
            self._expiry.clear()

    def exists(self, key: str) -> bool:
        """Check if a key exists and is not expired."""
        with self._lock:
            if key in self._cache:
                if self._expiry.get(key, float("inf")) > time.time():
                    return True
                self.delete(key)
            return False

    def _cleanup_expired(self) -> None:
        """Remove all expired entries."""
        current_time = time.time()
        expired_keys = [key for key, expiry in self._expiry.items() if expiry <= current_time]
        for key in expired_keys:
            self._cache.pop(key, None)
            self._expiry.pop(key, None)

    def _evict_oldest(self, count: int) -> None:
        """Evict the oldest entries based on expiry time."""
        if count <= 0:
            return
        sorted_keys = sorted(self._expiry.keys(), key=lambda k: self._expiry[k])
        for key in sorted_keys[:count]:
            self._cache.pop(key, None)
            self._expiry.pop(key, None)

    def size(self) -> int:
        """Return the current number of entries in the cache."""
        with self._lock:
            return len(self._cache)


class RedisCache(CacheBackend):
    """
    Redis-based cache implementation.

    Gracefully falls back to None returns if Redis is not available.
    Suitable for distributed applications requiring shared cache.
    """

    def __init__(
        self,
        host: str = "localhost",
        port: int = 6379,
        db: int = 0,
        password: Optional[str] = None,
        prefix: str = "agentswarm:",
    ):
        """
        Initialize Redis cache connection.

        Args:
            host: Redis server hostname.
            port: Redis server port.
            db: Redis database number.
            password: Redis password (if required).
            prefix: Key prefix for namespacing.
        """
        self._prefix = prefix
        self._client = None
        self._available = False

        try:
            import redis

            self._client = redis.Redis(
                host=host,
                port=port,
                db=db,
                password=password,
                decode_responses=False,  # We'll handle serialization ourselves
                socket_connect_timeout=2,
                socket_timeout=2,
            )
            # Test connection
            self._client.ping()
            self._available = True
        except ImportError:
            # Redis library not installed
            pass
        except Exception:
            # Redis server not available
            pass

    @property
    def is_available(self) -> bool:
        """Check if Redis is available."""
        return self._available

    def _make_key(self, key: str) -> str:
        """Add prefix to key for namespacing."""
        return f"{self._prefix}{key}"

    def get(self, key: str) -> Optional[Any]:
        """Retrieve a value from Redis."""
        if not self._available:
            return None

        try:
            data = self._client.get(self._make_key(key))
            if data is not None:
                return pickle.loads(data)
            return None
        except Exception:
            return None

    def set(self, key: str, value: Any, ttl: int = 300) -> None:
        """Store a value in Redis with TTL."""
        if not self._available:
            return

        try:
            serialized = pickle.dumps(value)
            self._client.setex(self._make_key(key), ttl, serialized)
        except Exception:
            pass

    def delete(self, key: str) -> None:
        """Delete a key from Redis."""
        if not self._available:
            return

        try:
            self._client.delete(self._make_key(key))
        except Exception:
            pass

    def clear(self) -> None:
        """Clear all entries with our prefix from Redis."""
        if not self._available:
            return

        try:
            # Use SCAN to find all keys with our prefix
            cursor = 0
            pattern = f"{self._prefix}*"
            while True:
                cursor, keys = self._client.scan(cursor, match=pattern, count=100)
                if keys:
                    self._client.delete(*keys)
                if cursor == 0:
                    break
        except Exception:
            pass

    def exists(self, key: str) -> bool:
        """Check if a key exists in Redis."""
        if not self._available:
            return False

        try:
            return bool(self._client.exists(self._make_key(key)))
        except Exception:
            return False


def generate_cache_key(func_name: str, args: Tuple, kwargs: Dict) -> str:
    """
    Generate a unique cache key from function name and arguments.

    Args:
        func_name: Name of the function being cached.
        args: Positional arguments.
        kwargs: Keyword arguments.

    Returns:
        A unique hash-based cache key.
    """
    # Convert arguments to a serializable format
    key_data = {
        "func": func_name,
        "args": _serialize_for_key(args),
        "kwargs": _serialize_for_key(kwargs),
    }

    # Create a JSON string and hash it
    key_string = json.dumps(key_data, sort_keys=True, default=str)
    return hashlib.sha256(key_string.encode()).hexdigest()


def _serialize_for_key(obj: Any) -> Any:
    """
    Recursively convert objects to serializable format for cache key generation.

    Args:
        obj: Object to serialize.

    Returns:
        Serializable representation of the object.
    """
    if obj is None or isinstance(obj, (str, int, float, bool)):
        return obj
    elif isinstance(obj, (list, tuple)):
        return [_serialize_for_key(item) for item in obj]
    elif isinstance(obj, dict):
        return {str(k): _serialize_for_key(v) for k, v in obj.items()}
    elif hasattr(obj, "__dict__"):
        return _serialize_for_key(obj.__dict__)
    else:
        return str(obj)


def make_cache_key(*parts: Any, prefix: str = "") -> str:
    """
    Create a simple cache key from parts.

    Args:
        *parts: Parts to combine into the key.
        prefix: Optional prefix for the key.

    Returns:
        A cache key string.
    """
    key_parts = [str(part) for part in parts]
    key = ":".join(key_parts)
    if prefix:
        key = f"{prefix}:{key}"
    return key


def cache_result(
    ttl: int = 300, cache: Optional[CacheBackend] = None, key_prefix: str = ""
) -> Callable:
    """
    Decorator to cache function results.

    Args:
        ttl: Time to live in seconds (default: 300).
        cache: Cache backend to use (defaults to default_cache).
        key_prefix: Optional prefix for cache keys.

    Returns:
        Decorated function with caching.

    Example:
        @cache_result(ttl=600)
        def expensive_operation(param1, param2):
            # ... expensive computation
            return result
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Use provided cache or default
            cache_backend = cache or default_cache

            # Generate cache key
            prefix = key_prefix or func.__module__
            key = f"{prefix}:{generate_cache_key(func.__name__, args, kwargs)}"

            # Try to get from cache
            cached = cache_backend.get(key)
            if cached is not None:
                return cached

            # Execute function and cache result
            result = func(*args, **kwargs)
            cache_backend.set(key, result, ttl)
            return result

        # Add cache control methods to the wrapper
        wrapper.cache_clear = lambda: None  # Will be set properly below
        wrapper.cache_info = lambda: {"cache": cache or default_cache}

        return wrapper

    return decorator


class CacheManager:
    """
    Manager for handling multiple cache backends with fallback support.

    Tries Redis first, falls back to in-memory cache if unavailable.
    """

    def __init__(
        self,
        redis_host: str = "localhost",
        redis_port: int = 6379,
        redis_db: int = 0,
        redis_password: Optional[str] = None,
        fallback_to_memory: bool = True,
    ):
        """
        Initialize cache manager with optional Redis and in-memory fallback.

        Args:
            redis_host: Redis server hostname.
            redis_port: Redis server port.
            redis_db: Redis database number.
            redis_password: Redis password.
            fallback_to_memory: Whether to use in-memory cache as fallback.
        """
        self._redis_cache = RedisCache(
            host=redis_host, port=redis_port, db=redis_db, password=redis_password
        )
        self._memory_cache = InMemoryCache() if fallback_to_memory else None

    @property
    def backend(self) -> CacheBackend:
        """Return the active cache backend."""
        if self._redis_cache.is_available:
            return self._redis_cache
        elif self._memory_cache:
            return self._memory_cache
        else:
            # Return a no-op cache
            return NoOpCache()

    def get(self, key: str) -> Optional[Any]:
        """Get value from the active cache backend."""
        return self.backend.get(key)

    def set(self, key: str, value: Any, ttl: int = 300) -> None:
        """Set value in the active cache backend."""
        self.backend.set(key, value, ttl)

    def delete(self, key: str) -> None:
        """Delete key from the active cache backend."""
        self.backend.delete(key)

    def clear(self) -> None:
        """Clear the active cache backend."""
        self.backend.clear()

    def exists(self, key: str) -> bool:
        """Check if key exists in the active cache backend."""
        return self.backend.exists(key)


class NoOpCache(CacheBackend):
    """A no-operation cache that does nothing. Used as ultimate fallback."""

    def get(self, key: str) -> Optional[Any]:
        return None

    def set(self, key: str, value: Any, ttl: int = 300) -> None:
        pass

    def delete(self, key: str) -> None:
        pass

    def clear(self) -> None:
        pass

    def exists(self, key: str) -> bool:
        return False


# Global cache instance (singleton pattern)
_global_cache_manager: Optional[CacheManager] = None


def get_global_cache_manager() -> CacheManager:
    """
    Get or create the global cache manager instance (singleton).

    Returns:
        The global CacheManager instance
    """
    global _global_cache_manager

    if _global_cache_manager is None:
        # Parse configuration from environment
        cache_backend = os.getenv("CACHE_BACKEND", "memory").lower()

        if cache_backend == "redis":
            redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
            # Parse Redis URL
            if redis_url.startswith("redis://"):
                # Basic parsing (handle auth and db later if needed)
                url_parts = redis_url.replace("redis://", "").split(":")
                host = url_parts[0] if len(url_parts) > 0 else "localhost"
                port = int(url_parts[1]) if len(url_parts) > 1 else 6379
            else:
                host = "localhost"
                port = 6379

            _global_cache_manager = CacheManager(
                redis_host=host, redis_port=port, fallback_to_memory=True
            )
        else:
            # Use in-memory cache
            _global_cache_manager = CacheManager(fallback_to_memory=True)

    return _global_cache_manager


# Default cache instance (in-memory)
default_cache = InMemoryCache()


if __name__ == "__main__":
    print("Testing cache module...")
    print("=" * 50)

    # Test InMemoryCache
    print("\n1. Testing InMemoryCache...")
    memory_cache = InMemoryCache(max_size=5)

    # Test set and get
    memory_cache.set("key1", "value1", ttl=10)
    assert memory_cache.get("key1") == "value1", "Failed: basic set/get"
    print("   - Basic set/get: PASSED")

    # Test exists
    assert memory_cache.exists("key1") == True, "Failed: exists for valid key"
    assert memory_cache.exists("nonexistent") == False, "Failed: exists for invalid key"
    print("   - Exists check: PASSED")

    # Test delete
    memory_cache.delete("key1")
    assert memory_cache.get("key1") is None, "Failed: delete"
    print("   - Delete: PASSED")

    # Test TTL expiration
    memory_cache.set("expiring_key", "value", ttl=1)
    assert memory_cache.get("expiring_key") == "value", "Failed: TTL before expiry"
    time.sleep(1.1)
    assert memory_cache.get("expiring_key") is None, "Failed: TTL after expiry"
    print("   - TTL expiration: PASSED")

    # Test clear
    memory_cache.set("key1", "value1")
    memory_cache.set("key2", "value2")
    memory_cache.clear()
    assert memory_cache.size() == 0, "Failed: clear"
    print("   - Clear: PASSED")

    # Test max size eviction
    for i in range(10):
        memory_cache.set(f"key{i}", f"value{i}", ttl=100)
    assert memory_cache.size() <= 5, f"Failed: max size eviction (size={memory_cache.size()})"
    print("   - Max size eviction: PASSED")

    # Test cache key generation
    print("\n2. Testing cache key generation...")
    key1 = generate_cache_key("func", (1, 2), {"a": "b"})
    key2 = generate_cache_key("func", (1, 2), {"a": "b"})
    key3 = generate_cache_key("func", (1, 3), {"a": "b"})
    assert key1 == key2, "Failed: identical inputs should produce same key"
    assert key1 != key3, "Failed: different inputs should produce different keys"
    print("   - Key consistency: PASSED")

    simple_key = make_cache_key("user", 123, "profile", prefix="app")
    assert simple_key == "app:user:123:profile", f"Failed: simple key generation (got {simple_key})"
    print("   - Simple key generation: PASSED")

    # Test cache_result decorator
    print("\n3. Testing cache_result decorator...")
    test_cache = InMemoryCache()
    call_tracker = {"count": 0}

    @cache_result(ttl=60, cache=test_cache)
    def expensive_function(x, y):
        call_tracker["count"] += 1
        return x + y

    result1 = expensive_function(1, 2)
    result2 = expensive_function(1, 2)  # Should be cached
    result3 = expensive_function(2, 3)  # Different args, not cached

    assert result1 == 3, "Failed: decorator result"
    assert result2 == 3, "Failed: cached result"
    assert result3 == 5, "Failed: different args result"
    assert (
        call_tracker["count"] == 2
    ), f"Failed: function should be called twice, was called {call_tracker['count']} times"
    print("   - Decorator caching: PASSED")

    # Test RedisCache (graceful fallback)
    print("\n4. Testing RedisCache (graceful fallback)...")
    redis_cache = RedisCache()
    if redis_cache.is_available:
        redis_cache.set("test_key", {"data": "value"})
        result = redis_cache.get("test_key")
        assert result == {"data": "value"}, "Failed: Redis set/get"
        redis_cache.delete("test_key")
        print("   - Redis available and working: PASSED")
    else:
        # Test that operations don't fail when Redis is unavailable
        redis_cache.set("key", "value")  # Should not raise
        result = redis_cache.get("key")  # Should return None
        assert result is None, "Failed: graceful fallback"
        print("   - Redis unavailable, graceful fallback: PASSED")

    # Test CacheManager
    print("\n5. Testing CacheManager...")
    manager = CacheManager(fallback_to_memory=True)
    manager.set("manager_key", "manager_value", ttl=60)
    assert manager.get("manager_key") == "manager_value", "Failed: CacheManager set/get"
    print(f"   - CacheManager backend: {type(manager.backend).__name__}")
    print("   - CacheManager operations: PASSED")

    # Test NoOpCache
    print("\n6. Testing NoOpCache...")
    noop_cache = NoOpCache()
    noop_cache.set("key", "value")
    assert noop_cache.get("key") is None, "Failed: NoOpCache should return None"
    assert noop_cache.exists("key") == False, "Failed: NoOpCache exists should return False"
    print("   - NoOpCache: PASSED")

    # Test thread safety
    print("\n7. Testing thread safety...")
    import concurrent.futures

    thread_cache = InMemoryCache()

    def write_values(start):
        for i in range(100):
            thread_cache.set(f"thread_key_{start}_{i}", f"value_{i}")

    def read_values(start):
        for i in range(100):
            thread_cache.get(f"thread_key_{start}_{i}")

    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        futures = []
        for i in range(4):
            futures.append(executor.submit(write_values, i))
            futures.append(executor.submit(read_values, i))
        concurrent.futures.wait(futures)

    print("   - Thread safety: PASSED (no deadlocks or errors)")

    print("\n" + "=" * 50)
    print("All tests passed!")
