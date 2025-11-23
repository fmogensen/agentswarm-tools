"""
Retrieve and convert content from URLs into readable format
"""

import os
from typing import Any, Dict

import requests
from bs4 import BeautifulSoup
from pydantic import Field

from shared.base import BaseTool
from shared.errors import APIError, ValidationError


class Crawler(BaseTool):
    """
    Retrieve and convert content from URLs into readable format

    Args:
        url: URL to crawl and extract content from
        max_depth: Maximum depth to crawl (0 = single page, 1 = follow links once, etc.)

    Returns:
        Dict containing:
        - success: Boolean indicating success
        - result: Tool-specific results (page content, links, etc.)
        - metadata: Additional information

    Example:
        >>> tool = Crawler(url="https://example.com", max_depth=1)
        >>> result = tool.run()
    """

    # Tool metadata
    tool_name: str = "crawler"
    tool_category: str = "content"
    tool_description: str = "Retrieve and convert content from URLs into readable format"

    # Parameters
    url: str = Field(..., description="URL to crawl and extract content from")
    max_depth: int = Field(0, description="Maximum crawl depth (0 = single page only)", ge=0, le=3)

    def _execute(self) -> Dict[str, Any]:
        """
        Execute the crawler tool.

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
        if not self.url.startswith("http://") and not self.url.startswith("https://"):
            raise ValidationError(
                "URL must start with http:// or https://",
                tool_name=self.tool_name,
                details={"url": self.url},
            )

    def _should_use_mock(self) -> bool:
        """Check if mock mode enabled."""
        return os.getenv("USE_MOCK_APIS", "false").lower() == "true"

    def _generate_mock_results(self) -> Dict[str, Any]:
        """Generate mock results for testing."""
        return {
            "success": True,
            "result": {
                "url": self.url,
                "max_depth": self.max_depth,
                "content": "This is mock crawled content from the webpage.",
                "title": "Mock Page Title",
                "links": ["https://example.com/page1", "https://example.com/page2"],
                "mock": True,
            },
            "metadata": {"mock_mode": True, "tool_name": self.tool_name},
        }

    def _process(self) -> Any:
        """Main processing logic."""
        try:
            response = requests.get(self.url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, "html.parser")

            # Extract text content
            text_content = soup.get_text(separator="\n", strip=True)

            # Extract title
            title = soup.title.string if soup.title else "No title"

            # Extract links (for potential depth crawling)
            links = [a.get("href") for a in soup.find_all("a", href=True)]

            result = {
                "url": self.url,
                "max_depth": self.max_depth,
                "content": text_content[:5000],  # Limit content size
                "title": title,
                "links": (
                    links[:20] if self.max_depth > 0 else []
                ),  # Only include links if crawling deeper
            }

            return result
        except requests.exceptions.RequestException as e:
            raise APIError(f"HTTP request failed: {e}", tool_name=self.tool_name)
        except Exception as e:
            raise APIError(f"Failed to process the URL: {e}", tool_name=self.tool_name)


if __name__ == "__main__":
    import os

    os.environ["USE_MOCK_APIS"] = "true"

    tool = Crawler(url="https://example.com", max_depth=1)
    result = tool.run()

    print(f"Success: {result.get('success')}")
    assert result.get("success") == True, "Tool execution failed"
    print(f"Result: {result.get('result')}")
