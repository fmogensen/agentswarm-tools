"""
Search for existing images on the internet
"""

from typing import Any, Dict, List
from pydantic import Field
import os
import requests

from shared.base import BaseTool
from shared.errors import ValidationError, APIError


class ImageSearch(BaseTool):
    """
    Search for existing images on the internet

    Args:
        query: Image search terms
        max_results: Maximum number of results to return

    Returns:
        Dict containing:
        - success: Boolean indicating success
        - result: Array of image results with URLs, thumbnails, metadata
        - metadata: Additional information

    Example:
        >>> tool = ImageSearch(query="sunset landscape", max_results=10)
        >>> result = tool.run()
    """

    # Tool metadata
    tool_name: str = "image_search"
    tool_category: str = "data"

    # Parameters
    query: str = Field(..., description="Image search terms", min_length=1, max_length=500)
    max_results: int = Field(
        10, description="Maximum number of results to return", ge=1, le=100
    )

    def _execute(self) -> Dict[str, Any]:
        """
        Execute the image_search tool.

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
                "position": i,
                "title": f"Mock Image {i}: {self.query}",
                "image_url": f"https://example.com/images/mock_{i}.jpg",
                "thumbnail_url": f"https://example.com/thumbnails/mock_{i}_thumb.jpg",
                "source_page": f"https://example.com/page/{i}",
                "dimensions": {"width": 1920, "height": 1080},
                "format": "JPEG",
                "file_size": "245 KB",
            }
            for i in range(1, min(self.max_results + 1, 11))
        ]

        return {
            "success": True,
            "result": {"images": mock_results, "total_count": len(mock_results)},
            "metadata": {
                "mock_mode": True,
                "tool_name": self.tool_name,
                "query": self.query,
                "max_results": self.max_results,
            },
        }

    def _process(self) -> Dict[str, Any]:
        """Main processing logic."""
        try:
            # In real implementation, this would call Google Images API or similar
            # Example: response = requests.get("https://api.serpapi.com/search", params={...})

            # Placeholder implementation
            api_key = os.getenv("SERPAPI_KEY")
            if not api_key:
                raise APIError(
                    "SERPAPI_KEY not found in environment variables",
                    tool_name=self.tool_name
                )

            # Simulated API call
            results = [
                {
                    "position": i,
                    "title": f"Image {i}",
                    "image_url": f"https://example.com/image_{i}.jpg",
                    "thumbnail_url": f"https://example.com/thumb_{i}.jpg",
                    "source_page": f"https://example.com/page_{i}",
                    "dimensions": {"width": 1920, "height": 1080},
                    "format": "JPEG",
                }
                for i in range(1, self.max_results + 1)
            ]

            return {"images": results, "total_count": len(results)}

        except Exception as e:
            raise APIError(f"Image search failed: {e}", tool_name=self.tool_name)


if __name__ == "__main__":
    # Test the image_search tool
    print("Testing ImageSearch tool...")

    # Test with mock mode
    import os
    os.environ["USE_MOCK_APIS"] = "true"

    tool = ImageSearch(query="sunset landscape", max_results=5)
    result = tool.run()

    print(f"Success: {result.get('success')}")
    print(f"Images found: {result.get('result', {}).get('total_count')}")
    print(f"First image: {result.get('result', {}).get('images', [{}])[0].get('title')}")
