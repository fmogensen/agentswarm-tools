"""
Search files and folders in Microsoft OneDrive (personal and business)
"""

from typing import Any, Dict, List
from pydantic import Field
import os
import requests

from shared.base import BaseTool
from shared.errors import ValidationError, APIError


class OnedriveSearch(BaseTool):
    """
    Search files and folders in Microsoft OneDrive (personal and business)

    Args:
        query: Search query string
        max_results: Maximum number of results to return

    Returns:
        Dict containing:
        - success: Boolean indicating success
        - result: Tool-specific results
        - metadata: Additional information

    Example:
        >>> tool = OnedriveSearch(query="example", max_results=5)
        >>> result = tool.run()
    """

    tool_name: str = "onedrive_search"
    tool_category: str = "infrastructure"

    query: str = Field(..., description="Search query string", min_length=1, max_length=500)
    max_results: int = Field(10, description="Maximum number of results to return", ge=1, le=200)

    def _execute(self) -> Dict[str, Any]:
        """
        Execute the onedrive_search tool.

        Returns:
            Dict with results
        """
        self._validate_parameters()

        if self._should_use_mock():
            return self._generate_mock_results()

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
        if not self.query or not self.query.strip():
            raise ValidationError(
                "Query cannot be empty",
                tool_name=self.tool_name,
                details={"query": self.query},
            )

        if not isinstance(self.max_results, int) or self.max_results <= 0:
            raise ValidationError(
                "max_results must be a positive integer",
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
                "name": f"Mock File {i}",
                "type": "file" if i % 2 == 0 else "folder",
                "size": 1234 + i,
                "path": f"/mock/path/{i}",
            }
            for i in range(1, self.max_results + 1)
        ]

        return {
            "success": True,
            "result": mock_items,
            "metadata": {
                "mock_mode": True,
                "query": self.query,
                "max_results": self.max_results,
            },
        }

    def _process(self) -> List[Dict[str, Any]]:
        """
        Main processing logic.

        Searches OneDrive using Microsoft Graph API.
        Expects environment variable MS_GRAPH_TOKEN to be set.

        Returns:
            List of file/folder metadata dictionaries
        """
        token = os.getenv("MS_GRAPH_TOKEN")
        if not token:
            raise APIError("MS_GRAPH_TOKEN environment variable not set", tool_name=self.tool_name)

        headers = {"Authorization": f"Bearer {token}"}

        url = f"https://graph.microsoft.com/v1.0/me/drive/root/search(q='{self.query}')"

        try:
            response = requests.get(url, headers=headers, timeout=10)
        except Exception as e:
            raise APIError(f"HTTP request failed: {e}", tool_name=self.tool_name)

        if response.status_code >= 400:
            raise APIError(
                f"Graph API error {response.status_code}: {response.text}",
                tool_name=self.tool_name,
            )

        data = response.json()
        items = data.get("value", [])

        results: List[Dict[str, Any]] = []

        for item in items[: self.max_results]:
            results.append(
                {
                    "id": item.get("id"),
                    "name": item.get("name"),
                    "type": "folder" if "folder" in item else "file",
                    "size": item.get("size"),
                    "web_url": item.get("webUrl"),
                    "path": item.get("parentReference", {}).get("path"),
                }
            )

        return results


if __name__ == "__main__":
    # Test the tool
    print("Testing OnedriveSearch...")

    import os

    os.environ["USE_MOCK_APIS"] = "true"

    tool = OnedriveSearch(query="test", max_results=5)
    result = tool.run()

    print(f"Success: {result.get('success')}")
    print(f"Results count: {len(result.get('result', []))}")
    assert result.get("success") == True
    assert len(result.get("result", [])) == 5
    print("All tests passed!")
