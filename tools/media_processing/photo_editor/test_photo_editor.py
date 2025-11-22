"""
Unit tests for PhotoEditorTool
"""

import pytest
import os
from unittest.mock import patch, MagicMock
from PIL import Image
import io

from tools.media_processing.photo_editor.photo_editor import PhotoEditorTool
from shared.errors import ValidationError, MediaError


class TestPhotoEditorTool:
    """Test suite for PhotoEditorTool"""

    def setup_method(self):
        """Setup test environment before each test"""
        os.environ["USE_MOCK_APIS"] = "true"

    def teardown_method(self):
        """Cleanup after each test"""
        if "USE_MOCK_APIS" in os.environ:
            del os.environ["USE_MOCK_APIS"]

    # ==========================
    # Mock Mode Tests
    # ==========================

    def test_mock_mode_basic(self):
        """Test basic mock mode functionality"""
        tool = PhotoEditorTool(
            image_url="https://example.com/photo.jpg",
            operations=[
                {"type": "resize", "width": 800, "height": 600},
            ],
        )
        result = tool.run()

        assert result["success"] == True
        assert "edited_image_url" in result["result"]
        assert result["result"]["operations_applied"] == 1
        assert result["metadata"]["mock_mode"] == True

    def test_mock_mode_multiple_operations(self):
        """Test mock mode with multiple operations"""
        tool = PhotoEditorTool(
            image_url="https://example.com/photo.jpg",
            operations=[
                {"type": "resize", "width": 800, "height": 600},
                {"type": "filter", "name": "brightness", "value": 1.2},
                {"type": "filter", "name": "contrast", "value": 1.1},
                {"type": "rotate", "degrees": 90},
            ],
            output_format="jpg",
            quality=90,
        )
        result = tool.run()

        assert result["success"] == True
        assert result["result"]["operations_applied"] == 4
        assert result["result"]["format"] == "jpg"

    def test_mock_mode_different_formats(self):
        """Test mock mode with different output formats"""
        formats = ["png", "jpg", "webp"]
        for fmt in formats:
            tool = PhotoEditorTool(
                image_url="https://example.com/photo.jpg",
                operations=[{"type": "resize", "width": 100, "height": 100}],
                output_format=fmt,
            )
            result = tool.run()
            assert result["success"] == True
            assert result["result"]["format"] == fmt

    # ==========================
    # Validation Tests
    # ==========================

    def test_validation_empty_image_url(self):
        """Test validation fails with empty image URL"""
        with pytest.raises(ValidationError) as exc_info:
            tool = PhotoEditorTool(
                image_url="   ",
                operations=[{"type": "resize", "width": 100, "height": 100}],
            )
            tool.run()

        assert "image_url cannot be empty" in str(exc_info.value)

    def test_validation_invalid_output_format(self):
        """Test validation fails with invalid output format"""
        with pytest.raises(ValidationError) as exc_info:
            tool = PhotoEditorTool(
                image_url="https://example.com/photo.jpg",
                operations=[{"type": "resize", "width": 100, "height": 100}],
                output_format="invalid",
            )
            tool.run()

        assert "output_format must be one of" in str(exc_info.value)

    def test_validation_empty_operations(self):
        """Test validation fails with empty operations list"""
        with pytest.raises(ValidationError) as exc_info:
            tool = PhotoEditorTool(
                image_url="https://example.com/photo.jpg",
                operations=[],
            )

        assert "At least one operation is required" in str(exc_info.value)

    def test_validation_operation_missing_type(self):
        """Test validation fails when operation missing type field"""
        with pytest.raises(ValidationError) as exc_info:
            tool = PhotoEditorTool(
                image_url="https://example.com/photo.jpg",
                operations=[{"width": 100, "height": 100}],
            )
            tool.run()

        assert "missing 'type' field" in str(exc_info.value)

    def test_validation_unsupported_operation_type(self):
        """Test validation fails with unsupported operation type"""
        with pytest.raises(ValidationError) as exc_info:
            tool = PhotoEditorTool(
                image_url="https://example.com/photo.jpg",
                operations=[{"type": "unsupported_op"}],
            )
            tool.run()

        assert "not supported" in str(exc_info.value)

    def test_validation_filter_missing_name(self):
        """Test validation fails when filter operation missing name"""
        with pytest.raises(ValidationError) as exc_info:
            tool = PhotoEditorTool(
                image_url="https://example.com/photo.jpg",
                operations=[{"type": "filter", "value": 1.2}],
            )
            tool.run()

        assert "missing 'name' field" in str(exc_info.value)

    def test_validation_unsupported_filter(self):
        """Test validation fails with unsupported filter name"""
        with pytest.raises(ValidationError) as exc_info:
            tool = PhotoEditorTool(
                image_url="https://example.com/photo.jpg",
                operations=[{"type": "filter", "name": "unsupported_filter"}],
            )
            tool.run()

        assert "Filter 'unsupported_filter' not supported" in str(exc_info.value)

    def test_validation_quality_range(self):
        """Test quality parameter validation (1-100)"""
        # Valid quality values
        for quality in [1, 50, 100]:
            tool = PhotoEditorTool(
                image_url="https://example.com/photo.jpg",
                operations=[{"type": "resize", "width": 100, "height": 100}],
                quality=quality,
            )
            result = tool.run()
            assert result["success"] == True

        # Invalid quality values should be caught by Pydantic
        with pytest.raises(Exception):  # Pydantic ValidationError
            tool = PhotoEditorTool(
                image_url="https://example.com/photo.jpg",
                operations=[{"type": "resize", "width": 100, "height": 100}],
                quality=0,
            )

        with pytest.raises(Exception):  # Pydantic ValidationError
            tool = PhotoEditorTool(
                image_url="https://example.com/photo.jpg",
                operations=[{"type": "resize", "width": 100, "height": 100}],
                quality=101,
            )

    # ==========================
    # Real Processing Tests (with mocked image)
    # ==========================

    def create_test_image(self, width=800, height=600, mode="RGB"):
        """Helper to create a test image"""
        return Image.new(mode, (width, height), color=(255, 0, 0))

    def test_process_resize_operation(self):
        """Test actual resize operation processing"""
        os.environ.pop("USE_MOCK_APIS", None)

        # Create test image
        test_image = self.create_test_image(800, 600)
        img_bytes = io.BytesIO()
        test_image.save(img_bytes, format="PNG")
        img_bytes.seek(0)

        with patch("requests.get") as mock_get:
            mock_response = MagicMock()
            mock_response.content = img_bytes.read()
            mock_response.raise_for_status = MagicMock()
            mock_get.return_value = mock_response

            tool = PhotoEditorTool(
                image_url="https://example.com/photo.jpg",
                operations=[{"type": "resize", "width": 400, "height": 300}],
                output_format="png",
            )
            result = tool.run()

            assert result["success"] == True
            assert "edited_image_url" in result["result"]
            assert result["result"]["size"] == "400x300"

    def test_process_crop_operation(self):
        """Test actual crop operation processing"""
        os.environ.pop("USE_MOCK_APIS", None)

        test_image = self.create_test_image(800, 600)
        img_bytes = io.BytesIO()
        test_image.save(img_bytes, format="PNG")
        img_bytes.seek(0)

        with patch("requests.get") as mock_get:
            mock_response = MagicMock()
            mock_response.content = img_bytes.read()
            mock_response.raise_for_status = MagicMock()
            mock_get.return_value = mock_response

            tool = PhotoEditorTool(
                image_url="https://example.com/photo.jpg",
                operations=[{"type": "crop", "x": 100, "y": 100, "width": 200, "height": 200}],
                output_format="png",
            )
            result = tool.run()

            assert result["success"] == True
            assert result["result"]["size"] == "200x200"

    def test_process_rotate_operation(self):
        """Test actual rotate operation processing"""
        os.environ.pop("USE_MOCK_APIS", None)

        test_image = self.create_test_image(800, 600)
        img_bytes = io.BytesIO()
        test_image.save(img_bytes, format="PNG")
        img_bytes.seek(0)

        with patch("requests.get") as mock_get:
            mock_response = MagicMock()
            mock_response.content = img_bytes.read()
            mock_response.raise_for_status = MagicMock()
            mock_get.return_value = mock_response

            tool = PhotoEditorTool(
                image_url="https://example.com/photo.jpg",
                operations=[{"type": "rotate", "degrees": 90}],
                output_format="png",
            )
            result = tool.run()

            assert result["success"] == True
            # After 90 degree rotation, dimensions should swap (with expand=True)

    def test_process_flip_horizontal(self):
        """Test horizontal flip operation"""
        os.environ.pop("USE_MOCK_APIS", None)

        test_image = self.create_test_image(800, 600)
        img_bytes = io.BytesIO()
        test_image.save(img_bytes, format="PNG")
        img_bytes.seek(0)

        with patch("requests.get") as mock_get:
            mock_response = MagicMock()
            mock_response.content = img_bytes.read()
            mock_response.raise_for_status = MagicMock()
            mock_get.return_value = mock_response

            tool = PhotoEditorTool(
                image_url="https://example.com/photo.jpg",
                operations=[{"type": "flip", "direction": "horizontal"}],
                output_format="png",
            )
            result = tool.run()

            assert result["success"] == True

    def test_process_flip_vertical(self):
        """Test vertical flip operation"""
        os.environ.pop("USE_MOCK_APIS", None)

        test_image = self.create_test_image(800, 600)
        img_bytes = io.BytesIO()
        test_image.save(img_bytes, format="PNG")
        img_bytes.seek(0)

        with patch("requests.get") as mock_get:
            mock_response = MagicMock()
            mock_response.content = img_bytes.read()
            mock_response.raise_for_status = MagicMock()
            mock_get.return_value = mock_response

            tool = PhotoEditorTool(
                image_url="https://example.com/photo.jpg",
                operations=[{"type": "flip", "direction": "vertical"}],
                output_format="png",
            )
            result = tool.run()

            assert result["success"] == True

    def test_process_brightness_filter(self):
        """Test brightness filter"""
        os.environ.pop("USE_MOCK_APIS", None)

        test_image = self.create_test_image(800, 600)
        img_bytes = io.BytesIO()
        test_image.save(img_bytes, format="PNG")
        img_bytes.seek(0)

        with patch("requests.get") as mock_get:
            mock_response = MagicMock()
            mock_response.content = img_bytes.read()
            mock_response.raise_for_status = MagicMock()
            mock_get.return_value = mock_response

            tool = PhotoEditorTool(
                image_url="https://example.com/photo.jpg",
                operations=[{"type": "filter", "name": "brightness", "value": 1.2}],
                output_format="png",
            )
            result = tool.run()

            assert result["success"] == True

    def test_process_contrast_filter(self):
        """Test contrast filter"""
        os.environ.pop("USE_MOCK_APIS", None)

        test_image = self.create_test_image(800, 600)
        img_bytes = io.BytesIO()
        test_image.save(img_bytes, format="PNG")
        img_bytes.seek(0)

        with patch("requests.get") as mock_get:
            mock_response = MagicMock()
            mock_response.content = img_bytes.read()
            mock_response.raise_for_status = MagicMock()
            mock_get.return_value = mock_response

            tool = PhotoEditorTool(
                image_url="https://example.com/photo.jpg",
                operations=[{"type": "filter", "name": "contrast", "value": 1.1}],
                output_format="png",
            )
            result = tool.run()

            assert result["success"] == True

    def test_process_saturation_filter(self):
        """Test saturation filter"""
        os.environ.pop("USE_MOCK_APIS", None)

        test_image = self.create_test_image(800, 600)
        img_bytes = io.BytesIO()
        test_image.save(img_bytes, format="PNG")
        img_bytes.seek(0)

        with patch("requests.get") as mock_get:
            mock_response = MagicMock()
            mock_response.content = img_bytes.read()
            mock_response.raise_for_status = MagicMock()
            mock_get.return_value = mock_response

            tool = PhotoEditorTool(
                image_url="https://example.com/photo.jpg",
                operations=[{"type": "filter", "name": "saturation", "value": 1.3}],
                output_format="png",
            )
            result = tool.run()

            assert result["success"] == True

    def test_process_blur_filter(self):
        """Test blur filter"""
        os.environ.pop("USE_MOCK_APIS", None)

        test_image = self.create_test_image(800, 600)
        img_bytes = io.BytesIO()
        test_image.save(img_bytes, format="PNG")
        img_bytes.seek(0)

        with patch("requests.get") as mock_get:
            mock_response = MagicMock()
            mock_response.content = img_bytes.read()
            mock_response.raise_for_status = MagicMock()
            mock_get.return_value = mock_response

            tool = PhotoEditorTool(
                image_url="https://example.com/photo.jpg",
                operations=[{"type": "filter", "name": "blur", "radius": 5}],
                output_format="png",
            )
            result = tool.run()

            assert result["success"] == True

    def test_process_sharpen_filter(self):
        """Test sharpen filter"""
        os.environ.pop("USE_MOCK_APIS", None)

        test_image = self.create_test_image(800, 600)
        img_bytes = io.BytesIO()
        test_image.save(img_bytes, format="PNG")
        img_bytes.seek(0)

        with patch("requests.get") as mock_get:
            mock_response = MagicMock()
            mock_response.content = img_bytes.read()
            mock_response.raise_for_status = MagicMock()
            mock_get.return_value = mock_response

            tool = PhotoEditorTool(
                image_url="https://example.com/photo.jpg",
                operations=[{"type": "filter", "name": "sharpen", "amount": 1.5}],
                output_format="png",
            )
            result = tool.run()

            assert result["success"] == True

    def test_process_multiple_operations_chained(self):
        """Test multiple operations applied in sequence"""
        os.environ.pop("USE_MOCK_APIS", None)

        test_image = self.create_test_image(800, 600)
        img_bytes = io.BytesIO()
        test_image.save(img_bytes, format="PNG")
        img_bytes.seek(0)

        with patch("requests.get") as mock_get:
            mock_response = MagicMock()
            mock_response.content = img_bytes.read()
            mock_response.raise_for_status = MagicMock()
            mock_get.return_value = mock_response

            tool = PhotoEditorTool(
                image_url="https://example.com/photo.jpg",
                operations=[
                    {"type": "resize", "width": 400, "height": 300},
                    {"type": "filter", "name": "brightness", "value": 1.2},
                    {"type": "filter", "name": "contrast", "value": 1.1},
                    {"type": "rotate", "degrees": 45},
                ],
                output_format="jpg",
                quality=85,
            )
            result = tool.run()

            assert result["success"] == True
            assert result["result"]["operations_applied"] == 4

    def test_process_jpeg_conversion_from_rgba(self):
        """Test JPEG output from RGBA image (should convert to RGB)"""
        os.environ.pop("USE_MOCK_APIS", None)

        test_image = self.create_test_image(800, 600, mode="RGBA")
        img_bytes = io.BytesIO()
        test_image.save(img_bytes, format="PNG")
        img_bytes.seek(0)

        with patch("requests.get") as mock_get:
            mock_response = MagicMock()
            mock_response.content = img_bytes.read()
            mock_response.raise_for_status = MagicMock()
            mock_get.return_value = mock_response

            tool = PhotoEditorTool(
                image_url="https://example.com/photo.png",
                operations=[{"type": "resize", "width": 400, "height": 300}],
                output_format="jpg",
                quality=90,
            )
            result = tool.run()

            assert result["success"] == True
            assert result["result"]["format"] == "jpg"

    # ==========================
    # Error Handling Tests
    # ==========================

    def test_error_invalid_image_url(self):
        """Test error handling for invalid image URL"""
        os.environ.pop("USE_MOCK_APIS", None)

        with patch("requests.get") as mock_get:
            mock_get.side_effect = Exception("Network error")

            tool = PhotoEditorTool(
                image_url="https://example.com/invalid.jpg",
                operations=[{"type": "resize", "width": 100, "height": 100}],
            )
            result = tool.run()

            assert result["success"] == False
            assert "error" in result

    def test_error_missing_resize_dimensions(self):
        """Test error when resize operation missing dimensions"""
        os.environ.pop("USE_MOCK_APIS", None)

        test_image = self.create_test_image(800, 600)
        img_bytes = io.BytesIO()
        test_image.save(img_bytes, format="PNG")
        img_bytes.seek(0)

        with patch("requests.get") as mock_get:
            mock_response = MagicMock()
            mock_response.content = img_bytes.read()
            mock_response.raise_for_status = MagicMock()
            mock_get.return_value = mock_response

            tool = PhotoEditorTool(
                image_url="https://example.com/photo.jpg",
                operations=[{"type": "resize"}],  # Missing width and height
            )
            result = tool.run()

            assert result["success"] == False
            assert "error" in result

    def test_error_missing_crop_dimensions(self):
        """Test error when crop operation missing dimensions"""
        os.environ.pop("USE_MOCK_APIS", None)

        test_image = self.create_test_image(800, 600)
        img_bytes = io.BytesIO()
        test_image.save(img_bytes, format="PNG")
        img_bytes.seek(0)

        with patch("requests.get") as mock_get:
            mock_response = MagicMock()
            mock_response.content = img_bytes.read()
            mock_response.raise_for_status = MagicMock()
            mock_get.return_value = mock_response

            tool = PhotoEditorTool(
                image_url="https://example.com/photo.jpg",
                operations=[{"type": "crop", "x": 0, "y": 0}],  # Missing width and height
            )
            result = tool.run()

            assert result["success"] == False
            assert "error" in result

    def test_error_invalid_flip_direction(self):
        """Test error when flip has invalid direction"""
        os.environ.pop("USE_MOCK_APIS", None)

        test_image = self.create_test_image(800, 600)
        img_bytes = io.BytesIO()
        test_image.save(img_bytes, format="PNG")
        img_bytes.seek(0)

        with patch("requests.get") as mock_get:
            mock_response = MagicMock()
            mock_response.content = img_bytes.read()
            mock_response.raise_for_status = MagicMock()
            mock_get.return_value = mock_response

            tool = PhotoEditorTool(
                image_url="https://example.com/photo.jpg",
                operations=[{"type": "flip", "direction": "invalid"}],
            )
            result = tool.run()

            assert result["success"] == False
            assert "error" in result

    # ==========================
    # Integration Tests
    # ==========================

    def test_integration_complete_workflow(self):
        """Test complete workflow with all operation types"""
        os.environ["USE_MOCK_APIS"] = "true"

        tool = PhotoEditorTool(
            image_url="https://example.com/photo.jpg",
            operations=[
                {"type": "resize", "width": 1000, "height": 800},
                {"type": "crop", "x": 100, "y": 100, "width": 800, "height": 600},
                {"type": "rotate", "degrees": 15},
                {"type": "flip", "direction": "horizontal"},
                {"type": "filter", "name": "brightness", "value": 1.1},
                {"type": "filter", "name": "contrast", "value": 1.2},
                {"type": "filter", "name": "saturation", "value": 1.15},
                {"type": "filter", "name": "sharpen", "amount": 1.3},
            ],
            output_format="jpg",
            quality=95,
        )
        result = tool.run()

        assert result["success"] == True
        assert result["result"]["operations_applied"] == 8
        assert result["result"]["format"] == "jpg"


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])
