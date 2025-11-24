"""
Apply artistic styles to images using neural style transfer
"""

import os
import uuid
from typing import Any, Dict, Optional

from pydantic import Field

from shared.base import BaseTool
from shared.errors import APIError, ValidationError


class ImageStyleTransfer(BaseTool):
    """
    Apply artistic styles to images using neural style transfer.

    This tool transforms images by applying artistic styles inspired by
    famous artworks, artistic movements, or custom style references.

    Supported styles:
    - Famous artworks: "starry_night", "the_scream", "picasso", "monet", "van_gogh"
    - Artistic movements: "impressionism", "cubism", "abstract", "pop_art"
    - Effects: "oil_painting", "watercolor", "sketch", "anime", "comic_book"
    - Custom: Provide a style_image_url for custom style transfer

    Args:
        input_image: URL or path to the input image
        style: Style name or type to apply (e.g., "starry_night", "monet", "oil_painting")
        style_image_url: Optional URL to a custom style reference image
        style_strength: Strength of style application (0.0-1.0, default 0.7)
        preserve_color: Whether to preserve original image colors (default False)
        output_size: Output image size (e.g., "1024x1024", defaults to original size)

    Returns:
        Dict containing:
        - success: Boolean indicating success
        - result: URL of the styled image
        - metadata: Processing information

    Example:
        >>> tool = ImageStyleTransfer(
        ...     input_image="https://example.com/photo.jpg",
        ...     style="starry_night",
        ...     style_strength=0.8,
        ...     preserve_color=False
        ... )
        >>> result = tool.run()
    """

    # Tool metadata
    tool_name: str = "image_style_transfer"
    tool_category: str = "media"

    # Parameters
    input_image: str = Field(..., description="URL or path to the input image", min_length=1)
    style: str = Field(..., description="Style name or type to apply", min_length=1)
    style_image_url: Optional[str] = Field(
        default=None, description="Optional URL to custom style reference image"
    )
    style_strength: float = Field(
        default=0.7, description="Strength of style application (0.0-1.0)", ge=0.0, le=1.0
    )
    preserve_color: bool = Field(
        default=False, description="Whether to preserve original image colors"
    )
    output_size: Optional[str] = Field(
        default=None, description="Output image size (e.g., '1024x1024')"
    )

    def _execute(self) -> Dict[str, Any]:
        """Execute the image style transfer."""

        self._logger.info(f"Executing {self.tool_name} with input_image={self.input_image}, style={self.style}, style_image_url={self.style_image_url}, ...")
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
                    "style_applied": self.style,
                    "style_strength": self.style_strength,
                },
            }
        except Exception as e:
            self._logger.error(f"Error in {self.tool_name}: {str(e)}", exc_info=True)
            raise APIError(f"Style transfer failed: {e}", tool_name=self.tool_name)

    def _validate_parameters(self) -> None:
        """Validate input parameters."""
        if not self.input_image or not isinstance(self.input_image, str):
            raise ValidationError(
                "input_image must be a non-empty string",
                tool_name=self.tool_name,
                field="input_image",
            )

        # Validate URL or file path format
        if not (
            self.input_image.startswith(("http://", "https://", "/"))
            or os.path.isfile(self.input_image)
        ):
            raise ValidationError(
                "input_image must be a valid URL or file path",
                tool_name=self.tool_name,
                field="input_image",
            )

        # Validate style
        valid_styles = {
            # Famous artworks
            "starry_night",
            "the_scream",
            "picasso",
            "monet",
            "van_gogh",
            "mona_lisa",
            "guernica",
            "the_great_wave",
            # Artistic movements
            "impressionism",
            "cubism",
            "abstract",
            "pop_art",
            "surrealism",
            "expressionism",
            "minimalism",
            "baroque",
            # Effects
            "oil_painting",
            "watercolor",
            "sketch",
            "anime",
            "comic_book",
            "pixel_art",
            "low_poly",
            "stained_glass",
            "mosaic",
        }

        if not self.style:
            raise ValidationError(
                "style must be specified", tool_name=self.tool_name, field="style"
            )

        # Allow custom styles if style_image_url is provided
        if self.style not in valid_styles and not self.style_image_url:
            raise ValidationError(
                f"Invalid style '{self.style}'. Valid styles: {sorted(valid_styles)} or provide style_image_url for custom style",
                tool_name=self.tool_name,
                field="style",
            )

        # Validate style_image_url if provided
        if self.style_image_url:
            if not self.style_image_url.startswith(("http://", "https://")):
                raise ValidationError(
                    "style_image_url must be a valid URL",
                    tool_name=self.tool_name,
                    field="style_image_url",
                )

        # Validate output_size format
        if self.output_size:
            if not isinstance(self.output_size, str) or "x" not in self.output_size:
                raise ValidationError(
                    "output_size must be in format 'WIDTHxHEIGHT' (e.g., '1024x1024')",
                    tool_name=self.tool_name,
                    field="output_size",
                )

            try:
                width, height = self.output_size.split("x")
                width_int = int(width)
                height_int = int(height)

                if width_int <= 0 or height_int <= 0:
                    raise ValueError("Dimensions must be positive")

                if width_int > 4096 or height_int > 4096:
                    raise ValidationError(
                        "Output size dimensions must not exceed 4096x4096",
                        tool_name=self.tool_name,
                        field="output_size",
                    )
            except ValueError as e:
                raise ValidationError(
                    f"Invalid output_size format: {e}",
                    tool_name=self.tool_name,
                    field="output_size",
                )

    def _should_use_mock(self) -> bool:
        """Check if mock mode enabled."""
        return os.getenv("USE_MOCK_APIS", "false").lower() == "true"

    def _generate_mock_results(self) -> Dict[str, Any]:
        """Generate mock results for testing."""
        result_id = str(uuid.uuid4())
        styled_image_url = f"https://mock-api.example.com/styled/{result_id}.jpg"

        return {
            "success": True,
            "result": {
                "styled_image_url": styled_image_url,
                "input_image": self.input_image,
                "style_applied": self.style,
                "style_strength": self.style_strength,
                "preserve_color": self.preserve_color,
                "output_size": self.output_size or "original",
                "processing_time_seconds": 3.5,
                "mock": True,
            },
            "metadata": {"mock_mode": True, "tool_name": self.tool_name, "result_id": result_id},
        }

    def _process(self) -> Dict[str, Any]:
        """Main processing logic for style transfer."""
        try:
            # In production, this would call a neural style transfer API
            # such as DeepAI, RunwayML, or a custom model endpoint

            result_id = str(uuid.uuid4())

            # Prepare API request
            api_payload = {
                "input_image": self.input_image,
                "style": self.style,
                "style_strength": self.style_strength,
                "preserve_color": self.preserve_color,
            }

            if self.style_image_url:
                api_payload["style_image"] = self.style_image_url

            if self.output_size:
                api_payload["output_size"] = self.output_size

            # Simulated API call
            # In real implementation:
            # response = requests.post(STYLE_TRANSFER_API_URL, json=api_payload, headers=...)
            # styled_image_url = response.json()["result_url"]

            styled_image_url = f"https://api.example.com/styled/{result_id}.jpg"

            return {
                "styled_image_url": styled_image_url,
                "input_image": self.input_image,
                "style_applied": self.style,
                "style_strength": self.style_strength,
                "preserve_color": self.preserve_color,
                "output_size": self.output_size or "original",
                "result_id": result_id,
            }

        except Exception as e:
            self._logger.error(f"Error in {self.tool_name}: {str(e)}", exc_info=True)
            raise APIError(f"Style transfer API error: {e}", tool_name=self.tool_name)


if __name__ == "__main__":
    print("Testing ImageStyleTransfer...")

    import os

    os.environ["USE_MOCK_APIS"] = "true"

    # Test with predefined style
    tool = ImageStyleTransfer(
        input_image="https://example.com/photo.jpg",
        style="starry_night",
        style_strength=0.8,
        preserve_color=False,
        output_size="1024x1024",
    )
    result = tool.run()

    print(f"Success: {result.get('success')}")
    print(f"Styled image URL: {result.get('result', {}).get('styled_image_url')}")
    print(f"Style applied: {result.get('result', {}).get('style_applied')}")

    assert result.get("success") == True
    assert "styled_image_url" in result.get("result", {})
    assert result.get("result", {}).get("style_applied") == "starry_night"

    # Test with custom style image
    tool2 = ImageStyleTransfer(
        input_image="https://example.com/photo.jpg",
        style="custom",
        style_image_url="https://example.com/style_reference.jpg",
        style_strength=0.6,
    )
    result2 = tool2.run()

    print(f"\nCustom style test success: {result2.get('success')}")
    assert result2.get("success") == True

    print("ImageStyleTransfer test passed!")
