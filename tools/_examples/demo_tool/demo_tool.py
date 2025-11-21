"""
Demo Tool - Reference Implementation

This is a complete example showing all best practices for AgentSwarm tool development.

Features demonstrated:
- Proper BaseTool inheritance
- Type hints on all parameters
- Google-style docstrings
- Error handling with shared.errors
- Parameter validation
- Structured return values
- Mock mode support for testing
"""

from typing import Any, Dict, List, Optional
from pydantic import Field
import os

from shared.base import BaseTool
from shared.errors import ValidationError, APIError


class DemoTool(BaseTool):
    """
    Demo tool for testing and reference.

    This tool demonstrates the complete pattern for AgentSwarm tool development.
    It processes a query and returns mock results, showcasing all best practices.

    Args:
        query: The search query to process (required)
        max_results: Maximum number of results to return (default: 10)
        filter_type: Optional filter to apply to results
        use_cache: Whether to use cached results if available

    Returns:
        Dict containing:
        - success: Boolean indicating success
        - results: List of result items
        - total_count: Total number of results
        - metadata: Additional information about the query

    Raises:
        ValidationError: If query is empty or invalid
        APIError: If external API call fails

    Example:
        >>> tool = DemoTool(query="test query", max_results=5)
        >>> result = tool.run()
        >>> print(result["total_count"])
        5
    """

    # ========== TOOL METADATA ==========
    tool_name: str = "demo_tool"
    tool_category: str = "examples"
    tool_description: str = "Demo tool showing complete implementation pattern"

    # ========== PARAMETERS ==========

    query: str = Field(
        ...,  # Required parameter
        description="Search query to process",
        min_length=1,
        max_length=500
    )

    max_results: int = Field(
        default=10,
        description="Maximum number of results to return",
        ge=1,  # Greater than or equal to 1
        le=100  # Less than or equal to 100
    )

    filter_type: Optional[str] = Field(
        default=None,
        description="Optional filter: 'recent', 'popular', or 'relevant'"
    )

    use_cache: bool = Field(
        default=True,
        description="Whether to use cached results if available"
    )

    # ========== IMPLEMENTATION ==========

    def _execute(self) -> Dict[str, Any]:
        """
        Execute the demo tool.

        This is the only method you need to implement when extending BaseTool.
        The run() method is already implemented in BaseTool and handles:
        - Analytics tracking
        - Rate limiting
        - Retry logic
        - Error formatting
        - Logging

        Returns:
            Dict with structured results

        Raises:
            ValidationError: For invalid parameters
            APIError: For external API failures
        """
        # 1. VALIDATE INPUTS
        self._validate_parameters()

        # 2. CHECK MOCK MODE
        if self._should_use_mock():
            return self._generate_mock_results()

        # 3. EXECUTE REAL LOGIC
        try:
            results = self._process_query()
            filtered_results = self._apply_filters(results)
            final_results = filtered_results[:self.max_results]

            # 4. RETURN STRUCTURED DATA
            return {
                "success": True,
                "results": final_results,
                "total_count": len(final_results),
                "metadata": {
                    "query": self.query,
                    "max_results": self.max_results,
                    "filter_type": self.filter_type,
                    "used_cache": self.use_cache,
                    "tool_version": "1.0.0"
                }
            }

        except Exception as e:
            # Wrap unexpected errors in APIError
            raise APIError(
                f"Failed to process query: {e}",
                tool_name=self.tool_name
            )

    def _validate_parameters(self) -> None:
        """
        Validate input parameters.

        Raises:
            ValidationError: If parameters are invalid
        """
        # Check query is not empty (Pydantic already handles this, but showing explicitly)
        if not self.query or not self.query.strip():
            raise ValidationError(
                "Query cannot be empty",
                tool_name=self.tool_name,
                details={"query": self.query}
            )

        # Check filter_type is valid
        valid_filters = ["recent", "popular", "relevant", None]
        if self.filter_type not in valid_filters:
            raise ValidationError(
                f"Invalid filter_type. Must be one of: {valid_filters}",
                tool_name=self.tool_name,
                details={"filter_type": self.filter_type}
            )

    def _should_use_mock(self) -> bool:
        """Check if mock mode is enabled."""
        return os.getenv("USE_MOCK_APIS", "false").lower() == "true"

    def _generate_mock_results(self) -> Dict[str, Any]:
        """
        Generate mock results for testing.

        This allows the tool to work without external APIs during development.
        """
        mock_results = [
            {
                "id": i,
                "title": f"Result {i}: {self.query}",
                "description": f"This is mock result {i} for query: {self.query}",
                "score": 1.0 - (i * 0.1),
                "source": "mock"
            }
            for i in range(1, min(self.max_results + 1, 11))
        ]

        return {
            "success": True,
            "results": mock_results,
            "total_count": len(mock_results),
            "metadata": {
                "query": self.query,
                "max_results": self.max_results,
                "filter_type": self.filter_type,
                "used_cache": False,
                "mock_mode": True,
                "tool_version": "1.0.0"
            }
        }

    def _process_query(self) -> List[Dict[str, Any]]:
        """
        Process the query and return results.

        In a real tool, this would call an external API.
        For demo purposes, returns sample data.
        """
        # Simulate API call
        # In real implementation:
        # response = requests.get(f"https://api.example.com/search?q={self.query}")
        # return response.json()["results"]

        return [
            {
                "id": i,
                "title": f"Real Result {i}",
                "description": f"Description for result {i}",
                "score": 0.95 - (i * 0.05),
                "source": "api"
            }
            for i in range(1, 21)  # Simulate 20 results from API
        ]

    def _apply_filters(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Apply filter_type to results.

        Args:
            results: Raw results to filter

        Returns:
            Filtered and sorted results
        """
        if not self.filter_type:
            return results

        if self.filter_type == "recent":
            # In real implementation, sort by date
            return sorted(results, key=lambda x: x["id"], reverse=True)

        elif self.filter_type == "popular":
            # In real implementation, sort by popularity metric
            return sorted(results, key=lambda x: x.get("score", 0), reverse=True)

        elif self.filter_type == "relevant":
            # In real implementation, use relevance scoring
            return sorted(results, key=lambda x: x.get("score", 0), reverse=True)

        return results


# ========== HELPER FUNCTION (Optional) ==========

def run_demo_tool(query: str, max_results: int = 10) -> Dict[str, Any]:
    """
    Convenience function to run demo tool.

    Args:
        query: Search query
        max_results: Maximum results to return

    Returns:
        Tool execution results
    """
    tool = DemoTool(query=query, max_results=max_results)
    return tool.run()


# ========== TEST BLOCK ==========

if __name__ == "__main__":
    # Test the demo_tool
    print("Testing DemoTool...")

    # Test with mock mode
    import os
    os.environ["USE_MOCK_APIS"] = "true"

    # Test 1: Basic usage
    print("\n--- Test 1: Basic usage ---")
    tool = DemoTool(query="machine learning", max_results=5)
    result = tool.run()
    print(f"Success: {result.get('success')}")
    print(f"Total results: {result.get('total_count')}")
    print(f"First result: {result.get('results', [{}])[0].get('title')}")

    # Test 2: With filter
    print("\n--- Test 2: With filter ---")
    tool2 = DemoTool(query="python", max_results=3, filter_type="popular")
    result2 = tool2.run()
    print(f"Success: {result2.get('success')}")
    print(f"Filter applied: {result2.get('metadata', {}).get('filter_type')}")

    # Test 3: Using convenience function
    print("\n--- Test 3: Convenience function ---")
    result3 = run_demo_tool("test query", max_results=2)
    print(f"Success: {result3.get('success')}")
    print(f"Results: {result3.get('total_count')}")
