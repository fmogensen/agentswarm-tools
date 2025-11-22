"""
Detect and catalog downloadable media resources from web pages
"""

from typing import Any, Dict, List, Optional
from pydantic import Field
import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

from shared.base import BaseTool
from shared.errors import ValidationError, APIError


class ResourceDiscovery(BaseTool):
    """
    Detect and catalog downloadable media resources from web pages

    Args:
        input: Primary input parameter

    Returns:
        Dict containing:
        - success: Boolean indicating success
        - result: Tool-specific results
        - metadata: Additional information

    Example:
        >>> tool = ResourceDiscovery(input="example")
        >>> result = tool.run()
    """

    # Tool metadata
    tool_name: str = "resource_discovery"
    tool_category: str = "content"

    # Parameters
    input: str = Field(..., description="Primary input parameter")

    def _execute(self) -> Dict[str, Any]:
        """
        Execute the resource_discovery tool.

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
        if not self.input or not isinstance(self.input, str):
            raise ValidationError(
                "Input must be a non-empty string",
                field="input",
                tool_name=self.tool_name,
            )

        if not (self.input.startswith("http://") or self.input.startswith("https://")):
            raise ValidationError(
                "Input must be a valid URL starting with http:// or https://",
                field="input",
                tool_name=self.tool_name,
            )

    def _should_use_mock(self) -> bool:
        """Check if mock mode enabled."""
        return os.getenv("USE_MOCK_APIS", "false").lower() == "true"

    def _generate_mock_results(self) -> Dict[str, Any]:
        """Generate mock results for testing."""
        mock_resources = [
            {
                "url": "https://example.com/file1.mp3",
                "type": "audio",
                "filename": "file1.mp3",
                "source_page": self.input,
            },
            {
                "url": "https://example.com/video.mp4",
                "type": "video",
                "filename": "video.mp4",
                "source_page": self.input,
            },
        ]

        return {
            "success": True,
            "result": {"resources": mock_resources},
            "metadata": {"mock_mode": True},
        }

    def _process(self) -> Any:
        """Main processing logic."""
        try:
            response = requests.get(self.input, timeout=10)
            response.raise_for_status()
        except Exception as e:
            raise APIError(f"Unable to retrieve URL: {e}", tool_name=self.tool_name)

        soup = BeautifulSoup(response.text, "html.parser")
        resources: List[Dict[str, Any]] = []

        media_extensions = {
            ".mp3": "audio",
            ".wav": "audio",
            ".ogg": "audio",
            ".mp4": "video",
            ".mov": "video",
            ".avi": "video",
            ".mkv": "video",
            ".jpg": "image",
            ".jpeg": "image",
            ".png": "image",
            ".gif": "image",
            ".zip": "archive",
            ".tar": "archive",
            ".gz": "archive",
            ".pdf": "document",
        }

        elements = soup.find_all(["a", "source", "img"])

        for el in elements:
            url = None

            if el.name == "a" and el.get("href"):
                url = el["href"]
            elif el.name == "source" and el.get("src"):
                url = el["src"]
            elif el.name == "img" and el.get("src"):
                url = el["src"]

            if not url:
                continue

            abs_url = urljoin(self.input, url)

            for ext, filetype in media_extensions.items():
                if abs_url.lower().endswith(ext):
                    filename = abs_url.split("/")[-1]
                    resources.append(
                        {
                            "url": abs_url,
                            "type": filetype,
                            "filename": filename,
                            "source_page": self.input,
                        }
                    )
                    break

        return {"resources": resources}


if __name__ == "__main__":
    # Test the resource_discovery tool
    print("Testing ResourceDiscovery tool...")

    # Test with mock mode
    import os
    os.environ["USE_MOCK_APIS"] = "true"

    tool = ResourceDiscovery(input="https://example.com/page")
    result = tool.run()

    print(f"Success: {result.get('success')}")
    print(f"Resources found: {len(result.get('result', {}).get('resources', []))}")
    print(f"First resource: {result.get('result', {}).get('resources', [{}])[0] if result.get('result', {}).get('resources') else 'None'}")
