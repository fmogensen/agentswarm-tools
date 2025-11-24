"""
Check URL metadata (content-type, size, filename) without downloading
"""

import os
from typing import Any, Dict

import requests
from pydantic import Field

from shared.base import BaseTool
from shared.errors import APIError, ValidationError


class UrlMetadata(BaseTool):
    """
    Check URL metadata (content-type, size, filename) without downloading

    Args:
        url: URL to check metadata for

    Returns:
        Dict containing:
        - success: Boolean indicating success
        - result: Tool-specific results (content-type, size, filename, etc.)
        - metadata: Additional information

    Example:
        >>> tool = UrlMetadata(url="http://example.com/file.pdf")
        >>> result = tool.run()
    """

    # Tool metadata
    tool_name: str = "url_metadata"
    tool_category: str = "content"

    # Parameters
    url: str = Field(..., description="URL to check metadata for")

    def _execute(self) -> Dict[str, Any]:
        """
        Execute the url_metadata tool.

        Returns:
            Dict with results
        """

        self._logger.info(f"Executing {self.tool_name} with url={self.url}")
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
                "metadata": {"tool_name": self.tool_name},
            }
        except Exception as e:
            self._logger.error(f"Error in {self.tool_name}: {str(e)}", exc_info=True)
            raise APIError(f"Failed: {e}", tool_name=self.tool_name)

    def _validate_parameters(self) -> None:
        """Validate input parameters."""
        if not self.url.startswith("http://") and not self.url.startswith("https://"):
            raise ValidationError(
                "Input must be a valid URL starting with http:// or https://",
                tool_name=self.tool_name,
                details={"input": self.url},
            )

    def _should_use_mock(self) -> bool:
        """Check if mock mode enabled."""
        return os.getenv("USE_MOCK_APIS", "false").lower() == "true"

    def _generate_mock_results(self) -> Dict[str, Any]:
        """Generate mock results for testing."""
        return {
            "success": True,
            "result": {
                "content_type": "text/html",
                "size": 1024,
                "filename": "mock_file.html",
            },
            "metadata": {"mock_mode": True},
        }

    def _process(self) -> Any:
        """Main processing logic."""
        try:
            response = requests.head(self.url, allow_redirects=True)
            response.raise_for_status()

            content_type = response.headers.get("Content-Type", "unknown")
            content_length = response.headers.get("Content-Length", "unknown")
            content_disposition = response.headers.get("Content-Disposition", "")

            if "filename=" in content_disposition:
                filename = content_disposition.split("filename=")[1].strip('"')
            else:
                filename = self.url.split("/")[-1] or "unknown"

            return {
                "content_type": content_type,
                "size": int(content_length) if content_length.isdigit() else "unknown",
                "filename": filename,
            }

        except requests.RequestException as e:
            self._logger.error(f"API request failed: {str(e)}", exc_info=True)
            raise APIError(f"HTTP request failed: {e}", tool_name=self.tool_name)


if __name__ == "__main__":
    import os

    os.environ["USE_MOCK_APIS"] = "true"

    tool = UrlMetadata(url="https://example.com/file.pdf")
    result = tool.run()

    print(f"Success: {result.get('success')}")
    assert result.get("success") == True, "Tool execution failed"
    print(f"Result: {result.get('result')}")
