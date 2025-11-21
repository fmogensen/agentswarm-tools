"""
Search scholarly articles, academic papers, and research publications
"""

from typing import Any, Dict, List
from pydantic import Field
import os
import requests

from shared.base import BaseTool
from shared.errors import ValidationError, APIError


class ScholarSearch(BaseTool):
    """
    Search scholarly articles, academic papers, and research publications

    Args:
        query: Search query string
        max_results: Maximum number of results to return

    Returns:
        Dict containing:
        - success: Boolean indicating success
        - result: Tool-specific results
        - metadata: Additional information

    Example:
        >>> tool = ScholarSearch(query="example", max_results=5)
        >>> result = tool.run()
    """

    # Tool metadata
    tool_name: str = "scholar_search"
    tool_category: str = "search"

    # Parameters
    query: str = Field(
        ..., description="Search query string", min_length=1, max_length=500
    )
    max_results: int = Field(
        10, description="Maximum number of results to return", ge=1, le=100
    )

    def _execute(self) -> Dict[str, Any]:
        """
        Execute the scholar_search tool.

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
                "metadata": {
                    "tool_name": self.tool_name,
                    "query": self.query,
                    "max_results": self.max_results,
                },
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
                "id": i,
                "title": f"Mock Article {i}",
                "abstract": f"This is a mock abstract for article {i}.",
                "authors": ["Author A", "Author B"],
                "source": "mock",
            }
            for i in range(1, self.max_results + 1)
        ]

        return {
            "success": True,
            "result": mock_results,
            "metadata": {"mock_mode": True, "tool_version": "1.0.0"},
        }

    def _process(self) -> List[Dict[str, Any]]:
        """Main processing logic using Semantic Scholar API."""
        try:
            # Use Semantic Scholar API (free, no key required for basic queries)
            response = requests.get(
                "https://api.semanticscholar.org/graph/v1/paper/search",
                params={
                    "query": self.query,
                    "limit": min(self.max_results, 100),  # API max is 100
                    "fields": "paperId,title,abstract,authors,year,url"
                },
                timeout=30
            )
            response.raise_for_status()
            data = response.json()

            # Transform Semantic Scholar response to our format
            papers = data.get("data", [])
            results = []
            for paper in papers:
                results.append({
                    "id": paper.get("paperId", ""),
                    "title": paper.get("title", ""),
                    "abstract": paper.get("abstract", "No abstract available"),
                    "authors": [author.get("name", "") for author in paper.get("authors", [])],
                    "year": paper.get("year"),
                    "url": paper.get("url", ""),
                    "source": "semanticscholar"
                })

            return results
        except requests.RequestException as e:
            raise APIError(f"API request failed: {e}", tool_name=self.tool_name)


if __name__ == "__main__":
    # Test the scholar_search tool
    print("Testing ScholarSearch tool...")

    # Test with mock mode
    import os
    os.environ["USE_MOCK_APIS"] = "true"

    tool = ScholarSearch(query="machine learning", max_results=5)
    result = tool.run()

    print(f"Success: {result.get('success')}")
    print(f"Results: {len(result.get('result', []))} articles")
    print(f"First article: {result.get('result', [{}])[0].get('title') if result.get('result') else 'None'}")
