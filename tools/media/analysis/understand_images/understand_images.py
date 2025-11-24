"""
Read and analyze image content from URLs or AI Drive paths using LiteLLM vision models
"""

import os
from typing import Any, Dict, Optional

from pydantic import Field

try:
    import requests
except ImportError:
    requests = None

from shared.analytics import AnalyticsEvent, EventType, record_event
from shared.base import BaseTool
from shared.errors import APIError, ValidationError
from shared.llm_client import LLMResponse, get_llm_client


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
    model: Optional[str] = Field(
        None, description="Vision model to use (e.g., 'gpt-4-turbo', 'claude-3-opus')"
    )
    fallback_models: Optional[list] = Field(
        None, description="List of fallback vision models if primary fails"
    )

    def _execute(self) -> Dict[str, Any]:
        """
        Execute the understand_images tool.

        Returns:
            Dict with results
        """

        self._logger.info(
            f"Executing {self.tool_name} with media_url={self.media_url}, instruction={self.instruction}, model={self.model}, fallback_models={self.fallback_models}"
        )
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
                "metadata": {
                    "tool_name": self.tool_name,
                    "instruction": self.instruction,
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
        Main processing logic using LiteLLM vision models.

        Analyzes image using AI vision capabilities.

        Raises:
            APIError: If the image cannot be retrieved or processed
        """
        try:
            # Get LiteLLM client
            client = get_llm_client()

            # Determine model to use
            model = self.model or os.getenv("LITELLM_DEFAULT_VISION_MODEL", "gpt-4-turbo")
            fallback = self.fallback_models or ["claude-3-opus-20240229", "gemini-pro-vision"]

            # Build instruction prompt
            instruction = (
                self.instruction
                or "Describe this image in detail, including objects, people, text, colors, and composition."
            )

            # Prepare messages for vision API
            messages = [{"role": "user", "content": instruction}]

            # Call vision completion
            response: LLMResponse = client.vision_completion(
                messages=messages,
                image_urls=[self.media_url],
                model=model,
                fallback_models=fallback,
                max_tokens=1000,
            )

            # Record cost event for analytics
            record_event(
                AnalyticsEvent(
                    event_type=EventType.LLM_COST,
                    tool_name=self.tool_name,
                    success=True,
                    metadata={
                        "model": response.model,
                        "provider": response.provider,
                        "cost": response.cost,
                        "total_tokens": response.usage.get("total_tokens", 0),
                        "task_type": "image_understanding",
                    },
                )
            )

            analysis = {
                "description": response.content,
                "instruction_applied": self.instruction,
                "model_used": response.model,
                "provider": response.provider,
                "cost": response.cost,
                "latency_ms": response.latency_ms,
                "tokens_used": response.usage.get("total_tokens", 0),
            }

            return analysis

        except Exception as e:
            self._logger.error(f"Error in {self.tool_name}: {str(e)}", exc_info=True)
            raise APIError(f"Error analyzing image: {e}", tool_name=self.tool_name)


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
