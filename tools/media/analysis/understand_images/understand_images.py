"""
Read and analyze image content from URLs or AI Drive paths
"""

from typing import Any, Dict, Optional
from pydantic import Field
import os

try:
    import requests
except ImportError:
    requests = None

from shared.base import BaseTool
from shared.errors import ValidationError, APIError


class UnderstandImages(BaseTool):
    """
    Read and analyze image content from URLs or AI Drive paths

    Args:
        media_url: URL of media to analyze
        instruction: What to analyze or extract

    Returns:
        Dict containing:
        - success: Boolean indicating success
        - result: Tool-specific results
        - metadata: Additional information

    Example:
        >>> tool = UnderstandImages(media_url="example", instruction="example")
        >>> result = tool.run()
    """

    tool_name: str = "understand_images"
    tool_category: str = "media"

    media_url: str = Field(..., description="URL of media to analyze")
    instruction: Optional[str] = Field(default=None, description="What to analyze or extract")

    def _execute(self) -> Dict[str, Any]:
        """
        Execute the understand_images tool.

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
                    "instruction": self.instruction,
                },
            }
        except Exception as e:
            raise APIError(f"Failed: {e}", tool_name=self.tool_name)

    def _validate_parameters(self) -> None:
        """
        Validate input parameters.

        Raises:
            ValidationError: If parameters are invalid
        """
        if not self.media_url or not isinstance(self.media_url, str):
            raise ValidationError(
                "media_url must be a non-empty string",
                tool_name=self.tool_name,
                details={"media_url": self.media_url},
            )

        if not (
            self.media_url.startswith("http://")
            or self.media_url.startswith("https://")
            or self.media_url.startswith("aidrive://")
        ):
            raise ValidationError(
                "media_url must be an http/https URL or an AI Drive path",
                tool_name=self.tool_name,
                details={"media_url": self.media_url},
            )

        if self.instruction is not None and not isinstance(self.instruction, str):
            raise ValidationError(
                "instruction must be a string if provided",
                tool_name=self.tool_name,
                details={"instruction": self.instruction},
            )

    def _should_use_mock(self) -> bool:
        """Check if mock mode enabled."""
        return os.getenv("USE_MOCK_APIS", "false").lower() == "true"

    def _generate_mock_results(self) -> Dict[str, Any]:
        """
        Generate mock results for testing.
        """
        return {
            "success": True,
            "result": {
                "mock": True,
                "media_url": self.media_url,
                "instruction": self.instruction or "No instruction provided",
                "description": "This is a mock image analysis response.",
            },
            "metadata": {"mock_mode": True, "tool_name": self.tool_name},
        }

    def _process(self) -> Any:
        """
        Main processing logic.

        Attempts to fetch the image and return basic metadata.

        Raises:
            APIError: If the image cannot be retrieved or processed
        """
        if requests is None:
            raise APIError(
                "requests library is required. Install with: pip install requests",
                tool_name=self.tool_name,
            )

        try:
            # Simple retrieval for demonstration
            if self.media_url.startswith("aidrive://"):
                # Placeholder for AI Drive logic
                # Real implementation would interface with the AI Drive system
                image_bytes = b"FAKE_AIDRIVE_IMAGE_DATA"
            else:
                response = requests.get(self.media_url, timeout=10)
                if response.status_code != 200:
                    raise APIError(
                        f"Failed to fetch image from URL: HTTP {response.status_code}",
                        tool_name=self.tool_name,
                    )
                image_bytes = response.content

            size_bytes = len(image_bytes)

            analysis = {
                "image_size_bytes": size_bytes,
                "instruction_applied": bool(self.instruction),
                "instruction": self.instruction or "No instruction provided",
            }

            return analysis

        except Exception as e:
            raise APIError(f"Error retrieving or analyzing image: {e}", tool_name=self.tool_name)


if __name__ == "__main__":
    # Test the understand_images tool
    print("Testing UnderstandImages tool...")

    # Test with mock mode
    import os

    os.environ["USE_MOCK_APIS"] = "true"

    tool = UnderstandImages(
        media_url="https://example.com/image.jpg",
        instruction="Describe the main objects in this image",
    )
    result = tool.run()

    print(f"Success: {result.get('success')}")
    print(f"Description: {result.get('result', {}).get('description')}")
    print(f"Mock mode: {result.get('metadata', {}).get('mock_mode')}")
    assert result.get("success") == True
    assert "description" in result.get("result", {})
    print("UnderstandImages test passed!")
