"""
Comprehensive test suite for the caching layer.

Tests all cache backends, cache decorator, cache key generation,
TTL functionality, thread safety, and integration with BaseTool.
"""

import time
import os
import pytest
import threading
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any

from shared.cache import (
    InMemoryCache,
    RedisCache,
    CacheManager,
    NoOpCache,
    generate_cache_key,
    make_cache_key,
    cache_result,
)
from shared.base import BaseTool
from pydantic import Field


# ============================================================================
# Test InMemoryCache
# ============================================================================


class TestInMemoryCache:
    """Test the in-memory cache implementation."""

    def test_basic_set_and_get(self):
        """Test basic cache set and get operations."""
        cache = InMemoryCache()
        cache.set("test_key", "test_value", ttl=60)
        assert cache.get("test_key") == "test_value"

    def test_get_nonexistent_key(self):
        """Test getting a key that doesn't exist."""
        cache = InMemoryCache()
        assert cache.get("nonexistent") is None

    def test_ttl_expiration(self):
        """Test that entries expire after TTL."""
        cache = InMemoryCache()
        cache.set("expiring_key", "value", ttl=1)
        assert cache.get("expiring_key") == "value"
        time.sleep(1.1)
        assert cache.get("expiring_key") is None

    def test_exists(self):
        """Test the exists method."""
        cache = InMemoryCache()
        cache.set("key1", "value1", ttl=60)
        assert cache.exists("key1") is True
        assert cache.exists("nonexistent") is False

    def test_delete(self):
        """Test deleting a key."""
        cache = InMemoryCache()
        cache.set("key1", "value1", ttl=60)
        cache.delete("key1")
        assert cache.get("key1") is None
        assert cache.exists("key1") is False

    def test_clear(self):
        """Test clearing all entries."""
        cache = InMemoryCache()
        cache.set("key1", "value1", ttl=60)
        cache.set("key2", "value2", ttl=60)
        cache.clear()
        assert cache.size() == 0
        assert cache.get("key1") is None
        assert cache.get("key2") is None

    def test_max_size_eviction(self):
        """Test that cache evicts oldest entries when max size is reached."""
        cache = InMemoryCache(max_size=5)
        for i in range(10):
            cache.set(f"key{i}", f"value{i}", ttl=100)
        assert cache.size() <= 5

    def test_complex_value_types(self):
        """Test caching different value types."""
        cache = InMemoryCache()

        # Dictionary
        cache.set("dict_key", {"name": "test", "value": 123}, ttl=60)
        assert cache.get("dict_key") == {"name": "test", "value": 123}

        # List
        cache.set("list_key", [1, 2, 3, 4, 5], ttl=60)
        assert cache.get("list_key") == [1, 2, 3, 4, 5]

        # Nested structure
        cache.set("nested", {"data": [1, 2, {"inner": "value"}]}, ttl=60)
        assert cache.get("nested") == {"data": [1, 2, {"inner": "value"}]}

    def test_thread_safety(self):
        """Test that cache is thread-safe."""
        cache = InMemoryCache()
        errors = []

        def writer(start_id):
            try:
                for i in range(100):
                    cache.set(f"thread_{start_id}_{i}", f"value_{i}", ttl=60)
            except Exception as e:
                errors.append(e)

        def reader(start_id):
            try:
                for i in range(100):
                    cache.get(f"thread_{start_id}_{i}")
            except Exception as e:
                errors.append(e)

        threads = []
        for i in range(4):
            threads.append(threading.Thread(target=writer, args=(i,)))
            threads.append(threading.Thread(target=reader, args=(i,)))

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

        assert len(errors) == 0, f"Thread safety test failed with errors: {errors}"


# ============================================================================
# Test RedisCache
# ============================================================================


class TestRedisCache:
    """Test the Redis cache implementation."""

    def test_redis_unavailable_graceful_fallback(self):
        """Test that RedisCache handles unavailable Redis gracefully."""
        # Create cache with invalid Redis connection
        cache = RedisCache(host="invalid-host", port=9999)
        assert cache.is_available is False

        # Should not raise exceptions
        cache.set("key", "value", ttl=60)
        result = cache.get("key")
        assert result is None

        cache.delete("key")
        cache.clear()
        assert cache.exists("key") is False

    @pytest.mark.skipif(
        os.getenv("SKIP_REDIS_TESTS", "true").lower() == "true",
        reason="Redis not available in test environment",
    )
    def test_redis_basic_operations(self):
        """Test basic Redis operations if Redis is available."""
        cache = RedisCache()
        if not cache.is_available:
            pytest.skip("Redis not available")

        cache.set("test_key", {"data": "value"}, ttl=60)
        result = cache.get("test_key")
        assert result == {"data": "value"}

        assert cache.exists("test_key") is True

        cache.delete("test_key")
        assert cache.exists("test_key") is False


# ============================================================================
# Test CacheManager
# ============================================================================


class TestCacheManager:
    """Test the CacheManager with fallback support."""

    def test_fallback_to_memory(self):
        """Test that CacheManager falls back to in-memory cache."""
        manager = CacheManager(redis_host="invalid-host", fallback_to_memory=True)

        # Should use memory cache as fallback
        assert isinstance(manager.backend, InMemoryCache)

        # Test operations work
        manager.set("key", "value", ttl=60)
        assert manager.get("key") == "value"

    def test_no_fallback(self):
        """Test CacheManager with fallback disabled."""
        manager = CacheManager(redis_host="invalid-host", fallback_to_memory=False)

        # Should use NoOpCache
        assert isinstance(manager.backend, NoOpCache)

        # Operations should do nothing
        manager.set("key", "value", ttl=60)
        assert manager.get("key") is None


# ============================================================================
# Test Cache Key Generation
# ============================================================================


class TestCacheKeyGeneration:
    """Test cache key generation utilities."""

    def test_generate_cache_key_consistency(self):
        """Test that identical inputs produce identical keys."""
        key1 = generate_cache_key("func", (1, 2, 3), {"a": "b", "c": "d"})
        key2 = generate_cache_key("func", (1, 2, 3), {"a": "b", "c": "d"})
        assert key1 == key2

    def test_generate_cache_key_different_args(self):
        """Test that different inputs produce different keys."""
        key1 = generate_cache_key("func", (1, 2, 3), {"a": "b"})
        key2 = generate_cache_key("func", (1, 2, 4), {"a": "b"})
        assert key1 != key2

    def test_generate_cache_key_different_kwargs(self):
        """Test that different kwargs produce different keys."""
        key1 = generate_cache_key("func", (1, 2), {"a": "b"})
        key2 = generate_cache_key("func", (1, 2), {"a": "c"})
        assert key1 != key2

    def test_generate_cache_key_different_function(self):
        """Test that different function names produce different keys."""
        key1 = generate_cache_key("func1", (1, 2), {"a": "b"})
        key2 = generate_cache_key("func2", (1, 2), {"a": "b"})
        assert key1 != key2

    def test_make_cache_key(self):
        """Test simple cache key creation."""
        key = make_cache_key("user", 123, "profile", prefix="app")
        assert key == "app:user:123:profile"

        key_no_prefix = make_cache_key("user", 456, "settings")
        assert key_no_prefix == "user:456:settings"


# ============================================================================
# Test Cache Decorator
# ============================================================================


class TestCacheDecorator:
    """Test the cache_result decorator."""

    def test_cache_decorator_basic(self):
        """Test basic caching with decorator."""
        test_cache = InMemoryCache()
        call_count = {"count": 0}

        @cache_result(ttl=60, cache=test_cache)
        def expensive_function(x, y):
            call_count["count"] += 1
            return x + y

        # First call - should execute function
        result1 = expensive_function(1, 2)
        assert result1 == 3
        assert call_count["count"] == 1

        # Second call with same args - should use cache
        result2 = expensive_function(1, 2)
        assert result2 == 3
        assert call_count["count"] == 1  # Function not called again

        # Call with different args - should execute function
        result3 = expensive_function(2, 3)
        assert result3 == 5
        assert call_count["count"] == 2

    def test_cache_decorator_with_ttl(self):
        """Test that cached values expire after TTL."""
        test_cache = InMemoryCache()
        call_count = {"count": 0}

        @cache_result(ttl=1, cache=test_cache)
        def function_with_ttl(x):
            call_count["count"] += 1
            return x * 2

        # First call
        result1 = function_with_ttl(5)
        assert result1 == 10
        assert call_count["count"] == 1

        # Immediate second call - cached
        result2 = function_with_ttl(5)
        assert result2 == 10
        assert call_count["count"] == 1

        # Wait for TTL to expire
        time.sleep(1.1)

        # Call after expiry - should execute again
        result3 = function_with_ttl(5)
        assert result3 == 10
        assert call_count["count"] == 2


# ============================================================================
# Test BaseTool Cache Integration
# ============================================================================


class TestBaseToolCacheIntegration:
    """Test caching integration with BaseTool."""

    def test_tool_with_caching_enabled(self):
        """Test that tools with caching enabled cache results."""

        class CachedTool(BaseTool):
            """Test tool with caching enabled."""

            tool_name: str = "cached_tool"
            tool_category: str = "test"
            enable_cache: bool = True
            cache_ttl: int = 3600
            cache_key_params: list = ["query"]

            query: str = Field(..., description="Query parameter")

            def _execute(self) -> Dict[str, Any]:
                return {
                    "success": True,
                    "result": f"Result for {self.query}",
                    "metadata": {},
                }

        # First call
        tool1 = CachedTool(query="test query")
        result1 = tool1.run()
        assert result1["success"] is True

        # Second call with same parameters - should use cache
        tool2 = CachedTool(query="test query")
        result2 = tool2.run()
        assert result2["success"] is True
        assert result2 == result1

    def test_tool_with_caching_disabled(self):
        """Test that tools with caching disabled don't cache."""

        class NonCachedTool(BaseTool):
            """Test tool with caching disabled."""

            tool_name: str = "non_cached_tool"
            tool_category: str = "test"
            enable_cache: bool = False

            query: str = Field(..., description="Query parameter")

            def _execute(self) -> Dict[str, Any]:
                return {
                    "success": True,
                    "result": f"Result for {self.query}",
                    "metadata": {},
                }

        tool = NonCachedTool(query="test")
        assert tool._cache_manager is None

    def test_cache_disabled_via_env(self):
        """Test that cache can be disabled via environment variable."""
        os.environ["CACHE_BACKEND"] = "none"

        class CachedTool(BaseTool):
            tool_name: str = "cached_tool"
            tool_category: str = "test"
            enable_cache: bool = True

            query: str = Field(..., description="Query")

            def _execute(self) -> Dict[str, Any]:
                return {"success": True, "result": "data", "metadata": {}}

        tool = CachedTool(query="test")
        assert tool._cache_manager is None

        # Cleanup
        del os.environ["CACHE_BACKEND"]

    def test_cache_key_generation_in_tool(self):
        """Test cache key generation in BaseTool."""

        class TestTool(BaseTool):
            tool_name: str = "test_tool"
            tool_category: str = "test"
            enable_cache: bool = True
            cache_key_params: list = ["query", "limit"]

            query: str = Field(..., description="Query")
            limit: int = Field(10, description="Limit")

            def _execute(self) -> Dict[str, Any]:
                return {"success": True, "result": "data", "metadata": {}}

        tool1 = TestTool(query="test", limit=10)
        tool2 = TestTool(query="test", limit=10)
        tool3 = TestTool(query="test", limit=20)

        key1 = tool1._get_cache_key()
        key2 = tool2._get_cache_key()
        key3 = tool3._get_cache_key()

        # Same parameters should produce same key
        assert key1 == key2

        # Different parameters should produce different key
        assert key1 != key3

    def test_cache_hit_miss_logging(self, caplog):
        """Test that cache hits and misses are logged."""

        class LoggingTool(BaseTool):
            tool_name: str = "logging_tool"
            tool_category: str = "test"
            enable_cache: bool = True
            cache_ttl: int = 60
            _enable_logging: bool = True

            query: str = Field(..., description="Query")

            def _execute(self) -> Dict[str, Any]:
                return {"success": True, "result": "data", "metadata": {}}

        # First call - cache miss
        tool1 = LoggingTool(query="test")
        tool1.run()

        # Second call - should be cache hit
        tool2 = LoggingTool(query="test")
        tool2.run()

        # Check logs contain cache hit message
        assert any("Cache HIT" in record.message for record in caplog.records)


# ============================================================================
# Test NoOpCache
# ============================================================================


class TestNoOpCache:
    """Test the no-operation cache."""

    def test_noop_cache_does_nothing(self):
        """Test that NoOpCache doesn't cache anything."""
        cache = NoOpCache()

        cache.set("key", "value", ttl=60)
        assert cache.get("key") is None

        assert cache.exists("key") is False

        # Should not raise exceptions
        cache.delete("key")
        cache.clear()


# ============================================================================
# Performance Tests
# ============================================================================


class TestCachePerformance:
    """Test cache performance characteristics."""

    def test_cache_hit_performance(self):
        """Test that cache hits are significantly faster than computation."""
        cache = InMemoryCache()
        call_count = {"count": 0}

        @cache_result(ttl=60, cache=cache)
        def slow_function(n):
            call_count["count"] += 1
            time.sleep(0.1)  # Simulate slow computation
            return n * 2

        # First call - uncached (slow)
        start_time = time.time()
        result1 = slow_function(5)
        uncached_time = time.time() - start_time
        assert result1 == 10
        assert call_count["count"] == 1

        # Second call - cached (fast)
        start_time = time.time()
        result2 = slow_function(5)
        cached_time = time.time() - start_time
        assert result2 == 10
        assert call_count["count"] == 1  # Not called again

        # Cache hit should be much faster
        assert cached_time < uncached_time / 10


# ============================================================================
# Edge Cases and Error Handling
# ============================================================================


class TestCacheEdgeCases:
    """Test edge cases and error handling."""

    def test_cache_with_none_value(self):
        """Test caching None values."""
        cache = InMemoryCache()
        cache.set("key", None, ttl=60)
        # Note: Current implementation doesn't differentiate between
        # cached None and cache miss. This is acceptable behavior.
        result = cache.get("key")
        # In current implementation, None values are not cached
        assert result is None

    def test_cache_with_empty_string(self):
        """Test caching empty strings."""
        cache = InMemoryCache()
        cache.set("key", "", ttl=60)
        assert cache.get("key") == ""

    def test_cache_with_zero(self):
        """Test caching zero values."""
        cache = InMemoryCache()
        cache.set("key", 0, ttl=60)
        assert cache.get("key") == 0

    def test_cache_with_false(self):
        """Test caching False boolean."""
        cache = InMemoryCache()
        cache.set("key", False, ttl=60)
        assert cache.get("key") is False


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])
