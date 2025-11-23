"""
Async version of web search - perform web searches with Google using non-blocking I/O
"""

import os
from typing import Any, Dict, List

from pydantic import Field

try:
    import httpx
except ImportError:
    httpx = None

from shared.async_base import AsyncBaseTool
from shared.errors import APIError, ValidationError
from shared.logging import get_logger

logger = get_logger(__name__)


class AsyncWebSearch(AsyncBaseTool):
    """
    Async web search with Google - non-blocking I/O for better concurrency

    This async version allows multiple searches to run concurrently without blocking.
    Use this when you need to perform many searches in parallel or in async contexts.

    Args:
        query: Search query string
        max_results: Maximum number of results to return

    Returns:
        Dict containing:
        - success: Boolean indicating success
        - result: List of search results
        - metadata: Additional information

    Example (async):
        >>> import asyncio
        >>> async def search():
        ...     tool = AsyncWebSearch(query="example", max_results=5)
        ...     result = await tool.run_async()
        ...     return result
        >>> asyncio.run(search())

    Example (sync wrapper):
        >>> tool = AsyncWebSearch(query="example", max_results=5)
        >>> result = tool.run()  # Automatically handles async execution
    """

    # Tool metadata
    tool_name: str = "async_web_search"
    tool_category: str = "data"

    # Parameters
    query: str = Field(..., description="Search query string", min_length=1)
    max_results: int = Field(10, description="Maximum number of results to return", ge=1, le=100)

    async def _execute(self) -> Dict[str, Any]:
        """
        Execute the async web search.

        Returns:
            Dict with results
        """
        # 1. VALIDATE
        self._validate_parameters()

        # 2. CHECK MOCK MODE
        if self._should_use_mock():
            return self._generate_mock_results()

        # 3. EXECUTE (async)
        try:
            result = await self._process()

            return {
                "success": True,
                "result": result,
                "metadata": {"tool_name": self.tool_name, "async": True},
            }
        except Exception as e:
            raise APIError(f"Failed: {e}", tool_name=self.tool_name)

    def _validate_parameters(self) -> None:
        """Validate input parameters."""
        if not self.query.strip():
            raise ValidationError("Query cannot be empty", tool_name=self.tool_name)

    def _should_use_mock(self) -> bool:
        """Check if mock mode enabled."""
        return os.getenv("USE_MOCK_APIS", "false").lower() == "true"

    def _generate_mock_results(self) -> Dict[str, Any]:
        """Generate mock results for testing."""
        mock_results = [
            {
                "title": f"Mock Async Result {i}",
                "link": f"https://example.com/async-mock/{i}",
                "snippet": f"This is a mock async snippet for result {i}.",
            }
            for i in range(1, self.max_results + 1)
        ]

        return {
            "success": True,
            "result": mock_results,
            "metadata": {"mock_mode": True, "async": True},
        }

    async def _process(self) -> List[Dict[str, Any]]:
        """Main async processing logic."""
        if httpx is None:
            raise APIError(
                "httpx library is required for async web search. Install with: pip install httpx",
                tool_name=self.tool_name,
            )

        try:
            # Get API credentials from environment
            api_key = os.getenv("GOOGLE_SEARCH_API_KEY") or os.getenv("GOOGLE_SHOPPING_API_KEY")
            engine_id = os.getenv("GOOGLE_SEARCH_ENGINE_ID") or os.getenv(
                "GOOGLE_SHOPPING_ENGINE_ID"
            )

            if not api_key or not engine_id:
                raise APIError(
                    "Missing API credentials. Set GOOGLE_SEARCH_API_KEY and GOOGLE_SEARCH_ENGINE_ID",
                    tool_name=self.tool_name,
                )

            # Call Google Custom Search API (async)
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    "https://www.googleapis.com/customsearch/v1",
                    params={
                        "q": self.query,
                        "num": self.max_results,
                        "key": api_key,
                        "cx": engine_id,
                    },
                )
                response.raise_for_status()
                search_results = response.json().get("items", [])

            return [
                {
                    "title": item.get("title"),
                    "link": item.get("link"),
                    "snippet": item.get("snippet"),
                }
                for item in search_results
            ]

        except httpx.HTTPStatusError as e:
            raise APIError(
                f"API request failed with status {e.response.status_code}: {e}",
                tool_name=self.tool_name,
            )
        except httpx.RequestError as e:
            raise APIError(f"API request failed: {e}", tool_name=self.tool_name)


if __name__ == "__main__":
    # Test the async web_search tool
    print("Testing AsyncWebSearch tool...")

    import asyncio

    async def test_async():
        """Test async execution."""
        print("\n1. Testing async execution...")

        # Test with mock mode
        os.environ["USE_MOCK_APIS"] = "true"

        tool = AsyncWebSearch(query="Python async programming", max_results=3)
        result = await tool.run_async()

        print(f"  Success: {result.get('success')}")
        print(f"  Results: {len(result.get('result', []))} items")
        print(
            f"  First result: {result.get('result', [{}])[0] if result.get('result') else 'None'}"
        )
        assert result.get("success") == True
        assert len(result.get("result", [])) == 3
        print("  ✓ Async execution test passed")

    async def test_concurrent():
        """Test concurrent searches."""
        print("\n2. Testing concurrent searches...")

        os.environ["USE_MOCK_APIS"] = "true"

        # Create multiple search tasks
        searches = [AsyncWebSearch(query=f"Query {i}", max_results=2) for i in range(5)]

        # Execute concurrently
        import time

        start = time.time()
        results = await asyncio.gather(*[tool.run_async() for tool in searches])
        duration = time.time() - start

        print(f"  Completed {len(results)} searches in {duration:.3f}s")
        print(f"  All successful: {all(r.get('success') for r in results)}")
        assert all(r.get("success") for r in results)
        print("  ✓ Concurrent search test passed")

    def test_sync_wrapper():
        """Test sync wrapper."""
        logger.info("\n3. Testing sync wrapper...")

        os.environ["USE_MOCK_APIS"] = "true"

        tool = AsyncWebSearch(query="Sync wrapper test", max_results=2)
        result = tool.run()  # Sync wrapper

        logger.info(f"  Success: {result.get('success')}")
        logger.info(f"  Results: {len(result.get('result', []))} items")
        assert result.get("success") == True
        logger.info("  ✓ Sync wrapper test passed")

    async def test_batch_processing():
        """Test batch processing with rate limiting."""
        logger.info("\n4. Testing batch processing...")

        os.environ["USE_MOCK_APIS"] = "true"

        from shared.async_batch import AsyncBatchProcessor

        async def search_query(query: str) -> Dict[str, Any]:
            tool = AsyncWebSearch(query=query, max_results=2)
            return await tool.run_async()

        processor = AsyncBatchProcessor(max_concurrency=3, rate_limit=5, rate_limit_per=1.0)

        queries = [f"Search query {i}" for i in range(10)]
        batch_result = await processor.process(
            items=queries, operation=search_query, description="Batch web searches"
        )

        logger.info(f"  Successful: {batch_result.successful_count}/{len(queries)}")
        logger.info(f"  Duration: {batch_result.duration_ms:.2f}ms")
        assert batch_result.successful_count == len(queries)
        logger.info("  ✓ Batch processing test passed")

    # Run tests
    async def main():
        await test_async()
        await test_concurrent()
        test_sync_wrapper()
        await test_batch_processing()
        logger.info("\n✓ All AsyncWebSearch tests passed!")

    asyncio.run(main())
