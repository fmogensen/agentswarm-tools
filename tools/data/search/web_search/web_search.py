"""
Perform web search with Google and return comprehensive results
"""

from typing import Any, Dict, List
from pydantic import Field
import os
import requests

from shared.base import BaseTool
from shared.errors import ValidationError, APIError


class WebSearch(BaseTool):
    """
    Perform web search with Google and return comprehensive results

    Args:
        query: Search query string
        max_results: Maximum number of results to return

    Returns:
        Dict containing:
        - success: Boolean indicating success
        - result: Tool-specific results
        - metadata: Additional information

    Example:
        >>> tool = WebSearch(query="example", max_results=5)
        >>> result = tool.run()
    """

    # Tool metadata
    tool_name: str = "web_search"
    tool_category: str = "data"

    # Parameters
    query: str = Field(..., description="Search query string", min_length=1)
    max_results: int = Field(
        10, description="Maximum number of results to return", ge=1, le=100
    )

    def _execute(self) -> Dict[str, Any]:
        """
        Execute the web_search tool.

        Returns:
            Dict with results
        """
        # 1. VALIDATE
        self._validate_parameters()

        # 2. CHECK MOCK MODE
        if self._should_use_mock():
            return self._generate_mock_results()

        # 3. EXECUTE
        try:
            result = self._process()

            return {
                "success": True,
                "result": result,
                "metadata": {"tool_name": self.tool_name},
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
                "title": f"Mock Result {i}",
                "link": f"https://example.com/mock/{i}",
                "snippet": f"This is a mock snippet for result {i}.",
            }
            for i in range(1, self.max_results + 1)
        ]

        return {
            "success": True,
            "result": mock_results,
            "metadata": {"mock_mode": True},
        }

    def _process(self) -> List[Dict[str, Any]]:
        """Main processing logic."""
        try:
            # Get API credentials from environment
            api_key = os.getenv("GOOGLE_SEARCH_API_KEY") or os.getenv("GOOGLE_SHOPPING_API_KEY")
            engine_id = os.getenv("GOOGLE_SEARCH_ENGINE_ID") or os.getenv("GOOGLE_SHOPPING_ENGINE_ID")

            if not api_key or not engine_id:
                raise APIError(
                    "Missing API credentials. Set GOOGLE_SEARCH_API_KEY and GOOGLE_SEARCH_ENGINE_ID",
                    tool_name=self.tool_name
                )

            # Call Google Custom Search API
            response = requests.get(
                "https://www.googleapis.com/customsearch/v1",
                params={
                    "q": self.query,
                    "num": self.max_results,
                    "key": api_key,
                    "cx": engine_id,
                },
                timeout=30,
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

        except requests.RequestException as e:
            raise APIError(f"API request failed: {e}", tool_name=self.tool_name)


if __name__ == "__main__":
    # Test the web_search tool
    print("Testing WebSearch tool...")

    # Test with mock mode
    import os
    os.environ["USE_MOCK_APIS"] = "true"

    tool = WebSearch(query="Python programming", max_results=3)
    result = tool.run()

    print(f"Success: {result.get('success')}")
    print(f"Results: {len(result.get('result', []))} items")
    print(f"First result: {result.get('result', [{}])[0] if result.get('result') else 'None'}")
