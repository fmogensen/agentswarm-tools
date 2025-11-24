"""
Deep analysis of images, audio, and video with custom requirements
"""

import os
from typing import Any, Dict, Optional

from pydantic import Field

from shared.base import BaseTool
from shared.errors import APIError, ValidationError


class AnalyzeMediaContent(BaseTool):
    """
    Deep analysis of images, audio, and video with custom requirements.

    Args:
        media_url: URL of media to analyze
        instruction: What to analyze or extract

    Returns:
        Dict containing:
        - success: Boolean indicating success
        - result: Tool-specific results
        - metadata: Additional information

    Example:
        >>> tool = AnalyzeMediaContent(media_url="http://example.com/img.jpg", instruction="Identify objects")
        >>> result = tool.run()
    """

    # Tool metadata
    tool_name: str = "analyze_media_content"
    tool_category: str = "media"
    tool_description: str = "Deep analysis of images, audio, and video with custom requirements"

    # Parameters
    media_url: str = Field(
        ..., description="URL of media to analyze", min_length=5, max_length=2000
    )

    instruction: Optional[str] = Field(default=None, description="What to analyze or extract")

    def _execute(self) -> Dict[str, Any]:
        """
        Execute the analyze_media_content tool.

        Returns:
            Dict with results

        Raises:
            ValidationError: For invalid parameters
            APIError: For external API failures
        """

        self._logger.info(f"Executing {self.tool_name} with media_url={self.media_url}, instruction={self.instruction}")
        # 1. VALIDATE
        self._logger.debug(f"Validating parameters for {self.tool_name}")
        self._validate_parameters()

        # 2. CHECK MOCK MODE
        if self._should_use_mock():
            self._logger.info("Using mock mode for testing")
            return self._generate_mock_results()

        # 3. EXECUTE REAL LOGIC
        try:
            result = self._process()

            self._logger.info(f"Successfully completed {self.tool_name}")

            return {
                "success": True,
                "result": result,
                "metadata": {
                    "tool_name": self.tool_name,
                    "media_url": self.media_url,
                    "instruction": self.instruction,
                    "tool_version": "1.0.0",
                },
            }

        except Exception as e:
            self._logger.error(f"Error in {self.tool_name}: {str(e)}", exc_info=True)
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

        if not (self.media_url.startswith("http://") or self.media_url.startswith("https://")):
            raise ValidationError(
                "media_url must begin with http:// or https://",
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

        Returns:
            Dict with mock analysis data
        """
        mock_analysis = {
            "media_url": self.media_url,
            "instruction": self.instruction or "No instruction provided",
            "analysis": "This is a mock analysis result",
            "confidence": 0.99,
        }

        return {
            "success": True,
            "result": mock_analysis,
            "metadata": {"mock_mode": True, "tool_name": self.tool_name},
        }

    def _process(self) -> Any:
        """
        Main processing logic.

        This function would normally call an external media analysis API,
        process the response, and format results.

        Returns:
            Parsed analysis results

        Raises:
            APIError: If API call fails
        """
        # Example placeholder logic:
        try:
            # Simulate media analysis
            analysis_result = {
                "media_url": self.media_url,
                "instruction": self.instruction or "Automatic analysis",
                "detected_features": [
                    {"type": "object", "label": "example", "confidence": 0.82},
                    {"type": "color", "label": "blue", "confidence": 0.91},
                ],
                "processing_notes": "Simulated analysis output",
            }

            return analysis_result

        except Exception as e:
            self._logger.error(f"Error in {self.tool_name}: {str(e)}", exc_info=True)
            raise APIError(f"Media analysis failed: {e}", tool_name=self.tool_name)


if __name__ == "__main__":
    print("Testing AnalyzeMediaContent...")

    import os

    os.environ["USE_MOCK_APIS"] = "true"

    # Test with mock data
    tool = AnalyzeMediaContent(
        media_url="https://example.com/image.jpg",
        instruction="Identify objects and colors",
    )
    result = tool.run()

    print(f"Success: {result.get('success')}")
    print(f"Result: {result.get('result')}")
    assert result.get("success") == True
    assert "analysis" in result.get("result", {})
    print("AnalyzeMediaContent test passed!")
