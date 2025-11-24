"""
Perform multiple web searches in parallel for maximum efficiency
"""

import os
from typing import Any, Dict, List

from pydantic import Field

from shared.base import BaseTool
from shared.batch import DefaultProgressCallback, parallel_process
from shared.errors import APIError, ValidationError


class BatchWebSearch(BaseTool):
    """
    Perform multiple web searches in parallel for maximum efficiency.

    This tool enables efficient batch processing of multiple search queries,
    processing them in parallel for 3-5x performance improvement over sequential searches.

    Args:
        queries: List of search queries to process
        max_results_per_query: Maximum results to return for each query
        max_workers: Number of parallel workers (default: 10)
        show_progress: Whether to show progress information

    Returns:
        Dict containing:
        - success: Boolean indicating success
        - results: List of search results for each query
        - metadata: Processing statistics

    Example:
        >>> tool = BatchWebSearch(
        ...     queries=["Python tutorial", "Machine learning basics", "Data science tools"],
        ...     max_results_per_query=5,
        ...     max_workers=10
        ... )
        >>> result = tool.run()
        >>> print(f"Processed {len(result['result']['results'])} queries")
    """

    # Tool metadata
    tool_name: str = "batch_web_search"
    tool_category: str = "data"

    # Parameters
    queries: List[str] = Field(
        ..., description="List of search queries to process", min_length=1, max_length=100
    )
    max_results_per_query: int = Field(
        10, description="Maximum number of results per query", ge=1, le=100
    )
    max_workers: int = Field(10, description="Maximum number of parallel workers", ge=1, le=50)
    show_progress: bool = Field(True, description="Whether to show progress information")

    def _execute(self) -> Dict[str, Any]:
        """
        Execute batch web search.

        Returns:
            Dict with results for all queries
        """

        self._logger.info(f"Executing {self.tool_name} with queries={self.queries}, max_results_per_query={self.max_results_per_query}, max_workers={self.max_workers}, show_progress={self.show_progress}")
        # 1. VALIDATE
        self._logger.debug(f"Validating parameters for {self.tool_name}")
        self._validate_parameters()

        # 2. CHECK MOCK MODE
        if self._should_use_mock():
            self._logger.info("Using mock mode for testing")
            return self._generate_mock_results()

        # 3. EXECUTE
        try:
            result = self._process()

            self._logger.info(f"Successfully completed {self.tool_name}")

            return {
                "success": True,
                "result": result,
                "metadata": {
                    "tool_name": self.tool_name,
                    "total_queries": len(self.queries),
                    "max_workers": self.max_workers,
                },
            }
        except Exception as e:
            self._logger.error(f"Error in {self.tool_name}: {str(e)}", exc_info=True)
            raise APIError(f"Batch web search failed: {e}", tool_name=self.tool_name)

    def _validate_parameters(self) -> None:
        """Validate input parameters."""
        if not self.queries or len(self.queries) == 0:
            raise ValidationError("queries cannot be empty", tool_name=self.tool_name)

        for idx, query in enumerate(self.queries):
            if not query or not query.strip():
                raise ValidationError(
                    f"Query at index {idx} is empty",
                    tool_name=self.tool_name,
                    details={"index": idx},
                )

    def _should_use_mock(self) -> bool:
        """Check if mock mode enabled."""
        return os.getenv("USE_MOCK_APIS", "false").lower() == "true"

    def _generate_mock_results(self) -> Dict[str, Any]:
        """Generate mock results for testing."""
        mock_results = []

        for query in self.queries:
            mock_results.append(
                {
                    "query": query,
                    "results": [
                        {
                            "title": f"Mock Result {i} for '{query}'",
                            "link": f"https://example.com/mock/{i}",
                            "snippet": f"This is a mock snippet for {query}.",
                        }
                        for i in range(1, min(4, self.max_results_per_query + 1))
                    ],
                    "result_count": min(3, self.max_results_per_query),
                }
            )

        return {
            "results": mock_results,
            "total_queries": len(self.queries),
            "total_results": len(mock_results),
            "successful_queries": len(mock_results),
            "failed_queries": 0,
            "mock": True,
        }

    def _process(self) -> Dict[str, Any]:
        """Process all queries in parallel."""
        progress_callback = (
            DefaultProgressCallback(verbose=self.show_progress)
            if self.show_progress
            else DefaultProgressCallback(verbose=False)
        )

        # Process queries in parallel
        batch_result = parallel_process(
            items=self.queries,
            processor=self._search_single_query,
            max_workers=self.max_workers,
            progress_callback=progress_callback,
            continue_on_error=True,
        )

        return {
            "results": batch_result.successes,
            "total_queries": len(self.queries),
            "total_results": len(batch_result.successes),
            "successful_queries": batch_result.successful_count,
            "failed_queries": batch_result.failed_count,
            "failures": batch_result.failures if batch_result.failed_count > 0 else [],
            "processing_time_ms": batch_result.processing_time_ms,
            "success_rate": batch_result.success_rate,
        }

    def _search_single_query(self, query: str) -> Dict[str, Any]:
        """
        Search a single query using WebSearch tool.

        Args:
            query: Search query string

        Returns:
            Dict with query and results

        Raises:
            APIError: If search fails
        """
        try:
            # Import WebSearch here to avoid circular imports and dependency issues
            import os
            import sys

            parent_dir = os.path.dirname(os.path.dirname(__file__))
            if parent_dir not in sys.path:
                sys.path.insert(0, parent_dir)

            from web_search.web_search import WebSearch

            # Use the WebSearch tool
            search_tool = WebSearch(query=query, max_results=self.max_results_per_query)
            result = search_tool.run()

            if not result.get("success", False):
                raise APIError(
                    f"Search failed for query: {query}",
                    tool_name=self.tool_name,
                )

            return {
                "query": query,
                "results": result.get("result", []),
                "result_count": len(result.get("result", [])),
            }

        except Exception as e:
            self._logger.error(f"Error in {self.tool_name}: {str(e)}", exc_info=True)
            raise APIError(
                f"Failed to search query '{query}': {e}",
                tool_name=self.tool_name,
            )


if __name__ == "__main__":
    # Test the batch_web_search tool
    print("Testing BatchWebSearch tool...")

    # Test with mock mode
    import os

    os.environ["USE_MOCK_APIS"] = "true"

    tool = BatchWebSearch(
        queries=[
            "Python programming",
            "Machine learning basics",
            "Data science tools",
            "AI development",
            "Cloud computing",
        ],
        max_results_per_query=3,
        max_workers=5,
        show_progress=True,
    )
    result = tool.run()

    print(f"\nSuccess: {result.get('success')}")
    print(f"Total queries: {result.get('result', {}).get('total_queries')}")
    print(f"Successful queries: {result.get('result', {}).get('successful_queries')}")
    print(f"Processing time: {result.get('result', {}).get('processing_time_ms', 0):.2f}ms")
    print(f"Success rate: {result.get('result', {}).get('success_rate', 0):.1f}%")

    assert result.get("success") == True
    assert result.get("result", {}).get("successful_queries") == 5
    print("\n✓ BatchWebSearch test passed!")
