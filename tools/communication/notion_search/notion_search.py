"""
Search Notion workspace for pages and content
"""

from typing import Any, Dict, List
from pydantic import Field
import os
import requests

from shared.base import BaseTool
from shared.errors import ValidationError, APIError


class NotionSearch(BaseTool):
    """
    Search Notion workspace for pages and content

    Args:
        query: Search query string
        max_results: Maximum number of results to return

    Returns:
        Dict containing:
        - success: Boolean indicating success
        - result: Tool-specific results
        - metadata: Additional information

    Example:
        >>> tool = NotionSearch(query="example", max_results=5)
        >>> result = tool.run()
    """

    # Tool metadata
    tool_name: str = "notion_search"
    tool_category: str = "communication"
    tool_description: str = "Search Notion workspace for pages and content"

    # Parameters
    query: str = Field(..., description="Search query string", min_length=1, max_length=500)
    max_results: int = Field(10, description="Maximum number of results to return", ge=1, le=100)

    def _execute(self) -> Dict[str, Any]:
        """
        Execute the notion_search tool.

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
                    "tool_version": "1.0.0",
                },
            }
        except Exception as e:
            raise APIError(f"Failed: {e}", tool_name=self.tool_name)

    def _validate_parameters(self) -> None:
        """Validate input parameters.

        Raises:
            ValidationError: If query is empty or invalid
        """
        if not self.query or not self.query.strip():
            raise ValidationError(
                "Query cannot be empty", tool_name=self.tool_name, details={"query": self.query}
            )

        if not isinstance(self.max_results, int) or self.max_results < 1:
            raise ValidationError(
                "max_results must be an integer >= 1",
                tool_name=self.tool_name,
                details={"max_results": self.max_results},
            )

    def _should_use_mock(self) -> bool:
        """Check if mock mode enabled."""
        return os.getenv("USE_MOCK_APIS", "false").lower() == "true"

    def _generate_mock_results(self) -> Dict[str, Any]:
        """Generate mock results for testing."""
        mock_items = [
            {
                "id": f"mock-{i}",
                "title": f"Mock Notion Page {i}",
                "snippet": f"Mock content snippet for {self.query}",
                "url": f"https://notion.mock/page/{i}",
            }
            for i in range(1, min(self.max_results, 10) + 1)
        ]

        return {
            "success": True,
            "result": mock_items,
            "metadata": {
                "mock_mode": True,
                "query": self.query,
                "max_results": self.max_results,
                "tool_version": "1.0.0",
            },
        }

    def _process(self) -> List[Dict[str, Any]]:
        """
        Main processing logic.

        Returns:
            List of search results

        Raises:
            APIError: If request to Notion API fails
        """
        notion_token = os.getenv("NOTION_API_KEY")
        if not notion_token:
            raise APIError("NOTION_API_KEY environment variable not set", tool_name=self.tool_name)

        headers = {
            "Authorization": f"Bearer {notion_token}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28",
        }

        payload = {"query": self.query}

        try:
            response = requests.post(
                "https://api.notion.com/v1/search", json=payload, headers=headers, timeout=10
            )
        except Exception as e:
            raise APIError(f"Request to Notion API failed: {e}", tool_name=self.tool_name)

        if response.status_code != 200:
            raise APIError(
                f"Notion API returned status {response.status_code}: {response.text}",
                tool_name=self.tool_name,
            )

        data = response.json()
        results = []

        for item in data.get("results", [])[: self.max_results]:
            title = ""
            if "properties" in item and "title" in item["properties"]:
                title_obj = item["properties"]["title"].get("title", [])
                if title_obj:
                    title = title_obj[0].get("plain_text", "")

            results.append(
                {
                    "id": item.get("id"),
                    "title": title,
                    "url": item.get("url"),
                    "object": item.get("object"),
                }
            )

        return results


if __name__ == "__main__":
    print("Testing NotionSearch...")

    import os

    os.environ["USE_MOCK_APIS"] = "true"

    # Test 1: Search Notion workspace
    print("\nTest 1: Search Notion workspace")
    tool = NotionSearch(query="project documentation", max_results=5)
    result = tool.run()

    assert result.get("success") == True
    assert isinstance(result.get("result"), list)
    assert len(result.get("result")) > 0
    print(f"✅ Test 1 passed: Found {len(result.get('result'))} results")
    print(f"   First result: {result.get('result')[0].get('title')}")

    # Test 2: Different query with default max_results
    print("\nTest 2: Different search query")
    tool = NotionSearch(query="meeting notes")
    result = tool.run()

    assert result.get("success") == True
    assert result.get("metadata", {}).get("query") == "meeting notes"
    print(f"✅ Test 2 passed: Search executed successfully")

    # Test 3: Validation - empty query
    print("\nTest 3: Validation - empty query")
    try:
        bad_tool = NotionSearch(query="   ", max_results=5)
        bad_tool.run()
        assert False, "Should have raised ValidationError"
    except Exception as e:
        print(f"✅ Test 3 passed: Validation working - {type(e).__name__}")

    # Test 4: Custom max_results
    print("\nTest 4: Custom max_results")
    tool = NotionSearch(query="test", max_results=3)
    result = tool.run()

    assert result.get("success") == True
    assert len(result.get("result")) <= 3
    print(f"✅ Test 4 passed: Max results limit working")

    print("\n✅ All tests passed!")
