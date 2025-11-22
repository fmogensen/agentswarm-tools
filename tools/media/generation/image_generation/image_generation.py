"""
Generate new images from text descriptions or reference images
"""

from typing import Any, Dict, Optional
from pydantic import Field
import os

from shared.base import BaseTool
from shared.errors import ValidationError, APIError


class ImageGeneration(BaseTool):
    """
    Generate new images from text descriptions or reference images.

    Args:
        prompt: Description of what to generate
        params: Additional generation parameters such as:
            - size: str (e.g., "1024x1024")
            - model: str (model name)
            - steps: int (generation steps)
            - seed: int (random seed)
            - guidance_scale: float

    Returns:
        Dict containing:
        - success: Boolean indicating success
        - result: Generation result payload
        - metadata: Additional information

    Example:
        >>> tool = ImageGeneration(prompt="a futuristic city", params={"size": "1024x1024"})
        >>> result = tool.run()
    """

    tool_name: str = "image_generation"
    tool_category: str = "media"
    tool_description: str = (
        "Generate new images from text descriptions or reference images"
    )

    # Parameters
    prompt: str = Field(
        ..., description="Description of what to generate", min_length=1
    )
    params: Dict[str, Any] = Field(
        default_factory=dict, description="Additional generation parameters"
    )

    def _execute(self) -> Dict[str, Any]:
        """
        Execute the image_generation tool.

        Returns:
            Dict with results

        Raises:
            ValidationError: For invalid inputs
            APIError: For external API failures
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
                    "model_used": self.params.get("model", "default"),
                    "mock_mode": False,
                },
            }
        except Exception as e:
            raise APIError(f"Failed to generate image: {e}", tool_name=self.tool_name)

    def _validate_parameters(self) -> None:
        """
        Validate input parameters.

        Raises:
            ValidationError: If parameters are invalid
        """
        if (
            not self.prompt
            or not isinstance(self.prompt, str)
            or not self.prompt.strip()
        ):
            raise ValidationError(
                "Prompt cannot be empty",
                tool_name=self.tool_name,
                details={"prompt": self.prompt},
            )

        if not isinstance(self.params, dict):
            raise ValidationError(
                "params must be an object (dictionary)",
                tool_name=self.tool_name,
                details={"params": self.params},
            )

        # Optional validations
        if "size" in self.params:
            size = self.params["size"]
            if not isinstance(size, str) or "x" not in size:
                raise ValidationError(
                    "size must be a string like '1024x1024'",
                    tool_name=self.tool_name,
                    details={"size": size},
                )

        if "steps" in self.params and (
            not isinstance(self.params["steps"], int) or self.params["steps"] <= 0
        ):
            raise ValidationError(
                "steps must be a positive integer",
                tool_name=self.tool_name,
                details={"steps": self.params.get("steps")},
            )

    def _should_use_mock(self) -> bool:
        """Check if mock mode enabled."""
        return os.getenv("USE_MOCK_APIS", "false").lower() == "true"

    def _generate_mock_results(self) -> Dict[str, Any]:
        """
        Generate mock results for testing without external API.
        """
        return {
            "success": True,
            "result": {
                "image_url": f"https://mock.api/image/{self.prompt.replace(' ', '_')}.png",
                "prompt": self.prompt,
                "params": self.params,
                "mock": True,
            },
            "metadata": {"mock_mode": True, "tool_name": self.tool_name},
        }

    def _process(self) -> Any:
        """
        Actual image-generation logic.

        Returns:
            The payload returned by the image generation API.

        Raises:
            APIError: If the API request fails
        """
        try:
            # Placeholder implementation
            # In a real tool, this would call an external image generation API.
            # Example:
            # response = requests.post("https://api.example.com/generate", json={...})
            # return response.json()

            return {
                "image_url": "https://example.com/generated_image.png",
                "prompt": self.prompt,
                "parameters_used": self.params,
            }

        except Exception as e:
            raise APIError(f"Image generation API error: {e}", tool_name=self.tool_name)


if __name__ == "__main__":
    # Test the image_generation tool
    print("Testing ImageGeneration tool...")

    # Test with mock mode
    import os
    os.environ["USE_MOCK_APIS"] = "true"

    tool = ImageGeneration(
        prompt="a futuristic city at sunset",
        params={"size": "1024x1024", "steps": 50}
    )
    result = tool.run()

    print(f"Success: {result.get('success')}")
    print(f"Image URL: {result.get('result', {}).get('image_url')}")
    print(f"Mock mode: {result.get('metadata', {}).get('mock_mode')}")
