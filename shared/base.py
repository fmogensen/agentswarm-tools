"""
Base tool class for AgentSwarm Tools Framework.
Provides built-in error handling, analytics, security, and logging.

This class extends Agency Swarm's BaseTool while maintaining 100% compatibility.
"""

import logging
import os
import time
import uuid
import warnings
from abc import abstractmethod
from datetime import datetime
from typing import Any, Dict, Optional

# Import from Agency Swarm
try:
    from agency_swarm.tools.base_tool import BaseTool as AgencyBaseTool
except ImportError:
    # Fallback for development/testing without agency-swarm installed
    from abc import ABC

    from pydantic import BaseModel

    class AgencyBaseTool(BaseModel, ABC):
        """Fallback BaseTool for development."""

        @abstractmethod
        def run(self):
            pass


from .analytics import AnalyticsEvent, EventType, record_event
from .cache import get_global_cache_manager, make_cache_key
from .errors import ToolError, ValidationError
from .monitoring import record_performance_metric
from .security import get_rate_limiter

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


class BaseTool(AgencyBaseTool):
    """
    Enhanced base tool with built-in error handling, analytics, and security.

    All tools should inherit from this class and implement the `_execute()` method.

    Features:
    - Automatic error handling and retry logic
    - Analytics tracking (requests, performance, errors)
    - Rate limiting
    - Input validation
    - Structured logging
    - Request tracing

    Example:
        ```python
        from agentswarm_tools.shared.base import BaseTool
        from pydantic import Field

        class MyTool(BaseTool):
            '''Tool description for AI agents.'''

            param1: str = Field(..., description="Parameter description")

            # Tool configuration
            tool_name = "my_tool"
            tool_category = "custom"
            rate_limit_type = "default"

            def _execute(self) -> Any:
                '''Implement your tool logic here.'''
                result = do_something(self.param1)
                return result
        ```
    """

    # Tool metadata (override in subclasses)
    tool_name: str = "base_tool"
    tool_category: str = "general"
    rate_limit_type: str = "default"
    rate_limit_cost: int = 1

    # Retry configuration
    max_retries: int = 3
    retry_delay: float = 1.0  # seconds

    # Analytics
    _enable_analytics: bool = True
    _enable_logging: bool = True

    # Caching configuration
    enable_cache: bool = False  # Set to True to enable caching for this tool
    cache_ttl: int = 3600  # Cache TTL in seconds (default: 1 hour)
    cache_key_params: Optional[list] = None  # List of param names to use for cache key

    def __init__(self, **data):
        """Initialize tool with request tracking."""
        super().__init__(**data)
        self._request_id = str(uuid.uuid4())
        self._user_id: Optional[str] = data.get("user_id")
        self._logger = logging.getLogger(f"agentswarm.tools.{self.tool_name}")
        self._start_time: Optional[float] = None
        self._cache_manager: Optional[CacheManager] = None
        self._init_cache()

    @abstractmethod
    def _execute(self) -> Any:
        """
        Execute the tool logic.

        This method must be implemented by all subclasses.

        Returns:
            Tool output (can be any type: str, dict, list, etc.)

        Raises:
            ToolError: On execution failure
        """
        raise NotImplementedError("Tool must implement _execute() method")

    def run(self) -> Any:
        """
        Run the tool with error handling, analytics, rate limiting, caching, and performance monitoring.

        This method is called by Agency Swarm and should not be overridden.

        Returns:
            Tool output or error message

        Note:
            This method wraps _execute() with all the framework features.
        """
        self._start_time = time.time()
        cache_hit = False
        error_type = None

        try:
            # Log start
            self._log_start()

            # Record start event
            if self._enable_analytics:
                self._record_event(EventType.TOOL_START)

            # Try to get from cache first
            cached_result = self._get_from_cache()
            if cached_result is not None:
                cache_hit = True
                # Log cache hit
                self._log_success(cached_result)
                if self._enable_analytics:
                    self._record_event(
                        EventType.TOOL_SUCCESS, success=True, metadata={"cache_hit": True}
                    )

                # Record performance metric for cache hit
                duration_ms = (time.time() - self._start_time) * 1000
                record_performance_metric(
                    tool_name=self.tool_name,
                    duration_ms=duration_ms,
                    success=True,
                    cache_hit=True,
                )

                return cached_result

            # Check rate limit
            self._check_rate_limit()

            # Execute with retry logic
            result = self._execute_with_retry()

            # Save to cache if enabled
            self._save_to_cache(result)

            # Log success
            self._log_success(result)

            # Record success event
            if self._enable_analytics:
                self._record_event(EventType.TOOL_SUCCESS, success=True)

            # Record performance metric for successful execution
            duration_ms = (time.time() - self._start_time) * 1000
            record_performance_metric(
                tool_name=self.tool_name,
                duration_ms=duration_ms,
                success=True,
                cache_hit=False,
            )

            return result

        except ToolError as e:
            # Known tool error - handle gracefully
            error_type = e.error_code
            self._log_error(e)

            if self._enable_analytics:
                self._record_event(
                    EventType.TOOL_ERROR,
                    success=False,
                    error_code=e.error_code,
                    error_message=str(e),
                )

            # Record performance metric for known error
            duration_ms = (time.time() - self._start_time) * 1000
            record_performance_metric(
                tool_name=self.tool_name,
                duration_ms=duration_ms,
                success=False,
                error_type=error_type,
            )

            return self._format_error_response(e)

        except Exception as e:
            # Unexpected error
            error_type = "UNEXPECTED_ERROR"
            self._log_error(e)

            if self._enable_analytics:
                self._record_event(
                    EventType.TOOL_ERROR,
                    success=False,
                    error_code="UNEXPECTED_ERROR",
                    error_message=str(e),
                )

            # Record performance metric for unexpected error
            duration_ms = (time.time() - self._start_time) * 1000
            record_performance_metric(
                tool_name=self.tool_name,
                duration_ms=duration_ms,
                success=False,
                error_type=error_type,
            )

            # Wrap in ToolError
            tool_error = ToolError(
                message=f"Unexpected error: {str(e)}",
                tool_name=self.tool_name,
                error_code="UNEXPECTED_ERROR",
            )
            return self._format_error_response(tool_error)

    def _execute_with_retry(self) -> Any:
        """Execute tool with retry logic."""
        last_exception = None

        for attempt in range(self.max_retries):
            try:
                return self._execute()

            except ToolError as e:
                last_exception = e

                # Don't retry validation or auth errors
                if e.error_code in ["VALIDATION_ERROR", "AUTH_ERROR", "SECURITY_ERROR"]:
                    raise

                # Retry on rate limit or temporary errors
                if attempt < self.max_retries - 1:
                    retry_delay = self.retry_delay * (2**attempt)  # Exponential backoff
                    self._logger.warning(
                        f"Attempt {attempt + 1} failed: {e}. Retrying in {retry_delay}s..."
                    )
                    time.sleep(retry_delay)
                else:
                    raise

        # All retries exhausted
        if last_exception:
            raise last_exception

    def _check_rate_limit(self) -> None:
        """Check rate limit for this tool."""
        # Skip rate limiting in mock mode
        if os.getenv("USE_MOCK_APIS", "false").lower() == "true":
            return

        try:
            limiter = get_rate_limiter()
            key = f"{self.tool_name}:{self._user_id or 'anonymous'}"
            limiter.check_rate_limit(key, self.rate_limit_type, self.rate_limit_cost)
        except Exception as e:
            # Record rate limit event
            if self._enable_analytics:
                self._record_event(EventType.RATE_LIMIT)
            raise

    def _record_event(
        self,
        event_type: EventType,
        success: bool = True,
        error_code: Optional[str] = None,
        error_message: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Record analytics event."""
        duration_ms = None
        if self._start_time:
            duration_ms = (time.time() - self._start_time) * 1000

        event = AnalyticsEvent(
            event_type=event_type,
            tool_name=self.tool_name,
            duration_ms=duration_ms,
            success=success,
            error_code=error_code,
            error_message=error_message,
            metadata=metadata or {},
            user_id=self._user_id,
            request_id=self._request_id,
        )

        record_event(event)

    def _log_start(self) -> None:
        """Log tool execution start."""
        if self._enable_logging:
            self._logger.info(f"Starting {self.tool_name} [request_id={self._request_id}]")

    def _log_success(self, result: Any) -> None:
        """Log successful execution."""
        if not self._enable_logging:
            return

        duration_ms = (time.time() - self._start_time) * 1000 if self._start_time else 0
        result_preview = str(result)[:100] + "..." if len(str(result)) > 100 else str(result)

        self._logger.info(
            f"Completed {self.tool_name} in {duration_ms:.2f}ms "
            f"[request_id={self._request_id}] Result: {result_preview}"
        )

    def _log_error(self, error: Exception) -> None:
        """Log error."""
        if not self._enable_logging:
            return

        duration_ms = (time.time() - self._start_time) * 1000 if self._start_time else 0

        self._logger.error(
            f"Failed {self.tool_name} after {duration_ms:.2f}ms "
            f"[request_id={self._request_id}] Error: {str(error)}",
            exc_info=not isinstance(error, ToolError),  # Full traceback for unexpected errors
        )

    def _format_error_response(self, error: ToolError) -> Dict[str, Any]:
        """
        Format error response for agents.

        Args:
            error: ToolError instance

        Returns:
            Structured error dictionary
        """
        return {
            "success": False,
            "error": {
                "code": error.error_code,
                "message": error.message,
                "tool": self.tool_name,
                "retry_after": error.retry_after,
                "details": error.details,
                "request_id": self._request_id,
            },
        }

    def _get_metadata(self) -> Dict[str, Any]:
        """Get tool metadata for logging/analytics."""
        return {
            "tool_name": self.tool_name,
            "tool_category": self.tool_category,
            "request_id": self._request_id,
            "user_id": self._user_id,
        }

    def _should_use_mock(self) -> bool:
        """Check if mock mode is enabled via environment variable."""
        return os.getenv("USE_MOCK_APIS", "false").lower() == "true"

    def _init_cache(self) -> None:
        """Initialize cache manager based on environment configuration."""
        if not self.enable_cache:
            return

        # Check if caching is disabled globally
        cache_backend = os.getenv("CACHE_BACKEND", "memory").lower()
        if cache_backend == "none":
            return

        # Use global cache manager (singleton pattern)
        try:
            self._cache_manager = get_global_cache_manager()

            if self._enable_logging:
                backend_type = type(self._cache_manager.backend).__name__
                self._logger.debug(
                    f"Cache initialized for {self.tool_name} with {backend_type} backend"
                )
        except Exception as e:
            if self._enable_logging:
                self._logger.warning(f"Failed to initialize cache: {e}. Caching disabled.")
            self._cache_manager = None

    def _get_cache_key(self) -> str:
        """
        Generate cache key for current tool execution.

        Returns:
            Cache key string based on tool name and parameters
        """
        # Get parameters to include in cache key
        if self.cache_key_params:
            params = {k: getattr(self, k, None) for k in self.cache_key_params}
        else:
            # Use all non-private attributes
            params = {
                k: v
                for k, v in self.__dict__.items()
                if not k.startswith("_")
                and k not in ["enable_cache", "cache_ttl", "cache_key_params"]
            }

        # Create cache key
        return make_cache_key(self.tool_name, str(sorted(params.items())), prefix="agentswarm")

    def _get_from_cache(self) -> Optional[Any]:
        """
        Try to retrieve result from cache.

        Returns:
            Cached result or None if not found or cache disabled
        """
        if not self.enable_cache or not self._cache_manager:
            return None

        try:
            cache_key = self._get_cache_key()
            result = self._cache_manager.get(cache_key)

            if result is not None and self._enable_logging:
                self._logger.info(f"Cache HIT for {self.tool_name} [request_id={self._request_id}]")

            return result
        except Exception as e:
            if self._enable_logging:
                self._logger.warning(f"Cache read error: {e}")
            return None

    def _save_to_cache(self, result: Any) -> None:
        """
        Save result to cache.

        Args:
            result: The result to cache
        """
        if not self.enable_cache or not self._cache_manager:
            return

        try:
            cache_key = self._get_cache_key()
            self._cache_manager.set(cache_key, result, ttl=self.cache_ttl)

            if self._enable_logging:
                self._logger.debug(f"Cached result for {self.tool_name} with TTL={self.cache_ttl}s")
        except Exception as e:
            if self._enable_logging:
                self._logger.warning(f"Cache write error: {e}")


class SimpleBaseTool(BaseTool):
    """
    Simplified base tool for tools that don't need retry logic or complex error handling.

    Use this for simple, fast tools like utilities.
    """

    max_retries: int = 1  # No retries
    _enable_analytics: bool = False  # Disable analytics for simple tools


# Utility function for quick tool creation


def create_simple_tool(name: str, execute_func, description: str = ""):
    """
    Create a simple tool from a function.

    Args:
        name: Tool name
        execute_func: Function to execute
        description: Tool description

    Returns:
        Tool class

    Example:
        ```python
        def my_function(input: str) -> str:
            return input.upper()

        MyTool = create_simple_tool("my_tool", my_function, "Converts to uppercase")
        tool = MyTool(input="hello")
        result = tool.run()  # "HELLO"
        ```
    """

    class DynamicTool(SimpleBaseTool):
        __doc__ = description or f"Dynamic tool: {name}"
        tool_name = name

        def _execute(self):
            return execute_func(self)

    return DynamicTool
