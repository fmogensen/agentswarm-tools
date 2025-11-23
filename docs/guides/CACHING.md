# Caching Guide for AgentSwarm Tools

**Version:** 1.0.0
**Last Updated:** 2025-11-23

This guide explains how to use the intelligent caching layer in AgentSwarm Tools to reduce API costs and improve performance.

## Table of Contents

- [Overview](#overview)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [Cache Backends](#cache-backends)
- [Using Caching in Tools](#using-caching-in-tools)
- [Cache Key Generation](#cache-key-generation)
- [Best Practices](#best-practices)
- [Performance Optimization](#performance-optimization)
- [Monitoring and Debugging](#monitoring-and-debugging)
- [Advanced Usage](#advanced-usage)
- [Troubleshooting](#troubleshooting)

## Overview

The AgentSwarm Tools caching layer provides:

- **Multiple backends**: Redis (production) and in-memory (development/testing)
- **Automatic cache management**: TTL-based expiration, thread-safe operations
- **Easy integration**: Enable caching with just a few lines of code
- **Flexible configuration**: Per-tool and global cache settings
- **Graceful fallback**: Continues working even if cache is unavailable

### Benefits

- **Cost Reduction**: Avoid redundant API calls (especially important for paid APIs)
- **Performance**: Faster response times for repeated queries
- **Rate Limit Protection**: Reduce API rate limit usage
- **Reliability**: Continue functioning even when cache is down

## Quick Start

### Enable Caching in a Tool

```python
from shared.base import BaseTool
from pydantic import Field
from typing import Dict, Any


class MySearchTool(BaseTool):
    """Search tool with caching enabled."""

    tool_name: str = "my_search"
    tool_category: str = "data"

    # Enable caching
    enable_cache: bool = True
    cache_ttl: int = 3600  # 1 hour in seconds
    cache_key_params: list = ["query", "max_results"]

    # Parameters
    query: str = Field(..., description="Search query")
    max_results: int = Field(10, description="Max results")

    def _execute(self) -> Dict[str, Any]:
        # Your implementation here
        return {
            "success": True,
            "result": [...],
            "metadata": {}
        }
```

That's it! The tool will now cache results automatically.

### Environment Configuration

```bash
# Use in-memory cache (default, good for development)
CACHE_BACKEND=memory

# Use Redis (recommended for production)
CACHE_BACKEND=redis
REDIS_URL=redis://localhost:6379

# Disable caching entirely
CACHE_BACKEND=none
```

## Configuration

### Cache Settings

| Setting | Description | Default | Example |
|---------|-------------|---------|---------|
| `enable_cache` | Enable caching for this tool | `False` | `True` |
| `cache_ttl` | Time-to-live in seconds | `3600` | `7200` (2 hours) |
| `cache_key_params` | Parameters to include in cache key | `None` | `["query", "limit"]` |

### Environment Variables

| Variable | Description | Values | Default |
|----------|-------------|--------|---------|
| `CACHE_BACKEND` | Cache backend to use | `memory`, `redis`, `none` | `memory` |
| `REDIS_URL` | Redis connection URL | `redis://host:port` | `redis://localhost:6379` |

## Cache Backends

### In-Memory Cache

**When to use:**
- Development and testing
- Single-process applications
- Low-volume workloads

**Characteristics:**
- Fast (no network overhead)
- Data lost on process restart
- Thread-safe
- Automatic size-based eviction

**Configuration:**
```bash
CACHE_BACKEND=memory
```

**Example:**
```python
class MyTool(BaseTool):
    enable_cache: bool = True
    cache_ttl: int = 1800  # 30 minutes
```

### Redis Cache

**When to use:**
- Production environments
- Multi-process/distributed applications
- Persistent caching across restarts
- High-volume workloads

**Characteristics:**
- Persistent storage
- Shared across processes
- Network overhead (minimal)
- Graceful fallback if unavailable

**Configuration:**
```bash
CACHE_BACKEND=redis
REDIS_URL=redis://localhost:6379

# With password
REDIS_URL=redis://:password@localhost:6379

# Different database
REDIS_URL=redis://localhost:6379/1
```

**Example:**
```python
# Same code works with Redis - just change environment variable
class MyTool(BaseTool):
    enable_cache: bool = True
    cache_ttl: int = 3600
```

### No-Op Cache

**When to use:**
- Debugging
- Testing without caching
- Specific performance testing scenarios

**Configuration:**
```bash
CACHE_BACKEND=none
```

## Using Caching in Tools

### Basic Pattern

```python
class WebSearch(BaseTool):
    """Web search with 1-hour caching."""

    tool_name: str = "web_search"
    tool_category: str = "data"

    # Caching configuration
    enable_cache: bool = True
    cache_ttl: int = 3600  # 1 hour
    cache_key_params: list = ["query", "max_results"]

    # Tool parameters
    query: str = Field(..., description="Search query")
    max_results: int = Field(10, description="Max results")

    def _execute(self) -> Dict[str, Any]:
        # This method only runs on cache miss
        results = self._call_search_api()
        return {
            "success": True,
            "result": results,
            "metadata": {"source": "api"}
        }
```

### TTL Recommendations by Tool Type

| Tool Type | Recommended TTL | Reasoning |
|-----------|----------------|-----------|
| Web Search | 1 hour (3600s) | Content changes moderately |
| Scholar Search | 2 hours (7200s) | Academic content is stable |
| Image Search | 1 hour (3600s) | Image results relatively stable |
| Product Search | 30 minutes (1800s) | Prices/availability change frequently |
| Weather Data | 10 minutes (600s) | Weather changes frequently |
| Stock Prices | 5 minutes (300s) | Real-time data |
| Analytics Reports | 6 hours (21600s) | Expensive queries, stable data |

### Cache Key Parameters

The `cache_key_params` list defines which tool parameters affect caching:

```python
class ExampleTool(BaseTool):
    # Only query and limit affect cache key
    cache_key_params: list = ["query", "limit"]

    query: str = Field(...)
    limit: int = Field(10)
    format: str = Field("json")  # Not in cache key

    # These two calls will use the same cache entry:
    # tool1 = ExampleTool(query="test", limit=5, format="json")
    # tool2 = ExampleTool(query="test", limit=5, format="xml")

    # This call will use a different cache entry:
    # tool3 = ExampleTool(query="test", limit=10, format="json")
```

**If `cache_key_params` is not specified:**
- All non-private attributes are included in the cache key
- Excludes: `enable_cache`, `cache_ttl`, `cache_key_params`
- Use explicit list for better control

## Cache Key Generation

### Automatic Key Generation

Cache keys are automatically generated based on:
1. Tool name
2. Parameter values (from `cache_key_params`)
3. SHA-256 hash for uniqueness

**Example:**
```python
tool = WebSearch(query="python", max_results=10)
# Cache key: "agentswarm:web_search:a3f8d9e2..." (hash of params)
```

### Manual Cache Control

You can override cache key generation if needed:

```python
class CustomCacheTool(BaseTool):
    def _get_cache_key(self) -> str:
        # Custom cache key logic
        return f"custom::{self.tool_name}::{self.special_id}"
```

## Best Practices

### 1. Choose Appropriate TTL Values

```python
# Good - Balances freshness and cost
class NewsSearch(BaseTool):
    enable_cache: bool = True
    cache_ttl: int = 1800  # 30 minutes for news

# Bad - Too long for time-sensitive data
class StockPrice(BaseTool):
    enable_cache: bool = True
    cache_ttl: int = 86400  # 24 hours is too long!
```

### 2. Specify Cache Key Parameters

```python
# Good - Explicit control
cache_key_params: list = ["query", "location", "date_range"]

# Okay - Uses all parameters
cache_key_params: list = None  # Default behavior

# Bad - Missing important parameters
cache_key_params: list = ["query"]  # Missing 'location'!
```

### 3. Handle Cache-Specific Use Cases

```python
class SearchTool(BaseTool):
    enable_cache: bool = True
    cache_ttl: int = 3600

    query: str = Field(...)
    force_refresh: bool = Field(False, description="Skip cache")

    def _execute(self) -> Dict[str, Any]:
        # Check force_refresh before caching
        if self.force_refresh:
            # Invalidate cache for this query
            if self._cache_manager:
                self._cache_manager.delete(self._get_cache_key())

        # Normal execution
        return self._process()
```

### 4. Monitor Cache Performance

```python
class MonitoredTool(BaseTool):
    enable_cache: bool = True
    _enable_logging: bool = True  # Enable cache hit/miss logging

    # Logs will show:
    # - "Cache HIT for tool_name [request_id=...]"
    # - "Cached result with TTL=3600s"
```

### 5. Use Redis in Production

```bash
# Development
CACHE_BACKEND=memory

# Staging/Production
CACHE_BACKEND=redis
REDIS_URL=redis://production-redis:6379
```

## Performance Optimization

### Cache Hit Rate Estimation

Expected cache hit rates by tool type:

| Tool Type | Expected Hit Rate | Notes |
|-----------|------------------|-------|
| Search Tools | 40-60% | Repeated queries common |
| Data Retrieval | 60-80% | Same data accessed multiple times |
| API Wrappers | 50-70% | Depends on query diversity |
| Analytics | 70-90% | Reports run repeatedly |

### Cost Savings Calculator

```python
# Example: Web Search Tool
API_COST_PER_CALL = 0.002  # $0.002 per search
DAILY_CALLS = 10000
CACHE_HIT_RATE = 0.5  # 50%

# Without caching
cost_without_cache = DAILY_CALLS * API_COST_PER_CALL
# $20.00/day

# With caching
cost_with_cache = DAILY_CALLS * (1 - CACHE_HIT_RATE) * API_COST_PER_CALL
# $10.00/day

# Savings
daily_savings = cost_without_cache - cost_with_cache
# $10.00/day = $300/month = $3,650/year
```

### Memory Usage

**In-Memory Cache:**
- Default max size: 1000 entries
- Average entry size: ~1-10 KB
- Total memory: ~1-10 MB (typical)

**Redis Cache:**
- Stored externally
- Minimal client memory footprint

## Monitoring and Debugging

### Enable Cache Logging

```python
class DebugTool(BaseTool):
    _enable_logging: bool = True  # Shows cache operations
    enable_cache: bool = True
```

**Log Messages:**
```
INFO - Cache HIT for web_search [request_id=abc123]
DEBUG - Cached result for web_search with TTL=3600s
DEBUG - Cache initialized for web_search with InMemoryCache backend
WARNING - Cache read error: Connection refused
```

### Check Cache Status

```python
from shared.cache import CacheManager

# Create manager
manager = CacheManager()

# Check backend type
print(f"Backend: {type(manager.backend).__name__}")
# Output: "InMemoryCache" or "RedisCache"

# Check if key exists
exists = manager.exists("agentswarm:web_search:key123")

# Get cache size (in-memory only)
if hasattr(manager.backend, 'size'):
    print(f"Cache size: {manager.backend.size()} entries")
```

### Testing Cache Behavior

```python
# Test with cache enabled
os.environ["CACHE_BACKEND"] = "memory"
tool1 = WebSearch(query="test")
result1 = tool1.run()  # API call

tool2 = WebSearch(query="test")
result2 = tool2.run()  # Cache hit

assert result1 == result2

# Test with cache disabled
os.environ["CACHE_BACKEND"] = "none"
tool3 = WebSearch(query="test")
result3 = tool3.run()  # API call (cache disabled)
```

## Advanced Usage

### Custom Cache Manager

```python
from shared.cache import CacheManager

class MyTool(BaseTool):
    def __init__(self, **data):
        super().__init__(**data)

        # Use custom cache configuration
        self._cache_manager = CacheManager(
            redis_host="custom-redis",
            redis_port=6380,
            redis_db=2,
            fallback_to_memory=True
        )
```

### Programmatic Cache Control

```python
class AdvancedTool(BaseTool):
    enable_cache: bool = True

    def _execute(self) -> Dict[str, Any]:
        # Check if specific key exists
        cache_key = self._get_cache_key()

        if self._cache_manager and self._cache_manager.exists(cache_key):
            # Custom handling for cache hit
            pass

        # Manual cache invalidation
        if some_condition:
            self._cache_manager.delete(cache_key)

        # Clear all cache entries for this tool
        # (Be careful - this affects all queries!)
        if reset_all:
            self._cache_manager.clear()

        return result
```

### Cache Warming

```python
def warm_cache():
    """Pre-populate cache with common queries."""
    common_queries = ["python", "javascript", "machine learning"]

    for query in common_queries:
        tool = WebSearch(query=query, max_results=10)
        tool.run()  # Populates cache

    print("Cache warming complete!")
```

### Cache Analytics

```python
class AnalyticsTool(BaseTool):
    enable_cache: bool = True

    def __init__(self, **data):
        super().__init__(**data)
        self.cache_hits = 0
        self.cache_misses = 0

    def run(self) -> Any:
        cached = self._get_from_cache()

        if cached:
            self.cache_hits += 1
        else:
            self.cache_misses += 1

        result = super().run()

        # Log cache performance
        total = self.cache_hits + self.cache_misses
        hit_rate = self.cache_hits / total if total > 0 else 0
        self._logger.info(f"Cache hit rate: {hit_rate:.2%}")

        return result
```

## Troubleshooting

### Cache Not Working

**Problem:** Results not being cached

**Solutions:**
```python
# 1. Check if caching is enabled
class MyTool(BaseTool):
    enable_cache: bool = True  # ← Must be True

# 2. Check environment variable
import os
print(os.getenv("CACHE_BACKEND"))  # Should not be "none"

# 3. Check cache initialization
tool = MyTool(...)
print(tool._cache_manager)  # Should not be None

# 4. Enable logging to see what's happening
class MyTool(BaseTool):
    _enable_logging: bool = True
```

### Redis Connection Errors

**Problem:** `WARNING - Failed to initialize cache: Connection refused`

**Solutions:**
```bash
# 1. Check Redis is running
redis-cli ping
# Should return: PONG

# 2. Check Redis URL
echo $REDIS_URL
# Should be: redis://localhost:6379

# 3. Check Redis is accessible
telnet localhost 6379

# 4. Fall back to memory cache (automatic)
# Tool will use InMemoryCache if Redis unavailable
```

### Different Results from Cache vs API

**Problem:** Cached results differ from fresh API results

**Solutions:**
```python
# 1. Reduce TTL for more frequent updates
cache_ttl: int = 600  # 10 minutes instead of 1 hour

# 2. Add force_refresh parameter
force_refresh: bool = Field(False, description="Skip cache")

if self.force_refresh:
    # Clear cache for this query
    self._cache_manager.delete(self._get_cache_key())

# 3. Include version in cache key
cache_key_params: list = ["query", "api_version"]
```

### Memory Issues with In-Memory Cache

**Problem:** High memory usage with in-memory cache

**Solutions:**
```python
# 1. Reduce max cache size
from shared.cache import InMemoryCache
cache = InMemoryCache(max_size=500)  # Default is 1000

# 2. Reduce TTL to expire entries faster
cache_ttl: int = 1800  # 30 minutes instead of 1 hour

# 3. Use Redis instead
# Set CACHE_BACKEND=redis in production

# 4. Clear cache periodically
if self._cache_manager:
    self._cache_manager.clear()
```

### Cache Key Collisions

**Problem:** Different queries returning same cached results

**Solutions:**
```python
# 1. Explicitly set cache_key_params
cache_key_params: list = ["query", "filters", "limit"]

# 2. Include all relevant parameters
cache_key_params: list = [
    "query",
    "max_results",
    "language",
    "region"
]

# 3. Debug cache keys
tool1 = MyTool(query="test", limit=10)
tool2 = MyTool(query="test", limit=20)

key1 = tool1._get_cache_key()
key2 = tool2._get_cache_key()

print(f"Key 1: {key1}")
print(f"Key 2: {key2}")
print(f"Same? {key1 == key2}")  # Should be False
```

## Examples

### Example 1: Web Search with Caching

```python
from shared.base import BaseTool
from pydantic import Field
from typing import Dict, Any

class WebSearch(BaseTool):
    """Web search with intelligent caching."""

    tool_name: str = "web_search"
    tool_category: str = "data"

    # Enable 1-hour caching
    enable_cache: bool = True
    cache_ttl: int = 3600
    cache_key_params: list = ["query", "max_results"]

    query: str = Field(..., description="Search query")
    max_results: int = Field(10, description="Max results")

    def _execute(self) -> Dict[str, Any]:
        # Only called on cache miss
        results = self._call_google_api()
        return {
            "success": True,
            "result": results,
            "metadata": {"cached": False}
        }

# Usage
tool = WebSearch(query="python tutorials", max_results=10)
result = tool.run()  # API call

# Second call with same params - cache hit!
tool2 = WebSearch(query="python tutorials", max_results=10)
result2 = tool2.run()  # No API call, instant response
```

### Example 2: Conditional Caching

```python
class SmartSearchTool(BaseTool):
    """Search tool with conditional caching."""

    tool_name: str = "smart_search"
    tool_category: str = "data"

    enable_cache: bool = True
    cache_ttl: int = 3600

    query: str = Field(...)
    force_fresh: bool = Field(False, description="Force fresh results")

    def _execute(self) -> Dict[str, Any]:
        # Skip cache if force_fresh is True
        if self.force_fresh and self._cache_manager:
            self._cache_manager.delete(self._get_cache_key())

        return self._process()
```

### Example 3: Multi-TTL Strategy

```python
class DataTool(BaseTool):
    """Tool with dynamic TTL based on data type."""

    tool_name: str = "data_tool"
    tool_category: str = "data"

    enable_cache: bool = True

    data_type: str = Field(...)  # "realtime" or "historical"

    def __init__(self, **data):
        super().__init__(**data)

        # Set TTL based on data type
        if self.data_type == "realtime":
            self.cache_ttl = 300  # 5 minutes
        elif self.data_type == "historical":
            self.cache_ttl = 86400  # 24 hours
        else:
            self.cache_ttl = 3600  # 1 hour default
```

## Summary

**Key Takeaways:**

1. **Easy to Enable**: Just set `enable_cache = True` and configure TTL
2. **Flexible Backends**: In-memory for dev, Redis for production
3. **Automatic Management**: Cache keys, expiration, and cleanup handled automatically
4. **Graceful Fallback**: Works even when cache is unavailable
5. **Cost Effective**: Can save 40-60% on API costs with typical hit rates

**Quick Reference:**

```python
# Enable caching in any tool
class MyTool(BaseTool):
    enable_cache: bool = True
    cache_ttl: int = 3600
    cache_key_params: list = ["query", "limit"]
```

**Environment Setup:**

```bash
# Development
CACHE_BACKEND=memory

# Production
CACHE_BACKEND=redis
REDIS_URL=redis://localhost:6379
```

For more information, see:
- [Contributing Guide](../../CONTRIBUTING.md)
- [Testing Guide](TESTING_GUIDE.md)
- [Framework Features](FRAMEWORK_FEATURES.md)

---

**Questions or Issues?**

- Open an issue on GitHub
- Check the troubleshooting section above
- Review the test suite in `tests/unit/shared/test_cache.py`
