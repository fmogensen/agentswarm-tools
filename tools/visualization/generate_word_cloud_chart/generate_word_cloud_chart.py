"""
Generate word cloud for word frequency visualization
"""

import base64
import io
import os
from typing import Any, Dict, List, Optional

from pydantic import Field

from shared.base import BaseTool
from shared.errors import APIError, ValidationError

try:
    from wordcloud import WordCloud
except Exception:
    WordCloud = None


class GenerateWordCloudChart(BaseTool):
    """
    Generate word cloud for word frequency visualization

    Args:
        prompt: Description of what to generate
        params: Additional generation parameters

    Returns:
        Dict containing:
        - success: Boolean indicating success
        - result: Tool-specific results
        - metadata: Additional information

    Example:
        >>> tool = GenerateWordCloudChart(prompt="example", params={"width": 400})
        >>> result = tool.run()
    """

    # Tool metadata
    tool_name: str = "generate_word_cloud_chart"
    tool_category: str = "visualization"

    # Parameters
    prompt: str = Field(..., description="Description of what to generate", min_length=1)
    params: Dict[str, Any] = Field(
        default_factory=dict, description="Additional generation parameters"
    )

    def _execute(self) -> Dict[str, Any]:
        """
        Execute the generate_word_cloud_chart tool.

        Returns:
            Dict with results
        """

        self._logger.info(f"Executing {self.tool_name} with prompt={self.prompt}, params={self.params}")
        self._validate_parameters()

        if self._should_use_mock():
            self._logger.info("Using mock mode for testing")
            return self._generate_mock_results()

        try:
            result = self._process()

            self._logger.info(f"Successfully completed {self.tool_name}")

            return {
                "success": True,
                "result": result,
                "metadata": {"tool_name": self.tool_name, "params_used": self.params},
            }

        except Exception as e:
            self._logger.error(f"Error in {self.tool_name}: {str(e)}", exc_info=True)
            raise APIError(f"Failed: {e}", tool_name=self.tool_name)

    def _validate_parameters(self) -> None:
        """Validate input parameters."""
        if not isinstance(self.prompt, str) or not self.prompt.strip():
            raise ValidationError(
                "Prompt must be a non-empty string",
                tool_name=self.tool_name,
                details={"prompt": self.prompt},
            )

        if not isinstance(self.params, dict):
            raise ValidationError(
                "Params must be a dictionary",
                tool_name=self.tool_name,
                details={"params": self.params},
            )

        if WordCloud is None and not self._should_use_mock():
            raise APIError("wordcloud library not installed", tool_name=self.tool_name)

    def _should_use_mock(self) -> bool:
        """Check if mock mode enabled."""
        return os.getenv("USE_MOCK_APIS", "false").lower() == "true"

    def _generate_mock_results(self) -> Dict[str, Any]:
        """Generate mock results for testing."""
        mock_image = (
            "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAA"
            "AAC0lEQVR42mP8/x8AAwMBAFf4Cw0AAAAASUVORK5CYII="
        )

        return {
            "success": True,
            "result": {"image_base64": mock_image, "mock": True},
            "metadata": {"mock_mode": True, "tool_name": self.tool_name},
        }

    def _process(self) -> Any:
        """Main processing logic."""
        try:
            width = int(self.params.get("width", 800))
            height = int(self.params.get("height", 400))
            background_color = self.params.get("background_color", "white")

            wc = WordCloud(width=width, height=height, background_color=background_color).generate(
                self.prompt
            )

            buffer = io.BytesIO()
            wc.to_image().save(buffer, format="PNG")
            encoded_image = base64.b64encode(buffer.getvalue()).decode("utf-8")

            return {"image_base64": encoded_image, "width": width, "height": height}

        except Exception as e:
            self._logger.error(f"Error in {self.tool_name}: {str(e)}", exc_info=True)
            raise APIError(f"Word cloud generation failed: {e}", tool_name=self.tool_name)


if __name__ == "__main__":
    import os

    os.environ["USE_MOCK_APIS"] = "true"

    tool = GenerateWordCloudChart(
        prompt="cloud computing data analytics machine learning artificial intelligence big data python programming",
        params={"width": 800, "height": 400, "background_color": "white"},
    )
    result = tool.run()

    print(f"Success: {result.get('success')}")
    assert result.get("success") == True, "Tool execution failed"
    print(f"Result: {result.get('result')}")
