"""
Search geographical information, places, businesses, and get directions
"""

from typing import Any, Dict, List
from pydantic import Field
import os
import requests

from shared.base import BaseTool
from shared.errors import ValidationError, APIError


class MapsSearch(BaseTool):
    """
    Search geographical information, places, businesses, and get directions

    Args:
        query: Search query string
        max_results: Maximum number of results to return

    Returns:
        Dict containing:
        - success: Boolean indicating success
        - result: Tool-specific results
        - metadata: Additional information

    Example:
        >>> tool = MapsSearch(query="example", max_results=5)
        >>> result = tool.run()
    """

    # Tool metadata
    tool_name: str = "maps_search"
    tool_category: str = "location"

    # Parameters
    query: str = Field(..., description="Search query string", min_length=1)
    max_results: int = Field(
        10, description="Maximum number of results to return", ge=1, le=50
    )

    def _execute(self) -> Dict[str, Any]:
        """
        Execute the maps_search tool.

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
                "name": f"Mock Place {i}",
                "address": f"Mock Address {i}",
                "type": "mock",
                "rating": 4.5,
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
        # Simulate an API call to a maps service
        try:
            # Example: Replace with actual API call
            response = requests.get(
                "https://maps.googleapis.com/maps/api/place/textsearch/json",
                params={
                    "query": self.query,
                    "key": os.getenv("GOOGLE_MAPS_API_KEY"),
                    "maxResults": self.max_results,
                },
            )
            response.raise_for_status()
            data = response.json()

            # Extract relevant information
            results = [
                {
                    "name": place.get("name"),
                    "address": place.get("formatted_address"),
                    "type": place.get("types", []),
                    "rating": place.get("rating"),
                }
                for place in data.get("results", [])
            ]

            return results

        except requests.RequestException as e:
            raise APIError(f"API request failed: {e}", tool_name=self.tool_name)


if __name__ == "__main__":
    import os
    os.environ["USE_MOCK_APIS"] = "true"

    tool = MapsSearch(query="coffee shops near me")
    result = tool.run()
    print(f"Success: {result.get('success')}")
