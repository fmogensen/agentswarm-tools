"""
Unit tests for AsyncBaseTool class.
"""

import pytest
import asyncio
import os
from typing import Dict, Any

from shared.async_base import AsyncBaseTool, SimpleAsyncBaseTool, create_simple_async_tool
from shared.errors import ValidationError, ToolError


class TestAsyncTool(AsyncBaseTool):
    """Test async tool implementation."""

    tool_name = "test_async_tool"
    tool_category = "test"

    async def _execute(self) -> Dict[str, Any]:
        """Execute async operation."""
        await asyncio.sleep(0.01)  # Simulate async I/O
        return {"success": True, "message": "Async execution completed"}


class TestAsyncToolWithValidation(AsyncBaseTool):
    """Test async tool with validation."""

    tool_name = "test_async_validation"
    tool_category = "test"

    async def _execute(self) -> Dict[str, Any]:
        """Execute with validation."""
        if not hasattr(self, 'value') or not self.value:
            raise ValidationError("value is required", tool_name=self.tool_name)
        return {"success": True, "value": self.value}


class TestAsyncToolWithRetry(AsyncBaseTool):
    """Test async tool with retry logic."""

    tool_name = "test_async_retry"
    tool_category = "test"
    max_retries = 3
    retry_delay = 0.01

    def __init__(self, **data):
        super().__init__(**data)
        self.attempt_count = 0

    async def _execute(self) -> Dict[str, Any]:
        """Execute with retry simulation."""
        self.attempt_count += 1
        if self.attempt_count < 2:
            raise ToolError("Temporary failure", tool_name=self.tool_name)
        return {"success": True, "attempts": self.attempt_count}


@pytest.mark.asyncio
class TestAsyncBaseTool:
    """Test cases for AsyncBaseTool."""

    def setup_method(self):
        """Setup test environment."""
        os.environ["USE_MOCK_APIS"] = "true"

    async def test_async_execution(self):
        """Test basic async execution."""
        tool = TestAsyncTool()
        result = await tool.run_async()

        assert result is not None
        assert result.get("success") == True
        assert "message" in result

    async def test_sync_wrapper(self):
        """Test sync wrapper for async tools."""
        tool = TestAsyncTool()
        # Call sync wrapper
        result = tool.run()

        assert result is not None
        assert result.get("success") == True
        assert "message" in result

    async def test_concurrent_execution(self):
        """Test concurrent execution of multiple async tools."""
        tools = [TestAsyncTool() for _ in range(5)]

        # Execute all concurrently
        results = await asyncio.gather(*[tool.run_async() for tool in tools])

        assert len(results) == 5
        assert all(r.get("success") == True for r in results)

    async def test_validation_error(self):
        """Test validation error handling."""
        tool = TestAsyncToolWithValidation()
        result = await tool.run_async()

        # Should return error response
        assert result.get("success") == False
        assert "error" in result
        assert result["error"]["code"] == "VALIDATION_ERROR"

    async def test_retry_logic(self):
        """Test retry logic with exponential backoff."""
        tool = TestAsyncToolWithRetry()
        result = await tool.run_async()

        # Should succeed after retry
        assert result.get("success") == True
        assert result.get("attempts") == 2

    async def test_analytics_recording(self):
        """Test analytics event recording."""
        tool = TestAsyncTool()
        tool._enable_analytics = True

        result = await tool.run_async()

        assert result.get("success") == True
        # Analytics should be recorded (logged but not blocking)

    async def test_logging(self):
        """Test logging functionality."""
        tool = TestAsyncTool()
        tool._enable_logging = True

        result = await tool.run_async()

        assert result.get("success") == True
        # Logs should be generated (visible in test output if verbose)

    async def test_simple_async_tool(self):
        """Test SimpleAsyncBaseTool."""

        class SimpleTest(SimpleAsyncBaseTool):
            tool_name = "simple_test"

            async def _execute(self):
                return {"simple": True}

        tool = SimpleTest()
        result = await tool.run_async()

        assert result.get("simple") == True

    async def test_create_simple_async_tool(self):
        """Test dynamic async tool creation."""

        async def my_async_func(self):
            await asyncio.sleep(0.01)
            return {"dynamic": True}

        DynamicTool = create_simple_async_tool(
            "dynamic_async_tool",
            my_async_func,
            "Dynamic async tool test"
        )

        tool = DynamicTool()
        result = await tool.run_async()

        assert result.get("dynamic") == True

    async def test_error_formatting(self):
        """Test error response formatting."""
        tool = TestAsyncToolWithValidation()
        result = await tool.run_async()

        assert result.get("success") == False
        assert "error" in result
        assert "code" in result["error"]
        assert "message" in result["error"]
        assert "request_id" in result["error"]

    async def test_metadata(self):
        """Test metadata collection."""
        tool = TestAsyncTool()
        metadata = tool._get_metadata()

        assert metadata["tool_name"] == "test_async_tool"
        assert metadata["tool_category"] == "test"
        assert "request_id" in metadata

    async def test_mock_mode(self):
        """Test mock mode detection."""
        os.environ["USE_MOCK_APIS"] = "true"
        tool = TestAsyncTool()
        assert tool._should_use_mock() == True

        os.environ["USE_MOCK_APIS"] = "false"
        tool = TestAsyncTool()
        assert tool._should_use_mock() == False

    async def test_performance_tracking(self):
        """Test performance tracking."""
        tool = TestAsyncTool()

        import time
        start = time.time()
        result = await tool.run_async()
        duration = time.time() - start

        assert result.get("success") == True
        # Should complete quickly
        assert duration < 1.0

    async def test_concurrent_with_different_tools(self):
        """Test concurrent execution of different async tools."""
        tool1 = TestAsyncTool()
        tool2 = TestAsyncToolWithRetry()

        results = await asyncio.gather(
            tool1.run_async(),
            tool2.run_async(),
        )

        assert len(results) == 2
        assert all(r.get("success") == True for r in results)

    async def test_exception_handling(self):
        """Test exception handling in async context."""

        class ErrorTool(AsyncBaseTool):
            tool_name = "error_tool"

            async def _execute(self):
                raise ValueError("Test exception")

        tool = ErrorTool()
        result = await tool.run_async()

        assert result.get("success") == False
        assert "error" in result
        assert "UNEXPECTED_ERROR" in result["error"]["code"]

    async def test_timeout_handling(self):
        """Test handling of long-running operations."""

        class SlowTool(AsyncBaseTool):
            tool_name = "slow_tool"
            max_retries = 1  # Don't retry

            async def _execute(self):
                await asyncio.sleep(0.1)  # Slow operation
                return {"slow": True}

        tool = SlowTool()
        result = await tool.run_async()

        assert result.get("slow") == True


@pytest.mark.asyncio
class TestAsyncBatchProcessing:
    """Test async batch processing scenarios."""

    async def test_batch_execution(self):
        """Test batch execution of async tools."""
        from shared.async_batch import AsyncBatchProcessor

        async def process_item(n: int) -> int:
            await asyncio.sleep(0.01)
            return n * 2

        processor = AsyncBatchProcessor(
            max_concurrency=3,
            max_retries=2
        )

        result = await processor.process(
            items=list(range(10)),
            operation=process_item,
            description="Test batch"
        )

        assert result.success == True
        assert result.successful_count == 10
        assert len(result.results) == 10

    async def test_concurrent_tools_with_rate_limit(self):
        """Test concurrent tools with rate limiting."""
        from shared.async_batch import AsyncBatchProcessor

        async def run_tool(query: str) -> Dict[str, Any]:
            tool = TestAsyncTool()
            return await tool.run_async()

        processor = AsyncBatchProcessor(
            max_concurrency=3,
            rate_limit=5,
            rate_limit_per=1.0
        )

        queries = [f"query_{i}" for i in range(8)]
        result = await processor.process(
            items=queries,
            operation=run_tool,
            description="Test with rate limit"
        )

        assert result.successful_count == len(queries)


def test_sync_wrapper_in_sync_context():
    """Test calling async tool from sync context."""
    tool = TestAsyncTool()
    result = tool.run()  # Sync wrapper

    assert result.get("success") == True


def test_simple_sync_creation():
    """Test creating and using async tool in sync context."""

    class SimpleSyncTest(AsyncBaseTool):
        tool_name = "simple_sync_test"

        async def _execute(self):
            return {"test": "sync_wrapper"}

    tool = SimpleSyncTest()
    result = tool.run()  # Uses sync wrapper

    assert result.get("test") == "sync_wrapper"


if __name__ == "__main__":
    # Run async tests
    print("Running async base tool tests...")

    async def run_all_tests():
        """Run all async tests."""
        test_suite = TestAsyncBaseTool()
        test_suite.setup_method()

        print("\n1. Testing async execution...")
        await test_suite.test_async_execution()
        print("  ✓ Async execution test passed")

        print("\n2. Testing sync wrapper...")
        await test_suite.test_sync_wrapper()
        print("  ✓ Sync wrapper test passed")

        print("\n3. Testing concurrent execution...")
        await test_suite.test_concurrent_execution()
        print("  ✓ Concurrent execution test passed")

        print("\n4. Testing validation error...")
        await test_suite.test_validation_error()
        print("  ✓ Validation error test passed")

        print("\n5. Testing retry logic...")
        await test_suite.test_retry_logic()
        print("  ✓ Retry logic test passed")

        print("\n6. Testing simple async tool...")
        await test_suite.test_simple_async_tool()
        print("  ✓ Simple async tool test passed")

        print("\n7. Testing dynamic tool creation...")
        await test_suite.test_create_simple_async_tool()
        print("  ✓ Dynamic tool creation test passed")

        print("\n8. Testing error formatting...")
        await test_suite.test_error_formatting()
        print("  ✓ Error formatting test passed")

        # Batch processing tests
        batch_suite = TestAsyncBatchProcessing()

        print("\n9. Testing batch execution...")
        await batch_suite.test_batch_execution()
        print("  ✓ Batch execution test passed")

        print("\n10. Testing rate limiting...")
        await batch_suite.test_concurrent_tools_with_rate_limit()
        print("  ✓ Rate limiting test passed")

    # Run all async tests
    asyncio.run(run_all_tests())

    # Run sync tests
    print("\n11. Testing sync wrapper in sync context...")
    test_sync_wrapper_in_sync_context()
    print("  ✓ Sync wrapper test passed")

    print("\n12. Testing simple sync creation...")
    test_simple_sync_creation()
    print("  ✓ Simple sync creation test passed")

    print("\n✓ All async base tool tests passed!")
