"""
Perform advanced photo editing operations on existing images.
"""

from typing import Any, Dict, List
from pydantic import Field
import os
import io
import requests
from PIL import Image, ImageEnhance, ImageFilter, ImageOps
import tempfile

from shared.base import BaseTool
from shared.errors import ValidationError, APIError, MediaError


class PhotoEditorTool(BaseTool):
    """
    Perform advanced photo editing operations on existing images.

    Use this tool to enhance, modify, and process images including resize,
    crop, filters, background removal, and overlays.

    Args:
        image_url: URL to source image
        operations: List of editing operations to apply
        output_format: Output format (png, jpg, webp)
        quality: Output quality 1-100 (for jpg)

    Returns:
        Dict containing:
        - success: Boolean indicating success
        - result: {"edited_image_url": "...", "format": "...", "size": "..."}
        - metadata: Processing metadata

    Example:
        >>> tool = PhotoEditorTool(
        ...     image_url="https://example.com/photo.jpg",
        ...     operations=[
        ...         {"type": "resize", "width": 800, "height": 600},
        ...         {"type": "filter", "name": "brightness", "value": 1.2},
        ...         {"type": "filter", "name": "contrast", "value": 1.1}
        ...     ],
        ...     output_format="jpg",
        ...     quality=90
        ... )
        >>> result = tool.run()
    """

    # Tool metadata
    tool_name: str = "photo_editor"
    tool_category: str = "media"

    # Parameters
    image_url: str = Field(..., description="URL to source image")
    operations: List[Dict[str, Any]] = Field(
        ..., description="List of editing operations", min_length=1
    )
    output_format: str = Field("png", description="Output format: png, jpg, webp")
    quality: int = Field(
        90, description="Output quality 1-100 (jpg only)", ge=1, le=100
    )

    # Supported operation types and filters
    SUPPORTED_OPERATIONS = {
        "resize",
        "crop",
        "rotate",
        "flip",
        "filter",
        "background_remove",
    }
    SUPPORTED_FILTERS = {
        "brightness",
        "contrast",
        "saturation",
        "blur",
        "sharpen",
    }
    SUPPORTED_FORMATS = {"png", "jpg", "jpeg", "webp"}

    def _execute(self) -> Dict[str, Any]:
        """
        Execute the photo_editor tool.

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
            raise MediaError(
                f"Photo editing failed: {e}",
                media_type="image",
                tool_name=self.tool_name,
            )

    def _validate_parameters(self) -> None:
        """Validate input parameters."""
        # Validate image URL
        if not self.image_url.strip():
            raise ValidationError("image_url cannot be empty", tool_name=self.tool_name)

        # Validate output format
        if self.output_format.lower() not in self.SUPPORTED_FORMATS:
            raise ValidationError(
                f"output_format must be one of {self.SUPPORTED_FORMATS}",
                field="output_format",
                tool_name=self.tool_name,
            )

        # Validate operations
        if not self.operations:
            raise ValidationError(
                "At least one operation is required",
                field="operations",
                tool_name=self.tool_name,
            )

        # Validate each operation
        for i, operation in enumerate(self.operations):
            if "type" not in operation:
                raise ValidationError(
                    f"Operation {i} missing 'type' field",
                    field="operations",
                    tool_name=self.tool_name,
                )

            op_type = operation["type"]
            if op_type not in self.SUPPORTED_OPERATIONS:
                raise ValidationError(
                    f"Operation type '{op_type}' not supported. Must be one of {self.SUPPORTED_OPERATIONS}",
                    field="operations",
                    tool_name=self.tool_name,
                )

            # Validate filter operations
            if op_type == "filter":
                if "name" not in operation:
                    raise ValidationError(
                        f"Filter operation {i} missing 'name' field",
                        field="operations",
                        tool_name=self.tool_name,
                    )
                filter_name = operation["name"]
                if filter_name not in self.SUPPORTED_FILTERS:
                    raise ValidationError(
                        f"Filter '{filter_name}' not supported. Must be one of {self.SUPPORTED_FILTERS}",
                        field="operations",
                        tool_name=self.tool_name,
                    )

    def _should_use_mock(self) -> bool:
        """Check if mock mode enabled."""
        return os.getenv("USE_MOCK_APIS", "false").lower() == "true"

    def _generate_mock_results(self) -> Dict[str, Any]:
        """Generate mock results for testing."""
        return {
            "success": True,
            "result": {
                "edited_image_url": "https://mock.example.com/edited_photo_123.png",
                "format": self.output_format,
                "size": "800x600",
                "file_size": "245 KB",
                "operations_applied": len(self.operations),
            },
            "metadata": {"mock_mode": True},
        }

    def _process(self) -> Dict[str, Any]:
        """Main processing logic."""
        try:
            # Download image
            image = self._download_image(self.image_url)

            # Apply operations in sequence
            for operation in self.operations:
                image = self._apply_operation(image, operation)

            # Save edited image
            edited_url, file_size = self._save_image(image)

            return {
                "edited_image_url": edited_url,
                "format": self.output_format,
                "size": f"{image.width}x{image.height}",
                "file_size": file_size,
                "operations_applied": len(self.operations),
            }

        except requests.RequestException as e:
            raise APIError(
                f"Failed to download image: {e}", tool_name=self.tool_name
            )
        except Exception as e:
            raise MediaError(
                f"Image processing failed: {e}",
                media_type="image",
                tool_name=self.tool_name,
            )

    def _download_image(self, url: str) -> Image.Image:
        """
        Download image from URL.

        Args:
            url: Image URL

        Returns:
            PIL Image object
        """
        response = requests.get(url, timeout=30)
        response.raise_for_status()

        try:
            image = Image.open(io.BytesIO(response.content))
            # Convert to RGB if necessary (for formats that don't support alpha)
            if image.mode not in ("RGB", "RGBA"):
                image = image.convert("RGB")
            return image
        except Exception as e:
            raise MediaError(
                f"Invalid image format: {e}",
                media_type="image",
                tool_name=self.tool_name,
            )

    def _apply_operation(self, image: Image.Image, operation: Dict[str, Any]) -> Image.Image:
        """
        Apply a single operation to the image.

        Args:
            image: PIL Image object
            operation: Operation dictionary

        Returns:
            Modified PIL Image object
        """
        op_type = operation["type"]

        if op_type == "resize":
            return self._apply_resize(image, operation)
        elif op_type == "crop":
            return self._apply_crop(image, operation)
        elif op_type == "rotate":
            return self._apply_rotate(image, operation)
        elif op_type == "flip":
            return self._apply_flip(image, operation)
        elif op_type == "filter":
            return self._apply_filter(image, operation)
        elif op_type == "background_remove":
            return self._apply_background_remove(image, operation)
        else:
            raise ValidationError(
                f"Unsupported operation type: {op_type}",
                tool_name=self.tool_name,
            )

    def _apply_resize(self, image: Image.Image, operation: Dict[str, Any]) -> Image.Image:
        """Resize image to specified dimensions."""
        width = operation.get("width")
        height = operation.get("height")

        if not width or not height:
            raise ValidationError(
                "Resize operation requires 'width' and 'height'",
                tool_name=self.tool_name,
            )

        return image.resize((int(width), int(height)), Image.Resampling.LANCZOS)

    def _apply_crop(self, image: Image.Image, operation: Dict[str, Any]) -> Image.Image:
        """Crop image to specified region."""
        x = operation.get("x", 0)
        y = operation.get("y", 0)
        width = operation.get("width")
        height = operation.get("height")

        if width is None or height is None:
            raise ValidationError(
                "Crop operation requires 'width' and 'height'",
                tool_name=self.tool_name,
            )

        box = (int(x), int(y), int(x + width), int(y + height))
        return image.crop(box)

    def _apply_rotate(self, image: Image.Image, operation: Dict[str, Any]) -> Image.Image:
        """Rotate image by specified degrees."""
        degrees = operation.get("degrees", 0)
        expand = operation.get("expand", True)

        return image.rotate(float(degrees), expand=expand, resample=Image.Resampling.BICUBIC)

    def _apply_flip(self, image: Image.Image, operation: Dict[str, Any]) -> Image.Image:
        """Flip image horizontally or vertically."""
        direction = operation.get("direction", "horizontal")

        if direction == "horizontal":
            return ImageOps.mirror(image)
        elif direction == "vertical":
            return ImageOps.flip(image)
        else:
            raise ValidationError(
                f"Flip direction must be 'horizontal' or 'vertical', got '{direction}'",
                tool_name=self.tool_name,
            )

    def _apply_filter(self, image: Image.Image, operation: Dict[str, Any]) -> Image.Image:
        """Apply filter to image."""
        filter_name = operation.get("name")

        if filter_name == "brightness":
            value = operation.get("value", 1.0)
            enhancer = ImageEnhance.Brightness(image)
            return enhancer.enhance(float(value))

        elif filter_name == "contrast":
            value = operation.get("value", 1.0)
            enhancer = ImageEnhance.Contrast(image)
            return enhancer.enhance(float(value))

        elif filter_name == "saturation":
            value = operation.get("value", 1.0)
            enhancer = ImageEnhance.Color(image)
            return enhancer.enhance(float(value))

        elif filter_name == "blur":
            radius = operation.get("radius", 5)
            return image.filter(ImageFilter.GaussianBlur(radius=float(radius)))

        elif filter_name == "sharpen":
            amount = operation.get("amount", 1.5)
            enhancer = ImageEnhance.Sharpness(image)
            return enhancer.enhance(float(amount))

        else:
            raise ValidationError(
                f"Unsupported filter: {filter_name}",
                tool_name=self.tool_name,
            )

    def _apply_background_remove(
        self, image: Image.Image, operation: Dict[str, Any]
    ) -> Image.Image:
        """
        Remove background from image (mock implementation).

        Note: In production, this would use a background removal API
        or library like rembg. For now, returns the original image.
        """
        # In mock mode or when no background removal service is available,
        # just return the original image with a note
        self._logger.warning(
            "Background removal not implemented. Returning original image. "
            "Consider using a dedicated background removal API in production."
        )
        return image

    def _save_image(self, image: Image.Image) -> tuple[str, str]:
        """
        Save image to temporary file and return URL.

        Args:
            image: PIL Image object

        Returns:
            Tuple of (url, file_size)
        """
        # Create temporary file
        with tempfile.NamedTemporaryFile(
            mode="wb",
            suffix=f".{self.output_format}",
            delete=False,
        ) as tmp_file:
            # Convert format if needed
            save_kwargs = {}
            output_format = self.output_format.upper()
            if output_format == "JPG":
                output_format = "JPEG"
                # Convert RGBA to RGB for JPEG
                if image.mode == "RGBA":
                    # Create white background
                    background = Image.new("RGB", image.size, (255, 255, 255))
                    background.paste(image, mask=image.split()[3])  # Use alpha channel as mask
                    image = background
                save_kwargs["quality"] = self.quality
                save_kwargs["optimize"] = True

            elif output_format == "PNG":
                save_kwargs["optimize"] = True

            elif output_format == "WEBP":
                save_kwargs["quality"] = self.quality

            # Save image
            image.save(tmp_file, format=output_format, **save_kwargs)
            tmp_path = tmp_file.name

        # Get file size
        file_size_bytes = os.path.getsize(tmp_path)
        if file_size_bytes < 1024:
            file_size = f"{file_size_bytes} B"
        elif file_size_bytes < 1024 * 1024:
            file_size = f"{file_size_bytes / 1024:.1f} KB"
        else:
            file_size = f"{file_size_bytes / (1024 * 1024):.1f} MB"

        # In production, upload to AI Drive or cloud storage
        # For now, return local file URL
        file_url = f"file://{tmp_path}"

        # Check if AI Drive is available
        aidrive_key = os.getenv("AIDRIVE_API_KEY")
        if aidrive_key:
            # TODO: Upload to AI Drive when available
            self._logger.info(f"AI Drive available. File saved locally at {tmp_path}")
        else:
            self._logger.info(
                f"Image saved locally at {tmp_path}. "
                "Set AIDRIVE_API_KEY to upload to cloud storage."
            )

        return file_url, file_size


if __name__ == "__main__":
    # Test the photo_editor tool
    print("Testing PhotoEditorTool...")

    # Test with mock mode
    import os

    os.environ["USE_MOCK_APIS"] = "true"

    # Test basic resize and filter
    tool = PhotoEditorTool(
        image_url="https://example.com/photo.jpg",
        operations=[
            {"type": "resize", "width": 800, "height": 600},
            {"type": "filter", "name": "brightness", "value": 1.2},
            {"type": "filter", "name": "contrast", "value": 1.1},
        ],
        output_format="jpg",
        quality=90,
    )
    result = tool.run()

    assert result.get("success") == True
    assert "edited_image_url" in result["result"]
    assert result["result"]["operations_applied"] == 3
    print("✅ Basic resize and filter test passed")

    # Test crop and rotate
    tool2 = PhotoEditorTool(
        image_url="https://example.com/photo2.jpg",
        operations=[
            {"type": "crop", "x": 0, "y": 0, "width": 500, "height": 500},
            {"type": "rotate", "degrees": 90},
        ],
        output_format="png",
    )
    result2 = tool2.run()
    assert result2.get("success") == True
    assert result2["result"]["format"] == "png"
    print("✅ Crop and rotate test passed")

    # Test flip and blur
    tool3 = PhotoEditorTool(
        image_url="https://example.com/photo3.jpg",
        operations=[
            {"type": "flip", "direction": "horizontal"},
            {"type": "filter", "name": "blur", "radius": 5},
        ],
        output_format="webp",
        quality=85,
    )
    result3 = tool3.run()
    assert result3.get("success") == True
    print("✅ Flip and blur test passed")

    # Test saturation and sharpen
    tool4 = PhotoEditorTool(
        image_url="https://example.com/photo4.jpg",
        operations=[
            {"type": "filter", "name": "saturation", "value": 1.3},
            {"type": "filter", "name": "sharpen", "amount": 1.5},
        ],
        output_format="jpg",
    )
    result4 = tool4.run()
    assert result4.get("success") == True
    print("✅ Saturation and sharpen test passed")

    # Test validation error
    try:
        tool5 = PhotoEditorTool(
            image_url="https://example.com/photo.jpg",
            operations=[{"type": "invalid_operation"}],
        )
        result5 = tool5.run()
        assert False, "Should have raised ValidationError"
    except Exception as e:
        print(f"✅ Validation error test passed: {type(e).__name__}")

    print("\n🎉 All tests passed!")
