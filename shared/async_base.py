"""
Async base tool class for AgentSwarm Tools Framework.
Provides async execution support for I/O-bound tools with non-blocking operations.

This class extends the sync BaseTool while maintaining 100% API compatibility.
"""

from typing import Any, Optional, Dict
from datetime import datetime
from abc import abstractmethod
import asyncio
import time
import logging
import uuid
import os

# Import from Agency Swarm
try:
    from agency_swarm.tools.base_tool import BaseTool as AgencyBaseTool
except ImportError:
    # Fallback for development/testing without agency-swarm installed
    from pydantic import BaseModel
    from abc import ABC

    class AgencyBaseTool(BaseModel, ABC):
        """Fallback BaseTool for development."""

        @abstractmethod
        def run(self):
            pass


from .errors import ToolError, ValidationError
from .analytics import record_event, AnalyticsEvent, EventType
from .security import get_rate_limiter


# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


class AsyncBaseTool(AgencyBaseTool):
    """
    Enhanced async base tool with built-in error handling, analytics, and security.

    All async tools should inherit from this class and implement the `_execute()` method.

    Features:
    - Automatic error handling and async retry logic
    - Analytics tracking (requests, performance, errors)
    - Rate limiting
    - Input validation
    - Structured logging
    - Request tracing
    - Non-blocking I/O operations

    Example:
        ```python
        from agentswarm_tools.shared.async_base import AsyncBaseTool
        from pydantic import Field
        import httpx

        class MyAsyncTool(AsyncBaseTool):
            '''Tool description for AI agents.'''

            param1: str = Field(..., description="Parameter description")

            # Tool configuration
            tool_name = "my_async_tool"
            tool_category = "custom"
            rate_limit_type = "default"

            async def _execute(self) -> Any:
                '''Implement your async tool logic here.'''
                async with httpx.AsyncClient() as client:
                    response = await client.get("https://api.example.com")
                    result = response.json()
                return result

        # Usage
        import asyncio
        async def main():
            tool = MyAsyncTool(param1="test")
            result = await tool.run_async()
            print(result)

        asyncio.run(main())
        ```
    """

    # Tool metadata (override in subclasses)
    tool_name: str = "async_base_tool"
    tool_category: str = "general"
    rate_limit_type: str = "default"
    rate_limit_cost: int = 1

    # Retry configuration
    max_retries: int = 3
    retry_delay: float = 1.0  # seconds

    # Analytics
    _enable_analytics: bool = True
    _enable_logging: bool = True

    def __init__(self, **data):
        """Initialize tool with request tracking."""
        super().__init__(**data)
        self._request_id = str(uuid.uuid4())
        self._user_id: Optional[str] = data.get("user_id")
        self._logger = logging.getLogger(f"agentswarm.tools.async.{self.tool_name}")
        self._start_time: Optional[float] = None

    @abstractmethod
    async def _execute(self) -> Any:
        """
        Execute the async tool logic.

        This method must be implemented by all subclasses.

        Returns:
            Tool output (can be any type: str, dict, list, etc.)

        Raises:
            ToolError: On execution failure
        """
        raise NotImplementedError("Async tool must implement _execute() method")

    async def run_async(self) -> Any:
        """
        Run the async tool with error handling, analytics, and rate limiting.

        This method should be called when using the tool in async context.

        Returns:
            Tool output or error message

        Note:
            This method wraps _execute() with all the framework features.
        """
        self._start_time = time.time()

        try:
            # Log start
            self._log_start()

            # Record start event
            if self._enable_analytics:
                self._record_event(EventType.TOOL_START)

            # Check rate limit (sync operation, but fast)
            self._check_rate_limit()

            # Execute with async retry logic
            result = await self._execute_with_retry()

            # Log success
            self._log_success(result)

            # Record success event
            if self._enable_analytics:
                self._record_event(EventType.TOOL_SUCCESS, success=True)

            return result

        except ToolError as e:
            # Known tool error - handle gracefully
            self._log_error(e)

            if self._enable_analytics:
                self._record_event(
                    EventType.TOOL_ERROR,
                    success=False,
                    error_code=e.error_code,
                    error_message=str(e),
                )

            return self._format_error_response(e)

        except Exception as e:
            # Unexpected error
            self._log_error(e)

            if self._enable_analytics:
                self._record_event(
                    EventType.TOOL_ERROR,
                    success=False,
                    error_code="UNEXPECTED_ERROR",
                    error_message=str(e),
                )

            # Wrap in ToolError
            tool_error = ToolError(
                message=f"Unexpected error: {str(e)}",
                tool_name=self.tool_name,
                error_code="UNEXPECTED_ERROR",
            )
            return self._format_error_response(tool_error)

    def run(self) -> Any:
        """
        Synchronous wrapper for async execution.

        This allows async tools to be called from sync contexts (e.g., Agency Swarm).
        Creates a new event loop if needed.

        Returns:
            Tool output or error message
        """
        try:
            # Try to get current event loop
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If loop is already running, create a new task
                # This shouldn't happen in normal Agency Swarm usage
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, self.run_async())
                    return future.result()
            else:
                return loop.run_until_complete(self.run_async())
        except RuntimeError:
            # No event loop exists, create one
            return asyncio.run(self.run_async())

    async def _execute_with_retry(self) -> Any:
        """Execute tool with async retry logic."""
        last_exception = None

        for attempt in range(self.max_retries):
            try:
                return await self._execute()

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
                    await asyncio.sleep(retry_delay)
                else:
                    raise

        # All retries exhausted
        if last_exception:
            raise last_exception

    def _check_rate_limit(self) -> None:
        """Check rate limit for this tool (sync operation)."""
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
            self._logger.info(f"Starting async {self.tool_name} [request_id={self._request_id}]")

    def _log_success(self, result: Any) -> None:
        """Log successful execution."""
        if not self._enable_logging:
            return

        duration_ms = (time.time() - self._start_time) * 1000 if self._start_time else 0
        result_preview = str(result)[:100] + "..." if len(str(result)) > 100 else str(result)

        self._logger.info(
            f"Completed async {self.tool_name} in {duration_ms:.2f}ms "
            f"[request_id={self._request_id}] Result: {result_preview}"
        )

    def _log_error(self, error: Exception) -> None:
        """Log error."""
        if not self._enable_logging:
            return

        duration_ms = (time.time() - self._start_time) * 1000 if self._start_time else 0

        self._logger.error(
            f"Failed async {self.tool_name} after {duration_ms:.2f}ms "
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


class SimpleAsyncBaseTool(AsyncBaseTool):
    """
    Simplified async base tool for tools that don't need retry logic or complex error handling.

    Use this for simple, fast async tools like utilities.
    """

    max_retries: int = 1  # No retries
    _enable_analytics: bool = False  # Disable analytics for simple tools


# Utility function for quick async tool creation


def create_simple_async_tool(name: str, execute_func, description: str = ""):
    """
    Create a simple async tool from an async function.

    Args:
        name: Tool name
        execute_func: Async function to execute
        description: Tool description

    Returns:
        Async tool class

    Example:
        ```python
        async def my_async_function(input: str) -> str:
            await asyncio.sleep(0.1)
            return input.upper()

        MyAsyncTool = create_simple_async_tool("my_async_tool", my_async_function, "Converts to uppercase")

        async def main():
            tool = MyAsyncTool(input="hello")
            result = await tool.run_async()  # "HELLO"

        asyncio.run(main())
        ```
    """

    class DynamicAsyncTool(SimpleAsyncBaseTool):
        __doc__ = description or f"Dynamic async tool: {name}"
        tool_name = name

        async def _execute(self):
            return await execute_func(self)

    return DynamicAsyncTool


if __name__ == "__main__":
    # Test the async base tool
    print("Testing AsyncBaseTool...")

    import asyncio

    class TestAsyncTool(AsyncBaseTool):
        """Test async tool."""

        tool_name = "test_async_tool"
        tool_category = "test"

        async def _execute(self) -> Dict[str, Any]:
            """Simulate async operation."""
            await asyncio.sleep(0.1)
            return {"success": True, "message": "Async execution completed"}

    async def test_async():
        """Test async execution."""
        os.environ["USE_MOCK_APIS"] = "true"

        tool = TestAsyncTool()
        result = await tool.run_async()

        print(f"Async test - Success: {result.get('success')}")
        print(f"Message: {result.get('message')}")
        assert result.get("success") == True
        print("Async test passed!")

    def test_sync():
        """Test sync wrapper."""
        os.environ["USE_MOCK_APIS"] = "true"

        tool = TestAsyncTool()
        result = tool.run()  # Sync wrapper

        print(f"Sync wrapper test - Success: {result.get('success')}")
        print(f"Message: {result.get('message')}")
        assert result.get("success") == True
        print("Sync wrapper test passed!")

    # Run async test
    asyncio.run(test_async())

    # Run sync wrapper test
    test_sync()

    print("\nAll AsyncBaseTool tests passed!")
